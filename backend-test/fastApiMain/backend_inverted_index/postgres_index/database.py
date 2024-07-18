import asyncpg

async def get_database_connection():
    conn = await asyncpg.connect(
        user='postgres',
        password='postgres',
        database='postgres',
        host='dbbd2.c3k4mdbqyxzb.us-east-1.rds.amazonaws.com',
        port=5432
    )
    return conn
