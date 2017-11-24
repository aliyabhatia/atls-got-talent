# import relevant libraries
import os

from flask import Flask, request, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

# import Listing db class object
from listing import Listing

# configure flask app and SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

# setup home page
@app.route("/")
def index():
    listings = Listing.query.order_by(Listing.id).all()
    return render_template("index.html", listings=listings)
