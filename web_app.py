"""
ProFlow Agent - Flask Web Dashboard

Provides web interface for monitoring and controlling the ProFlow system.
"""

from flask import Flask, render_template, request, jsonify
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from workflows.orchestrator import ProFlowOrchestrator
from data import read_emails_from_csv, read_calendar_from_json
from workflows.async_orchestrator import AsyncOrchestrator
from services.weather_service import WeatherService
import asyncio

app = Flask(__name__)
app.secret_key = 'proflow-secret-key-2024'

# Initialize components
orchestrator = ProFlowOrchestrator(enable_logging=False)  # Reduce console noise
async_orchestrator = AsyncOrchestrator()
weather_service = WeatherService()


@app.route('/')
def index():
    """Main dashboard"""
    return render_template('index.html')


@app.route('/api/briefing', methods=['GET'])
def get_briefing():
    """Get daily briefing"""
    try:
        # Load data
        emails = read_emails_from_csv()
        calendar = read_calendar_from_json()
        
        # Get weather
        weather = weather_service.get_weather()
        
        # Generate briefing
        briefing = orchestrator.generate_daily_briefing(emails, calendar)
        
        return jsonify({
            'status': 'success',
            'briefing': briefing,
            'email_count': len(emails),
            'meeting_count': len(calendar),
            'weather': weather,
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/emails', methods=['GET'])
def get_emails():
    """Get email analysis"""
    try:
        emails = read_emails_from_csv()
        
        # Process emails using orchestrator
        results = []
        for email in emails:
            # Use orchestrator's email analysis
            classification = orchestrator.email_tools.classify_email_priority(
                subject=email.get('subject', ''),
                sender=email.get('from', ''),
                body=email.get('body', '')
            )
            results.append({
                'email': email,
                'analysis': classification
            })
        
        return jsonify({
            'status': 'success',
            'emails': results,
            'count': len(results)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/performance', methods=['GET'])
def get_performance():
    """Get performance metrics"""
    try:
        emails = read_emails_from_csv()
        
        if len(emails) == 0:
            return jsonify({
                'status': 'error',
                'message': 'No emails to process'
            }), 400
        
        # Time sequential
        start = time.time()
        seq_results = []
        for email in emails:
            classification = orchestrator.email_tools.classify_email_priority(
                subject=email.get('subject', ''),
                sender=email.get('from', ''),
                body=email.get('body', '')
            )
            seq_results.append(classification)
            time.sleep(0.1)  # Simulate processing time
        seq_time = time.time() - start
        
        # Time parallel
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        start = time.time()
        par_results = loop.run_until_complete(
            async_orchestrator.process_emails_parallel(emails)
        )
        par_time = time.time() - start
        loop.close()
        
        speedup = seq_time / par_time if par_time > 0 else 1.0
        
        return jsonify({
            'status': 'success',
            'sequential_time': round(seq_time, 3),
            'parallel_time': round(par_time, 3),
            'speedup': round(speedup, 2),
            'email_count': len(emails)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/messages', methods=['GET'])
def get_messages():
    """Get agent message history"""
    try:
        message_file = Path('data/agent_messages.json')
        if message_file.exists():
            with open(message_file, 'r', encoding='utf-8') as f:
                messages = json.load(f)
        else:
            messages = []
        
        return jsonify({
            'status': 'success',
            'messages': messages[-50:],  # Last 50 messages
            'count': len(messages)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


@app.route('/api/weather', methods=['GET'])
def get_weather():
    """Get weather information"""
    try:
        city = request.args.get('city', 'Denver')
        weather = weather_service.get_weather(city)
        
        return jsonify({
            'status': 'success',
            'weather': weather
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    # Create templates directory if it doesn't exist
    templates_dir = Path('templates')
    templates_dir.mkdir(exist_ok=True)
    
    print("="*70)
    print("ProFlow Agent - Web Dashboard")
    print("="*70)
    print("\nStarting Flask server...")
    print("Open http://localhost:5000 in your browser")
    print("\nPress Ctrl+C to stop\n")
    
    app.run(debug=True, port=5000, host='0.0.0.0')

