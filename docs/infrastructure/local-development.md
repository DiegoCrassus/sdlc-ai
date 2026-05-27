# Local Development Setup

## Prerequisites

- Python 3.11+ (check: `python --version`)
- pip or uv (for dependency management)
- Git
- Cursor IDE (for AI-native workflow)

## Initial Setup

```bash
# 1. Clone the repository
git clone https://github.com/DiegoCrassus/sdlc-ai.git
cd sdlc-ai

# 2. Create a virtual environment
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# or: .venv\Scripts\activate  # Windows

# 3. Install dependencies
pip install -e ".[dev]"
# or if using uv:
uv sync

# 4. Copy and configure environment
cp .env.example .env  # NOTE: .env.example does not exist yet — TBD
# Edit .env with your credentials

# 5. Validate the repository structure
make sdlc-doctor
```

## Environment Variables

Required variables (see `.env` for full list):

| Variable                              | Purpose                    |
|---------------------------------------|----------------------------|
| `GITHUB_PERSONAL_ACCESS_TOKEN_CLASSIC`| GitHub MCP access          |
| `PLANE_API_KEY`                       | Plane task management      |
| `OPENAI_API_KEY`                      | LLM inference              |
| `DATABASE_URL`                        | Local SQLite path          |
| `AGENT_MODEL`                         | LLM model identifier       |

## Running the SDLC Doctor

```bash
make sdlc-doctor
```

Expected output: all `[PASS]`, some `[WARN]` for unconfigured integrations.

## Running Tests

```bash
# When tests exist:
python -m pytest app/ -v
```

## Known Local Setup Issues

- No application services to run yet — this is the initialization phase.
- Container setup (Docker) will be documented here when services are defined.

## IDE Configuration

Open the project in Cursor. The `.cursor/` directory will be automatically loaded by Cursor, providing:
- Agent rules
- Command shortcuts
- Skill procedures
- SDLC context
