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
