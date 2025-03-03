import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv
import os
# Read Excel file
df = pd.read_excel("final_data.xlsx")
load_dotenv()
#MySQL Connection Details
# host = os.getenv('HOST')
# user = os.getenv('USERNAME')
# password = os.getenv('DB_PASSWORD')
# database = os.getenv('DB') 
# table_name = "property_data"

host ='localhost'
user ="root"
password = '#1Krishna'
database ='chatbot_db'
table_name = "property_data"

# Create MySQL engine
engine = create_engine(f"mysql+pymysql://{user}:{password}@{host}/{database}")

# Insert DataFrame into MySQL table

df.to_sql(table_name, con=engine, if_exists="replace", index=False)

print("Data inserted successfully!")
