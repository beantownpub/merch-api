import logging
import os
import time
import jwt
import psycopg2
from flask import jsonify, request
from flask_httpauth import HTTPBasicAuth
from flask_restful import Resource
from werkzeug.security import generate_password_hash, check_password_hash

app_log = logging.getLogger()

if __name__ != '__main__':
    gunicorn_logger = logging.getLogger('gunicorn.error')
    app_log.handlers = gunicorn_logger.handlers
    app_log.setLevel('INFO')

SECRET_KEY = os.environ.get('AUTH_API_KEY')

auth = HTTPBasicAuth()


def connect_to_db():
    db = os.environ.get("AUTH_DB")
    db_user = os.environ.get("AUTH_DB_USER")
    db_pw = os.environ.get("AUTH_DB_PW")
    db_host = os.environ.get("AUTH_DB_HOST", "172.17.0.6")
    db_port = os.environ.get("AUTH_DB_PORT", "5432")
    conn = psycopg2.connect(
        database=db,
        user=db_user,
        password=db_pw,
        host=db_host,
        port=db_port
    )
    return conn


def generate_auth_token(account_id, expires_in=600):
    expiration = time.time() + expires_in
    return jwt.encode(
        {'id': account_id, 'exp': expiration},
        SECRET_KEY, algorithm='HS256')


@auth.verify_password
def verfify_password(username, password):
    account = get_account(username)
    if account:
        _id, user, password_hash = account
        if check_password_hash(password_hash, password):
            return True
    return False


def authenticate(username, password):
    account = get_account(username)
    if account:
        _id, user, password_hash = account
        if check_password_hash(password_hash, password):
            return account


def get_account(user):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT * FROM accounts WHERE username=%s", (user,))
    account = cur.fetchone()
    conn.close()
    if account:
        _id, user, password = account
        return _id, user, generate_password_hash(password)


class AuthAPI(Resource):
    @auth.login_required
    def get(self):
        logging.info(request.authorization)
        return jsonify({'hello': 'world'})

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        except Exception:
            return
        return data['id']


def main():
    user = authenticate('jal', 'wtfasshole')
    _id, _, _ = user
    token = generate_auth_token(_id)
    print(token)


if __name__ == '__main__':
    main()
