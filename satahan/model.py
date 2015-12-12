from flask_user import UserMixin
from flask.ext.sqlalchemy import SQLAlchemy
from werkzeug import generate_password_hash, check_password_hash
import datetime

db = SQLAlchemy()
tags = db.Table('notetag',
    db.Column('idtag', db.Integer, db.ForeignKey('tag.idtag')),
    db.Column('idnote', db.Integer, db.ForeignKey('note.idnote'))
)

usertaggroups = db.Table('usertaggroup',
    db.Column('iduser', db.Integer, db.ForeignKey('user.id')),
    db.Column('idtaggroup', db.Integer, db.ForeignKey('taggroup.idtaggroup')),
)

# Define User model. Make sure to add flask.ext.user UserMixin !!!
class User(db.Model, UserMixin):
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), nullable=False, default='')
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(60), nullable=False, default='')
    active = db.Column(db.Boolean(), nullable=False, server_default='0')
    confirmed_at = db.Column(db.DateTime())
    is_admin = db.Column(db.Boolean(), nullable=False, server_default='0')
    usertaggroups = db.relationship('TagGroup', secondary=usertaggroups, backref='user', lazy='dynamic')

    @property
    def serialize(self):
       return {
           'id'                 : self.id,
           'username'           : self.username,
           'email'              : self.email,
           'password'           : self.password,
           'active'             : self.active,
           'confirmed_at'       : self.confirmed_at,
           'is_admin'           : self.is_admin
       }

class UserSettings(db.Model):
    __tablename__ = 'usersettings'

    iduser = db.Column(db.Integer, primary_key=True)
    idtaggroup_def = db.Column(db.Integer, nullable=True)
    admin_points = db.Column(db.Integer, nullable=False, default=10)

    user = db.relationship("User", primaryjoin="and_(UserSettings.iduser==foreign(User.id))" )

    def __init__(self, iduser):
        self.iduser = iduser
        self.admin_points = 0

    def is_active(self):
        return True

class Note(db.Model):
    __tablename__ = 'note'

    idnote = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(256), nullable=False, default='')
    text = db.Column(db.String(65535), nullable=False, default='')
    iduser = db.Column(db.Integer, db.ForeignKey('user.id'))
    comments_count = db.Column(db.Integer, nullable=False, default=0)
    createdatetime = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    published = db.Column(db.Boolean, nullable=False, default=False)
    attachment_count = db.Column(db.Integer, nullable=False, default=0)

    tags = db.relationship('Tag', secondary=tags, backref='note', lazy='dynamic')
    user = db.relationship("User", primaryjoin="and_(Note.iduser==foreign(User.id))" )

    def __init__(self, title, text, iduser, published):
        self.title = title
        self.text = text
        self.iduser = iduser
        self.published = published

    def is_active(self):
        return True

    @property
    def serialize(self):
       return {
           'idnote'             : self.idnote,
           'title'              : self.title,
           'text'               : self.text,
           'tags'               : self.serialize_tags,
           'iduser'             : self.iduser,
           'comments_count'     : self.comments_count,
           'createdatetime'     : self.createdatetime,
           'published'          : self.published,
           'user'               : self.serialize_user,
           'attachment_count'   : self.attachment_count
       }

    @property
    def serialize_tags(self):
       return [ item.serialize for item in self.tags]

    @property
    def serialize_user(self):
        return [ item.serialize for item in self.user]

class TagGroup(db.Model):
    __tablename__ = 'taggroup'

    idtaggroup = db.Column(db.Integer, primary_key=True)
    taggroupname = db.Column(db.String(256), nullable=False)

    tags = db.relationship("Tag", primaryjoin="and_(Tag.idtaggroup==foreign(TagGroup.idtaggroup))" )

    def __init__(self, taggroupname):
        self.taggroupname = taggroupname

    @property
    def serialize(self):
       return {
           'idtaggroup'          : self.idtaggroup,
           'taggroupname'        : self.taggroupname,
       }

class Tag(db.Model):
    __tablename__ = 'tag'

    idtag = db.Column(db.Integer, primary_key=True)
    tagname = db.Column(db.String(256), nullable=False)
    idtaggroup = db.Column(db.Integer, db.ForeignKey('taggroup.idtaggroup'))
    tagpage = db.Column(db.String(256), nullable=True)

    taggroup = db.relationship("TagGroup", primaryjoin="and_(Tag.idtaggroup==foreign(TagGroup.idtaggroup))" )

    def __init__(self, tagname, idtaggroup, tagpage=None):
        self.tagname = tagname
        self.idtaggroup = idtaggroup
        self.tagpage = tagpage

    def is_active(self):
        return True

    @property
    def serialize(self):
       return {
           'idtag'          : self.idtag,
           'tagname'        : self.tagname,
           'idtaggroup'     : self.idtaggroup,
           'tagpage'           : self.tagpage
       }

class Comment(db.Model):
    __tablename__ = 'comment'

    idcomment = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.String(65535), nullable=False, default='')
    iduser = db.Column(db.Integer, db.ForeignKey('user.id'))
    createdatetime = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    idnote = db.Column(db.Integer, db.ForeignKey('note.idnote'))

    user = db.relationship("User", primaryjoin="and_(Comment.iduser==foreign(User.id))" )

    def __init__(self, text, iduser, idnote):
        self.text = text
        self.iduser = iduser
        self.idnote = idnote

    def is_active(self):
        return True

    @property
    def serialize(self):
       return {
           'idcomment'          : self.idcomment,
           'text'               : self.text,
           'iduser'             : self.iduser,
           'createdatetime'     : self.createdatetime,
           'idnote'             : self.idnote,
           'user'               : self.serialize_user
       }

    @property
    def serialize_user(self):
        return [ item.serialize for item in self.user]

class Attachment(db.Model):
    __tablename__ = 'attachment'

    idattachment = db.Column(db.Integer, primary_key=True)
    idnote = db.Column(db.Integer, db.ForeignKey('note.idnote'))
    filename = db.Column(db.String(256), nullable=False)

    def __init__(self, idnote, filename):
        self.idnote = idnote
        self.filename = filename

    def is_active(self):
        return True

    @property
    def serialize(self):
       return {
           'idattachment'       : self.idattachment,
           'idnote'             : self.idnote,
           'filename'           : self.filename,
       }
