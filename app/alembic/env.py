from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config
from alembic import context
from logging.config import fileConfig
from app.database.base import Base 
from app.core.config import get_settings 
import asyncio

config = context.config
fileConfig(config.config_file_name)
target_metadata = Base.metadata

settings = get_settings()

# Define the synchronous migration runner function first.
# This function is executed by connection.run_sync() and receives the 
# SYNCHRONOUS connection adapter object as its first argument (conn).
def do_run_migrations_sync(conn):
    """Configures Alembic context and runs migrations synchronously."""
    
    # 1. Configure the context using the SYNCHRONOUS connection adapter (conn)
    context.configure(
        connection=conn,
        target_metadata=target_metadata,
    )
    
    # 2. Start the synchronous transaction and run the migrations inside it.
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        url=settings.DATABASE_URL,
        poolclass=pool.NullPool,
    )

    # New wrapper function to handle the async connection setup
    async def process_migrations():
        # Use connectable.begin() for transactional integrity during migration.
        # This yields an AsyncConnection object.
        async with connectable.begin() as connection:
            # connection.run_sync() executes the synchronous function 'do_run_migrations_sync' 
            # in a thread, passing the necessary synchronous connection adapter object as the 'conn' argument.
            await connection.run_sync(do_run_migrations_sync)

    # Run the new async wrapper function to start the process
    asyncio.run(process_migrations())

run_migrations_online()