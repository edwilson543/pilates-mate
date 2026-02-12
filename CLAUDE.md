# Project Overview

This repository implements a webapp for generating pilates lesson plans.

**Technology Stack:**
- Backend: Python with FastAPI
- Frontend: TypeScript with Next.js
- API: OpenAPI/Swagger specification

# Project Structure

The project is split into two main areas:

**Backend (`./backend/`)**
- Work here when you need to: Add API endpoints, implement domain logic, modify data access
- More details: `./backend/CLAUDE.md`

**Frontend (`./frontend/`)**
- Work here when you need to: Build UI components, create pages, handle forms
- More details: `./frontend/CLAUDE.md`

**How they integrate:**
Backend exposes OpenAPI spec → Frontend generates API client → Hooks wrap client → Components use hooks

# Development Workflow

**Local Development:**
- Backend runs on `http://localhost:8000`
- Frontend runs on `http://localhost:3000`

**API Changes Flow:**
1. Modify backend API endpoints
2. Run backend: `make api` from `./backend/`
3. Generate API client: `pnpm openapi-ts` from `./frontend/`
4. Format API client: `make format` from `./frontend/`
5. Commit API client with message: `Auto-update frontend API client using hey-api`

**Testing:**
- Backend: `make test` from `./backend/`
- Frontend: No tests yet

# Git
This project uses atomic commits. 
All linting checks must pass before committing.