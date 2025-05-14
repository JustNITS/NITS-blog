from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
from ... import db
from ...models import Post, Comment, Report
from datetime import datetime
import os

report = Blueprint('report', __name__)

@report.route('/report', methods=['POST'])
def makereport():
    data = request.form or request.json
    content_type = data.get('content_type')
    content_id = data.get('content_id')
    reason = data.get('reason')
    ip_address = request.remote_addr

    if not content_type or not content_id or not reason:
        return jsonify({'success': False, 'error': 'Missing required fields.'}), 400

    try:
        content_id = int(content_id)
    except Exception:
        return jsonify({'success': False, 'error': 'Invalid content_id.'}), 400

    report_kwargs = {
        'reason': reason,
        'ip_address': ip_address,
        'created_at': datetime.utcnow(),
        'status': 'pending'
    }

    if content_type == 'post':
        post = Post.query.get(content_id)
        if not post:
            return jsonify({'success': False, 'error': 'Post not found.'}), 404
        report_kwargs['post_id'] = content_id
    elif content_type == 'comment':
        comment = Comment.query.get(content_id)
        if not comment:
            return jsonify({'success': False, 'error': 'Comment not found.'}), 404
        report_kwargs['comment_id'] = content_id
    else:
        return jsonify({'success': False, 'error': 'Invalid content_type.'}), 400

    new_report = Report(**report_kwargs)
    db.session.add(new_report)
    db.session.commit()

    return jsonify({'success': True, 'message': 'Report submitted.'})