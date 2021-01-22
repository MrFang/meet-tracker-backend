from app.db import get_db


def contacts(request_data):
    query = request_data.get('q')
    db = get_db()
    error = None

    if query is None:
        error = 'Query is required'

    if error is None:
        contacts = db.execute(
            'SELECT * FROM contact ' +
            'WHERE (first_name || \' \' || IFNULL(second_name, \'\')) ' +
            'LIKE (? || \'%\')',
            (query,)
        ).fetchall()

        return {
            'success': True,
            'error': error,
            'data': [dict(contact) for contact in contacts]
        }
    else:
        return {
            'success': False,
            'error': error,
            'data': None
        }
