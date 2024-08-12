from typing import Type,List
from backend.database.base import Base
from backend.models import Student,School,SchoolStaff,SchoolParent,Inventory,InventoryItem,File,Payment,SchoolStaffPermissions,StaffUser

ALL_MODELS: List[Type[Base]] = [

    Student,
    School,
    SchoolStaff,
    SchoolParent,
    Inventory,
    InventoryItem,
    File,
    Payment,
    SchoolStaffPermissions,
    StaffUser,
]