'use client'

import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import styles from './Chatbot.module.css'
import StructuredResponse from './StructuredResponse'
import MapPopup from './MapPopup'
import BookingForm, { BookingFormData } from './BookingForm'
import GoogleMapPanel from './GoogleMapPanel'
import HotelCarousel, { Hotel, HOTELS_DATA } from './HotelCarousel'
import DestinationCarousel from './DestinationCarousel'
import TypingText from './TypingText'
import LoginPage from './LoginPage'
import BookingDetails from './BookingDetails'
import TypingGreeting from './TypingGreeting'

interface Message {
  id: string
  text?: string
  sender: 'user' | 'bot'
  timestamp: Date
  structuredData?: any
  type?: 'text' | 'structured' | 'booking_form' | 'hotel_carousel' | 'booking_details' | 'destination_carousel'
  showMapButton?: boolean
  showConfirmationButton?: boolean
  reservationURL?: string
  hotels?: Hotel[]
  selectedHotel?: { id: string; name: string }
  bookingData?: {
    bookingRef: string
    hotel: string
    checkIn: string
    checkOut: string
    guests: string
    room: string
    isUpdated: boolean
  }
  additionalMessage?: string
  isTyping?: boolean
  typingComplete?: boolean
}

const QUICK_ACTIONS = [
  { id: 'booking', label: 'Booking', icon: '/booking.png' },
  { id: 'edit', label: 'Edit', icon: '/manage.svg' },
  { id: 'dining', label: 'Dinning', icon: '/explore1.svg' },
  { id: 'info', label: 'Info', icon: '/info.png' },
]

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const GREETING_MESSAGE = "AYUBOWAN! I'm Maya. How can I assist you?"

export default function Chatbot() {
  const [isOpen, setIsOpen] = useState(false)
  const [isMinimized, setIsMinimized] = useState(false)
  const [isMaximized, setIsMaximized] = useState(false)
  const [isLoggedIn, setIsLoggedIn] = useState(false)
  const [userEmail, setUserEmail] = useState('')
  const [userType, setUserType] = useState('')
  const [emailInput, setEmailInput] = useState('')
  const [emailError, setEmailError] = useState('')
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
  const [isGoogleMapOpen, setIsGoogleMapOpen] = useState(false)
  const [isQuickActionsCollapsed, setIsQuickActionsCollapsed] = useState(false)
  const [hasUserSentMessage, setHasUserSentMessage] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const handleTypingComplete = (messageId: string) => {
    setMessages(prev => prev.map(msg =>
      msg.id === messageId ? { ...msg, typingComplete: true } : msg
    ))
  }

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  // Clear login on page refresh - user must login again
  useEffect(() => {
    localStorage.removeItem('chatbot_user_email')
    localStorage.removeItem('chatbot_user_type')
    setIsLoggedIn(false)
  }, [])


  const handleDemoUserSelect = (demoUser: typeof DEMO_USERS[0]) => {
    localStorage.setItem('chatbot_user_email', demoUser.email)
    localStorage.setItem('chatbot_user_type', demoUser.type)
    setUserEmail(demoUser.email)
    setUserType(demoUser.type)
    setIsLoggedIn(true)
    setEmailError('')
  }

  const handleHotelSelect = (hotel: Hotel) => {
    // User selected a hotel from carousel, show booking form
    const botMessage: Message = {
      id: Date.now().toString(),
      text: `Great choice! ${hotel.name} is a wonderful property. Please fill in your booking details:`,
      sender: 'bot',
      timestamp: new Date(),
      type: 'text'
    }

    const formMessage: Message = {
      id: (Date.now() + 1).toString(),
      sender: 'bot',
      timestamp: new Date(),
      type: 'booking_form',
      selectedHotel: { id: hotel.id, name: hotel.name }
    }

    setMessages(prev => [...prev, botMessage, formMessage])
  }

  const handleDestinationSelect = (destination: string) => {
    // Send the selected destination as a user message
    handleSendMessage(destination)
  }

  const handleBookingFormSubmit = async (data: BookingFormData) => {
    try {
      // Call backend to process reservation
      const response = await axios.post(`${API_BASE_URL}/process_reservation`, {
        session_id: userEmail || userType,
        reservation_data: {
          checkIn: data.checkIn,
          checkOut: data.checkOut,
          adults: data.adults,
          children: data.children,
          rooms: data.rooms,
          promo: data.specialCode || ''
        }
      })

      // Backend returns { reservation_url: "https://..." }
      const reservationURL = response.data.reservation_url

      // Add bot response with clickable button
      const botMessage: Message = {
        id: Date.now().toString(),
        text: `Perfect! I've prepared your reservation for ${data.hotelName}.\n\nCheck-in: ${data.checkIn}\nCheck-out: ${data.checkOut}\nGuests: ${data.adults} Adult${data.adults > 1 ? 's' : ''}${data.children > 0 ? `, ${data.children} Child${data.children > 1 ? 'ren' : ''}` : ''}\nRooms: ${data.rooms} Room${data.rooms > 1 ? 's' : ''}`,
        sender: 'bot',
        timestamp: new Date(),
        type: 'text',
        reservationURL: reservationURL
      }

      setMessages(prev => [...prev, botMessage])
    } catch (error) {
      console.error('Error processing reservation:', error)

      // Fallback: generate URL on frontend if backend fails
      const baseURL = 'https://reservations.cinnamonhotels.com/'
      const params = new URLSearchParams({
        adult: data.adults.toString(),
        arrive: data.checkIn,
        depart: data.checkOut,
        hotel: data.hotel,
        child: data.children.toString(),
        currency: 'USD',
        rooms: data.rooms.toString(),
        chain: '31106',
        level: 'chain',
        locale: 'en-US',
        productcurrency: 'USD'
      })

      if (data.specialCode) {
        params.append('promo', data.specialCode)
      }

      const reservationURL = `${baseURL}?${params.toString()}`

      const botMessage: Message = {
        id: Date.now().toString(),
        text: `Perfect! I've prepared your reservation for ${data.hotelName}.\n\nCheck-in: ${data.checkIn}\nCheck-out: ${data.checkOut}\nGuests: ${data.adults} Adult${data.adults > 1 ? 's' : ''}${data.children > 0 ? `, ${data.children} Child${data.children > 1 ? 'ren' : ''}` : ''}\nRooms: ${data.rooms} Room${data.rooms > 1 ? 's' : ''}`,
        sender: 'bot',
        timestamp: new Date(),
        type: 'text',
        reservationURL: reservationURL
      }

      setMessages(prev => [...prev, botMessage])
    }
  }

  const handleSendMessage = async (messageText?: string) => {
    const textToSend = messageText || inputValue.trim()

    if (!textToSend) return

    // Collapse quick actions after first user message
    if (!hasUserSentMessage) {
      setHasUserSentMessage(true)
      setIsQuickActionsCollapsed(true)
    }

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
      // Call FastAPI backend
      const response = await axios.post(`${API_BASE_URL}/process_query`, {
        query: textToSend,
        session_id: userEmail || userType // Use email as session ID, fallback to userType
      })

      // Handle response based on backend response
      let botMessage: Message

      // Check if backend is asking for destination (Sri Lanka or Maldives)
      const responseLower = response.data.response.toLowerCase()
      const isDestinationPrompt = (
        (responseLower.includes('sri lanka') && responseLower.includes('maldives')) ||
        (responseLower.includes('destination') && (responseLower.includes('prefer') || responseLower.includes('interested') || responseLower.includes('choose')))
      )

      // Check if backend is listing hotels (has multiple hotel names)
      const hotelNames = ['cinnamon grand', 'cinnamon lakeside', 'cinnamon lodge', 'cinnamon bey', 'cinnamon citadel']
      const hotelMentions = hotelNames.filter(name => responseLower.includes(name)).length
      const isHotelListing = hotelMentions >= 3 && (responseLower.includes('properties') || responseLower.includes('wonderful') || responseLower.includes('great choice'))

      if (isHotelListing) {
        // Show hotel carousel
        botMessage = {
          id: (Date.now() + 1).toString(),
          text: response.data.response,
          sender: 'bot',
          timestamp: new Date(),
          type: 'hotel_carousel',
          hotels: HOTELS_DATA,
          isTyping: true
        }
      } else if (isDestinationPrompt) {
        // Show destination carousel
        botMessage = {
          id: (Date.now() + 1).toString(),
          text: response.data.response,
          sender: 'bot',
          timestamp: new Date(),
          type: 'destination_carousel',
          isTyping: true
        }
      } else if (response.data.show_form) {
        // Backend wants to show booking form
        botMessage = {
          id: (Date.now() + 1).toString(),
          text: response.data.response,
          sender: 'bot',
          timestamp: new Date(),
          type: 'booking_form',
          isTyping: true
        }
      } else if (response.data.reservation_url) {
        // Manage booking URL provided
        botMessage = {
          id: (Date.now() + 1).toString(),
          text: response.data.response,
          sender: 'bot',
          timestamp: new Date(),
          type: 'text',
          reservationURL: response.data.reservation_url,
          isTyping: true
        }
      } else {
        // Simple text response
        botMessage = {
          id: (Date.now() + 1).toString(),
          text: response.data.response,
          sender: 'bot',
          timestamp: new Date(),
          type: 'text',
          isTyping: true
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
    // Map quick actions to user messages and send to backend
    const actionMessages: { [key: string]: string } = {
      booking: 'I need to book a hotel',
      edit: 'I need to modify my existing booking',
      dining: 'Tell me about dining options at your hotels',
      info: 'I need information about your hotels'
    }

    const messageText = actionMessages[action] || 'How can I assist you today?'
    handleSendMessage(messageText)
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
          {/* Greeting Bubble */}
          <div className={styles.greetingBubble}>
            <span className={styles.greetingText}>
              <TypingGreeting text={GREETING_MESSAGE} speed={50} />
            </span>
          </div>

          {/* Chat Button with Avatar */}
          <button
            className={styles.chatButton}
            onClick={() => setIsOpen(true)}
            aria-label="Open chat"
          >
            <img src="/cinnamon-flower.png" alt="Chat with us" className={styles.chatButtonImage} />
          </button>
        </div>
      )}

      {/* Google Map Panel */}
      <GoogleMapPanel isVisible={isGoogleMapOpen} onClose={() => setIsGoogleMapOpen(false)} />

      {/* Chatbot Window */}
      {isOpen && (
        <div className={`${styles.chatWindow} ${isMinimized ? styles.minimized : ''} ${isMaximized ? styles.maximized : ''} ${isGoogleMapOpen ? styles.withMap : ''}`}>
          {/* Header */}
          <div className={styles.chatHeader}>
            <div className={styles.headerContent}>
              {isLoggedIn && hasUserSentMessage && (
                <button
                  className={styles.headerMenuButton}
                  onClick={() => setIsQuickActionsCollapsed(!isQuickActionsCollapsed)}
                  aria-label="Toggle menu"
                >
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="3" y1="12" x2="21" y2="12"></line>
                    <line x1="3" y1="6" x2="21" y2="6"></line>
                    <line x1="3" y1="18" x2="21" y2="18"></line>
                  </svg>
                </button>
              )}
              <div className={styles.logoContainer}>
                <img
                  src="/logo.png"
                  alt="Cinnamon Hotels & Resorts"
                  className={styles.logo}
                />
              </div>
            </div>
            <div className={styles.headerActions}>
              <button
                className={styles.minimizeButton}
                onClick={() => {
                  setIsMinimized(!isMinimized)
                  setIsMaximized(false)
                }}
                aria-label={isMinimized ? "Restore chat" : "Minimize chat"}
              >
                {isMinimized ? (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="18 15 12 9 6 15"></polyline>
                  </svg>
                ) : (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <line x1="5" y1="12" x2="19" y2="12"></line>
                  </svg>
                )}
              </button>
              <button
                className={styles.maximizeButton}
                onClick={() => {
                  setIsMaximized(!isMaximized)
                  setIsMinimized(false)
                }}
                aria-label={isMaximized ? "Restore chat" : "Maximize chat"}
              >
                {isMaximized ? (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="4 14 10 14 10 20"></polyline>
                    <polyline points="20 10 14 10 14 4"></polyline>
                  </svg>
                ) : (
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                    <polyline points="15 3 21 3 21 9"></polyline>
                    <polyline points="9 21 3 21 3 15"></polyline>
                    <line x1="21" y1="3" x2="14" y2="10"></line>
                    <line x1="3" y1="21" x2="10" y2="14"></line>
                  </svg>
                )}
              </button>
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
          </div>

          {/* Login or Chat Content */}
          {!isLoggedIn ? (
            <LoginPage onLogin={(email, type) => {
              setUserEmail(email)
              setUserType(type)
              setIsLoggedIn(true)
            }} />
          ) : (
            <>
              {/* Quick Actions - Collapsible */}
              {!isQuickActionsCollapsed && (
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
              )}
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
                      src="/ayunew.png"
                      alt="Virtual Concierge"
                    />
                  </div>
                )}
                <div className={styles.messageBubble}>
                  {message.type === 'booking_form' ? (
                    <BookingForm onSubmit={handleBookingFormSubmit} selectedHotel={message.selectedHotel} isMaximized={isMaximized} />
                  ) : message.type === 'booking_details' && message.bookingData ? (
                    <>
                      {message.text && (
                        <p className={styles.messageText}>
                          {message.isTyping && !message.typingComplete ? (
                            <TypingText text={message.text} onComplete={() => handleTypingComplete(message.id)} />
                          ) : (
                            message.text
                          )}
                        </p>
                      )}
                      {(!message.isTyping || message.typingComplete) && (
                        <>
                          <BookingDetails
                            bookingRef={message.bookingData.bookingRef}
                            hotel={message.bookingData.hotel}
                            checkIn={message.bookingData.checkIn}
                            checkOut={message.bookingData.checkOut}
                            guests={message.bookingData.guests}
                            room={message.bookingData.room}
                            isUpdated={message.bookingData.isUpdated}
                          />
                          {message.additionalMessage && (
                            <p className={styles.additionalMessage}>{message.additionalMessage}</p>
                          )}
                        </>
                      )}
                      {(!message.isTyping || message.typingComplete) && message.showConfirmationButton && (
                        <button
                          className={styles.confirmButton}
                          onClick={() => handleSendMessage('confirm')}
                        >
                          Confirm Changes
                        </button>
                      )}
                    </>
                  ) : message.type === 'destination_carousel' ? (
                    <>
                      {message.text && (
                        <p className={styles.messageText}>
                          {message.isTyping && !message.typingComplete ? (
                            <TypingText text={message.text} onComplete={() => handleTypingComplete(message.id)} />
                          ) : (
                            message.text
                          )}
                        </p>
                      )}
                      {(!message.isTyping || message.typingComplete) && (
                        <DestinationCarousel onSelect={handleDestinationSelect} />
                      )}
                    </>
                  ) : message.type === 'hotel_carousel' && message.hotels ? (
                    <>
                      {message.text && (
                        <p className={styles.messageText}>
                          {message.isTyping && !message.typingComplete ? (
                            <TypingText text={message.text} onComplete={() => handleTypingComplete(message.id)} />
                          ) : (
                            message.text
                          )}
                        </p>
                      )}
                      {(!message.isTyping || message.typingComplete) && (
                        <HotelCarousel hotels={message.hotels} onHotelSelect={handleHotelSelect} />
                      )}
                    </>
                  ) : message.type === 'structured' && message.structuredData ? (
                    <StructuredResponse data={message.structuredData} />
                  ) : (
                    <>
                      <p className={styles.messageText}>
                        {message.isTyping && !message.typingComplete && message.text ? (
                          <TypingText text={message.text} onComplete={() => handleTypingComplete(message.id)} />
                        ) : (
                          message.text
                        )}
                      </p>
                      {(!message.isTyping || message.typingComplete) && message.reservationURL && (
                        <button
                          className={styles.reservationButton}
                          onClick={() => window.open(message.reservationURL, '_blank')}
                        >
                          Complete Your Booking
                        </button>
                      )}
                      {(!message.isTyping || message.typingComplete) && message.showConfirmationButton && (
                        <button
                          className={styles.confirmButton}
                          onClick={() => handleSendMessage('confirm')}
                        >
                          Confirm Changes
                        </button>
                      )}
                      {(!message.isTyping || message.typingComplete) && message.showMapButton && (
                        <button
                          className={styles.mapButton}
                          onClick={() => setIsGoogleMapOpen(true)}
                        >
                          Open Map
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
                    src="/ayunew.png"
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
