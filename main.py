from fastapi import FastAPI
import aiomysql
from datamodel.database import MySQLPool

app=FastAPI()

db_config={
    "host": "localhost",
    "port": 3306,
    "user": "root",
    "password": "password",
    "db": "testdb"
}

mysql_pool = MySQLPool(**db_config)



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
    return {"item_id": item_id, "q": q}



@app.get("/items/")
async def read_items():
    conn: Connection = await MySQLPool.get_connection()
    async with conn.cursor() as cursor:
        await cursor.execute("SELECT * FROM items;")
        result = await cursor.fetchall()
    await MySQLPool.release_connection(conn)
    return result
