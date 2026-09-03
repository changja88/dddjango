# 현장 보고(typecheck) 회신 — dddjango 처분 (2026-09-03)

대상 보고: `2026-09-03-field-report-spring-dream-typecheck.md`(spring_dream_server 발주자 세션). 검증 절차: 적대 리뷰 ①(문제 검증)·③(계획) 각 3기 + 구현 ⑤·감사 ⑥ — 루브릭 `2026-09-03-field-report-repair-rubric.md`, 계획 `2026-09-03-field-report-repair-plan.md`, 증거 `workspace/eval/field-report-typecheck/`.

| # | 보고 항목 | 판정 | 처분 |
|---|---|---|---|
| A | 값 객체 템플릿의 선언 타입 재검사 | **성립** — 단 «죽은 조건» 전제는 과장(mypy는 `float` 자리 `int`·`int` 자리 `bool`을 통과시키므로 float/bool 가드는 살아 있음 · 어드민 폼 2곳은 `dict[str, Any]`를 팩토리에 직접 전달) | 규범 정본 리비전: `architecture-ddd` §3.1 Money 예제 교체(타입 재검사·`int()` 강제 변환 삭제 → `type(x) is bool` 값 검사 · `result: int` · PhoneNumber `-> None`) + 신규 규범 **R-3442**(자기 검증은 값의 불변식만 · 타입 체커 통과 값의 거부는 `type(x) is T` 형 · 시그니처가 수용을 약속한 값은 거부하지 않음 · **적용 대상 = 이번 작업이 새로 쓰거나 손대는 값 객체** — 기존 코드 소급 아님) · **R-3443**(값 객체 안 선언 타입 재검사·강제 변환 금지 · 좁히기는 값 객체 호출 전 경계 소유). 렌더본 mypy strict(+warn_unreachable+redundant-expr) 0건·plain strict 0건 실측 |
| A-3 | 제안 3(`type: ignore[arg-type]` 거부 테스트 금지 규율) | 범위 밖 | 1프로젝트 테스트 관행 기반 — 이번 배치 제외(과적합 경계). 필요 시 별도 발주 |
| A-4 | 제안 4(예제 mypy 스모크 하네스) | 기각 | 코퍼스 예제 strict-clean 비율 4/28·12/78 — 1블록 하네스는 과적합 |
| B | G2에서 mypy·ruff format이 결정적 단계가 아님 | 사실 검증됨(23 run 중 mypy 무기록 7 · A/C 발화 3레인 전부 무기록) — **기각·발주측 소관** | 프로젝트 툴체인 선택은 플러그인이 게이트로 삼지 않는다(다른 프로젝트 오차단·설정 결합). 정위치 = pre-push 훅 + 발주서 G2 체크리스트(발주자가 이미 적용). R-12 발주 가이드에 «툴체인 게이트는 훅·발주서 소유» 1줄 반영 예정. reading REPORT의 mypy 무언급은 «미실행 사유 명시» 기존 문면 미준수 |
| C | 하우스룰 §2가 Enum 멤버에 타입 주석을 요구 | **불성립(문면)** — Enum 멤버 예외는 R-3154(SKILL.md:72 «프레임워크 선언 … enum 멤버(`RED = 1`)»)에 v1.0.0부터 성문·Coordinator·검사기 docstring·pregate b35·rulepack 5표면 일치 | 규범 변경 0. 실물 원인 = **검사기 #493의 import 별칭 사각**: `from enum import StrEnum as _StrEnum` 형상에서 base 이름을 문자열 비교해 무주석 멤버를 blocker로 오판 → 레인이 주석 부착으로 우회 → mypy `[misc]`. 09-01 STOP(strenum-registry-alias)에서 결정 C(plain StrEnum)로 종결됐으나 WIP 커밋 2파일 잔재. **검사기 수리**: base·데코레이터 이름을 모듈 import 바인딩으로 원명 해소(그림자 pop 포함) — 오탐 소거 + 별칭 그림자 미탐 폐쇄 · 양 저장소 전/후 차분 0 · 픽스처 good/bad 추가 · 증거 `evidence-alias-strenum/`(orig 6 → patched 0). 잔재 2파일 정리는 발주측(09-03 17:57 커밋으로 이미 해소 확인) |

## 발주측에 남는 것
- B: pre-push 훅·G2 체크리스트 유지(플러그인 수정 없음). `mypy --follow-imports=silent <BC 루트>` 판형은 발주서 소유.
- A: 기존 값 객체의 재검사 정리는 소급 의무가 아니다(R-3442 적용 대상 = 신규·수정). 정리 커밋은 발주측 재량.
- C: 별칭 import(`as _StrEnum`)는 이제 검사기가 원명으로 풀지만, 09-01 결정 C(plain StrEnum)를 바꿀 이유는 없다.

## 릴리즈
- 수리는 브랜치 `fix/field-typecheck`에 착지. 릴리즈 시점은 사용자 결정(즉시 v2.17.17 또는 pre-gate 승격 배치 동승).
