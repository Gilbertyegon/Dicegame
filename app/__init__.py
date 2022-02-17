import logging
from flask import Flask

logging.basicConfig(level=logging.DEBUG)

SECRET_KEY = 'This is secret'

def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = SECRET_KEY

    from app.main.routes import main
    from app.game.routes import game
    app.register_blueprint(main)
    app.register_blueprint(game)

    return app
    