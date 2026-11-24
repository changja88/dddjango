# dddjango 2.45.1 — 422 입력 오류 항목의 `ctx`(F4-216)

상태: 배포 끝(2026-11-25 06시 29분 · 태그 `dddjango--v2.45.1` · 고침 f5cd13cb · release 9c98c18e · 봉인 aadde109 · 3c22cb9e).

- 계획: `plan.md`(v1 — 사용자 «진행해줘»). 구현 중 바뀐 것은 이 문서 «독립 검토 반영» 이 정본이다.
- 노트: GitHub Release `dddjango--v2.45.1`.

## 현장 보고

- **F4-216**(수리됨): 경로 앞 응답 정본의 422 몸통 `NinjaValidationItemOut` 이 `type` · `loc` · `msg` 만 적었다. django-ninja 는 실제 422 항목에 `ctx` 를 싣는다(`validation_error_from_error_contexts` 가 pydantic 항목에서 `input` 만 지운다 · 오류 종류에 따라 있고 없다). 그래서 생성 문서와 실제 답이 달랐다. 프로젝트는 정본 사본을 고칠 수 없다(#63 b).

## 원인

- 2.37.0(F4-173) 정본이 422 몸통을 규범 글 `{"detail": [{type, loc, msg}]}` 대로 적었다. 2.38.0 · 2.45.0 판도 그대로 옮겼다.
- 동작 스모크는 실제 422 몸통을 문서와 대 보고 있었다. 장난감에도 `ctx` 가 실린 답(변환기 없는 uuid · 값 제약)이 있었다. 그러나 대조가 «문서에 없는 칸» 을 허용해서 놓쳤다.
- 정본의 다른 Ninja 행(401 · 403 CSRF · 403 권한 · 429 · 400)은 실제 답 키 `detail` 하나와 맞는다.

## 결정

- **사용자**: 계획 v1 «진행해줘»(범위 = F4-216 하나 · 2.45.1).
- **운영자 처리**(질문 생략 · 설계 처리 · 이의 시 뒤집음):
  1. `ctx` 꼴은 선택 칸 · 객체로 둔다. null 갈래와 기본값은 없다. 요청 쪽이 낸 안과 같다.
  2. 옛 사본 처리는 2.45.0 자산을 `pre_route_responses_canonical_2_45_0.py` 로 받는 것이다(11-22 «옛 정본 사본 계속 받음» 과 같음).
- 판 번호 **2.45.1**(patch) — 생성 문서 꼴 고침. 요청 가이드 바뀔 것 없음. README · master 문서 바뀔 것 없음(몸통 꼴을 적지 않음).

## 고침

- **정본**(자산 · 참조 글 코드 블록 · Codex):
  - `ctx: dict[str, JsonValue] = Field(default_factory=dict, json_schema_extra={"additionalProperties": True})`
  - 생성 문서에서는 선택 칸이고 꼴은 `{"type": "object", "additionalProperties": true}` 다. 따로 붙는 component 는 없다.
- **글**(graph-owned ninja §6.2):
  - Ninja 기본 행 422 몸통 → `{type, loc, msg, ctx?}`.
  - R-3749 rev5 · R-3750 rev4(명확화): 받는 옛 판 2.37.0 · 2.38.0 · 2.45.0 · `exempt_pattern` 은 2.45.0 부터의 정본 · 422 `ctx` 는 지금 판만.
- **검사기**: `PRE_ROUTE_CANONICAL_ASSETS` 넷(지금 판 · 2.45.0 · 2.38.0 · 2.37.0).
- **되돌아옴 막기**:
  - 동작 스모크 ② 가 실제 몸통 칸 ⊆ 문서 칸을 본다(`additionalProperties` 를 연 꼴만 뺌).
  - ⑦ 은 `ctx` 문서 꼴과, 실제 422 에 `ctx` 가 든 항목 · 빠진 항목이 모두 있는지를 본다.
  - 장난감 `books` 가 프로젝트 자기 `JsonValue` 별칭을 쓴다.
  - backstop 사례 넷: 2.45.0 사본 받음 · 그 판 `exempt_pattern` · 고친 2.45.0 사본 · 손으로 ctx 를 더한 사본.
- 딸린 것: LEDGER · 계수표(ExpressionShape 4524) · rulepack · 소스 미러 · 봉인 목록 · reverse_coverage · pre_route_canonical_check · 픽스처 정본 사본 셋 · pregate kinds.

## 사용자에게 보이는 흐름(전 → 후 · 행동 시험)

| 꼴 | 2.45.0 | 2.45.1 |
|---|---|---|
| 같은 장난감 422(항목 여섯 · `ctx` 든 것 넷) | 문서 밖 `ctx` 4 | 0 |
| 프로젝트가 사본에 `ctx` 를 손으로 더함 | #63 exit 2 | exit 2 그대로(지금 판 정본을 다시 옮긴다) |
| 지금 판 정본 사본 · 2.45.0 사본 | 0 · — | 0 · 0 |
| 프로젝트 자기 `JsonValue` 별칭이 있는 문서 | 200 | 200(구현 첫 꼴은 component 충돌로 500 — 검토 B1) |
| 동작 스모크 `--canonical` 2.45.0 | PASS(놓침) | FAIL 3(`ctx` 칸 없음 · 문서 밖 `ctx` 둘) |

변이(모두 죽음): `ctx` 지움 · null 허용 · 필수 칸 · 기본값 `{}` · component 를 붙이는 꼴 · 검사기 받는 목록에서 2.45.0 뺌.

## 독립 검토 반영

| 검토 | 결과 | 처분 |
|---|---|---|
| 구현 검토(정확성 · 과적합 · 모순) | 차단 1 · 중요 1 · 사소 3 | B1 받음: 첫 꼴 `dict[str, JsonValue]` 가 문서에 `JsonValue: {}` component 를 붙여, 플러그인 규범대로 자기 `type JsonValue` 별칭을 Schema 에 쓰는 프로젝트의 문서 만들기가 이름 충돌로 멈춤(재현됨 · 현장 저장소에도 별칭 있음) → `json_schema_extra` 로 component 없앰 + 장난감 별칭. I1 받음: 받는 옛 판 글 → R-3749 · R-3750 명확화. S1 판 밖(CursorPagination 422 꼴 `{"detail":[{"cursor": …}]}` · 2.37.0 부터 · 재현됨 · 작업 리스트 후보). S2 · S3 받음 |
| 좁은 재확인 | 차단 0 · 중요 0 · 사소 0 | 참고 하나 받음 — 손으로 ctx 를 더한 사본 사례의 기대 글에 견주는 자산 이름까지(«같으면 뒤 자산» 변이도 이 사례가 직접 잡게) · 검사기 «`exempt_pattern` 칸은 지금 판 정본이라야» 글은 옛 판(2.37.0 · 2.38.0) 사본에만 나고 권고가 맞아 둠 |

설계 메모: 처음 고른 `dict[str, object]` 는 문서가 가장 깨끗했으나 플러그인 타입 검사기 #647 이 Schema 칸의 `object` 값을 막는다(프로젝트 사본이 blocker 를 얻음). 그래서 `JsonValue` 로 적고 문서 꼴만 덮었다.

## 한계

- CursorPagination 422 꼴(위 S1)은 그대로다.
- 옛 사본(2.45.0 이전)을 쓰는 프로젝트는 다시 옮기기 전까지 문서에 `ctx` 가 없다. 검사기는 막지 않는다.
- pydantic 2.5 ~ 2.13 에서 `json_schema_extra` 덮기 결과는 재지 않았다(재는 판 `.venv-probe` 2.14.3).

## 검사 수치(마지막 실행)

- 커밋 f5cd13cb 뒤 push 전:
  - `make verify` 6/6 녹색(2503초) — 탐침 B0 696/696(R 412 · N 56 · C 228 · 다름 0) · API 오류 검사기 행렬 1080(어긋남 0) · `test_watch` 73 · 경로 앞 응답 operation 57 · 실제 요청 74(어긋남 0) · 검사기 픽스처 행렬 173/173 · 동작 보존 장치 픽스처(리팩토링 close 368회 · 자동 초록 0).
  - `make verify-mutation` exit 0 — rulepack 12 · 픽스처 88 · 행렬 208 · 검사기 스모크 205 · registry_gate 11 + 64 · pre-gate 25 · behavior_guard 85 · refactor_audit 69.
- 배포 안(깨끗한 클론) `make verify` 6/6 녹색(2778초) — B0 696/696 · 행렬 1080 · operation 57 · 픽스처 173/173 · close 368회 자동 초록 0.
- 봉인: `--check --draft` green(그룹 10 · 파일 274). 엄격 `--check` 의 external_annex 두 줄(A/B 평가 주문 O-4 · O-5 칸)은 2.45.0 봉인 커밋에서도 붉다(그때 셋) — 이 판과 무관.
- README 대상 명령 · 요청 가이드: 바뀔 것 없음.

## 정리

일 폴더 `workspace/scratch/f4-216-ctx-1125/`(장난감 · 변이 · 검토 사본 포함) · `release-2.45.1/`(클론 둘) · 이 일의 `/tmp/djr-verify.*` 둘을 지웠다.
