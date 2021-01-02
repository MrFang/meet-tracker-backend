from flask import Flask, render_template
from flask_cors import CORS
from . import db
from . import api

import os


def create_app():
    app = Flask(
        __name__,
        instance_relative_config=True,
        static_folder='../dist',
        template_folder='../dist',
        static_url_path=''
    )
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    db.init_app(app)

    app.register_blueprint(api.bp)
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return render_template('index.html')

    return app
