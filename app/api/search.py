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
