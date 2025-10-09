from langchain_core.tools import tool


@tool
def change_existing_booking(booking_id: str, change_request: str) -> str:
    """Handle changes to existing bookings."""
    return f"""I'd be happy to help you modify your booking (ID: {booking_id}).

For booking changes, I'll need to verify your details first. Please provide:
- Your confirmation email or phone number
- What you'd like to change: {change_request}

Alternatively, you can contact our reservations team directly at:
📞 Phone: +94 11 123 4567
📧 Email: reservations@cinnamonhotels.com

They can assist you with modifications, cancellations, or special requests immediately."""
