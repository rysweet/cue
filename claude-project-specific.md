# AI-SIP Workshop Project-Specific Instructions

## Overview

This repository contains a sample JavaScript application used in the AI-SIP (AI-enhanced Software development In Practice) workshop. The application visualizes file system structures as an interactive graph using D3.js, providing a hands-on environment for demonstrating AI-assisted development workflows, debugging practices, and automated issue management.

The workshop focuses on:
- Leveraging AI tools like Claude Code and GitHub Copilot for efficient development
- Implementing test-driven development with AI assistance
- Creating automated error handling and issue creation workflows
- Building visual debugging and annotation features

## Project-Specific Guidelines

### Code Style
- Follow existing patterns in the codebase
- Use ES6+ JavaScript features
- Maintain consistent indentation (2 spaces)
- Add meaningful variable and function names

### Workshop-Specific Git Practices
- Keep feature branches (don't delete) for workshop instruction purposes
- Use descriptive branch names that help workshop attendees understand the progression

### Project-Specific Files to Verify
- Always verify existence of: `CLAUDE.md`, `prompts/`, `.github/agents/`
- These files may contain critical project configuration
- The repository should be: `rysweet/cue`

### Testing Strategy
- Write tests for all new features
- Maintain test coverage above 80%
- Use Playwright for E2E testing
- Test error scenarios and edge cases

### Error Handling
- Catch and log all exceptions appropriately
- Create GitHub issues for production errors
- Include stack traces and reproduction steps
- Assign issues to appropriate team members

## Available Project Agents
- **test-solver**: Specialized in fixing failing tests, particularly Playwright E2E tests. Excels at debugging cross-browser issues, timing problems, and test stability.

## Visual-First Development
- Use screenshots and mockups to guide implementation
- Test UI changes visually using the Playwright MCP service
- Capture and annotate screenshots for bug reports

## Technology Stack Resources
- [Neo4j Documentation](https://neo4j.com/docs/)
- [D3.js Documentation](https://d3js.org/)
- [Playwright Documentation](https://playwright.dev/docs/intro)

## Project Structure
This is a JavaScript/TypeScript project with:
- D3.js for graph visualization
- Neo4j for graph database
- Playwright for E2E testing
- GitHub Actions for CI/CD

## Workshop Context
This repository serves as a teaching tool for AI-enhanced development practices. When making changes:
- Consider the educational value of the implementation
- Document the AI assistance process
- Create clear examples for workshop participants
- Maintain progression of complexity across branches