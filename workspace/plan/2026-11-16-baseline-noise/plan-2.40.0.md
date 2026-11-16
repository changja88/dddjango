# dddjango 2.40.0 — 판정 차분 게이트 기준선 일곱 · 검사기 ⓓ 물음 소음 셋 · 글 둘

상태: 배포 끝(2026-11-16 23:33 · 태그 `dddjango--v2.40.0` · 고침 f3563ff9 · release 3b6d470a · 봉인 c558cfa3 · 사실 칸 446efd2d · 42cbe852).

- 계획: `plan.md`(v1.2 — 계획 독립 검토 · 좁은 재확인 처분 반영).
- 설계 정리본: `design.md`(설계 초안 셋 — c 글 v3 · b 검사기 v3 · a 게이트 v5 · 현장 이름 걷음). 구현 중 바뀐 것은 이 문서 «결정» · «독립 검토 반영» 이 정본이다.
- 규칙 글의 최종 문장은 렌더된 파일에 있다.
  - `dddjango/skills/discipline-houserules`(§3 «포트 메서드 이름» 새 블록) · `discipline-cleancode`(§2.6 다시 말함 블록).
  - `dddjango/agents/discipline-reviewer.md`(감수 물음 #485) · `design-architect.md`(자기모순 스캔) · `acceptance-tester.md`(arrange 점검 입력 · 읽기 범위 · 도구) · `dddjango/commands/dddjango.md`(arrange 점검 입력 · 판정 차분 게이트 계약 줄).

## 범위

판정 차분 게이트(G2)의 기준선 오판 · 검사기 ⓓ 물음 소음 · 규칙 글 어긋남을 고친다. 사용자 «3판 진행하자.»(11-16 02:56)로 `work_list.html` 3판 항목을, «가»(08:42)로 재현 중 찾은 게이트 결함 셋(N1 ~ N3)을 넣었다.

| 단위 | 보고 | 고친 것 |
|---|---|---|
| A 게이트 · 기준선 | F4-27 · F4-136 | `findings.py` — 검사기 위반 기록의 기본 자리는 온톨로지 A/B 실런일 때만 · `anchor_diff.py` scope 렌더 직접 실행도 `DJR_VIOLATIONS_DIR` 를 걷음 |
| A | F4-28 · N2 · N3 | `registry_gate.py` · `checker_target.py` · `check-app-container.py` · `check-idempotency-scope-creep.py` — 지금 사본 «건드림» = 앵커부터의 변경(`DJR_SOURCE_GIT_BASE`) · 앵커 사본 = 커밋 트리 표지(`DJR_COMMITTED_SNAPSHOT`) · 승인 머지 출처 재실행 = 앵커..그 커밋(`DJR_SOURCE_GIT_TIP` · 게이트 사본에서만) · git 뿌리 아래 하위 폴더 대상도 같은 기준 · 직접 실행의 첫 `migrations/` 폴더 |
| A | N1 | `registry_gate.py` — 계약 문법 검사기 일곱의 줄 차분(다중 집합 순번 · 흔들리는 칸만 다른 줄 짝 · 레코드가 성하지 않으면 2.39.0 합성 줄) |
| A | F4-46 | `registry_gate.py` — ⓓ 후보 수 칸 줄음은 그 파일이 지움만일 때 legacy 짝(폴더 조건은 #547 만) |
| B 검사기 | F4-26 · F4-32 · F4-95 | `check-domain-model.py`(#257 확인 뒤 값만 돌려주는 return · 길 읽기 · self 컨테이너 바꿈) · `check-usecase-dto-placement.py`(#191 묻는 동사 머리) · `check-port-adapter-pairing.py`(#485 원시 값 · Enum 반환 + 모호 동사 아님 · 물음 글) |
| G 그래프 · 글 | F4-29 · F4-45 · F4-95 · N1 | 새 Norm R-3765 · R-3766 · 개정 R-1754 · R-3607 · R-3608 · R-3613 · R-3614 · R-3615 · R-3617 · R-1123 · 새 블록 둘(houserules s011-3/b4 · cleancode s018-2.6/b2) · 트리 명세 #485 행 · DEVELOPMENT §3 체크리스트 8 한 줄 |

- 그래프: target-counts NormShape · WorkShape +2 · ExpressionShape +10 · BlockShape +2 · LEDGER 7 행 · q4 골든 rows 3764 → 3766.

## 결정

- **사용자 결정**: 3판 «3판 진행하자.»(11-16 02:56) · 범위 «가»(08:42) · F4-95 «확정»(13:30 — 포트 메서드 이름 규칙 넷 · 검사기 면제 · 받아들인 놓침 · 기억 port-query-noun-decision-1116) · 게이트 셋째 확인 차단 «가.»(16:07 — 고치고 넷째 확인) · 계획 «진행»(18:43).
- **운영자 처분**(질문 생략 · 설계 처리 · 이의 시 뒤집음 — 계획 승인 때 밝힘): `plan.md` «결정» 운영자 처리 1 ~ 9. 특히:
  - 승인 머지가 들인 파일(마이그레이션 포함)을 레인이 고친 것은 레인 몫 아님(넷째 확인 검토자는 legacy 앱 쪽을 «귀속이 맞다» 고 적었음 — 검사기 정의 «새 파일» · 2.39.0 판정에 맞춤).
  - 레인 문서 «멱등성 미요청» + 승인 머지가 들인 멱등 파일은 2.39.0 처럼 귀속.
  - F4-95 결정 밖 세부(«그 목록 · Optional» 해석 · Enum 은 `enum` · `django` 기저만 · cleancode §2.6 은 넓히지 않음).
- **구현 중 운영자 처분**: 구현 검토가 찾은 하위 폴더 프로젝트 차단 · #257 컨테이너 바꿈 놓침은 고침 · 구현자 지시 밖 고침 둘(`anchor_diff.PathFacts` 의 경로 기준 맞춤 — 없으면 하위 폴더에서 2.39.0 이 막던 꼴을 새로 뚫음 · #257 return 식 안 self 바꿈)은 넣음 · 확정 줄 안내 글(«물으면 묻는 꼴»)은 그대로.

## 사용자에게 보이는 변화

- G2 의 거짓 «legacy 해소» 가 사라지고, 레인의 새 마이그레이션 · 새 평면 앱 · legacy 멱등 파일 고침을 커밋 여부와 상관없이 귀속한다.
- 계약 문법 검사기 일곱에서 legacy 가 새 위반을 가리지 않는다.
- 승인 머지가 그대로 들인 legacy 앱 마이그레이션 · 새 평면 앱 · 계약 위반은 «승인 유입» 으로 기록되고 막지 않는다.
- 검사기 ⓓ 물음이 줄어든다(대상 저장소 사본: #485 69 → 38 · #257 120 → 74 · #191 4 → 0 · 새로 묻는 자리 0).
- 포트 메서드 이름 규칙(조회면 명사구 · 묻는 꼴도 · 아니면 명령이라 동사구)이 런타임 글에 생겼다.
- 검사기를 직접 돌려도 대상 저장소 작업 트리에 위반 기록 파일이 남지 않는다.
- 새로 막는 것 · 푸는 것 · 한계: `plan.md` 그대로 — 사용자에게 닿는 것은 릴리스 노트 «도는 실행에 미치는 것» · «받아들인 한계».
- 진행 중 레인은 pre-gate 재예보가 필요하다(`dddjango/scripts` 가 바뀌어 툴체인 digest 가 바뀌고 계약 검사기 줄의 안정 ID 가 바뀜).

## 독립 검토 반영

- **설계**: c(글) 차단 0 · 중요 5 · 사소 9 → 재확인 1 닫힘 · b(검사기) 차단 1(F4-95 → 사용자 결정) · 중요 2 · 사소 5 → 재확인 둘 닫힘 · a(게이트) 차단 1 · 중요 8 · 사소 5 → 재확인 1(새 차단 1) → 셋째 확인(차단 1 남음 → 사용자 «가.») → 넷째 확인 차단 0(중요 1 · 사소 1 구현 때).
- **계획**: v1 검토 차단 0 · 중요 5 · 사소 11 → v1.1 좁은 재확인(중요 1 · 사소 4) → v1.2. 검토자가 a + b 합친 시제품으로 시험 행렬을 돌려 새 붉음 0 확인.
- **구현 — 코드**: 차단 1(git 뿌리 아래 하위 폴더 프로젝트에서 무관 변경 레인이 손대지 않은 legacy 앱 귀속) · 중요 1(#257 앞 갈래의 self 컨테이너 바꿈 놓침) · 사소 4 → 모두 고침 → 좁은 재확인 새 지적 0.
- **구현 — 글**: 차단 0 · 중요 0 · 사소 6(다섯 고침 · 하나 받아들임) → 좁은 재확인 닫힘.
- 차단 · 중요는 모두 운영자가 장난감 · 사본으로 재현한 뒤 처분했다.

## 검증

- 합친 main(넣을 때마다): 세 단위 diff 를 넣은 판으로 시험 13(fixture_matrix 171 · findings_count 지문 하나 계획대로 · registry_gate_smoke · anchor_diff_smoke · pregate 셋 · 현장 보고 시험) · 고침 뒤 새 diff 와 worktree byte 같음(51 파일).
- 체크리스트 8: Codex byte 미러 아홉 · findings_count EXPECTED port-adapter 지문 하나(`b0c0ad90cfce6b9e` → `423cf2d5c9625d1d` — 물음 글) · checker_baseline · cross · construct_drift 무변 · `pregate_symbol_kinds.json` 마지막 재소성 · 봉인.
- **push 전**(커밋 f3563ff9): `make verify` 6/6 녹색(1685초 — 검사기 행렬 928 · `fixture_matrix` 171 · 현장 보고 시험 182 · 기준선 시험 145 · 귀속 시험 97(표 45/45) · cross 349 차이 0 · baseline 73 · findings_count 73 · 대표 byte 골든 8 · 탐침 644/644 · `folder_group` 567 / 568(Python 3.9 · 3.15) · `test_watch` 73 · pre-gate · behavior_guard · refactor_audit 픽스처 PASS) · `make verify-mutation` exit 0(843초 — 변이 12 · 83 · fixture_matrix 208 · 현장 보고 186 · registry_gate 11 + 기준선 · 귀속 50 · pre-gate 21 · behavior_guard 9 · refactor_audit 61 전부 red).
- **대상 저장소 사본**(읽기만 · 2.39.0 대비): 게이트 `--anchor HEAD` 표 `check-app-container.py | 2 | 0` → `0 | 0` · 거짓 해소 1 → 0 · 그 밖 차이 0 · 검사기 #485 69 → 38 · #257 120 → 74 · #191 4 → 0(새로 묻는 자리 0 · 그 밖 줄 byte 같음) · 실행 시간 느려짐 없음.
- **배포**: 깨끗한 클론의 `make release` 안 `make verify` 6/6 녹색(2961초) · 총 49분 30초 · 봉인 `--check --draft` green(그룹 10 · 봉인 파일 272 · 엄격 `--check` 의 붉음은 설치 캐시 · 실험 부속 기록 항목뿐) · `claude plugin validate` 는 릴리스 1/7 단계에서 통과. 봉인 chore 에서 T2-0b 설계 문서의 사실 칸을 빠뜨려 뒤 커밋 둘로 맞췄다.
- **장부**: 계획 확정 때 · 배포 직전 마지막 F4-180(11-16 00:44 뒤 바뀜 없음 — 새 보고 0).
- **요청 가이드**: 바뀔 것 없음(요청 칸 · 좋은 예 · 나쁜 예 · 플러그인이 묻는 일 그대로 · 포트 메서드 이름 규칙은 설계 · 감수 쪽 글).

## 다음 판 후보

- 이번 판에서 본 옛 구멍(2.39.0 같음): `anchor_diff` 의 `exists_at` 이 하위 폴더 대상에서 `git cat-file -e <sha>:<path>` 로 늘 «없음» — `<sha>:./<path>` 로.
- #485 남은 소음(목록 밖 동사 · 현장 25/38) · #191 다른 동사 머리 · F4-26 덤(덧셈 대입 · 끝 if) · 양쪽 고친 자동 머지 사각(pre-gate · arrange 점검) · 기존 시험에 대상 저장소 BC 이름과 같은 이름(이번 판이 들인 것 아님 — 지은 이름으로 바꿈).
- 그 뒤 차례: `work_list.html` 그대로(F4-150 큰 판 → web 판).
