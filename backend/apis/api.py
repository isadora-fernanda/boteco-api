from decimal import Decimal, InvalidOperation

from flask import Blueprint, Flask, current_app, request
from sqlalchemy.orm import Session, sessionmaker

from backend.cartoes import alterar_ativo, cadastrar_cartao
from backend.clientes import alterar_nome, cadastrar_cliente
from backend.connection import criar_engine
from backend.consumos import registrar_consumo
from backend.erros import NaoEncontrado
from backend.models import Base
from backend.produtos import alterar_produto, cadastrar_produto
from backend.recargas import recarregar_cartao
from backend.saldo import consultar_saldo

bp = Blueprint("api", __name__, url_prefix="/api")


# ==========================
# Funções auxiliares
# ==========================
def nova_sessao() -> Session:
    return current_app.config["SESSION_FACTORY"]()


def ler_json(*campos: str) -> dict:
    """Lê o corpo da requisição e confere se os campos obrigatórios vieram."""
    dados = request.get_json(silent=True)

    if not isinstance(dados, dict):
        raise ValueError("O corpo da requisição deve ser um JSON.")

    faltando = [campo for campo in campos if campo not in dados]
    if faltando:
        raise ValueError(f"Campos obrigatórios ausentes: {', '.join(faltando)}.")

    return dados


def para_inteiro(valor, campo: str) -> int:
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValueError(f"O campo '{campo}' deve ser um número inteiro.")
    return valor


def para_decimal(valor, campo: str) -> Decimal:
    # Converte pelo texto para não carregar o erro de arredondamento do float
    if isinstance(valor, bool):
        raise ValueError(f"O campo '{campo}' deve ser um número.")
    try:
        numero = Decimal(str(valor))
    except InvalidOperation:
        raise ValueError(f"O campo '{campo}' deve ser um número.")
    if not numero.is_finite():
        raise ValueError(f"O campo '{campo}' deve ser um número.")
    return numero


# ==========================
# Clientes
# ==========================
@bp.route("/cadastrar-cliente", methods=["POST"])
def cadastrar_cliente_api():
    dados = ler_json("nome", "cpf")

    with nova_sessao() as session:
        cliente = cadastrar_cliente(session, dados["nome"], dados["cpf"])
        return {"message": "Cliente cadastrado.", "id": cliente.id}, 201


@bp.route("/alterar-nome-cliente", methods=["PUT"])
def alterar_nome_cliente_api():
    dados = ler_json("id", "nome")

    with nova_sessao() as session:
        alterar_nome(session, para_inteiro(dados["id"], "id"), dados["nome"])
        return {"message": "Nome alterado."}, 200


# ==========================
# Cartões
# ==========================
@bp.route("/cadastrar-cartao", methods=["POST"])
def cadastrar_cartao_api():
    dados = ler_json("cliente_id")

    with nova_sessao() as session:
        cartao = cadastrar_cartao(session, para_inteiro(dados["cliente_id"], "cliente_id"))
        return {"message": "Cartão cadastrado.", "id": cartao.id}, 201


@bp.route("/alterar-ativo", methods=["PUT"])
def alterar_ativo_cartao_api():
    dados = ler_json("cartao_id", "ativo")

    with nova_sessao() as session:
        alterar_ativo(session, para_inteiro(dados["cartao_id"], "cartao_id"), dados["ativo"])
        return {"message": "Cartão alterado."}, 200


@bp.route("/recarregar-cartao", methods=["POST"])
def recarregar_cartao_api():
    dados = ler_json("cartao_id", "valor")

    with nova_sessao() as session:
        recarga = recarregar_cartao(
            session,
            para_inteiro(dados["cartao_id"], "cartao_id"),
            para_decimal(dados["valor"], "valor"),
        )
        return {"message": "Recarga registrada.", "id": recarga.id}, 201


@bp.route("/saldo/<int:cartao_id>", methods=["GET"])
def consultar_saldo_api(cartao_id: int):
    with nova_sessao() as session:
        saldo = consultar_saldo(session, cartao_id)
        return {"cartao_id": cartao_id, "saldo": f"{saldo:.2f}"}, 200


# ==========================
# Produtos
# ==========================
@bp.route("/cadastrar-produto", methods=["POST"])
def cadastrar_produto_api():
    dados = ler_json("descricao", "preco")

    with nova_sessao() as session:
        produto = cadastrar_produto(session, dados["descricao"], para_decimal(dados["preco"], "preco"))
        return {"message": "Produto cadastrado.", "id": produto.id}, 201


@bp.route("/alterar-produto", methods=["PATCH"])
def alterar_produto_api():
    dados = ler_json("produto_id")
    preco = para_decimal(dados["preco"], "preco") if "preco" in dados else None

    with nova_sessao() as session:
        produto = alterar_produto(
            session,
            para_inteiro(dados["produto_id"], "produto_id"),
            dados.get("descricao"),
            preco,
        )
        return {"message": "Produto alterado.", "id": produto.id}, 200


# ==========================
# Consumos
# ==========================
@bp.route("/registrar-consumo", methods=["POST"])
def registrar_consumo_api():
    dados = ler_json("cartao_id", "produto_id", "quantidade")

    with nova_sessao() as session:
        consumo = registrar_consumo(
            session,
            para_inteiro(dados["cartao_id"], "cartao_id"),
            para_inteiro(dados["produto_id"], "produto_id"),
            para_inteiro(dados["quantidade"], "quantidade"),
        )
        return {"message": "Consumo registrado.", "id": consumo.id}, 201


# ==========================
# Aplicação
# ==========================
def create_app(database_url: str | None = None) -> Flask:
    app = Flask(__name__)

    engine = criar_engine(database_url)
    Base.metadata.create_all(engine)
    app.config["SESSION_FACTORY"] = sessionmaker(bind=engine, autoflush=True)

    app.register_blueprint(bp)

    @app.errorhandler(NaoEncontrado)
    def nao_encontrado(erro):
        return {"error": str(erro)}, 404

    @app.errorhandler(ValueError)
    def dado_invalido(erro):
        return {"error": str(erro)}, 400

    return app
