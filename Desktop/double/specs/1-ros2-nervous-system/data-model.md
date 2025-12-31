# Data Model: ROS 2 Book Content Structure

**Feature**: Module 1 - The Robotic Nervous System (ROS 2)
**Date**: 2025-12-16

## Content Entities

### Module
- **Name**: String (e.g., "Module 1: The Robotic Nervous System")
- **Description**: String (overview of the module's focus)
- **Learning Objectives**: Array of strings (what students will learn)
- **Prerequisites**: Array of strings (required knowledge)
- **Chapters**: Array of Chapter references
- **Relationships**: Contains multiple Chapters

### Chapter
- **Title**: String (e.g., "ROS 2 Fundamentals")
- **Slug**: String (URL-friendly identifier)
- **Content**: String (Markdown content)
- **Learning Objectives**: Array of strings (specific to this chapter)
- **Examples**: Array of CodeExample references
- **Diagrams**: Array of Diagram references
- **Module**: Reference to parent Module
- **Relationships**: Belongs to one Module, contains multiple Examples and Diagrams

### CodeExample
- **Title**: String (description of the example)
- **Language**: String (programming language for syntax highlighting)
- **Code**: String (actual code content)
- **Explanation**: String (description of what the code does)
- **Chapter**: Reference to parent Chapter
- **Relationships**: Belongs to one Chapter

### Diagram
- **Title**: String (description of the diagram)
- **FileName**: String (file path in static directory)
- **AltText**: String (accessibility description)
- **Caption**: String (explanation of the diagram)
- **Chapter**: Reference to parent Chapter
- **Relationships**: Belongs to one Chapter

### NavigationItem
- **Label**: String (display name in sidebar)
- **Type**: String (doc, link, category)
- **Id**: String (reference to document or URL)
- **Priority**: Number (ordering in navigation)
- **Parent**: Reference to parent NavigationItem (for nested structure)

## Content Validation Rules

### Module Validation
- Title must be 5-100 characters
- Description must be 20-500 characters
- Must have 1-10 chapters
- Learning objectives must be 3-10 items

### Chapter Validation
- Title must be 5-100 characters
- Content must be 500-10000 characters
- Must have 1-5 learning objectives
- Slug must be URL-friendly (lowercase, hyphens only)
- Must belong to exactly one module

### CodeExample Validation
- Title must be 5-100 characters
- Language must be a supported syntax highlighting language
- Code must be 10-5000 characters
- Must belong to exactly one chapter

### Diagram Validation
- Title must be 5-100 characters
- FileName must exist in static directory
- AltText is required for accessibility
- Must belong to exactly one chapter

## State Transitions

### Content Creation Flow
1. Module created with basic metadata
2. Chapters added to Module with titles and slugs
3. Content written for each Chapter
4. CodeExamples and Diagrams added to Chapters
5. Navigation structure defined
6. Content reviewed and validated
7. Published to Docusaurus site

### Content Update Flow
1. Content draft created
2. Technical accuracy verified
3. Accessibility compliance checked
4. Updates applied to entities
5. Navigation updated if needed
6. Changes published

## Content Relationships

The content structure forms a hierarchical tree:
- Module (root) → Chapters (children)
- Chapter → CodeExamples, Diagrams (children)
- Navigation follows the same hierarchy for user experience
- Cross-chapter references are handled through navigation links