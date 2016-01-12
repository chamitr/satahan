__author__ = 'Chamit'

from flask import Flask
from flask_mail import Mail
from flask_user import SQLAlchemyAdapter, UserManager
from flask.ext.triangle import Triangle
from model import User
from configclass import ConfigClass
from database import init_db, db_session, Database

app = Flask(__name__)

# create our little application :)
app.config.from_object(__name__+'.ConfigClass')
mail = Mail(app)

init_db()

# Setup Flask-User
db = Database()
db_adapter = SQLAlchemyAdapter(db, User)        # Register the User model
user_manager = UserManager(db_adapter, app)     # Initialize Flask-User

app.secret_key = 'haha'
Triangle(app)

@app.teardown_appcontext
def shutdown_session(exception=None):
    db_session.remove()

import note
import comment
import group
import tag
import timesince
import attachments
import back
import upload
import database
import facebook