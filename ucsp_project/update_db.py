import sqlite3

conn = sqlite3.connect("ucsp.db")
cur = conn.cursor()

print("Updating Database...")

# ---------- Complaints table columns ----------
columns = [
    ("name", "TEXT"),
    ("department", "TEXT"),
    ("date", "TEXT"),
    ("location", "TEXT")
]

for column, dtype in columns:
    try:
        cur.execute(f"ALTER TABLE complaints ADD COLUMN {column} {dtype}")
        print(f"Column '{column}' added")
    except:
        print(f"Column '{column}' already exists")


# ---------- Legal Cases table ----------
cur.execute('''
CREATE TABLE IF NOT EXISTS legal_cases(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    case_number TEXT,
    name TEXT,
    case_type TEXT,
    description TEXT,
    status TEXT
)
''')
print("Table 'legal_cases' checked")
# ---------- Add user_email to legal_cases ----------
try:
    cur.execute("ALTER TABLE legal_cases ADD COLUMN user_email TEXT")
    print("Column 'user_email' added to legal_cases")
except:
    print("Column 'user_email' already exists in legal_cases")


# ---------- Agents table ----------
cur.execute('''
CREATE TABLE IF NOT EXISTS agents(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    department TEXT
)
''')
print("Table 'agents' checked")


# ---------- Default Agents ----------
agents = [
    ("Police Officer", "police@ucsp.com", "123", "Police"),
    ("Grievance Officer", "grievance@ucsp.com", "123", "Grievance"),
    ("Legal Officer", "legal@ucsp.com", "123", "Legal")
]

for agent in agents:
    try:
        cur.execute(
            "INSERT OR IGNORE INTO agents(name,email,password,department) VALUES(?,?,?,?)",
            agent
        )
    except:
        pass

print("Default agents added/checked")



# ---------- Commit ----------
conn.commit()
conn.close()

print("Database Updated Successfully!")