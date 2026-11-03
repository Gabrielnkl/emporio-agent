"""Responses API loop for the Empório customer-support assistant."""

import json
import os
from typing import Any

from openai import OpenAI

from .prompts import STORE_AGENT_INSTRUCTIONS
from .tools import TOOLS, call_tool

MAX_TOOL_ROUNDS = 5


def respond(
    client: OpenAI,
    message: str,
    history: list[Any] | None = None,
) -> tuple[str, list[Any]]:
    """Run one turn, execute requested local tools, and return text plus history."""
    input_items: list[Any] = list(history or [])
    input_items.append({"role": "user", "content": message})

    for _ in range(MAX_TOOL_ROUNDS + 1):
        response = client.responses.create(
            model=os.getenv("OPENAI_MODEL", "gpt-6-luna"),
            instructions=STORE_AGENT_INSTRUCTIONS,
            tools=TOOLS,
            input=input_items,
            parallel_tool_calls=False,
            store=False,
        )
        function_calls = [item for item in response.output if item.type == "function_call"]
        if not function_calls:
            return response.output_text, input_items + list(response.output)

        # Keep the model's function call items in the transcript before adding outputs.
        input_items.extend(response.output)
        for function_call in function_calls:
            try:
                arguments = json.loads(function_call.arguments)
                tool_output = call_tool(function_call.name, arguments, client)
            except Exception:
                tool_output = "Não consegui concluir essa consulta. Encaminhe para a equipe confirmar."
            input_items.append(
                {
                    "type": "function_call_output",
                    "call_id": function_call.call_id,
                    "output": tool_output,
                }
            )

    raise RuntimeError("The model exceeded the maximum number of tool rounds.")
