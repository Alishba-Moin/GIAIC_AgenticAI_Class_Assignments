from agents import Agent, Runner, RunConfig, OpenAIChatCompletionsModel, function_tool
from openai import AsyncOpenAI
from dotenv import load_dotenv
import chainlit as cl
from typing import cast
import os
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

    # Career roadmap tool
    @function_tool
    def get_career_roadmap(career):
        """Generates a skill-building roadmap for a given career in 2025."""
        roadmaps = {
            "machine learning engineer": {
                "skills": ["Python", "TensorFlow", "PyTorch", "Machine Learning", "Deep Learning", "Mathematics"],
                "courses": ["Deep Learning Specialization (Coursera)", "Scaler AI & ML Course", "Introduction to AI (IBM SkillsBuild)"],
                "timeline": "6-12 months for basics; 1-2 years for proficiency"
            },
            "data scientist": {
                "skills": ["Python", "R", "SQL", "Machine Learning", "Statistics", "Data Visualization"],
                "courses": ["Data Science (Coursera)", "Python for Data Science (Udemy)", "Data Engineering Fundamentals (edX)"],
                "timeline": "6-18 months based on math background"
            },
            "cybersecurity analyst": {
                "skills": ["Threat Analysis", "Ethical Hacking", "Python", "Networking", "AI-powered Cybersecurity"],
                "courses": ["Google IT Support (Coursera)", "Complete Cyber Security Course (Udemy)", "Cisco Networking Academy"],
                "timeline": "6-12 months for entry-level; 1-2 years for advanced"
            },
            "ui/ux designer": {
                "skills": ["Figma", "User Research", "Wireframing", "UI Design", "Basic JavaScript"],
                "courses": ["Google UX Design (Coursera)", "UI/UX Design Bootcamp (Udemy)", "FreeCodeCamp UI Design"],
                "timeline": "3-6 months for basics; 1 year for proficiency"
            },
            "cloud computing": {
                "skills": ["Kubernetes", "Docker", "AWS", "Azure", "Linux", "CI/CD", "Networking"],
                "courses": ["Google Cloud DevOps Engineer (Coursera)", "Kubernetes for Beginners (Udemy)", "Certified Kubernetes Administrator (Linux Foundation)"],
                "timeline": "3-6 months for basics; 6-12 months for proficiency"
            },
            "agentic ai": {
                "skills": ["Python", "LangChain", "LLM APIs", "Reinforcement Learning", "Prompt Engineering", "Workflow Automation"],
                "courses": ["Building AI Agents with LangChain (Coursera)", "Mastering LLMs (Udemy)", "Reinforcement Learning Specialization (DeepLearning.AI)"],
                "timeline": "6-12 months for basics; 1-2 years for proficiency"
            },
            "freelancing": {
                "skills": ["Graphic Design", "Writing", "Virtual Assistance", "Agentic AI", "Digital Marketing"],
                "courses": ["Graphic Design (Coursera)", "Writing Essentials (Udemy)", "Virtual Assistant Training (Udemy)", "Building AI Agents (Coursera)"],
                "timeline": "3-6 months for basics; 1-2 months for first client"
            },
            "default": {
                "skills": ["Python", "Basic IT skills", "Research required"],
                "courses": ["Explore Coursera, edX, Udemy", "FreeCodeCamp", "Kaggle Tutorials"],
                "timeline": "Varies by career"
            }
        }
        return roadmaps.get(career.lower(), roadmaps["default"])

    # Initialize chat history
    cl.user_session.set("chat_history", [])

    # Define agents with concise instructions
    CareerAgent = Agent(
        name="career_agent",
        instructions="""
        Suggest 2-3 tech/freelancing careers matching user interests with brief reasons why they fit. Tailor for 2025 Pakistan/global demand. End with “Want skills or job details?” Use chat history to personalize. Keep answers short, friendly, and focused on USD/₹ earnings.
        """,
        handoff_description="Handles career exploration."
    )

    SkillAgent = Agent(
        name="skill_agent",
        instructions="""
        For skill queries (e.g., “how to earn on Upwork”), deliver a roadmap with skills, profile setup, courses, and success tips in a markdown table. Tailor for Pakistan beginners, emphasizing 2025 trends (e.g., Agentic AI). Use chat history for context. End with “Want job details?” Answer directly and concisely.
        """,
        handoff_description="Handles skill queries.",
        tools=[get_career_roadmap]
    )

    JobAgent = Agent(
        name="job_agent",
        instructions="""
        For job queries (e.g., “what’s freelancing like”), describe roles, responsibilities, work environment, and USD/₹ earnings for Pakistan in 2025. Suggest related tech jobs if unsupported. End with “Need skills to start?” Use chat history for context. Keep answers direct and friendly.
        """,
        handoff_description="Handles job role queries."
    )

    triage_agent = Agent(
        name="triage_agent",
        instructions="""
        Route user queries to the right agent based on intent: CareerAgent for interests (e.g., “tech”), SkillAgent for skill queries (e.g., “skills for freelancing”), or JobAgent for job details (e.g., “what’s freelancing like”). Extract key terms (e.g., “Upwork,” “Agentic AI”) and use chat history for follow-up context. If unclear, route to CareerAgent and ask for interests. Deliver answers seamlessly as one responder, focusing on Pakistan’s 2025 job market with USD/₹ earnings.
        """,
        handoffs=[CareerAgent, SkillAgent, JobAgent]
    )

    # Store agents and config
    cl.user_session.set("career_agent", CareerAgent)
    cl.user_session.set("skill_agent", SkillAgent)
    cl.user_session.set("job_agent", JobAgent)
    cl.user_session.set("triage_agent", triage_agent)
    cl.user_session.set("config", config)

    await cl.Message(
        content="Welcome to Career Mentor! Ask about tech jobs, skills, or earning online."
    ).send()

@cl.on_message
async def main(message: cl.Message):
    msg = cl.Message(content="Thinking...")
    await msg.send()

    triage_agent: Agent = cast(Agent, cl.user_session.get("triage_agent"))
    config: RunConfig = cast(RunConfig, cl.user_session.get("config"))
    history = cl.user_session.get("chat_history") or []

    # Use raw input
    user_input = message.content

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