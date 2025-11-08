from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlalchemy import inspect
from app.database.session import engine
from app.database.base import Base, SCHEMA_CREATION_ENVS
from app.core.config import get_settings

settings = get_settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    if settings.ENV in SCHEMA_CREATION_ENVS:
        print(f"[{settings.ENV.upper()}]: Auto-creating database schema...")
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)

    async with engine.begin() as conn:

        def list_tables(connection):
            inspector = inspect(connection)
            return inspector.get_table_names(schema="public")
        
        table_names = await conn.run_sync(list_tables)

    if table_names:
        print(f"Found {len(table_names)} tables: {', '.join(table_names)}")
    else:
        print("No tables found in the database.")
        
    yield 
    
    print("Application shutting down...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan
)