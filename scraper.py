##### IMPORT RELEVANT LIBRARIES AND CLASSES #####

# os helps detect environment variables, in this case the DB URL
import os

# urllib and beautiful soup facilitate scraping
import urllib
from bs4 import BeautifulSoup as soup

# datetime to support parsing posting dates
from datetime import datetime, timedelta

# import random range generator to help make random dates for Boardwalk listings
from random import randrange

# flask and sqlalchemy facilitate web app
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy

# import Listing db class object
from listing import Listing


##### CONFIGURE FLASK APP AND SQLALCHEMY #####

app = Flask(__name__)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ['DATABASE_URL']
db = SQLAlchemy(app)


##### HELPER FUNCTIONS THAT ARE USED THROUGHOUT #####

# Grab Beautiful Soup from each website
def make_page_soup(my_url):
	try:
		# opening up the conection and grabbing HTML from the page
		# set timeout limit to 60 seconds
		req = urllib.request.Request(my_url, headers = {'User-Agent':"Magic Browser"})
		con = urllib.request.urlopen(req, timeout=60)
		page_html = con.read()
		con.close()

		# initiate html parsing
		page_soup = soup(page_html, "html.parser")
		return page_soup
	
	# if the website does not respond or there is another failure to grab the HTML, return none 
	# which will then prompt that scraper to exit without deleting current entries
	except:
		return None

# random date generator
# generates a random date in last 30 days to give useful date to un-dated listings
def rand_date():
	
	# get number of days in a 30 day range
	int_delta = 30

	# generate a random day in that 30-day range
	random_day = randrange(int_delta)

	# return today minus the random moment between 0 and 30 days to get a time in the last 30 days
	return datetime.now() - timedelta(days=random_day)

# write new listing to database
def write_listing(job_title, job_link, org_name, source, date_posted):
	new_listing = Listing(job_title, job_link, org_name, source, date_posted)
	db.session.add(new_listing)
	db.session.commit()


##### FUNCTIONS TO SCRAPE SPECIFIC SITES #####

# bridgespan non-profit job scraper
def bridgespan_scraper():
	
	# set url prefix for job descriptions
	url_prefix = "https://www.bridgespan.org/jobs/nonprofit-jobs/"

	# set my_url to a specific page
	my_url = 'https://www.bridgespan.org/jobs/nonprofit-jobs/nonprofit-job-board'

	page_soup = make_page_soup(my_url)

	# check for an error, e.g. timeout or other reason why no page soup returned
	if not page_soup:
		return

	# delete existing Bridgespan listings
	db.session.query(Listing).filter_by(source="Bridgespan").delete()

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

			# get the posting date and convert into datetime object
			date_posted_raw = container.findAll("div",{"class":"LighterJobListing"})[2].text.strip().replace('Date Posted:', '').strip()
			date_posted = datetime.strptime(date_posted_raw, '%m/%d/%Y')

			# identify source
			source = "Bridgespan"

			# create new db model object and post to SQL database using write_listing() helper function
			write_listing(job_title, job_link, org_name, source, date_posted)

# workforgood job scraper - searches pages 1-6 for roles containing one or more keywords
def workforgood_scraper(key_words):
	
	# set url prefix for job descriptions
	url_prefix = "https://www.workforgood.org"
	
	# check for an error, e.g. timeout or other reason why no page soup returned
	my_url = 'https://www.workforgood.org/landingpage/87/georgia-nonprofit-jobs/'
	page_soup = make_page_soup(my_url)
	if not page_soup:
		return

	# delete existing Work For Good listings
	db.session.query(Listing).filter_by(source="Work For Good").delete()

	# loop through pages 1 through 6 of workforgood Georgia site
	counter = 2
	while counter <= 6:

		# first round through while loop uses page_soup from first Work for Good page
		# which was already collected in error checking above
		# this avoids additional unecessary calculations since this page has already been "scraped"

		# grabs each listing
		containers = page_soup.findAll("div",{"class":"lister__details cf js-clickable"})

		for container in containers:
			
			# grab the name of the role
			job_title_container = container.findAll("h3",{"class":"lister__header"})
			job_title = job_title_container[0].text
			
			# filter for roles with keywords
			if any(x in job_title for x in key_words):
				
				# pull url and organization name
				job_link = url_prefix + job_title_container[0].a["href"]
				org_name_container = container.findAll("li",{"class":"lister__meta-item lister__meta-item--recruiter"})
				org_name = org_name_container[0].text

				# identify date posted
				# have to go into the link for the job posting
				date_posted_soup = make_page_soup(job_link)

				# find all relevant classes where date posted could be
				role_items = date_posted_soup.findAll("div",{"class":"cf margin-bottom-5"})

				# search through different attributes until date posted is found
				for role_item in role_items:
					if "Posted" in role_item.text:
						date_posted_raw = role_item.text.strip().replace('Posted','').strip()
						date_posted = datetime.strptime(date_posted_raw, '%b %d, %Y')
						break

				# identify static information
				source = "Work For Good"

				# create new db model object and post to SQL database
				write_listing(job_title, job_link, org_name, source, date_posted)
		
		# get page soup for current counter - starts at 2 and increments until 6 per the while loop
		my_url = 'https://www.workforgood.org/landingpage/87/georgia-nonprofit-jobs/' + str(counter) + '/'
		page_soup = make_page_soup(my_url)

		# increment counter for next loop
		counter += 1

def boardwalk_scraper():
	
	# set url prefix for job descriptions
	url_prefix = "http://www.boardwalkconsulting.com/"

	# set my_url to a specific page
	my_url = "http://www.boardwalkconsulting.com/our-clients.aspx"

	page_soup = make_page_soup(my_url)

	# check for an error, e.g. timeout or other reason why no page soup returned
	if not page_soup:
		return

	# delete existing Boardwalk listings
	db.session.query(Listing).filter_by(source="Boardwalk").delete()

	# grabs subset of HTML with job listings
	boardwalk_clients = page_soup.findAll("div",{"id":"clientsColumn2"})

	# grabs each job listing
	containers = boardwalk_clients[0].findAll("div")

	# get today's date
	now = datetime.now()

	# grabs key information from each listing
	for container in containers:
		possible_roles = container.findAll("p")
		
		for possible_role in possible_roles:

			# screen for "Active Assignment"
			if "Active Assignment" in possible_role.text:
				# screen for Atlanta
				if "Atlanta" in container.h1.text:
					
					# pull the name of the role
					job_title = possible_role.text.replace('Active Assignment: ','').replace('View Leadership Profile','')
					
					# pull the Organizationnization's name
					org_name = container.h1.text.replace(', Atlanta, GA','')
					
					# pull the URL for the listing
					job_link = url_prefix + possible_role.a["href"]

					# Boardwalk doesn't seem to share date posted, so need to create "pseudodate"
					# call rand_date() function to find a random date in last 30 days
					date_posted = rand_date()					

					# identify static information
					source = "Boardwalk"

					# create new db model object and post to SQL database
					write_listing(job_title, job_link, org_name, source, date_posted)

##### MAIN CODE STARTS HERE #####

# master list of key words for more varied job searches
key_words = ['Director','Chief','Senior','Vice President','Officer','Executive','VP','President']

# call individual scrapers
bridgespan_scraper()
workforgood_scraper(key_words)
boardwalk_scraper()