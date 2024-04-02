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
        name TEXT,
        spin INTEGER
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

# Insert sample data into Employees table
c.execute("INSERT INTO Employees (name, spin) VALUES ('John Doe', 1)")
c.execute("INSERT INTO Employees (name, spin) VALUES ('Jane Doe', 2)")

# Get the ids of the inserted employees
john_id = c.lastrowid
c.execute("INSERT INTO Employees (name, spin) VALUES ('Jane Doe', 2)")
jane_id = c.lastrowid

# Insert sample data into Skills table
c.execute(f"INSERT INTO Skills (skill_name, employee_id) VALUES ('Python', {john_id})")
c.execute(f"INSERT INTO Skills (skill_name, employee_id) VALUES ('Java', {jane_id})")

# Commit the changes and close the connection
conn.commit()
conn.close()