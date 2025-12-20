---
id: "0003"
title: "Update UI Module Names"
stage: "green"
dateIso: "2025-12-18"
surface: "agent"
model: "claude-sonnet-4-5-20250929"
feature: "002-docusaurus-accent-color-update"
branch: "002-docusaurus-accent-color-update"
user: "KARAKORUM TRADERS"
command: "Manual"
labels:
  - "docusaurus"
  - "ui-enhancement"
  - "homepage"
  - "sidebar"
  - "navigation"
  - "implementation"
links:
  spec: null
  ticket: null
  adr: null
  pr: null
filesYaml:
  - "src/pages/index.js"
  - "src/pages/index.module.css"
  - "sidebars.ts"
testsYaml:
  - "none"
---

# PHR-0003: Update UI Module Names

## Prompt Text

Enhance the Docusaurus book UI for "Physical AI & Humanoid Robotics" with the following updates:

Homepage Module Boxes:

Replace old cards/boxes with simple rectangular boxes containing only the module name.

Use these module names:

Module 1: The Robotic Nervous System (ROS 2)

Module 2: The Digital Twin (Gazebo & Unity)

Module 3: The AI-Robot Brain (NVIDIA Isaac™)

Module 4: Vision-Language-Action (VLA)

Clicking a box navigates to that module's first chapter page (no page not found).

Boxes should have a slightly thicker border, white/off-white background, steel-blue hover, and black/slate text.

Sidebar:

Remove old placeholders: Basics, Sensors, Actuators, Vision Language Action.

Add correct modules with proper links to their chapters.

Highlight the active module/page in steel blue.

Homepage "Get Started" Button:

Ensure it navigates correctly to the book content (first module or intro page) instead of page not found.

Constraints & Design:

Docusaurus classic theme, custom.css only.

## Response Text

Successfully updated the UI with correct module names, navigation paths, and styling as requested.

## Outcome Impact

Updated the homepage and sidebar to display accurate module names and navigation paths, ensuring all links point to valid documentation pages.

## Tests Summary

none

## Files Summary

- src/pages/index.js
- src/pages/index.module.css
- sidebars.ts

## Next Prompts

none

## Reflection Note

Completed UI updates with correct module names and navigation paths, maintaining all functionality.

## Evaluation

Failure modes observed: none

Next experiment to improve prompt quality: none needed