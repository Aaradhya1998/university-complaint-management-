from __future__ import annotations
import random
import sqlite3
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from flask import Flask, current_app, g

DATABASE_NAME = "database.db"


@dataclass
class Complaint:
    id: int
    email: str
    prn_or_faculty_id: str
    category: str
    description: str
    image_path: str | None
    status: str
    created_at: str


def _database_path() -> Path:
    return Path(current_app.root_path) / DATABASE_NAME


def get_db() -> sqlite3.Connection:
    if "db" not in g:
        g.db = sqlite3.connect(str(_database_path()))
        g.db.row_factory = sqlite3.Row
    return g.db


def close_db(e=None):
    db = g.pop("db", None)
    if db is not None:
        db.close()


def init_db():
    db = get_db()
    print("DB PATH:", _database_path())
    db.execute("""
        CREATE TABLE IF NOT EXISTS complaints (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_id TEXT UNIQUE,
            email TEXT NOT NULL,
            prn_or_faculty_id TEXT NOT NULL,
            category TEXT NOT NULL,
            description TEXT NOT NULL,
            image_path TEXT,
            status TEXT NOT NULL DEFAULT 'Not Resolved',
            created_at TEXT NOT NULL
        )
    """)
    db.commit()


def init_app(app: Flask):
    app.teardown_appcontext(close_db)
    with app.app_context():
        init_db()


def _row_to_complaint(row):
    return Complaint(
        id=row["id"],
        email=row["email"],
        prn_or_faculty_id=row["prn_or_faculty_id"],
        category=row["category"],
        description=row["description"],
        image_path=row["image_path"],
        status=row["status"],
        created_at=row["created_at"],
    )


def generate_ticket_id():
    return str(random.randint(1000, 9999))


def insert_complaint(email, prn_or_faculty_id, category, description, image_path):
    db = get_db()

    ticket_id = generate_ticket_id()

    # ensure unique
    while db.execute(
        "SELECT 1 FROM complaints WHERE ticket_id = ?", (ticket_id,)
    ).fetchone():
        ticket_id = generate_ticket_id()

    created_at = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")

    db.execute("""
        INSERT INTO complaints (
            ticket_id, email, prn_or_faculty_id, category,
            description, image_path, status, created_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticket_id, email, prn_or_faculty_id,
        category, description, image_path,
        "Not Resolved", created_at
    ))

    db.commit()

    return ticket_id

def get_complaint_by_id(complaint_id):
    db = get_db()
    row = db.execute(
        """
        SELECT id, email, prn_or_faculty_id, category,
               description, image_path, status, created_at
        FROM complaints
        WHERE id = ?
        """,
        (complaint_id,),
    ).fetchone()

    if not row:
        return None

    return _row_to_complaint(row)

def get_complaint_by_ticket(ticket_id):
    db = get_db()
    row = db.execute(
        """
        SELECT id, email, prn_or_faculty_id, category,
               description, image_path, status, created_at
        FROM complaints
        WHERE ticket_id = ?
        """,
        (ticket_id,),
    ).fetchone()

    if not row:
        return None

    return _row_to_complaint(row)


def get_complaints(category=None, status=None):
    db = get_db()

    query = """
        SELECT id, email, prn_or_faculty_id, category,
               description, image_path, status, created_at
        FROM complaints
    """

    params = []

    if category:
        query += " WHERE category = ?"
        params.append(category)

    rows = db.execute(query, params).fetchall()
    return [_row_to_complaint(r) for r in rows]


def get_categories():
    db = get_db()
    rows = db.execute("SELECT DISTINCT category FROM complaints").fetchall()
    return [row["category"] for row in rows]


def get_category_counts():
    db = get_db()
    rows = db.execute("""
        SELECT category, COUNT(*) as count
        FROM complaints
        GROUP BY category
    """).fetchall()

    return [(row["category"], row["count"]) for row in rows]


def get_status_counts():
    db = get_db()
    row = db.execute("""
        SELECT
            SUM(CASE WHEN status='Resolved' THEN 1 ELSE 0 END),
            SUM(CASE WHEN status='Not Resolved' THEN 1 ELSE 0 END)
        FROM complaints
    """).fetchone()

    return row[0] or 0, row[1] or 0


def mark_complaint_resolved(complaint_id):
    db = get_db()
    db.execute(
        "UPDATE complaints SET status='Resolved' WHERE id=?",
        (complaint_id,)
    )
    db.commit()
    return True