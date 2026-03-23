from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from .common import ActStatus


class Publisher(BaseModel):
    code: str
    name: str


class Act(BaseModel):
    model_config = {"populate_by_name": True}

    eli: str = Field(alias="ELI")
    address: str
    display_address: str = Field(alias="displayAddress")
    publisher: str
    year: int
    pos: int
    title: str
    act_type: str = Field(alias="type")
    status: ActStatus
    announcement_date: Optional[date] = Field(None, alias="announcementDate")
    promulgation: Optional[date] = None
    entry_into_force: Optional[date] = Field(None, alias="entryIntoForce")
    valid_from: Optional[date] = Field(None, alias="validFrom")
    repeal_date: Optional[date] = Field(None, alias="repealDate")
    change_date: Optional[datetime] = Field(None, alias="changeDate")
    text_pdf: bool = Field(False, alias="textPDF")
    text_html: bool = Field(False, alias="textHTML")
