"""
Data Transformation:
This module defines functions for transforming data in a Pandas DataFrame.

Authors: Elias Eschenauer, Tamara Weilharter
Version: 2024/06
"""

# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
import io
import os
import sys
import requests
import pandas as pd
import numpy as np
from sklearn.preprocessing import OneHotEncoder


# --------------------------------------------------------------------
# Functions definition
# --------------------------------------------------------------------

# Dollar to Euro exchange rate from 2024-03-22
exchange_rate = 0.9210

# District mapping dictionary
district_mapping = {
    'Innere Stadt': 1,
    'Leopoldstadt': 2,
    'Landstraße': 3,
    'Wieden': 4,
    'Margareten': 5,
    'Mariahilf': 6,
    'Neubau': 7,
    'Josefstadt': 8,
    'Alsergrund': 9,
    'Favoriten': 10,
    'Simmering': 11,
    'Meidling': 12,
    'Hietzing': 13,
    'Penzing': 14,
    'Rudolfsheim-Fünfhaus': 15,
    'Ottakring': 16,
    'Hernals': 17,
    'Währing': 18,
    'Döbling': 19,
    'Brigittenau': 20,
    'Floridsdorf': 21,
    'Donaustadt': 22,
    'Liesing': 23
}

# Property type mapping dictionary
property_type_mapping = {
    'Entire rental unit': 1,
    'Private room in rental unit': 2,
    'Entire condo': 3,
    'Entire serviced apartment': 4,
    'Entire loft': 5,
    'Private room in home': 6,
    'Private room in condo': 7,
    'Entire home': 8,
    'Entire place': 9,
    'Private room in treehouse': 10,
    'Entire villa': 11,
    'Entire guest suite': 12,
    'Shared room in rental unit': 13,
    'Private room in townhouse': 14,
    'Shared room in home': 15,
    'Entire vacation home': 16,
    'Entire townhouse': 17,
    'Private room in loft': 18,
    'Private room in cottage': 19,
    'Private room': 20,
    'Private room in cave': 21,
    'Shared room in hotel': 22,
    'Room in hotel': 23,
    'Private room in villa': 24,
    'Room in boutique hotel': 25,
    'Private room in guesthouse': 26,
    'Room in aparthotel': 27,
    'Room in serviced apartment': 28,
    'Entire chalet': 29,
    'Private room in serviced apartment': 30,
    'Entire bungalow': 31,
    'Private room in pension': 32,
    'Lighthouse': 33,
    'Private room in nature lodge': 34,
    'Private room in bed and breakfast': 35,
    'Shared room in condo': 36,
    'Private room in guest suite': 37,
    'Shared room in hostel': 38,
    'Tiny home': 39,
    'Entire guesthouse': 40,
    'Entire cottage': 41,
    'Shared room in loft': 42,
    'Private room in camper/rv': 43,
    'Entire cabin': 44,
    'Casa particular': 45,
    'Private room in hostel': 46,
    'Shared room in bed and breakfast': 47,
    'Shared room in serviced apartment': 48,
    'Private room in castle': 49,
    'Private room in casa particular': 50,
    'Tower': 51,
    'Private room in barn': 52,
    'Dome': 53,
    'Barn': 54,
    'Castle': 55,
    'Entire hostel': 56,
    'Shared room in tiny home': 57,
    'Shared room in casa particular': 58,
    'Camper/RV': 59
}

# Room type mapping dictionary
room_type_mapping = {
    'Entire home/apt': 1,
    'Private room': 2,
    'Shared room': 3,
    'Hotel room': 4
}

# Host response time mapping dictionary
host_response_time_mapping = {
    'within an hour': 1,
    'within a few hours': 2,
    'within a day': 3,
    'a few days or more': 4
}

# Platform mapping dictionary
platform_mapping = {
    'airbnb': 0,
    'booking': 1
}


def read_url(link):
    """
    Reads a CSV file from a URL and returns it as a Pandas DataFrame.

    Args:
        link (str): The URL of the CSV file.

    Returns:
        pd.DataFrame: The DataFrame containing the CSV data.
    """
    response = requests.get(link)
    content = response.content
    data = pd.read_csv(io.BytesIO(content), sep=',', header=0, compression='gzip', low_memory=False)
    return data


def merge_csv_files(urls, column):
    """
    Merges multiple CSV files from URLs into a single DataFrame, keeping only the specified columns.

    Args:
        urls (list of str): List of URLs pointing to the CSV files.
        column (str): The column to check for duplicates.

    Returns:
        pd.DataFrame: The merged DataFrame.
    """
    dataframes = []
    for i, url in enumerate(urls):
        df = read_url(url)
        if i == 0:
            cols_to_keep = df.columns  # Save the columns of the first dataframe
        else:
            df = df[cols_to_keep]  # Keep only the columns of the first dataframe
        dataframes.append(df)

    merged_df = pd.concat(dataframes, ignore_index=True)
    merged_df = merged_df.drop_duplicates(subset=column, keep='first')

    return merged_df


def remove_dollar_and_convert_to_float(price):
    """
    Converts a dollar price string to a float value in Euros.

    Args:
        price (str): The price string (e.g., "$1,000.00").

    Returns:
        float: The price in Euros.
    """
    if isinstance(price, str):
        price_in_usd = float(price[1:].replace(',', ''))
        price_in_euro = price_in_usd * exchange_rate
        return round(price_in_euro, 2)
    else:
        return np.nan


def map_district_to_number(district_name):
    """
    Maps a district name to its corresponding number.

    Args:
        district_name (str): The name of the district.

    Returns:
        int: The corresponding district number.
    """
    return district_mapping.get(district_name, None)


def map_property_type_to_number(property_types):
    """
    Maps a property type to its corresponding number.

    Args:
        property_types (str): The property type.

    Returns:
        int: The corresponding property type number.
    """
    return property_type_mapping.get(property_types, None)


def map_room_type_to_number(room_types):
    """
    Maps a room type to its corresponding number.

    Args:
        room_types (str): The room type.

    Returns:
        int: The corresponding room type number.
    """
    return room_type_mapping.get(room_types, None)


def map_response_time_to_number(response_time):
    """
    Maps a host response time to its corresponding number.

    Args:
        response_time (str): The host response time.

    Returns:
        int: The corresponding response time number.
    """
    return host_response_time_mapping.get(response_time, None)


def map_platform_to_number(platform):
    """
    Maps a platform to its corresponding number.

    Args:
        platform (str): The platform name.

    Returns:
        int: The corresponding platform number.
    """
    return platform_mapping.get(platform, None)


def one_hot_encoder(word, data, text, aux):
    """
    Performs one-hot encoding on a specified word within a DataFrame column.

    Args:
        word (str): The word to be encoded.
        data (pd.DataFrame): The DataFrame containing the data.
        text (str): The column name to search for the word.
        aux (str): An auxiliary word to consider for encoding.

    Returns:
        None
    """
    data[word] = data[text].apply(lambda x: 1 if (word in str(x).lower() or aux in str(x).lower()) else 0)


def convert_boolean_values(df, column):
    """
    Converts boolean-like values in a column from 't'/'f' to 'true'/'false'.

    Args:
        df (pd.DataFrame): The DataFrame containing the data.
        column (str): The column name with boolean-like values.

    Returns:
        None
    """
    df[column] = df[column].replace({'t': 'true', 'f': 'false'})


def transform_booking_data(df, col, filename):
    """
    Transforms the booking data by formatting timestamps, removing duplicates, cleaning rating scores,
    selecting specific columns, and saving the cleaned data to a .csv file.

    Args:
        df (pd.DataFrame): The DataFrame with the booking data.
        col (list of str): The columns which should be in the final .csv file.
        filename (str): The name of the .csv file.

    Returns:
        pd.DataFrame: The cleaned DataFrame (if not saved locally).
    """
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df['timestamp'] = df['timestamp'].dt.strftime('%Y-%m-%d %H:%M:%S')

    df_unique = df.drop_duplicates(subset=['name', 'room_name'])

    df_unique.loc[:, 'rating_score'] = df_unique['rating_score'].astype(str).str.replace('S', '')

    df_clean = df_unique[col]

    if os.getenv('DB_HOST'):
        return df_clean

    if sys.platform.startswith('win'):
        directory = os.getcwd() + '\data'
        file_path = os.path.join(directory, 'booking_data.csv')
        df_clean.to_csv(file_path, index=False)
        return df_clean

    if not sys.platform.startswith('win') and not os.getenv('DB_HOST'):
        csv_filename = filename.replace('.csv', '-clean.csv')
        df_clean.to_csv(csv_filename, index=False)
        return df_clean


def transform_machine_learning_data(data):
    """
    Transforms the data for machine learning by mapping platforms to numeric values,
    rounding prices, and dropping rows with missing prices.

    Args:
        data (pd.DataFrame): The DataFrame with the data.

    Returns:
        pd.DataFrame: The transformed DataFrame.
    """
    data['platform'] = data['platform'].apply(map_platform_to_number)
    data['price'] = data['price'].round(2)
    data = data.dropna(subset=['price'])

    return data


def encoding_machine_learning_data(data):
    """
    Encodes the data for machine learning by separating features and labels,
    and performing one-hot encoding on categorical variables.

    Args:
        data (pd.DataFrame): The DataFrame with the data.

    Returns:
        tuple: A tuple containing the processed features and labels.
    """
    features = data.drop('price', axis=1)
    labels = data['price']

    categorical_features = ['platform', 'neighbourhood_id', 'room_type_id']
    binary_features = [col for col in features.columns if col not in categorical_features]

    categorical_transformed = OneHotEncoder().fit_transform(data[categorical_features]).toarray()
    binary_transformed = data[binary_features].values

    features_processed = np.hstack((categorical_transformed, binary_transformed))

    return features_processed, labels
