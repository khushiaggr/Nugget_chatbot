import requests
from bs4 import BeautifulSoup
import json
import time
import random
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# --- IMPORTANT ---
# 1. Check robots.txt for each site before scraping. Example: http://example.com/robots.txt
# 2. Be respectful: Add delays between requests. Identify your scraper with a User-Agent.
# 3. Adapt Selectors: CSS selectors are highly specific to website structure and WILL change.
#    You MUST inspect each target website's HTML to find the correct selectors.
# 4. Error Handling: Add more robust error handling for network issues, missing elements, etc.

HEADERS = {
    'User-Agent': 'ZomatoAssignmentScraper/1.0 (+(YourContactInfo))' # Be transparent
}

# --- Placeholder URLs - Replace with your target restaurant website URLs ---
RESTAURANT_URLS = [
    "https://www.dominos.co.in/menu", # Replace!
    "https://restaurants.kfc.co.in/kfc-nehru-nagar-restaurants-nehru-nagar-roorkee-123460/Home",
    "https://www.pizzahut.co.in/menu/pizzas",
     # Replace!
    # Add 3-8 more URLs
]

def safe_get_text(element, selector, default="N/A"):
    """Safely extracts text using a CSS selector."""
    try:
        found = element.select_one(selector)
        return found.get_text(strip=True) if found else default
    except Exception as e:
        logging.warning(f"Error extracting text with selector '{selector}': {e}")
        return default

def scrape_restaurant_website(url):
    """
    Scrapes a single restaurant website.
    ** This function requires significant adaptation per website. **
    """
    logging.info(f"Attempting to scrape: {url}")
    try:
        # Respectful delay
        time.sleep(random.uniform(2, 5))
        response = requests.get(url, headers=HEADERS, timeout=15)
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        soup = BeautifulSoup(response.content, 'html.parser')

        # --- Adapt These Selectors Based on Target Website HTML ---
        restaurant_name = safe_get_text(soup, "h1.restaurant-title") # Example selector
        location = safe_get_text(soup, "div.address p") # Example selector
        hours = safe_get_text(soup, "div.opening-hours span.hours-text") # Example selector
        contact = safe_get_text(soup, "a.contact-phone") # Example selector

        menu_items = []
        # Example: Find menu sections and items within them
        menu_sections = soup.select("section.menu-category") # Example selector
        for section in menu_sections:
            category_name = safe_get_text(section, "h2.category-name") # Example selector
            items = section.select("div.menu-item") # Example selector
            for item_div in items:
                item_name = safe_get_text(item_div, "h3.item-name") # Example selector
                description = safe_get_text(item_div, "p.item-description") # Example selector
                price = safe_get_text(item_div, "span.item-price") # Example selector

                # Basic Tagging (Needs refinement based on actual text)
                tags = []
                desc_lower = description.lower()
                if "vegetarian" in desc_lower or "veg" in desc_lower:
                    tags.append("vegetarian")
                if "vegan" in desc_lower:
                    tags.append("vegan")
                if "gluten-free" in desc_lower or "gf" in desc_lower:
                     tags.append("gluten-free")
                if "spicy" in desc_lower or "hot" in desc_lower:
                    tags.append("spicy")

                if item_name != "N/A":
                    menu_items.append({
                        "item": item_name,
                        "description": description,
                        "price": price,
                        "category": category_name,
                        "tags": tags
                    })

        # Extract special features (e.g., search for keywords in descriptions or dedicated sections)
        special_features = [] # Example: Find a list like soup.select("ul.features li")
        # Add logic here to find features like "vegetarian options", "spice levels indicated" etc.
        # This often requires searching text content or specific page sections.

        restaurant_data = {
            "name": restaurant_name,
            "location": location,
            "menu": menu_items,
            "special_features": special_features,
            "operating_hours": hours,
            "contact_info": contact,
            "source_url": url # Good practice to keep track of source
        }
        logging.info(f"Successfully scraped basic data for: {restaurant_name}")
        return restaurant_data

    except requests.exceptions.RequestException as e:
        logging.error(f"HTTP Error scraping {url}: {e}")
        return None
    except Exception as e:
        logging.error(f"General Error scraping {url}: {e}")
        return None

def main():
    all_restaurants_data = []
    for url in RESTAURANT_URLS:
        data = scrape_restaurant_website(url)
        if data:
            all_restaurants_data.append(data)

    output_file = 'restaurants.json'
    try:
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_restaurants_data, f, ensure_ascii=False, indent=2)
        logging.info(f"Scraped data saved to {output_file}")
    except IOError as e:
        logging.error(f"Error writing data to {output_file}: {e}")

if __name__ == "__main__":
    main()