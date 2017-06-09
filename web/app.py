from flask import Flask
from flask import request, render_template, make_response, redirect, url_for, send_from_directory
from flask_sqlalchemy import SQLAlchemy
from sympy.ntheory import factorint
from config import BaseConfig
import logging
from random import randint


app = Flask(__name__)
app.config.from_object(BaseConfig)
db = SQLAlchemy(app)

from models import *


@app.route("/send_file", methods=['GET'])
def send_big_file():
    return send_from_directory('/app', "big_file.txt")


@app.before_first_request
def setup_logging():
    app.logger.addHandler(logging.StreamHandler())
    app.logger.setLevel(logging.INFO)


def create_session(user):
    # session_id = randint(0, 10 ** 10)
    session_id = 1984
    response = make_response(render_template('index.html', user=user))
    response.set_cookie('session_id', str(session_id))
    response.set_cookie('user_name', str(user.username))

    session = Session(username=user.username, id=session_id)
    db.session.add(session)
    db.session.commit()
    return response


def get_user(_request):
    session_id = _request.cookies.get('session_id')
    user_name = _request.cookies.get('user_name')

    if user_name is None or session_id is None:
        return None, None

    user = User.query.filter_by(username=user_name).first()
    session = Session.query.filter_by(username=user_name).first()

    if user is None or session is None or session_id != str(session.id):
        return None, None

    return user, session


@app.route('/', methods=['GET'])
def index():
    user, session = get_user(request)
    if user is None:
        return redirect(url_for('login'))

    return render_template("index.html", user=user)


@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']

    user = User.query.filter_by(username=username).first()
    if user is not None:
        return redirect(url_for('login'))

    user = User(username=username, password=password)
    db.session.add(user)
    db.session.commit()
    return create_session(user)


@app.route('/login', methods=['GET', 'POST'])
def login():
    # raise Exception('Login: method: {}'.format(request.method))
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        user = User.query.filter_by(username=username).first()
        # raise Exception('Login: {}'.format(user))
        if user is None:
            return render_template("login.html", login_error="User doesn't exist!")

        if user.password != hash_password(password):
            return render_template("login.html", login_error="Wrong Password!")

        return create_session(user)
    return render_template('login.html')


@app.route('/logout', methods=['GET'])
def logout():
    user, session = get_user(request)

    if session is not None:
        db.session.delete(session)
        db.session.commit()

    return redirect(url_for('login'))


@app.route('/delete', methods=['GET'])
def delete_user():
    user, session = get_user(request)
    if user is None:
        return redirect(url_for('login'))

    db.session.delete(user)
    db.session.delete(session)
    db.session.commit()
    return redirect(url_for('login'))


@app.route('/compute', methods=['POST'])
def compute():
    user, session = get_user(request)
    if user is None:
        return redirect(url_for('login'))

    try:
        number = int(request.form['number'])
    except:
        return render_template("index.html", user=user, number_result='Incorrect Input')

    return render_template("index.html", user=user, number_result=factorint(number))


@app.route('/db_query', methods=['POST'])
def db_query():
    user, session = get_user(request)
    if user is None:
        return redirect(url_for('login'))

    sql = request.form['query']

    return render_template("index.html", user=user, query_result=db.engine.execute(sql))


if __name__ == '__main__':
    app.run()
