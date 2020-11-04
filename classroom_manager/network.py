from flask import session, redirect, url_for,request
from flask_login import current_user
from flask_socketio import SocketIO, emit, send, disconnect, join_room, leave_room
from classroom_manager import socketio
from classroom_manager.models import User, Classroom, Membership, Channel, Message, Note, DirectMessage
from classroom_manager.utils import generate_code
from classroom_manager import db
from datetime import datetime

users = {}

@socketio.on('connect')
def handle_connections():
    if not current_user.is_authenticated:
    	disconnect()
    	return redirect(url_for('login'))
    user = User.query.filter(User.id==current_user.get_id()).first()
    users[user.username] = request.sid
    user_memberships = Membership.query.filter(Membership.user_id==current_user.get_id())
    [join_room(str(user_membership.classroom_id)) for user_membership in user_memberships] #Instead of making a room for every channel we will make a room for every classroom

@socketio.on('disconnect')
def handle_disconnections():
    if not current_user.is_authenticated:
    	disconnect()
    	return redirect(url_for('login'))

@socketio.on('channel_conversation')
def handle_conversations(data):
    if current_user.is_authenticated:
        if len(data['message']):
            sender_id = current_user.get_id()
            sender = User.query.filter(User.id==sender_id).first()
            #broadcastting message to users in this room
            room = Channel.query.filter(Channel.id==data['channel_id']).first()
            if Membership.query.filter(Membership.user_id==sender_id, Membership.classroom_id==room.classroom_id).first():
                new_message = Message(author_id=sender_id, channel_id=data['channel_id'], contents=data['message'])
                emit('channel_conversation', {'content': data['message'], 'date': 'just now', 'author': {'id':sender_id, 'name': sender.first_name + ' ' + sender.last_name}, 'channel_id': data['channel_id']}, room=str(room.classroom_id))
                #Saving the message in the db
                db.session.add(new_message) #adding message
                db.session.commit()
        else:
            socket.emit('error', 'message must have more than one character.')

    else:
        disconnect()
        return redirect(url_for('login'))

@socketio.on('join-room')
def joinroom(room_id):
    if current_user.is_authenticated:
        join_room(str(room_id))

@socketio.on('channel_action')
def channel_action(data):
    membership = Membership.query.filter(Membership.user_id==current_user.get_id(), Membership.classroom_id==data['classroom_id']).first()
    if membership.role == 'super':
        if data['action'] == 'add':
            new_channel = Channel(classroom_id=int(data['classroom_id']),name=data['name_input'])
            db.session.add(new_channel)
            db.session.flush()
            db.session.commit()
            emit('new_channel', {'classroom_id': data['classroom_id'],'name': new_channel.name, 'id': new_channel.id},room=str(data['classroom_id']))
        elif data['action'] == 'rename':
            specified_channel = Channel.query.filter(Channel.id==data['channel_id']).first()
            specified_channel.name = data['name_input']
            db.session.commit()
            emit('channel_rename', {'classroom_id':data['classroom_id'],'new_name': data['name_input'], 'id': data['channel_id']}, room=str(data['classroom_id']))
        elif data['action'] == 'delete':
            specified_channel = Channel.query.filter(Channel.id==data['channel_id']).delete()
            Message.query.filter(Message.channel_id==data['channel_id']).delete()
            Note.query.filter(Note.channel_id==data['channel_id']).delete()
            db.session.commit()
            emit('channel_delete', {'classroom_id':data['classroom_id'],'id': data['channel_id']}, room=str(data['classroom_id']))
    else:
        pass

@socketio.on('code_regeneration_req')
def regenerate_code(data):
    Classroom.query.filter(Classroom.id==data['classroom_id']).first().code=generate_code(data['classroom_id'])
    db.session.commit()
    emit('code_regeneration', {'classroom_id': data['classroom_id'], 'code':Classroom.query.filter(Classroom.id==data['classroom_id']).first().code})

@socketio.on('user_action')
def user_action(data):
    membership = Membership.query.filter(Membership.user_id==current_user.get_id(), Membership.classroom_id==data['classroom_id']).first()
    if membership.role == 'super':
        if data['action'] == 'kick':
            Membership.query.filter(Membership.classroom_id==int(data['classroom_id']), Membership.user_id==int(data['user_id'])).delete()
            db.session.commit()
            emit('user_kick', {'user_id': data['user_id'], 'classroom_id': data['classroom_id']}, room=str(data['classroom_id']))
        elif data['action'] == 'ban':
            pass

@socketio.on('classroom_leave')
def user_leave(data):
    if current_user.is_authenticated:
        Membership.query.filter(Membership.user_id==current_user.get_id(), Membership.classroom_id==data['classroom_id']).delete()
        db.session.commit()

@socketio.on('direct_message')
def direct_message(data):
    new_direct_message = DirectMessage(sender_id=current_user.get_id(), receiver_id=data['to'], content=data['message'])
    db.session.add(new_direct_message)
    db.session.commit()
    recipient_username = User.query.filter(User.id==data['to']).first().username
    if recipient_username in users.keys():
        emit('direct_message', {'content': data['message'], 'author': User.query.filter(User.id==current_user.get_id()).first().username, 'date': 'Just now'}, room=users[recipient_username])
    emit('direct_message', {'content': data['message'], 'author': User.query.filter(User.id==current_user.get_id()).first().username, 'date': 'Just now'}, room=users[User.query.filter(User.id==current_user.get_id()).first().username])