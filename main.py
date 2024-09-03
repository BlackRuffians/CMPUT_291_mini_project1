import sqlite3
import sys
from display import Display
from interface import Interface
from functionality import Functionality

def main():
    if len(sys.argv) != 2:
      print("Usage: python3 main.py filename")
      sys.exit(1)
    dbfilename = sys.argv[1]                       
    db_connection = sqlite3.connect(dbfilename)           # Connect to an SQLite database (it will be created if it doesn't exist)
    cursor = db_connection.cursor()                       # Create a cursor object to execute SQL commands
    interface = Interface(db_connection)                  # Create interface object 
    interface.launch_Twitter()                            # Launch interface (complete after login)
    db_connection.close()
    return         

if __name__ == "__main__":
    main()
