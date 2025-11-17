'use client'

import styles from './BookingDetails.module.css'

interface BookingDetailsProps {
  bookingRef: string
  hotel: string
  checkIn: string
  checkOut: string
  guests: string
  room: string
  isUpdated?: boolean
}

export default function BookingDetails({
  bookingRef,
  hotel,
  checkIn,
  checkOut,
  guests,
  room,
  isUpdated
}: BookingDetailsProps) {
  return (
    <div className={styles.bookingCard}>
      <div className={styles.header}>
        <div className={styles.bookingRef}>
          <span className={styles.refLabel}>Booking Reference</span>
          <span className={styles.refNumber}>{bookingRef}</span>
        </div>
        {isUpdated && (
          <div className={styles.updatedBadge}>
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            Updated
          </div>
        )}
      </div>

      <div className={styles.divider}></div>

      <div className={styles.detailsGrid}>
        <div className={styles.detailItem}>
          <div className={styles.iconWrapper}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
          </div>
          <div className={styles.detailContent}>
            <span className={styles.detailLabel}>Hotel</span>
            <span className={styles.detailValue}>{hotel}</span>
          </div>
        </div>

        <div className={styles.detailItem}>
          <div className={styles.iconWrapper}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
          </div>
          <div className={styles.detailContent}>
            <span className={styles.detailLabel}>Check-in</span>
            <span className={styles.detailValue}>{checkIn}</span>
          </div>
        </div>

        <div className={styles.detailItem}>
          <div className={styles.iconWrapper}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
          </div>
          <div className={styles.detailContent}>
            <span className={styles.detailLabel}>Check-out</span>
            <span className={styles.detailValue}>{checkOut}</span>
          </div>
        </div>

        <div className={styles.detailItem}>
          <div className={styles.iconWrapper}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
          <div className={styles.detailContent}>
            <span className={styles.detailLabel}>Guests</span>
            <span className={styles.detailValue}>{guests}</span>
          </div>
        </div>

        <div className={styles.detailItem}>
          <div className={styles.iconWrapper}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M2 10s3-3 10-3 10 3 10 3-3 3-10 3-10-3-10-3Z"></path>
              <path d="M12 13v8"></path>
            </svg>
          </div>
          <div className={styles.detailContent}>
            <span className={styles.detailLabel}>Room Type</span>
            <span className={styles.detailValue}>{room}</span>
          </div>
        </div>
      </div>

      <div className={styles.footer}>
        <p className={styles.footerText}>What would you like to change?</p>
      </div>
    </div>
  )
}
