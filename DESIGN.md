# Talented Atlantans - Design Documentation

## listing.py

**Listing.py creates a single Flask-SQLAlchemy class for the database object that holds job listings. It is then imported into scraper.py and application.py for use in those files. Technical details:**
* id is a primary key and is set to auto-populate/auto-increment
* job_title, job_link, org_name, and source are all strings and required inputs - for now, they can be any length as Postgres does not require a character limit and the format of the data suggests these items will already be short in the first place
* date_posted is a datetime object and is not required, as there may be versions of this app in the future that leave the date_posted field blank for un-dated postings

## scraper.py

**Scraper.py pulls senior-level jobs from several sites on a daily basis so they can be served up to the Talented Atlantans site. Technical details:**
* Is a Flask app so that it can use the same `listing.py` model for storing to the Postgres SQL database
* Runs daily using the Heroku Scheduler plug-in
* Uses `Beautiful Soup` plug-in to support web scraping using HTML tags (e.g. "class," "div," and "li" tags) to identify valuable information
* For each site, the scraper first checks that it can open the page using a `try except` sequence in the `make_page_soup()` function, then deletes database entries related to that page so that it can load in revised set of entries
* Some sites (Bridgespan, Boardwalk) only include senior level roles, in which case all Atlanta-area roles are scraped - other sites (Work For Good) have a range of roles, so a set of key words are used to narrow down which Atlanta-area roles are scraped
* Some sites (Bridgespan, Work For Good) include the date posted which the Scraper will pull - other sites (Boardwalk) do not, and are assigned a random date in the last 30 days using the `rand_date()` function to help vary where the user sees these posts in the list (rather than putting them all in any one part of the list)

## application.py

**Application.py pulls in everything stored in the Postgres SQL database, sorts by date, and then serves that up to the front-end website. Technical details:**
* Like `scraper.py`, `application.py` also pulls from `listing.py` as its model for the Postgres SQL database listings 
* The homepage function `index()` first checks if there are any listings to pull - if not, then it serves up an error message

## static/styles.css

**CSS for the site was developed by using Webflow to craft the styles, colors, and mobile-responsiveness, and then saving the CSS from that Webflow site to the static/styles.css file.**

## other helper documents

* **The Procfile** helps Heroku determine what type of project this is - in this case, a web app
* **requirements.txt** helps Heroku install the right plug-ins and add-ons to support the application
* **runtime.txt** specifies which version of Python to use to run the python files
