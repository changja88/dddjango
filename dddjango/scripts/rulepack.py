#!/usr/bin/env python3
"""규칙 팩 조회 — 설치본 무의존 소비자 (T2-4 · C암 selector 재료).

정본은 `ontology/` 그래프이고, 이 모듈이 읽는 `rulepack.json` 은 **투영물**이다
(생성기 = `workspace/tools/ontology_rulepack.py`, 저장소 전용 rdflib). 설치본에는 rdflib 가
침투하지 않는다는 동결 E7 배포 경계 때문에 여기는 **표준 라이브러리만** 쓴다. python3.9 호환.

**팩에 규범 본문은 없다**(동결 E8 · 절차 정본 step 6′ · 개정 8). 조회로 얻는 것은 구조 인덱스와
**명칭**뿐이다 — 본문이 팩에 존재하지 않으므로 호출자가 실수해도 실을 수 없다.

T3 q4 개정(2026-08-22): 팩은 그래프 Work **전량**을 담는다(무앵커 절 포함). 이에 따라
`works.*.section_number` 와 `by_section.*.number` 의 값 공간이 `string | null` 로 넓어졌다 —
이 모듈은 두 필드를 읽지 않으므로 조회 코드 무변(스키마 `rulepack/1` 유지).

**fail-closed**: 팩이 없거나 스키마가 어긋나면 예외를 던진다. 조용히 B암으로 폴백하지 않는다 —
그 폴백은 「C 처치가 걸리지 않은 런」을 「정상 C 런」으로 위장시켜 A/B 전체를 오염시킨다
(T2-3 SF-10 「계측 실패를 수렴으로 오독」의 동형 방어).
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

SCHEMA: str = "rulepack/1"
ENV_PATH: str = "DJR_RULEPACK"          # 시험·probe 용 경로 주입
DEFAULT_NAME: str = "rulepack.json"

# `<rules>` 블록에 실리는 필드 — 이 집합이 계약이다(동결 개정 8이 정한 범위 = 번호·명칭).
RULE_FIELDS: "tuple[str, str]" = ("rule", "label")

TIER_ALIAS: int = 1      # 위반의 `#N` 이 대장에 있어 Work 를 정확히 짚었다
TIER_CHECKER: int = 2    # 검사기가 집행하는 Work 집합까지만 좁혔다(1:N — 정밀도 손실)
TIER_NONE: int = 3       # 팩 밖 — B암과 같은 재료로 폴백


class PackError(RuntimeError):
    """팩 부재·손상. 호출자는 이것을 잡아 **중단**해야 한다(폴백 금지)."""


_SEGMENT_OK: "re.Pattern" = re.compile(r"\A[A-Za-z0-9_.*-]+\Z")


def validate_glob(glob: str) -> "list":
    """폐쇄 문법 검사 — 세그먼트 목록을 돌려주거나 `ValueError`. **문법의 단일 출처**다.

    사후 리뷰 AS-14 가 실증했듯 «허용 문자 집합» 정규식만으로는 `a/***/b`·`a//b`·`a/../b`·
    `/absolute/**`·`a/`·`a/**/**/b` 가 전부 통과한다 — 정적 셰이프·구조 검사·런타임 matcher 가
    각자 다른 관용도를 갖고 있었다. 셋이 이 함수 하나를 부른다.

    규칙: 저장소 상대 POSIX · 빈 세그먼트 금지(선행·후행·연속 `/`) · `..` 금지 ·
    세그먼트는 `**` **단독**이거나 `[A-Za-z0-9_.*-]+` · `***` 이상 금지 · `**` 연속 금지.
    """
    if not isinstance(glob, str) or not glob:
        raise ValueError(f"글롭이 비었거나 문자열이 아니다: {glob!r}")
    if glob.startswith("/"):
        raise ValueError(f"절대 경로 금지: {glob!r}")
    segments: "list" = glob.split("/")
    prev_star: bool = False
    for seg in segments:
        if seg == "":
            raise ValueError(f"빈 세그먼트(선행·후행·연속 구분자) 금지: {glob!r}")
        if seg == "..":
            raise ValueError(f"상위 참조 금지: {glob!r}")
        if seg == "**":
            if prev_star:
                raise ValueError(f"`**` 연속 금지: {glob!r}")
            prev_star = True
            continue
        prev_star = False
        if "**" in seg:
            raise ValueError(f"`**` 는 세그먼트 단독이어야 한다: {glob!r}")
        if not _SEGMENT_OK.match(seg):
            raise ValueError(f"세그먼트 문자 집합 이탈: {seg!r} in {glob!r}")
    return segments


def compile_glob(glob: str) -> "re.Pattern":
    """폐쇄 문법 → 정규식. 정적 셰이프와 **다른 게이트**다(적대 리뷰 AR 4-4).

    문법(저작 규약과 동일 — `workspace/tools/derive_path_globs.py` docstring):
      · 저장소 상대 POSIX · **전체 일치**(prefix 아님) · case sensitive
      · `*` = 한 세그먼트 내 임의(`/` 불포함) · `**` = 0개 이상 세그먼트

    셰이프가 통과해도 이 구현이 다르게 동작할 수 있으므로 conformance 케이스 표가 따로 있다.
    """
    validate_glob(glob)          # 문법 위반은 컴파일 전에 거절한다(관용 금지)
    out: "list" = []
    i: int = 0
    while i < len(glob):
        if glob.startswith("**/", i):
            out.append("(?:[^/]+/)*")
            i += 3
        elif glob.startswith("**", i):
            out.append(".*")
            i += 2
        elif glob[i] == "*":
            out.append("[^/]*")
            i += 1
        else:
            out.append(re.escape(glob[i]))
            i += 1
    return re.compile("\\A" + "".join(out) + "\\Z")


class Rulepack:
    """조회 전용 래퍼 — 팩의 배열 순서를 신뢰하고 재정렬하지 않는다.

    정렬의 단일 출처는 **생성기가 박아 넣은 `order_rank`** 다. 소비자가 절 번호를 다시
    자연 정렬하면 두 구현이 갈라진다(파일럿에서는 우연히 같고 §10 이 생기면 어긋난다).
    """

    __slots__ = ("works", "by_alias", "by_checker", "by_section", "by_path", "built_from")

    def __init__(self, data: "dict") -> None:
        if data.get("schema") != SCHEMA:
            raise PackError(f"스키마 불일치: {data.get('schema')!r} != {SCHEMA!r}")
        for key in ("works", "by_alias", "by_checker", "by_section"):
            if not isinstance(data.get(key), dict):
                raise PackError(f"필수 키 결손·형상 이탈: {key}")
        self.works: "dict" = data["works"]
        self.by_alias: "dict" = data["by_alias"]
        self.by_checker: "dict" = data["by_checker"]
        self.by_section: "dict" = data["by_section"]
        self.by_path: "list" = data.get("by_path", [])
        self.built_from: "list" = data.get("built_from", [])
        for wid, w in self.works.items():
            if "order_rank" not in w or "label" not in w:
                raise PackError(f"{wid}: order_rank·label 결손 — 팩이 낡았다")
        self._validate_refs()

    def _validate_refs(self) -> None:
        """참조 무결성 — **손상 팩과 정상 미등록 조회를 구분한다**(사후 리뷰 AS-07).

        검증이 없으면 `works={}`·`by_alias["#3"]="R-MISSING"`·`by_checker[x]=[]` 가 전부
        조용히 **tier 3(폴백)** 이 된다. 그러면 «C 처치가 걸리지 않은 런»이 «팩 밖이라 폴백한
        정상 런»과 로그에서 구별되지 않는다 — A/B 를 오염시키는 정확한 경로다.
        """
        if not self.works:
            raise PackError("works 가 비었다 — 빈 팩은 C 처치를 전건 폴백으로 만든다")
        for alias, wid in self.by_alias.items():
            if wid not in self.works:
                raise PackError(f"by_alias[{alias}] → {wid} 가 works 에 없다(손상 참조)")
        for checker, wids in self.by_checker.items():
            if not wids:
                raise PackError(f"by_checker[{checker}] 가 빈 목록이다(손상 참조)")
            for wid in wids:
                if wid not in self.works:
                    raise PackError(f"by_checker[{checker}] → {wid} 가 works 에 없다")
        for sec, entry in self.by_section.items():
            for wid in entry.get("works", []):
                if wid not in self.works:
                    raise PackError(f"by_section[{sec}] → {wid} 가 works 에 없다")
        for entry in self.by_path:
            try:
                validate_glob(entry.get("glob", ""))
            except ValueError as exc:
                raise PackError(f"by_path 글롭 문법 위반: {exc}")
            for wid in entry.get("works", []):
                if wid not in self.works:
                    raise PackError(f"by_path[{entry.get('glob')}] → {wid} 가 works 에 없다")

    @classmethod
    def load(cls, path: "str | Path | None" = None) -> "Rulepack":
        target: Path = Path(path or os.environ.get(ENV_PATH)
                            or Path(__file__).resolve().with_name(DEFAULT_NAME))
        if not target.is_file():
            raise PackError(f"팩 부재: {target} — 설치본에 rulepack.json 이 동봉되지 않았다")
        try:
            data = json.loads(target.read_text(encoding="utf-8"))
        except ValueError as exc:
            raise PackError(f"팩 손상: {target} — {exc}")
        return cls(data)

    # ── 조회 ────────────────────────────────────────────────────────────────
    def rank(self, wid: str) -> int:
        return int(self.works[wid]["order_rank"])

    def locate(self, record: "dict") -> "tuple":
        """위반 1건 → `(tier, order_rank, works)`.

        tier 2 의 `order_rank` 는 그 검사기가 집행하는 Work 들의 **최소값**이다 — 거친
        대리값이며(자인 W3′) 한 검사기 안의 세부 규범 차이를 구분하지 못한다.
        tier 3 은 `order_rank = None` 이라 호출자가 원래 순서를 보존해 뒤에 붙인다.
        """
        alias_hit: "str | None" = self.by_alias.get(record.get("rule"))
        if alias_hit is not None and alias_hit in self.works:
            return (TIER_ALIAS, self.rank(alias_hit), [alias_hit])
        wids: "list" = [w for w in self.by_checker.get(record.get("checker"), [])
                        if w in self.works]
        if wids:
            return (TIER_CHECKER, min(self.rank(w) for w in wids), wids)
        return (TIER_NONE, None, [])

    def norms_for_path(self, path: str) -> "list":
        """경로 → 적용 규범 Work 목록(`order_rank` 순·중복 제거) — **Q1 조회 전용**.

        C암 selector 는 이것을 **쓰지 않는다**(처치 밖 — 적대 리뷰 AP-08). 위반 레코드가 이미
        `checker` 를 운반하므로 경로 축은 선별에 추가 정보를 주지 않고, 처치에 넣으면
        「발주 산출 경로에 맞춰 글롭을 저작했다」는 의심만 남는다.
        """
        hits: "list" = []
        for entry in self.by_path:
            if compile_glob(entry["glob"]).match(path):
                hits.extend(entry.get("works", []))
        seen: "set" = set()
        out: "list" = []
        for wid in hits:
            if wid in seen or wid not in self.works:
                continue
            seen.add(wid)
            out.append(wid)
        out.sort(key=self.rank)
        return out

    def rules(self, wids: "list", exact: "set" = None) -> "list":
        """Work 목록 → `<rules>` 항목(번호·명칭). `order_rank` 순·중복 제거.

        `rule` 자리에는 alias(`#N`)가 있으면 그것을, 없으면 Work 번호(`R-NNNN`)를 쓴다 —
        위반 목록이 `#N` 으로 말하므로 같은 번호 체계로 맞춘다.
        """
        seen: "set" = set()
        picked: "list" = []
        for wid in wids:
            if wid in seen or wid not in self.works:
                continue
            seen.add(wid)
            picked.append(wid)
        picked.sort(key=self.rank)
        hit: "set" = exact or set()
        out: "list" = []
        for wid in picked:
            aliases: "list" = self.works[wid].get("aliases") or []
            number: str = ("#" + aliases[0].split("#", 1)[1]) if aliases else wid
            out.append({"rule": number, "label": self.works[wid]["label"],
                        "join": "exact" if wid in hit else "candidate"})
        return out
