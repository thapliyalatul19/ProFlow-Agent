"""
Calendar data reader for ProFlow Agent.

Reads calendar events from JSON files.
"""

import json
import os
from typing import List, Dict
from pathlib import Path


def read_calendar_from_json(json_path: str = None) -> List[Dict]:
    """
    Read calendar events from a JSON file.
    
    Expected JSON format:
    [
        {
            "summary": "Meeting title",
            "start": "09:00" or "2024-11-20T09:00:00",
            "end": "10:00" or "2024-11-20T10:00:00",
            "duration_minutes": 60,
            "type": "meeting" or "personal" or "focus",
            "attendees": ["person1@example.com", "Person Name"]
        },
        ...
    ]
    
    Args:
        json_path: Path to JSON file. If None, uses default data/calendar.json
        
    Returns:
        List of calendar event dictionaries
    """
    if json_path is None:
        # Default to data/calendar.json relative to project root
        project_root = Path(__file__).parent.parent.parent
        json_path = project_root / "data" / "calendar.json"
    
    # Convert to Path object if string
    if isinstance(json_path, str):
        json_path = Path(json_path)
    
    if not json_path.exists():
        raise FileNotFoundError(f"Calendar JSON file not found: {json_path}")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            events = json.load(f)
    
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in calendar file {json_path}: {str(e)}")
    except Exception as e:
        raise IOError(f"Error reading calendar JSON file {json_path}: {str(e)}")
    
    # Validate that it's a list
    if not isinstance(events, list):
        raise ValueError(f"Calendar JSON must contain a list of events, got {type(events)}")
    
    return events

