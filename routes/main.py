from flask import Flask

from forums import main as forum_routes
from user import main as user_routes
from topic import main as topic_routes
from question import main as question_routes
from comment import main as comment_routes

import redis

from models import User
from models import Question
from models import Comment


# from . import app

red = redis.Redis(host='localhost', port=6379, db=0)




# ns = Node.query.all()
# for n in ns:
#     red.lpush('l1', n.name)
# d = red.lrange('l1', 0, 10)
# for i in d:
#     print(i.decode('utf-8'))

# u = User.query.count()
# q = Question.query.count()
# c = Comment.query.count()

# print(u, q, c)
# red.set('user', u)
# red.set('question', q)
# red.set('comment', c)

# qs = Question.query.all()
# for q in qs:
#     red.set(q.id, q.click_count)

# cs = Comment.query.all()
# for c in cs:
#     u = User.query.get(c.user_id)
#     red.lpush('crl', {'node_id': c.node_id,
#                'username': u.username,
#                'created_time': c.created_time,
#                'content': c.content,
#                'question_id':c.question_id})

# l = red.lrange('crl', 0, -1)
# for i in l:
#     print(i.decode('utf-8'))
# red.set('comment', 8)



if __name__ == '__main__':
    app.run(debug=True)