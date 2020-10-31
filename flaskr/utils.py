import os, random
from flask import request, abort
from azure.cosmosdb.table.tableservice import TableService

def validate_request_args(requiredFields):
    for field in requiredFields:
        if field not in request.args:
            abort(400, description=field + " is a required field")

def validate_request_form(requiredFields):
    for field in requiredFields:
        if field not in request.form:
            abort(400, description=field + " is a required field")

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def validate_request_form_photo():
    if 'photo' not in request.files:
        abort(400, description="photo required in files")
    elif not allowed_file(request.files['photo'].filename):
        abort(400, description="Not an allowed filetype")

def validate_user_in_template(userId, templateId):
    table_service = TableService(connection_string=os.environ['AZURE_STORAGE_CONNECTION_STRING'])
    try:
        table_service.get_entity('user', templateId, userId)
    except:
        abort(403, description="user_id not found in template_id")

def validate_submission_in_template():
    templateId = request.form['template_id']
    submissionId = request.form['submission_id']
    table_service = TableService(connection_string=os.environ['AZURE_STORAGE_CONNECTION_STRING'])
    try:
        table_service.get_entity('submission', templateId, submissionId)
    except:
        abort(400, description="submission_id not found in template_id")

def build_user_id(size):
    validChars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    validCharsList = [char for char in validChars]
    userId = ""
    for i in range(0, size):
        userId += random.choice(validCharsList)
    return userId

def build_login_link(userId):
    return os.environ['CLIENT_BASE_URI'] + "/" + userId