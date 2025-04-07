from fastapi import FastAPI,HTTPException,Request
import aiomysql
from datamodel.database import Mysqlpool
import os 
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from datamodel.database import SessionLocal ,User
from fastapi.middleware.cors import CORSMiddleware
from datamodel.utils import Rawsqlquery

app=FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_methods=["*"],
    allow_headers=["*"],
)


load_dotenv()


db_config={
    "host": os.getenv("host"),
    "port": int(os.getenv("port")),
    "user": os.getenv("user"),
    "password": os.getenv("password"),
    "db": os.getenv("db")
}

#define mysql_pool for ecommerce daatabase---------------
mysql_pool = Mysqlpool(**db_config)


@app.on_event("startup")
async def startup_event():
    await mysql_pool.init_pool()


@app.on_event("shutdown")
async def shutdown_event():
    await mysql_pool.close_pool()



@app.get("/")
async def read_root():
    return {"message": "Welcome to FastAPI!"}


@app.get("/items/{item_id}")
async def read_item(item_id: int, q: str = None):
    db: Session = SessionLocal()
    new_user = User(username="john_doe", email="john@example.com", password="password123")
    db.add(new_user)
    db.commit()
    user = db.query(User).filter(User.id == item_id).first()
    print("username:",user.username)
    return {"item_id": item_id, "q": user}


#calling selection query----------------------------
@app.get("/items_selection/")
async def read_items():
    result=await Rawsqlquery.selection_query(mysql_pool,"SELECT * FROM user;")
    return result


#calling insertion query-----------------------------
from pydanticmodel import UserSchema
@app.post("/items_insertion/")
async def read_items(user:UserSchema):
    query="insert into user(username,email,password) values(%s,%s,%s)"
    params=(str(user.user_name),str(user.email),str(user.password))
    result=await Rawsqlquery.insertion_query(mysql_pool,query,params)
    if result > 0:
        return {"message": "data added successfully", "status": "success"}
    else:
        raise HTTPException(status_code=400,detail="No user was inserted")


#calling deletion query-------------------------------
from pydanticmodel import UserDeletionSchema
@app.post("/items_deletion/")
async def read_items(user:UserDeletionSchema):
    query="delete from user where id = %s"
    params=(user.user_id)
    result=await Rawsqlquery.insertion_query(mysql_pool,query,params)
    if result > 0:
        return {"message": "data deleted successfully", "status": "success"}
    else:
        raise HTTPException(status_code=400,detail="No user was deleted")


#calling updation query-------------------------------
from pydanticmodel import UserUpdationSchema
@app.post("/items_updation/")
async def read_items(user:UserUpdationSchema):
    query = "UPDATE user SET username = %s WHERE id = %s"
    params=(user.user_name,user.user_id)
    result=await Rawsqlquery.updation_query(mysql_pool,query,params)
    if result > 0:
        return {"message": "data updated successfully", "status": "success"}
    else:
        raise HTTPException(status_code=400,detail="No user was updated")



from datamodel.utils import Hashing
from pydanticmodel import Developer_auth
from datamodel.utils import JWTHandler


dev_SECRET_KEY=os.getenv("HASH_SECRET_KEY")
dev_ALGORITHM="HS256"
dev_ACCESS_TOKEN_EXPIRE_MINUTES=60 
developer_jwt = JWTHandler(dev_SECRET_KEY, dev_ALGORITHM, dev_ACCESS_TOKEN_EXPIRE_MINUTES)


#client authentication and token creation
@app.post("/developer_auth")
async def developer_auth(auth:Developer_auth):
    #password="nibhas1234"
    passhash=os.getenv("developer_password_hash")
    if passhash is None:
        raise HTTPException(status_code=500, detail="Server misconfiguration: Hash not set")
    status=await Hashing.verify_password(auth.password,passhash)
    print("user:",auth.username)
    print("password:",auth.password)
    print("status:",status)
    if status :
        token = developer_jwt.create_access_token(data={"username": auth.username})
        print("token",token)
        return {"message": "Login successful", "status": "success","token": token}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")



#check token is stored client side
@app.get("/protected")
async def protected_route(request: Request):
    # token = request.headers.get("Authorization")
    # if not token or not token.startswith("Bearer "):
    #     raise HTTPException(status_code=401, detail="Token not provided or invalid format")
    # token = token.split(" ")[1]
    # payload = developer_jwt.verify_token(token)
    # print("payload:",payload)
    # return {"message": "Access granted", "user": payload.get("username")}
    payload=JWTHandler.jwt_header_extraction(developer_jwt,request)
    return {"message": "Access granted", "user": payload['user']['username']}


from datamodel.database import OwnerDetails
from pydanticmodel import OwnerDetailsSchema


@app.post("/register_owner/")
def register_owner(owner: OwnerDetailsSchema):
    db =SessionLocal()
    db_owner=OwnerDetails(**owner.dict())

    try:
        db.add(db_owner)
        db.commit()
        db.refresh(db_owner)
        return {"message": "Owner registered successfully", "owner_id": db_owner.ownerid}
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username, phone, or company name already exists")
    finally:
        db.close()
    

from pydanticmodel import RegisterWebsiteSchema
@app.post("/register_website/")
def register_website(website: RegisterWebsiteSchema):
    query="insert into websitedetails(owner_id,website_name) values(%s,%s)"
    params=(website.owner_id,website.website_name)
    result=await Rawsqlquery.insertion_query(mysql_pool,query,params)
    if result > 0:
        return {"message": "website added successfully", "status": "success"}
    else:
        raise HTTPException(status_code=400,detail="No website was inserted")









