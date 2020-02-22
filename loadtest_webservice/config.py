import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = 'postgresql://<username>:<password>@localhost/loadtest_db'
    SQLALCHEMY_TRACK_MODIFICATIONS = True