# Coding Preferences

This document describes how he prefers software to be written and organized. It should be used when EdgeMind needs to recommend implementation choices or describe how he likes to work.

## Frontend Preferences

He prefers React with Next.js App Router for modern web applications, especially when the project needs routing, server rendering, and a path to production-ready structure. TypeScript is the default language because it improves refactoring safety and keeps large codebases more maintainable. Tailwind CSS is his preferred styling approach because it keeps implementation fast and avoids unnecessary CSS complexity.

## Backend Preferences

He is comfortable with Node.js, Express, NestJS, and Python FastAPI. He tends to prefer backend code that is organized around services, clear boundaries, and readable business logic instead of framework-heavy code. When the project is small and direct, FastAPI is a natural fit. When the backend needs stronger structure, NestJS becomes more attractive.

## Architecture Preferences

He prefers feature-based folders, dependency injection, a service layer, and the repository pattern when it actually improves the design. He values clean architecture, SOLID principles, composition over inheritance, and simple abstractions that can be understood by another developer without long explanation.

## Database Preferences

PostgreSQL is the default recommendation when data is structured, integrity matters, and the application may grow. MongoDB is appropriate when the domain is document-shaped, flexible, or content-driven. Firebase is useful when rapid application development and managed services are more valuable than full relational control.

## Authentication Preferences

JWT authentication is a common preference for REST APIs and modern web backends. He tends to favor auth flows that are easy to reason about, easy to secure, and easy to integrate into the app's architecture without coupling too much business logic to the framework.

## Deployment Preferences

He works comfortably with Linux, Fedora, VS Code, Neovim, Railway, Azure, VPS environments, Docker, and GitHub Actions. He prefers deployments that are simple enough to maintain and automate, rather than setups that require constant manual care.

## Testing Philosophy

Playwright is the preferred tool when end-to-end browser behavior needs to be verified. Manual QA is also part of the workflow, especially for UI-heavy or product-facing work. He values tests that validate important behavior rather than tests that exist only to increase coverage numbers.

## Naming Conventions

He prefers names that are descriptive, stable, and easy to scan. Files, folders, functions, and components should say what they do without relying on clever abbreviations.

## Folder Organization

He prefers feature-based organization when the codebase grows. That means keeping related logic close together instead of scattering it across framework-driven folders that are technically correct but hard to navigate later.

## API Design

He prefers REST for most application APIs because it is simple, predictable, and easy to integrate. For APIs that need authentication, JWT is a practical default. He likes endpoints and request shapes that are easy to explain and easy to debug.

## Error Handling

Error handling should be explicit, user-facing when needed, and logged in a way that helps debugging. Failures should be understandable rather than hidden inside generic errors.

## Logging

Logging should help trace behavior in production without becoming noisy. He prefers logs that provide useful context, especially around deployment issues, API failures, and system boundaries.

## Performance

Performance matters, but he does not optimize blindly. The preference is to build with performance in mind from the beginning, keep the design simple, and only add complexity when the bottleneck is real.

## Security

Security should be considered early. That includes safe auth handling, sensible environment variable management, avoiding unnecessary secrets in code, and choosing technologies that do not make secure behavior difficult.

## Related Documents

- [technology_preferences](technology_preferences.md)
- [workflow](workflow.md)
- [decision_making](decision_making.md)