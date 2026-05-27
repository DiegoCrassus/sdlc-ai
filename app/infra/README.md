# app/infra

## Purpose

Infrastructure-as-code for the sdlc-ai project. Contains all infrastructure definitions, container configuration, and deployment tooling.

## Status

**Not yet implemented.** This boundary is reserved for infrastructure definitions.

## What Belongs Here

- Docker and docker-compose configuration
- Kubernetes manifests (if applicable)
- Cloud infrastructure definitions (Terraform, Pulumi, etc.)
- CI/CD pipeline configuration (GitHub Actions workflows)
- Environment configuration templates
- Deployment scripts

## What Does NOT Belong Here

- Application code — goes in `app/backend/` or `app/frontend/`
- SDLC configuration — goes in `.sdlc/`
- Documentation — goes in `docs/infrastructure/`
- Secrets or actual credentials — never committed to version control

## Expected Future Structure

```
app/infra/
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── k8s/                ← Kubernetes manifests (if used)
├── terraform/          ← IaC (if used)
├── github/
│   └── workflows/      ← CI/CD pipeline definitions
└── README.md           ← (this file, extended with setup instructions)
```

## Principles

1. All infrastructure is versioned and reviewable.
2. No manual console changes to production.
3. Every environment can be reproduced from this directory.
4. Secrets are managed via environment variables or a secrets manager — never committed.

## Setup (When Implemented)

TBD.
