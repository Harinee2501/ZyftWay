from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from backend import db
from backend.models import RideRequest, RideOffer, User
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy import func
from flask import jsonify
from datetime import datetime
from backend.models import Notification  # Make sure this is imported

routes_bp = Blueprint('routes', __name__)

@routes_bp.route('/')
def home():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('index.html', user=user)
    return redirect(url_for('routes.login'))

@routes_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()
        
        if existing_user:
            flash('Username already exists. Please choose another one.')
            return redirect(url_for('routes.register'))  
        if existing_email:
            flash('Email already registered. Please use a different email.')
            return redirect(url_for('routes.register'))  
        
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('routes.login'))
    
    return render_template('register.html')

@routes_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id  
            flash('Logged in successfully!')
            return redirect(url_for('routes.home')) 
        else:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('routes.login')) 
    
    return render_template('login.html')

@routes_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.')
    return redirect(url_for('routes.login'))

@routes_bp.route('/request_ride', methods=['GET', 'POST'])
def request_ride():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    
    if request.method == 'POST':
        pickup = request.form['pickup'].strip().lower()
        dropoff = request.form['dropoff'].strip().lower()
        
        new_ride_request = RideRequest(
            pickup=pickup,
            dropoff=dropoff,
            user_id=session['user_id']
        )
        db.session.add(new_ride_request)
        db.session.commit()
        
        # Try to match immediately
        matched_offer = RideOffer.query.filter(
            func.lower(RideOffer.pickup) == pickup,
            func.lower(RideOffer.dropoff) == dropoff
        ).first()
        
        if matched_offer:
            new_ride_request.matched_ride_id = matched_offer.id
            db.session.commit()
            flash('Ride requested and matched successfully!')
        else:
            flash('Ride requested successfully. No matches found yet.')
        
        return redirect(url_for('routes.home'))
    
    return render_template('request_ride.html')

@routes_bp.route('/offer_ride', methods=['GET', 'POST'])
def offer_ride():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    
    if request.method == 'POST':
        pickup = request.form['pickup_offer'].strip().lower()
        dropoff = request.form['dropoff_offer'].strip().lower()
        
        new_ride_offer = RideOffer(
            pickup=pickup,
            dropoff=dropoff,
            user_id=session['user_id']
        )
        db.session.add(new_ride_offer)
        db.session.commit()
        
        # Try to match immediately with existing requests
        matched_request = RideRequest.query.filter(
            func.lower(RideRequest.pickup) == pickup,
            func.lower(RideRequest.dropoff) == dropoff,
            RideRequest.matched_ride_id == None
        ).first()
        
        if matched_request:
            matched_request.matched_ride_id = new_ride_offer.id
            db.session.commit()
            flash('Ride offered and matched with an existing request!')
        else:
            flash('Ride offer posted successfully.')
        
        return redirect(url_for('routes.home'))
    
    return render_template('offer_ride.html')

@routes_bp.route('/my_rides')
def my_rides():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    
    user_id = session['user_id']
    offered_rides = RideOffer.query.filter_by(user_id=user_id).all()
    requested_rides = RideRequest.query.filter_by(user_id=user_id).all()
    
    return render_template('my_rides.html', 
                         offered_rides=offered_rides, 
                         requested_rides=requested_rides)

@routes_bp.route('/search_rides', methods=['POST'])
def search_rides():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))

    pickup = request.form['pickup'].strip().lower()
    dropoff = request.form['dropoff'].strip().lower()

    matches = RideOffer.query.filter(
        func.lower(RideOffer.pickup).contains(pickup),
        func.lower(RideOffer.dropoff).contains(dropoff)
    ).all()

    user = User.query.get(session['user_id'])
    return render_template('index.html', user=user, matches=matches)

@routes_bp.route('/confirm_ride', methods=['POST'])
def confirm_ride():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))

    ride_id = request.form['ride_id']
    pickup = request.form['pickup'].strip().lower()
    dropoff = request.form['dropoff'].strip().lower()

    requested_ride = RideRequest.query.filter_by(
        user_id=session['user_id'],
        pickup=pickup,
        dropoff=dropoff
    ).first()

    if requested_ride:
        requested_ride.matched_ride_id = ride_id
        db.session.commit()
        
        # Get the ride offer
        offered_ride = RideOffer.query.get(ride_id)
        
        if offered_ride:
            # Create notification for the ride offerer
            notification = Notification(
                user_id=offered_ride.user_id,
                message=f"User {session['user_id']} has confirmed your ride from {pickup} to {dropoff}",
                ride_id=ride_id,
                notification_type='ride_confirmed'
            )
            db.session.add(notification)
            db.session.commit()
        
        flash('Your ride has been confirmed with the selected offer. The driver has been notified.')
    else:
        flash('No matching ride request found to confirm.')

    return redirect(url_for('routes.home'))

@routes_bp.route('/notifications')
def notifications():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    
    user_notifications = Notification.query.filter_by(
        user_id=session['user_id']
    ).order_by(Notification.created_at.desc()).all()
    
    # Mark notifications as read when viewed
    for notification in user_notifications:
        if not notification.is_read:
            notification.is_read = True
            db.session.commit()
    
    return render_template('notifications.html', notifications=user_notifications)

@routes_bp.route('/check_notifications')
def check_notifications():
    if 'user_id' not in session:
        return jsonify({'unread_count': 0})
    
    unread_count = Notification.query.filter_by(
        user_id=session['user_id'],
        is_read=False
    ).count()
    
    return jsonify({'unread_count': unread_count})

@routes_bp.route('/match_rides', methods=['GET'])
def match_rides():
    print("Running matching algorithm...")
    
    # Get all unmatched requests
    unmatched_requests = RideRequest.query.filter_by(matched_ride_id=None).all()
    print(f"Found {len(unmatched_requests)} unmatched requests")
    
    match_count = 0
    
    for request in unmatched_requests:
        # Find matching offers
        matched_offer = RideOffer.query.filter(
            func.lower(RideOffer.pickup) == func.lower(request.pickup),
            func.lower(RideOffer.dropoff) == func.lower(request.dropoff)
        ).first()
        
        if matched_offer:
            request.matched_ride_id = matched_offer.id
            db.session.commit()
            match_count += 1
            print(f"Matched request {request.id} with offer {matched_offer.id}")
    
    flash(f"Matching completed. Found {match_count} new matches.")
    return redirect(url_for('routes.home'))

@routes_bp.route('/share_ride/<int:ride_id>', methods=['POST'])
def share_ride(ride_id):
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    
    ride = RideOffer.query.get_or_404(ride_id)
    
    requested_ride = RideRequest(
        pickup=ride.pickup, 
        dropoff=ride.dropoff, 
        user_id=session['user_id'], 
        matched_ride_id=ride.id
    )
    db.session.add(requested_ride)
    db.session.commit()

    flash(f'Your request to share a ride has been sent!')
    return redirect(url_for('routes.home'))

def init_app(app):
    app.register_blueprint(routes_bp)