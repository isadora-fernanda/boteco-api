def test_cartao_novo_comeca_com_saldo_zero(client, cartao_id, saldo):
    assert saldo(cartao_id) == "0.00"


def test_cartao_para_cliente_inexistente_retorna_404(client):
    resposta = client.post("/api/cadastrar-cartao", json={"cliente_id": 999})

    assert resposta.status_code == 404


def test_desativa_cartao(client, cartao_id):
    resposta = client.put("/api/alterar-ativo", json={"cartao_id": cartao_id, "ativo": False})

    assert resposta.status_code == 200


def test_ativo_precisa_ser_booleano(client, cartao_id):
    resposta = client.put("/api/alterar-ativo", json={"cartao_id": cartao_id, "ativo": "não"})

    assert resposta.status_code == 400


def test_saldo_de_cartao_inexistente_retorna_404(client):
    assert client.get("/api/saldo/999").status_code == 404


def test_recarga_soma_ao_saldo(client, cartao_id, saldo):
    client.post("/api/recarregar-cartao", json={"cartao_id": cartao_id, "valor": 50})
    resposta = client.post("/api/recarregar-cartao", json={"cartao_id": cartao_id, "valor": 10.25})

    assert resposta.status_code == 201
    assert saldo(cartao_id) == "60.25"


def test_recarga_com_valor_zero_ou_negativo(client, cartao_id, saldo):
    for valor in (0, -10):
        resposta = client.post("/api/recarregar-cartao", json={"cartao_id": cartao_id, "valor": valor})
        assert resposta.status_code == 400

    assert saldo(cartao_id) == "0.00"


def test_recarga_com_valor_que_nao_e_numero(client, cartao_id):
    resposta = client.post("/api/recarregar-cartao", json={"cartao_id": cartao_id, "valor": "dez"})

    assert resposta.status_code == 400


def test_recarga_em_cartao_inexistente_retorna_404(client):
    resposta = client.post("/api/recarregar-cartao", json={"cartao_id": 999, "valor": 20})

    assert resposta.status_code == 404


def test_recarga_em_cartao_desativado(client, cartao_id, saldo):
    client.put("/api/alterar-ativo", json={"cartao_id": cartao_id, "ativo": False})
    resposta = client.post("/api/recarregar-cartao", json={"cartao_id": cartao_id, "valor": 20})

    assert resposta.status_code == 400
    assert saldo(cartao_id) == "0.00"
