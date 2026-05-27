# Skill: IaC Generation

## Purpose

Gerar módulos Terraform reproduzíveis para os serviços da stack (PostgreSQL, Redis, backend, frontend) a partir da definição de arquitetura em `docs/architecture/`, garantindo que a infraestrutura seja provisionada de forma determinística e sem intervenção humana.

## When to use

- Após o Architect finalizar o `docs/architecture/overview.md` e os ADRs
- Quando o Implementer precisar de um ambiente de staging ou produção para testes de integração
- Como gate do estágio de Deployment: IaC deve existir e ser válido antes do deploy

## Required inputs

- `docs/architecture/overview.md` — define os serviços e suas configurações
- `docs/architecture/decisions.md` — ADRs com decisões de infraestrutura
- `.sdlc/memory/architecture.md` — constraints de infraestrutura
- Variáveis de ambiente: `TF_VAR_*` para credenciais e configurações

## Procedure

### 1. Gerar estrutura base

```
app/infra/terraform/
├── main.tf            ← provider config + workspace
├── variables.tf       ← todas as variáveis configuráveis
├── outputs.tf         ← outputs para outros módulos
├── modules/
│   ├── database/      ← PostgreSQL (RDS / Cloud SQL / local)
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── cache/         ← Redis (ElastiCache / Azure Cache / local)
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   ├── backend/       ← Container service (ECS / Cloud Run / Docker)
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   └── outputs.tf
│   └── frontend/      ← CDN / static hosting (CloudFront / Vercel / nginx)
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
└── environments/
    ├── local.tfvars   ← variáveis para Docker Compose local
    └── staging.tfvars ← variáveis para ambiente de staging
```

### 2. Validar IaC gerado

```bash
cd app/infra/terraform
terraform init -backend=false
terraform validate
terraform fmt -check

# Para ambiente local com Docker
terraform plan -var-file=environments/local.tfvars -out=plan.tfplan
```

### 3. Template de módulo database (PostgreSQL)

```hcl
# app/infra/terraform/modules/database/main.tf
variable "db_name"     { type = string }
variable "db_user"     { type = string }
variable "db_password" { type = string; sensitive = true }
variable "db_port"     { type = number; default = 5432 }
variable "environment" { type = string; default = "local" }

resource "docker_container" "postgres" {
  count = var.environment == "local" ? 1 : 0
  name  = "postgres-${var.environment}"
  image = "postgres:16-alpine"
  env = [
    "POSTGRES_DB=${var.db_name}",
    "POSTGRES_USER=${var.db_user}",
    "POSTGRES_PASSWORD=${var.db_password}",
  ]
  ports { internal = 5432; external = var.db_port }
}

output "connection_string" {
  value     = "postgresql://${var.db_user}:${var.db_password}@localhost:${var.db_port}/${var.db_name}"
  sensitive = true
}
```

### 4. Template de módulo cache (Redis)

```hcl
# app/infra/terraform/modules/cache/main.tf
variable "redis_port"  { type = number; default = 6379 }
variable "environment" { type = string; default = "local" }

resource "docker_container" "redis" {
  count = var.environment == "local" ? 1 : 0
  name  = "redis-${var.environment}"
  image = "redis:7-alpine"
  command = ["redis-server", "--save", "", "--loglevel", "warning"]
  ports { internal = 6379; external = var.redis_port }
}

output "redis_url" {
  value = "redis://localhost:${var.redis_port}"
}
```

## Outputs

- `app/infra/terraform/` com todos os módulos gerados
- `terraform validate` passa sem erros
- `terraform plan` produz plano sem erros de sintaxe
- Outputs documentados em `outputs.tf` para consumo pelo backend

## Validation checklist

- [ ] `terraform init -backend=false` sem erros
- [ ] `terraform validate` passa
- [ ] `terraform fmt -check` sem diferenças (código formatado)
- [ ] Nenhuma credencial hardcoded — tudo em `variables.tf` com `sensitive = true`
- [ ] `environments/local.tfvars` existe e provê todos os valores necessários
- [ ] Outputs incluem connection strings para banco e cache

## Failure modes

| Falha | Causa | Ação |
|-------|-------|------|
| `terraform validate` falha | Syntax error no HCL | Corrigir conforme output do validate |
| Provider não encontrado | `terraform init` não executado | Executar `terraform init -backend=false` primeiro |
| Variável sensível exposta | Hardcoded no código | Mover para `variables.tf` com `sensitive = true` |
| Module não encontrado | Path incorreto em `source` | Verificar estrutura de diretórios |
