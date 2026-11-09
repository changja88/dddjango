# dddjango 2.34.0 — 레인을 멈추는 현장 보고 수리 13건

상태: 배포 끝(2026-11-10 02:39 · 태그 `dddjango--v2.34.0` · 커밋 4d785333 · release 98dac918 · 봉인 425ab211). 계획 전문(항목마다 고친 자리 · 파일 · 일하는 법)은 `plan.md`, 규칙 글의 최종 문장은 렌더된 `dddjango/agents/design-architect.md` · `dddjango/agents/design-review-api.md` · `dddjango/agents/design-review-ddd.md` · 스킬 `implementation-django-ninja` · `architecture-api` · `discipline-houserules` 에 있다.

## 범위

장부의 열린 항목 46건을 읽어 대조한 뒤(고쳐짐 1 · 일부 11 · 그대로 34), 묶음 순서 1판 «레인을 멈춤» 을 배포판 2.33.0(태그 `dddjango--v2.33.0` · a4f005ec)으로 재현했다. F4-34 · F4-55 는 현장 꼴이 쓰임새 호출 뒤라 대상에서 빠졌다.

| 묶음 | 항목 | 고친 것 |
|---|---|---|
| 호출 앞 입력 검사 | F4-130 | #15 가 쓰임새 호출 앞을 판정 · 오류 동작은 위반 · 메시지 세 갈래 · 406 · 415 비켜 줌 · 글(§2.2 · 상태 코드 표 · G1 표면) |
| OHS 승인 값 | F4-105 | exception-map 값 칸 · G2 한 문장 `raise` 꼴 · #474 · #153 공용 판정 |
| 기준선 · #2 | F4-59 ① · F4-40 · F4-37 · F4-44 | 못 읽음에 버팀 · 오류 모듈 없는 BC 걷기 · common 오류 모듈 넣기 · 없는 경로 빼기 |
| 구조 · 실행 검사기 | F4-131 · F4-94 · F4-62 ① · F4-138 · F4-137 · F4-157 | 포트 이름 파일별 제외 · #101 부칙 · BC `test/` 직계 `conftest.py` · cron_job 입구 · 숨김 경로 범위 · 이번 실행 줄의 앵커만 사용 |
| 리뷰 글 | F4-143 | 저장 경계 리뷰를 사실 · 도메인 이벤트를 내보내는 유스케이스로 좁힘 |

## 결정

- 사용자 결정(2026-11-09 «진행하자»): 남은 항목은 결정은 하나씩 · 고침과 배포는 묶음으로. 1 레인 멈춤 → 2 위반을 못 잡음 → 3 소음 · 글 → 4 F4-150 → 5 web · «설계 때 못 봄» 은 보류.
- 사용자 결정(2026-11-09 «나.»): 빈 값 · 범위 같은 입력 확인은 입력 Schema 선언으로만 · 응답은 framework 422 · 컨트롤러 = 입력 · 유스케이스 = 말이 되는 요청인지.
- 사용자 «진행해»(2026-11-09): 계획 v3 승인.
- 운영자 처분(질문 생략 · 설계 처리 · 이의 시 뒤집음): F4-105 = OHS 입구도 승인 값만 허용 · F4-143 = 리뷰 문구만 좁힘.

## 한계

`plan.md` «받아들이는 한계» 그대로다. 사용자에게 닿는 것:

- 입력 Schema 검증의 422 본문에는 BC `code` 가 없다. 코드로 오류를 가르는 소비자(web 의 `safe_api_call`)는 이 경우를 코드로 가를 수 없다.
- 쓰임새 호출 알아보기는 글자 판정이라 `self._repo.find()` 뒤 `is None` · `run_it(build_x(), id)` · 같은 파일 도움 함수 안의 호출이 호출 앞으로 나온다.
- F4-105 의 명세 값 칸과 코드 필드의 일치는 G2 기계 밖이다(감수 몫).

## 독립 검토 반영

- 계획 독립 검토 1: 차단 3 · 중요 11 · 사소 9 — v2 에 반영. 좁은 재확인 뒤 v3.
- 구현 독립 검토 1: 차단 1 · 중요 4 · 사소 8 — 차단은 빈 폴더에 기댄 픽스처. 좁은 재확인에서 B1 · M1 ~ M4 닫힘 · 새 문제 N1 고침 · N2 는 한계.
- 운영자가 첫 추천에서 틀린 것 둘을 사용자가 바로잡았다: 호출 앞 입력 확인의 자리(옆 규범을 안 읽음) · F4-105 를 빈도로 미룬 것.

## 검증

- 시험: 항목마다 픽스처 · 스모크(옛 판 붉음 → 새 판 녹색) — `api_error_backstop_matrix` · `fixture_matrix` · `anchor_diff_smoke` · `field_report_checker_smoke` · `pregate_field_report_smoke` · `pregate_transcription_smoke` · `registry_gate_smoke` · `behavior_guard_fixture_run` · `folder_group_fixture_run`.
- 커밋 뒤 push 전 `make verify` 6/6(2121초) · `make verify-mutation` exit 0(변이 12 · 81 · 줄 대조 60 · registry_gate 11 · pre-gate 4 · behavior_guard 9 · refactor_audit 5 전부 red 확인).
- 깨끗한 클론의 `make release` 안 `make verify` 6/6(2272초) · 봉인 `--check --draft` green(그룹 10 · 봉인 파일 270).
- 장부: 계획 확정 때와 배포 직전 모두 마지막 F4-159 · 새 항목 없음 · 배포 뒤 13건에 수리 처분 줄 · F4-34 · F4-55 에 대상 아님 처분 줄.
- 요청 가이드 · README · `docs/`: 바뀔 것 없음(사용자가 요청에 쓰는 칸 · 물음이 그대로이고, `docs/file_tree.html` 의 422 줄은 새 규칙과 같다).
- 레인 영향: `dddjango/scripts/` 가 바뀌어 진행 중인 실행의 pre-gate 예보는 툴체인 stale — 다시 예보해야 한다.

## 다음 판 후보

- 2판 위반을 못 잡음(F4-50 · F4-49 · F4-103 · F4-83 · F4-135 · F4-33) → 3판 소음 · 글 → 4판 F4-150 → 5판 web.
- 새 보고 F4-158 · F4-159(Django admin 입구).
