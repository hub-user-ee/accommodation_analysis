"""
Main database:
This script loads the transformed airbnb data, creates the main database and populates
the database with the airbnb data.

Author: Tamara Weilharter
Version: 2024/06
"""

# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
import pandas as pd
from modules.clean_data import *
from modules.database import ManageDatabase
from colorama import Fore, Style


# --------------------------------------------------------------------
# Function definition
# --------------------------------------------------------------------
def create_and_populate_database():
    print(Fore.GREEN + 'Populating main database:')
    # Create database
    database = ManageDatabase('accommodation_db', 'accommodations')
    database.create_database()

    # Create and populate NEIGHBOURHOODS table
    neighbourhoods_table = pd.DataFrame(list(district_mapping.items()), columns=['neighbourhood_name', 'neighbourhood_id'])
    database.create_table('neighbourhoods', 'neighbourhood_id INTEGER PRIMARY KEY, neighbourhood_name VARCHAR')
    database.populate_table('neighbourhoods', neighbourhoods_table)

    # Create and populate ROOM TYPES table
    room_types_table = pd.DataFrame(list(room_type_mapping.items()), columns=['room_type_name', 'room_type_id'])
    database.create_table('room_types', 'room_type_id INTEGER PRIMARY KEY, room_type_name VARCHAR')
    database.populate_table('room_types', room_types_table)

    # Create and populate PROPERTY TYPES table
    property_types_table = pd.DataFrame(list(property_type_mapping.items()), columns=['property_type_name', 'property_type_id'])
    database.create_table('property_types', 'property_type_id INTEGER PRIMARY KEY, property_type_name VARCHAR')
    database.populate_table('property_types', property_types_table)

    # Create and populate HOSTS table
    hosts_table = pd.read_csv('data/hosts.csv')
    database.create_table('hosts', 'host_id BIGINT PRIMARY KEY, host_name VARCHAR, host_since DATE NOT NULL, host_country '
                                   'VARCHAR, host_about VARCHAR, host_response_time_int INTEGER, host_response_rate FLOAT, '
                                   'host_acceptance_rate FLOAT, host_is_superhost BOOLEAN, host_picture_url VARCHAR, '
                                   'host_identity_verified BOOLEAN')
    database.populate_table('hosts', hosts_table)

    # Create and populate LISTINGS table
    listings_table = pd.read_csv('data/listings.csv')
    listings_table['platform'] = 'airbnb'
    listings_table.rename(columns={'index': 'listing_id'}, inplace=True)
    listings_table.rename(columns={'review_scores_rating': 'rating_score', 'number_of_reviews': 'rating_count', 'id': 'airbnb_id'}, inplace=True)
    database.create_table('listings', 'listing_id SERIAL PRIMARY KEY, neighbourhood_id INTEGER, room_type_id INTEGER, platform VARCHAR, name VARCHAR, rating_score FLOAT, rating_count INTEGER, kitchen INTEGER, tv INTEGER, wifi INTEGER, gym INTEGER, elevator '
                                       'INTEGER, fridge INTEGER, heating INTEGER, hair_dryer INTEGER, air_conditioning '
                                       'INTEGER, hot_tub INTEGER, oven INTEGER, bbq INTEGER, '
                                       'coffee INTEGER, pool INTEGER, balcony INTEGER, '
                                       'furniture INTEGER, microwave INTEGER, '
                                      'FOREIGN KEY (neighbourhood_id) REFERENCES accommodations.neighbourhoods('
                                      'neighbourhood_id), FOREIGN KEY (room_type_id) REFERENCES '
                                      'accommodations.room_types(room_type_id)')
    database.populate_table('listings', listings_table)

    # Create and populate AIRBNB table
    airbnb_table = pd.read_csv('data/airbnb.csv')
    airbnb_table.rename(columns={'id': 'airbnb_id'}, inplace=True)
    airbnb_table.rename(columns={'index': 'listing_id'}, inplace=True)
    database.create_table('airbnb', 'airbnb_id BIGINT PRIMARY KEY, listing_id INTEGER, host_id BIGINT, property_type_id INTEGER, last_scraped DATE, '
                                    'description VARCHAR, picture_url VARCHAR, latitude FLOAT, longitude FLOAT, '
                                    'accommodates INTEGER, bathrooms FLOAT, bedrooms FLOAT, beds FLOAT, '
                                    'price NUMERIC(10, 2), minimum_nights INTEGER, maximum_nights INTEGER, has_availability '
                                    'BOOLEAN, availability_30 INTEGER, availability_60 INTEGER, availability_90 INTEGER, '
                                    'availability_365 INTEGER, number_of_reviews_ltm INTEGER, number_of_reviews_l30d '
                                    'INTEGER, first_review DATE, last_review DATE, review_scores_accuracy FLOAT, '
                                    'review_scores_cleanliness FLOAT, review_scores_checkin FLOAT, '
                                    'review_scores_communication FLOAT, review_scores_location FLOAT, '
                                    'review_scores_value FLOAT, reviews_per_month INTEGER, instant_bookable BOOLEAN, '
                                    'FOREIGN KEY (listing_id) REFERENCES accommodations.listings(listing_id),'
                                    'FOREIGN KEY (property_type_id) REFERENCES accommodations.property_types(property_type_id), '
                                    'FOREIGN KEY (host_id) REFERENCES accommodations.hosts(host_id)')
    database.populate_table('airbnb', airbnb_table)


    # Create BOOKING table
    database.create_table('booking', 'booking_id SERIAL PRIMARY KEY, listing_id INTEGER, room_name VARCHAR, timestamp TIMESTAMP, price NUMERIC(10, 2), '
                                     'FOREIGN KEY (listing_id) REFERENCES accommodations.listings(listing_id)')


    print('Database created:\nConnect to your PostgreSQL server to see the database.')


if __name__ == '__main__':
    """
    This is executed only when this file is executed directly.
    """
    create_and_populate_database()
