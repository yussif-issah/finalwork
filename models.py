from db import db
from flask_login import UserMixin



class User(db.Model,UserMixin):
    id=db.Column(db.Integer,primary_key=True)
    email=db.Column(db.String(150),unique=True)
    password=db.Column(db.String(150))
    fullname=db.Column(db.String(150))
    contact=db.Column(db.String(150))
    town=db.Column(db.String(150))

class imgModel(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    img=db.Column(db.Text,nullable=False)
    name=db.Column(db.Text,nullable=False)
    mimetype=db.Column(db.Text,nullable=False)
    prediction=db.Column(db.String(100))
    crop=db.Column(db.String(100))
    user=db.Column(db.Integer,db.ForeignKey("user.id"))



