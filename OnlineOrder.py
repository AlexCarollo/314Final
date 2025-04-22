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
                    #Failure cases should be in DMs with jimmy
                    
                    # Step 1: Compile info of customer, store, inventory, and not ordered yet
                    
                    # List index breakdown: 0 name, 1 cart id, 2 customer id, 3 store id, 4 UPC, 5 quantity, 6 inventory quantity, 7 order processed 
                    select_statement = ("SELECT cust_name, "
	                    "cart_id, `Customer Cart`.cust_id, `Customer Cart`.store_id, `Customer Cart`.UPC, prod_quantity, "
                        "inv_space, order_processed FROM `aajm`.`Customer Cart` "
	                    "JOIN Customer ON `Customer Cart`.cust_id = `Customer`.cust_id "
                        "JOIN Inventory ON `Customer Cart`.UPC = `Inventory`.UPC "
                        "WHERE `Customer Cart`.store_id = `Inventory`.store_id AND `Customer Cart`.cust_id = %s AND order_processed = 0;")
                    
                    curr_customer = 1
                    # Executes the select statement on the customer with id curr_customer
                    cursor.execute(select_statement, [curr_customer])
                    
                    # Step 2: Attempt to order - succeed if quantity of each items <  quantity of each item in inventory
                    # Each successful AND failed item should be recorded, in order to show what needs to be changed about the order
                    
                    # Lists to keep track of what products can and cannot be purchased
                    successes = []
                    failures = []
                    row = cursor.fetchone()
                    # Sorts all items in a cart based on whether the quantity a customer is ordering is less than that store's inventory
                    while row is not None:
                        print(row)
                        if(row[5] <= row[6]):
                            successes.append(row)
                        else:
                            failures.append(row)

                        # Updates the row to "processed" in the database. Line causes error for some reason???
                        # cursor.execute("UPDATE `Customer Cart` SET order_processed = 1 WHERE cart_id = %s", [row[1]])
                        row = row = cursor.fetchone()
                        
                    print("Successes: ")
                    for item in successes:
                        print(item)
                    print()
                    
                    print("Failures: ")
                    for item in failures:
                        print(item) 
                    
                    #Step 4: If success, print success message to console. Reduce quantity of each item in inventory
                    if len(failures) == 0:
                        for item in successes:
                            new_inventory = item[6] - item[5]
                            # Update inventory of store.
                            cursor.execute("UPDATE `Inventory` SET inv_space = %s WHERE store_id = %s AND UPC = %s;", 
                                           [new_inventory, item[3], item[4]])
                            # Update customer's cart to have a success message.
                            cursor.execute("UPDATE `Customer Cart` SET order_feedback = 'Purchase Successful!' WHERE cart_id = %s AND cust_id = %s",
                                           [item[1], item[2]])
                    
                    #Step 4: If failure, tell which items are causing the order to fail. Next, check if any stores in the same state have the inventory
                    else:
                        for item in successes:
                            cursor.execute("UPDATE `Customer Cart` SET order_feedback = 'Order failed due to another product.' WHERE cart_id = %s AND cust_id = %s",
                                           [item[1], item[2]])
                        
                        for item in failures:
                            pass
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
                    
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