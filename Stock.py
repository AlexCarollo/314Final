import mysql.connector
from mysql.connector import errorcode

def get_connection() -> mysql.connector.connection:
    #Try to open the SQL connection:
    try:
        cnx = mysql.connector.connect(user='aajm', password='final314', host='cs314.iwu.edu', database='aajm')
    
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            raise mysql.connector.Error("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            raise mysql.connector.Error("Database does not exist")
        else:
            raise mysql.connector.Error(err)

    return cnx 