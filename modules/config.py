"""
Database configuration:
This module defines a function that extracts parameters from the database.ini file and
creates a dictionary based on these parameters for connecting to a PostgreSQL database.

Author: Tamara Weilharter
Version: 2024/06
"""

# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
import os
from configparser import ConfigParser


# --------------------------------------------------------------------
# Function definition
# --------------------------------------------------------------------
def config(filename='database.ini', section='postgresql'):
    """
    Extracts database connection parameters from a specified .ini file.

    :param filename: The name of the .ini file containing the database configuration. Defaults to 'database.ini'.
    :param section: The section within the .ini file containing the database parameters. Defaults to 'postgresql'.
    :return: A dictionary containing the database connection parameters.
    """
    # constructs the full file path relative to the current working directory
    current_dir = os.path.dirname(__file__)
    filepath = os.path.join(current_dir, filename)

    # creates a parser
    parser = ConfigParser()
    # reads config file
    parser.read(filepath)

    # gets section and updates dictionary with connection string key:value pairs
    db_infos = {}
    if section in parser:
        for key in parser[section]:
            db_infos[key] = parser[section][key]
    else:
        raise FileNotFoundError(
            f'Section "{section}" not found in the "{filename}" file')
    return db_infos


# for testing and building this module
if __name__ == '__main__':
    """
    This is executed only when this file is executed directly.
    """
    config_dict = config()
    print(config_dict)
