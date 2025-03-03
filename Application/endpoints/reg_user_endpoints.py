

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from datetime import datetime
import uuid
import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from Application.database import SessionLocal, Session_Table, Chat
from Application.endpoints.prompt_generator import registered_prompt
from Application.retiever import validate_collection_id,retrieve_chunks
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

# Define system instruction


# Initialize FastAPI app
registered_router = APIRouter()

# Initialize model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=registered_prompt,
)
chat = model.start_chat()
# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@registered_router.get("/create_session/Registered")
def create_session(db: Session = Depends(get_db)):
    """Generates a new session ID for a guest user."""
    
    user_id = str(uuid.uuid4())  
    session_id = str(uuid.uuid4())  

    new_session = Session_Table(
        session_id=session_id,
        user_id=user_id,
        user_type="Registered",
        status="active",
        started_at=datetime.utcnow(),
    )

    db.add(new_session)
    db.commit()
    
    
    return {
        "message": "Registered user session created successfully!!",
        "Session_id": session_id,
        
    }

@registered_router.post("/chat/registered")
def chat_with_bot(session_id: str,property_id:str, user_input: str, db: Session = Depends(get_db)):
    """Takes user input, generates LLM response, and appends conversation in DB."""
    
    user = db.query(Session_Table).filter_by(session_id=session_id).first()
    record_search = db.query(Chat).filter_by(session_id=session_id).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid session ID")

    # Generate LLM response
    
    
    if not validate_collection_id(property_id):
        raise HTTPException(status_code=400, detail=f"Please enter valid property ID")
        
    
        


    
    # Retrieve context from ChromaDB
    context = retrieve_chunks(user_input,property_id)
    augmented_query = f"Context: {context}\nQuestion: {user_input}. Please note nick_name in given Context  means property name."

    response = chat.send_message(augmented_query)
    final_response=response.text
    message_container = f"\n USER-> {user_input}\n RESPONSE-> {final_response}"

    # Ensure timestamps are datetime
    user.ended_at = datetime.utcnow()
    
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
        record_search.message = (record_search.message or "") + message_container
        record_search.sent_at = datetime.utcnow()

    db.add(user)
    db.commit()
    db.refresh(user)

    return {"session_id": session_id,
             "User: ":user_input,
             "AI Response: ":final_response}



from fastapi.encoders import jsonable_encoder
@registered_router.get("/Get_session_chat/")
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


