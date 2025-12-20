# Chatbot Widget Component

A floating chatbot widget that appears on all pages of the Docusaurus book, positioned at the bottom-left corner and labeled "Ask the Book".

## Features

- Floating button that toggles a chat interface
- Responsive design for mobile and desktop
- Matches the book's theme colors
- Input field with send functionality (placeholder only)
- Console logging of user inputs
- Accessible with proper ARIA labels

## Implementation Details

- Uses Docusaurus' Root component override to appear on all pages
- Implements BrowserOnly to prevent server-side rendering issues
- Uses CSS modules for styling with theme support
- Includes mobile-responsive design with media queries

## Placeholders

This component is a frontend-only placeholder. Future implementation will include:
- RAG backend integration
- Actual book content search and retrieval
- AI-powered responses