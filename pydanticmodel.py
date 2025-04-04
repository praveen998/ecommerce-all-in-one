from pydantic import BaseModel

class Developer_auth(BaseModel):
    username:str
    password:str
    