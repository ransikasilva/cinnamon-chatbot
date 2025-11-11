'use client'

import styles from './StructuredResponse.module.css'
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
      <div className={styles.structuredResponse}>
        <div className={styles.messageText}>{data.message}</div>

        <div className={styles.section}>
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
      <div className={styles.structuredResponse}>
        <div className={styles.messageText}>{data.message}</div>

        <div className={styles.section}>
          <HotelCard
            hotel={data.hotel}
            room={data.room}
            nights={data.nights}
            totalCost={data.total}
          />

          {data.activities && data.activities.length > 0 && (
            <div className={styles.activitiesSection}>
              <h5 className={styles.miniTitle}>Included Activities</h5>
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
      <div className={styles.structuredResponse}>
        <div className={styles.messageText}>{data.message}</div>

        <div className={styles.section}>
          <h4 className={styles.sectionTitle}>Your 10-Day Itinerary</h4>
          {data.itinerary?.map((leg: any, index: number) => (
            <div key={index} className={styles.itineraryLeg}>
              <div className={styles.dayBadge}>Day {leg.day_range}</div>
              <HotelCard
                hotel={leg.hotel}
                room={leg.room}
                nights={leg.nights}
                totalCost={leg.room.price * leg.nights}
              />

              {leg.activities && leg.activities.length > 0 && (
                <div className={styles.activitiesSection}>
                  <h5 className={styles.miniTitle}>Recommended Activities</h5>
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
      <div className={styles.structuredResponse}>
        <div className={styles.messageText}>{data.message}</div>

        <div className={styles.section}>
          <h4 className={styles.sectionTitle}>Available Options</h4>
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
          <div className={styles.section}>
            <h4 className={styles.sectionTitle}>Alternative Options</h4>
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
      <div className={styles.structuredResponse}>
        <div className={styles.messageText}>{data.message}</div>

        <div className={styles.budgetInfo}>
          <IoInformationCircle className={styles.infoIcon} />
          <span>Your budget: ${data.budget} • {data.nights} nights • {data.kids || 0} kids</span>
        </div>

        {data.options && data.options.length > 0 ? (
          <div className={styles.section}>
            <h4 className={styles.sectionTitle}>Perfect Matches</h4>
            {data.options.slice(0, 3).map((option: any, index: number) => (
            <div key={index} className={styles.familyOption}>
              <HotelCard
                hotel={option.hotel}
                room={option.room}
                nights={option.nights}
                totalCost={option.room_total}
              />

              <div className={styles.breakdown}>
                <div className={styles.breakdownRow}>
                  <span>Room ({option.nights} nights)</span>
                  <span>${option.room_total}</span>
                </div>
                <div className={styles.breakdownRow}>
                  <span>Breakfast Plan</span>
                  <span>${option.meal_cost}</span>
                </div>
                <div className={`${styles.breakdownRow} ${styles.total}`}>
                  <span>Total Cost</span>
                  <span>${option.total_cost}</span>
                </div>
                {option.within_budget && (
                  <div className={styles.savingsBadge}>
                    <IoCheckmarkCircle />
                    <span>Saves you ${option.savings}!</span>
                  </div>
                )}
              </div>

              {option.activities && option.activities.length > 0 && (
                <div className={styles.activitiesSection}>
                  <h5 className={styles.miniTitle}>Available Activities</h5>
                  {option.activities.map((activity: any, actIndex: number) => (
                    <ActivityCard key={actIndex} activity={activity} />
                  ))}
                </div>
              )}
            </div>
          ))}
          </div>
        ) : (
          <div className={styles.messageText}>
            No options found within your budget. Would you like to see alternatives or adjust your criteria?
          </div>
        )}
      </div>
    )
  }

  if (data.type === 'full_trip_planning') {
    return (
      <div className={styles.structuredResponse}>
        <div className={styles.messageText}>{data.message}</div>

        <div className={styles.budgetInfo}>
          <IoInformationCircle className={styles.infoIcon} />
          <span>{data.days} days • Budget: ${data.budget}</span>
        </div>

        <div className={styles.section}>
          <h4 className={styles.sectionTitle}>Your Itinerary</h4>
          {data.itinerary?.map((leg: any, index: number) => (
            <div key={index} className={styles.itineraryLeg}>
              <div className={styles.dayBadge}>Day {leg.day_range}</div>
              <HotelCard
                hotel={leg.hotel}
                room={leg.room}
                nights={leg.nights}
                totalCost={leg.room.price * leg.nights}
              />

              {leg.activities && leg.activities.length > 0 && (
                <div className={styles.activitiesSection}>
                  <h5 className={styles.miniTitle}>Recommended Activities</h5>
                  {leg.activities.map((activity: any, actIndex: number) => (
                    <ActivityCard key={actIndex} activity={activity} />
                  ))}
                </div>
              )}
            </div>
          ))}
        </div>

        <div className={styles.section}>
          <h4 className={styles.sectionTitle}>Cost Breakdown</h4>
          <div className={styles.costBreakdown}>
            <div className={styles.breakdownRow}>
              <span>Accommodation</span>
              <span>${data.cost_breakdown?.accommodation}</span>
            </div>
            <div className={styles.breakdownRow}>
              <span>Transportation ({data.transportation_details?.total_distance}km)</span>
              <span>${data.cost_breakdown?.transportation}</span>
            </div>
            <div className={styles.breakdownRow}>
              <span>Activities</span>
              <span>${data.cost_breakdown?.activities}</span>
            </div>
            <div className={styles.breakdownRow}>
              <span>Meals</span>
              <span>${data.cost_breakdown?.meals}</span>
            </div>
            {data.cost_breakdown?.discount > 0 && (
              <div className={`${styles.breakdownRow} ${styles.discount}`}>
                <span>Discount (Multi-Property)</span>
                <span>-${data.cost_breakdown.discount}</span>
              </div>
            )}
            <div className={`${styles.breakdownRow} ${styles.grandTotal}`}>
              <span>Total Cost</span>
              <span>${data.cost_breakdown?.total}</span>
            </div>
          </div>

          {data.within_budget ? (
            <div className={styles.successBadge}>
              <IoCheckmarkCircle />
              <span>Perfect! This fits your budget of ${data.budget}</span>
            </div>
          ) : (
            <div className={styles.warningBadge}>
              <IoInformationCircle />
              <span>Slightly over budget. Would you like to see alternatives?</span>
            </div>
          )}
        </div>
      </div>
    )
  }

  if (data.type === 'general') {
    return (
      <div className={styles.structuredResponse}>
        <div className={styles.messageText}>{data.message}</div>

        {data.quick_suggestions && (
          <div className={styles.suggestions}>
            <h5 className={styles.miniTitle}>Try asking:</h5>
            {data.quick_suggestions.map((suggestion: string, index: number) => (
              <div key={index} className={styles.suggestionChip}>
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
      <div className={styles.structuredResponse}>
        <div className={styles.messageText}>{data.message}</div>

        <div className={styles.section}>
          {data.recommendations?.map((rec: any, index: number) => (
            <div key={index} className={styles.explorerCard}>
              <HotelCard hotel={rec.hotel} />
              <div className={styles.highlights}>
                <h5 className={styles.miniTitle}>Highlights:</h5>
                <ul className={styles.highlightList}>
                  {rec.highlights?.map((highlight: string, idx: number) => (
                    <li key={idx}>{highlight}</li>
                  ))}
                </ul>
                <div className={styles.bestFor}>
                  <strong>Best for:</strong> {rec.best_for}
                </div>
              </div>
            </div>
          ))}
        </div>

        {data.next_question && (
          <div className={styles.messageText} style={{ marginTop: '12px' }}>
            {data.next_question}
          </div>
        )}
      </div>
    )
  }

  // Itinerary display
  if (data.type === 'itinerary') {
    return (
      <div className={styles.structuredResponse}>
        <div className={styles.messageText}>{data.message}</div>

        <div className={styles.itinerarySchedule}>
          {data.schedule?.morning && (
            <div className={styles.scheduleBlock}>
              <div className={styles.scheduleTime}>🌅 {data.schedule.morning.time}</div>
              <ul className={styles.scheduleList}>
                {data.schedule.morning.activities.map((activity: string, idx: number) => (
                  <li key={idx}>{activity}</li>
                ))}
              </ul>
            </div>
          )}

          {data.schedule?.lunch && (
            <div className={styles.scheduleBlock}>
              <div className={styles.scheduleTime}>🍽️ {data.schedule.lunch.time}</div>
              <ul className={styles.scheduleList}>
                {data.schedule.lunch.activities.map((activity: string, idx: number) => (
                  <li key={idx}>{activity}</li>
                ))}
              </ul>
            </div>
          )}

          {data.schedule?.evening && (
            <div className={styles.scheduleBlock}>
              <div className={styles.scheduleTime}>🌆 {data.schedule.evening.time}</div>
              <ul className={styles.scheduleList}>
                {data.schedule.evening.activities.map((activity: string, idx: number) => (
                  <li key={idx}>{activity}</li>
                ))}
              </ul>
            </div>
          )}
        </div>

        {data.closing && (
          <div className={styles.messageText} style={{ marginTop: '12px' }}>
            {data.closing}
          </div>
        )}
      </div>
    )
  }

  return (
    <div className={styles.structuredResponse}>
      <div className={styles.messageText}>
        {data.message || 'I received your message. How can I help you further?'}
      </div>
    </div>
  )
}
