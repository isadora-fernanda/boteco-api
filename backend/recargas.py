from decimal import Decimal

from sqlalchemy.orm import Session

from backend.erros import NaoEncontrado
from backend.models import Cartao, Recarga


def recarregar_cartao(session: Session, cartao_id: int, valor: Decimal) -> Recarga:
    """Registra uma recarga e soma o valor ao saldo do cartão."""
    cartao = session.get(Cartao, cartao_id)

    if cartao is None:
        raise NaoEncontrado("Cartão não encontrado.")

    if not cartao.ativo:
        raise ValueError("O cartão está desativado.")

    if valor <= Decimal("0"):
        raise ValueError("O valor da recarga deve ser maior que zero.")

    recarga = Recarga(cartao_id=cartao_id, valor_recarga=valor)

    session.add(recarga)
    cartao.saldo.saldo += valor
    session.commit()
    session.refresh(recarga)

    return recarga
