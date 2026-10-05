"""픽스처 보조 — 완전한 1x1 PNG 를 만든다(v1.3.1 test_assets.py 의 png() 만 옮김).

fixtures_extract.sh 가 `from test_assets import png` 로 쓴다. 매직 헤더만 있는 가짜가 아니라
청크 · 압축 스캔라인까지 갖춘 실제 PNG 다.
"""
import struct
import zlib


def png(pixel=b'\xff\0\0'):
    # One 1x1 RGB pixel, complete chunks + compressed scanline (not a magic stub).
    def chunk(kind, data):
        return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', 1, 1, 8, 2, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(b'\0' + pixel)) + chunk(b'IEND', b'')
