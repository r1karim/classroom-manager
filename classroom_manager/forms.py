from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, RadioField
from wtforms.validators import DataRequired, Length, Email, EqualTo, InputRequired, ValidationError
from classroom_manager.models import User

class RegistrationForm(FlaskForm): # Form objects for the front-end devs
    name = StringField("Name", 
                            validators=[DataRequired(), Length(min=2, max=25)])
    last_name = StringField("Last Name", 
                            validators=[DataRequired(), Length(min=2, max=25)])
    username = StringField("Username", 
                            validators=[DataRequired(), Length(min=2, max=25)])
    email = StringField("Email", 
                            validators=[DataRequired(), Email()])
    password = PasswordField("Password", 
                            validators=[DataRequired()])
    confirm_password = PasswordField("Confirm Password", 
                            validators=[DataRequired(), EqualTo('password')])
    student_or_teacher = RadioField("Teacher or student", 
                            choices=[('teacher', 'Teacher'), ('student', 'Student')], 
                            validators=[InputRequired()])
    submit = SubmitField('Sign Up')

    def validate_username(self, username):
        if User.query.filter_by(username=username.data).first(): # Checks if a user with the same username is in the database
            raise ValidationError("That username is taken, please choose a different one.")

    def validate_email(self, email):
        if User.query.filter_by(email=email.data).first(): # Checks if a user with the same username is in the database
            raise ValidationError("That email is taken, please choose a different one.")

class LoginForm(FlaskForm): # Form objects for the front-end devs
    email = StringField("Email", 
                            validators=[DataRequired(), Email()])
    password = PasswordField("Password", 
                            validators=[DataRequired()])
    remember = BooleanField("Remember Me")
    submit = SubmitField('Log In')
