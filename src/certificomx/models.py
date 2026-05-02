from enum import Enum
from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, ConfigDict


class Trade(str, Enum):
    welding = "welding"
    electrical = "electrical"
    automotive = "automotive"
    plumbing = "plumbing"
    electronics = "electronics"
    logistics = "logistics"
    manufacturing = "manufacturing"


class EducationLevel(str, Enum):
    primaria = "primaria"
    secundaria = "secundaria"
    preparatoria = "preparatoria"
    tecnico = "tecnico"
    universidad = "universidad"


class EnglishLevel(str, Enum):
    none = "none"
    basic = "basic"
    intermediate = "intermediate"
    advanced = "advanced"


class WorkerStatus(str, Enum):
    seeking = "seeking"
    certified = "certified"
    placed = "placed"
    inactive = "inactive"


class CertLevel(str, Enum):
    basic = "basic"
    intermediate = "intermediate"
    advanced = "advanced"


class CertAuthority(str, Enum):
    CONALEP = "CONALEP"
    CONOCER = "CONOCER"
    STPS = "STPS"
    NOM = "NOM"
    IMSS = "IMSS"


class CertStatus(str, Enum):
    enrolled = "enrolled"
    in_progress = "in_progress"
    passed = "passed"
    failed = "failed"
    expired = "expired"


class LocationType(str, Enum):
    onsite_us = "onsite_us"
    onsite_mx = "onsite_mx"
    hybrid = "hybrid"


class JobStatus(str, Enum):
    active = "active"
    filled = "filled"
    expired = "expired"


class ApplicationStatus(str, Enum):
    applied = "applied"
    screening = "screening"
    interview = "interview"
    offer = "offer"
    hired = "hired"
    rejected = "rejected"


# Workers
class WorkerCreate(BaseModel):
    name: str
    phone: str
    email: str = ""
    whatsapp_number: str = ""
    state: str = ""
    city: str = ""
    trade: Trade
    experience_years: int = 0
    education_level: EducationLevel = EducationLevel.secundaria
    english_level: EnglishLevel = EnglishLevel.none


class WorkerUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    state: Optional[str] = None
    city: Optional[str] = None
    experience_years: Optional[int] = None
    education_level: Optional[EducationLevel] = None
    english_level: Optional[EnglishLevel] = None
    english_score: Optional[float] = None
    status: Optional[WorkerStatus] = None


class WorkerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    phone: str
    email: str
    state: str
    city: str
    trade: str
    experience_years: int
    education_level: str
    english_level: str
    english_score: Optional[float]
    status: str
    created_at: datetime


# Certifications
class CertificationCreate(BaseModel):
    name: str
    code: str
    trade: Trade
    authority: CertAuthority
    level: CertLevel = CertLevel.basic
    duration_hours: int = 40
    cost_mxn: float = 300.0
    passing_score: int = 70
    us_equivalent: str = ""
    description_es: str = ""
    description_en: str = ""


class CertificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    code: str
    trade: str
    authority: str
    level: str
    duration_hours: int
    cost_mxn: float
    passing_score: int
    us_equivalent: str
    description_es: str
    description_en: str
    active: bool


class WorkerCertCreate(BaseModel):
    score: Optional[float] = None
    exam_date: Optional[date] = None


class WorkerCertResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    worker_id: int
    certification_id: int
    status: str
    score: Optional[float]
    attempt_number: int
    exam_date: Optional[date]
    expiry_date: Optional[date]
    created_at: datetime


# Employers
class EmployerCreate(BaseModel):
    company_name: str
    country: str = "us"
    state_province: str = ""
    city: str = ""
    industry: str
    contact_name: str = ""
    contact_email: str = ""
    contact_phone: str = ""
    nearshoring_partner: bool = True


class EmployerResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    company_name: str
    country: str
    state_province: str
    city: str
    industry: str
    contact_name: str
    contact_email: str
    nearshoring_partner: bool
    verified: bool
    created_at: datetime


# Jobs
class JobPostingCreate(BaseModel):
    title: str
    trade: Trade
    description_es: str = ""
    description_en: str = ""
    salary_usd_min: float = 0
    salary_usd_max: float = 0
    location_type: LocationType = LocationType.onsite_us
    required_english_level: EnglishLevel = EnglishLevel.basic
    visa_sponsored: bool = False
    positions_available: int = 1


class JobPostingResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    employer_id: int
    title: str
    trade: str
    description_es: str
    description_en: str
    salary_usd_min: float
    salary_usd_max: float
    location_type: str
    required_english_level: str
    visa_sponsored: bool
    positions_available: int
    status: str
    posted_at: datetime


# Applications
class ApplicationCreate(BaseModel):
    worker_id: int


class ApplicationUpdate(BaseModel):
    status: ApplicationStatus
    notes: Optional[str] = None
    placement_fee_mxn: Optional[float] = None


class ApplicationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    worker_id: int
    job_id: int
    status: str
    placement_fee_mxn: Optional[float]
    notes: str
    applied_at: datetime
    updated_at: datetime


# Dashboard
class DashboardResponse(BaseModel):
    total_workers: int
    active_workers: int
    placed_this_month: int
    active_jobs: int
    total_employers: int
    total_applications: int
    top_trades: list[dict]
    placement_rate: float
