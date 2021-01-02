from flask import Blueprint, request, jsonify, Response
from . import meetings

import json


bp = Blueprint('api', __name__, url_prefix='/api')


@bp.route('/meetings', defaults={'action': 'list'})
@bp.route('/meetings/<action>', methods=('GET', 'POST', 'PUT', 'DELETE'))
def meetings_endpoint(action):
    if request.method == 'POST' and action == 'create':
        resp_data = meetings.create(request.json)

        if resp_data['success']:
            return jsonify(resp_data)
        else:
            return Response(json.dumps(resp_data), status=400, mimetype='application/json')
