from playwright.sync_api import sync_playwright
import time
import json

def scrape_ekantipur():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)  # headless=False to see browser
        page = browser.new_page()
        page.goto("https://ekantipur.com/entertainment")
        page.wait_for_load_state("networkidle")

        # ---------------------------
        # Scroll until bottom dynamically
        # ---------------------------
        last_height = page.evaluate("document.body.scrollHeight")
        while True:
            page.evaluate("window.scrollBy(0, 5000)")
            time.sleep(2)  # wait for content to load
            new_height = page.evaluate("document.body.scrollHeight")
            if new_height == last_height:  # no more content
                break
            last_height = new_height

        # ---------------------------
        # Scrape entertainment news
        # ---------------------------
        news_items = []
        articles = page.query_selector_all("div.category")
        for art in articles:
            title_el = art.query_selector("h2 a")
            if title_el:
                title = title_el.inner_text().strip()
                link = title_el.get_attribute("href")
                news_items.append({
                    "title": title,
                    "url": link
                })

        # ---------------------------
        # Scrape cartoon of the day
        # ---------------------------
        cartoon_section = page.query_selector(".cartoon-of-the-day")  # adjust selector
        if cartoon_section:
            title_el = cartoon_section.query_selector("h3")  # cartoon title
            img_el = cartoon_section.query_selector("img")    # cartoon image
            author_el = cartoon_section.query_selector(".author")  # cartoon author

            cartoon = {
                "title": title_el.inner_text().strip() if title_el else "",
                "image_url": img_el.get_attribute("src") if img_el else "",
                "author": author_el.inner_text().strip() if author_el else ""
            }
        else:
            cartoon = {}  # empty dict if cartoon not found

        # ---------------------------
        # Save to JSON
        # ---------------------------
        output = {
            "entertainment_news": news_items,
            "cartoon_of_the_day": cartoon
        }

        with open("output.json", "w", encoding="utf-8") as f:
            json.dump(output, f, ensure_ascii=False, indent=2)

        browser.close()
        print("Done! output.json now has both entertainment_news and cartoon_of_the_day.")

# Run the scraper
scrape_ekantipur()