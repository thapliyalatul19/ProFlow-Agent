"""
Tests for Message Bus - Agent-to-Agent Communication.
"""

import unittest
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from messaging.message_bus import MessageBus, AgentMessage, MessageType


class TestMessageBus(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.bus = MessageBus()
        # Clear subscribers for clean test
        self.bus.subscribers = {}
        self.bus.message_history = []
    
    def test_subscribe(self):
        """Test agent subscription"""
        def dummy_callback(msg):
            pass
        
        self.bus.subscribe('test_agent', dummy_callback)
        self.assertIn('test_agent', self.bus.subscribers)
        self.assertEqual(len(self.bus.subscribers['test_agent']), 1)
    
    def test_publish_message(self):
        """Test message publishing"""
        received = []
        
        def callback(msg):
            received.append(msg)
        
        self.bus.subscribe('receiver', callback)
        
        message = AgentMessage(
            sender='sender',
            receiver='receiver',
            message_type=MessageType.REQUEST,
            content={'test': 'data'}
        )
        
        self.bus.publish(message)
        
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].content['test'], 'data')
        self.assertEqual(received[0].sender, 'sender')
        self.assertEqual(received[0].receiver, 'receiver')
    
    def test_broadcast(self):
        """Test broadcast to all agents"""
        received_a = []
        received_b = []
        
        self.bus.subscribe('agent_a', lambda m: received_a.append(m))
        self.bus.subscribe('agent_b', lambda m: received_b.append(m))
        
        message = AgentMessage(
            sender='broadcaster',
            receiver='ALL',
            message_type=MessageType.BROADCAST,
            content={'announcement': 'test'}
        )
        
        self.bus.publish(message)
        
        self.assertEqual(len(received_a), 1)
        self.assertEqual(len(received_b), 1)
        self.assertEqual(received_a[0].content['announcement'], 'test')
        self.assertEqual(received_b[0].content['announcement'], 'test')
    
    def test_message_history(self):
        """Test message history tracking"""
        message = AgentMessage(
            sender='test1',
            receiver='test2',
            message_type=MessageType.REQUEST,
            content={'data': 'test'}
        )
        
        self.bus.publish(message)
        
        history = self.bus.get_conversation('test1', 'test2')
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].sender, 'test1')
        self.assertEqual(history[0].receiver, 'test2')
    
    def test_agent_message_creation(self):
        """Test AgentMessage dataclass"""
        message = AgentMessage(
            sender='agent1',
            receiver='agent2',
            message_type=MessageType.REQUEST,
            content={'key': 'value'}
        )
        
        self.assertIsNotNone(message.timestamp)
        self.assertIsNotNone(message.message_id)
        self.assertEqual(message.sender, 'agent1')
        self.assertEqual(message.receiver, 'agent2')
        
        # Test to_dict
        msg_dict = message.to_dict()
        self.assertEqual(msg_dict['sender'], 'agent1')
        self.assertEqual(msg_dict['message_type'], 'request')


if __name__ == '__main__':
    unittest.main()

