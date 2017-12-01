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
	# opening up the conection and grabbing HTML from the page
	req = urllib.request.Request(my_url, headers = {'User-Agent':"Magic Browser"})
	con = urllib.request.urlopen(req)
	page_html = con.read()
	con.close()

	# html parsing
	page_soup = soup(page_html, "html.parser")
	return page_soup


##### FUNCTIONS TO SCRAPE SPECIFIC SITES #####

# random date generator
# generates a random date in last 30 days to give useful date to un-dated listings
def rand_date():
	
	# get number of seconds in a 30 day range - 30 times hours/day times mins/hour times seconds/minute
	int_delta = (30 * 24 * 60 * 60)

	# generate a random second in that 30-day range (and therefore a random day as well)
	random_second = randrange(int_delta)

	# return today minus the random moment between 0 and 30 days to get a time in the last 30 days
	return datetime.now() + timedelta(seconds=(-1 * random_second))

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

			# get the posting date and convert into datetime object
			date_posted_raw = container.findAll("div",{"class":"LighterJobListing"})[2].text.strip().replace('Date Posted:', '').strip()
			date_posted = datetime.strptime(date_posted_raw, '%m/%d/%Y')

			# identify source
			source = "Bridgespan"

			# create new db model object and post to SQL database
			new_listing = Listing(job_title, job_link, org_name, source, date_posted)
			db.session.add(new_listing)
			db.session.commit()

# workforgood job scraper - searches pages 1-6 for roles containing one or more keywords
def workforgood_scraper(key_words):
	
	# set url prefix for job descriptions
	url_prefix = "https://www.workforgood.org"
	
	# loop through pages 1 through 6 of workforgood Georgia site
	counter = 1
	while counter <= 6:
		if counter == 1:
			my_url = 'https://www.workforgood.org/landingpage/87/georgia-nonprofit-jobs/'
		else:
			my_url = 'https://www.workforgood.org/landingpage/87/georgia-nonprofit-jobs/' + str(counter) + '/'
		
		page_soup = make_page_soup(my_url)

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
				org_name_container = container.findAll("li",{"itemprop":"hiringOrganization"})
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
				new_listing = Listing(job_title, job_link, org_name, source, date_posted)
				db.session.add(new_listing)
				db.session.commit()
		
		counter += 1

def boardwalk_scraper():
	
	# set url prefix for job descriptions
	url_prefix = "http://www.boardwalkconsulting.com/"

	# set my_url to a specific page
	my_url = "http://www.boardwalkconsulting.com/our-clients.aspx"

	page_soup = make_page_soup(my_url)

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
					new_listing = Listing(job_title, job_link, org_name, source, date_posted)
					db.session.add(new_listing)
					db.session.commit()


##### MAIN CODE STARTS HERE #####

# clear out data from database
db.session.query(Listing).delete()

# master list of key words for more varied job searches
key_words = ['Director','Chief','Senior','Vice President','Officer']

# call individual scrapers
bridgespan_scraper()
workforgood_scraper(key_words)
boardwalk_scraper()