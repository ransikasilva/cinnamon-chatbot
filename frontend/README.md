# Cinnamon Hotels Chatbot - Frontend

Next.js frontend for the Cinnamon Hotels chatbot demo.

## Quick Start

1. Install dependencies:
```bash
npm install
```

2. Run the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

## Important Notes

- Make sure the Flask backend is running on port 5000
- The chatbot button appears in the bottom-right corner
- Click it to open the chat interface

## Building for Production

```bash
npm run build
npm start
```

## Component Structure

- `app/page.tsx` - Main page with demo content
- `components/Chatbot.tsx` - Main chatbot component
- `components/Chatbot.module.css` - Chatbot styles
- `app/globals.css` - Global styles

## Customization

Edit the Cinnamon Hotels purple color in `Chatbot.module.css`:
```css
background: linear-gradient(135deg, #6B2C91 0%, #8B3FB8 100%);
```

Change the backend API URL in `components/Chatbot.tsx`:
```typescript
const API_BASE_URL = 'http://localhost:5000'
```
