from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os
from dotenv import load_dotenv
from reservation_tool import HotelReservationTool

# Load environment variables
load_dotenv()

app = FastAPI(title="Cinnamon Hotels Reservation Chatbot API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # React app URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize the reservation tool
reservation_tool = HotelReservationTool()

# Pydantic models for request/response
class QueryRequest(BaseModel):
    query: str
    session_id: str

class ReservationRequest(BaseModel):
    session_id: str
    reservation_data: Dict[str, Any]

class QueryResponse(BaseModel):
    response: str
    show_form: bool = False
    prefilled_data: Dict[str, Any] = {}
    reservation_url: Optional[str] = None
    session_state: Dict[str, Any] = {}

class ReservationResponse(BaseModel):
    reservation_url: Optional[str] = None
    property: Optional[Dict[str, Any]] = None
    session_state: Dict[str, Any] = {}
    error: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Cinnamon Hotels Reservation Chatbot API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API is running"}

@app.post("/process_query", response_model=QueryResponse)
async def process_query(request: QueryRequest):
    """
    Process user queries and handle the conversation flow
    """
    try:
        result = reservation_tool.process_reservation_query(
            session_id=request.session_id,
            query=request.query
        )
        
        return QueryResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing query: {str(e)}")

@app.post("/process_reservation", response_model=ReservationResponse)
async def process_reservation(request: ReservationRequest):
    """
    Complete the reservation with final details and generate booking URL
    """
    try:
        result = reservation_tool.complete_reservation(
            session_id=request.session_id,
            reservation_data=request.reservation_data
        )
        
        return ReservationResponse(**result)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing reservation: {str(e)}")

@app.get("/session/{session_id}")
async def get_session_state(session_id: str):
    """
    Get current session state for debugging or frontend sync
    """
    try:
        if session_id in reservation_tool.sessions:
            session = reservation_tool.sessions[session_id]
            return {"session_state": session.__dict__}
        else:
            return {"session_state": None, "message": "Session not found"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")

@app.delete("/session/{session_id}")
async def clear_session(session_id: str):
    """
    Clear session data (useful for testing or reset functionality)
    """
    try:
        if session_id in reservation_tool.sessions:
            del reservation_tool.sessions[session_id]
            return {"message": f"Session {session_id} cleared successfully"}
        else:
            return {"message": f"Session {session_id} not found"}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error clearing session: {str(e)}")

@app.get("/hotels")
async def get_hotels():
    """
    Get available hotels data (for frontend display or debugging)
    """
    try:
        return reservation_tool.hotels_data
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving hotels data: {str(e)}")

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("BACKEND_PORT", 8000))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )