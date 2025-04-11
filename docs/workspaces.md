# Workspaces

## Overview

Workspaces are integrated environments within the AI App Store that allow individuals or job families to create managed spaces for collaboration and productivity. They provide a consistent environment for working with AI applications, tools, and workflows, maintaining context and history to enhance the user experience.

## Key Features

### Workspace Creation and Management

The integration of Workspaces within the AI App Store allows individuals or specific job families to create and manage Workspaces. This feature enables a Workspace to be created and administered by an individual for personal use or for group (job family) management, fostering collaboration and tailored workspace environments.

### App Integration

Users can add available apps to a Workspace from the AI App Store, including published apps, MCP servers, utilities, agents, tools, and Python or code snippets. This integration ensures that users have the flexibility to customize their Workspaces with the tools they need.

### Memory and Workflow Management

Workspaces implement memory functionality to retain context and history, supporting multiple workflows within a Workspace. Each workflow maintains a memory of actions taken, stored for a predefined period, allowing users to define actions as sequences such as chat flows, app usage, data creation or utilization, analysis, decision-making, and procedure following.

### User-Directed Operations

Users can direct the Workspace, switching between utilities, tools, models, agents, or apps. The integration of the LLM Suite as part of the Workspace enhances functionality, providing users with a powerful toolset for their operations.

### Local and Remote Access

Workspaces support local builds to access local files and MCP servers, while also enabling connectivity to Knowledge Bases, Databases, or the web through MCP servers. This dual access capability ensures that users can work seamlessly across different environments.

### Action Logging and Checkpoints

A running log of all actions within a workflow is maintained, time-indexed with universal identifiers for data, apps, and actions. The implementation of "Checkpoints" allows users to recreate any step or stage, with expected outcomes for agents to self-reflect or verify work.

## Workspace Types

1. **Personal Workspace**: Created by an individual for their own use, containing personal tools, workflows, and settings.

2. **Job Family Workspace**: Shared among members of a specific job function (e.g., underwriters, loan officers), with specialized tools and group collaboration features.

3. **Team Workspace**: Created for cross-functional teams working on specific projects, enabling seamless collaboration and knowledge sharing.

4. **Project Workspace**: Dedicated to a specific project with relevant apps, workflows, and documentation accessible to all project members.

## Components

### Workspace Manager

The Workspace Manager handles the creation, configuration, and administration of workspaces. It manages member access and permissions, app installations, and workspace settings.

### Memory Manager

The Memory Manager maintains the context and history within a workspace, allowing for persistent state across sessions. It implements retention policies and provides mechanisms for retrieving past actions and data.

### App Integration

The App Integration component enables the incorporation of various app types into a workspace, including connection to MCP servers for remote resources, local file access, and integration with external tools.

### Workflow System

The Workflow System supports the creation and execution of workflows within a workspace, with logging of actions, checkpoints for reproducibility, and the ability to save and reuse workflows.

## Usage Examples

### Personal Research Assistant

A data scientist creates a personal workspace with various research tools, databases, and AI models. The workspace maintains context across research sessions, saving queries, results, and insights for easy reference.

### Loan Processing Team

A loan processing team creates a shared workspace with loan evaluation tools, document processing apps, and compliance checkers. The workspace tracks the progress of each loan application through a standardized workflow with checkpoints at key stages.

### Financial Analyst

A financial analyst uses a workspace to connect to market data sources, run analysis tools, and generate reports. The workspace maintains a history of analyses performed, allowing for easy comparison and verification of results.

### Compliance Review

A compliance team uses a workspace to review loan applications, with built-in validation tools and regulatory checkers. The workspace logs all review actions and decisions for audit purposes.