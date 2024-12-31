from web3 import Web3


def is_eq_address(addr1: str, addr2: str) -> bool:
    addr1_checksum = Web3.to_checksum_address(addr1)
    addr2_checksum = Web3.to_checksum_address(addr2)

    return addr1_checksum == addr2_checksum
