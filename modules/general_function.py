"""
General Functions for Booking.com Scraper

This module contains general utility functions used by the Booking.com scraper.
It includes functions to set up a Selenium WebDriver, extract district information from an address,
and transform property types to room type IDs.

Functions:
    get_driver(): Sets up and returns a Selenium WebDriver instance.
    extract_district(address): Extracts the district code from a given address string.
    transform_property_type(p_type, name, room_name): Transforms property type information to a room type ID.

Dependencies:
    - selenium (for web scraping)
    - sys (for checking the operating system)
    - re (for regular expressions)
    - webdriver_manager.chrome (for managing ChromeDriver installation on Windows)

Author: Elias Eschenauer
Version: 2024/06
"""
import os
# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
import sys
import re
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options

# --------------------------------------------------------------------
# Functions definition
# --------------------------------------------------------------------
def get_driver():
    """
    Set up and return a Selenium WebDriver instance.

    Returns:
        WebDriver: A Selenium WebDriver instance configured with headless Chrome options.
    """
    # Set up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run headless Chrome
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (X11; CrOS x86_64 8172.45.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.64"
        "Safari/537.36"
    )
    chrome_options.add_argument("accept-language=en-US,en;q=0.5")

    # Check the operating system
    if sys.platform.startswith('win') or os.getenv('DB_HOST'):
        from webdriver_manager.chrome import ChromeDriverManager
        # Set up the WebDriver for Windows
        service = Service(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
    else:
        # Set up the WebDriver for Unix-based systems
        chrome_options.binary_location = "/usr/local/bin/google-chrome"
        driver_path = '/usr/local/bin/chromedriver'
        service = Service(driver_path)
        driver = webdriver.Chrome(service=service, options=chrome_options)

    return driver


def extract_district(address):
    """
    Extract the district code from a given address string.

    Args:
        address (str): The address string to extract the district from.

    Returns:
        str: The extracted district code, or None if no match is found.
    """
    pattern = r'1(\d{2})\d Vienna'
    match = re.search(pattern, address)
    if match:
        return match.group(1)
    else:
        return None


def transform_property_type(p_type, name, room_name):
    """
    Transform property type information to a room type ID.

    Args:
        p_type (str): The property type string.
        name (str): The name of the hotel or property.
        room_name (str): The name of the room.

    Returns:
        int: The corresponding room type ID.
    """
    if p_type == "Room":
        return 4
    elif p_type == "Entire apartment" or p_type == "Entire studio":
        return 1
    elif "m²" in p_type:
        size = int(p_type.split()[0])
        if size > 50:
            return 1
        else:
            return 4
    else:
        if "room" in room_name.lower() or "accommodations" in name.lower():
            return 2
        elif "hostel" in name.lower():
            return 4
        else:
            return 1
