'use client'

import { useState } from 'react'
import styles from './Login.module.css'

interface LoginProps {
  onLogin: (email: string) => void
}

export default function Login({ onLogin }: LoginProps) {
  const [email, setEmail] = useState('')
  const [error, setError] = useState('')

  const validateEmail = (email: string) => {
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
    return emailRegex.test(email)
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()

    if (!email.trim()) {
      setError('Please enter your email address')
      return
    }

    if (!validateEmail(email)) {
      setError('Please enter a valid email address')
      return
    }

    setError('')
    onLogin(email)
  }

  return (
    <div className={styles.loginContainer}>
      <div className={styles.loginBox}>
        <div className={styles.logoSection}>
          <img src="/ayunew.png" alt="Cinnamon Hotels" className={styles.logo} />
          <h1 className={styles.title}>Welcome to Cinnamon Hotels</h1>
          <p className={styles.subtitle}>Your Virtual Concierge</p>
        </div>

        <form onSubmit={handleSubmit} className={styles.loginForm}>
          <div className={styles.inputGroup}>
            <label htmlFor="email" className={styles.label}>
              Email Address
            </label>
            <input
              type="email"
              id="email"
              value={email}
              onChange={(e) => {
                setEmail(e.target.value)
                setError('')
              }}
              className={styles.input}
              placeholder="Enter your email"
              autoFocus
            />
            {error && <p className={styles.error}>{error}</p>}
          </div>

          <button type="submit" className={styles.submitButton}>
            Start Chat
          </button>
        </form>

        <p className={styles.privacy}>
          We respect your privacy. Your email is only used for this chat session.
        </p>
      </div>
    </div>
  )
}
