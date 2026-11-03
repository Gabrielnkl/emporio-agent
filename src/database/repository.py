"""Read-only repositories for products and order records."""

from __future__ import annotations

import re
import unicodedata
from decimal import Decimal

from .connection import CsvDataSource
from .models import Category, Customer, Order, OrderItem, Product, Promotion


def _normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


def _currency(amount: Decimal) -> str:
    whole, cents = f"{amount:,.2f}".split(".")
    return f"R$ {whole.replace(',', '.')},{cents}"


class StoreRepository:
    """Load the challenge's CSV records and answer deterministic lookups."""

    def __init__(self, source: CsvDataSource | None = None) -> None:
        self.source = source or CsvDataSource()
        self.categories = {
            category.category_id: category
            for category in map(Category.from_row, self.source.read("categories.csv"))
        }
        self.products = list(map(Product.from_row, self.source.read("products.csv")))
        self.customers = list(map(Customer.from_row, self.source.read("customers.csv")))
        self.orders = list(map(Order.from_row, self.source.read("orders.csv")))
        self.order_items = list(map(OrderItem.from_row, self.source.read("order_items.csv")))
        self.promotions = list(map(Promotion.from_row, self.source.read("promotions.csv")))

    def search_catalog(self, query: str) -> str:
        normalized_query = _normalize(query)
        active_products = [product for product in self.products if product.status.casefold() == "active"]
        budget_match = re.search(r"(?:ate|menos de|abaixo de)\s*r?\$?\s*([\d.,]+)", normalized_query)
        category_terms = {
            5: ("violao", "violoes"), 1: ("guitarra", "guitarras"),
            2: ("baixo", "baixos"), 4: ("teclado", "teclados", "piano"),
            3: ("bateria", "baterias"), 9: ("ukulele", "ukuleles"),
        }

        if budget_match:
            raw_limit = budget_match.group(1)
            normalized_limit = raw_limit.replace(".", "").replace(",", ".") if "," in raw_limit else raw_limit
            limit = Decimal(normalized_limit)
            categories = [
                category_id
                for category_id, terms in category_terms.items()
                if any(term in normalized_query for term in terms)
            ]
            matches = [
                product for product in active_products
                if product.price_brl <= limit
                and (not categories or product.category_id in categories)
            ]
        else:
            ignored = {"quanto", "custa", "preco", "disponivel", "catalogo", "produto", "tem", "qual", "opcoes"}
            terms = [term for term in normalized_query.split() if len(term) > 2 and term not in ignored]
            matches = [
                product for product in active_products
                if any(term in _normalize(product.name) for term in terms)
            ]

        matches.sort(key=lambda product: product.price_brl)
        if not matches:
            return "Não encontrei esse modelo no catálogo atual. Se me disser a categoria ou o estilo, procuro algumas opções."

        lines: list[str] = []
        for product in matches:
            if budget_match and product.stock_quantity == 0:
                continue
            promotion = next(
                (promo for promo in self.promotions if promo.product_id == product.product_id and promo.is_active),
                None,
            )
            if promotion:
                sale_price = product.price_brl * (Decimal("1") - promotion.discount_percent / Decimal("100"))
                price_text = (
                    f"{_currency(sale_price)} (de {_currency(product.price_brl)}, "
                    f"{promotion.discount_percent:g}% off)"
                )
            else:
                price_text = _currency(product.price_brl)
            stock_text = (
                f"{product.stock_quantity} em estoque"
                if product.stock_quantity
                else "indisponível no momento"
            )
            lines.append(f"• {product.name} — {price_text}; {stock_text}")
            if len(lines) == (8 if budget_match else 5):
                break

        if not lines:
            return "Encontrei opções nessa faixa, mas estão sem estoque no momento. Quer que eu procure alternativas?"
        lead = "Consultei o catálogo e encontrei estas opções:" if budget_match else "Consultei o catálogo:"
        return lead + "\n" + "\n".join(lines)

    def lookup_order(self, order_number: str, customer_full_name: str) -> str:
        if not order_number.isdigit() or not customer_full_name.strip():
            return "Para consultar, preciso do número do pedido e do nome completo do titular."
        order = next((record for record in self.orders if str(record.order_id) == order_number), None)
        if not order:
            return "Não encontrei esse pedido nos dados disponíveis. Confira o número ou fale com a equipe pelo (67) 3341-4444."
        customer = next((record for record in self.customers if record.customer_id == order.customer_id), None)
        if not customer:
            return "Encontrei o pedido, mas não consegui validar o titular. A equipe pode ajudar pelo (67) 3341-4444."

        supplied_name = _normalize(customer_full_name)
        required_tokens = [token for token in _normalize(customer.name).split() if len(token) > 2]
        if not all(token in supplied_name for token in required_tokens):
            return "Os dados não conferem. Confira o número do pedido e o nome completo do titular."

        product_by_id = {product.product_id: product for product in self.products}
        item_names = [
            f"{item.quantity}× {product_by_id[item.product_id].name}"
            for item in self.order_items
            if item.order_id == order.order_id and item.product_id in product_by_id
        ]
        answer = f"Pedido {order_number}: status {order.status.replace('_', ' ').capitalize()}."
        if item_names:
            answer += " Itens: " + ", ".join(item_names) + "."
        if order.estimated_delivery:
            answer += f" Previsão registrada: {order.estimated_delivery}."
        if order.tracking_code:
            answer += f" Código de rastreio: {order.tracking_code}."
        return answer
