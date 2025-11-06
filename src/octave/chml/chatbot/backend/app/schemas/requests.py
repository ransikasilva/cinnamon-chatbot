"""Request schemas for API validation.

========================================================================================
 Copyright (c) 2025 OCTAVE. All rights reserved.

 This is proprietary and confidential software of OCTAVE.
 Unauthorized use, reproduction, or distribution is strictly prohibited.
========================================================================================
"""
import pydantic


class QueryRequest(pydantic.BaseModel):
    """Request model for user queries."""

    query: str
    session_id: str


class ReservationRequest(pydantic.BaseModel):
    """Request model for hotel reservations."""

    session_id: str
    reservation_data: dict
