"""LLM model configuration and initialization utilities.

========================================================================================
 Copyright (c) 2025 OCTAVE. All rights reserved.

 This is proprietary and confidential software of OCTAVE.
 Unauthorized use, reproduction, or distribution is strictly prohibited.
========================================================================================
"""

import os

import dotenv
import httpx
import langchain_google_genai
import langchain_openai
from langchain_core.utils import utils

# Load environment variables from .env file
dotenv.load_dotenv()


def get_llm():
    """Get the Azure OpenAI LLM with API key authentication and caching."""

    # Azure OpenAI configuration with API key authentication
    endpoint = os.getenv("ENDPOINT_URL")
    deployment = os.getenv("DEPLOYMENT_NAME")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if not api_key:
        raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")

    # Create and cache the LLM using API key authentication

    llm = langchain_openai.AzureChatOpenAI(
        azure_deployment=deployment,
        azure_endpoint=endpoint,
        api_version="2025-01-01-preview",
        temperature=0.0,
        api_key=utils.convert_to_secret_str(api_key),
        http_client=httpx.Client(verify=False),
    )

    return llm


def get_gemini_llm():
    """Get the Google Gemini LLM with API key authentication"""

    # Google Gemini configuration with API key authentication
    api_key = os.getenv("GOOGLE_API_KEY")

    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")

    # Create and cache the Gemini LLM
    llm = langchain_google_genai.ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.0,
    )

    return llm
