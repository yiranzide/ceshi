from routes import *

from models.models import User
from models.models import Node
from models.models import Question
from models.models import Topic
from models.models import Comment

import json


from routes.forums import red


import hashlib


main = Blueprint('user',__name__)


def current_user():
    uid = session.get('user_id', None)
    if uid is not None:
        u = User.query.get(uid)
        return u


@main.route('/login')
def login():
    result = ''
    id = 0
    return render_template('user_login.html', result=result, user_id=id)


@main.route('/register')
def register():
    result = ''
    id = 0
    return render_template('user_register.html', result=result, user_id=id)


@main.route('/register/form', methods=['POST'])
def register_form():
    form = request.form
    u = User(form)
    user = User.query.filter_by(username=u.username).first()
    if user is not None:
        result = '用户名已经存在'
        id = 0
    elif user is None and u.valid():
        u.save()
        result = '注册成功'
        id = u.id
        red.incr('user')
        return redirect('/login')
    else:
        result = '用户名或者密码的长度必须大于2个字符'
        id = 0
    return render_template('user_register.html', result=result, user_id=id)


@main.route('/login/form', methods=['POST'])
def login_form():
    form = request.form
    u = User(form)
    user = User.query.filter_by(username=u.username).first()
    if user is None:
        result = '用户不存在'
        id = 0
    elif user.validate(u):
        session['user_id'] = user.id
        return redirect('/')
    else:
        result = '用户名或者密码错误'
        id = 0
    return render_template('user_login.html', result=result, user_id=id)


@main.route('/login_out')
def login_out():
    session['user_id'] = ''
    id = 0
    result = ''
    return render_template('user_login.html', result=result, user_id=id)


@main.route('/index/<int:node_id>/<name>')
def index_name(node_id, name):
    node = Node.query.get(node_id)
    title = node.name
    u = User.query.filter_by(username=name).first()
    u_id = u.id
    questions = Question.query.filter_by(user_id=u_id).all()
    for q in questions:
        t = Topic.query.get(q.topic_id)
        q.name = t.name
        q.count = len(Comment.query.filter_by(question_id=q.id).all())
        c_l = Comment.query.filter_by(question_id=q.id).order_by(Comment.created_time.desc()).first()
        if c_l is None:
            q.last_name = ''
        else:
            c_l_name = User.query.get(c_l.user_id)
            q.last_name = c_l_name.username
    comments = Comment.query.filter_by(user_id=u_id).all()
    for c in comments:
        cct = Question.query.get(c.question_id)
        c.title = cct.title
        un = User.query.get(cct.user_id)
        c.username = un.username
        cqn = Topic.query.get(c.topic_id)
        c.top_name = cqn.name
    return render_template('user_index.html', u_name=name, n_id=node_id,
                           node_title=title, uId=u_id, time=u.created_time,
                           name=name, question=questions,
                           comment = comments, mark=0)


# @main.route('/user/question', methods=['POST'])
@main.route('/user/question/<int:node_id>/<u_name>')
def user_question(node_id, u_name):
    # form = request.form
    # node_id = form.get('node_id', None)
    # questions = Question.query.filter_by(node_id=node_id).order_by(Question.created_time.desc()).all()
    # # print(type(questions))
    # # question = str(questions)
    # questions = str(questions)
    # return questions
    questions = Question.query.all()
    u = current_user()
    name = u_name
    node = Node.query.get(node_id)
    title = node.name
    u = User.query.filter_by(username=name).first()
    u_id = u.id
    questions = Question.query.filter_by(user_id=u_id, node_id=node_id).all()
    for q in questions:
        t = Topic.query.get(q.topic_id)
        q.name = t.name
        q.count = len(Comment.query.filter_by(question_id=q.id).all())
        c_l = Comment.query.filter_by(question_id=q.id).order_by(Comment.created_time.desc()).first()
        if c_l is None:
            q.last_name = ''
        else:
            c_l_name = User.query.get(c_l.user_id)
            q.last_name = c_l_name.username
    comments = Comment.query.filter_by(user_id=u_id, node_id=node_id).all()
    for c in comments:
        cct = Question.query.get(c.question_id)
        c.title = cct.title
        un = User.query.get(cct.user_id)
        c.username = un.username
        cqn = Topic.query.get(c.topic_id)
        c.top_name = cqn.name
    return render_template('user_index.html', u_name=name, n_id=node_id,
                           node_title=title, uId=u_id, time=u.created_time,
                           name=name, question=questions,
                           comment=comments)


@main.route('/user/comment/replies/<int:n_id>/<u_name>')
def comment_replies(n_id, u_name):
    u = User.query.filter_by(username=u_name).first()
    u_id = u.id
    if n_id == 0:
        node = Node.query.get(1)
        title = node.name
        comments = Comment.query.filter_by(user_id=u_id).all()
        n_id = 1
    else:
        node = Node.query.get(n_id)
        title = node.name
        comments = Comment.query.filter_by(user_id=u_id, node_id=n_id).all()
    for c in comments:
        cct = Question.query.get(c.question_id)
        c.title = cct.title
        un = User.query.get(cct.user_id)
        c.username = un.username
        cqn = Topic.query.get(c.topic_id)
        c.top_name = cqn.name
    return render_template('comment-reply.html',u_name=u_name, n_id=n_id,
                           node_title=title, uId=u_id, time=u.created_time,
                           name=u_name,
                           comment=comments)