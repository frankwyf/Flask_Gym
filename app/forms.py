import datetime

from app.model import Customer, Coach, Manager
from flask_login import current_user
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, IntegerField, SelectField, \
    DateField, TextAreaField, DateTimeLocalField
from wtforms.validators import DataRequired, Length, Email, ValidationError, NumberRange, EqualTo, Regexp


# General manager login in form
class ManagerLogin(FlaskForm):  # flask form for general manger log in
    username = StringField('Username',
                           validators=[DataRequired(), Length(max=20)], render_kw={'placeholder': 'Enter username'})
    password = PasswordField('Password', validators=[DataRequired()], render_kw={'placeholder': 'Enter password'})
    remember = BooleanField('Remember me', default=True)  # cookie to keep manger to login
    login = SubmitField('Log in')


# the form for email request to be sent
class ForgetPassword(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(max=20)],
                           render_kw={'placeholder': 'Enter your username'})
    email = StringField('E-mail Address', validators=[DataRequired(), Email()],
                        render_kw={'placeholder': 'Enter your E-mail box'})
    CustomerType = SelectField('type', validators=[DataRequired()],
                               choices=[("Customer", 'Member'), ("Coach", 'Coach'), ('Manager', 'Manager')],
                               default='Customer', coerce=str)
    adjust = SubmitField('Send request')

    def validate_user(self, username):
        user = Customer.query.filter_by(username=username.data).first()
        if user is None:
            raise ValidationError('There is no account with this username. You must register first.')


# retrieve password form
class ResetPassword(FlaskForm):
    password = PasswordField('New Password',
                             validators=[DataRequired(), Regexp(r"^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)[A-Za-z\d]{8,16}$",
                                                                message='Password must have numbers, upper and lower '
                                                                        'case letters, and between 8-16 characters')],
                             render_kw={'placeholder': 'Enter new Password'})
    confirmpassword = PasswordField('Confirm Password', validators=[DataRequired(),
                                                                    EqualTo('password', 'Confirm password is '
                                                                                        'different to '
                                                                                        'Password!')],
                                    render_kw={'placeholder': 'Confirm new Password'})
    confirm = SubmitField('Reset Password')


# change personal information for customer
class UpdateAccountFrom(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(max=20)],
                           render_kw={'placeholder': 'Enter new username'})
    email = StringField('E-mail Address', validators=[DataRequired(), Email()],
                        render_kw={'placeholder': 'Enter new E-mail'})
    picture = FileField('profile', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    gender = SelectField('gender', validators=[DataRequired()],
                         choices=[(0, 'Secret'), (1, 'Male'), (2, 'Female')], default=0, coerce=int)
    birthday = DateField('birthday', validators=[DataRequired()])
    weight = IntegerField('age', validators=[NumberRange(min=0)], render_kw={'placeholder': 'Enter current weight'})
    height = IntegerField('age', validators=[NumberRange(min=0)], render_kw={'placeholder': 'Enter current height'})
    aim = IntegerField('age', validators=[NumberRange(min=0)], render_kw={'placeholder': 'Enter aim_weight'})
    prefer = SelectField('speciality', validators=[DataRequired()],
                         choices=[("swimming", 'Swimming'), ("strength", 'Strength'), ('yoga', 'Yoga'),
                                  ('fitting', 'Fitting'), ('all', 'All-round')], default='all', coerce=str)
    submit = SubmitField('Update')

    # username must be unique
    def validate_username(self, username):
        if username.data != current_user.username:
            user = Customer.query.filter_by(username=username.data).first()
            # if result found, then this name must be changed
            if user:
                raise ValidationError('This username has already been taken!')

    def clean_date(self, birthday):
        if birthday > datetime.date.today():
            raise ValidationError("Birthday cannot be in the future!")


# change personal information
class ManagerAccountFrom(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(max=20)],
                           render_kw={'placeholder': 'Enter new username'})
    email = StringField('E-mail Address', validators=[DataRequired(), Email()],
                        render_kw={'placeholder': 'Enter new E-mail'})
    submit = SubmitField('Update')

    # username must be unique
    def validate_username(self, username):
        if username.data != current_user.username:
            user = Manager.query.filter_by(username=username.data).first()
            # if result found, then this name must be changed
            if user:
                raise ValidationError('This username has already been taken!')


# manager can adjust customer's membership level
class Membership(FlaskForm):
    membership = SelectField('Edit membership', choices=[(0, 'Free Trail'), (1, 'Valid member'),
                                                         (2, 'Overdue'), (3, 'Freeze')], default=0, coerce=int)
    submit = SubmitField('Update')


# change personal information for coach
class UpdateCoachFrom(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(max=20)],
                           render_kw={'placeholder': 'Enter new username'})
    email = StringField('E-mail Address', validators=[DataRequired(), Email()],
                        render_kw={'placeholder': 'Enter new E-mail'})
    picture = FileField('profile', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    gender = SelectField('gender', choices=[(0, 'Secret'), (1, 'Male'), (2, 'Female')], default=0, coerce=int)
    speciality = SelectField('speciality', validators=[DataRequired()],
                             choices=[("swimming", 'Swimming'), ("strength", 'Strength'), ('yoga', 'Yoga'),
                                      ('fitting', 'Fitting'), ('all', 'All-round')], default='all', coerce=str)
    submit = SubmitField('Update')

    # username must be unique
    def validate_username(self, username):
        if username.data != current_user.username:
            user = Coach.query.filter_by(username=username.data).first()
            # if result found, then this name must be changed
            if user:
                raise ValidationError('This username has already been taken!')


# post form
class PostFrom(FlaskForm):
    description = TextAreaField('Username',
                                validators=[DataRequired(), Length(max=200)],
                                render_kw={'placeholder': 'Enter Post content (under 200)'})
    tag = StringField('tag', validators=[DataRequired(), Length(max=20)],
                      render_kw={'placeholder': 'Enter post tag (under 20)'})
    picture = FileField('Chose a photo to show your work!', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    submit = SubmitField('Post')


# new course form
class NewCourse(FlaskForm):
    cname = StringField('Course Name:', validators=[DataRequired(), Length(max=20)],
                        render_kw={'placeholder': 'Enter course name'})
    description = TextAreaField('Describe your course:', validators=[DataRequired(), Length(max=200)],
                                render_kw={'placeholder': 'Enter course description'})
    start = DateTimeLocalField('Starting from:', validators=[DataRequired()], default=datetime.datetime.now())
    end = DateTimeLocalField('End by:', validators=[DataRequired(), ], default=datetime.datetime.now())
    cprofile = FileField('Chose a Cover for your course:', validators=[FileAllowed(['jpg', 'png', 'jpeg'])])
    video = FileField('Demo video for your course:', validators=[FileAllowed(['mp4', 'ogg', 'webm'])])
    submit = SubmitField('Release')

    def validat_start_end_time(self, start, end):
        if end < start:
            raise ValidationError("End time can't be earlier than start time!")
