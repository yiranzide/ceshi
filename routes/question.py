from routes import *


from models.models import User
from models.models import Node
from models.models import Topic
from models.models import Question
from models.models import Comment


main = Blueprint('question', __name__)

from routes.forums import red

import json


def current_user():
    uid = session.get('user_id', None)
    if uid is not None:
        u = User.query.get(uid)
        return u


@main.route('/all/<int:n_id>/<int:t_id>')
def question_all(n_id, t_id):
    topic = Topic.query.get(t_id)
    print('here')
    topics_node = Topic.query.filter_by(node_id=n_id).all()
    nodes = Node.query.all()
    topics = Topic.query.all()
    node = Node.query.get(n_id)
    if node is None:
        title = ''
    else:
        title = node.name
    u = current_user()
    if u is None:
        # return redirect('/login')
        id = 0
        name = ''
    else:
        id = u.id
        name = u.username
    questions = Question.query.filter_by(topic_id=t_id).all()
    for q in questions:
        user = User.query.get(q.user_id)
        q.name = user.username
        q.topic_name = topic.name
        c = Comment.query.filter_by(question_id=q.id).order_by(Comment.created_time.desc()).first()
        if c is None:
            c_name = ''
        else:
            c.name = User.query.get(c.user_id).username
            c_name = c.name
        q.commentName = c_name
        q.count = len(Comment.query.filter_by(question_id=q.id).all())
    l = []
    for n in nodes:
        key = red.get(n.id)
        l.append(int(key.decode('utf-8')))
    l.sort()
    # print('newl', l)
    l.reverse()
    l = l[:10]
    # print('ll', l)
    ml = []
    for n in nodes:
        key = red.get(n.id)
        if int(key.decode('utf-8')) in l:
            # print(n.id)
            ml.append((n.name, n.id))
    ml = ml[:10]
    que = Question.query.all()
    tt = []
    for q in que:
        key = red.get(q.id)
        tt.append(int(key.decode('utf-8')))
    tt.sort()
    # print('newl', l)
    tt.reverse()
    tt = tt[:10]
    # print('ll', l)
    mt = []
    for q in que:
        key = red.get(q.id)
        if int(key.decode('utf-8')) in tt:
            # print(n.id)
            u = User.query.get(q.user_id)
            mt.append((q.title, q.node_id, u.username, q.topic_id, q.id))
    mt = mt[:10]
    dl = []
    d = red.lrange('l1', 0, 10)
    for i in d:
        dname = i.decode('utf-8')
        dn_id = Node.query.filter_by(name=dname).first().id
        dl.append((i.decode('utf-8'), dn_id))
    dl = dl[:10]
    shequ = [red.get('user').decode('utf-8'),
             red.get('question').decode('utf-8'),
             red.get('comment').decode('utf-8')
    ]
    return render_template('index.html', user_id=id, node=nodes, topic_node=topics_node,
                           question = questions, t=topic, node_title=title, mt=mt, dl=dl,
                           q_n_id=n_id, n_id=n_id, nodeId=n_id, name=name, ml=ml, shequ=shequ)


@main.route('/add/<int:n_id>/<int:t_id>')
def question_add(n_id, t_id):
    u = current_user()
    if u is None:
        return redirect('/login')
    else:
        name = u.username
    node = Node.query.get(n_id)
    if node is None:
        title = ''
    else:
        title = node.name
    return render_template('question_add.html', name=name, n_id=n_id, nId=n_id, tId=t_id, node_title=title)


@main.route('/publish', methods=['POST'])
def question_publish():
    form = request.form
    question = Question(form)
    u = current_user()
    question.user_id = u.id
    question.save()
    red.incr('question')
    return redirect(url_for('.question_all', n_id=question.node_id, t_id=question.topic_id))


@main.route('/detail/<int:node_id>/<int:topic_id>/<int:q_id>')
def question_detail(node_id, topic_id, q_id):
    # red.incr(q_id)
    u = current_user()
    if u is None:
        id = 0
        name = ''
    else:
        red.incr(q_id)
        id = u.id
        name = u.username
    question = Question.query.get(q_id)
    if u is not None:
       question.click_count += 1
       question.save()
    count = len(Comment.query.filter_by(question_id=q_id).all())
    title = question.title
    topic_name = Topic.query.get(topic_id).name
    u = User.query.get(question.user_id)
    username = u.username
    created_time = question.created_time
    content = question.content
    # comments = Comment.query.filter_by(question_id=q_id).order_by(Comment.created_time.desc()).all()
    cl = red.lrange('crl', 0, -1)
    comments = []
    for i in cl:
        i = eval(i.decode('utf-8'))
        # print(type(i))
        if i['question_id'] == q_id:
            comments.append(i)
    print(comments)
    new_c = Comment.query.filter_by(question_id=q_id).order_by(Comment.c_time.desc()).first()
    if new_c is None:
        new_time = ''
    else:
        new_time = new_c.c_time
    # for c in comments:
    #     u = User.query.get(c.user_id)
    #     c.username = u.username
    ccount = red.get(q_id).decode('utf-8')
    return render_template('question_detail.html', qId=q_id, qTiele=title, ticName=topic_name,
                           topicId=topic_id, d_nodeId=node_id, username=username, n_id=node_id,
                           created_time=created_time, content=content, comment=comments, user_id=id,
                           name = name, count=count, newTime=new_time,
                           # clickCount = question.click_count,
                           clickCount = ccount
                           )