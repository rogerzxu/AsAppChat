import functools
from flask import Flask, render_template, request, g, flash, redirect, url_for, jsonify
from flask.ext.login import LoginManager, login_required, login_user, logout_user, current_user
from flask_socketio import SocketIO, disconnect, join_room, leave_room, emit

from DBTools import query_db, insert_db
from User import User

app = Flask(__name__)
app.secret_key = 'secret!'
app.config['SECRET_KEY'] = 'secret!'
login_manager = LoginManager()
login_manager.init_app(app)
socketio = SocketIO(app)


def authenticated_only(f):
    @functools.wraps(f)
    def wrapped(*args, **kwargs):
        if not current_user.is_authenticated:
            disconnect()
        else:
            return f(*args, **kwargs)
    return wrapped


@socketio.on('connect', namespace='/chat')
@authenticated_only
def connect_handler():
    join_room(current_user.user_name)
    print(current_user.user_name + " has connected!")


@socketio.on('text', namespace='/chat')
@authenticated_only
def text_handler(data):
    print('new message: ' + str(data))


@login_manager.user_loader
def load_user(user_id):
    retuser = query_db('select * from users where id = ?', [int(user_id)], one=True)
    if retuser is not None:
        return User(retuser['user_name'], retuser['id'])
    return None


@app.teardown_appcontext
def close_connection(exception):
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def sign_in():
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
        retuser = query_db('select * from users where user_name = ?', [username], one=True)
        if retuser is not None:
            login_user(User(username, retuser['id']))
            flash('You were successfully logged in!')
            return redirect(url_for('user_home'))
        else:
            flash('Invalid username!')
    return render_template('signin.html')


@app.route('/logout', methods=['GET'])
@login_required
def logout():
    logout_user()
    flash('You were logged out!')
    return redirect(url_for('sign_in'))


@app.route('/user-home', methods=['GET'])
@login_required
def user_home():
    users = query_db('select * from users where user_name != ?', [current_user.user_name])
    return render_template('user-home.html', users=users)


@app.route('/chat-history/<withUser>', methods=['GET'])
@login_required
def chat_history(withUser):
    userId = current_user.user_id
    query = """select senders.user_name as sender, receivers.user_name as receiver, m.message_content, m.timestamp
              from message m, users senders, users receivers
              where m.sender_user_id = senders.id
              and m.receiver_user_id = receivers.id
              and ((sender_user_id = ? and receivers.user_name = ?)
                or (senders.user_name = ? and receiver_user_id = ?))
              order by timestamp ASC"""
    messages = query_db(query, [userId, withUser, withUser, userId])
    return jsonify(messages=messages)


if __name__ == '__main__':
    app.debug=True
    socketio.run(app)
