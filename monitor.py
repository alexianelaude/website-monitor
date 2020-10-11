
import datetime
from datetime import datetime as dt
from db import insert_alert, purge_database, get_webchecks, get_time_for_alerts, get_site_status



def get_stats(url, timeGap):
    """Returns statistiques over the past "timeGap" minutes
    Return type is a dictionnary, times are converted to string to display on home page"""
    checks = get_webchecks((url, dt.now() - timeGap))
    max_response = 0
    sum_response = 0
    availability = 0
    response_dict = {}
    n = len(checks)
    if n > 0 :
        for check in checks:
            response_time = check[3]
            status = check[4]
            if status:
                if status >= 200 and status < 300:
                    availability += 1
                if response_dict.get(status) is not None:
                    response_dict[status] += 1
                else:
                    response_dict[status] = 1
            else:
                response_dict['Error'] +=1

            if response_time:
                if response_time > max_response:
                    max_response = response_time
                sum_response += response_time
        avg_response = sum_response/n
        max_response_str = "%ss " % (round(max_response, 4))
        avg_response_str = "%ss " % (round(avg_response, 4))
        availability = (availability/n)*100  #in purcentage

        return {'time_gap': "past " + str(timeGap.seconds/60) +"min",
                'availability': round(availability,4),
                'response_dict': response_dict,
                'max_response': max_response_str,
                'avg_response' : avg_response_str,
                'check_nb': n,
                } #We return the check number to use it for alert creation, only used for timeGap = 2min
    else:
        return {'time_gap': "past " + str(timeGap.seconds/60) +"min",
                'availability': 0,
                'response_dict': {},
                'max_response': 'No data',
                'avg_response':'No data',
                'check_nb': 0,
                } #Returned if no webchecks have been created in the past "timeGap" minutes

def get_alerts(username, url, down, twoMin):

    """Detects alerts, either up or down
    Down alerts are only generated for websites which are currently up, and vice versa
    Parameters: the user (to get the check interval) the website, and statistics over past two minutes
    Returns: True if an alert was created, False otherwise, so if an alert does occur, the home page is reloaded"""

    t = get_time_for_alerts((url, username))
    if twoMin['check_nb'] >= (100/t[0]): #We only start to launch alerts if there has been sufficient data collected in the past two minutes
        if ((down == 0) and twoMin['availability'] < 80):
            availability = twoMin['availability']
            insert_alert((url, username, dt.now(), 1, availability), (1, url, username))
            alert_msg =  "%s, Status: %s, availability: %s at: %s" % (url, 'down', round(availability, 4), dt.now().strftime("%H:%M:%S, %d/%m/%y"))
            return (alert_msg, 1) #The integer corresponds to the curses.color_pair id

        if ((down == 1) and twoMin['availability'] > 80):
            availability = twoMin['availability']
            insert_alert((url, username, dt.now(), 0, availability), (0, url, username))
            alert_msg = "%s,\n Status: %s,\n availability: %s \n At: %s" % (url, 'up', round(availability, 4), dt.now().strftime("%H:%M:%S, %d/%m/%y"))
            return (alert_msg, 2)
    return None

class Monitor(object):

    def __init__(self, user = None, websites = None):
        self.user = user
        self.websites = websites


    def get_info_short(self):
        """Called every 10s, gets metrics for websites over past 2 and 10 minutes
        Also used to create alerts if needed, and to purge database of webchecks that are more than one hour old
        Returns: dictionnary of metrics --> keys are the websites'url, values are the past 2 and 10min statistics, as well as eventual alerts"""
        total_data = {}
        for website in self.websites:
            url = website[0]
            twoMin = get_stats(url, datetime.timedelta(minutes=2))
            tenMin = get_stats(url, datetime.timedelta(minutes=10))

            status = get_site_status((url, self.user)) #We check if the site status has changed

            alert_msg = get_alerts(self.user, url, status, twoMin)

            purge_database((url, dt.today() - datetime.timedelta(hours=1)))

            data = ([twoMin, tenMin], alert_msg)
            total_data[url] = data
        return total_data

    def get_info_long(self):
        """Called every minute, gets metrics for website over past hour"""
        total_data = {}
        for website in self.websites:
            data = get_stats(website[0], datetime.timedelta(hours=1))
            total_data[website[0]] = data
        return total_data











