from flask_sqlalchemy import SQLAlchemy
from backend import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    ride_offers = db.relationship('RideOffer', backref='user', lazy=True)
    ride_requests = db.relationship('RideRequest', backref='user', lazy=True)

class RideOffer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pickup = db.Column(db.String(100), nullable=False)
    dropoff = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

class RideRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pickup = db.Column(db.String(100), nullable=False)
    dropoff = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    matched_ride_id = db.Column(db.Integer, db.ForeignKey('ride_offer.id'))
    matched_ride = db.relationship('RideOffer', backref='matched_requests', foreign_keys=[matched_ride_id])
