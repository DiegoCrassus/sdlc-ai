# Skill: Container Validation

## Purpose

Verificar que o Docker build e o `docker compose up` passam antes de qualquer PR ser mergeado, garantindo que a stack completa sobe corretamente no ambiente de CI.

## When to use

- Após qualquer alteração em `Dockerfile*`, `docker-compose*.yml`, `pyproject.toml`, `requirements.txt`, `package.json`
- Como gate obrigatório no CI após os testes unitários e antes dos testes de integração

## Required inputs

- `app/infra/docker-compose.yml` (ou `docker-compose.dev.yml`)
- Dockerfiles de cada serviço
- `.env.example` (variáveis necessárias)

## Procedure

```bash
# 1. Validar sintaxe dos Dockerfiles (sem build)
docker build --check -f app/infra/docker/Dockerfile.backend .
docker build --check -f app/infra/docker/Dockerfile.frontend .

# 2. Build completo de cada imagem
docker compose -f app/infra/docker-compose.yml build --no-cache 2>&1 | tee build.log
BUILD_EXIT=$?

# 3. Se build passou, subir a stack
if [ $BUILD_EXIT -eq 0 ]; then
  docker compose -f app/infra/docker-compose.yml up -d
  sleep 10  # aguardar services ficarem healthy

  # 4. Health checks de cada serviço
  docker compose ps --format json | python3 -c "
import json, sys
services = [json.loads(l) for l in sys.stdin]
failed = [s for s in services if s.get('Health') not in ('healthy', '')]
if failed:
    print('FAIL:', [s['Service'] for s in failed])
    sys.exit(1)
print('PASS: all services healthy')
"

  # 5. Teardown
  docker compose -f app/infra/docker-compose.yml down -v
fi

exit $BUILD_EXIT
```

## Outputs

- Log de build (stdout + stderr)
- Status de health de cada container
- Código de saída: 0 (todos healthy) ou 1 (qualquer falha)

## Validation checklist

- [ ] `docker build` passou sem erros para cada imagem
- [ ] Nenhum `docker compose up` ficou em `unhealthy` por mais de 30s
- [ ] Backend `/health` retorna 200 após `up`
- [ ] PostgreSQL aceita conexão após `up`
- [ ] Redis aceita `PING` após `up`
- [ ] Nenhum segredo hardcoded nas imagens (verificar com `docker inspect`)

## Failure modes

| Falha | Causa comum | Ação |
|-------|-------------|------|
| Build error | Dependência ausente no Dockerfile | Reportar ao Implementer |
| Container unhealthy | Env var faltando | Verificar `.env.example` e reportar ao DevOps |
| Port conflict | Porta já em uso no CI | Usar portas alternativas no docker-compose.ci.yml |
| Build timeout | Layer cache inválido ou imagem base lenta | Otimizar Dockerfile com multi-stage build |
