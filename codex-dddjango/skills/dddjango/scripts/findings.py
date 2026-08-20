"""dddjango 검사기 공용 구조화 출력 모듈 v0 — 위반 레코드 스키마 findings/0 (T0 B2).

역할: 검사기 출력의 «위반 = 1급 데이터» 통일(동결 블루프린트 E8)의 v0 부품.
라인 채널(stdout)은 기존 규약 그대로 두고 레코드는 «추가» 채널로만 나간다
(stdout 오염 금지: registry_gate 의 위반 라인 파싱 등 기존 소비자 무영향).

레코드 sink 우선순위(T2-2 — t2-plan §T2-2 L-7):
  ① DJR_FINDINGS_JSON=<파일>   지정 파일에 append(하네스·스모크 계약 — 최우선·무변)
  ② DJR_VIOLATIONS_DIR=<폴더>  `<UTC ISO>-<세션 8자>.jsonl` 로 원자 게시
  ③ 설치본 기본                `<TARGET>/.dddjango/violations/` — **표식(.dddjango/)이
                              이미 있을 때만** 켜진다(임의 프로젝트에 디렉터리를 새로
                              만들지 않는다·hermetic 사본에는 표식이 없어 무영향).
                              TARGET 등록은 checker_target 한 곳이 한다(27종 봉인점).
②③ 은 **지연 개방**(첫 레코드에서만 임시 파일 개방 — 빈 파일 미생성)이고 프로세스
종료 시 임시→최종 `os.replace` 로 원자 게시한다. 기록 실패는 sink 만 끄고 검사기의
라인 출력·exit 를 바꾸지 않는다(의도적 fail-open — 관측이 처치를 오염시키지 않는다).
수집은 저장소 측 `make collect-violations`(workspace/tools/collect_violations.py).
무의존 표준 라이브러리 구현(E7 배포 경계 — scripts 동봉 가능 층). python3.9 호환.

스키마 v0 (레코드 = JSON 한 줄 · 필드 추가=호환 확장, 기존 필드 의미 변경=버전 증가):
  schema       "findings/0" 고정(스트림/레코드 버전 — 이후 판 판별용)
  run_id       실행 식별(검사기 이름 + UTC 시각 + pid) — 한 프로세스의 전 레코드가 공유
  ts           판정 시점(UTC ISO 8601) — E6 «판정 시점 Expression» 도출 재료
  record_id    run_id + 서수 — E6 «위반 개체 = 어댑터가 채번»의 재료
  rule         무접두 "#N" 문자열 그대로(정수 아님 — Work IRI 조인은 alias 경유, T2 몫).
               "#N" 꼴 밖 센티널(parse-fail 류)은 rule=null 로 두고 sentinel 필드에 격리.
               선행 계약 검사기(rule-owner-map 규칙 0건)는 rule=null + contract_ref.
  sentinel     "#N" 꼴 밖 표지 원문(해당 없으면 null)
  contract_ref 선행 계약 표기(해당 없으면 null)
  checker      검사기 파일 이름(예: check-domain-model.py)
  file         라인 채널의 where 문자열 그대로(경로[:행] locator — v0 단순화 · 분해는 T2 IRI화 몫).
               where 는 str(where) 로 고정해 라인 문면과 레코드가 항상 같은 문자열이다
               (기계 치환군 B/C형 8종이 Path 객체를 넘긴다 — json 직렬화 계약)
  symbol       위반 심볼 이름(검사기가 아는 경우에만 — v0 대표 2종은 위치 단위가
               파일·디렉터리라 null)
  severity     값 공간 3종 — SHACL 3값 대응과 현행 exit 의미론 매핑의 선언:
                 "violation" = blocker  (sh:Violation 대응 — 현행 exit 2 산입 재료)
                 "warning"   = 주의     (sh:Warning 대응 — 현행 exit 불산입 · v0 발화 없음, 예약)
                 "info"      = 정보     (sh:Info 대응 — ⓓ 후보 채널 · 현행 exit 불산입)
  message      검사기 산출 메시지(ⓓ 후보는 «— 물음: …» 포함 — 라인 채널과 같은 문면)
  expression   null 예약 — T2 어댑터가 판정 시점 Expression 실값을 채운다

사용(검사기 쪽):
  from findings import Findings, Candidates     # 출력 규약 준수군
  from findings import ContractFindings         # 규약 밖·선행 계약 검사기
  Findings().add(rule, where, msg)         → 라인 "[{rule}] {where}: {msg}" + violation 레코드
  Candidates().add(rule, where, msg, 물음) → 라인 "[ⓓ{rule}] {where}: {msg} — 물음: {q}" + info 레코드
  ContractFindings(contract_ref, defer=True).add(where=…, msg=…)
                                           → 라인 "- {where}: {msg}"(계약 문법) +
                                             rule=null·contract_ref 레코드
셋 다 list 하위 타입이라 기존 «if findings: … / for x in findings: print(…)» 사용처가 그대로 돈다.
(SliceFindings·ContractFindings 의 line= 표면은 3단계 이행 완료로 제거 — V25 ⑤.)
"""
from __future__ import annotations

import atexit
import json
import os
import re
import sys
import time
from pathlib import Path

ENV_VAR: str = "DJR_FINDINGS_JSON"
# 설치본 위반 레코드 채널(T2-2 · t2-plan §T2-2 L-7) — 디렉터리 sink.
ENV_DIR: str = "DJR_VIOLATIONS_DIR"
ENV_SESSION: str = "DJR_SESSION_ID"
INSTALL_MARKER: str = ".dddjango"   # 설치 표식(도구 영역 — F-C 관례)
VIOLATIONS_SUBDIR: str = "violations"
SCHEMA: str = "findings/0"
SEVERITIES: "tuple[str, str, str]" = ("violation", "warning", "info")

_RULE_FORM: "re.Pattern[str]" = re.compile(r"#\d+\Z")  # 무접두 "#N" 꼴 — 밖이면 센티널


def _default_checker() -> str:
    """검사기 파일 이름 — 스크립트 직접 실행 관례(argv[0])에서 얻는다."""
    name: str = Path(sys.argv[0]).name
    return name if name else "<unknown-checker>"


class _Run:
    """프로세스 단위 실행 문맥 — run_id 하나 + 레코드 서수 채번.

    run_id 의 검사기 몫은 첫 방출 레코드의 checker 값을 쓴다(docstring 정의
    «검사기 이름+UTC 시각+pid»와 일치 — argv[0] 는 checker 미지정 시의 기본값일 뿐).
    """

    def __init__(self, checker: str) -> None:
        stamp: str = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
        self.run_id: str = f"{checker}-{stamp}-{os.getpid()}"
        self.serial: int = 0

    def next_record_id(self) -> str:
        self.serial += 1
        return f"{self.run_id}:{self.serial:04d}"


_run: "_Run | None" = None
_sink_disabled: bool = False  # 쓰기 실패 후 프로세스 단위 비활성(라인 채널은 계속 산다)
_target_root: "Path | None" = None      # checker_target 이 등록(27종 단일 봉인점)
_dir_writer: "tuple | None" = None      # (handle, tmp, final) — 지연 개방


def set_target(root: "str | Path") -> None:
    """검사 대상 저장소 루트 등록 — 설치본 기본 sink 경로(`<root>/.dddjango/violations/`)
    해석에만 쓴다. `checker_target.bc_shaped_target_reason` 한 곳이 호출한다."""
    global _target_root
    _target_root = Path(root)


def _default_dir() -> "Path | None":
    """설치 표식이 «이미 있을 때만» 기본 sink 를 켠다 — 임의 프로젝트에 디렉터리를
    새로 만들지 않는다(놀람 최소화·하네스 hermetic 사본에도 표식이 없어 무영향)."""
    if _target_root is None:
        return None
    marker: Path = _target_root / INSTALL_MARKER
    return (marker / VIOLATIONS_SUBDIR) if marker.is_dir() else None


def _sink_mode() -> "str | None":
    """우선순위: 명시 파일(DJR_FINDINGS_JSON) → 명시 디렉터리 → 설치본 기본 디렉터리."""
    if os.environ.get(ENV_VAR, "").strip():
        return "file"
    if os.environ.get(ENV_DIR, "").strip() or _default_dir() is not None:
        return "dir"
    return None


def _session_tag() -> str:
    raw: str = re.sub(r"[^0-9A-Za-z]", "", os.environ.get(ENV_SESSION, ""))[:8]
    if raw:
        return raw
    import uuid

    return uuid.uuid4().hex[:8]


def _dir_handle():
    """첫 레코드에서만 임시 파일을 연다(빈 파일 미생성 — lazy-open). 실패는 fail-open."""
    global _dir_writer
    if _dir_writer is not None:
        return _dir_writer
    d: str = os.environ.get(ENV_DIR, "").strip()
    out: "Path | None" = Path(d) if d else _default_dir()
    if out is None:
        return None
    out.mkdir(parents=True, exist_ok=True)
    stamp: str = time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    final: Path = out / f"{stamp}-{_session_tag()}.jsonl"
    if final.exists():  # 같은 초·같은 세션의 병렬 검사기 — pid 로 분리
        final = out / f"{stamp}-{_session_tag()}-{os.getpid()}.jsonl"
    tmp: Path = out / f".{final.name}.part"
    _dir_writer = (open(tmp, "a", encoding="utf-8"), tmp, final)
    atexit.register(_publish)
    return _dir_writer


def _publish() -> None:
    """임시 → 최종 원자 게시(rename). 레코드 0건이면 게시하지 않는다."""
    global _dir_writer
    w = _dir_writer
    if w is None:
        return
    _dir_writer = None
    fh, tmp, final = w
    try:
        fh.close()
        if tmp.stat().st_size == 0:
            tmp.unlink()
            return
        os.replace(tmp, final)
    except OSError:
        pass  # 관측 부산물 — 게시 실패가 검사 결과를 바꾸지 않는다


def _emit(checker: str, rule: "str | None", file: str, symbol: "str | None",
          severity: str, message: str, contract_ref: "str | None" = None) -> None:
    """구조화 레코드 1건 방출 — 환경변수 미지정이면 무동작(라인 채널만 남는다)."""
    global _run, _sink_disabled
    if _sink_disabled:
        return
    mode: "str | None" = _sink_mode()
    if mode is None:
        return
    if severity not in SEVERITIES:
        raise ValueError(f"severity 값 공간 밖: {severity!r} (허용: {SEVERITIES})")
    sentinel: "str | None" = None
    if rule is not None and not _RULE_FORM.fullmatch(rule):
        sentinel, rule = rule, None
    if _run is None:
        _run = _Run(checker)
    record: "dict[str, object]" = {
        "schema": SCHEMA,
        "run_id": _run.run_id,
        "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "record_id": _run.next_record_id(),
        "rule": rule,
        "sentinel": sentinel,
        "contract_ref": contract_ref,
        "checker": checker,
        "file": file,
        "symbol": symbol,
        "severity": severity,
        "message": message,
        "expression": None,
    }
    line: str = json.dumps(record, ensure_ascii=False) + "\n"
    try:
        if mode == "file":
            with open(os.environ[ENV_VAR].strip(), "a", encoding="utf-8") as fh:
                fh.write(line)
        else:
            w = _dir_handle()
            if w is None:
                return
            w[0].write(line)
    except OSError as exc:
        # 레코드는 «추가» 채널이다 — 쓰기 실패가 검사기의 라인 출력·exit 를 죽이면
        # 그 선언(«라인 출력·exit 의미론 무변»)이 거짓이 된다. 프로세스 단위로 sink 를
        # 끄고 한 번만 경고한다(T2-1 적대 검증 레인 R 1번 — 부모 없는 경로·읽기 전용에서
        # 27종 전부 FileNotFoundError 로 죽던 회귀).
        _sink_disabled = True
        where: str = ENV_VAR if mode == "file" else f"{ENV_DIR}/설치본 위반 디렉터리"
        print(f"주의: 구조화 레코드 채널 비활성 — {where} 경로에 쓸 수 없다({exc})",
              file=sys.stderr)


class FindingEntry:
    """구조화 엔트리 — 공용 포매터의 유일한 입력(출력 계약 v2 §1).

    라인은 엔트리 필드의 순수 함수다(레코드만으로 stdout 위반 라인 재구성 가능).
    kind 별 문법: violation `[{rule}] {where}: {msg}` · candidate `[ⓓ{rule}] {where}:
    {msg} — 물음: {q}` · contract `- {where}: {msg}` · guard `{msg}` 원문.
    """

    __slots__ = ("kind", "rule", "contract_ref", "where", "symbol", "severity",
                 "msg", "question", "checker")

    def __init__(self, kind: str, rule: "str | None", where: "str | Path", msg: str,
                 symbol: "str | None", severity: str, checker: str,
                 question: "str | None" = None,
                 contract_ref: "str | None" = None) -> None:
        self.kind = kind
        self.rule = rule
        self.contract_ref = contract_ref
        self.where = str(where)
        self.symbol = symbol
        self.severity = severity
        self.msg = msg
        self.question = question
        self.checker = checker

    @property
    def line(self) -> str:
        if self.kind == "violation":
            return f"[{self.rule}] {self.where}: {self.msg}"
        if self.kind == "candidate":
            return f"[ⓓ{self.rule}] {self.where}: {self.msg} — 물음: {self.question}"
        if self.kind == "contract":
            return f"- {self.where}: {self.msg}"
        return self.msg  # guard — 라인 = msg 원문

    @property
    def message(self) -> str:
        """레코드 message — candidate 는 라인과 같은 결합 문면(현행 의미 유지)."""
        if self.kind == "candidate":
            return f"{self.msg} — 물음: {self.question}"
        return self.msg


def line_of_record(record: "dict") -> str:
    """레코드 → stdout 라인 **역방향** 재구성(출력 계약 v2 §1 의 역함수).

    `FindingEntry.line` 이 «엔트리 → 라인»이라면 이것은 «레코드 → 라인»이다. 두 함수가
    같은 문법을 쓰므로 레코드만으로 stdout 라인을 되돌릴 수 있고, 그래서 «게이트가 고른
    귀속 라인 ↔ 그 라인을 낸 레코드» 매칭이 성립한다(T2-3 게이트 sidecar).

    이 구현이 단일 출처다 — 저장소 측 하네스(`findings_count_matrix`)도 이 함수를
    import 해서 쓴다(두 곳에 복제하면 문법이 갈라진다).
    """
    rule = record.get("rule")
    sev, f, m = record.get("severity"), record.get("file", ""), record.get("message", "")
    if rule is not None:
        return f"[ⓓ{rule}] {f}: {m}" if sev == "info" else f"[{rule}] {f}: {m}"
    sent = record.get("sentinel")
    if sent is not None:
        # guard(대상-0 — file 은 "(target)" 고정)만 msg 원문 라인, 그 외 센티널
        # («합성»·«바인딩»·«분석» — F0 격리)은 rule 자리 판형 그대로.
        return m if f == "(target)" else f"[{sent}] {f}: {m}"
    return f"- {f}: {m}"  # 계약(rule=null + contract_ref)


def emit_all(*collections: "list", printer=None, indent: str = "  ") -> None:
    """유일한 방출 지점(출력 계약 v2 — W1): 한 루프에서 라인 인쇄와 레코드 방출을
    같은 순서로 수행한다. record 순서 = stdout 위반 라인 순서가 이 함수의 불변식.

    defer 컬렉션 전용 — 즉시 방출 컬렉션(과도기 legacy)을 넘기면 이중 방출이므로
    거부한다. printer=None 이면 레코드만(앵커 모드처럼 라인을 별도 소비하는 경로).
    """
    for coll in collections:
        if not getattr(coll, "_defer", False):
            raise ValueError("emit_all 은 defer 컬렉션 전용 — 즉시 방출분과 섞으면 레코드가 중복된다")
        for entry in coll.entries:
            if printer is not None:
                printer(f"{indent}{entry.line}")
            _emit(entry.checker, entry.rule, entry.where, entry.symbol,
                  entry.severity, entry.message, contract_ref=entry.contract_ref)


def lines(coll: "list") -> "list[str]":
    """포매터 재사용 순수 함수(부작용 없음) — 앵커 collected 합류 등 라인 문자열 소비자용."""
    return [entry.line for entry in coll.entries]


def zero_target_guard(msg: str, checker: "str | None" = None) -> "Findings":
    """대상-0 가드(21종 공용 — 계약 v2 이행 표): 라인 = msg 원문 + rule=«대상0» 센티널
    레코드(_emit 의 격리로 rule=null+sentinel). exit 2 산입이므로 severity=violation."""
    out = Findings(checker, defer=True)
    entry = FindingEntry("guard", "대상0", "(target)", msg, None, "violation", out.checker)
    out.entries.append(entry)
    out.append(entry.line)
    return out


class Findings(list):
    """출력 규약 준수군용 — 라인 "[{rule}] {where}: {msg}" + violation 레코드.

    과도기 이중 모드(계약 v2 이행 — V25 3단계 완료 시 defer 가 유일 모드로 승격):
    defer=False(기본·legacy) = add 시 즉시 레코드 방출 / defer=True = 구조화 수집만,
    방출은 emit_all 에서 한 순서로. 두 모드 모두 list 내용물은 포매터 라인(소비자 호환)."""

    def __init__(self, checker: "str | None" = None, defer: bool = False) -> None:
        super().__init__()
        self.checker: str = checker or _default_checker()
        self._defer: bool = defer
        self.entries: "list[FindingEntry]" = []

    def add(self, rule: str, where: "str | Path", msg: str, symbol: "str | None" = None) -> None:
        entry = FindingEntry("violation", rule, where, msg, symbol, "violation", self.checker)
        self.entries.append(entry)
        self.append(entry.line)
        if not self._defer:
            _emit(self.checker, entry.rule, entry.where, entry.symbol, "violation", entry.msg)


class Candidates(list):
    """ⓓ 후보 채널 — 라인 "[ⓓ{rule}] {where}: {msg} — 물음: {q}" + info 레코드(exit 불산입)."""

    def __init__(self, checker: "str | None" = None, defer: bool = False) -> None:
        super().__init__()
        self.checker: str = checker or _default_checker()
        self._defer: bool = defer
        self.entries: "list[FindingEntry]" = []

    def add(self, rule: str, where: "str | Path", msg: str, question: str,
            symbol: "str | None" = None) -> None:
        entry = FindingEntry("candidate", rule, where, msg, symbol, "info", self.checker,
                             question=question)
        self.entries.append(entry)
        self.append(entry.line)
        if not self._defer:
            _emit(self.checker, entry.rule, entry.where, entry.symbol, "info", entry.message)


class ContractFindings(list):
    """선행 계약 검사기용(rule-owner-map 규칙 0건) — 레코드는 rule=null + contract_ref.

    라인은 포매터 계약 문법 `- {where}: {msg}`(FindingEntry 의 순수 함수) — line 표면은
    3단계 이행 완료로 제거됐다(V25 ⑤). defer=True + emit_all 방출이 표준."""

    def __init__(self, contract_ref: str, checker: "str | None" = None,
                 defer: bool = False) -> None:
        super().__init__()
        self.contract_ref: str = contract_ref
        self.checker: str = checker or _default_checker()
        self._defer: bool = defer
        self.entries: "list[FindingEntry]" = []

    def add(self, where: "str | Path", msg: str, symbol: "str | None" = None) -> None:
        entry = FindingEntry("contract", None, where, msg, symbol, "violation",
                             self.checker, contract_ref=self.contract_ref)
        self.entries.append(entry)
        self.append(entry.line)
        if not self._defer:
            _emit(self.checker, None, entry.where, entry.symbol, "violation", entry.msg,
                  contract_ref=self.contract_ref)
