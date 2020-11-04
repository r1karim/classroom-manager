from flask import Flask, render_template, url_for, flash, redirect, request, jsonify
from classroom_manager.forms import RegistrationForm, LoginForm
from classroom_manager import app, bcrypt, db, socketio
from classroom_manager.models import User, Classroom, Membership, Channel, Message, Note, Assignment, DirectMessage, AssignmentSubmission
from flask_login import login_user, current_user, logout_user, login_required
from classroom_manager.utils import generate_code
from werkzeug.utils import secure_filename
from types import SimpleNamespace
from dateutil import parser
import os

@app.route("/")
@app.route("/home")
def home():
    return render_template("home.html", title='Home Page')

@app.route("/login", methods=["GET", "POST"]) # Make sure the form tag has the method, "POST"
def login():
    if current_user.is_authenticated:
        return redirect(url_for("home"))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            flash(f"Successfully logged in!", 'success')
            return redirect(next_page) if next_page else redirect(url_for('__app__'))
        else:
            flash("Login unsuccessful, please try again.", 'danger')
    return render_template("login.html", form=form, title='Login')

@app.route("/register", methods=["GET", "POST"]) # Make sure the form tag has the method, "POST"
def register():
    if current_user.is_authenticated:
        return redirect(url_for("__app__"))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode("utf-8") # Hash the password
        new_user = User(first_name=form.name.data, last_name=form.last_name.data, username=form.username.data,
                    email=form.email.data, status=form.student_or_teacher.data, password=hashed_password)
        db.session.add(new_user) # Add the new user to the database queue
        db.session.commit() # Commit all the changes in the queue
        return redirect(url_for('login'))
    return render_template("register.html", form=form, title='Register')

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("home"))

@app.route("/app")
@login_required
def __app__():
    return render_template("app.html", title='Application')

@app.route('/app/chats', methods=['POST'])
def app_chats():
    users, contacts = set(), []
    messages = DirectMessage.query.filter((DirectMessage.receiver_id==current_user.get_id()) | (DirectMessage.sender_id==current_user.get_id())).all()
    [users.add(message.receiver_id) if int(message.receiver_id) != int(current_user.get_id()) else users.add(int(message.sender_id)) for message in messages]
    for user in User.query.filter(User.id.in_(users)).all():
        contact = SimpleNamespace()
        contact.id = user.id
        contact.name = user.username
        contacts.append(contact)
    return render_template('chats.html', title='Contacts', data=contacts, type='contact')

@app.route('/add-contact', methods=['POST'])
def add_contact():
    contact = User.query.filter(User.username==request.form['username']).first()
    if contact and int(contact.id) == int(current_user.get_id()):
        contact = None #
    return jsonify({'name': contact.username, 'id': contact.id, 'img_url': url_for('static', filename='imgs/defaultuser-icon.png')}) if contact and contact.id != current_user.get_id() else jsonify({'error': 'user not found.'})

@app.route('/retrieve-directmessages/<user_id>', methods=['POST'])
def retrieve_directmessages(user_id):
    messages = DirectMessage.query.filter((DirectMessage.sender_id==user_id) & (DirectMessage.receiver_id==current_user.get_id()) | (DirectMessage.sender_id==current_user.get_id()) & (DirectMessage.receiver_id==user_id))
    return jsonify({'messages': [{'content': message.content, 'date': message.date, 'author': User.query.filter(User.id==message.sender_id).first().username, 'mein': int(current_user.get_id())==(message.sender_id)} for message in messages]})

'''
@app.route('/retrieve-contacts', methods=['POST'])
def retrieve_contacts():
    pass'''

@app.route('/app/classrooms', methods=['POST'])
def app_classrooms():
    memberships = Membership.query.filter(Membership.user_id==current_user.get_id()).all()
    classrooms = Classroom.query.filter(Classroom.id.in_([membership.classroom_id for membership in memberships])).all()
    return render_template('classrooms.html', title='Classrooms', data=classrooms, type='classroom')

@app.route('/add-note', methods=['POST'])
def add_note():
    if request.form['note_title'] and request.form['note_text'] and request.form['channel_id']: 
        note_title = request.form['note_title']
        note_text = request.form['note_text']
        note_channel_id = request.form['channel_id']
        if request.files["note_image"]:
            image = request.files["note_image"]
            filename = secure_filename(image.filename)
            image.save(os.path.join(app.config['IMAGE_UPLOADS'], filename))
        new_note = Note(author_id=current_user.get_id(), title=note_title, note_text=note_text,note_imgs=filename, channel_id=note_channel_id)
        db.session.add(new_note)
        db.session.commit()
        return jsonify({'new_note': {'note_title':new_note.title, 'note_id': new_note.id, 'note_text': new_note.note_text, 'note_img': url_for('static', filename='imgs/' + new_note.note_imgs)}})
    else:
        pass

@app.route('/classroom-settings/<classroom_id>', methods=['POST'])
def classroom_settings(classroom_id):
    specified_classroom = Classroom.query.filter(Classroom.id==classroom_id).first()
    if specified_classroom:
        membership = Membership.query.filter(Membership.classroom_id==classroom_id, Membership.user_id==current_user.get_id()).first()
        members = Membership.query.filter(Membership.classroom_id==classroom_id)
        members = User.query.filter(User.id.in_([member.user_id for member in members]))
        permission = membership.role == 'super'
        return jsonify({'room_code': specified_classroom.code, 
            'permission': permission, 
            'members': [{'name': member.first_name + ' ' + member.last_name, 
            'id': member.id} for member in members if int(member.id) != int(current_user.get_id())],
            'channels': [{'id': channel.id, 'name': channel.name} for channel in Channel.query.filter(Channel.classroom_id==classroom_id)]})
    return jsonify({'error': 'Classroom wasn\'t found.'})

@app.route('/create-team', methods=['POST'])
def create_team():
    #getting data from the form
    team_name = request.form['team_name'] 
    team_description = request.form['team_description']
    if team_name:
        #creating the classroom
        new_classroom = Classroom(name=team_name, description=team_description)
        db.session.add(new_classroom) #adding the new classroom
        db.session.flush() #using flush just so we can get the id of the classroom
        new_classroom.code = generate_code(new_classroom.id)
        db.session.flush()
        new_channel = Channel(name="General", classroom_id=new_classroom.id) #creating general channel for the classroom
        db.session.add(new_channel)
        db.session.flush() #same here...
        #Creating membership for the user and classroom
        new_membership = Membership(user_id=current_user.get_id(), classroom_id=new_classroom.id, role='super')
        db.session.add(new_membership)
        db.session.commit()
        #sending back the classroom object
        return jsonify({'new_classroom': {
            'name': new_classroom.name,
            'id': new_classroom.id,
            'imgurl': url_for('static', filename="imgs/" + new_classroom.image_file)
            },
            'channel': new_channel.id
        })
    return jsonify({'error': 'given name is invalid.'}) #Returning an error if the given name is empty


@app.route('/join-team', methods=['POST'])
def join_team():
    team_code = request.form['code']
    if team_code:
        classroom_id = Classroom.query.filter(Classroom.code==team_code).first()
        if classroom_id:
            new_membership = Membership(user_id=current_user.get_id(), classroom_id=classroom_id.id, role='regular')
            db.session.add(new_membership)
            db.session.commit()
            return jsonify({'result': {'id': classroom_id.id,
                'name': classroom_id.name}, 
                'url_for_img': url_for('static', filename='imgs/'+ classroom_id.image_file)})
        return jsonify({'error': "given code has either expired or is not valid"})
    return jsonify({'error': 'given code is invalid'})

@app.route('/retrieve-notes/<channel>', methods=['POST'])
def retrieve_notes(channel):
    notes = Note.query.filter(Note.channel_id==channel)
    return jsonify([{'author_id': note.author_id, 'note_title': note.title,'note_id': note.id,'note_text': note.note_text, 'note_img': url_for('static', filename='imgs/'+note.note_imgs) if note.note_imgs else None} for note in notes])

@app.route('/retrieve-assignments/<channel>', methods=['POST'])
def retrieve_assignments(channel):
    assignments = Assignment.query.filter(Assignment.channel_id==channel)
    role = Membership.query.filter(Membership.classroom_id==Channel.query.filter(Channel.id==channel).first().classroom_id, Membership.user_id==current_user.get_id()).first().role
    return jsonify({'role': role, 'assignments': [{'id': assignment.id, 'text': assignment.assignment_text, 'duedate': assignment.due_date, 'submission_state': AssignmentSubmission.query.filter(assignment.id==AssignmentSubmission.assignment_id, AssignmentSubmission.user_id==current_user.get_id()).first() is not None} for assignment in assignments]})

@app.route('/add-assignment', methods=['POST'])
def add_assignment():
    get_date = parser.parse(request.form['assignment_date'])
    new_assignment = Assignment(author_id=current_user.get_id(), due_date=get_date, assignment_text=request.form['assignment_text'], channel_id=request.form['channel_id'])
    db.session.add(new_assignment)
    db.session.commit()
    return jsonify({'id': new_assignment.id, 'text': new_assignment.assignment_text, 'duedate': new_assignment.due_date})

@app.route('/homework-submit', methods=['POST'])
def homework_submit():
    if request.files["homework"]:
        homework_file = request.files["homework"]
        filename = secure_filename(homework_file.filename)
        homework_file.save(os.path.join(app.config['FILE_UPLOADS'], filename))
        new_submission = AssignmentSubmission(user_id=current_user.get_id(),assignment_id=request.form['assignment_id'], file_location=filename)
        db.session.add(new_submission)
        db.session.commit()
    return jsonify({'message': 'successfuly submitted'})

@app.route('/retrieve-submissions/<assignment_id>', methods=['POST'])
def retrieve_submissions(assignment_id):
    assignments = AssignmentSubmission.query.filter(AssignmentSubmission.assignment_id==assignment_id)
    return jsonify([{'name': User.query.filter(User.id==assignment.user_id).first().username, 'file': url_for('static', filename='submissions/'+str(assignment.file_location))} for assignment in assignments])


@app.route('/retrieve-channels/<classroom>', methods=['POST'])
def retrieve_channels(classroom):
    channels = Channel.query.filter(classroom==Channel.classroom_id)
    return jsonify({ 'result': [ { 'id': channel.id, 'name': channel.name } for channel in channels ] })

@app.route('/retrieve-messages/<channel>', methods=['POST'])
def retrieve_messages(channel):
    POSTS_COUNT_ONLOAD = 50
    messages = Message.query.filter(Message.channel_id==channel, Message.ischild==-1)
    return jsonify({'result': [ { 'id': message.id, 
        'content': message.contents, 
        'date': message.date,
        'author': {
            'id': message.author_id,
            'name': User.query.filter(User.id==message.author_id)[0].first_name + ' ' + User.query.filter(User.id==message.author_id)[0].last_name,
            'avatar':url_for('static', filename="imgs/" + User.query.filter(User.id==message.author_id)[0].image_file)}
            } for message in messages][-POSTS_COUNT_ONLOAD:] #returning the last ten messages in this channel
        })

@app.route('/app/activity', methods=['POST'])
def app_activity():
    messages = Message.query.filter(Message.author_id==current_user.get_id())
    return render_template('activity.html', data=messages)

@app.route('/app/meetings', methods=['POST'])
def app_meetings():
    return render_template('meetings.html')

@app.route('/app/calls', methods=['POST'])
def app_calls():
    return render_template('calls.html')