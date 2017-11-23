# import relevant libraries
import os

from flask import Flask, request, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy

# configure flask app and SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

# setup SQL database and object
class Listing(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String, unique=False, nullable=False)
    job_link = db.Column(db.String, unique=False, nullable=False)
    org_name = db.Column(db.String, unique=False, nullable=False)
    source = db.Column(db.String, unique=False, nullable=False)
    date_posted = db.Column(db.DateTime, unique=False, nullable=True)

    def __init__(self, job_title, job_link, org_name, source, date_posted):
        self.job_title = job_title
        self.job_link = job_link
        self.org_name = org_name
        self.source = source
        self.date_posted = date_posted

# setup home page
@app.route("/")
def index():
    listings = Listing.query.order_by(Listing.id).all()
    return render_template("index.html", listings=listings)
