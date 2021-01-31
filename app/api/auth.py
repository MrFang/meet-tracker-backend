from flask import current_app, request
from app.db import get_db
import bcrypt
import jwt

from datetime import datetime, timezone, timedelta
import functools


def check_token(jwt_token):
    db = get_db()
    tokens = db.execute(
        'SELECT * FROM revoked_token WHERE token = ?',
        (jwt_token,)
    ).fetchall()

    if len(tokens) > 0:
        return {
            'success': False,
            'error': 'Token revoked',
            'data': None
        }

    try:
        payload = jwt.decode(
            jwt_token,
            current_app.config['SECRET_KEY'],
            algorithms=['HS256']
        )

        return {
            'success': True,
            'error': None,
            'data': payload
        }
    except (UnicodeDecodeError, jwt.ExpiredSignatureError):
        return {
            'success': False,
            'error': 'Token invalid',
            'data': None
        }


def register(request_data):
    username = request_data.get('username')
    password = request_data.get('password')
    db = get_db()
    error = None

    if username is None or len(username) == 0:
        error = 'Username is required'
    elif password is None or len(password) == 0:
        error = 'Password is required'
    else:
        user = db.execute(
            'SELECT * FROM user WHERE username = ?',
            (username, )
        ).fetchone()

        if user is not None:
            error = 'User is already registered'

    if error is None:
        db.execute(
            'INSERT INTO user (username, password_hash) ' +
            'VALUES (?, ?)',
            (
                username,
                bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            )
        )
        db.commit()

        return {
            'status': 200,
            'success': True,
            'error': error,
            'data': None
        }
    else:
        return {
            'status': 400,
            'success': False,
            'error': error,
            'data': None
        }


def login(request_data):
    username = request_data.get('username')
    password = request_data.get('password')
    db = get_db()
    error = None

    user = None

    if username is None or len(username) == 0:
        error = 'Username is required'
    elif password is None or len(password) == 0:
        error = 'Password is required'
    else:
        user = dict(db.execute(
            'SELECT * FROM user WHERE username = ?',
            (username,)
        ).fetchone())

        if not bcrypt.checkpw(
            password.encode('utf-8'),
            user['password_hash']
        ):
            error = 'Password is incorrect'

    if error is None:
        now = datetime.now(timezone.utc)
        access_expires = now + timedelta(minutes=15)
        refresh_expires = now + timedelta(days=30)
        secret = current_app.config['SECRET_KEY']

        access_payload = {
            'user_id': user['id'],
            'iat': now.timestamp(),
            'exp': access_expires.timestamp(),
            'access': True
        }

        refresh_payload = {
            'user_id': user['id'],
            'iat': now.timestamp(),
            'exp': refresh_expires.timestamp(),
            'access': False
        }

        return {
            'status': 200,
            'success': True,
            'error': error,
            'data': {
                'access_token': jwt.encode(
                    access_payload,
                    secret,
                    algorithm='HS256'
                ),
                'refresh_token': jwt.encode(
                    refresh_payload,
                    secret,
                    algorithm='HS256'
                )
            }
        }
    else:
        return {
            'status': 400,
            'success': False,
            'error': error,
            'data': None
        }


def refresh(refresh_token):
    check = check_token(refresh_token)

    if check['success'] and not check['data']['access']:
        now = datetime.now(timezone.utc)
        expires = now + timedelta(minutes=15)
        user_id = check['data']['user_id']
        secret = current_app.config['SECRET_KEY']

        payload = {
            'user_id': user_id,
            'iat': now.timestamp(),
            'exp': expires.timestamp(),
            'access': True
        }

        return {
            'status': 200,
            'success': True,
            'error': None,
            'data': {
                'token': jwt.encode(payload, secret, algorithm='HS256')
            }
        }
    else:
        return {
            'status': 400,
            'success': False,
            'error': check['error'] or 'Token invalid',
            'data': None
        }


def logout(request_data):
    access_token = request_data.get('access_token')
    refresh_token = request_data.get('refresh_token')
    db = get_db()
    error = None

    if access_token is None:
        error = 'Access token is required'
    elif refresh_token is None:
        error = 'Refresh token is required'

    if error is None:
        db.execute(
            'INSERT INTO revoked_token (token) ' +
            'VALUES (?), (?)',
            (access_token, refresh_token)
        )
        db.commit()

        return {
            'status': 200,
            'success': True,
            'error': error,
            'data': None
        }
    else:
        return {
            'status': 400,
            'success': False,
            'error': error,
            'data': None
        }


def token_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        header = request.headers.get('Authorization', '')

        if header is not None:
            auth_type, token = '', ''
            try:
                [auth_type, token] = header.split(' ')
            except ValueError:
                return {
                    'status': 401,
                    'success': False,
                    'error': 'Invalid header',
                    'data': None
                }
            check = check_token(token)

            if (
                auth_type == 'Bearer' and
                check['success'] and
                check['data']['access']
            ):
                return view(check['data']['user_id'], **kwargs)
            else:
                return {
                    'status': 401,
                    'success': False,
                    'error': check['error'] or 'Login required',
                    'data': None
                }

        else:
            return {
                'status': 401,
                'success': False,
                'error': '"Authorizaton" header required',
                'data': None
            }

    return wrapped_view
