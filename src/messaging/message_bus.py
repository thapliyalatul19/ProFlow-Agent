"""
Message Bus for Agent-to-Agent Communication.

Provides centralized messaging system for multi-agent coordination.
"""

import json
import os
from typing import Dict, List, Callable, Any
from datetime import datetime
from dataclasses import dataclass, asdict
import asyncio
from enum import Enum
from pathlib import Path
import logging


class MessageType(Enum):
    """Message types for agent communication"""
    REQUEST = "request"
    RESPONSE = "response"
    BROADCAST = "broadcast"
    ERROR = "error"


@dataclass
class AgentMessage:
    """Message structure for agent communication"""
    sender: str
    receiver: str
    message_type: MessageType
    content: Dict[str, Any]
    timestamp: str = None
    message_id: str = None
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
        if not self.message_id:
            self.message_id = f"{self.sender}_{self.receiver}_{datetime.now().timestamp()}"
    
    def to_dict(self):
        """Convert message to dictionary"""
        return {
            'sender': self.sender,
            'receiver': self.receiver,
            'message_type': self.message_type.value,
            'content': self.content,
            'timestamp': self.timestamp,
            'message_id': self.message_id
        }


class MessageBus:
    """Central message bus for agent communication"""
    
    def __init__(self):
        self.subscribers: Dict[str, List[Callable]] = {}
        self.message_history: List[AgentMessage] = []
        
        # Setup log file path
        project_root = Path(__file__).parent.parent.parent
        self.message_log_file = project_root / 'data' / 'agent_messages.json'
        self.logger = logging.getLogger(__name__)
        
        self._load_history()
    
    def _load_history(self):
        """Load message history from file"""
        if self.message_log_file.exists():
            try:
                with open(self.message_log_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Convert back to AgentMessage objects
                    self.message_history = []
                    for msg in data:
                        try:
                            message = AgentMessage(
                                sender=msg['sender'],
                                receiver=msg['receiver'],
                                message_type=MessageType(msg['message_type']),
                                content=msg['content'],
                                timestamp=msg.get('timestamp'),
                                message_id=msg.get('message_id')
                            )
                            self.message_history.append(message)
                        except Exception as e:
                            self.logger.warning(f"Error loading message: {e}")
            except Exception as e:
                self.logger.warning(f"Error loading message history: {e}")
                self.message_history = []
    
    def _save_history(self):
        """Save message history to file"""
        self.message_log_file.parent.mkdir(parents=True, exist_ok=True)
        try:
            with open(self.message_log_file, 'w', encoding='utf-8') as f:
                json.dump(
                    [msg.to_dict() for msg in self.message_history[-100:]],  # Keep last 100
                    f, indent=2, ensure_ascii=False
                )
        except Exception as e:
            self.logger.error(f"Error saving message history: {e}")
    
    def subscribe(self, agent_name: str, callback: Callable):
        """
        Subscribe an agent to receive messages.
        
        Args:
            agent_name: Name of the agent
            callback: Callback function to handle messages
        """
        if agent_name not in self.subscribers:
            self.subscribers[agent_name] = []
        self.subscribers[agent_name].append(callback)
        self.logger.info(f"Agent '{agent_name}' subscribed to message bus")
    
    def publish(self, message: AgentMessage):
        """
        Publish message to receiver(s).
        
        Args:
            message: AgentMessage to publish
        """
        # Log message
        self.message_history.append(message)
        self._save_history()
        
        self.logger.info(
            f"[MESSAGE BUS] {message.sender} -> {message.receiver}: {message.message_type.value}"
        )
        
        # Deliver to specific receiver
        if message.receiver in self.subscribers:
            for callback in self.subscribers[message.receiver]:
                try:
                    callback(message)
                except Exception as e:
                    self.logger.error(f"Error in message callback: {e}")
        
        # Handle broadcasts
        elif message.receiver == "ALL":
            for agent, callbacks in self.subscribers.items():
                if agent != message.sender:
                    for callback in callbacks:
                        try:
                            callback(message)
                        except Exception as e:
                            self.logger.error(f"Error in broadcast callback: {e}")
    
    async def publish_async(self, message: AgentMessage):
        """Async message publishing"""
        await asyncio.get_event_loop().run_in_executor(
            None, self.publish, message
        )
    
    def get_conversation(self, agent1: str, agent2: str) -> List[AgentMessage]:
        """
        Get message history between two agents.
        
        Args:
            agent1: First agent name
            agent2: Second agent name
        
        Returns:
            List of messages between the two agents
        """
        return [
            msg for msg in self.message_history
            if (msg.sender == agent1 and msg.receiver == agent2) or
               (msg.sender == agent2 and msg.receiver == agent1)
        ]


# Global message bus instance
message_bus = MessageBus()


# Example usage
if __name__ == "__main__":
    import sys
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
    
    from utils.logger import setup_logging
    logger = setup_logging()
    
    print("Testing MessageBus...")
    
    bus = MessageBus()
    
    # Test subscription
    received_messages = []
    
    def callback(msg):
        received_messages.append(msg)
        print(f"  Received: {msg.sender} -> {msg.receiver}: {msg.content}")
    
    bus.subscribe('agent_b', callback)
    
    # Test message publishing
    message = AgentMessage(
        sender='agent_a',
        receiver='agent_b',
        message_type=MessageType.REQUEST,
        content={'action': 'test', 'data': 'hello'}
    )
    
    bus.publish(message)
    
    assert len(received_messages) == 1
    print(f"\n✅ MessageBus test complete! ({len(received_messages)} message received)")

