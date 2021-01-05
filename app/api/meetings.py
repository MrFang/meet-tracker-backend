from os import error
from app.db import get_db

import datetime


def create(data):
    title = data.get('title')
    datetime_string = data.get('datetime')
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