from dotenv import load_dotenv
from eth_account.messages import encode_defunct
from web3 import Web3
import os
import sys


def load_config():
    load_dotenv()
    pkey = os.getenv("PRIVATE_KEY")
    mainnet_endpoint = os.getenv("MAINNET_RPC")

    if not pkey:
        print("private key not found in .env")
    if not mainnet_endpoint:
        print("mainnet_endpoint not found in .env")

    return {"pkey": pkey, "mainnet_endpoint": mainnet_endpoint}


def sign_msg(provider, pkey: str, msg: str):
    encoded_msg = encode_defunct(text=str(msg))
    signed_msg = provider.eth.account.sign_message(encoded_msg, pkey)
    return {"signature": signed_msg["signature"], "signed_message": msg}


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("msg not found.")
        exit()

    msg = sys.argv[1]
    config = load_config()
    endpoint = config["mainnet_endpoint"]
    pkey = config["pkey"]
    w3 = Web3(Web3.HTTPProvider(endpoint))
    if not w3.is_connected():
        print(f"Failed to connect to {endpoint}")
    print("Signing message...")
    print(f"wallet_address: {w3.eth.account.from_key(pkey).address}")
    print("message to be signed: ", msg)
    sign = sign_msg(w3, pkey, msg)
    if sign:
        print("Message signed.")
        print(f"Signature: {sign['signature'].hex()}")
    else:
        print(f"failed to sign msg: {msg}")
