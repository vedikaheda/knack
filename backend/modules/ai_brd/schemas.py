from pydantic import BaseModel


class DocumentInfo(BaseModel):
    title: str
    version: str
    date: str
    engagement_model: str | None


class Phase(BaseModel):
    name: str
    summary: str
    key_features: list[str] | None


class ExecutiveSummary(BaseModel):
    overview: str
    phases: list[Phase]


class ScopeItem(BaseModel):
    name: str
    details: list[str] | None
    phase: str | None


class Scope(BaseModel):
    in_scope: list[ScopeItem]
    out_of_scope: list[str] | None


class Platform(BaseModel):
    name: str
    type: str
    notes: str | None
    phase: str | None


class Persona(BaseModel):
    name: str
    description: str | None


class FunctionalGroup(BaseModel):
    name: str
    features: list[str]
    phase: str | None


class NfrGroup(BaseModel):
    category: str
    requirements: list[str]


class TechnicalGroup(BaseModel):
    category: str
    requirements: list[str]


class IntegrationItem(BaseModel):
    name: str
    purpose: str | None
    notes: str | None


class BRDJson(BaseModel):
    document_info: DocumentInfo
    executive_summary: ExecutiveSummary
    business_objectives: list[str]
    scope: Scope
    platforms: list[Platform]
    functional_requirements: list[FunctionalGroup]
    non_functional_requirements: list[NfrGroup]
    technical_requirements: list[TechnicalGroup]
    integrations: list[IntegrationItem] | None
    data_requirements: list[str] | None
    ui_ux_requirements: list[str] | None
    reporting_analytics: list[str] | None
    support_requirements: list[str] | None
    assumptions: list[str] | None
    dependencies: list[str] | None
    risks: list[str] | None
    constraints: list[str] | None
    change_control: list[str] | None
    compliance_security: list[str] | None
