"""BFF smoke coverage for campaign, sheet and template MVP flows."""

import struct
import zlib

import pytest
from app.database import init_db
from app.main import app
from httpx import ASGITransport, AsyncClient


def tiny_png() -> bytes:
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    ihdr_chunk = b"IHDR" + ihdr
    ihdr_crc = struct.pack(">I", zlib.crc32(ihdr_chunk) & 0xFFFFFFFF)
    raw = b"\x00" + b"\xff\x00\x00"
    compressed = zlib.compress(raw)
    idat_chunk = b"IDAT" + compressed
    idat_crc = struct.pack(">I", zlib.crc32(idat_chunk) & 0xFFFFFFFF)
    return (
        sig
        + struct.pack(">I", 13)
        + ihdr_chunk
        + ihdr_crc
        + struct.pack(">I", len(compressed))
        + idat_chunk
        + idat_crc
        + struct.pack(">I", 0)
        + b"IEND"
        + struct.pack(">I", zlib.crc32(b"IEND") & 0xFFFFFFFF)
    )


@pytest.mark.asyncio
async def test_campaign_sheet_template_flow() -> None:
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        created = await client.post(
            "/v1/campaigns",
            data={
                "name": "Mesa Teste",
                "description": "Fluxo MVP",
                "version": "1.0.0",
                "max_members": "4",
            },
            files={"template_image": ("sheet.png", tiny_png(), "image/png")},
        )
        assert created.status_code == 201
        campaign_id = created.json()["id"]

        sheets = await client.get(f"/v1/campaigns/{campaign_id}/sheets")
        assert sheets.status_code == 200
        sheet_id = sheets.json()["sheets"][0]["id"]

        updated = await client.put(
            f"/v1/sheets/{sheet_id}",
            json={"data": {"character_name": "Lyra Updated", "level": 6}},
        )
        assert updated.status_code == 200
        body = updated.json()
        assert body["data"]["character_name"] == "Lyra Updated"
        assert body["revision"] == 2

        analysis = await client.post(
            f"/v1/campaigns/{campaign_id}/template/source",
            files={"template_source": ("draft.png", tiny_png(), "image/png")},
        )
        assert analysis.status_code == 200
        assert analysis.json()["template"]["status"] == "draft"

        published = await client.post(
            f"/v1/campaigns/{campaign_id}/template/publish",
            json={"confirm": True},
        )
        assert published.status_code == 200
        assert published.json()["status"] == "published"

        extension = await client.post(
            f"/v1/campaigns/{campaign_id}/template/extend",
            json={
                "section_title": "Inventário",
                "field_key": "inventory",
                "field_label": "Inventário",
                "field_type": "text",
            },
        )
        assert extension.status_code == 200

        extended_sheet = await client.get(f"/v1/sheets/{sheet_id}")
        assert extended_sheet.status_code == 200
        assert "inventory" in extended_sheet.json()["schema_data"]["fields"]
