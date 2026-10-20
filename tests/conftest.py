import pytest

from backend.apis.api import create_app


@pytest.fixture
def client():
    # Cada teste começa com um banco SQLite novo, em memória
    app = create_app("sqlite:///:memory:")
    app.config["TESTING"] = True
    return app.test_client()


@pytest.fixture
def cliente_id(client):
    resposta = client.post("/api/cadastrar-cliente", json={"nome": "Maria Souza", "cpf": "123.456.789-00"})
    return resposta.get_json()["id"]


@pytest.fixture
def cartao_id(client, cliente_id):
    resposta = client.post("/api/cadastrar-cartao", json={"cliente_id": cliente_id})
    return resposta.get_json()["id"]


@pytest.fixture
def produto_id(client):
    # Chope a R$ 0,035 por ml, ou seja, R$ 17,50 por 500 ml
    resposta = client.post("/api/cadastrar-produto", json={"descricao": "Chope Pilsen", "preco": 0.035})
    return resposta.get_json()["id"]


@pytest.fixture
def saldo(client):
    """Consulta o saldo de um cartão pela API, como texto com 2 casas decimais."""
    def consultar(cartao_id):
        return client.get(f"/api/saldo/{cartao_id}").get_json()["saldo"]
    return consultar
