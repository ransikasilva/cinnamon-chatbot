'use client'

import styles from './ActivityCard.module.css'
import { IoTimeOutline, IoSunnyOutline, IoMoonOutline, IoCloudyOutline } from 'react-icons/io5'

interface ActivityCardProps {
  activity: {
    activity: string
    duration: string
    best_time: string
    price: number
  }
  onClick?: () => void
}

export default function ActivityCard({ activity, onClick }: ActivityCardProps) {
  const getTimeIcon = (time: string) => {
    const timeLower = time.toLowerCase()
    if (timeLower.includes('morning')) return <IoSunnyOutline />
    if (timeLower.includes('afternoon')) return <IoCloudyOutline />
    if (timeLower.includes('evening')) return <IoMoonOutline />
    return <IoTimeOutline />
  }

  return (
    <div className={styles.activityCard} onClick={onClick}>
      <div className={styles.activityHeader}>
        <h4 className={styles.activityName}>{activity.activity}</h4>
        <span className={styles.price}>${activity.price}</span>
      </div>

      <div className={styles.activityDetails}>
        <div className={styles.detailItem}>
          <IoTimeOutline className={styles.icon} />
          <span>{activity.duration}</span>
        </div>
        <div className={styles.detailItem}>
          {getTimeIcon(activity.best_time)}
          <span>{activity.best_time}</span>
        </div>
      </div>
    </div>
  )
}
