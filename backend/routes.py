from flask import Blueprint, request, jsonify
from backend.models import Ride

bp = Blueprint('rides', __name__)

# Route to request a ride
@bp.route('/api/request_ride', methods=['POST'])
def request_ride():
    data = request.get_json()
    pickup = data.get('pickup')
    dropoff = data.get('dropoff')

    if not pickup or not dropoff:
        return jsonify({'error': 'Invalid request'}), 400

    # Assuming user_id is provided as part of the request (for simplicity)
    user_id = 1  # Placeholder, in a real application, this would be dynamic

    new_ride = Ride(pickup, dropoff, user_id)
    new_ride.save()

    return jsonify({'message': 'Ride requested successfully'}), 200
