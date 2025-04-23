import mysql.connector
from mysql.connector import errorcode
from datetime import date
from typing import List, Dict


def shipment(
        store_id: int,
        vend_id: int,
        delivery_date: date,
        reorders: List[int],
        shipment_items: Dict[int, Dict[str, int]]
):
    """
    Record one or more shipments fulfilling BMart reorder requests.

    Parameters
    ----------
    store_id: int
    The BMart.store_id to which these shipments are headed.
    vend_id: int
    The Vendor.vend_id who is fulfilling these requests.
    delivery_date: date
    The date the shipment is sent (goes into Shipments.date_sent).
    reorders: list of int
    A list of Reorder Requests.request_id values that this shipment is fulfilling.
    shipment_items: dict
    A mapping from each request_id to another dict of UPC->quantity shipped

    Purpose
    --------
    1. Validates that each request_id exists, belongs to (store_id, vend_id) and is not yet shipped.
    2. Computes total_price = sum(qty * Product.unit_price).
    3. For each request_id:
    INSERT a row into Shipments
    INSERT rows into hipped Product
    UPDATE Reorder Requests to set order_status='shipped' and order_seen=1
    4. f error occurs, rolls back and prints an error message
    5. When successful, commits and then prints a shipping manifest, list of fulfilled request_ids, outstanding reorder counts for this store and for this vendor.
    """
    try:
        cnx = mysql.connector.connect(
            user='aajm',
            password='final314',
            host='cs314.iwu.edu',
            database='aajm',
        )
        cursor = cnx.cursor(buffered=True)

        try:
            # Basic check
            if set(reorders) != set(shipment_items.keys()):
                raise ValueError("Mismatch between reorders list and shipment_items keys")

            manifest = []
            fulfilled = []

            # Validates each reorder request
            for req_id in reorders:
                cursor.execute("""
                               SELECT store_id, vendor_id, order_status
                               FROM `Reorder Requests`
                               WHERE request_id = %s
                                   FOR UPDATE
                               """, (req_id,))
                row = cursor.fetchone()
                if not row:
                    raise ValueError(f"Invalid reorder request ID {req_id}!")
                rid_store, rid_vendor, status = row
                if rid_store != store_id:
                    raise ValueError(f"Reorder {req_id} is not for store {store_id}!")
                if rid_vendor != vend_id:
                    raise ValueError(f"Reorder {req_id} is not assigned to vendor {vend_id}!")
                if status.lower() == 'shipped':
                    raise ValueError(f"Reorder {req_id} has already been shipped!")

            # Proceses each reorder as its own shipment
            for req_id in reorders:
                items = shipment_items[req_id]
                total_price = 0
                line_items = []

                #Line totals
                for upc, qty in items.items():
                    cursor.execute(
                        "SELECT unit_price FROM `Product` WHERE UPC = %s", (upc,)
                    )
                    pr = cursor.fetchone()
                    if not pr:
                        raise ValueError(f"Invalid shipment item UPC {upc}!")
                    unit_price = pr[0]
                    total_price += unit_price * qty
                    line_items.append((upc, qty, unit_price))

                #Insert into Shipments
                cursor.execute("""
                               INSERT INTO `Shipments` (total_price, date_sent, store_id, request_id, vend_id)
                               VALUES (%s, %s, %s, %s, %s)""",
                               (total_price, delivery_date, store_id, req_id, vend_id))
                ship_id = cursor.lastrowid

                # Insert into Shipped Product
                for upc, qty, _ in line_items:
                    cursor.execute("""
                                   INSERT INTO `Shipped Product` (UPC, ship_id, quantity)
                                   VALUES (%s, %s, %s)""", (upc, ship_id, qty))

                # Check the request as shipped
                cursor.execute("""
                               UPDATE `Reorder Requests`
                               SET order_status = 'shipped', order_seen   = 1
                               WHERE request_id = %s""", (req_id,))
                manifest.append({
                    'ship_id': ship_id,
                    'request_id': req_id,
                    'items': line_items,
                    'total_price': total_price
                })
                fulfilled.append(req_id)

            # Commit everything
            cnx.commit()

            # Outstanding counts
            cursor.execute("""
                            SELECT COUNT(*)
                            FROM `Reorder Requests`
                            WHERE store_id = %s
                            AND vendor_id = %s
                            AND order_status != 'shipped'
                           """, (store_id, vend_id))
            out_store = cursor.fetchone()[0]
            cursor.execute("""
                            SELECT COUNT(*)
                            FROM `Reorder Requests`
                            WHERE vendor_id = %s
                            AND order_status != 'shipped'
                           """, (vend_id,))
            out_vendor = cursor.fetchone()[0]

            # Print the summary
            print("\nShipment Manifest:")
            for m in manifest:
                print(f"Shipment #{m['ship_id']} -> Reorder #{m['request_id']}:")
                for upc, qty, up in m['items']:
                    print(f"– {upc}: {qty} units at ${up:.2f} each")
                print(f"Total: ${m['total_price']:.2f}\n")

            print("Fulfilled reorder requests:", fulfilled)
            print(f"Outstanding for store {store_id}: {out_store}")
            print(f"Outstanding for vendor {vend_id}: {out_vendor}\n")

        except Exception as e:
            cnx.rollback()
            print("Error during shipment:", e)

        finally:
            cursor.close()
            cnx.close()

    except mysql.connector.Error as db_err:
        if db_err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Database access denied, check your credentials")
        elif db_err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print("Database connection error:", db_err)

