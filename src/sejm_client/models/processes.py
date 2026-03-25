from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from .common import UrgencyStatus


class ProcessStage(BaseModel):
    model_config = {"populate_by_name": True}

    stage_name: str = Field(alias="stageName")
    date: Optional[date] = None
    child_stages: list["ProcessStage"] = Field(default_factory=list, alias="children")


class ProcessDocument(BaseModel):
    model_config = {"populate_by_name": True}

    num: str
    name: str
    document_date: Optional[date] = Field(None, alias="documentDate")
    document_type: str = Field(alias="documentType")
    links: list[dict] = Field(default_factory=list)


class Process(BaseModel):
    model_config = {"populate_by_name": True}

    num: str = Field(alias="number")
    term: int
    title: str
    description: Optional[str] = None
    document_type: str = Field(alias="documentType")
    document_date: Optional[date] = Field(None, alias="documentDate")
    process_start_date: Optional[date] = Field(None, alias="processStartDate")
    change_date: Optional[datetime] = Field(None, alias="changeDate")
    stages: list[ProcessStage] = Field(default_factory=list)
    eli: Optional[str] = Field(None, alias="ELI")
    passed: bool = False
    urgency_status: Optional[UrgencyStatus] = Field(None, alias="urgencyStatus")
    rcl_num: Optional[str] = Field(None, alias="rclNum")
    rcl_link: Optional[str] = Field(None, alias="rclLink")
    eu_status: Optional[str] = Field(None, alias="UE")
    legislative_committee: Optional[bool] = Field(None, alias="legislativeCommittee")
    other_documents: list[ProcessDocument] = Field(
        default_factory=list, alias="otherDocuments"
    )
    prints_considered_jointly: list[str] = Field(
        default_factory=list, alias="printsConsideredJointly"
    )
