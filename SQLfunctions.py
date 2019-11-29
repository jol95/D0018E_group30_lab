import MySQLdb

# MYSQL settings
mysql_host = 'localhost'
mysql_user = 'root'
mysql_pw = 'Choss!95'
mysql_db = 'webshop'

# Open connection to database
mysql = MySQLdb.connect(mysql_host, mysql_user, mysql_pw, mysql_db)

# This function returns all contents of a table.
#def getTable(table, mysql):
def getTable(table):
    query = 'SELECT * FROM '+table
    cur = mysql.cursor()
    cur.execute(query)
    result = cur.fetchall() # saves all rows in tuples
    cur.close()
    return result

# Get row from table with specific condition
def getRow(table, condition):
    query = 'SELECT * FROM '+table+' where '+condition
    cur = mysql.cursor()
    cur.execute(query)
    result = cur.fetchone() # saves all attributes for condition row
    cur.close()
    return result

# INNER JOIN FUNCTION
def innerJoin(table, attr, join, condition):
    # check if condition is set
    query = 'SELECT '+attr+' FROM '+join
    if condition:
        query = 'SELECT '+attr+' FROM ('+table+' INNER JOIN '+join+') WHERE '+condition
    cur = mysql.cursor()
    cur.execute(query)
    result = cur.fetchall()
    cur.close()
    return result


# Insert row into a table with sepcified attributes
def insertTo(table, attr, values):
    query = 'INSERT INTO '+table+' ('+attr+') VALUES ('+values+')'
    cur = mysql.cursor()
    cur.execute(query)
    mysql.commit()
    cur.close()
    return query

# Update column-value in given table with specified condition
def updateIn(table, column, value, condition):
    query = 'UPDATE '+table+' SET '+column+'='+value+' WHERE '+condition
    cur = mysql.cursor()
    cur.execute(query)
    mysql.commit()
    cur.close()
    return query

# Update row in given table and columns with specified condition
def updateAll(table, update, condition):
    query = 'UPDATE '+table+' SET '+update+' WHERE '+condition
    cur = mysql.cursor()
    cur.execute(query)
    mysql.commit()
    cur.close()
    return query

# delete from given tabel with specified condition
def deleteFrom(table, condition):
    query = 'DELETE FROM '+table+' WHERE '+condition
    cur = mysql.cursor()
    cur.execute(query)
    mysql.commit()
    cur.close()
    return query


# Check if post exists in given table based on condition
def exist(table, condition):
    res = getRow(table, condition)
    if res:
        return True
    else:
        return False
