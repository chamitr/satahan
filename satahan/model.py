from flask_user import UserMixin
import datetime
from database import Base
from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table, DateTime, Boolean
from sqlalchemy.orm import relationship

notetags = Table('notetag', Base.metadata,
    Column('idtag', Integer, ForeignKey('tag.idtag')),
    Column('idnote', Integer, ForeignKey('note.idnote'))
)

usertaggroups = Table('usertaggroup', Base.metadata,
    Column('iduser', Integer, ForeignKey('user.id')),
    Column('idtaggroup', Integer, ForeignKey('taggroup.idtaggroup')),
)

# Define User model. Make sure to add flask.ext.user UserMixin !!!
class User(Base, UserMixin):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False, default='')
    email = Column(String(120), nullable=False, unique=True)
    password = Column(String(60), nullable=False, default='')
    active = Column(Boolean(), nullable=False, server_default='0')
    confirmed_at = Column(DateTime())
    is_admin = Column(Boolean(), nullable=False, server_default='0')
    usertaggroups = relationship('TagGroup', secondary=usertaggroups, backref='user', lazy='dynamic')

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

class UserSettings(Base):
    __tablename__ = 'usersettings'

    iduser = Column(Integer, primary_key=True)
    idtaggroup_def = Column(Integer, nullable=True)
    admin_points = Column(Integer, nullable=False, default=10)

    user = relationship("User", primaryjoin="and_(UserSettings.iduser==foreign(User.id))" )

    def __init__(self, iduser):
        self.iduser = iduser
        self.admin_points = 10

    def is_active(self):
        return True

class Note(Base):
    __tablename__ = 'note'

    idnote = Column(Integer, primary_key=True)
    title = Column(String(256), nullable=False, default='')
    text = Column(String(65535), nullable=False, default='')
    iduser = Column(Integer, ForeignKey('user.id'))
    comments_count = Column(Integer, nullable=False, default=0)
    createdatetime = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    published = Column(Boolean, nullable=False, default=False)
    attachment_count = Column(Integer, nullable=False, default=0)

    tags = relationship('Tag', secondary=notetags, backref='note', lazy='dynamic')
    user = relationship("User", primaryjoin="and_(Note.iduser==foreign(User.id))" )

    def __init__(self, title, text, iduser, published, idnote=None):
        if idnote:
            self.idnote = idnote
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

class TagGroup(Base):
    __tablename__ = 'taggroup'

    idtaggroup = Column(Integer, primary_key=True)
    taggroupname = Column(String(256), nullable=False)

    tags = relationship("Tag", primaryjoin="and_(Tag.idtaggroup==foreign(TagGroup.idtaggroup))" )

    def __init__(self, taggroupname):
        self.taggroupname = taggroupname

    @property
    def serialize(self):
       return {
           'idtaggroup'          : self.idtaggroup,
           'taggroupname'        : self.taggroupname,
       }

class Tag(Base):
    __tablename__ = 'tag'

    idtag = Column(Integer, primary_key=True)
    tagname = Column(String(256), nullable=False)
    idtaggroup = Column(Integer, ForeignKey('taggroup.idtaggroup'))
    tagpage = Column(String(256), nullable=True)

    taggroup = relationship("TagGroup", primaryjoin="and_(Tag.idtaggroup==foreign(TagGroup.idtaggroup))" )

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

class Comment(Base):
    __tablename__ = 'comment'

    idcomment = Column(Integer, primary_key=True)
    text = Column(String(65535), nullable=False, default='')
    iduser = Column(Integer, ForeignKey('user.id'))
    createdatetime = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)
    idnote = Column(Integer, ForeignKey('note.idnote'))

    user = relationship("User", primaryjoin="and_(Comment.iduser==foreign(User.id))" )

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

class Attachment(Base):
    __tablename__ = 'attachment'

    idattachment = Column(Integer, primary_key=True)
    idnote = Column(Integer, ForeignKey('note.idnote'))
    filename = Column(String(256), nullable=False)

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
