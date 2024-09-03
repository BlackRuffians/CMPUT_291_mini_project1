import sqlite3
from datetime import date

class UserSearch:
    
    def __init__(self, connection):
        self.connection = connection

    def is_userid_in_page(userid, page):
        """
        Checks if a user's id is being displayed on the current page

        Args:
            userid (str): userid of the user
            page (list[str]): list of users being displayed

        Returns:
            _type_: _description_
        """
        return any(user[0] == userid for user in page)

    def show_tweets(tweet_pages, current_tweet_page):
        """
            Prints all of the tweets on a current tweet page
        Args:
            tweet_pages (list[list[tuple]]): a list of all tweet pages containing tweets
            current_tweet_page (int): Current index of the tweet page
        """

        if tweet_pages:
            for tweet in tweet_pages[current_tweet_page]: 
                print(tweet)
        else: 
            print("Selected user has no tweets.")
                      
    def follow_user(self, cursor, current_usr, selected_user):
        """
            Follows a user
        Args:
            cursor (Cursor), used to query the database
            current_user (str): The user that is logged in 
            selected_user (int): The user that the current)user wants to follow
            
        """
        # Check if current user is already following the selected user
        if int(current_usr) == selected_user:
            print("You cannot follow yourself")
            return
        cursor.execute("""
                    SELECT 1 
                    FROM follows
                    WHERE flwer = ? AND flwee = ?;""",
                    (current_usr, selected_user))
        result = cursor.fetchall()
        if result:
            print("You are already following the selected user")
            return
        
        try:
            cursor.execute("""
            INSERT INTO follows(flwer, flwee, start_date)
            VALUES(?, ?, date('now'))""",
            (current_usr, selected_user))
        
            self.connection.commit()
            print("Successfully followed selected user")
            
        except sqlite3.Error as e:
            print(f"SQLite error: {e}")
            self.connection.rollback()

    def display_user_stats(cursor, usr):
        """
            Display user stats: # of tweets, # of followers, # of users, # of followers
        Args:
            cursor (Cursor), used to query the database
            usr (int): The user that was selected
            
        """
        # get # of tweets
        cursor.execute("""
            SELECT COUNT(tid)
            FROM tweets
            WHERE writer = ?;""", (str(usr),))
        num_of_tweets = cursor.fetchall()
        
        # get # of followers
        cursor.execute("""
            SELECT COUNT(*)
            FROM follows
            WHERE flwee = ?;""", (str(usr),))
        num_of_followers = cursor.fetchall()
        
        # get # of users that the user is following
        cursor.execute("""
            SELECT COUNT(*)
            FROM follows
            WHERE flwer = ?;""", (str(usr),))
        num_of_people_following = cursor.fetchall()
        
        # Print the stats
        print(f"Number of tweets: {num_of_tweets[0][0]}")
        print(f"Number of users following: {num_of_people_following[0][0]}")
        print(f"Number of followers: {num_of_followers[0][0]}")
        
    def get_all_tweets(cursor, usr):
        """
            Gets all the tweets from a selected user
            Args:
            cursor (Cursor), used to query the database
            usr (int): The user that was selected
            Returns list(tuple): A list of all tweets
         """
        cursor.execute("""
            SELECT tid, writer, tdate, text
            FROM tweets
            WHERE writer = ?
            ORDER BY tdate ASC;""", (str(usr),))
        return cursor.fetchall()

    def show_users(self, pages, current_page):
        """
            Display users on a current page
            Args:
            pages (list): A list of all pages containing users returned in a search
            current_page (int): The index of the current page
            
        """
        print("(UserID | Name | City)")
        
        if pages:
            for user in pages[current_page]: 
                print(user)
              
    def search_users(self, cursor, usr_name):
        """
            Allows for a user to search for a user via a keyword
            Args:
            cursor (Cursor), used to query the database
            usr_name (int): The user that is currently logged in
            
        """
        print("Search for a user and press enter.")
        keyword = input("Enter a keyword: ")
        if not keyword.isdigit(): 
            keyword = keyword.lower()
        # Find all users whose name match the keyword
        cursor.execute("""
                    SELECT usr, name, city
                    FROM users
                    WHERE LOWER(name) LIKE ? ORDER BY LENGTH(name) ASC;""",
                    ('%'+keyword+'%',))
        result = cursor.fetchall()
            
        # Find all users whose city but not name match
        cursor.execute("""
                        SELECT usr, name, city
                        FROM users
                        WHERE LOWER(city) LIKE ? AND LOWER(name) NOT LIKE ?
                        ORDER BY LENGTH(city) ASC;""", ('%'+keyword+'%','%'+keyword+'%'))
        result.extend(cursor.fetchall())
        
        
        # Divide the results into pages of 5
        max_page_length = 5
        
        pages = [result[x: x+max_page_length] for x in range(0, len(result), 5)]
        
        # List all users on the current page
        current_page = 0
        
        # Select a user and see more information about them
        while True:
            self.show_users(pages, current_page)
            command = input("\n (b) Previous users (n) Next users (i) Select a user (0) Return to Profile \n Enter command: ")
            if command.lower() == 'b':
                        if current_page != 0:
                            current_page -= 1
                            self.show_users(pages, current_page)
                        else:
                            print("You are already on the first page.")
            elif command == 'n':
                if current_page < len(pages) - 1:
                    current_page += 1
                    self.show_users(pages, current_page)
                else:
                    print("No more users")
                        
            
            elif command.isnumeric():
                command = int(command)
                if command == 0:
                    return
                
                elif UserSearch.is_userid_in_page(int(command), pages[current_page]):
                    selected_user = int(command)
                    UserSearch.display_user_stats(cursor, selected_user)

                    
                    # print the 3 most recent tweets
                    tweets = UserSearch.get_all_tweets(cursor, selected_user)
                    max_tweet_page_length = 3

                    tweet_pages = [tweets[x: x+max_tweet_page_length] for x in range(0, len(tweets), max_tweet_page_length)]
            
                    current_tweet_page = 0 
                    UserSearch.show_tweets(tweet_pages, current_tweet_page)
                        
                    # Give the user the option to follow the selected user or see more tweets
                    while True:
                        command = input("\n (1) Previous tweets (2) Next tweets (3) Follow the selected user (4) Return to main menu \n Enter command: ")
                        if command == '1':
                            if current_tweet_page > 0:
                                current_tweet_page -= 1
                                UserSearch.show_tweets(tweet_pages, current_tweet_page)
                            else:
                                print("You are already on the first page.")
                        elif command == '2':
                            if current_tweet_page < len(tweet_pages) - 1:
                                current_tweet_page += 1
                                UserSearch.show_tweets(tweet_pages, current_tweet_page)
                            else:
                                print("No more tweets")
                        
                        elif command == '3': 
                            UserSearch.follow_user(self, cursor, usr_name, selected_user)
                        elif command == '4':
                            return
                        else:
                            print("Please input one of the commands above.")
                else:
                    print("Please Enter a valid command")
                        
            else:
                print("Please Enter a valid command")
