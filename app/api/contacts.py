from os import error
from app.db import get_db

def list():
    db = get_db()
    contacts = db.execute('SELECT * FROM contact').fetchall()
    return {
        'success': True,
        'error': None,
        'data': [dict(contact) for contact in contacts]
    }

def create(request_data):
    first_name = request_data.get('first_name')
    second_name = request_data.get('second_name')
    telephone = request_data.get('telephone')
    db = get_db()
    error = None

    if first_name is None:
        error = 'First name is required'

    if error is None:
        db.execute(
            'INSERT INTO contact (first_name, second_name, telephone) VALUES (?, ?, ?)',
            (first_name, second_name, telephone)
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


def get(request_data):
    id = request_data.get('id')
    db = get_db()
    error = None
    contact = None

    if id is None:
        error = 'Contact ID is required'
    else:
        contact = db.execute('SELECT * FROM contact WHERE id = ?', (id,)).fetchone()
        
        if contact is None:
            error = 'No contact with such ID'
    
    if error is None:
        return {
            'success': True,
            'error': error,
            'data': dict(contact)
        }
    else:
        return {
            'success': False,
            'error': error,
            'data': None
        }
