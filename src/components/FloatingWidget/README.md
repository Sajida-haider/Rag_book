# Floating Widget Component

This component implements a floating chatbot widget that appears on all pages in the Docusaurus site. The widget is positioned at the bottom-left corner and provides an AI assistant interface.

## Implementation Details

- **Location**: `src/components/FloatingWidget/`
- **Global Integration**: Using Docusaurus `Root` theme component
- **Position**: Fixed position at bottom-left of the viewport
- **State Management**: React hooks for open/close state
- **Styling**: CSS modules with dark mode support
- **Accessibility**: Proper ARIA labels and keyboard navigation

## Docusaurus Integration Pattern

The component is integrated globally using the Docusaurus theme override pattern:

1. **Root Component Override**: `src/theme/Root/index.tsx` renders the widget on all pages
2. **BrowserOnly Wrapper**: Prevents SSR issues by only rendering on the client
3. **CSS Modules**: Scoped styling with theme support

## Features

- Toggle open/close functionality
- Responsive design for mobile devices
- Dark/light mode support matching the site theme
- Accessible interface elements
- Clean, modern UI design

## Files

- `FloatingWidget.tsx`: Main component implementation
- `FloatingWidget.module.css`: Component-specific styles
- `Root/index.tsx`: Global integration in Docusaurus theme