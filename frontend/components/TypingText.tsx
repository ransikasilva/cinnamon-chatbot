'use client'

import { useState, useEffect } from 'react'

interface TypingTextProps {
  text: string
  speed?: number
  onComplete?: () => void
}

export default function TypingText({ text, speed = 30, onComplete }: TypingTextProps) {
  const [displayedText, setDisplayedText] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    if (!text) return

    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(prev => prev + text[currentIndex])
        setCurrentIndex(prev => prev + 1)
      }, speed)

      return () => clearTimeout(timeout)
    } else if (onComplete && currentIndex === text.length && currentIndex > 0) {
      const callComplete = setTimeout(() => {
        onComplete()
      }, 0)
      return () => clearTimeout(callComplete)
    }
  }, [currentIndex, text, speed, onComplete])

  // Reset when text changes
  useEffect(() => {
    setDisplayedText('')
    setCurrentIndex(0)
  }, [text])

  return <>{displayedText}</>
}
