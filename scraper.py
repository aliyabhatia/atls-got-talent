# import relevant libraries 
import os
import urllib
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from bs4 import BeautifulSoup as soup

# configure flask app and SQLAlchemy
app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)

##### HELPER FUNCTIONS AND CLASSES THAT ARE USED THROUGHOUT #####

# Setup SQL database and object
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

# Grab Beautiful Soup from each website
def make_page_soup(my_url):
	# opening up the conection and grabbing the page - eventually should make this its own function
	req = urllib.request.Request(my_url, headers = {'User-Agent':"Magic Browser"})
	con = urllib.request.urlopen(req)
	page_html = con.read()
	con.close()

	# html parsing
	page_soup = soup(page_html, "html.parser")
	return page_soup

##### FUNCTIONS TO SCRAPE SPECIFIC SITES #####

# bridgespan non-profit job scraper
def bridgespan_scraper():
	# set url prefix for job descriptions
	url_prefix = "https://www.bridgespan.org/jobs/nonprofit-jobs/"

	# set my_url to a specific page
	my_url = 'https://www.bridgespan.org/jobs/nonprofit-jobs/nonprofit-job-board'

	page_soup = make_page_soup(my_url)

	# grabs each job listing
	containers = page_soup.findAll("div",{"class":"dxdvFlowItem_Moderno dxdvItem_Moderno JobsDataViewItem dx-wrap"})

	# grabs key information from each listing
	for container in containers:
		# grabs the location
		# note that not simple to isolate location in the tree
		# so instead find all the items with the same class location has
		# and go to the first item in that set which should be the location
		lighterListing = container.findAll("div",{"class":"LighterJobListing"})
		location = lighterListing[0].text
		
		# check if the job is in Atlanta
		if "Atlanta" in location:
			
			# pull the organization's name
			org_name_container = container.findAll("div",{"class":"OrgNameListing"})
			org_name = org_name_container[0].text.strip()
			
			# pull the name of the role and the URL for the listing
			job_title_container = container.findAll("div",{"class":"PositionTitleLink"})
			job_title = job_title_container[0].text.strip()
			job_link = url_prefix + job_title_container[0].a["href"]

			# identify static information
			source = "Bridgespan"
			date_posted = "2017-11-23"

			# create new db model object and post to SQL database
			new_listing = Listing(job_title, job_link, org_name, source, date_posted)
			db.session.add(new_listing)
			db.session.commit()

# # workforgood job scraper - searches pages 1-6 for roles containing one or more keywords
# def workforgood_scraper(key_words):
# 	# set url prefix for job descriptions
# 	url_prefix = "https://www.workforgood.org"
	
# 	# loop through pages 1 through 6 of workforgood site
# 	counter = 1
# 	while counter <= 6:
# 		if counter == 1:
# 			my_url = 'https://www.workforgood.org/landingpage/87/georgia-nonprofit-jobs/'
# 		else:
# 			my_url = 'https://www.workforgood.org/landingpage/87/georgia-nonprofit-jobs/' + str(counter) + '/'
		
# 		page_soup = make_page_soup(my_url)

# 		# grabs each listing
# 		containers = page_soup.findAll("div",{"class":"lister__details cf js-clickable"})

# 		for container in containers:
			
# 			# grab the name of the role
# 			role_name_container = container.findAll("h3",{"class":"lister__header"})
# 			role_name = role_name_container[0].text
			
# 			# filter for roles with keywords
# 			if any(x in role_name for x in key_words):
				
# 				# pull url and organization name
# 				role_url = role_name_container[0].a["href"]
# 				org_name_container = container.findAll("li",{"itemprop":"hiringOrganization"})
# 				org_name = org_name_container[0].text

# 				# append job postings to csv
# 				add_to_csv(org_name,role_name,url_prefix,role_url)

# 		counter += 1

# def boardwalk_scraper():
# 	# set url prefix for job descriptions
# 	url_prefix = "http://www.boardwalkconsulting.com/"

# 	# set my_url to a specific page
# 	my_url = "http://www.boardwalkconsulting.com/our-clients.aspx"

# 	page_soup = make_page_soup(my_url)

# 	# grabs subset of HTML with job listings
# 	boardwalk_clients = page_soup.findAll("div",{"id":"clientsColumn2"})

# 	# grabs each job listing
# 	containers = boardwalk_clients[0].findAll("div")

# 	# grabs key information from each listing
# 	for container in containers:
# 		possible_roles = container.findAll("p")
		
# 		for possible_role in possible_roles:

# 			# screen for "Active Assignment"
# 			if "Active Assignment" in possible_role.text:
# 				# screen for Atlanta
# 				if "Atlanta" in container.h1.text:
					
# 					# pull the name of the role
# 					role_name = possible_role.text.replace('Active Assignment: ','').replace('View Leadership Profile','')
					
# 					# pull the Organizationnization's name
# 					org_name = container.h1.text.replace(', Atlanta, GA','')
					
# 					# pull the URL for the listing
# 					role_url = possible_role.a["href"]

# 					# append job postings to csv
# 					add_to_csv(org_name,role_name,url_prefix,role_url)

##### MAIN CODE STARTS HERE #####

# master list of key words for more varied job searches
# key_words = ['Director','Chief','Senior','Vice President','Officer']

# call individual scrapers
bridgespan_scraper()
# workforgood_scraper(key_words)
# boardwalk_scraper()