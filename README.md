# atls-got-talent

This is a web app that shows recent postings for senior level non-profit jobs in Atlanta. It includes:
* a Python scraper in scraper.py that saves data to a Heroku Postgres database 
* a Heroku-hosted Flask front-end web-app in application.py that serves up the data using HTML/Jinja 
* a Python object specification in listing.py to keep server object standard across multiple Python files