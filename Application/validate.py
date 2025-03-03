import logging
import httpx
import streamlit as st
import random
from Application.database import SessionLocal,Session_Table,Chat,ChatTransfer
import uuid
from datetime import datetime, timezone
db = SessionLocal()
def get_db():
   
    try:
        yield db
    finally:
        db.close()
async def login_user(id):
    try:
            
        
            user_id = random.randint(1, 100)
            user_role = "Registered/Guest"
            

            
            # Create new session entry
            session_id = str(uuid.uuid4())  # Generate a unique session ID
            new_session = Session_Table(
                session_id=session_id,  
                user_id=str(user_id),   # Convert user_id to string to match column type
                user_type=user_role,
                status="active",
                started_at= datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
                ended_at= datetime.utcnow().strftime('%Y-%m-%d %H:%M'),
                Duration=None
                
            )
            logging.info("Inserting Value to session Table")
            db.add(new_session)
            db.commit()
            logging.info("Inserted Value is commited to session Table")
            # Add session_id to the returned data
            #data['session_id'] = session_id
            return user_id,user_role,session_id

    except Exception as e:
        logging.info("Invalid Credential!!")
        st.sidebar.error(f"Error during login: {str(e)}")
        return None
