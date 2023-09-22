import sqlite3  #to use sqlite
import psycopg2


#Constants
DB_FILENAME = "planner.db"  # filename to form database for sqlite


# function that initializes the db locally for sqlite
def init_sqlite_database():
    # try to connect to the database first
    try:
        conn = sqlite3.connect(DB_FILENAME)
        print(f"Database {DB_FILENAME} created successfully.")
    except:
        print(f"Database {DB_FILENAME} not created.")

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


# initializes the remote postgresql database
def init_postgresql_remote():
    
"""


if __name__ == '__main__':
    init_sqlite_database()
