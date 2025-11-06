"""Response schemas for API.

========================================================================================
 Copyright (c) 2025 OCTAVE. All rights reserved.

 This is proprietary and confidential software of OCTAVE.
 Unauthorized use, reproduction, or distribution is strictly prohibited.
========================================================================================
"""
from typing import Optional

import pydantic


class QueryResponse(pydantic.BaseModel):
    """Response model for user queries."""

    response: str
    show_form: bool = False
    prefilled_data: Optional[dict] = None
    reservation_url: Optional[str] = None
