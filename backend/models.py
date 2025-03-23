from flask_pymongo import PyMongo
from flask import Flask

app = Flask(__name__)

# MongoDB URI
app.config['MONGO_URI'] = 'mongodb://localhost:27017/zyftgo'
mongo = PyMongo(app)

# Model for ride request
class Ride:
    def __init__(self, pickup, dropoff, user_id, driver_id=None):
        self.pickup = pickup
        self.dropoff = dropoff
        self.user_id = user_id
        self.driver_id = driver_id

    def save(self):
        ride_data = {
            'pickup': self.pickup,
            'dropoff': self.dropoff,
            'user_id': self.user_id,
            'driver_id': self.driver_id
        }
        mongo.db.rides.insert_one(ride_data)
