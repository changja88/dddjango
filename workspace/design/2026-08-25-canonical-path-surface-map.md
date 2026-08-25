# canonical 오류 스키마 경로 — 결합 표면 좌표 대장 (W6-2 · 구현 착수 조건)

> **철회(2026-08-25 · 판정 ⑫)**: 이 대장이 설계한 변형 집합(㉮)은 유일 사용처(tarot)의 정본
> 경로 전환 확정으로 원인이 소멸해 **되돌렸다** — `_CANONICAL_VARIANTS`·`_select_canonical`
> 철거·단일 정본 복원·그래프 R-0029·R-2918 리비전 3 동반. 이 문서는 가산 당시의 표면 좌표
> 기록으로 보존한다(리터럴→상수 재배선은 유지 — 단일 정본 값으로 수렴).

- 기준: HEAD(=v2.17.3) `dddjango/scripts/` — 2026-08-25 grep 전수. 개조 방식 = 검사기별
  `_CANONICAL_VARIANTS` 정의 + `_select_canonical(root)`가 config 직후 전역 상수를 재바인딩.
  이중 실재는 UsageError(«정본 이중화») exit 1. 클래스명 `FrameworkErrorSchema` 축은 불변
  (kkebi 실물 동일 — 메시지 문면·클래스명 검사 표면은 개조 대상 아님).

## check-error-centralization.py — 상수 5·사용 17·리터럴 1

| 표면 | 좌표 |
|---|---|
| 상수 정의 | :70 `COMMON_INIT` · :71 `COMMON_ERROR` · :72 `COMMON_VALIDATION` · :73 `COMMON_ERROR_MODULE` · :74 `COMMON_ERROR_OUT` |
| 상수 사용 | :635 · :687 · :697 · :703 · :729 · :2572 · :2680 · :3031 · :3257 · :3322 · :3348 · :3540 · :4518 · :4520 · :4522 · :4524 · :4529 |
| 경로 리터럴 | :689 메시지 «framework/ninja/framework_error_schema.py가 필요함» → 상수 f-string화 |
| 훅 지점 | `main:4802` `_parse_config` 직후 `_select_canonical(config.root)` — UsageError 채널(:4803-4805) 재사용 |

## check-api-error-controller-contract.py — 상수 3·리터럴 4

| 표면 | 좌표 |
|---|---|
| 상수 정의 | :72 `COMMON_ERROR_PATH` · :73 `COMMON_ERROR_MODULE` · :74 `COMMON_ERROR_OUT` |
| 모듈 리터럴 | :4566 등호+endswith · :4580 dotted containment · :5398 **basename+package 등호**(`framework_error_schema`·`framework.ninja`) · :5837 dotted containment |
| 파생 필요 | `COMMON_ERROR_BASENAME`·`COMMON_ERROR_PACKAGE` 신설(:5398용) — 변형 B는 `error_schema`·`framework.django_ninja` |

## check-openapi-error-declaration.py — 상수 2·리터럴 3

| 표면 | 좌표 |
|---|---|
| 상수 정의 | :52 `COMMON_ERROR_MODULE` · :53 `COMMON_ERROR_OUT` |
| 경로 리터럴 | :522 `required.append(Path(...))` · :2132 **dict 직접 인덱스**(`parsed_by_path[Path(...)]` — 누락 시 KeyError) · :2143 `common_relative` |
| 파생 필요 | `COMMON_ERROR_PATH` 상수 신설 후 3좌표 경유 |

## 변형 정의 (파생 튜플)

| 축 | A(정본 기본) | B(kkebi 승인 대체 — STOP 08-23 16:44) |
|---|---|---|
| dir | `framework/ninja` | `framework/django_ninja` |
| init | `framework/ninja/__init__.py` | `framework/django_ninja/__init__.py` |
| path | `framework/ninja/framework_error_schema.py` | `framework/django_ninja/error_schema.py` |
| module | `framework.ninja.framework_error_schema` | `framework.django_ninja.error_schema` |
| basename/package | `framework_error_schema` / `framework.ninja` | `error_schema` / `framework.django_ninja` |
| validation(선택 — 실재 시만 편입) | `framework/ninja/framework_validation_error_schema.py` | `framework/django_ninja/framework_validation_error_schema.py` |

선택 규칙: B의 path 실재 ∧ A의 path 부재 → B · 둘 다 실재 → UsageError · 그 외 → A(부재 blocker 현행 유지).
