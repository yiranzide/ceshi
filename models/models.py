from . import ModelMixin
from . import db
from . import timestamp


import time


import hashlib



format = '%Y/%m/%d %H:%M:%S'
value = time.localtime(int(time.time()))
dt = time.strftime(format, value)


class User(db.Model, ModelMixin):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String())
    password = db.Column(db.String())
    comments = db.relationship('Comment', backref='user', foreign_keys='Comment.user_id')
    questions = db.relationship('Question', backref='user', foreign_keys='Question.user_id')
    created_time = db.Column(db.String())


    def __init__(self, form):
        self.username = form.get('username', '')
        self.password = form.get('password', '')
        self.created_time = dt

    def valid(self):
        return len(self.username) > 2 and len(self.password) > 2

    def validate(self, u):
        salt = 'this is a secret'
        pw = u.password.encode('ascii')
        hash1 = hashlib.sha1(pw).hexdigest()
        hash2 = hashlib.sha1((hash1 + salt).encode('ascii')).hexdigest()
        if hash2 == self.password:
            self.password = u.password
        else:
            return False
        return self is not None and self.username == u.username and self.password == u.password

    def save(self):
        salt = 'this is a secret'
        pw = self.password.encode('ascii')
        hash1 = hashlib.sha1(pw).hexdigest()
        hash2 = hashlib.sha1((hash1 + salt).encode('ascii')).hexdigest()
        self.password = hash2
        db.session.add(self)
        db.session.commit()


class Node(db.Model, ModelMixin):
    __tablename__ = 'nodes'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    topics = db.relationship('Topic', backref='node', foreign_keys='Topic.node_id')
    questions = db.relationship('Question', backref='node', foreign_keys='Question.node_id')
    created_time = db.Column(db.String())


    def __init__(self, form):
        self.name = form.get('name', '')
        self.created_time = dt


class Topic(db.Model, ModelMixin):
    __tablename__ = 'topics'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String())
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'))
    comments = db.relationship('Comment', backref='topic', foreign_keys='Comment.topic_id')
    questions = db.relationship('Question', backref='topic', foreign_keys='Question.topic_id')
    created_time = db.Column(db.String())

    def __init__(self, form):
        self.name = form.get('name', '')
        self.node_id = form.get('node_id', None)
        self.created = dt


class Comment(db.Model, ModelMixin):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))
    content = db.Column(db.String())
    created_time = db.Column(db.String())
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'))
    question_id = db.Column(db.Integer, db.ForeignKey('questions.id'))
    c_time = db.Column(db.String())

    def __init__(self, form):
        self.user_id = form.get('user_id', None)
        self.content = form.get('content', '')
        self.topic_id = form.get('topic_id', None)
        self.node_id = form.get('node_id', None)
        self.question_id = form.get('question_id', None)
        self.created_time = int(time.time())
        self.c_time = dt


class Question(db.Model, ModelMixin):
    __tablename__ = 'questions'
    id = db.Column(db.Integer, primary_key=True)
    topic_id = db.Column(db.Integer, db.ForeignKey('topics.id'))
    content = db.Column(db.String())
    title = db.Column(db.String())
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    node_id = db.Column(db.Integer, db.ForeignKey('nodes.id'))
    created_time = db.Column(db.String())
    q_time = db.Column(db.String())
    click_count = db.Column(db.Integer)
    click_name = db.Column(db.String())

    def __init__(self, form):
        self.content = form.get('content', '')
        self.topic_id = form.get('topic_id', None)
        self.user_id = form.get('user_id', None)
        self.node_id = form.get('node_id', None)
        self.title = form.get('title', '')
        self.created_time = int(time.time())
        self.q_time = dt
        self.count = 0
        self.click_count = form.get('click_count', 0)
        self.click_name = form.get('click_name', '')
