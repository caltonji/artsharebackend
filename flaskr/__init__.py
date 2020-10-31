import os, uuid

from flask import Flask, send_from_directory
from flask_cors import CORS
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from flaskr.service_factory import get_table_service, get_blob_service_client

def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_mapping(
        SECRET_KEY='dev',
        DATABASE=os.path.join(app.instance_path, 'flaskr.sqlite'),
    )

    # Setup storage
    with app.app_context():
        table_service = get_table_service()
        tables = ['user', 'submission', 'response']
        for table in tables:
            print('Setting up "' + table + '" table.')
            try:
                table_service.create_table('user')
            except Exception as ex:
                print(ex)

        blob_service_client = get_blob_service_client()
        containers = ['photos', 'artuploadphotos']
        for container in containers:
            print('Setting up "' + container + '" container.')
            try:
                container_client = blob_service_client.create_container(container)
            except Exception as ex:
                print(ex)

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
    
    @app.route('/', methods=['GET'])
    def hello():
        return "Hello!"

    from . import db
    db.init_app(app)

    from . import user
    app.register_blueprint(user.bp)

    from . import submission
    app.register_blueprint(submission.bp)

    from . import response
    app.register_blueprint(response.bp)

    CORS(app)
    return app