from backend import db, app
from backend.models import User, RideOffer, RideRequest

def check_users():
    users = User.query.all()
    print("=== Users in Database ===")
    if not users:
        print("No users found.")
    for user in users:
        print(f"ID: {user.id}, Username: {user.username}")

def check_ride_offers():
    offers = RideOffer.query.all()
    print("\n=== Offered Rides ===")
    if not offers:
        print("No ride offers found.")
    for offer in offers:
        print(f"ID: {offer.id}, From: {offer.pickup_offer}, To: {offer.dropoff_offer}, User ID: {offer.user_id}")

def check_ride_requests():
    requests = RideRequest.query.all()
    print("\n=== Requested Rides ===")
    if not requests:
        print("No ride requests found.")
    for request in requests:
        print(f"ID: {request.id}, From: {request.pickup}, To: {request.dropoff}, User ID: {request.user_id}")

if __name__ == "__main__":
    with app.app_context():
        check_users()
        check_ride_offers()
        check_ride_requests()
