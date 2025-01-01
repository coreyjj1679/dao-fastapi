from ..main import app
from fastapi.testclient import TestClient
from eth_account.messages import encode_defunct
from web3 import Web3

client = TestClient(app)


def test_create_vote_success():
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

    jwt_token = auth_res.json()["token"]
    headers = {"Authorization": f"Bearer {jwt_token}"}
    create_proposal_res = client.post(
        "/proposals",
        params={
            "title": "test proposal",
            "description": "test description",
        },
        headers=headers,
    )

    proposal_id = create_proposal_res.json()["proposal_id"]
    endpoint = f"/proposals/{proposal_id}/vote"

    vote_res = client.post(
        endpoint,
        params={
            "proposal_id": proposal_id,
            "option": "yes",
        },
        headers=headers,
    )

    assert vote_res.status_code == 200


def test_create_vote_fail():
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

    jwt_token = auth_res.json()["token"]
    headers = {"Authorization": f"Bearer {jwt_token}"}
    create_proposal_res = client.post(
        "/proposals",
        params={
            "title": "test proposal",
            "description": "test description",
        },
        headers=headers,
    )

    proposal_id = create_proposal_res.json()["proposal_id"]
    endpoint = f"/proposals/{proposal_id}/vote"

    vote_res = client.post(
        endpoint,
        params={
            "proposal_id": proposal_id,
            "option": "yes",
        },
    )

    assert vote_res.status_code == 403
