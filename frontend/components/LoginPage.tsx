'use client'

import { useState } from 'react'
import styles from './LoginPage.module.css'

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
    <div className={styles.loginContainer}>
      <div className={styles.loginContent}>
        <div className={styles.avatarContainer}>
          <img src="/ayunew.png" alt="Maya" className={styles.avatar} />
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
