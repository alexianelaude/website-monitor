import sqlite3
from db import DATABASE_NAME

def create_db():
    conn = sqlite3.connect(DATABASE_NAME)
    cursor = conn.cursor()
    print("Opened database successfully")

    cursor.execute('''CREATE TABLE USER 
             ( USERNAME TEXT PRIMARY KEY NOT NULL
             );''')
    print("User table created successfully")

    cursor.execute('''CREATE TABLE WEBSITE 
                 (
                 URL       TEXT   NOT NULL,
                 USER TEXT NOT NULL,
                 INTERVAL        FLOAT,
                 DOWN INTEGER ,
                 PRIMARY KEY (URL, USER)
                 )''')
    print("Website table created successfully")

    cursor.execute('''CREATE TABLE WEBCHECK 
                     (ID INTEGER PRIMARY KEY  AUTOINCREMENT,
                     URL       VARCHAR  NOT NULL,
                     REQUESTTIME  VARCHAR(20) ,
                     RESPONSETIME FLOAT ,
                     STATUS INTEGER,
                     ERROR TEXT DEFAULT NULL     
                     )''')
    print("Webcheck table created successfully")

    cursor.execute('''CREATE TABLE ALERT 
                     (ID INTEGER PRIMARY KEY  AUTOINCREMENT,
                     URL       VARCHAR  NOT NULL,
                     USER TEXT NOT NULL,
                     TIME   VARCHAR (20),
                     DOWN INTEGER,
                     AVAILABILITY FLOAT
                     )''')
    print("Alert table created successfully")
    conn.commit()
    conn.close()

create_db()
print("Database initialization succeeded")