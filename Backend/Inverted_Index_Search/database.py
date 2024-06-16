import asyncpg

async def get_database_connection():
    conn = await asyncpg.connect(
        user='postgres',
        password='postgres',
        database='postgres',
        host='localhost',
        port=5432
    )
    return conn
