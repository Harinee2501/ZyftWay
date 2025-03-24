from backend import db

class User(db.Model):
    __tablename__ = 'user'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)  # store hashed password

class RideRequest(db.Model):
    __tablename__ = 'ride_request'
    
    id = db.Column(db.Integer, primary_key=True)
    pickup = db.Column(db.String(100), nullable=False)
    dropoff = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # add this line

class RideOffer(db.Model):
    __tablename__ = 'ride_offer'
    
    id = db.Column(db.Integer, primary_key=True)
    pickup_offer = db.Column(db.String(100), nullable=False)
    dropoff_offer = db.Column(db.String(100), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # add this line
