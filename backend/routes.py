from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from backend import db
from backend.models import RideRequest, RideOffer, User
from werkzeug.security import generate_password_hash, check_password_hash

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
        
        # Check if username or email already exists
        existing_user = User.query.filter_by(username=username).first()
        existing_email = User.query.filter_by(email=email).first()
        
        if existing_user:
            flash('Username already exists. Please choose another one.')
            return redirect(url_for('routes.register'))  # Correct
        if existing_email:
            flash('Email already registered. Please use a different email.')
            return redirect(url_for('routes.register'))  # Correct
        
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, email=email, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('routes.login'))  # Correct
    
    return render_template('register.html')



@routes_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id  # Store user ID in session
            flash('Logged in successfully!')
            return redirect(url_for('routes.home'))  # Redirect to home page
        else:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('routes.login'))  # Stay on login page if invalid credentials
    
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
        pickup = request.form['pickup']
        dropoff = request.form['dropoff']
        new_ride_request = RideRequest(pickup=pickup, dropoff=dropoff, user_id=session['user_id'])
        db.session.add(new_ride_request)
        db.session.commit()
        flash('Ride requested successfully.')
        return redirect(url_for('routes.home'))
    return render_template('request_ride.html')

@routes_bp.route('/offer_ride', methods=['GET', 'POST'])
def offer_ride():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    
    if request.method == 'POST':
        pickup = request.form['pickup_offer']  # Changed to match 'pickup_offer'
        dropoff = request.form['dropoff_offer']  # Changed to match 'dropoff_offer'
        
        new_ride_offer = RideOffer(pickup=pickup, dropoff=dropoff, user_id=session['user_id'])
        db.session.add(new_ride_offer)
        db.session.commit()
        
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
    return render_template('my_rides.html', offered_rides=offered_rides, requested_rides=requested_rides)

@routes_bp.route('/search_rides', methods=['POST'])
def search_rides():
    pickup = request.form['pickup']
    dropoff = request.form['dropoff']
    
    # Find matching offered rides based on pickup and dropoff
    matches = RideOffer.query.filter(
        RideOffer.pickup.ilike(f"%{pickup}%"),
        RideOffer.dropoff.ilike(f"%{dropoff}%")
    ).all()
    
    # Iterate through the matches and find requested rides that are not yet matched
    for match in matches:
        # Check for requested rides that match this offered ride
        requested_ride = RequestedRide.query.filter_by(
            pickup=match.pickup,
            dropoff=match.dropoff,
            matched_ride_id=None  # Ensure this ride hasn't been matched yet
        ).first()
        
        if requested_ride:
            # If a match is found, update the matched_ride_id
            requested_ride.matched_ride_id = match.id
            db.session.commit()  # Commit the changes to the database
            
            # Optionally print to debug:
            print(f"Match found! Requested Ride ID: {requested_ride.id} matched with Offered Ride ID: {match.id}")
    
    # Fetch the current user for rendering the template
    user = User.query.get(session['user_id'])
    
    # Return the matches to the template
    return render_template('index.html', user=user, matches=matches)



@routes_bp.route('/confirm_ride', methods=['POST'])
def confirm_ride():
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    ride_id = request.form['ride_id']
    pickup = request.form['pickup']
    dropoff = request.form['dropoff']
    
    # Creating a ride request and linking to the offered ride
    requested_ride = RideRequest(
        pickup=pickup, 
        dropoff=dropoff, 
        user_id=session['user_id'], 
        matched_ride_id=ride_id
    )
    db.session.add(requested_ride)
    db.session.commit()
    flash('Your ride has been confirmed with the selected match.')
    return redirect(url_for('routes.home'))



@routes_bp.route('/share_ride/<int:ride_id>', methods=['POST'])
def share_ride(ride_id):
    if 'user_id' not in session:
        return redirect(url_for('routes.login'))
    
    # Find the offered ride
    ride = RideOffer.query.get_or_404(ride_id)
    
    # Create a RideRequest with matched ride information
    requested_ride = RideRequest(
        pickup=ride.pickup, 
        dropoff=ride.dropoff, 
        user_id=session['user_id'], 
        matched_ride_id=ride.id
    )
    db.session.add(requested_ride)
    db.session.commit()

    flash(f'Your request to share a ride with user {ride.user_id} has been sent!')
    return redirect(url_for('routes.home'))

@routes_bp.route('/request_match/<int:ride_id>', methods=['POST'])
def request_match(ride_id):
    # Get the requested ride
    requested_ride = RequestedRide.query.get(ride_id)
    
    # Find the offered ride that matches
    offered_ride = RideOffer.query.get(requested_ride.matched_ride_id)
    
    # If a matching offered ride is found, update the requested ride
    if offered_ride:
        requested_ride.matched_ride_id = offered_ride.id
        db.session.commit()  # Commit the change to the database
        
    return redirect(url_for('index'))  # Redirect to the index page (or wherever necessary)


@routes_bp.route('/match_rides', methods=['GET'])
def match_rides():
    print("Match rides route has been triggered!")
    offered_rides = RideOffer.query.all()
    requested_rides = RideRequest.query.all()

    # Log the number of offered and requested rides
    print(f"Number of offered rides: {len(offered_rides)}")  # Log number of offered rides
    print(f"Number of requested rides: {len(requested_rides)}")  # Log number of requested rides

    # Check if there are any offered and requested rides
    if not offered_rides:
        print("No offered rides available.")
    if not requested_rides:
        print("No requested rides available.")

    # Loop through requested rides to find a match
    match_found = False  # Flag to check if any match is found
    for requested_ride in requested_rides:
        for offered_ride in offered_rides:
            # Exact match check for both pickup and dropoff locations
            if (requested_ride.pickup.lower() == offered_ride.pickup.lower() and
                requested_ride.dropoff.lower() == offered_ride.dropoff.lower()):
                # Log the match found
                print(f"Match found: Requested Ride ID: {requested_ride.id} - Offered Ride ID: {offered_ride.id}")

                # Update the requested ride with the matched ride ID
                requested_ride.matched_ride_id = offered_ride.id
                db.session.commit()  # Save the matched ride ID in the database

                # Log after committing
                print(f"Requested ride {requested_ride.id} matched with offered ride {offered_ride.id}")
                match_found = True  # Set flag to True when a match is found
                break  # Once a match is found, exit the inner loop

    if not match_found:
        print("No matches were found.")  # Log if no matches were found

    return redirect(url_for('routes.home'))  # Redirect or render the matched rides view




def init_app(app):
    app.register_blueprint(routes_bp)
