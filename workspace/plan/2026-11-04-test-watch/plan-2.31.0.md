# dddjango 2.31.0 — 멈춘 시험 깨우기

함께 나가는 판: dddjango-web 2.9.0(같은 도구 · 문제 · 결정 · 설계 검토 · 행동 시험은 `workspace/plan/2026-10-06-web-dddart/plan-2.9.0.md`).

## 문제

dddjango 조정자 · coder 도 배경 시험의 끝 알림을 기다리기만 한다. 규칙 R-3668(조정자) · R-3670(coder)은 «돌고 있는 시험 멈추기» 의 끄는 법만 있고 무엇이 깨우는지는 없었다. dddjango 의 전체 suite 에도 브라우저 시험이 들어 있어 web 레인에서 6시간 멈춘 것과 같은 시험을 돈다(이 플러그인 기록에서 멈춤으로 확인된 사례는 아직 없음 · 사용자 «가.» = 같은 계획에 넣음).

## 고침

- 새 도구 `scripts/test_watch.py` · `scripts/watch_probe/test_watch_probe.py` — dddjango-web 판과 byte 동일(Makefile `verify-base-core` 가 대조) · Codex byte 미러.
- 그래프 개정: R-3668 · R-3670 리비전 2(amendment) — 블록 `commands/dddjango.md` s007/b9 · `agents/coder.md` s004/b10 에 «멈춘 시험 깨우기» 를 더하고 «돌고 있는 시험 멈추기» 첫머리를 감시 도구 쪽으로. 관련 테스트 · 기능/수정 모드 전체 suite · coder 배경 시험은 `test_watch.py run` 으로 · 리팩토링 모드 `behavior_guard.py` 처럼 출력을 모아 두는 실행은 감싸지 않음(제 시간 상한이 있음 · R-3669 그대로) · 감싸지 않는 실행은 PGID 사다리 그대로.
- 렌더 재투영 · LEDGER 재기준선(s007 · s004 각 두 행 — 개정 · 같은 판 안 행동 시험 맞춤) · 계수표 ExpressionShape +2 · q4 골든 · rulepack 재소성 · Codex 의미 미러(조정자 · coder — Codex 는 앞 실행 · 셸 시간 제한) · `reverse_coverage.py` 설명 두 줄 · Makefile 대조 줄(두 런타임 깨우기 글 · core ↔ web 도구 byte · 도구 시험).

## 행동 변화 · 검토 · 행동 시험 · 한계

dddjango-web 2.9.0 판 기록의 «멈춘 시험 깨우기» 와 같다. dddjango coder 역할 행동 시험: 조용히 멈추는 시험에서 멈춤 확정 → 끔 → 노드만 → 결함 보고 · 살아 있는 묶음 0. acceptance-tester 는 시험 멈추기 규칙이 없고 짧은 실행이라 이번 판 밖(감싸지 않음). coder 는 조정자가 이미 주던 플러그인 설치 루트(Codex 는 조정자 스킬 폴더 절대 경로를 새로 줌)로 도구를 부른다. 구현 검토 맞춤(같은 판 안 — 새 Expression 없음): 셸 별칭 · 함수 안 씀 · 도구가 «다른 실행 환경»으로 끝나면 같은 환경에서 다시 · coder 도구 경로 — LEDGER 재기준선 두 행 더.

## 다음 판으로

- F4-137(pre-gate file-plan 파서의 숨김 세그먼트 경로).

## 검증

(배포 때 채움)
