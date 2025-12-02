"""
Messaging system for ProFlow Agent.

Provides agent-to-agent communication via message bus.
"""

from .message_bus import MessageBus, AgentMessage, MessageType, message_bus

__all__ = ['MessageBus', 'AgentMessage', 'MessageType', 'message_bus']

