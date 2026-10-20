from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from backend.erros import NaoEncontrado
from backend.models import Cliente


def cadastrar_cliente(session: Session, nome: str, cpf: str) -> Cliente:
    """
    Cadastra um novo cliente.

    Raises:
        ValueError: Se o nome ou o CPF estiverem vazios, ou se o CPF já existir.
    """
    nome = (nome or "").strip()
    cpf = (cpf or "").strip()

    if not nome:
        raise ValueError("O nome do cliente é obrigatório.")
    if not cpf:
        raise ValueError("O CPF do cliente é obrigatório.")

    cliente = Cliente(nome=nome, cpf=cpf)

    try:
        session.add(cliente)
        session.commit()
    except IntegrityError:
        session.rollback()
        raise ValueError("Já existe um cliente cadastrado com este CPF.")

    session.refresh(cliente)
    return cliente


def alterar_nome(session: Session, cliente_id: int, novo_nome: str) -> Cliente:
    """
    Altera o nome de um cliente.

    Raises:
        NaoEncontrado: Se o cliente não existir.
        ValueError: Se o novo nome estiver vazio.
    """
    cliente = session.get(Cliente, cliente_id)

    if cliente is None:
        raise NaoEncontrado(f"Cliente com ID {cliente_id} não encontrado.")

    novo_nome = (novo_nome or "").strip()
    if not novo_nome:
        raise ValueError("O nome do cliente é obrigatório.")

    cliente.nome = novo_nome
    session.commit()
    session.refresh(cliente)

    return cliente
