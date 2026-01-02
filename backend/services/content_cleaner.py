"""Service for cleaning and preprocessing extracted content"""

import re
from typing import List, Tuple


class ContentCleanerService:
    def __init__(self):
        pass

    def clean_content(self, content: str) -> str:
        """Clean and preprocess extracted content"""
        if not content:
            return ""

        # Remove extra whitespace and normalize
        content = re.sub(r'\s+', ' ', content)

        # Remove special characters but keep punctuation
        content = re.sub(r'[^\w\s\.\!\?,:;\'\"-]', ' ', content)

        # Normalize whitespace
        content = ' '.join(content.split())

        return content.strip()

    def clean_multiple_contents(self, contents: List[str]) -> List[str]:
        """Clean multiple content strings"""
        return [self.clean_content(content) for content in contents]

    def remove_boilerplate(self, content: str) -> str:
        """Remove common boilerplate text from content"""
        if not content:
            return ""

        # Common patterns to remove
        patterns_to_remove = [
            r'copyright \d{4}.*?(?=\n|$)',  # Copyright notices
            r'privacy policy.*?(?=\n|$)',    # Privacy policy mentions
            r'terms of service.*?(?=\n|$)', # Terms of service mentions
            r'all rights reserved.*?(?=\n|$)', # Rights reserved statements
        ]

        for pattern in patterns_to_remove:
            content = re.sub(pattern, '', content, flags=re.IGNORECASE)

        # Clean up multiple newlines and spaces
        content = re.sub(r'\n\s*\n', '\n\n', content)
        content = content.strip()

        return content

    def preprocess_for_embedding(self, content: str) -> str:
        """Preprocess content specifically for embedding generation"""
        # First clean the content
        cleaned = self.clean_content(content)

        # Then remove boilerplate
        cleaned = self.remove_boilerplate(cleaned)

        # Ensure content is not too short
        if len(cleaned) < 10:
            return ""

        return cleaned

    def clean_and_validate(self, content: str) -> Tuple[str, bool]:
        """Clean content and return whether it's valid for processing"""
        cleaned = self.preprocess_for_embedding(content)

        # Check if content is valid (not empty and has sufficient length - at least 50 characters)
        is_valid = len(cleaned) >= 50 and bool(cleaned.strip())

        return cleaned, is_valid