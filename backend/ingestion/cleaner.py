import re
from typing import List, Tuple
import logging
from markdown import markdown
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)

class ContentCleaner:
    """
    Module to clean markdown content while preserving hierarchy
    """

    def __init__(self):
        pass

    def clean_content(self, content: str) -> str:
        """
        Remove unnecessary formatting and HTML tags while preserving headings hierarchy
        """
        # Remove HTML comments
        content = re.sub(r'<!--.*?-->', '', content, flags=re.DOTALL)

        # Remove script and style tags if any
        content = re.sub(r'<script.*?</script>', '', content, flags=re.DOTALL | re.IGNORECASE)
        content = re.sub(r'<style.*?</style>', '', content, flags=re.DOTALL | re.IGNORECASE)

        # Remove Docusaurus-specific JSX comments and metadata
        content = re.sub(r'^---\n.*?\n---\n?', '', content, flags=re.DOTALL)  # Frontmatter

        # Remove code block comments
        content = re.sub(r'//.*?$', '', content, flags=re.MULTILINE)

        # Remove extra whitespace while preserving paragraph structure
        content = re.sub(r'\n\s*\n', '\n\n', content)  # Multiple newlines to double newlines
        content = re.sub(r'^\s+', '', content, flags=re.MULTILINE)  # Leading whitespace

        # Clean up extra spaces
        content = re.sub(r' +', ' ', content)

        logger.debug(f"Cleaned content from {len(content)} characters")
        return content.strip()

    def extract_headings_hierarchy(self, content: str) -> List[Tuple[int, str]]:
        """
        Extract headings hierarchy from markdown content
        Returns a list of (level, heading_text) tuples
        """
        # Find markdown headings (supports #, ##, ###, etc.)
        heading_pattern = r'^(#{1,6})\s+(.+)$'
        lines = content.split('\n')

        headings = []
        for line in lines:
            match = re.match(heading_pattern, line.strip())
            if match:
                level = len(match.group(1))  # Number of # symbols
                text = match.group(2).strip()
                headings.append((level, text))

        logger.debug(f"Extracted {len(headings)} headings from content")
        return headings

    def preserve_headings_hierarchy(self, content: str) -> str:
        """
        Process content while ensuring headings hierarchy is preserved
        """
        # This method would process the content in a way that maintains
        # the relationship between headings and their content
        # For now, we'll just ensure the content is clean but headings are preserved
        return self.clean_content(content)

    def remove_unnecessary_elements(self, content: str) -> str:
        """
        Remove unnecessary formatting, scripts, or HTML tags
        """
        # Convert markdown to HTML temporarily to use BeautifulSoup for cleaning
        try:
            html = markdown(content)
            soup = BeautifulSoup(html, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text content
            text = soup.get_text()

            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)

            return text
        except Exception as e:
            logger.warning(f"Could not convert markdown to HTML for cleaning: {e}")
            # If markdown conversion fails, fall back to regex cleaning
            return self.clean_content(content)

    def process_content(self, content: str) -> Tuple[str, List[Tuple[int, str]]]:
        """
        Process content by cleaning and extracting headings hierarchy
        Returns cleaned content and headings hierarchy
        """
        headings = self.extract_headings_hierarchy(content)
        cleaned_content = self.preserve_headings_hierarchy(content)

        logger.info(f"Processed content: {len(headings)} headings preserved, {len(cleaned_content)} characters cleaned")
        return cleaned_content, headings

# Example usage
if __name__ == "__main__":
    cleaner = ContentCleaner()

    sample_content = """
# Introduction

This is the introduction to the book.

## Chapter 1

Some content for chapter 1.

### Section 1.1

Detailed content here.

## Chapter 2

More content for chapter 2.
"""

    cleaned, headings = cleaner.process_content(sample_content)

    print(f"Cleaned content length: {len(cleaned)} characters")
    print(f"Headings hierarchy:")
    for level, text in headings:
        print(f"  {'#' * level} {text}")