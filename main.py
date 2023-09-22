import sqlite3  #to use sqlite
import psycopg2
from supabase import create_client
import json

#Constants
DB_FILENAME = "planner.db"  # filename to form database for sqlite

"""
# function that initializes the db locally for sqlite
def init_sqlite_database():
    # try to connect to the database first
    try:
        conn = sqlite3.connect(DB_FILENAME)
        print(f"Database {DB_FILENAME} created successfully.")
    except:
        print(f"Database {DB_FILENAME} not created.")

    # Close the connection
    conn.close()
"""

"""
# initializes the db locally for postgresql
def init_postgresql_local():
    # establishing the db connection
    conn = psycopg2.connect(database="postgres",
                            user="postgres",
                            host='localhost',
                            password="NiJD557#",
                            port=5432)
    #
    conn.autocommit = True

    # Creating a cursor to do database operations
    cursor = conn.cursor()

    # create a database via sql query
    sql = ''' CREATE database plannerDB ''';

    # executes the database creation query
    cursor.execute(sql)
    print("Database has been created successfully !!");

    # Closing the connection
    conn.close()

"""


# connects to database
def connectDatabase():

    conn = psycopg2.connect(
        host = 'db.qwydklzwvbrgvdomhxjb.supabase.co',
        port = 5432,
        user = 'postgres',
        password = '2&?jL!Un?SV$Q5j',
        database='postgres'
    )

    conn.autocommit = True

    cursor = conn.cursor()

    cursor.execute("select * from course")

    names = list(map(lambda x: x[0], cursor.description))

    # retrieve the records from the database
    records = cursor.fetchall()

    print(records)
    print(names)

"""
def init_postgresql_remote():
    API_URL = 'https://qwydklzwvbrgvdomhxjb.supabase.co'
    API_KEY = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InF3eWRrbHp3dmJyZ3Zkb21oeGpiIiwicm9sZSI6ImFub24iLCJpYXQiOjE2OTU0MDcxNjcsImV4cCI6MjAxMDk4MzE2N30.UNZJCMI1NxpSyFr8bBooIIGPqTbDe3N-_YV9ZHbE_1g'
    supabase = create_client(API_URL, API_KEY)
    supabase

    conn.autocommit = True

    cursor = conn.cursor()

    cursor.execute("select * from course")

    names = list(map(lambda x: x[0], cursor.description))

    # retrieve the records from the database
    records = cursor.fetchall()

    print(records)
    print(names)
"""

if __name__ == '__main__':
    connectDatabase()
    print("done")
