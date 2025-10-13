'use client'

import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import styles from './Chatbot.module.css'
import StructuredResponse from './StructuredResponse'
import MapPopup from './MapPopup'

interface Message {
  id: string
  text?: string
  sender: 'user' | 'bot'
  timestamp: Date
  structuredData?: any
  type?: 'text' | 'structured'
  showMapButton?: boolean
}

const QUICK_ACTIONS = [
  { id: 'booking', label: 'Booking', icon: '/booking.png' },
  { id: 'edit', label: 'Edit', icon: '/edit.png' },
  { id: 'dining', label: 'Dinning', icon: '/dining.png' },
  { id: 'hotels', label: 'Hotels', icon: '/hotels.png' },
  { id: 'info', label: 'Info', icon: '/info.png' },
]

const API_BASE_URL = 'http://localhost:5000'

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      text: 'Hello and welcome to Cinnamon Hotels & Resorts! I\'m your virtual concierge. How can I help you today?',
      sender: 'bot',
      timestamp: new Date()
    }
  ])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isMapOpen, setIsMapOpen] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSendMessage = async (messageText?: string) => {
    const textToSend = messageText || inputValue.trim()

    if (!textToSend) return

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      text: textToSend,
      sender: 'user',
      timestamp: new Date()
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)

    try {
      // Call Flask backend
      const response = await axios.post(`${API_BASE_URL}/api/chat`, {
        message: textToSend
      })

      // Handle response based on type
      let botMessage: Message

      if (response.data.type === 'structured') {
        // Structured response with cards
        botMessage = {
          id: (Date.now() + 1).toString(),
          sender: 'bot',
          timestamp: new Date(),
          type: 'structured',
          structuredData: response.data.data
        }
      } else {
        // Simple text response
        botMessage = {
          id: (Date.now() + 1).toString(),
          text: response.data.response,
          sender: 'bot',
          timestamp: new Date(),
          type: 'text',
          showMapButton: response.data.show_map_button || false
        }
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error('Error sending message:', error)

      // Fallback response if backend is not running
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        text: 'I apologize, but I\'m having trouble connecting right now. Please try again in a moment or call us at +94 11 249 1000.',
        sender: 'bot',
        timestamp: new Date(),
        type: 'text'
      }
      setMessages(prev => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleQuickAction = async (action: string) => {
    setIsLoading(true)

    try {
      const response = await axios.post(`${API_BASE_URL}/api/quick-action`, {
        action: action
      })

      // Add bot response
      const botMessage: Message = {
        id: Date.now().toString(),
        text: response.data.response,
        sender: 'bot',
        timestamp: new Date()
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error('Error with quick action:', error)

      // Fallback responses
      const fallbackResponses: { [key: string]: string } = {
        rooms: 'We offer luxurious rooms with stunning views. Our Deluxe Rooms start from $150/night. Would you like to know more?',
        eat: 'Experience fine dining at our multiple restaurants featuring Sri Lankan and international cuisine.',
        dining: 'Our restaurants offer breakfast buffets, à la carte lunch, and themed dinner nights with live music.',
        explore: 'Discover Sri Lanka with our curated tours - whale watching, temple visits, and safari adventures!',
        help: 'I\'m here to help! Call us at +94 11 249 1000 or email reservations@cinnamonhotels.com'
      }

      const botMessage: Message = {
        id: Date.now().toString(),
        text: fallbackResponses[action] || 'How can I assist you today?',
        sender: 'bot',
        timestamp: new Date()
      }
      setMessages(prev => [...prev, botMessage])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  return (
    <>
      {/* Floating Chat Button */}
      {!isOpen && (
        <button
          className={styles.chatButton}
          onClick={() => setIsOpen(true)}
          aria-label="Open chat"
        >
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
          </svg>
        </button>
      )}

      {/* Chatbot Window */}
      {isOpen && (
        <div className={styles.chatWindow}>
          {/* Header */}
          <div className={styles.chatHeader}>
            <div className={styles.headerContent}>
              <div className={styles.logoContainer}>
                <img
                  src="/logo.png"
                  alt="Cinnamon Hotels & Resorts"
                  className={styles.logo}
                />
              </div>
            </div>
            <button
              className={styles.closeButton}
              onClick={() => setIsOpen(false)}
              aria-label="Close chat"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
                <line x1="18" y1="6" x2="6" y2="18"></line>
                <line x1="6" y1="6" x2="18" y2="18"></line>
              </svg>
            </button>
          </div>

          {/* Quick Actions */}
          <div className={styles.quickActions}>
            {QUICK_ACTIONS.map(action => (
              <button
                key={action.id}
                className={styles.quickActionButton}
                onClick={() => handleQuickAction(action.id)}
                disabled={isLoading}
              >
                <img src={action.icon} alt={action.label} className={styles.quickActionIcon} />
              </button>
            ))}
          </div>
          {/* Messages */}
          <div className={styles.messagesContainer}>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`${styles.messageWrapper} ${
                  message.sender === 'user' ? styles.userMessage : styles.botMessage
                }`}
              >
                {message.sender === 'bot' && (
                  <div className={styles.messageAvatar}>
                    <img
                      src="/ayu.jpg"
                      alt="Virtual Concierge"
                    />
                  </div>
                )}
                <div className={styles.messageBubble}>
                  {message.type === 'structured' && message.structuredData ? (
                    <StructuredResponse data={message.structuredData} />
                  ) : (
                    <>
                      <p className={styles.messageText}>{message.text}</p>
                      {message.showMapButton && (
                        <button
                          className={styles.mapButton}
                          onClick={() => setIsMapOpen(true)}
                        >
                          🗺️ Open Map
                        </button>
                      )}
                    </>
                  )}
                </div>
              </div>
            ))}

            {isLoading && (
              <div className={`${styles.messageWrapper} ${styles.botMessage}`}>
                <div className={styles.messageAvatar}>
                  <img
                    src="/ayu.jpg"
                    alt="Virtual Concierge"
                  />
                </div>
                <div className={styles.messageBubble}>
                  <div className={styles.typingIndicator}>
                    <span></span>
                    <span></span>
                    <span></span>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Area */}
          <div className={styles.inputContainer}>
            <input
              type="text"
              className={styles.input}
              placeholder="Type your message here..."
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              onKeyPress={handleKeyPress}
              disabled={isLoading}
            />
            <button
              className={styles.sendButton}
              onClick={() => handleSendMessage()}
              disabled={!inputValue.trim() || isLoading}
              aria-label="Send message"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="currentColor">
                <path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z" />
              </svg>
            </button>
          </div>
        </div>
      )}

      {/* Map Popup */}
      <MapPopup isOpen={isMapOpen} onClose={() => setIsMapOpen(false)} />
    </>
  )
}
