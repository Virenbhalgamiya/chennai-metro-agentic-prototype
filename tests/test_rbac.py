import pytest
from src.db.models import UserRecord, ComplaintRecord
from src.db.database import Base, engine, SessionLocal
from src.db.repositories import UserRepository, ComplaintRepository
from src.services.auth import hash_password

@pytest.fixture(scope="module")
def test_db():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

def test_user_creation_and_retrieval(test_db):
    user_repo = UserRepository(test_db)
    
    user = UserRecord(
        user_id="TEST-USER",
        full_name="Test Passenger",
        email="test@demo.com",
        password_hash=hash_password("password"),
        role="PASSENGER"
    )
    user_repo.save(user)
    
    fetched = user_repo.get_by_email("test@demo.com")
    assert fetched is not None
    assert fetched.full_name == "Test Passenger"
    assert fetched.role == "PASSENGER"
    assert fetched.password_hash != "password" # ensuring plain text is not saved here

def test_passenger_complaint_ownership(test_db):
    user_repo = UserRepository(test_db)
    comp_repo = ComplaintRepository(test_db)
    
    user1 = UserRecord(user_id="U1", full_name="User 1", password_hash="hash", role="PASSENGER")
    user2 = UserRecord(user_id="U2", full_name="User 2", password_hash="hash", role="PASSENGER")
    user_repo.save(user1)
    user_repo.save(user2)
    
    c1 = ComplaintRecord(complaint_id="C1", user_id="U1", original_text="U1 complaint", source="WEB")
    c2 = ComplaintRecord(complaint_id="C2", user_id="U2", original_text="U2 complaint", source="WEB")
    comp_repo.save(c1)
    comp_repo.save(c2)
    
    u1_complaints = comp_repo.get_by_user_id("U1")
    assert len(u1_complaints) == 1
    assert u1_complaints[0].complaint_id == "C1"
    
    u2_complaints = comp_repo.get_by_user_id("U2")
    assert len(u2_complaints) == 1
    assert u2_complaints[0].complaint_id == "C2"
