import sqlite3

# filename to form database
DB_FILENAME = "planner.db"

def initDatabase():
    conn = sqlite3.connect(DB_FILENAME)

    conn.execute('''CREATE TABLE COMPANY
             (ID INT PRIMARY KEY     NOT NULL,
             NAME           TEXT    NOT NULL,
             AGE            INT     NOT NULL,
             ADDRESS        CHAR(50),
             SALARY         REAL);''')

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    initDatabase()
