'use client'

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
    <div
      className="bg-gradient-to-br from-white to-purple-50 border border-neutral-200 rounded-[10px] px-4 py-3.5 my-2 transition-all duration-300 cursor-pointer hover:shadow-lg hover:shadow-purple-secondary/12 hover:border-purple-light hover:translate-x-1"
      onClick={onClick}
    >
      <div className="flex justify-between items-center mb-2.5">
        <h4 className="text-[15px] font-semibold text-neutral-800 m-0 font-poppins flex-1">
          {activity.activity}
        </h4>
      </div>

      <div className="flex gap-4 flex-wrap">
        <div className="flex items-center gap-1.5 text-xs text-neutral-600 font-inter">
          <IoTimeOutline className="text-purple-light text-sm" />
          <span>{activity.duration}</span>
        </div>
        <div className="flex items-center gap-1.5 text-xs text-neutral-600 font-inter">
          <span className="text-purple-light text-sm">{getTimeIcon(activity.best_time)}</span>
          <span>{activity.best_time}</span>
        </div>
      </div>
    </div>
  )
}
