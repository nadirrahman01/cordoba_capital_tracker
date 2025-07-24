import json
import os
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

URLS = {
    "Summer Internships": "https://app.the-trackr.com/uk-finance/summer-internships",
    "Spring Weeks": "https://app.the-trackr.com/uk-finance/spring-weeks",
    "Off‑Cycle Internships": "https://app.the-trackr.com/uk-finance/off-cycle-internships",
    "Industrial Placements": "https://app.the-trackr.com/uk-finance/industrial-placements",
    "Graduate Programmes": "https://app.the-trackr.com/uk-finance/graduate-programmes",
    "Pre‑University": "https://app.the-trackr.com/uk-finance/pre-university",
    "Events": "https://app.the-trackr.com/uk-finance/events"
}


def clean_category(cat):
    return cat.replace('\u2011', '-').strip()


def fetch_html(url):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, timeout=60000)
        page.wait_for_selector("table tbody tr", timeout=60000)
        html = page.content()
        browser.close()
        return html


def parse_table(html, category, url):
    soup = BeautifulSoup(html, 'html.parser')

    headers = [
        cell.get_text(strip=True).replace("\xa0", " ")
        for cell in soup.select("table thead tr th")
    ]

    rows = soup.select("table tbody tr")
    cleaned_category = clean_category(category)

    for row in rows:
        cells = row.find_all("td")
        if len(cells) != len(headers):
            continue

        row_data = dict(zip(headers, [cell.get_text(strip=True) for cell in cells]))

        job = {
            "title": row_data.get("Programme Name", ""),
            "company": row_data.get("Company Name", ""),
            "opening_date": row_data.get("Opening Date", ""),
            "closing_date": row_data.get("Closing Date", ""),
            "last_stage": row_data.get("Latest Stage", "-"),
            "status": "Upcoming" if not row_data.get("Opening Date") else "Open",
            "url": cells[-1].find("a")["href"] if cells[-1].find("a") else url,
            "category": cleaned_category
        }

        if not job["title"] and not job["company"]:
            continue

        yield job


def scrape_all():
    all_jobs = []
    for category, url in URLS.items():
        print(f"Scraping: {category}...")
        try:
            html = fetch_html(url)
            jobs = parse_table(html, category, url)
            all_jobs.extend(jobs)
        except Exception as e:
            print(f"Error scraping {category}: {e}")

    output_path = os.path.join(os.path.dirname(__file__), "data", "jobs.json")
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w") as f:
        json.dump(all_jobs, f, indent=2)

    print(f"[✓] Scraped {len(all_jobs)} jobs — saved to jobs.json")


if __name__ == "__main__":
    scrape_all()
