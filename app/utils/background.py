import asyncio
import logging

logger = logging.getLogger(__name__)

def fire_and_forget(coro):
    """Schedule a coroutine to run in background (non-blocking)."""
    try:
        asyncio.create_task(coro)
    except RuntimeError:
        logger.exception("Failed to schedule background task")
        raise