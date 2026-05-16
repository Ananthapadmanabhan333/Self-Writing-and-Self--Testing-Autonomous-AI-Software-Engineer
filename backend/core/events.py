"""
NEXUS OS — Event Orchestration (Kafka)
Asynchronous event producer for distributed system coordination.
"""

import json
from typing import Any, Dict, Optional
import arrow
import structlog
from aiokafka import AIOKafkaProducer
from core.config import settings

logger = structlog.get_logger()

class KafkaProducer:
    def __init__(self):
        self.bootstrap_servers = settings.KAFKA_BOOTSTRAP_SERVERS
        self.producer: Optional[AIOKafkaProducer] = None

    async def start(self):
        """Start the Kafka producer."""
        try:
            self.producer = AIOKafkaProducer(
                bootstrap_servers=self.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode('utf-8')
            )
            await self.producer.start()
            logger.info("✅ Kafka producer started", servers=self.bootstrap_servers)
        except Exception as e:
            logger.error("❌ Kafka producer failed to start", error=str(e))
            # Fallback for local development without Kafka
            self.producer = None

    async def stop(self):
        """Stop the Kafka producer."""
        if self.producer:
            await self.producer.stop()
            logger.info("✅ Kafka producer stopped")

    async def emit_event(self, topic: str, event_type: str, payload: Dict[str, Any]):
        """Emit an event to a Kafka topic."""
        if not self.producer:
            logger.debug("📡 Event emitted (fallback)", topic=topic, event=event_type)
            return

        message = {
            "event_type": event_type,
            "payload": payload,
            "timestamp": arrow.now().isoformat()
        }
        
        try:
            await self.producer.send_and_wait(topic, message)
            logger.debug("📡 Event emitted", topic=topic, event=event_type)
        except Exception as e:
            logger.error("❌ Failed to emit Kafka event", error=str(e), topic=topic)

kafka_producer = KafkaProducer()
