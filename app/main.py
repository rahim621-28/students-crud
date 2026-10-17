from datetime import date
from typing import List, Optional
import httpx
from fastapi import Depends, FastAPI, HTTPException, Query, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from . import ai, crud, models, schemas
from .database import Base, engine, get_db

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Students Database API", version="1.0.0")


def get_or_404(db: Session, student_id: int) -> models.Student:
    student = crud.get_student(db, student_id)
    if not student:
        raise HTTPException(status_code=404, detail=f"Student {student_id} not found")
    return student


@app.post("/students", response_model=schemas.StudentOut, status_code=status.HTTP_201_CREATED)
def create_student(data: schemas.StudentCreate, db: Session = Depends(get_db)):
    if data.email and crud.get_by_email(db, data.email):
        raise HTTPException(status_code=409, detail="A student with this email already exists")
    return crud.create_student(db, data)


@app.get("/students", response_model=List[schemas.StudentOut])
def list_students(
    name: Optional[str] = None,
    course: Optional[str] = None,
    born_after: Optional[date] = None,
    born_before: Optional[date] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return crud.list_students(db, name, course, born_after, born_before, skip, limit)


@app.get("/students/{student_id}", response_model=schemas.StudentOut)
def get_student(student_id: int, db: Session = Depends(get_db)):
    return get_or_404(db, student_id)


@app.put("/students/{student_id}", response_model=schemas.StudentOut)
@app.patch("/students/{student_id}", response_model=schemas.StudentOut)
def update_student(student_id: int, data: schemas.StudentUpdate, db: Session = Depends(get_db)):
    student = get_or_404(db, student_id)
    if data.email and data.email != student.email and crud.get_by_email(db, data.email):
        raise HTTPException(status_code=409, detail="A student with this email already exists")
    return crud.update_student(db, student, data)


@app.delete("/students/{student_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_student(student_id: int, db: Session = Depends(get_db)):
    crud.delete_student(db, get_or_404(db, student_id))


# ---------- Optional bonus: local AI with Ollama ----------
class Question(BaseModel):
    question: str


@app.post("/ask")
def ask_ai(body: Question, db: Session = Depends(get_db)):
    try:
        return {"question": body.question, "answer": ai.ask(db, body.question)}
    except httpx.HTTPError as e:
         raise HTTPException(
            status_code=503,
            detail=f"Ollama request failed ({type(e).__name__}): {e}. Check OLLAMA_MODEL and that Ollama is running.",
        )
