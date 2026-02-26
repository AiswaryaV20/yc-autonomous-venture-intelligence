from playwright.sync_api import sync_playwright
import time

URL = "https://www.ycombinator.com/companies"

def scrape_all_companies():
    companies = []

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(URL, timeout=60000)

        # Scroll multiple times to load more companies
        for _ in range(20):  # increase if needed
            page.mouse.wheel(0, 10000)
            time.sleep(2)

        page.wait_for_selector("a[href^='/companies/']")

        elements = page.query_selector_all("a[href^='/companies/']")

        seen = set()

        for el in elements:
            name = el.inner_text().strip()
            link = el.get_attribute("href")

            if link not in seen:
                seen.add(link)
                companies.append({
                    "name": name,
                    "profile_link": "https://www.ycombinator.com" + link
                })

        browser.close()

    return companies