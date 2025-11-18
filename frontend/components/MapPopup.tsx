'use client'

interface MapPopupProps {
  isOpen: boolean
  onClose: () => void
}

export default function MapPopup({ isOpen, onClose }: MapPopupProps) {
  if (!isOpen) return null

  return (
    <div className="fixed inset-0 bg-black/70 flex items-center justify-center z-[2000] animate-fadeIn" onClick={onClose}>
      <div className="bg-white rounded-[20px] w-[90%] max-w-[1100px] max-h-[90vh] overflow-hidden relative shadow-2xl animate-slideUp" onClick={(e) => e.stopPropagation()}>
        <button className="absolute top-4 right-4 bg-white border-none w-10 h-10 rounded-full cursor-pointer flex items-center justify-center shadow-md z-10 transition-all duration-200 hover:bg-neutral-100 hover:scale-110" onClick={onClose} aria-label="Close map">
          <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" className="text-neutral-700">
            <line x1="18" y1="6" x2="6" y2="18"></line>
            <line x1="6" y1="6" x2="18" y2="18"></line>
          </svg>
        </button>

        <div className="flex h-[85vh] max-h-[700px] md:flex-row flex-col">
          <div className="flex-1 bg-neutral-100 flex items-center justify-center p-5 border-r border-neutral-200 md:border-r md:border-b-0 border-b border-neutral-200">
            <img src="/map.png" alt="Sri Lanka Travel Map" className="w-full h-full object-contain" />
          </div>

          <div className="flex-1 flex flex-col bg-white">
            <div className="bg-purple-primary p-5 flex items-center justify-center">
              <div className="w-[60px] h-[60px] rounded-full bg-white overflow-hidden flex items-center justify-center shadow-lg">
                <img src="/ayunew.png" alt="Concierge" className="w-full h-full object-cover" />
              </div>
            </div>

            <div className="flex-1 overflow-y-auto p-[30px] md:p-5 scrollbar-thin scrollbar-thumb-purple-light scrollbar-track-transparent">
              <p className="text-sm leading-relaxed text-neutral-800 mb-6 font-inter bg-purple-light/20 p-5 rounded-lg border-l-4 border-purple-primary">
                Welcome to Sri Lanka, solo adventurer! 🙏 This teardrop island offers
                ancient temples, pristine beaches, wildlife safaris, and warm
                hospitality - perfect for your first solo journey. Let me help you craft
                an unforgettable experience across this diverse paradise.
              </p>

              <div className="mt-2.5">
                <h3 className="text-lg font-bold text-purple-primary mb-5 font-poppins border-b-2 border-purple-primary pb-2">Quick Trip Essentials for Solo Travelers</h3>

                <h4 className="text-sm font-semibold text-neutral-800 mt-4 mb-2 font-poppins md:text-base">Best Time to Visit:</h4>
                <ul className="list-none p-0 mb-4">
                  <li className="text-sm leading-relaxed text-neutral-600 my-1.5 pl-5 relative font-inter before:content-['•'] before:absolute before:left-0 before:text-purple-primary before:font-bold before:text-lg md:text-base">West/South Coast: November - April</li>
                  <li className="text-sm leading-relaxed text-neutral-600 my-1.5 pl-5 relative font-inter before:content-['•'] before:absolute before:left-0 before:text-purple-primary before:font-bold before:text-lg md:text-base">East Coast: April - September</li>
                  <li className="text-sm leading-relaxed text-neutral-600 my-1.5 pl-5 relative font-inter before:content-['•'] before:absolute before:left-0 before:text-purple-primary before:font-bold before:text-lg md:text-base">Hill Country: Year-round</li>
                </ul>

                <h4 className="text-sm font-semibold text-neutral-800 mt-4 mb-2 font-poppins md:text-base">Getting Around:</h4>
                <ul className="list-none p-0 mb-4">
                  <li className="text-sm leading-relaxed text-neutral-600 my-1.5 pl-5 relative font-inter before:content-['•'] before:absolute before:left-0 before:text-purple-primary before:font-bold before:text-lg md:text-base">Trains: Scenic & budget-friendly (book ahead!)</li>
                  <li className="text-sm leading-relaxed text-neutral-600 my-1.5 pl-5 relative font-inter before:content-['•'] before:absolute before:left-0 before:text-purple-primary before:font-bold before:text-lg md:text-base">Private driver: Comfortable for 3-7 days</li>
                  <li className="text-sm leading-relaxed text-neutral-600 my-1.5 pl-5 relative font-inter before:content-['•'] before:absolute before:left-0 before:text-purple-primary before:font-bold before:text-lg md:text-base">Tuk-tuks: Great for short distances</li>
                  <li className="text-sm leading-relaxed text-neutral-600 my-1.5 pl-5 relative font-inter before:content-['•'] before:absolute before:left-0 before:text-purple-primary before:font-bold before:text-lg md:text-base">Domestic flights: Colombo to Jaffna saves time</li>
                </ul>

                <h4 className="text-sm font-semibold text-neutral-800 mt-4 mb-2 font-poppins md:text-base">Solo Traveler Tips:</h4>
                <ul className="list-none p-0">
                  <li className="text-sm leading-relaxed text-neutral-600 my-2 font-inter md:text-base">✓ Sri Lankans are incredibly friendly and helpful</li>
                  <li className="text-sm leading-relaxed text-neutral-600 my-2 font-inter md:text-base">✓ Stay connected with local SIM card (Dialog/Mobitel)</li>
                  <li className="text-sm leading-relaxed text-neutral-600 my-2 font-inter md:text-base">✓ Dress modestly at religious sites</li>
                  <li className="text-sm leading-relaxed text-neutral-600 my-2 font-inter md:text-base">✓ Pre-book accommodation during peak season</li>
                  <li className="text-sm leading-relaxed text-neutral-600 my-2 font-inter md:text-base">✓ Join group tours to meet fellow travelers</li>
                </ul>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
