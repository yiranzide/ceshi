from routes import *


from models.models import User
from models.models import Node
from models.models import Topic
from models.models import Question
from models.models import Comment


import time


from routes.forums import red

import json


main = Blueprint('comment', __name__)


def current_user():
    uid = session.get('user_id', None)
    if uid is not None:
        u = User.query.get(uid)
        return u


format = '%Y/%m/%d %H:%M:%S'
value = time.localtime(int(time.time()))
dt = time.strftime(format, value)


@main.route('/add', methods=['POST'])
def comment_add():
    form = request.form
    comment = Comment(form)
    u = current_user()
    if u is None:
        return redirect('/login')
    comment.user_id = u.id
    comment.c_time = dt
    comment.save()
    red.incr('comment')
    u = User.query.get(comment.user_id)
    red.lpush('crl', {'node_id': comment.node_id,
               'username': u.username,
               'created_time': comment.created_time,
               'content': comment.content,
               'question_id':comment.question_id})
    # return redirect(url_for('question.question_detail', node_id=comment.node_id,
    #                         topic_id=comment.topic_id,
    #                         q_id=comment.question_id))
    u = User.query.get(comment.user_id)
    data = {
        'name': u.username,
        'time': comment.created_time,
        'content': comment.content,
        'node_id': comment.node_id
    }
    return json.dumps(data)