from fastapi import APIRouter, HTTPException, Depends,Response,Request
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from datetime import datetime
import uuid
import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai
from Application.database import get_db, Session_Table, Chat,ChatTransfer
from Application.endpoints.prompt_generator import registered_prompt
from Application.retiever import validate_collection_id,retrieve_chunks
# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("guest_user.log", mode="a"), logging.StreamHandler()],
)


load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_KEY")

if not GEMINI_API_KEY:
    logging.error("GEMINI_API_KEY environment variable is missing!")
    raise ValueError("GEMINI_KEY is not set in environment variables")

genai.configure(api_key=GEMINI_API_KEY)





registered_router = APIRouter()

# Initialize model
generation_config = {
    "temperature": 1,
    "top_p": 0.95,
    "top_k": 40,
    "max_output_tokens": 8192,
    "response_mime_type": "text/plain",
}
def transfer_to_customer_team():
        
        """Simulates transferring the chat to the customer service team."""
        logging.info("Inside the transfer_to_customer_service")
        message = "Sure I'm transferring your call to the customer service team. Please wait a moment. Call transferred to the customer service team successfully!!!!"
            
        logging.info(message)  # Log the message
        
        logging.info("Returning the message from transfer_to_customer_service")
        return message

model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    generation_config=generation_config,
    system_instruction=registered_prompt,
  tools=[transfer_to_customer_team]
)
chat = model.start_chat()


@registered_router.get("/create_session/")
def guest_create_session(response:Response,db: Session = Depends(get_db)):
    """Generates a new session ID for a Registered user."""
    
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
    response.set_cookie(key="reg_session_id", value=session_id, httponly=True) 
    
    return {
        "message": "Customer's session created successfully!!",
        "session_id": session_id,
        
    }

@registered_router.post("/chat/registered")
def chat_with_bot(request:Request,property_id:str, user_input: str, db: Session = Depends(get_db)):
    """Takes user input, generates LLM response, and appends conversation in DB."""
    session_id=request.cookies.get("reg_session_id")
    user = db.query(Session_Table).filter_by(session_id=session_id).first()
    record_search = db.query(Chat).filter_by(session_id=session_id).first()
    
    if not user:
        raise HTTPException(status_code=400, detail="Invalid session ID")


    
    
    if not validate_collection_id(property_id):
        raise HTTPException(status_code=400, detail=f"Please enter valid property ID")
 
    context = retrieve_chunks(user_input,property_id)
    augmented_query = f"Context: {context}\nQuestion: {user_input}."

    response = chat.send_message(augmented_query)



###
    for part in response.candidates[0].content.parts:

        if hasattr(part, "function_call") and part.function_call is not None and part.function_call.name == "transfer_to_customer_team":
            transfer_chat = ChatTransfer(session_id=session_id, transferred_by="bot",
                                          transfer_reason="Transfer to customer service team",
                                          transferred_at=datetime.utcnow())
            logging.info(f"Entry made to ChatTransfer table")
            db.add(transfer_chat)
            session_record = db.query(Session_Table).filter_by(session_id=session_id).first()
            if session_record:
                session_record.ended_at = datetime.utcnow()
            db.commit()
            db.refresh(transfer_chat)
            logging.info(f"Entry made successfully to ChatTransfer table")
            if session_record:
                db.refresh(session_record)
            logging.info(f"calling transfer_to_customer_service funtion....")
            return {"Session ID":session_id,"message": transfer_to_customer_team()}
    final_response=response.text
    
    message_container = f"\n USER-> {user_input}\n RESPONSE-> {final_response}"

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




@registered_router.get("/Get_session_chat/")
def get_session_chat(session_id: str, db: Session = Depends(get_db)):
    """Fetches Conversation History for a given session ID."""
    
    record_search =db.query(Chat).filter_by(session_id = session_id).all() #db.query(Chat).filter(Chat.session_id == session_id).all()

    if not record_search:
        raise HTTPException(status_code=400, detail="No Chat found for given session ID")

    messages = [record.message for record in record_search]  # Extract messages

    return {
        "Session ID": session_id,
        "Conversation History": messages
    }


