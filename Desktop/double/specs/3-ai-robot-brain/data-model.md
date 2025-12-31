# Data Model: AI Robot Brain Book Content Structure

**Feature**: Module 3 - The AI-Robot Brain (NVIDIA Isaac™)
**Date**: 2025-12-16

## Content Entities

### Module
- **Name**: String (e.g., "Module 3: The AI-Robot Brain")
- **Description**: String (overview of the module's focus on NVIDIA Isaac)
- **Learning Objectives**: Array of strings (what students will learn about Isaac ecosystem)
- **Prerequisites**: Array of strings (required knowledge - ROS 2 and simulation basics)
- **Chapters**: Array of Chapter references
- **Relationships**: Contains multiple Chapters

### Chapter
- **Title**: String (e.g., "NVIDIA Isaac Sim", "Isaac ROS Perception", "Nav2 Navigation")
- **Slug**: String (URL-friendly identifier)
- **Content**: String (Markdown content with concept-first approach)
- **Learning Objectives**: Array of strings (specific to this chapter)
- **Concepts**: Array of AIConcept references
- **Diagrams**: Array of Diagram references
- **Module**: Reference to parent Module
- **Relationships**: Belongs to one Module, contains multiple Concepts and Diagrams

### AIConcept
- **Name**: String (e.g., "Visual SLAM", "Sensor Fusion", "Path Planning")
- **Definition**: String (clear definition of the concept)
- **Applications**: Array of strings (how the concept is used in Isaac ecosystem)
- **RelatedConcepts**: Array of AIConcept references
- **Chapter**: Reference to parent Chapter
- **Relationships**: Belongs to one Chapter, connects to other concepts

### Diagram
- **Title**: String (description of the diagram)
- **FileName**: String (file path in static directory)
- **AltText**: String (accessibility description)
- **Caption**: String (explanation of the diagram)
- **Chapter**: Reference to parent Chapter
- **Relationships**: Belongs to one Chapter

### IsaacComponent
- **Name**: String (e.g., "Isaac Sim", "Isaac ROS", "Nav2")
- **Purpose**: String (what the component does in the ecosystem)
- **KeyFeatures**: Array of strings (main capabilities)
- **IntegrationPoints**: Array of IsaacComponent references
- **Chapter**: Reference to parent Chapter
- **Relationships**: Belongs to one Chapter, connects to other components

## Content Validation Rules

### Module Validation
- Title must be 5-100 characters
- Description must be 20-500 characters
- Must have 1-10 chapters
- Learning objectives must be 3-10 items
- Prerequisites must be clearly stated and achievable

### Chapter Validation
- Title must be 5-100 characters
- Content must be 500-10000 characters
- Must have 1-5 learning objectives
- Slug must be URL-friendly (lowercase, hyphens only)
- Must belong to exactly one module
- Must follow concept-first approach with minimal code

### AIConcept Validation
- Name must be 2-50 characters
- Definition must be clear and concise (20-200 characters)
- Must have 1-5 applications
- Must be connected to 0-5 related concepts

### Diagram Validation
- Title must be 5-100 characters
- FileName must exist in static directory
- AltText is required for accessibility
- Must belong to exactly one chapter

### IsaacComponent Validation
- Name must be 2-50 characters
- Purpose must be clear and concise (20-200 characters)
- Must have 1-10 key features
- Must be connected to 0-5 integration points

## State Transitions

### Content Creation Flow
1. Module created with basic metadata and learning objectives
2. Chapters added to Module with titles and conceptual focus
3. Content written for each Chapter with concepts and diagrams
4. AIConcepts and Diagrams added to Chapters
5. IsaacComponent relationships defined
6. Navigation structure defined
7. Content reviewed and validated
8. Published to Docusaurus site

### Content Update Flow
1. Content draft created
2. Technical accuracy verified
3. Conceptual clarity validated
4. Accessibility compliance checked
5. Updates applied to entities
6. Navigation updated if needed
7. Changes published

## Content Relationships

The content structure forms a hierarchical tree with cross-connections:
- Module (root) → Chapters (children)
- Chapter → AIConcepts, Diagrams, IsaacComponents (children)
- AIConcept → RelatedConcepts (connections across chapters)
- IsaacComponent → IntegrationPoints (connections across chapters)
- Navigation follows the same hierarchy for user experience
- Cross-chapter references are handled through concept and component connections