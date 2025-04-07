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


class UserSchema(BaseModel):
    user_name:str
    email:str
    password:str


class UserDeletionSchema(BaseModel):
    user_id:int


class UserUpdationSchema(BaseModel):
    user_id:int
    user_name:str


class RegisterWebsiteSchema(BaseModel):
    owner_id:int
    website_name:str
    

