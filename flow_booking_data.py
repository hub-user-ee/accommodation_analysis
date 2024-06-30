"""
Workflow for booking data:
This script extracts, transforms and loads the bookings data into the main database.

Author: Tamara Weilharter
Version: 2024/06
"""

# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
from modules.booking_hotel_information_scraper import get_all_hotel_information
from modules.database import ManageDatabase
from modules.clean_data import transform_booking_data


# --------------------------------------------------------------------
# Program code
# --------------------------------------------------------------------

###########
# EXTRACT #
###########

# scrapes data from booking and saves it in a DataFrame
data, csv_filename = get_all_hotel_information(0)


#############
# TRANSFORM #
#############

# defines final columns for database
columns = ['neighbourhood_id', 'room_type_id', 'name', 'rating_score', 'rating_count', 'kitchen', 'tv', 'wifi', 'gym',
           'elevator', 'fridge', 'heating', 'hair_dryer', 'air_conditioning',
           'hot_tub', 'oven', 'bbq', 'coffee', 'pool',
           'balcony', 'furniture', 'microwave', 'room_name', 'timestamp', 'price']

# transforms data and returns a DataFrame
data_clean = transform_booking_data(data, columns, csv_filename)


########
# LOAD #
########

# adds missing column
data_clean['platform'] = 'booking'

# establishes connection
database = ManageDatabase('accommodation_db', 'accommodations')
# populates booking table
database.add_booking_data(data_clean)
