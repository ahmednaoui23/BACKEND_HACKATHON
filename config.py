from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Config:
    SQLALCHEMY_DATABASE_URI = "mysql+pymysql://root:Hayder1920@localhost:3306/indus"
    SQLALCHEMY_TRACK_MODIFICATIONS = False