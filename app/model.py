from app import db, login_manager, app
from hashlib import sha256
from joserfc import jwk, jwt
from joserfc.errors import JoseError
from flask import session, request, redirect, url_for, flash
from flask_login import UserMixin


def _jwt_signing_key():
    secret = app.config["SECRET_KEY"]
    if isinstance(secret, str):
        secret = secret.encode("utf-8")
    return jwk.import_key(sha256(secret).digest(), "oct")


@login_manager.user_loader
def load_Users(user_id):
    if session.get('role') == 'Manager':
        return Manager.query.get(int(user_id))
    elif session.get('role') == 'Coach':
        return Coach.query.get(int(user_id))
    else:
        return Customer.query.get(int(user_id))


# listening to url accessing for defending of illegal url visits
@app.before_request
def before_user():
    # all sing up routes should be able to visit
    if request.path == "/":
        return None
    if request.path == "/newlogin":
        return None
    if request.path == "/Managerlogin":
        return None
    if request.path == "/Managers":
        return None
    if request.path == "/CustomerLogin":
        return None
    if request.path.startswith("/static"):
        return None
    # some functions before sign in should be able to visit without authentication
    if request.path == "/manager":
        return None
    if request.path == "/register":
        return None
    if request.path == "/newAccount":
        return None
    if request.path == "/Request_password_reset":
        return None
    if request.path.startswith("/Reset_password"):
        return None
    if not session.get("role"):
        flash("Login to explore this app!", 'info')
        return redirect(url_for('newlogin'))


# defining objects for database ORMs

# managers of the gym
class Manager(db.Model, UserMixin):
    aid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200))
    Email = db.Column(db.String(200), nullable=False)
    log = db.Column(db.Integer)  # 0 for offline, 1 for online

    def get_reset_token(self, **kwargs):
        # signature algorithm
        header = {'alg': 'HS256'}
        key = _jwt_signing_key()
        # data in the signature
        data = {'id': self.id, 'role': 'Manager'}
        data.update(**kwargs)

        return jwt.encode(header=header, claims=data, key=key, algorithms=['HS256'])

    @staticmethod
    def verify_reset_token(token):
        try:
            token_data = jwt.decode(token, _jwt_signing_key(), algorithms=['HS256'])
            user_id = token_data.claims['id']
        except JoseError:
            return None
        if token_data.claims['role'] == 'Manager':
            return Manager.query.get(user_id)
        else:
            return None

    def __int__(self, username, Email, log, password):
        self.username = username
        self.Email = Email
        self.log = log
        self.password = password

    @property
    def id(self):
        return self.aid


# Customers of the gym
class Customer(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200))
    profile = db.Column(db.String(200))  # store the file path of customer's profile
    Email = db.Column(db.String(200), nullable=False)
    status = db.Column(db.Integer, default=False)  # 0 for trail, 1 for valid and 2 for overdue (3 for freeze)
    log = db.Column(db.Integer)  # 0 for offline, 1 for online
    sex = db.Column(db.Integer)  # 0 for unknown, 1 for male and 2 for female
    posts = db.Column(db.Integer)  # how many posts have been posted by this user, for user profile show

    def get_reset_token(self, **kwargs):
        # signature algorithm
        header = {'alg': 'HS256'}
        key = _jwt_signing_key()
        # data in the signature
        data = {'id': self.id, 'role': 'Customer'}
        data.update(**kwargs)

        return jwt.encode(header=header, claims=data, key=key, algorithms=['HS256'])

    @staticmethod
    def verify_reset_token(token):
        try:
            token_data = jwt.decode(token, _jwt_signing_key(), algorithms=['HS256'])
            user_id = token_data.claims['id']
        except JoseError:
            return None
        if token_data.claims['role'] == 'Customer':
            return Customer.query.get(user_id)
        else:
            return None

    def __int__(self, username, Email, status, password, profile, log, sex, posts):
        self.username = username
        self.Email = Email
        self.status = status
        self.password = password
        self.log = log
        self.posts = posts
        self.profile = profile


# Health data of customer
class Health(db.Model):
    # build the foreign key between customer and health data
    uid = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False, primary_key=True)
    birthday = db.Column(db.Date)  # birthday of the customer (precise to date is enough)
    height = db.Column(db.Integer)  # current height of the customer
    weight = db.Column(db.Integer)  # current weight of the customer
    aim_weight = db.Column(db.Integer)  # current weight of the customer
    prefer = db.Column(db.String(200))  # customer's preferred sports

    def __int__(self, birthday, height, weight, aim_weight, prefer):
        self.birthday = birthday
        self.height = height
        self.weight = weight
        self.aim_weight = aim_weight
        self.prefer = prefer


# Posts data of customer
class Post(db.Model):
    # build the foreign key between customer and posts
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    photo = db.Column(db.String(200))  # store the file path of photos of the post
    description = db.Column(db.String(200))  # store the words of the post
    tag = db.Column(db.String(20))  # store the field of this post (up to 20 characters)

    def __int__(self, photo, description, tag):
        self.photo = photo
        self.description = description
        self.tag = tag


# Coaches in the gym
class Coach(db.Model, UserMixin):
    cid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    password = db.Column(db.String(200))
    cprofile = db.Column(db.String(200))  # store the file path of customer's profile
    Email = db.Column(db.String(200), nullable=False)
    speciality = db.Column(db.String(200))  # speciality at teaching
    sex = db.Column(db.Integer)  # 0 for unknown, 1 for male and 2 for female

    def __int__(self, username, Email, password, cprofile, speciality, sex):
        self.username = username
        self.Email = Email
        self.speciality = speciality
        self.password = password
        self.sex = sex
        self.cprofile = cprofile

    def get_reset_token(self, **kwargs):
        # signature algorithm
        header = {'alg': 'HS256'}
        key = _jwt_signing_key()
        # data in the signature
        data = {'id': self.id, 'role': 'Coach'}
        data.update(**kwargs)

        return jwt.encode(header=header, claims=data, key=key, algorithms=['HS256'])

    @staticmethod
    def verify_reset_token(token):
        try:
            token_data = jwt.decode(token, _jwt_signing_key(), algorithms=['HS256'])
            user_id = token_data.claims['id']
        except JoseError:
            return None
        if token_data.claims['role'] == 'Coach':
            return Coach.query.get(user_id)
        else:
            return None

    @property
    def id(self):
        return self.cid


# Courses coaches teach in the gym
class Course(db.Model):
    # build the foreign key between course and coach
    id = db.Column(db.Integer, primary_key=True)
    cid = db.Column(db.Integer, db.ForeignKey('coach.cid'), nullable=False)
    name = db.Column(db.String(20), nullable=False)  # course name
    description = db.Column(db.String(200))  # description of the course
    courseProfile = db.Column(db.String(200))  # store the file path of course's profile
    start = db.Column(db.DateTime)  # start time of the course
    end = db.Column(db.DateTime)  # end time of the course
    video = db.Column(db.String(200))  # store the file oath for potential video of the course

    def __int__(self, name, description, courseProfile, start, end, video):
        self.name = name
        self.courseProfile = courseProfile
        self.start = start
        self.end = end
        self.video = video


# connection between customer, coach and course
class Connect(db.Model):
    num = db.Column(db.Integer, nullable=False, primary_key=True)
    id = db.Column(db.Integer, db.ForeignKey('customer.id'), nullable=False)
    cid = db.Column(db.Integer, db.ForeignKey('coach.cid'), nullable=False)
    courseid = db.Column(db.Integer, db.ForeignKey('course.id'), nullable=False)

    def __init__(self, id, cid, courseid):
        self.id = id
        self.cid = cid
        self.courseid = courseid
