"""Load dummy data (no real personal info)."""
from datetime import date
from app.database import Base, SessionLocal, engine
from app import crud, models, schemas

Base.metadata.create_all(bind=engine)

DUMMY = [
    ("Aarav Kumar", date(2004, 3, 14), "aarav@example.com", None, "Computer Science"),
    ("Diya Sharma", date(2005, 7, 21), "diya@example.com", "9876543210", "Data Science"),
    ("Karthik Raja", date(2003, 11, 2), None, "9123456780", "Electronics"),
    ("Meera Nair", date(2006, 1, 9), "meera@example.com", None, "Computer Science"),
    ("Rohan Iyer", date(2005, 5, 30), "rohan@example.com", "9988776655", "Mechanical"),
]

with SessionLocal() as db:
    if db.query(models.Student).count() == 0:
        for name, dob, email, phone, course in DUMMY:
            crud.create_student(db, schemas.StudentCreate(
                name=name, date_of_birth=dob, email=email, phone=phone,
                course=course, enrollment_date=date(2025, 8, 1)))
        print("Seeded", len(DUMMY), "students")
    else:
        print("DB already has data, skipping")
