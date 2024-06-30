"""
Main script:
- Collects and transforms all data.
- Creates and populates the database.
- Creates Data Mart.

Authors: Elias Eschenauer, Tamara Weilharter
Version: 2024/06
"""
# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
from transform_airbnb_data import process_airbnb_data
from create_main_database import create_and_populate_database
from modules.booking_hotel_information_scraper import get_all_hotel_information
from modules.clean_data import transform_booking_data
from modules.database import ManageDatabase
from colorama import Fore, Style
import os

# if True: creates a small batch of all data for testing the script locally
TEST_MODE = True

# --------------------------------------------------------------------
# Program code
# --------------------------------------------------------------------

###############
# AIRBNB DATA #
###############

print(Fore.GREEN + 'Collecting and transforming Airbnb data.\n')

# define location (works only for Austria right now)
city = 'Vienna'
country = 'Austria'

# transform airbnb data. test_mode=True only loads 20 airbnb listings / False loads all listings
process_airbnb_data(city, country, test_mode=TEST_MODE)


#################
# MAIN DATABASE #
#################

# populating database
create_and_populate_database()


################
# BOOKING DATA #
################

# USUALLY LOCATED IN GOOGLE CLOUD
# DUE TO SECURITY RESTRICTIONS BOOKING.COM CHANGE THEIR HTML CLASSES REGULARLY
# IF AN ERROR OCCURS -> CHANGING CLASSES MIGHT HELP

print('\nCollecting and transforming Booking.com data.')

# scrapes data from booking and saves it in a DataFrame
script_dir = os.path.dirname(__file__)
csv_path = os.path.join(script_dir, 'data', 'hotels_links.csv')
data, csv_filename = get_all_hotel_information(csv_path, test_mode=TEST_MODE)

# defines final columns for database
columns = ['neighbourhood_id', 'room_type_id', 'name', 'rating_score', 'rating_count', 'kitchen', 'tv', 'wifi', 'gym',
           'elevator', 'fridge', 'heating', 'hair_dryer', 'air_conditioning',
           'hot_tub', 'oven', 'bbq', 'coffee', 'pool',
           'balcony', 'furniture', 'microwave', 'room_name', 'timestamp', 'price']

# transforms data and returns a DataFrame
data_clean = transform_booking_data(data, columns, csv_filename)

# adds missing column
data_clean['platform'] = 'booking'

print('\nPopulating database with Booking.com data.')

# establishes connection to database
database = ManageDatabase('accommodation_db', 'accommodations')

# populates booking and listings table
database.add_booking_data(data_clean)


#############
# DATA MART #
#############

# SQL query
query = """
SELECT 
    platform, neighbourhood_id, room_type_id, kitchen, tv, wifi, gym, elevator, fridge, heating,
    hair_dryer, air_conditioning, hot_tub, oven, bbq, coffee, pool, balcony, furniture, microwave, 
    beds, accommodates, bathrooms, bedrooms, price
FROM 
    accommodations.listings
JOIN 
    accommodations.airbnb ON listings.listing_id = airbnb.listing_id

UNION

SELECT 
    l.platform, l.neighbourhood_id, l.room_type_id, l.kitchen, l.tv, l.wifi, l.gym, l.elevator, l.fridge, l.heating, l.hair_dryer,
    l.air_conditioning, l.hot_tub, l.oven, l.bbq, l.coffee, l.pool, l.balcony, l.furniture, l.microwave, 
    NULL AS beds, NULL AS accommodates, NULL AS bathrooms, NULL AS bedrooms, b.booking_avg_price AS price
FROM 
    accommodations.listings AS l
JOIN 
    (SELECT listing_id, AVG(price) AS booking_avg_price FROM accommodations.booking GROUP BY listing_id) AS b ON l.listing_id = b.listing_id;
"""

# establishes connection and creates data mart
database = ManageDatabase('accommodation_db', 'machine_learning')
database.create_data_mart(query, 'data')

print('\nData Mart created.' + Style.RESET_ALL)
