from routes import *


from models.models import User
from models.models import Node
from models.models import Topic
from models.models import Question
from models.models import Comment


import redis


red = redis.Redis(host='localhost', port=6379, db=0)


main = Blueprint('topic', __name__)


def current_user():
    uid = session.get('user_id', None)
    if uid is not None:
        u = User.query.get(uid)
        return u


@main.route('/add', methods=['POST'])
def topic_add():
    form = request.form
    topic = Topic(form)
    topic.save()
    red.set(topic.id, 1)
    return redirect(url_for('forum.topic_all', nid=topic.node_id))


@main.route('/edit/<int:tid>')
def topic_edit(tid):
    return render_template('topic_edit.html', tId=tid)


@main.route('/update', methods=['POST'])
def topic_update():
    topic_id = request.form.get('tid', None)
    name = request.form.get('name', '')
    t = Topic.query.get(topic_id)
    t.name = name
    t.save()
    return redirect(url_for('forum.topic_all', nid=t.node_id))


@main.route('/delete/<int:tid>')
def topic_delete(tid):
    t = Topic.query.get(tid)
    node_id = t.node_id
    t.delete()
    return redirect(url_for('forum.topic_all', nid=node_id))


@main.route('/all/<int:nid>')
def topic_all(nid):
    red.incr(nid)
    topics_node = Topic.query.filter_by(node_id=nid).all()
    nodes = Node.query.all()
    u = current_user()
    if u is None:
        id = 0
        name = ''
    else:
        id = u.id
        name = u.username
    t = {
        'id': 0
    }
    title = Node.query.get(nid).name
    questions = Question.query.filter_by(node_id=nid).all()
    for q in questions:
        toc = Topic.query.get(q.topic_id)
        u = User.query.get(q.user_id)
        q.name = u.username
        q.topic_name = toc.name
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
    return render_template('index.html', user_id=id, n_id=nid, node=nodes, topic_node=topics_node,
                           t=t, node_title=title, question=questions, shequ=shequ,
                           nodeId=nid, name=name, ml=ml, mt=mt, dl=dl)