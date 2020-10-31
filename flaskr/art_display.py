import os, uuid
from flask import (
    Blueprint, g, request, session, jsonify, current_app, url_for
)
from werkzeug.utils import secure_filename
from azure.cosmosdb.table.tableservice import TableService
from azure.cosmosdb.table.models import Entity
from azure.storage.blob import BlobServiceClient, BlobClient, ContainerClient
from flaskr.db import get_db
from twilio.rest import Client

bp = Blueprint('art_display', __name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
PARITION_KEY = "p_key"

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/artdisplays', methods=['GET'])
def getAll():
    # db = get_db()
    # cur = db.cursor()
    # artdisplays = cur.execute(
    #     'SELECT *'
    #     ' FROM artDisplay'
    #     ' ORDER BY created DESC'
    # ).fetchall()
    # cur.close()
    table_service = TableService(account_name='artsharestorage', account_key='zCN3F1TuFjeSw8alIDF0bcvSQoLe5tJHRcavpRKZ31JUUkPuHLtVSqP9WJ3oQU7ty/ZAisWl8CDcFtZHsZ15MQ==')
    artuploads = table_service.query_entities('artuploads', filter="PartitionKey eq '" + PARITION_KEY + "'")
    
    return jsonify([to_json(artupload) for artupload in artuploads])

@bp.route('/artdisplay', methods=['POST'])
def create():
    error = None
    print(request)
    print(request.data)
    print(request.form)
    print(request.files['artPhoto'])
    if 'artPhoto' not in request.files:
        error = 'artPhoto is required.'
    elif request.files["artPhoto"].filename == "":
        error = "filename required"
    elif not allowed_file(request.files["artPhoto"].filename):
        error = "not allowed file"
    elif 'artName' not in request.form:
        error = 'artName is required.'
    elif 'artistName' not in request.form:
        error = 'artistName is required.'
    elif 'curatorName' not in request.form:
        error = 'curatorName is required.'
    elif 'curatorNotes' not in request.form:
        error = 'curatorNotes is required.'
    else:
        newId = str(uuid.uuid1())
        artPhoto = request.files["artPhoto"]
        print(artPhoto)
        fileExtension = artPhoto.filename.rsplit('.', 1)[1]
        filename = secure_filename(newId + "_photo." + fileExtension)
        print(filename)
        # artPhoto.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))

        connect_str = "DefaultEndpointsProtocol=https;AccountName=artsharestorage;AccountKey=zCN3F1TuFjeSw8alIDF0bcvSQoLe5tJHRcavpRKZ31JUUkPuHLtVSqP9WJ3oQU7ty/ZAisWl8CDcFtZHsZ15MQ==;EndpointSuffix=core.windows.net"
        blob_service_client = BlobServiceClient.from_connection_string(connect_str)
        container_name = "artuploadphotos"
        blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
        # print(artPhoto.read())
        # print(artPhoto.stream.read())
        blob_client.upload_blob(artPhoto.stream.read())




        print(blob_client)
        # apiObject.blobUri = "https://" + azureStorageAccountName + ".blob.core.windows.net/" + exports.blobContainer + "/" + apiObject.id + "." + fileExtension;
        print(blob_client.get_blob_properties())
        photoUrl = blob_client.url
        print(photoUrl)
        artName = request.form["artName"]
        print(artName)
        artistName = request.form["artistName"]
        print(artistName)
        curatorName = request.form["curatorName"]
        print(curatorName)
        curatorNotes = request.form["curatorNotes"]
        print(curatorNotes)
        
        table_service = TableService(account_name='artsharestorage', account_key='zCN3F1TuFjeSw8alIDF0bcvSQoLe5tJHRcavpRKZ31JUUkPuHLtVSqP9WJ3oQU7ty/ZAisWl8CDcFtZHsZ15MQ==')
        artupload = {
            'PartitionKey': PARITION_KEY,
            'RowKey': newId,
            'artName': artName,
            'artistName': artistName,
            'curatorName': curatorName,
            'curatorNotes': curatorNotes,
            'photoUrl': photoUrl
        }
        table_service.insert_entity('artuploads', artupload)

        # Your Account SID from twilio.com/console
        account_sid = "ACce268cc948742f9dcec8827d91f45965"
        # Your Auth Token from twilio.com/console
        auth_token  = "1d407a9350de8d6260cfb5ea64969299"

        client = Client(account_sid, auth_token)

        message = "New photo uploaded: " + photoUrl
        message = client.messages.create(
            to="+12245672736", 
            from_="+19382010795",
            body=message)
        
        # db = get_db()
        # cur = db.cursor()
        # cur.execute(
        #         'INSERT INTO artDisplay (upload_name, art_name, artist_name, curator_name, curator_notes)'
        #         ' VALUES (?,?,?,?,?)',
        #         (filename,artName,artistName,curatorName,curatorNotes,)
        #     )
        # createdId = cur.lastrowid
        
        # error = None
        # artDisplay = cur.execute(
        #     'SELECT * FROM artDisplay WHERE id = ?', (createdId,)
        # ).fetchone()
        # db.commit()
        # cur.close()
        if artupload is None:
            error = 'unknown'
        else:
            return to_json(artupload)
    return { 'error' : error }

def to_json(art_display_row):
    return {
        'art_url' : art_display_row['photoUrl'],
        'art_name' : art_display_row['artName'],
        'artist_name' : art_display_row['artistName'],
        'curator_name' : art_display_row['curatorName'],
        'curator_notes' : art_display_row['curatorNotes']
    }
