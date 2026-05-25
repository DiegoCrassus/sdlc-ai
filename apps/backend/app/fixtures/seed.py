"""Seed the D&D 5e example workspace and demo characters on startup."""

import uuid
from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import dumps_json
from app.fixtures.default_template import DEFAULT_CANVAS_SPEC, DEFAULT_SCHEMA, MOCK_SHEET_DATA
from app.models import EXAMPLE_WORKSPACE_ID, Character, ExampleSheet, Sheet, Workspace
from app.services.template_publish import schema_field_keys

_DEMO_CHARACTERS = [
    {
        "name": "Lyra Moonwhisper",
        "email": "lyra@jogador.dev",
        "data": MOCK_SHEET_DATA,
    },
    {
        "name": "Thorin Ironshield",
        "email": "thorin@jogador.dev",
        "data": {
            **MOCK_SHEET_DATA,
            "character_name": "Thorin Ironshield",
            "player_name": "Thorin",
            "class_name": "Fighter",
            "level": 4,
            "strength": 18,
            "constitution": 16,
        },
    },
]


async def ensure_example_workspace(session: AsyncSession) -> None:
    result = await session.execute(select(Workspace).where(Workspace.id == EXAMPLE_WORKSPACE_ID))
    workspace = result.scalar_one_or_none()
    if not workspace:
        now = datetime.now(timezone.utc)
        workspace = Workspace(
            id=EXAMPLE_WORKSPACE_ID,
            name="D&D 5e — Mesa de Exemplo",
            description=(
                "Workspace de referência com ficha D&D 5ª edição. "
                "Use como mock para explorar o canvas antes de criar sua mesa."
            ),
            master_name="Mestre Exemplo",
            version="5e",
            max_members=6,
            sheet_source="file",
            sheet_input_raw=None,
            template_image_path=None,
            schema_json=dumps_json(DEFAULT_SCHEMA),
            canvas_spec_json=dumps_json(DEFAULT_CANVAS_SPEC),
            analysis_json=dumps_json(
                {
                    "last_published_field_keys": list(schema_field_keys(DEFAULT_SCHEMA)),
                    "confidence": "high",
                    "warnings": [],
                }
            ),
            template_status="published",
            template_version=1,
            published_at=now,
            is_example=True,
        )
        workspace.example_sheet = ExampleSheet(
            workspace_id=EXAMPLE_WORKSPACE_ID,
            data_json=dumps_json(MOCK_SHEET_DATA),
            label="Ficha D&D 5e — Lyra Moonwhisper (mock)",
        )
        session.add(workspace)
        await session.commit()
    elif not workspace.analysis_json:
        workspace.analysis_json = dumps_json(
            {
                "last_published_field_keys": list(schema_field_keys(DEFAULT_SCHEMA)),
                "confidence": "high",
                "warnings": [],
            }
        )
        await session.commit()

    count = await session.execute(
        select(func.count())
        .select_from(Character)
        .where(Character.workspace_id == EXAMPLE_WORKSPACE_ID)
    )
    if count.scalar_one() > 0:
        return

    now = datetime.now(timezone.utc)
    for demo in _DEMO_CHARACTERS:
        char_id = str(uuid.uuid4())
        sheet_id = str(uuid.uuid4())
        data = {**demo["data"], "player_name": demo["email"].split("@")[0]}
        character = Character(
            id=char_id,
            workspace_id=EXAMPLE_WORKSPACE_ID,
            name=demo["name"],
            player_email=demo["email"],
        )
        character.sheet = Sheet(
            id=sheet_id,
            workspace_id=EXAMPLE_WORKSPACE_ID,
            character_id=char_id,
            template_version=1,
            data_json=dumps_json(data),
            revision=1,
            updated_at=now,
        )
        session.add(character)
    await session.commit()
