##### IMPORT RELEVANT LIBRARIES #####

# os helps detect environment variables, in this case the DB URL
import os

# flask and sqlalchemy facilitate web app
from flask import Flask, request, render_template, url_for, redirect
from flask_sqlalchemy import SQLAlchemy


##### CONFIGURE FLASK APP AND SQLALCHEMY #####

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


##### SETUP SQL DATABASE OBJECT FOR USE IN WEB APP #####

class Listing(db.Model):

    # establish model for Listing database object 
    id = db.Column(db.Integer, primary_key=True)
    job_title = db.Column(db.String, unique=False, nullable=False)
    job_link = db.Column(db.String, unique=False, nullable=False)
    org_name = db.Column(db.String, unique=False, nullable=False)
    source = db.Column(db.String, unique=False, nullable=False)
    date_posted = db.Column(db.DateTime, unique=False, nullable=True)

    # initialization method to create new database object
    def __init__(self, job_title, job_link, org_name, source, date_posted):
        self.job_title = job_title
        self.job_link = job_link
        self.org_name = org_name
        self.source = source
        self.date_posted = date_posted