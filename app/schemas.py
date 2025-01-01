from sqlmodel import Field, SQLModel
from enum import Enum
from uuid import uuid4


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
    proposal_id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    title: str
    description: str
    proposer: str
    created_timestamp: float
    start_timestamp: float
    end_timestamp: float
    status: ProposalStatus


class Vote(SQLModel, table=True):
    vote_id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    proposal_id: str
    voter_address: str
    voted_timestamp: int
    option: Option


# @TODO: Inherite from Proposal
class TokenWeightProposal(SQLModel, table=True):
    proposal_id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    title: str
    description: str
    proposer: str
    created_timestamp: float
    start_timestamp: float
    end_timestamp: float
    status: ProposalStatus

    token_address: str


class TokenWeightVote(SQLModel, table=True):
    vote_id: str = Field(default_factory=lambda: uuid4().hex, primary_key=True)
    proposal_id: str
    voter_address: str
    voted_timestamp: int
    option: Option

    weight: float
