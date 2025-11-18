'use client'

import HotelCard from './HotelCard'
import ActivityCard from './ActivityCard'
import { IoCheckmarkCircle, IoInformationCircle } from 'react-icons/io5'

interface StructuredResponseProps {
  data: any
}

export default function StructuredResponse({ data }: StructuredResponseProps) {
  // Handle room comparison (Scenario 1)
  if (data.response_type === 'room_comparison') {
    return (
      <div className="w-full">
        <div className="text-sm text-neutral-800 leading-relaxed mb-4 font-inter">{data.message}</div>

        <div className="my-4">
          {data.options?.map((option: any, index: number) => (
            <HotelCard
              key={index}
              hotel={option.hotel}
              room={option.room}
              nights={option.nights}
              totalCost={option.total}
            />
          ))}
        </div>
      </div>
    )
  }

  // Handle family package (Scenario 2)
  if (data.response_type === 'family_package') {
    return (
      <div className="w-full">
        <div className="text-sm text-neutral-800 leading-relaxed mb-4 font-inter">{data.message}</div>

        <div className="my-4">
          <HotelCard
            hotel={data.hotel}
            room={data.room}
            nights={data.nights}
            totalCost={data.total}
          />

          {data.activities && data.activities.length > 0 && (
            <div className="mt-3.5 pt-3.5 border-t border-neutral-200">
              <h5 className="text-[13px] font-semibold text-neutral-600 my-3 font-poppins">Included Activities</h5>
              {data.activities.map((activity: any, index: number) => (
                <ActivityCard key={index} activity={activity} />
              ))}
            </div>
          )}
        </div>
      </div>
    )
  }

  // Handle itinerary (Scenario 3)
  if (data.response_type === 'itinerary') {
    return (
      <div className="w-full">
        <div className="text-sm text-neutral-800 leading-relaxed mb-4 font-inter">{data.message}</div>

        <div className="my-4">
          <h4 className="text-[15px] font-bold text-purple-primary m-0 mb-3 font-poppins uppercase tracking-wider">Your 10-Day Itinerary</h4>
          {data.itinerary?.map((leg: any, index: number) => (
            <div key={index} className="bg-neutral-50 rounded-xl p-4 mb-4 relative">
              <div className="absolute -top-2.5 left-4 bg-purple-primary text-white py-1 px-3.5 rounded-xl text-xs font-bold font-poppins uppercase tracking-wide shadow-[0_2px_8px_rgba(107,44,145,0.3)]">Day {leg.day_range}</div>
              <HotelCard
                hotel={leg.hotel}
                room={leg.room}
                nights={leg.nights}
                totalCost={leg.room.price * leg.nights}
              />

              {leg.activities && leg.activities.length > 0 && (
                <div className="mt-3.5 pt-3.5 border-t border-neutral-200">
                  <h5 className="text-[13px] font-semibold text-neutral-600 my-3 font-poppins">Recommended Activities</h5>
                  {leg.activities.map((activity: any, actIndex: number) => (
                    <ActivityCard key={actIndex} activity={activity} />
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>
      </div>
    )
  }

  if (data.type === 'sea_view_booking') {
    return (
      <div className="w-full">
        <div className="text-sm text-neutral-800 leading-relaxed mb-4 font-inter">{data.message}</div>

        <div className="my-4">
          <h4 className="text-[15px] font-bold text-purple-primary m-0 mb-3 font-poppins uppercase tracking-wider">Available Options</h4>
          {data.total_prices?.map((option: any, index: number) => {
            const room = data.rooms?.[index]
            return (
              <HotelCard
                key={index}
                hotel={data.hotel}
                room={room}
                nights={data.nights}
                totalCost={option.total}
              />
            )
          })}
        </div>

        {data.alternatives && data.alternatives.length > 0 && (
          <div className="my-4">
            <h4 className="text-[15px] font-bold text-purple-primary m-0 mb-3 font-poppins uppercase tracking-wider">Alternative Options</h4>
            {data.alternatives.map((alt: any, index: number) => (
              <HotelCard
                key={index}
                hotel={alt.hotel}
                room={alt.room}
                nights={data.nights}
                totalCost={alt.total_cost}
              />
            ))}
          </div>
        )}
      </div>
    )
  }

  if (data.type === 'family_trip') {
    return (
      <div className="w-full">
        <div className="text-sm text-neutral-800 leading-relaxed mb-4 font-inter">{data.message}</div>

        <div className="flex items-center gap-2 bg-[#F0E6F6] py-2.5 px-3.5 rounded-lg mb-4 text-[13px] text-purple-primary font-semibold font-inter">
          <IoInformationCircle className="text-lg text-purple-primary" />
          <span>Your budget: ${data.budget} • {data.nights} nights • {data.kids || 0} kids</span>
        </div>

        {data.options && data.options.length > 0 ? (
          <div className="my-4">
            <h4 className="text-[15px] font-bold text-purple-primary m-0 mb-3 font-poppins uppercase tracking-wider">Perfect Matches</h4>
            {data.options.slice(0, 3).map((option: any, index: number) => (
            <div key={index} className="bg-neutral-50 rounded-xl p-4 mb-4">
              <HotelCard
                hotel={option.hotel}
                room={option.room}
                nights={option.nights}
                totalCost={option.room_total}
              />

              <div className="bg-white rounded-[10px] p-3.5 mt-3">
                <div className="flex justify-between py-2 text-[13px] text-neutral-600 font-inter">
                  <span>Room ({option.nights} nights)</span>
                  <span>${option.room_total}</span>
                </div>
                <div className="flex justify-between py-2 text-[13px] text-neutral-600 font-inter">
                  <span>Breakfast Plan</span>
                  <span>${option.meal_cost}</span>
                </div>
                <div className="flex justify-between py-2 text-[13px] text-neutral-600 font-inter border-t-2 border-neutral-200 mt-2 pt-3 font-bold text-neutral-800 text-[15px]">
                  <span>Total Cost</span>
                  <span>${option.total_cost}</span>
                </div>
                {option.within_budget && (
                  <div className="flex items-center gap-1.5 bg-success-light text-success py-2 px-3 rounded-lg mt-2.5 text-[13px] font-semibold font-inter">
                    <IoCheckmarkCircle className="text-lg" />
                    <span>Saves you ${option.savings}!</span>
                  </div>
                )}
              </div>

              {option.activities && option.activities.length > 0 && (
                <div className="mt-3.5 pt-3.5 border-t border-neutral-200">
                  <h5 className="text-[13px] font-semibold text-neutral-600 my-3 font-poppins">Available Activities</h5>
                  {option.activities.map((activity: any, actIndex: number) => (
                    <ActivityCard key={actIndex} activity={activity} />
                  ))}
                </div>
              )}
            </div>
          ))}
          </div>
        ) : (
          <div className="text-sm text-neutral-800 leading-relaxed mb-4 font-inter">
            No options found within your budget. Would you like to see alternatives or adjust your criteria?
          </div>
        )}
      </div>
    )
  }

  if (data.type === 'full_trip_planning') {
    return (
      <div className="w-full">
        <div className="text-sm text-neutral-800 leading-relaxed mb-4 font-inter">{data.message}</div>

        <div className="flex items-center gap-2 bg-[#F0E6F6] py-2.5 px-3.5 rounded-lg mb-4 text-[13px] text-purple-primary font-semibold font-inter">
          <IoInformationCircle className="text-lg text-purple-primary" />
          <span>{data.days} days • Budget: ${data.budget}</span>
        </div>

        <div className="my-4">
          <h4 className="text-[15px] font-bold text-purple-primary m-0 mb-3 font-poppins uppercase tracking-wider">Your Itinerary</h4>
          {data.itinerary?.map((leg: any, index: number) => (
            <div key={index} className="bg-neutral-50 rounded-xl p-4 mb-4 relative">
              <div className="absolute -top-2.5 left-4 bg-purple-primary text-white py-1 px-3.5 rounded-xl text-xs font-bold font-poppins uppercase tracking-wide shadow-[0_2px_8px_rgba(107,44,145,0.3)]">Day {leg.day_range}</div>
              <HotelCard
                hotel={leg.hotel}
                room={leg.room}
                nights={leg.nights}
                totalCost={leg.room.price * leg.nights}
              />

              {leg.activities && leg.activities.length > 0 && (
                <div className="mt-3.5 pt-3.5 border-t border-neutral-200">
                  <h5 className="text-[13px] font-semibold text-neutral-600 my-3 font-poppins">Recommended Activities</h5>
                  {leg.activities.map((activity: any, actIndex: number) => (
                    <ActivityCard key={actIndex} activity={activity} />
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="my-4">
          <h4 className="text-[15px] font-bold text-purple-primary m-0 mb-3 font-poppins uppercase tracking-wider">Cost Breakdown</h4>
          <div className="bg-white border border-neutral-200 rounded-[10px] p-4 mb-3">
            <div className="flex justify-between py-2 text-[13px] text-neutral-600 font-inter">
              <span>Accommodation</span>
              <span>${data.cost_breakdown?.accommodation}</span>
            </div>
            <div className="flex justify-between py-2 text-[13px] text-neutral-600 font-inter">
              <span>Transportation ({data.transportation_details?.total_distance}km)</span>
              <span>${data.cost_breakdown?.transportation}</span>
            </div>
            <div className="flex justify-between py-2 text-[13px] text-neutral-600 font-inter">
              <span>Activities</span>
              <span>${data.cost_breakdown?.activities}</span>
            </div>
            <div className="flex justify-between py-2 text-[13px] text-neutral-600 font-inter">
              <span>Meals</span>
              <span>${data.cost_breakdown?.meals}</span>
            </div>
            {data.cost_breakdown?.discount > 0 && (
              <div className="flex justify-between py-2 text-[13px] text-neutral-600 font-inter text-success font-semibold">
                <span>Discount (Multi-Property)</span>
                <span>-${data.cost_breakdown.discount}</span>
              </div>
            )}
            <div className="flex justify-between py-2 text-[13px] text-neutral-600 font-inter border-t-[3px] border-purple-primary mt-3 pt-3 font-bold text-purple-primary text-base">
              <span>Total Cost</span>
              <span>${data.cost_breakdown?.total}</span>
            </div>
          </div>

          {data.within_budget ? (
            <div className="flex items-center gap-2 bg-success-light text-success py-3 px-4 rounded-[10px] text-[13px] font-semibold font-inter">
              <IoCheckmarkCircle className="text-xl" />
              <span>Perfect! This fits your budget of ${data.budget}</span>
            </div>
          ) : (
            <div className="flex items-center gap-2 bg-warning-light text-warning py-3 px-4 rounded-[10px] text-[13px] font-semibold font-inter">
              <IoInformationCircle className="text-xl" />
              <span>Slightly over budget. Would you like to see alternatives?</span>
            </div>
          )}
        </div>
      </div>
    )
  }

  if (data.type === 'general') {
    return (
      <div className="w-full">
        <div className="text-sm text-neutral-800 leading-relaxed mb-4 font-inter">{data.message}</div>

        {data.quick_suggestions && (
          <div className="mt-4 p-3.5 bg-neutral-100 rounded-[10px]">
            <h5 className="text-[13px] font-semibold text-neutral-600 my-3 font-poppins">Try asking:</h5>
            {data.quick_suggestions.map((suggestion: string, index: number) => (
              <div key={index} className="bg-white border border-neutral-200 py-2.5 px-3.5 rounded-lg my-2 text-[13px] text-purple-primary cursor-pointer transition-all duration-200 ease-in-out font-inter hover:bg-purple-primary hover:text-white hover:border-purple-primary hover:translate-x-1">
                {suggestion}
              </div>
            ))}
          </div>
        )}
      </div>
    )
  }

  // Explorer recommendations
  if (data.type === 'explorer_recommendations') {
    return (
      <div className="w-full">
        <div className="text-sm text-neutral-800 leading-relaxed mb-4 font-inter">{data.message}</div>

        <div className="my-4">
          {data.recommendations?.map((rec: any, index: number) => (
            <div key={index} className="bg-neutral-50 rounded-xl p-4 mb-4">
              <HotelCard hotel={rec.hotel} />
              <div className="bg-white rounded-[10px] p-3.5 mt-3">
                <h5 className="text-[13px] font-semibold text-neutral-600 my-3 font-poppins">Highlights:</h5>
                <ul className="list-none p-0 my-2">
                  {rec.highlights?.map((highlight: string, idx: number) => (
                    <li key={idx} className="py-1.5 text-[13px] text-neutral-600 font-inter relative pl-5 before:content-['✓'] before:absolute before:left-0 before:text-purple-primary before:font-bold">{highlight}</li>
                  ))}
                </ul>
                <div className="mt-3 pt-3 border-t border-neutral-200 text-[13px] text-neutral-600 font-inter">
                  <strong className="text-purple-primary">Best for:</strong> {rec.best_for}
                </div>
              </div>
            </div>
          ))}
        </div>

        {data.next_question && (
          <div className="text-sm text-neutral-800 leading-relaxed mb-4 font-inter mt-3">
            {data.next_question}
          </div>
        )}
      </div>
    )
  }

  // Itinerary display
  if (data.type === 'itinerary') {
    return (
      <div className="w-full">
        <div className="text-sm text-neutral-800 leading-relaxed mb-4 font-inter">{data.message}</div>

        <div className="my-4">
          {data.schedule?.morning && (
            <div className="bg-white border-l-4 border-purple-primary py-3.5 px-4 mb-3.5 rounded-lg shadow-[0_2px_8px_rgba(0,0,0,0.05)]">
              <div className="text-sm font-bold text-purple-primary mb-2.5 font-poppins">🌅 {data.schedule.morning.time}</div>
              <ul className="list-none p-0 m-0">
                {data.schedule.morning.activities.map((activity: string, idx: number) => (
                  <li key={idx} className="py-1.5 text-[13px] text-neutral-600 font-inter relative pl-5 before:content-['•'] before:absolute before:left-0 before:text-purple-primary before:font-bold before:text-base">{activity}</li>
                ))}
              </ul>
            </div>
          )}

          {data.schedule?.lunch && (
            <div className="bg-white border-l-4 border-purple-primary py-3.5 px-4 mb-3.5 rounded-lg shadow-[0_2px_8px_rgba(0,0,0,0.05)]">
              <div className="text-sm font-bold text-purple-primary mb-2.5 font-poppins">🍽️ {data.schedule.lunch.time}</div>
              <ul className="list-none p-0 m-0">
                {data.schedule.lunch.activities.map((activity: string, idx: number) => (
                  <li key={idx} className="py-1.5 text-[13px] text-neutral-600 font-inter relative pl-5 before:content-['•'] before:absolute before:left-0 before:text-purple-primary before:font-bold before:text-base">{activity}</li>
                ))}
              </ul>
            </div>
          )}

          {data.schedule?.evening && (
            <div className="bg-white border-l-4 border-purple-primary py-3.5 px-4 mb-3.5 rounded-lg shadow-[0_2px_8px_rgba(0,0,0,0.05)]">
              <div className="text-sm font-bold text-purple-primary mb-2.5 font-poppins">🌆 {data.schedule.evening.time}</div>
              <ul className="list-none p-0 m-0">
                {data.schedule.evening.activities.map((activity: string, idx: number) => (
                  <li key={idx} className="py-1.5 text-[13px] text-neutral-600 font-inter relative pl-5 before:content-['•'] before:absolute before:left-0 before:text-purple-primary before:font-bold before:text-base">{activity}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {data.closing && (
          <div className="text-sm text-neutral-800 leading-relaxed mb-4 font-inter mt-3">
            {data.closing}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className="w-full">
      <div className="text-sm text-neutral-800 leading-relaxed mb-4 font-inter">
        {data.message || 'I received your message. How can I help you further?'}
      </div>
    </div>
  )
}
