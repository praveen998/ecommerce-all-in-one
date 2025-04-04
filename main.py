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
developer_jwt = JWTHandler(SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES)

@app.post("/developer_auth")
async def developer_auth(auth:Developer_auth):
    #password="nibhas1234"
    passhash=os.getenv("developer_password_hash")
    if passhash is None:
        raise HTTPException(status_code=500, detail="Server misconfiguration: Hash not set")
    status=await Hashing.verify_password(auth.password,passhash)
    # print("user:",auth.username)
    # print("password:",auth.password)
    if status :
        token = developer_jwt.create_access_token(data={"username": auth.username})
        return {"message": "Login successful", "status": "success","token": token}
    else:
        raise HTTPException(status_code=401, detail="Invalid username or password")




@app.get("/protected")
async def protected_route(request: Request):
    token = request.headers.get("Authorization")
    if not token or not token.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Token not provided or invalid format")

    token = token.split(" ")[1]
    payload = jwt_handler.verify_token(token)
    return {"message": "Access granted", "user": payload.get("username")}
