'use client'

import { useState, useEffect } from 'react'

interface TypingGreetingProps {
  text: string
  speed?: number
}

export default function TypingGreeting({ text, speed = 50 }: TypingGreetingProps) {
  const [displayedText, setDisplayedText] = useState('')
  const [currentIndex, setCurrentIndex] = useState(0)

  useEffect(() => {
    if (currentIndex < text.length) {
      const timeout = setTimeout(() => {
        setDisplayedText(prev => prev + text[currentIndex])
        setCurrentIndex(prev => prev + 1)
      }, speed)

      return () => clearTimeout(timeout)
    }
  }, [currentIndex, text, speed])

  return <>{displayedText}</>
}
