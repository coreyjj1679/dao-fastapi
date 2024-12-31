import pytest
from ..main import app
from fastapi.testclient import TestClient
from eth_account.messages import encode_defunct
from web3 import Web3
from ..dependencies import SessionDep

client = TestClient(app)


def test_request_nonce_success():
    response = client.post(
        "/auth/request-nonce",
    )
    assert response.status_code == 200
    assert "nonce" in response.json()


def test_login_success():
    response = client.post(
        "/auth/request-nonce",
    )

    nonce = response.json()["nonce"]

    # create dummy web3 address
    w3 = Web3(Web3.HTTPProvider("https://eth.llamarpc.com"))

    acc = w3.eth.account.create()
    private_key = w3.to_hex(acc.key)
    wallet_address = acc.address

    encoded_msg = encode_defunct(text=str(nonce))
    signed_msg = w3.eth.account.sign_message(encoded_msg, private_key)

    signautre = signed_msg["signature"].hex()

    auth_res = client.post(
        "/auth/login",
        params={
            "wallet_address": wallet_address,
            "signed_message": nonce,
            "signature": signautre,
        },
    )

    assert auth_res.status_code == 200


def test_login_fail():
    response = client.post(
        "/auth/request-nonce",
    )

    nonce = response.json()["nonce"]

    # create dummy web3 address
    w3 = Web3(Web3.HTTPProvider("https://eth.llamarpc.com"))

    acc = w3.eth.account.create()
    private_key = w3.to_hex(acc.key)
    wallet_address = acc.address

    encoded_msg = encode_defunct(text=str(nonce))
    signed_msg = w3.eth.account.sign_message(encoded_msg, private_key)

    signautre = signed_msg["signature"].hex()

    # incorrect nonce
    auth_res = client.post(
        "/auth/login",
        params={
            "wallet_address": wallet_address,
            "signed_message": nonce[::-1],
            "signature": signautre,
        },
    )

    assert auth_res.status_code == 401
