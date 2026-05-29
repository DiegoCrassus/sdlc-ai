# Doctor checks

> **Data:** `checks.yaml` · **Entry:** `.sdlc/sdlc.yaml` → `contract.modules.doctor`

## Tooling

- `doctor.py` → `doctor_health_canvas.py`
- **Every run:** Canvas `sdlc-doctor-health.canvas.tsx` + `.sdlc/memory/doctor-health.json`

## Edit checklist

1. Update `checks.yaml`
2. Run `make sdlc-doctor` and `make sdlc-validate`
