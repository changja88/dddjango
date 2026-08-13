# broccoli-server 전면 리빌드 마스터 로드맵 (정본 · 2026-08-13)

최종 목표: **broccoli-server 16 BC 전부를 dddjango 표준 트리로 재구현**해 rebuild/standard-tree 를 완성하고 main 에 랜딩한다. 완성 판정 = migration_gate 잔존 0 · registry 귀속 0 · 빚 파일 전량 소멸 · make test green · A축(shape) 등가.

문서 관계: 이 문서=전체 조감(국면·BC 큐·결정 대기). 라운드 상세=`2026-08-12-bc-rebuild-protocol.md`(대장). 플러그인 업그레이드=`2026-08-13-upgrade-queue.md`. 속도=`2026-08-13-speed-plan-v0.md`. 갱신 규약: 라운드 종결·국면 전환 때마다 상태 열만 고쳐 쓴다(행 삭제 금지 — 이력 보존).

## §1 스케줄 (순차 단계 · 2026-08-13 사용자 확정 골격 — 1→2 순서 승인)

| 단계 | 내용 | 진입 조건 | 종료 판정 | 상태 |
|---|---|---|---|---|
| S1 | **라운드 3 종결·rubric 평가** — 양 레인(claude·codex) 완주/정지 접수 → ⑤ 3축 판정 + ⑥a v5 결과지 + ⑥b 사람 평가 + v2.5.0 관측 의무 | 양 레인 보고 | 결점 0 → 스트릭 1·S2 진입 / 결점 → 수정 사이클 후 재라운드(S1 재진입) | **진행 중**(3h+·레인 A 재작업 중) |
| S2 | **속도·최적화 사이클(speed v1)** — 라운드 3 수확이 입력: preflight 배선 스모크(재료 규율)·L8 병렬 coder 설계(슬라이스 겹침 실측)·L5 postgres 격리·L7 계측 기반 잔여. S1 에서 결점이 나오면 그 수정과 **한 릴리즈로 묶는다**(스트릭 리셋 1회 최소화 — 기승인 로직) | S1 평가 완료 | 검증 세트 green·릴리즈·설치본 갱신 | 대기(중간 실측 확보됨 — speed-plan §1.5) |
| S3 | **성숙기 스트릭** — 소형 BC 라운드 반복(child_settings 재도전 → products → entitlements …)·각 라운드 S1 동일 평가·S2 적용분은 속도 A/B 겸함 | S2 릴리즈 | **무수정 통과 연속 N**(기본 2·N=결정 대기 ①) | 대기 |
| S4 | **전 BC 일괄 설계** — 선행 결정 3(게이트 승인 주체·병렬/순차·운영 모드 규칙)+BC 순서 확정(accounts 시점=결정 대기 ②)+클린룸 의례 축소 규칙 | S3 스트릭 달성 | 설계 문서 사용자 승인 | 대기 |
| S5 | **일괄 리팩토링 실행** — §2 큐 잔여 소화(billing 재료 재사용·accounts 이관 시 빚 자동 소멸) | S4 승인 | 전 BC migration_gate 0·registry 귀속 0 | 대기 |
| S6 | **마무리·랜딩** — 중앙 api.py 오류 테이블 소멸·루트 common→framework·빚 파일 전량 소멸·delivery 거짓 성공 버그·main 병합(전략=결정 대기 ⑤) | S5 완료 | main 랜딩·전수 재실측 | 대기 |

병행 허용: **L5(하네스 갈래)는 스트릭 무관** — S1 평가 중에도 선행 투입 가능. L1 G0 인터뷰·L3 사전 lint·#4 재료 규율 ⓒⓓ 는 S2 또는 S3 사이 수정 사이클에 동승(upgrade-queue 표 참조).

## §2 BC 리빌드 큐 (16 BC — 순서는 제안·P2 에서 확정)

실측(2026-08-13 · main repo V1): 비-test LOC=`find -name '*.py' -not -path '*test*'`·인바운드=생산 코드의 `application.<bc>` 소비 BC(배선 3파일 제외)·HTTP=urls/api 배선 유무. migration_gate 잔존 합 72건(V1 전체·BC당 4~5 폴더).

| # | BC | 비-test LOC | 인바운드(생산) | HTTP | 상태 | 비고 |
|---|---|---|---|---|---|---|
| 1 | child_settings | 705 | 0 | ✓ | 라운드 1·1′ 불통과(미랜딩) | 재도전 후보 — 최소형·인바운드 0 |
| 2 | billing | 2,215 | 1(ai_chat) | ✓ | 라운드 2·2′ STOP(미랜딩) | 재료 재사용 가능 — spec 개정 2건(grant already-entitled·int64)·빚 3행 권고안 확정돼 있음 |
| 3 | **parent_settings** | 793 | 1(notifications) | ✓ | **라운드 3 진행 중** | OHS 동결 장치 첫 실전(인바운드 중화) |
| 4 | products | 1,867 | 1(billing) | ✓ | 대기 | 소형 — 성숙기 후보 |
| 5 | entitlements | 1,497 | 2(billing·usage_quota) | ✓ | 대기 | 소형 — 성숙기 후보 |
| 6 | managed_copy | 3,266 | 0 | ✓ | 대기 | |
| 7 | delivery | 3,848 | 3(accounts·lessons·notifications) | ✗ | 대기 | 거짓 성공 버그 존치(P4 에서 확인) |
| 8 | notifications | 4,112 | 4(entitlements·lessons·pairing·usage_quota) | ✓ | 대기 | parent_settings 소비자 — 라운드 3 shim 원복 포함 |
| 9 | llm_meta | 5,082 | 2(ai_chat·usage_quota) | ✗ | 대기 | |
| 10 | usage_quota | 5,344 | 1(ai_chat) | ✓ | 대기 | |
| 11 | parental_controls | 5,296 | 1(lessons) | ✓ | 대기 | |
| 12 | pairing | 5,111 | 7 | ✓ | 대기 | 인바운드 최다급 — OHS 장치 대규모 |
| 13 | accounts | 6,487 | **14(전원)** | ✓ | 대기 | **인증 표면·빚 #12/#385/#389 근원 — 이관 시 이후 라운드 빚 목록 자동 소멸. 시점=결정 대기 ②** |
| 14 | lessons | 9,416 | 1(report) | ✓ | 대기 | 대형 |
| 15 | ai_chat | 11,494 | 0 | ✓ | 대기 | 대형·아웃바운드 최다(소비 5 BC) |
| 16 | report | 13,136 | 0 | ✗ | 대기 | 최대형 |

정렬 원리(초안): 성숙기=소형·저인바운드(#1~5 권역) → P2 설계 후 일괄기=중형→대형. accounts 는 «빚 소멸 효과 vs 대형·전원 소비» 트레이드오프라 P2 순서 결정의 핵심 논점.

## §3 결정 대기 (사용자 몫)

| # | 결정 | 맥락 |
|---|---|---|
| ① | 성숙 종료 판정 — 무수정 통과 스트릭 몇 라운드에 P2 진입? | 현재 스트릭 0(라운드 3 결과 대기) |
| ② | accounts 이관 시점 — 당기면 빚 자동 소멸·이후 라운드 청결 / 대형·인바운드 14 리스크 | OHS 동결 장치(라운드 3)가 실증되면 확장 근거 |
| ③ | 업무 낱말 2건 귀속 — child_report_topic→lessons 테스트 재료·notification_navigation→notifications VO | 3번 선행 이관 때 표기(08-12) |
| ④ | S4 선행 결정 3 — **게이트 승인 주체(=조정자 대리 답변 위임장: 위임 가능/에스컬레이션 분류·codex 36s 자동해소=권고안 채택기 실증·claude 는 SendMessage 주입 실측 필요)**·병렬/순차·운영 모드 규칙 | after-round-2-queue ⑵ · 08-13 라운드 3 에서 대리 답변 3건 실증(#210 기각·#51 승인·usage_quota 스코프) |
| ⑤ | 최종 랜딩 전략 — rebuild/standard-tree→main 병합 방식·시점 | P4 |
| ⑥ | dddjango 대장 미커밋(라운드 3 두 행+2′ 종결) — 커밋 지시 대기 | 이 로드맵 파일도 동반 |
