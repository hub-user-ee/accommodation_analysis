"""
Booking.com Hotel Link Scraper

This module contains a function to scrape hotel links from Booking.com search results for a specified
location and date range. It uses Selenium to interact with the webpage and BeautifulSoup to parse the
HTML content. The scraped links are either saved to a CSV file (on Windows) or returned as a list (on
other operating systems).

Functions:
    load_site_save_links(location_id, location_type, check_in, check_out): Loads Booking.com search results,
    extracts hotel links, and saves them to a CSV file or returns them as a list.

Dependencies:
    - general_function (for get_driver)
    - selenium (for web scraping)
    - BeautifulSoup (for HTML parsing)
    - csv (for saving data)
    - sys (for checking the operating system)
    - time (for managing delays)

Usage:
    This module can be run as a script to scrape hotel links for a specified location and date range.
    Example:
        load_site_save_links(location_id="1995499", location_type="city", check_in="2024-06-27", check_out="2024-06-28")

Author: Elias Eschenauer
Version: 2024/06
"""
# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
import os
import csv
import sys
import time
from tqdm import tqdm
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from modules.general_function import get_driver


# --------------------------------------------------------------------
# Functions definition
# --------------------------------------------------------------------
def scrape_links_for_stars(location_id, location_type, check_in, check_out, rating):
    """
    Scrape hotel links for a specified location, date range, and star rating.

    Args:
        location_id (str): The destination id to search for hotels.
        location_type (str): The type to search for hotels.
        check_in (str): The check-in date in the format YYYY-MM-DD.
        check_out (str): The check-out date in the format YYYY-MM-DD.
        rating (int): The rating to filter hotels.

    Returns:
        list: A list of hotel links for the specified star rating.
    """
    url = (f"https://www.booking.com/searchresults.en-gb.html?label=gen173nr-1BCAEoggI46AdIM1gEaA6IAQGYAQm4ARfIAQz"
           f"YAQHoAQGIAgGoAgO4AuC8qrMGwAIB0gIkYzQ0MzUxMzctYWYwZC00YTQyLWE4MWEtODEyNWMxOGY1OThl2AIF4AIB&sid=3d0e2ed4"
           f"47f14f8ab6d93efc253892a7&aid=304142&ss=Vienna&ssne=Vienna&ssne_untouched=Vienna&lang=en-gb"
           f"&src=index&dest_id=-{location_id}&dest_type={location_type}&checkin={check_in}&checkout={check_out}&"
           f"group_adults=2&no_rooms=1&group_children=0&nflt=class%3D{rating}")

    try:
        # Open the URL
        driver = get_driver()
        driver.get(url)

        # Wait for the results to load
        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div[data-testid='property-card']"))
        )

        # Function to scroll down and load more results
        def load_all_results():
            # Get total iterations with number of properties found
            page_source_1 = driver.page_source
            iteration_soup = BeautifulSoup(page_source_1, "html.parser")
            properties_found = iteration_soup.find('h1', {'aria-live': 'assertive'}).text.split()[1]
            properties_found = (int(properties_found) - 50) / 25
            total_iterations = int(properties_found)

            progress_bar = tqdm(total=total_iterations, desc=f"Loading hotels rated {rating}")

            while True:
                try:
                    # Scroll down to the bottom
                    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)  # Adjust this delay as needed

                    # Find and click the "Load more results" button
                    load_more_button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.XPATH, "//button[span[text()='Load more results']]"))
                    )
                    load_more_button.click()  # click button
                    progress_bar.update(1)
                    time.sleep(1)  # Wait for new results to load
                except Exception:
                    progress_bar.close()
                    break

        # Load all results by clicking the button until it's no longer available
        load_all_results()

        # Get the page source after scrolling and loading all results
        page_source_2 = driver.page_source

    except Exception as e:
        driver.quit()
        return []

    finally:
        # Close the WebDriver
        driver.quit()

    # Parse the page source with BeautifulSoup
    soup = BeautifulSoup(page_source_2, 'html.parser')

    # Find all the hotel elements in the HTML document
    hotels = soup.find_all('div', {'data-testid': 'property-card'})

    hotels_links = []
    # Loop over the hotel elements and extract the desired data
    for hotel in hotels:
        # Extract the link from the <a> tag
        link_element = hotel.find('a', href=True)
        if link_element:
            link = link_element['href']
            hotels_links.append(link)

    return hotels_links


def load_site_save_links(location_id, location_type, check_in, check_out):
    """
    Load the booking.com search results for a specified location and date range, extract hotel links,
    and save them to a CSV file on Windows or return them as a list on other operating systems.

    Args:
        location_id (str): The id of the location to search for hotels.
        location_type (str): The type of the location to search for hotels.
        check_in (str): The check-in date in the format YYYY-MM-DD.
        check_out (str): The check-out date in the format YYYY-MM-DD.

    Returns:
        list: A list of hotel links if the operating system is not Windows.
    """

    ratings_list = [0, 1, 2, 3, 4, 5]
    all_hotels_links = []

    for rating in ratings_list:
        links = scrape_links_for_stars(location_id, location_type, check_in, check_out, rating)
        all_hotels_links.extend(links)

    print(f"Found {len(all_hotels_links)} links")

    # Save the links to a CSV file on Windows, return the list otherwise
    if sys.platform.startswith('win') or os.getenv('DB_HOST'):
        directory = 'data'
        if not os.path.exists(directory):
            os.makedirs(directory)
        csv_file = os.path.join(directory, 'hotels_links.csv')
        try:
            with open(csv_file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(['Links'])
                for link in all_hotels_links:
                    writer.writerow([link])
        except IOError as e:
            print(f"An error occurred while writing to the file: {e}")
    else:
        return all_hotels_links


if __name__ == "__main__":
    load_site_save_links(location_id="1995499", location_type="city", check_in="2024-06-27", check_out="2024-06-28")
