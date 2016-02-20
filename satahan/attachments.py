__author__ = 'Chamit'

from flask import request, render_template, redirect, send_from_directory, flash, jsonify, send_file, make_response, url_for
from satahan import app, back
from flask.ext.uploads import UploadSet, configure_uploads, AllExcept, IMAGES, EXECUTABLES
from model import Note, Attachment
from flask_user import login_required
from werkzeug import secure_filename
import os
from configclass import ConfigClass
from database import db_session
from werkzeug.exceptions import RequestEntityTooLarge
from PIL import Image
from cStringIO import StringIO

@login_required
def upload_file(idnote, filename, imagesonly):
    note = Note.query.filter_by(idnote=idnote).first()
    if not note:
        return False, 'Note could not be found.', '', 0, 0

    if not secure_filename(filename.filename):
        return False, 'File name is not secure.', '', 0, 0

    attachment = Attachment.query.filter_by(idnote=idnote,filename=filename.filename).first()
    if attachment:
        return False, 'Attachment already exists.', '', 0, 0

    try:
        attachments = UploadSet(str(idnote), IMAGES if imagesonly else AllExcept(EXECUTABLES))
        configure_uploads(app, (attachments))

        image = Image.open(filename.stream)
        maxWidthOrHeight = 1024
        if (image.size[0] > maxWidthOrHeight or image.size[1] > maxWidthOrHeight):
            maxSize = (maxWidthOrHeight, maxWidthOrHeight)
            image.thumbnail(maxSize, Image.ANTIALIAS)
            thumb_io = StringIO()
            file_name, file_extension = os.path.splitext(filename.filename)
            image.save(thumb_io, format='JPEG')
            thumb_io.seek(0)
            filename.stream = thumb_io

        filename = attachments.save(filename)

        attachment = Attachment(idnote,filename)
        db_session.add(attachment)
        note.attachment_count += 1

        return True, '', filename, image.size[0], image.size[1]
    except Exception as e:
        return False, str(e), '', 0, 0

@app.route('/uploadimage/<int:idnote>/', methods=['POST', 'OPTIONS'])
@login_required
def uploadimage(idnote):
    error = ''
    url = ''
    callback = request.args.get("CKEditorFuncNum")
    if request.method == 'POST' and 'upload' in request.files:
        filename=request.files['upload']
        ret, error, filename, w, h = upload_file(idnote, filename, True)
        #if file saved successfully, commit it to db as well.
        if ret:
            db_session.commit()
            url = '/imgs/'+ str(idnote) + "/" + filename
    else:
        error = 'post error'
    res = """<script type="text/javascript">
    window.parent.CKEDITOR.tools.callFunction(%s, '%s', '%s');
    </script>""" % (callback, url, error)
    response = make_response(res)
    response.headers["Content-Type"] = "text/html"
    return response

@app.route('/uploadimage_json/<int:idnote>/', methods=['POST', 'OPTIONS'])
@login_required
def uploadimage_json(idnote):
    error = ''
    url = ''
    filename = ''
    w = 0
    h = 0
    try:
        request.files
    except RequestEntityTooLarge:
        error = 'File too large. Maximum file size allowed is 8MB.'

    if len(error) == 0 and request.method == 'POST' and 'upload' in request.files:
        filename=request.files['upload']
        ret, error, filename, w, h = upload_file(idnote, filename, True)
        #if file saved successfully, commit it to db as well.
        if ret:
            db_session.commit()
            url = '/imgs/'+ str(idnote) + "/" + filename
    else:
        error = error if len(error) > 0 else 'post error'

    res = {
        "uploaded": 0 if len(error) > 0 else 1,
        "fileName": filename,
        "url": url,
        "width": w,
        "height": h,
        "error": {
            "message": error
        }
    }
    return jsonify(res)

@app.route('/imgs/<int:idnote>/<path:filename>')
@login_required
def images(idnote, filename):
    fullpath = os.path.join(ConfigClass.UPLOADS_DEFAULT_DEST+'/' + str(idnote), filename)
    return send_file(fullpath,
                 attachment_filename=filename,
                 mimetype='image/png')

@app.route('/download/<int:idnote>/<path:filename>')
@login_required
def download(idnote, filename):
    attachment = Attachment.query.filter_by(idnote=idnote,filename=filename).first()
    if not attachment:
        flash('Attachment does not exists', 'error')
        return back.goback()
    return send_from_directory(ConfigClass.UPLOADS_DEFAULT_DEST+'/' + str(idnote), filename, as_attachment= True)

@app.route('/upload/<int:idnote>', methods=['GET', 'POST'])
@login_required
def upload(idnote):
    """Upload a new file."""
    if request.method == 'POST':
        filename=request.files['attachment']
        ret, error, filename, w, h = upload_file(idnote, filename, False)
        if ret:
            #if file saved successfully, commit it to db as well.
            db_session.commit()
            flash('Attachment successfully uploaded.', 'success')
        else:
            flash(error, 'error')
    return back.goback()

@app.errorhandler(413)
def error413(e):
    flash('File too large. Maximum file size allowed is 8MB.', 'error')
    return back.goback()

@app.route('/delete_attachment/<int:idnote>/<path:filename>', methods=['GET', 'POST'])
@login_required
def delete_attachment(idnote, filename):
    if request.method == 'POST':
        attachment_query = Attachment.query.filter_by(idnote=idnote,filename=filename)
        if not attachment_query.first():
            flash('Attachment does not exist.', 'error')
            return back.goback()

        note = Note.query.filter_by(idnote=idnote).first()
        if note:
            note.attachment_count -= 1

        os.remove(os.path.join(ConfigClass.UPLOADS_DEFAULT_DEST+'/' + str(idnote), filename))
        attachment_query.delete()
        db_session.commit()
        flash('Attachment successfully deleted.', 'success')

    return back.goback()

def delete_all_attachments(idnote):
    attachments_query = Attachment.query.filter_by(idnote=idnote)
    attachments = attachments_query.all()
    for attachment in attachments:
        os.remove(os.path.join(ConfigClass.UPLOADS_DEFAULT_DEST+'/' + str(idnote), attachment.filename))
    attachments_query.delete()

def get_all_attachments(idnote):
    return Attachment.query.order_by(Attachment.filename.desc()).filter_by(idnote=idnote).all()