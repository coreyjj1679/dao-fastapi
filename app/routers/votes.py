from fastapi import APIRouter
from datetime import datetime
from typing import Annotated

from fastapi import Depends, HTTPException, Query
from sqlmodel import select

from ..auth import JWTBearer

from ..dependencies import SessionDep
from ..schemas import Proposal, Vote, Option

router = APIRouter(
    tags=["votes"],
)


@router.post(
    "/proposals/{proposal_id}/vote",
    dependencies=[Depends(JWTBearer())],
)
async def cast_vote(
    proposal_id: str,
    voter_address: Annotated[
        str,
        Query(
            description="adress of the voter",
        ),
    ],
    option: Annotated[
        Option,
        Query(
            description="option of the vote",
        ),
    ],
    session: SessionDep,
) -> Vote | None:
    """
    vote a proposal by a proposal id
    """
    proposal = session.get(Proposal, proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=422,
            detail=f"`proposal`: {proposal_id} not found.",
        )

    vote = {
        "proposal_id": proposal_id,
        "voter_address": voter_address,
        "option": option,
        "voted_timestamp": int(datetime.now().timestamp()),
    }
    vote_obj = Vote(**vote)
    session.add(vote_obj)
    session.commit()
    session.refresh(vote_obj)
    return vote_obj


@router.get("/proposals/{proposal_id}/results")
async def get_votes(
    proposal_id: str,
    session: SessionDep,
) -> list[Vote] | None:
    """
    get all votes of a proposal
    """
    votes = session.exec(select(Vote).filter(Vote.proposal_id == proposal_id)).all()

    return votes
