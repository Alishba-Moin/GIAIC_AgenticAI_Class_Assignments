from agents import Agent, Runner, RunConfig, OpenAIChatCompletionsModel, function_tool
from openai import AsyncOpenAI
from dotenv import load_dotenv
import chainlit as cl
from typing import cast
import os
import random

# Load environment variables
load_dotenv()
gemini_api_key = os.getenv("GEMINI_API_KEY")

if not gemini_api_key:
    raise ValueError("GEMINI_API_KEY is not set.")

@cl.on_chat_start
async def start():
    # Initialize AsyncOpenAI client
    client = AsyncOpenAI(
        api_key=gemini_api_key,
        base_url="https://generativelanguage.googleapis.com/v1beta/openai"
    )

    # Define the model
    model = OpenAIChatCompletionsModel(
        model="gemini-2.0-flash",
        openai_client=client
    )

    # Configure the runner
    config = RunConfig(
        model=model,
        model_provider=client,
        tracing_disabled=True
    )

    # Tools for travel planning
    @function_tool
    def get_flights(destination):
        """Returns realistic flight data for 2025, tailored for Pakistani travelers."""
        flights = {
            "dubai": [
                {"from": "Karachi", "airline": "Emirates", "price": "$350 (₹98,000 PKR)", "duration": "2h 15m"},
                {"from": "Lahore", "airline": "Flydubai", "price": "$300 (₹84,000 PKR)", "duration": "2h 30m"}
            ],
            "istanbul": [
                {"from": "Karachi", "airline": "Turkish Airlines", "price": "$450 (₹126,000 PKR)", "duration": "5h 45m"},
                {"from": "Islamabad", "airline": "PIA", "price": "$400 (₹112,000 PKR)", "duration": "6h"}
            ],
            "maldives": [
                {"from": "Karachi", "airline": "Qatar Airways", "price": "$600 (₹168,000 PKR)", "duration": "5h via Doha"},
                {"from": "Lahore", "airline": "Emirates", "price": "$650 (₹182,000 PKR)", "duration": "5h 30m"}
            ],
            "hunza": [
                {"from": "Islamabad", "airline": "Bus (NATCO)", "price": "₹6,000 PKR", "duration": "14h"},
                {"from": "Karachi", "airline": "PIA (to Gilgit)", "price": "₹25,000 PKR", "duration": "2h + 3h road"}
            ],
            "murree": [
                {"from": "Islamabad", "airline": "Bus (Daewoo)", "price": "₹5,000 PKR", "duration": "2h"},
                {"from": "Lahore", "airline": "Bus", "price": "₹7,000 PKR", "duration": "5h"}
            ],
            "skardu": [
                {"from": "Islamabad", "airline": "PIA", "price": "₹20,000 PKR", "duration": "1h"},
                {"from": "Karachi", "airline": "Serene Air", "price": "₹30,000 PKR", "duration": "2h"}
            ],
            "neelum valley": [
                {"from": "Islamabad", "airline": "Bus", "price": "₹3,000 PKR", "duration": "5h"},
                {"from": "Lahore", "airline": "Bus", "price": "₹6,000 PKR", "duration": "8h"}
            ],
            "khanpur dam": [
                {"from": "Islamabad", "airline": "Bus", "price": "₹2,000 PKR", "duration": "1h"},
                {"from": "Rawalpindi", "airline": "Bus", "price": "₹2,000 PKR", "duration": "1h"}
            ],
            "default": [
                {"from": "N/A", "airline": "N/A", "price": "Research flights", "duration": "N/A"}
            ]
        }
        return flights.get(destination.lower(), flights["default"])

    @function_tool
    def suggest_hotels(destination):
        """Returns realistic hotel suggestions for 2025, tailored for Pakistani travelers."""
        hotels = {
            "dubai": [
                {"name": "Burj Al Arab", "price": "$500/night (₹140,000 PKR)", "type": "Luxury"},
                {"name": "Premier Inn", "price": "$80/night (₹22,400 PKR)", "type": "Budget"}
            ],
            "istanbul": [
                {"name": "Pera Palace", "price": "$120/night (₹33,600 PKR)", "type": "Historic"},
                {"name": "Ibis Istanbul", "price": "$60/night (₹16,800 PKR)", "type": "Budget"}
            ],
            "maldives": [
                {"name": "Sun Siyam Resort", "price": "$250/night (₹70,000 PKR)", "type": "Beachfront"},
                {"name": "Guesthouse Male", "price": "$100/night (₹28,000 PKR)", "type": "Budget"}
            ],
            "hunza": [
                {"name": "Serena Hotel", "price": "₹18,000 PKR/night", "type": "Luxury"},
                {"name": "Local Guesthouse", "price": "₹5,000 PKR/night", "type": "Budget"}
            ],
            "murree": [
                {"name": "PC Bhurban", "price": "₹15,000 PKR/night", "type": "Luxury"},
                {"name": "Hilltop Hotel", "price": "₹6,000 PKR/night", "type": "Budget"}
            ],
            "skardu": [
                {"name": "Shangrila Resort", "price": "₹20,000 PKR/night", "type": "Luxury"},
                {"name": "Skardu Inn", "price": "₹7,000 PKR/night", "type": "Budget"}
            ],
            "neelum valley": [
                {"name": "Neelum View Hotel", "price": "₹4,000 PKR/night", "type": "Budget"},
                {"name": "Keran Resort", "price": "₹6,000 PKR/night", "type": "Mid-range"}
            ],
            "khanpur dam": [
                {"name": "Khanpur Lake Resort", "price": "₹3,000 PKR/night", "type": "Budget"},
                {"name": "Local Campsite", "price": "₹2,000 PKR/night", "type": "Budget"}
            ],
            "default": [
                {"name": "Research hotels", "price": "N/A", "type": "N/A"}
            ]
        }
        return hotels.get(destination.lower(), hotels["default"])

    @function_tool
    def confirm_booking(flight, hotel, destination):
        """Simulates booking confirmation with a mock receipt."""
        return {
            "confirmation": f"Booking confirmed for {destination.title()}!",
            "flight": flight,
            "hotel": hotel,
            "receipt_id": f"TRV-{destination.upper()}-2025-{random.randint(1000, 9999)}",
            "message": "You'll receive a confirmation email."
        }

    @function_tool
    def get_travel_alerts(destination):
        """Returns mock travel alerts for a destination in 2025."""
        alerts = {
            "dubai": "Weather: Sunny, 35°C. No disruptions expected.",
            "istanbul": "Flight delays possible due to high traffic. Check status before departure.",
            "maldives": "Monsoon season alert: Expect occasional rain.",
            "hunza": "Road conditions: Clear. Book buses early for peak season.",
            "murree": "Fog alert: Drive cautiously in early mornings.",
            "skardu": "Flight cancellations possible due to weather. Confirm with airline.",
            "neelum valley": "Road access good. Book early for peak season.",
            "khanpur dam": "Safe for boating. Check local safety guidelines.",
            "default": "No specific alerts. Check local conditions before travel."
        }
        return alerts.get(destination, alerts["default"])

    @function_tool
    def integrate_platform(platform, destination):
        """Simulates integration with travel platforms."""
        platforms = {
            "skyscanner": f"Connected to Skyscanner: Fetched flight data for {destination.title()}.",
            "booking.com": f"Connected to Booking.com: Fetched hotel data for {destination.title()}.",
            "default": f"Platform {platform} not supported. Try Skyscanner or Booking.com."
        }
        return platforms.get(platform.lower(), platforms["default"])

    @function_tool
    def manage_budget(flight_price, hotel_price, budget):
        """Tracks trip costs against budget and suggests alternatives if over budget."""
        try:
            flight_cost = float(flight_price.split("₹")[1].split(" ")[0].replace(",", ""))
            hotel_cost = float(hotel_price.split("₹")[1].split(" ")[0].replace(",", ""))
            total_cost = flight_cost + hotel_cost
            budget = float(budget)
            if total_cost > budget:
                return f"Warning: Total cost (₹{total_cost:,} PKR) exceeds budget (₹{budget:,} PKR). Try Murree or Khanpur Dam for budget-friendly options."
            return f"Total cost: ₹{total_cost:,} PKR (Flight: ₹{flight_cost:,} PKR, Hotel: ₹{hotel_cost:,} PKR). Within budget (₹{budget:,} PKR)."
        except:
            return "Error calculating budget. Please provide valid prices and budget."

    # Initialize chat history and session data
    cl.user_session.set("chat_history", [])
    cl.user_session.set("budget", None)
    cl.user_session.set("destination", None)

    # Define agents with clear, concise instructions
    DestinationAgent = Agent(
        name="destination_agent",
        instructions="""
        Suggest 2-3 destinations based on user mood, interests, or budget (e.g., “50,000 PKR”). Use chat history and session data (destination/budget) for personalization. Provide PKR/USD costs for Pakistani travelers in 2025. End with “Want to book, explore attractions, or adjust budget?” Deliver concise, friendly, actionable answers.
        """,
        handoff_description="Handles destination suggestions."
    )

    BookingAgent = Agent(
        name="booking_agent",
        instructions="""
            You are the booking agent. You can use the following tools:
            - get_flights(destination)
            - suggest_hotels(destination)
            - confirm_booking(flight, hotel, destination)
            - manage_budget(flight_price, hotel_price, budget)
            - integrate_platform(platform, destination)

            Your goal is to:
            1. Suggest realistic flights & hotels
            2. Respect budget if provided
            3. Call tools to simulate booking
            4. Always respond with actionable info

            ALWAYS use tools. NEVER say “I cannot search…” or “I cannot confirm…”
            """,
        handoff_description="Handles travel bookings.",
        tools=[get_flights, suggest_hotels, confirm_booking, integrate_platform, manage_budget]
    )

    ExploreAgent = Agent(
        name="explore_agent",
        instructions="""
        For attraction/food queries, suggest 2-3 attractions and food options using get_travel_alerts() for alerts. Use chat history and session data (destination). Tailor for Pakistani travelers in 2025. End with “Need booking help, more destinations, or budget tracking?” Deliver concise, friendly answers.
        """,
        handoff_description="Handles attractions and food suggestions.",
        tools=[get_travel_alerts]
    )

    triage_agent = Agent(
        name="triage_agent",
        instructions="""
            You are the triage agent for travel planning.

            **Always** route messages based on these keywords:

            - To `BookingAgent`: if input mentions flights, hotels, booking, Skyscanner, Booking.com, confirm, budget check.
            - To `ExploreAgent`: if input mentions explore, food, attraction, alerts, or names of cities with "explore".
            - To `DestinationAgent`: if input is vague or just mentions mood/interest (e.g. “I want nature”, “Where should I go?”)

            If unsure, prefer routing to BookingAgent.
            """,
        handoffs=[DestinationAgent, BookingAgent, ExploreAgent]
    )

    # Store agents and config
    cl.user_session.set("destination_agent", DestinationAgent)
    cl.user_session.set("booking_agent", BookingAgent)
    cl.user_session.set("explore_agent", ExploreAgent)
    cl.user_session.set("triage_agent", triage_agent)
    cl.user_session.set("config", config)

    await cl.Message(
        content="Welcome to the AI Travel Designer! Where would you like to go?"
    ).send()

@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="Let me think about that...")
    await msg.send()

    triage_agent: Agent = cast(Agent, cl.user_session.get("triage_agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))
    history = cl.user_session.get("chat_history") or []

    # Use raw input (assume Gemini handles Urdu)
    user_input = message.content.lower()

    # Store budget or destination
    if "budget" in user_input:
        try:
            budget = float(user_input.split("budget")[1].split()[0].replace("₹", "").replace(",", ""))
            cl.user_session.set("budget", budget)
        except:
            pass

    # Append to history
    history.append({"role": "user", "content": user_input})

    try:
        # Pass chat history
        result = await Runner.run(
            starting_agent=triage_agent,
            input=history,
            run_config=config
        )
        response_result = result.final_output

        msg.content = response_result
        await msg.update()

        # Update history
        history.append({"role": "assistant", "content": response_result})
        cl.user_session.set("chat_history", history)

    except Exception as e:
        msg.content = f"Oops, something went wrong: {str(e)}"
        await msg.update()