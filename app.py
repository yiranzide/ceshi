from flask import Flask
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager

from models import db
# 这里 import 具体的 Model 类是为了给 migrate 用
# 如果不 import 那么无法迁移
# 这是 SQLAlchemy 的机制
from models.models import User
from models.models import Node
from models.models import Topic
from models.models import Comment
from models.models import Question


import redis


app = Flask(__name__)
db_path = 'forums.sqlite'
manager = Manager(app)

red = redis.Redis(host='localhost', port=6379, db=0)




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
               'question_id':c.question_id})

# l = red.lrange('crl', 0, -1)
# for i in l:
#     print(i.decode('utf-8'))
red.set('comment', 8)


def register_routes(app):
    from routes.forums import main as forum_routes
    from routes.user import main as user_routes
    from routes.topic import main as topic_routes
    from routes.question import main as question_routes
    from routes.comment import main as comment_routes

    app.register_blueprint(forum_routes)
    app.register_blueprint(user_routes)
    app.register_blueprint(topic_routes, url_prefix='/topic')
    app.register_blueprint(question_routes, url_prefix='/question')
    app.register_blueprint(comment_routes, url_prefix='/comment')


def configure_app():
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.secret_key = 'secret key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///{}'.format(db_path)
    # app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:pwd@localhost/bbs'
    db.init_app(app)
    register_routes(app)


def configured_app():
    configure_app()
    return app


# 自定义的命令行命令用来运行服务器
@manager.command
def server():
    print('server run')
    # app = configured_app()
    config = dict(
        debug=True,
        host='0.0.0.0',
        port=5000,
    )
    app.run(**config)


def configure_manager():
    """
    这个函数用来配置命令行选项
    """
    Migrate(app, db)
    manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    configure_manager()
    configure_app()
    manager.run()
    # server()

# gunicorn -b '0.0.0.0:80' redischat:app
