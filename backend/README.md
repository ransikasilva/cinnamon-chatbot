# Cinnamon Hotels Chatbot Backend

Flask backend for the Cinnamon Hotels chatbot demo.

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the server:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

- `POST /api/chat` - Send a chat message
- `POST /api/quick-action` - Handle quick action button clicks
- `GET /api/health` - Health check

## Example Request

```bash
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "Tell me about your rooms"}'
```
