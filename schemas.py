from pydantic import BaseModel
from typing import Optional, Union


class AnalyzeRequest(BaseModel):
    domain: str


class AnalyzeResponse(BaseModel):
    success: bool
    domain: Optional[str] = None
    trust_score: Optional[int] = None
    data_retention: Optional[str] = None
    trains_on_input: Optional[Union[bool, str]] = None
    soc2_certified: Optional[Union[bool, str]] = None
    hipaa_compliant: Optional[Union[bool, str]] = None
    gdpr_compliant: Optional[Union[bool, str]] = None
    iso_27001: Optional[Union[bool, str]] = None
    breach_mentions: Optional[Union[bool, str]] = None
    processing_time_ms: Optional[int] = None
    error: Optional[str] = None