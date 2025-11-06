"""Health check endpoints.

========================================================================================
 Copyright (c) 2025 OCTAVE. All rights reserved.

 This is proprietary and confidential software of OCTAVE.
 Unauthorized use, reproduction, or distribution is strictly prohibited.
========================================================================================
"""
import datetime

import fastapi

router = fastapi.APIRouter()


@router.get("/")
def read_root():
    """Root endpoint returning API status."""
    return {"message": "Hotel Booking Chatbot API is running"}


@router.get("/health")
def health_check():
    """Health check endpoint returning service status."""
    return {"status": "healthy", "timestamp": datetime.datetime.now().isoformat()}
