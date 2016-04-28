import sqlite3

from flask import Flask
from flask import render_template
from flask import request
from flask import g
from flask import flash

app = Flask(__name__)
app.secret_key = 'many random bytes'

DATABASE = 'resources/sqlite/AsAppChat.db'


def connect_db():
    rv = sqlite3.connect(DATABASE)
    rv.row_factory = sqlite3.Row
    return rv


def get_db():
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


@app.teardown_appcontext
def close_connection(exception):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


def query_db(query, args=(), one=False):
    cur = get_db().execute(query, args)
    rv = cur.fetchall()
    cur.close()
    return (rv[0] if rv else None) if one else rv


def insert_db(query, args=()):
    db = get_db()
    db.execute(query, args)
    db.commit()


@app.route('/')
def hello_world():
    return render_template('signin.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        retUser = query_db('select * from users where user_name = ?', [username], one=True)
        if retUser is None:
            insert_db('insert into users (user_name) values(?)', [username])
            flash('You were successfully registered!')
            return render_template('signin.html')
        else:
            flash('That username is already taken!')

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        retUser = query_db('select * from users where user_name = ?', [username], one=True)
        if retUser is not None:
            flash('You were successfully logged in!')
            return render_template('success.html')
        else:
            flash('Invalid username!')
    return render_template('signin.html')


if __name__ == '__main__':
    app.run(debug=True)
