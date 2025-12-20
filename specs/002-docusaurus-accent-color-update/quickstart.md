# Quickstart Guide: Docusaurus Accent Color Update for Physical AI & Humanoid Robotics

## Overview
This guide provides instructions for implementing the accent color update from orange (#F97316) to black (#000) or white (#FFF) in the Physical AI & Humanoid Robotics documentation site.

## Prerequisites
- Node.js 18+ installed
- npm or yarn package manager
- Access to the existing Docusaurus project
- Understanding of CSS custom properties

## Implementation Steps

### 1. Identify Current Orange Accent Usage
**File**: `src/css/custom.css` and other CSS files

1. Search for all instances of orange color (#F97316):
   ```bash
   grep -r "#F97316" src/
   ```

2. Identify where black (#000) or white (#FFF) should be used instead based on background context:
   - Use black (#000) on light backgrounds where high contrast is needed
   - Use white (#FFF) on dark backgrounds where high contrast is needed

### 2. Update CSS Custom Properties
**File**: `src/css/custom.css`

1. Update accent color custom properties:
   ```css
   :root {
     /* Keep primary colors unchanged */
     --ifm-color-primary: #0EA5E9;          /* Steel Blue - unchanged */
     --ifm-background-color: #F8FAFC;       /* Off-white background - unchanged */
     --ifm-font-color-base: #334155;        /* Slate text color - unchanged */

     /* Update accent color from orange to black/white as appropriate */
     /* For light backgrounds, use black */
     --ifm-color-accent-light: #000000;     /* Black accent for light backgrounds */
     /* For dark backgrounds, use white */
     --ifm-color-accent-dark: #FFFFFF;      /* White accent for dark backgrounds */
   }
   ```

### 3. Update Specific Accent Elements
**File**: `src/css/custom.css`

1. Update admonition elements that previously used orange:
   ```css
   /* For light-themed admonitions */
   .admonition {
     border-left-color: #000000; /* Black accent on light backgrounds */
   }

   .admonition-icon {
     color: #000000; /* Black accent on light backgrounds */
   }

   /* If any dark-themed elements exist */
   [data-theme='dark'] .admonition {
     border-left-color: #FFFFFF; /* White accent on dark backgrounds */
   }

   [data-theme='dark'] .admonition-icon {
     color: #FFFFFF; /* White accent on dark backgrounds */
   }
   ```

### 4. Update Homepage Module Cards
**File**: `src/pages/index.module.css`

1. Ensure module cards maintain white background, soft shadows, and hover effect:
   ```css
   .card {
     background: white; /* Maintain white background */
     border-radius: 0.75rem;
     padding: 1.5rem;
     height: 100%;
     box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
     transition: transform 0.2s ease, box-shadow 0.2s ease;
     display: flex;
     flex-direction: column;
   }

   .card:hover {
     transform: translateY(-4px);
     box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
   }

   /* Update card links to use appropriate accent color */
   .cardLink {
     color: #000000; /* Black accent on light background */
     text-decoration: none;
     font-weight: 500;
   }

   .cardLink:hover {
     text-decoration: underline;
   }
   ```

### 5. Update Navigation Elements
**File**: `src/css/custom.css`

1. Ensure navigation elements maintain functionality while updating accents:
   ```css
   /* Sidebar remains unchanged - soft blue background with steel blue highlighting */
   .sidebar {
     background-color: #dbeafe; /* Soft blue background - unchanged */
   }

   .sidebar .menu__list .menu__link--active {
     background-color: #0EA5E9; /* Steel blue highlight - unchanged */
     color: white;
     border-radius: 4px;
   }

   .sidebar .menu__list .menu__link:hover {
     background-color: #bae6fd; /* Light steel blue on hover - unchanged */
     border-radius: 4px;
   }

   /* Update any navigation accent elements as needed */
   .menu__list .menu__link:hover {
     color: #000000; /* Black accent on hover for light backgrounds */
   }
   ```

### 6. Update Other Accent Elements
**File**: `src/css/custom.css`

1. Find and update any remaining orange accent elements:
   ```css
   /* Update table of contents links */
   .table-of-contents__link,
   .table-of-contents__link:hover {
     color: #334155; /* Maintain slate color, not accent */
   }

   /* Update any other elements that may have used orange as an accent */
   .navbar__item:hover {
     color: #000000; /* Black accent on hover */
   }
   ```

### 7. Test Color Accessibility
1. Verify all color combinations meet WCAG accessibility standards
2. Ensure text remains readable against all backgrounds
3. Test both light and dark modes if applicable

### 8. Verify Functionality Preservation
1. Confirm homepage hero section remains engaging
2. Verify module cards still navigate to correct chapters
3. Ensure sidebar remains collapsible with soft blue background
4. Confirm active page highlighting still uses steel blue
5. Verify breadcrumbs and search functionality remain intact

## Running the Site
1. Start the development server:
   ```bash
   npm run start
   # or
   yarn start
   ```

2. Visit `http://localhost:3000` to see the updated accent colors

## Building for Production
```bash
npm run build
# or
yarn build
```

## Testing
1. Verify all orange accents (#F97316) have been replaced with black (#000) or white (#FFF)
2. Test that module names remain clearly visible
3. Confirm all navigation functionality is preserved
4. Verify hero section remains engaging
5. Ensure navigation remains smooth
6. Check that the professional robotics/AI theme is enhanced by the new color scheme