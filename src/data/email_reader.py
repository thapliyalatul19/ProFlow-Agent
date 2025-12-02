"""
Email data reader for ProFlow Agent.

Reads email data from CSV files.
"""

import csv
import os
from typing import List, Dict
from pathlib import Path


def read_emails_from_csv(csv_path: str = None) -> List[Dict]:
    """
    Read emails from a CSV file.
    
    Expected CSV format:
    - subject: Email subject line
    - from: Sender email address
    - body: Email body content
    - timestamp: Optional timestamp (ISO format or readable date)
    
    Args:
        csv_path: Path to CSV file. If None, uses default data/sample_emails.csv
        
    Returns:
        List of email dictionaries with keys: subject, from, body, timestamp
    """
    if csv_path is None:
        # Default to data/sample_emails.csv relative to project root
        project_root = Path(__file__).parent.parent.parent
        csv_path = project_root / "data" / "sample_emails.csv"
    
    # Convert to Path object if string
    if isinstance(csv_path, str):
        csv_path = Path(csv_path)
    
    if not csv_path.exists():
        raise FileNotFoundError(f"Email CSV file not found: {csv_path}")
    
    emails = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            for row in reader:
                # Normalize column names (handle case variations)
                email = {
                    'subject': row.get('subject', row.get('Subject', '')),
                    'from': row.get('from', row.get('From', row.get('sender', ''))),
                    'body': row.get('body', row.get('Body', row.get('content', ''))),
                    'timestamp': row.get('timestamp', row.get('Timestamp', row.get('date', '')))
                }
                
                # Only add if we have at least subject and from
                if email['subject'] or email['from']:
                    emails.append(email)
    
    except Exception as e:
        raise IOError(f"Error reading email CSV file {csv_path}: {str(e)}")
    
    return emails

