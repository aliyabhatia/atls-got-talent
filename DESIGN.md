# Talented Atlantans - Design Documentation

## Listing.py

**Listing.py creates a single Flask-SQLAlchemy class for the database object that holds job listings. It is then imported into scraper.py and application.py for use in those files. Technical details:**
* id is a primary key and is set to auto-populate/auto-increment
* job_title, job_link, org_name, and source are all strings and required inputs - for now, they can be any length as Postgres does not require a character limit and the format of the data suggests these items will already be short in the first place
* date_posted is a datetime object and is not required, as there may be versions of this app in the future that leave the date_posted field blank for un-dated postings

## Scraper.py

**Scraper.py pulls senior-level jobs from several sites on a daily basis so they can be served up to the Talented Atlantans site. Technical details:**
* Runs daily using the Heroku Scheduler plug-in - currently, the scraper first deletes everything in the Heroku Postgres database before replenishing it with the up-to-date job listings
* Uses `Beautiful Soup` plug-in to support web scraping using HTML tags (e.g. "class," "div," and "li" tags) to identify valuable information
* Some sites (Bridgespan, Boardwalk) only include senior level roles, in which case all Atlanta-area roles are scraped - other sites (Work For Good) have a range of roles, so a set of key words are used to narrow down which Atlanta-area roles are scraped
* Some sites (Bridgespan, Work For Good) include the date posted which the Scraper will pull - other sites (Boardwalk) do not, and are assigned a random date in the last 30 days using the `rand_date()` function to help vary where the user sees these posts in the list

## Application.py

## Other helper documents

* **The Procfile** helps Heroku determine what type of project this is - in this case, a web app
* **requirements.txt** helps Heroku install the right plug-ins and add-ons to support the application
