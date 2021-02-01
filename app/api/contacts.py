from app.db import get_db
from app.api.auth import token_required


@token_required()
def list(user_id):
    db = get_db()
    contacts = db.execute(
        'SELECT * FROM contact WHERE user_id = ?',
        (user_id,)
    ).fetchall()
    return {
        'status': 200,
        'success': True,
        'error': None,
        'data': [dict(contact) for contact in contacts]
    }


@token_required()
def create(user_id, request_data):
    first_name = request_data.get('first_name')
    second_name = request_data.get('second_name')
    telephone = request_data.get('telephone')
    db = get_db()
    error = None

    if first_name is None:
        error = 'First name is required'

    if error is None:
        db.execute(
            'INSERT INTO contact ' +
            '(first_name, second_name, telephone, user_id) ' +
            'VALUES (?, ?, ?, ?)',
            (first_name, second_name, telephone, user_id)
        )
        db.commit()

        return {
            'status': 200,
            'success': True,
            'error': error,
            'data': None
        }
    else:
        return {
            'status': 400,
            'success': False,
            'error': error,
            'data': None
        }


@token_required()
def get(user_id, request_data):
    id = request_data.get('id')
    db = get_db()
    error = None
    contact = None

    if id is None:
        error = 'Contact ID is required'
    else:
        contact = db.execute(
            'SELECT * FROM contact WHERE id = ? AND user_id = ?',
            (id, user_id)
        ).fetchone()

        if contact is None:
            error = 'No contact with such ID'

    if error is None:
        return {
            'status': 200,
            'success': True,
            'error': error,
            'data': dict(contact)
        }
    else:
        return {
            'status': 400,
            'success': False,
            'error': error,
            'data': None
        }


@token_required()
def delete(user_id, request_data):
    id = request_data.get('id')
    db = get_db()
    error = None

    if id is None:
        error = 'Contact ID is required'
    else:
        contact = db.execute(
            'SELECT * FROM contact WHERE id = ? AND user_id = ?',
            (id, user_id)
        ).fetchone()

        if contact is None:
            error = 'There is no contact with such ID'

    if error is None:
        db.execute(
            'DELETE FROM contact WHERE id = ? AND user_id = ?',
            (id, user_id)
        )
        db.commit()

        return {
            'status': 200,
            'success': True,
            'error': error,
            'data': None
        }
    else:
        return {
            'status': 400,
            'success': False,
            'error': error,
            'data': None
        }


@token_required()
def update(user_id, request_data):
    id = request_data.get('id')
    first_name = request_data.get('first_name')
    second_name = request_data.get('second_name')
    telephone = request_data.get('telephone')
    db = get_db()
    error = None

    if id is None:
        error = 'Contact ID is required'
    elif first_name is None or len(first_name) == 0:
        error = 'First name is required'
    else:
        contact = db.execute(
            'SELECT * FROM contact WHERE id = ? AND user_id = ?',
            (id, user_id)
        ).fetchone()

        if contact is None:
            error = 'There is no contact with such ID'

    if error is None:
        db.execute(
            'UPDATE contact SET ' +
            'first_name = ?, ' +
            'second_name = ?, ' +
            'telephone = ? ' +
            'WHERE id = ? ' +
            'AND user_id = ?',
            (first_name, second_name, telephone, id, user_id)
        )
        db.commit()

        return {
            'status': 200,
            'success': True,
            'error': error,
            'data': None
        }
    else:
        return {
            'status': 400,
            'success': False,
            'error': error,
            'data': None
        }
