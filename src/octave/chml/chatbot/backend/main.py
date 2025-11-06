"""Hotel booking chatbot FastAPI backend.

========================================================================================
 Copyright (c) 2025 OCTAVE. All rights reserved.

 This is proprietary and confidential software of OCTAVE.
 Unauthorized use, reproduction, or distribution is strictly prohibited.
========================================================================================
"""
import logging

import fastapi
from fastapi.middleware import cors

from octave.chml.chatbot.backend.app.api.endpoints import chatbot, health

logger = logging.getLogger(__name__)

app = fastapi.FastAPI(title="Hotel Booking Chatbot API")

# Enable CORS
app.add_middleware(
    cors.CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router, tags=["health"])
app.include_router(chatbot.router, tags=["chatbot"])


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
