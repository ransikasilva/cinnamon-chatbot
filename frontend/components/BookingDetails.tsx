'use client'

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
    <div className="bg-white border border-neutral-200 rounded-xl md:rounded-2xl p-0 my-3 overflow-hidden shadow-md">
      <div className="bg-gradient-to-br from-purple-primary to-purple-light px-4.5 py-4 md:px-6 md:py-5 flex justify-between items-center">
        <div className="flex flex-col gap-1">
          <span className="text-[11px] md:text-xs text-white/80 font-inter uppercase tracking-wide font-medium">
            Booking Reference
          </span>
          <span className="text-base md:text-lg text-white font-poppins font-bold tracking-wide">
            {bookingRef}
          </span>
        </div>
        {isUpdated && (
          <div className="flex items-center gap-1.5 bg-white/20 px-3 py-1.5 md:px-3.5 md:py-2 rounded-full text-xs md:text-[13px] text-white font-semibold font-inter">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="flex-shrink-0">
              <polyline points="20 6 9 17 4 12"></polyline>
            </svg>
            Updated
          </div>
        )}
      </div>

      <div className="h-px bg-neutral-200"></div>

      <div className="px-4.5 py-4.5 md:px-6 md:py-6 flex flex-col gap-4 md:gap-4.5">
        <div className="flex items-start gap-3">
          <div className="w-10 h-10 md:w-11 md:h-11 rounded-[10px] bg-purple-primary/10 flex items-center justify-center flex-shrink-0 text-purple-primary">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z"></path>
              <polyline points="9 22 9 12 15 12 15 22"></polyline>
            </svg>
          </div>
          <div className="flex flex-col gap-1 flex-1">
            <span className="text-[11px] md:text-xs text-neutral-500 font-inter uppercase tracking-wide font-semibold">
              Hotel
            </span>
            <span className="text-sm md:text-[15px] text-neutral-800 font-poppins font-semibold leading-snug">
              {hotel}
            </span>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <div className="w-10 h-10 md:w-11 md:h-11 rounded-[10px] bg-purple-primary/10 flex items-center justify-center flex-shrink-0 text-purple-primary">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
          </div>
          <div className="flex flex-col gap-1 flex-1">
            <span className="text-[11px] md:text-xs text-neutral-500 font-inter uppercase tracking-wide font-semibold">
              Check-in
            </span>
            <span className="text-sm md:text-[15px] text-neutral-800 font-poppins font-semibold leading-snug">
              {checkIn}
            </span>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <div className="w-10 h-10 md:w-11 md:h-11 rounded-[10px] bg-purple-primary/10 flex items-center justify-center flex-shrink-0 text-purple-primary">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <rect x="3" y="4" width="18" height="18" rx="2" ry="2"></rect>
              <line x1="16" y1="2" x2="16" y2="6"></line>
              <line x1="8" y1="2" x2="8" y2="6"></line>
              <line x1="3" y1="10" x2="21" y2="10"></line>
            </svg>
          </div>
          <div className="flex flex-col gap-1 flex-1">
            <span className="text-[11px] md:text-xs text-neutral-500 font-inter uppercase tracking-wide font-semibold">
              Check-out
            </span>
            <span className="text-sm md:text-[15px] text-neutral-800 font-poppins font-semibold leading-snug">
              {checkOut}
            </span>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <div className="w-10 h-10 md:w-11 md:h-11 rounded-[10px] bg-purple-primary/10 flex items-center justify-center flex-shrink-0 text-purple-primary">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"></path>
              <circle cx="12" cy="7" r="4"></circle>
            </svg>
          </div>
          <div className="flex flex-col gap-1 flex-1">
            <span className="text-[11px] md:text-xs text-neutral-500 font-inter uppercase tracking-wide font-semibold">
              Guests
            </span>
            <span className="text-sm md:text-[15px] text-neutral-800 font-poppins font-semibold leading-snug">
              {guests}
            </span>
          </div>
        </div>

        <div className="flex items-start gap-3">
          <div className="w-10 h-10 md:w-11 md:h-11 rounded-[10px] bg-purple-primary/10 flex items-center justify-center flex-shrink-0 text-purple-primary">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
              <path d="M2 10s3-3 10-3 10 3 10 3-3 3-10 3-10-3-10-3Z"></path>
              <path d="M12 13v8"></path>
            </svg>
          </div>
          <div className="flex flex-col gap-1 flex-1">
            <span className="text-[11px] md:text-xs text-neutral-500 font-inter uppercase tracking-wide font-semibold">
              Room Type
            </span>
            <span className="text-sm md:text-[15px] text-neutral-800 font-poppins font-semibold leading-snug">
              {room}
            </span>
          </div>
        </div>
      </div>

      <div className="bg-neutral-50 px-4.5 py-3.5 md:px-6 md:py-4 border-t border-neutral-200">
        <p className="m-0 text-[13px] md:text-sm text-neutral-600 font-inter font-medium text-center">
          What would you like to change?
        </p>
      </div>
    </div>
  )
}
