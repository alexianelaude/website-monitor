import sqlite3

DATABASE_NAME = 'webmonitor.db'


def get_websites(user):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM website WHERE  user = ?", (user,))
    websites = cursor.fetchall()
    conn.close()
    return websites

def insert_check(values):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT into WEBCHECK (URL, REQUESTTIME, RESPONSETIME, STATUS, ERROR) VALUES (?, ?, ?, ?, ?)",
                            values)
    conn.commit()
    conn.close()

def insert_alert(alert, webinfo):
    """Also updates the website's status"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT into ALERT (URL, USER, TIME, DOWN, AVAILABILITY) VALUES (?, ?, ?, ?, ?)",
                       alert)
    cursor.execute("UPDATE WEBSITE set DOWN = ? where url = ? AND user =  ?", webinfo)
    conn.commit()
    conn.close()


def purge_database(values):
    """Webchecks older than one hour are automatically deleted from the database, so as to not overload it"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM WEBCHECK WHERE url = ? and REQUESTTIME < ?",
                   values)
    conn.commit()
    conn.close()

def get_webchecks(values):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM WEBCHECK WHERE  url = ? and REQUESTTIME > ? ", values)
    checks = cursor.fetchall()
    conn.close()
    return checks

def get_time_for_alerts(values):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT INTERVAL FROM WEBSITE WHERE  url = ? AND user =  ?",values)
    t = cursor.fetchone()
    conn.close()
    return t

def get_alert(url):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ALERT WHERE  url = ? ", (url, ))
    alert = cursor.fetchone()
    conn.close()
    return alert

def get_site_status(values):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM WEBSITE WHERE  url = ? AND user = ? ", values)
    website = cursor.fetchone()
    is_down = website[3]
    conn.close()
    return is_down

def create_user(username):
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("INSERT into USER (USERNAME) VALUES (?)",(username, ))
    conn.commit()
    conn.close()
    print("Your user has been created!")

def create_website(url, username, dt = None, down = 0):
    """We automatically add http:// to the url if it isn't included in the url given by the user
    t is the check interval, entered by the user but default to 2s,
    down is the status, default to False"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    protocol = url.split(":")[0]
    if protocol != 'http':
        url = "http://" + url
    cursor.execute("SELECT * FROM website WHERE user = ?  and url = ?", (username, url))
    existing_website = cursor.fetchone()
    if existing_website is None:
        if dt is None:
            print("Enter the check interval for in this website (in seconds - enter a float")
            dt = input()
            try:
                dt = float(dt)
            except:
                print("This is not a valid time interval")
        try:
            cursor.execute("INSERT into WEBSITE (URL, USER, INTERVAL, DOWN) VALUES (?, ?, ?, ?)", (url, username, dt, down))
            conn.commit()
            print("Your website has been created!")
        except sqlite3.Error:
            print("error creating the website")
    else:
        print("You have already created this website!")
    conn.close()

def delete_website(url, user):
    """Also deletes all alerts related to this website,
    We automatically add http:// to the url if it isn't included in the url given by the user"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()

    protocol = url.split(":")[0]
    if protocol != 'http':
        url = "http://" + url

    cursor.execute("SELECT * FROM website WHERE url = ? and user = ?", (url, user))
    website_user = cursor.fetchone()
    if website_user is not None:
        print("Are you sure you want to delete this website? [yes/no]")
        answer = input()
        if answer == 'yes'.lower():
            cursor.execute("DELETE from WEBSITE WHERE url = ? and user = ?", (url, user))
            cursor.execute("DELETE FROM ALERT WHERE url = ? and user = ?", (url,user))
            conn.commit()
            print("The website has been deleted")
    else:
        print("You can't delete a website that you haven't added yet!")
    conn.close()

def delete_test_variables():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE from USER WHERE username = ?", ("testUser",))
    cursor.execute("DELETE from WEBSITE WHERE url = ? AND user = ?", ("http://www.downWebsite.com", "testUser"))
    cursor.execute("DELETE from WEBSITE WHERE url = ? AND user = ?", ("http://www.upWebsite.com", "testUser"))
    cursor.execute("DELETE from ALERT WHERE url = ?", ("http://www.upWebsite.com", ))
    cursor.execute("DELETE from ALERT WHERE url = ?", ("http://www.downWebsite.com", ))
    cursor.execute("DELETE from WEBCHECK WHERE url = ?", ("http://www.upWebsite.com", ))
    cursor.execute("DELETE from WEBCHECK WHERE url = ?", ("http://www.downWebsite.com", ))

    print("Test variables deleted")
    conn.commit()
    conn.close()

def get_all_alerts(user):
    """Used to display all previous alerts at the launch of the program"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * from ALERT WHERE user = ? ORDER BY date(TIME) ", (user,))
    alerts = cursor.fetchall()
    alert_msgs = []
    for alert in alerts:
        if alert[4] == 1:
            status = 'down'
            color = 1 #corresponds to the curses.init_pair id
        else:
            status = 'up'
            color = 2
        alert_msg = "%s, \n Status: %s,\n availability: %s \n At: %s" % (alert[1], status, round(alert[5], 4), alert[3])
        alert_msgs.append((alert_msg, color))
    conn.close()
    return alert_msgs



