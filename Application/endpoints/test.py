import pymysql

# Connect to MySQL
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="#1Krishna",
    database='chatbot_db'
)

cursor = conn.cursor()

# Fetch table schema
cursor.execute("DESCRIBE property_data")
schema = cursor.fetchall()

# Print table schema
print("Database Schema:\nDatabase: Conversations\nTable:chatbot_db\nColumns:")
for column in schema:
    col_name, col_type, _, _, _, _ = column
    print(f"        - {col_name} {col_type},")

cursor.close()
conn.close()
