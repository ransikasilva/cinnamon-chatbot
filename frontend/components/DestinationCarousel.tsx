'use client'

import { useState } from 'react'

interface Destination {
  name: string
  image: string
  description: string
}

interface DestinationCarouselProps {
  onSelect: (destination: string) => void
  isMaximized?: boolean
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

export default function DestinationCarousel({ onSelect, isMaximized = false }: DestinationCarouselProps) {
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

  // Grid view for maximized mode
  if (isMaximized) {
    return (
      <div className="w-full grid grid-cols-2 gap-4 mt-3">
        {DESTINATIONS.map((destination) => (
          <div key={destination.name} className="bg-white rounded-xl overflow-hidden shadow-lg transition-all duration-300 flex flex-col group hover:shadow-xl hover:-translate-y-1">
            <div className="relative w-full h-[180px] overflow-hidden flex-shrink-0">
              <img
                src={destination.image}
                alt={destination.name}
                className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
              />
              <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent flex items-end">
                <h3 className="text-white text-lg font-bold px-4 pb-3 font-poppins">
                  {destination.name}
                </h3>
              </div>
            </div>
            <div className="p-3.5 flex-1 flex flex-col justify-between">
              <p className="text-[13px] text-neutral-600 mb-3 font-inter leading-relaxed">
                {destination.description}
              </p>
              <button
                className="w-full px-4 py-2.5 bg-gradient-to-br from-purple-primary to-purple-light text-white border-none rounded-skewed text-[13px] font-bold cursor-pointer transition-all duration-300 font-poppins uppercase tracking-wide hover:-translate-y-0.5 hover:shadow-lg hover:shadow-purple-secondary/30 active:translate-y-0"
                onClick={() => onSelect(destination.name)}
              >
                Select {destination.name}
              </button>
            </div>
          </div>
        ))}
      </div>
    )
  }

  // Carousel view for normal mode
  return (
    <div className="w-full max-w-full flex flex-col gap-3 px-1 min-h-[340px]">
      <div className="relative w-full max-w-full overflow-hidden min-h-[310px]">
        {/* Destination Card */}
        <div className="bg-white rounded-xl overflow-hidden shadow-lg transition-transform duration-300 max-w-full min-h-[310px] flex flex-col group">
          <div className="relative w-full h-[200px] md:h-[220px] overflow-hidden flex-shrink-0">
            <img
              src={currentDestination.image}
              alt={currentDestination.name}
              className="w-full h-[200px] md:h-[220px] object-cover transition-transform duration-300 group-hover:scale-105"
            />
            <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent flex items-end">
              <h3 className="text-white text-lg md:text-xl font-bold px-4 pb-4 font-poppins">
                {currentDestination.name}
              </h3>
            </div>
          </div>

          <div className="p-3 md:p-4 flex-1 flex flex-col justify-between">
            <p className="text-[12px] md:text-sm text-neutral-600 mb-3 md:mb-4 font-inter leading-relaxed">
              {currentDestination.description}
            </p>
            <button
              className="w-full px-4 py-2.5 md:py-3 bg-gradient-to-br from-purple-primary to-purple-light text-white border-none rounded-skewed-sm md:rounded-skewed text-[12px] md:text-sm font-bold cursor-pointer transition-all duration-300 font-poppins uppercase tracking-wide hover:-translate-y-0.5 hover:shadow-lg hover:shadow-purple-secondary/30 active:translate-y-0"
              onClick={() => onSelect(currentDestination.name)}
            >
              Select {currentDestination.name}
            </button>
          </div>
        </div>

        {/* Navigation Arrows */}
        <button
          className="absolute top-[40%] -translate-y-1/2 left-[-8px] md:left-2 bg-white/95 border-none w-8 h-8 md:w-9 md:h-9 rounded-full flex items-center justify-center cursor-pointer transition-all duration-200 z-10 shadow-md text-purple-primary hover:bg-purple-primary hover:text-white hover:scale-110 active:scale-95"
          onClick={prevSlide}
          aria-label="Previous destination"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="md:w-[18px] md:h-[18px]">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>

        <button
          className="absolute top-[40%] -translate-y-1/2 right-[-8px] md:right-2 bg-white/95 border-none w-8 h-8 md:w-9 md:h-9 rounded-full flex items-center justify-center cursor-pointer transition-all duration-200 z-10 shadow-md text-purple-primary hover:bg-purple-primary hover:text-white hover:scale-110 active:scale-95"
          onClick={nextSlide}
          aria-label="Next destination"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="md:w-[18px] md:h-[18px]">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </div>

      {/* Dots Indicator */}
      <div className="flex justify-center gap-2 py-1">
        {DESTINATIONS.map((_, index) => (
          <button
            key={index}
            className={`w-2 h-2 md:w-[9px] md:h-[9px] rounded-full border-none cursor-pointer transition-all duration-300 p-0 hover:bg-neutral-400 ${
              index === currentIndex
                ? 'bg-purple-primary w-6 md:w-[26px] rounded'
                : 'bg-neutral-300'
            }`}
            onClick={() => goToSlide(index)}
            aria-label={`Go to destination ${index + 1}`}
          />
        ))}
      </div>
    </div>
  )
}
