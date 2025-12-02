"""
Tests for Base Agent class.
"""

import unittest
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from agents.base_agent import BaseAgent
from messaging.message_bus import AgentMessage, MessageType


class TestBaseAgent(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures"""
        self.agent = BaseAgent('test_agent')
    
    def test_agent_initialization(self):
        """Test agent is properly initialized"""
        self.assertEqual(self.agent.name, 'test_agent')
        self.assertIsNotNone(self.agent.message_bus)
        self.assertIsNotNone(self.agent.logger)
    
    def test_send_message(self):
        """Test sending messages"""
        received = []
        
        def callback(msg):
            received.append(msg)
        
        # Subscribe another agent
        self.agent.message_bus.subscribe('receiver_agent', callback)
        
        # Send message
        self.agent.send_message(
            receiver='receiver_agent',
            message_type=MessageType.REQUEST,
            content={'test': 'data'}
        )
        
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].sender, 'test_agent')
        self.assertEqual(received[0].receiver, 'receiver_agent')
        self.assertEqual(received[0].content['test'], 'data')
    
    def test_broadcast(self):
        """Test broadcasting messages"""
        received = []
        
        def callback(msg):
            received.append(msg)
        
        self.agent.message_bus.subscribe('other_agent', callback)
        
        self.agent.broadcast({'announcement': 'test'})
        
        self.assertEqual(len(received), 1)
        self.assertEqual(received[0].receiver, 'ALL')
        self.assertEqual(received[0].content['announcement'], 'test')
    
    def test_process_request(self):
        """Test processing requests"""
        response = self.agent.process_request({'action': 'test'})
        
        self.assertIn('status', response)
        self.assertIn('agent', response)
        self.assertEqual(response['agent'], 'test_agent')


if __name__ == '__main__':
    unittest.main()

