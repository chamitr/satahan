__author__ = 'Chamit'

from satahan import app, back
from flask import request, flash, redirect
from werkzeug import secure_filename
from flask.ext.uploads import UploadSet, configure_uploads
from flask_user import login_required, current_user
import os
from model import db, Tag, TagGroup, Note
import codecs

@app.route('/upload_notes/<int:idtaggroup>', methods=['POST'])
@login_required
def upload_notes(idtaggroup):

    if not current_user.is_admin:
        flash('You have to be an admin user to perform this action.', 'error')
        return back.goback()

    taggroup = TagGroup.query.filter_by(idtaggroup=idtaggroup).first()
    if not taggroup:
        flash('Group not found.', 'error')
        return back.goback()

    filename=request.files['upload_notes']
    if not secure_filename(filename.filename):
        flash('File name is not secure.', 'error')
        return back.goback()

    try:
        upload_notes = UploadSet("uploadnotes", 'csv')
        configure_uploads(app, (upload_notes))
        upload_notes.save(filename)
    except:
        flash('File upload failed.', 'error')
        return back.goback()

    filepath = app.config['UPLOADS_DEFAULT_DEST']+'/' + "uploadnotes"

    dbdirty = False
    f = codecs.open(filepath + '/' + filename.filename,'r', encoding='utf-16')
    for line in f:
        line_data = line.split(',')
        if len(line_data) == 3:
            note_tags = line_data[0].strip().split('|')
            note_title = line_data[1].strip()
            note_text = line_data[2].strip()

            #add note
            newnote = Note(note_title, note_text, current_user.id, True)
            db.session.add(newnote)

            #add tags
            for note_tag in note_tags:
                tag_query = Tag.query.filter_by(tagname=note_tag, idtaggroup=idtaggroup).first()
                tag = None
                if tag_query:
                    tag = tag_query
                else:
                    tag = Tag(note_tag, idtaggroup)
                    tag.taggroup.append(taggroup)
                    db.session.add(tag)
                newnote.tags.append(tag)
                if not dbdirty:
                    dbdirty = True

    if dbdirty:
        db.session.commit()

    f.close()

    os.remove(os.path.join(filepath, filename.filename))

    flash('Note data upload successful.', 'success')
    return redirect('/')