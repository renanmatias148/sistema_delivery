from flask import Flask

def create_app():
    app = Flask(__name__)
    app.config.from_pyfile('../instance/config.py')

    @app.route('/')
    def home():
        return 'Sistema de Delivery Iniciado!'

    return app
