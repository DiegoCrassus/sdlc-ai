# Supabase MCP

Integra o Cursor ao Supabase via MCP remoto oficial.

## Configuração

Arquivo: `.cursor/mcp.json`

```json
{
  "mcpServers": {
    "supabase": {
      "type": "http",
      "url": "https://mcp.supabase.com/mcp?project_ref=${env:SUPABASE_PROJECT_REF}&read_only=true",
      "headers": {
        "Authorization": "Bearer ${env:SUPABASE_ACCESS_TOKEN}"
      }
    }
  }
}
```

## Variáveis

```bash
SUPABASE_ACCESS_TOKEN=
SUPABASE_PROJECT_REF=
```

Como obter:

1. `SUPABASE_ACCESS_TOKEN`: Supabase Dashboard → Account → Access Tokens.
2. `SUPABASE_PROJECT_REF`: Project Settings → General → Reference ID.

## Uso

1. Preencha as variáveis no `.env`.
2. Abra o Cursor via `./launch.sh` para o processo herdar as envs.
3. Reinicie ou recarregue o Cursor.
4. Confirme em Cursor Settings → Tools & MCP que `supabase` está conectado.

## Segurança

- O MCP está configurado com `read_only=true`.
- Não conecte este MCP a dados de produção para operações destrutivas.
- Não commite `SUPABASE_ACCESS_TOKEN`.
- Use um PAT dedicado para Cursor/MCP e revogue se houver suspeita de vazamento.
