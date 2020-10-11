import requests
import threading

from datetime import datetime as dt
from db import insert_check


class WebThreading(threading.Thread):

    def __init__(self, url, check_interval):
        threading.Thread.__init__(self)
        self.url = url
        self.check_interval = check_interval

    def run(self):
            self._perform_checks()
            threading.Timer(self.check_interval, self.run).start()


    def _perform_checks(self):
        """
        Method responsible for creating checks
        """
        response = self.make_request()
        if response == None:
            return
        response_time = response.elapsed #as a time delta value
        response_time = response_time.total_seconds() #as a float, in seconds
        insert_check((self.url, dt.now(), response_time, response.status_code, None))


    def make_request(self):
        """
        Method used to perform actual request to the server.
        :return: If successful returns requests, as Response object, otherwise None
        If return is None, creates Webcheck containing error message, and prints the message
        """
        try:
            response = requests.get(self.url)
        except requests.exceptions.RequestException as e:
            insert_check((self.url, dt.now(), 0, None, e))
            print("Error %s for website %s at %s" % (str(e[:20]), self.url, dt.now().strftime("%H:%M:%S, %D-%M-%Y")))
            return None
        else:
            return response
