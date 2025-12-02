"""
Session Manager for ProFlow Agent - State Persistence

Manages session state, caching, and history tracking with JSON file persistence.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import hashlib


class SessionManager:
    """
    Manages session state with file persistence.
    
    Handles:
    - Session data loading/saving
    - Action history tracking
    - Result caching
    - Processed item tracking
    """
    
    def __init__(self, session_file: str = None):
        """
        Initialize SessionManager.
        
        Args:
            session_file: Path to session JSON file. Defaults to data/session.json
        """
        if session_file is None:
            # Default to data/session.json relative to project root
            project_root = Path(__file__).parent.parent.parent
            session_file = project_root / "data" / "session.json"
        
        if isinstance(session_file, str):
            session_file = Path(session_file)
        
        self.session_file = session_file
        self.session_data = {
            'session_id': None,
            'created_at': None,
            'last_updated': None,
            'processed_emails': {},  # email_id -> analysis_result
            'cache': {},  # cache_key -> cached_result
            'history': []  # List of all actions with timestamps
        }
    
    def load_session(self) -> Dict:
        """
        Load existing session or create new one.
        
        Returns:
            Session data dictionary
        """
        if self.session_file.exists():
            try:
                with open(self.session_file, 'r', encoding='utf-8') as f:
                    self.session_data = json.load(f)
                
                # Ensure all required keys exist
                if 'processed_emails' not in self.session_data:
                    self.session_data['processed_emails'] = {}
                if 'cache' not in self.session_data:
                    self.session_data['cache'] = {}
                if 'history' not in self.session_data:
                    self.session_data['history'] = []
                
                self._add_to_history('session_loaded', {
                    'session_id': self.session_data.get('session_id'),
                    'loaded_at': datetime.now().isoformat()
                })
                
                return self.session_data
            
            except (json.JSONDecodeError, IOError) as e:
                print(f"⚠️  Error loading session: {e}. Creating new session.")
                self._create_new_session()
                return self.session_data
        else:
            # Create new session
            self._create_new_session()
            return self.session_data
    
    def _create_new_session(self):
        """Create a new session with unique ID."""
        session_id = f"session_{int(datetime.now().timestamp())}"
        self.session_data = {
            'session_id': session_id,
            'created_at': datetime.now().isoformat(),
            'last_updated': datetime.now().isoformat(),
            'processed_emails': {},
            'cache': {},
            'history': []
        }
        self._add_to_history('session_created', {
            'session_id': session_id,
            'created_at': self.session_data['created_at']
        })
        self.save_session()
    
    def save_session(self) -> bool:
        """
        Write session data to disk.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            # Ensure directory exists
            self.session_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Update last_updated timestamp
            self.session_data['last_updated'] = datetime.now().isoformat()
            
            # Write to file with pretty formatting
            with open(self.session_file, 'w', encoding='utf-8') as f:
                json.dump(self.session_data, f, indent=2, ensure_ascii=False)
            
            return True
        
        except IOError as e:
            print(f"❌ Error saving session: {e}")
            return False
    
    def add_to_history(self, action: str, details: Dict = None, result: Any = None):
        """
        Track an action in the history log.
        
        Args:
            action: Action name (e.g., 'email_processed', 'cache_hit')
            details: Additional details about the action
            result: Optional result data
        """
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details or {},
            'result': result
        }
        
        self.session_data['history'].append(history_entry)
        
        # Keep history size manageable (last 1000 entries)
        if len(self.session_data['history']) > 1000:
            self.session_data['history'] = self.session_data['history'][-1000:]
        
        # Auto-save after adding to history
        self.save_session()
    
    def _add_to_history(self, action: str, details: Dict = None, result: Any = None):
        """Internal method to add to history without auto-save (to avoid recursion)."""
        history_entry = {
            'timestamp': datetime.now().isoformat(),
            'action': action,
            'details': details or {},
            'result': result
        }
        
        self.session_data['history'].append(history_entry)
        
        # Keep history size manageable
        if len(self.session_data['history']) > 1000:
            self.session_data['history'] = self.session_data['history'][-1000:]
    
    def cache_result(self, key: str, value: Any, metadata: Dict = None):
        """
        Cache a result for later retrieval.
        
        Args:
            key: Cache key (should be unique)
            value: Value to cache
            metadata: Optional metadata about the cached value
        """
        cache_entry = {
            'value': value,
            'cached_at': datetime.now().isoformat(),
            'metadata': metadata or {}
        }
        
        self.session_data['cache'][key] = cache_entry
        self.add_to_history('cache_set', {
            'key': key,
            'metadata': metadata
        })
    
    def get_cached_result(self, key: str) -> Optional[Any]:
        """
        Retrieve a cached result.
        
        Args:
            key: Cache key
        
        Returns:
            Cached value if found, None otherwise
        """
        if key in self.session_data['cache']:
            cache_entry = self.session_data['cache'][key]
            self.add_to_history('cache_hit', {
                'key': key,
                'cached_at': cache_entry.get('cached_at')
            })
            return cache_entry['value']
        
        self.add_to_history('cache_miss', {'key': key})
        return None
    
    def mark_email_processed(self, email_id: str, analysis_result: Dict):
        """
        Mark an email as processed and store its analysis result.
        
        Args:
            email_id: Unique identifier for the email
            analysis_result: Analysis result dictionary
        """
        self.session_data['processed_emails'][email_id] = {
            'analysis': analysis_result,
            'processed_at': datetime.now().isoformat()
        }
        
        self.add_to_history('email_processed', {
            'email_id': email_id,
            'subject': analysis_result.get('subject', 'Unknown')
        })
    
    def is_email_processed(self, email_id: str) -> bool:
        """
        Check if an email has already been processed.
        
        Args:
            email_id: Unique identifier for the email
        
        Returns:
            True if email was processed, False otherwise
        """
        return email_id in self.session_data['processed_emails']
    
    def get_email_analysis(self, email_id: str) -> Optional[Dict]:
        """
        Get cached analysis result for an email.
        
        Args:
            email_id: Unique identifier for the email
        
        Returns:
            Analysis result if found, None otherwise
        """
        if email_id in self.session_data['processed_emails']:
            return self.session_data['processed_emails'][email_id]['analysis']
        return None
    
    def get_history(self, action_filter: str = None, limit: int = None) -> List[Dict]:
        """
        Get action history, optionally filtered.
        
        Args:
            action_filter: Optional action name to filter by
            limit: Optional limit on number of entries to return
        
        Returns:
            List of history entries
        """
        history = self.session_data['history']
        
        if action_filter:
            history = [h for h in history if h['action'] == action_filter]
        
        if limit:
            history = history[-limit:]
        
        return history
    
    def get_session_stats(self) -> Dict:
        """
        Get statistics about the current session.
        
        Returns:
            Dictionary with session statistics
        """
        return {
            'session_id': self.session_data.get('session_id'),
            'created_at': self.session_data.get('created_at'),
            'last_updated': self.session_data.get('last_updated'),
            'emails_processed': len(self.session_data.get('processed_emails', {})),
            'cache_entries': len(self.session_data.get('cache', {})),
            'history_entries': len(self.session_data.get('history', []))
        }
    
    @staticmethod
    def generate_email_id(email: Dict) -> str:
        """
        Generate a unique ID for an email based on its content.
        
        Args:
            email: Email dictionary with subject, from, body
        
        Returns:
            Unique email ID (hash of subject + from + timestamp)
        """
        # Create hash from email content
        content = f"{email.get('subject', '')}{email.get('from', '')}{email.get('timestamp', '')}"
        email_hash = hashlib.md5(content.encode('utf-8')).hexdigest()[:12]
        return f"email_{email_hash}"


# Example usage
if __name__ == "__main__":
    print("Testing SessionManager...")
    
    # Create session manager
    manager = SessionManager()
    
    # Load or create session
    session = manager.load_session()
    print(f"\n✓ Session loaded: {session['session_id']}")
    
    # Test caching
    manager.cache_result('test_key', {'result': 'test_value'}, {'source': 'test'})
    cached = manager.get_cached_result('test_key')
    print(f"✓ Cache test: {cached}")
    
    # Test email processing
    test_email = {
        'subject': 'Test Email',
        'from': 'test@example.com',
        'body': 'Test body'
    }
    email_id = manager.generate_email_id(test_email)
    manager.mark_email_processed(email_id, {'subject': 'Test Email', 'priority': 'high'})
    print(f"✓ Email marked as processed: {email_id}")
    
    # Get stats
    stats = manager.get_session_stats()
    print(f"\n📊 Session Stats:")
    print(f"   Emails processed: {stats['emails_processed']}")
    print(f"   Cache entries: {stats['cache_entries']}")
    print(f"   History entries: {stats['history_entries']}")
    
    print("\n✅ SessionManager test complete!")

