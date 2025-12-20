# Quickstart Guide: Docusaurus UI Enhancement for Physical AI & Humanoid Robotics

## Overview
This guide provides instructions for implementing the UI enhancements for the Physical AI & Humanoid Robotics documentation site. The enhancements include theme customization, homepage redesign, sidebar improvements, and responsive design.

## Prerequisites
- Node.js 18+ installed
- npm or yarn package manager
- Basic knowledge of React and CSS
- Docusaurus 2.x project setup

## Installation
1. Navigate to your Docusaurus project directory
2. Ensure dependencies are installed:
   ```bash
   npm install
   # or
   yarn install
   ```

## Implementation Steps

### 1. Theme & Colors Setup
**File**: `src/css/custom.css`

1. Apply the specified color palette:
   ```css
   :root {
     --ifm-color-primary: #0EA5E9;          /* Steel Blue */
     --ifm-color-primary-dark: #0284C7;     /* Darker Steel Blue */
     --ifm-color-primary-darker: #0369A1;   /* Even Darker Steel Blue */
     --ifm-color-primary-darkest: #075985;  /* Darkest Steel Blue */
     --ifm-color-primary-light: #38BDF8;    /* Light Steel Blue */
     --ifm-color-primary-lighter: #7DD3FC;  /* Lighter Steel Blue */
     --ifm-color-primary-lightest: #BAE6FD; /* Lightest Steel Blue */

     --ifm-background-color: #F8FAFC;       /* Off-white background */
     --ifm-font-color-base: #334155;        /* Slate text color */
     --ifm-color-secondary: #F97316;        /* Soft Orange accent */
   }
   ```

2. Set background and text colors:
   ```css
   body {
     background-color: #F8FAFC;
     color: #334155;
   }
   ```

### 2. Typography Setup
**File**: `src/css/custom.css`

1. Add modern sans-serif fonts:
   ```css
   :root {
     --ifm-font-family-base: "Inter", "Roboto", system-ui, -apple-system, sans-serif;
   }

   body {
     font-family: var(--ifm-font-family-base);
     line-height: 1.6;
   }

   h1, h2, h3, h4, h5, h6 {
     font-weight: 600;
     line-height: 1.3;
   }

   /* Add appropriate spacing */
   .markdown h1,
   .markdown h2,
   .markdown h3 {
     margin-top: 2rem;
     margin-bottom: 1rem;
   }

   .markdown p {
     margin-bottom: 1rem;
   }
   ```

### 3. Homepage Customization
**File**: `src/pages/index.js` and `src/pages/index.module.css`

1. Create a custom homepage with hero section and navigation cards:
   ```javascript
   import React from 'react';
   import clsx from 'clsx';
   import Link from '@docusaurus/Link';
   import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
   import Layout from '@theme/Layout';
   import styles from './index.module.css';

   function HomepageHeader() {
     const {siteConfig} = useDocusaurusContext();
     return (
       <header className={clsx('hero hero--primary', styles.heroBanner)}>
         <div className="container">
           <h1 className="hero__title">{siteConfig.title}</h1>
           <p className="hero__subtitle">{siteConfig.tagline}</p>
           <div className={styles.buttons}>
             <Link
               className="button button--secondary button--lg"
               to="/docs/intro">
               Get Started
             </Link>
           </div>
         </div>
       </header>
     );
   }

   function NavigationCards() {
     const cards = [
       {
         title: 'Basics',
         icon: '💡',
         description: 'Fundamental concepts of Physical AI and Robotics',
         to: '/docs/basics/intro'
       },
       {
         title: 'Sensors',
         icon: '👁️',
         description: 'Understanding sensor systems in robotics',
         to: '/docs/sensors/intro'
       },
       {
         title: 'Actuators',
         icon: '⚙️',
         description: 'Actuator mechanisms and control systems',
         to: '/docs/actuators/intro'
       },
       {
         title: 'Vision Language Action',
         icon: '🔳',
         description: 'Integration of vision, language and action',
         to: '/docs/vision-language-action/intro'
       }
     ];

     return (
       <section className={styles.features}>
         <div className="container">
           <div className="row">
             {cards.map((card, idx) => (
               <div key={idx} className={clsx('col col--3', styles.featureCard)}>
                 <div className={styles.card}>
                   <span className={styles.cardIcon}>{card.icon}</span>
                   <h3>{card.title}</h3>
                   <p>{card.description}</p>
                   <Link to={card.to} className={styles.cardLink}>
                     Explore →
                   </Link>
                 </div>
               </div>
             ))}
           </div>
         </div>
       </section>
     );
   }

   export default function Home() {
     const {siteConfig} = useDocusaurusContext();
     return (
       <Layout
         title={`Hello from ${siteConfig.title}`}
         description="Physical AI & Humanoid Robotics Documentation">
         <HomepageHeader />
         <NavigationCards />
       </Layout>
     );
   }
   ```

2. Add CSS for homepage cards:
   ```css
   .heroBanner {
     padding: 4rem 0;
     text-align: center;
     position: relative;
     overflow: hidden;
     background: linear-gradient(135deg, #0EA5E9 0%, #0284C7 100%);
     color: white;
   }

   @media screen and (max-width: 996px) {
     .heroBanner {
       padding: 2rem;
     }
   }

   .buttons {
     display: flex;
     align-items: center;
     justify-content: center;
   }

   .features {
     padding: 4rem 0;
   }

   .featureCard {
     padding: 1rem;
   }

   .card {
     background: white;
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

   .cardIcon {
     font-size: 2rem;
     margin-bottom: 1rem;
     display: block;
   }

   .card h3 {
     color: #334155;
     margin: 0 0 1rem 0;
   }

   .card p {
     color: #64748b;
     margin: 0 0 1rem 0;
     flex-grow: 1;
   }

   .cardLink {
     color: #0EA5E9;
     text-decoration: none;
     font-weight: 500;
   }

   .cardLink:hover {
     text-decoration: underline;
   }
   ```

### 4. Sidebar Customization
**File**: `docusaurus.config.js` and `src/css/custom.css`

1. Update docusaurus.config.js for sidebar configuration:
   ```javascript
   module.exports = {
     // ... other config
     themeConfig: {
       // ... other theme config
       navbar: {
         // ... navbar config
       },
       footer: {
         // ... footer config
       },
       sidebar: {
         // Use default sidebar behavior
       },
       colorMode: {
         defaultMode: 'light',
         disableSwitch: false,
         respectPrefersColorScheme: false,
       },
       // Enable breadcrumbs
       tableOfContents: {
         minHeadingLevel: 2,
         maxHeadingLevel: 5,
       },
     },
   };
   ```

2. Customize sidebar appearance in custom.css:
   ```css
   .sidebar {
     background-color: #dbeafe; /* Soft blue background */
   }

   .sidebar .menu__list .menu__link--active {
     background-color: #0EA5E9; /* Steel blue highlight */
     color: white;
     border-radius: 4px;
   }

   .sidebar .menu__list .menu__link:hover {
     background-color: #bae6fd; /* Light steel blue on hover */
     border-radius: 4px;
   }

   .sidebar .menu__list .menu__link {
     border-radius: 4px;
   }
   ```

### 5. Functional Elements Configuration
**File**: `docusaurus.config.js`

1. Enable breadcrumbs and search:
   ```javascript
   module.exports = {
     // ... other config
     themeConfig: {
       // ... other config
       algolia: {
         // Your Algolia config or use default search
         appId: 'YOUR_APP_ID',
         apiKey: 'YOUR_SEARCH_API_KEY',
         indexName: 'YOUR_INDEX_NAME',
       },
       // Enable breadcrumbs
       tableOfContents: {
         minHeadingLevel: 2,
         maxHeadingLevel: 5,
       },
     },
     presets: [
       [
         'classic',
         {
           docs: {
             sidebar: {
               autoCollapseCategories: true, // Collapsible sidebar
             },
             // ... other docs config
           },
           // ... other preset config
         },
       ],
     ],
   };
   ```

### 6. Responsive Design & Performance Optimization
1. Add responsive styles:
   ```css
   /* Responsive adjustments for cards */
   @media (max-width: 996px) {
     .featureCard {
       margin-bottom: 1rem;
     }

     .card {
       padding: 1rem;
     }
   }

   @media (max-width: 768px) {
     .heroBanner {
       padding: 2rem 1rem;
     }

     .cardIcon {
       font-size: 1.5rem;
     }
   }

   @media (max-width: 576px) {
     .featureCard {
       flex: 0 0 100%;
       max-width: 100%;
     }
   }
   ```

2. Optimize for performance:
   - Minimize custom CSS
   - Use efficient selectors
   - Optimize images for web
   - Enable Docusaurus built-in optimizations

## Running the Site
1. Start the development server:
   ```bash
   npm run start
   # or
   yarn start
   ```

2. Visit `http://localhost:3000` to see the enhanced UI

## Building for Production
```bash
npm run build
# or
yarn build
```

## Testing
1. Verify all color changes are applied correctly
2. Test navigation cards functionality
3. Check sidebar highlighting
4. Verify responsive behavior on different screen sizes
5. Ensure search and breadcrumbs work properly