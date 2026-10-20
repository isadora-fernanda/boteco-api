def test_cadastra_produto(client):
    resposta = client.post("/api/cadastrar-produto", json={"descricao": "Chope IPA", "preco": 0.05})

    assert resposta.status_code == 201


def test_produto_precisa_de_descricao_e_preco_positivo(client):
    sem_nome = client.post("/api/cadastrar-produto", json={"descricao": " ", "preco": 0.05})
    preco_zero = client.post("/api/cadastrar-produto", json={"descricao": "Chope", "preco": 0})

    assert sem_nome.status_code == 400
    assert preco_zero.status_code == 400


def test_altera_so_o_preco(client, produto_id):
    resposta = client.patch("/api/alterar-produto", json={"produto_id": produto_id, "preco": 0.04})

    assert resposta.status_code == 200


def test_alterar_produto_inexistente_retorna_404(client):
    resposta = client.patch("/api/alterar-produto", json={"produto_id": 999, "descricao": "Nada"})

    assert resposta.status_code == 404


def test_consumo_debita_preco_por_ml_vezes_quantidade(client, cartao_id, produto_id, saldo):
    client.post("/api/recarregar-cartao", json={"cartao_id": cartao_id, "valor": 50})

    resposta = client.post(
        "/api/registrar-consumo",
        json={"cartao_id": cartao_id, "produto_id": produto_id, "quantidade": 500},
    )

    assert resposta.status_code == 201
    # 500 ml x R$ 0,035 = R$ 17,50
    assert saldo(cartao_id) == "32.50"


def test_consumo_recusa_valor_acima_do_saldo_e_arredonda_ao_centavo(client, cartao_id, produto_id, saldo):
    client.post("/api/recarregar-cartao", json={"cartao_id": cartao_id, "valor": 10})

    client.post(
        "/api/registrar-consumo",
        json={"cartao_id": cartao_id, "produto_id": produto_id, "quantidade": 333},
    )

    # 333 ml x R$ 0,035 = R$ 11,655, que passa do saldo e é recusado
    assert saldo(cartao_id) == "10.00"

    client.post(
        "/api/registrar-consumo",
        json={"cartao_id": cartao_id, "produto_id": produto_id, "quantidade": 99},
    )

    # 99 ml x R$ 0,035 = R$ 3,465, arredondado para R$ 3,47
    assert saldo(cartao_id) == "6.53"


def test_consumo_com_saldo_insuficiente_nao_altera_saldo(client, cartao_id, produto_id, saldo):
    client.post("/api/recarregar-cartao", json={"cartao_id": cartao_id, "valor": 5})

    resposta = client.post(
        "/api/registrar-consumo",
        json={"cartao_id": cartao_id, "produto_id": produto_id, "quantidade": 500},
    )

    assert resposta.status_code == 400
    assert "Saldo insuficiente" in resposta.get_json()["error"]
    assert saldo(cartao_id) == "5.00"


def test_consumo_em_cartao_desativado(client, cartao_id, produto_id, saldo):
    client.post("/api/recarregar-cartao", json={"cartao_id": cartao_id, "valor": 50})
    client.put("/api/alterar-ativo", json={"cartao_id": cartao_id, "ativo": False})

    resposta = client.post(
        "/api/registrar-consumo",
        json={"cartao_id": cartao_id, "produto_id": produto_id, "quantidade": 300},
    )

    assert resposta.status_code == 400
    assert saldo(cartao_id) == "50.00"


def test_consumo_com_quantidade_invalida(client, cartao_id, produto_id):
    for quantidade in (0, -100, 2.5):
        resposta = client.post(
            "/api/registrar-consumo",
            json={"cartao_id": cartao_id, "produto_id": produto_id, "quantidade": quantidade},
        )
        assert resposta.status_code == 400


def test_consumo_de_produto_inexistente_retorna_404(client, cartao_id):
    client.post("/api/recarregar-cartao", json={"cartao_id": cartao_id, "valor": 50})

    resposta = client.post(
        "/api/registrar-consumo",
        json={"cartao_id": cartao_id, "produto_id": 999, "quantidade": 300},
    )

    assert resposta.status_code == 404
