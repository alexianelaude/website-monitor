#Website monitoring console program - Alexiane Laude

##Documentation:
Start by installing the packages from the requirements.txt file
Then, run "python setup.py" to initialize the database

You can then start the app by running "python run.py youUsername" (the username is required for all options, if the user can't be found in the database, you will have the possibility to create it)
You can add a website using the -w option, the "http://" is not mandatory in the url
You can delete a website using the -d option
You can list all the user's websites using the -l option
To quit the app, press "Ctrl + C"
In case of a curses.error, make the terminal window wider

Metrics computed are : availability, average and max response time, dictionnary of the responses status. Error raised by requests are printed on screen until the next refresh (<10s). Metrics are computed over the past 2 minutes, ten minutes (refreshed every 10s) and hour (refreshed every minute).

Every website check is saved in the database, and retrieved to calculate metrics
Every 10s, the database is purged of every Webcheck created more than an hour ago

Alerts are listed on the right side of the screen. All alerts are shown, including those raised during a previous run of the app. Alerts of websites which were deleted are also deleted.
Alerts are created if a website availability is under 80% for over 2 minutes (or over 80% for websites who are initially "down")
If the program has just been restarted, or if the website has just been created, the alert is launched only after a little less than 2 minutes of collecting data.  

##Things to improve:

I only computed the basic metrics suggested by the project's subject, because I didn't know what other metrics could be relevant, using only http requests to the webpage. An improved version could include other metrics, perhaps using the response's history (and checking for redirections), or by using different methods, like post or head.

The handling of requests errors should be improved: for now they are only printed for a very short period of time (<10s), and at the bottom of the screen. The same error raised by successive requests is printed for every webcheck, which quickly overloads the screen. It would be preferable to print errors under each website, and not to print duplicate errors. 

The overall human-machine interface could also be improved, in particular it would be best if websites could be created or deleted while the app is running.

Finally, the app could also be improved by diplaying the stats in the form of graphs, given that we collect and store data continuously. 

