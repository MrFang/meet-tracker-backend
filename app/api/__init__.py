from flask import Blueprint, request, jsonify, Response
from . import meetings

import json


bp = Blueprint('api', __name__, url_prefix='/api')

@bp.route('/meetings/<action>', methods=('GET', 'POST', 'PUT', 'DELETE'))
def meetings_endpoint(action):
    if action == 'list' and request.method == 'GET':
        resp_data = meetings.list()
        return response(resp_data)
    elif action == 'create' and request.method == 'POST':
        resp_data = meetings.create(request.json)
        return response(resp_data)
    else:
        return response({ 'success': False, 'error': 'Bad request or method', 'data': None })


def response(data):
    if data['success']:
        return jsonify(data)
    else:
        return Response(json.dumps(data), status=400, mimetype='application/json')
