"""Repeatable student/faculty accounts for the local presentation stack."""
import os

from app.core.database import SessionLocal
from app.core.security import hash_password, verify_password
from app.models.user import User


DEMO_ACCOUNTS = (
    ("demostudent@example.com", "demostudent", "Demo Student", "student"),
    ("demofaculty@example.com", "demofaculty", "Demo Faculty", "faculty"),
)


def seed_demo_accounts(db):
    for email, password, name, role in DEMO_ACCOUNTS:
        user = db.query(User).filter(User.email == email).first()
        if user is None and role == "student":
            # Keep the old demo learner's ID, progress and external note scope.
            user = db.query(User).filter(User.email == "demo@example.com").first()
        if user is None:
            user = User(email=email, full_name=name, role=role)
            db.add(user)
        user.email, user.full_name, user.role = email, name, role
        if not user.hashed_password or not verify_password(password, user.hashed_password):
            user.hashed_password = hash_password(password)
    db.commit()


def main():
    if os.environ.get("SEED_DEMO_USER", "false").lower() != "true":
        return
    with SessionLocal() as db:
        seed_demo_accounts(db)
    print("Demo student and faculty accounts are ready.")


if __name__ == "__main__":
    main()
