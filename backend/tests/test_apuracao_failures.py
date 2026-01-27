import pytest
import requests
from datetime import datetime, timedelta, timezone



BASE_URL = "http://localhost:8000/api/v1"


def _create_rifa(token_value: str, status: str) -> str:
    headers = {"Authorization": f"Bearer {token_value}"}
    now = datetime.now(timezone.utc)
    payload = {
        "titulo": f"Rifa Falha {now.timestamp()}",
        "descricao": "Rifa criada para testes de falha de apuração",
        "preco_numero": 10.0,
        "tipo_rifa": "dezena",
        "data_sorteio": (now + timedelta(hours=1)).isoformat(),
        "hora_encerramento": (now + timedelta(minutes=30)).isoformat(),
        "local_sorteio": "PT-RJ",
        "status": status,
    }
    res = requests.post(f"{BASE_URL}/rifas/", json=payload, headers=headers)
    assert res.status_code == 200, f"Falha ao criar rifa: {res.text}"
    data = res.json()
    return data["id"]


def _criar_resultado(token_value: str, rifa_id_value: str, resultado: str = "01") -> None:
    headers = {"Authorization": f"Bearer {token_value}"}
    payload = {
        "resultado": resultado,
        "local_sorteio": "PT-RJ",
        "data_resultado": datetime.now(timezone.utc).isoformat(),
    }
    res = requests.post(
        f"{BASE_URL}/admin/rifas/{rifa_id_value}/resultado",
        json=payload,
        headers=headers,
    )
    assert res.status_code == 200, f"Falha ao lançar resultado: {res.text}"


def _pagar_numero(token_value: str, rifa_id_value: str) -> str:
    headers = {"Authorization": f"Bearer {token_value}"}
    numeros_res = requests.get(f"{BASE_URL}/rifas/{rifa_id_value}/numeros", headers=headers)
    assert numeros_res.status_code == 200, f"Falha ao listar números: {numeros_res.text}"
    numeros = numeros_res.json()
    if not numeros:
        raise AssertionError("Nenhum número disponível na rifa para teste")

    alvo = numeros[0]
    numero = alvo["numero"]

    if alvo["status"] == "livre":
        reserva_res = requests.post(
            f"{BASE_URL}/rifas/{rifa_id_value}/numeros/{numero}/reservar",
            headers=headers,
        )
        assert reserva_res.status_code == 200, f"Falha ao reservar número: {reserva_res.text}"

        numeros_res = requests.get(f"{BASE_URL}/rifas/{rifa_id_value}/numeros", headers=headers)
        assert numeros_res.status_code == 200, f"Falha ao reler números: {numeros_res.text}"
        numeros = numeros_res.json()
        alvo = next((n for n in numeros if n["numero"] == numero), None)
        assert alvo is not None, "Número reservado não encontrado após reserva"

    payment_id = alvo.get("payment_id")
    assert payment_id, "payment_id não encontrado para número reservado"

    webhook_res = requests.post(
        f"{BASE_URL}/webhooks/picpay",
        json={"payment_id": payment_id, "status": "paid"},
    )
    assert webhook_res.status_code == 200, f"Falha no webhook PicPay: {webhook_res.text}"

    return numero


def test_apurar_sem_numeros_pagos(token):
    token_value = token
    rifa_id_local = _create_rifa(token_value, "encerrada")
    _criar_resultado(token_value, rifa_id_local, resultado="01")

    headers = {"Authorization": f"Bearer {token_value}"}
    res = requests.post(f"{BASE_URL}/admin/rifas/{rifa_id_local}/apurar", headers=headers)

    assert res.status_code == 400
    detail = res.json().get("detail", "").lower()
    assert "nenhum" in detail and "número pago" in detail


def test_apurar_rifa_nao_encerrada(token):
    token_value = token
    rifa_id_local = _create_rifa(token_value, "ativa")

    headers = {"Authorization": f"Bearer {token_value}"}
    res = requests.post(f"{BASE_URL}/admin/rifas/{rifa_id_local}/apurar", headers=headers)

    assert res.status_code == 400
    assert res.json().get("detail") == "Rifa precisa estar ENCERRADA para apuração"


def test_lancar_resultado_duas_vezes(token):
    token_value = token
    rifa_id_local = _create_rifa(token_value, "encerrada")

    headers = {"Authorization": f"Bearer {token_value}"}
    payload = {
        "resultado": "01",
        "local_sorteio": "PT-RJ",
        "data_resultado": datetime.now(timezone.utc).isoformat(),
    }

    primeira = requests.post(
        f"{BASE_URL}/admin/rifas/{rifa_id_local}/resultado",
        json=payload,
        headers=headers,
    )
    assert primeira.status_code == 200

    segunda = requests.post(
        f"{BASE_URL}/admin/rifas/{rifa_id_local}/resultado",
        json=payload,
        headers=headers,
    )
    assert segunda.status_code == 400
    assert segunda.json().get("detail") == "Resultado já lançado para esta rifa"


def test_apurar_resultado_sem_qualquer_ganhador(token):
    token_value = token
    rifa_id_local = _create_rifa(token_value, "ativa")

    pago_numero = _pagar_numero(token_value, rifa_id_local)

    headers = {"Authorization": f"Bearer {token_value}"}
    fechar_res = requests.post(
        f"{BASE_URL}/admin/rifas/{rifa_id_local}/fechar",
        headers=headers,
    )
    assert fechar_res.status_code == 200, f"Falha ao fechar rifa: {fechar_res.text}"

    resultado_invalido = "99" if pago_numero != "99" else "98"
    _criar_resultado(token_value, rifa_id_local, resultado=resultado_invalido)

    res = requests.post(f"{BASE_URL}/admin/rifas/{rifa_id_local}/apurar", headers=headers)

    assert res.status_code == 400
    detail = res.json().get("detail", "").lower()
    assert "sem ganhador" in detail or "nenhum ganhador" in detail


def test_apurar_rifa_outro_tenant(token, rifa_id):
    token_value = token
    headers = {
        "Authorization": f"Bearer {token_value}",
        "Host": "outro-tenant.com",
    }
    res = requests.post(f"{BASE_URL}/admin/rifas/{rifa_id}/apurar", headers=headers)

    assert res.status_code in (400, 404)
    detail = res.json().get("detail", "")
    assert "tenant" in detail.lower() or "não encontrada" in detail.lower()

