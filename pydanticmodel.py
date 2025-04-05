from pydantic import BaseModel

class Developer_auth(BaseModel):
    username:str
    password:str
    

class OwnerDetailsSchema(BaseModel):
    company_name: str
    owner_name: str
    phone: str
    username: str
    password: str
    company_type: str

