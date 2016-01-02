__author__ = 'Chamit'

from model import  UserSettings
from flask_user import current_user

class AdminPoints:

    def __init__(self, db_session):
        self.us = UserSettings.query.filter_by(iduser=current_user.id).first()
        if not self.us:
            self.us = UserSettings(current_user.id)
            db_session.add(self.us)

    def is_enough_admin_points(self, admin_points):
        if current_user.is_admin or self.us.admin_points >= admin_points:
            return True
        else:
            return False

    def change_admin_points(self, admin_points):
        if not current_user.is_admin:
            self.us.admin_points += admin_points

    @staticmethod
    def get_user_settings():
        us = UserSettings.query.filter_by(iduser=current_user.id).first()
        if not us:
            return UserSettings(current_user.id)
        return us
