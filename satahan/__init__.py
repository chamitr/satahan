__author__ = 'Chamit'

from flask import Flask
from flask_mail import Mail
from flask_user import SQLAlchemyAdapter, UserManager
from flask.ext.triangle import Triangle
from model import User, db
from configclass import ConfigClass

app = Flask(__name__)

# create our little application :)
app.config.from_object(__name__+'.ConfigClass')
mail = Mail(app)

# Setup Flask-User
db_adapter = SQLAlchemyAdapter(db, User)        # Register the User model
user_manager = UserManager(db_adapter, app)     # Initialize Flask-User

app.secret_key = 'haha'
db.init_app(app)
Triangle(app)

import note
import comment
import group
import tag
import timesince
import attachments
import back
import upload