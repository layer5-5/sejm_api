from __future__ import annotations

from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, Field

from .common import ApplicantType, BillStatus, BillType, UrgencyStatus


class Bill(BaseModel):
    model_config = {"populate_by_name": True}

    num: str = Field(alias="number")
    term: int
    title: str
    description: Optional[str] = None
    submission_date: Optional[date] = Field(None, alias="dateOfReceipt")
    last_modified: Optional[datetime] = Field(None, alias="changeDate")
    status: BillStatus
    bill_type: BillType = Field(alias="submissionType")
    applicant_type: ApplicantType = Field(alias="applicantType")
    urgency_status: Optional[UrgencyStatus] = Field(None, alias="urgencyStatus")
    passed: bool = False
    eu_related: bool = Field(False, alias="euRelated")
    public_consultation: bool = Field(False, alias="publicConsultation")
    consultation_results: bool = Field(False, alias="consultationResults")
    shorten_procedure: bool = Field(False, alias="shortenProcedure")
    rcl_num: Optional[str] = Field(None, alias="rclNum")
    rcl_link: Optional[str] = Field(None, alias="rclLink")
    eli: Optional[str] = Field(None, alias="ELI")
    print_num: Optional[str] = Field(None, alias="print")
    links: list[str] = Field(default_factory=list)
