from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.db import get_db
from database.models import WorkshopInfo
from schemas import WorkshopInfoUpdate, WorkshopInfoResponse
from auth_utils import get_current_admin

router = APIRouter()


@router.get("/workshop", response_model=WorkshopInfoResponse)
async def get_workshop(db: Session = Depends(get_db)):
    workshop = db.query(WorkshopInfo).filter(WorkshopInfo.id == "default_workshop").first()
    if not workshop:
        # Create a default workshop info row if none exists
        workshop = WorkshopInfo(
            id="default_workshop",
            date="27th June 2026",
            time="9:30 AM",
            venue="Poonamalle, Chennai",
            registration_process="Free, via Google Form on the website or walk-in at the venue.",
            eligibility="All students, job seekers, and professionals looking to map their careers.",
            contact_number="+91 99 44 74 7090",
            whatsapp_number="+91 99 44 74 7090",
            email="admin@21stacademy.in",
            google_maps_location="https://maps.google.com/?q=Poonamalle,Chennai",
            website="https://21stacademy.in"
        )
        db.add(workshop)
        db.commit()
        db.refresh(workshop)
    return workshop


@router.put("/workshop", response_model=WorkshopInfoResponse)
async def update_workshop(
    body: WorkshopInfoUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    workshop = db.query(WorkshopInfo).filter(WorkshopInfo.id == "default_workshop").first()
    if not workshop:
        workshop = WorkshopInfo(id="default_workshop")
        db.add(workshop)
        db.commit()
        db.refresh(workshop)

    for key, value in body.model_dump().items():
        if value is not None:
            setattr(workshop, key, value)

    db.commit()
    db.refresh(workshop)
    return workshop
