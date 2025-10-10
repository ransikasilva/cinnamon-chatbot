'use client'

import Chatbot from '@/components/Chatbot'

export default function Home() {
  return (
    <main style={{ minHeight: '100vh', position: 'relative' }}>
      {/* Top Bar */}
      <div style={{
        background: '#6B2C91',
        padding: '25px 60px',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        fontSize: '12px',
        color: 'white',
        position: 'absolute',
        top: 0,
        left: 0,
        right: 0,
        zIndex: 100
      }}>
        <div style={{ position: 'absolute', left: '60px', display: 'flex', gap: '20px', alignItems: 'center' }}>
          <span style={{ letterSpacing: '0.8px', fontSize: '12px' }}>SEARCH</span>
          <span style={{ opacity: 0.6 }}>|</span>
          <span style={{
            fontFamily: 'var(--font-poppins), serif',
            fontStyle: 'italic',
            fontSize: '18px',
            fontWeight: '400'
          }}>Cinnamon</span>
          <span style={{ opacity: 0.6 }}>|</span>
          <span style={{ letterSpacing: '1.5px', fontSize: '11px' }}>DISCOVERY</span>
        </div>
        <img
          src="/logo.png"
          alt="Cinnamon Hotels & Resorts"
          style={{ height: '50px', width: 'auto', filter: 'brightness(0) invert(1)' }}
        />
        <div style={{ position: 'absolute', right: '60px', display: 'flex', gap: '30px', alignItems: 'center' }}>
          <span style={{ letterSpacing: '0.8px', fontSize: '12px' }}>ENGLISH</span>
          <span style={{ letterSpacing: '0.8px', fontSize: '12px' }}>MANAGE BOOKINGS</span>
          <button style={{
            background: 'white',
            color: '#6B2C91',
            border: 'none',
            padding: '12px 28px',
            borderRadius: '5px',
            cursor: 'pointer',
            fontWeight: '700',
            fontSize: '12px',
            letterSpacing: '0.8px',
            boxShadow: '0 2px 8px rgba(0,0,0,0.15)'
          }}>
            BOOK NOW
          </button>
        </div>
      </div>

      {/* Main Navigation */}
      <nav style={{
        background: 'white',
        padding: '22px 60px',
        display: 'flex',
        justifyContent: 'center',
        gap: '30px',
        alignItems: 'center',
        boxShadow: '0 2px 8px rgba(0,0,0,0.05)',
        position: 'absolute',
        top: '100px',
        left: 0,
        right: 0,
        zIndex: 99
      }}>
        <a href="#" style={{ color: '#2a2a2a', textDecoration: 'none', fontSize: '12px', fontWeight: '500', letterSpacing: '0.8px' }}>HOTELS & RESORTS</a>
        <span style={{ color: '#9b59b6', fontSize: '8px' }}>✦</span>
        <a href="#" style={{ color: '#2a2a2a', textDecoration: 'none', fontSize: '12px', fontWeight: '500', letterSpacing: '0.8px' }}>EXPERIENCES</a>
        <span style={{ color: '#9b59b6', fontSize: '8px' }}>✦</span>
        <a href="#" style={{ color: '#2a2a2a', textDecoration: 'none', fontSize: '12px', fontWeight: '500', letterSpacing: '0.8px' }}>WEDDINGS & EVENTS</a>
        <span style={{ color: '#9b59b6', fontSize: '8px' }}>✦</span>
        <a href="#" style={{ color: '#2a2a2a', textDecoration: 'none', fontSize: '12px', fontWeight: '500', letterSpacing: '0.8px' }}>OFFERS</a>
        <span style={{ color: '#9b59b6', fontSize: '8px' }}>✦</span>
        <a href="#" style={{ color: '#2a2a2a', textDecoration: 'none', fontSize: '12px', fontWeight: '500', letterSpacing: '0.8px' }}>GIFT CARDS</a>
        <span style={{ color: '#9b59b6', fontSize: '8px' }}>✦</span>
        <a href="#" style={{ color: '#2a2a2a', textDecoration: 'none', fontSize: '12px', fontWeight: '500', letterSpacing: '0.8px' }}>BOOK DIRECT</a>
        <span style={{ color: '#9b59b6', fontSize: '8px' }}>✦</span>
        <a href="#" style={{ color: '#2a2a2a', textDecoration: 'none', fontSize: '12px', fontWeight: '500', letterSpacing: '0.8px' }}>ABOUT US</a>
        <span style={{ color: '#9b59b6', fontSize: '8px' }}>✦</span>
        <a href="#" style={{ color: '#2a2a2a', textDecoration: 'none', fontSize: '12px', fontWeight: '500', letterSpacing: '0.8px' }}>ESG</a>
      </nav>

      {/* Hero Section */}
      <div style={{
        minHeight: '100vh',
        background: 'url("https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=1920&h=1080&fit=crop") center/cover',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        position: 'relative',
        backgroundPosition: 'center'
      }}>
        {/* Cinnamon Logo Overlay */}
        <div style={{
          position: 'absolute',
          top: '180px',
          left: '50%',
          transform: 'translateX(-50%)',
          textAlign: 'center'
        }}>
          <img
            src="/logo.png"
            alt="Cinnamon Hotels & Resorts"
            style={{
              height: '120px',
              width: 'auto',
              filter: 'brightness(0) invert(1) drop-shadow(0 4px 20px rgba(0,0,0,0.3))'
            }}
          />
        </div>

        {/* Booking Widget */}
        <div style={{
          position: 'absolute',
          bottom: '40px',
          left: '50%',
          transform: 'translateX(-50%)',
          width: '90%',
          maxWidth: '1200px',
          background: 'white',
          borderRadius: '0',
          boxShadow: '0 10px 40px rgba(0,0,0,0.2)',
          display: 'flex',
          alignItems: 'stretch',
          overflow: 'hidden'
        }}>
          <div style={{
            flex: '1',
            padding: '20px 30px',
            borderRight: '1px solid #e0e0e0'
          }}>
            <div style={{ fontSize: '13px', color: '#666', marginBottom: '8px' }}>Select Destination</div>
            <div style={{ fontSize: '15px', color: '#333', fontWeight: '500' }}>Select Destination</div>
          </div>

          <div style={{
            flex: '1',
            padding: '20px 30px',
            borderRight: '1px solid #e0e0e0'
          }}>
            <div style={{ fontSize: '13px', color: '#666', marginBottom: '8px' }}>Check-in / Check-out</div>
            <div style={{ fontSize: '15px', color: '#333', fontWeight: '500' }}>10 Oct - 11 Oct, 25</div>
          </div>

          <div style={{
            flex: '1',
            padding: '20px 30px',
            borderRight: '1px solid #e0e0e0'
          }}>
            <div style={{ fontSize: '13px', color: '#666', marginBottom: '8px' }}>Guests</div>
            <div style={{ fontSize: '15px', color: '#333', fontWeight: '500' }}>01 Rooms, 02 Adults</div>
          </div>

          <div style={{
            flex: '1',
            padding: '20px 30px',
            borderRight: '1px solid #e0e0e0'
          }}>
            <div style={{ fontSize: '13px', color: '#666', marginBottom: '8px' }}>Promo Code</div>
            <div style={{ fontSize: '15px', color: '#999', fontWeight: '400' }}>Promo Code</div>
          </div>

          <button style={{
            background: '#6B2C91',
            color: 'white',
            border: 'none',
            padding: '0 50px',
            cursor: 'pointer',
            fontWeight: '600',
            fontSize: '14px',
            letterSpacing: '1px',
            fontFamily: 'var(--font-poppins), sans-serif'
          }}>
            BOOK NOW
          </button>
        </div>
      </div>

      {/* Chatbot Component */}
      <Chatbot />
    </main>
  )
}
