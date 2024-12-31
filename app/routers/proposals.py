from datetime import datetime
from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import select

from ..auth import JWTBearer

from ..dependencies import SessionDep
from ..schemas import Proposal, ProposalStatus

router = APIRouter(
    prefix="/proposals",
    tags=["proposals"],
)


@router.get(
    "/{proposal_id}",
)
async def get_proposal(
    proposal_id: str,
    session: SessionDep,
) -> Proposal | None:
    """
    get proposal by proposal id
    """
    proposal = session.get(Proposal, proposal_id)
    return proposal


@router.get("/")
async def get_proposals(session: SessionDep) -> Sequence[Proposal] | None:
    """
    list all proposals
    """
    proposals = session.exec(select(Proposal)).all()
    return proposals


@router.post(
    "/",
    dependencies=[Depends(JWTBearer())],
)
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
