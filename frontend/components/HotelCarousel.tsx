'use client'

import { useState } from 'react'

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
  isMaximized?: boolean
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

export default function HotelCarousel({ hotels = HOTELS_DATA, onHotelSelect, isMaximized = false }: HotelCarouselProps) {
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

  // Grid view for maximized mode
  if (isMaximized) {
    return (
      <div className="w-full grid grid-cols-2 lg:grid-cols-3 gap-4 mt-3">
        {hotels.map((hotel) => (
          <div key={hotel.id} className="bg-white rounded-xl overflow-hidden shadow-lg transition-all duration-300 flex flex-col group hover:shadow-xl hover:-translate-y-1">
            <div className="relative w-full h-[160px] overflow-hidden flex-shrink-0">
              <img
                src={hotel.image || '/placeholder-hotel.jpg'}
                alt={hotel.name}
                className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
                onError={(e) => {
                  e.currentTarget.src = '/placeholder-hotel.jpg'
                }}
              />
              <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent px-3 py-2">
                <span className="text-white text-[11px] font-medium font-inter">{hotel.location}</span>
              </div>
            </div>
            <div className="p-3 flex-1 flex flex-col justify-between">
              <h3 className="text-[13px] font-bold text-purple-primary mb-1 font-poppins leading-tight">
                {hotel.name}
              </h3>
              <p className="text-[11px] text-neutral-600 mb-2 font-inter leading-tight">
                {hotel.description || ''}
              </p>
              <div className="flex flex-wrap gap-1 mb-2 flex-1">
                {hotel.highlights?.slice(0, 3).map((highlight, idx) => (
                  <span key={idx} className="text-[9px] px-1.5 py-0.5 bg-purple-primary/10 text-purple-primary rounded font-semibold font-inter">
                    {highlight}
                  </span>
                ))}
              </div>
              <button
                className="w-full px-3 py-2 bg-gradient-to-br from-purple-primary to-purple-light text-white border-none rounded-skewed text-[11px] font-bold cursor-pointer transition-all duration-300 font-poppins uppercase tracking-wide mt-auto flex-shrink-0 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-purple-secondary/30 active:translate-y-0"
                onClick={() => onHotelSelect(hotel)}
              >
                Book This Hotel
              </button>
            </div>
          </div>
        ))}
      </div>
    )
  }

  // Carousel view for normal mode
  return (
    <div className="w-full max-w-full flex flex-col gap-3 px-1 min-h-[380px]">
      <div className="relative w-full max-w-full overflow-hidden min-h-[350px]">
        {/* Hotel Card */}
        <div className="bg-white rounded-xl overflow-hidden shadow-lg transition-transform duration-300 max-w-full min-h-[350px] flex flex-col group">
          <div className="relative w-full h-[180px] md:h-[200px] overflow-hidden flex-shrink-0">
            <img
              src={currentHotel.image || '/placeholder-hotel.jpg'}
              alt={currentHotel.name}
              className="w-full h-[180px] md:h-[200px] object-cover transition-transform duration-300 group-hover:scale-105"
              onError={(e) => {
                e.currentTarget.src = '/placeholder-hotel.jpg'
              }}
            />
            <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/70 to-transparent px-4 py-3">
              <span className="text-white text-[11px] font-medium font-inter">{currentHotel.location}</span>
            </div>
          </div>

          <div className="p-2.5 md:p-3.5 flex-1 flex flex-col justify-between">
            <h3 className="text-[13px] md:text-base font-bold text-purple-primary mb-1 md:mb-1.5 font-poppins leading-tight">
              {currentHotel.name}
            </h3>
            <p className="text-[11px] md:text-[13px] text-neutral-600 mb-2 md:mb-2.5 font-inter leading-tight">
              {currentHotel.description || ''}
            </p>

            <div className="flex flex-wrap gap-1 mb-2 flex-1">
              {currentHotel.highlights?.map((highlight, idx) => (
                <span key={idx} className="text-[9px] md:text-[10px] px-1.5 md:px-2 py-0.5 md:py-1 bg-purple-primary/10 text-purple-primary rounded font-semibold font-inter">
                  {highlight}
                </span>
              ))}
            </div>

            <button
              className="w-full px-3 md:px-4 py-2 md:py-2.5 bg-gradient-to-br from-purple-primary to-purple-light text-white border-none rounded-skewed-sm md:rounded-skewed text-[11px] md:text-[13px] font-bold cursor-pointer transition-all duration-300 font-poppins uppercase tracking-wide mt-auto flex-shrink-0 hover:-translate-y-0.5 hover:shadow-lg hover:shadow-purple-secondary/30 active:translate-y-0"
              onClick={() => onHotelSelect(currentHotel)}
            >
              Book This Hotel
            </button>
          </div>
        </div>

        {/* Navigation Arrows */}
        <button
          className="absolute top-[40%] -translate-y-1/2 left-[-8px] md:left-2 bg-white/95 border-none w-8 h-8 md:w-9 md:h-9 rounded-full flex items-center justify-center cursor-pointer transition-all duration-200 z-10 shadow-md text-purple-primary hover:bg-purple-primary hover:text-white hover:scale-110 active:scale-95"
          onClick={prevSlide}
          aria-label="Previous hotel"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="md:w-[18px] md:h-[18px]">
            <polyline points="15 18 9 12 15 6"></polyline>
          </svg>
        </button>

        <button
          className="absolute top-[40%] -translate-y-1/2 right-[-8px] md:right-2 bg-white/95 border-none w-8 h-8 md:w-9 md:h-9 rounded-full flex items-center justify-center cursor-pointer transition-all duration-200 z-10 shadow-md text-purple-primary hover:bg-purple-primary hover:text-white hover:scale-110 active:scale-95"
          onClick={nextSlide}
          aria-label="Next hotel"
        >
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="md:w-[18px] md:h-[18px]">
            <polyline points="9 18 15 12 9 6"></polyline>
          </svg>
        </button>
      </div>

      {/* Dots Indicator */}
      <div className="flex justify-center gap-2 py-1">
        {hotels.map((_, index) => (
          <button
            key={index}
            className={`w-2 h-2 md:w-[9px] md:h-[9px] rounded-full border-none cursor-pointer transition-all duration-300 p-0 hover:bg-neutral-400 ${
              index === currentIndex
                ? 'bg-purple-primary w-6 md:w-[26px] rounded'
                : 'bg-neutral-300'
            }`}
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
