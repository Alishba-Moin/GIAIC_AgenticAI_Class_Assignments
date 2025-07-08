import random
from agents import Agent, OpenAIChatCompletionsModel, RunConfig, Runner, function_tool
from openai import AsyncOpenAI
import chainlit as cl
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set. Please set it in the .env file.")


# Chainlit Integration
@cl.on_chat_start
async def start():
    # Initialize AsyncOpenAI client
    client = AsyncOpenAI(
        api_key=GEMINI_API_KEY,
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

    # Define Tools
    @function_tool
    def roll_dice(sides: int) -> int:
        """Rolls a dice with the specified number of sides."""
        return random.randint(1, sides)

    @function_tool
    def generate_event() -> str:
        """Generates a random game event."""
        events = [
            "You find a hidden treasure chest with gold!",
            "A trap springs! Lose 5 health.",
            "You discover a mysterious potion.",
            "A friendly NPC offers you a map."
        ]
        return random.choice(events)

    # Define Agents
    narrator_agent = Agent(
        name="NarratorAgent",
        instructions=(
            "You are the Narrator for a fantasy adventure game. "
            "Create immersive story descriptions based on player actions (e.g., 'explore', 'move forward'). "
            "Use the generate_event tool to add random events during exploration."
        ),
        model=model,
        tools=[roll_dice, generate_event]
    )

    monster_agent = Agent(
        name="MonsterAgent",
        instructions=(
            "You handle combat in a fantasy adventure game. "
            "When the player chooses to fight, describe a monster encounter and use roll_dice to determine outcomes. "
            "A roll of 10+ on a D20 is a hit, dealing 5 damage. Below 10 is a miss."
        ),
        model=model,
        tools=[roll_dice]
    )

    item_agent = Agent(
        name="ItemAgent",
        instructions=(
            "You manage the player's inventory and rewards in a fantasy adventure game. "
            "When the player checks inventory or receives a reward, describe their items or add new ones using generate_event."
        ),
        model=model,
        tools=[generate_event]
    )

    game_master_agent = Agent(
        name="GameMaster",
        instructions=(
            "You are the Game Master for a fantasy adventure game. "
            "Based on the player's input, decide whether to hand off to the NarratorAgent (for story progression), "
            "MonsterAgent (for combat), or ItemAgent (for inventory/rewards). "
            "If the input is unclear, ask the player to clarify. "
            "Use tools when appropriate (e.g., roll_dice for combat, generate_event for exploration)."
        ),
        model=model,
        handoffs=[narrator_agent, monster_agent, item_agent]
    )

    # Store agents and config
    cl.user_session.set("narrator_agent", narrator_agent)
    cl.user_session.set("monster_agent", monster_agent)
    cl.user_session.set("item_agent", item_agent)
    cl.user_session.set("game_master_agent", game_master_agent)
    cl.user_session.set("client", client)
    cl.user_session.set("config", config)
    

    await cl.Message(
        content="Welcome to the Fantasy Adventure Game! Type 'explore', 'fight', or 'check inventory' to begin."
    ).send()

@cl.on_message
async def main(message: cl.Message):
    # Initialize or retrieve session state
    if not cl.user_session.get("player_state"):
        cl.user_session.set("player_state", {
            "health": 20,
            "inventory": ["sword", "shield"],
            "location": "a dark forest"
        })

    player_input = message.content.strip().lower()
    player_state = cl.user_session.get("player_state")
    game_master = cl.user_session.get("game_master_agent")
    config = cl.user_session.get("config")

    try:
        # Run the GameMasterAgent with the player's input
        result = await Runner.run(
            game_master,
            input=message.content
        )

        # Parse the result and update player state
        response = result.final_output
        if not response:
            response = "Please try again with a valid action."

        # Update player state based on response
        if "damage" in response.lower():
            damage = 5 if "hit" in response.lower() else 0
            player_state["health"] -= damage
            if player_state["health"] <= 0:
                response += "\nGame Over! Your health reached 0."


        # Update location if the player moves
        if "explore" in player_input or "move" in player_input:
            locations = ["a dark forest", "an ancient castle", "a mystical cave"]
            player_state["location"] = random.choice(locations)

        # Save updated state
        cl.user_session.set("player_state", player_state)

        # Send response to Chainlit
        await cl.Message(
            content=f"{response}\n\n**Player State**: Health: {player_state['health']}, Inventory: {player_state['inventory']}, Location: {player_state['location']}"
        ).send()

    except Exception as e:
        await cl.Message(
            content=f"An error occurred: {str(e)}. Please check your API key or try again."
        ).send()

