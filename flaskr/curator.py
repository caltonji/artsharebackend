from flask import (
    Blueprint, g, request, session, jsonify
)

from flaskr.db import get_db

bp = Blueprint('curator', __name__)

@bp.route('/curators/me', methods=['GET'])
def getMe():
    error = None
    print(session)
    if not 'user_id' in session:
        error = "Not logged in"
    else:
        userId = session['user_id']
        db = get_db()
        cur = db.cursor()
        curator = cur.execute(
            'SELECT * FROM curator WHERE id = ?', (userId,)
        ).fetchone()
        cur.close()

        if curator is None:
            error = "unknown"
        else:
            return to_json(curator)
    return { 'error' : error }

@bp.route('/curator', methods=['POST'])
def create():
    error = None
    if not request.is_json:
        error = 'json accepted only'
    else:
        content = request.get_json()
        if 'name' not in content:
            error = 'name is required.'
        else:
            name = content['name']

            db = get_db()
            cur = db.cursor()
            cur.execute(
                'INSERT INTO curator (name)'
                ' VALUES (?)',
                (name,)
            )
            createdCuratorId = cur.lastrowid

            error = None
            curator = cur.execute(
                'SELECT * FROM curator WHERE id = ?', (createdCuratorId,)
            ).fetchone()
            db.commit()
            cur.close()
            if curator is None:
                error = 'unknown'
            else:
                session['user_id'] = curator['id']
                print(curator.keys)
                return to_json(curator)
    return { 'error': error }
    
@bp.route('/curators', methods=['GET'])
def get_all():
    db = get_db()
    curators = db.execute(
        'SELECT id, name, created'
        ' FROM curator'
        ' ORDER BY created DESC'
    ).fetchall()
    return jsonify([to_json(curator) for curator in curators])

def to_json(curator_row):
    return {
        'name' : curator_row['name'],
        'id': curator_row['id'],
        'created': curator_row['created']
    }