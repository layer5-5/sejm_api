from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from .common import VotingResult


class Vote(BaseModel):
    model_config = {"populate_by_name": True}

    mp_id: int = Field(alias="MP")
    vote: VotingResult


class Voting(BaseModel):
    model_config = {"populate_by_name": True}

    term: int
    sitting: int
    voting_number: int = Field(alias="votingNumber")
    date: datetime
    title: str
    topic: Optional[str] = None
    description: Optional[str] = None
    yes: int
    no: int
    abstain: int
    not_participating: int = Field(alias="notParticipating")
    total_voted: int = Field(alias="totalVoted")
    majority_type: Optional[str] = Field(None, alias="majorityType")
    majority_votes: Optional[int] = Field(None, alias="majorityVotes")
    kind: str
    votes: Optional[list[Vote]] = None
