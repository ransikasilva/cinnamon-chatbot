# Cinnamon Hotels Chatbot - User Flows Documentation

## User Type 1: New Booking (newbooking@demo.com)

### Flow: Book Cinnamon Grand Colombo
**Keywords to trigger:** "I want to book Cinnamon Grand", "book Cinnamon Grand", "Cinnamon Grand Colombo"

1. Login with: `newbooking@demo.com`
2. Bot greets: "Hello and welcome to Cinnamon Hotels & Resorts! I'm your virtual concierge. How can I help you today?"
3. You say: **"I want to book Cinnamon Grand"** (must specify hotel name)
4. Bot shows booking form for Cinnamon Grand
5. Fill in: Check-in date, Check-out date, Adults (max 3), Children, Rooms
6. Submit form
7. Bot sends reservation link to complete booking

**Key Notes:**
- User Type 1 focuses on direct booking of Cinnamon Grand Colombo only
- Must specify "Cinnamon Grand" to trigger the booking form
- Booking form limits adults to 3 per room

---

## User Type 2: Explorer (explorer@demo.com)

### Primary Flow: Explore and Book Based on Preferences
**Keywords to trigger:**
- Start: "hi", "hello", "I just landed", "landed in Sri Lanka"
- Preferences: "beach", "sea", "ocean" | "culture", "temple", "heritage" | "food", "dining", "restaurant" | "mix", "everything"

1. Login with: `explorer@demo.com`
2. Bot greets: "Hello and welcome to Cinnamon Hotels & Resorts! I'm your virtual concierge. How can I help you today?"
3. You say: **"Hi, I just landed in Sri Lanka"**
4. Bot responds: "AYUBOWAN! Welcome to Sri Lanka! 🌴 I'm thrilled to help you explore our beautiful island. You can explore our hotels on the map or tell me - what kind of experience are you looking for? Beaches, cultural sites, wildlife, or a mix of everything?"
5. You say: **"I like beaches"** (or "culture", "food", "mix of everything")
6. Bot shows hotel carousel with relevant hotels based on your preference:
   - **Beach**: Cinnamon Bey Beruwala, Cinnamon Wild Yala
   - **Culture**: Cinnamon Grand Colombo, Cinnamon Lakeside
   - **Food**: Cinnamon Grand Colombo, Cinnamon Life
   - **Mix**: All 5 hotels (Grand, Lakeside, Beruwala, Life, Wild Yala)
7. Click "Book This Hotel" on any hotel
8. Bot shows booking form for selected hotel
9. Fill in booking details and submit
10. Bot sends reservation link

### Alternative Flow: Direct Booking Request
**Keywords to trigger:** "I need to book a hotel", "book a hotel", "show me hotels", "book", "reservation", "reserve"

1. Login with: `explorer@demo.com`
2. Bot greets
3. You say: **"I need to book a hotel"** or click **"Booking"** quick action button
4. Bot shows carousel with ALL available hotels
5. Click "Book This Hotel" on any hotel
6. Bot shows booking form
7. Fill in details and submit
8. Bot sends reservation link

**Key Notes:**
- User Type 2 is exploratory - they want recommendations
- Can explore by preference (beach, culture, food) OR directly book
- "I need to book a hotel" works in ANY flow at ANY time

---

## User Type 3: Edit Booking (editbooking@demo.com)

### Primary Flow: Edit Existing Reservation
**Keywords to trigger:**
- Start: "I want to change my booking", "edit booking", "modify reservation"
- Booking ref: "CLB-4821", "CGD-", "CB-", "CC-" (any booking reference format)
- Changes: "change checkout to 20th", "update checkout", "checkout 20th"

1. Login with: `editbooking@demo.com`
2. Bot greets: "Hello and welcome to Cinnamon Hotels & Resorts! I'm your virtual concierge. How can I help you today?"
3. You say: **"I want to change my booking"**
4. Bot asks: "I'd be happy to help you modify your reservation. Please provide your booking reference number (e.g., CLB-4821)"
5. You say: **"CLB-4821"**
6. Bot shows current booking details:
   - Booking Ref: CLB-4821
   - Hotel: Cinnamon Grand Colombo
   - Check-in: November 15, 2025
   - Check-out: November 18, 2025
   - Guests: 2 Adults
   - Room: Deluxe Room
7. You say: **"change checkout to 20th"**
8. Bot shows updated booking details with new checkout: November 20, 2025
9. Bot asks: "No extra charges apply. Please confirm your changes to complete the modification."
10. You say: **"confirm"**
11. Bot sends updated reservation link

### Alternative Flow: Create New Booking
**Keywords to trigger:** "I need to book a hotel", "book a hotel", "new booking", "show me hotels"

1. Login with: `editbooking@demo.com`
2. Bot greets
3. You say: **"I need to book a hotel"** or click **"Booking"** quick action button
4. Bot shows carousel with ALL available hotels
5. Click "Book This Hotel" on any hotel
6. Bot shows booking form
7. Fill in details and submit
8. Bot sends reservation link

**Key Notes:**
- User Type 3 focuses on editing existing bookings
- Can also create NEW bookings using "I need to book a hotel"
- Booking reference formats: CLB-XXXX, CGD-XXXX, CB-XXXX, CC-XXXX

---

## Quick Actions (Available in All User Types)

The chatbot header has quick action buttons:

1. **Booking** → Triggers "I need to book a hotel" → Shows all hotels carousel
2. **Edit** → For editing existing bookings
3. **Dining** → Information about restaurants
4. **Info** → General information

---

## Hotel IDs (for developers)

- **42169**: Cinnamon Grand Colombo
- **42170**: Cinnamon Lakeside Colombo
- **42175**: Cinnamon Bey Beruwala (Beach resort)
- **42174**: Cinnamon Life
- **42171**: Cinnamon Wild Yala (Safari & wildlife)

---

## Universal Keywords (Work in ALL User Types)

These keywords will show the hotel carousel in ANY user flow:

- "I need to book a hotel"
- "book a hotel"
- "show me hotels"
- "available hotels"
- "book"
- "reservation"
- "reserve"

Or simply click the **"Booking"** quick action button!

---

## Key Features

✅ Adults limited to max 3 per room (increase rooms for more guests)
✅ Hotel carousel with images and highlights
✅ Direct reservation links to Cinnamon Hotels booking system
✅ Works across all user types (Type 1, 2, and 3)
✅ Quick action buttons for fast access
✅ Correct hotel IDs mapped to reservation URLs
