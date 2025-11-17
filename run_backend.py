"""Simple script to run the backend with correct Python path."""
import sys
from pathlib import Path

# Add src directory to Python path
src_dir = Path(__file__).parent / "src"
sys.path.insert(0, str(src_dir))

# Now import and run the backend
from octave.chml.chatbot.backend.main import app
import uvicorn

if __name__ == "__main__":
    uvicorn.run("octave.chml.chatbot.backend.main:app", host="0.0.0.0", port=8000, reload=True)
