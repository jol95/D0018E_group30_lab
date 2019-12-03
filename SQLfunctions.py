import MySQLdb

# MYSQL settings
mysql_host = 'localhost'
mysql_user = 'root'
mysql_pw = 'Choss!95'
mysql_db = 'webshop'

# Open connection to database
mysql = MySQLdb.connect(mysql_host, mysql_user, mysql_pw, mysql_db)

# settings
mysql.autocommit(False)

# This function returns all contents of a table.
#def getTable(table, mysql):
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
    cur = mysql.cursor()
    cur.execute(query)
    res = cur.fetchone()
    cur.close()
    return res

# fetchall and close
def fetchall(query):
    cur = mysql.cursor()
    cur.execute(query)
    res = cur.fetchall() # saves all rows in tuples
    cur.close()
    return res

# commit and close
def commit(query):
    cur = mysql.cursor()
    cur.execute(query)
    mysql.commit()
    cur.close()
    return query
