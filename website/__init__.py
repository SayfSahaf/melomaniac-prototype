from flask import Flask

def create_app() :
    app = Flask(__name__)
    
    app.config['SESSION_COOKIE_NAME'] = 'prototype cookie'

    from .views import views

    app.register_blueprint(views, url_prefix='/')

    return app