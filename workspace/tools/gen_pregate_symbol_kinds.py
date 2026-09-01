#!/usr/bin/env python3
"""pre-gate 소성물 생성기 — [신규 2] Base 병기 의무 종류의 기계 추출 닫힌 목록.

배경(설계 §4 [신규 2] — `workspace/design/2026-09-01-pregate-design.md`):
설계 명세의 공개 심볼 표기 `경로::Symbol(Base)` 에서 Base 병기가 «의무»인 종류는
재량 목록이 아니라 **검사기 소스에서 기계 추출한 닫힌 목록**이어야 하고, 검사기
개정 시 rulepack 과 함께 재소성된다(드리프트 감시 — 설계 R5·§9-3).

추출 원리(결정적 — 조용한 공집합 금지):
  «클래스의 베이스 이름을 판정 재료로 쓰는» 규칙들의 재료를, (검사기 파일 ×
  AST 앵커) 명시 로스터(ROSTER)로 정적 스캔한다. 로스터가 가리키는 소재가
  검사기에서 사라지면 red(exit 1)다 — 재량 판단·산문 추론 재료는 0 이다.

닫힌 세계 불변식:
  ① 디스크의 check-*.py 집합 ≡ KNOWN_CHECKERS(27종) — 검사기 신설·소멸은 red 로
     로스터 재검토를 강제한다.
  ② ROSTER 의 검사기 ∪ NO_BASE_MATERIAL ≡ KNOWN_CHECKERS — «베이스 판정 없음»도
     명시 확인 목록으로 성문한다(2026-09-01 `.bases` 전수 스캔).

base 표기법(소성물 JSON 의 "base" 필드):
  `TestCase`        — 정확 일치 베이스(검사기가 이름 그대로 판정)
  `*Port`           — 접미 일치 베이스(검사기가 endswith 로 판정 — 과제 문면의 `*Factory` 표기 준용)
  `@abstractmethod` — 데코레이터 토큰(베이스 슬롯의 판정 재료 — #212·#493 계열)

방출 제외(검증 전용 소재 — 존재만 확인, kinds 비방출):
  django_db 마커·Client 상수([신규 4]·D2 ② 채널), Adapter/UseCase/Factory «Symbol
  이름» 판정, `_port.py` 파일명 판정(#396) — Base 채널이 아닌 소재는 목록을 오염하지
  않되 드리프트 가드에는 남긴다.

산출(소성물): `dddjango/scripts/pregate_symbol_kinds.json` +
  `codex-dddjango/skills/dddjango/scripts/pregate_symbol_kinds.json` (byte 동일 미러).

exit:  0 = 생성/일치   1 = red(소재 소실·닫힌 세계 위반·소성물 드리프트·usage)
"""
from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path

EXIT_OK: int = 0
EXIT_RED: int = 1

SCRIPTS_REL: str = "dddjango/scripts"
CODEX_SCRIPTS_REL: str = "codex-dddjango/skills/dddjango/scripts"
OUT_NAME: str = "pregate_symbol_kinds.json"
SCHEMA_ID: str = "pregate-symbol-kinds/0"

# 디스크 실물과 대조하는 검사기 전수 목록(27종 — 2026-09-01 기준).
KNOWN_CHECKERS: tuple[str, ...] = (
    "check-api-error-controller-contract.py",
    "check-app-container.py",
    "check-broker-contract.py",
    "check-business-vocabulary.py",
    "check-choices-literal-consumption.py",
    "check-common-container.py",
    "check-composition-root.py",
    "check-context-isolation.py",
    "check-db-table.py",
    "check-domain-model.py",
    "check-error-centralization.py",
    "check-event-publish.py",
    "check-idempotency-scope-creep.py",
    "check-layer-skeleton.py",
    "check-mechanism-ownership.py",
    "check-missable-entrance.py",
    "check-naming.py",
    "check-ninja-boundary-middleware.py",
    "check-openapi-error-declaration.py",
    "check-port-adapter-pairing.py",
    "check-public-surface-annotation.py",
    "check-response-schema-bypass.py",
    "check-synthetic-infra-exc.py",
    "check-test-config.py",
    "check-transaction-boundary.py",
    "check-transient-overmapping.py",
    "check-usecase-dto-placement.py",
)

# «클래스 베이스 판정 재료 없음» 확인 목록 — 2026-09-01 `ClassDef.bases` 전수 스캔.
# (check-transaction-boundary 의 Repository/UnitOfWork 는 «애너테이션» 판정이라 제외.)
NO_BASE_MATERIAL: frozenset[str] = frozenset({
    "check-app-container.py",
    "check-broker-contract.py",
    "check-common-container.py",
    "check-idempotency-scope-creep.py",
    "check-layer-skeleton.py",
    "check-mechanism-ownership.py",
    "check-missable-entrance.py",
    "check-ninja-boundary-middleware.py",
    "check-response-schema-bypass.py",
    "check-synthetic-infra-exc.py",
    "check-transaction-boundary.py",
    "check-transient-overmapping.py",
})


@dataclass(frozen=True)
class Emit:
    """소재가 닫힌 목록에 내보내는 모양 — shape 가 base 표기(정확/접미/데코레이터)를 정한다."""

    shape: str  # "exact" | "suffix" | "decorator"
    rules: tuple[str, ...]  # 이 소재를 판정 재료로 쓰는 규칙 번호("#NNN")
    bases: tuple[str, ...] = ()  # 리터럴 앵커의 고정 방출(집합 앵커는 () — 추출값 방출)


@dataclass(frozen=True)
class Material:
    """로스터 1행 — (검사기, AST 앵커, 키). emit=None 이면 존재 검증 전용."""

    checker: str
    anchor: str  # "assign_set" | "assign_str" | "assign_fstring_tail" | "set_literal" | "endswith_literal" | "compare_literal"
    key: str  # 변수명(assign_*) 또는 대표 리터럴(그 외)
    expect: tuple[str, ...] = ()  # 집합 앵커의 최소 부분집합 센티널 / f-string 꼬리
    emit: Emit | None = None
    note: str = ""  # 검증 전용 소재의 채널 귀속 근거


# ── 명시 로스터 — 검사기 소스의 «클래스 베이스 판정 재료» 전수(2026-09-01 스캔) ──
ROSTER: tuple[Material, ...] = (
    # 선언형 클래스 판정(#493 애너테이션 의무의 면제 갈림) — 베이스·데코레이터 재료.
    Material("check-public-surface-annotation.py", "assign_set", "DECLARATIVE_BASE_NAMES",
             expect=("Model", "Schema", "BaseModel"), emit=Emit("exact", ("#493",))),
    Material("check-public-surface-annotation.py", "assign_set", "DECLARATIVE_DECORATORS",
             expect=("dataclass",), emit=Emit("decorator", ("#493",))),
    # 테스트 물리 신호 — DB 켜는 베이스(#387/#389)·factory_boy 베이스(#392).
    Material("check-test-config.py", "assign_set", "DB_TEST_BASES",
             expect=("TestCase", "TransactionTestCase", "LiveServerTestCase"),
             emit=Emit("exact", ("#387", "#389"))),
    Material("check-test-config.py", "endswith_literal", "Factory",
             emit=Emit("suffix", ("#392",), bases=("Factory",))),
    Material("check-test-config.py", "compare_literal", "django_db",
             note="[신규 4] 물리 신호 채널(markers) — Base 종류 아님(방출 제외)"),
    Material("check-test-config.py", "compare_literal", "Client",
             note="D2 ② e2e client 시그니처 상수 채널(#390) — Base 종류 아님(방출 제외)"),
    # 오류 중앙화 — StrEnum·Enum 계열·FrameworkErrorSchema·*ErrorSchema/*ErrorCode.
    Material("check-error-centralization.py", "assign_str", "STR_ENUM",
             expect=("enum.StrEnum",), emit=Emit("exact", ("#572", "#636"))),
    Material("check-error-centralization.py", "assign_set", "ENUM_BASES",
             expect=("enum.Enum", "enum.StrEnum"), emit=Emit("exact", ())),
    Material("check-error-centralization.py", "assign_str", "NINJA_SCHEMA",
             expect=("ninja.Schema",), emit=Emit("exact", ())),
    Material("check-error-centralization.py", "compare_literal", "FrameworkErrorSchema",
             emit=Emit("exact", ("#572",), bases=("FrameworkErrorSchema",))),
    Material("check-error-centralization.py", "endswith_literal", "ErrorSchema",
             emit=Emit("suffix", ("#572",), bases=("ErrorSchema",))),
    Material("check-error-centralization.py", "endswith_literal", "ErrorCode",
             emit=Emit("suffix", ("#572", "#636"), bases=("ErrorCode",))),
    # DB 테이블 — ORM 모델 베이스(*Model — BaseModel 제외)·AppConfig.
    Material("check-db-table.py", "assign_str", "MODEL_SUFFIX",
             expect=("Model",), emit=Emit("suffix", ("#631", "#632"))),
    Material("check-db-table.py", "assign_set", "NON_MODEL_BASES",
             expect=("BaseModel",), emit=Emit("exact", ("#631", "#632"))),
    Material("check-db-table.py", "endswith_literal", "AppConfig",
             emit=Emit("suffix", ("#329", "#538"), bases=("AppConfig",))),
    # choices 소비 계약(선행 계약 소유 — #N 무배정) — 같은 Model 판(드리프트 짝).
    Material("check-choices-literal-consumption.py", "assign_str", "MODEL_SUFFIX",
             expect=("Model",), emit=Emit("suffix", ())),
    Material("check-choices-literal-consumption.py", "assign_set", "NON_MODEL_BASES",
             expect=("BaseModel",), emit=Emit("exact", ())),
    # 포트·어댑터 — ABC/@abstractmethod 정본 토큰(#551/#212)·계약 상속(#552/#577).
    Material("check-port-adapter-pairing.py", "compare_literal", "ABC",
             emit=Emit("exact", ("#551",), bases=("ABC",))),
    Material("check-port-adapter-pairing.py", "compare_literal", "abstractmethod",
             emit=Emit("decorator", ("#212",), bases=("abstractmethod",))),
    Material("check-port-adapter-pairing.py", "endswith_literal", "Port",
             emit=Emit("suffix", ("#552", "#577"), bases=("Port",))),
    Material("check-port-adapter-pairing.py", "endswith_literal", "Repository",
             emit=Emit("suffix", ("#577",), bases=("Repository",))),
    Material("check-port-adapter-pairing.py", "endswith_literal", "UnitOfWork",
             emit=Emit("suffix", ("#577",), bases=("UnitOfWork",))),
    Material("check-port-adapter-pairing.py", "endswith_literal", "DomainBypassQuery",
             emit=Emit("suffix", ("#577",), bases=("DomainBypassQuery",))),
    Material("check-port-adapter-pairing.py", "endswith_literal", "Adapter",
             note="Symbol «이름» 명명 판정(#370/#373) — Base 채널 아님(방출 제외)"),
    Material("check-port-adapter-pairing.py", "endswith_literal", "UseCase",
             note="컨트롤러 직접 생성의 호출 «이름» 판정(#134) — Base 채널 아님(방출 제외)"),
    # 도메인 모델 — 도메인 Enum 계열(#565 후보)·Factory «이름» 판정(#315).
    Material("check-domain-model.py", "set_literal", "domain-enum-bases",
             expect=("Enum", "StrEnum", "IntEnum", "TextChoices", "Choices"),
             emit=Emit("exact", ("#565",))),
    Material("check-domain-model.py", "compare_literal", "Factory",
             note="애그리거트 폴더 밖 Factory 는 «이름 포함» 판정(#315) — Base 채널 아님(방출 제외)"),
    # 컨텍스트 격리 — published 예외 기저(#167)·둘째 ErrorCode 컨테이너(#117)·경계 애너테이션 Model/BaseModel 구분(#11).
    Material("check-context-isolation.py", "set_literal", "published-exception-bases",
             expect=("Exception", "BaseException"), emit=Emit("exact", ("#167",))),
    Material("check-context-isolation.py", "assign_set", "_ENUM_BASE_NAMES",
             expect=("Enum", "StrEnum"), emit=Emit("exact", ("#117",))),
    Material("check-context-isolation.py", "set_literal", "strenum-container",
             expect=("StrEnum",), emit=Emit("exact", ("#117",))),
    Material("check-context-isolation.py", "endswith_literal", "ErrorCode",
             emit=Emit("suffix", ("#117",), bases=("ErrorCode",))),
    Material("check-context-isolation.py", "endswith_literal", "Model",
             emit=Emit("suffix", ("#11",), bases=("Model",))),
    Material("check-context-isolation.py", "compare_literal", "BaseModel",
             emit=Emit("exact", ("#11",), bases=("BaseModel",))),
    # 업무 어휘 — 페이크의 포트 상속(#622)·HttpError 재선언 금지(#119)·저장 실패 넷째 자리(#294).
    Material("check-business-vocabulary.py", "endswith_literal", "Port",
             emit=Emit("suffix", ("#622",), bases=("Port",))),
    Material("check-business-vocabulary.py", "compare_literal", "HttpError",
             emit=Emit("exact", ("#119",), bases=("HttpError",))),
    Material("check-business-vocabulary.py", "set_literal", "storage-failure-exception",
             expect=("Exception",), emit=Emit("exact", ("#294",))),
    Material("check-business-vocabulary.py", "endswith_literal", "_port.py",
             note="framework 4단 판정(#396)은 «파일명» 채널 — Base 종류 아님(방출 제외)"),
    # 컨트롤러 결과 소비 — 예외 기반 사슬 면제(#210)의 Exception/*Exception/*Error.
    Material("check-usecase-dto-placement.py", "compare_literal", "Exception",
             emit=Emit("exact", ("#210",), bases=("Exception",))),
    Material("check-usecase-dto-placement.py", "endswith_literal", "Exception",
             emit=Emit("suffix", ("#210",), bases=("Exception",))),
    Material("check-usecase-dto-placement.py", "endswith_literal", "Error",
             emit=Emit("suffix", ("#210",), bases=("Error",))),
    # 이벤트 발행 — 도메인 Enum 값↔유스케이스 이름 겹침(#564 후보).
    Material("check-event-publish.py", "set_literal", "event-enum-bases",
             expect=("Enum", "StrEnum", "TextChoices", "IntChoices", "Choices"),
             emit=Emit("exact", ("#564",))),
    # 명명 — admin 패널 베이스(#342).
    Material("check-naming.py", "set_literal", "admin-panel-bases",
             expect=("ModelAdmin", "TabularInline", "StackedInline"),
             emit=Emit("exact", ("#342",))),
    # 합성 루트 — Ninja API 루트 생성자 서브클래스(#437/#440).
    Material("check-composition-root.py", "assign_set", "ROOT_API_CONSTRUCTORS",
             expect=("ninja.NinjaAPI", "ninja_extra.NinjaExtraAPI"),
             emit=Emit("exact", ("#437", "#440"))),
    # OpenAPI 오류 계약(전 위반 귀속 #63) — 같은 루트 생성자·FrameworkErrorSchema 기저.
    Material("check-openapi-error-declaration.py", "assign_set", "ROOT_API_CONSTRUCTORS",
             expect=("ninja.NinjaAPI", "ninja_extra.NinjaExtraAPI"),
             emit=Emit("exact", ("#63",))),
    Material("check-openapi-error-declaration.py", "assign_fstring_tail", "COMMON_ERROR_OUT",
             expect=(".FrameworkErrorSchema",),
             emit=Emit("exact", ("#63",), bases=("FrameworkErrorSchema",))),
    # 컨트롤러 오류 매핑 — prepared FrameworkErrorSchema 카탈로그 기저(귀속 매핑표 v2 소유 — #N 무배정).
    Material("check-api-error-controller-contract.py", "assign_fstring_tail", "COMMON_ERROR_OUT",
             expect=(".FrameworkErrorSchema",),
             emit=Emit("exact", (), bases=("FrameworkErrorSchema",))),
)

# base 표기 → 정본 import 문(큐레이션 주석 — 기계 추출 대상이 아니라 소비 편의 메타데이터).
IMPORT_HINTS: dict[str, str | None] = {
    "ABC": "from abc import ABC",
    "@abstractmethod": "from abc import abstractmethod",
    "@attrs": "from attr import attrs",
    "@dataclass": "from dataclasses import dataclass",
    "@define": "from attrs import define",
    "@frozen": "from attrs import frozen",
    "AbstractBaseUser": "from django.contrib.auth.models import AbstractBaseUser",
    "AbstractUser": "from django.contrib.auth.models import AbstractUser",
    "AdminSite": "from django.contrib.admin import AdminSite",
    "AppConfig": "from django.apps import AppConfig",
    "*AppConfig": "from django.apps import AppConfig",
    "BaseModel": "from pydantic import BaseModel",
    "Choices": "from django.db.models import Choices",
    "DjangoModelFactory": "from factory.django import DjangoModelFactory",
    "Enum": "from enum import Enum",
    "Factory": "from factory import Factory",
    "Flag": "from enum import Flag",
    "Form": "from django.forms import Form",
    "FrameworkErrorSchema": "from framework.ninja.framework_error_schema import FrameworkErrorSchema",
    "HttpError": "from ninja.errors import HttpError",
    "HyperlinkedModelSerializer": "from rest_framework.serializers import HyperlinkedModelSerializer",
    "IntEnum": "from enum import IntEnum",
    "IntFlag": "from enum import IntFlag",
    "IntegerChoices": "from django.db.models import IntegerChoices",
    "LiveServerTestCase": "from django.test import LiveServerTestCase",
    "Model": "from django.db.models import Model",
    "ModelAdmin": "from django.contrib.admin import ModelAdmin",
    "ModelForm": "from django.forms import ModelForm",
    "ModelSerializer": "from rest_framework.serializers import ModelSerializer",
    "NamedTuple": "from typing import NamedTuple",
    "NinjaAPI": "from ninja import NinjaAPI",
    "NinjaExtraAPI": "from ninja_extra import NinjaExtraAPI",
    "PermissionsMixin": "from django.contrib.auth.models import PermissionsMixin",
    "ReprEnum": "from enum import ReprEnum",
    "Schema": "from ninja import Schema",
    "Serializer": "from rest_framework.serializers import Serializer",
    "StackedInline": "from django.contrib.admin import StackedInline",
    "StrEnum": "from enum import StrEnum",
    "TabularInline": "from django.contrib.admin import TabularInline",
    "TestCase": "from django.test import TestCase",
    "TextChoices": "from django.db.models import TextChoices",
    "TransactionTestCase": "from django.test import TransactionTestCase",
    "TypedDict": "from typing import TypedDict",
    # 접미 종류·검사기 리터럴 축자 종류(IntChoices — Django 정식 이름은 IntegerChoices)는 None.
}


def _tail(name: str) -> str:
    """점 경로의 꼬리 — `enum.StrEnum` → `StrEnum` (평이름은 그대로)."""
    return name.rsplit(".", 1)[-1]


def _shaped(shape: str, name: str) -> str:
    """emit shape 를 base 표기로 — exact 그대로 · suffix `*X` · decorator `@x`."""
    tail: str = _tail(name)
    if shape == "suffix":
        return f"*{tail}"
    if shape == "decorator":
        return f"@{tail}"
    return tail


def _const_str_set(node: ast.expr) -> frozenset[str] | None:
    """ast.Set 전 원소가 문자열 상수면 그 값 집합 — 아니면 None."""
    if not isinstance(node, ast.Set):
        return None
    values: set[str] = set()
    for elt in node.elts:
        if not (isinstance(elt, ast.Constant) and isinstance(elt.value, str)):
            return None
        values.add(elt.value)
    return frozenset(values)


def _module_assign_value(tree: ast.Module, var: str) -> ast.expr | None:
    """모듈 최상위 `var = …` (Assign/AnnAssign 단일 타깃)의 우변 — 없으면 None."""
    for stmt in tree.body:
        if isinstance(stmt, ast.Assign) and len(stmt.targets) == 1:
            target: ast.expr = stmt.targets[0]
            if isinstance(target, ast.Name) and target.id == var:
                return stmt.value
        elif isinstance(stmt, ast.AnnAssign) and isinstance(stmt.target, ast.Name) \
                and stmt.target.id == var:
            return stmt.value
    return None


def _find_assign_set(tree: ast.Module, var: str) -> frozenset[str] | None:
    value: ast.expr | None = _module_assign_value(tree, var)
    if value is None:
        return None
    return _const_str_set(value)


def _find_assign_str(tree: ast.Module, var: str) -> str | None:
    value: ast.expr | None = _module_assign_value(tree, var)
    if isinstance(value, ast.Constant) and isinstance(value.value, str):
        return value.value
    return None


def _find_assign_fstring_tail(tree: ast.Module, var: str, tail_lit: str) -> bool:
    """`var = f"…{X}.Tail"` — JoinedStr 상수 조각에 tail_lit 이 있는가."""
    value: ast.expr | None = _module_assign_value(tree, var)
    if not isinstance(value, ast.JoinedStr):
        return False
    return any(isinstance(part, ast.Constant) and part.value == tail_lit
               for part in value.values)


def _find_set_literal(tree: ast.Module, expect: frozenset[str]) -> frozenset[str] | None:
    """expect ⊇ 인 문자열 상수 set 리터럴 중 «최소» 집합의 전 원소(추가분 자동 수확)."""
    best: frozenset[str] | None = None
    for node in ast.walk(tree):
        values: frozenset[str] | None = _const_str_set(node) if isinstance(node, ast.Set) else None
        if values is None or not expect <= values:
            continue
        if best is None or len(values) < len(best):
            best = values
    return best


def _find_endswith_literal(tree: ast.Module, lit: str) -> bool:
    """`….endswith("lit")` 또는 `….endswith((…, "lit", …))` 호출 존재 여부."""
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute)
                and node.func.attr == "endswith" and node.args):
            continue
        arg: ast.expr = node.args[0]
        if isinstance(arg, ast.Constant) and arg.value == lit:
            return True
        if isinstance(arg, ast.Tuple) and any(
                isinstance(e, ast.Constant) and e.value == lit for e in arg.elts):
            return True
    return False


def _find_compare_literal(tree: ast.Module, lit: str) -> bool:
    """비교식(==·in·not in 등)의 어느 변에든 문자열 상수 lit 이 놓였는가."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare):
            continue
        for side in (node.left, *node.comparators):
            elts: tuple[ast.expr, ...] = tuple(side.elts) \
                if isinstance(side, (ast.Tuple, ast.List, ast.Set)) else (side,)
            if any(isinstance(e, ast.Constant) and e.value == lit for e in elts):
                return True
    return False


def _extract_material(tree: ast.Module, m: Material) -> tuple[frozenset[str] | None, str | None]:
    """소재 1건 추출 — (방출 이름 집합 | 검증전용 None, 오류 문면 | None)."""
    where: str = f"{m.checker} · {m.anchor}({m.key})"
    if m.anchor == "assign_set":
        values: frozenset[str] | None = _find_assign_set(tree, m.key)
        if values is None or not values:
            return None, f"{where} — 집합 대입 소재가 없다(또는 비문자열/공집합)"
        missing: frozenset[str] = frozenset(m.expect) - values
        if missing:
            return None, f"{where} — 센티널 원소 소실: {sorted(missing)}"
        return values, None
    if m.anchor == "assign_str":
        value: str | None = _find_assign_str(tree, m.key)
        if value is None:
            return None, f"{where} — 문자열 대입 소재가 없다"
        if m.expect and value not in m.expect:
            return None, f"{where} — 값 드리프트: {value!r} (기대 {list(m.expect)})"
        return frozenset({value}), None
    if m.anchor == "assign_fstring_tail":
        if not _find_assign_fstring_tail(tree, m.key, m.expect[0]):
            return None, f"{where} — f-string 꼬리 {m.expect[0]!r} 소재가 없다"
        return frozenset(m.emit.bases) if m.emit else frozenset(), None
    if m.anchor == "set_literal":
        found: frozenset[str] | None = _find_set_literal(tree, frozenset(m.expect))
        if found is None:
            return None, f"{where} — 기대 원소 {sorted(m.expect)} ⊆ 인 set 리터럴이 없다"
        return found, None
    if m.anchor == "endswith_literal":
        if not _find_endswith_literal(tree, m.key):
            return None, f"{where} — endswith 리터럴 소재가 없다"
        return frozenset(m.emit.bases) if m.emit else frozenset(), None
    if m.anchor == "compare_literal":
        if not _find_compare_literal(tree, m.key):
            return None, f"{where} — 비교식 리터럴 소재가 없다"
        return frozenset(m.emit.bases) if m.emit else frozenset(), None
    return None, f"{where} — 알 수 없는 앵커"


def _closed_world_errors(scripts_dir: Path) -> list[str]:
    """닫힌 세계 불변식 ①·② — 위반 문면 목록(비면 통과)."""
    errors: list[str] = []
    on_disk: frozenset[str] = frozenset(p.name for p in scripts_dir.glob("check-*.py"))
    known: frozenset[str] = frozenset(KNOWN_CHECKERS)
    for extra in sorted(on_disk - known):
        errors.append(f"미등재 검사기 발견: {extra} — 로스터/NO_BASE_MATERIAL 재검토 후 등재하라")
    for gone in sorted(known - on_disk):
        errors.append(f"등재 검사기 부재: {gone}")
    rostered: frozenset[str] = frozenset(m.checker for m in ROSTER)
    uncovered: frozenset[str] = known - rostered - NO_BASE_MATERIAL
    for name in sorted(uncovered):
        errors.append(f"귀속 미확인 검사기: {name} — ROSTER 또는 NO_BASE_MATERIAL 에 명시하라")
    for name in sorted(rostered & NO_BASE_MATERIAL):
        errors.append(f"모순 등재: {name} 이 ROSTER 와 NO_BASE_MATERIAL 양쪽에 있다")
    return errors


def build_payload(root: Path) -> dict[str, object]:
    """저장소 루트에서 소성물 payload 를 결정적으로 구성 — 실패는 SystemExit(red)."""
    scripts_dir: Path = root / SCRIPTS_REL
    if not scripts_dir.is_dir():
        raise SystemExit(f"red: 검사기 디렉터리 부재 — {scripts_dir}")
    errors: list[str] = _closed_world_errors(scripts_dir)

    trees: dict[str, ast.Module] = {}
    source_sha: dict[str, str] = {}
    for name in KNOWN_CHECKERS:
        path: Path = scripts_dir / name
        if not path.is_file():
            continue  # 부재는 닫힌 세계 검사에서 이미 red
        raw: bytes = path.read_bytes()
        source_sha[name] = hashlib.sha256(raw).hexdigest()[:16]
        try:
            trees[name] = ast.parse(raw.decode("utf-8"))
        except (SyntaxError, UnicodeDecodeError) as exc:
            errors.append(f"{name} — 파싱 실패: {exc}")

    kinds_map: dict[str, dict[str, set[str]]] = {}
    for m in ROSTER:
        tree: ast.Module | None = trees.get(m.checker)
        if tree is None:
            continue  # 파일 부재/파싱 실패는 위에서 red
        names, error = _extract_material(tree, m)
        if error is not None:
            errors.append(error)
            continue
        if m.emit is None:
            continue  # 검증 전용 소재 — 존재 확인만
        for name in names or frozenset():
            base: str = _shaped(m.emit.shape, name)
            entry: dict[str, set[str]] = kinds_map.setdefault(base, {"checkers": set(), "rules": set()})
            entry["checkers"].add(m.checker)
            entry["rules"].update(m.emit.rules)

    if errors:
        for line in errors:
            print(f"red: {line}", file=sys.stderr)
        raise SystemExit(EXIT_RED)
    if not kinds_map:
        raise SystemExit("red: 추출된 종류가 0 — 조용한 공집합 금지")

    kinds: list[dict[str, object]] = []
    for base in sorted(kinds_map):
        entry = kinds_map[base]
        kinds.append({
            "base": base,
            "checkers": sorted(entry["checkers"]),
            "rules": sorted(entry["rules"], key=lambda r: int(r.lstrip("#"))),
            "import_hint": IMPORT_HINTS.get(base),
        })
    return {
        "schema": SCHEMA_ID,
        "source_sha": {name: source_sha[name] for name in sorted(source_sha)},
        "kinds": kinds,
    }


def render(payload: dict[str, object]) -> bytes:
    """payload 의 결정적 byte 직렬화 — 재현성(정렬·개행)은 여기서 닫힌다."""
    return (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")


def _out_paths(root: Path) -> tuple[Path, Path]:
    return (root / SCRIPTS_REL / OUT_NAME,
            root / CODEX_SCRIPTS_REL / OUT_NAME)


def main(argv: list[str]) -> int:
    ap: argparse.ArgumentParser = argparse.ArgumentParser(
        description="pre-gate [신규 2] Base 병기 의무 종류 닫힌 목록 소성기")
    ap.add_argument("--root", default=".", help="저장소 루트(기본: 현재 디렉터리)")
    ap.add_argument("--check", action="store_true",
                    help="재생성 결과와 소성물의 byte 일치 검사(exit 0/1) — make verify 편입용")
    args: argparse.Namespace = ap.parse_args(argv)
    root: Path = Path(args.root).resolve()

    payload: dict[str, object] = build_payload(root)
    blob: bytes = render(payload)
    plugin_out, codex_out = _out_paths(root)

    if args.check:
        drift: list[str] = []
        for path in (plugin_out, codex_out):
            if not path.is_file():
                drift.append(f"소성물 부재: {path.relative_to(root)}")
            elif path.read_bytes() != blob:
                drift.append(f"소성물 드리프트: {path.relative_to(root)} — 재생성 결과와 byte 불일치")
        if drift:
            for line in drift:
                print(f"red: {line}", file=sys.stderr)
            print("→ workspace/tools/gen_pregate_symbol_kinds.py 재실행으로 재소성하라", file=sys.stderr)
            return EXIT_RED
        kinds_count: int = len(payload["kinds"])  # type: ignore[arg-type]
        print(f"in-sync: {OUT_NAME} ≡ 재생성 결과 (종류 {kinds_count}·검사기 {len(KNOWN_CHECKERS)}종·양쪽 미러 일치)")
        return EXIT_OK

    for path in (plugin_out, codex_out):
        if not path.parent.is_dir():
            raise SystemExit(f"red: 산출 디렉터리 부재 — {path.parent}")
        path.write_bytes(blob)
    kinds_total: int = len(payload["kinds"])  # type: ignore[arg-type]
    print(f"소성: {OUT_NAME} — 종류 {kinds_total}건 · 소재 {len(ROSTER)}행 · 검사기 {len(KNOWN_CHECKERS)}종")
    print(f"  → {plugin_out.relative_to(root)}")
    print(f"  → {codex_out.relative_to(root)} (byte 동일)")
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
