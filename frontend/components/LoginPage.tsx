'use client'

import { useState } from 'react'
import styles from './LoginPage.module.css'

interface LoginPageProps {
  onLogin: (email: string, userType: string) => void
}

const VALID_USERS = {
  'newbooking@demo.com': 'new_booking',
  'explorer@demo.com': 'explorer',
  'editbooking@demo.com': 'edit_booking'
}

export default function LoginPage({ onLogin }: LoginPageProps) {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    const userType = VALID_USERS[email.toLowerCase().trim() as keyof typeof VALID_USERS]

    if (userType) {
      setError('')
      onLogin(email, userType)
    } else {
      setError('Invalid email. Please use a valid demo email.')
    }
  }

  return (
    <div className={styles.loginContainer}>
      <div className={styles.loginContent}>
        <div className={styles.avatarContainer}>
          <img src="/ayu.jpg" alt="Maya" className={styles.avatar} />
        </div>

        <h1 className={styles.greeting}>Hi! I am Maya</h1>
        <p className={styles.subtitle}>Welcome to Cinnamon Hotels</p>

        <form onSubmit={handleSubmit} className={styles.loginForm}>
          <div className={styles.formGroup}>
            <label htmlFor="email" className={styles.label}>Email Address</label>
            <input
              type="email"
              id="email"
              className={styles.emailInput}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="Enter your email"
              required
            />
          </div>

          {error && <div className={styles.errorMessage}>{error}</div>}

          <button type="submit" className={styles.loginButton}>
            Sign In
          </button>
        </form>
      </div>
    </div>
  )
}
