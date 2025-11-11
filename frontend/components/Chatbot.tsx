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
  { id: 'edit', label: 'Edit', icon: '/manage.svg' },
  { id: 'dining', label: 'Dinning', icon: '/explore1.svg' },
  { id: 'hotels', label: 'Hotels', icon: '/hotels.png' },
  { id: 'info', label: 'Info', icon: '/info.png' },
]

const API_BASE_URL = 'http://localhost:5000'

const DISCOUNT_MESSAGES = [
  "Get 20% off your next booking!",
  "Special weekend offers available!",
  "Book now and save up to 30%!",
  "Exclusive discounts just for you!",
  "Limited time offer - 25% off!",
]

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false)
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [userEmail, setUserEmail] = useState('')
  const [emailInput, setEmailInput] = useState('')
  const [emailError, setEmailError] = useState('')
  const [currentDiscountIndex, setCurrentDiscountIndex] = useState(0)
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

  // Check if user is already logged in when component mounts
  useEffect(() => {
    const savedEmail = localStorage.getItem('chatbot_user_email')
    if (savedEmail) {
      setUserEmail(savedEmail)
      setIsLoggedIn(true)
    }
  }, [])

  // Rotate discount messages
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentDiscountIndex((prev) => (prev + 1) % DISCOUNT_MESSAGES.length)
    }, 3000) // Change every 3 seconds

    return () => clearInterval(interval)
  }, [])

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const handleEmailSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!emailInput.trim()) {
      setEmailError('Please enter your email address')
      return
    }

    if (!validateEmail(emailInput)) {
      setEmailError('Please enter a valid email address')
      return
    }

    localStorage.setItem('chatbot_user_email', emailInput)
    setUserEmail(emailInput)
    setIsLoggedIn(true)
    setEmailError('')
  }

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
        <div className={styles.chatButtonContainer}>
          {/* Discount Bubble */}
          <div className={styles.discountBubble}>
            <span className={styles.discountText} key={currentDiscountIndex}>
              {DISCOUNT_MESSAGES[currentDiscountIndex]}
            </span>
          </div>

          {/* Chat Button with Avatar */}
          <button
            className={styles.chatButton}
            onClick={() => setIsOpen(true)}
            aria-label="Open chat"
          >
            <img src="/ayu.jpg" alt="Chat with us" className={styles.chatButtonImage} />
          </button>
        </div>
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

          {/* Login or Chat Content */}
          {!isLoggedIn ? (
            <div className={styles.loginContent}>
              <div className={styles.loginWrapper}>
                <div className={styles.loginAvatar}>
                  <img src="/ayu.jpg" alt="Concierge" />
                </div>
                <h2 className={styles.loginTitle}>Welcome!</h2>
                <p className={styles.loginSubtitle}>Please enter your email to start chatting</p>

                <form onSubmit={handleEmailSubmit} className={styles.loginFormChat}>
                  <input
                    type="email"
                    value={emailInput}
                    onChange={(e) => {
                      setEmailInput(e.target.value)
                      setEmailError('')
                    }}
                    placeholder="Enter your email"
                    className={styles.loginInput}
                    autoFocus
                  />
                  {emailError && <p className={styles.loginError}>{emailError}</p>}
                  <button type="submit" className={styles.loginSubmit}>
                    Start Chat
                  </button>
                </form>

                <p className={styles.loginPrivacy}>
                  We respect your privacy. Your email is only used for this chat session.
                </p>
              </div>
            </div>
          ) : (
            <>
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
            </>
          )}
        </div>
      )}

      {/* Map Popup */}
      <MapPopup isOpen={isMapOpen} onClose={() => setIsMapOpen(false)} />
    </>
  )
}
