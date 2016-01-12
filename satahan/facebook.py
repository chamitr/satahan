__author__ = 'Chamit'

from satahan import app
from flask_oauth import OAuth
from flask import session, url_for, request, redirect, flash
from model import User
from database import db_session
from flask.ext.login import login_user
from datetime import datetime

oauth = OAuth()

facebook = oauth.remote_app('facebook',
    base_url='https://graph.facebook.com/',
    request_token_url=None,
    access_token_url='/oauth/access_token',
    authorize_url='https://www.facebook.com/dialog/oauth',
    consumer_key=app.config['FACEBOOK_APP_ID'],
    consumer_secret=app.config['FACEBOOK_APP_SECRET'],
    request_token_params={'scope': 'email'},
    access_token_method='GET'
)

@facebook.tokengetter
def get_facebook_oauth_token():
    return session.get('oauth_token')

@app.route('/facebook_login')
def facebook_login():
    return facebook.authorize(callback=url_for('facebook_authorized',
        next=request.args.get('next') or request.referrer or None,
        _external=True))

@app.route('/login/authorized')
@facebook.authorized_handler
def facebook_authorized(resp):
    if resp is None:
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['oauth_token'] = (resp['access_token'], '')
    me = facebook.get('/me?fields=name,email')
    user = User.query.filter_by(social_id=me.data['id']).first()
    print(me.data)
    if not user:
        user = User(social_id=me.data['id'], username=me.data['name'], email=me.data['email'],
                    active=True, confirmed_at=datetime.now())
        db_session.add(user)
        db_session.commit()
    login_user(user, True)
    flash('You have signed in successfully.', 'success')
    return redirect('/')