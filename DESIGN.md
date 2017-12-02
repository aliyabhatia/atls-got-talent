# Talented Atlantans - Design Documentation

---

## Scraper.py

Scraper.py pulls senior-level jobs from several sites on a daily basis so they can be served up to the Talented Atlantans site. Technical details:
* Runs daily using the Heroku Scheduler plug-in - currently, the scraper first deletes everything in the Heroku Postgres database before replenishing it with the up-to-date job listings
* Uses `Beautiful Soup` plug-in to support web scraping using HTML tags (e.g. "class," "div," and "li" tags) to identify valuable information
* Some sites (Bridgespan, Boardwalk) only include senior level roles, in which case all Atlanta-area roles are scraped - other sites (Work For Good) have a range of roles, so a set of key words are used to narrow down which Atlanta-area roles are scraped
* Some sites (Bridgespan, Work For Good) include the date posted which the Scraper will pull - other sites (Boardwalk) do not, and are assigned a random date in the last 30 days using the `rand_date()` function to help vary where the user sees these posts in the list

