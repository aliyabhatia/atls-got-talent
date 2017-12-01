# atls-got-talent

**Talented Atlantans** supports metro Atlanta's talent retention aspirations by creating transparency around senior level non-profit roles in the area. Very simply, it is a website that gathers senior level non-profit jobs from various job listing sites and posts them, roughly in order of the date they were posted.

The **Talented Atlantans site** itself is at https://atls-got-talent.herokuapp.com/ 

Clicking any particular job posting opens the posting in a new window for the a job-seeker to explore further. 

The **Talented Atlantans scraper** (aka the scraper.py file) and its corresponding Postgres database can also be used independently. Heroku runs the scraper once per day through the Heroku scheduler. However, a user can force the scraper to update the database by running the scraper.py file.