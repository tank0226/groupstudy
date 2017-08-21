#!/usr/bin/env python
from threading import Lock
from flask import Flask, render_template, session, request
from flask_socketio import SocketIO, emit, join_room, leave_room, \
    close_room, rooms, disconnect

# Set this variable to "threading", "eventlet" or "gevent" to test the
# different async modes, or leave it set to None for the application to choose
# the best option based on installed packages.
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()



# def background_thread():
#     """Example of how to send server generated events to clients."""
#     while True:
#         socketio.sleep(10)
#         socketio.emit('response',
#                       {'data': 'Server generated event'},
#                       namespace='/process')
@socketio.on('connect', namespace='/process')
def connect():
    # global thread
    # with thread_lock:
    #     if thread is None:
    #         thread = socketio.start_background_task(target=background_thread)
    emit('response', {'data': 'Connected. Room Number: '+ request.sid})

@socketio.on('disconnect_request', namespace='/process')
def disconnect_request():
    # session['receive_count'] = session.get('receive_count', 0) - 1
    emit('response',
         {'data': 'Disconnected!'})
    disconnect()

@socketio.on('disconnect', namespace='/process')
def disconnect():
    print('Client disconnected', request.sid)


@app.route('/')
def index():
    return render_template('index.html', async_mode=socketio.async_mode)


# @socketio.on('message_event', namespace='/process')
# def test_message(message):
#     # session['receive_count'] = session.get('receive_count', 0)
#     emit('response',
#          {'data': message['data']})


@socketio.on('broadcast_event', namespace='/process')
def broadcast_message(message):
    # session['receive_count'] = session.get('receive_count', 0)
    emit('response',
         {'data': message['data']},
         broadcast=True)


@socketio.on('join_event', namespace='/process')
def join(message):
    room = message["room"]
    send_room_message({"data":"Someone is about to join a room", "room":message['room']})
    join_room(message['room'])
    # session['receive_count'] = session.get('receive_count', 0) + 1
    emit('response',
         {'data': 'In rooms: ' + ', '.join(rooms())})

    send_room_message({"data":"Someone has joined the room", "room":message['room']})


@socketio.on('room_event', namespace='/process')
def send_room_message(message):
    # session['receive_count'] = session.get('receive_count', 0)
    emit('response',
         {'data': message['data']},
         room=message['room'])


@socketio.on('my_ping', namespace='/process')
def ping_pong():
    emit('my_pong')


if __name__ == '__main__':
    socketio.run(app, debug=True)
