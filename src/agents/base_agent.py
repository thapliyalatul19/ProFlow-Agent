"""
Base Agent class with messaging capability.

All agents inherit from this to enable inter-agent communication.
"""

import logging
from typing import Dict
from messaging.message_bus import message_bus, AgentMessage, MessageType


class BaseAgent:
    """Base class for all agents with messaging capability"""
    
    def __init__(self, name: str):
        """
        Initialize base agent.
        
        Args:
            name: Agent name (used for messaging)
        """
        self.name = name
        self.message_bus = message_bus
        self.message_bus.subscribe(name, self.handle_message)
        self.logger = logging.getLogger(name)
        self.logger.info(f"Agent '{name}' initialized with messaging")
    
    def handle_message(self, message: AgentMessage):
        """
        Handle incoming messages.
        
        Args:
            message: Incoming AgentMessage
        """
        self.logger.info(f"Received message from {message.sender}: {message.message_type.value}")
        
        if message.message_type == MessageType.REQUEST:
            response = self.process_request(message.content)
            self.send_message(
                receiver=message.sender,
                message_type=MessageType.RESPONSE,
                content=response
            )
        elif message.message_type == MessageType.BROADCAST:
            self.process_broadcast(message.content)
    
    def send_message(self, receiver: str, message_type: MessageType, content: Dict):
        """
        Send message to another agent.
        
        Args:
            receiver: Receiver agent name
            message_type: Type of message
            content: Message content dictionary
        """
        message = AgentMessage(
            sender=self.name,
            receiver=receiver,
            message_type=message_type,
            content=content
        )
        self.message_bus.publish(message)
    
    def broadcast(self, content: Dict):
        """
        Broadcast message to all agents.
        
        Args:
            content: Message content dictionary
        """
        message = AgentMessage(
            sender=self.name,
            receiver="ALL",
            message_type=MessageType.BROADCAST,
            content=content
        )
        self.message_bus.publish(message)
    
    def process_request(self, content: Dict) -> Dict:
        """
        Process incoming request. Override in subclasses.
        
        Args:
            content: Request content
        
        Returns:
            Response dictionary
        """
        self.logger.debug(f"Processing request: {content}")
        return {"status": "received", "agent": self.name}
    
    def process_broadcast(self, content: Dict):
        """
        Process broadcast message. Override in subclasses.
        
        Args:
            content: Broadcast content
        """
        self.logger.debug(f"Processing broadcast: {content}")

