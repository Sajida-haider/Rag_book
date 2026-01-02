"""Service for detecting changes in book content"""

import hashlib
from typing import Dict, List, Optional
from datetime import datetime
import json
import sys
import os
# Add the backend directory to path for imports
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, backend_dir)

from models import BookContent


class ChangeDetectorService:
    def __init__(self):
        self.content_hashes = {}

    def calculate_content_hash(self, content: str) -> str:
        """Calculate hash of content to detect changes"""
        return hashlib.md5(content.encode('utf-8')).hexdigest()

    def get_content_fingerprint(self, book_content: BookContent) -> str:
        """Create a fingerprint of the content for comparison"""
        content_data = {
            'url': book_content.url,
            'title': book_content.title,
            'content': book_content.content,
            'section': book_content.section
        }
        content_str = json.dumps(content_data, sort_keys=True)
        return self.calculate_content_hash(content_str)

    def detect_changes(self, current_content: List[BookContent],
                      previous_content_hashes: Dict[str, str]) -> Dict[str, str]:
        """Detect which content items have changed"""
        changes = {
            'added': [],
            'modified': [],
            'removed': []
        }

        current_hashes = {}
        current_urls = set()

        # Calculate hashes for current content
        for content in current_content:
            fingerprint = self.get_content_fingerprint(content)
            current_hashes[content.url] = fingerprint
            current_urls.add(content.url)

        # Identify previous URLs
        previous_urls = set(previous_content_hashes.keys())

        # Find added content (in current but not in previous)
        added_urls = current_urls - previous_urls
        for url in added_urls:
            changes['added'].append(url)

        # Find removed content (in previous but not in current)
        removed_urls = previous_urls - current_urls
        for url in removed_urls:
            changes['removed'].append(url)

        # Find modified content (same URL but different hash)
        common_urls = current_urls.intersection(previous_urls)
        for url in common_urls:
            current_hash = current_hashes[url]
            previous_hash = previous_content_hashes[url]

            if current_hash != previous_hash:
                changes['modified'].append(url)

        return changes

    def has_content_changed(self, book_content: BookContent,
                          previous_hash: Optional[str] = None) -> bool:
        """Check if a specific content item has changed"""
        current_fingerprint = self.get_content_fingerprint(book_content)

        if previous_hash is None:
            return True  # If no previous hash, consider it changed

        return current_fingerprint != previous_hash

    def store_content_hashes(self, content_list: List[BookContent]) -> Dict[str, str]:
        """Store hashes of content for future comparison"""
        hashes = {}
        for content in content_list:
            hashes[content.url] = self.get_content_fingerprint(content)
        return hashes

    def save_hashes_to_file(self, hashes: Dict[str, str], filepath: str):
        """Save content hashes to a file for persistence"""
        with open(filepath, 'w') as f:
            json.dump(hashes, f, indent=2)

    def load_hashes_from_file(self, filepath: str) -> Dict[str, str]:
        """Load content hashes from a file"""
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}  # Return empty dict if file doesn't exist