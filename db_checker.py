from backend import create_app, db
from backend.models import User, RideOffer, RideRequest  # ✅ import all models

app = create_app()

def check_all_data():
    with app.app_context():
        print("=== Users ===")
        users = User.query.all()
        for user in users:
            print(f"ID: {user.id}, Username: {user.username}, Email: {user.email}")

        print("\n=== Offered Rides ===")
        offered_rides = RideOffer.query.all()
        for ride in offered_rides:
            print(f"ID: {ride.id}, Pickup: {ride.pickup}, Dropoff: {ride.dropoff}, User ID: {ride.user_id}")

        print("\n=== Requested Rides ===")
        requested_rides = RideRequest.query.all()
        for request in requested_rides:
            print(f"ID: {request.id}, Pickup: {request.pickup}, Dropoff: {request.dropoff}, "
                  f"User ID: {request.user_id}, Matched Ride ID: {request.matched_ride_id}")

if __name__ == "__main__":
    check_all_data()
