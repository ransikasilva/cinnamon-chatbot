import os

import httpx
from dotenv import load_dotenv
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from langchain_google_genai import ChatGoogleGenerativeAI

# Load environment variables from .env file
load_dotenv()

# Global variable to cache LLM
_cached_llm = None
_cached_gemini_llm = None


def get_llm():
    global _cached_llm

    # Return cached LLM if it exists
    if _cached_llm is not None:
        return _cached_llm

    # Azure OpenAI configuration with API key authentication
    endpoint = os.getenv("ENDPOINT_URL")
    deployment = os.getenv("DEPLOYMENT_NAME")
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    if not api_key:
        raise ValueError("AZURE_OPENAI_API_KEY environment variable is required")

    # Create and cache the LLM using API key authentication
    _cached_llm = AzureChatOpenAI(
        azure_deployment=deployment,
        azure_endpoint=endpoint,
        api_version="2025-01-01-preview",
        temperature=0.0,
        api_key=api_key,
        http_client=httpx.Client(verify=False),
    )

    return _cached_llm


def get_gemini_llm():
    global _cached_gemini_llm

    # Return cached Gemini LLM if it exists
    if _cached_gemini_llm is not None:
        return _cached_gemini_llm

    # Google Gemini configuration with API key authentication
    api_key = os.getenv("GOOGLE_API_KEY")
    
    if not api_key:
        raise ValueError("GOOGLE_API_KEY environment variable is required")

    # Create and cache the Gemini LLM
    _cached_gemini_llm = ChatGoogleGenerativeAI(
        model="gemini-2.5-flash",
        google_api_key=api_key,
        temperature=0.0,
    )

    return _cached_gemini_llm
