"""Smoke test for workspace API."""

import json
import struct
import zlib
from urllib import request


def tiny_png() -> bytes:
    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", 1, 1, 8, 2, 0, 0, 0)
    ihdr_chunk = b"IHDR" + ihdr
    ihdr_crc = struct.pack(">I", zlib.crc32(ihdr_chunk) & 0xFFFFFFFF)
    raw = b"\x00" + b"\xff\x00\x00"
    compressed = zlib.compress(raw)
    idat_chunk = b"IDAT" + compressed
    idat_crc = struct.pack(">I", zlib.crc32(idat_chunk) & 0xFFFFFFFF)
    iend = struct.pack(">I", 0) + b"IEND" + struct.pack(">I", zlib.crc32(b"IEND") & 0xFFFFFFFF)
    return (
        sig
        + struct.pack(">I", 13)
        + ihdr_chunk
        + ihdr_crc
        + struct.pack(">I", len(compressed))
        + idat_chunk
        + idat_crc
        + iend
    )


def main() -> None:
    with request.urlopen("http://127.0.0.1:8000/v1/workspaces") as resp:
        workspaces = json.loads(resp.read())
        example = next((w for w in workspaces if w.get("is_example")), None)
        print("list ok", len(workspaces), "example=", example["name"] if example else None)

    png = tiny_png()
    boundary = "----RpgOpTest"
    parts: list[bytes] = []
    for key, val in [
        ("name", "Test Mesa"),
        ("master_name", "Mestre Teste"),
        ("description", "Workspace de teste"),
        ("version", "0.1.0"),
        ("max_members", "5"),
        ("sheet_source", "file"),
        ("sheet_json", ""),
        ("sheet_text", ""),
    ]:
        parts.append(
            f'--{boundary}\r\nContent-Disposition: form-data; name="{key}"\r\n\r\n{val}\r\n'.encode()
        )
    parts.append(
        f'--{boundary}\r\nContent-Disposition: form-data; name="template_image"; filename="sheet.png"\r\nContent-Type: image/png\r\n\r\n'.encode()
    )
    parts.append(png)
    parts.append(f"\r\n--{boundary}--\r\n".encode())
    body = b"".join(parts)

    req = request.Request(
        "http://127.0.0.1:8000/v1/workspaces",
        data=body,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
    )
    with request.urlopen(req) as resp:
        workspace = json.loads(resp.read())
        wid = workspace["id"]
        print("create ok", wid, workspace["master_name"])

    with request.urlopen(f"http://127.0.0.1:8000/v1/workspaces/{wid}/example-sheet") as resp:
        example = json.loads(resp.read())
        fields = example.get("schema_data", {}).get("fields") or {}
        if not fields:
            raise SystemExit("example-sheet missing schema fields")
        print("example ok", example.get("label"), f"({len(fields)} fields)")

    inv_body = json.dumps({"email": "a@b.com", "role": "player"}).encode()
    req2 = request.Request(
        f"http://127.0.0.1:8000/v1/workspaces/{wid}/invites",
        data=inv_body,
        method="POST",
        headers={"Content-Type": "application/json"},
    )
    with request.urlopen(req2) as resp:
        print("invite ok", resp.status)


if __name__ == "__main__":
    main()
