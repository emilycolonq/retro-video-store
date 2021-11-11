from app import db
from flask import current_app

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String)
    release_date = db.Column(db.DateTime)
    total_inventory = db.Column(db.Integer)
    
    customer = db.relationship("Customer", secondary = "rental", backref="videos")
