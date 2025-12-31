# Quickstart: Setting Up the ROS 2 Book with Docusaurus

**Feature**: Module 1 - The Robotic Nervous System (ROS 2)
**Date**: 2025-12-16

## Prerequisites

- Node.js 18+ installed
- npm or yarn package manager
- Git for version control
- Basic knowledge of Markdown and JavaScript

## Installation Steps

### 1. Initialize Docusaurus Project

```bash
# Create a new Docusaurus project
npx create-docusaurus@latest my-book classic

# Navigate to the project directory
cd my-book
```

### 2. Install Additional Dependencies

```bash
# Install dependencies for code examples and diagrams
npm install @docusaurus/module-type-aliases @docusaurus/types
```

### 3. Configure Docusaurus

Update `docusaurus.config.js` with the following configuration:

```javascript
// docusaurus.config.js
import {themes as prismThemes} from 'prism-react-renderer';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Physical AI & Humanoid Robotics',
  tagline: 'Bridging the gap between digital AI and physical robots',
  favicon: 'img/favicon.ico',

  // Set the production url of your site here
  url: 'https://your-username.github.io',
  // Set the /<baseUrl>/ pathname under which your site is served
  // For GitHub Pages, this is usually '/<project-name>/'
  baseUrl: '/my-book/',

  // GitHub pages deployment config
  organizationName: 'your-username', // Usually your GitHub org/user name
  projectName: 'my-book', // Usually your repo name
  deploymentBranch: 'gh-pages', // Branch that GitHub Pages will deploy from

  onBrokenLinks: 'throw',
  onBrokenMarkdownLinks: 'warn',

  // Even if you don't use internationalization, you can use this field to set
  // useful metadata like html lang. For example, if your site is Chinese, you
  // may want to replace "en" with "zh-Hans".
  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          sidebarPath: './sidebars.js',
          // Please change this to your repo.
          // Remove this to remove the "edit this page" links.
          editUrl:
            'https://github.com/your-username/my-book/edit/main/',
        },
        blog: false, // Optional: disable the blog plugin
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      // Replace with your project's social card
      image: 'img/docusaurus-social-card.jpg',
      navbar: {
        title: 'Physical AI & Robotics',
        logo: {
          alt: 'My Site Logo',
          src: 'img/logo.svg',
        },
        items: [
          {
            type: 'docSidebar',
            sidebarId: 'tutorialSidebar',
            position: 'left',
            label: 'Book',
          },
          {
            href: 'https://github.com/your-username/my-book',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Docs',
            items: [
              {
                label: 'Module 1: ROS 2',
                to: '/docs/module-1/chapter-1-ros2-fundamentals',
              },
            ],
          },
          {
            title: 'More',
            items: [
              {
                label: 'GitHub',
                href: 'https://github.com/your-username/my-book',
              },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Physical AI & Humanoid Robotics. Built with Docusaurus.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
        additionalLanguages: ['python', 'bash', 'xml'],
      },
    }),
};

export default config;
```

### 4. Create Sidebar Configuration

Create `sidebars.js` with the following content:

```javascript
// sidebars.js

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  tutorialSidebar: [
    'intro',
    {
      type: 'category',
      label: 'Module 1: The Robotic Nervous System (ROS 2)',
      items: [
        'module-1/chapter-1-ros2-fundamentals',
        'module-1/chapter-2-python-agents-ros2',
        'module-1/chapter-3-urdf-humanoid-models',
      ],
    },
    // Additional modules will be added here as they are created
  ],
};

export default sidebars;
```

### 5. Create Initial Content Structure

Create the directory structure and initial files:

```bash
# Create module directory
mkdir -p docs/module-1

# Create initial content files
touch docs/intro.md
touch docs/module-1/chapter-1-ros2-fundamentals.md
touch docs/module-1/chapter-2-python-agents-ros2.md
touch docs/module-1/chapter-3-urdf-humanoid-models.md
```

### 6. Add Initial Content

Add basic content to `docs/intro.md`:

```markdown
---
sidebar_position: 1
---

# Introduction

Welcome to the Physical AI & Humanoid Robotics book. This comprehensive guide covers the intersection of artificial intelligence and robotics, focusing on how AI systems can function in the physical world.

## What You'll Learn

- How to bridge the gap between digital AI and physical robots
- The fundamentals of ROS 2 for robot communication
- How to connect Python AI agents to robot controllers
- Working with URDF for humanoid robot models
- Advanced topics in physical AI and humanoid robotics

## Prerequisites

This book assumes you have:
- Basic Python programming knowledge
- Familiarity with AI/ML concepts
- Interest in robotics and physical systems

Let's begin our journey into Physical AI!
```

### 7. Run the Development Server

```bash
# Start the development server
npm run start

# The site will be available at http://localhost:3000
```

### 8. Build for Production

```bash
# Build the static site
npm run build

# The built site will be in the build/ directory
```

### 9. Deploy to GitHub Pages

```bash
# Deploy to GitHub Pages
GIT_USER=<your-github-username> npm run deploy
```

## Next Steps

1. Add content to the module-1 chapters based on the specification
2. Create diagrams and images for the static/img directory
3. Implement the three chapters as specified:
   - Chapter 1: ROS 2 Fundamentals
   - Chapter 2: Python Agents with ROS 2 (rclpy)
   - Chapter 3: Humanoid Robot Description with URDF
4. Test the site locally before deployment
5. Set up GitHub Actions for automated deployment (optional)