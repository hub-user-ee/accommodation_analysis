"""
Transformation Airbnb data:
This script loads and transforms the airbnb data and saves the final .csv files in a 'data' folder.

Authors: Elias Eschenauer, Tamara Weilharter
Version: 2024/06
"""
# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
from modules.airbnb_dataset_link_scraper import scrape_airbnb_csv_links
from modules.clean_data import *


# --------------------------------------------------------------------
# Function definition
# --------------------------------------------------------------------
def process_airbnb_data(city, country, test_mode=False):
    """
    Processes Airbnb data for a specified city and country and saves the .csv files in a 'data' folder.

    :param city: The name of the city for which to process Airbnb data.
    :param country: The name of the country where the city is located.
    :param test_mode: If test_mode=True only loads 20 airbnb listings
    """
    urls_vienna_listings = scrape_airbnb_csv_links(city, country)

    # creates folder for .csv
    directory = os.path.join(os.getcwd(), 'data')
    if not os.path.exists(directory):
        os.makedirs(directory)

    # merges data and loads it into a .csv file
    merged_data = merge_csv_files(urls_vienna_listings, 'id')
    file_path = os.path.join(directory, 'full_listings.csv')
    merged_data.to_csv(file_path, index=False)

    # define columns for different tables
    listings_col = ['index', 'neighbourhood_id', 'room_type_id', 'name', 'review_scores_rating', 'number_of_reviews', 'kitchen', 'tv', 'wifi', 'gym',
                    'elevator', 'fridge', 'heating', 'hair_dryer', 'air_conditioning',
                    'hot_tub', 'oven', 'bbq', 'coffee', 'pool',
                    'balcony', 'furniture', 'microwave']

    airbnb_col = ['index', 'id', 'host_id', 'property_type_id', 'last_scraped',
                  'description', 'picture_url', 'latitude', 'longitude', 'accommodates', 'bathrooms',
                  'bedrooms', 'beds', 'price',
                  'minimum_nights', 'maximum_nights', 'has_availability',
                  'availability_30', 'availability_60', 'availability_90',
                  'availability_365',
                  'number_of_reviews_ltm', 'number_of_reviews_l30d', 'first_review',
                  'last_review', 'review_scores_accuracy',
                  'review_scores_cleanliness', 'review_scores_checkin',
                  'review_scores_communication', 'review_scores_location',
                  'review_scores_value', 'reviews_per_month', 'instant_bookable']

    hosts_col = ['host_id', 'host_name', 'host_since', 'host_country', 'host_about',
                 'host_response_time_int', 'host_response_rate', 'host_acceptance_rate',
                 'host_is_superhost', 'host_picture_url', 'host_identity_verified']

    # reads the .csv with all data
    data = pd.read_csv(file_path, low_memory=False)

    # perform data cleaning and transformation
    data = clean_and_transform_data(data)

    if test_mode:
        data = data[:20]

    # splits into DataFrames with specified columns
    listings = data[listings_col]
    airbnb = data[airbnb_col]
    hosts = data[hosts_col]

    # removes duplicate values for host_id in hosts
    hosts = hosts.drop_duplicates(subset='host_id', keep='first')

    # create .csv files
    listings.to_csv(os.path.join(directory, 'listings.csv'), index=False)
    airbnb.to_csv(os.path.join(directory, 'airbnb.csv'), index=False)
    hosts.to_csv(os.path.join(directory, 'hosts.csv'), index=False)


def clean_and_transform_data(data):
    """
    Cleans and transforms the Airbnb data.

    :param data: The original data as a DataFrame.
    :return: The cleaned and transformed data as a DataFrame.
    """
    # drops unlisted hosts
    data = data.drop(data[data["host_since"].isnull()].index)

    # dataframe index reset
    data = data.reset_index(drop=True)

    # create index column beginning with 1
    data.index = data.index + 1
    data = data.reset_index()

    # removes dollar symbol
    data['price'] = data['price'].apply(remove_dollar_and_convert_to_float)

    # defines encoding
    data['neighbourhood_cleansed'] = data['neighbourhood_cleansed'].replace({
        'Rudolfsheim-Fnfhaus': 'Rudolfsheim-Fünfhaus',
        'Whring': 'Währing',
        'Dbling': 'Döbling',
        'Landstra§e': 'Landstraße'
    })

    # adds columns with foreign keys
    data['neighbourhood_id'] = data['neighbourhood_cleansed'].apply(map_district_to_number)
    data['property_type_id'] = data['property_type'].apply(map_property_type_to_number)
    data['room_type_id'] = data['room_type'].apply(map_room_type_to_number)

    # adds column with integer for host_response_time
    data['host_response_time_int'] = data['host_response_time'].apply(map_response_time_to_number)

    # adds column with extracted country of host_location (Vienna, Austria)
    data['host_country'] = data['host_location'].str.split(',').str[1].str.strip()

    # transforms percentage values
    data['host_response_rate'] = data['host_response_rate'].str.rstrip('%').astype(float) / 100
    data['host_acceptance_rate'] = data['host_acceptance_rate'].str.rstrip('%').astype(float) / 100

    # transform boolean values
    convert_boolean_values(data, 'host_is_superhost')
    convert_boolean_values(data, 'host_identity_verified')
    convert_boolean_values(data, 'has_availability')
    convert_boolean_values(data, 'instant_bookable')

    # encodes amenities
    one_hot_encoder('kitchen', data, 'amenities', 'kitchen')
    one_hot_encoder('tv', data, 'amenities', 'television')
    one_hot_encoder('wifi', data, 'amenities', 'wifi')
    one_hot_encoder('gym', data, 'amenities', 'gym')
    one_hot_encoder('elevator', data, 'amenities', 'lift')
    one_hot_encoder('fridge', data, 'amenities', 'refrigerator')
    one_hot_encoder('heating', data, 'amenities', 'heating')
    one_hot_encoder('hair_dryer', data, 'amenities', 'hair dryer')
    one_hot_encoder('air_conditioning', data, 'amenities', 'air conditioning')
    one_hot_encoder('hot_tub', data, 'amenities', 'hot tub')
    one_hot_encoder('oven', data, 'amenities', 'oven')
    one_hot_encoder('bbq', data, 'amenities', 'barbecue')
    one_hot_encoder('coffee', data, 'amenities', 'coffee maker')
    one_hot_encoder('pool', data, 'amenities', 'pool')
    one_hot_encoder('balcony', data, 'amenities', 'patio')
    one_hot_encoder('furniture', data, 'amenities', 'outdoor furniture')
    one_hot_encoder('microwave', data, 'amenities', 'microwave')

    amenities_list = []
    amenities = data['amenities']
    for i in range(len(amenities)):
        amenities_list.append(amenities[i])
    amenities_list = (','.join(amenities_list)
                      .replace('],[', ', ')
                      .replace('', 'ü')
                      .replace('', 'ä')
                      .replace('', 'ö')
                      .replace('§', 'ß')
                      )

    amenities_list = amenities_list.split(',')

    # get new_price and id from csv where the price changed
    new_price = pd.read_csv('airbnb_prices.csv', low_memory=False)

    # change the datatype to float
    new_price['new_price'] = new_price['new_price'].astype(float)

    # merge the new price to the 'full' dataset
    df_merged = pd.merge(data, new_price, on='id', how='left')

    # change old to new price
    data.loc[data['id'].isin(new_price['id']), 'price'] = df_merged['new_price']

    # get all the ids from the listings that are offline
    data_off = pd.read_csv('airbnb_prices_off.csv', low_memory=False)

    # safe the ids in a list
    off_ids = data_off['id']

    # remove all the data with the offline ids
    data = data[~data['id'].isin(off_ids)]

    return data


if __name__ == '__main__':
    """
    This is executed only when this file is executed directly.
    """
    process_airbnb_data('Vienna', 'Austria')
