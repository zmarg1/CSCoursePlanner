import sqlite3

# filename to form database
DB_FILENAME = "planner.db"

# function that initializes the db
def initDatabase():
    conn = sqlite3.connect(DB_FILENAME)

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    initDatabase()
