import os

from flask import Flask, send_from_directory
from flask_cors import CORS

UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'static/uploads')

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass
    
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

    @app.route('/', methods=['GET'])
    def hello():
        return "Hello!"

    @app.route('/uploads/<filename>', methods=['GET'])
    def uploaded_file(filename):
        return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

    from . import db
    db.init_app(app)

    from . import curator
    app.register_blueprint(curator.bp)

    from . import art_display
    app.register_blueprint(art_display.bp)

    CORS(app)
    return app