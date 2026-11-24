# F4-216 — 422 항목 `ctx` · 재현 · 원인 · 고침 계획 v1 (dddjango 2.45.1 · 2026-11-25 03:51)

장부 읽기: 마지막 F4-216(읽은 때 2026-11-25 03:46). 상태: 사용자 «진행해줘»(04:00 앞)로 승인 · 구현 때 바뀐 것은 `plan-2.45.1.md` «독립 검토 반영» 이 정본이다.

## 1. 재현(배포판 2.45.0 · 장난감 `toy/` · `repro.py`)

| 무엇 | 결과 | 출력 |
|---|---|---|
| 실제 422(django-ninja 1.6.3 · pydantic 2.14.3) | 항목 여섯 중 넷에 `ctx`(string_too_short `{min_length}` · greater_than `{gt}` · literal_error `{expected}` · value_error `{error}` 글) · missing · int_parsing 은 `ctx` 없음 | out-repro-2.45.0.txt |
| 2.45.0 정본이 만든 문서 `NinjaValidationItemOut` | properties = type · loc · msg 뿐 → 문서 밖 키 `ctx` 4건 | 같음 |
| 프로젝트가 사본에 ctx 를 더하면 | 배포판 검사기 #63 exit 2(«7번째 정의 `NinjaValidationItemOut` 부터 다름 · 정본 코드는 고치지 않는다») | out-checker.txt |
| NinjaExtraAPI 도 같음 | 같은 답 | out-repro-new.txt |
| 같은 꼴 다른 자리(정본 Ninja 행 401 · 403 CSRF · 403 권한 · 429 · 400) | 실제 답 키 = `detail` 하나 = 정본 `NinjaDetailOut` 와 맞음 | out-kin.txt |

**원인**: 2.37.0(F4-173) 정본이 422 몸통을 규범 글 `{"detail": [{type, loc, msg}]}` 대로 적었고, ninja `validation_error_from_error_contexts`(main.py:619-638)는 pydantic 항목에서 `input` 만 지우고 `ctx` 를 남긴다. 정본 몸통 꼴을 실제 답과 대 보는 시험이 없어(행 붙임만 봄) 2.38.0 · 2.45.0 판에도 그대로 옮겨졌다. 다른 행은 맞다 — 빠진 것은 422 의 `ctx` 하나.

## 2. 고침(질문 생략 · 설계 처리 · 이의 시 뒤집음)

- **정본**: `NinjaValidationItemOut` 에 `ctx: dict[str, JsonValue] = Field(default_factory=dict, json_schema_extra={"additionalProperties": True})`(+ `pydantic.Field` import — 구현 때 바뀜 · plan-2.45.1 «독립 검토 반영»). 생성 문서 = `ctx` 선택 칸 · `{"type": "object", "additionalProperties": true}` · null 갈래 0 · 기본값 0 · 따로 붙는 component 0(probe: out-shapes.txt · out-defs.txt — `| None` 은 null 갈래 · `= {}` 는 기본값 · `JsonValue` 값은 `JsonValue` component 하나가 더 붙어 버림).
- **글**(graph-owned ninja §6.2): 코드 블록 + 산문 `{"detail": [{type, loc, msg}]}` → `{type, loc, msg, ctx?}` 와 «`ctx` 는 오류 종류에 따라 있고 없다(있으면 객체)».
- **옛 사본**: 지금 자산 → `pre_route_responses_canonical_2_45_0.py`(2.45.0 byte) · 검사기가 받는 자산 넷. 옛 사본 프로젝트는 그대로 녹색(문서에 ctx 가 없을 뿐) — 11-22 결정(옛 정본 사본 계속 받음)과 같다.
- **되돌아옴 막기**: `pre_route_behavior_smoke` 에 «실제 답 ↔ 문서 꼴» 시험 — 진짜 Django + ninja 로 422(ctx 있는 종류 · 없는 종류) · 401 · 403 · 429 · 400 을 내고 모든 답 키 ⊆ 문서 properties · required ⊆ 답 키 · `ctx` 칸에 null 갈래 · default 없음. backstop: 2.45.0 사본 받음 · 고친 2.45.0 사본 막음.
- **딸린 것**: Codex 미러 · workspace/reference 소스 미러 · LEDGER · rulepack · 골든 · 계수표 · 봉인 목록(manifest_seal · T2-0b) · reverse_coverage · pre_route_canonical_check · 픽스처 정본 사본 셋(새 판으로) · pregate kinds.

## 3. 행동 시험 · 변이

- 같은 장난감: 2.45.0 = 문서 밖 ctx 4건 · 새 판 = 0건 · required 빠진 항목 0. 검사기: 새 정본 사본 exit 0 · 2.45.0 사본 exit 0 · 고친 사본 exit 2.
- 변이(모두 죽어야): ctx 뺌 · `ctx: dict[str, object] | None = None` · 필수 칸(기본 없음) · 받는 목록에서 2_45_0 뺌.

## 4. 차례

구현(운영자 · 작은 수리) → 행동 시험 → 독립 검토 한 번(Claude · 과적합 · 모순 관점 포함) → 처분 → 봉인 · 커밋 → make verify + verify-mutation → 장부 다시 읽기 → push → 깨끗한 클론 make release patch(2.45.1) → 노트 · 봉인 chore → 판 기록 `workspace/plan/2026-11-25-validation-ctx/` → 작업 리스트(F4-216 수리 · 새 보고 F4-207 ~ 215 등록) → 장부 처분 → 정리 → 보고 · 요청한 쪽에 판 번호.

**범위 밖(다음 판)**: F4-204 ~ 215 · 새-1 · 새-2. web 플러그인 무변(422 몸통 꼴을 적은 자리 없음 · 확인함).

**프로젝트 할 일(배포 뒤 알림)**: 새 정본을 `framework/ninja/pre_route_responses.py` 로 다시 옮김 → 생성 문서 · 손님 web 타입 다시 만듦. 옛 사본은 막지 않으므로 옮기기 전까지 다른 프로젝트 실행은 무변.
