# Infraestrutura e stack recomendada

Recomendações para um produto **minimalista no início** e **escalável** quando a mesa crescer (mais campanhas, mais tokens, app móvel).

## Stack sugerida

| Camada | Tecnologia | Motivo |
|--------|------------|--------|
| Linguagem backend | **Python 3.12+** | Ecossistema LangChain / Deep Agents / LangGraph |
| API + BFF | **FastAPI** | Async, OpenAPI, SSE nativo |
| Agente | **deepagents** + **langgraph** | Harness oficial, checkpoints, HITL |
| ORM | **SQLAlchemy 2** + **Alembic** | Migrações maduras |
| Banco | **PostgreSQL 16** | JSONB para fichas, ACID, revisions |
| Cache / fila | **Redis 7** | Sessão, rate limit, jobs ARQ/Celery |
| Object storage | **MinIO** (dev) / **S3** (prod) | Scans e exports |
| Frontend | **Next.js 15** (App Router) | SSR, PWA futura para mesa |
| Auth | **Clerk**, **Auth0** ou **Keycloak** (self-host) | Não reinventar OAuth |
| Container | **Docker Compose** → **Kubernetes** ou **Railway/Fly** | Compose basta até ~100 usuários ativos |
| IaC (fase 2) | **Terraform** ou **Pulumi** | Reprodutibilidade |

### Modelos LLM

- **Desenvolvimento:** modelo econômico (ex. `gpt-4.1-mini`, Gemini Flash) para iterar.
- **Produção orquestrador:** modelo forte em tool use (ex. `gpt-5.4`, Claude Sonnet) — configurável via env.
- **Subagente intake (visão):** modelo multimodal forte ou pipeline híbrido (OCR dedicado + LLM estruturação).

Usar variável `AGENT_MODEL=openai:gpt-5.4` e [harness profiles](https://docs.langchain.com/oss/python/deepagents/profiles) para trocar provedor sem mudar código.

## Ambientes

| Ambiente | Propósito | Dados |
|----------|-----------|-------|
| `local` | Dev com Compose | DB efêmero ou volume nomeado |
| `staging` | QA + evals LangSmith | Anonimizado |
| `production` | Usuários reais | Backups automáticos |

## Docker Compose (desenvolvimento)

Serviços mínimos:

```yaml
# esboço — ver infra/docker-compose.yml quando implementado
services:
  postgres:
    image: postgres:16-alpine
  redis:
    image: redis:7-alpine
  minio:
    image: minio/minio
  api:
    build: .
    depends_on: [postgres, redis, minio]
    environment:
      DATABASE_URL: postgresql+asyncpg://...
      REDIS_URL: redis://redis:6379/0
      S3_ENDPOINT: http://minio:9000
```

Opcional em dev: **LangGraph Studio** / API local para debug de grafos.

## Deploy produção (caminhos)

### Opção A — PaaS (recomendado para MVP)

- **Fly.io** ou **Railway**: API + worker no mesmo app; Postgres gerenciado; bucket S3 (Cloudflare R2).
- Vantagem: poucos arquivos de infra, deploy em minutos.
- Worker separado para jobs OCR/async subagents.

### Opção B — VPS + Compose

- Um servidor (Hetzner, DigitalOcean) com Compose, Caddy como reverse proxy, TLS automático.
- Custo previsível; você gerencia patches.

### Opção C — Kubernetes

- Só quando houver necessidade real (múltiplos serviços, autoscaling fino, equipe ops).
- Separar deployment `api` e `agent-worker` com HPA em CPU e fila Redis.

## Rede e BFF

```
Internet → CDN (assets) → WAF/reverse proxy → BFF (HTTPS)
                              ↓
                    Domain + Agent (rede privada)
                              ↓
                    PostgreSQL / Redis (não público)
```

- CORS restrito ao domínio do frontend.
- SSE/WebSocket apenas no BFF; agent service não exposto publicamente.

## Segurança

| Tópico | Prática |
|--------|---------|
| Secrets | Doppler, Infisical ou secrets do PaaS; rotação de API keys LLM |
| Dados em repouso | Postgres com encryption at rest (provedor); SSE-S3 |
| Dados em trânsito | TLS 1.2+ everywhere |
| RBAC | Políticas na Domain API; JWT com `sub`, `campaign_roles` |
| Agent service | mTLS ou rede interna + token serviço; validar `sheet_id` pertence ao usuário da thread |
| Uploads | Limite de tamanho, antivírus opcional (ClamAV), tipos MIME permitidos |
| LGPD | Export/delete de conta; política de retenção de threads |
| Prompt injection | Tools só leem IDs validados; sem SQL livre; instruções em skills não substituem auth |

## Observabilidade

| Ferramenta | Uso |
|------------|-----|
| **LangSmith** | Traces de agente, datasets de eval, regressão de prompts |
| **OpenTelemetry** | Traces HTTP + DB no FastAPI |
| **Prometheus + Grafana** ou provedor (Datadog) | Latência p95 BFF, fila Redis, erros 5xx |
| **Sentry** | Exceções Python e frontend |

Alertas mínimos: taxa de erro > 1%, latência BFF > 3s, fila OCR > 50 jobs, custo diário LLM acima do orçamento.

## Backup e DR

- Postgres: snapshot diário + PITR se disponível no provedor.
- Object storage: versionamento de bucket.
- Checkpoints LangGraph: incluir no backup do Postgres se usar mesmo cluster; documentar restore de `thread_id`.

RPO alvo MVP: 24h. RTO: 4h (aceitável para hobby/prosumer).

## CI/CD

```mermaid
flowchart LR
    PR[Pull Request] --> Validate[rpg validate specs/]
    Validate --> Compile[rpg compile --target all]
    Compile --> Lint[lint + typecheck]
    Lint --> Test[pytest domain]
    Test --> Eval[evals agent smoke]
    Eval --> Merge[merge main]
    Merge --> Deploy[deploy staging]
    Deploy --> Manual[approve prod]
```

- `rpg validate` + `rpg compile` em todo PR que toca `specs/` ou `packages/rpg_dsl/`.
- `pytest` para Domain API e tools (mocks LLM).
- Evals LangSmith em PRs que tocam `specs/agents/`, `specs/evals/` ou `services/agent/`.
- Migrações Alembic no deploy antes de subir tráfego.
- Política recomendada: **commitar `generated/`** para revisão de contrato em PR.

Detalhes do SDLC AI-native: [06-sdlc-ai-native.md](06-sdlc-ai-native.md).

## Custos (ordem de grandeza)

| Item | MVP (poucos usuários) | Escala moderada |
|------|----------------------|-----------------|
| Postgres gerenciado | $15–25/mês | $50–150/mês |
| API hosting | $5–20/mês | $50–200/mês |
| S3/R2 | < $5/mês | $10–50/mês |
| LLM | variável | maior custo — cache, modelos menores para subagentes, limites por usuário |

Implementar **quota por campanha** (mensagens/dia) no BFF para evitar surpresa.

## Variáveis de ambiente (checklist)

```bash
# App
ENVIRONMENT=production
DATABASE_URL=
REDIS_URL=

# Storage
S3_ENDPOINT=
S3_BUCKET=
S3_ACCESS_KEY=
S3_SECRET_KEY=

# Auth (exemplo Clerk)
CLERK_SECRET_KEY=
JWT_ISSUER=

# Agent
AGENT_MODEL=openai:gpt-5.4
OPENAI_API_KEY=
LANGCHAIN_API_KEY=
LANGCHAIN_TRACING_V2=true
LANGCHAIN_PROJECT=rpg-op

# Internal
DOMAIN_API_INTERNAL_URL=http://domain:8001
AGENT_SERVICE_INTERNAL_URL=http://agent:8002
SERVICE_TOKEN=
```

## Mobile (futuro)

- Mesmos endpoints `/v1/*` do BFF.
- OAuth PKCE no app; refresh token seguro (Keychain/Keystore).
- Push notifications via fila (level up, import pronto) — Firebase/APNs; fora do MVP.

## Decisões a validar com você

1. **Ficha exemplo** — pode enviar PDF/foto anonimizada da mesa para fixture de eval?
2. **Self-host vs SaaS** para auth e deploy
3. **Campos só-GM** — exemplos do que jogador não deve editar (XP, aprovações, etc.)
4. **Análise async** — GM espera na tela ou recebe notificação quando análise terminar?
