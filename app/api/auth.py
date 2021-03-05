from flask import current_app, request
from app.db import get_db
import bcrypt
import jwt

from datetime import datetime, timezone, timedelta


def token_required(access=True):
    def wrapper(view):
        def wrapped_view(*args, **kwargs):
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
                check_result = check_token(token)

                if (
                    auth_type == 'Bearer' and
                    check_result['success'] and
                    (
                        (check_result['data']['access'] and access) or
                        (not check_result['data']['access'] and not access)
                    )
                ):
                    return view(
                        check_result['data']['user_id'],
                        *args,
                        **kwargs
                    )
                else:
                    return {
                        'status': 401,
                        'success': False,
                        'error': check_result['error'] or 'Login required',
                        'data': None
                    }

            else:
                return {
                    'status': 401,
                    'success': False,
                    'error': '"Authorization" header required',
                    'data': None
                }

        return wrapped_view
    return wrapper


def check_token(jwt_token, allowExpired=False):
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
            algorithms=['HS256'],
            options={
                'verify_exp': not allowExpired
            }
        )

        user = db.execute(
            'SELECT * FROM user WHERE id = ?',
            (payload['user_id'],)
        ).fetchone()

        if user is None:
            raise jwt.DecodeError

        return {
            'success': True,
            'error': None,
            'data': payload
        }
    except (UnicodeDecodeError, jwt.ExpiredSignatureError, jwt.DecodeError):
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
        user = db.execute(
            'SELECT * FROM user WHERE username = ?',
            (username,)
        ).fetchone()

        if user is None:
            error = 'Login is incorrect'
        else:
            user = dict(user)

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


@token_required(access=False)
def refresh(user_id,):
    now = datetime.now(timezone.utc)
    expires = now + timedelta(minutes=15)
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


def logout(request_data):
    access_token = request_data.get('access_token')
    refresh_token = request_data.get('refresh_token')
    db = get_db()
    error = None

    if access_token is None:
        error = 'Access token is required'
    elif refresh_token is None:
        error = 'Refresh token is required'
    elif not check_token(access_token, allowExpired=True)['success']:
        error = 'Access token is invalid'
    elif not check_token(refresh_token, allowExpired=True)['success']:
        error = 'Refresh token is invalid'

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
