from flask import Blueprint, render_template, request, jsonify, current_app
from werkzeug.utils import secure_filename
from ... import db
from ...models import Media
from datetime import datetime
import os


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ['jpg', 'jpeg', 'png', 'gif', 'mp4', 'avi', 'mov', 'mkv']

upload = Blueprint('upload', __name__)

@upload.route('/upload-file', methods=['POST'])
def upload_file():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    
    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{timestamp}_{filename}"
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
        
        # Ensure the upload folder exists
        os.makedirs(current_app.config['UPLOAD_FOLDER'], exist_ok=True)
        
        file.save(file_path)
        return jsonify({
            'location': f"/static/uploads/{filename}"
        })
    
    return jsonify({'error': 'Invalid file type'}), 400