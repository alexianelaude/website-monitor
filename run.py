import argparse
import sqlite3
from db import DATABASE_NAME, delete_website, create_website, create_user, get_all_alerts, get_websites
from monitor import Monitor
from webchecks import WebThreading
import time
import curses
from curses import wrapper


parser = argparse.ArgumentParser(description='Monitor website')

parser.add_argument('user', type = str, help='your user')
parser.add_argument('-w', '--website', type = str,  help='create a new website')
parser.add_argument('-d', '--delete', type = str, help = 'delete a website')
parser.add_argument('-l', '--list', action = 'store_true', help = "list all the user's websites")


args = parser.parse_args()


def init_screen(screen, websites, user):
    """Creates all the necessary windows:
    3 for each website, one for the past 2min statistics, one for the past 10min statistics, and one for long term statistics,
    One side window for the alerts
    All of the alert history is then displayed
    The colors for the alerts are created"""
    n = len(websites)
    tot_ligns, tot_columns = screen.getmaxyx()
    screen.addstr(0, tot_columns//3, "Welcome to the website monitor app!", curses.A_STANDOUT)
    screen.refresh()

    alert_win = curses.newwin(tot_ligns-2, tot_columns//4, 2, int(tot_columns *(3/4)))
    windows = {}
    windows_long = {}

    for (i, website) in enumerate(websites):
        web_win2 = curses.newwin((tot_ligns-2)//n, tot_columns//4, ((tot_ligns-2)//n)*i + 2, 0)
        web_win10 = curses.newwin((tot_ligns-2)//n, tot_columns//4, ((tot_ligns-2)//n)*i + 2, tot_columns // 4)
        web_win_long = curses.newwin((tot_ligns-2)//n, tot_columns //4, ((tot_ligns-2)//n)*i + 2, tot_columns // 2)
        windows[website[0]] = (web_win2, web_win10)
        windows_long[website[0]] = web_win_long

    curses.init_pair(1, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_GREEN, curses.COLOR_BLACK)

    alert_win.addstr("Alerts: \n", curses.A_BOLD)
    alerts = get_all_alerts(user)
    for (alert, color) in alerts:
        alert_win.addstr(alert + '\n', curses.color_pair(color))
    alert_win.refresh()

    return windows, windows_long, alert_win


def run(screen, user):
    """Initializes the curses screen
    Initializes a monitor to retrieve the websites' statistics and generate alerts
    Starts threads for each website to generate webchecks
    Displays the statistics and alerts on the screen"""

    websites = get_websites(user)
    windows, windows_long, alert_win = init_screen(screen, websites, user)
    monitor = Monitor(user, websites)
    timer_long = 0

    for website in websites:
        url = website[0]
        dt = website[2]
        t = WebThreading(url ,dt)
        t.start()

    while True:
        tot_data = monitor.get_info_short() #Statistics over the past 2 and 10 minutes, refreshed every 10s
        for (k, v) in tot_data.items():
            ((twoMin, tenMin), alert) = v
            (web_win2, web_win10) = windows.get(k)
            web_win2.clear()
            web_win10.clear()
            web_win2.addstr(k + ": \n", curses.A_BOLD)
            web_win10.addstr("\n")
            for data, web_win in zip([twoMin, tenMin], [web_win2, web_win10]):
                web_win.addstr("Statistics over %s: \n" % (data['time_gap']))
                web_win.addstr("Availability: " + str(data['availability']) +"\n")
                web_win.addstr("Max response time: %s \n" % (data['max_response']))
                web_win.addstr("Average response time: %s \n" % (data['avg_response']))
                web_win.addstr("Response codes counts:" + str([(str(k) + ": " + str(v)) for (k,v) in data['response_dict'].items()])+ '\n')
                web_win.refresh()
            if alert is not None:
                alert_win.addstr(alert[0] + '\n', curses.color_pair(alert[1]))
                alert_win.refresh()

        time.sleep(10)
        timer_long += 10
        if timer_long == 60:
            timer_long = 0
            tot_data = monitor.get_info_long() #Statistics over the past hour, refreshed every minute
            for (k, data) in tot_data.items():
                web_win_long = windows_long.get(k)
                web_win_long.clear()
                web_win_long.addstr("\n")
                web_win_long.addstr("Statistics over past hour: \n")
                web_win_long.addstr("Availability: " + str(data['availability']) + "\n")
                web_win_long.addstr("Max response time: %s \n" % (data['max_response']))
                web_win_long.addstr("Average response time: %s \n" % (data['avg_response']))
                web_win_long.addstr("Response codes counts:" + str(
                    [(str(k) + ": " + str(v)) for (k, v) in data['response_dict'].items()]) + '\n')
                web_win_long.refresh()



def authenticate(user):
    """Returns true if user is authenticated, false otherwise
    Enables creation of new user (who is then authenticated)"""
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM user WHERE username = ? ", (user, ))
    existing_user = cursor.fetchone()
    conn.close()
    if existing_user is None:
        print("This user doesn't exist, do you want to create it ? [yes/no]")
        answer = input()
        if answer == 'yes'.lower():
            create_user(user)
            return True
        else:
            return False
    else:
        return True

if args.list:
    permission = authenticate(args.user)
    if permission:
        websites = get_websites(args.user)
        for website in websites:
            print("%s, check interval: %s s, current status: %s" % (website[0], website[2], website[3]))
    quit()

if args.website:
    permission = authenticate(args.user)
    if permission:
        create_website(args.website, args.user)
    else:
        print("You must create a user before creating a website")
    quit()

if args.delete:
    permission = authenticate(args.user)
    if permission:
        delete_website(args.delete, args.user)
    else:
        print("You must create a user before deleting a website")
    quit()


authenticated = authenticate(args.user)
if authenticate:
    wrapper(run, args.user)





