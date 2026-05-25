# Command: Issue Resolution Validation

## Objetivo

Validar que uma issue resolvida realmente ficou fechada por evidências: fix no PR,
Actions verdes, review pós-correção, card Plane atualizado e integração em
`develop` quando permitido.

## Procedimento

1. Ler issue, PR, branch, commit e card Plane relacionados.
2. Confirmar que o commit de correção está no head do PR.
3. Conferir Actions obrigatórias no SHA atual, não em SHA antigo.
4. Acionar `code-reviewer` novamente após a correção.
5. Se não houver bloqueios e a base for `develop`, aprovar/mergear de forma autônoma.
6. Se não mergear, comentar no PR e issue o motivo exato:
   - checks pendentes ou falhos;
   - PR não mergeable;
   - base diferente de `develop`;
   - branch protection exigindo ação humana;
   - blocker de review ainda aberto.
7. Só fechar issue após evidência completa.

## Saída Esperada

- Issue fechada ou comentário explicando por que permanece aberta.
- PR mergeado em `develop` ou comentário de bloqueio.
- Card Plane com evidência final.

## Guardrails

- Não burlar proteção de branch.
- Não fechar issue com PR aberto e sem justificativa.
- Não considerar checks verdes se forem de commit antigo.
