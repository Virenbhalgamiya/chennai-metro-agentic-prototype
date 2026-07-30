from sqlalchemy.orm import Session
from src.db.database import engine, Base, SessionLocal
from src.db.models import OfficerRecord, LostAndFoundItem, UserRecord
from src.models.enums import ComplaintCategory

def seed_db():
    from src.services.auth import hash_password
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    
    # Check if officers already exist
    officers_exist = db.query(OfficerRecord).first() is not None

    print("Seeding database with demo data...")
    
    if not officers_exist:
        officers = [
            OfficerRecord(
                officer_id="NO-01",
                name="Officer 1 (Ticketing)",
                department="Revenue & Ticketing",
                responsibilities="TICKETING_SMART_CARDS",
                status="AVAILABLE",
                capacity=5
            ),
            OfficerRecord(
                officer_id="NO-02",
                name="Officer 2 (Station)",
                department="Station Management",
                responsibilities="STATION_FACILITIES",
                status="AVAILABLE",
                capacity=8
            ),
            OfficerRecord(
                officer_id="NO-03",
                name="Officer 3 (Train Ops)",
                department="Train Operations",
                responsibilities="TRAIN_OPERATIONS",
                status="AVAILABLE",
                capacity=15
            ),
            OfficerRecord(
                officer_id="NO-04",
                name="Officer 4 (Staff & Safety)",
                department="Customer Service & Security",
                responsibilities="STAFF_BEHAVIOR,SAFETY_SECURITY",
                status="AVAILABLE",
                capacity=10
            ),
            OfficerRecord(
                officer_id="NO-05",
                name="Officer 5 (General)",
                department="General Administration",
                responsibilities="OTHER",
                status="AVAILABLE",
                capacity=20
            )
        ]
        
        db.bulk_save_objects(officers)
    
    if not db.query(UserRecord).first():
        users = [
            UserRecord(
                user_id="USR-PASSENGER",
                full_name="Passenger Demo",
                phone="555-0100",
                email="passenger@demo.com",
                gender="Male",
                age=30,
                password_hash=hash_password("password123"),
                role="PASSENGER"
            ),
            UserRecord(
                user_id="USR-OFFICER",
                full_name="Officer Demo",
                phone="555-0200",
                email="officer@demo.com",
                gender="Female",
                age=35,
                password_hash=hash_password("password123"),
                role="OFFICER"
            ),
            UserRecord(
                user_id="USR-ADMIN",
                full_name="Admin Demo",
                phone="555-0300",
                email="admin@demo.com",
                gender="Male",
                age=40,
                password_hash=hash_password("password123"),
                role="ADMIN"
            )
        ]
        db.bulk_save_objects(users)
    
    if not db.query(LostAndFoundItem).first():
        items = [
            LostAndFoundItem(
                item_id="LF-001",
                description="black backpack",
                station="Chennai Central",
                status="AVAILABLE",
                notes="Found near ticket counter."
            ),
            LostAndFoundItem(
                item_id="LF-002",
                description="wallet",
                station="Guindy",
                status="AVAILABLE",
                notes="Contains ID card."
            ),
            LostAndFoundItem(
                item_id="LF-003",
                description="mobile phone",
                station="Airport",
                status="CLAIMED",
                notes="Claimed on 2023-10-01."
            ),
            LostAndFoundItem(
                item_id="LF-004",
                description="laptop bag",
                station="Alandur",
                status="AVAILABLE",
                notes="Found on platform 2."
            )
        ]
        db.bulk_save_objects(items)
    
    db.commit()
    db.close()
    print("Database seeding completed.")

if __name__ == "__main__":
    seed_db()
