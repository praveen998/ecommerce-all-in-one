from aiomysql import create_pool
from typing import Optional
import asyncio
import os 
from dotenv import load_dotenv


class Mysqlpool:
    _instance: Optional["Mysqlpool"] = None

    def __new__(cls,*args,**kwargs):
        if not cls._instance:
            cls._instance=super().__new__(cls)
            return cls._instance  
    
    def __init__(self, host: str, port: int, user: str, password: str, db: str):
        if not hasattr(self, "_initialized"):
            self._initialized = True
            self._pool = None
            self.host = host
            self.port = port
            self.user = user
            self.password = password
            self.db = db


    async def init_pool(self):
        print("pool started------------------------------------")
        if not self._pool:
            self._pool = await create_pool(
                host=self.host,
                port=self.port,
                user=self.user,
                password=self.password,
                db=self.db,
                minsize=1,
                maxsize=10,
            )

    async def get_connection(self):
        if not self._pool:
            await self.init_pool()
        return await self._pool.acquire()

    async def release_connection(self, conn):
        self._pool.release(conn)

    async def close_pool(self):
        print("pool stoped--------------------------------------")
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()

#------------------------------------------------------------------------------------------------------

from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


load_dotenv()

host = os.getenv("host")
port = int(os.getenv("port"))  # Convert to integer
user = os.getenv("user")
password = os.getenv("password")
db = os.getenv("db")
Base = declarative_base()


DATABASE_URL = f"mysql+pymysql://{user}:{password}@{host}:{port}/{db}"
engine = create_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)



class User(Base):
    __tablename__ = 'user'  

    id = Column(Integer, primary_key=True)
    username = Column(String(50), nullable=False)
    email = Column(String(100), nullable=False)
    password = Column(String(100), nullable=False)



class OwnerDetails(Base):
    __tablename__= 'ownerdetails'
    
    ownerid=        Column(Integer,primary_key=True)
    company_name=   Column(String(100), nullable=False,unique=True)
    owner_name=     Column(String(100), nullable=False)
    phone=          Column(String(50), nullable=False,unique=True)
    username=       Column(String(100), nullable=False,unique=True)
    password=       Column(String(100), nullable=False,unique=True)
    company_type=   Column(String(100), nullable=False)


Base.metadata.create_all(engine)

