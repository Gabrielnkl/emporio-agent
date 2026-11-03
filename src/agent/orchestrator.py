"""Create and run the Empório customer-support agent."""

import os

from agents import Agent, Runner

from .prompts import STORE_AGENT_INSTRUCTIONS
from .tools import check_order, search_catalog, search_store_policies


def create_agent() -> Agent:
    return Agent(
        name="Atendimento Empório da Música",
        instructions=STORE_AGENT_INSTRUCTIONS,
        model=os.getenv("OPENAI_MODEL", "gpt-6-luna"),
        tools=[search_catalog, check_order, search_store_policies],
    )


async def respond(agent: Agent, message: str, history: list | None = None):
    """Run one user turn, optionally continuing the in-memory conversation history."""
    conversation = list(history or [])
    conversation.append({"role": "user", "content": message})
    return await Runner.run(agent, conversation)
