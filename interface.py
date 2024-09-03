import msvcrt
import sqlite3
import getpass

class Interface:
    def __init__(self,connection):
        self.connection=connection
        
    def launch_Twitter(self):
        """
        Opens up the main page 
        """
        cursor = self.connection.cursor() 
        
        print("(1) Login    (2) Create Account  (q) Quit")
        while True:
            #if msvcrt.kbhit():
                key = msvcrt.getch()
                try:
                    key = key.decode('utf-8')  # Convert bytes to string
                except UnicodeDecodeError as e:
                    print("Invalid input")
                    print("(1) Login    (2) Create Account  (q) Quit")
                if key == '1':
                    self.launch_Login(cursor)
                    return
                if key == '2':
                    self.launch_CreateAccount(cursor)
                elif key == 'q' or key == 'Q':
                    print("Come back soon!")
                    return

    def launch_Login(self, cursor):
        """
        Prompts the user to login
        Checks if the user's username and password are valid

        Args:
            cursor (Cursor), used to query the database
        """
        from display import Display
        print("  \n"*5)
        print("        LOGIN       \n")
        print("Please type your username and press enter.")
        while True:
            username = input("Enter your username: ")
            if self.is_valid_username(username, cursor):
                print(f"Valid username")
                break
            else:
                print("Invalid username. Please try again.")
        print("Please type your password and press enter.")
        while True:
            password = getpass.getpass("Enter your password: ")
            if self.is_valid_password(username, password, cursor):
                print(f"Valid password.")
                #return username
                userDisplay = Display(self.connection)                               # create a display page object
                userDisplay.openDisplay(username, cursor)
                return 

            else:
                print("Incorrect password. Please try again.")
        
    def is_valid_username(self, username, cursor):
        """
        Checks if a username is valid

        Args:
            username (str): The username a user inputted
            cursor (Cursor), used to query the database

        Returns:
            A boolean value indicating if the username is valid or not
        """
        try:
            cursor.execute("SELECT usr FROM users WHERE usr = ?", (username,))
            result = cursor.fetchone()
            if result:
                return True
        except sqlite3.Error as e:
            print("Database error:", e)
        return False
    
    def is_valid_password(self, username, password, cursor):
        """
        Checks if a password is valid

        Args:
            username (str): The valid username a user inputed
            password (str): The password a user inputed 
            cursor (Cursor), used to query the database

        Returns:
            A boolean value indicating if the username is valid or not
        """
        try:
            cursor.execute("SELECT pwd FROM users WHERE usr = ?", (username,))
            result = cursor.fetchone()
            if result[0] == password:
                return True
        except sqlite3.Error as e:
            print("Database error:", e)
        return False

    def launch_CreateAccount(self, cursor):
        """
        Creates an account when a user selects to create an account

        Args:
            cursor (Cursor), used to query the database
        """
        print("Create a username and press enter.")
        # Added type checking
        name= str(input("Please enter your Name : "))
        city=str(input("Please enter your city : "))
        while True:
            try:
                Timezone = float(input("Please enter your Timezone in (-8.0) format: "))
                break
            except ValueError:
                print("Invalid input. Please enter a decimal number for timezone.")
        Password=str(input("Please enter your new Password : "))
        email=str(input("Please enter your email : "))
        try:
            cursor.execute("SELECT max(usr) FROM users")
            highest_usr=cursor.fetchone()[0]
            highest_usr=0 if highest_usr is None else highest_usr

            new_usr=highest_usr+1

            #cursor.execute('''select * From users''')
            #print("done")
            cursor.execute('''INSERT INTO users (usr, pwd, name, email, city, timezone) VALUES (?, ?, ?, ?, ?, ?)''',(new_usr,Password, name, email, city, Timezone))
            
            print("Your username is: ",new_usr)


            self.connection.commit()
            print("  \n")
            print("---- SUCCESSFUL SIGNUP -----\n")
            self.launch_Login(cursor)

        except sqlite3.Error as e:
            print("Database error:", e)
            return
        
