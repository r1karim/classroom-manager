from flask_sqlalchemy import SQLAlchemy
from classroom_manager import login_manager, db
from flask_login import UserMixin
from datetime import datetime

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(25), nullable=False)
    last_name = db.Column(db.String(25), nullable=False)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(254), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default="default.jpg")
    status = db.Column(db.String(10), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    notes = db.relationship('Note', backref='author', lazy=True)
    assignments = db.relationship('Assignment', backref='author', lazy=True)
    messages = db.relationship('Message', backref='author', lazy=True)
    membership = db.relationship('Membership', backref='classroom', lazy=True)
    submission = db.relationship('AssignmentSubmission', backref='submission', lazy=True)
    def __repr__(self):
        return f"User(username: '{self.username}', email: '{self.email}', profile_img: '{self.image_file}')"


class Classroom(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(60), nullable=True)
    image_file = db.Column(db.String(42), nullable=False, default="default_class.png")
    name = db.Column(db.String(25), nullable=False)
    description = db.Column(db.String(262), nullable=True)
    membership = db.relationship('Membership', backref='membership', lazy=True)

    def __repr__(self):
        return f"Classroom(name: '{self.name}', class_img: '{self.image_file}'"
    
class Membership(db.Model):
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    role = db.Column(db.String(7), nullable=False)
    
    __table_args__ = (
        db.PrimaryKeyConstraint(user_id, classroom_id), # Allows two primary keys
    )
    
    def __repr__(self):
        return f"Membership(user_id: '{self.user_id}', classroom_id: '{self.classroom_id}')"

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    contents = db.Column(db.String(100), nullable=False)
    ischild = db.Column(db.Integer, default=-1, nullable=False) # if this is set to -1 then this message is not a reply
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Message(author_id: '{self.author_id}', classroom: '{self.classroom}')"

class Note(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    title = db.Column(db.String(32), nullable=False)
    note_text = db.Column(db.String(300), nullable=False)
    note_imgs = db.Column(db.String(52), nullable=True)

    def __repr__(self):
        return f"Note(author_id: '{self.author_id}', classroom: '{self.classroom}')"

class Assignment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    channel_id = db.Column(db.Integer, db.ForeignKey('channel.id'), nullable=False)
    assignment_text = db.Column(db.String(200), nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    submission = db.relationship('AssignmentSubmission', backref='assignment', lazy=True)
    def __repr__(self):
        return f"Assignment(author_id: '{self.author_id}', classroom: '{self.classroom}')"


class Channel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    name = db.Column(db.String(30), nullable=False)
    message = db.relationship('Message', backref='mesage', lazy=True)
    note = db.relationship('Note', backref='note', lazy=True)
    assignment = db.relationship('Assignment', backref='assignment', lazy=True)

    def __repr__(self):
        return f"Channel(classroom: '{self.classroom_id}', name: '{self.name}')"

class Ban(db.Model): #hasnt been fully implemented yet
    id = db.Column(db.Integer, primary_key=True) 
    classroom_id = db.Column(db.Integer, db.ForeignKey('classroom.id'), nullable=False)
    def __repr__(self):
        return f"Ban(classroom: '{self.classroom_id}', user_id: '{self.user_id}')"

class DirectMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, nullable=False)
    receiver_id = db.Column(db.Integer, nullable=False)
    content = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    def __repr__(self):
        return f"Message(author_id: '{self.sender_id}')"


class AssignmentSubmission(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    assignment_id = db.Column(db.Integer, db.ForeignKey('assignment.id'), nullable=False)
    file_location = db.Column(db.String(52), nullable=True)

    def __repr__(self):
        return f'submission({id})'