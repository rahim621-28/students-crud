from datetime import date
from typing import Optional
from sqlalchemy import select
from sqlalchemy.orm import Session
from . import models, schemas


def create_student(db: Session, data: schemas.StudentCreate) -> models.Student:
    student = models.Student(**data.model_dump())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student


def get_student(db: Session, student_id: int) -> Optional[models.Student]:
    return db.get(models.Student, student_id)


def get_by_email(db: Session, email: str) -> Optional[models.Student]:
    return db.scalar(select(models.Student).where(models.Student.email == email))


def list_students(
    db: Session,
    name: Optional[str] = None,
    course: Optional[str] = None,
    born_after: Optional[date] = None,
    born_before: Optional[date] = None,
    skip: int = 0,
    limit: int = 100,
):
    q = select(models.Student)
    if name:
        q = q.where(models.Student.name.ilike(f"%{name}%"))
    if course:
        q = q.where(models.Student.course.ilike(f"%{course}%"))
    if born_after:
        q = q.where(models.Student.date_of_birth > born_after)
    if born_before:
        q = q.where(models.Student.date_of_birth < born_before)
    return list(db.scalars(q.order_by(models.Student.id).offset(skip).limit(limit)))


def update_student(db: Session, student: models.Student, data: schemas.StudentUpdate):
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(student, key, value)
    db.commit()
    db.refresh(student)
    return student


def delete_student(db: Session, student: models.Student) -> None:
    db.delete(student)
    db.commit()
