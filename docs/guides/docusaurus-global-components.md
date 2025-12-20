# Docusaurus Global UI Component Implementation Guide

This document outlines the patterns and approaches used for implementing global UI components in the Docusaurus site, specifically for the floating chatbot widget.

## Recommended Docusaurus Patterns for Global Components

### 1. Theme Component Override Pattern

The preferred approach for adding global UI elements is to use Docusaurus theme component overrides:

- **Root Component**: Override `src/theme/Root/index.tsx` to add components that appear on every page
- **Layout Component**: Override `src/theme/Layout/index.tsx` to wrap the entire page layout
- **Use BrowserOnly**: Wrap client-side components to avoid SSR issues

### 2. Component Structure

```
src/
├── components/
│   └── FloatingWidget/
│       ├── FloatingWidget.tsx
│       ├── FloatingWidget.module.css
│       └── README.md
└── theme/
    └── Root/
        └── index.tsx
```

### 3. Best Practices

- Use CSS modules for scoped styling
- Implement responsive design considerations
- Support both light and dark themes
- Add proper accessibility attributes
- Use BrowserOnly for client-side only components
- Maintain performance by minimizing global component complexity

### 4. Floating Widget Specific Implementation

The floating chatbot widget implements these patterns by:

- Creating a self-contained component with its own styles
- Using the Root theme override to appear on all pages
- Implementing proper state management for open/close functionality
- Including responsive design for mobile devices
- Supporting Docusaurus' light/dark mode system

## CSS Custom Properties Integration

The widget integrates with the site's existing color scheme by using CSS custom properties defined in `src/css/custom.css`, ensuring visual consistency with the overall theme.

## Testing Considerations

When implementing global components:

- Test on multiple page types (docs, blog, custom pages)
- Verify responsive behavior on different screen sizes
- Check both light and dark mode compatibility
- Ensure performance impact is minimal
- Validate accessibility compliance