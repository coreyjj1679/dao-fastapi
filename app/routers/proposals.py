from datetime import datetime
from typing import Annotated, Sequence

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlmodel import select

from ..auth import JWTBearer, get_wallet_from_rq
from ..dependencies import SessionDep
from ..schemas import Proposal, ProposalStatus, TokenWeightProposal

router = APIRouter(
    prefix="/proposals",
    tags=["proposals"],
)


def update_expired_proposals(session: SessionDep):
    # fetch all expired proposals
    current_timestamp = datetime.now().timestamp()
    proposals_db = session.exec(
        select(Proposal)
        .filter(Proposal.status == ProposalStatus.ACTIVE)
        .filter(current_timestamp > Proposal.end_timestamp)
    )

    for proposal in proposals_db:
        proposal.status = ProposalStatus.CLOSED

    proposals_tw_db = session.exec(
        select(TokenWeightProposal)
        .filter(TokenWeightProposal.status == ProposalStatus.ACTIVE)
        .filter(current_timestamp > TokenWeightProposal.end_timestamp)
    )

    for proposals_tw in proposals_tw_db:
        proposals_tw.status = ProposalStatus.CLOSED

    session.commit()


@router.get("/")
async def get_proposals(session: SessionDep) -> Sequence[Proposal] | None:
    """
    list all proposals
    """
    update_expired_proposals(session)

    proposals = session.exec(select(Proposal)).all()
    return proposals


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
    update_expired_proposals(session)

    proposal = session.get(Proposal, proposal_id)
    return proposal


@router.post(
    "/",
    dependencies=[Depends(JWTBearer())],
)
async def create_proposals(
    session: SessionDep,
    request: Request,
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
    wallet_address = get_wallet_from_rq(request)
    if not wallet_address:
        raise HTTPException(status_code=422, detail="voter address not found.")

    proposal = {
        "title": title,
        "description": description,
        "proposer": wallet_address,
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


"""
  Bonus: Token Weight Proposals
"""


@router.get("/token_weight/")
async def get_token_weight_proposals(
    session: SessionDep,
) -> Sequence[TokenWeightProposal] | None:
    """
    list all proposals
    """
    update_expired_proposals(session)

    proposals = session.exec(select(TokenWeightProposal)).all()
    return proposals


@router.get(
    "/token_weight/{proposal_id}",
)
async def get_token_weight_proposal(
    proposal_id: str,
    session: SessionDep,
) -> TokenWeightProposal | None:
    """
    get proposal by proposal id
    """
    update_expired_proposals(session)

    proposal = session.get(TokenWeightProposal, proposal_id)
    return proposal


@router.post(
    "/token_weight/",
    dependencies=[Depends(JWTBearer())],
)
async def create_token_weight_proposals(
    session: SessionDep,
    request: Request,
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
    token_address: Annotated[
        str,
        Query(
            description="address of the token",
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
) -> TokenWeightProposal:
    wallet_address = get_wallet_from_rq(request)
    if not wallet_address:
        raise HTTPException(status_code=422, detail="voter address not found.")

    proposal = {
        "title": title,
        "description": description,
        "proposer": wallet_address,
        "token_address": token_address,
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

    proposal_obj = TokenWeightProposal(**proposal)
    session.add(proposal_obj)
    session.commit()
    session.refresh(proposal_obj)

    return proposal_obj
