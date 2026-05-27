# Command: SDLC Audit

## Purpose

Executar uma auditoria 100% autônoma do SDLC completo — estrutura, subagentes, skills, MCP, pipeline, observabilidade, gaps e CI/CD — gerando um canvas interativo de relatório com scores de autonomia.

## When to run

- `/sdlc-audit` — auditoria completa
- Após adição ou modificação de subagentes, skills ou configurações SDLC
- Antes de uma retrospectiva ou planejamento de sprint
- Quando o score de autonomia precisa ser avaliado

## Required context

- Acesso ao repositório completo
- Python 3.8+ disponível
- `app/infra/sdlc_obs/auditor.py` presente

## Execution procedure

### 1. Executar o auditor

```bash
python app/infra/sdlc_obs/auditor.py
```

O script:
- Roda ~8 categorias de checks automaticamente
- Gera o canvas em `~/.cursor/projects/.../canvases/sdlc-audit-report.canvas.tsx`
- Imprime resultado no terminal
- Retorna exit code 0 (sem FAILs) ou 1 (há FAILs)

### 2. Interpretar output

Ler o output e identificar:
- Autonomy Score (%)
- Health Score (%)
- Counts: PASS / WARN / FAIL
- Lista de FAILs com recomendações

### 3. Apresentar ao usuário

```markdown
## Resultado da Auditoria SDLC

**Autonomy Score:** X% | **Health Score:** Y%

**Resumo:** Z checks executados — A PASS / B WARN / C FAIL

### Gaps Críticos (FAIL)
1. [categoria] check — recomendação
2. ...

### Avisos (WARN)
1. ...

### Próximos passos
1. Fechar os FAILs de maior impacto
2. Planejar sprint para gaps da simulação
```

### 4. Criar Issues GitHub (se FAILs encontrados)

Para cada FAIL de categoria "Gaps da Simulação" ou "Pipeline":
```
github.createIssue(
  title="[SDLC Gap] <check>",
  body="<detail>\n\n## Recomendação\n<recommendation>",
  labels=["sdlc-gap", "priority:high"]
)
```

### 5. Abrir canvas

Informar ao usuário o path do canvas gerado e sugerir abertura.

## Expected outputs

- Terminal com todos os checks impressos
- Canvas `sdlc-audit-report.canvas.tsx` gerado com dados reais
- Resumo em texto no chat
- Issues GitHub criadas para FAILs críticos (opcional)

## Validation

- [ ] `auditor.py` executou sem erro de Python
- [ ] Canvas foi gerado com dados reais (não placeholder)
- [ ] Autonomy Score calculado corretamente
- [ ] Recomendações apresentadas em ordem de prioridade (FAIL primeiro)
- [ ] Usuário informado sobre path do canvas

## Failure modes

| Falha | Causa | Ação |
|-------|-------|------|
| `ModuleNotFoundError` | Python path incorreto | Executar do root do repositório |
| Canvas não gerado | Path do diretório canvases não encontrado | Auditor cria automaticamente; verificar permissões |
| Exit code 1 | FAILs encontrados | Listar FAILs e recomendar ações |
| `make sdlc-doctor` falha | Estrutura SDLC degradada | Corrigir com `make sdlc-doctor` primeiro |
