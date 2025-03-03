import streamlit as st
import requests
import json
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
import httpx
import asyncio
import google.generativeai as genai
import chromadb
from sqlalchemy.orm import Session
from Application.guest_user_retriever import collection
from dotenv import load_dotenv
from Application.database import SessionLocal,Session_Table,Chat,ChatTransfer
import logging
import uuid
import os
import streamlit as st
import requests
import json
from datetime import datetime, timezone
from fastapi import FastAPI, HTTPException
import httpx
import asyncio
import google.generativeai as genai
import chromadb
from sqlalchemy.orm import Session
from retiever import retrieve_chunks, validate_collection_id
from dotenv import load_dotenv
from Application.database import SessionLocal,Session_Table,Chat,ChatTransfer
import logging
import uuid
from Application.guest_user_retriever import collection
import os
from validate import login_user


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('guest_user.log', mode='a'), 
        logging.StreamHandler()
    ],
)

#logging.info("Doing Database Configuration...")
db = SessionLocal()
def get_db():
   
    try:
        yield db
    finally:
        db.close()


logging.info("Doing Gemini Configuration...")

load_dotenv()


GEMINI_API_KEY =os.getenv('GEMINI_KEY') 
if not GEMINI_API_KEY:
        logging.info(" GEMINI_API_KEY variable not found...")
        raise ValueError("GEMINI_KEY environment variable is not set")
genai.configure(api_key=GEMINI_API_KEY)
logging.info("Gemini Key founded !!")





generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

system_instruction = """
  
    Persona:  You are a helpful and professional assistant for a hotel booking system. Your primary role is to answer questions from guest users who have not booked a room and are
      inquiring about available rooms, pricing, amenities, policies, and general hotel-related information..
      Here you are representing  Neovis Consulting,it is a leading firm specializing in business transformation, strategy, human capital development, technology, and operations. You are professional, knowledgeable, and formal in tone, delivering comprehensive and detailed responses.
   

Guidelines:

Provide Clear & Friendly Responses: Always maintain a professional and courteous tone when assisting guests.
Restrict Sensitive Information: If the user asks about cleaning_fee_id, cleaning_fee_value_type, cleaning_fee_formula, channel_commission_use_account_settings, any kind of commission, any kind of ID, password, or formula, NEVER provide any details of sensitive information. Instead, respond professionally:
"I'm sorry, but I can't provide that information."
Encourage Booking Actions: If the guest is interested, guide them on how to proceed with booking a room.
Avoid Speculation : If the information is unavailable, politely inform the guest and direct them to the appropriate contact.

    
"""

model = genai.GenerativeModel(

    model_name="models/gemini-2.0-flash",
    generation_config=generation_config,
  
    system_instruction=system_instruction)

chat = model.start_chat()

query_text=" What ammenities are provided by Zen Lodge .also provide wifi password?"


results = collection.query(
    query_texts=[query_text],
    n_results=1  # Retrieve top 3 matches
)

context = results['documents']

print("Length of Document is-->",len(context))
augmented_query = f"Context: {context}\nQuestion: {query_text}.Please note nick_name means property name.  "
    
response = chat.send_message(augmented_query)



print(response.text)

######




