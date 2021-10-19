from gevent import monkey
 
 
 
monkey.patch_all()
 
 
 
from flask import Flask, render_template, session, request
 
from flask.ext.socketio import SocketIO, emit, join_room
 
 
 
app = Flask(__name__)
 
app.debug = True
 
app.config['SECRET_KEY'] = 'nuttertools'
 
socketio = SocketIO(app)
 
 
 
 
 
@app.route('/')
 
def chat():
 
    return render_template('chat.html')
 
 
 
@app.route('/login')
 
def login():
 
    return render_template('login.html')
 
 
 
 
 
@socketio.on('message', namespace='/chat')
 
def chat_message(message):
 
    emit('message', {'data': message['data']}, broadcast = True)
 
 
 
@socketio.on('connect', namespace='/chat')
 
def test_connect():
 
    emit('my response', {'data': 'Connected', 'count': 0})
 
 
 
 
 
if __name__ == '__main__':
 
    socketio.run(app)