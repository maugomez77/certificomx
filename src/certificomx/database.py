import os
from datetime import datetime, date
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, mapped_column, Mapped
from sqlalchemy import Integer, String, Float, Boolean, DateTime, Date, Text, ForeignKey
from dotenv import load_dotenv

load_dotenv()

_raw_url = os.getenv("DATABASE_URL", "")
DATABASE_URL = _raw_url
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://") and "+asyncpg" not in DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)
DATABASE_URL = DATABASE_URL.replace("sslmode=require", "ssl=require")

engine = create_async_engine(DATABASE_URL, echo=False) if DATABASE_URL else None
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False) if engine else None


class Base(DeclarativeBase):
    pass


class WorkerDB(Base):
    __tablename__ = "workers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    phone: Mapped[str] = mapped_column(String, nullable=False)
    email: Mapped[str] = mapped_column(String, default="")
    whatsapp_number: Mapped[str] = mapped_column(String, default="")
    state: Mapped[str] = mapped_column(String, default="")
    city: Mapped[str] = mapped_column(String, default="")
    trade: Mapped[str] = mapped_column(String, nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    education_level: Mapped[str] = mapped_column(String, default="secundaria")
    english_level: Mapped[str] = mapped_column(String, default="none")
    english_score: Mapped[float] = mapped_column(Float, nullable=True)
    status: Mapped[str] = mapped_column(String, default="seeking")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class CertificationDB(Base):
    __tablename__ = "certifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    code: Mapped[str] = mapped_column(String, nullable=False)
    trade: Mapped[str] = mapped_column(String, nullable=False)
    authority: Mapped[str] = mapped_column(String, nullable=False)
    level: Mapped[str] = mapped_column(String, default="basic")
    duration_hours: Mapped[int] = mapped_column(Integer, default=40)
    cost_mxn: Mapped[float] = mapped_column(Float, default=300.0)
    passing_score: Mapped[int] = mapped_column(Integer, default=70)
    us_equivalent: Mapped[str] = mapped_column(String, default="")
    description_es: Mapped[str] = mapped_column(Text, default="")
    description_en: Mapped[str] = mapped_column(Text, default="")
    active: Mapped[bool] = mapped_column(Boolean, default=True)


class WorkerCertificationDB(Base):
    __tablename__ = "worker_certifications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    worker_id: Mapped[int] = mapped_column(Integer, ForeignKey("workers.id"))
    certification_id: Mapped[int] = mapped_column(Integer, ForeignKey("certifications.id"))
    status: Mapped[str] = mapped_column(String, default="enrolled")
    score: Mapped[float] = mapped_column(Float, nullable=True)
    attempt_number: Mapped[int] = mapped_column(Integer, default=1)
    exam_date: Mapped[date] = mapped_column(Date, nullable=True)
    expiry_date: Mapped[date] = mapped_column(Date, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class EmployerDB(Base):
    __tablename__ = "employers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company_name: Mapped[str] = mapped_column(String, nullable=False)
    country: Mapped[str] = mapped_column(String, default="us")
    state_province: Mapped[str] = mapped_column(String, default="")
    city: Mapped[str] = mapped_column(String, default="")
    industry: Mapped[str] = mapped_column(String, nullable=False)
    contact_name: Mapped[str] = mapped_column(String, default="")
    contact_email: Mapped[str] = mapped_column(String, default="")
    contact_phone: Mapped[str] = mapped_column(String, default="")
    nearshoring_partner: Mapped[bool] = mapped_column(Boolean, default=True)
    verified: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class JobPostingDB(Base):
    __tablename__ = "job_postings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employer_id: Mapped[int] = mapped_column(Integer, ForeignKey("employers.id"))
    title: Mapped[str] = mapped_column(String, nullable=False)
    trade: Mapped[str] = mapped_column(String, nullable=False)
    description_es: Mapped[str] = mapped_column(Text, default="")
    description_en: Mapped[str] = mapped_column(Text, default="")
    salary_usd_min: Mapped[float] = mapped_column(Float, default=0)
    salary_usd_max: Mapped[float] = mapped_column(Float, default=0)
    location_type: Mapped[str] = mapped_column(String, default="onsite_us")
    required_english_level: Mapped[str] = mapped_column(String, default="basic")
    visa_sponsored: Mapped[bool] = mapped_column(Boolean, default=False)
    positions_available: Mapped[int] = mapped_column(Integer, default=1)
    status: Mapped[str] = mapped_column(String, default="active")
    posted_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    expires_at: Mapped[datetime] = mapped_column(DateTime, nullable=True)


class JobApplicationDB(Base):
    __tablename__ = "job_applications"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    worker_id: Mapped[int] = mapped_column(Integer, ForeignKey("workers.id"))
    job_id: Mapped[int] = mapped_column(Integer, ForeignKey("job_postings.id"))
    status: Mapped[str] = mapped_column(String, default="applied")
    placement_fee_mxn: Mapped[float] = mapped_column(Float, nullable=True)
    notes: Mapped[str] = mapped_column(Text, default="")
    applied_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


async def init_db():
    if engine:
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)


async def get_db():
    if not AsyncSessionLocal:
        raise RuntimeError("DATABASE_URL not configured")
    async with AsyncSessionLocal() as session:
        yield session
