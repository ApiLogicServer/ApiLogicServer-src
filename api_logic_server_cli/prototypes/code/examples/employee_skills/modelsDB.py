import sqlite3

# Connect to the SQLite database
# If the database does not exist, it will be created
conn = sqlite3.connect('employees_skills.db')

# Create a cursor object
c = conn.cursor()

# Create Employees table
c.execute('''
    CREATE TABLE Employees (
        id INTEGER PRIMARY KEY,
        name TEXT
    )
''')

# Create Skills table
c.execute('''
    CREATE TABLE Skills (
        id INTEGER PRIMARY_KEY,
        skill_name TEXT,
        employee_id INTEGER,
        FOREIGN KEY(employee_id) REFERENCES Employees(id)
    )
''')

# Commit the changes and close the connection
conn.commit()
conn.close()