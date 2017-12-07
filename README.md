# atls-got-talent

**Talented Atlantans** supports metro Atlanta's talent retention aspirations by creating transparency around senior level non-profit roles in the area. Very simply, it is a website that gathers senior level non-profit jobs from various job listing sites and posts them, roughly in order of the date they were posted.

The **Talented Atlantans site** itself is at https://atls-got-talent.herokuapp.com/ 

Clicking any particular job posting opens the posting in a new window for the a job-seeker to explore further. 

If your local terminal has all the installations and plug-ins listed in `requirements.txt`, then you can manually run a locally-hosted Flask version of this app through the following sequence of commands:

````
source .env
export FLASK_APP=application.py
flask run
````

Note that the CS50 IDE does NOT by default have all these plugins. For grading purposes, I recommend going to the website listed above.

The **Talented Atlantans scraper** (aka the `scraper.py` file) and its corresponding Postgres database can also be used independently. Heroku runs the scraper once per day through the Heroku scheduler. However, a user can force the scraper to update the database through the following sequence of commands:

````
source .env
python scraper.py
````
