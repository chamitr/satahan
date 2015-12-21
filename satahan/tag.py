__author__ = 'Chamit'

from flask import request, jsonify, json, flash, render_template, redirect
from flask_user import login_required, current_user
from model import db, Tag, TagGroup, UserSettings, notetags
from satahan import app, back
from admin_points import AdminPoints

@app.route('/add_tag', methods=['GET', 'POST'])
@login_required
def add_tag():
    tg = request.form['tg']
    tag = request.form['tagname']
    page = request.form['tagpage']
    if len(page) <= 0:
        page = None

    adminpoints = AdminPoints(db)
    #check admin points
    if not adminpoints.is_enough_admin_points(1):
        flash("Not enough admin points.", "error")
        return tag_manage_view(tg)

    #if found, return it
    tag_query = Tag.query.filter_by(tagname=tag, idtaggroup=tg).first()
    if tag_query:
        flash('Failed to add tag. Tag already exists.', 'error')
        return tag_manage_view(tg)

    taggroup = TagGroup.query.filter_by(idtaggroup=tg).first()
    tag = Tag(tag, tg, page)
    tag.taggroup.append(taggroup)
    db.session.add(tag)

    #reduce admin points
    adminpoints.change_admin_points(-1)

    db.session.commit()
    flash('Tag successfully added to group.', 'success')
    return tag_manage_view(tg)

def tag_manage_view(tg):
    current_user_taggroup = TagGroup.query.filter_by(idtaggroup=tg).first()
    tgs = Tag.query.filter_by(idtaggroup=tg).all()
    tags_in_use = db.session.query(notetags.c.idtag).filter(notetags.c.idtag.in_(t.idtag for t in tgs)).all()
    tags_in_use = [t[0] for t in tags_in_use]
    user_settings = AdminPoints.get_user_settings()
    return render_template('/manage_tags.html', tags=tgs, current_user_taggroup = current_user_taggroup,\
                           tags_in_use = tags_in_use, user_settings=user_settings)

@app.route('/manage_tags', methods=['GET'])
@login_required
def manage_tags():
    tg = request.args.get('tg', None)
    if not tg:
        return flash('Could not find group.', 'error')
    return tag_manage_view(tg)

@app.route('/edit_tag', methods=['GET', 'POST'])
@login_required
def edit_tag():
    adminpoints = AdminPoints(db)
    #check admin points
    if not adminpoints.is_enough_admin_points(1):
        flash("Not enough admin points.", "error")
        return ('', 500)

    args = request.args.get('p', None)
    json_args = json.loads(args)
    tag = Tag.query.filter_by(idtag = json_args['edit_idtag']).first()
    if not tag:
        return ('', 500)

    tag.tagname = json_args['edit_tagname']
    page = json_args['edit_tagpage']
    if len(page) > 0:
        tag.tagpage = page
    else:
        tag.tagpage = None

    #reduce admin points
    adminpoints.change_admin_points(-1)

    db.session.commit()

    return ('', 204)

@app.route('/delete_tag/<int:idtaggroup>/<int:idtag>', methods=['GET', 'POST'])
@login_required
def delete_tag(idtaggroup, idtag):
    adminpoints = AdminPoints(db)
    #check admin points
    if not adminpoints.is_enough_admin_points(1):
        flash("Not enough admin points.", "error")
        return tag_manage_view(idtaggroup)

    tag = Tag.query.filter_by(idtag = idtag)
    if not tag:
        flash('Tag could not be found.', 'error')
        return tag_manage_view(idtaggroup)
    tag.delete()

    #reduce admin points
    adminpoints.change_admin_points(-1)

    db.session.commit()
    flash('Tag successfully deleted from group.', 'success')
    return tag_manage_view(idtaggroup)

@app.route('/move_tags')
@login_required
def move_tags():
    if not current_user.is_admin:
        flash('You have to be an admin user to perform this action.', 'error')

    tag_group_name = request.args.get('taggroupname', None)
    tag_group_name.strip()
    if len(tag_group_name) == 0:
        flash('Group name is empty.', 'error')
        return back.goback()

    tag_group = TagGroup.query.filter_by(taggroupname=tag_group_name).first()
    if not tag_group:
        tag_group = TagGroup(tag_group_name)
        db.session.add(tag_group)
        current_user.usertaggroups.append(tag_group)
        db.session.commit()
        tag_group = TagGroup.query.filter_by(taggroupname=tag_group_name).first()

    tags = request.args.getlist('t')
    stmt = Tag.__table__.update().where(Tag.idtag.in_(tags)).values(idtaggroup=tag_group.idtaggroup)
    db.session.execute(stmt)
    db.session.commit()
    flash('Tags successfully moved.', 'success')

    return back.goback()

@app.route('/merge_tags')
@login_required
def merge_tags():
    if not current_user.is_admin:
        flash('You have to be an admin user to perform this action.', 'error')

    tag_name = request.args.get('tagname', None)
    tag_name.strip()
    if len(tag_name) == 0:
        flash('Target tag name is empty.', 'error')
        return back.goback()

    tg = request.args.get('tg', None)

    #if found, return it
    tag_query = Tag.query.filter_by(tagname=tag_name, idtaggroup=tg).first()
    if not tag_query:
        taggroup = TagGroup.query.filter_by(idtaggroup=tg).first()
        tag = Tag(tag_name, tg)
        tag.taggroup.append(taggroup)
        db.session.add(tag)
        db.session.commit()
        tag_query = Tag.query.filter_by(tagname=tag, idtaggroup=tg).first()

    tgs = request.args.getlist('t')
    stmt = notetags.update().where(notetags.c.idtag.in_(tgs)).values(idtag=tag_query.idtag)
    db.session.execute(stmt)
    db.session.commit()
    flash('Tags successfully merged. Delete unused tags', 'success')

    return back.goback()