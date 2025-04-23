import mysql.connector
from mysql.connector import errorcode
from datetime import datetime, timedelta


def main():

    # Try to open the SQL connection...
    try:

        # This is how "modern" Python wants programmers to do "finally: close"
        with mysql.connector.connect(user='aajm', password='final314', host='cs314.iwu.edu', database='aajm') as cnx:

            # Same, but now with a cursor for your SQL work
            try:
                with cnx.cursor(buffered=True) as cursor:

                    store_c = 0

                    # while loop to select which stores reorder request we are looking at for inventory updates
                    #to test the code use store_id 50
                    while store_c != 1:

                        store = int(input('Type the store ID of your location'))

                        store_check = cursor.execute('SELECT Shipments.store_id FROM Shipments JOIN `Reorder Requests` ON Shipments.store_id = `Reorder Requests`.store_id ' 
                                                                'WHERE Shipments.store_id = %s AND `Reorder Requests`.order_status != "Complete" ', [store])
                        result = cursor.fetchone()

                        #checks if the store entered has a shipment currently
                        if result is not None:
                            store_c = 1

                        else:
                            print('store does not have a shipment, enter another one')



                    shipmentq = cursor.execute('SELECT Shipments.request_id FROM Shipments WHERE store_id = %s',[store])
                    results_q = cursor.fetchall()

                    #for loop that checks if a product has been received that was requested by another store
                    for row in results_q:
                        listCheck = cursor.execute('SELECT store_id FROM `Reorder Requests` where request_id = %s', [row[0]])
                        resultLc = cursor.fetchone()

                        #print(resultLc)

                        #if the shipment's store_id on a shipment was sent to a place thar does not match with its request in the 'Reorder Request' table
                        # then it prompts and error message and give instructions on what to do
                        if resultLc[0] != store:
                            print("Shipment with request_id", row[0]," was sent to the wrong store and needs to be sent to store ID", resultLc[0], '\t', "Starting reroute to correct store")

                            cursor.execute('UPDATE Shipments SET store_id = %s WHERE store_id = %s', [resultLc[0], row[0]])
                            cursor.execute('UPDATE `Reorder Requests` SET order_status = "Rerouted" WHERE request_id = %s', [row[0]] )

                    #list of the ship_id and request_id that has to do with the chosen store
                    shipmentShip = cursor.execute('SELECT ship_id, request_id FROM Shipments WHERE store_id = %s',
                                               [store])
                    resultShip = cursor.fetchall()

                    #for loop to check if a shipment has given a product that was not requested
                    for row in resultShip:

                        #collects the UPC of each table to check if there are any differences between them and deal with them accordingly
                        UPC_s = cursor.execute('SELECT UPC FROM `Shipped Product` WHERE ship_id = %s', [row[0]])
                        resultUPC_s = cursor.fetchone()

                        UPC_r = cursor.execute('SELECT UPC FROM `Requested Product` WHERE request_id = %s', [row[1]])
                        resultUPC_r = cursor.fetchone()

                        if resultUPC_s[0] != resultUPC_r[0]:

                            phoneV = cursor.execute('SELECT Vendor.phone_number FROM Vendor JOIN Shipments ON Vendor.vend_id = Shipments.vend_id '
                                                    'WHERE Shipments.request_id = %s AND ship_id = %s ',[row[1], row[0]] )
                            phone = cursor.fetchone()

                            print('The following shipment id has given us the wrong product ',resultUPC_s[0],' instead of ', resultUPC_r[0],':', row[0] ,'\t',
                                  'Call the following number to send the shipment back', phone)
                            cursor.execute('UPDATE `Reorder Requests` SET order_status = "Reorder" WHERE request_id = %s', [row[1]])

                    #checks and updates inventory based on if we have an over fill of a product or were given less than we requested.
                    for row in resultShip:

                        # collects the UPC and quantity of each table to check if there are any differences between them and deal with them accordingly
                        quantity_s = cursor.execute('SELECT quantity,UPC FROM `Shipped Product` WHERE ship_id = %s', [row[0]])
                        resultQ_s = cursor.fetchone()

                        quantity_r = cursor.execute('SELECT quantity,UPC FROM `Requested Product` WHERE request_id = %s', [row[1]])
                        resultQ_r = cursor.fetchone()

                        if resultQ_s[0] > resultQ_r[0]:

                            print('The following shipment id has given us over the requested amount of the product', resultQ_s[1],':', row[0], '\t',
                                  'Make sure to find space for the overflow of the product')

                            product_size = cursor.execute('SELECT product_size FROM Product WHERE UPC = %s ', [resultQ_s[1]])
                            productS = cursor.fetchone()

                            invSpace_new = productS[0] * resultQ_s[0]

                            product_inv = cursor.execute('SELECT inv_space FROM Inventory WHERE store_id = %s and UPC = %s ', [store, resultQ_s[1]])
                            productInv = cursor.fetchone()

                            #print(productInv[0])

                            # used to make sure we are adding to the old inventory space and not replacing it
                            invSpace = invSpace_new + productInv[0]

                            #print(invSpace)

                            date = datetime.now()
                            dateComplete = date.strftime("%Y-%m-%d")

                            #print(dateComplete)

                            cursor.execute('UPDATE Inventory SET inv_space = %s ', [invSpace])
                            cursor.execute('UPDATE `Reorder Requests` SET order_status = "OverFill", reorder_received_date = %s WHERE request_id = %s ',
                                           [dateComplete, row[1]])


                        if resultQ_s[0] < resultQ_r[0]:

                            print('The following shipment id has given us under the requested amount of the product', resultQ_s[1],':', row[0], '\t',
                                  'Make sure the vendor sends the rest of it in a future shipment')

                            product_size = cursor.execute('SELECT product_size FROM Product WHERE UPC = %s ', [resultQ_s[1]])
                            productS = cursor.fetchone()

                            invSpace_new = productS[0] * resultQ_s[0]

                            product_inv = cursor.execute('SELECT inv_space FROM Inventory WHERE store_id = %s and UPC = %s ', [store, resultQ_s[1]])
                            productInv = cursor.fetchone()

                            #print(productInv[0])

                            #used to make sure we are adding to the old inventory space and not replacing it
                            invSpace = invSpace_new + productInv[0]

                            #print(invSpace)

                            date = datetime.now()
                            dateComplete = date.strftime("%Y-%m-%d")

                            #print(dateComplete)

                            cursor.execute('UPDATE Inventory SET inv_space = %s ', [invSpace])
                            cursor.execute('UPDATE `Reorder Requests` SET order_status = "UnderFill", reorder_received_date = %s WHERE request_id = %s ',
                                           [dateComplete, row[1]])

                    shipmentR = cursor.execute('SELECT request_id FROM `Reorder Requests` WHERE store_id = %s and order_status = "Pending" ',
                                                  [store])
                    resultR = cursor.fetchone()

                    #print(resultR)

                    #updates the inventory based on the correct shipments that have arrived at the store with no issues
                    for row in resultR:
                        #print(row)
                        quantity_s = cursor.execute('SELECT quantity,UPC FROM `Shipped Product` JOIN Shipments ON `Shipped Product`.ship_id = Shipments.ship_id '
                                                    'WHERE Shipments.request_id = %s',
                                                    [row])
                        resultQ_s = cursor.fetchone()

                        quantity_r = cursor.execute(
                            'SELECT quantity,UPC FROM `Requested Product` WHERE request_id = %s', [row])
                        resultQ_r = cursor.fetchone()

                        if resultQ_s == resultQ_r:
                            print('The following request id has given the correct shipment, proceed to stock inventory:',row)

                            product_size = cursor.execute('SELECT product_size FROM Product WHERE UPC = %s ',
                                                          [resultQ_s[1]])
                            productS = cursor.fetchone()

                            invSpace_new = productS[0] * resultQ_s[0]

                            product_inv = cursor.execute(
                                'SELECT inv_space FROM Inventory WHERE store_id = %s and UPC = %s ',
                                [store, resultQ_s[1]])
                            productInv = cursor.fetchone()

                            #print(productInv[0])

                            # used to make sure we are adding to the old inventory space and not replacing it
                            invSpace = invSpace_new + productInv[0]

                            #print(invSpace)

                            date = datetime.now()
                            dateComplete = date.strftime("%Y-%m-%d")

                            #print(dateComplete)

                            cursor.execute('UPDATE Inventory SET inv_space = %s ', [invSpace])
                            cursor.execute(
                                'UPDATE `Reorder Requests` SET order_status = "Complete", reorder_received_date = %s WHERE request_id = %s ',
                                [dateComplete, row])


                        #print(resultQ_s)
                        #print(resultQ_r)

                    cnx.commit()
                    cnx.close()



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

    print(cnx is None or not cnx.is_connected())

    print("In theory, the program could do other things here, including loop back and ask the user to try again.")

if __name__ == "__main__":
    main()



