from agents import Agent, Runner, set_tracing_disabled, AsyncOpenAI, OpenAIChatCompletionsModel
from dotenv import load_dotenv
import os

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

provider = AsyncOpenAI(
    api_key= GEMINI_API_KEY,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai",
)
set_tracing_disabled(disabled=True)


client = OpenAIChatCompletionsModel(
    model="gemini-2.0-flash",
    openai_client=provider
)

agent = Agent(
    name="Smart Student Agent Assistant",
    instructions=""" You are a helpful student assistant. You help users by:
- Explaining academic topics in a simple way
- Giving useful study tips
- Summarizing short text passages

Always be friendly, clear, and student-focused.
""",
    model=client,
)

result = Runner.run_sync(agent, 'who is the founder of Pakistan?')

print(result.final_output)

