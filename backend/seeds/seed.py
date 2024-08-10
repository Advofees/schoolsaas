from dotenv import load_dotenv
import sys
load_dotenv()
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
import backend.database.all_models  # pyright: ignore [reportUnusedImport]

from backend.models import User,  SchoolStaff, School,SchoolStaffPermissions
from backend.authentication.passwords import hash_password
from sqlalchemy.orm import Session
from backend.database.database import get_db 

def seed_user(db: Session):
    # Create a school
    school = School(
        name="Sample School",
        address="123 School Lane",
        country="Sample Country"
    )
    db.add(school)
    db.flush()

    # Create permissions
    permissions = SchoolStaffPermissions(
        can_add_students=True,
        can_manage_classes=True,
        can_view_reports=False
    )
    db.add(permissions)
    db.flush()

    # Create school staff
    school_staff = SchoolStaff(
        name="Sample Staff",
        school_id=school.id,
        permissions_id=permissions.id,
    )
    db.add(school_staff)
    db.flush()

    # Create user
    user = User(
        username="sampleuser",
        email="user@app.com",
        password_hash=hash_password("password123"),
        school_staff_id=school_staff.id
    )
    db.add(user)
    
    db.commit()



if __name__ == "__main__":
    db = get_db()  
    seed_user(db)
