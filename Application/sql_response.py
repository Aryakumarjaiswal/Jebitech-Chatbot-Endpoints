import pymysql


    
       
        
def clean_sql_query(sql_query):
    return " ".join(sql_query.replace("```sql", "").replace("```", "").strip().split())

def execute_sql(conn, sql_query):
    try:
        cleaned_query = clean_sql_query(sql_query)
        cursor = conn.cursor()
        cursor.execute(cleaned_query)
        results = cursor.fetchall()

        if results:
            formatted_results = "\n".join([str(row) for row in results])
            return f"Query executed successfully.\nResults:\n{formatted_results}"
        else:
            return "Query executed successfully, but no results were found."
    except pymysql.MySQLError as e:
        return f"MySQL Error: {e}"

