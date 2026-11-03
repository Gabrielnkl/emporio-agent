"""Function tools backed by the supplied CSV and policy data."""

from agents import function_tool

from src.database.repository import StoreRepository
from src.knowledge.retrieval import search_policy

_store = StoreRepository()


@function_tool
def search_catalog(query: str) -> str:
    """Search the current product catalog for matching instruments, prices, and stock."""
    return _store.search_catalog(query)


@function_tool
def check_order(order_number: str, customer_full_name: str) -> str:
    """Look up an order. Requires both its number and the full name of its customer."""
    order_number = order_number.strip()
    customer_full_name = customer_full_name.strip()
    if not order_number.isdigit():
        return "Número de pedido inválido. Peça ao cliente para conferir o número."
    if not customer_full_name:
        return "Para proteger os dados do cliente, solicite o nome completo do titular antes da consulta."
    return _store.lookup_order(order_number, customer_full_name)


@function_tool
def search_store_policies(question: str) -> str:
    """Find store policy information about hours, contact, payments, returns, warranty, shipping, or promotions."""
    answer = search_policy(question)
    return answer or "Não encontrei uma regra da loja que responda a essa pergunta. Encaminhe para a equipe confirmar."
