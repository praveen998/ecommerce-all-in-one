from aiomysql import create_pool
from typing import Optional
import asyncio


class Mysqlpool:
    _instance: Optional["MySQLPool"] = None

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
        if self._pool:
            self._pool.close()
            await self._pool.wait_closed()