from os import error
from app.db import get_db

import datetime


def create(request_data):
    title = request_data.get('title')
    datetime_string = request_data.get('datetime')
    db = get_db()
    error = None

    if title is None:
        error = 'Title is required'
    elif datetime_string is None:
        error = 'Date and time is reqired'
    else:    
        try:
            datetime.datetime.strptime(datetime_string, '%Y-%m-%dT%H:%M')
        except ValueError:
            error = 'Datetime string is invalid'
    
    if error is None:
        db.execute(
            'INSERT INTO meeting (title, datetime) VALUES (?, ?)',
            (title, datetime_string)
        )
        db.commit()
        
        return {'success': True, 'error': error, 'data': None}
    else:
        return {'success': False, 'error': error, 'data': None}


def list():
    db = get_db()
    meetings = db.execute('SELECT * FROM meeting').fetchall()
    return {
        'success': True,
        'error': None,
        'data': [dict(meeting) for meeting in meetings]
    }


def get_meeting(request_data):
    id = request_data.get('id')
    db = get_db()
    error = None
    meeting = None

    if id is None:
        error = 'Meeting ID is required'
    
    if error is None:
        meeting = db.execute('SELECT * FROM meeting WHERE id = ?', (id,)).fetchone()
        
        if meeting is None:
            error = 'There is no meeting with such ID'
    
    if error is None:
        return {
            'success': True,
            'error': error,
            'data': dict(meeting)
        }
    else:
        return {
            'success': False,
            'error': error,
            'data': None
        }


def delete(request_data):
    id = request_data.get('id')
    db = get_db()
    error = None

    if id is None:
        error = 'Meeting ID is required'
    
    if error is None:
        meeting = db.execute('SELECT * FROM meeting WHERE id = ?', (id,)).fetchone()

        if meeting is None:
            error = 'There is no meeting with such ID'
    
    if error is None:
        db.execute('DELETE FROM meeting WHERE id = ?', (id,))
        db.commit()

        return {
            'success': True,
            'error': error,
            'data': None
        }
    else:
        return {
            'success': False,
            'error': error,
            'data': None
        }


def update(request_data):
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
        meeting = db.execute('SELECT * FROM meeting WHERE id = ?', (id,)).fetchone()

        if meeting is None:
            error = 'There is no meeting with such ID'
    
    if error is None:
        db.execute(
            'UPDATE meeting SET ' +
            'title = ?, ' +
            'datetime = ? ' +
            'WHERE id = ?',
            (title, datetime_string, id)
        )
        db.commit()

        return {
            'success': True,
            'error': error,
            'data': None
        }
    else: 
        return {
            'success': False,
            'error': error,
            'data': None
        }

