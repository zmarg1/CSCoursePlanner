import sqlite3  #to use sqlite

#Constants
DB_FILENAME = "planner.db" # filename to form database


# function that initializes the db
def initDatabase():
    conn = sqlite3.connect(DB_FILENAME)


if __name__ == '__main__':
    initDatabase()
