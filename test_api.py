from scraper.yc_scraper import scrape_all_companies

companies = scrape_all_companies()
print("Total companies fetched:", len(companies))