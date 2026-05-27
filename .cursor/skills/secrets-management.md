# Skill: Secrets Management

## Purpose

Garantir que nenhum segredo (chaves de API, senhas, tokens, certificados) seja commitado no repositório, usando verificação automática em cada commit e em cada PR.

## When to use

- Como hook pré-commit em toda máquina de desenvolvimento
- Como gate obrigatório no CI antes de qualquer outro check
- Ao revisar PRs que alteram arquivos de configuração ou infraestrutura

## Required inputs

- Diff do PR ou arquivos staged para commit
- `.gitleaks.toml` (regras personalizadas — opcional)
- Lista de allowlist para falsos positivos conhecidos

## Procedure

### Pré-commit (local)

```bash
# Instalar gitleaks
brew install gitleaks
# ou: pip install gitleaks-python / download binary

# Configurar hook pré-commit (.git/hooks/pre-commit)
cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
gitleaks protect --staged --redact --exit-code 1
if [ $? -ne 0 ]; then
  echo "ERROR: Segredo detectado no staged diff. Remova antes de commitar."
  exit 1
fi
EOF
chmod +x .git/hooks/pre-commit
```

### CI (por PR)

```bash
# Escanear o repositório completo
gitleaks detect --source . \
  --report-format json \
  --report-path gitleaks-report.json \
  --redact \
  --exit-code 1

# Escanear apenas o diff do PR
gitleaks detect --source . \
  --log-opts="origin/develop..HEAD" \
  --report-format json \
  --exit-code 1
```

### Padrões detectados automaticamente

| Tipo | Exemplos |
|------|---------|
| AWS keys | `AKIA...`, `aws_secret_access_key` |
| GitHub tokens | `ghp_`, `github_pat_` |
| OpenAI keys | `sk-proj-`, `sk-` |
| Stripe keys | `sk_live_`, `pk_live_` |
| Private keys | `-----BEGIN RSA PRIVATE KEY-----` |
| Database URLs | `postgres://user:password@host` |
| JWT secrets | `JWT_SECRET=`, `SECRET_KEY=` |
| Qualquer padrão `= "sk-"`, `= "key-"` | Heurística genérica |

## Regras do .env

- `.env` deve estar em `.gitignore` — nunca commitado
- `.env.example` deve conter apenas chaves sem valores reais
- Comentar no `.env.example` qual serviço cada variável pertence

```bash
# Verificar que .env está ignorado
git check-ignore .env || echo "AVISO: .env não está no .gitignore"

# Verificar que .env.example não tem valores reais
grep -E "=.{8,}" .env.example | grep -v "^#" | grep -v "=your_" | grep -v "=<" | grep -v "=placeholder"
```

## Outputs

- `gitleaks-report.json` com todos os findings
- Lista de arquivos + linhas onde segredos foram detectados
- Código de saída: 0 (limpo) ou 1 (segredo detectado)

## Validation checklist

- [ ] Hook pré-commit instalado e funcionando
- [ ] `.env` está no `.gitignore`
- [ ] `.env.example` não contém valores reais
- [ ] CI gate de gitleaks está ativo no workflow
- [ ] Nenhum `console.log()` ou `print()` expondo variáveis de ambiente

## Failure modes

| Falha | Ação imediata |
|-------|---------------|
| Segredo encontrado no diff | Remover do código, revogar credencial, force push se necessário |
| Segredo encontrado em commit antigo | `git filter-repo` para remover da história + revogar |
| Falso positivo bloqueando CI | Adicionar ao allowlist em `.gitleaks.toml` com justificativa |
| `.env` commitado acidentalmente | Remover do histórico imediatamente + revogar todas as credenciais do arquivo |
