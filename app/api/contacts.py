from app.db import get_db

def list():
    db = get_db()
    contacts = db.execute('SELECT * FROM contact').fetchall()
    return {
        'success': True,
        'error': None,
        'data': [dict(contact) for contact in contacts]
    }