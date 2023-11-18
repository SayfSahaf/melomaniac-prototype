from website import create_app
import os

app = create_app()

app.secret_key = os.getenv("COOKIE_KEY")
if __name__ == '__main__':
    app.run(debug=True)