import os
basedir = os.path.abspath(os.path.dirname(__file__))

class Config(object):
    SQLALCHEMY_DATABASE_URI = 'postgresql://senior_user:password@localhost/loadtestdb'
    SQLALCHEMY_TRACK_MODIFICATIONS = True
