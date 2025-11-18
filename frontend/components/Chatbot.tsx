'use client'

import { useState, useRef, useEffect } from 'react'
import axios from 'axios'
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
        <div className="fixed bottom-6 right-6 z-[1000]">
          {/* Greeting Bubble */}
          <div className="absolute bottom-[50px] right-20 bg-purple-light text-white py-3.5 px-5 rounded-[18px] shadow-[0_4px_16px_rgba(90,48,130,0.4)] text-sm font-semibold font-poppins max-w-[220px] animate-bubbleSlide leading-[1.5] break-words after:content-[''] after:absolute after:bottom-2 after:right-[-8px] after:w-0 after:h-0 after:border-[8px] after:border-transparent after:border-l-purple-light after:border-r-0 after:border-b-0 after:mt-[-4px]">
            <span className="relative z-[2] inline-block">
              <TypingGreeting text={GREETING_MESSAGE} speed={50} />
            </span>
          </div>

          {/* Chat Button with Avatar */}
          <button
            className="w-[70px] h-[70px] rounded-full bg-white border-none cursor-pointer shadow-[0_4px_20px_rgba(90,48,130,0.3)] flex items-center justify-center transition-all duration-300 p-0 overflow-hidden hover:scale-110 hover:shadow-[0_6px_25px_rgba(107,44,145,0.5)] active:scale-95"
            onClick={() => setIsOpen(true)}
            aria-label="Open chat"
          >
            <img src="/cinnamon-flower.png" alt="Chat with us" className="w-[120%] h-[120%] object-contain" />
          </button>
        </div>
      )}

      {/* Google Map Panel */}
      <GoogleMapPanel isVisible={isGoogleMapOpen} onClose={() => setIsGoogleMapOpen(false)} />

      {/* Chatbot Window */}
      {isOpen && (
        <div className={`fixed bottom-6 right-6 w-[400px] h-[600px] bg-white rounded-2xl shadow-[0_10px_50px_rgba(0,0,0,0.2)] flex flex-col overflow-hidden z-[1000] animate-slideUp transition-[height,border-radius] duration-300 ${isMinimized ? 'h-16 rounded-[32px] [&>*:not(.chatHeader)]:hidden' : ''} ${isMaximized ? 'w-[calc(100vw-3rem)] h-[calc(100vh-3rem)] max-w-[calc(100vw-3rem)] max-h-[calc(100vh-3rem)] rounded-xl' : ''} ${isGoogleMapOpen ? 'right-0 w-3/5 left-auto h-screen bottom-0 rounded-none md:w-1/2' : ''}`}>
          {/* Header */}
          <div className="bg-purple-primary text-white py-3 px-4 flex items-center justify-between rounded-t-2xl border-b-2 border-dotted border-white/40">
            <div className="flex items-center flex-1 gap-2">
              {isLoggedIn && hasUserSentMessage && (
                <button
                  className="bg-white/20 border-none text-white w-9 h-9 rounded-lg flex items-center justify-center cursor-pointer transition-all duration-300 flex-shrink-0 hover:bg-white/30 hover:scale-105 active:scale-95"
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
              <div className="flex-1 flex items-center justify-start">
                <img
                  src="/logo.png"
                  alt="Cinnamon Hotels & Resorts"
                  className="h-10 w-auto max-w-[180px] object-contain brightness-0 invert"
                />
              </div>
            </div>
            <div className="flex gap-2 items-center">
              <button
                className="bg-white/20 border-none text-white w-8 h-8 rounded-full cursor-pointer text-xl flex items-center justify-center transition-[background] duration-200 hover:bg-white/30"
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
                className="bg-white/20 border-none text-white w-8 h-8 rounded-full cursor-pointer text-xl flex items-center justify-center transition-[background] duration-200 hover:bg-white/30"
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
                className="bg-white/20 border-none text-white w-8 h-8 rounded-full cursor-pointer text-xl flex items-center justify-center transition-[background] duration-200 hover:bg-white/30"
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
                <div className="flex gap-2 py-2 px-3 bg-purple-primary border-b border-white/10 justify-evenly overflow-visible transition-all duration-300">
                  {QUICK_ACTIONS.map(action => (
                    <button
                      key={action.id}
                      className="flex items-center justify-center bg-transparent border-none w-[70px] h-[70px] cursor-pointer transition-all duration-[250ms] flex-shrink-0 p-0 flex-[0_0_auto] hover:translate-y-[-2px] disabled:opacity-50 disabled:cursor-not-allowed"
                      onClick={() => handleQuickAction(action.id)}
                      disabled={isLoading}
                    >
                      <img src={action.icon} alt={action.label} className="w-[65px] h-[65px] object-contain transition-transform duration-[250ms] hover:scale-105" />
                    </button>
                  ))}
                </div>
              )}
              {/* Messages */}
              <div className={`flex-1 overflow-y-auto p-5 bg-neutral-50 flex flex-col gap-4 [&::-webkit-scrollbar]:w-1.5 [&::-webkit-scrollbar-thumb]:bg-[#d0c4dc] [&::-webkit-scrollbar-thumb]:rounded-[3px] ${isMaximized ? 'p-6' : ''}`}>
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex gap-2 max-w-[85%] w-auto animate-fadeIn ${
                  message.sender === 'user' ? 'self-end flex-row-reverse' : 'self-start'
                }`}
              >
                {message.sender === 'bot' && (
                  <div className="w-10 h-10 rounded-full overflow-hidden flex-shrink-0 flex items-center justify-center">
                    <img
                      src="/ayunew.png"
                      alt="Virtual Concierge"
                      className="w-full h-full object-cover"
                    />
                  </div>
                )}
                <div className={`py-3.5 rounded-[20px] shadow-[0_2px_8px_rgba(0,0,0,0.08)] relative flex-1 break-words [&:has(form)]:py-3 [&:has(form)]:px-3.5 ${
                  message.sender === 'user'
                    ? 'bg-purple-primary text-white rounded-[20px_20px_4px_20px] px-5'
                    : 'bg-white text-neutral-700 rounded-[4px_20px_20px_20px] border border-neutral-300 px-5 before:content-[""] before:absolute before:left-[-8px] before:top-3 before:w-0 before:h-0 before:border-solid before:border-[0_8px_8px_0] before:border-transparent before:border-r-white before:[filter:drop-shadow(-1px_1px_1px_rgba(0,0,0,0.05))]'
                }`}>
                  {message.type === 'booking_form' ? (
                    <BookingForm onSubmit={handleBookingFormSubmit} selectedHotel={message.selectedHotel} isMaximized={isMaximized} />
                  ) : message.type === 'booking_details' && message.bookingData ? (
                    <>
                      {message.text && (
                        <p className={`m-0 text-[13px] leading-[1.5] break-words overflow-hidden font-inter font-normal whitespace-pre-line ${message.sender === 'user' ? 'text-white' : 'text-neutral-700'}`}>
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
                            <p className="my-3 mx-0 p-3 px-3.5 bg-[#F0F7FF] border-l-[3px] border-purple-primary rounded-md text-[13px] text-neutral-700 font-inter leading-[1.5]">{message.additionalMessage}</p>
                          )}
                        </>
                      )}
                      {(!message.isTyping || message.typingComplete) && message.showConfirmationButton && (
                        <button
                          className="mt-3 py-3 px-6 bg-gradient-to-br from-purple-primary to-purple-light text-white border-none rounded-[20px_0_20px_0] text-sm font-bold cursor-pointer transition-all duration-300 inline-flex items-center justify-center w-full font-poppins shadow-[0_3px_10px_rgba(90,48,130,0.4)] uppercase tracking-wider hover:translate-y-[-2px] hover:shadow-[0_5px_16px_rgba(90,48,130,0.5)] active:translate-y-0"
                          onClick={() => handleSendMessage('confirm')}
                        >
                          Confirm Changes
                        </button>
                      )}
                    </>
                  ) : message.type === 'destination_carousel' ? (
                    <>
                      {message.text && (
                        <p className={`m-0 text-[13px] leading-[1.5] break-words overflow-hidden font-inter font-normal whitespace-pre-line ${message.sender === 'user' ? 'text-white' : 'text-neutral-700'}`}>
                          {message.isTyping && !message.typingComplete ? (
                            <TypingText text={message.text} onComplete={() => handleTypingComplete(message.id)} />
                          ) : (
                            message.text
                          )}
                        </p>
                      )}
                      {(!message.isTyping || message.typingComplete) && (
                        <DestinationCarousel onSelect={handleDestinationSelect} isMaximized={isMaximized} />
                      )}
                    </>
                  ) : message.type === 'hotel_carousel' && message.hotels ? (
                    <>
                      {message.text && (
                        <p className={`m-0 text-[13px] leading-[1.5] break-words overflow-hidden font-inter font-normal whitespace-pre-line ${message.sender === 'user' ? 'text-white' : 'text-neutral-700'}`}>
                          {message.isTyping && !message.typingComplete ? (
                            <TypingText text={message.text} onComplete={() => handleTypingComplete(message.id)} />
                          ) : (
                            message.text
                          )}
                        </p>
                      )}
                      {(!message.isTyping || message.typingComplete) && (
                        <HotelCarousel hotels={message.hotels} onHotelSelect={handleHotelSelect} isMaximized={isMaximized} />
                      )}
                    </>
                  ) : message.type === 'structured' && message.structuredData ? (
                    <StructuredResponse data={message.structuredData} />
                  ) : (
                    <>
                      <p className={`m-0 text-[13px] leading-[1.5] break-words font-inter font-normal whitespace-pre-line ${message.sender === 'user' ? 'text-white' : 'text-neutral-700'}`}>
                        {message.isTyping && !message.typingComplete && message.text ? (
                          <TypingText text={message.text} onComplete={() => handleTypingComplete(message.id)} />
                        ) : (
                          message.text
                        )}
                      </p>
                      {(!message.isTyping || message.typingComplete) && message.reservationURL && (
                        <button
                          className="mt-3.5 py-3 px-5 bg-gradient-to-br from-purple-primary to-purple-light text-white border-none rounded-[25px_0_25px_0] text-xs font-bold cursor-pointer transition-all duration-300 inline-flex items-center justify-center gap-2.5 font-poppins shadow-[0_4px_12px_rgba(107,44,145,0.4)] w-full uppercase tracking-wider hover:translate-y-[-3px] hover:shadow-[0_6px_20px_rgba(107,44,145,0.5)] active:translate-y-[-1px]"
                          onClick={() => window.open(message.reservationURL, '_blank')}
                        >
                          Complete Your Booking
                        </button>
                      )}
                      {(!message.isTyping || message.typingComplete) && message.showConfirmationButton && (
                        <button
                          className="mt-3 py-3 px-6 bg-gradient-to-br from-purple-primary to-purple-light text-white border-none rounded-[20px_0_20px_0] text-sm font-bold cursor-pointer transition-all duration-300 inline-flex items-center justify-center w-full font-poppins shadow-[0_3px_10px_rgba(90,48,130,0.4)] uppercase tracking-wider hover:translate-y-[-2px] hover:shadow-[0_5px_16px_rgba(90,48,130,0.5)] active:translate-y-0"
                          onClick={() => handleSendMessage('confirm')}
                        >
                          Confirm Changes
                        </button>
                      )}
                      {(!message.isTyping || message.typingComplete) && message.showMapButton && (
                        <button
                          className="mt-3 py-2.5 px-5 bg-purple-primary text-white border-none rounded-[20px_0_20px_0] text-sm font-semibold cursor-pointer transition-all duration-300 flex items-center gap-2 font-poppins shadow-[0_2px_8px_rgba(107,44,145,0.3)] hover:bg-purple-light hover:translate-y-[-2px] hover:shadow-[0_4px_12px_rgba(107,44,145,0.4)] active:translate-y-0"
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
              <div className="flex gap-2 max-w-[85%] animate-fadeIn self-start">
                <div className="w-10 h-10 rounded-full overflow-hidden flex-shrink-0 flex items-center justify-center">
                  <img
                    src="/ayunew.png"
                    alt="Virtual Concierge"
                    className="w-full h-full object-cover"
                  />
                </div>
                <div className="py-3.5 px-5 rounded-[20px] shadow-[0_2px_8px_rgba(0,0,0,0.08)] relative bg-white text-neutral-700 rounded-[4px_20px_20px_20px] border border-neutral-300 before:content-[''] before:absolute before:left-[-8px] before:top-3 before:w-0 before:h-0 before:border-solid before:border-[0_8px_8px_0] before:border-transparent before:border-r-white before:[filter:drop-shadow(-1px_1px_1px_rgba(0,0,0,0.05))]">
                  <div className="flex gap-1 py-1">
                    <span className="w-2 h-2 rounded-full bg-purple-primary animate-typing"></span>
                    <span className="w-2 h-2 rounded-full bg-purple-primary animate-typing [animation-delay:0.2s]"></span>
                    <span className="w-2 h-2 rounded-full bg-purple-primary animate-typing [animation-delay:0.4s]"></span>
                  </div>
                </div>
              </div>
            )}

                <div ref={messagesEndRef} />
              </div>

              {/* Input Area */}
              <div className="flex gap-0 p-4 bg-white border-t border-neutral-300 rounded-b-2xl relative">
                <input
                  type="text"
                  className="flex-1 py-3 pr-[50px] pl-5 border border-neutral-300 rounded-3xl text-sm outline-none transition-[border-color] duration-200 font-inter text-neutral-700 placeholder:text-neutral-500 placeholder:text-xs focus:border-purple-primary disabled:bg-neutral-100 disabled:cursor-not-allowed"
                  placeholder="Type your message here..."
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  disabled={isLoading}
                />
                <button
                  className="absolute right-6 top-1/2 -translate-y-1/2 w-9 h-9 rounded-full bg-transparent border-none text-purple-primary cursor-pointer flex items-center justify-center transition-all duration-200 flex-shrink-0 hover:text-purple-light hover:scale-110 disabled:opacity-30 disabled:cursor-not-allowed"
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
