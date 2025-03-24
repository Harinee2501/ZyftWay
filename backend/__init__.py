from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os

# Initialize the Flask app
app = Flask(__name__, template_folder='../templates') 


# Set up the database URI (update this based on your database choice)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///zyftway.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database
db = SQLAlchemy(app)

# Import routes after app is created to avoid circular imports
from backend import routes
