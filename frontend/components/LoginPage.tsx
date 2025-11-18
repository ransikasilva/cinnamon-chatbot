'use client'

import { useState } from 'react'

interface LoginPageProps {
  onLogin: (email: string, userType: string) => void
}

export default function LoginPage({ onLogin }: LoginPageProps) {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const trimmedEmail = email.toLowerCase().trim()

    // Basic email validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/

    if (!emailRegex.test(trimmedEmail)) {
      setError('Please enter a valid email address.')
      return
    }

    setError('')
    // Use 'general' as default user type for all users
    onLogin(trimmedEmail, 'general')
  }

  return (
    <div className="w-full h-full flex items-center justify-center bg-cover bg-center bg-no-repeat relative"
         style={{backgroundImage: "url('/cinnamonlife.jpg')"}}>
      {/* Purple overlay with blur */}
      <div className="absolute inset-0 bg-purple-secondary/70 backdrop-blur-sm"></div>

      {/* Login card */}
      <div className="relative z-10 bg-white p-7 md:p-9 rounded-2xl shadow-2xl max-w-[340px] md:max-w-[400px] w-[90%]">
        {/* Avatar */}
        <div className="text-center mb-4">
          <img
            src="/ayunew.png"
            alt="Maya"
            className="w-20 h-20 md:w-24 md:h-24 rounded-full object-cover mx-auto"
          />
        </div>

        {/* Greeting */}
        <h1 className="text-[22px] md:text-[26px] font-bold text-purple-primary text-center mb-1 font-poppins">
          Hi! I am Maya
        </h1>
        <p className="text-sm md:text-[15px] text-neutral-500 text-center mb-6 font-inter">
          Welcome to Cinnamon Hotels
        </p>

        {/* Form */}
        <form onSubmit={handleSubmit} className="flex flex-col gap-4">
          <div className="flex flex-col gap-1.5">
            <label
              htmlFor="email"
              className="text-[13px] md:text-sm font-semibold text-neutral-800 font-inter"
            >
              Email Address
            </label>
            <input
              type="email"
              id="email"
              className="w-full px-3.5 py-3 md:px-4 md:py-3.5 text-sm md:text-[15px] border-2 border-neutral-200 rounded-lg outline-none transition-all duration-300 font-inter focus:border-purple-primary focus:ring-4 focus:ring-purple-secondary/10"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
            />
          </div>

          {/* Error message */}
          {error && (
            <div className="bg-red-50 text-red-700 px-3 py-2.5 rounded-md text-xs font-medium font-inter text-center">
              {error}
            </div>
          )}

          {/* Submit button */}
          <button
            type="submit"
            className="w-full px-5 py-3.5 md:px-6 md:py-4 bg-gradient-to-br from-purple-primary to-purple-light text-white border-none rounded-[25px_0_25px_0] text-[15px] md:text-base font-bold cursor-pointer transition-all duration-300 font-poppins uppercase tracking-wide shadow-lg shadow-purple-secondary/40 hover:-translate-y-0.5 hover:shadow-xl hover:shadow-purple-secondary/50 active:translate-y-0"
          >
            Sign In
          </button>
        </form>
      </div>
    </div>
  )
}
