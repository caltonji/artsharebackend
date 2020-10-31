import os, uuid
from flask import (
    Blueprint, request, abort
)
from flaskr.utils import build_user_id, validate_request_form, validate_user_in_template, validate_submission_in_template
from flaskr.sms_client import send_text
from azure.cosmosdb.table.tableservice import TableService
from flaskr.service_factory import get_table_service

bp = Blueprint('response', __name__)

@bp.route('/response', methods=['PUT'])
def upsert_response():
    validate_request_form(['template_id', 'user_id', 'submission_id', 'text'])
    userId = request.form['user_id']
    templateId = request.form['template_id']
    validate_user_in_template(userId, templateId)
    validate_submission_in_template()

    response_id = request.form['response_id'] if 'response_id' in request.form else str(uuid.uuid1())

    response_to_upload = {
        'PartitionKey': templateId,
        'RowKey': response_id,
        'user_id': userId,
        'submission_id': request.form['submission_id'],
        'text': request.form['text']
    }
    table_service = get_table_service()
    table_service.insert_or_replace_entity('response', response_to_upload)
    
    return convert_table_response_to_json(response_to_upload)

def convert_table_response_to_json(response):
    return {
        'template_id': response['PartitionKey'],
        'response_id': response['RowKey'],
        'user_id': response['user_id'],
        'submission_id': response['submission_id'],
        'text': response['text'],
    }