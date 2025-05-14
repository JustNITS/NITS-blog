import hashlib
from flask import Blueprint, render_template, current_app
from ...models import Post, Section  # Add import

common = Blueprint('common', __name__)

@common.route('/')
@common.route('/home')
def home():
    # Fetch up to 4 posts for each section
    featured_section = Section.query.filter_by(name='feature-posts').first()
    recent_section = Section.query.filter_by(name='recent-posts').first()
    top_section = Section.query.filter_by(name='top-posts').first()
    notice_section = Section.query.filter_by(name='notice-board').first()
    confessions_section = Section.query.filter_by(name='confessions').first()
    buysell_section = Section.query.filter_by(name='buy-sell').first()

    featured_posts = []
    recent_posts = []
    top_posts = []
    notice_posts = []
    confessions_posts = []
    buysell_posts = []

    if featured_section:
        featured_posts = (
            Post.query
            .join(Post.sections)
            .filter(Section.id == featured_section.id)
            .filter(Post.is_approved == True)
            .order_by(Post.created_at.desc())
            .limit(4)
            .all()
        )
    if recent_section:
        recent_posts = (
            Post.query
            .join(Post.sections)
            .filter(Section.id == recent_section.id)
            .order_by(Post.created_at.desc())
            .limit(4)
            .all()
        )
    if top_section:
        top_posts = (
            Post.query
            .join(Post.sections)
            .filter(Section.id == top_section.id)
            .filter(Post.is_approved == True)
            .order_by(Post.upvotes.desc())
            .limit(4)
            .all()
        )
    if notice_section:
        notice_posts = (
            Post.query
            .join(Post.sections)
            .filter(Section.id == notice_section.id)
            .filter(Post.is_approved == True)
            .order_by(Post.created_at.desc())
            .limit(4)
            .all()
        )
    if confessions_section:
        confessions_posts = (
            Post.query
            .join(Post.sections)
            .filter(Section.id == confessions_section.id)
            .filter(Post.is_approved == True)
            .order_by(Post.created_at.desc())
            .limit(4)
            .all()
        )
    if buysell_section:
        buysell_posts = (
            Post.query
            .join(Post.sections)
            .filter(Section.id == buysell_section.id)
            .filter(Post.is_approved == True)
            .order_by(Post.created_at.desc())
            .limit(4)
            .all()
        )

    return render_template(
        'home.html',
        featured_posts=featured_posts,
        recent_posts=recent_posts,
        top_posts=top_posts,
        notice_posts=notice_posts,
        confessions_posts=confessions_posts,
        buysell_posts=buysell_posts
    )


def picktwo(s):
    name = current_app.config['data']['random_names']
    h = hashlib.md5(s.encode()).hexdigest()
    i1 = int(h[:8], 16) % len(name)
    i2 = int(h[8:16], 16) % len(name)
    
    return [name[i1], name[i2]]
