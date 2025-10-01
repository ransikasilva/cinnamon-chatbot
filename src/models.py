
import os 
from langchain_openai import AzureChatOpenAI, AzureOpenAIEmbeddings
from dotenv import load_dotenv
import httpx

# Load environment variables from .env file
load_dotenv()

# Global variable to cache LLM
_cached_llm = None

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
        http_client=httpx.Client(verify=False)
    )

    return _cached_llm



