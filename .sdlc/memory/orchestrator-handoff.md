# Orchestrator Handoff (latest)

```yaml
intent: GREENFIELD
confidence: 0.95
greenfield_signals: [user_words, repense_do_zero]
scope_hint: MarketPulse — dashboard financeiro/cripto mock-first com provider pattern
requires_plane: true
requires_branch: true
autonomous: true
card: INVES-27
branch: feature/INVES-27-marketpulse-dashboard
next_agent: implementer
rationale: |
  Usuario pediu app greenfield para acompanhar mercado financeiro e cripto.
  Dados mockados, preparado para APIs reais. Deep research concluido.
  Plano validado no Plane. Gate aberto para implementation.
api_research_summary: |
  Primary future provider: Twelve Data (800 req/day free, multi-asset).
  Prototype: Alpha Vantage (25/day, broad coverage).
  Real-time US: Polygon/Massive, Finnhub WebSocket.
  Crypto-only: CoinGecko (no key, research).
  Architecture: Provider interface + Mock default + env MARKET_DATA_PROVIDER.
```
