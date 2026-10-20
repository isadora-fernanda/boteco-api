from decimal import ROUND_HALF_UP, Decimal

from sqlalchemy.orm import Session

from backend.erros import NaoEncontrado
from backend.models import Cartao, Consumo, Produto

CENTAVO = Decimal("0.01")


def registrar_consumo(session: Session, cartao_id: int, produto_id: int, quantidade_ml: int) -> Consumo:
    """Registra um consumo e debita do saldo o preço por ml vezes a quantidade."""
    if quantidade_ml <= 0:
        raise ValueError("A quantidade em ml deve ser maior que zero.")

    cartao = session.get(Cartao, cartao_id)

    if cartao is None:
        raise NaoEncontrado("Cartão não encontrado.")

    if not cartao.ativo:
        raise ValueError("O cartão está desativado.")

    produto = session.get(Produto, produto_id)

    if produto is None:
        raise NaoEncontrado("Produto não encontrado.")

    # O preço tem 3 casas decimais e o saldo tem 2, então o valor é arredondado ao centavo
    valor_consumo = (produto.valorML * Decimal(quantidade_ml)).quantize(CENTAVO, rounding=ROUND_HALF_UP)

    if cartao.saldo.saldo < valor_consumo:
        raise ValueError("Saldo insuficiente.")

    consumo = Consumo(cartao_id=cartao_id, produto_id=produto_id, quantidade=quantidade_ml)

    session.add(consumo)
    cartao.saldo.saldo -= valor_consumo

    session.commit()
    session.refresh(consumo)

    return consumo
