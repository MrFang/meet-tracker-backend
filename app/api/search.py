from app.db import get_db
from app.api.auth import token_required


@token_required()
def contacts(user_id, request_data):
    query = request_data.get('q')
    db = get_db()
    error = None

    if query is None:
        error = 'Query is required'

    if error is None:
        contacts = db.execute(
            'SELECT * FROM contact ' +
            'WHERE (first_name || \' \' || IFNULL(second_name, \'\')) ' +
            'LIKE (\'%\' || ? || \'%\') ' +
            'AND user_id = ?',
            (query, user_id)
        ).fetchall()

        return {
            'status': 200,
            'success': True,
            'error': error,
            'data': [dict(contact) for contact in contacts]
        }
    else:
        return {
            'status': 400,
            'success': False,
            'error': error,
            'data': None
        }


@token_required()
def meetings(user_id, request_data):
    query = request_data.get('q')
    db = get_db()
    error = None

    if query is None:
        error = 'Query is required'

    if error is None:
        meetings = db.execute(
            'SELECT * FROM meeting ' +
            'WHERE title ' +
            'LIKE (\'%\' || ? || \'%\') ' +
            'AND user_id = ?',
            (query, user_id)
        ).fetchall()

        data = [dict(meeting) for meeting in meetings]

        return {
            'status': 200,
            'success': True,
            'error': error,
            'data': data,
        }
    else:
        return {
            'status': 400,
            'success': False,
            'error': error,
            'data': None
        }
