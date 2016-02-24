__author__ = 'Chamit'

from flask import session, redirect, request
from satahan import app
import functools

class back(object):

    cfg = app.config.get
    cookie = cfg('REDIRECT_BACK_COOKIE', 'back')

    @staticmethod
    def anchor(func, cookie=cookie):
        @functools.wraps(func)
        def result(*args, **kwargs):
            session[cookie] = request.path
            if request.query_string:
                session[cookie] = request.path+"?"+request.query_string
            return func(*args, **kwargs)
        return result

    @staticmethod
    def goback(cookie=cookie):
        url = None
        try:
            url = session[cookie]
        except:
            pass
        if url:
            return redirect(url)
        else:
            return redirect("/query_note")

back = back()
anchor = back.anchor
goback = back.goback

def go_back():
    return back.goback()