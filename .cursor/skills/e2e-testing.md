# Skill: E2E Testing

## Purpose

Validar o sistema de ponta a ponta usando um browser headless (Playwright), garantindo que os fluxos críticos do usuário funcionam com frontend e backend integrados, antes de qualquer PR ser mergeado.

## When to use

- Em todo PR que modifica `app/frontend/` ou endpoints de `app/backend/`
- Como gate obrigatório do QA para fluxos que envolvem UI
- Após testes unitários e de integração passarem

## Required inputs

- Stack completa rodando (use `container-validation.md` primeiro)
- `app/frontend/e2e/` — arquivos de testes Playwright
- `BASE_URL` da aplicação (ex: `http://localhost:3000`)

## Procedure

```bash
# 1. Garantir stack rodando
docker compose -f app/infra/docker-compose.yml up -d
sleep 15

# 2. Instalar Playwright (se não instalado)
cd app/frontend
npx playwright install --with-deps chromium

# 3. Executar testes E2E
BASE_URL=http://localhost:3000 npx playwright test \
  --reporter=json \
  --output=test-results/ \
  2>&1 | tee e2e-results.log

# 4. Capturar artefatos de falha
# Playwright auto-salva screenshots + vídeos em test-results/ para testes que falham

# 5. Teardown
docker compose down -v
```

## Critérios de cobertura mínima

| Fluxo | Tipo de teste |
|-------|--------------|
| Login / logout | Autenticação |
| CRUD principal do domínio | Funcionalidade core |
| Formulário com validação | Inputs |
| Listagem + paginação | Data display |
| Erro de API (mock 500) | Resiliência |
| Redirecionamento autenticado | Navegação |

## Outputs

- JSON com resultado por teste (pass/fail/flaky)
- Screenshots e vídeos dos testes que falharam
- Taxa de sucesso: N/M testes passando
- Código de saída: 0 (todos passaram) ou 1 (qualquer falha não flaky)

## Validation checklist

- [ ] Todos os fluxos críticos têm cobertura E2E
- [ ] Testes não dependem de dados externos — usam seeds controlados
- [ ] Testes são determinísticos — sem `sleep` arbitrários
- [ ] Screenshots salvas para testes que falham
- [ ] Taxa de flakiness < 5%

## Failure modes

| Falha | Causa comum | Ação |
|-------|-------------|------|
| Timeout em elemento | UI lenta ou elemento não existe | Aumentar seletores; verificar se componente foi criado |
| 404 em rota | Roteamento frontend quebrado | Reportar ao Implementer |
| API error 500 durante teste | Bug no backend exposto pelo E2E | Reportar ao QA como critério de aceite não atendido |
| Teste flaky | Race condition na UI | Usar `waitForSelector` + `expect.poll` |
