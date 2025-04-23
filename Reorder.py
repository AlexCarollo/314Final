import mysql.connector
from mysql.connector import errorcode

def reorder(store_id):
    '''
    The Reorder function...
        param: store_id - int identifying the store that is reordering
        return: void
    '''

    try:

        # This is how "modern" Python wants programmers to do "finally: close"
        with mysql.connector.connect(user='aajm', password='final314', host='cs314.iwu.edu', database='aajm') as cnx:

            # Same, but now with a cursor for your SQL work
            try:
                with cnx.cursor(buffered=True) as cursor:
                    # Step 1: Check what needs to be reordered
                    reorder_check_statement = (
                        "SELECT `Requested Orders`.request_id FROM `Requested Orders` AS req_id WHERE `Requested Orders`.store_id = %s"
	                    "SELECT "
                    )

                    # Executes the select statement using the store id from the function parameter
                    # cursor.execute(request_order_statement, [store_id])
                    
                    # Step 2: Make the request to reorder the needed products
                    # Each successful AND failed item should be recorded, in order to show what needs to be changed about the order
                    reorder_statement = (
                        
                    )
                cnx.commit()
                
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
            print("The username or password did not work")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)

def main():
    reorder(1)

if __name__ == "__main__":
    main()