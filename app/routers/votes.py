import random
from collections import defaultdict
from fastapi import APIRouter, Request
from datetime import datetime
from typing import Annotated

from fastapi import Depends, HTTPException, Query
from sqlmodel import select

from .proposals import update_expired_proposals
from ..auth import JWTBearer, get_wallet_from_rq
from ..dependencies import SessionDep
from ..schemas import (
    Proposal,
    TokenWeightProposal,
    TokenWeightVote,
    Vote,
    Option,
    ProposalStatus,
)

router = APIRouter(
    tags=["votes"],
)


# Fake function
# def get_balance(token_address: str, wallet_address: str):
def fake_get_balance():
    # Eth balance if wallet_address is zero address
    # if token_address == constants.ZERO_ADDRESS:
    #     return get_native_balance(wallet_address)

    # ERC20 balance
    # erc20 = get_erc20_instance(token_address)
    # balance_wei = erc20.balance_of(wallet_address)
    # if balance_wei == 0:
    #     return 0.0
    # else:
    #     return balance_wei / 10 ** (erc20.decimals)

    return random.uniform(100, 30_000)


@router.post(
    "/proposals/{proposal_id}/vote",
    dependencies=[Depends(JWTBearer())],
)
async def cast_vote(
    proposal_id: str,
    option: Annotated[
        Option,
        Query(
            description="option of the vote",
        ),
    ],
    session: SessionDep,
    request: Request,
) -> Vote | None:
    """
    vote a proposal by a proposal id
    """
    update_expired_proposals(session)

    proposal = session.get(Proposal, proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=422,
            detail=f"proposal: {proposal_id} not found.",
        )

    if proposal.status == ProposalStatus.CLOSED:
        raise HTTPException(
            status_code=422, detail=f"proposal: {proposal_id} is closed"
        )
    voter_address = get_wallet_from_rq(request)
    if voter_address is None:
        raise HTTPException(status_code=422, detail="voter address not found.")

    # check valid vote
    prev_vote = session.exec(
        select(Vote)
        .filter(Vote.voter_address == voter_address)
        .filter(Vote.proposal_id == proposal_id)
    ).all()
    if prev_vote:
        raise HTTPException(status_code=422, detail="You could only vote once.")

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


@router.get("/proposals/{proposal_id}/votes")
async def get_votes(
    proposal_id: str,
    session: SessionDep,
) -> list[Vote] | None:
    """
    get all votes of a proposal
    """
    update_expired_proposals(session)

    votes = session.exec(select(Vote).filter(Vote.proposal_id == proposal_id)).all()

    return votes


@router.get("/proposals/{proposal_id}/results")
async def get_results(
    proposal_id: str,
    session: SessionDep,
) -> dict | None:
    """
    get all votes of a proposal
    """
    update_expired_proposals(session)

    votes = session.exec(select(Vote).filter(Vote.proposal_id == proposal_id)).all()
    result = defaultdict(int)

    for vote in votes:
        result[vote.option] += 1

    winner = "invalid"
    if result[Option.YES] > result[Option.NO]:
        winner = "yes"
    elif result[Option.NO] > result[Option.YES]:
        winner = "no"
    elif result[Option.Yes] == result[Option.NO] and result[Option.YES] > 0:
        winner = "draw"

    return {
        "proposal_id": proposal_id,
        "# of votes": result[Option.YES] + result[Option.NO],
        "yes": result[Option.YES],
        "no": result[Option.NO],
        "winner": winner,
    }


"""
    Bonus: Token-Weight Proposals
"""


@router.post(
    "/proposals/token_weight/{proposal_id}/vote",
    dependencies=[Depends(JWTBearer())],
)
async def cast_vote_token_weight(
    proposal_id: str,
    option: Annotated[
        Option,
        Query(
            description="option of the vote",
        ),
    ],
    session: SessionDep,
    request: Request,
) -> TokenWeightVote | None:
    """
    vote a proposal by a proposal id
    """
    update_expired_proposals(session)

    proposal = session.get(TokenWeightProposal, proposal_id)
    if not proposal:
        raise HTTPException(
            status_code=422,
            detail=f"proposal: {proposal_id} not found.",
        )

    if proposal.status == ProposalStatus.CLOSED:
        raise HTTPException(
            status_code=422, detail=f"proposal: {proposal_id} is closed"
        )
    voter_address = get_wallet_from_rq(request)
    if voter_address is None:
        raise HTTPException(status_code=422, detail="voter address not found.")

    token_balance = fake_get_balance()
    if token_balance == 0:
        raise HTTPException(status_code=422, detail="Zero voting power")

    # check valid vote
    prev_vote = session.exec(
        select(TokenWeightVote)
        .filter(TokenWeightVote.voter_address == voter_address)
        .filter(TokenWeightVote.proposal_id == proposal_id)
    ).all()
    if prev_vote:
        raise HTTPException(status_code=422, detail="You could only vote once.")

    vote = {
        "proposal_id": proposal_id,
        "voter_address": voter_address,
        "option": option,
        "voted_timestamp": int(datetime.now().timestamp()),
        "weight": token_balance,
    }
    vote_obj = TokenWeightVote(**vote)
    session.add(vote_obj)
    session.commit()
    session.refresh(vote_obj)
    return vote_obj


@router.get("/proposals/token_weight/{proposal_id}/votes")
async def get_token_weight_votes(
    proposal_id: str,
    session: SessionDep,
) -> list[TokenWeightVote] | None:
    """
    get all votes of a token weight proposal
    """
    update_expired_proposals(session)

    votes = session.exec(
        select(TokenWeightVote).filter(TokenWeightVote.proposal_id == proposal_id)
    ).all()

    return votes


@router.get("/proposals/token_weight/{proposal_id}/results")
async def get_token_weight_results(
    proposal_id: str,
    session: SessionDep,
) -> dict | None:
    """
    get all votes of a token weight proposal
    """
    update_expired_proposals(session)

    votes = session.exec(
        select(TokenWeightVote).filter(TokenWeightVote.proposal_id == proposal_id)
    ).all()
    result = defaultdict(int)

    for vote in votes:
        result[vote.option] += vote.weight

    winner = "invalid"
    if result[Option.YES] > result[Option.NO]:
        winner = "yes"
    elif result[Option.NO] > result[Option.YES]:
        winner = "no"
    elif result[Option.Yes] == result[Option.NO] and result[Option.YES] > 0:
        winner = "draw"

    return {
        "proposal_id": proposal_id,
        "total_voting_power": result[Option.YES] + result[Option.NO],
        "yes": result[Option.YES],
        "no": result[Option.NO],
        "winner": winner,
    }
