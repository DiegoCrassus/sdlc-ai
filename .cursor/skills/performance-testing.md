# Skill: Performance Testing

## Purpose

Detectar regressões de performance antes do deploy, medindo latência, throughput e uso de recursos sob carga realista, usando k6 como ferramenta principal.

## When to use

- Em PRs que afetam endpoints de alta frequência ou queries de banco
- Antes de qualquer deploy para produção
- Após mudanças no schema de banco ou índices
- Após adicionar/modificar cache Redis

## Required inputs

- Stack rodando em ambiente de teste (use `container-validation.md`)
- `app/backend/tests/performance/` — scripts k6
- Baselines de performance anteriores (em `.sdlc/memory/`)

## Procedure

```bash
# 1. Instalar k6
brew install k6
# ou: docker pull grafana/k6

# 2. Executar teste de carga
k6 run \
  --out json=k6-results.json \
  --vus 10 \
  --duration 30s \
  app/backend/tests/performance/load-test.js

# 3. Smoke test (1 VU, 1 min) para detectar erros básicos
k6 run --vus 1 --duration 60s \
  app/backend/tests/performance/smoke-test.js

# 4. Comparar com baseline
python3 .sdlc/dsl/perf_compare.py \
  --current k6-results.json \
  --baseline .sdlc/memory/perf-baseline.json \
  --threshold 20  # % de regressão aceitável
```

## Thresholds de baseline (padrão)

| Métrica | Threshold de alerta | Threshold de bloqueio |
|---------|--------------------|-----------------------|
| p95 latência | > 200ms (+20% do baseline) | > 500ms |
| p99 latência | > 500ms (+30% do baseline) | > 2000ms |
| Error rate | > 0.1% | > 1% |
| Throughput | < 80% do baseline | < 60% do baseline |
| CPU uso médio | > 70% | > 90% |

## Template de script k6

```javascript
// app/backend/tests/performance/load-test.js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { Rate } from 'k6/metrics';

const errorRate = new Rate('error_rate');

export const options = {
  vus: 10,
  duration: '30s',
  thresholds: {
    http_req_duration: ['p(95)<200'],
    error_rate: ['rate<0.01'],
  },
};

export default function () {
  const res = http.get(`${__ENV.BASE_URL}/api/v1/investments`);
  check(res, { 'status 200': (r) => r.status === 200 });
  errorRate.add(res.status !== 200);
  sleep(1);
}
```

## Outputs

- `k6-results.json` com métricas completas
- Relatório de comparação com baseline (% de mudança por métrica)
- Código de saída: 0 (dentro dos thresholds) ou 1 (regressão detectada)

## Validation checklist

- [ ] Smoke test passa sem erros
- [ ] p95 dentro do threshold
- [ ] Error rate < 0.1%
- [ ] Nenhuma query N+1 detectada (via OTel traces)
- [ ] Redis hit rate > 80% para endpoints cacheados

## Failure modes

| Falha | Causa comum | Ação |
|-------|-------------|------|
| Regressão de latência | Query sem índice | Reportar ao Implementer + sugerir `EXPLAIN ANALYZE` |
| Error rate alta | Bug em endpoint | Reportar ao QA como CA não atendido |
| Throughput baixo | Lock de banco | Revisar transações com Architect |
| Degradação com Redis | Cache miss alto | Verificar TTL e invalidação de cache |
