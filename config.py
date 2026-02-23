from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:1234@localhost/hackathon?charset=utf8"
    SQLALCHEMY_TRACK_MODIFICATIONS = False