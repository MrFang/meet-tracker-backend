from app.api.contacts import check_contact
from app.db import get_db
from app.api.auth import token_required

import datetime


def check_meeting(user_id, request_data):
    id = request_data.get('id')
    title = request_data.get('title')
    start_datetime_string = request_data.get('start_datetime')
    contacts = request_data.get('contacts')
    end_datetime_string = request_data.get('end_datetime')
    error = None
    db = get_db()

    if title is None or len(title) == 0:
        error = 'Title is required'
    elif start_datetime_string is None:
        error = 'Date and time is reqired'
    elif end_datetime_string is None:
        error = 'Date and time is reqired'
    elif contacts is None:
        error = 'Contacts must be an array'
    else:
        try:
            datetime.datetime.strptime(start_datetime_string, '%Y-%m-%dT%H:%M')
            datetime.datetime.strptime(end_datetime_string, '%Y-%m-%dT%H:%M')
        except ValueError:
            error = 'Datetime string is invalid'

    if error is None:
        meetings = db.execute(
            'SELECT id FROM meeting '
            'WHERE user_id = ? '
            'AND id != ? '
            'AND ('
            '(datetime(start_datetime) BETWEEN datetime(?) AND datetime(?)) '
            'OR (datetime(end_datetime) BETWEEN datetime(?) AND datetime(?))'
            ')',
            (
                user_id,
                id,
                start_datetime_string,
                end_datetime_string,
                start_datetime_string,
                end_datetime_string
            )
        ).fetchall()

        if len(meetings) > 0:
            error = 'Meetings cannot collapse'

    if error is None:
        for contact in contacts:
            contact_error = check_contact(contact)
            if contact_error is not None:
                error = 'Error: ' \
                    + contact_error + ' on contact: ' + str(contact)

    return error


@token_required()
def create(user_id, request_data):
    title = request_data.get('title')
    start_datetime_string = request_data.get('start_datetime')
    contacts = request_data.get('contacts')
    end_datetime_string = request_data.get('end_datetime')
    db = get_db()
    error = check_meeting(user_id, request_data)

    if error is None:
        db.execute(
            'INSERT INTO meeting '
            '(title, start_datetime, end_datetime, user_id) '
            'VALUES (?, ?, ?, ?)',
            (title, start_datetime_string, end_datetime_string, user_id)
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
def list(user_id, request_data):
    db = get_db()
    start_date_string = '0000-01-01'
    end_date_string = '9999-12-31'

    if request_data is not None:
        start_date_string = request_data.get('start_date', '0000-01-01')
        end_date_string = request_data.get('end_date', '9999-12-31')

    meetings = db.execute(
        'SELECT id, title, start_datetime, end_datetime FROM meeting '
        'WHERE user_id = ? '
        'AND datetime(start_datetime) BETWEEN datetime(?) AND datetime (?)',
        (user_id, start_date_string + 'T00:00', end_date_string + 'T23:59')
    ).fetchall()

    data = [dict(meeting) for meeting in meetings]

    for idx, meeting in enumerate(data):
        contacts = db.execute(
            'SELECT '
            'contact.id, '
            'contact.first_name, '
            'contact.second_name, '
            'contact.telephone '
            'FROM contact '
            'JOIN meetings_to_contacts AS map ON map.contact_id = contact.id '
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
        contacts = db.execute(
            'SELECT '
            'contact.id, '
            'contact.first_name, '
            'contact.second_name, '
            'contact.telephone '
            'FROM contact '
            'JOIN meetings_to_contacts AS map ON map.contact_id = contact.id '
            'WHERE contact.user_id = ? AND map.meeting_id = ?',
            (user_id, id)
        ).fetchall()

        data = dict(meeting)
        data['contacts'] = []

        for contact in contacts:
            data['contacts'].append(dict(contact))

        return {
            'status': 200,
            'success': True,
            'error': error,
            'data': data
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
        db.execute(
            'DELETE FROM meetings_to_contacts WHERE meeting_id = ?',
            (id,)
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
    start_datetime_string = request_data.get('start_datetime')
    contacts = request_data.get('contacts')
    end_datetime_string = request_data.get('end_datetime')
    db = get_db()
    error = None

    if id is None:
        error = 'Meeting ID is required'
    else:
        error = check_meeting(user_id, request_data)

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
            'start_datetime = ?, ' +
            'end_datetime = ? ' +
            'WHERE id = ? ' +
            'AND user_id = ?',
            (title, start_datetime_string, end_datetime_string, id, user_id)
        )
        existing_contacts_ids = db.execute(
            'SELECT contact.id '
            'FROM contact '
            'JOIN meetings_to_contacts AS map ON contact.id = map.contact_id '
            'WHERE contact.user_id = ? AND map.meeting_id = ?',
            (user_id, id)
        ).fetchall()

        existing_contacts_ids = set(
            [dict(contact_id)['id'] for contact_id in existing_contacts_ids]
        )
        new_contact_ids = set(map(lambda contact: contact['id'], contacts))

        for contact_id in existing_contacts_ids.difference(new_contact_ids):
            db.execute(
                'DELETE from meetings_to_contacts '
                'WHERE meeting_id = ? AND contact_id = ?',
                (id, contact_id)
            )

        for contact_id in new_contact_ids.difference(existing_contacts_ids):
            db.execute(
                'INSERT INTO meetings_to_contacts (meeting_id, contact_id) '
                'VALUES (?, ?)',
                (id, contact_id)
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
