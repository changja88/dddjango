# pre-gate 차단 승격 배치 (G-A · R-1) — 절차·⓪ 증거·적대 리뷰 루브릭 (2026-09-03)

브랜치 `feat/pregate-enforce`. 절차는 수리 배치 2 판형(`2026-09-03-repair-batch-2-rubric.md`)을 그대로 쓴다:
⓪ 증거 수집 → ① 문제 검증 적대 리뷰(3기) → ② 계획 → ③ 계획 적대 리뷰(3기) → ④ 구현 → ⑤ 구현 적대 리뷰(3기) → ⑥ 감사 + 재검.
결정 게이트(사용자 명시 확정): ① 뒤 «범위 확정» · ③ 뒤 «문면 확정» · ⑥ 뒤 «머지». 릴리즈는 사용자 요청 시까지 보류.
심각도 BLOCKER/MAJOR/MINOR/검증됨 · 3축(코퍼스 정합·일반화·무손실) · 공격 질문 ⓐ 재현성 ⓑ 무손실 판정식 ⓒ 효과 과대.

## 승격 판정 근거 (기계 판정 — 설계 v4 §8)

§8은 «실전 레인 ≥2·신규 BC ≥1에서 ⑴ 오탐 0 ⑵ 미탐 0 ⑶ 형식 반송 ≤1/레인 충족 시 승격»으로 사전 합의된 판정식이다. 재실측 표본(v2.17.16 로드 세션 완주)은 카탈로그 레인 하나이며 신규 BC다.

| 레인 | 판 | 런 | 정위치 형식 red | corrected / ignored / filtered (고유 ID) | G2 귀속 | ③형 STOP | 총 소요 |
|---|---|---|---|---|---|---|---|
| 1 media-library | v2.17.14 | 4 | 2 | 17 ID · 실질 오탐 0 | 0 | 0 | ≈4h10m |
| 2 notification | v2.17.14 | 4 | 0 | 25 ID · 실질 오탐 0(라벨 재분류 후) | 0 | 0 | ≈2h56m |
| 3 email-template | v2.17.14 | 5 | 1(+중반 2 별도) | 7 ID | 0 | 0 | — |
| R reading | v2.17.14 | 44 | 7(중반 포함) | 24 ID · #188 filtered 오처분 → P4 registry 149건 실발화(발견 ⑧) | — | STOP 다수(구판·승격 표본 아님) | ≈49h |
| **4 fortune-catalog** | **v2.17.16** | 4 | **0** | corrected 2(#392·#576 — 다음 실행 소멸 = 진탐) · ignored 0 · filtered 0 | **0** | **0** | ≈6h31m(pre-gate 43분) |

- 기계 판정: 레인 4 = ⑴ 충족 · ⑵ 충족 · ⑶ 충족(0) · 라벨 성문(발견 ①) rev2 적법 기재 → **§8 전 기준 충족**. 가치 실증 4회(레인 1 corrected 6축 · 레인 2 #14 이관 빚 사전화 · 레인 3 #356/#390 · 레인 4 #392/#576).
- ⑷ 계약 실존 채널: 레인 4 최종 run 행 6 · 실존 확인 2 · 저장소 밖 4 · 결손 0 · 도구 오류 0 · 진탐 0 → 별도 판정식(«도구 오류 0 ∧ 진탐 ≥1 over ≥2 레인») 미충족 → **exit 5 비차단 유지**(R-2).
- 표본 외(kkebi-server 21런): 전부 pre-gate 형식 규범 이전 명세(pregate-report 0/21) — 승격 판정의 표본 외 대조는 구조적으로 불가. 대신 «차단 전환이 구형 명세 레인을 세우는가»의 대조로만 쓴다(구형 명세 skip 폐지의 영향 = kkebi형 발주에 블록 의무 발생).

## 승격 패키지 (⓪ 초안 — ①에서 공격 대상)

| # | 항목 | 정본 | 변경 초안 |
|---|---|---|---|
| P1 | 실행기 모드 상수 | `dddjango/scripts/design_pregate.py`(+codex byte 미러) | `MODE = "observe"` → `"enforce"`. 헤더·stdout·요약 문면 «모드 관찰(observe)» → «모드 차단(enforce)». **exit 규약 불변**(0/2/3/4/5/1 · exit 5 비차단 유지) |
| P2 | 구형 명세 skip 폐지(실행기) | 같은 파일 | file-plan 블록 부재 → 현행 exit 4 «skip — 구형 명세 한정 조항» 대신 **exit 3 형식 red «machine 블록 부재 — 차단 모드: 블록 의무»**. 실체화 0·결손 0 skip(공허 차분 가드)은 exit 4 유지. 픽스처 `noblock-spec.md` 신설(exit 3) |
| P3 | R-3433 rev3(redefinition) | `ontology/rules/command-dddjango.ttl` s006/b9 | «red 는 게이트 차단이 아니라 … 권고(관찰 모드)» → **«귀속 red(exit 2)·형식 red(exit 3)는 architect 반송 의무 — G1/G1′ 배너는 최종본 예보가 red 가 아닐 때(exit 0·4·5)만 제시한다. 반송 없이 배너를 내는 유일한 경로는 red 전건에 닫힌 처분 라벨을 근거와 함께 기재하고 배너 예보 1행에 `red N건 · 처분 전건 기재` 를 병기하는 것뿐이다»**. 라벨 집합 불변(corrected\|ignored\|filtered · 실존 채널 corrected\|deferred\|filtered) |
| P4 | 이월 ⑧ — filtered 근거 유형 닫기 | R-3433 rev3 같은 문면 | «`filtered` 의 근거 유형은 둘뿐이다: ⓐ 리포트 사각 목록 항목 인용 ⓑ 같은 형태의 실코드 파일이 해당 검사기 exit 0 인 대조 경로. **판정 입력이 경로·폴더 존재뿐인 구조 규칙(예: #81 트리 밖 칸 · #325 마이그레이션 위치)은 스텁 내용과 무관하므로 filtered 대상이 아니다** — corrected 또는 ignored+빚 매칭이다» |
| P5 | R-3436 개정(Exception → Prohibition · redefinition) | 같은 블록 | «구형 명세 skip 한정» 예외 폐지 → **«machine 블록 부재 skip 금지 — 블록 부재는 형식 red 이며 architect 반송이다(캐시 skip·실체화 0 skip 과 구별)»**. ID 유지(폐지 대신 재정의 — wiring·rulepack 참조 보존 · `djr:deprecated` 는 어휘만 있고 선례 0) |
| P6 | 발견 ⑩ 집행선 — R-3432 rev3(amendment) | 같은 블록 | «Phase 2 중 design-spec 변경(G1′ 반송 개정·정합 개정·설계 진화 전부)은 슬라이스 dispatch 전 `--base` 재발화가 선행한다. **G2 배너 직전 최종 design-spec 의 `--block-hash` 가 pregate-report 마지막 헤더 «블록 해시» 와 같아야 하며 G2 배너에 `pre-gate 최신성: 블록 해시 <값> = 리포트 <값>` 1행을 둔다 — 다르면 재발화 후 G2 다**» (관측 근거: 카탈로그 Phase 2 개정 3회 · 해시 6cf8e2ffdfc3→cb95a1bddb32 · 재실행 0) |
| P7 | 산문 정합 | s006/b9 제목 «(관찰 모드)» → «(차단 모드)» · s002/b8 R-3438 «skip 행의 종류(캐시 skip·실체화 0·구형 명세)» → 구형 명세 삭제 · codex Coordinator SKILL.md 손 미러(같은 취지·codex 병렬 문면 유지) | |
| P8 | manifest | `workspace/tools/manifest_seal.py` GROUPS.pipeline | `dddjango/scripts/design_pregate.py` 등재(설계 §9-6 «승격 릴리즈에서 pipeline 그룹 등재») → 봉인 draft 재발행 |
| P9 | 기록 | ledger «승격 집행» 절 · 로드맵 R-1 · 카탈로그 #392 처분 = 첫 rev2 corrected 표본 병기 · 조감도 | |

건드리는 규범 ID: R-3432(rev3) · R-3433(rev3) · R-3436(rev2 redefinition) · R-3438(amendment · s002/b8) · (검토) R-3437 배너 1행 — «red N건 · 처분 전건 기재» 형식이 R-3437 문면에 필요한지 ①에서 판정.
건드리지 않는 것: exit 규약 · 라벨 집합 · R-3434(대체 금지) · R-3435 · R-3439~3441(provenance) · 검사기 27종 · 계약 실존 채널(exit 5 비차단).

## ① 공격 질문 (리뷰어 3기 · 항목마다 필답)

- A(판정식·효과): §8 판정식이 «신판 레인 1»로 닫히는가(표본 크기·공허 충족·구판 레인 3의 증거 가중치) · 가치 실증 4회의 각 근거가 재현 가능한가 · 차단 전환 후 형식 반송 증가 위험의 근거 수치.
- B(패키지 설계·무손실): P2 exit 3 전환이 구형 명세 레인(kkebi형)을 세우는가 → 이것이 의도된 손실인지 · P3 «반송 의무 + 처분 예외»가 관찰 모드와 실질 동일해지는 구멍(ignored 남용) · P4 «구조 규칙» 정의가 결정적인가(경로·폴더 존재 판정 = 어떤 검사기 집합?) · P6 해시 대조가 R-3432 캐시 skip 규칙과 모순 없는가.
- C(코퍼스 정합·표본 외): R-343x family 전수 열거 후 충돌/중복/약화 없음 · design-architect 에이전트·codex 미러·픽스처 러너·manifest·rulepack 체인의 드리프트 지점 · «관찰 모드» 문자열이 남는 모든 정본/투영물 위치 열거.
