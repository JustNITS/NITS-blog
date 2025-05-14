import datetime
from .extensions import db  # <-- Now clean import
import os
from flask import current_app

post_sections = db.Table(
    'post_sections',
    db.Column('post_id', db.Integer, db.ForeignKey('posts.id'), primary_key=True),
    db.Column('section_id', db.Integer, db.ForeignKey('sections.id'), primary_key=True)
)

class Post(db.Model):
    __tablename__ = 'posts'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text, nullable=False)
    author_name = db.Column(db.String(80))  # Optional author name
    ip_address = db.Column(db.String(45), nullable=False)  # IPv4/IPv6 address
    category = db.Column(db.String(50), nullable=False)
    hash_tags = db.Column(db.String(50))  # For professor/student specific posts
    is_approved = db.Column(db.Boolean, default=False)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationships
    sections = db.relationship('Section', secondary='post_sections', back_populates='posts')
    comments = db.relationship('Comment', backref='post', lazy=True, cascade='all, delete-orphan')
    media = db.relationship('Media', backref='post', lazy=True, cascade='all, delete-orphan')
    reports = db.relationship('Report', backref='post', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='post', lazy=True, cascade='all, delete-orphan')

class Comment(db.Model):
    __tablename__ = 'comments'
    
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    author_name = db.Column(db.String(80))
    ip_address = db.Column(db.String(45), nullable=False)
    upvotes = db.Column(db.Integer, default=0)
    downvotes = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('comments.id'))  # For nested replies
    
    # Relationships
    replies = db.relationship('Comment', backref=db.backref('parent', remote_side=[id]), lazy=True)
    reports = db.relationship('Report', backref='comment', lazy=True, cascade='all, delete-orphan')
    votes = db.relationship('Vote', backref='comment', lazy=True, cascade='all, delete-orphan')

class Vote(db.Model):
    __tablename__ = 'votes'
    
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(45), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # 'upvote' or 'downvote'
    content_type = db.Column(db.String(10), nullable=False)  # 'post' or 'comment'
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Foreign keys for either post or comment
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))
    
    # Composite unique constraint to prevent multiple votes from same IP
    __table_args__ = (
        db.UniqueConstraint('ip_address', 'content_type', 'post_id', name='unique_post_vote'),
        db.UniqueConstraint('ip_address', 'content_type', 'comment_id', name='unique_comment_vote'),
    )

class Media(db.Model):
    __tablename__ = 'media'
    
    id = db.Column(db.Integer, primary_key=True)
    file_path = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # image, video, etc.
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'), nullable=False)



# Delete file from disk when Media is deleted
from sqlalchemy import event

@event.listens_for(Media, 'after_delete')
def delete_media_file(mapper, connection, target):
    if target.file_path:
        try:
            # Check if any other Media uses the same file_path
            from sqlalchemy.orm import object_session
            session = object_session(target)
            count = session.query(Media).filter(Media.file_path == target.file_path).count()
            if count == 0:
                file_path = target.file_path
                if not os.path.isabs(file_path):
                    file_path = current_app.config['current_dir'] + file_path
                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception as e:
            print(f"Error deleting file {getattr(target, 'file_path', '')}: {e}")
            pass  # Optionally log error



class Report(db.Model):
    __tablename__ = 'reports'
    
    id = db.Column(db.Integer, primary_key=True)
    reason = db.Column(db.String(100), nullable=False)
    ip_address = db.Column(db.String(45), nullable=False)  # IPv4/IPv6 address
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    resolved_at = db.Column(db.DateTime)
    
    # Polymorphic relationships for reported content
    post_id = db.Column(db.Integer, db.ForeignKey('posts.id'))
    comment_id = db.Column(db.Integer, db.ForeignKey('comments.id'))

class Section(db.Model):
    __tablename__ = 'sections'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.datetime.utcnow)
    
    # Relationship with Post
    posts = db.relationship('Post', secondary='post_sections', back_populates='sections')

# Initialize database
def init_db(app):
    db.init_app(app)
    with app.app_context():
        db.create_all()
        
        # Create default sections if they don't exist
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