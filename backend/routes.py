from flask import render_template, request, redirect, url_for, session, flash
from backend import app, db
from backend.models import RideRequest, RideOffer, User
from werkzeug.security import generate_password_hash, check_password_hash

app.secret_key = 'supersecret123'

@app.route('/')
def home():
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return render_template('index.html', user=user)
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        hashed_pw = generate_password_hash(password, method='pbkdf2:sha256')
        new_user = User(username=username, password=hashed_pw)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash('Logged in successfully!')
            return redirect(url_for('home'))
        else:
            flash('Invalid credentials. Please try again.')
            return redirect(url_for('login'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    flash('Logged out successfully.')
    return redirect(url_for('login'))

@app.route('/request_ride', methods=['GET', 'POST'])
def request_ride():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        pickup = request.form['pickup']
        dropoff = request.form['dropoff']
        new_ride_request = RideRequest(pickup=pickup, dropoff=dropoff, user_id=session['user_id'])
        db.session.add(new_ride_request)
        db.session.commit()
        flash('Ride requested successfully.')
        return redirect(url_for('home'))
    return render_template('request_ride.html')

@app.route('/offer_ride', methods=['GET', 'POST'])
def offer_ride():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        pickup_offer = request.form['pickup_offer']
        dropoff_offer = request.form['dropoff_offer']
        new_ride_offer = RideOffer(pickup_offer=pickup_offer, dropoff_offer=dropoff_offer, user_id=session['user_id'])
        db.session.add(new_ride_offer)
        db.session.commit()
        flash('Ride offer posted successfully.')
        return redirect(url_for('home'))
    return render_template('offer_ride.html')

@app.route('/my_rides')
def my_rides():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    offered_rides = RideOffer.query.filter_by(user_id=user_id).all()
    requested_rides = RideRequest.query.filter_by(user_id=user_id).all()
    return render_template('my_rides.html', offered_rides=offered_rides, requested_rides=requested_rides)

@app.route('/search_rides', methods=['GET', 'POST'])
def search_rides():
    if request.method == 'POST':
        pickup = request.form['pickup']
        dropoff = request.form['dropoff']
        rides = RideOffer.query.filter(
            RideOffer.pickup_offer.contains(pickup),
            RideOffer.dropoff_offer.contains(dropoff)
        ).all()
        return render_template('search_results.html', rides=rides)
    return render_template('search_rides.html')

@app.route('/share_ride/<int:ride_id>', methods=['POST'])
def share_ride(ride_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    ride = RideOffer.query.get_or_404(ride_id)
    flash(f'Your request to share ride with user {ride.user_id} has been sent!')
    return redirect(url_for('search_rides'))
