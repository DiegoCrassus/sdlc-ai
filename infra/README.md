# Infrastructure

Infrastructure artifacts live here when they are not application code.

Expected contents:

- `migrations/`: database schema migrations and migration notes.
- `docker/`: Dockerfiles, compose files, and container runtime assets when introduced.
- IaC manifests: Terraform, Pulumi, Helm, or provider-specific configuration when adopted.

Do not store secrets, local databases, dumps, or environment-specific credentials in this directory.
