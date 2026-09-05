"""Bounded byte acquisition and container checks shared by design/image freezing.

These checks reject empty/error/truncated payloads; a browser must still decode and
render fonts/images before visual verification can pass. Standard library only.
"""
from __future__ import annotations

import base64
import hashlib
import json
from pathlib import Path
import re
import struct
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
import zlib

MAX_BYTES = 32 * 1024 * 1024
MAX_INFLATED_BYTES = 64 * 1024 * 1024


def read_resource(source: str, base: str | None = None, metadata: dict | None = None) -> tuple[bytes, str]:
    """Read a full bounded payload. A local base confines paths, including symlinks."""
    if source.startswith('data:'):
        meta, separator, value = source[5:].partition(',')
        if not separator:
            raise ValueError('invalid data URL')
        data = base64.b64decode(re.sub(r'\s', '', value), validate=True) if ';base64' in meta else urllib.parse.unquote_to_bytes(value)
        mime = meta.split(';')[0]
    elif source.startswith(('https://', 'http://')):
        request = urllib.request.Request(source, headers={'User-Agent': 'dddjango-web-freeze/1'})
        with urllib.request.urlopen(request, timeout=20) as response:
            length = response.headers.get('Content-Length')
            if length and int(length) > MAX_BYTES:
                raise ValueError('payload exceeds 32 MiB')
            data = response.read(MAX_BYTES + 1)
            if length and len(data) != int(length):
                raise ValueError('incomplete HTTP response')
            mime = response.headers.get_content_type()
            if metadata is not None:
                metadata['final_url'] = response.geturl()
    else:
        parsed = urllib.parse.urlsplit(source)
        if parsed.scheme not in ('', 'file'):
            raise ValueError('unsupported source scheme')
        path = Path(urllib.parse.unquote(parsed.path))
        root = Path(base).resolve() if base is not None else None
        path = ((root / path) if root is not None else path).resolve()
        if root is not None and not path.is_relative_to(root):
            raise ValueError('source escapes asset base')
        with path.open('rb') as stream:
            data = stream.read(MAX_BYTES + 1)
        mime = ''
    if not data:
        raise ValueError('empty payload')
    if len(data) > MAX_BYTES:
        raise ValueError('payload exceeds 32 MiB')
    return data, mime


def image_extension(data: bytes) -> str:
    """Verify container integrity before claiming an image was acquired."""
    if data.startswith(b'\x89PNG\r\n\x1a\n'):
        offset = 8
        idat = bytearray()
        header = None
        ended = False
        while offset + 12 <= len(data):
            size = struct.unpack('>I', data[offset:offset + 4])[0]
            kind = data[offset + 4:offset + 8]
            end = offset + 12 + size
            if end > len(data):
                raise ValueError('truncated PNG chunk')
            payload = data[offset + 8:end - 4]
            crc = struct.unpack('>I', data[end - 4:end])[0]
            if zlib.crc32(kind + payload) != crc:
                raise ValueError('PNG chunk checksum mismatch')
            if header is None:
                if kind != b'IHDR' or size != 13:
                    raise ValueError('missing PNG header')
                header = struct.unpack('>IIBBBBB', payload)
            elif kind == b'IDAT':
                idat.extend(payload)
            elif kind == b'IEND':
                if size != 0 or end != len(data):
                    raise ValueError('invalid PNG end')
                ended = True
                break
            offset = end
        if not ended or not header or not idat:
            raise ValueError('incomplete PNG (IHDR/IDAT/IEND required)')
        width, height, bits, color, compression, filtering, interlace = header
        channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}.get(color)
        legal_bits = {0: (1, 2, 4, 8, 16), 2: (8, 16), 3: (1, 2, 4, 8), 4: (8, 16), 6: (8, 16)}
        if not width or not height or not channels or bits not in legal_bits[color] or compression or filtering or interlace not in (0, 1):
            raise ValueError('invalid PNG dimensions or encoding')
        passes = [(0, 0, 1, 1)] if not interlace else [(0, 0, 8, 8), (4, 0, 8, 8), (0, 4, 4, 8), (2, 0, 4, 4), (0, 2, 2, 4), (1, 0, 2, 2), (0, 1, 1, 2)]
        rows = []
        for x, y, dx, dy in passes:
            w, h = max(0, (width - x + dx - 1) // dx), max(0, (height - y + dy - 1) // dy)
            if w and h:
                rows.append((1 + (w * channels * bits + 7) // 8, h))
        expected = sum(stride * count for stride, count in rows)
        if expected > MAX_INFLATED_BYTES:
            raise ValueError('PNG decoded size exceeds 64 MiB')
        decoder = zlib.decompressobj()
        decoded = decoder.decompress(bytes(idat), expected + 1)
        if not decoder.eof or decoder.unused_data or len(decoded) != expected:
            raise ValueError('incomplete PNG compressed pixels')
        pos = 0
        for stride, count in rows:
            for _ in range(count):
                if decoded[pos] > 4:
                    raise ValueError('invalid PNG row filter')
                pos += stride
        return 'png'
    if data.startswith(b'\xff\xd8\xff'):
        if len(data) < 12 or not data.endswith(b'\xff\xd9'):
            raise ValueError('incomplete JPEG')
        return 'jpg'
    if data.startswith((b'GIF87a', b'GIF89a')):
        if len(data) < 14 or data[-1:] != b';':
            raise ValueError('incomplete GIF')
        return 'gif'
    if data.startswith(b'RIFF') and data[8:12] == b'WEBP':
        if len(data) < 20 or struct.unpack('<I', data[4:8])[0] + 8 != len(data):
            raise ValueError('incomplete WebP')
        return 'webp'
    try:
        root = ET.fromstring(data)
        if root.tag.split('}')[-1] == 'svg':
            return 'svg'
    except ET.ParseError:
        pass
    raise ValueError('unsupported image or non-image/error body')


def validate_payload(data: bytes, kind: str, mime: str = "") -> None:
    if kind != "html" and mime.split(";")[0].strip().lower() in ("text/html", "application/xhtml+xml"):
        raise ValueError("HTML response MIME in non-HTML resource")
    if kind == 'image':
        image_extension(data)
    elif kind != 'html' and re.match(rb'\s*(?:<!doctype\s+html|<html\b)', data, re.I):
        raise ValueError('HTML error body in non-HTML resource')
    elif kind in ('css', 'script', 'component', 'html'):
        data.decode('utf-8-sig')
    elif kind == 'font':
        if data[:4] in (b'wOFF', b'wOF2'):
            if len(data) < 44 or int.from_bytes(data[8:12], 'big') != len(data):
                raise ValueError('incomplete WOFF font')
        elif data[:4] in (b'\0\1\0\0', b'OTTO', b'true'):
            if len(data) < 12:
                raise ValueError('incomplete sfnt font')
            tables = int.from_bytes(data[4:6], 'big')
            if len(data) < 12 + tables * 16:
                raise ValueError('incomplete sfnt table directory')
            for index in range(tables):
                offset, size = struct.unpack('>II', data[20 + index * 16:28 + index * 16])
                if offset + size > len(data):
                    raise ValueError('incomplete sfnt table')
        else:
            raise ValueError('unsupported font container')


def write_verified(destination: Path, data: bytes) -> None:
    """Never overwrite a different file or follow a destination symlink."""
    if destination.is_symlink():
        raise ValueError('destination is a symlink')
    if destination.exists():
        if destination.read_bytes() != data:
            raise ValueError('destination collision; use a fresh output directory')
        return
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open('xb') as stream:
        stream.write(data)


def digest_fields(data: bytes) -> dict:
    return {'sha256': hashlib.sha256(data).hexdigest(), 'size_bytes': len(data)}


def load_source_manifest(root: Path, explicit: str | None = None) -> dict:
    """Reuse the source acquisition mapping; never silently ignore an explicit file."""
    candidates = [Path(explicit)] if explicit else [root / "source-manifest.json", root.parent / "source-manifest.json"]
    for path in candidates:
        if explicit or path.exists():
            data = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(data, dict) or not isinstance(data.get("files"), list):
                raise ValueError("source manifest requires files array")
            return data
    return {}


def source_identity_root(manifest: dict, fallback: Path) -> Path:
    """Root for resolving original identifiers only; it is never a read permission."""
    if manifest.get('source_root'):
        return Path(manifest['source_root'])
    entrypoint = manifest.get('entrypoint')
    for row in manifest.get('files', []):
        source = row.get('source', '')
        if row.get('local_path') == entrypoint and not source.startswith(('http://', 'https://', 'data:')):
            root = Path(source)
            for _part in Path(entrypoint).parts:
                root = root.parent
            return root
    return fallback


def source_index(manifest: dict) -> dict:
    """Index original/final URL aliases without reopening the origin."""
    index = {}
    for row in manifest.get('files', []):
        index[row['source']] = row
        if row.get('requested_source'):
            index[row['requested_source']] = row
    return index


def frozen_resource(source: str, by_source: dict, root: Path) -> tuple[str, str]:
    """Resolve only a recorded successful frozen file, confined to the snapshot."""
    row = by_source.get(source, {})
    if row.get('status') != 'ok' or not row.get('local_path') or not row.get('sha256'):
        raise ValueError('source is missing a verified frozen-file mapping')
    path = (root / row['local_path']).resolve()
    if not path.is_relative_to(root.resolve()):
        raise ValueError('frozen path escapes design-ref')
    return str(path), row['sha256']
