import MySQLdb

# MYSQL settings
mysql_host = 'localhost'
mysql_user = 'root'
mysql_pw = 'Choss!95'
mysql_db = 'webshop'

# This function returns all contents of a table.
def getTable(table):
    query = 'SELECT * FROM '+table
    return fetchall(query)

# Get row from table with specific condition
def getRow(table, condition):
    query = 'SELECT * FROM '+table+' where '+condition
    return fetchone(query)

# Get attributes from specific row
def getOne(table, attr, condition):
    query = 'SELECT '+attr+' FROM '+table+' WHERE '+condition
    return fetchone(query)

# INNER JOIN FUNCTION
def innerJoin(table, attr, join, condition):
    # check if condition is set
    query = 'SELECT '+attr+' FROM ('+table+' INNER JOIN '+join+')'
    if condition:
        query += ' WHERE '+condition
    return fetchall(query)

# LEFT JOIN FUNCTION
def leftJoin(table, attr, join, condition):
    # check if condition is set
    query = 'SELECT '+attr+' FROM ('+table+' LEFT JOIN '+join+')'
    if condition:
        query += ' WHERE '+condition
    return fetchall(query)

# Insert row into a table with sepcified attributes
def insertTo(table, attr, values):
    query = 'INSERT INTO '+table+' ('+attr+') VALUES ('+values+')'
    return commit(query)

# Update column-value in given table with specified condition
def updateIn(table, column, value, condition):
    query = 'UPDATE '+table+' SET '+column+'='+value+' WHERE '+condition
    return commit(query)

# Update row in given table and columns with specified condition
def updateAll(table, update, condition):
    query = 'UPDATE '+table+' SET '+update+' WHERE '+condition
    return commit(query)

# delete from given tabel with specified condition
def deleteFrom(table, condition):
    query = 'DELETE FROM '+table+' WHERE '+condition
    return commit(query)

# get sum of a column
def getSum(**kwargs):
    return fetchone('SELECT SUM({}) FROM {} WHERE {}'.format(kwargs.get('column'),
    kwargs.get('table'), kwargs.get('condition')))

# Check if post exists in given table based on condition
def exist(table, condition):
    res = getRow(table, condition)
    if res:
        return True
    else:
        return False

# fetchone and close
def fetchone(query):
    # Open connection to database
    mysql = MySQLdb.connect(mysql_host, mysql_user, mysql_pw, mysql_db)
    cur = mysql.cursor()
    cur.execute(query)
    res = cur.fetchone()
    cur.close()
    mysql.close()
    return res

# fetchall and close
def fetchall(query):
    # Open connection to database
    mysql = MySQLdb.connect(mysql_host, mysql_user, mysql_pw, mysql_db)
    cur = mysql.cursor()
    cur.execute(query)
    res = cur.fetchall() # saves all rows in tuples
    cur.close()
    mysql.close()
    return res

# commit and close
def commit(query):
    # Open connection to database
    mysql = MySQLdb.connect(mysql_host, mysql_user, mysql_pw, mysql_db)
    cur = mysql.cursor()
    cur.execute(query)
    mysql.commit()
    cur.close()
    mysql.close()
    return query

# checkout cart function using transaction
def checkoutcart(**kwargs):
    # Open connection to database
    mysql = MySQLdb.connect(mysql_host, mysql_user, mysql_pw, mysql_db)
    # disable autocommit
    mysql.autocommit(False)
    # initiate cursor
    cur = mysql.cursor()
    # transaction status
    success = False

    try:
        # check if orders exist in ordertable
        orders = fetchone('SELECT COUNT(orderID) FROM `orders`')[0]
        if orders:
            # get order number
            orderno = fetchone('SELECT `orderID` FROM `orders` ORDER BY orderID DESC LIMIT 1')[0]+1
        else:
            orderno = 60000     # startnumber for order table

        # create order
        cur.execute('INSERT INTO orders (`custID`, `status`, `amount`, `orderID`) VALUES({}, 0, 0, {})'.format(
            kwargs.get('custno'),
            orderno
        ))

        # move cart to orderlines
        lineno = 1  # startnumber for each order
        cartamount = 0  # order amount
        for post in kwargs.get('cart'):
            # insert cart row into order row
            cur.execute('INSERT INTO orderln (`orderID`, `lineno`, `prodID`, `qty`, `price`, `discount`)\
                VALUES ({}, {}, {}, {}, {}, {})'.format(
                    orderno,
                    lineno,
                    post[0],
                    str(post[4]),
                    str(post[2]),
                    str(post[3])
                ))
            # increase order_qty in product table
            cur.execute('UPDATE products SET order_qty=order_qty+{} WHERE prodID={}'.format(
                str(post[4]),
                post[0]
            ))
            lineno+=1   # increase line number
            cartamount += post[2]*(100-post[3])/100*post[4] # calculate total order amount

        # insert cart amount to order amount
        cur.execute('UPDATE orders SET amount={} WHERE orderID={}'.format(
            str(cartamount),
            orderno
        ))

        # delete the cart once moved to order
        cur.execute('DELETE FROM cart WHERE custID={}'.format(
            kwargs.get('custno')
        ))

        # commit changes
        mysql.commit()

        # set transaction status succeed
        success = True

    except mysql.Error as error:
        print('Failed to update record to database rollback: {}'.format(error))
        # rollback changes because of exception
        mysql.rollback()
    finally:
        # closing database connection
        cur.close()
        mysql.close()
        return success


# order confirm function using transaction
def confirm_order(**kwargs):
    ordno = kwargs.get('orderno')
    ordlns = kwargs.get('orderlns')
    success = False

    # Open connection to database
    mysql = MySQLdb.connect(mysql_host, mysql_user, mysql_pw, mysql_db)
    # disable autocommit
    mysql.autocommit(False)
    # initiate cursor
    cur = mysql.cursor()
    # transaction status
    success = False

    try:
        for ordln in ordlns:
            item = ordln
            confirm_qty = ordlns.get(item)
            # confirm qty. for each item
            cur.execute('UPDATE orderln SET confirmed_qty={} WHERE orderID={} AND \
                prodID={}'.format(confirm_qty, ordno, item))
            # update the stock, order_qty and sold_qty for each item
            cur.execute('UPDATE products SET stock=stock-{0}, order_qty=order_qty-{0}, \
                sold_qty=sold_qty+{0} WHERE prodID={1}'.format(
                confirm_qty,
                item
            ))
            # update orderstatus to "confirmed"
            cur.execute('UPDATE orders SET status=1 WHERE orderID={}'.format(ordno))
        
        # commit changes
        mysql.commit()

        # set transaction status succeed 
        success = True
    except mysql.Error as error:
        print('Failed to update record to database rollback: {}'.format(error))
        # rollback changes because of exception
        mysql.rollback()
    finally:
        # closing database connection
        cur.close()
        mysql.close()
        return success

# delete order with transactions (only for order under process)
def deleteOrder(**kwargs):
    # Open connection to database
    mysql = MySQLdb.connect(mysql_host, mysql_user, mysql_pw, mysql_db)
    # disable autocommit
    mysql.autocommit(False)
    # initiate cursor
    cur = mysql.cursor()
    # transaction status
    success = False

    try:
        orderno = kwargs.get('ordno')
        orderstatus = fetchone('SELECT status from orders WHERE orderID={}'.format(orderno))[0]
        orderlns = fetchall('SELECT * FROM orderln WHERE orderID={}'.format(orderno))
        print(orderstatus)
        if orderstatus != 0:
            raise mysql.Error
        
        # delete from orderlns and decrease order_qty in products
        for orderln in orderlns:
            item = orderln[3]
            qty = orderln[4]
            cur.execute('UPDATE products SET order_qty=order_qty-{} WHERE prodID={}'.format(
                qty, item
            ))
        cur.execute('DELETE FROM orderln WHERE orderID={}'.format(orderno))

        # delete order from order table
        cur.execute('DELETE FROM orders WHERE orderID={}'.format(orderno))

        # commit changes
        mysql.commit()

        # set transaction status succeed
        success = True

    except mysql.Error as error:
        print('Failed to update record to database rollback: {}'.format(error))
        # rollback changes because of exception
        mysql.rollback()
    finally:
        # closing database connection
        cur.close()
        mysql.close()
        return success