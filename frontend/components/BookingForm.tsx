'use client'

import { useState } from 'react'
import styles from './BookingForm.module.css'

interface BookingFormProps {
  onSubmit: (data: BookingFormData) => void
  selectedHotel?: { id: string; name: string }
  isMaximized?: boolean
}

export interface BookingFormData {
  hotel: string
  hotelName: string
  checkIn: string
  checkOut: string
  adults: number
  children: number
  rooms: number
  specialCode?: string
}

// Only Cinnamon Grand for Type 1 users
const CINNAMON_GRAND = { id: '42169', name: 'Cinnamon Grand Colombo' }

export default function BookingForm({ onSubmit, selectedHotel, isMaximized }: BookingFormProps) {
  // Use selectedHotel if provided, otherwise default to Cinnamon Grand
  const hotel = selectedHotel || CINNAMON_GRAND

  const [checkIn, setCheckIn] = useState('')
  const [checkOut, setCheckOut] = useState('')
  const [adults, setAdults] = useState(4)
  const [children, setChildren] = useState(0)
  const [rooms, setRooms] = useState(1)
  const [specialCode, setSpecialCode] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!checkIn || !checkOut) {
      alert('Please select check-in and check-out dates')
      return
    }

    onSubmit({
      hotel: hotel.id,
      hotelName: hotel.name,
      checkIn,
      checkOut,
      adults,
      children,
      rooms,
      specialCode
    })
  }

  // Get today's date in YYYY-MM-DD format for min date
  const today = new Date().toISOString().split('T')[0]

  return (
    <form className={`${styles.bookingForm} ${isMaximized ? styles.maximized : ''}`} onSubmit={handleSubmit}>
      <div className={styles.formTitle}>Complete Your Booking</div>

      {/* Check-in Date */}
      <div className={styles.formGroup}>
        <label className={styles.label}>Check-in Date</label>
        <input
          type="date"
          className={styles.dateInput}
          value={checkIn}
          onChange={(e) => setCheckIn(e.target.value)}
          min={today}
          required
        />
      </div>

      {/* Check-out Date */}
      <div className={styles.formGroup}>
        <label className={styles.label}>Check-out Date</label>
        <input
          type="date"
          className={styles.dateInput}
          value={checkOut}
          onChange={(e) => setCheckOut(e.target.value)}
          min={checkIn || today}
          required
        />
      </div>

      {/* Guests */}
      <div className={styles.formGroup}>
        <label className={styles.label}>Guests</label>
        <div className={styles.guestsRow}>
          <div className={styles.guestControl}>
            <span className={styles.guestLabel}>Adults</span>
            <div className={styles.counter}>
              <button
                type="button"
                className={styles.counterBtn}
                onClick={() => setAdults(Math.max(1, adults - 1))}
              >
                -
              </button>
              <span className={styles.counterValue}>{adults}</span>
              <button
                type="button"
                className={styles.counterBtn}
                onClick={() => setAdults(Math.min(10, adults + 1))}
              >
                +
              </button>
            </div>
          </div>

          <div className={styles.guestControl}>
            <span className={styles.guestLabel}>Children</span>
            <div className={styles.counter}>
              <button
                type="button"
                className={styles.counterBtn}
                onClick={() => setChildren(Math.max(0, children - 1))}
              >
                -
              </button>
              <span className={styles.counterValue}>{children}</span>
              <button
                type="button"
                className={styles.counterBtn}
                onClick={() => setChildren(Math.min(10, children + 1))}
              >
                +
              </button>
            </div>
          </div>

          <div className={styles.guestControl}>
            <span className={styles.guestLabel}>Rooms</span>
            <div className={styles.counter}>
              <button
                type="button"
                className={styles.counterBtn}
                onClick={() => setRooms(Math.max(1, rooms - 1))}
              >
                -
              </button>
              <span className={styles.counterValue}>{rooms}</span>
              <button
                type="button"
                className={styles.counterBtn}
                onClick={() => setRooms(Math.min(5, rooms + 1))}
              >
                +
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Special Code */}
      <div className={styles.formGroup}>
        <label className={styles.label}>Promo Code (Optional)</label>
        <input
          type="text"
          className={styles.textInput}
          value={specialCode}
          onChange={(e) => setSpecialCode(e.target.value)}
          placeholder="Enter promo code"
        />
      </div>

      {/* Submit Button */}
      <button type="submit" className={styles.submitBtn}>
        Continue to Reservation
      </button>
    </form>
  )
}
