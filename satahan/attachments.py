__author__ = 'Chamit'

from flask import request, render_template, redirect, send_from_directory, flash
from satahan import app, back
from flask.ext.uploads import UploadSet, configure_uploads, AllExcept
from model import db, Note, Attachment
from flask_user import login_required
from werkzeug import secure_filename
import os

@app.route('/download/<int:idnote>/<path:filename>')
def download(idnote, filename):
    attachment = Attachment.query.filter_by(idnote=idnote,filename=filename).first()
    if not attachment:
        flash('Attachment does not exists', 'error')
        return back.goback()
    return send_from_directory(app.config['UPLOADS_DEFAULT_DEST']+'/' + str(idnote), filename, as_attachment= True)

@app.route('/upload/<int:idnote>', methods=['GET', 'POST'])
@login_required
def upload(idnote):
    """Upload a new file."""
    if request.method == 'POST':
        note = Note.query.filter_by(idnote=idnote, published = True).first()
        if not note:
            flash('Note could not be found.', 'error')
            return back.goback()

        filename=request.files['attachment']
        if not secure_filename(filename.filename):
            flash('File name is not secure.', 'error')
            return back.goback()

        attachment = Attachment.query.filter_by(idnote=idnote,filename=filename.filename).first()
        if attachment:
            flash('Attachment already exists.', 'error')
            return back.goback()

        attachment = Attachment(idnote,filename.filename)
        db.session.add(attachment)

        attachments = UploadSet(str(idnote), AllExcept(('exe', 'so', 'dll')))
        configure_uploads(app, (attachments))

        #if file saved successfully, commit it to db as well.
        if attachments.save(filename):
            note.attachment_count += 1
            db.session.commit()
            flash('Attachment successfully uploaded.', 'success')

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

        os.remove(os.path.join(app.config['UPLOADS_DEFAULT_DEST']+'/' + str(idnote), filename))
        attachment_query.delete()
        db.session.commit()
        flash('Attachment successfully deleted.', 'success')

    return back.goback()

def delete_all_attachments(idnote):
    attachments_query = Attachment.query.filter_by(idnote=idnote)
    attachments = attachments_query.all()
    for attachment in attachments:
        os.remove(os.path.join(app.config['UPLOADS_DEFAULT_DEST']+'/' + str(idnote), attachment.filename))
    attachments_query.delete()

def get_all_attachments(idnote):
    return Attachment.query.order_by(Attachment.filename.desc()).filter_by(idnote=idnote).all()