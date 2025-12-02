"""
Tests for Flask Web Application.
"""

import unittest
import json
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from web_app import app


class TestWebApp(unittest.TestCase):
    
    def setUp(self):
        """Set up test client"""
        self.app = app.test_client()
        self.app.testing = True
    
    def test_index_page(self):
        """Test main page loads"""
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'ProFlow Executive Agent', response.data)
    
    def test_briefing_api(self):
        """Test briefing API endpoint"""
        response = self.app.get('/api/briefing')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('briefing', data)
        self.assertIn('email_count', data)
        self.assertIn('meeting_count', data)
    
    def test_performance_api(self):
        """Test performance API endpoint"""
        response = self.app.get('/api/performance')
        
        # May return 200 or 400 (if no emails)
        self.assertIn(response.status_code, [200, 400])
        
        data = json.loads(response.data)
        if response.status_code == 200:
            self.assertEqual(data['status'], 'success')
            self.assertIn('sequential_time', data)
            self.assertIn('parallel_time', data)
            self.assertIn('speedup', data)
    
    def test_messages_api(self):
        """Test messages API endpoint"""
        response = self.app.get('/api/messages')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('messages', data)
        self.assertIn('count', data)
    
    def test_weather_api(self):
        """Test weather API endpoint"""
        response = self.app.get('/api/weather')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('weather', data)
        self.assertIn('city', data['weather'])
        self.assertIn('temperature', data['weather'])
    
    def test_weather_api_with_city(self):
        """Test weather API with city parameter"""
        response = self.app.get('/api/weather?city=New York')
        self.assertEqual(response.status_code, 200)
        
        data = json.loads(response.data)
        self.assertEqual(data['status'], 'success')
        self.assertIn('weather', data)


if __name__ == '__main__':
    unittest.main()

