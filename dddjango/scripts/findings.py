"""dddjango 검사기 공용 구조화 출력 모듈 v0 — 위반 레코드 스키마 findings/0 (T0 B2).

역할: 검사기 출력의 «위반 = 1급 데이터» 통일(동결 블루프린트 E8)의 v0 부품.
라인 채널(stdout)은 기존 규약 그대로 두고, 환경변수 DJR_FINDINGS_JSON=<파일 경로>가
지정된 경우에만 JSON lines 레코드를 그 파일에 append 로 방출한다(추가 채널 —
stdout 오염 금지: registry_gate 의 위반 라인 파싱 등 기존 소비자 무영향).
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
  ContractFindings(contract_ref).add(line, where=…, msg=…)
                                           → 라인 문면은 호출자 소유 그대로(규약 밖 유지) +
                                             rule=null·contract_ref 레코드
셋 다 list 하위 타입이라 기존 «if findings: … / for x in findings: print(…)» 사용처가 그대로 돈다.
"""
from __future__ import annotations

import json
import os
import re
import sys
import time
from pathlib import Path

ENV_VAR: str = "DJR_FINDINGS_JSON"
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


def _emit(checker: str, rule: "str | None", file: str, symbol: "str | None",
          severity: str, message: str, contract_ref: "str | None" = None) -> None:
    """구조화 레코드 1건 방출 — 환경변수 미지정이면 무동작(라인 채널만 남는다)."""
    path_s: str = os.environ.get(ENV_VAR, "").strip()
    if not path_s:
        return
    if severity not in SEVERITIES:
        raise ValueError(f"severity 값 공간 밖: {severity!r} (허용: {SEVERITIES})")
    sentinel: "str | None" = None
    if rule is not None and not _RULE_FORM.fullmatch(rule):
        sentinel, rule = rule, None
    global _run
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
    with open(path_s, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(record, ensure_ascii=False) + "\n")


class Findings(list):
    """출력 규약 준수군용 — 라인 "[{rule}] {where}: {msg}" + violation 레코드."""

    def __init__(self, checker: "str | None" = None) -> None:
        super().__init__()
        self.checker: str = checker or _default_checker()

    def add(self, rule: str, where: "str | Path", msg: str, symbol: "str | None" = None) -> None:
        where_s: str = str(where)  # Path 호출자(B/C형)와 라인 문면·레코드 file 을 한 문자열로 고정
        self.append(f"[{rule}] {where_s}: {msg}")
        _emit(self.checker, rule, where_s, symbol, "violation", msg)


class Candidates(list):
    """ⓓ 후보 채널 — 라인 "[ⓓ{rule}] {where}: {msg} — 물음: {q}" + info 레코드(exit 불산입)."""

    def __init__(self, checker: "str | None" = None) -> None:
        super().__init__()
        self.checker: str = checker or _default_checker()

    def add(self, rule: str, where: "str | Path", msg: str, question: str,
            symbol: "str | None" = None) -> None:
        where_s: str = str(where)
        self.append(f"[ⓓ{rule}] {where_s}: {msg} — 물음: {question}")
        _emit(self.checker, rule, where_s, symbol, "info", f"{msg} — 물음: {question}")


class ContractFindings(list):
    """선행 계약 검사기용(rule-owner-map 규칙 0건 — 출력 규약 밖) — 라인 문면은 호출자
    소유 그대로 append 하고, 구조화 레코드는 rule=null + contract_ref 로 나간다."""

    def __init__(self, contract_ref: str, checker: "str | None" = None) -> None:
        super().__init__()
        self.contract_ref: str = contract_ref
        self.checker: str = checker or _default_checker()

    def add(self, line: str, where: "str | Path", msg: str, symbol: "str | None" = None) -> None:
        self.append(line)
        _emit(self.checker, None, str(where), symbol, "violation", msg,
              contract_ref=self.contract_ref)
