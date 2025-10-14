"""RabbitMQ message queue tools for MCP"""
import os
import aio_pika
import json
from typing import Dict, Any, Optional

class RabbitMQTools:
    """Tools for RabbitMQ message queue operations."""

    connection: Optional[aio_pika.Connection] = None
    channel: Optional[aio_pika.Channel] = None

    @classmethod
    async def get_connection(cls):
        """Get or create RabbitMQ connection."""
        if cls.connection is None or cls.connection.is_closed:
            rabbitmq_url = os.getenv("RABBITMQ_URI")
            if rabbitmq_url:
                try:
                    cls.connection = await aio_pika.connect_robust(
                        rabbitmq_url,
                        timeout=10
                    )
                    cls.channel = await cls.connection.channel()
                except Exception as e:
                    print(f"RabbitMQ connection failed: {e}")
                    return None
        return cls.connection

    @staticmethod
    async def handle(name: str, arguments: Dict[str, Any]) -> str:
        """Handle RabbitMQ tool calls."""

        if name == "rabbitmq_publish":
            return await RabbitMQTools.publish_message(
                arguments.get("queue"),
                arguments.get("message"),
                arguments.get("exchange", "")
            )
        elif name == "rabbitmq_consume":
            return await RabbitMQTools.consume_message(
                arguments.get("queue"),
                arguments.get("count", 1)
            )
        elif name == "rabbitmq_queue_info":
            return await RabbitMQTools.queue_info(
                arguments.get("queue")
            )
        elif name == "rabbitmq_declare_queue":
            return await RabbitMQTools.declare_queue(
                arguments.get("queue"),
                arguments.get("durable", True)
            )

        return f"Unknown RabbitMQ tool: {name}"

    @staticmethod
    async def publish_message(queue: str, message: dict, exchange: str = "") -> str:
        """Publish a message to RabbitMQ queue."""
        try:
            conn = await RabbitMQTools.get_connection()
            if not conn:
                return "RabbitMQ not configured. Set RABBITMQ_URI environment variable."

            channel = RabbitMQTools.channel

            # Declare queue (ensure it exists)
            await channel.declare_queue(queue, durable=True)

            # Publish message
            message_body = json.dumps(message).encode()
            await channel.default_exchange.publish(
                aio_pika.Message(body=message_body),
                routing_key=queue
            )

            return f"Message published to queue '{queue}'"

        except Exception as e:
            return f"RabbitMQ publish error: {str(e)}"

    @staticmethod
    async def consume_message(queue: str, count: int = 1) -> str:
        """Consume messages from RabbitMQ queue."""
        try:
            conn = await RabbitMQTools.get_connection()
            if not conn:
                return "RabbitMQ not configured."

            channel = RabbitMQTools.channel

            # Declare queue
            queue_obj = await channel.declare_queue(queue, durable=True)

            # Get messages
            messages = []
            for _ in range(count):
                msg = await queue_obj.get(timeout=5.0)
                if msg:
                    messages.append(msg.body.decode())
                    await msg.ack()
                else:
                    break

            if messages:
                return f"Consumed {len(messages)} messages: {messages}"
            else:
                return "No messages in queue"

        except Exception as e:
            return f"RabbitMQ consume error: {str(e)}"

    @staticmethod
    async def queue_info(queue: str) -> str:
        """Get information about a RabbitMQ queue."""
        try:
            conn = await RabbitMQTools.get_connection()
            if not conn:
                return "RabbitMQ not configured."

            channel = RabbitMQTools.channel

            # Declare queue (passive to not create)
            queue_obj = await channel.declare_queue(queue, passive=True)

            return f"Queue '{queue}': {queue_obj.declaration_result.message_count} messages"

        except Exception as e:
            return f"RabbitMQ queue info error: {str(e)}"

    @staticmethod
    async def declare_queue(queue: str, durable: bool = True) -> str:
        """Declare/create a RabbitMQ queue."""
        try:
            conn = await RabbitMQTools.get_connection()
            if not conn:
                return "RabbitMQ not configured."

            channel = RabbitMQTools.channel

            await channel.declare_queue(queue, durable=durable)

            return f"Queue '{queue}' declared successfully"

        except Exception as e:
            return f"RabbitMQ declare error: {str(e)}"

    @classmethod
    async def close(cls):
        """Close RabbitMQ connection."""
        if cls.connection and not cls.connection.is_closed:
            await cls.connection.close()
            cls.connection = None
            cls.channel = None
