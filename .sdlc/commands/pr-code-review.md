# Command: PR Code Review

## Objetivo

Acionar revisão técnica autônoma quando uma PR é criada ou atualizada.

## Procedimento

1. Ler PR, commits, arquivos alterados e issue/Plane relacionados.
2. Verificar aderência ao SDLC: spec, compile, generated, validação e evidências.
3. Revisar bugs, segurança, regressões, testes ausentes e riscos de execução.
4. Publicar comentário com findings ordenados por severidade.
5. Se houver bloqueio, criar ou linkar issue para `issue-resolver`.

## Saída

- Comentário de review no PR.
- Status de aprovação recomendada ou bloqueio.
- Link para issue corretiva quando aplicável.
