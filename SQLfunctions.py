# This function returns all contents of a table.
def getTable(table, mysql):
    query = 'SELECT * FROM '+table
    cur = mysql.connection.cursor()
    cur.execute(query)
    result = cur.fetchall() # saves all rows in tuples
    cur.close()
    return result

# Get row from table with specific condition
def getRow(table, condition, mysql):
    query = 'SELECT * FROM '+table+' where '+condition
    cur = mysql.connection.cursor()
    cur.execute(query)
    result = cur.fetchall() # saves all attributes for condition row
    cur.close()
    return result

# Insert row into a table with sepcified attributes
def insertTo(table, attr, values, mysql):
    query = 'INSERT INTO '+table+' ('+attr+') VALUES ('+values+')'
    cur = mysql.connection.cursor()
    cur.execute(query)
    mysql.connection.commit()
    cur.close()
    return query
