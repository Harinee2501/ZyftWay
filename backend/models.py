from datetime import datetime
from backend import db
from sqlalchemy import func

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), nullable=False, unique=True)
    email = db.Column(db.String(120), nullable=False, unique=True)
    password = db.Column(db.String(200), nullable=False)
    ride_offers = db.relationship('RideOffer', backref='user', lazy=True)
    ride_requests = db.relationship('RideRequest', backref='user', lazy=True)
    notifications = db.relationship('Notification', backref='user', lazy=True)

class RideOffer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pickup = db.Column(db.String(100), nullable=False)
    dropoff = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    __table_args__ = (
        db.Index('ix_ride_offer_pickup_dropoff', func.lower(pickup), func.lower(dropoff)),
    )

class RideRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pickup = db.Column(db.String(100), nullable=False)
    dropoff = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    matched_ride_id = db.Column(db.Integer, db.ForeignKey('ride_offer.id'))
    matched_ride = db.relationship('RideOffer', backref='matched_requests', foreign_keys=[matched_ride_id])
    
    __table_args__ = (
        db.Index('ix_ride_request_pickup_dropoff', func.lower(pickup), func.lower(dropoff)),
    )

class Notification(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message = db.Column(db.String(200), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    ride_id = db.Column(db.Integer)  # Can be either offer or request ID
    notification_type = db.Column(db.String(50))  # e.g., 'ride_confirmed'