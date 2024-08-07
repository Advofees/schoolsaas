from pydantic import BaseModel

class GetSchool(BaseModel):
    name: str
    location: str
    phone_number: str
    email: str
    website: str
    logo: str

class CreateSchool(BaseModel):
    name: str
    location: str
    phone_number: str
    email: str
    website: str
    logo: str

class UpdateSchool(BaseModel):
    name: str
    location: str
    phone_number: str
    email: str
    website: str
    logo: str
    
class DeleteSchool(BaseModel):
    school_id: str