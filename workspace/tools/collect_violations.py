#!/usr/bin/env python3
"""설치본 위반 레코드 수집기 — `.dddjango/violations/*.jsonl` → `workspace/eval/violations/raw/`.

T2-2(t2-plan §T2-2 L-7 «설치본 위반 레코드 경로 확정»)의 저장소 측 절반이다.
설치본(검사 대상 프로젝트)은 검사기가 도는 자리에서 `<root>/.dddjango/violations/`에
`<UTC ISO>-<세션 8자>.jsonl`을 원자 게시하고(생산자 = `dddjango/scripts/findings.py`),
이 도구가 그것을 저장소의 A/B 자산 자리로 **복사**한다(원본 무삭제 — 재수집 안전).

- 원천: `--from <dir>` 반복(미지정 시 `DJR_VIOLATIONS_DIR` 또는 `<repo>/.dddjango/violations`)
- 대상: `workspace/eval/violations/raw/<원천 이름>[/<실런 id>]/<파일명>` — 원천·실런별 폴더로 출처 보존
- **실런 격리**: `--run <experiment_run_id>` 를 주면 그 실런의 레코드만 수집한다. 격리가
  어댑터의 노드 키에만 있고 수집 단계에 없으면, 미추적 `.dddjango/` 가 리셋에 살아남는
  워크트리 판형에서 앞 런의 레코드가 뒤 런 자산에 섞인다(레인 AV 발견 10)
- 중복: 같은 (원천, 파일명)은 내용 sha256 이 같으면 건너뛰고 다르면 이름에 `-<sha8>` 부가
- 검증: 각 줄이 findings/0 JSON 인지 파싱만 확인(스키마 필드 단언은 findings_count_matrix 소유)
- ttl 변환은 위반 그래프 어댑터(별도)가 이 raw/ 를 입력으로 한다 — 여기서는 하지 않는다.

사용: python3 workspace/tools/collect_violations.py [--from <dir>]... [--run <id>] [--dry-run]
exit 0 = 수집 완료(0건 포함) / 1 = 재료 결손·사용 오류 / 2 = 손상 레코드 발견
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ROOT: Path = Path(__file__).resolve().parents[2]
DEST: Path = ROOT / "workspace" / "eval" / "violations" / "raw"
INSTALL_REL: Path = Path(".dddjango") / "violations"


def _sources(explicit: "list[str]") -> "list[Path]":
    if explicit:
        return [Path(p).expanduser().resolve() for p in explicit]
    env: str = os.environ.get("DJR_VIOLATIONS_DIR", "").strip()
    if env:
        return [Path(env).expanduser().resolve()]
    return [(ROOT / INSTALL_REL).resolve()]


def _sha8(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()[:8]


def main(argv: "list[str]") -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--from", dest="src", action="append", default=[],
                    help="원천 디렉터리(반복 가능) — 미지정 시 DJR_VIOLATIONS_DIR 또는 저장소 설치본")
    ap.add_argument("--dry-run", action="store_true", help="복사 없이 계획만 출력")
    ap.add_argument("--run", default="",
                    help="A/B 실런 격리 — 이 `experiment_run_id` 의 레코드만 수집한다. "
                         "미지정이면 전량. 격리가 어댑터의 노드 키에만 있고 **수집 단계에는 "
                         "없어서**, 앞 런의 레코드가 뒤 런 자산에 섞여 들어올 수 있었다"
                         "(레인 AV 발견 10)")
    args = ap.parse_args(argv)

    rows: "list[str]" = ["| 원천 | 파일 | 레코드 | 처분 |", "|---|---|---|---|"]
    copied = skipped = broken = 0
    for src in _sources(args.src):
        if not src.is_dir():
            rows.append(f"| `{src}` | — | — | 원천 부재(건너뜀) |")
            continue
        for f in sorted(src.glob("*.jsonl")):
            n = 0
            other = 0
            bad = False
            for line in f.read_text(encoding="utf-8").splitlines():
                if not line.strip():
                    continue
                try:
                    obj = json.loads(line)
                except ValueError:
                    bad = True
                    break
                if obj.get("schema") != "findings/0":
                    bad = True
                    break
                if args.run and obj.get("experiment_run_id") != args.run:
                    other += 1
                    continue
                n += 1
            if bad:
                broken += 1
                rows.append(f"| `{src.name}` | {f.name} | — | **손상 — 미수집** |")
                continue
            if args.run and n == 0:
                rows.append(f"| `{src.name}` | {f.name} | 0 | 다른 실런({other}건) — 미수집 |")
                continue
            out_dir: Path = DEST / (f"{src.name}/{args.run}" if args.run else src.name)
            out: Path = out_dir / f.name
            if out.exists():
                if _sha8(out) == _sha8(f):
                    skipped += 1
                    rows.append(f"| `{src.name}` | {f.name} | {n} | 동일 사본 존재(건너뜀) |")
                    continue
                out = out_dir / f"{f.stem}-{_sha8(f)}{f.suffix}"
            if not args.dry_run:
                out_dir.mkdir(parents=True, exist_ok=True)
                shutil.copy2(f, out)
            copied += 1
            rows.append(f"| `{src.name}` | {f.name} | {n} | {'복사 예정' if args.dry_run else '복사'} → `{out.relative_to(ROOT)}` |")

    print("\n".join(rows))
    print(f"[collect-violations] 복사 {copied} · 중복 건너뜀 {skipped} · 손상 {broken}"
          f"{' (dry-run)' if args.dry_run else ''}")
    if broken:
        print(f"[collect-violations] 손상 레코드 파일 {broken}건 — 원천 확인 필요", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
