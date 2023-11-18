import os
from dotenv import load_dotenv
import spotipy
import time
from datetime import datetime 
from spotipy.oauth2 import SpotifyOAuth
from flask import Flask, request, url_for, session, redirect, render_template, Blueprint, flash
import random

TOKEN_INFO = 'token_info'

load_dotenv()

views = Blueprint('views', __name__)

client_key = os.getenv("CLIENT_KEY")
secret_key = os.getenv("SECRET_KEY")

@views.route('/')
def home():
    return render_template("home.html")

@views.route('/auth_spotify')
def authSpotify():
    auth_url = create_spotify_oauth().get_authorize_url()
    return redirect(auth_url)

@views.route('/redirect')
def redirect_page():
    session.clear()
    code = request.args.get('code')
    token_info = create_spotify_oauth().get_access_token(code)
    session[TOKEN_INFO] = token_info
    return redirect(url_for('views.standby_page', _external=True))
    

@views.route('/standby')
def standby_page():
    return render_template("ready.html")

@views.route('/ready')
def ready():
    return redirect(url_for('views.create_new_playlist', _external=True))

@views.route('/create_new_playlist')
def create_new_playlist():
    try:
        token_info = get_token()
    except:
        return redirect('/')

    sp = spotipy.Spotify(auth=token_info['access_token'])
    user_id = sp.current_user()['id']
    
    top_artists = sp.current_user_top_artists(30)
    top_tracks = sp.current_user_top_tracks(30)

    temp1 = datetime.now()
    current_time = temp1.strftime("%Y-%m-%d")

    print(current_time)

    temp_genre = []
    temp_artist_id = []
    temp_track_id = []

    recomendations_size = 20
    recommended_tracks_size = 15

    for i in range(recomendations_size):
        for genre in top_artists['items'][i]['genres']:
            if genre not in temp_genre:
                temp_genre.append(genre)
        temp_artist_id.append(top_artists['items'][i]['id'])
        temp_track_id.append(top_tracks['items'][i]['id'])

    recommended_tracks = sp.recommendations(seed_artists=[random.choice(temp_artist_id)], seed_genres=[random.choice(temp_genre)], seed_tracks=[random.choice(temp_track_id)], limit=recommended_tracks_size)
    recommended_tracks_uri = []

    for i in range(recommended_tracks_size):
        recommended_tracks_uri.append(recommended_tracks['tracks'][i]['uri'])

    new_playlist = sp.user_playlist_create(user_id, f'Melomaniac! {current_time}', True)

    sp.user_playlist_add_tracks(user_id, new_playlist['id'], recommended_tracks_uri)

    flash('Playlist added.', category='success')

    return redirect(url_for('views.standby_page', _external=True))





def get_token():
    token_info = session.get(TOKEN_INFO, None)
    if not token_info:
        redirect(url_for('login', _external=False))

    now = int(time.time())

    is_expired = token_info['expires_at'] - now < 60

    if(is_expired):
        spotify_oauth = create_spotify_oauth()
        token_info = spotify_oauth.refresh_access_token(token_info['refresh_token'])
    
    return token_info


def create_spotify_oauth():
    return SpotifyOAuth(
        client_id =     client_key,
        client_secret = secret_key,
        redirect_uri =  url_for('views.redirect_page', _external=True),
        scope =         'user-library-read playlist-modify-public playlist-modify-private user-top-read'
    )