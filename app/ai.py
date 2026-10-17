"""Optional bonus: ask questions about students using a local Ollama model.

Safety: the model NEVER writes or runs SQL. The backend fetches records with
fixed, parameterised queries and passes them to the model as context only.
"""
import os
import re
from datetime import date
import httpx
from sqlalchemy import func, select
from sqlalchemy.orm import Session
from . import models, crud

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3.2:1b")


def build_context(db: Session, question: str) -> str:
    """Pick relevant records using simple, safe rules (no model-generated SQL)."""
    q = question.lower()
    total = db.scalar(select(func.count()).select_from(models.Student))
    lines = [f"Total students: {total}"]

    born_after = re.search(r"born (?:after|since) (\d{4})", q)
    born_before = re.search(r"born before (\d{4})", q)
    kwargs = {}
    if born_after:
        kwargs["born_after"] = date(int(born_after.group(1)), 12, 31)
    if born_before:
        kwargs["born_before"] = date(int(born_before.group(1)), 1, 1)

    students = crud.list_students(db, limit=50, **kwargs)
    for s in students:
        lines.append(
            f"ID {s.id}: {s.name}, DOB {s.date_of_birth}, course {s.course or 'N/A'}"
        )
    return "\n".join(lines)


def ask(db: Session, question: str) -> str:
    context = build_context(db, question)
    prompt = (
        "You answer questions about a student database. Use ONLY the records below. "
        "If the answer is not in the records, say you don't know.\n\n"
        f"RECORDS:\n{context}\n\nQUESTION: {question}\nANSWER:"
    )
    resp = httpx.post(
        f"{OLLAMA_URL}/api/generate",
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["response"].strip()
