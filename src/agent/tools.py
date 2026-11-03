"""OpenAI Responses API function schemas and local tool dispatch."""

from typing import Any

from src.database.repository import StoreRepository
from src.knowledge.retrieval import retrieve_policy

_store = StoreRepository()

TOOLS: list[dict[str, Any]] = [
    {
        "type": "function",
        "name": "search_catalog",
        "description": "Search the product catalog for instruments, prices, and current stock in the supplied data.",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "The instrument, model, category, or budget to search for."}},
            "required": ["query"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "check_order",
        "description": "Look up an order after receiving both its order number and the full name of its customer.",
        "parameters": {
            "type": "object",
            "properties": {
                "order_number": {"type": "string", "description": "Numeric order number."},
                "customer_full_name": {"type": "string", "description": "Full name of the order holder."},
            },
            "required": ["order_number", "customer_full_name"],
            "additionalProperties": False,
        },
        "strict": True,
    },
    {
        "type": "function",
        "name": "search_store_policies",
        "description": "Find store policy information about hours, contact, payments, returns, warranty, shipping, or promotions.",
        "parameters": {
            "type": "object",
            "properties": {"question": {"type": "string", "description": "The customer's policy question."}},
            "required": ["question"],
            "additionalProperties": False,
        },
        "strict": True,
    },
]


def call_tool(name: str, arguments: dict[str, Any], openai_client: Any) -> str:
    """Dispatch a model function call to local, read-only application code."""
    if name == "search_catalog":
        return _store.search_catalog(arguments["query"])
    if name == "check_order":
        order_number = str(arguments["order_number"]).strip()
        full_name = str(arguments["customer_full_name"]).strip()
        if not order_number.isdigit() or not full_name:
            return "Para consultar, preciso do número do pedido e do nome completo do titular."
        return _store.lookup_order(order_number, full_name)
    if name == "search_store_policies":
        return retrieve_policy(arguments["question"], openai_client)
    raise ValueError(f"Unknown tool: {name}")
