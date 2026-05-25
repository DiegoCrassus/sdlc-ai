"""Apply published template version to all workspace sheets."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import dumps_json, loads_json
from app.models import ExampleSheet, Sheet, Workspace
from app.services.provisioning import empty_defaults
from app.services.template_extend import merge_new_fields_into_sheet


async def collect_sheet_data(db: AsyncSession, workspace_id: str) -> list[dict]:
    result = await db.execute(
        select(Sheet).join(Character).where(Sheet.workspace_id == workspace_id)
    )
    out: list[dict] = []
    for sheet in result.scalars().all():
        data = loads_json(sheet.data_json)
        if isinstance(data, dict):
            out.append(data)
    return out


async def migrate_sheets_to_template(
    db: AsyncSession,
    workspace: Workspace,
    schema: dict,
    *,
    previous_field_keys: set[str],
) -> None:
    result = await db.execute(select(Sheet).where(Sheet.workspace_id == workspace.id))
    now = datetime.now(timezone.utc)
    for sheet in result.scalars().all():
        data = loads_json(sheet.data_json)
        if not isinstance(data, dict):
            continue
        merged = merge_new_fields_into_sheet(data, schema, previous_field_keys)
        sheet.data_json = dumps_json(merged)
        sheet.template_version = workspace.template_version
        sheet.updated_at = now

    ex = await db.execute(select(ExampleSheet).where(ExampleSheet.workspace_id == workspace.id))
    example = ex.scalar_one_or_none()
    if example:
        data = loads_json(example.data_json)
        if isinstance(data, dict):
            if previous_field_keys:
                example.data_json = dumps_json(
                    merge_new_fields_into_sheet(data, schema, previous_field_keys)
                )
            else:
                example.data_json = dumps_json(empty_defaults(schema))
            example.label = f"Ficha exemplo — template v{workspace.template_version}"


def schema_field_keys(schema: dict) -> set[str]:
    fields = schema.get("fields") or {}
    return set(fields.keys()) if isinstance(fields, dict) else set()
