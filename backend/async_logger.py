"""
Non-blocking async logging for UsageLog entries.

Architecture:
- Main thread: Queue log entries (O(1) fast)
- Background task: Batch write logs every N seconds
- No DB blocking on POST requests

Features:
- asyncio.Queue for buffering logs
- Batch writes: group N logs into single transaction
- Automatic flush: write every T seconds
- Error handling: failed writes don't crash app
- Graceful shutdown: flush remaining logs on exit
"""

import asyncio
import logging
from typing import List, Optional
from datetime import datetime
from models import UsageLog
from db import AsyncSessionLocal

logger = logging.getLogger(__name__)

# Configuration
QUEUE_SIZE = 1000  # Buffer up to 1000 logs in memory
BATCH_SIZE = 50    # Write 50 logs per batch
FLUSH_INTERVAL = 5  # Flush every 5 seconds

# Global queue and worker task
_log_queue: Optional[asyncio.Queue] = None
_worker_task: Optional[asyncio.Task] = None


class LogEntry:
    """Internal representation of a log entry"""
    def __init__(
        self,
        id: str,
        customer_id: str,
        api_key_id: str,
        model: str,
        operation: str,
        meta: dict,
        risk_score: int,
        allowed: bool,
        reason: str,
        created_at: Optional[datetime] = None
    ):
        self.id = id
        self.customer_id = customer_id
        self.api_key_id = api_key_id
        self.model = model
        self.operation = operation
        self.meta = meta
        self.risk_score = risk_score
        self.allowed = allowed
        self.reason = reason
        self.created_at = created_at or datetime.utcnow()


async def init_logger():
    """Initialize the logging queue and worker"""
    global _log_queue, _worker_task
    
    if _log_queue is not None:
        logger.warning("Logger already initialized")
        return
    
    _log_queue = asyncio.Queue(maxsize=QUEUE_SIZE)
    _worker_task = asyncio.create_task(_worker_loop())
    logger.info("✅ Async logging initialized")


async def shutdown_logger():
    """Flush remaining logs and shutdown"""
    global _log_queue, _worker_task
    
    if _log_queue is None:
        return
    
    logger.info("Shutting down logger - flushing remaining logs...")
    
    # Flush remaining items
    remaining = []
    while not _log_queue.empty():
        try:
            entry = _log_queue.get_nowait()
            remaining.append(entry)
        except asyncio.QueueEmpty:
            break
    
    if remaining:
        logger.info(f"Flushing {len(remaining)} remaining logs")
        await _batch_write(remaining)
    
    # Cancel worker task
    if _worker_task:
        _worker_task.cancel()
        try:
            await _worker_task
        except asyncio.CancelledError:
            pass
    
    _log_queue = None
    _worker_task = None
    logger.info("✅ Logger shutdown complete")


async def queue_log(
    id: str,
    customer_id: str,
    api_key_id: str,
    model: str,
    operation: str,
    meta: dict,
    risk_score: int,
    allowed: bool,
    reason: str
) -> bool:
    """
    Queue a log entry (non-blocking).
    
    Args:
        All parameters same as UsageLog model
    
    Returns:
        True if queued successfully, False if queue full
    """
    if _log_queue is None:
        logger.warning("Logger not initialized - dropping log")
        return False
    
    entry = LogEntry(
        id=id,
        customer_id=customer_id,
        api_key_id=api_key_id,
        model=model,
        operation=operation,
        meta=meta,
        risk_score=risk_score,
        allowed=allowed,
        reason=reason
    )
    
    try:
        # Non-blocking put (raises asyncio.QueueFull if full)
        _log_queue.put_nowait(entry)
        return True
    except asyncio.QueueFull:
        logger.error("Log queue full - dropping entry")
        return False


async def _worker_loop():
    """
    Background worker that batches and writes logs.
    
    - Collects logs into batches
    - Writes every BATCH_SIZE or FLUSH_INTERVAL
    - Never blocks main thread
    """
    batch: List[LogEntry] = []
    last_flush = asyncio.get_event_loop().time()
    
    while True:
        try:
            # Calculate timeout for next flush
            now = asyncio.get_event_loop().time()
            time_since_flush = now - last_flush
            wait_time = max(0, FLUSH_INTERVAL - time_since_flush)
            
            # Try to get next log entry (with timeout)
            try:
                entry = await asyncio.wait_for(
                    _log_queue.get(),
                    timeout=wait_time
                )
                batch.append(entry)
            except asyncio.TimeoutError:
                # Timeout reached - flush if we have logs
                if batch:
                    await _batch_write(batch)
                    batch = []
                    last_flush = asyncio.get_event_loop().time()
                continue
            
            # Check if batch is full
            if len(batch) >= BATCH_SIZE:
                await _batch_write(batch)
                batch = []
                last_flush = asyncio.get_event_loop().time()
        
        except asyncio.CancelledError:
            logger.info("Worker loop cancelled")
            break
        except Exception as e:
            logger.error(f"Unexpected error in worker loop: {e}", exc_info=True)
            await asyncio.sleep(1)  # Back off on error


async def _batch_write(batch: List[LogEntry]):
    """Write a batch of logs to database"""
    if not batch:
        return
    
    try:
        async with AsyncSessionLocal() as session:
            # Convert LogEntry objects to UsageLog models
            logs = [
                UsageLog(
                    id=entry.id,
                    customer_id=entry.customer_id,
                    api_key_id=entry.api_key_id,
                    model=entry.model,
                    operation=entry.operation,
                    meta=entry.meta,
                    risk_score=entry.risk_score,
                    allowed=entry.allowed,
                    reason=entry.reason,
                    created_at=entry.created_at
                )
                for entry in batch
            ]
            
            # Batch insert
            session.add_all(logs)
            await session.commit()
            
            logger.debug(f"✅ Flushed {len(batch)} logs to database")
    
    except Exception as e:
        logger.error(f"❌ Failed to write logs: {e}", exc_info=True)
        # Don't crash - logs will be retried next batch


async def get_queue_stats() -> dict:
    """Get current queue statistics"""
    if _log_queue is None:
        return {"status": "not_initialized"}
    
    return {
        "status": "running",
        "queue_size": _log_queue.qsize(),
        "queue_maxsize": _log_queue.maxsize,
        "batch_size": BATCH_SIZE,
        "flush_interval": FLUSH_INTERVAL
    }
