from flask import Blueprint, request, Response
from . import auth, meetings, contacts, search

import json


bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/auth/<action>', methods=('GET', 'POST'))
def auth_endpoint(action):
    if action == 'register' and request.method == 'POST':
        resp_data = auth.register(request.json)
        return response(resp_data)
    if action == 'login' and request.method == 'POST':
        resp_data = auth.login(request.json)
        return response(resp_data)
    if action == 'logout' and request.method == 'POST':
        resp_data = auth.logout(request.json)
        return response(resp_data)
    if action == 'refresh' and request.method == 'GET':
        resp_data = auth.refresh()
        return response(resp_data)
    else:
        return response({
            'status': 400,
            'success': False,
            'error': 'Bad request or method',
            'data': None
        })


@bp.route('/meetings/<action>', methods=('GET', 'POST', 'PUT', 'DELETE'))
def meetings_endpoint(action):
    if action == 'list' and request.method == 'GET':
        resp_data = meetings.list()
        return response(resp_data)
    elif action == 'get' and request.method == 'GET':
        resp_data = meetings.get(request.args)
        return response(resp_data)
    elif action == 'create' and request.method == 'POST':
        resp_data = meetings.create(request.json)
        return response(resp_data)
    elif action == 'update' and request.method == 'PUT':
        resp_data = meetings.update(request.json)
        return response(resp_data)
    elif action == 'delete' and request.method == 'DELETE':
        resp_data = meetings.delete(request.json)
        return response(resp_data)
    else:
        return response({
            'status': 400,
            'success': False,
            'error': 'Bad request or method',
            'data': None
        })


@bp.route('contacts/<action>', methods=('GET', 'POST', 'PUT', 'DELETE'))
def contacts_endpoint(action):
    if action == 'list' and request.method == 'GET':
        resp_data = contacts.list()
        return response(resp_data)
    if action == 'get' and request.method == 'GET':
        resp_data = contacts.get(request.args)
        return response(resp_data)
    elif action == 'create' and request.method == 'POST':
        resp_data = contacts.create(request.json)
        return response(resp_data)
    elif action == 'update' and request.method == 'PUT':
        resp_data = contacts.update(request.json)
        return response(resp_data)
    elif action == 'delete' and request.method == 'DELETE':
        resp_data = contacts.delete(request.json)
        return response(resp_data)
    else:
        return response({
            'status': 400,
            'success': False,
            'error': 'Bad request or method',
            'data': None
        })


@bp.route('search/<action>')
def search_endpoint(action):
    if action == 'contacts':
        resp_data = search.contacts(request.args)
        return response(resp_data)
    else:
        return response({
            'status': 400,
            'success': False,
            'error': 'Bad request or method',
            'data': None
        })


def response(data):
    status = data.pop('status')
    resp = Response(
        json.dumps(data),
        status=status,
        mimetype='application/json'
    )

    return(resp)
