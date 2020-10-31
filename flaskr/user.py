import os, uuid, sys
from flask import (
    Blueprint, request, abort
)
from flaskr.utils import build_user_id, validate_request_form, validate_request_args, build_login_link
from flaskr.sms_client import send_text
from azure.cosmosdb.table.tableservice import TableService
from flaskr.service_factory import get_table_service

bp = Blueprint('user', __name__)

@bp.route('/user', methods=['POST'])
def create_user():
    validate_request_form(['name', 'phone_number', 'template_id'])
    userToUpload = {
        'PartitionKey': request.form['template_id'],
        'RowKey': build_user_id(4),
        'name': request.form['name'],
        'phone_number': request.form['phone_number'],
    }
    table_service = get_table_service()
    table_service.insert_entity('user', userToUpload)

    message = "Hey, " + userToUpload['name'] + "! Thanks for getting going on Chris's caption competition.  If you need to finish uploading your photo or captioning later, use your personal login link: " + build_login_link(userToUpload["RowKey"])
    print("a.sending text to: " + userToUpload["phone_number"], file=sys.stderr)
    print("a.sending text to: " + userToUpload["phone_number"])
    send_text(userToUpload["phone_number"], message)
    return convert_table_user_to_json(userToUpload)

@bp.route('/user', methods=["GET"])
def get_user_by_id():
    validate_request_args(['template_id', 'user_id'])
    table_service = get_table_service()
    user = table_service.get_entity('user', request.args['template_id'], request.args['user_id'])
    return convert_table_user_to_json(user)

def convert_table_user_to_json(user):
    return {
        'template_id': user['PartitionKey'],
        'user_id': user['RowKey'],
        'name': user['name'],
        'phone_number': user['phone_number'],
    }

def convert_table_user_to_short_json(user):
    return {
        'template_id': user['PartitionKey'],
        'user_id': user['RowKey'],
        'name': user['name']
    }