"""
Scrapes prices of specific Airbnb listings from the official website.

Author: Elias Eschenauer
Version: 2024/06
"""

# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
import os
import re
import time
import numpy as np
import pandas as pd
from tqdm import tqdm
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from modules.general_function import get_driver
from modules.clean_data import remove_dollar_and_convert_to_float


# --------------------------------------------------------------------
# Functions definition
# --------------------------------------------------------------------
def extract_price_and_min_days(driver, airbnb_id, check_in, check_out, min_days=None):
    """
    Extracts the price and minimum stay duration from an Airbnb listing.

    Args:
        driver (webdriver): The Selenium WebDriver instance.
        airbnb_id (str): The ID of the Airbnb listing.
        check_in (str): The check-in date in 'YYYY-MM-DD' format.
        check_out (str): The check-out date in 'YYYY-MM-DD' format.
        min_days (int, optional): The minimum number of days required for the stay.

    Returns:
        tuple: A tuple containing the price (int) and the minimum number of days (int).
    """
    url = (f"https://www.airbnb.at/rooms/{airbnb_id}?category_tag=Tag%3A8678&enable_m3_private_room=true&photo_id="
           f"1025527847&search_mode=regular_search&check_in={check_in}&check_out={check_out}&source_impression_id="
           f"p3_1718620889_P3JJZnIeCQ6srj0v&previous_page_section_name=1000&federated_search_id="
           f"caf7a402-500a-4157-9a15-32f4a76d48e1")
    driver.get(url)
    time.sleep(1)  # Wait for the page to load
    page_source = driver.page_source
    soup = BeautifulSoup(page_source, "lxml")

    try:
        timeslot = soup.find('div', class_='_wgmchy').text
    except Exception as e:
        print(e)
        return 0, None

    try:
        # Extract price
        price_element = soup.find('span', class_='_1y74zjx')
        price = None
        if price_element:
            raw_price = price_element.text
            price = re.sub(r'\D', '', raw_price)  # Remove non-numeric characters
            price = int(price)  # Convert to integer

        # Extract minimum stay error
        error_element = soup.find('div', id='bookItTripDetailsError')
        if error_element:
            error_text = error_element.text
            if 'Minimale Dauer eines Aufenthalts beträgt' in error_text:
                min_days_str = ''.join(filter(str.isdigit, error_text))
                min_days = int(min_days_str)

        # Adjust price for long stays
        if price is not None and min_days is not None:
            if min_days >= 28:
                price = price / 30

        return price, min_days

    except Exception as e:
        print(e)
        return np.nan, None


def get_price_and_status(max_price):
    """
    Fetches the current prices and minimum stay durations for Airbnb listings exceeding a specified price.

    Args:
        max_price (float): The maximum price threshold for filtering listings.

    Returns:
        None
    """
    # Load listings data
    df = pd.read_csv(os.path.join(os.path.dirname(__file__), '../data/full_listings.csv'))
    df['price'] = df['price'].apply(remove_dollar_and_convert_to_float)
    df_filtered = df[df['price'] > max_price]
    airbnb_ids = df_filtered['id'].tolist()

    # Store the old prices in a dictionary
    old_prices = dict(zip(df['id'], df['price']))

    driver = get_driver()
    prices = []

    # Define the dates to check
    dates = [
        ("2024-06-26", "2024-06-28"),
        ("2024-09-20", "2024-09-22"),
        ("2025-01-01", "2025-01-03"),
        ("2025-03-20", "2025-03-22"),
        ("2025-06-26", "2025-06-28")
    ]

    for airbnb_id in tqdm(airbnb_ids, desc="Gathering: "):
        price = None
        min_days = None

        # Try each date pair
        for check_in, check_out in dates:
            price, min_days = extract_price_and_min_days(driver, airbnb_id, check_in, check_out)
            if price is not None or min_days is not None:
                break
            time.sleep(1)  # Wait before trying the next date pair

        # Adjust check-out date if necessary
        if price is None and min_days is not None:
            for check_in, _ in dates:
                check_out_date = datetime.strptime(check_in, "%Y-%m-%d") + timedelta(days=min_days)
                check_out = check_out_date.strftime("%Y-%m-%d")
                price, _ = extract_price_and_min_days(driver, airbnb_id, check_in, check_out, min_days)
                if price is not None:
                    break

        price_old = old_prices.get(airbnb_id, None)
        prices.append({'id': airbnb_id, 'price_old': price_old, 'price': price, 'min_days': min_days})

    driver.quit()

    # Save the results to a CSV file
    price_df = pd.DataFrame(prices)
    price_df.to_csv("airbnb_prices.csv", index=False)


if __name__ == "__main__":
    get_price_and_status(400)
