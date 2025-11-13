'use client'

import styles from './MapPopup.module.css'

interface MapPopupProps {
  isOpen: boolean
  onClose: () => void
}

export default function MapPopup({ isOpen, onClose }: MapPopupProps) {
  if (!isOpen) return null

  return (
    <div className={styles.overlay} onClick={onClose}>
      <div className={styles.modal} onClick={(e) => e.stopPropagation()}>
        <button className={styles.closeButton} onClick={onClose} aria-label="Close map">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>

        <div className={styles.content}>
          <div className={styles.leftSection}>
            <img src="/map.png" alt="Sri Lanka Travel Map" className={styles.mapImage} />
          </div>

          <div className={styles.rightSection}>
            <div className={styles.header}>
              <div className={styles.avatarCircle}>
                <img src="/ayunew.png" alt="Concierge" />
              </div>
            </div>

            <div className={styles.textContent}>
              <p className={styles.welcomeText}>
                Welcome to Sri Lanka, solo adventurer! 🙏 This teardrop island offers
                ancient temples, pristine beaches, wildlife safaris, and warm
                hospitality - perfect for your first solo journey. Let me help you craft
                an unforgettable experience across this diverse paradise.
              </p>

              <div className={styles.section}>
                <h3 className={styles.sectionTitle}>Quick Trip Essentials for Solo Travelers</h3>

                <h4 className={styles.subTitle}>Best Time to Visit:</h4>
                <ul className={styles.bulletList}>
                  <li>West/South Coast: November - April</li>
                  <li>East Coast: April - September</li>
                  <li>Hill Country: Year-round</li>
                </ul>

                <h4 className={styles.subTitle}>Getting Around:</h4>
                <ul className={styles.bulletList}>
                  <li>Trains: Scenic & budget-friendly (book ahead!)</li>
                  <li>Private driver: Comfortable for 3-7 days</li>
                  <li>Tuk-tuks: Great for short distances</li>
                  <li>Domestic flights: Colombo to Jaffna saves time</li>
                </ul>

                <h4 className={styles.subTitle}>Solo Traveler Tips:</h4>
                <ul className={styles.checkList}>
                  <li>✓ Sri Lankans are incredibly friendly and helpful</li>
                  <li>✓ Stay connected with local SIM card (Dialog/Mobitel)</li>
                  <li>✓ Dress modestly at religious sites</li>
                  <li>✓ Pre-book accommodation during peak season</li>
                  <li>✓ Join group tours to meet fellow travelers</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
