"""
Data Mart:
Creates Data Mart with data for Machine Learning Model.

Author: Tamara Weilharter
Version: 2024/06
"""
# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
from modules.database import ManageDatabase


# --------------------------------------------------------------------
# Program code
# --------------------------------------------------------------------

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

database = ManageDatabase(database_name='accommodation_db', schema_name='machine_learning')
database.create_data_mart(query, 'data')
