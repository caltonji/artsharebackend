from flask import Flask, request, flash
app = Flask(__name__)

app.secret_key = b'_5#y2L"F4Qs8z\n\xec]/'

@app.route("/flash")
def do_a_flash():
    flash("Some content")

@app.route('/upload', methods=['POST'])
def upload_file():
    f = request.files['the_file']
    f.save('/var/www/uploads/uploaded_file.txt')

@app.route("/user/", methods=['POST'])
def create_user():
    # create user. Save them, add their ID to the cookie