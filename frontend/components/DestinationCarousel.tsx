'use client'

import { useState } from 'react'
import styles from './DestinationCarousel.module.css'

interface Destination {
  name: string
  image: string
  description: string
}

interface DestinationCarouselProps {
  onSelect: (destination: string) => void
}

const DESTINATIONS: Destination[] = [
  {
    name: 'Sri Lanka',
    image: '/srilanka.avif',
    description: 'Explore pristine beaches, ancient temples, and lush tea plantations'
  },
  {
    name: 'Maldives',
    image: '/maldives.jpg',
    description: 'Experience luxury overwater villas and crystal-clear turquoise waters'
  }
]

export default function DestinationCarousel({ onSelect }: DestinationCarouselProps) {
  const [currentIndex, setCurrentIndex] = useState(0)

  const nextSlide = () => {
    setCurrentIndex((prev) => (prev + 1) % DESTINATIONS.length)
  }

  const prevSlide = () => {
    setCurrentIndex((prev) => (prev - 1 + DESTINATIONS.length) % DESTINATIONS.length)
  }

  const goToSlide = (index: number) => {
    setCurrentIndex(index)
  }

  const currentDestination = DESTINATIONS[currentIndex]

  return (
    <div className={styles.carouselContainer}>
      <div className={styles.carousel}>
        {/* Destination Card */}
        <div className={styles.destinationCard}>
          <div className={styles.imageContainer}>
            <img
              src={currentDestination.image}
              alt={currentDestination.name}
              className={styles.destinationImage}
            />
            <div className={styles.imageOverlay}>
              <h3 className={styles.destinationName}>{currentDestination.name}</h3>
            </div>
          </div>

          <div className={styles.cardContent}>
            <p className={styles.description}>{currentDestination.description}</p>
            <button
              className={styles.selectButton}
              onClick={() => onSelect(currentDestination.name)}
            >
              Select {currentDestination.name}
            </button>
          </div>
        </div>

        {/* Navigation Arrows */}
        <button
          className={`${styles.navButton} ${styles.prevButton}`}
          onClick={prevSlide}
          aria-label="Previous destination"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>

        <button
          className={`${styles.navButton} ${styles.nextButton}`}
          onClick={nextSlide}
          aria-label="Next destination"
        >
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </div>

      {/* Dots Indicator */}
      <div className={styles.dotsContainer}>
        {DESTINATIONS.map((_, index) => (
          <button
            key={index}
            className={`${styles.dot} ${index === currentIndex ? styles.activeDot : ''}`}
            onClick={() => goToSlide(index)}
            aria-label={`Go to destination ${index + 1}`}
          />
        ))}
      </div>
    </div>
  )
}
