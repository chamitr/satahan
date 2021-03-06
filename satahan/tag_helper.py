__author__ = 'Chamit'

from flask import request
from flask_user import current_user
from model import usertaggroups, TagGroup, Tag, UserSettings
from database import db_session

def get_note_tags(form):
    tags = request.form['note_tags']
    if not tags:
        return None
    return tags.split(',')

def get_tags_in_group(idtaggroup):
    return Tag.query.order_by(Tag.tagpage).filter_by(idtaggroup=idtaggroup)

def get_user_default_taggroup():

    usersettings = UserSettings.query.filter_by(iduser = current_user.id).first()#try default
    if usersettings and usersettings.idtaggroup_def:
        return TagGroup.query.filter_by(idtaggroup = usersettings.idtaggroup_def).first()
    else:
        return current_user.usertaggroups.first()#just use the first one

def set_default_group(tg):
    usersettings = UserSettings.query.filter_by(iduser = current_user.id).first()
    if not usersettings:
        usersettings = UserSettings(current_user.id)
        db_session.add(usersettings)
    usersettings.idtaggroup_def = tg

def get_current_user_taggroup():
    idtaggroup = request.args.get('tg', None)#both t and tg must be provided
    usertaggroup = None
    try:
        if idtaggroup:
            usertaggroup = current_user.usertaggroups.filter(usertaggroups.c.idtaggroup==int(idtaggroup)).first()
            if not usertaggroup:
                taggroup = TagGroup.query.filter_by(idtaggroup=idtaggroup).first()
                if not taggroup:
                    usertaggroup = get_user_default_taggroup()
                else:
                    publishing = request.args.get('publishing', None)
                    publishing= True if publishing is not None else False
                    if publishing:
                        #if publishing automatically add taggroup to usertaggroups
                        current_user.usertaggroups.append(taggroup)
                        db_session.commit()
                    usertaggroup = taggroup
        else:
            usertaggroup = get_user_default_taggroup()
    except ValueError:
        usertaggroup = None
    return usertaggroup
