'use client'

import { useState } from 'react'
import styles from './HotelCarousel.module.css'

interface Hotel {
  id: string
  name: string
  location: string
  image?: string
  description?: string
  highlights?: string[]
}

interface HotelCarouselProps {
  hotels: Hotel[]
  onHotelSelect: (hotel: Hotel) => void
}

const HOTELS_DATA: Hotel[] = [
  {
    id: '42169',
    name: 'Cinnamon Grand Colombo',
    location: 'Colombo, Sri Lanka',
    image: '/hotels/grand.jpg',
    description: 'Luxury city hotel in the heart of Colombo',
    highlights: ['City Center', 'Business Hub', 'Fine Dining', 'Rooftop Bar']
  },
  {
    id: '46402',
    name: 'Cinnamon Lakeside Colombo',
    location: 'Colombo, Sri Lanka',
    image: '/hotels/lakeside.jpg',
    description: 'Waterfront hotel with lake and city views',
    highlights: ['Lake View', 'Spa & Wellness', 'Cultural Sites', 'Shopping']
  },
  {
    id: '46403',
    name: 'Cinnamon Lodge Habarana',
    location: 'Habarana, Sri Lanka',
    image: '/habarana.jpg',
    description: 'Eco-friendly resort near ancient cultural sites',
    highlights: ['Nature', 'Wildlife', 'Cultural Tours', 'Eco-Resort']
  },
  {
    id: '46404',
    name: 'Cinnamon Bey Beruwala',
    location: 'Beruwala, Sri Lanka',
    image: '/bentota.jpg',
    description: 'Beachfront resort with stunning ocean views',
    highlights: ['Beach Access', 'Water Sports', 'Ayurveda Spa', 'Seafood']
  },
  {
    id: '46405',
    name: 'Cinnamon Citadel Kandy',
    location: 'Kandy, Sri Lanka',
    image: '/citadel.avif',
    description: 'Scenic hotel overlooking Kandy Lake and mountains',
    highlights: ['Lake View', 'Hill Country', 'Cultural Sites', 'Temple']
  }
]

export default function HotelCarousel({ hotels = HOTELS_DATA, onHotelSelect }: HotelCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0)

  const nextSlide = () => {
    setCurrentIndex((prev) => (prev + 1) % hotels.length)
  }

  const prevSlide = () => {
    setCurrentIndex((prev) => (prev - 1 + hotels.length) % hotels.length)
  }

  const goToSlide = (index: number) => {
    setCurrentIndex(index)
  }

  const currentHotel = hotels[currentIndex]

  return (
    <div className={styles.carouselContainer}>
      <div className={styles.carousel}>
        {/* Hotel Card */}
        <div className={styles.hotelCard}>
          <div className={styles.imageContainer}>
            <img
              src={currentHotel.image || '/placeholder-hotel.jpg'}
              alt={currentHotel.name}
              className={styles.hotelImage}
              onError={(e) => {
                e.currentTarget.src = '/placeholder-hotel.jpg'
              }}
            />
            <div className={styles.imageOverlay}>
              <span className={styles.hotelLocation}>{currentHotel.location}</span>
            </div>
          </div>

          <div className={styles.cardContent}>
            <h3 className={styles.hotelName}>{currentHotel.name}</h3>
            <p className={styles.hotelDescription}>{currentHotel.description || ''}</p>

            <div className={styles.highlights}>
              {currentHotel.highlights?.map((highlight, idx) => (
                <span key={idx} className={styles.highlightBadge}>
                  {highlight}
                </span>
              ))}
            </div>

            <button
              className={styles.selectButton}
              onClick={() => onHotelSelect(currentHotel)}
            >
              Book This Hotel
            </button>
          </div>
        </div>

        {/* Navigation Arrows */}
        <button
          className={`${styles.navButton} ${styles.prevButton}`}
          onClick={prevSlide}
          aria-label="Previous hotel"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>

        <button
          className={`${styles.navButton} ${styles.nextButton}`}
          onClick={nextSlide}
          aria-label="Next hotel"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </div>

      {/* Dots Indicator */}
      <div className={styles.dotsContainer}>
        {hotels.map((_, index) => (
          <button
            key={index}
            className={`${styles.dot} ${index === currentIndex ? styles.activeDot : ''}`}
            onClick={() => goToSlide(index)}
            aria-label={`Go to hotel ${index + 1}`}
          />
        ))}
      </div>
    </div>
  )
}

export { HOTELS_DATA }
export type { Hotel }
