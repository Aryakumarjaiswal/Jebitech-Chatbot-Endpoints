from fastapi import APIRouter, HTTPException, Depends,Response,Request
from sqlalchemy.orm import Session
from fuzzywuzzy import process
from datetime import datetime
import pymysql
import uuid
import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from Application.database import get_db, Session_Table, Chat
from Application.guest_user_retriever import collection  
from Application.endpoints.prompt_generator import guest_prompt
from Application.sql_response import execute_sql,get_property_names
# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("guest_user.log", mode="a"), logging.StreamHandler()],
)

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_KEY")

if not GEMINI_API_KEY:
    logging.error("GEMINI_API_KEY environment variable is missing!")
    raise ValueError("GEMINI_KEY is not set in environment variables")

# Configure Gemini API
genai.configure(api_key=GEMINI_API_KEY)


guest_router = APIRouter()

generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model2 = genai.GenerativeModel(
    model_name= "gemini-2.0-flash",   #"gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=guest_prompt,
)
chat_session = model2.start_chat()


@guest_router.get("/create_session/")
def guest_create_session(response:Response,db: Session = Depends(get_db)):
    """Generates a new session ID for a guest user."""
    
    user_id = str(uuid.uuid4())  
    session_id = str(uuid.uuid4())  

    new_session = Session_Table(
        session_id=session_id,
        user_id=user_id,
        user_type="guest",
        status="active",
        started_at=datetime.utcnow(),
    )

    db.add(new_session)
    db.commit()
    response.set_cookie(key="guest_session_id", value=session_id, httponly=True) 
    
    return {
        "message": "Guest session created successfully!!",
        "session_id": session_id,
        
    }

@guest_router.post("/chat/guest")
def chat_with_bot(request:Request, user_input: str, db: Session = Depends(get_db)):
    """Takes user input, generates LLM response, and appends conversation in DB."""
    session_id = request.cookies.get("guest_session_id") 
    user = db.query(Session_Table).filter_by(session_id=session_id).first()
    record_search = db.query(Chat).filter_by(session_id=session_id).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid session ID")
        
        
    property_list=get_property_names()
    property_name, score = process.extractOne(user_input, property_list)
    print("User Input: ",user_input,"Retrieved property name: ",property_name)
    modified_input = f"User asked:{user_input},property_name:{property_name}"     
    response = chat_session.send_message(modified_input)
    generated_sql = response.text
    

    if  "property_building" in generated_sql or "nick_name" in generated_sql:
        logging.info("SQL query detected in response")
        
        query_result = execute_sql(generated_sql)
        generated_sql
        final_response = chat_session.send_message(
            f"User asked: '{user_input}'. The query result is: {query_result}. Format it for user understanding in natural language professionaly."
        )
        response_text = final_response.candidates[0].content.parts[0].text
        generated_sql=response_text
    else:
        logging.info("Non-SQL response detected")
        

    
    user.ended_at = datetime.utcnow()
    message_container=f"\n USER-> {user_input}\n RESPONSE-> {generated_sql}"
    if user.started_at:
        user.Duration = (user.ended_at - user.started_at).total_seconds() 
    if not record_search:
        first_chat = Chat(
            session_id=session_id,
            sender="user",
            message=message_container,
            sent_at=datetime.utcnow(),
            status="read"
        )
        db.add(first_chat)
    else:
        record_search.message = str((record_search.message or "") + message_container)
        record_search.sent_at = datetime.utcnow()

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"session_id": session_id,
             "User: ":user_input,
             "AI Response: ":generated_sql}



@guest_router.get("/Get_session_chat/")
def get_session_chat(session_id: str, db: Session = Depends(get_db)):
    """Fetches Conversation History for a given session ID."""
    
    record_search =db.query(Chat).filter_by(session_id = session_id).all() #db.query(Chat).filter(Chat.session_id == session_id).all()

    if not record_search:
        raise HTTPException(status_code=400, detail="Please enter a valid session ID")

    messages = [record.message for record in record_search]  # Extract messages

    return {
        "Session ID": session_id,
        "Conversation History": messages
    }



