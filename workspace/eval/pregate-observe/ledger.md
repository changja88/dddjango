# pre-gate 관찰 모드 실측 대장 (v2.17.14~)

- 지위: 속도 리비전 ⑦ 관찰 모드의 실측 원장. 승격 판정(⑦′)의 근거 자료.
- 판정 규칙(설계 v3 §8): 실전 레인 ≥2(신규 BC ≥1)에서 ⑴ 오탐 0 이원 판정(`ignored` red→G2 실측 전건 실위반 / `corrected` red→재실행 green+명세 diff 귀속; 필터 건 별도 계수) ⑵ 커버 표면 미탐 0(G2 귀속 red ∩ P/S/I 표면 기계 대조) ⑶ 형식 반송 ≤1회/레인 + pre-gate 총 소요 보고.
- 1차 자료 경로: 각 소비 워크트리 `.dddjango/<런 폴더>/{pregate-report.md, g2-registry-evidence.md}` + `docs/superpowers/orders/lane/STOP-*·REPORT-*`.

## 총괄 표

| # | 레인 | 유형 | 런타임 | 실행 | 형식 red | 귀속 예보(최종) | corrected | ignored | filtered | G2 귀속 | 오탐 | 미탐 | ⑶ 형식 ≤1 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | spring_dream_server media-library (09-02) | 신규 BC | Claude Opus 4.8 | 4회 | **2** | 15건 | 6축(진탐) | 0 | 15건(전건 적중) | **0** | **0** | **0** | **✗ (2회)** |

표본 상태: 레인 1/2 (신규 BC 1/1 ✓) — 승격 판정은 레인 ≥2 충족 후.

## 레인 1 — spring_dream_server media-library (2026-09-02) 상세

- 런 폴더: `~/.herdr/worktrees/spring_dream_server/feat-media-library/.dddjango/20260902-0128-media-library/`
- 타임라인(KST): 레인 개시 01:28 → G0 01:45 → pre-gate 실행 4회 02:02·02:23·02:28·02:42 → G1 02:52 → G2 승인·REPORT ~05:40. **레인 총 ≈4시간 10분**(베이스라인 Claude dddjango 평균 활성 399분 대비 짧은 완주).
- 결과: G2 완주(96 passed·`registry_gate --anchor c489ac0` 귀속 0·make test 전체 green). **③형 STOP 0** — G1 이후 «결정적 사전 검출 가능 설계 결함» 반송이 없었다(베이스라인: ③형 발생 레인 평균 ≈56분 손실).

### ⑴ 오탐 이원 판정 — 0

- `corrected` 6축(형식 1 + 귀속 5): `spec`→`specification` 개명(#28×2) · OHS get_asset stem(#483/#484) · result aux 언더스코어 복원(#571) · 비-DB 테스트 unit/ 이동(#389×2) · repo 도메인 import(#477) · symbols 언더스코어+필드 문법. **전건이 다음 실행에서 소멸**(실행 3 귀속 22 → 실행 4 귀속 15의 차분과 처분 기록 정합) = «재실행 green + 명세 diff 귀속» 충족 → **정정 유발 진탐**.
- `ignored`: 0건.
- 필터 건(별도 계수): **15건** — 스텁/문법 한계 4계열(port/repo ABC `@abstractmethod` 표기 부재 #212×5·#283×3 / apps·model Meta 값 미탑재 #329·#332·#630 / factory_boy 형태 #392 / OHS 어노테이션-참조 aux 예외 미모델 #160·#484). **G2 registry 귀속 0으로 «real checker 통과» 예측 15/15 적중** — filtered 처분 정확성 실증. 계통성 여부: 4계열 모두 «스텁 형태 기인·유형 전 인스턴스 발화»에 가까워 §6-2선(계통적 오탐=설계 반송 사유)의 검토 대상이나, 관찰 모드 처분 채널(filtered)로 흡수됐고 레인 피해 0 — **스텁 문법 확장 후보로 이관**(아래 개선 후보 ①).

### ⑵ 커버 표면 미탐 — 0

- G2 귀속 red = 0건(전 슬라이스 S1·S2·S3 포함) → 교집합 공집합. `g2-registry-evidence.md` §1.
- 표면 밖 발견 1건(미탐 아님·사각 기록): G2 직전 반송 BLOCKER «postgresql 마커 누락 8 DB 테스트» — pytest 마커는 registry 검사기 27종 표면에 규칙이 없고(check-test-config 실독 — 마커 규칙 부재) make test 러너 실측으로만 드러남. 물리 신호 채널 `[markers:…]`는 명세에 있으나 이를 판정하는 검사기가 없어 원리적 예보 불가. → **별도 후보: 마커 정합 검사기**(pre-gate 결함 아님).

### ⑶ 형식 반송 — 2회 (기준 ≤1 초과)

- 실행 1(02:02)·실행 2(02:23) **동일 오류 반복**: symbols 행 «함수에 필드 목록을 쓸 수 없다»(list_group_media_assets_result.py). architect가 1차 형식 red 후에도 같은 결함을 재제출 — 21분 소요 후 실행 3에서 해소.
- 보수 계상으로 반송 2회. 해석 병기: 동일 원인 1결함의 재시도 실패로 볼 여지도 있으나, 문법 성문(architect s005/b33~b38)은 v2.17.14에 배포된 상태였으므로 규범 전달력 문제로 기록. 승격 게이트에서 이 레인은 ⑶ 미충족 레인으로 계상.

### pre-gate 총 소요

- 실행 구간 02:02~02:42(40분·리뷰 다발과 병렬 — 순증 시간은 그 이하). 런당 실행 시간 ≈1분 대역(백테스트 실측 준용). 형식 red 왕복 2회가 구간의 주 성분.

### 관측 공백(개선 후보 ②의 근거)

- G2 직전 반송으로 `design-spec.md`가 05:00에 개정됐으나(§14.3 정정·언어 §5 정규화·픽스처 타입) `pregate-report.md`는 02:44 이후 무기록. Coordinator 규범(반송 개정 시 재승인 전 재실행)과의 정합은 **판정 불가** — Coordinator 캐시 조항(«기계 블록 해시 불변이면 skip»)에 따른 정당한 호출 생략일 개연성이 높으나(개정 내용이 산문 절 위주), 실행기에는 캐시가 없고 skip 흔적도 리포트에 남지 않아 준수 여부가 관측되지 않는다.

### 개선 후보 (이 레인 발화분 — 별도 배치)

1. **스텁 문법 확장 4계열**: symbols에 `@abstractmethod`/ABC 선언 표기·apps/model 정형 값(Meta.db_table·label·name) 반영·factory_boy DjangoModelFactory 형태·OHS 어노테이션-참조 aux 예외 모델링 — 최종 라운드 잡음(15/15 filtered)을 줄여 filtered 대조 노동(선례 검색) 절감.
2. **캐시 skip 관측성**: Coordinator가 블록 해시 불변으로 호출을 생략할 때도 pregate-report에 1행(«블록 해시 불변 — 재실행 생략») 기록 — 재실행 규범 준수를 관측 가능하게.
3. **(pre-gate 밖) pytest 마커 정합 검사기**: physical-signals `[markers:…]` ↔ 테스트 파일 `pytestmark` 대조 — G2 직전 반송 1회분의 표면 편입 후보.
