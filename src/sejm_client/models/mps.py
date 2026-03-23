from __future__ import annotations

from datetime import date
from typing import Optional

from pydantic import BaseModel, Field


class Club(BaseModel):
    model_config = {"populate_by_name": True}

    id: str
    name: str
    phone: Optional[str] = None
    fax: Optional[str] = None
    email: Optional[str] = None
    members_count: Optional[int] = Field(None, alias="membersCount")


class Committee(BaseModel):
    model_config = {"populate_by_name": True}

    code: str
    name: str
    name_genitive: Optional[str] = Field(None, alias="nameGenitive")
    type: Optional[str] = None
    appointed_date: Optional[date] = Field(None, alias="appointedDate")


class MP(BaseModel):
    model_config = {"populate_by_name": True}

    id: int
    term: Optional[int] = None
    first_name: str = Field(alias="firstName")
    last_name: str = Field(alias="lastName")
    club: Optional[str] = None
    active: bool = True
    district_name: Optional[str] = Field(None, alias="districtName")
    voivodeship: Optional[str] = None
    birth_date: Optional[date] = Field(None, alias="birthDate")
    profession: Optional[str] = None
    email: Optional[str] = None
    number_of_votes: Optional[int] = Field(None, alias="numberOfVotes")
