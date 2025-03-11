import pymysql
from fastapi import HTTPException
        
def clean_sql_query(sql_query):
    return " ".join(sql_query.replace("```sql", "").replace("```", "").strip().split())

def execute_sql(sql_query):
    try:
        cleaned_query = clean_sql_query(sql_query)
   

        conn = pymysql.connect(
    host="localhost",
    user="root",  
    password="#1Krishna",  
    database="chatbot_db"  
)       
        cursor = conn.cursor()
        cursor.execute(cleaned_query)
        results = cursor.fetchall()
        print(sql_query)
        if results:
            formatted_results = "\n".join([str(row) for row in results])
            return formatted_results
        else:
            return "Query executed successfully, but no results were found."
            
    except pymysql.MySQLError as e:
    
        raise HTTPException( f"MySQL Error: {e}")
    
def get_property_names():
    """Fetches property names from the database, considering both property_name and nick_name."""
    property_names = []
    try:
        connection = pymysql.connect(
    host="localhost",
    user="root",  
    password="#1Krishna",  
    database="chatbot_db"  
)       
        cursor = connection.cursor()

        # SQL query to select both property_name and nick_name
        query = "SELECT property_building, nick_name FROM property_data"
       
        cursor.execute(query)

        results = cursor.fetchall()

        for row in results:
            if row[0]:
                property_names.append(row[0])  # Append property_name if it exists
            if row[1] and row[1] not in property_names:
                property_names.append(row[1]) # append nick_name if it exist and is not already in the list.
        cursor.close()
        connection.close()

    except pymysql.MySQLError as e:
        print(f"Error connecting to MySQL: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

    return property_names

