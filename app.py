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
