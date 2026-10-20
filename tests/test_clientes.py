def test_cadastra_cliente(client):
    resposta = client.post("/api/cadastrar-cliente", json={"nome": "João Lima", "cpf": "111.222.333-44"})

    assert resposta.status_code == 201
    assert resposta.get_json()["id"] == 1


def test_nao_aceita_cpf_repetido(client, cliente_id):
    resposta = client.post("/api/cadastrar-cliente", json={"nome": "Outra Pessoa", "cpf": "123.456.789-00"})

    assert resposta.status_code == 400
    assert "CPF" in resposta.get_json()["error"]


def test_exige_nome_e_cpf(client):
    resposta = client.post("/api/cadastrar-cliente", json={"nome": "Sem CPF"})

    assert resposta.status_code == 400
    assert "cpf" in resposta.get_json()["error"]


def test_nao_aceita_nome_em_branco(client):
    resposta = client.post("/api/cadastrar-cliente", json={"nome": "   ", "cpf": "999.888.777-66"})

    assert resposta.status_code == 400


def test_recusa_corpo_que_nao_e_json(client):
    resposta = client.post("/api/cadastrar-cliente", data="nome=Maria", content_type="text/plain")

    assert resposta.status_code == 400


def test_altera_nome(client, cliente_id):
    resposta = client.put("/api/alterar-nome-cliente", json={"id": cliente_id, "nome": "Maria S. Lima"})

    assert resposta.status_code == 200


def test_alterar_nome_de_cliente_inexistente_retorna_404(client):
    resposta = client.put("/api/alterar-nome-cliente", json={"id": 999, "nome": "Ninguém"})

    assert resposta.status_code == 404
