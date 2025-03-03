import chromadb
import pandas as pd
final_sheet=pd.read_excel("final_data.xlsx")
content,ids=[],[]
for i in range(0,20):
    ids.append(str(i))

for idx, row in final_sheet.iterrows():
    
    combined_info = row['summary']
    content.append(combined_info)


client=chromadb.PersistentClient("INT_CHUNCKS")
collection=client.get_or_create_collection(name="Int_Collection")
collection.add(documents=content,ids=ids)
