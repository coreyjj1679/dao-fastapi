import jwt
from datetime import datetime, timedelta, timezone
from typing import Annotated
from uuid import uuid4
from eth_account.messages import encode_defunct
from fastapi import APIRouter, HTTPException, Query
from web3 import Web3
from config import SECRET_KEY, TOKEN_DURATION_MINUTES
from ..utils import is_eq_address
from ..dependencies import SessionDep
from ..schemas import User

router = APIRouter(
    prefix="/auth",
    tags=["login"],
)


def add_or_update_user(new_user: User, session: SessionDep) -> User:
    user_db = session.get(User, new_user.wallet_address)
    if user_db is None:
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return new_user

    user_data = new_user.model_dump(exclude_unset=True)
    user_db.sqlmodel_update(user_data)
    session.add(user_db)
    session.commit()
    session.refresh(user_db)

    return user_db


@router.post(
    "/request-nonce",
)
async def get_nonce():
    """
    Generates a unique nonce for each login request.
    """
    return {"nonce": uuid4().hex}


@router.post(
    "/login",
)
async def login(
    wallet_address: Annotated[
        str,
        Query(
            description="ethereum address of the user",
        ),
    ],
    signed_message: Annotated[
        str,
        Query(
            description="message signed, it should be the nonce generated from the `/auth/request-nonce` endpoint",
        ),
    ],
    signature: Annotated[
        str,
        Query(
            description="signature retrived after calling `signature().hex()`",
        ),
    ],
    session: SessionDep,
) -> dict:
    """
    Verify the signature to authenticate the user and associate the wallet with the session.
    """
    recovered_address = Web3().eth.account.recover_message(
        encode_defunct(text=str(signed_message)),
        signature=bytes.fromhex(signature),
    )

    if is_eq_address(wallet_address, recovered_address):
        to_encode = {
            "wallet_address": wallet_address,
            "signed_message": signed_message,
            "signature": signature,
        }
        expiration = datetime.now(timezone.utc) + timedelta(
            minutes=TOKEN_DURATION_MINUTES
        )
        expiration_timestamp = expiration.replace(tzinfo=timezone.utc).timestamp()
        to_encode.update({"expires": expiration_timestamp})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm="HS256")

        new_user = User(
            wallet_address=str(wallet_address),
            token=encoded_jwt,
            expiration_timestamp=expiration_timestamp,
        )

        add_or_update_user(new_user, session)
        return {"token": encoded_jwt}
    else:
        raise HTTPException(status_code=401, detail="Unauthorized")
