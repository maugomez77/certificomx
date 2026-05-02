from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import Optional
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from .database import init_db, get_db, WorkerDB, CertificationDB, WorkerCertificationDB, EmployerDB, JobPostingDB, JobApplicationDB
from .models import (
    WorkerCreate, WorkerUpdate, WorkerResponse,
    CertificationCreate, CertificationResponse,
    WorkerCertCreate, WorkerCertResponse,
    EmployerCreate, EmployerResponse,
    JobPostingCreate, JobPostingResponse,
    ApplicationCreate, ApplicationUpdate, ApplicationResponse,
    DashboardResponse,
)
from . import ai


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(title="CertificoMX API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Workers ──────────────────────────────────────────────────────────────────

@app.get("/api/v1/workers", response_model=list[WorkerResponse])
async def list_workers(
    trade: Optional[str] = None,
    status: Optional[str] = None,
    city: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(WorkerDB)
    if trade:
        q = q.where(WorkerDB.trade == trade)
    if status:
        q = q.where(WorkerDB.status == status)
    if city:
        q = q.where(WorkerDB.city.ilike(f"%{city}%"))
    result = await db.execute(q)
    return result.scalars().all()


@app.post("/api/v1/workers", response_model=WorkerResponse)
async def create_worker(body: WorkerCreate, db: AsyncSession = Depends(get_db)):
    worker = WorkerDB(**body.model_dump())
    db.add(worker)
    await db.commit()
    await db.refresh(worker)
    return worker


@app.get("/api/v1/workers/{worker_id}", response_model=WorkerResponse)
async def get_worker(worker_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkerDB).where(WorkerDB.id == worker_id))
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(404, "Worker not found")
    return worker


@app.put("/api/v1/workers/{worker_id}", response_model=WorkerResponse)
async def update_worker(worker_id: int, body: WorkerUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkerDB).where(WorkerDB.id == worker_id))
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(404, "Worker not found")
    for k, v in body.model_dump(exclude_none=True).items():
        setattr(worker, k, v)
    await db.commit()
    await db.refresh(worker)
    return worker


@app.get("/api/v1/workers/{worker_id}/certifications", response_model=list[WorkerCertResponse])
async def worker_certifications(worker_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WorkerCertificationDB).where(WorkerCertificationDB.worker_id == worker_id)
    )
    return result.scalars().all()


@app.post("/api/v1/workers/{worker_id}/english-assess")
async def english_assess(worker_id: int, question_answers: list[dict], db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkerDB).where(WorkerDB.id == worker_id))
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(404, "Worker not found")
    assessment = ai.assess_english(question_answers)
    worker.english_level = assessment.get("level", "none")
    worker.english_score = assessment.get("total_score")
    await db.commit()
    return assessment


@app.get("/api/v1/workers/{worker_id}/recommended-jobs")
async def recommended_jobs(worker_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkerDB).where(WorkerDB.id == worker_id))
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(404, "Worker not found")
    jobs_result = await db.execute(
        select(JobPostingDB).where(JobPostingDB.status == "active", JobPostingDB.trade == worker.trade)
    )
    jobs = [{"id": j.id, "title": j.title, "trade": j.trade, "employer_id": j.employer_id,
              "salary_usd_min": j.salary_usd_min, "salary_usd_max": j.salary_usd_max,
              "required_english_level": j.required_english_level, "visa_sponsored": j.visa_sponsored,
              "location_type": j.location_type}
             for j in jobs_result.scalars().all()]
    return ai.match_jobs({"trade": worker.trade, "english_level": worker.english_level,
                           "experience_years": worker.experience_years}, jobs)


# ── Certifications ────────────────────────────────────────────────────────────

@app.get("/api/v1/certifications", response_model=list[CertificationResponse])
async def list_certifications(
    trade: Optional[str] = None,
    level: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(CertificationDB).where(CertificationDB.active == True)
    if trade:
        q = q.where(CertificationDB.trade == trade)
    if level:
        q = q.where(CertificationDB.level == level)
    result = await db.execute(q)
    return result.scalars().all()


@app.get("/api/v1/certifications/{cert_id}", response_model=CertificationResponse)
async def get_certification(cert_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CertificationDB).where(CertificationDB.id == cert_id))
    cert = result.scalar_one_or_none()
    if not cert:
        raise HTTPException(404, "Certification not found")
    return cert


@app.post("/api/v1/workers/{worker_id}/certifications/{cert_id}/enroll", response_model=WorkerCertResponse)
async def enroll_certification(worker_id: int, cert_id: int, db: AsyncSession = Depends(get_db)):
    wc = WorkerCertificationDB(worker_id=worker_id, certification_id=cert_id, status="enrolled")
    db.add(wc)
    await db.commit()
    await db.refresh(wc)
    return wc


@app.put("/api/v1/workers/{worker_id}/certifications/{cert_id}/complete", response_model=WorkerCertResponse)
async def complete_certification(worker_id: int, cert_id: int, body: WorkerCertCreate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(WorkerCertificationDB).where(
            WorkerCertificationDB.worker_id == worker_id,
            WorkerCertificationDB.certification_id == cert_id,
        )
    )
    wc = result.scalar_one_or_none()
    if not wc:
        raise HTTPException(404, "Enrollment not found")
    wc.score = body.score
    wc.exam_date = body.exam_date
    wc.status = "passed" if (body.score or 0) >= 70 else "failed"
    await db.commit()
    await db.refresh(wc)
    return wc


# ── Employers ─────────────────────────────────────────────────────────────────

@app.get("/api/v1/employers", response_model=list[EmployerResponse])
async def list_employers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EmployerDB))
    return result.scalars().all()


@app.post("/api/v1/employers", response_model=EmployerResponse)
async def create_employer(body: EmployerCreate, db: AsyncSession = Depends(get_db)):
    employer = EmployerDB(**body.model_dump())
    db.add(employer)
    await db.commit()
    await db.refresh(employer)
    return employer


@app.get("/api/v1/employers/{employer_id}", response_model=EmployerResponse)
async def get_employer(employer_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(EmployerDB).where(EmployerDB.id == employer_id))
    employer = result.scalar_one_or_none()
    if not employer:
        raise HTTPException(404, "Employer not found")
    return employer


# ── Jobs ──────────────────────────────────────────────────────────────────────

@app.get("/api/v1/jobs", response_model=list[JobPostingResponse])
async def list_jobs(
    trade: Optional[str] = None,
    location_type: Optional[str] = None,
    english_level: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    q = select(JobPostingDB).where(JobPostingDB.status == "active")
    if trade:
        q = q.where(JobPostingDB.trade == trade)
    if location_type:
        q = q.where(JobPostingDB.location_type == location_type)
    result = await db.execute(q)
    return result.scalars().all()


@app.get("/api/v1/employers/{employer_id}/jobs", response_model=list[JobPostingResponse])
async def employer_jobs(employer_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JobPostingDB).where(JobPostingDB.employer_id == employer_id))
    return result.scalars().all()


@app.post("/api/v1/employers/{employer_id}/jobs", response_model=JobPostingResponse)
async def create_job(employer_id: int, body: JobPostingCreate, db: AsyncSession = Depends(get_db)):
    job = JobPostingDB(employer_id=employer_id, **body.model_dump())
    db.add(job)
    await db.commit()
    await db.refresh(job)
    return job


@app.get("/api/v1/jobs/{job_id}", response_model=JobPostingResponse)
async def get_job(job_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JobPostingDB).where(JobPostingDB.id == job_id))
    job = result.scalar_one_or_none()
    if not job:
        raise HTTPException(404, "Job not found")
    return job


@app.post("/api/v1/jobs/{job_id}/apply", response_model=ApplicationResponse)
async def apply_job(job_id: int, body: ApplicationCreate, db: AsyncSession = Depends(get_db)):
    app_obj = JobApplicationDB(worker_id=body.worker_id, job_id=job_id)
    db.add(app_obj)
    await db.commit()
    await db.refresh(app_obj)
    return app_obj


@app.get("/api/v1/jobs/{job_id}/applications", response_model=list[ApplicationResponse])
async def job_applications(job_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JobApplicationDB).where(JobApplicationDB.job_id == job_id))
    return result.scalars().all()


@app.put("/api/v1/applications/{app_id}/status", response_model=ApplicationResponse)
async def update_application(app_id: int, body: ApplicationUpdate, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(JobApplicationDB).where(JobApplicationDB.id == app_id))
    app_obj = result.scalar_one_or_none()
    if not app_obj:
        raise HTTPException(404, "Application not found")
    app_obj.status = body.status
    if body.notes:
        app_obj.notes = body.notes
    if body.placement_fee_mxn:
        app_obj.placement_fee_mxn = body.placement_fee_mxn
    app_obj.updated_at = datetime.utcnow()
    await db.commit()
    await db.refresh(app_obj)
    return app_obj


# ── AI ────────────────────────────────────────────────────────────────────────

@app.post("/api/v1/ai/career-path")
async def career_path(worker_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkerDB).where(WorkerDB.id == worker_id))
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(404, "Worker not found")
    worker_dict = {c.name: getattr(worker, c.name) for c in WorkerDB.__table__.columns}
    return ai.suggest_career_path(worker_dict)


@app.post("/api/v1/ai/job-match")
async def job_match(worker_id: int, db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(WorkerDB).where(WorkerDB.id == worker_id))
    worker = result.scalar_one_or_none()
    if not worker:
        raise HTTPException(404, "Worker not found")
    jobs_result = await db.execute(select(JobPostingDB).where(JobPostingDB.status == "active"))
    jobs = [{"id": j.id, "title": j.title, "trade": j.trade, "employer_id": j.employer_id,
              "salary_usd_min": j.salary_usd_min, "salary_usd_max": j.salary_usd_max,
              "required_english_level": j.required_english_level, "visa_sponsored": j.visa_sponsored,
              "location_type": j.location_type}
             for j in jobs_result.scalars().all()]
    return ai.match_jobs({"trade": worker.trade, "english_level": worker.english_level,
                           "experience_years": worker.experience_years}, jobs)


@app.post("/api/v1/ai/english-assess")
async def english_assess_anon(question_answers: list[dict]):
    return ai.assess_english(question_answers)


@app.get("/api/v1/ai/market-intel")
async def market_intel():
    return ai.get_market_intel()


# ── Dashboard ─────────────────────────────────────────────────────────────────

@app.get("/api/v1/dashboard", response_model=DashboardResponse)
async def dashboard(db: AsyncSession = Depends(get_db)):
    total_workers = (await db.execute(select(func.count(WorkerDB.id)))).scalar() or 0
    active_workers = (await db.execute(
        select(func.count(WorkerDB.id)).where(WorkerDB.status == "seeking")
    )).scalar() or 0
    placed_this_month = (await db.execute(
        select(func.count(WorkerDB.id)).where(WorkerDB.status == "placed")
    )).scalar() or 0
    active_jobs = (await db.execute(
        select(func.count(JobPostingDB.id)).where(JobPostingDB.status == "active")
    )).scalar() or 0
    total_employers = (await db.execute(select(func.count(EmployerDB.id)))).scalar() or 0
    total_applications = (await db.execute(select(func.count(JobApplicationDB.id)))).scalar() or 0

    placement_rate = round((placed_this_month / total_workers * 100) if total_workers > 0 else 0, 1)

    trades = ["welding", "electrical", "automotive", "plumbing", "electronics", "logistics", "manufacturing"]
    top_trades = []
    for trade in trades:
        count = (await db.execute(
            select(func.count(WorkerDB.id)).where(WorkerDB.trade == trade)
        )).scalar() or 0
        if count > 0:
            top_trades.append({"trade": trade, "count": count})
    top_trades.sort(key=lambda x: x["count"], reverse=True)

    return DashboardResponse(
        total_workers=total_workers,
        active_workers=active_workers,
        placed_this_month=placed_this_month,
        active_jobs=active_jobs,
        total_employers=total_employers,
        total_applications=total_applications,
        top_trades=top_trades[:5],
        placement_rate=placement_rate,
    )
