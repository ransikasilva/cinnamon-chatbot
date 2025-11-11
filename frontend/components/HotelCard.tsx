'use client'

import styles from './HotelCard.module.css'
import { IoLocation, IoStar } from 'react-icons/io5'

interface HotelCardProps {
  hotel: {
    id: string
    name: string
    region: string
    type: string
    stars: number
    description: string
    amenities: string[]
  }
  room?: {
    type: string
    price: number
    availability: string
    image?: string
  }
  nights?: number
  totalCost?: number
  onClick?: () => void
}

export default function HotelCard({ hotel, room, nights, totalCost, onClick }: HotelCardProps) {
  return (
    <div className={styles.hotelCard} onClick={onClick}>
      {room?.image && (
        <div className={styles.roomImageContainer}>
          <img src={room.image} alt={room.type} className={styles.roomImage} />
        </div>
      )}

      <div className={styles.hotelHeader}>
        <div className={styles.hotelInfo}>
          <h3 className={styles.hotelName}>{hotel.name}</h3>
          <div className={styles.locationRow}>
            <IoLocation className={styles.locationIcon} />
            <span className={styles.location}>{hotel.region} • {hotel.type}</span>
          </div>
          <div className={styles.starsRow}>
            {Array.from({ length: hotel.stars }).map((_, i) => (
              <IoStar key={i} className={styles.starIcon} />
            ))}
          </div>
        </div>
      </div>

      <p className={styles.description}>{hotel.description}</p>

      <div className={styles.amenities}>
        {hotel.amenities.slice(0, 4).map((amenity, index) => (
          <span key={index} className={styles.amenityBadge}>
            {amenity}
          </span>
        ))}
      </div>

      {room && (
        <div className={styles.roomSection}>
          <div className={styles.roomInfo}>
            <div className={styles.roomType}>{room.type}</div>
            <div className={styles.availability}>
              <span className={room.availability === 'Available' ? styles.availableBadge : styles.limitedBadge}>
                {room.availability}
              </span>
            </div>
          </div>

          <div className={styles.pricingRow}>
            <div className={styles.priceInfo}>
              <span className={styles.priceLabel}>Per Night</span>
              <span className={styles.price}>${room.price}</span>
            </div>

            {nights && totalCost && (
              <div className={styles.totalInfo}>
                <span className={styles.totalLabel}>{nights} nights total</span>
                <span className={styles.totalPrice}>${totalCost}</span>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
