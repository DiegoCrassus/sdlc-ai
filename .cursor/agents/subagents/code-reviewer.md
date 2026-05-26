# Code Reviewer Adapter

YAML canônico: `.sdlc/agents/subagents/code-reviewer.yaml`

Use quando uma PR for criada ou atualizada e precisar de revisão técnica SDLC.

## No Cursor

- Leia o YAML canônico e a skill `.sdlc/skills/pr-code-review/`.
- Priorize bugs, riscos, testes, segurança, branch naming e rastreabilidade Plane/GitHub.
- Se houver bloqueio, crie/linke issue e delegue ao `issue-resolver`.
- Após a correção, retorne ao PR e rode validação pós-issue.
- Não faça merge sem aprovação humana explícita; comente o motivo quando o PR permanecer bloqueado.
