"""
Booking.com Hotel Information Scraper

This module scrapes hotel information from Booking.com for a specified location and date range.
It uses Selenium to interact with the webpage and BeautifulSoup to parse the HTML content.
The scraped information includes hotel name, room name, rating, rating count, price, property type, amenities,
and district. The information is then saved to a CSV file or returned as a pandas DataFrame.

Functions:
    get_hotel_information(link, driver): Retrieves detailed information about a hotel from its booking.com page.
    get_all_hotel_information(test_mode=0): Scrapes information for all hotels in the specified location and date range.

Dependencies:
    - general_function (for get_driver, extract_district, transform_property_type)
    - clean_data (for one_hot_encoder)
    - booking_link_scraper (for load_site_save_links)
    - selenium (for web scraping)
    - BeautifulSoup (for HTML parsing)
    - csv (for saving data)
    - sys (for checking the operating system)
    - pandas (for data manipulation)
    - tqdm (for progress bar)

Authors: Elias Eschenauer, Hanna Scharinger
Version: 2024/06
"""
# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
import os
import datetime
import sys
from bs4 import BeautifulSoup
from tqdm import tqdm
import pandas as pd
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, WebDriverException
from modules.general_function import get_driver, extract_district, transform_property_type
from modules.clean_data import one_hot_encoder
from modules.booking_link_scraper import load_site_save_links

# --------------------------------------------------------------------
# Functions definition
# --------------------------------------------------------------------

# Get current timestamp
TIMESTAMP = datetime.datetime.now()

# Convert timestamp to string for CSV filename
DATE_STR = TIMESTAMP.strftime('%Y-%m-%d-%H-%M-%S')


def get_hotel_information(link, driver):
    """
    Retrieve detailed information about a hotel from its booking.com page.

    Args:
        link (str): URL of the hotel page.
        driver (WebDriver): Selenium WebDriver instance.

    Returns:
        list: A list containing hotel name, room name, rating score, rating count, price, property type,
              amenities, district, and timestamp. Returns None if an error occurs.
    """
    try:
        # Navigate to the hotel page
        driver.get(link)
        WebDriverWait(driver, 0.1).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "h2.aceeb7ecbc.pp-header__title"))
        )
        page_source_hotel = driver.page_source
        hotel_soup = BeautifulSoup(page_source_hotel, 'html.parser')

        # Extract hotel information
        hotel_name = hotel_soup.find('h2', class_='aceeb7ecbc pp-header__title').text.strip()
        hotel_room_name = hotel_soup.find('span', class_='hprt-roomtype-icon-link').text.strip()
        hotel_rating = hotel_soup.find('div', class_='f13857cc8c e008572b71').text.strip()[:3]
        hotel_rating_count = hotel_soup.find('div', class_='b290e5dfa6 a5cc9f664c c4b07b6aa8').text.strip().split()[0].replace(',', '')
        hotel_price = hotel_soup.find('span', class_='prco-valign-middle-helper').text.strip().replace('€\xa0', '').replace(',', '')
        property_type = hotel_soup.find('span', class_='bui-badge bui-badge--outline room_highlight_badge--without_borders').text.strip()
        district = extract_district(hotel_soup.find('span', class_='hp_address_subtitle').text)

        if district.startswith('0'):
            district = district[1:]

        # Extract amenities
        facilities_block = hotel_soup.find('div', class_='hprt-facilities-block')
        amenities_elements_1 = []
        if facilities_block:
            badges = facilities_block.find_all('span', class_='bui-badge bui-badge--outline room_highlight_badge--without_borders')
            for badge in badges:
                amenities_elements_1.append(badge.text.strip())

        amenities_elements_2_main = hotel_soup.find('ul', class_='hprt-facilities-others')
        amenities_elements_2 = []
        if amenities_elements_2_main:
            facilities = amenities_elements_2_main.find_all('span', class_='hprt-facilities-facility')
            for facility in facilities:
                amenities_elements_2.append(facility.text.strip())

        # Combine amenities lists
        text_contents = amenities_elements_1 + amenities_elements_2

        return [
            hotel_name,
            hotel_room_name,
            hotel_rating,
            int(hotel_rating_count),
            float(hotel_price),
            property_type,
            text_contents,
            district,
            TIMESTAMP
        ]

    except TimeoutException:
        # Handle timeout exception
        return None
    except AttributeError:
        # Handle attribute error
        return None
    except Exception as e:
        # Handle any unexpected errors
        print(f"An unexpected error occurred while retrieving hotel information: {e}")
        return None


def get_all_hotel_information(csv_path, test_mode=False):
    """
    Scrape information for all hotels in the specified location and date range.

    Args:
        test_mode (int): If test_mode=True only loads 20 booking listings.
        csv_path (str): The path of the "hotels_links.csv".
    Returns:
        pd.DataFrame: DataFrame containing hotel information. Returns None if an error occurs.
    """
    try:
        # Load hotel links from CSV or scrape from website
        if not os.path.isfile(csv_path):
            load_site_save_links("1995499", "city", "2024-06-27", "2024-06-28")
        links_df = pd.read_csv(csv_path)
    except IOError as e:
        # Handle IO error
        print(f"Error reading or loading links: {e}")
        return

    hotel_info_list = []
    links_not_found = []

    try:
        # Initialize the WebDriver
        driver = get_driver()
    except WebDriverException as e:
        # Handle WebDriver error
        print(f"Error initializing the WebDriver: {e}")
        return

    if test_mode:
        test_size = 20
    else:
        test_size = len(links_df)

    # Loop through hotel links and scrape information
    for link in tqdm(links_df['Links'][:test_size], desc="Scraping hotel information"):
        hotel_info = get_hotel_information(link, driver)

        if hotel_info is None:  # If failed, try again
            hotel_info = get_hotel_information(link, driver)

        if hotel_info:
            hotel_info_list.append(hotel_info)
        else:
            links_not_found.append(link)

    df_columns = ["name", "room_name", "rating_score", "rating_count",
                  "price", "property_type", "amenities", "neighbourhood_id", "timestamp"]

    booking_df = pd.DataFrame(hotel_info_list, columns=df_columns)

    try:
        # Apply one-hot encoding to amenities
        one_hot_encoder('kitchen', booking_df, 'amenities', 'kitchen')
        one_hot_encoder('tv', booking_df, 'amenities', 'television')
        one_hot_encoder('wifi', booking_df, 'amenities', 'wifi')
        one_hot_encoder('gym', booking_df, 'amenities', 'gym')
        one_hot_encoder('elevator', booking_df, 'amenities', 'lift')
        one_hot_encoder('fridge', booking_df, 'amenities', 'refrigerator')
        one_hot_encoder('heating', booking_df, 'amenities', 'heating')
        one_hot_encoder('hair_dryer', booking_df, 'amenities', 'hairdryer')
        one_hot_encoder('air_conditioning', booking_df, 'amenities', 'air conditioning')
        one_hot_encoder('hot_tub', booking_df, 'amenities', 'hot tub')
        one_hot_encoder('oven', booking_df, 'amenities', 'oven')
        one_hot_encoder('bbq', booking_df, 'amenities', 'barbecue')
        one_hot_encoder('coffee', booking_df, 'amenities', 'coffee maker')
        one_hot_encoder('pool', booking_df, 'amenities', 'pool')
        one_hot_encoder('balcony', booking_df, 'amenities', 'patio')
        one_hot_encoder('furniture', booking_df, 'amenities', 'outdoor furniture')
        one_hot_encoder('microwave', booking_df, 'amenities', 'microwave')

        # Transform property type to room type ID
        booking_df["room_type_id"] = booking_df.apply(lambda row: transform_property_type(row['property_type'],
                                                                                          row['name'],
                                                                                          row['room_name']), axis=1)

        csv_filename = f'{DATE_STR}.csv'

        return booking_df, csv_filename

    except Exception as e:
        # Handle data processing or CSV writing error
        print(f"An error occurred during data processing or CSV writing: {e}")

    finally:
        # Quit the WebDriver
        try:
            driver.quit()
        except Exception:
            print("An error occurred while quitting the WebDriver")


if __name__ == "__main__":
    # Run the scraping function with test mode set to True
    try:
        booking_df, csv_filename = get_all_hotel_information('hotels_links.csv', True)
        if booking_df is not None:
            csv_filename = f'{DATE_STR}.csv'
            booking_df.to_csv(csv_filename, index=False)
            print(f"Data saved to {csv_filename}")
    except Exception as e:
        print(f"An error occurred: {e}")

