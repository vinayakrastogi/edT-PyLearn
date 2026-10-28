from app.core.security import hash_password, verify_password
from app.models.user import User
from tools.seed_demo import DEMO_ACCOUNTS, seed_demo_accounts


def test_demo_seeding_migrates_the_original_learner_and_creates_faculty(db):
    original = User(email="demo@example.com", full_name="Demo Learner", role="student",
                    hashed_password=hash_password("PyLearnDemo123!"))
    db.add(original)
    db.commit()
    original_id = original.id
    seed_demo_accounts(db)
    student = db.query(User).filter_by(email="demostudent@example.com").one()
    assert student.id == original_id
    assert db.query(User).filter_by(email="demo@example.com").first() is None
    assert db.query(User).count() == 2
    for email, password, name, role in DEMO_ACCOUNTS:
        user = db.query(User).filter_by(email=email).one()
        assert user.role == role and user.full_name == name
        assert verify_password(password, user.hashed_password)


def test_repeated_seeding_preserves_ids_and_unrelated_users(db):
    other = User(email="other@example.com", full_name="Other User", role="student",
                 hashed_password=hash_password("AnotherPassword!"))
    db.add(other)
    db.commit()
    seed_demo_accounts(db)
    before = {u.email: (u.id, u.hashed_password) for u in db.query(User).all()}
    seed_demo_accounts(db)
    assert {u.email: (u.id, u.hashed_password) for u in db.query(User).all()} == before
    assert other.full_name == "Other User"
