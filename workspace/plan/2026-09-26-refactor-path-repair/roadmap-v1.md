# 로드맵 v1 — 결정 1~6 전부 진행 후 한 번에 배포 (2026-09-26 22시대 사용자 승인)

사용자 원문: «아니 전부다 진행하고 배포하자. 어차피 spring dreram server 할일 다하고 쓸거니깐» → 검증 단계를 넣은 수정안에 «그러자».
결정 기록: `evening-report.md` §5.

| # | 작업 | 검증 | 끝 |
|---|---|---|---|
| 1 | 이번 변경 마무리(결정 5 반영 — 규칙 이전 폴더 = 끝남 → 새 실행) | 시험 T5n·T5c 재실행 · `make verify` | 변경 커밋 → 봉인 chore 커밋 |
| 2 | 결정 3 F4-24 문언 정정(R-3448 clarification · 잠금 픽스처 1) | `make verify` | 커밋 |
| 3 | 결정 4 pre-gate 4개(digest → F4-23 → F4-22(문서 반영 필수) → F4-21) | 결함마다 재현(수정 전 red · 수정 후 green) · 픽스처 · 구현 리뷰 · `make verify` | 커밋 |
| 4 | 결정 2 동작 보존 장치 최소판(정리 있는 모든 작업 · 문서 층 보고만) | 동작을 일부러 바꾼 사본으로 탐지 시험 · 구현 리뷰 · `make verify` | 커밋 |
| 5 | 결정 1 dddjango 리팩토링 커맨드(리뷰어 전체 점검 → architect 판정 → 사용자 G0 · 약한 단언 강화 결정 포함) | 행동 시험 · 구현 리뷰 · `make verify` | 커밋 |
| 6 | 결정 1 web — 기능 요청 빚 처리(dddjango 와 동일) + web 리팩토링 커맨드(동작 보존 장치의 web 판 설계 포함) | 행동 시험 · 구현 리뷰 · `make verify`(verify-web 포함) | 커밋 |
| 7 | **통합 검증** — 최종 합본으로 | 전체 행동 시험 회귀(기존 22 + 신규) · `make verify` · `make verify-mutation` · Codex 미러 대조 · `claude plugin validate --strict` ×2 | — |
| 8 | **실전 리허설** — spring_dream_server 사본에서 배포 전 플러그인으로 끝까지 실행(원본 쓰기 0 · 결과물 폐기) | 리팩토링 커맨드 BC 1(service_policy) · 작은 기능 수정 1(빚 조사→정리→동작 보존) · web 작업 1 · G2 까지 | 리허설 보고 |
| 9 | 배포 | 릴리즈 창(진행 중 dddjango 레인 G0~G2 사이 0) 확인 · `make release` · `make release-web` · 봉인 재발행 | — |
| 10 | 배포 후 | 설치본 갱신 확인 · 발주자 세션 가이드 재독 · 첫 실전 레인 관찰 | — |

- 3~6 은 각각 수리 관례 절차를 따른다: 진단 → 설계 → 적대 검토 → 계획 → 계획 리뷰 → 구현 → 행동 시험 → 구현 리뷰 → verify.
- 사용자가 정할 것은 그 자리에서 짧게 묻는다. 결정은 명시 답 뒤에만 기록한다.
- 커밋은 항목마다 로컬로 한다(사용자 기존 변경 4건 제외: `docs/master.html` · `workspace/eval/field-report-4/…` · `workspace/plan/2026-09-26-refactor-campaign/` · `synthesis-v2.md` 의 사용자 몫). push 는 9 에서 한다.
- 8 의 로컬 플러그인 실행 방법은 그 단계에서 확인한다.
