# File Upload/ Download
# TODO: AUTH!!!
import os
import safrs
import subprocess
import logging
import shutil
import tempfile

from flask import Flask, request, redirect, flash, jsonify, send_from_directory, abort
from werkzeug.utils import secure_filename
from pathlib import Path
from database.models import File, Project, PROJ_ROOT
from ulid import ULID

log = logging.getLogger("api_logic_server_app")

def customize_app(app: Flask):
    app.config['UPLOAD_FOLDER'] = os.getenv("UPLOAD_FOLDER", '/opt/projects/uploads')
    app.config['ALLOWED_EXTENSIONS'] = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
    app.secret_key = 'supersecretkey'

    @app.route('/upload', methods=['GET', 'POST'])
    def upload_file():
        if request.method == 'POST':
            # Check if the post request has the file part
            if 'file' not in request.files:
                flash('No file part')
                return redirect(request.url)
            file = request.files['file']
            #If the user does not select a file, the browser submits an empty file without a filename
            if file.filename == '':
                flash('No selected file')
                return redirect(request.url)
            if file: # and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                id_ = str(ULID())
                file_instance = File(name=filename)
                safrs.DB.session.add(file_instance)
                safrs.DB.session.commit()
                upload_dir = Path(app.config['UPLOAD_FOLDER']) / file_instance.id
                upload_dir.mkdir(parents=True, exist_ok=True)
                file.save(upload_dir / filename )
                
                return jsonify({"message": "File uploaded successfully",
                                "filename": filename,
                                "path" : file_instance.path,
                                "connection_string": file_instance.connection_string,
                                "id": file_instance.id})
        return '''
        <!doctype html>
        <title>Upload new File</title>
        <h1>Upload new File</h1>
        <form method=post enctype=multipart/form-data>
        <input type=file name=file>
        <input type=submit value=Upload>
        </form>
        '''
    
    @app.route('/download', methods=['GET'])
    def download_file():
        """
        Download a file
        """
        filename = request.args.get('filename')
        project_id = request.args.get('project_id')
        if project_id:
            return download_project(project_id)
        
        if not filename or not '/' in filename:
            abort(400, description="Filename parameter is required")
        
        id, filename = filename.split('/')
        folder = Path(app.config['UPLOAD_FOLDER']) / secure_filename(id)
        if not folder.exists() or not (folder / filename).exists():
            abort(404, description="File not found")
        
        return send_from_directory(folder, filename, as_attachment=True)
    
    @app.route('/download_project/<string:project_id>', methods=['GET'])
    def download_project(project_id):
        """
        tar project and send it to the user
        """
        project_id = secure_filename(project_id)
        project = safrs.DB.session.query(Project).get(project_id)
        if not project or not project.path.exists():
            abort(404, description="Project not found")
        filename = f"{project.name}.tgz"
        try:
            temp_dir = Path(tempfile.mkdtemp())
            subprocess.check_output(["tar", "-czf",  filename, project.name], cwd=PROJ_ROOT, stderr=subprocess.STDOUT, universal_newlines=True)
            shutil.move(PROJ_ROOT / filename, temp_dir / filename)
        except subprocess.CalledProcessError as e:
            log.error(f"download_project tar error: {e} - {e.output}")
            abort(500, description="Project tar error")
        except Exception as e:
            log.error(f"download_project tar error: {e}")
            abort(500, description="Project tar error")
            
        return send_from_directory(temp_dir, filename, as_attachment=True)
        
