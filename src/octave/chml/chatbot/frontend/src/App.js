import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, Calendar, Users, Home } from 'lucide-react';
import './App.css';

const API_BASE_URL = 'http://localhost:8000';

const ChatBot = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      id: 1,
      text: "Hello! I'm your Cinnamon Hotels reservation assistant. I can help you find and book the perfect hotel. Where would you like to stay?",
      isBot: true,
      timestamp: new Date()
    }
  ]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [showReservationForm, setShowReservationForm] = useState(false);
  const [reservationData, setReservationData] = useState({
    checkIn: '',
    checkOut: '',
    adults: 1,
    children: 0,
    rooms: 1
  });
  const [sessionId] = useState(() => Math.random().toString(36).substr(2, 9));
  
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    if (isOpen && inputRef.current) {
      inputRef.current.focus();
    }
  }, [isOpen]);

  const sendMessage = async (messageText) => {
    if (!messageText.trim()) return;

    const userMessage = {
      id: Date.now(),
      text: messageText,
      isBot: false,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/process_query`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          query: messageText,
          session_id: sessionId
        }),
      });

      if (!response.ok) {
        throw new Error('Network response was not ok');
      }

      const data = await response.json();

      const botMessage = {
        id: Date.now() + 1,
        text: data.response,
        isBot: true,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, botMessage]);

      // Check if we need to show the reservation form
      if (data.show_form) {
        setReservationData(prev => ({
          ...prev,
          ...data.prefilled_data
        }));
        setShowReservationForm(true);
      }

      // If we have a reservation URL, redirect to it
      if (data.reservation_url) {
        window.open(data.reservation_url, '_blank');
      }

    } catch (error) {
      console.error('Error:', error);
      const errorMessage = {
        id: Date.now() + 1,
        text: "I'm sorry, I'm having trouble connecting right now. Please try again in a moment.",
        isBot: true,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    }

    setIsLoading(false);
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    sendMessage(inputMessage);
  };

  const handleReservationSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/process_reservation`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          session_id: sessionId,
          reservation_data: reservationData
        }),
      });

      const data = await response.json();

      if (data.reservation_url) {
        window.open(data.reservation_url, '_blank');
        setShowReservationForm(false);
        
        const confirmMessage = {
          id: Date.now(),
          text: "Perfect! I've opened the reservation page with your details pre-filled. You can complete your booking there. Is there anything else I can help you with?",
          isBot: true,
          timestamp: new Date()
        };
        setMessages(prev => [...prev, confirmMessage]);
      }

    } catch (error) {
      console.error('Error:', error);
    }

    setIsLoading(false);
  };

  const formatTime = (timestamp) => {
    return timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <>
      {/* Chat Button */}
      <div className={`chat-button ${isOpen ? 'hidden' : ''}`}>
        <button onClick={() => setIsOpen(true)} className="chat-toggle">
          <MessageCircle size={24} />
          <span className="chat-badge">Chat with us!</span>
        </button>
      </div>

      {/* Chat Window */}
      {isOpen && (
        <div className="chat-window">
          <div className="chat-header">
            <div className="chat-header-content">
              <MessageCircle size={20} />
              <span>Cinnamon Hotels Assistant</span>
            </div>
            <button onClick={() => setIsOpen(false)} className="chat-close">
              <X size={20} />
            </button>
          </div>

          <div className="chat-messages">
            {messages.map((message) => (
              <div key={message.id} className={`message ${message.isBot ? 'bot' : 'user'}`}>
                <div className="message-content">
                  <p>{message.text}</p>
                  <span className="message-time">{formatTime(message.timestamp)}</span>
                </div>
              </div>
            ))}
            {isLoading && (
              <div className="message bot">
                <div className="message-content">
                  <div className="typing-indicator">
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          <form onSubmit={handleSubmit} className="chat-input-form">
            <div className="chat-input-container">
              <input
                ref={inputRef}
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Type your message..."
                disabled={isLoading}
                className="chat-input"
              />
              <button type="submit" disabled={isLoading || !inputMessage.trim()} className="chat-send">
                <Send size={18} />
              </button>
            </div>
          </form>
        </div>
      )}

      {/* Reservation Form Modal */}
      {showReservationForm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Complete Your Reservation Details</h3>
              <button onClick={() => setShowReservationForm(false)} className="modal-close">
                <X size={20} />
              </button>
            </div>

            <form onSubmit={handleReservationSubmit} className="reservation-form">
              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="checkIn">
                    <Calendar size={16} />
                    Check-in Date
                  </label>
                  <input
                    type="date"
                    id="checkIn"
                    value={reservationData.checkIn}
                    onChange={(e) => setReservationData(prev => ({ ...prev, checkIn: e.target.value }))}
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="checkOut">
                    <Calendar size={16} />
                    Check-out Date
                  </label>
                  <input
                    type="date"
                    id="checkOut"
                    value={reservationData.checkOut}
                    onChange={(e) => setReservationData(prev => ({ ...prev, checkOut: e.target.value }))}
                    required
                  />
                </div>
              </div>

              <div className="form-row">
                <div className="form-group">
                  <label htmlFor="adults">
                    <Users size={16} />
                    Adults
                  </label>
                  <input
                    type="number"
                    id="adults"
                    min="1"
                    max="8"
                    value={reservationData.adults}
                    onChange={(e) => setReservationData(prev => ({ ...prev, adults: parseInt(e.target.value) }))}
                    required
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="children">
                    <Users size={16} />
                    Children
                  </label>
                  <input
                    type="number"
                    id="children"
                    min="0"
                    max="8"
                    value={reservationData.children}
                    onChange={(e) => setReservationData(prev => ({ ...prev, children: parseInt(e.target.value) }))}
                  />
                </div>
                <div className="form-group">
                  <label htmlFor="rooms">
                    <Home size={16} />
                    Rooms
                  </label>
                  <input
                    type="number"
                    id="rooms"
                    min="1"
                    max="5"
                    value={reservationData.rooms}
                    onChange={(e) => setReservationData(prev => ({ ...prev, rooms: parseInt(e.target.value) }))}
                    required
                  />
                </div>
              </div>

              <button type="submit" disabled={isLoading} className="reservation-submit">
                {isLoading ? 'Processing...' : 'Continue to Reservation'}
              </button>
            </form>
          </div>
        </div>
      )}
    </>
  );
};

const App = () => {
  return (
    <div className="App">
      <header className="App-header">
        <div className="hero-section">
          <h1>Welcome to Cinnamon Hotels</h1>
          <p>Discover luxury accommodations in Sri Lanka and the Maldives</p>
          <div className="hero-content">
            <div className="hotel-grid">
              <div className="hotel-card">
                <h3>Sri Lanka</h3>
                <p>Experience the pearl of the Indian Ocean with our luxury hotels across the island.</p>
              </div>
              <div className="hotel-card">
                <h3>Maldives</h3>
                <p>Pristine beaches and overwater villas await you in paradise.</p>
              </div>
            </div>
          </div>
        </div>
      </header>
      <ChatBot />
    </div>
  );
};

export default App;