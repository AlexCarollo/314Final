import mysql.connector
from mysql.connector import errorcode

def online_order():
    # Try to open the SQL connection...
    try:

        # This is how "modern" Python wants programmers to do "finally: close"
        with mysql.connector.connect(user='aajm', password='final314', host='cs314.iwu.edu', database='aajm') as cnx:

            # Same, but now with a cursor for your SQL work
            try:
                with cnx.cursor(buffered=True) as cursor:       
                    #Failure cases should be in DMs with jimmy
                    
                    # Step 1: Compile info of customer, store, inventory, and not ordered yet
                    # List index breakdown: 0: name, 1: cart id, 2: customer id, 3: store id, 4: UPC, 5: product name, 6: quantity, 7: inventory quantity, 8: order processed,
                    select_statement = ("SELECT cust_name, "
	                    "cart_id, `Customer Cart`.cust_id, `Customer Cart`.store_id, `Customer Cart`.UPC, product_name, prod_quantity, "
                        "inv_space, order_processed FROM `aajm`.`Customer Cart` "
	                    "JOIN Customer ON `Customer Cart`.cust_id = `Customer`.cust_id "
                        "JOIN Inventory ON `Customer Cart`.UPC = `Inventory`.UPC "
                        "JOIN Product ON `Customer Cart`.UPC = Product.UPC "
                        # Note that this where clause skips over any already processed order in the cart.
                        "WHERE `Customer Cart`.store_id = `Inventory`.store_id AND `Customer Cart`.cust_id = %s AND order_processed = 0;")
                    
                    print("What is the ID of the customer currently ordering?")
                    curr_customer = input()
                    # Break out of function if the input is incorrect
                    if curr_customer is not int:
                        print("Invalid customer!")
                        cnx.rollback()
                        return
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
                        if(row[6] <= row[7]):
                            successes.append(row)
                        else:
                            failures.append(row)

                        row = row = cursor.fetchone()
                    
                    # Updates all orders in the current customer's cart to be marked as processed.
                    cursor.execute("UPDATE `Customer Cart` SET order_processed = 1 WHERE cust_id = %s", [curr_customer])    
                    
                    # Success/failure print testing.
                    print("Successes: ")
                    for item in successes:
                        print(item)
                    print()
                    print("Failures: ")
                    for item in failures:
                        print(item) 
                    print()
                    
                    #Step 3: If all items checks were successful, print success message to console. Reduce quantity of each item in inventory.
                    if len(failures) == 0:
                        # Edge case for empty cart
                        if len(successes) == 0:
                            print("Your cart is empty!")
                        else:
                            for item in successes:
                                new_inventory = item[7] - item[6]
                                # Update inventory of store.
                                cursor.execute("UPDATE `Inventory` SET inv_space = %s WHERE store_id = %s AND UPC = %s;", 
                                            [new_inventory, item[3], item[4]])
                                # Update customer's cart to have a success message.
                                cursor.execute("UPDATE `Customer Cart` SET order_feedback = 'Purchase Successful!' WHERE cart_id = %s AND cust_id = %s",
                                            [item[1], item[2]])
                            print("Order placed!")
                    
                    #Step 4: If failure, tell which items are causing the order to fail. Next, check if any stores in the same state have the inventory
                    else:
                        for item in successes:
                            cursor.execute("UPDATE `Customer Cart` SET order_feedback = 'Order failed due to another product.' WHERE cart_id = %s AND cust_id = %s",
                                           [item[1], item[2]])
                        
                        # Create and print a list of the items that caused the purchase to fail.
                        bad_items = []
                        for item in failures:
                            bad_items.append(item[5])
                        print("Purchase failed due to the following products:", bad_items)
                        
                        # Iterate through the failed purchases and give alternative locations if available.
                        for item in failures:
                            cursor.execute("SELECT `state` FROM `BMart Address` WHERE store_id = %s;", [item[3]])
                            s = cursor.fetchone()
                            state = s[0]
                            #print(state[0])

                            #List index breakdown: 0: store id, 1: city, 2: state, 3: inventory space, 4: upc
                            cursor.execute("SELECT `BMart Address`.store_id, city, `state`, inv_space, UPC from `BMart Address` "
	                                        "JOIN Inventory ON `BMart Address`.store_id = Inventory.store_id "
                                            "WHERE UPC = %s AND state = %s;", [item[4], state])
                            
                            # Compiles a list of alternative stores in the same state that carry enough of the requested product.
                            alt_stores = []
                            newrow = cursor.fetchone()
                            while newrow is not None:
                                if item[6] < newrow[3]:
                                    alt_stores.append(newrow[1])
                                newrow = newrow = cursor.fetchone()

                            if len(alt_stores) == 0:
                                print("There are no stores in", state, "that carry", item[6], item[5])
                            else:
                                print("You can purchase", item[6], item[5], "at the", alt_stores, "location(s).")

                        # Adds feedback for each failed purchase within the database itself. Done in a seperate for loop to prevent errors.
                        for item in failures:
                            cursor.execute("UPDATE `Customer Cart` SET order_feedback = 'Order failed: not enough inventory' WHERE cart_id = %s AND cust_id = %s",
                                           [item[1], item[2]])
                            
                # Once the online order is fully processed, commit the changes to the database.
                #cnx.commit()
                
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
    
def main():
    online_order()

if __name__ == "__main__":
    main()