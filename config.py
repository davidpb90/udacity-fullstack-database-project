import os

class Config:
    SECRET_KEY = os.urandom(32)
    # Grabs the folder where the script runs.
    basedir = os.path.abspath(os.path.dirname(__file__))

    # Enable debug mode.
    #DEBUG = True
    # TODO IMPLEMENT DATABASE URL
    # Connect to the database
    SQLALCHEMY_DATABASE_URI = 'postgresql://davidpardob@localhost:5432/fyyur'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'max_overflow': 20,
        'pool_pre_ping': True,
        'pool_recycle': 300,
    }




