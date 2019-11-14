# This function returns contents of a table.
def getTable(table, mysql):
    query = 'SELECT * FROM '+table
    cur = mysql.connection.cursor()
    cur.execute(query)
    result = cur.fetchall() # saves all rows in tuples
    cur.close()
    return result

def getRow(table, condition, mysql):
    query = 'SELECT * FROM '+table+' where '+condition
    cur = mysql.connection.cursor()
    cur.execute(query)
    result = cur.fetchall() # saves all attributes for condition row
    cur.close()
    return result