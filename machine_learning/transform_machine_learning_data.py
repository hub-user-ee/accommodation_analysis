"""
Transforms .csv file of Machine Learning data and calculates some additional features
for Booking.com data.

Author: Elias Eschenauer
Version: 2024/06
"""

# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
import os
import pandas as pd
from modules.clean_data import transform_machine_learning_data


# --------------------------------------------------------------------
# Program code
# --------------------------------------------------------------------

# Read data
data = pd.read_csv('machine_learning_data.csv')
airbnb = data[data['platform'] == 'airbnb']
booking = data[data['platform'] == 'booking']
booking = booking.drop(['beds', 'accommodates', 'bathrooms', 'bedrooms'], axis=1)

################
# ADD FEATURES #
################

# Determine min and max prices from airbnb_df
min_price = airbnb['price'].min()
max_price = airbnb['price'].max()

# Define number of bins
n = 20

# Calculate bin width
bin_width = (max_price - min_price) / n

# Create price bins
price_bins = [(min_price + i * n, min_price + (i + 1) * n) for i in range(int((max_price - min_price) / n))]

# Calculate means for each price bin from airbnb_df
mean_beds_per_price_bin = []
for lower_bound, upper_bound in price_bins:
    filtered_data = airbnb[(airbnb['price'] >= lower_bound) & (airbnb['price'] < upper_bound)]
    mean_beds = round(filtered_data['beds'].mean(), 1)
    mean_beds_per_price_bin.append((lower_bound, upper_bound, mean_beds))

mean_accommodates_per_price_bin = []
for lower_bound, upper_bound in price_bins:
    filtered_data = airbnb[(airbnb['price'] >= lower_bound) & (airbnb['price'] < upper_bound)]
    mean_accommodates = round(filtered_data['accommodates'].mean(), 1)
    mean_accommodates_per_price_bin.append((lower_bound, upper_bound, mean_accommodates))

mean_bathrooms_per_price_bin = []
for lower_bound, upper_bound in price_bins:
    filtered_data = airbnb[(airbnb['price'] >= lower_bound) & (airbnb['price'] < upper_bound)]
    mean_bathrooms = round(filtered_data['bathrooms'].mean(), 1)
    mean_bathrooms_per_price_bin.append((lower_bound, upper_bound, mean_bathrooms))

mean_bedrooms_per_price_bin = []
for lower_bound, upper_bound in price_bins:
    filtered_data = airbnb[(airbnb['price'] >= lower_bound) & (airbnb['price'] < upper_bound)]
    mean_bedrooms = round(filtered_data['bedrooms'].mean(), 1)
    mean_bedrooms_per_price_bin.append((lower_bound, upper_bound, mean_bedrooms))


# Function to assign mean beds based on price range
def assign_means(row, means_per):
    price = row['price']
    for lower_bound, upper_bound, means in means_per:
        if lower_bound <= price < upper_bound:
            return means
    return None


# Add new column to listings_df with mean beds by price range
booking['beds'] = booking.apply(lambda row: assign_means(row, mean_beds_per_price_bin), axis=1)
booking['accommodates'] = booking.apply(lambda row: assign_means(row, mean_accommodates_per_price_bin), axis=1)
booking['bathrooms'] = booking.apply(lambda row: assign_means(row, mean_bathrooms_per_price_bin), axis=1)
booking['bedrooms'] = booking.apply(lambda row: assign_means(row, mean_bedrooms_per_price_bin), axis=1)

# Merge both dataframes
merged_df = pd.concat([airbnb, booking], ignore_index=True)
merged_df = merged_df.dropna(subset=['price', 'beds', 'accommodates', 'bathrooms', 'bedrooms'])

##################
# TRANSFORMATION #
##################

# transforms data
data_clean = transform_machine_learning_data(merged_df)

# Save the updated listings_df to a new CSV file
path = os.path.join(os.getcwd(), 'machine_learning_data_clean.csv')
data_clean.to_csv(path, index=False)
