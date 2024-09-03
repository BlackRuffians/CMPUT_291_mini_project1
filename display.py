import sqlite3
import math
import getpass
import msvcrt
from functionality import Functionality
from searchusers import UserSearch


class Display:

    page = 1 #controlled by Functionality.displayFive(tweets, page)

    def __init__(self, connection):
        self.connection = connection

    def openDisplay(self, user, cursor):
        """Display a users tweets with several options.
        Arguments:
            - (Display) self, to use methods within the Display class
            - (int) user, the user for which the display is created
            - (Connection) connection, a connection to a database with sqlite3
        Description:
            This function will display tweets descending in date, five at a time. Tweets to be displayed
            are tweets from followed users and tweets that are retweeted by followed users.
            The user can select options (1) and (2) to scroll through pages containing five tweets.
            The user can select a tweet (i), in which the user enters the tweet number (shown on the display),
            and launch_tweet_interface(self, cursor, tid, user) is called with the selected tweets tid.
            The user can open thier user profile (p), which calls launchUserProfile(self, cursor, user).
            The user can exit the display by logging out (3), in which logout_test(self) is called upon return.
        """
        try:
            cursor.execute("""
                SELECT t.writer, t.tdate, t.text, t.tid, u.name
                FROM tweets t, users u
                JOIN follows f ON t.writer = f.flwee
                WHERE f.flwer = ? AND t.writer=u.usr
                UNION
                SELECT t.writer, t.tdate, t.text, t.tid, u.name
                FROM tweets t, users u
                JOIN retweets r ON t.tid = r.tid
                JOIN follows f ON r.usr = f.flwee
                WHERE f.flwer = ? AND t.writer=u.usr
                ORDER BY tdate DESC;
                           """, (user, user))
            tweets = cursor.fetchall()
        except sqlite3.Error as e:
            print("Database error:", e)

        self.nextPage()
        Functionality.displayFive(tweets, self.page)
        print("\n (1) Previous Page   (2) Next Page  (3)Logout   (i) Select tweet    (p) Profile")
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                try:
                    key = key.decode('utf-8')  # Convert bytes to string
                except UnicodeDecodeError as e:
                    print("Invalid input")
                    print(
                        "\n (1) Previous Page   (2) Next Page  (3)Logout   (i) Select tweet    (p) Profile")
                if key == '1':
                    if self.page != 1:
                        self.page -= 1
                        self.nextPage()
                        Functionality.displayFive(tweets, self.page)
                        print(
                            "\n (1) Previous Page   (2) Next Page  (3)Logout   (i) Select tweet    (p) Profile")
                    else:
                        self.nextPage()
                        Functionality.displayFive(tweets, self.page)
                        print("You are already on the first page! \n")
                        print("\n (1) Previous Page   (2) Next Page  (3)Logout   (i) Select tweet    (p) Profile")
                if key == '2':
                    if self.page != math.ceil(len(tweets)/5) and math.ceil(len(tweets)/5) != 0:
                        self.page += 1
                        self.nextPage()
                        Functionality.displayFive(tweets, self.page)
                        print(
                            "\n (1) Previous Page   (2) Next Page  (3)Logout   (i) Select tweet    (p) Profile")
                if key == 'i' or key == 'I':
                    self.nextPage()
                    max_count = Functionality.displayFive(tweets, self.page)
                    print("\n Enter tweet number or press b to go back: ")
                    while True:
                        if msvcrt.kbhit():
                            key1 = msvcrt.getch()
                            try:
                                key1 = key1.decode('utf-8')
                            except UnicodeDecodeError as e:
                                Functionality.displayFive(tweets, self.page)
                                print(
                                    "\n Enter tweet number or press b to go back: ")

                            if key1.isnumeric():

                                if int(key1) > 0 and int(key1) <= max_count:
                                    try:
                                        tweet_id = tweets[(
                                            5*(self.page - 1))+int(key1)-1][3]
                                    except IndexError:
                                        tweet_id = None
                                        pass  # the case when displayFive must display less then five
                                    self.nextPage()
                                    self.launch_tweet_interface(
                                        cursor, tweet_id, user)
                                    Functionality.displayFive(
                                        tweets, self.page)
                                    print(
                                        "\n (1) Previous Page   (2) Next Page  (3)Logout   (i) Select tweet    (p) Profile")
                                    break
                            if key1 == 'b' or key == 'B':
                                self.nextPage()
                                Functionality.displayFive(tweets, self.page)
                                print(
                                    "\n (1) Previous Page   (2) Next Page  (3)Logout   (i) Select tweet    (p) Profile")
                                break
                if key == '3':
                    self.nextPage()
                    return self.logout()
                if key == 'p' or key == 'P':
                    self.nextPage()
                    self.launchUserProfile(cursor, user)
                    self.nextPage()
                    return self.openDisplay(user, cursor)

    def logout(self):
        """Transitions from an open Display to the login page.
        Arguments:
            - (Display) self, to use methods within the Display class
        Description:
            This function is called after a display is closed (a user logs out). It
            launches a new login page by calling Interface.launch_Twitter(self).
        """
        from interface import Interface
        print("   \n")
        print("------- LOGGING OUT -----------\n")
        User_interface = Interface(self.connection)
        User_interface.launch_Twitter()

    def launch_tweet_interface(self, cursor, tid, user):
        """Display a selected tweet with some options. 
        Arguments:
            - (Display) self, to use methods within the Display class
            - (Cursor) cursor, used to query the database
            - (int) tid, the tid of the selected tweet
            - (int) user, id of the logged in user selecting a tweet
        Description:
            Called from Display.openDisplay, this function will display the selected tweet, along with extra information 
            like its author, date, retweet count and reply count. The user can select (1) to retweet the selected tweet. 
            The user can select (2) to reply to a tweet, in which they will be prompted to input a text that will create
            a new tweet in response to the selected tweet. The user can select (b) to return to the openDisplay function. 
        """
        try:  # get author
            cursor.execute("""
                SELECT u.name
                FROM users u, tweets t
                WHERE t.tid = ? AND t.writer = u.usr
                           """, (tid,))
            author = cursor.fetchone()[0]
        except sqlite3.Error as e:
            print("Database error:", e)
        try:  # get date
            cursor.execute("""
                SELECT tdate
                FROM tweets
                WHERE tid = ?
                           """, (tid,))
            date = cursor.fetchone()[0]
        except sqlite3.Error as e:
            print("Database error:", e)
        try:  # get text
            cursor.execute("""
                SELECT text
                FROM tweets
                WHERE tid = ?
                           """, (tid,))
            text = cursor.fetchone()[0]
        except sqlite3.Error as e:
            print("Database error:", e)
        try:  # get number of retweets
            cursor.execute("""
                SELECT count(*)
                FROM retweets 
                WHERE tid = ?
                           """, (tid,))
            retweetCount = cursor.fetchone()[0]
        except sqlite3.Error as e:
            print("Database error:", e)
        try:  # get number of replies
            cursor.execute("""
                SELECT count(*)
                FROM tweets
                WHERE replyto = ?
                           """, (tid,))
            replyCount = cursor.fetchone()[0]
        except sqlite3.Error as e:
            print("Database error:", e)

        self.nextPage()
        print("Author: " + str(author) + "      Date: " + str(date))
        print("\n"+str(text))
        print("\nRetweets: " + str(retweetCount) +
              "    Replies: " + str(replyCount)+"\n")
        print("(1) Retweet       (2) Reply to Tweet        (b) Back")
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                try:
                    key = key.decode('utf-8')  # Convert bytes to string
                except UnicodeDecodeError as e:
                    self.nextPage()
                    print("Author: " + str(author) +
                          "      Date: " + str(date))
                    print("\n"+str(text))
                    print("\nRetweets: " + str(retweetCount) +
                          "    Replies: " + str(replyCount)+"\n")
                    print("(1) Retweet       (2) Reply to Tweet        (b) Back")
                if key == '1':
                    try:
                        cursor.execute('''
                            SELECT usr
                            FROM retweets
                            WHERE tid = ? AND usr = ?;
                                        ''', (tid, user))
                    except sqlite3.IntegrityError as e:
                        print("Database Error: "+e)
                    if cursor.fetchone() == None:
                        try:
                            cursor.execute('''
                                INSERT INTO retweets(usr, tid, rdate)
                                VALUES (?,?,date('now'))
                                            ''', (user, tid))
                        except sqlite3.IntegrityError as e:
                            self.nextPage()
                            print("Tweet already Retweeted")

                        self.connection.commit()
                        cursor.execute("""
                        SELECT count(*)
                        FROM retweets 
                        WHERE tid = ?
                           """, (tid,))
                        retweetCount = cursor.fetchone()[0]
                        self.nextPage()
                        print("Author: " + str(author) +
                              "      Date: " + str(date))
                        print("\n"+str(text))
                        print("\nRetweets: " + str(retweetCount) +
                              "    Replies: " + str(replyCount)+"\n")
                        print("Retweeted  post by " + author)
                        print("(1) Retweet       (2) Reply to Tweet        (b) Back")

                    else:
                        self.nextPage()
                        print("Author: " + str(author) +
                              "      Date: " + str(date))
                        print("\n"+str(text))
                        print("\nRetweets: " + str(retweetCount) +
                              "    Replies: " + str(replyCount)+"\n")
                        print("Tweet already Retweeted")
                        print("(1) Retweet       (2) Reply to Tweet        (b) Back")

                if key == '2':
                    self.nextPage()
                    print("Author: " + str(author) +
                          "      Date: " + str(date))
                    print("\n"+str(text))
                    print("\nRetweets: " + str(retweetCount) +
                          "    Replies: " + str(replyCount)+"\n")
                    reply = input("Replying to " + author+": ")
                    cursor.execute("SELECT max(tid) FROM tweets")
                    newtid = cursor.fetchone()[0] + 1
                    cursor.execute('''
                                   INSERT INTO tweets(tid, writer, tdate, text, replyto)
                                   VALUES (?,?,date('now'),?,?)
                                   ''', (newtid, user, reply, tid))
                    self.connection.commit()

                    words = reply.split()
                    for word in words:
                        if word.startswith('#'):
                            word = word[1:]
                            # insert these words into metions
                            cursor.execute(
                                "INSERT INTO mentions (tid, term) VALUES(?,?)", (newtid, word.lower()))
                            self.connection.commit()
                            # insert into hashtags conditionally
                            cursor.execute(
                                "SELECT term FROM hashtags WHERE term LIKE ?;", (word,))
                            exists = cursor.fetchone()
                            if exists == None:
                                cursor.execute(
                                    "INSERT INTO hashtags(term) VALUes(?)", (word.lower(),))
                                self.connection.commit()

                    # get new reply count for display
                    cursor.execute("""
                    SELECT count(*)
                    FROM tweets
                    WHERE replyto = ?
                           """, (tid,))
                    replyCount = cursor.fetchone()[0]
                    self.nextPage()
                    print("Author: " + str(author) +
                          "      Date: " + str(date))
                    print("\n"+str(text))
                    print("\nRetweets: " + str(retweetCount) +
                          "    Replies: " + str(replyCount)+"\n")
                    print("Replied to post by " + str(author)+"\n")
                    print("(1) Retweet       (2) Reply to Tweet        (b) Back")

                if key == 'B' or key == 'b':
                    self.nextPage()
                    return

    def launchUserProfile(self, cursor, user):
        """Display options for a user.
        Arguments:
            - (Display) self, to use methods within the Display class
            - (Cursor) cursor, to query the database
            - (int) user, the user id of the user.
        Description:
            called from Display.openDisplay, this function will display options for the user. The user can select 
            (1) to compose a tweet in which Functionality.compose_tweet(self, cursor, user) is called, (2) to view
            followers in which Functionality.listFollowers(cursor, user) is called, (3) to search for tweets by keyword 
            in which Functionality.searchTweets(cursor) and Functionality.displaySearch(searchedTweets) is called, (4)
            to search for users in which userSearch.search_users(cursor, user) is called, and (b) in which the function 
            is returned to the 
            openDisplay function. 

        """

        print("USER PROFILE \n\n(1) Compose Tweet\n(2) View Followers\n(3) Search Tweets\n(4) Search Users\n(b) Back")
        while True:
            if msvcrt.kbhit():
                key = msvcrt.getch()
                try:
                    key = key.decode('utf-8')  # Convert bytes to string
                except UnicodeDecodeError as e:
                    pass
                if key == '1':
                    Functionality.compose_tweet(self, cursor, user)
                    self.nextPage()
                    return self.launchUserProfile(cursor, user)
                if key == '2':
                    Functionality.listFollowers(self, cursor, user)
                    self.nextPage()
                    return self.launchUserProfile(cursor, user)
                if key == '3':
                    searchedTweets = Functionality.searchTweets(cursor)
                    while True:
                        option = Functionality.displaySearch(searchedTweets)
                        self.nextPage()
                        if option == 'b':
                            break
                        self.launch_tweet_interface(cursor, option, user)
                    searchedTweets = []
                    return self.launchUserProfile(cursor, user)
                if key == '4':
                    search_instance = UserSearch(self.connection)
                    search_instance.search_users(cursor, user)
                    return self.launchUserProfile(cursor, user)
                if key == 'b' or key == 'B':
                    return

    def nextPage(self):
        """Print 30 new lines, used for organizing the display in the command line output"""
        print("\n"*30)
