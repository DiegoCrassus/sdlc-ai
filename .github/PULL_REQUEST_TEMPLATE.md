## Summary

<!-- 1–3 frases: o que e por quê -->

## SDLC checklist

- [ ] **Plane** — task `RPG-N` linkada
- [ ] **Branch** — `feature/RPG-N` ou `bugfix/RPG-N`, criada a partir de `develop`
- [ ] **Base** — PR aponta para `develop`
- [ ] **Local gates** — `make test`, `make lint` e `make validate` verdes
- [ ] **Actions** — lint e testes unitários verdes no head SHA mais recente
- [ ] **Owner approval** — aprovação humana antes do merge

## Test plan

- [ ] `make test`
- [ ] `make lint`
- [ ] `make validate`
- [ ] Smoke/API manual, se aplicável
- [ ] UI manual, se frontend

## Plane / Issue

Plane: `RPG-`
Issue: closes #

## Notas

<!-- decisões, dívida técnica, follow-ups -->
