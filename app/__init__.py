from flask import Flask
from flask_cors import CORS
from . import db
from . import api

import os


def create_app():
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder='../dist',
    )
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite3'),
    )

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    db.init_app(app)

    app.register_blueprint(api.bp)

    @app.route('/css/<path:path>')
    def serve_css(path):
        print('path', path)
        return app.send_static_file('css/' + path)

    @app.route('/js/<path:path>')
    def serve_js(path):
        return app.send_static_file('js/' + path)

    @app.route('/vendor/<path:path>')
    def serve_vendor(path):
        return app.send_static_file('vendor/' + path)

    @app.route('/favicon.ico')
    def serve_icon():
        return app.send_static_file('favicon.ico')

    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return app.send_static_file('index.html')

    return app
