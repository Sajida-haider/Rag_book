import os
import glob
from typing import List, Dict, Tuple
import logging

logger = logging.getLogger(__name__)

class ContentReader:
    """
    Module to read and parse markdown files from the book directory
    """

    def __init__(self, book_path: str = "book/"):
        self.book_path = book_path

    def list_markdown_files(self) -> List[str]:
        """
        List all markdown files in the book directory and subdirectories
        """
        pattern = os.path.join(self.book_path, "**/*.md")
        files = glob.glob(pattern, recursive=True)

        # Also look for .mdx files which are also used in Docusaurus
        mdx_pattern = os.path.join(self.book_path, "**/*.mdx")
        mdx_files = glob.glob(mdx_pattern, recursive=True)

        all_files = files + mdx_files
        logger.info(f"Found {len(all_files)} markdown files in {self.book_path}")
        return all_files

    def map_to_modules_chapters(self, file_paths: List[str]) -> List[Dict]:
        """
        Map file paths to module and chapter names based on directory structure
        """
        mappings = []

        for file_path in file_paths:
            # Extract directory structure to determine module/chapter
            rel_path = os.path.relpath(file_path, self.book_path)
            path_parts = rel_path.split(os.sep)

            # Module is typically the first directory, chapter is the filename
            if len(path_parts) >= 2:
                module = path_parts[0] or "root"
                chapter = path_parts[-1].replace('.md', '').replace('.mdx', '')
            else:
                module = "root"
                chapter = path_parts[-1].replace('.md', '').replace('.mdx', '')

            mapping = {
                "file_path": file_path,
                "module": module,
                "chapter": chapter,
                "relative_path": rel_path
            }
            mappings.append(mapping)

        logger.info(f"Mapped {len(mappings)} files to modules and chapters")
        return mappings

    def read_file_content(self, file_path: str) -> str:
        """
        Read content from a markdown file
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                logger.debug(f"Read {len(content)} characters from {file_path}")
                return content
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            return ""

    def get_content_manifest(self) -> List[Dict]:
        """
        Create a manifest of files to be processed with their metadata mappings
        """
        files = self.list_markdown_files()
        mappings = self.map_to_modules_chapters(files)
        return mappings

# Example usage
if __name__ == "__main__":
    reader = ContentReader()
    manifest = reader.get_content_manifest()

    print(f"Found {len(manifest)} files:")
    for item in manifest[:5]:  # Print first 5 for demo
        print(f"  - {item['relative_path']} -> Module: {item['module']}, Chapter: {item['chapter']}")