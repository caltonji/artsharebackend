import os
from flask import (
    Blueprint, g, request, session, jsonify, current_app, url_for
)
from werkzeug.utils import secure_filename

from flaskr.db import get_db

bp = Blueprint('art_display', __name__)

ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@bp.route('/artdisplays', methods=['GET'])
def getAll():
    db = get_db()
    cur = db.cursor()
    artdisplays = cur.execute(
        'SELECT *'
        ' FROM artDisplay'
        ' ORDER BY created DESC'
    ).fetchall()
    cur.close()
    
    return jsonify([to_json(artdisplay) for artdisplay in artdisplays])

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
        artPhoto = request.files["artPhoto"]
        print(artPhoto)
        filename = secure_filename(artPhoto.filename)
        print(filename)
        artPhoto.save(os.path.join(current_app.config['UPLOAD_FOLDER'], filename))
        photoUrl = url_for('uploaded_file', filename=filename, _external=True)
        print(photoUrl)
        artName = request.form["artName"]
        print(artName)
        artistName = request.form["artistName"]
        print(artistName)
        curatorName = request.form["curatorName"]
        print(curatorName)
        curatorNotes = request.form["curatorNotes"]
        print(curatorNotes)
        
        db = get_db()
        cur = db.cursor()
        cur.execute(
                'INSERT INTO artDisplay (upload_name, art_name, artist_name, curator_name, curator_notes)'
                ' VALUES (?,?,?,?,?)',
                (filename,artName,artistName,curatorName,curatorNotes,)
            )
        createdId = cur.lastrowid
        
        error = None
        artDisplay = cur.execute(
            'SELECT * FROM artDisplay WHERE id = ?', (createdId,)
        ).fetchone()
        db.commit()
        cur.close()
        if artDisplay is None:
            error = 'unknown'
        else:
            return to_json(artDisplay)
    return { 'error' : error }

def to_json(art_display_row):
    return {
        'id': art_display_row['id'],
        'created': art_display_row['created'],
        'art_url' : url_for('uploaded_file', filename=art_display_row['upload_name'], _external=True),
        'art_name' : art_display_row['art_name'],
        'artist_name' : art_display_row['artist_name'],
        'curator_name' : art_display_row['curator_name'],
        'curator_notes' : art_display_row['curator_notes']
    }
