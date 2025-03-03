import chromadb


client = chromadb.PersistentClient(path=r"C:\Users\ARYAN\OneDrive\Desktop\Chatbot\CHUNCKS")



def validate_collection_id(collection_id: str) -> bool:
    """Validates if a collection ID exists in ChromaDB."""
    

    

    try:


        collection = client.get_collection("collection_" + collection_id)

        #logging.info("Property ID is valid!!")
        return True
    except Exception:
        #logging.error(f"Collection ID {collection_id} not found.")
        return False
def retrieve_chunks(query, collection_name, top_k=4):
    #logging.info("Inside the retrieve_chunks function")
    try:
        #logging.info("Retrieving Collection id..")
        collection = client.get_collection("collection_" + collection_name)
     
        results = collection.query(query_texts=[query], n_results=top_k)
        return " ".join(doc for doc in results["documents"][0])
    except Exception as e:
        error_message = f"Error retrieving context: {e}"
        
        #logging.error(error_message)
        return error_message
