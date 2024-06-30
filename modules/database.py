"""
Database configuration:
This module defines a class for creating and populating a PostgreSQL database.

The "Usage for methods:" DocString defines in which methods the method is used within the class.

Author: Tamara Weilharter
Version: 2024/06
"""

# --------------------------------------------------------------------
# Imports
# --------------------------------------------------------------------
import psycopg2
import os
import pandas as pd
import numpy as np
from modules.config import config
from psycopg2 import sql
from tqdm import tqdm


# --------------------------------------------------------------------
# Class definition
# --------------------------------------------------------------------
class ManageDatabase:
    """
    Provides methods for creating and populating a database in PostgreSQL.
    """

    def __init__(self, database_name, schema_name):
        """
        Initializes the ManageDatabase class with the given database and schema names.

        :param database_name: The name of the database as string.
        :param schema_name: The name of the schema as string.
        """
        self.database_name = database_name
        self.schema_name = schema_name
        self.params = config()

    def connect(self, dbname=None):
        """
        Establishes a connection to the PostgreSQL database.

        :param dbname: The name of the database to connect to as string. If None, connects to the default database.
        :return: A connection object to the database.

        Usage for methods: execute_query, get_column_values_as_list, load_existing_values, add_booking_data
        """
        if dbname is None:
            dbname = self.params['database']
        if os.getenv('DB_HOST'):
            host_var = os.getenv('DB_HOST')
        else:
            host_var = self.params['host']
        return psycopg2.connect(
            database=dbname,
            user=self.params['username'],
            password=self.params['password'],
            host=host_var,
            port=self.params['port']
        )

    def execute_query(self, query, params=None, dbname=None, commit=False):
        """
        Executes a given SQL query on the database.

        :param query: The SQL query to execute as string.
        :param params: The parameters to pass with the query as tuple, optional.
        :param dbname: The name of the database to connect to as string, optional.
        :param commit: Whether to autocommit the transaction as boolean, optional.

        Usage for methods: create_database, create_table, log_error, populate_table
        """
        conn = self.connect(dbname)
        conn.autocommit = commit
        cursor = conn.cursor()
        try:
            cursor.execute(query, params)
            if commit:
                conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error during query execution: {error}")
            if commit:
                conn.rollback()
            raise error
        finally:
            conn.close()

    def create_database(self):
        """
        Creates the database and schema specified in the class attributes.
        """
        try:
            self.execute_query(f'CREATE DATABASE {self.database_name};', commit=True)
            self.execute_query(f'CREATE SCHEMA {self.schema_name};', dbname=self.database_name, commit=True)
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error while creating database or schema: {error}")

    def create_table(self, table_name, column_definition):
        """
        Creates a table within the specified schema in the database.

        :param table_name: The name of the table to create as string.
        :param column_definition: The SQL column definitions as string.
        """
        query = f'CREATE TABLE {self.schema_name}.{table_name}({column_definition});'
        self.execute_query(query, dbname=self.database_name, commit=True)

    def log_error(self, table_name, columns, error_message, values):
        """
        Logs errors during data insertion by creating an error log table and storing the values that caused
        the error along with the error message.

        :param table_name: The name of the table where the error occurred as string.
        :param columns: The columns in the table as list.
        :param error_message: The error message to log as string.
        :param values: The values that caused the error as tuple.

        Usage for methods: populate_table, insert_booking_data
        """
        # defines error_log table
        error_log_table = f'{table_name}_error_log'
        error_columns = ', '.join([f"{col} TEXT" for col in columns]) + ", error_message TEXT"
        # creates table
        self.execute_query(f"""
            DO $$
            BEGIN
                IF NOT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = '{self.schema_name}' 
                    AND table_name = '{error_log_table}'
                ) THEN
                    CREATE TABLE {self.schema_name}.{error_log_table} ({error_columns});
                END IF;
            END
            $$;
        """, dbname=self.database_name, commit=True)
        # defines values which will be inserted
        error_values = values + (str(error_message),)
        placeholders = ', '.join(['%s'] * len(error_values))
        # inserts values into error_log table
        self.execute_query(
            f'INSERT INTO {self.schema_name}.{error_log_table} ({", ".join(columns)}, error_message) VALUES ({placeholders})',
            error_values,
            dbname=self.database_name,
            commit=True
        )

    def populate_table(self, table_name, df):
        """
        Populates a table with data from a Pandas DataFrame.

        :param table_name: The name of the table to populate as string.
        :param df: The DataFrame containing the data to insert.

        Usage for methods: add_booking_data
        """
        # defines column names and placeholders
        columns = list(df.columns)
        column_names = ','.join(columns)
        column_placeholders = ','.join(['%s'] * len(columns))

        # initializes progress bar
        pbar = tqdm(total=len(df), desc=f"Populating {table_name}", ncols=100, unit="row")

        # iterates through the DataFrame
        for _, row in df.iterrows():
            # get values for each row as tuples and replace NaN with None
            values_tuple = tuple(None if pd.isna(x) else x for x in row)
            try:
                # inserts values into table
                self.execute_query(
                    f'INSERT INTO {self.schema_name}.{table_name} ({column_names}) VALUES ({column_placeholders})',
                    values_tuple,
                    dbname=self.database_name,
                    commit=True
                )
            # if an error occurs an error_log table will be created with the values
            except (Exception, psycopg2.DatabaseError) as error:
                self.log_error(table_name, columns, error, values_tuple)

            # update progress bar
            pbar.update(1)

        pbar.close()

    def get_column_values_as_list(self, column, table_name):
        """
        Selects and returns all values from a column in a random order.

        :return: The values as a list.
        """
        query = f"SELECT {column} FROM {self.schema_name}.{table_name}"
        conn = self.connect(dbname=self.database_name)
        cursor = conn.cursor()
        cursor.execute(query)
        listing_ids = cursor.fetchall()
        conn.close()
        return [listing_id[0] for listing_id in listing_ids]

    def load_existing_values(self, table_name):
        """
        Loads existing names and platforms from the specified table.

        :param table_name: The name of the table to query as string.
        :return: A dictionary mapping names to platforms.

        Usage for methods: add_booking_data
        """
        query = f"SELECT name, platform FROM {self.schema_name}.{table_name}"
        conn = self.connect(dbname=self.database_name)
        df = pd.read_sql(query, conn)
        conn.close()
        return {row['name']: row['platform'] for _, row in df.iterrows()}

    def add_booking_data(self, df):
        """
        Adds booking data to the database, inserting new listings if necessary.

        :param df: The DataFrame containing the booking data.
        """
        # loads existing names and platform of the listing table
        db_names = self.load_existing_values('listings')
        # connects to database
        conn = self.connect(dbname=self.database_name)
        # defines columns for booking table
        booking_columns = ['listing_id', 'room_name', 'timestamp', 'price']

        # Get the current maximum listing_id and set the sequence
        max_listing_id = self.get_max_listing_id()
        self.set_listing_id_sequence(max_listing_id)

        # initializes progress bar
        pbar = tqdm(total=len(df), desc="Adding booking data", ncols=100, unit="row")

        # iterates through the DataFrame
        for _, row in df.iterrows():
            # checks if listing name already exists and if listing is from booking
            if row['name'] in db_names and db_names[row['name']] == 'booking':
                # if True -> selects listing_id from booking listing and adds data to booking table
                listing_id = self.get_listing_id(row['name'], conn)
                if not listing_id:
                    continue
                subset_booking = row[['room_name', 'timestamp', 'price']].copy()
                subset_booking['listing_id'] = listing_id
                self.insert_booking_data(subset_booking, booking_columns, conn)
            else:
                # if False -> inserts booking listing in listings table, selects listing_id and
                # adds data to booking table
                subset_listings = row[
                    ['neighbourhood_id', 'room_type_id', 'name', 'rating_score', 'rating_count', 'kitchen', 'tv',
                     'wifi', 'gym', 'elevator', 'fridge', 'heating', 'hair_dryer', 'air_conditioning',
                     'hot_tub', 'oven', 'bbq', 'coffee', 'pool', 'balcony', 'furniture', 'microwave', 'platform']
                ].to_frame().T
                self.populate_table('listings', subset_listings)
                listing_id = self.get_listing_id(row['name'], conn)
                if not listing_id:
                    continue
                subset_booking = row[['room_name', 'timestamp', 'price']].copy()
                subset_booking['listing_id'] = listing_id
                self.insert_booking_data(subset_booking, booking_columns, conn)

            # update progress bar
            pbar.update(1)

        pbar.close()
        conn.close()


    def get_listing_id(self, name, conn):
        """
        Retrieves the listing ID for a given name.

        :param name: The name of the listing as string.
        :param conn: The database connection.
        :return: The listing ID as integer if found, otherwise None.

        Usage for methods: add_booking_data
        """
        query = sql.SQL(f"SELECT listing_id FROM {self.schema_name}.listings WHERE name = %s AND platform = 'booking'")
        with conn.cursor() as cursor:
            cursor.execute(query, (name,))
            result = cursor.fetchone()
            if result:
                return result[0]
        return None

    def insert_booking_data(self, subset_booking, booking_columns, conn):
        """
        Inserts booking data into the booking table.

        :param subset_booking: The subset of the booking data as DataFrame.
        :param booking_columns: The columns for the booking table as list
        :param conn: The database connection.

        Usage for methods: add_booking_data
        """
        try:
            with conn.cursor() as cursor:
                insert_query = sql.SQL(f"""
                    INSERT INTO {self.schema_name}.booking (room_name, timestamp, price, listing_id)
                    VALUES (%s, %s, %s, %s)
                """)
                cursor.execute(insert_query, (
                    subset_booking['room_name'], subset_booking['timestamp'], subset_booking['price'],
                    subset_booking['listing_id']
                ))
                conn.commit()
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error during booking data insertion: {error}")
            conn.rollback()
            self.log_error('booking', booking_columns, error, (
                subset_booking['listing_id'], subset_booking['room_name'], subset_booking['timestamp'],
                subset_booking['price']))

    def create_data_mart(self, query, table_name):
        """
        Creates a data mart by executing a query to create and populate a table within a specified schema.

        :param query: The SQL query used to create and populate the table as a string.
        :param table_name: The name of the table to be created within the schema as a string.
        """
        create_schema_query = f"""
        CREATE SCHEMA IF NOT EXISTS {self.schema_name};
        """

        create_table_query = f"""
        CREATE TABLE {self.schema_name}.{table_name} AS {query}
        """

        try:
            self.execute_query(create_schema_query, dbname=self.database_name, commit=True)
            self.execute_query(create_table_query, dbname=self.database_name, commit=True)
        except (Exception, psycopg2.DatabaseError) as error:
            print(f"Error while creating schema or table: {error}")

    def get_max_listing_id(self):
        """
        Retrieves the maximum listing_id from the listings table.

        :return: The maximum listing_id as integer.

        Usage for methods: add_booking_data
        """
        query = f"SELECT MAX(listing_id) FROM {self.schema_name}.listings"
        conn = self.connect(dbname=self.database_name)
        cursor = conn.cursor()
        cursor.execute(query)
        max_id = cursor.fetchone()[0]
        conn.close()
        return max_id if max_id is not None else 0

    def set_listing_id_sequence(self, max_id):
        """
        Sets the listing_id sequence to start from max_id + 1.

        :param max_id: The maximum listing_id currently in the listings table.

        Usage for methods: add_booking_data
        """
        sequence_query = f"SELECT setval(pg_get_serial_sequence('{self.schema_name}.listings', 'listing_id'), {max_id + 1}, false)"
        self.execute_query(sequence_query, dbname=self.database_name, commit=True)


# for testing and building this module
if __name__ == '__main__':
    """
    This is executed only when this file is executed directly.
    """
    database = ManageDatabase('test_db', 'test_schema')
    database.create_database()
    database.create_table('test_table', 'test_id SERIAL PRIMARY KEY, column1 VARCHAR(255), column2 INTEGER')

    test_data = {
        'column1': ['valueone', 'valuetwo', 'valuethree', 'valuefour', 'valuefive'],
        'column2': [3, np.nan, 'x', 'y', 5]
    }

    test_df = pd.DataFrame(test_data)

    database.populate_table('test_table', test_df)
