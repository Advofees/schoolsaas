import sys
import os

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv

load_dotenv()


import backend.database.all_models  # pyright: ignore [reportUnusedImport]

from backend.models import StaffUser,  SchoolStaff, School,SchoolStaffPermissions
from backend.authentication.passwords import hash_password
from sqlalchemy.orm import Session
from backend.database.database import get_db 

def seed_user(db: Session):
    # Create a school
    school = School(
        name="Sample School",
        address="123 School Lane",
        country="Sample Country",
        school_number="123456",
    )
    db.add(school)
    db.flush()

    # Create permissions
    permissions_1 = SchoolStaffPermissions(
        can_add_students=True,
        can_manage_classes=True,
        can_view_reports=False,
        can_add_parents=True
    )
    permission_2 = SchoolStaffPermissions(
        can_add_students=True,
        can_manage_classes=True,
        can_view_reports=True,
        can_add_parents=True
    )
    db.add_all([permissions_1, permission_2])
    db.flush()


    school_staff = SchoolStaff(
        name="Sample Staff",
        school_id=school.id,
        permissions_id=permissions_1.id,
    )
    school_staff_1 = SchoolStaff(
        name="shoooo staff user",
        school_id=school.id,
        permissions_id=permission_2.id,
    )
    db.add_all([school_staff, school_staff_1])
    db.flush()


    user = StaffUser(
        username="sampleuser",
        email="user@app.com",
        password_hash=hash_password("password123"),
        school_staff_id=school_staff.id
    )
    user_1 = StaffUser(
        username="sampleuser_2",
        email="user_2@app.com",
        password_hash=hash_password("password123"),
        school_staff_id=school_staff.id
    )
    db.add_all([user, user_1])
    db.flush()
    db.commit()



if __name__ == "__main__":
    db = get_db()  
    seed_user(db)
