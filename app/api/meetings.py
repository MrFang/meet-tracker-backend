from app.db import get_db
from app.api.auth import token_required

import datetime

# TODO: Error handling, contacts in meeting update


@token_required()
def create(user_id, request_data):
    title = request_data.get('title')
    datetime_string = request_data.get('datetime')
    contacts = request_data.get('contacts')
    db = get_db()
    error = None

    if title is None or len(title) == 0:
        error = 'Title is required'
    elif datetime_string is None:
        error = 'Date and time is reqired'
    elif contacts is None:
        error = 'Contacts must be an array'
    else:
        try:
            datetime.datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M')
        except ValueError:
            error = 'Datetime string is invalid'

    if error is None:
        db.execute(
            'INSERT INTO meeting (title, datetime, user_id) VALUES (?, ?, ?)',
            (title, datetime_string, user_id)
        )

        meeting_id = db.execute(
            'SELECT MAX(id) AS id FROM meeting WHERE user_id = ?',
            (user_id,)
        ).fetchone()['id']

        for contact in contacts:
            db.execute(
                'INSERT INTO meetings_to_contacts (meeting_id, contact_id) '
                'VALUES (?, ?)',
                (meeting_id, contact['id'])
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
def list(user_id):
    db = get_db()
    meetings = db.execute(
        'SELECT * FROM meeting WHERE user_id = ?',
        (user_id, )
    ).fetchall()
    data = [dict(meeting) for meeting in meetings]
    for idx, meeting in enumerate(data):
        contacts = db.execute(
            'SELECT contact.id, contact.first_name, contact.second_name '
            'FROM contact, meetings_to_contacts AS map '
            'WHERE contact.user_id = ? AND map.meeting_id = ?',
            (user_id, meeting['id'])
        ).fetchall()
        data[idx]['contacts'] = [dict(contact) for contact in contacts]
    return {
        'status': 200,
        'success': True,
        'error': None,
        'data': data
    }


@token_required()
def get(user_id, request_data):
    id = request_data.get('id')
    db = get_db()
    error = None
    meeting = None

    if id is None:
        error = 'Meeting ID is required'
    else:
        meeting = db.execute(
            'SELECT * FROM meeting WHERE id = ? AND user_id = ?',
            (id, user_id)
        ).fetchone()

        if meeting is None:
            error = 'There is no meeting with such ID'

    if error is None:
        return {
            'status': 200,
            'success': True,
            'error': error,
            'data': dict(meeting)
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
        error = 'Meeting ID is required'

    if error is None:
        meeting = db.execute(
            'SELECT * FROM meeting WHERE id = ? AND user_id = ?',
            (id, user_id)
        ).fetchone()

        if meeting is None:
            error = 'There is no meeting with such ID'

    if error is None:
        db.execute(
            'DELETE FROM meeting WHERE id = ? AND user_id = ?',
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
    title = request_data.get('title')
    datetime_string = request_data.get('datetime')
    db = get_db()
    error = None

    if id is None:
        error = 'Meeting ID is required'
    elif title is None:
        error = 'Title is required'
    elif datetime_string is None:
        error = 'Datetime is required'
    else:
        try:
            datetime.datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M')
        except ValueError:
            error = 'Datetime string is invalid'

    if error is None:
        meeting = db.execute(
            'SELECT * FROM meeting WHERE id = ? AND user_id = ?',
            (id, user_id)
        ).fetchone()

        if meeting is None:
            error = 'There is no meeting with such ID'

    if error is None:
        db.execute(
            'UPDATE meeting SET ' +
            'title = ?, ' +
            'datetime = ? ' +
            'WHERE id = ? ' +
            'AND user_id = ?',
            (title, datetime_string, id, user_id)
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
