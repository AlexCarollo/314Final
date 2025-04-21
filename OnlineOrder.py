import mysql.connector
from mysql.connector import errorcode

def main():

    # Try to open the SQL connection...
    try:

        # This is how "modern" Python wants programmers to do "finally: close"
        with mysql.connector.connect(user='aajm', password='final314', host='cs314.iwu.edu', database='aajm') as cnx:

            # Same, but now with a cursor for your SQL work
            try:
                with cnx.cursor() as cursor:
                    cursor.execute('SELECT * FROM Bmart')

            # This code should handle any issues DURING SQL work.
            except mysql.connector.Error as err:
                print('Error while executing', cursor.statement, '--', str(err))

                # If some part of our SQL queries errored, explicitly rollback all of them
                # to "reset" the database back to its original state. Only needed for SQL
                # queries that alter the database.
                cnx.rollback()

        # Any additional Python work that doesn't require the database, but does need the database data, can be
        # performed here.
        
    # Connection errors handled here, with explicit handling for different types of errors.
    except mysql.connector.Error as err:

        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
            
    #print(cnx is None or not cnx.is_connected())

    print("In theory, the program could do other things here, including loop back and ask the user to try again.")

if __name__ == "__main__":
    main()
