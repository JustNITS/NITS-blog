from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
from ... import db
from ...models import Post, Media, Section
from ..common.video_thumb import create_thumbnail
import os
from bs4 import BeautifulSoup

makepost = Blueprint('makepost', __name__)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['jpg', 'jpeg', 'png', 'gif', 'mp4']

@makepost.route('/make-post', methods=['GET', 'POST'])
def make_post():
    if request.method == 'POST':
        try:
            # Get form data
            title = request.form.get('title')
            category = request.form.get('category')
            content = request.form.get('content')
            author_name = request.form.get('author_name')
            if not author_name or not author_name.strip():
                author_name = "Anonymous"
            subcategory = request.form.get('subcategory')
            # Only concatenate if subcategory exists, is not empty, and is not 'all'
            if subcategory and subcategory.strip():
                category = f"{category} > {subcategory}"

            # Handle suggested placement (sections)
            section_names = request.form.getlist('sections')
            # Always ensure 'recent-posts' is included
            if 'recent-posts' not in section_names:
                section_names.append('recent-posts')
            # Remove duplicates
            section_names = list(set(section_names))

            # Query Section objects for the given names
            sections = []
            for name in section_names:
                section = Section.query.filter_by(name=name).first()
                if section:
                    sections.append(section)
            if not sections:
                raise Exception("No valid section selected.")

            # Here you would typically save the post to a database
            # For now, we'll just return success
            post = Post(
                title=title,
                content=content,
                author_name=author_name,
                ip_address=request.remote_addr,
                category=category,
            )
            # Associate the post with the selected sections
            post.sections.extend(sections)
            db.session.add(post)
            db.session.flush()  # Flush to get the post ID before committing
            
            media_paths = []
            if content:
                # Parse the HTML content to extract media file paths
                soup = BeautifulSoup(content, 'html.parser')
                for tag in soup.find_all(['img', 'video', 'source']):
                    if tag.name == 'source' and tag.parent.name == 'video':
                        src = tag.get('src')
                    else:
                        src = tag.get('src')
                    if src and allowed_file(src):
                        media_paths.append(src)

            for index, path in enumerate(media_paths):
                file_type = 'image' if path.split('.')[-1].lower() in ['jpg', 'jpeg', 'png', 'gif'] else 'video'
                if "static" not in path:
                    continue
                if index == 0 and file_type == 'video':
                    thumbnail_path = create_thumbnail(current_app.config['current_dir'], path)
                    if thumbnail_path:
                        media = Media(
                            file_path=thumbnail_path,
                            file_type='image',  # Thumbnail is an image
                            post_id=post.id
                        )
                        db.session.add(media)
                print(f"Adding media: {path} of type {file_type}")
                media = Media(
                    file_path=path,
                    file_type=file_type,
                    post_id=post.id
                )
                db.session.add(media)
            db.session.commit()
            return jsonify({
                'success': True,
                'message': 'Post created successfully',
                'media_paths': media_paths
            })
            
        except Exception as e:
            return jsonify({
                'success': False,
                'message': str(e)
            }), 500
    
    # GET request: render form with professor names from config
    professor_names = current_app.config['data']['departments']['ComputerScience']['faculty_names']
    return render_template('make_post.html', professor_names=professor_names)