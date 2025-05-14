from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
from ... import db
from ...models import Post, Media, Section


thumbpost = Blueprint('thumbpost', __name__)

@thumbpost.route('/notice-board')
@thumbpost.route('/recent-posts')
@thumbpost.route('/feature-posts')
@thumbpost.route('/top-posts')
@thumbpost.route('/confessions')
@thumbpost.route('/buy-sell')
def common_posts():
    # Get the current path to determine post type
    path = request.path.strip('/')

    # Find the section by name
    section = Section.query.filter_by(name=path).first()
    if section:
        post_query = (
            Post.query
            .join(Post.sections)
            .filter(Section.id == section.id)
        )
        if path != 'recent-posts':
            post_query = post_query.filter(Post.is_approved == True)
        if path == 'top-posts':
            posts = (
                post_query
                .order_by(Post.upvotes.desc())
                .limit(10)
                .all()
            )
        else:
            posts = (
                post_query
                .order_by(Post.created_at.desc())
                .limit(10)
                .all()
            )
    else:
        posts = []

    thumbnail = {}
    for post in posts:
        # Get the first media file associated with the post
        media = Media.query.filter_by(post_id=post.id).first()
        if media:
            thumbnail[post.id] = media.file_path
        else:
            thumbnail[post.id] = None
    titles = {
        'notice-board': 'Official notices and announcements',
        'recent-posts': 'Most recent posts',
        'feature-posts': 'Featured and highlighted posts',
        'top-posts': 'Most popular and trending posts',
        'confessions': 'Anonymous confessions',
        'buy-sell': 'Buy or Sell items'
    }

    return render_template('thumbposts.html', 
                        posts=posts, 
                        title=titles.get(path, 'Posts'),
                        post_type=path, thumbnails=thumbnail)