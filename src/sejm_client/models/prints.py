from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field


class Print(BaseModel):
    model_config = {"populate_by_name": True}

    num: str = Field(alias="number")
    term: int
    title: str
    document_date: Optional[date] = Field(None, alias="documentDate")
    delivery_date: Optional[date] = Field(None, alias="deliveryDate")
    change_date: Optional[datetime] = Field(None, alias="changeDate")
    attachments: list[str] = Field(default_factory=list)
    process_print: list[str] = Field(default_factory=list, alias="processPrint")
