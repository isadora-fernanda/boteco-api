from sqlalchemy.orm import Session

from backend.erros import NaoEncontrado
from backend.models import Cartao, Cliente
from backend.saldo import cadastrar_saldo


def cadastrar_cartao(session: Session, cliente_id: int) -> Cartao:
    """Cria um cartão ativo para o cliente, já com saldo zero."""
    cliente = session.get(Cliente, cliente_id)

    if cliente is None:
        raise NaoEncontrado("Cliente não encontrado.")

    cartao = Cartao(cliente_id=cliente_id, ativo=True)

    session.add(cartao)
    session.flush()

    cadastrar_saldo(session, cartao.id)

    session.commit()
    session.refresh(cartao)

    return cartao


def alterar_ativo(session: Session, cartao_id: int, ativo: bool) -> Cartao:
    """Ativa ou desativa um cartão."""
    if not isinstance(ativo, bool):
        raise ValueError("O campo 'ativo' deve ser true ou false.")

    cartao = session.get(Cartao, cartao_id)

    if cartao is None:
        raise NaoEncontrado("Cartão não encontrado.")

    cartao.ativo = ativo

    session.commit()
    session.refresh(cartao)

    return cartao
