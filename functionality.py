import sqlite3
from interface import Interface
import msvcrt
import math
import datetime
from searchusers import UserSearch


class Functionality:
    def __init__(self, connection):
        self.connection = connection

    def compose_tweet(self, cursor, usr_name):
        """Allows the user to post a tweet based on the functionality on the CMPUT 291 Mini project 1 Spec
        Args:
            cursor (Cursor), used to query the database
            usr_name (str): The user that is logged in 
        """
        print("Compose a tweet and press enter. \n")
        tweet_text = str(input("Enter your tweet: "))
        try:
            # Add tweets to database
            cursor.execute("SELECT MAX(tid) FROM Tweets")
            highest_tid = cursor.fetchone()[0]
            highest_tid = 0 if highest_tid is None else highest_tid
            new_tid = highest_tid + 1

            cursor.execute("""
                        INSERT INTO Tweets (tid, writer, tdate, text)
                        VALUES (?, ?, date('now'), ?);""",
                           (new_tid, usr_name, tweet_text))
            # add relevant data to hashtags table and mentions table
            # if tweet text like "I hate #Trump" then add Trump to hashtags table
            words = tweet_text.split()
            hashtags = [word for word in words if word.startswith("#")]
            hashtags = [hashtag[1:] for hashtag in hashtags]
            for hashtag in hashtags:
                # check and insert into hashtags, ignore if already exists in database
                # lower all hashtags in the hashtags list
                hashtag = hashtag.lower()
                cursor.execute("""
                            INSERT OR IGNORE INTO Hashtags (term) VALUES (?);""",
                               (hashtag,))
                # add mention to mentions table
                cursor.execute("""
                            INSERT INTO Mentions (tid, term) VALUES (?, ?);""",
                               (new_tid, hashtag))
            print("Tweet posted successfully.")
        except sqlite3.Error as e:
            print("Database error:", e)
        self.connection.commit()
        return

    def listFollowers(self, cursor, usr_name):
        """Allows the user to list the people following them
        based on the functionality on the CMPUT 291 Mini project 1 Spec
        Args:
            cursor (Cursor), used to query the database
            usr_name (str): The user that is logged in 
        """
        
        page = 0
        key = '0'
        while key != 'b' and key != 'B':
            cursor.execute('''
                            SELECT u.name, u.usr
                            FROM follows f, users u
                            WHERE flwee = ? AND u.usr = f.flwer
                            ''', (usr_name,))
            followers = cursor.fetchall()
            # print("\n"*30)
            print("Followers:\n___________")
            for follower in followers:
                print(str(follower[1]) +
                      (" "*(10-len(str(follower[1]))))+follower[0])
            print("\n (1) View profile by Id (b) to return to profile.")
            key = msvcrt.getch()
            try:
                key = key.decode('utf-8')  # Convert bytes to string
            except UnicodeDecodeError as e:
                print("Invalid input")

            if key == '1':

                follower_list = []
                for follower in followers:
                    follower_list.append(str(follower[1]))

                while True:

                    selected_username = input("UserID: ")
                    current_tweet_page = 0
                    if selected_username.isnumeric() and selected_username in follower_list:
                        selected_username = int(selected_username)
                        UserSearch.display_user_stats(
                            cursor, selected_username)
                        # print the 3 most recent tweets
                        tweets = UserSearch.get_all_tweets(
                            cursor, selected_username)
                        max_tweet_page_length = 3

                        tweet_pages = [tweets[x: x+max_tweet_page_length]
                                       for x in range(0, len(tweets), max_tweet_page_length)]

                        current_tweet_page = 0
                        UserSearch.show_tweets(tweet_pages, current_tweet_page)

                        # Give the user the option to follow the selected user or see more tweets

                        while True:
                            command = input(
                                "\n (1) Previous tweets (2) Next tweets (3) Follow the selected user (4) Return to main menu \n Enter command: ")
                            if command == '1':
                                if current_tweet_page > 0:
                                    current_tweet_page -= 1
                                    UserSearch.show_tweets(
                                        tweet_pages, current_tweet_page)
                                else:
                                    print("You are already on the first page.")
                            elif command == '2':
                                if current_tweet_page < len(tweet_pages) - 1:
                                    current_tweet_page += 1
                                    UserSearch.show_tweets(
                                        tweet_pages, current_tweet_page)
                                else:
                                    print("No more tweets")

                            elif command == '3':
                                UserSearch.follow_user(
                                    self, cursor, usr_name, selected_username)
                            elif command == '4':
                                return
                            else:
                                print("Please input one of the commands above.")
                    else:
                        print("Please Enter a valid username")

    def searchTweets(cursor):  # return a sorted lsit of tweets to display
        """Allows the user to search for tweets based on the functionality in the cmput 291 spec
        Args:
            cursor (Cursor), used to query the database
            
        """
        words = input(
            "Search for tweets using space separated keywords and hashtags:\n")
        words = words.split(" ")
        tweets = []
        for word in words:
            if word.startswith("#"):
                word1 = word[1:]
                cursor.execute('''
                    SELECT t.writer, t.tdate, t.text, t.tid, u.name
                    FROM tweets t, mentions m, users u
                    WHERE u.usr = t.writer AND m.tid = t.tid AND m.term LIKE ?
                                ''', (word1,))
                result = cursor.fetchall()
                tweets = tweets + result
            if word.startswith('#') == False:
                cursor.execute('''
                    SELECT t.writer, t.tdate, t.text, t.tid, u.name
                    FROM tweets t, users u
                    WHERE u.usr=t.writer AND  t.text LIKE ?;
                    ''', ('%'+word+'%',))
                result = cursor.fetchall()
                tweets = tweets + result

        tweets = list(set(tweets))
        tweets = sorted(tweets, key=lambda x: x[1], reverse=True)
        return tweets

    def displaySearch(tweets):
        """Shows the output of a search for tweets
        Arguments:
            -tweets()
        """
        page = 1
        print("\n"*30)
        print("Search results")

        Functionality.displayFive(tweets, page)
        print(
            "\n(1)Previous Page   (2)Next Page    (i)Select tweet     (b) Back to Profile")
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                try:
                    key = key.decode('utf-8')  # Convert bytes to string
                except UnicodeDecodeError as e:
                    print("Invalid input")
                    print(
                        "\n(1)Previous Page   (2)Next Page    (i)Select tweet     (b) Back to Profile")
                if key == '1':
                    if page != 1:
                        page -= 1
                        print("\n"*30)
                        print("Search results")
                        Functionality.displayFive(tweets, page)
                        print(
                            "\n(1)Previous Page   (2)Next Page    (i)Select tweet     (b) Back to Profile")
                if key == '2':
                    if page != math.ceil(len(tweets)/5) and math.ceil(len(tweets)/5) != 0:
                        page += 1
                        print("\n"*30)
                        print("Search results")
                        Functionality.displayFive(tweets, page)
                        print(
                            "\n(1)Previous Page   (2)Next Page    (i)Select tweet     (b) Back to Profile")
                if key == 'i' or key == 'I':
                    print("\n"*30)
                    max_count = Functionality.displayFive(tweets, page)
                    print("\n Enter tweet number or press b to go back: ")
                    while True:
                        if msvcrt.kbhit():
                            key1 = msvcrt.getch()
                            try:
                                # Convert bytes to string
                                key1 = key1.decode('utf-8')
                            except UnicodeDecodeError as e:
                                Functionality.displayFive(tweets, page)
                                print(
                                    "\n Enter tweet number or press b to go back: ")

                            if key1.isnumeric():

                                if int(key1) > 0 and int(key1) <= max_count:
                                    try:
                                        tweet_id = tweets[(
                                            5*(page - 1))+int(key1)-1][3]
                                    except IndexError:
                                        tweet_id = None
                                        pass  # the case when displayFive must display less then five
                                    print("\n"*30)
                                    return tweet_id
                if key == 'b' or key == 'B':
                    return 'b'

    def displayFive(tweets, page):
        
        """Displays five tweets
        Args:
            -tweets ():
            -page ():
            
        """
        count = 0

        while count < 5:
            try:
                tweet = tweets[(5*page)-(5-count)]
            except IndexError:
                break
            print("")
            print("Tweet #" + str(count+1))
            print("Author: " + str(tweet[4]) + " Date: " + tweet[1])
            print(tweet[2])
            count += 1
        if page == math.ceil(len(tweets)/5):
            print("\n No more tweets!")
        print("\n--Page " + str(page) + " of " +
              str(math.ceil(len(tweets)/5)) + "--")
        return count
