from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
from ... import db
from ...models import Post, Comment, Vote
import os


vote = Blueprint('vote', __name__)

@vote.route('/vote', methods=['POST'])
def makevote():
    ip_address = request.remote_addr
    content_type = request.form.get('content_type')  # 'post', 'comment', or 'reply'
    content_id = request.form.get('content_id')
    vote_type = request.form.get('vote_type')  # 'upvote' or 'downvote'
    
    try:
        # Normalize: treat 'reply' as 'comment' for DB purposes
        db_content_type = 'comment' if content_type in ('comment', 'reply') else 'post'
        id_field = f'{db_content_type}_id'

        # Check if vote already exists
        existing_vote = Vote.query.filter_by(
            ip_address=ip_address,
            content_type=db_content_type,
            **{id_field: content_id}
        ).first()
        
        if existing_vote:
            # Update existing vote
            if existing_vote.vote_type != vote_type:
                # Change vote type
                if db_content_type == 'post':
                    post = Post.query.get(content_id)
                    if existing_vote.vote_type == 'upvote':
                        post.upvotes -= 1
                        post.downvotes += 1
                    else:
                        post.upvotes += 1
                        post.downvotes -= 1
                else:
                    comment = Comment.query.get(content_id)
                    if existing_vote.vote_type == 'upvote':
                        comment.upvotes -= 1
                        comment.downvotes += 1
                    else:
                        comment.upvotes += 1
                        comment.downvotes -= 1
                existing_vote.vote_type = vote_type
            
            if db_content_type == 'post':
                post = Post.query.get(content_id)
                upvotes = post.upvotes
                downvotes = post.downvotes
            else:
                comment = Comment.query.get(content_id)
                upvotes = comment.upvotes
                downvotes = comment.downvotes
        else:
            # Create new vote
            vote = Vote(
                ip_address=ip_address,
                content_type=db_content_type,
                vote_type=vote_type,
                **{id_field: content_id}
            )
            db.session.add(vote)
            
            # Update vote counts
            if db_content_type == 'post':
                post = Post.query.get(content_id)
                if vote_type == 'upvote':
                    post.upvotes += 1
                else:
                    post.downvotes += 1
                upvotes = post.upvotes
                downvotes = post.downvotes
            else:
                comment = Comment.query.get(content_id)
                if vote_type == 'upvote':
                    comment.upvotes += 1
                else:
                    comment.downvotes += 1
                upvotes = comment.upvotes
                downvotes = comment.downvotes
        
        db.session.commit()
        return jsonify({'success': True, 'upvotes': upvotes, 'downvotes': downvotes})
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)})