import sqlite3
def dbselect(query, payload):
	"""Return result of query from database."""
	connection = sqlite3.connect('Gradget.db')
	cursorObj = connection.cursor()
	if not payload:
	    rows = cursorObj.execute(query)
	else:
	    rows = cursorObj.execute(query,payload)
	results = []
	for row in rows:
	    results.append(row)
	cursorObj.close()
	return results

def change_db(command, payload=None):
    """Execute command (with given payload, if any) in given database."""
    connection = sqlite3.connect('Gradget.db')
    cursor = connection.cursor()
    cursor.execute(command, payload)
    connection.commit()
    connection.close()