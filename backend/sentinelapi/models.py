from typing import Any, Literal
from pydantic import BaseModel, Field, HttpUrl, field_validator


Mode = Literal["easy", "moderate", "brutal"]


class DiscoverRequest(BaseModel):
    target_url: HttpUrl
    openapi_url: HttpUrl | None = None


class Identity(BaseModel):
    username: str = Field(min_length=1, max_length=128)
    password: str = Field(min_length=1, max_length=512)


class ScanRequest(BaseModel):
    session_id: str = Field(min_length=16, max_length=64)
    mode: Mode = "moderate"
    login_path: str = "/auth/login"
    identity_a: Identity
    identity_b: Identity

    @field_validator("login_path")
    @classmethod
    def relative_login_path(cls, value: str) -> str:
        if not value.startswith("/") or value.startswith("//"):
            raise ValueError("login_path must be an absolute path on the target")
        return value


class Finding(BaseModel):
    finding_id: str
    type: str
    status: Literal["confirmed", "probable", "inconclusive", "not_vulnerable"]
    severity: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFO"]
    confidence: Literal["HIGH", "MEDIUM", "LOW"]
    endpoint: str
    method: str
    resource_identifier: str | None = None
    evidence: dict[str, Any]
    description: str


class Poc(BaseModel):
    finding_id: str
    method: str
    url: str
    headers: dict[str, str]
    authentication_context: str


class ScanResult(BaseModel):
    scan_id: str
    status: Literal["completed", "failed"]
    target: dict[str, Any]
    mode: Mode
    summary: dict[str, int]
    score: dict[str, Any]
    findings: list[Finding]
    pocs: list[Poc]
    statistics: dict[str, Any]
    safety: dict[str, Any]


class AIReport(BaseModel):
    executive_summary: str = ""
    findings: list[dict[str, Any]] = Field(default_factory=list)
    remediation: list[str] = Field(default_factory=list)
    limitations: list[str] = Field(default_factory=list)
