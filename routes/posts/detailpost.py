from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
from ... import db
from ...models import Post, Comment, Section
from ..common.common import picktwo
from datetime import datetime
import os


detailpost = Blueprint('detailpost', __name__)


@detailpost.route('/<post_type>/post-<post_id>', methods=['GET'])
def post_detail(post_type, post_id):
    if not post_id.isdigit():
        return jsonify({'error': 'Invalid post ID'}), 400

    post = Post.query.get(post_id)
    
    if not post:
        return jsonify({'error': 'Post not found'}), 404

    # Ensure post_type matches a section the post belongs to
    section = Section.query.filter_by(name=post_type).first()
    if not section or section not in post.sections:
        return jsonify({'error': 'Post not found in this section'}), 404

    comments = post.comments
    return render_template('detailpost.html', post=post, comments=comments)

@detailpost.route('/make_comment', methods=['POST'])
def make_comment():
    post_id = request.form.get('post_id')
    author_name = author_name = ' '.join(picktwo(request.remote_addr))
    content = request.form.get('content')

    if not post_id or not content:
        return jsonify({'error': 'Post ID and content are required'}), 400

    post = Post.query.get(post_id)
    
    if not post:
        return jsonify({'error': 'Post not found'}), 404

    comment = Comment(
        post_id=post.id,
        author_name=author_name,
        content=content,
        created_at=datetime.utcnow(),
        ip_address=request.remote_addr
    )
    
    db.session.add(comment)
    db.session.commit()

    return jsonify({'message': 'Comment added successfully'}), 201

@detailpost.route('/make_reply', methods=['POST'])
def make_reply():
    post_id = request.form.get('post_id')
    parent_id = request.form.get('parent_id')
    author_name = ' '.join(picktwo(request.remote_addr))
    content = request.form.get('content')

    if not post_id or not parent_id or not content:
        return jsonify({'error': 'Post ID, parent comment ID, and content are required'}), 400

    post = Post.query.get(post_id)
    if not post:
        return jsonify({'error': 'Post not found'}), 404

    parent_comment = Comment.query.get(parent_id)
    if not parent_comment:
        return jsonify({'error': 'Parent comment not found'}), 404

    reply = Comment(
        parent_id=parent_comment.id,
        author_name=author_name,
        content=content,
        created_at=datetime.utcnow(),
        ip_address=request.remote_addr
    )

    db.session.add(reply)
    db.session.commit()

    return jsonify({'message': 'Reply added successfully'}), 201