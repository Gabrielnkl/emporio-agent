"""Lightweight policy retrieval from curated rules transcribed from the PDF."""

from __future__ import annotations

import unicodedata


def _normalize(value: str) -> str:
    decomposed = unicodedata.normalize("NFKD", value.casefold())
    return "".join(char for char in decomposed if not unicodedata.combining(char))


POLICY_ANSWERS: tuple[tuple[tuple[str, ...], str], ...] = (
    (("horario", "abre", "fecha", "aberto", "funcionamento"),
     "Nosso horário é de segunda a sexta, das 9h às 18h, e aos sábados, das 9h às 13h. Domingos e feriados, fechado."),
    (("endereco", "onde fica", "localizacao", "telefone", "contato"),
     "Estamos na Rua 14 de Maio, 3200 — Centro, Campo Grande/MS, CEP 79202-333. Telefone: (67) 3341-4444."),
    (("pix", "parcel", "cartao", "pagamento", "boleto"),
     "Aceitamos PIX (5% de desconto sobre o preço de tabela), débito, crédito em até 12x sem juros (parcela mínima de R$ 100) e boleto à vista. O desconto PIX não acumula com promoções."),
    (("devol", "arrepend", "desisti"),
     "Em compras online, você pode pedir devolução em até 7 dias corridos após receber o produto, sem justificar. Ele deve estar sem uso e na embalagem original, com acessórios e manuais. O reembolso é feito pela forma de pagamento original em até 10 dias úteis; o frete de devolução fica por conta da loja."),
    (("troca", "defeito"),
     "Trocas por preferência podem ser solicitadas em até 7 dias, com o produto em perfeito estado e na embalagem original, sujeitas à disponibilidade. Para defeito de fabricação, o prazo de troca previsto pela loja é de 30 dias; depois disso, podemos intermediar a garantia do fabricante."),
    (("garantia",),
     "Todos os produtos têm garantia legal de 90 dias contra defeitos de fabricação, contados do recebimento. A garantia não cobre mau uso, quedas, condições climáticas extremas ou modificações não autorizadas."),
    (("frete", "entrega"),
     "Na região metropolitana de Campo Grande, o frete é grátis para pedidos acima de R$ 500; abaixo disso, custa R$ 35. O prazo estimado é de 1 a 3 dias úteis. Para outras cidades, usamos Correios ou Jadlog; consulte a equipe para prazo e valor do seu CEP."),
    (("promoc", "desconto"),
     "As promoções dependem do produto e do estoque, e não são cumulativas com o desconto de 5% no PIX. Posso consultar o catálogo se você me disser o modelo que procura."),
    (("acessorio", "corda", "palheta", "cabo", "case", "pedal", "amplificador"),
     "A loja trabalha exclusivamente com instrumentos musicais; não comercializamos acessórios. Posso ajudar a encontrar um instrumento do nosso catálogo."),
)


def search_policy(question: str) -> str | None:
    """Return the first curated policy entry matching a question."""
    query = _normalize(question)
    for terms, answer in POLICY_ANSWERS:
        if any(_normalize(term) in query for term in terms):
            return answer
    return None
