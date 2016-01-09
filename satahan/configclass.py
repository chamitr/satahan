import os
import socket

# Use a Class-based config to avoid needing a 2nd file
# os.getenv() enables configuration through OS environment variables
class ConfigClass(object):
    # Flask settings
    SECRET_KEY =              os.getenv('SECRET_KEY',       'THIS IS AN INSECURE SECRET')
    SECURITY_PASSWORD_SALT = 'my_precious_two'

    if socket.gethostname() == 'BFF':
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',     'mysql://root:@localhost/satahan')
    else:
        SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URL',     'mysql://satahan:2015SenuthMenuth@satahan.mysql.pythonanywhere-services.com/satahan$satahan')
    CSRF_ENABLED = True
    SQLALCHEMY_TRACK_MODIFICATIONS = True

    # Flask-Mail settings
    MAIL_USERNAME =           os.getenv('MAIL_USERNAME',        'satahan@yahoo.com')
    MAIL_PASSWORD =           os.getenv('MAIL_PASSWORD',        '5BGalMin')
    MAIL_DEFAULT_SENDER =     os.getenv('MAIL_DEFAULT_SENDER',  '"Satahan" <satahan@yahoo.com>')
    MAIL_SERVER =             os.getenv('MAIL_SERVER',          'smtp.mail.yahoo.com')
    MAIL_PORT =           int(os.getenv('MAIL_PORT',            '465'))
    MAIL_USE_SSL =        int(os.getenv('MAIL_USE_SSL',         True))
    MAIL_USE_TLS =        int(os.getenv('MAIL_USE_TLS',         False))

    # Flask-User settings
    USER_APP_NAME        = 'Satahan'                # Used by email templates

    # Flask-Uploads settings
    if socket.gethostname() == 'BFF':
        DEBUG = True
        UPLOADS_DEFAULT_DEST =      '/var/uploads'
        UPLOADS_DEFAULT_URL =       'http://localhost:5001/'
    else:
        UPLOADS_DEFAULT_DEST =      '/home/satahan/uploads'
        UPLOADS_DEFAULT_URL =       'http://localhost:5001/'
    MAX_CONTENT_LENGTH = 2 * 1024 * 1024