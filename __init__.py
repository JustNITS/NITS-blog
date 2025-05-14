# __init__.py
import json
from flask import Flask
from .extensions import db, login_manager
from .models import Section
from flask_login import UserMixin
import os

current_dir = os.path.basename(os.path.dirname(__file__)) +'/'

class AdminUser(UserMixin):
    def __init__(self, user_id):
        self.id = user_id

with open(current_dir + 'config.json', 'r') as file:
    config = json.load(file)

def create_app():
    app = Flask(__name__)
    from .commands import create_db
    app.cli.add_command(create_db)

    app.config['SECRET_KEY'] = "settings.secret_key"
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:123456ABC.@localhost/college'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 280}
    app.config['current_dir'] = current_dir
    app.config['UPLOAD_FOLDER'] = app.config['current_dir']+'/static/uploads'
    app.config['data'] = config
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'admin_login'

    with app.app_context():
        db.create_all()
        default_sections = [
            ('notice-board', 'Official notices and announcements'),
            ('feature-posts', 'Featured and highlighted posts'),
            ('recent-posts', 'Most recent posts'),
            ('top-posts', 'Most popular and trending posts'),
            ('confessions', 'Anonymous confessions'),
            ('buy-sell', 'Buy or Sell items'),
        ]

        for name, description in default_sections:
            if not Section.query.filter_by(name=name).first():
                section = Section(name=name, description=description)
                db.session.add(section)

        db.session.commit()
        print("Database initialized successfully!")

    @login_manager.user_loader
    def load_user(user_id):
        if user_id == 'admin':
            return AdminUser(user_id)
        return None

    # Register Blueprints
    from .routes.admin.admin import admin
    app.register_blueprint(admin)

    from .routes.common.common import common
    app.register_blueprint(common)

    from .routes.common.vote import vote
    app.register_blueprint(vote)

    from .routes.common.report import report
    app.register_blueprint(report)

    from .routes.common.upload import upload
    app.register_blueprint(upload)

    from .routes.posts.detailpost import detailpost
    app.register_blueprint(detailpost)

    from .routes.posts.makepost import makepost
    app.register_blueprint(makepost)

    from .routes.posts.thumbpost import thumbpost
    app.register_blueprint(thumbpost)

    return app
