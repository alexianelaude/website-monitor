
import random
import datetime
from datetime import datetime as dt

from monitor import get_stats, get_alerts
from db import insert_check, get_alert, get_site_status, create_user, create_website, delete_test_variables


def create_variables():
    create_user("testUser")
    create_website("http://www.downWebsite.com", "testUser", 2, 1) #A website already marked as down
    create_website("http://www.upWebsite.com", "testUser", 2, 0) #A website marked as up


def test_alerts_down():
    """Tests that alerts are launched when needed, and website status is set to down
    The same code with a website already down will not create an alert
    Tested by generating webchecks with random status code every 2s"""

    create_variables()

    t0 = dt.now()
    t = datetime.timedelta(seconds = 0)

    def create_down_check(url, t, status):
        insert_check((url, (t0 + t), 1, random.randint(1,600), None))
        twoMin = get_stats(url, datetime.timedelta(minutes = 2))
        get_alerts("testUser", url, status , twoMin)

    while (get_alert("http://www.upWebsite.com") is None) and t <= datetime.timedelta(minutes = 3):
        down_status = get_site_status(("http://www.downWebsite.com", "testUser"))
        up_status = get_site_status(("http://www.upWebsite.com", "testUser"))

        create_down_check("http://www.downWebsite.com", t, down_status)
        create_down_check("http://www.upWebsite.com", t, up_status)
        t += datetime.timedelta(seconds = 2)
    alert_upSite = get_alert("http://www.upWebsite.com")

    if alert_upSite is not None:

        print("Alert created at t + %s" % (str(t)))

        assert(alert_upSite[4] == 1) #The alert signals the website is now down

        assert(get_site_status(("http://www.upWebsite.com", "testUser")) == 1) #The website indeed is now down

        assert(alert_upSite[5] < 80)   #The website availability is under the 80% bar

        assert(get_alert("http://www.downWebsite.com") is None) #The website that was initially down hasn't created a new alert

    else:
        assert(alert_upSite is None)
    delete_test_variables()



def test_alerts_up():
    """Tests that alerts are launched when website has recovered, website status is set to up
        The same code with a website already up will not create an alert
        Tested by generating webchecks with 200 status code every 2s"""

    create_variables()

    t0 = dt.now()
    t = datetime.timedelta(seconds = 0)

    def create_up_check(url, t ,status):
        insert_check((url, (t0 + t), 1, 200, None))
        twoMin = get_stats(url, datetime.timedelta(minutes = 2))
        get_alerts("testUser", url, status, twoMin)

    while (get_alert("http://www.downWebsite.com") is None) and t <= datetime.timedelta(minutes = 3):
        down_status = get_site_status(("http://www.downWebsite.com", "testUser"))
        up_status = get_site_status(("http://www.upWebsite.com", "testUser"))

        create_up_check("http://www.downWebsite.com", t, down_status)
        create_up_check("http://www.upWebsite.com", t ,up_status)
        t += datetime.timedelta(seconds = 2)

    alert_downSite = get_alert("http://www.downWebsite.com")

    if alert_downSite is not None:

        print("Alert created at t + %s" % (str(t)))

        assert(alert_downSite[4] == 0) #The alert signals the website is now up

        assert(get_site_status(("http://www.upWebsite.com", "testUser")) == 0) #The website indeed is now up

        assert(alert_downSite[5] > 80)   #The website availability is above the 80% bar

        assert(get_alert("http://www.upWebsite.com") is None) #The website that was initially up hasn't created a new alert

    else:
        assert(alert_downSite is None)
    delete_test_variables()

delete_test_variables() #In case the test previously failed before delete..
test_alerts_down()
test_alerts_up()
print("Test succeeded!")
