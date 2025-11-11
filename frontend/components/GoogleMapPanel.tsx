'use client'

import { useEffect, useRef, useState } from 'react'
import styles from './GoogleMapPanel.module.css'

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
    id: '42170',
    name: 'Cinnamon Lakeside Colombo',
    lat: 6.9271,
    lng: 79.8612,
    placeId: 'ChIJv1bUJj1Z4joRyDlJ1LITJZc'
  },
  {
    id: '42171',
    name: 'Cinnamon Bey Beruwala',
    lat: 6.4787,
    lng: 79.9820,
    placeId: 'ChIJvRNrbpAu4joRfzR3iJN4iJ8'
  },
  {
    id: '42174',
    name: 'Cinnamon Life',
    lat: 6.9207,
    lng: 79.8458,
    placeId: 'ChIJZ0NJ0z1Z4joRxqYXI3CeGmY'
  },
  {
    id: '42175',
    name: 'Cinnamon Wild Yala',
    lat: 6.4456,
    lng: 81.5314,
    placeId: 'ChIJS1hoz4yD5joREWNrIi3i8aM'
  },
  {
    id: '42176',
    name: 'Cinnamon Citadel Kandy',
    lat: 7.3063,
    lng: 80.6238,
    placeId: 'ChIJ-XGT93po4zoRHShxzlBmszM'
  },
  {
    id: '42177',
    name: 'Habarana Village by Cinnamon',
    lat: 8.0333,
    lng: 80.7500,
    placeId: 'ChIJV9-azWWf_DoR6x941O3kB-4'
  },
  {
    id: '42178',
    name: 'Trinco Blu by Cinnamon',
    lat: 8.6193,
    lng: 81.2184,
    placeId: 'ChIJKZE_cE-8-zoR1rF4o6Ud6NA'
  },
  {
    id: '42179',
    name: 'Hikka Tranz by Cinnamon',
    lat: 6.1397,
    lng: 80.1004,
    placeId: 'ChIJ-T8ImsJ34ToRp_ivcngipSU'
  }
]

export default function GoogleMapPanel({ isVisible, onClose }: GoogleMapPanelProps) {
  const mapRef = useRef<HTMLDivElement>(null)
  const googleMapRef = useRef<google.maps.Map | null>(null)
  const markersRef = useRef<google.maps.marker.AdvancedMarkerElement[]>([])
  const infoWindowRef = useRef<google.maps.InfoWindow | null>(null)
  const [isLoaded, setIsLoaded] = useState(false)

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
      script.src = `https://maps.googleapis.com/maps/api/js?key=AIzaSyBlAOzYVavkFKdyByg8DOPJXdwYd-dsJMM&libraries=places,marker&v=weekly`
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
        markerContent.className = styles.markerPin
        markerContent.innerHTML = `
          <div class="${styles.pinIcon}">
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
            <div class="${styles.infoWindow}">
              <div class="${styles.infoLoading}">Loading...</div>
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
                      <div class="${styles.photoCarousel}" id="carousel-${hotel.id}">
                        <div class="${styles.photoContainer}">
                          ${photoUrls.map((url, idx) => `
                            <img src="${url}" alt="${hotel.name}" class="${styles.infoImage} ${idx === 0 ? styles.activePhoto : ''}" data-index="${idx}" />
                          `).join('')}
                        </div>
                        ${photoUrls.length > 1 ? `
                          <div class="${styles.photoNav}">
                            ${photoUrls.map((_, idx) => `
                              <button class="${styles.photoDot} ${idx === 0 ? styles.activeDot : ''}" data-index="${idx}"></button>
                            `).join('')}
                          </div>
                        ` : ''}
                      </div>
                    `
                  }

                  const content = `
                    <div class="${styles.infoWindow}">
                      ${photosHTML}
                      <div class="${styles.infoContent}">
                        <h3 class="${styles.infoTitle}">${hotel.name}</h3>
                        ${place.rating ? `<div class="${styles.infoRating}">⭐ ${place.rating}</div>` : ''}
                        <p class="${styles.infoAddress}">${place.formatted_address || ''}</p>
                      </div>
                    </div>
                  `
                  infoWindowRef.current?.setContent(content)

                  // Add click handlers for photo navigation
                  if (photoUrls.length > 1) {
                    setTimeout(() => {
                      const dots = document.querySelectorAll(`#carousel-${hotel.id} .${styles.photoDot}`)
                      const images = document.querySelectorAll(`#carousel-${hotel.id} .${styles.infoImage}`)

                      dots.forEach((dot, index) => {
                        dot.addEventListener('click', () => {
                          images.forEach(img => img.classList.remove(styles.activePhoto))
                          dots.forEach(d => d.classList.remove(styles.activeDot))
                          images[index].classList.add(styles.activePhoto)
                          dot.classList.add(styles.activeDot)
                        })
                      })
                    }, 100)
                  }
                } else {
                  // Fallback if API fails
                  const fallbackContent = `
                    <div class="${styles.infoWindow}">
                      <div class="${styles.infoContent}">
                        <h3 class="${styles.infoTitle}">${hotel.name}</h3>
                        <p class="${styles.infoAddress}">Premium Cinnamon Hotels property</p>
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
              <div class="${styles.infoWindow}">
                <div class="${styles.infoContent}">
                  <h3 class="${styles.infoTitle}">${hotel.name}</h3>
                  <p class="${styles.infoAddress}">Premium Cinnamon Hotels property</p>
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
    <div className={styles.mapPanel}>
      <button className={styles.closeButton} onClick={onClose} aria-label="Close map">
        <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
          <line x1="18" y1="6" x2="6" y2="18"></line>
          <line x1="6" y1="6" x2="18" y2="18"></line>
        </svg>
      </button>
      <div ref={mapRef} className={styles.map}></div>
    </div>
  )
}
