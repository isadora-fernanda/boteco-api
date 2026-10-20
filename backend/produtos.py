from decimal import Decimal

from sqlalchemy.orm import Session

from backend.erros import NaoEncontrado
from backend.models import Produto


def cadastrar_produto(session: Session, descricao: str, preco: Decimal) -> Produto:
    """Cadastra um produto com o preço por mililitro."""
    descricao = (descricao or "").strip()

    if not descricao:
        raise ValueError("O nome do produto é obrigatório.")

    if preco <= Decimal("0"):
        raise ValueError("O preço deve ser maior que zero.")

    produto = Produto(descricao=descricao, valorML=preco)

    session.add(produto)
    session.commit()
    session.refresh(produto)

    return produto


def alterar_produto(
    session: Session,
    produto_id: int,
    descricao: str | None = None,
    preco: Decimal | None = None,
) -> Produto:
    """Altera a descrição, o preço ou os dois."""
    produto = session.get(Produto, produto_id)

    if produto is None:
        raise NaoEncontrado("Produto não encontrado.")

    if descricao is not None:
        descricao = descricao.strip()
        if not descricao:
            raise ValueError("A descrição não pode estar vazia.")
        produto.descricao = descricao

    if preco is not None:
        if preco <= Decimal("0"):
            raise ValueError("O preço deve ser maior que zero.")
        produto.valorML = preco

    session.commit()
    session.refresh(produto)

    return produto
