import os

class Config:
    SECRET_KEY = 'secretkey123'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///ucsp.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
