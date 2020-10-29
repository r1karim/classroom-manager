from flask import session, redirect, url_for
from flask_login import current_user
from flask_socketio import SocketIO, emit, send, disconnect, join_room, leave_room
from classroom_manager import socketio
from classroom_manager.models import User, Classroom, Membership, Channel, Message
from classroom_manager import db
from datetime import datetime

@socketio.on('connect')
def handle_connections():
    if not current_user.is_authenticated:
    	disconnect()
    	return redirect(url_for('login'))
    user_memberships = Membership.query.filter(Membership.user_id==current_user.get_id())
    '''user_rooms = Channel.query.filter(Channel.classroom_id.in_([membership.classroom_id for membership in user_memberships])) #getting all channels inside of classrooms in which the user has access to
    [join_room(str(user_room.id)) for user_room in user_rooms] #joining all rooms'''
    [join_room(str(user_membership.classroom_id)) for user_membership in user_memberships] #Instead of making a room for every channel we will make a room for every classroom


@socketio.on('disconnect')
def handle_disconnections():
    if not current_user.is_authenticated:
    	disconnect()
    	return redirect(url_for('login'))


@socketio.on('channel_conversation')
def handle_conversations(data):
    if not current_user.is_authenticated:
    	disconnect()
    	return redirect(url_for('login'))
    else:
    	if not len(data['message']):
    		socket.emit('error', 'message must have more than one character.')
    	else:
            sender_id = current_user.get_id()
            new_message = Message(author_id=sender_id, channel_id=data['channel_id'], contents=data['message'])
            sender = User.query.filter(User.id==sender_id).first()
            #broadcastting message to users in this room
            room = Channel.query.filter(Channel.id==data['channel_id']).first()
            emit('channel_conversation', {'content': data['message'], 'date': 'just now', 'author': {'id':sender_id, 'name': sender.first_name + ' ' + sender.last_name}, 'channel_id': data['channel_id']}, room=str(room.classroom_id))
            #Saving the message in the db
            db.session.add(new_message) #adding message
            db.session.commit()

@socketio.on('join-room')
def joinroom(room_id):
    if current_user.is_authenticated:
        join_room(str(room_id))
