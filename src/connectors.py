import sys
import snowflake.connector
from snowflake.snowpark import Session
import os
from dotenv import load_dotenv, find_dotenv

# Get environment vars
load_dotenv(find_dotenv())


def get_snowflake_connection(method):
    """ Confirm Access to Snowflake"""

    def close_session_wrapper():
        return session.close()

    try:

        params = {
            "user": os.getenv('SFUSER'),
            "password": os.getenv('SFPW'),
            "account": os.getenv('SNOWFLAKE_ACCT'),
            "warehouse": os.getenv('SFWH'),
            "database": os.getenv('SNOWFLAKE_DB'),
            "schema": os.getenv('SFSCHEMA')
        }

        key_vals = {key: val for key, val in params.items() if not val}

        if len(key_vals) > 0:
            print(f"Value in environment variables is missing!: {key_vals}")
            sys.exit(-1)

        if method == 'standard':
            conn = snowflake.connector.connect(
                user=params['user'],
                password=params['password'],
                account=params['account'],
                warehouse=params['warehouse'],
                database=params['database'],
                schema=params['schema']
            )

            return conn

        if method == 'spark':
            session = Session.builder.configs(params).create()
            return session

        if method == 'spark-close':
            close_session_wrapper()

    except Exception as e:
        raise e
