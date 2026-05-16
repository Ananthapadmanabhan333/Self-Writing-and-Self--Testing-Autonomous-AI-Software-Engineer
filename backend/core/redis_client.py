"""
NEXUS OS — Redis Client
Async client for caching and task queue coordination.
"""

from typing import Optional
import redis.asyncio as redis
import structlog
from core.config import settings

logger = structlog.get_logger()

class RedisClient:
    def __init__(self):
        self.url = settings.REDIS_URL
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        """Initialize the async Redis client."""
        if not self.client:
            try:
                self.client = await redis.from_url(
                    self.url, 
                    encoding="utf-8", 
                    decode_responses=True,
                    socket_timeout=5.0
                )
                await self.client.ping()
                logger.info("✅ Redis client connected", url=self.url)
            except Exception as e:
                logger.error("❌ Redis connection failed", error=str(e))
                raise e

    async def disconnect(self):
        """Close the Redis connection."""
        if self.client:
            await self.client.close()
            logger.info("✅ Redis client disconnected")

    async def get(self, key: str) -> Optional[str]:
        return await self.client.get(key)

    async def set(self, key: str, value: str, expire: Optional[int] = None):
        await self.client.set(key, value, ex=expire)

    async def delete(self, key: str):
        await self.client.delete(key)

    async def ping(self) -> bool:
        try:
            return await self.client.ping()
        except Exception:
            return False

    async def publish(self, channel: str, message: str):
        """Publish a message to a Redis Pub/Sub channel."""
        await self.client.publish(channel, message)

redis_client = RedisClient()
