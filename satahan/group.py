__author__ = 'Chamit'

from flask import request, render_template, flash, json, redirect
from flask_user import login_required, current_user
from model import db, TagGroup, usertaggroups, UserSettings, Tag, notetags
from satahan import app, back
from admin_points import AdminPoints
from sqlalchemy import delete, and_

def get_taggroups_in_use():
    taggroups_in_use = Tag.query.filter(Tag.idtag.in_(db.session.query(notetags.c.idtag))).all()
    return [usertag.idtaggroup for usertag in taggroups_in_use]

def get_manage_group_view(s=None):
    taggroupsinuse = get_taggroups_in_use()
    f = request.args.get('f', None)
    taggroups = None
    if f == 'f':
        if s:
            taggroups = TagGroup.query.filter(TagGroup.taggroupname.like('%'+s+'%'),\
                TagGroup.idtaggroup.in_(t.idtaggroup for t in current_user.usertaggroups) )\
                .order_by(TagGroup.taggroupname.asc()).all()
        else:
            taggroups = current_user.usertaggroups
    else:
        if s:
            taggroups = TagGroup.query.filter(TagGroup.taggroupname.like('%'+s+'%'))\
                .order_by(TagGroup.taggroupname.asc()).all()
        else:
            taggroups = TagGroup.query.order_by(TagGroup.taggroupname.asc()).all()
    user_settings = AdminPoints.get_user_settings()
    return render_template('/manage_group.html', taggroups=taggroups, taggroupsinuse = taggroupsinuse,\
                           user_settings=user_settings,f=f)

@app.route('/view_group', methods=['GET', 'POST'])
def view_group():
    s = request.args.get('taggroupname', None)
    if s:
        taggroups = TagGroup.query.filter(TagGroup.taggroupname.like('%'+s+'%'))\
            .order_by(TagGroup.taggroupname.asc()).all()
    else:
        taggroups = TagGroup.query.order_by(TagGroup.taggroupname.asc()).all()
    return render_template('/view_group.html', taggroups=taggroups)

@app.route('/manage_group', methods=['GET', 'POST'])
@back.anchor
@login_required
def manage_group():
    if request.method == 'GET':
        return get_manage_group_view(request.args.get('taggroupname', None))

    manage_groups = None
    if len(request.form) > 0 :
        manage_groups = request.form.getlist('taggroup')
    before_count = current_user.usertaggroups.count()
    current_user.usertaggroups = []
    if manage_groups:
        for tg in manage_groups:
            g = TagGroup.query.filter_by(idtaggroup = tg).first()
            current_user.usertaggroups.append(g)
    db.session.commit()

    flash("Group successfully updated.", "success")

    #If there was not favourites and they were added for the first time, this could be a new user.
    #Redirect to home page.
    if before_count == 0 and len(manage_groups) > 0 :
        return redirect('/')

    return get_manage_group_view()

@app.route('/manage_group2', methods=['GET', 'POST'])
@login_required
def manage_group2():
    tag = request.args.get('p')
    json_tag = json.loads(tag)
    tg = json_tag['tg']
    g = TagGroup.query.filter_by(idtaggroup = tg).first()
    if not g:
        return ('', 500)
    current_user.usertaggroups.append(g)
    db.session.commit()
    return ('', 204)

@app.route('/add_group', methods=['POST'])
@login_required
def add_group():
    adminpoints = AdminPoints(db)
    #check admin points
    if not adminpoints.is_enough_admin_points(2):
        flash("Not enough admin points.", "error")
        return back.go_back()

    tag_group_name = request.form['taggroupname']
    tg = TagGroup.query.filter_by(taggroupname = tag_group_name).first()
    if tg:
        flash("Group already exists.", "error")
        return back.go_back()

    taggroup = TagGroup(tag_group_name)
    current_user.usertaggroups.append(taggroup)
    db.session.add(taggroup)

    #reduce admin points
    adminpoints.change_admin_points(-2)

    db.session.commit()

    flash("Group successfully added.", "success")
    return back.go_back()

@app.route('/delete_group/<int:idtaggroup>', methods=['POST'])
@login_required
def delete_group(idtaggroup):
    adminpoints = AdminPoints(db)
    #check admin points
    if not adminpoints.is_enough_admin_points(1):
        flash("Not enough admin points.", "error")
        return back.go_back()

    tg_query = TagGroup.query.filter_by(idtaggroup = idtaggroup)
    tg = tg_query.first()
    if not tg:
        flash("Group could not be found.", "error")
        return back.go_back()

    if idtaggroup in get_taggroups_in_use():
        flash("Group is in use.", "error")
        return back.go_back()

    if tg in current_user.usertaggroups:
        #if tag group is in current user's favourites, remove it before deleting it.
        stmt = delete(usertaggroups).where(and_(usertaggroups.c.iduser==current_user.id,
                                                      usertaggroups.c.idtaggroup==idtaggroup))
        db.session.execute(stmt)

    tg_query.delete()

    #reduce admin points
    adminpoints.change_admin_points(-1)

    db.session.commit()

    flash("Group successfully deleted.", "success")
    return back.go_back()

@app.route('/edit_group', methods=['GET', 'POST'])
@login_required
def edit_group():
    adminpoints = AdminPoints(db)
    #check admin points
    if not adminpoints.is_enough_admin_points(1):
        flash("Not enough admin points.", "error")
        return back.go_back()

    args = request.args.get('p', None)
    json_args = json.loads(args)
    tg = TagGroup.query.filter_by(idtaggroup = json_args['edit_idtaggroup']).first()
    if not tg:
        flash("Group could not be found.", "error")
        return back.go_back()

    if not tg in current_user.usertaggroups:
        flash("You have not subscribed to this group.", "error")
        return back.go_back()

    tg.taggroupname = json_args['edit_taggroupname']

    #reduce admin points
    adminpoints.change_admin_points(-1)

    db.session.commit()

    flash("Group successfully updated.", "success")
    return back.go_back()

@app.route('/default_group', methods=['GET', 'POST'])
@login_required
def default_group():
    usersettings = UserSettings.query.filter_by(iduser = current_user.id).first()
    tag = request.args.get('p')
    json_tag = json.loads(tag)
    tg = json_tag['tg']
    if not usersettings:
        usersettings = UserSettings(current_user.id)
        db.session.add(usersettings)
    usersettings.idtaggroup_def = tg
    db.session.commit()
    return ('', 204)
