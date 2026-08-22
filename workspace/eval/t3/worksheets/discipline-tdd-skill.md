# T3 저작 검수표 — discipline-tdd-skill

- 원문: `dddjango/skills/discipline-tdd/SKILL.md (53행)` · spec: `workspace/eval/t3/specs/discipline-tdd-skill.spec.json`
- 자기 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/discipline-tdd-skill.spec.json` → **exit 0** (블록 4·5·12·16 = 37 · Work 26 · exit 0 · `--write` 미사용)
- 필독 이행: 발주서 · authoring.md §13~§16 · `ontology_migrate.py` 선두 docstring · 파일럿 spec 2건 · `dddjango/scripts/check-*.py` **27종 docstring 선두 전수 실독**(묶음 «py-test-skills» 3문서 공통 1회)

## 1. census 대사

| 절 | 헤딩 | 발주서(센서스) 규범 수 | spec 규범 수 | 블록 수 | 판정 |
|---|---|---|---|---|---|
| s001 | (전문) — frontmatter | 2 | 2 | 4 | 일치 |
| s003 | 언제 쓰나 | 5 | 5 | 5 | 일치 |
| s004 | 핵심 운영 원칙 | 17 | 17 | 12 | 일치 |
| s005 | 상세 레퍼런스 | 2 | 2 | 16 | 일치 |
| **계** | — | **26** | **26** | **37** | **불일치 절 0** |

불일치 절 0. s004 는 12불릿·17 Work — **문장 해상도 그대로**(불릿별 1·1·1·1·2·3·2·1·1·1·2·1)로 17 이 나온다.
- 이 문서에서는 «한 문장 안 다른 deontic class» 분할이 필요 없었다. 분할 후보 2건은 다음 근거로 1 Work 를 유지했다:
  22행(«고전 학파 기본, … 목적일 때만 런던 학파 선택») = 조건이 내장된 **단일 선택 규칙**이라 Obligation 1;
  23행(«4대 기둥 … — 리팩토링 내성은 타협하지 않는다») = 뒤 절이 앞 의무의 **강조 절**이라 Obligation 1.
  둘 다 분할하면 19가 되어 센서스와 어긋난다 → **센서스 산정이 옳다**고 판정.
- 24·25·26·30행은 문장이 각각 2·3·2·2개라 그대로 2·3·2·2 Work.
- s005 표 13행은 센서스 비고대로 비규범(라우팅 정보).

## 2. 배선 근거 표 (전 규범)

| # | 절·블록 | class | Work label | enforcedBy | delegatedTo | 4원 근거(① 문면 역할명 ② docstring § 인용 ③ P0 커버 ④ registry·기본값) |
|---|---|---|---|---|---|---|
| 1 | s001/b2 | Obligation | TDD 사이클 설계·학파 선택·테스트 생성·수명 주기·검증 우선순위 결정 시 로드 | — | agent-discipline-reviewer | ①문면 — 프론트매터 description 은 스킬 라우터 트리거(«…필요하면 로드한다») · ②check-*.py 27종 docstring 선두 전수 실독 — 스킬 로드 라우팅을 집행하는 검사기 0 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 2 | s001/b2 | Obligation | 테스트 코드 작성법(mock·assert·픽스처·pytest 메커니즘)의 implementation-test 위임 | — | agent-discipline-reviewer | ①문면이 위임 상대를 직접 지정 · ③discipline-tdd-final s038-8 b1 «테스트 더블 분류·Python 구현의 implementation-test 위임» 동축 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 3 | s003/b1 | Obligation | TDD 운용·학파 선택·테스트 목록 시작점·AI 보조 명세 활용이 불명확할 때 로드 | — | agent-discipline-reviewer | ①문면 «…불명확할 때 로드한다» · ②check-*.py 27종 docstring 선두 전수 실독 — 스킬 로드 조건 판정 술어 0 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 4 | s003/b2 | Obligation | pytest fixture·mock·assert·팩토리 상세 작성법의 implementation-test 위임 | — | agent-discipline-reviewer | ①문면 «→ implementation-test» · ③discipline-tdd-final s038-8 b1 동일 위임 스텁의 요약 사본 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 5 | s003/b3 | Obligation | 테스트 코드 품질(가독성·구조·냄새) 원칙의 discipline-cleancode 위임 | — | agent-discipline-reviewer | ①문면 «→ discipline-cleancode» · ④§16 기본값 표 discipline-cleancode 행 → agent-discipline-reviewer |
| 6 | s003/b4 | Obligation | Django TestClient·API 테스트 메커니즘의 implementation-django 위임 | — | agent-discipline-reviewer | ①문면 «→ implementation-django» · ②check-*.py 27종 docstring 선두 전수 실독 — 스킬 간 관할 이관 술어 0 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 7 | s003/b5 | Obligation | migration 전용·DB-backed 현행 동작 테스트 기술적 식별의 implementation-test 위임 | — | agent-discipline-reviewer | ①문면 «→ implementation-test» · ③discipline-tdd-final s025-5.5 b46 «기술적 식별 예시의 implementation-test §1.4 위임» 동일 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 8 | s004/b1 | Obligation | TDD 목표 — 작동하는 깔끔한 코드와 두려움 없이 변경할 용기 | — | agent-discipline-reviewer | ①문면 «TDD의 목표는 … 용기가 핵심» — 가치 선언이나 후속 규범의 보수(保守)를 포함(센서스 P0 승계) · ②check-*.py 27종 docstring 선두 전수 실독 — TDD 목표 판정 술어 0 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 9 | s004/b2 | Obligation | Red-Green-Refactor 순서 준수 — 실패 테스트 먼저·통과 후에만 리팩토링 | — | agent-discipline-reviewer | ①문면 «순서를 지켜라» · ③discipline-tdd-final s006-2.1 b1 Red/Green/Refactor 3 Work 의 요약 사본 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 10 | s004/b3 | Obligation | 고전 학파 기본·협력 구조 설계 목적 한정 런던 학파 선택 | — | agent-discipline-reviewer | ①문면 «…기본으로, … 목적일 때만 … 선택한다» — 조건 내장 단일 선택 규칙 · ③discipline-tdd-final s012-3.4 b7 «저장소 기본은 고전 학파» 동축 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 11 | s004/b4 | Obligation | 좋은 테스트 4대 기둥 준수와 리팩토링 내성 비타협 | — | agent-discipline-reviewer | ①문면 «…리팩토링 내성은 타협하지 않는다» — 4대 기둥 준수의 강조 절 · ③discipline-tdd-final s015-4.2 b1 동축 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 12 | s004/b5 | Prohibition | 테스트 목록의 후보 지위 — test artifact 작성 의무 아님 | — | agent-discipline-reviewer | ①문면 «테스트 목록은 후보일 뿐이다» · ③discipline-tdd-final s021-5.1 b1 «후보 목록은 탐색 메모 — test artifact 작성 의무 아님»(Prohibition) 동일 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 13 | s004/b5 | Obligation | 전 영구 test artifact 변경 전 §5.5 입장 심사와 의미 보존 재조직의 새 case·Red 0 | — | agent-discipline-reviewer | ①문면 «…전에 §5.5 입장 심사를 거치며 …» · ③discipline-tdd-final s025-5.5 b2·b17 동축 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 14 | s004/b6 | Obligation | 영구 테스트의 판정 기준 — 승인된 현행 계약·독자 실패·기존 권위 coverage | — | agent-discipline-reviewer | ①문면 «영구 테스트는 … 판정한다» · ③discipline-tdd-final s025-5.5 b1·b5~b7 심사 열의 요약 사본 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 15 | s004/b6 | Permission | 공개 Python 계약의 자격 근거 택일(별도 사용자 승인 또는 deployed consumer evidence) | — | agent-discipline-reviewer | ①문면 «… 중 하나로 자격을 얻는다» · ③discipline-tdd-final s025-5.5 b34 «공개 Python 계약의 근거 택일 입장»(Permission) 동일 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 16 | s004/b6 | Prohibition | pending 의 G1 차단과 reuse·reject 의 test artifact write 0 | — | command-dddjango · agent-discipline-reviewer | ①문면 «pending은 G1을 막고 reuse·reject는 test artifact write가 0이다» · ③discipline-tdd-final s025-5.5 b17 에서 pending 차단 조항은 command-dddjango(게이트 승인 주체)로, write 0 조항은 discipline-reviewer 로 배선된 선례 — 한 문장 압축이라 두 소유자 병기 · 센서스 P0 표류 의심 기록(final 원문은 G1/G1preview·Phase 2 를 모두 막지만 스킬 사본은 G1 만 언급) |
| 17 | s004/b7 | Prohibition | migration 전용 테스트의 신규 생성·새 case·assertion·시나리오 확장 금지 | — | agent-discipline-reviewer | ①문면 «…만들거나 … 확장하지 않는다» · ③discipline-tdd-final s025-5.5 b46 «migration 전용 테스트 신규 생성·확장 금지» 동일 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 18 | s004/b7 | Obligation | 과거 버그 출신이라도 현행 계약을 검증하는 회귀 테스트 보존 | — | agent-discipline-reviewer | ①문면 «…회귀 테스트는 보존한다» — 스킬 사본은 보존을 의무로 진술(final s025-5.5 b37 은 같은 내용을 Permission «유효 회귀 테스트»로 진술 — 압축 시 강도 상향) · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 19 | s004/b8 | Obligation | 초록 막대 전략 순서 — 가짜로 구현하기→삼각측량→명백한 구현 | — | agent-discipline-reviewer | ①문면 «…순으로 진행» · ③discipline-tdd-final s027-6.1 b1 동축 · ②check-*.py 27종 docstring 선두 전수 실독 — 구현 진행 순서 술어 0 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 20 | s004/b9 | Obligation | 테스트 격리와 AAA 패턴 구조화 | — | agent-discipline-reviewer | ①문면 «격리하고 … 구조화하라» — 같은 deontic class 의 병렬 절이라 1 Work · ③discipline-tdd-final s031-7.1 b1·b2 동축 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 21 | s004/b10 | Obligation | Mock 보다 출력·상태 검증 우선(Mock 과다는 리팩토링 내성 약화) | — | agent-discipline-reviewer | ①문면 «…우선한다» + 뒤 절은 근거 진술 · ③discipline-tdd-final s036-7.6 b1 «검증 방식 우선순위 — 출력 기반 > 상태 기반 > 통신 기반» 동일 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 22 | s004/b11 | Prohibition | Outside-In 이중 루프의 바깥·안쪽 테스트 자동 의무화 금지 | — | agent-discipline-reviewer | ①문면 «…자동 의무화하지 않는다» · ③discipline-tdd-final s040-9.1 b1 «이중 루프라는 이유만으로 양쪽 테스트가 자동 의무가 되지 않음» 동일 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 23 | s004/b11 | Obligation | Walking Skeleton 의 실제 얇은 E2E 행동 요건 | — | agent-discipline-reviewer | ①문면 «Walking Skeleton은 실제 얇은 E2E 행동이다» — 형태 요건 규정 · ②check-*.py 27종 docstring 선두 전수 실독 — E2E 골격 판정 술어 0 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 24 | s004/b12 | Obligation | AI 보조 TDD 의 테스트=명세 — 개발자가 테스트 작성·AI 구현은 통과 후 검증 | — | agent-discipline-reviewer | ①문면 «개발자가 테스트를 작성하고, AI 구현은 테스트를 통과한 후 검증한다» · ③discipline-tdd-final s066-17.1 b2 동축 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 25 | s005/b1 | Obligation | 주제별 references/final.md 해당 절 준수 | — | agent-discipline-reviewer | ①문면 «…해당 절을 따른다» — 상세 규범의 정본 위치 지정 · ②check-*.py 27종 docstring 선두 전수 실독 — 문서 라우팅 술어 0 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 26 | s005/b16 | Obligation | 필요한 항목만 부분 로드(전체 로드 불필요) | — | agent-discipline-reviewer | ①문면 «필요한 항목만 읽는다(전체 로드 불필요)» · ②check-*.py 27종 docstring 선두 전수 실독 — 로드 범위 술어 0 · ④§16 위임 기본값 표(discipline-tdd·implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |

## 3. 재진술 유예

센서스 restate 열 기준. 좌표는 **마커 제거본(센서스) 기준** — 상대 `discipline-tdd-final` 은 웨이브 2 기이관이라
현재 파일에 마커가 삽입돼 있으나 아래는 마커 없는 절 키·블록 서수다.

① 문서 내(= spec 수록, 유예 아님)
| 사본 블록 | 정본 블록 | 근거 |
|---|---|---|
| s001/b2 (frontmatter description) | s003/b1 · s003/b2 | description 의 2문장 = 로드 트리거(→ s003 b1) + «테스트 코드 작성법은 implementation-test 위임»(→ s003 b2). s003 b3(cleancode)·b4(django)·b5(migration 식별)는 description 에 없어 정본 지목에서 제외 |

② 교차 문서(유예)
| 사본 블록 | 상대 문서/절(센서스 좌표) | 대조 결과 |
|---|---|---|
| s003/b2 (§ 위임) | discipline-tdd-final / s038-8 b1 | 센서스가 지목한 위임 스텁. 축자 요약 |
| s003/b3 (테스트 코드 품질 → `discipline-cleancode`) | **상대 없음** | 초판이 적은 `s061-14` 는 실물이 «14. Property-Based Testing → `implementation-test` 참조»(final 1037–1040행)라 주제·위임 상대 둘 다 불일치 — 오기 정정. final 의 cleancode 위임 스텁은 `s060-13`(«13. 레거시 코드 다루기 → `discipline-cleancode`») 하나뿐이고 이는 **위임 상대만 같고 주제가 레거시 코드**라 재진술 쌍이 아니다. 테스트 냄새·품질 주제는 final 이 §12(s057-12·s058-12.1·s059-12.2) 본문으로 **직접 보유**하므로 위임 스텁 자체가 없다 |
| s003/b4 (Django TestClient·API 테스트 메커니즘 → `implementation-django`) | **상대 없음** | 초판이 적은 `s060-13` 은 실물이 «13. 레거시 코드 다루기 → `discipline-cleancode`»라 불일치 — 오기 정정. `discipline-tdd-final` 전문 검색 결과 **`implementation-django` 문자열 0건**이라 대응 위임 스텁이 존재하지 않는다 |
| s003/b5 | discipline-tdd-final / s025-5.5 b46 «기술적 식별 예시의 implementation-test §1.4 위임» | 축자 대응 |
| s004/b1 (§1.1–§1.2) | discipline-tdd-final / s001 b1 계열(§1 철학) | 가치 선언 요약 |
| s004/b2 (§2.1) | discipline-tdd-final / s006-2.1 b1 (3 Work) | 3 Work 를 1문장으로 압축 |
| s004/b3 (§3.1–§3.4) | discipline-tdd-final / s012-3.4 b7 | 축자 대응 |
| s004/b4 (§4.1–§4.4) | discipline-tdd-final / s015-4.2 b1 · s018-4.5 b6 | 요약 사본 |
| s004/b5 (§5.1–§5.3) | discipline-tdd-final / s021-5.1 b1 · s025-5.5 b2 · b17 | 규범 2 가 세 블록에 대응 |
| s004/b6 (§5.5) | discipline-tdd-final / s025-5.5 b1·b5~b7 · b34 · b17 | 규범 3 대응. **b17 은 pending 조항의 소유가 command-dddjango** — 사본 배선을 정본과 일치시켰다 |
| s004/b7 (§5.5) | discipline-tdd-final / s025-5.5 b46 · b37 | 규범 2 대응. b37 은 final 이 Permission, 스킬 사본은 «보존한다» Obligation — **강도 상향 표류** 기록 |
| s004/b8 (§6.1–§6.3) | discipline-tdd-final / s027-6.1 b1 · s028-6.2 · s029-6.3 | 요약 사본 |
| s004/b9 (§7.1–§7.2) | discipline-tdd-final / s031-7.1 b1·b2 · s032-7.2 b1 | 요약 사본 |
| s004/b10 (§7.6) | discipline-tdd-final / s036-7.6 b1 | 축자 대응 |
| s004/b11 (§9.1–§9.2) | discipline-tdd-final / s040-9.1 b1 · s041-9.2 b1 | 규범 2 대응 |
| s004/b12 (§17.1–§17.4) | discipline-tdd-final / s066-17.1 b2 · s069-17.4 b1 | 요약 사본 |

s005 는 센서스 restate=N — 확인 결과 유예 대상 0.

**발주서 비고와의 차이(사유 기록)**: 발주서 s003 행은 «위임 4건이 final 위임 스텁(§8·§13~§15·§18)과 중복»이라
적었으나, 브리프 «센서스 restate 열 참고·**직접 확인 후**» 의무에 따라 실물을 대조한 결과 final 스텁 5건의 주제는
§8 테스트 더블 분류(→`implementation-test`) · §13 레거시 코드(→`discipline-cleancode`) · §14 PBT(→`implementation-test`) ·
§15 Mutation Testing(→`implementation-test`) · §18 Python 테스트 생태계(→`implementation-test`) 이고,
스킬 s003 의 위임 4건 중 **주제까지 일치하는 것은 b2(→§8) 하나뿐**이다(b5 는 스텁이 아니라 s025-5.5 b46 본문과 대응).
발주서 비고는 «위임 상대가 겹친다»를 «스텁과 중복»으로 과대 서술한 것으로 판정하고 승계를 파기했다 —
초판이 b3·b4 에 채운 s061-14·s060-13 은 이 승계에서 나온 허위 쌍이라 삭제한다(소급 연결 패스 오염 차단).

## 4. 경계 판단 메모

- **frontmatter kind**: 웨이브 2 판례대로 행 단위 prose/norm(여는 `---` = 헤딩 라인). description 만 norm 2.
- **25행 셋째 문장의 소유 2인**: «pending은 G1을 막고 reuse·reject는 write가 0이다»는 한 문장에 두 조항이 압축돼 있고,
  정본(discipline-tdd-final s025-5.5 b17)에서 앞 조항은 `command-dddjango`(G1 게이트 승인 주체), 뒤 조항은
  `agent-discipline-reviewer` 로 배선돼 있다. 문장을 쪼개면 센서스 17을 넘기므로 **1 Work 에 두 소유자를 병기**했다.
  §16 «기본값 이탈은 문면 근거 필요» 조건은 정본 선례 + «G1» 문면 자체로 충족한다.
- **26행 둘째 문장 강도**: final 이 Permission(«…유효 회귀 테스트»)으로 둔 내용을 스킬이 «보존한다» 의무로 진술한다.
  사본을 원문대로 Obligation 으로 채번하고 표류 사실을 위 §3 에 기록했다(정본 개정은 소급 패스·T4 몫).
- **20행(목표·용기)**: 가치 선언이지만 센서스가 규범 1로 잡았고(P0 승계), 뒤 규범들의 «보수» 근거가 되므로 Obligation 유지.
- **절 선두·후행 공백**: s003/s004/s005 첫 블록이 헤딩 직후 빈 줄을 선두 귀속(§13 유일 예외), 각 절 마지막 블록이 후행 빈 줄 흡수.
- **표 블록**: 37~38행(머리행+구분행) 1블록 + 39~51행 1행 1블록(51행이 52행 빈 줄 흡수), 53행은 별도 norm 블록.
