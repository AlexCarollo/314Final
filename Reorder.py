import mysql.connector
from mysql.connector import errorcode
from datetime import datetime, timedelta

def reorder(store_id):
    '''
    The Reorder function will check if there is inventory that needs to be reordered,
    then it will reorder it accordingly
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
                    check_inv = (
                        "SELECT Inventory.UPC, inv_space, max_inv_space, vend_id FROM Inventory"
                        "JOIN Product ON Product.UPC = Inventory.UPC"
                        "JOIN Brand ON Product.brand = brand_name"
                        "WHERE store_id = %s;"
                    )

                    # Executes the check for inventory
                    cursor.execute(check_inv, [store_id])

                    success = []
                    fail = []
                    row = cursor.fetchone()
                    # Sorts all items in a cart based on whether the quantity a customer is ordering is less than that store's inventory
                    while row is not None:
                        if(row[1] == row[2]):
                            success.append(row)
                        else:
                            fail.append(row)

                        row = row = cursor.fetchone()
                    
                    print(success)
                    
                    # Step 2: Make the request to reorder the needed products
                    # Each successful AND failed item should be recorded, in order to show what needs to be changed about the order
                    fetch_current_reorders = (
                        "SELECT Reorder Requests.request_id, Requested Product.UPC, Requested Product.quantity FROM Reorder Requests"
                        "JOIN Requested Product ON Reorder Requests.request_id = Requested Product.request_id"
                        "WHERE Reorder Requests.order_status = 'Pending' AND store_id = %s;"
                    )

                    cursor.execute(fetch_current_reorders, [store_id])

                    fetch_current_shipments = (
                        "SELECT Shipments.ship_id, Shipped Product.UPC, Shipped Product.quantity FROM Shipments"
                        "JOIN Shipped Product ON Shipments.ship_id = Shipped Product.ship_id"
                        "JOIN Reorder Requests ON Shipments.request_id = Reorder Requests.request_id"
                        "WHERE Reorder Requests.reorder_received_date = NULL AND Shipments.store_id = %s;"
                    )

                    cursor.execute(fetch_current_shipments)

                    date = datetime.now()
                    dateComplete = date.strftime("%Y-%m-%d")

                    add_reorder = (
                        "INSERT INTO Reorder Requests (order_status, order_seen, reorder_date, reorder_received_date, store_id, vendor_id)"
                        "VALUE ('Pending', 0, %s, NULL, %s, %s)"
                    )

                # cnx.commit()
                
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