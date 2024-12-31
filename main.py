import uuid
from datetime import datetime, timedelta, timezone
from enum import Enum, IntEnum
from os import walk
from re import I
from typing import Annotated, Sequence

import jwt
from eth_account.messages import encode_defunct
from fastapi import Depends, FastAPI, HTTPException, Query
from pydantic import BaseModel, ValidationError, validator
from sqlmodel import Field, Session, SQLModel, create_engine, select
from web3 import Web3

from config import SECRET_KEY, TOKEN_DURATION_MINUTES
from utils import is_eq_address


class Option(str, Enum):
    YES = "yes"
    NO = "no"


class ProposalStatus(str, Enum):
    ACTIVE = "active"
    CLOSED = "closed"


class User(SQLModel, table=True):
    wallet_address: str = Field(primary_key=True)
    token: str | None
    expiration_timestamp: float | None


class Proposal(SQLModel, table=True):
    proposal_id: str = Field(default_factory=lambda: uuid.uuid4().hex, primary_key=True)
    title: str
    description: str
    proposer: str
    created_timestamp: float
    start_timestamp: float
    end_timestamp: float
    status: ProposalStatus


class Vote(SQLModel, table=True):
    vote_id: str = Field(primary_key=True)
    proposal_id: str
    voter_address: str = Field(
        title="The Snap",
        description="this is the value of snap",
    )
    voted_timestamp: int
    option: Option


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)


def get_session():
    with Session(engine) as session:
        yield session


SessionDep = Annotated[Session, Depends(get_session)]


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def add_or_update_user(new_user: User, session: SessionDep) -> User:
    user_db = session.get(User, new_user.wallet_address)
    print(user_db)
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


app = FastAPI()


@app.on_event("startup")
def on_startup():
    create_db_and_tables()


@app.post(
    "/auth/request-nonce",
    tags=["login"],
)
async def get_nonce():
    """
    Generates a unique nonce for each login request.
    """
    return {"nonce": uuid.uuid4().hex}


@app.post("/auth/login", tags=["login"])
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
            description="message signed, it should be the nonce generated from the `get_nonce` endpoint",
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
        to_encode.update({"expiration": expiration_timestamp})
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


@app.post("/proposals", tags=["proposals"])
async def create_proposals(
    session: SessionDep,
    title: Annotated[
        str,
        Query(
            description="title of the proposal",
        ),
    ],
    description: Annotated[
        str,
        Query(
            description="description of the proposal",
        ),
    ],
    proposer: Annotated[
        str,
        Query(
            description="address of the proposer",
        ),
    ],
    start_timestamp: Annotated[
        float | None,
        Query(
            description="start timestamp of the proposal. default: `created_timestamp`",
        ),
    ] = None,
    duration: Annotated[
        float,
        Query(
            description="duration of the proposal. default: 86400.0 (1day)",
        ),
    ] = 86400.0,
) -> Proposal:
    # @TODO: Check auth with JWT
    proposal = {
        "title": title,
        "description": description,
        "proposer": proposer,
        "created_timestamp": datetime.now().timestamp(),
        "start_timestamp": None,
    }

    # handle create/start/end timestamp
    if start_timestamp:
        # start timestamp couldnt be earlier then create timestamp
        # @TODO: Handle it with pydantic validator
        if proposal["created_timestamp"] > start_timestamp:
            raise HTTPException(
                status_code=422,
                detail=f"Invalid `start_timestamp`. created: {proposal['created_timestamp']}, start: {start_timestamp}",
            )
        proposal["start_timestamp"] = start_timestamp
    else:
        proposal["start_timestamp"] = proposal["created_timestamp"]

    if datetime.now().timestamp() > proposal["start_timestamp"]:
        proposal["status"] = ProposalStatus.ACTIVE
    else:
        proposal["status"] = ProposalStatus.CLOSED

    proposal["end_timestamp"] = proposal["start_timestamp"] + duration

    proposal_obj = Proposal(**proposal)
    session.add(proposal_obj)
    session.commit()
    session.refresh(proposal_obj)

    return proposal_obj


@app.get("/proposals", tags=["proposals"])
async def get_proposals(session: SessionDep) -> Sequence[Proposal] | None:
    """
    list all proposals
    """
    proposals = session.exec(select(Proposal)).all()
    return proposals


@app.post("/proposals/{id}/vote")
async def cast_vote(session: SessionDep) -> Vote | None:
    pass


@app.get("/proposals/{id}/results")
async def get_votes(session: SessionDep) -> list[Vote] | None:
    pass