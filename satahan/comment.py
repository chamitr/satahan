__author__ = 'Chamit'

from flask import request, redirect, flash
from flask_user import login_required, current_user
from model import db, Note, Comment
from satahan import app

@app.route('/add_comment', methods=['POST'])
@login_required
def add_comment():
    note = request.form['note']
    note_query = Note.query.filter_by(idnote=note).first()
    if not note_query:
        flash("Please select a Note.", "error")
        return redirect('/get_note/' + note)
    newcomment = Comment(request.form['text'], current_user.id, note)
    db.session.add(newcomment)
    note_query.comments_count = note_query.comments_count + 1
    db.session.commit()
    flash('New comment was successfully posted', 'success')
    return redirect('/get_note/' + note)
