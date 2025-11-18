'use client'

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
    <div
      className="bg-white border border-neutral-200 rounded-xl p-0 my-3 transition-all duration-300 cursor-pointer overflow-hidden hover:shadow-xl hover:shadow-purple-secondary/15 hover:border-purple-primary hover:-translate-y-0.5 group"
      onClick={onClick}
    >
      {room?.image && (
        <div className="w-full h-[200px] overflow-hidden bg-neutral-100">
          <img
            src={room.image}
            alt={room.type}
            className="w-full h-full object-cover transition-transform duration-300 group-hover:scale-105"
          />
        </div>
      )}

      <div className="flex justify-between items-start mb-3 pt-4.5 px-4.5">
        <div className="flex-1">
          <h3 className="text-lg font-bold text-neutral-800 m-0 mb-1.5 font-poppins">
            {hotel.name}
          </h3>
          <div className="flex items-center gap-1.5 mb-1.5">
            <IoLocation className="text-purple-primary text-sm" />
            <span className="text-[13px] text-neutral-600 font-inter">
              {hotel.region} • {hotel.type}
            </span>
          </div>
          <div className="flex gap-0.5 mt-1">
            {Array.from({ length: hotel.stars }).map((_, i) => (
              <IoStar key={i} className="text-yellow-500 text-sm" />
            ))}
          </div>
        </div>
      </div>

      <p className="text-[13px] text-neutral-600 my-3 px-4.5 leading-relaxed font-inter">
        {hotel.description}
      </p>

      <div className="flex flex-wrap gap-2 my-3 px-4.5">
        {hotel.amenities.slice(0, 4).map((amenity, index) => (
          <span
            key={index}
            className="bg-neutral-100 text-neutral-600 px-2.5 py-1 rounded-md text-[11px] font-medium font-inter"
          >
            {amenity}
          </span>
        ))}
      </div>

      {room && (
        <div className="border-t border-neutral-200 p-4.5 mt-3">
          <div className="flex justify-between items-center mb-3">
            <div className="text-sm font-semibold text-neutral-800 font-poppins">
              {room.type}
            </div>
            <div className="flex gap-1.5">
              <span
                className={`px-3 py-1 rounded-md text-[11px] font-bold font-inter uppercase tracking-wide ${
                  room.availability === 'Available'
                    ? 'bg-success-light text-success'
                    : 'bg-warning-light text-warning'
                }`}
              >
                {room.availability}
              </span>
            </div>
          </div>

          {nights && (
            <div className="mt-3 bg-purple-primary/10 px-3 py-2.5 rounded-lg text-center">
              <span className="text-[13px] text-purple-primary font-semibold font-inter">
                {nights} night{nights > 1 ? 's' : ''} stay
              </span>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
