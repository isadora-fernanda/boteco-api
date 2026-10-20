from decimal import Decimal

from sqlalchemy.orm import Session

from backend.erros import NaoEncontrado
from backend.models import Cartao, Saldo


def cadastrar_saldo(
    session: Session,
    cartao_id: int,
    saldo_inicial: Decimal = Decimal("0.00"),
) -> Saldo:
    saldo = Saldo(cartao_id=cartao_id, saldo=saldo_inicial)
    session.add(saldo)
    return saldo


def consultar_saldo(session: Session, cartao_id: int) -> Decimal:
    cartao = session.get(Cartao, cartao_id)

    if cartao is None:
        raise NaoEncontrado("Cartão não encontrado.")

    return cartao.saldo.saldo
