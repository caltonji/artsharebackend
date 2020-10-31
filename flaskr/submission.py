import os, uuid
from flask import (
    Blueprint, request, abort, jsonify
)
from flaskr.utils import (
    build_user_id,
    validate_request_form,
    validate_request_form_photo,
    validate_user_in_template,
    validate_request_args,
    build_login_link
)
from flaskr.sms_client import send_text

from werkzeug.utils import secure_filename
from azure.storage.blob import BlobServiceClient, BlobClient
from flaskr.response import convert_table_response_to_json
from flaskr.user import convert_table_user_to_short_json, convert_table_user_to_json
from flaskr.service_factory import get_table_service, get_blob_service_client

bp = Blueprint('submission', __name__)

@bp.route('/submission', methods=['PUT'])
def upsert_submission():
    validate_request_form(['template_id', 'user_id'])
    validate_request_form_photo()
    validate_user_in_template(request.form['user_id'], request.form['template_id'])

    # get submission id and check if upsert
    upsert = False
    submission_id = request.form['submission_id'] if 'submission_id' in request.form else str(uuid.uuid1())
    photo_url = upload_photo()

    submission_to_upload = {
        'PartitionKey': request.form['template_id'],
        'RowKey': submission_id,
        'user_id': request.form['user_id'],
        'photo_url': photo_url
    }
    table_service = get_table_service()
    table_service.insert_or_replace_entity('submission', submission_to_upload)
    text_others(request.form['user_id'], request.form['template_id'])

    return convert_table_submission_to_json(submission_to_upload)

@bp.route('/submissions', methods=["GET"])
def get_submissions():
    validate_request_args(['template_id', 'user_id'])
    userId = request.args['user_id']
    templateId = request.args['template_id']
    validate_user_in_template(userId, templateId)

    table_service = get_table_service()
    submissions = table_service.query_entities(
        'submission', filter="PartitionKey eq '" + templateId + "'")
    submissions = [convert_table_submission_to_json(submission) for submission in submissions]

    responses = table_service.query_entities(
        'response', filter="PartitionKey eq '" + templateId + "'")
    responses = [convert_table_response_to_json(response) for response in responses]

    users = table_service.query_entities(
        'user', filter="PartitionKey eq '" + templateId + "'")
    users = [convert_table_user_to_short_json(user) for user in users]
    
    for response in responses:
        # raises StopIteration.  Letting it because I don't expect this to happen
        user = next(user for user in users if user['user_id'] == response['user_id'])
        response['user'] = user

    for submission in submissions:
        submissionResponses = [response for response in responses if response['submission_id'] == submission['submission_id']]
        submission['responses'] = submissionResponses

        user = next(user for user in users if user['user_id'] == submission['user_id'])
        submission['user'] = user
    return jsonify(submissions)

def upload_photo():
    # Get photo and filename
    photoFile = request.files["photo"]
    fileExtension = photoFile.filename.rsplit('.', 1)[1]
    filename = secure_filename(str(uuid.uuid1()) + "." + fileExtension)

    # Get blob client
    blob_service_client = get_blob_service_client()
    container_name = "photos"
    blob_client = blob_service_client.get_blob_client(container=container_name, blob=filename)
    blob_client.upload_blob(photoFile.stream.read())
    
    return blob_client.url

def text_others(userId, templateId):
    table_service = get_table_service()
    users = table_service.query_entities(
        'user', filter="PartitionKey eq '" + templateId + "'")
    users = [convert_table_user_to_json(user) for user in users]
    othersUsers = [user for user in users if user['user_id'] != userId]
    user = next(user for user in users if user['user_id'] == userId)
    for otherUser in othersUsers:
        message = "New submission from " + user['name'] + ".  Use your login link to check it out: " + build_login_link(otherUser['user_id'])
        send_text(otherUser['phone_number'], message)

def convert_table_submission_to_json(submission):
    return {
        'template_id': submission['PartitionKey'],
        'submission_id': submission['RowKey'],
        'user_id': submission['user_id'],
        'photo_url': submission['photo_url']
    }