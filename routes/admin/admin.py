from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from ... import AdminUser, db
from ...models import Report, Post, Comment, Section
from sqlalchemy.orm import joinedload
from datetime import datetime

admin = Blueprint('admin', __name__)

ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = 'admin'

@admin.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.moderation'))
        
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            user = AdminUser(username)
            login_user(user)
            return redirect(url_for('admin.moderation'))
        else:
            flash('Invalid username or password')
    
    return render_template('admin_login.html')

@admin.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    return redirect(url_for('admin.admin_login'))

@admin.route('/admin/moderation')
@login_required
def moderation():
    # Fetch all pending reports, eager load post and comment relationships
    reports = Report.query.options(
        joinedload(Report.post),
        joinedload(Report.comment)
    ).filter_by(status='pending').order_by(Report.created_at.desc()).all()
    pending_posts = Post.query.filter_by(is_approved=False).order_by(Post.created_at.desc()).all()
    return render_template('moderation.html', reports=reports, pending_posts=pending_posts)

@admin.route('/moderation/report_action', methods=['POST'])
@login_required
def report_action():
    data = request.get_json()
    report_id = data.get('report_id')
    action = data.get('action')
    report = Report.query.get(report_id)
    if not report:
        return jsonify({'success': False, 'error': 'Report not found.'}), 404

    if action == 'approve':
        report.status = 'approved'
        report.resolved_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True})
    elif action == 'reject':
        # Optionally, remove the content as well
        if report.post_id and report.post:
            db.session.delete(report.post)
        if report.comment_id and report.comment:
            db.session.delete(report.comment)
        report.status = 'rejected'
        report.resolved_at = datetime.utcnow()
        db.session.commit()
        return jsonify({'success': True})
    else:
        return jsonify({'success': False, 'error': 'Invalid action.'}), 400

@admin.route('/moderation/approve_post', methods=['POST'])
@login_required
def approve_post():
    data = request.get_json()
    post_id = data.get('post_id')
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'success': False, 'error': 'Post not found.'}), 404
    post.is_approved = True
    db.session.commit()
    return jsonify({'success': True})

@admin.route('/moderation/delete_post', methods=['POST'])
@login_required
def delete_post():
    data = request.get_json()
    post_id = data.get('post_id')
    post = Post.query.get(post_id)
    if not post:
        return jsonify({'success': False, 'error': 'Post not found.'}), 404
    db.session.delete(post)
    db.session.commit()
    return jsonify({'success': True})

@admin.route('/moderation/edit_post/<int:post_id>', methods=['GET', 'POST'])
@login_required
def edit_post(post_id):
    post = Post.query.get_or_404(post_id)
    sections = Section.query.all()
    if request.method == 'POST':
        title = request.form.get('title')
        content = request.form.get('content')
        category = request.form.get('category')
        author_name = request.form.get('author_name')
        section_ids = request.form.getlist('sections')
        post.title = title
        post.content = content
        post.category = category
        post.author_name = author_name
        # Update sections
        post.sections = [Section.query.get(int(sid)) for sid in section_ids]
        db.session.commit()
        return redirect(url_for('admin.moderation'))
    return render_template('edit_post.html', post=post, sections=sections)