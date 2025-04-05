from fastapi import FastAPI,HTTPException,Request
import aiomysql
from datamodel.database import Mysqlpool
import os 
from dotenv import load_dotenv
from sqlalchemy.orm import Session
from datamodel.database import SessionLocal ,User
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/items/")
async def read_items():
    conn: Connection = await mysql_pool.get_connection()
    async with conn.cursor() as cursor:
        await cursor.execute("SELECT * FROM user;")
        result = await cursor.fetchall()
    await mysql_pool.release_connection(conn)
    return result


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



