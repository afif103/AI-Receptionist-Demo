from langchain_core.tools import tool

@tool
def greet_visitor(name: str) -> str:
    """Greet a visitor by name."""
    return f"Hello {name}, welcome! How can I assist you today?"

@tool
def check_availability(time: str) -> str:
    """Check availability for a given time slot."""
    # Dummy logic - in real implementation, integrate with calendar API
    available_times = ["9:00 AM", "10:00 AM", "2:00 PM"]
    if time in available_times:
        return f"Yes, {time} is available. Would you like to schedule?"
    else:
        return f"Sorry, {time} is not available. Available slots: {', '.join(available_times)}."