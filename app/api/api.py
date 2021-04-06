from flask import Flask
from flask import request, jsonify, abort, url_for, g
import threading
import random
import time
import sys

# auth:
from itsdangerous import (TimedJSONWebSignatureSerializer
                          as Serializer, BadSignature, SignatureExpired)
from passlib.apps import custom_app_context as pwd_context
from flask_httpauth import HTTPBasicAuth
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import jwt

sys.path.append('/opt/app/flask-react/app/api')
from olxjj import OLXJJ

app = Flask(__name__, static_folder='../build', static_url_path='/') # so can server static from react folder
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///./database.db'
app.config['SECRET_KEY'] = 'adfjiodf#$%^&*(#v8923rhwef8suv98^H52h3209sfvdhfvjq393$^&^GYIj390'
db = SQLAlchemy(app)
auth = HTTPBasicAuth()
olx_threads = {}


class User(db.Model):
    
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key = True)
    username = db.Column(db.String(32), index = True)
    email = db.Column(db.String(255), nullable=True, unique=True)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def generate_auth_token(self, expires_in=600):
        return jwt.encode(
            {'id': self.id, 'exp': time.time() + expires_in},
            app.config['SECRET_KEY'], algorithm='HS256')

    @staticmethod
    def verify_auth_token(token):
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'],
                              algorithms=['HS256'])
        except:
            return
        return User.query.get(data['id'])


class OlxThread(threading.Thread):
    def __init__(self, url, ignore_list):
        self.progress = 0
        self._return = None
        self.olx = OLXJJ(url)
        self.ignore_list = ignore_list
        super().__init__()

    def run(self):
        self._return =  self.olx.get_all_prices(self.ignore_list)

    def join(self):
        threading.Thread.join(self)
        return self._return


@app.route('/api/time')
def get_current_time():
    return {'time': f'{int(time.time())}'}

@app.route('/api/olxresult/', methods = ['POST'])
@auth.login_required
def olx():
    global olx_threads
    thread_id = request.json.get('id')
    olxjj_result_dict = olx_threads[thread_id].join()
    olx_threads.pop(thread_id, None)
    return olxjj_result_dict

@app.route('/api/olx_get_id/', methods = ['POST'])
@auth.login_required
def olx_id():
    global olx_threads
    url = request.json.get('url')
    ignore_list = request.json.get('ignore_list').split()
    thread_id = random.randint(1, 100)
    while(olx_threads.get(thread_id)):
        thread_id = random.randint(1, 100)
    olx_threads[thread_id] = OlxThread(url, ignore_list)
    olx_threads[thread_id].start()
    return {'id': thread_id}

@app.route('/api/progress/<int:thread_id>', methods = ['GET'])
@auth.login_required
def progress(thread_id):
    global olx_threads
    if not thread_id:
        return {'progress': 0}
    olx_thread_obj = olx_threads.get(thread_id)
    progress = str(olx_thread_obj.olx.percent_progress) if olx_thread_obj else '100'  # 100 if thread was already removed
    return {'progress': progress}

@app.route('/api/users', methods = ['POST'])
def new_user():
    username = request.json.get('username')
    email = request.json.get('email')
    password = request.json.get('password')
    if any([username, password, email]) is None:
        abort(400) # missing arguments
    if User.query.filter_by(username = username).first() is not None:
        abort(400) # existing user
    user = User(username=username, email=email)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()

    token = user.generate_auth_token(600).decode('ascii')

    return jsonify({ 'username': user.username, 'token': token }),\
           201,\
           {'Location': url_for('get_user', id = user.id, _external = True)}

@app.route('/api/users/<int:id>')
def get_user(id):
    user = User.query.get(id)
    if not user:
        abort(400)
    return jsonify({'username': user.username})

@app.route('/api/token')
@auth.login_required
def get_auth_token():
    token = g.user.generate_auth_token(600)
    return jsonify({'token': token.decode('ascii'), 'duration': 600})

@auth.verify_password
def verify_password(username_or_token, password):
    '''It makes http-auth work for all all login_required routes'''
    # first try to authenticate by token
    user = User.verify_auth_token(username_or_token)
    if not user:
        # try to authenticate with username/password
        user = User.query.filter_by(username=username_or_token).first()
        if not user or not user.verify_password(password):
            return False
    g.user = user
    return True

@app.route('/api/user/me')
@auth.login_required
def get_user_me():
    return jsonify({'data': 'Hello, %s!' % g.user.username})

@app.route('/')
def index():
    return app.send_static_file('index.html') # served rrom react


db.create_all()