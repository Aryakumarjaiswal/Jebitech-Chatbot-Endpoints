from fastapi import FastAPI, HTTPException,APIRouter
from Application.endpoints.guest_user_endpoint import guest_router
from Application.endpoints.reg_user_endpoints import registered_router
app=FastAPI()

app.include_router(guest_router, prefix="/Guest_user", tags=["Guest_user"])
app.include_router(registered_router, prefix="/Registered_user", tags=["Registered_user"])
  #facing issue on guest user message retrieval endpoint
  
   #uvicorn Application.endpoints.app:app --reload
