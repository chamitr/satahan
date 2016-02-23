from flask import request, session, redirect, render_template, flash
from flask_user import login_required, current_user
from model import Note, Tag, Comment, notetags, TagGroup, UserSettings, User
from flask.ext.paginate import Pagination
from satahan import app, back
from tag_helper import get_note_tags, get_tags_in_group, get_current_user_taggroup
from attachments import delete_all_attachments, get_all_attachments
from admin_points import AdminPoints
from sets import Set
from sqlalchemy import and_, select, union, func, desc
from database import db_session
import datetime

per_page = 10

def get_notes_in_group_stmt(returned_fields, where_clause):
    s1 = select(returned_fields).select_from(Note.__table__.outerjoin(notetags, notetags.c.idnote==Note.__table__.c.idnote)\
        .outerjoin(Tag.__table__, notetags.c.idtag==Tag.__table__.c.idtag)\
        .outerjoin(User.__table__, Note.__table__.c.iduser==User.__table__.c.id))\
        .where(where_clause)
    s2 = select(returned_fields).select_from(notetags.outerjoin(Note.__table__, notetags.c.idnote==Note.__table__.c.idnote)\
        .outerjoin(Tag.__table__, notetags.c.idtag==Tag.__table__.c.idtag)\
        .outerjoin(User.__table__, Note.__table__.c.iduser==User.__table__.c.id))\
        .where(where_clause)
    return union(s1,s2).order_by(desc("idnote"))

@app.route('/')
@back.anchor
#@login_required
def query_note():
    idtaggroup = request.args.get('tg', None)
    if not current_user.is_authenticated() or not idtaggroup:
        return render_template('index.html')

    #get query tags
    q = request.args.getlist('t')
    #get page
    try:
        page = int(request.args.get('page', 1))
    except ValueError:
        page = 1
    #get tags

    usertaggroup = None
    if current_user.is_authenticated():
        usertaggroup = get_current_user_taggroup()
    else:
        usertaggroup = TagGroup.query.filter_by(idtaggroup=idtaggroup).first()
    if not usertaggroup:
        return redirect('/about')

    tags = get_tags_in_group(usertaggroup.idtaggroup)

    #get resulting notes
    note_total = 0
    note_items = []
    if q and len(q) > 0:
        #try filter
        where_clause = and_(Tag.idtag.in_(q), Note.published==True)
    elif usertaggroup:
        where_clause = and_(Tag.idtaggroup==usertaggroup.idtaggroup, Note.published==True)

    #  get total count
    stmt = get_notes_in_group_stmt([Note.idnote], where_clause)
    note_total = len(db_session.execute(stmt).fetchall())
    #  get data
    stmt = get_notes_in_group_stmt([Note, User], where_clause)
    stmt = stmt.offset((page-1)*per_page)\
            .limit(per_page)
    note_items = db_session.execute(stmt).fetchall()

    pagination = Pagination(page=page, total=note_total, record_name='note', per_page = per_page,\
                            css_framework='foundation')
    #render
    usertaggroups = None
    if current_user.is_authenticated():
        usertaggroups = current_user.usertaggroups
    favourite = True
    if not usertaggroups or not usertaggroups.filter_by(idtaggroup = usertaggroup.idtaggroup).first():
        usertaggroups = [usertaggroup]
        favourite = False #Not one of user's favourite tags
    defaut_tag_group=False
    usersettings = None
    if current_user.is_authenticated():
        usersettings = UserSettings.query.filter_by(iduser=current_user.id).first()
    if usersettings and usersettings.idtaggroup_def == usertaggroup.idtaggroup:
        defaut_tag_group=True
    tagpages = Set()
    for tg in tags:
        tagpages.add(tg.tagpage)
    return render_template('home.html', notes=note_items, pagination=pagination, usertaggroups = usertaggroups,\
                           tags = tags, checked_tags = q, current_user_taggroup = usertaggroup, favourite = favourite,\
                           defaut_tag_group=defaut_tag_group, show_tag_ctrl=True, tagpages=sorted(tagpages))

@app.route('/add_note/<int:published>', methods=['GET', 'POST'])
@back.anchor
@login_required
def add_note(published):
    usertaggroup = get_current_user_taggroup()
    tagsingroup = []
    if usertaggroup:
        tagsingroup = get_tags_in_group(usertaggroup.idtaggroup)
    if request.method == 'GET':
        usertaggroup = get_current_user_taggroup()
        draft_note = Note.query.filter_by(iduser=current_user.id, published=False).first()
        publishing = request.args.get('publishing', None)
        publishing= True if publishing is not None else False
        if publishing:
            flash("Select tags for your note above and click the Share button below.", "info")
        if draft_note:
            checked_tags = []
            #If draft note is found, display it. However, if the user has a selection, it should get priority.
            if draft_note.tags and not request.args.get('tg', None):
                firsttag = draft_note.tags.first()
                if firsttag:
                    usertaggroup = TagGroup.query.filter_by(idtaggroup = firsttag.idtaggroup).first()
                    for item in draft_note.tags:
                        checked_tags.append(str(item.idtag))
            attachments = get_all_attachments(idnote=draft_note.idnote)
            tags_in_group=[]
            if usertaggroup:
                tags_in_group=get_tags_in_group(usertaggroup.idtaggroup)
            return render_template('add_note.html', new_note = draft_note, tags = tags_in_group,\
                usertaggroups = current_user.usertaggroups, current_user_taggroup = usertaggroup,\
                checked_tags = checked_tags, attachments = attachments, show_tag_ctrl=True,
                publishing=publishing)
        else:
            idnote_next = db_session.query(func.max(Note.idnote)).first()[0] + 1
            #write new empty draft note
            draft_note = Note("", "", current_user.id, False, idnote=idnote_next)
            db_session.add(draft_note)
            db_session.commit()
            return render_template('add_note.html', new_note = draft_note, tags = tagsingroup,\
                                   usertaggroups = current_user.usertaggroups,\
                                   current_user_taggroup = usertaggroup, show_tag_ctrl=True,
                                   publishing=publishing)
    #if draft found, update it - we should always find it because we create empty one in get section
    newnote = Note.query.filter_by(iduser=current_user.id, published=False).first()
    if newnote:
        newnote.title = request.form['title']
        newnote.text = request.form['notetext']
        newnote.published = published
        newnote.tags = []

    if newnote.title == "" and newnote.text == "" and published == 1:
        flash('There is nothing to publish.', 'error')
        return back.go_back()

    #get tag selectoin
    tags = get_note_tags(request.form)
    if not tags and published == 1:
        #if no taggroup, we save work as draft so user data is not lost
        newnote.published = 0
        db_session.add(newnote)
        db_session.commit()

        publishing = request.args.get('publishing', None)
        publishing= True if publishing is not None else False
        if publishing:
            #meaning the user has gone through the topic and tag selection. Give an error.
            flash("Please select tags above before you could publish.", "error")
            return back.go_back()

        #problem with tag selection
        flash("Content needs a topic and tags to publish them. Select a topic and then tags.", "info")
        return redirect('/manage_group?publishing')

    #add note to db
    if published == 1:
        newnote.createdatetime = datetime.datetime.utcnow()
    db_session.add(newnote)
    #link tags to note
    if tags:
        tags = Tag.query.filter(Tag.idtag.in_(tags)).all()
        for tag in tags:
            newnote.tags.append(tag)
    #add admin points
    if published == 1:
        adminpoints = AdminPoints(db_session)
        adminpoints.change_admin_points(10)

    #commit to db
    db_session.commit()
    if published == 1:
        flash('New note was successfully posted', 'success')
        return redirect('/get_note/' + str(newnote.idnote))
    else:
        flash('New note was successfully saved', 'success')
        return back.go_back()

@app.route('/get_note/<int:idnote>', methods=['GET'])
@back.anchor
@login_required
def get_note(idnote):
    note = Note.query.filter_by(idnote=idnote, published = True).first()
    if not note:
        #check if this is an unpublished note for current user
        note = Note.query.filter_by(idnote=idnote, published = False, iduser = current_user.id).first()
    if not note:
        flash('Could not fined note', 'error')
        return redirect('/')

    comments = Comment.query.order_by(Comment.idcomment.desc()).filter_by(idnote=idnote)
    attachments = get_all_attachments(idnote=idnote)

    return render_template('/note_full.html', full_note=note, comments=comments,\
        attachments=attachments)

@app.route('/delete_note/<int:idnote>', methods=['GET', 'POST'])
@login_required
def delete_note(idnote):
    #GET request doing POST work here.
    note_query = Note.query.filter_by(idnote=idnote).first()
    if note_query == None:
        flash('Could not fined note', 'error')
        return back.go_back()
    if note_query.iduser != current_user.id and current_user.is_admin == 0:
        flash("Please select a Note that belongs to you.", "error")
        return back.go_back()

    delete_all_attachments(idnote=idnote)
    Comment.query.filter_by(idnote=idnote).delete()
    note_query.tags = []
    Note.query.filter_by(idnote=idnote).delete()
    db_session.commit()
    return redirect('/')

@app.route('/edit_note/<int:idnote>', methods=['GET', 'POST'])
@back.anchor
@login_required
def edit_note(idnote):
    idtaggroup = 0#XXX
    if request.method == 'GET':
        note = Note.query.filter_by(idnote=idnote).first()
        idtaggroup = None
        idtaggroup = request.args.get('tg', None)
        if not idtaggroup:
            tg = note.tags.first()
            if tg:
                idtaggroup = tg.idtaggroup #assuming all tags belong to the same taggroup
        checked_tags = []
        if note:
            for item in note.tags:
                checked_tags.append(str(item.idtag))
        tags = get_tags_in_group(idtaggroup)
        taggroup = TagGroup.query.filter_by(idtaggroup = idtaggroup)
        attachments = get_all_attachments(idnote=idnote)
        return render_template('/edit_note.html', edit_note=note, usertaggroups = current_user.usertaggroups,\
                               current_user_taggroup = taggroup.first(), tags = tags, checked_tags = checked_tags,\
                               attachments = attachments, show_tag_ctrl=True)

    note_query = Note.query.filter_by(idnote=idnote, iduser=current_user.id).first()
    if not note_query:
        flash("Please select a Note that belongs to you.", "error")
        return redirect('/')
    else:
        tags = get_note_tags(request.form)
        if not tags:
            flash("Please select tags.", "error")
            return redirect('/edit_note/' + str(idnote))

        tags = Tag.query.filter(Tag.idtag.in_(tags)).all()

        # we are changing idtaggroup
        idtaggroup = tags[0].idtaggroup

        #  remove tags for the group
        for t in note_query.tags:
            if t.idtaggroup == idtaggroup:
                note_query.tags.remove(t)

        for tag in tags:
            note_query.tags.append(tag)

        note_query.title=request.form['title']
        note_query.text=request.form['notetext']
        db_session.commit()
        return redirect('/')

@app.route('/delete_draft', methods=['POST'])
@login_required
def delete_draft():
    draft_note_query = Note.query.filter_by(iduser=current_user.id, published=False)
    if draft_note_query:
        draft_note=draft_note_query.first()
        delete_all_attachments(idnote=draft_note.idnote)
        draft_note.tags = []
        draft_note_query.delete()
        db_session.commit()
    return redirect('/add_note/0')

@app.route('/about', methods=['GET'])
@login_required
def about():
    return render_template('about.html')
