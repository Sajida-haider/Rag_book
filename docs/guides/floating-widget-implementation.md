---
title: Floating Chatbot Widget Implementation
sidebar_label: Floating Widget
---

# Floating Chatbot Widget Implementation

This page details the implementation of the floating chatbot widget that appears on all pages of the documentation site.

## Overview

The floating chatbot widget is implemented using Docusaurus theme component overrides to ensure it appears on every page of the site. The widget is positioned at the bottom-left corner of the viewport and provides an AI assistant interface for users.

## Implementation Approach

### 1. Component Structure

The widget is implemented as a self-contained React component with:

- State management for open/close functionality
- CSS module styling with responsive design
- Accessibility considerations
- Dark/light mode support

### 2. Global Integration

The component is integrated globally using the Docusaurus `Root` theme override:

```jsx
// src/theme/Root/index.tsx
import React from 'react';
import BrowserOnly from '@docusaurus/BrowserOnly';
import FloatingWidget from '@site/src/components/FloatingWidget/FloatingWidget';

export default function Root({children}) {
  return (
    <>
      {children}
      <BrowserOnly>
        {() => <FloatingWidget />}
      </BrowserOnly>
    </>
  );
}
```

### 3. BrowserOnly Pattern

The `BrowserOnly` wrapper ensures the component is only rendered on the client-side, preventing server-side rendering issues that can occur with floating elements that need to access browser APIs.

## Features

- **Toggle Functionality**: Click the floating button to open/close the chat interface
- **Responsive Design**: Adapts to different screen sizes
- **Theme Support**: Automatically matches the site's light/dark mode
- **Accessibility**: Proper ARIA labels and keyboard navigation support
- **Performance**: Lightweight implementation with minimal impact on page load

## Styling

The widget uses CSS modules for scoped styling and integrates with the site's existing CSS custom properties to maintain visual consistency with the overall theme.

## Usage

The widget automatically appears on all pages due to the Root theme override. No additional setup is required on individual pages.