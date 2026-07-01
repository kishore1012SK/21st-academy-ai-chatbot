from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from database.db import get_db
from database.models import Course
from schemas import CourseCreate, CourseUpdate, CourseResponse
from auth_utils import get_current_admin

router = APIRouter()


@router.get("/courses", response_model=List[CourseResponse])
async def list_courses(db: Session = Depends(get_db)):
    return db.query(Course).all()


@router.get("/courses/{course_id}", response_model=CourseResponse)
async def get_course(course_id: str, db: Session = Depends(get_db)):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    return course


@router.post("/courses", response_model=CourseResponse, status_code=status.HTTP_201_CREATED)
async def create_course(
    body: CourseCreate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    # Check if course with same name exists
    existing = db.query(Course).filter(Course.name == body.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Course with this name already exists")

    course = Course(**body.model_dump())
    db.add(course)
    db.commit()
    db.refresh(course)
    return course


@router.put("/courses/{course_id}", response_model=CourseResponse)
async def update_course(
    course_id: str,
    body: CourseUpdate,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if updated name conflicts with another course
    if body.name != course.name:
        existing = db.query(Course).filter(Course.name == body.name).first()
        if existing:
            raise HTTPException(status_code=400, detail="Course with this name already exists")

    for key, value in body.model_dump().items():
        setattr(course, key, value)

    db.commit()
    db.refresh(course)
    return course


@router.delete("/courses/{course_id}")
async def delete_course(
    course_id: str,
    db: Session = Depends(get_db),
    admin=Depends(get_current_admin)
):
    course = db.query(Course).filter(Course.id == course_id).first()
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    db.delete(course)
    db.commit()
    return {"success": True, "message": "Course deleted successfully"}
