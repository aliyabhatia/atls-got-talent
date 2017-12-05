##### IMPORT RELEVANT LIBRARIES #####

# os helps detect environment variables, in this case the DB URL
import os

# flask and sqlalchemy facilitate web app
from flask import Flask, request, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

# import Listing db class object
from listing import Listing


##### CONFIGURE FLASK APP AND SQLALCHEMY #####

# configure flask app and SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


##### MAIN FLASK APP #####

# setup home page to pull job listings from server
@app.route("/")
def index():
    # establish listings as set of objects from server
    listings = Listing.query.order_by(Listing.date_posted.desc()).all()

    # check if listings pull was successful
    # if it failed, redirect to an error message
    if len(listings) == 0:
    	return render_template("error.html")

    # if listings pull succeeded, serve up listings to index.html
    return render_template("index.html", listings=listings)
