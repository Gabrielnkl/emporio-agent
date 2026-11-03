"""Read-only repository over the CSV files supplied with the challenge."""

from __future__ import annotations

import csv
import re
import unicodedata
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"


def _normalize(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in normalized if not unicodedata.combining(char))


def _load(filename: str) -> list[dict[str, str]]:
    with (DATA / filename).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def _currency(amount: float) -> str:
    whole, cents = f"{amount:,.2f}".split(".")
    return f"R$ {whole.replace(',', '.')},{cents}"


class StoreRepository:
    """Small CSV repository. CSV remains the canonical source of truth."""

    def __init__(self) -> None:
        self.products = _load("products.csv")
        self.categories = {row["category_id"]: row["name"] for row in _load("categories.csv")}
        self.promotions = _load("promotions.csv")
        self.orders = _load("orders.csv")
        self.customers = _load("customers.csv")
        self.order_items = _load("order_items.csv")

    def search_catalog(self, query: str) -> str:
        q = _normalize(query)
        active = [p for p in self.products if p.get("status", "active").casefold() == "active"]
        budget_match = re.search(r"(?:ate|menos de|abaixo de)\s*r?\$?\s*([\d.,]+)", q)
        category_terms = {
            "5": ("violao", "violoes"), "1": ("guitarra", "guitarras"),
            "2": ("baixo", "baixos"), "4": ("teclado", "teclados", "piano"),
            "3": ("bateria", "baterias"), "9": ("ukulele", "ukuleles"),
        }
        if budget_match:
            raw_limit = budget_match.group(1)
            limit = float(raw_limit.replace(".", "").replace(",", ".") if "," in raw_limit else raw_limit)
            categories = [cid for cid, terms in category_terms.items() if any(term in q for term in terms)]
            matches = [p for p in active if float(p["price_brl"]) <= limit and
                       (not categories or p["category_id"] in categories)]
        else:
            ignored = {"quanto", "custa", "preco", "disponivel", "catalogo", "produto", "tem", "qual", "opcoes"}
            terms = [term for term in q.split() if len(term) > 2 and term not in ignored]
            matches = [p for p in active if any(term in _normalize(p["name"]) for term in terms)]

        matches.sort(key=lambda product: float(product["price_brl"]))
        if not matches:
            return "Não encontrei esse modelo no catálogo atual. Se me disser a categoria ou o estilo, procuro algumas opções."

        lines: list[str] = []
        for product in matches:
            stock = int(product["stock_quantity"])
            if budget_match and stock == 0:
                continue
            price = float(product["price_brl"])
            promotion = next((promo for promo in self.promotions
                              if promo["product_id"] == product["product_id"] and promo["is_active"] == "1"), None)
            if promotion:
                discount = float(promotion["discount_percent"])
                sale_price = price * (1 - discount / 100)
                price_text = f"{_currency(sale_price)} (de {_currency(price)}, {discount:g}% off)"
            else:
                price_text = _currency(price)
            stock_text = f"{stock} em estoque" if stock else "indisponível no momento"
            lines.append(f"• {product['name']} — {price_text}; {stock_text}")
            if len(lines) == (8 if budget_match else 5):
                break
        if not lines:
            return "Encontrei opções nessa faixa, mas estão sem estoque no momento. Quer que eu procure alternativas?"
        lead = "Consultei o catálogo e encontrei estas opções:" if budget_match else "Consultei o catálogo:"
        return lead + "\n" + "\n".join(lines)

    def lookup_order(self, order_number: str, customer_full_name: str) -> str:
        if not order_number.isdigit() or not customer_full_name.strip():
            return "Para consultar, preciso do número do pedido e do nome completo do titular."
        order = next((row for row in self.orders if row["order_id"] == order_number), None)
        if not order:
            return "Não encontrei esse pedido nos dados disponíveis. Confira o número ou fale com a equipe pelo (67) 3341-4444."
        customer = next((row for row in self.customers if row["customer_id"] == order["customer_id"]), None)
        if not customer:
            return "Encontrei o pedido, mas não consegui validar o titular. A equipe pode ajudar pelo (67) 3341-4444."
        supplied = _normalize(customer_full_name)
        if not all(token in supplied for token in _normalize(customer["name"]).split() if len(token) > 2):
            return "Os dados não conferem. Confira o número do pedido e o nome completo do titular."
        item_names = []
        for item in self.order_items:
            if item["order_id"] != order_number:
                continue
            product = next((p for p in self.products if p["product_id"] == item["product_id"]), None)
            if product:
                item_names.append(f"{item['quantity']}× {product['name']}")
        status = order["status"].replace("_", " ").capitalize()
        answer = f"Pedido {order_number}: status {status}."
        if item_names:
            answer += " Itens: " + ", ".join(item_names) + "."
        if order.get("estimated_delivery"):
            answer += f" Previsão registrada: {order['estimated_delivery']}."
        if order.get("tracking_code"):
            answer += f" Código de rastreio: {order['tracking_code']}."
        return answer


def search_policy(question: str) -> str | None:
    """Return a concise, curated answer grounded in the supplied policy PDF."""
    q = _normalize(question)
    if any(term in q for term in ("horario", "abre", "fecha", "aberto", "funcionamento")):
        return "Nosso horário é de segunda a sexta, das 9h às 18h, e aos sábados, das 9h às 13h. Domingos e feriados, fechado."
    if any(term in q for term in ("endereco", "onde fica", "localizacao", "telefone", "contato")):
        return "Estamos na Rua 14 de Maio, 3200 — Centro, Campo Grande/MS, CEP 79202-333. Telefone: (67) 3341-4444."
    if any(term in q for term in ("pix", "parcel", "cartao", "pagamento", "boleto")):
        return "Aceitamos PIX (5% de desconto sobre o preço de tabela), débito, crédito em até 12x sem juros (parcela mínima de R$ 100) e boleto à vista. O desconto PIX não acumula com promoções."
    if any(term in q for term in ("devol", "arrepend", "desisti")):
        return "Em compras online, você pode pedir devolução em até 7 dias corridos após receber o produto, sem justificar. Ele deve estar sem uso e na embalagem original, com acessórios e manuais. O reembolso é feito pela forma de pagamento original em até 10 dias úteis; o frete de devolução fica por conta da loja."
    if any(term in q for term in ("troca", "defeito")):
        return "Trocas por preferência podem ser solicitadas em até 7 dias, com o produto em perfeito estado e na embalagem original, sujeitas à disponibilidade. Para defeito de fabricação, o prazo de troca previsto pela loja é de 30 dias; depois disso, podemos intermediar a garantia do fabricante."
    if "garantia" in q:
        return "Todos os produtos têm garantia legal de 90 dias contra defeitos de fabricação, contados do recebimento. A garantia não cobre mau uso, quedas, condições climáticas extremas ou modificações não autorizadas."
    if any(term in q for term in ("frete", "entrega")):
        return "Na região metropolitana de Campo Grande, o frete é grátis para pedidos acima de R$ 500; abaixo disso, custa R$ 35. O prazo estimado é de 1 a 3 dias úteis. Para outras cidades, usamos Correios ou Jadlog; consulte a equipe para prazo e valor do seu CEP."
    if any(term in q for term in ("promoc", "desconto")):
        return "As promoções dependem do produto e do estoque, e não são cumulativas com o desconto de 5% no PIX. Posso consultar o catálogo se você me disser o modelo que procura."
    if any(term in q for term in ("acessorio", "corda", "palheta", "cabo", "case", "pedal", "amplificador")):
        return "A loja trabalha exclusivamente com instrumentos musicais; não comercializamos acessórios. Posso ajudar a encontrar um instrumento do nosso catálogo."
    return None
