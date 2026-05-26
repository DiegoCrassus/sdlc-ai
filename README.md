# RPG-OP

RPG-OP é uma aplicação para mesas de RPG com backend FastAPI, frontend React/Vite e harness operacional SDLC em shell.

## Estrutura

```text
rpg-op/
├── .cursor/      # configuração do Cursor
├── .github/      # workflows e templates GitHub
├── .sdlc/        # scripts, comandos e workflows operacionais
├── apps/
│   ├── backend/  # FastAPI
│   └── frontend/ # React + Vite
├── tests/        # pytest
├── Makefile
├── dev.sh
└── launch.sh
```

## Execução Local

Pré-requisitos: `bash`, Python 3.12+, Node 20+, `uv`, `make` e `npm`.

```bash
make setup
./dev.sh
```

- App: http://127.0.0.1:5173
- API: http://127.0.0.1:8000/health
- Swagger: http://127.0.0.1:8000/docs

## Comandos

```bash
make dev
make dev-backend
make dev-frontend
make test
make lint
make validate
make smoke
```

`make smoke` requer o backend rodando em `127.0.0.1:8000`.
