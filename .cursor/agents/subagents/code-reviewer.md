# Code Reviewer Adapter

YAML canônico: `.sdlc/agents/subagents/code-reviewer.yaml`

Use quando uma PR for criada ou atualizada e precisar de revisão técnica SDLC.

## No Cursor

- Leia o YAML canônico e a skill `.sdlc/skills/pr-code-review/`.
- Priorize bugs, riscos, testes, segurança, generated e rastreabilidade Plane/GitHub.
- Se houver bloqueio, crie/linke issue e delegue ao `issue-resolver`.
- Após a correção, retorne ao PR, rode validação pós-issue e aprove/mergeie até `develop` quando permitido.
- Se não fizer merge autônomo, comente no PR o motivo exato.
