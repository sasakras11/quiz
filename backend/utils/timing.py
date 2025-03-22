import time
import logging

logger = logging.getLogger(__name__)

class Timer:
    """Timer utility for tracking execution time"""
    def __init__(self, name: str):
        self.name = name
        
    async def __aenter__(self):
        self.start = time.time()
        logger.info(f"🔄 Starting {self.name}...")
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        duration = time.time() - self.start
        logger.info(f"⏱️ {self.name} took {duration:.2f} seconds")
        self.duration = duration