'use client'

import { useEffect, useRef, useState } from 'react'

interface Hotel {
  id: string
  name: string
  lat: number
  lng: number
  placeId?: string
}

interface GoogleMapPanelProps {
  isVisible: boolean
  onClose: () => void
}

const HOTELS: Hotel[] = [
  {
    id: '42169',
    name: 'Cinnamon Grand Colombo',
    lat: 6.9167,
    lng: 79.8500,
    placeId: 'ChIJO9nMCQBZ4joRPxfF2JlAKu4'
  },
  {
    id: '46402',
    name: 'Cinnamon Lakeside Colombo',
    lat: 6.9271,
    lng: 79.8612,
    placeId: 'ChIJv1bUJj1Z4joRyDlJ1LITJZc'
  },
  {
    id: '46403',
    name: 'Cinnamon Lodge Habarana',
    lat: 8.0333,
    lng: 80.7500,
    placeId: 'ChIJV9-azWWf_DoR6x941O3kB-4'
  },
  {
    id: '46404',
    name: 'Cinnamon Bey Beruwala',
    lat: 6.4787,
    lng: 79.9820,
    placeId: 'ChIJvRNrbpAu4joRfzR3iJN4iJ8'
  },
  {
    id: '46405',
    name: 'Cinnamon Citadel Kandy',
    lat: 7.3063,
    lng: 80.6238,
    placeId: 'ChIJ-XGT93po4zoRHShxzlBmszM'
  }
]

export default function GoogleMapPanel({ isVisible, onClose }: GoogleMapPanelProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const googleMapRef = useRef<google.maps.Map | null>(null)
  const markersRef = useRef<google.maps.marker.AdvancedMarkerElement[]>([])
  const infoWindowRef = useRef<google.maps.InfoWindow | null>(null)
  const [isLoaded, setIsLoaded] = useState(false)
  const [selectedHotel, setSelectedHotel] = useState<string>('')

  const handleHotelSelect = (hotelId: string) => {
    const hotelIndex = HOTELS.findIndex(h => h.id === hotelId)
    if (hotelIndex !== -1 && googleMapRef.current && markersRef.current[hotelIndex]) {
      const hotel = HOTELS[hotelIndex]
      // Pan to hotel location
      googleMapRef.current.panTo({ lat: hotel.lat, lng: hotel.lng })
      googleMapRef.current.setZoom(14)
      // Trigger marker click to show info
      google.maps.event.trigger(markersRef.current[hotelIndex], 'click')
    }
    setSelectedHotel(hotelId)
  }

  useEffect(() => {
    // Load Google Maps script
    const loadGoogleMaps = () => {
      if (window.google && window.google.maps) {
        setIsLoaded(true)
        return
      }

      // Check if script is already loading
      const existingScript = document.querySelector('script[src*="maps.googleapis.com"]')
      if (existingScript) {
        existingScript.addEventListener('load', () => setIsLoaded(true))
        return
      }

      const script = document.createElement('script')
      const apiKey = process.env.NEXT_PUBLIC_GOOGLE_MAPS_API_KEY || ''
      script.src = `https://maps.googleapis.com/maps/api/js?key=${apiKey}&libraries=places,marker&v=weekly`
      script.async = true
      script.defer = true
      script.onload = () => setIsLoaded(true)
      document.head.appendChild(script)
    }

    loadGoogleMaps()
  }, [])

  useEffect(() => {
    if (!isLoaded || !mapRef.current || !isVisible) return

    // Initialize map
    if (!googleMapRef.current) {
      googleMapRef.current = new google.maps.Map(mapRef.current, {
        center: { lat: 7.8731, lng: 80.7718 }, // Center of Sri Lanka
        zoom: 8,
        mapId: 'cinnamon_hotels_map',
        disableDefaultUI: false,
        zoomControl: true,
        mapTypeControl: false,
        streetViewControl: false,
        fullscreenControl: false
      })

      // Initialize InfoWindow
      infoWindowRef.current = new google.maps.InfoWindow()

      // Create markers for each hotel
      const placesService = new google.maps.places.PlacesService(googleMapRef.current)

      HOTELS.forEach((hotel) => {
        const markerContent = document.createElement('div')
        markerContent.className = 'cursor-pointer transition-transform duration-200 ease-in-out hover:scale-115'
        markerContent.innerHTML = `
          <div class="drop-shadow-md">
            <svg width="32" height="40" viewBox="0 0 32 40" fill="none">
              <path d="M16 0C7.163 0 0 7.163 0 16c0 16 16 24 16 24s16-8 16-24c0-8.837-7.163-16-16-16z" fill="#6B2C91"/>
              <circle cx="16" cy="16" r="6" fill="white"/>
            </svg>
          </div>
        `

        const marker = new google.maps.marker.AdvancedMarkerElement({
          map: googleMapRef.current,
          position: { lat: hotel.lat, lng: hotel.lng },
          content: markerContent,
          title: hotel.name
        })

        // Click event to show hotel info with photos
        marker.addListener('click', () => {
          if (!infoWindowRef.current) return

          // Show loading state
          infoWindowRef.current.setContent(`
            <div class="max-w-xs font-inter">
              <div class="p-5 text-center text-neutral-600 text-sm">Loading...</div>
            </div>
          `)
          infoWindowRef.current.open(googleMapRef.current, marker)

          // Fetch place details with valid Place ID
          if (hotel.placeId) {
            placesService.getDetails(
              {
                placeId: hotel.placeId,
                fields: ['name', 'photos', 'rating', 'formatted_address']
              },
              (place, status) => {
                if (status === google.maps.places.PlacesServiceStatus.OK && place) {
                  // Get up to 5 photos
                  const photos = place.photos?.slice(0, 5) || []
                  const photoUrls = photos.map(photo => photo.getUrl({ maxWidth: 300, maxHeight: 200 }))

                  let photosHTML = ''
                  if (photoUrls.length > 0) {
                    photosHTML = `
                      <div class="relative w-full" id="carousel-${hotel.id}">
                        <div class="relative w-full h-56">
                          ${photoUrls.map((url, idx) => `
                            <img src="${url}" alt="${hotel.name}" class="w-full h-56 object-cover rounded-t-lg mb-3 ${idx === 0 ? 'block' : 'hidden'}" data-index="${idx}" />
                          `).join('')}
                        </div>
                        ${photoUrls.length > 1 ? `
                          <div class="absolute bottom-5 left-1/2 -translate-x-1/2 flex gap-1.5 z-10">
                            ${photoUrls.map((_, idx) => `
                              <button class="w-2 h-2 rounded-full bg-white/60 hover:bg-white/90 transition-all duration-300 cursor-pointer ${idx === 0 ? 'w-5 rounded' : ''}" data-index="${idx}"></button>
                            `).join('')}
                          </div>
                        ` : ''}
                      </div>
                    `
                  }

                  const content = `
                    <div class="max-w-xs font-inter">
                      ${photosHTML}
                      <div class="p-1">
                        <h3 class="text-base font-bold text-purple-primary mb-2 font-poppins">${hotel.name}</h3>
                        ${place.rating ? `<div class="text-sm text-neutral-800 mb-1.5">⭐ ${place.rating}</div>` : ''}
                        <p class="text-xs text-neutral-500 m-0 leading-relaxed">${place.formatted_address || ''}</p>
                        <a
                          href="https://www.google.com/maps/dir/?api=1&destination=${hotel.lat},${hotel.lng}"
                          target="_blank"
                          rel="noopener noreferrer"
                          class="inline-block mt-3 px-4 py-2 bg-gradient-to-br from-purple-primary to-purple-light text-white text-xs font-semibold font-poppins transition-all duration-300 ease-in-out hover:shadow-md hover:-translate-y-0.5 active:translate-y-0 no-underline rounded-l-3xl"
                          style="border-radius: 18px 0 18px 0"
                        >
                          Get Directions
                        </a>
                      </div>
                    </div>
                  `
                  infoWindowRef.current?.setContent(content)

                  // Add click handlers for photo navigation
                  if (photoUrls.length > 1) {
                    setTimeout(() => {
                      const dots = document.querySelectorAll(`#carousel-${hotel.id} button`)
                      const images = document.querySelectorAll(`#carousel-${hotel.id} img`)

                      dots.forEach((dot, index) => {
                        dot.addEventListener('click', () => {
                          images.forEach(img => img.classList.add('hidden'))
                          dots.forEach(d => {
                            d.classList.remove('w-5')
                            d.classList.add('w-2')
                          })
                          images[index].classList.remove('hidden')
                          dot.classList.add('w-5')
                          dot.classList.remove('w-2')
                        })
                      })
                    }, 100)
                  }
                } else {
                  // Fallback if API fails
                  const fallbackContent = `
                    <div class="max-w-xs font-inter">
                      <div class="p-1">
                        <h3 class="text-base font-bold text-purple-primary mb-2 font-poppins">${hotel.name}</h3>
                        <p class="text-xs text-neutral-500 m-0 leading-relaxed">Premium Cinnamon Hotels property</p>
                      </div>
                    </div>
                  `
                  infoWindowRef.current?.setContent(fallbackContent)
                }
              }
            )
          } else {
            // No Place ID - show basic info
            const basicContent = `
              <div class="max-w-xs font-inter">
                <div class="p-1">
                  <h3 class="text-base font-bold text-purple-primary mb-2 font-poppins">${hotel.name}</h3>
                  <p class="text-xs text-neutral-500 m-0 leading-relaxed">Premium Cinnamon Hotels property</p>
                </div>
              </div>
            `
            infoWindowRef.current.setContent(basicContent)
          }
        })

        markersRef.current.push(marker)
      })
    }
  }, [isLoaded, isVisible])

  if (!isVisible) return null

  return (
    <div className="fixed top-0 left-0 w-2/5 md:w-1/2 h-screen bg-white z-[1000] shadow-lg">
      <button className="absolute top-4 right-4 w-9 h-9 rounded-full bg-white border-none shadow-md flex items-center justify-center cursor-pointer z-10 transition-all duration-200 ease-in-out text-purple-primary hover:bg-purple-primary hover:text-white hover:scale-110 active:scale-95" onClick={onClose} aria-label="Close map">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>

      {/* Hotel Search Dropdown */}
      <div className="absolute top-4 left-4 z-10 w-[calc(100%-100px)] max-w-xs">
        <select
          className="w-full px-4 py-3 pr-9 border-none rounded-3xl bg-gradient-to-br from-purple-primary to-purple-light shadow-lg shadow-purple-secondary/30 text-xs font-poppins font-semibold text-white cursor-pointer transition-all duration-300 ease-in-out hover:shadow-xl hover:shadow-purple-secondary/40 hover:-translate-y-0.5 focus:outline-none focus:shadow-xl focus:shadow-purple-secondary/50 focus:-translate-y-0.5 appearance-none bg-no-repeat bg-right-2"
          style={{
            backgroundImage: "url(\"data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='white' stroke-width='2' stroke-linecap='round' stroke-linejoin='round'%3E%3Cpolyline points='6 9 12 15 18 9'%3E%3C/polyline%3E%3C/svg%3E\")",
            backgroundPosition: 'right 12px center',
            backgroundRepeat: 'no-repeat',
            paddingRight: '36px'
          }}
          value={selectedHotel}
          onChange={(e) => handleHotelSelect(e.target.value)}
        >
          <option value="" style={{ color: '#999' }}>Select a hotel to view</option>
          {HOTELS.map((hotel) => (
            <option key={hotel.id} value={hotel.id} style={{ color: '#333' }}>
              {hotel.name}
            </option>
          ))}
        </select>
      </div>

      <div ref={mapRef} className="w-full h-full"></div>
    </div>
  )
}
