from flask import Flask, render_template


def create_app(test_config=None):
    app = Flask(
        __name__,
        static_folder='../dist',
        static_url_path='',
        template_folder='../dist'
    )
    
    @app.route('/', defaults={'path': ''})
    @app.route('/<path:path>')
    def catch_all(path):
        return render_template("index.html")

    return app
