# ⑤ 구현 적대 리뷰 A — 검사기 구현 (현장 보고 typecheck 수리 · 대상 커밋 `b2e1f42` · 브랜치 `fix/field-typecheck` HEAD 27342a3) · 2026-09-03

저장소 파일 무수정. 실행은 스크래치 `b3/rv5/` 아래(원본 검사기 = `git show main:…` 사본 `orig/`, 형상 26종 `shapes/`, 라이브 실행은 `DJR_FINDINGS_JSON=<스크래치>` 로 sink 를 명시 파일로 돌려 `.dddjango/violations/` 사이드카 **0건 생성**(전/후 디렉터리 목록 diff 없음 — `sidecar-{before,after}-*.txt`)). 하네스 로그 `harness-*.log`, 형상 결과 `shapes-result.txt`, 라이브 출력 `live-*.txt`.

## 1. 드리프트 표 (계획 v2 Part 2 D2-1~D2-7 ↔ 구현)

| 항목 | 계획 v2 | 구현(b2e1f42) | 판정 |
|---|---|---|---|
| D2-3 helper 판형 | `_module_bindings(mod)` 모듈 수준 Import/ImportFrom(asname→원명) + if/try 재귀 + **그림자 pop**(ClassDef/FunctionDef/Assign) · 적용 = base(Name)+데코레이터(Name·Call.func) · Attribute 현행 | `_module_bindings` :146-182 — ImportFrom/Import 바인딩 · if/try(handlers·orelse·finalbody) 재귀 · pop = ClassDef/FunctionDef/**AsyncFunctionDef**/Assign(Name 타깃)/**AnnAssign(Name)** · `_resolved_name` :185-190 Name→`bindings.get(id,id)` · Attribute→`_name_of`(attr) · `_is_declarative_class` :193-201 base·데코레이터(Call.func) 양쪽 적용 | **검증됨** — pop 대상이 계획(3종)보다 2종 넓으나 «모듈 수준 재바인딩» 의미 안(AsyncFunctionDef·AnnAssign). 형상 t1~t4 로 Attribute 판정 원본 동일 확인(§2) |
| D2-3 선례 인용 | `check-error-centralization._module_bindings` | docstring :147 동일 인용 | **MINOR(문구)** — EC `_module_bindings` :866-891 은 문장별 스냅숏(`before[id(node)]`)+절대 모듈 경로 해소 판형이고, 평탄 최종 바인딩 맵은 EC `_final_module_bindings` :4124 가 더 가까운 판형. 동작 영향 0 |
| D2-3 관통 | «`_scan_stmts` 시그니처 관통(재귀 10곳+main)» | `_scan_stmts(..., bindings)` 재귀 10곳 + `_scan_class` + main :477 전건 갱신 | **검증됨** |
| D2-2 bad 픽스처 | 같은 폴더 import + `__init__.py`×2 · 잔여 = domain-model ⓓ#268 info 1 | `aliased_shadow.py` `from .plain_base import PlainBase as StrEnum` + `plain_base.py` + `__init__.py`×2 | **MINOR** — 실측 `check-domain-model.py bad_rules` → **`[#298]` blocker 1 + ⓓ#268×2, exit 2**(계획 «ⓓ#268 info 1» 아님). 원인: `_check_shared_imports` :521-536 은 `node.module` 문자열에 `shared_value_object` 가 있어야 ok — 상대 import(`.plain_base` → module="plain_base") 는 ok 아님. 하네스 무영향(bad_rules 는 cross census 밖) 이나 D2-2 의 채택 사유(«#298 회피»)가 실현되지 않음. 절대 경로 `from application.orders.domain_layer.shared_value_object.plain_base import PlainBase as StrEnum` 로 바꾸면 #298 0·ⓓ#268×2·exit 0 이고 public-surface 판정 불변(aliased_shadow 1건) — 스크래치 `absimp/` 실측 |
| D2-1 하네스 | fixture_matrix 무변 · findings_count `#493×7→8`+sha 3 · baseline `11→12` · **cross +1행** · construct_drift 무접촉 | fixture_matrix 무변 ✓ · findings_count `(2,12,2,"#358×2,#456×2,#493×8,#69×2",9a05…,4641…,5d31…)` ✓ · baseline `(2,12,12,4,False)` ✓ · **cross 무변** · construct_drift 무접촉 ✓ | **MINOR(계획 문면 오류·구현이 옳음)** — `checker_cross_matrix.census()` :66 «비-0 exit 만» 기록. good/ 에 대한 domain-model 은 ⓓ#268×2·**exit 0** 이라 행이 생기지 않는다(rv3 A 의 `(0,(),((268,1),))` 예측이 census 규약과 어긋남). 루브릭 «cross 무변(픽스처 #264 정리 후 행 제거)» 는 근거 미기재 — 기록 보강 권고 |
| D2-1 EXPECTED sha | «sha 3 재실측» | 3열 갱신(rv3 A 예측 3열째 `757f…` ≠ 커밋 `5d31…` — good 픽스처에 `reading_cursor.py` 추가로 변동) | **검증됨** — 4종 하네스 green 재현(§4) |
| D2-6 docstring | «검출 한계(오탐 가능 형상)» — 중간 base 전이 면제 없음 · Attribute receiver 무검사 · 동명 비선언 별칭 | :31-40 «검출 한계 (선언적 클래스 판정 — 오탐·미탐 가능 형상 …)» 불릿 **5**(모듈 수준 import 해소·Attribute attr·전이 면제 없음·동명 비선언 별칭/중간 base 별칭·동명 로컬 클래스 사각) | **검증됨** — 루브릭 «docstring «검출 한계» 4항» 은 실물 5항과 불일치(기록 MINOR) |
| D2-4 무손실 문면 | 감소 1형(a17)·a09 비면제 명기 | docstring 불릿 4 «동명 비선언 클래스의 별칭 … 면제되고, 중간 base 를 선언적 이름으로 별칭한 정당 코드는 면제되지 않는다(양 저장소 실측 0)» | **검증됨**(a09 는 «불변»이 아니라 green→red — §2 표; 실측 0 이라 수용) |
| D2-5 증거 | HEAD 사본 주석 제거본 orig 6 → patched 0 | `evidence-alias-strenum/`(README·2 py·orig/patched txt — 커밋 27342a3) | **검증됨** — 재현 orig `#493` 6 / patched «clean — 파일 2개» |
| D2-7 로드맵 | R-15b·R-16 등재 | `2026-09-03-improvement-roadmap.md:51-52` R-15(a)(b)·R-16 (커밋 27342a3) | **검증됨**(대상 커밋 밖 · 문서) |
| 범위 이탈 | — | diff 14파일 = 검사기·codex byte 미러·`pregate_symbol_kinds.json`×2(검사기 소스 해시만 `404f…→e907…` · `gen_pregate_symbol_kinds --check` in-sync)·픽스처 8·하네스 2 | **검증됨** — 계획 밖 변경 없음 |
| 통합 절 «수리 전 red 증명 커밋 포함» | 커밋 ① 에 red 증명 커밋 | main..HEAD 4커밋 중 red 증명 별도 커밋 없음 — 증거 dir + 검수표 «수리 전 #493×3 오탐 재현» 로 대체 | **MINOR(절차 기록)** — 재현 가능(§3) 하므로 실질 손실 없음 |
| 검수표 하네스 숫자 | — | «fixture_matrix 73/73 · findings 73/73 · baseline 73/73 · cross 102/102» | **MINOR(기록)** — 실측 fixture **102/102** · findings 73 · baseline 73 · cross **350/350** |

## 2. 반례 재실측 표 (원본 = main 검사기 · 수리본 = HEAD · `#493` 건수(exit))

| 형상 | 원본 | 수리본 | 판정 |
|---|---|---|---|
| a03 `try: from enum import StrEnum as _S / except ImportError: … as _S` | 1(e2) | 0(e0) | 오탐 소거 ✓ |
| a09 `from .domain_enum import DomainStrEnum as StrEnum`(정당 중간 base 별칭) | 0(e0) | **1(e2)** | green→red — docstring 명기·양 저장소 실측 0(§3) · 전이 면제 비범위(R-15b) |
| a13 `@_dataclass(frozen=True)` + 클래스 상수 | 1(e2) | 0(e0) | 오탐 소거 ✓(데코레이터 별칭 포함 — D2-3) |
| a19 `@_dataclass` 비-frozen `self.last = v` | 1(e2) | 0(e0) | 오탐 소거 ✓(속성 규칙도 면제) |
| a16 `from enum import StrEnum` 뒤 `from .plain import Plain as StrEnum` | 0(e0) | **1(e2)** | 미탐 폐쇄(의도) ✓ — 마지막 바인딩 승 |
| a17 내부 비선언 `Schema` 를 `as _Schema` | 1(e2) | 0(e0) | 검출 감소 1형(계획 D2-4 명기·실측 0) |
| a21a `Plain as StrEnum` 뒤 로컬 `class StrEnum(Enum)` 재정의 | 0(e0) | 0(e0) | 그림자 pop 작동 — 원본 판정 복원 ✓ |
| a21b `StrEnum as _S` 뒤 로컬 `class _S:` 재정의 | 1(e2) | 1(e2) | pop → 식별자 `_S` ∉ 집합 — 원본과 동일(비선언 로컬이라 정당) ✓ |
| t8 대조군 로컬 `class StrEnum:`(import 없음) | 0(e0) | 0(e0) | 기존 사각 유지(docstring 불릿 5) |
| **추가 s1** 함수 안 재정의 `def make(): _S: int = 1` | 1(e2) | 0(e0) | 함수 본문은 walk 밖 → 모듈 바인딩 유지 → 정당(모듈 `_S`=StrEnum) green ✓ |
| **추가 s2a** `if sys.version_info>=(3,11): from enum import StrEnum as _S / else: class _S(str, Enum)` | 1(e2) | 1(e2) | 조건부 재정의 → pop → `_S` 식별자 → red. **원본과 동일**(회귀 아님 · 별칭 polyfill 잔여 오탐) |
| **추가 s2b** 동명 polyfill `try: from enum import StrEnum / except: class StrEnum(str, Enum)` | 0(e0) | 0(e0) | pop 후 식별자 `StrEnum` ∈ 집합 → green ✓ |
| **추가 s2c** `from enum import StrEnum as _S` 뒤 `if os.environ…: class _S:` | 1(e2) | 1(e2) | 조건부 그림자 pop — 원본 동일 |
| **추가 s3** 함수 안 `global _S; _S = object` | 1(e2) | 0(e0) | `Global` 은 `_record_syntax_bindings` 가 bound 처리 · 모듈 바인딩 유지 → green(이론상 미탐 · 무의미 코드) |
| s4 `_S: type = _S` AnnAssign 재대입 | 1(e2) | 1(e2) | AnnAssign pop — 원본 동일 |
| s5 `class _S(Enum)` **뒤** `from enum import StrEnum as _S` | 1(e2) | 0(e0) | 소스 순서 — import 가 뒤면 바인딩 유지 ✓ |
| s6 `with suppress(ImportError): … as _S` | 1(e2) | 1(e2) | 잔여(모듈 with 블록 미탐색 · 원본 동일) |
| s7 `except* ImportError`(TryStar) | 1(e2) | 1(e2) | 잔여(TryStar 미탐색 · 원본 동일) |
| t1 `import enum as e; class X(e.StrEnum)` | 0 | 0 | Attribute attr 동일 ✓ |
| t2 `class M(models.Model)` | 0 | 0 | 동일 ✓ |
| t3 `class X(enum.StrEnum)` | 0 | 0 | 동일 ✓ |
| t4 `import dataclasses as dc; @dc.dataclass(frozen=True)` | 0 | 0 | Attribute 데코레이터 동일 ✓ |
| t5 `from pydantic import BaseModel as _BM` | 1 | 0 | 오탐 소거(StrEnum 밖 형상) |
| t6 `import django.db.models as Model; class X(Model)` | 0 | 1 | a15 동종 무의미 코드 — 무시 |
| t7 plain `from enum import StrEnum` · t9 `from enum import *` | 0 | 0 | 대조군 동일 |

**오차단(정당 코드 green→red) 경로 판정 — 그림자 pop**: pop 은 «로컬 이름 Y → 원명 X» 바인딩을 제거해 `_resolved_name` 을 식별자 Y 로 되돌린다. 원본 검사기는 항상 Y 로 판정했으므로 **pop 이 적용된 이름의 판정은 원본과 동일**(a21a/a21b/s2a/s2b/s2c/s4 전건 일치). pop 은 새 오차단을 만들 수 없다. 함수 안 재정의·`global` 은 walk 밖이라 바인딩 유지(green 방향). 조건부(if/try 하위) 재정의는 분기 무관 소스 순서 pop → 원본 판정 복원(보수적). **BLOCKER 없음.** 잔여(원본 동일) = 별칭 polyfill(s2a/s2c)·`with`/`except*` 안 import(s6/s7) — docstring :34 «함수·클래스 본문 안 import 는 보지 않는다» 는 정확하나 «if/try 외 모듈 블록(with·match·except*)도 보지 않는다» 가 빠져 있음(MINOR 문구).

## 3. 무손실 독립 재실측 (원본 ↔ 수리본 · 전 트리 · sink 명시 파일)

| 대상 | 원본 | 수리본 | stdout diff | 사이드카 |
|---|---|---|---|---|
| `~/Desktop/spring_dream_server` | 위반 3225 + ⓓ 84 = 레코드 3309 · exit 2 | 3225 + 84 = 3309 · exit 2 | **identical** | 생성 0(목록 diff 없음) |
| `~/Desktop/kkebi-server` | 위반 173 + ⓓ 172 = 345 · exit 2 | 173 + 172 = 345 · exit 2 | **identical** | 생성 0 |
| 증거 `evidence-alias-strenum/`(주석 제거본 2파일) | `#493` 6 | clean(2파일) | — | — |
| 픽스처 `public_surface/good` | `#493` 3(book_usage_policy 2·reading_cursor 1) · exit 2 | clean · exit 0 | — | — |
| 픽스처 `public_surface/bad_rules` | `#493` 7 · 전체 11 · exit 2 | `#493` **8**(aliased_shadow:7 `FIRST` +1) · 전체 12 · exit 2 | — | — |

계획 주장(3309/3309 · 345/345 · 차분 0 · orig 6→0 · good clean · bad #493×8) 전건 재현.

## 4. 하네스·린트 정합

| 도구 | 결과 |
|---|---|
| `fixture_matrix.py` | 케이스 102 · 일치 102 · exit 0 |
| `findings_count_matrix.py` | 레인 73 · 일치 73 · exit 0 |
| `checker_baseline_matrix.py` | 레인 73 · 일치 73 · exit 0 |
| `checker_cross_matrix.py` | census 350 · EXPECTED 350 · 차이 0 · exit 0 |
| `checker_lint.py` | 검사기 27개 · 위반 0(규칙 앵커·가드·면제금지 낱말만 검사 — docstring 절 형식 요구 없음) |
| `spec_lint.py` | 규칙 546 · 위반 0(:418 «타입|애너테이션|mypy» → 이 검사기 매핑 유지) |
| `gen_pregate_symbol_kinds.py --check` | in-sync(56종·27검사기·양 미러) |
| `diff -rq dddjango/scripts codex-…/scripts` | 동일(검사기·pregate json byte 미러) |

## 5. 코드 품질

- 타입: 신설 코드의 첫 대입 전건 애너테이션(`bindings: dict[str,str]`·`top: str`·`walk(...) -> None`). 기존 `deco = set()` :198 무주석은 원본 잔존(범위 밖 · 검사기 코드 자체는 #493 대상 트리 밖이며 Makefile 에 mypy 없음 — 관례상 강제 아님).
- 이름·주석: 한국어 주석·docstring 관례 일치. `_resolved_name` 의 Attribute 경로는 `_name_of` 위임이라 `enum.StrEnum`·`models.Model`·`dc.dataclass` 판정 원본 동일(t1~t4).
- 불필요 변경 없음. `_module_bindings` docstring 의 EC 선례 인용은 위 D2-3 MINOR.

## 6. 판정·수정 요구

- **BLOCKER 0 · MAJOR 0.**
- **MINOR-1(픽스처 충실도)**: `aliased_shadow.py` import 를 절대 경로로 바꿔 D2-2 의 «#298 회피» 를 실현(실측 #298 0 · public-surface 판정 불변). 바꾸면 findings_count sha 열 재실측 필요.
- **MINOR-2(기록)**: 계획 D2-1 «cross +1행» 을 «cross 무변(census 는 비-0 exit 만 · domain-model good/ 는 exit 0)» 로 정정하고 루브릭 «#264 정리 후 행 제거» 근거 기재 · 루브릭 «검출 한계 4항» → 5항 · 검수표 «fixture 73/73·cross 102/102» → «fixture 102/102 · cross 350/350» · «수리 전 red 증명 커밋» 부재 → 증거 dir 대체 명기.
- **MINOR-3(문구)**: `_module_bindings` docstring 선례를 `_final_module_bindings` 판형으로, 모듈 헤더 :34 에 «with·match·except* 블록 안 import 도 보지 않는다» 병기.

## 7. 10줄 요약
1. 드리프트: D2-3 helper·pop·base+데코레이터·Attribute attr 구현 일치(pop 은 계획 3종 + AsyncFunctionDef·AnnAssign 확장, 의미 안). D2-6 «검출 한계» 5항. 범위 이탈 0(14파일 전건 계획 안 · pregate json 재소성 in-sync).
2. D2-2 MINOR: bad 픽스처의 상대 import 는 check-domain-model #298 을 여전히 울림(blocker 1 + ⓓ#268×2) — 계획 «잔여 ⓓ#268 1» 불일치. 절대 경로로 바꾸면 #298 0·판정 불변(실측).
3. D2-1 MINOR: 계획 «cross +1행» 은 오류 — census 가 비-0 exit 만 기록해 무변이 옳음(구현 정확). 루브릭 «#264 정리» 근거·검수표 하네스 숫자(fixture 102·cross 350) 기록 정정 필요.
4. 반례 재실측: a03·a13·a19·t5 오탐→0 · a16 미탐→1(의도) · a17 감소 1형(실측 0) · a09 green→red(docstring 명기·실측 0) · a21a/a21b pop 작동.
5. 추가 3형상: 함수 안 재정의(s1)·`global`(s3) 은 walk 밖이라 바인딩 유지(green) · 조건부 재정의(s2a/s2c) 는 pop → 원본 판정 복원. **pop 은 원본 판정을 되돌릴 뿐 새 오차단을 만들 수 없다 — BLOCKER 없음.**
6. 잔여(원본 동일·회귀 아님): 별칭 polyfill(s2a)·`with`/`except*` 안 import(s6/s7) red — docstring 에 «if/try 외 모듈 블록 미탐색» 병기 권고.
7. 무손실: spring 3225+84=3309 / kkebi 173+172=345 원본↔수리본 stdout identical · 사이드카 생성 0(sink 명시 파일).
8. 증거·픽스처 재현: evidence orig 6 → clean · good orig #493×3 → clean · bad 7 → 8(aliased_shadow +1).
9. 하네스 4종 green(102/73/73/350) · checker_lint·spec_lint 0건(docstring 절 형식 요구 없음) · codex 미러 byte 동일.
10. 판정: **통과(BLOCKER 0 · MAJOR 0 · MINOR 3 — 픽스처 절대 import · 기록 정정 · docstring 문구)**.
