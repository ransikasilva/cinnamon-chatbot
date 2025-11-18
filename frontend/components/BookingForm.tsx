'use client'

import { useState } from 'react'

interface BookingFormProps {
  onSubmit: (data: BookingFormData) => void
  selectedHotel?: { id: string; name: string }
  isMaximized?: boolean
}

export interface BookingFormData {
  hotel: string
  hotelName: string
  checkIn: string
  checkOut: string
  adults: number
  children: number
  rooms: number
  specialCode?: string
}

// Only Cinnamon Grand for Type 1 users
const CINNAMON_GRAND = { id: '42169', name: 'Cinnamon Grand Colombo' }

export default function BookingForm({ onSubmit, selectedHotel, isMaximized }: BookingFormProps) {
  // Use selectedHotel if provided, otherwise default to Cinnamon Grand
  const hotel = selectedHotel || CINNAMON_GRAND

  const [checkIn, setCheckIn] = useState('')
  const [checkOut, setCheckOut] = useState('')
  const [adults, setAdults] = useState(2)
  const [children, setChildren] = useState(0)
  const [rooms, setRooms] = useState(1)
  const [specialCode, setSpecialCode] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!checkIn || !checkOut) {
      alert('Please select check-in and check-out dates')
      return
    }

    onSubmit({
      hotel: hotel.id,
      hotelName: hotel.name,
      checkIn,
      checkOut,
      adults,
      children,
      rooms,
      specialCode
    })
  }

  // Get today's date in YYYY-MM-DD format for min date
  const today = new Date().toISOString().split('T')[0]

  return (
    <form
      className="flex flex-col gap-2 px-3 bg-transparent w-full max-w-full box-border animate-[slideInUp_0.4s_ease-out]"
      onSubmit={handleSubmit}
    >
      <div className="text-[13px] font-semibold text-purple-primary font-poppins text-center mb-0 py-2 px-3 bg-[#f9f5fc] rounded-md">
        Complete Your Booking
      </div>

      {/* Check-in Date */}
      <div className="flex flex-col gap-[3px]">
        <label className="text-[10px] font-semibold text-neutral-600 font-inter uppercase tracking-[0.3px]">
          Check-in Date
        </label>
        <input
          type="date"
          className="w-full py-2 px-[10px] text-[13px] border-2 border-neutral-300 rounded-md outline-none transition-all duration-200 font-inter bg-white cursor-pointer font-medium text-neutral-800 box-border relative hover:border-purple-primary focus:border-purple-primary focus:shadow-[0_0_0_3px_rgba(90,48,130,0.1)] [&::-webkit-calendar-picker-indicator]:cursor-pointer [&::-webkit-calendar-picker-indicator]:w-4 [&::-webkit-calendar-picker-indicator]:h-4 [&::-webkit-calendar-picker-indicator]:opacity-60 [&::-webkit-calendar-picker-indicator]:transition-opacity [&::-webkit-calendar-picker-indicator]:duration-200 [&::-webkit-calendar-picker-indicator]:hover:opacity-100 [&::-webkit-datetime-edit-fields-wrapper]:p-0 [&::-webkit-datetime-edit-text]:text-neutral-400 [&::-webkit-datetime-edit-text]:px-[2px] [&::-webkit-datetime-edit-month-field]:text-neutral-800 [&::-webkit-datetime-edit-month-field]:font-semibold [&::-webkit-datetime-edit-day-field]:text-neutral-800 [&::-webkit-datetime-edit-day-field]:font-semibold [&::-webkit-datetime-edit-year-field]:text-neutral-800 [&::-webkit-datetime-edit-year-field]:font-semibold [&::-webkit-datetime-edit-month-field:focus]:bg-[#F5F0FA] [&::-webkit-datetime-edit-month-field:focus]:text-purple-primary [&::-webkit-datetime-edit-month-field:focus]:rounded-[3px] [&::-webkit-datetime-edit-month-field:focus]:outline-none [&::-webkit-datetime-edit-day-field:focus]:bg-[#F5F0FA] [&::-webkit-datetime-edit-day-field:focus]:text-purple-primary [&::-webkit-datetime-edit-day-field:focus]:rounded-[3px] [&::-webkit-datetime-edit-day-field:focus]:outline-none [&::-webkit-datetime-edit-year-field:focus]:bg-[#F5F0FA] [&::-webkit-datetime-edit-year-field:focus]:text-purple-primary [&::-webkit-datetime-edit-year-field:focus]:rounded-[3px] [&::-webkit-datetime-edit-year-field:focus]:outline-none valid:text-purple-primary valid:font-semibold"
          value={checkIn}
          onChange={(e) => setCheckIn(e.target.value)}
          min={today}
          required
        />
      </div>

      {/* Check-out Date */}
      <div className="flex flex-col gap-[3px]">
        <label className="text-[10px] font-semibold text-neutral-600 font-inter uppercase tracking-[0.3px]">
          Check-out Date
        </label>
        <input
          type="date"
          className="w-full py-2 px-[10px] text-[13px] border-2 border-neutral-300 rounded-md outline-none transition-all duration-200 font-inter bg-white cursor-pointer font-medium text-neutral-800 box-border relative hover:border-purple-primary focus:border-purple-primary focus:shadow-[0_0_0_3px_rgba(90,48,130,0.1)] [&::-webkit-calendar-picker-indicator]:cursor-pointer [&::-webkit-calendar-picker-indicator]:w-4 [&::-webkit-calendar-picker-indicator]:h-4 [&::-webkit-calendar-picker-indicator]:opacity-60 [&::-webkit-calendar-picker-indicator]:transition-opacity [&::-webkit-calendar-picker-indicator]:duration-200 [&::-webkit-calendar-picker-indicator]:hover:opacity-100 [&::-webkit-datetime-edit-fields-wrapper]:p-0 [&::-webkit-datetime-edit-text]:text-neutral-400 [&::-webkit-datetime-edit-text]:px-[2px] [&::-webkit-datetime-edit-month-field]:text-neutral-800 [&::-webkit-datetime-edit-month-field]:font-semibold [&::-webkit-datetime-edit-day-field]:text-neutral-800 [&::-webkit-datetime-edit-day-field]:font-semibold [&::-webkit-datetime-edit-year-field]:text-neutral-800 [&::-webkit-datetime-edit-year-field]:font-semibold [&::-webkit-datetime-edit-month-field:focus]:bg-[#F5F0FA] [&::-webkit-datetime-edit-month-field:focus]:text-purple-primary [&::-webkit-datetime-edit-month-field:focus]:rounded-[3px] [&::-webkit-datetime-edit-month-field:focus]:outline-none [&::-webkit-datetime-edit-day-field:focus]:bg-[#F5F0FA] [&::-webkit-datetime-edit-day-field:focus]:text-purple-primary [&::-webkit-datetime-edit-day-field:focus]:rounded-[3px] [&::-webkit-datetime-edit-day-field:focus]:outline-none [&::-webkit-datetime-edit-year-field:focus]:bg-[#F5F0FA] [&::-webkit-datetime-edit-year-field:focus]:text-purple-primary [&::-webkit-datetime-edit-year-field:focus]:rounded-[3px] [&::-webkit-datetime-edit-year-field:focus]:outline-none valid:text-purple-primary valid:font-semibold"
          value={checkOut}
          onChange={(e) => setCheckOut(e.target.value)}
          min={checkIn || today}
          required
        />
      </div>

      {/* Guests */}
      <div className="flex flex-col gap-[3px]">
        <label className="text-[10px] font-semibold text-neutral-600 font-inter uppercase tracking-[0.3px]">
          Guests
        </label>
        <div className={`grid grid-cols-1 gap-[5px] ${isMaximized ? 'md:grid-cols-3 md:gap-3' : ''}`}>
          <div className="flex flex-row items-center justify-between gap-[6px] w-full">
            <span className="text-[10px] text-neutral-600 font-inter font-semibold uppercase tracking-[0.2px] flex-1 text-left min-w-0">
              Adults
            </span>
            <div className="flex items-center justify-between bg-white border border-neutral-300 rounded-[5px] p-[3px] gap-[5px] min-w-[85px] flex-shrink-0">
              <button
                type="button"
                className="w-[22px] h-[22px] bg-white border-0 rounded text-purple-primary text-sm font-bold cursor-pointer flex items-center justify-center transition-all duration-150 flex-shrink-0 hover:bg-purple-primary hover:text-white active:scale-90"
                onClick={() => setAdults(Math.max(1, adults - 1))}
              >
                -
              </button>
              <span className="text-[13px] font-bold text-neutral-800 min-w-[18px] text-center font-poppins">
                {adults}
              </span>
              <button
                type="button"
                className="w-[22px] h-[22px] bg-white border-0 rounded text-purple-primary text-sm font-bold cursor-pointer flex items-center justify-center transition-all duration-150 flex-shrink-0 hover:bg-purple-primary hover:text-white active:scale-90"
                onClick={() => setAdults(Math.min(3, adults + 1))}
              >
                +
              </button>
            </div>
          </div>

          <div className="flex flex-row items-center justify-between gap-[6px] w-full">
            <span className="text-[10px] text-neutral-600 font-inter font-semibold uppercase tracking-[0.2px] flex-1 text-left min-w-0">
              Children
            </span>
            <div className="flex items-center justify-between bg-white border border-neutral-300 rounded-[5px] p-[3px] gap-[5px] min-w-[85px] flex-shrink-0">
              <button
                type="button"
                className="w-[22px] h-[22px] bg-white border-0 rounded text-purple-primary text-sm font-bold cursor-pointer flex items-center justify-center transition-all duration-150 flex-shrink-0 hover:bg-purple-primary hover:text-white active:scale-90"
                onClick={() => setChildren(Math.max(0, children - 1))}
              >
                -
              </button>
              <span className="text-[13px] font-bold text-neutral-800 min-w-[18px] text-center font-poppins">
                {children}
              </span>
              <button
                type="button"
                className="w-[22px] h-[22px] bg-white border-0 rounded text-purple-primary text-sm font-bold cursor-pointer flex items-center justify-center transition-all duration-150 flex-shrink-0 hover:bg-purple-primary hover:text-white active:scale-90"
                onClick={() => setChildren(Math.min(10, children + 1))}
              >
                +
              </button>
            </div>
          </div>

          <div className="flex flex-row items-center justify-between gap-[6px] w-full">
            <span className="text-[10px] text-neutral-600 font-inter font-semibold uppercase tracking-[0.2px] flex-1 text-left min-w-0">
              Rooms
            </span>
            <div className="flex items-center justify-between bg-white border border-neutral-300 rounded-[5px] p-[3px] gap-[5px] min-w-[85px] flex-shrink-0">
              <button
                type="button"
                className="w-[22px] h-[22px] bg-white border-0 rounded text-purple-primary text-sm font-bold cursor-pointer flex items-center justify-center transition-all duration-150 flex-shrink-0 hover:bg-purple-primary hover:text-white active:scale-90"
                onClick={() => setRooms(Math.max(1, rooms - 1))}
              >
                -
              </button>
              <span className="text-[13px] font-bold text-neutral-800 min-w-[18px] text-center font-poppins">
                {rooms}
              </span>
              <button
                type="button"
                className="w-[22px] h-[22px] bg-white border-0 rounded text-purple-primary text-sm font-bold cursor-pointer flex items-center justify-center transition-all duration-150 flex-shrink-0 hover:bg-purple-primary hover:text-white active:scale-90"
                onClick={() => setRooms(Math.min(5, rooms + 1))}
              >
                +
              </button>
            </div>
          </div>
        </div>
      </div>

      {/* Special Code */}
      <div className="flex flex-col gap-[3px]">
        <label className="text-[10px] font-semibold text-neutral-600 font-inter uppercase tracking-[0.3px]">
          Promo Code (Optional)
        </label>
        <input
          type="text"
          className="w-full py-2 px-[10px] text-[13px] border border-neutral-300 rounded-md outline-none transition-all duration-200 font-inter box-border font-medium text-neutral-800 focus:border-purple-primary focus:shadow-[0_0_0_2px_rgba(107,44,145,0.08)] placeholder:text-neutral-400 placeholder:font-normal placeholder:text-[10px]"
          value={specialCode}
          onChange={(e) => setSpecialCode(e.target.value)}
          placeholder="Enter promo code"
        />
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        className="w-full py-[10px] px-[18px] bg-gradient-to-br from-purple-primary to-purple-light text-white border-0 rounded-skewed text-xs font-bold cursor-pointer transition-all duration-200 font-poppins shadow-[0_2px_8px_rgba(107,44,145,0.25)] mt-1 uppercase tracking-[0.5px] hover:-translate-y-0.5 hover:shadow-[0_4px_12px_rgba(107,44,145,0.35)] active:translate-y-0"
      >
        Continue to Reservation
      </button>
    </form>
  )
}
