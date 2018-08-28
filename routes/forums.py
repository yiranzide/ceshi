from routes import *


from models.models import User
from models.models import Node
from models.models import Topic
from models.models import Question
from models.models import Comment


import redis


red = redis.Redis(host='localhost', port=6379, db=0)


main = Blueprint('forum', __name__)



def current_user():
    uid = session.get('user_id', None)
    if uid is not None:
        u = User.query.get(uid)
        return u


@main.route('/')
def index():
    ns = Node.query.all()
    for n in ns:
        red.lpush('l1', n.name)
    # d = red.lrange('l1', 0, 10)
    # for i in d:
    #     print(i.decode('utf-8'))

    u = User.query.count()
    q = Question.query.count()
    c = Comment.query.count()

    # print(u, q, c)
    red.set('user', u)
    red.set('question', q)
    red.set('comment', c)

    qs = Question.query.all()
    for q in qs:
        red.set(q.id, q.click_count)

    cs = Comment.query.all()
    for c in cs:
        u = User.query.get(c.user_id)
        red.lpush('crl', {'node_id': c.node_id,
                          'username': u.username,
                          'created_time': c.created_time,
                          'content': c.content,
                          'question_id': c.question_id})

    # l = red.lrange('crl', 0, -1)
    # for i in l:
    #     print(i.decode('utf-8'))
    red.set('comment', 8)
    u = current_user()
    if u is None:
        id = 0
        name = ''
    else:
        id = u.id
        name = u.username
    nodes = Node.query.all()
    topics = Topic.query.all()
    t = {
        'id': 0
    }
    node = Node.query.get(1)
    if node is None:
        title = ''
    else:
        title = node.name
    topic_nodes = Topic.query.filter_by(node_id=1).all()
    questions = Question.query.filter_by(node_id=1).all()
    for q in questions:
        top = Topic.query.get(q.topic_id)
        u = User.query.get(q.user_id)
        q.name = u.username
        q.topic_name = top.name
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
        dl.append((dname, dn_id))
    dl = dl[:10]
    shequ = [red.get('user').decode('utf-8'),
             red.get('question').decode('utf-8'),
             red.get('comment').decode('utf-8')
    ]
    return render_template('index.html', user_id=id, name=name, node=nodes, topic=topics,
                           t=t, topic_node=topic_nodes, question=questions, node_title=title,
                           nodeId=1, n_id=1, ml=ml, mt=mt, dl=dl, shequ=shequ)


@main.route('/<int:node_id>')
def node_index(node_id):
    u = current_user()
    if u is None:
        id = 0
        name = ''
    else:
        id = u.id
        name = u.username
    nodes = Node.query.all()
    topics = Topic.query.all()
    t = {
        'id': 0
    }
    node = Node.query.get(node_id)
    if node is None:
        title = ''
    else:
        title = node.name
    topic_nodes = Topic.query.filter_by(node_id=node_id).all()
    questions = Question.query.filter_by(node_id=node_id).all()
    for q in questions:
        top = Topic.query.get(q.topic_id)
        u = User.query.get(q.user_id)
        q.name = u.username
        q.topic_name = top.name
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
    # print('shuqu', shequ)
    return render_template('index.html', user_id=id, name=name, node=nodes, topic=topics,
                           t=t, topic_node=topic_nodes, question=questions, node_title=title,
                           nodeId=node_id, n_id=node_id, ml=ml, mt=mt, dl=dl, shequ=shequ)


@main.route('/add', methods=['POST'])
def node_add():
    form = request.form
    n = Node(form)
    n.save()
    red.set(n.id, 1)
    red.lpush('l', n.name)
    return redirect(url_for('.index'))


@main.route('/edit/<int:nid>')
def node_edit(nid):
    return render_template('node_edit.html', nId=nid)


@main.route('/update', methods=['POST'])
def node_update():
    node_id = request.form.get('nid', None)
    name = request.form.get('name', '')
    n = Node.query.get(node_id)
    n.name = name
    n.save()
    return redirect(url_for('.index'))


@main.route('/delete/<int:nid>')
def node_delete(nid):
    node = Node.query.get(nid)
    node.delete()
    return redirect(url_for('.index'))


@main.route('/node/topic/<int:nid>')
def topic_all(nid):
    topics = Topic.query.filter_by(node_id=nid).all()
    return render_template('topic_all.html', nid=nid, topic=topics)