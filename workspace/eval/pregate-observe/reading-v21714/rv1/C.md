# 수리 배치 3 · 1단계 적대 리뷰 C — ⓪ 증거 재산출·효과 추정 검증

- 검토자: C(독립 재산출 + 효과 추정 반증 + 표본 외 대조). 저장소 무수정 — 읽기·스크래치 실행만.
- 재산출 방법: 파서(`parse_report.py`)를 쓰지 않고 grep/awk/자체 python으로 `pregate-report.md` 44절을 직접 집계. 명세 히스토리는 `git show <sha>:<path>` file-plan 펜스를 직접 셈. 수리판 소급 재실행은 스크래치 clone(`scratchpad/b3/sds`, HEAD 5c4a07d, clean)에서 `design_pregate.py`(플러그인 매니페스트 2.17.16)로 4회 재실행(⓪의 A·B 2회 + 추가 C·D 2회).
- 시각 표기: 리포트 헤더는 UTC(Z), 커밋·STOP은 KST(+9). 아래는 병기하거나 KST로 통일.

## 1. 주장별 대조표

| # | 주장(⓪) | 재산출 값 | 판정 | 근거 |
|---|---|---|---|---|
| 1 | 44회 = 예보 red 29 · green 4 · 형식 red 6 · skip 5(구형 1+공허 4) · 안정 ID 22 · 규칙 13 | `## pre-gate 예보 — ` 44절. `- 판정:` 행 44개(절당 1). skip = run 1(«machine 블록 부재») + run 41~44(«실체화 0건 공허 차분») = 5. 형식 red = run 18·21·30·34·39·40 = 6. green = run 32·33·37·38 = 4. red = 29. 고유 ID 22개(`^- \`[0-9a-f]{12}\` check-` 유일 22) · 규칙 13종(#28 #107 #121 #188 #193 #219 #389 #488 #490 #569 #570 #576 #635) | **일치** | 리포트 L2~L3149 헤더 grep; 부기: 44는 «리포트 절 수»이지 실행기 호출 수가 아니다 — L1266 «machine file-plan hash 불변이라 예보 cache가 적중해 새 report block 0» 사례가 최소 1회 있어 호출 수 ≥45 |
| 2 | 형식 red 6/6 = 기실현 add 충돌 | 6절의 사유행 전부 `- add 충돌(실존): …` (L1073·1256·1986·2277·2839·2847). 경로: service_runtime.py · test_active_bundle_matrix.py · test_evidence_openapi.py · api/evidence_provisioning/__init__.py · validate_citations/__init__.py · validate_citations_use_case.py | **일치** | 다른 형식 오류(symbols 문법 등) 0 |
| 3 | 말기 skip 4회 = add 0 · 초기 e6fb491 add 42/update 30 · 최종 19b27df add 0/update 73/remove 19 | e6fb491(09-02 10:26 KST) add 42 · update 30 · remove 6 · empty 3 / 19b27df(09-03 05:41) add 0 · update 73 · remove 19 · empty 3. run 41~44 사유 «실체화 0건» | 수치 **일치** / 해석 **정정 필요(§2-c)** | 궤적: 42→34(590a5de 14:03)→33→31(e606eb9 00:07)→**7**(78e616a 01:21)→**0**(f256458 03:47). 31→7의 24경로는 run 37 처분 L2555 «실존하는 machine `add` 24경로만 `update`로 교정» — 기실현 add 충돌을 피하려는 **수동 재라벨**이다. 최종 update 73 중 ≥31행이 원래 add 행 |
| 4a | `92767435ca49` #107 — 도구 한계 정당 filtered · **20회 재기재** | 예보 항목 발화 **20 run**(run 2~17·19·20·22·23). 명시 처분은 **8회**(표 행 7: L77·658·732·806·1153·1242·1361 + 산문 «stable filtered» 1: L942) + «미발행(dirty-overlay)» 메모 5회(L1455·1545·1635·1806·1897). 리포트 내 ID 언급 총 36행 | **정정**: 20 = 예보 발화 횟수. 처분 재기재는 8회(메모 포함 13회) | 표 행 길이 166~260자 · 행 1↔2, 3↔4 byte 동일(복사). 처분 표는 시간순 append가 아니라 Coordinator가 절 안에 삽입(run 2 절 L72에 «귀속 2건» 최종본이 들어 있음 — run 2 raw는 11건) |
| 4b | `57a4705e1218` #188 — filtered 26회 → P4 149 귀속 실발화 → 권고 수리 = 예보 함의 → run 30 소멸 | 발화 **26 run**(run 2~17·19·20·22~29). 명시 처분 13회(표 12 + 산문 1). 마지막 발화 run 29(09-02 11:30Z=20:30 KST). STOP-149 생성 87fef40 **21:50:59 KST**(L76·L165·L179 #188 인용 확인) → run 30(22:36 KST)은 형식 red라 항목 없음 → run 31(23:26 KST)이 첫 부재 raw. 최종 코드: `application_layer/citation_validation`·`driving_layer/api/citation_validation` 모두 부재(OHS 폴더만 잔존), 585c9c6(09-03 02:32) | **일치**(«run 30 소멸»은 «run 29 마지막·run 31 첫 부재»가 정밀) | **추가 발견**: e6fb491 file-plan에 이미 `driving_layer/api/evidence_provisioning/*` add 5행 + `application_layer/citation_validation/*` add 6행 → #188은 G1 시점부터 유효한 진탐. STOP-149 L165 «P4가 concrete api surface를 만들면서 1:1 규칙이 활성화»는 사실과 다름(활성화는 명세 단계). 선행 STOP 4건(p2-registry-contract·p3-registry-gate·d54 2건)에 #188 언급 0 → 오처분이 P4까지 무검토 통과. N-1 강화 |
| 5 | R-5 스텁 계열 reading 0 · 레인 1: #392 1 ID·#160/#484 2 ID · 레인 2·3: 0 | reading: #392 0·#160 0·#484 0·abc.ABC 0(«ABC» 1행은 L79 처분 근거 산문). 레인 1(4 run·17 ID): #392 `508cb023eceb` 1 · #160 `0545691c4eac` 1 · #484 `cc49ccf434d0` 1 = 2 ID. 레인 2(4 run·25 ID): 0. 레인 3(5 run·7 ID): 0 | **일치** | 카탈로그(v2.17.16·1 run) #392 `869e0acd832f` 1 ID — 성격은 §4 |
| 6 | 수리판 소급 A = 예보 2건 동일 ID·결손 0 / B = skip·결손 0·판정 불능 0 | 독립 재실행 A(e6fb491·`--base d892894`): exit 2 · 67 s · #107·#188 2건 · 실존 행 11·결손 0·판정 불능 0. B(19b27df·`--base 80431d9`): exit 4 · 8 s · skip · 행 17·결손 0·판정 불능 0. ⓪ 파일과 헤더(ts·`--base` 표기) 외 **byte 동일** | **일치(재현)** | `rv1/rerunA-C.md`·`rerunB-C.md` vs `reading-v21714/rerun-*.md` diff |
| 7 | kkebi-server 명세 1/1 구형(기계 블록 0) → 구조적 불충족 | **`~/Desktop/kkebi-server/.dddjango/` 실물 = 런 폴더 20개**(08-23~08-26) · design-spec.md 20/20 기계 블록 0 · pregate-report.md 0/20. 별도 `.dddjango-web/` 10개(자매 플러그인·pre-gate 밖). `~/kkebi-mirror`(refs 동결 08-24 01:52)는 1개만 보유 → ⓪가 미러만 읽음. `~/.herdr/worktrees/kkebi-server/` 비어 있음(확인) | **정정: 1/1 → 20/20**(결론 동일·더 강함) | 기계 블록 규범 최초 커밋 cdca837 09-01 17:58 · v2.17.14 태그 09-01 18:38 → kkebi 20런 전부 규범 이전. 메모리 `kkebi-read-access.md`의 «Desktop TCC 차단»은 현재 불성립(직접 ls 성공) |
| 8 | 카탈로그 #392 `relation_graph_factory.py` = 진탐(turtle 빌더·factory_boy 아님) | 카탈로그 spec L54 «`factories/`(합성 관계표 turtle 빌더)» · L385 add 행 · factory_boy/DjangoModelFactory 언급 0 · 리포트 1 run(09-03 03:59Z·v2.17.16·블록 해시 d759829e35d6) #392 1건 | **일치** | 레인 1 #392는 반대로 스텁 아티팩트: spec L375 `MediaAssetModelFactory(테스트 재료)` 계획 · HEAD 실코드 `class MediaAssetModelFactory(DjangoModelFactory)`(L13) — factory_boy 형태를 스텁이 못 그려 발화 |

## 2. 효과 추정 반증

### (a) #107 20회 «재처분» 실노동 (분)

| 항목 | 값 |
|---|---|
| 발화 창 | run 2(09-02 08:43 KST) → run 23(17:02 KST) = **8h18m** · 이후 run 24~29는 WIP api_router 실물화로 미발화(메모 5회) |
| 명시 처분 건수 | **8**(표 7 + 산문 1) — 20이 아님 |
| 처분 행 길이 | 표 166·166·169·169·223·231·260자 · 산문 322자. 행 1↔2·3↔4 byte 동일 = 복사 |
| 하한 | 복사 0.5분×8 + 메모 0.3분×5 ≈ **6분** |
| 상한 | 재작성+ID 재확인 4분×8 + 메모 1.5분×5 ≈ **40분** |
| 판정 | «20회 재기재»는 예보 발화 수를 처분 수로 오독. R-5d의 «재처분 노동» 논거는 30h 레인에서 **6~40분** 규모 |

### (b) #188 오처분 실비용과 G1 시점 절감분 (분)

| 항목 | 값 |
|---|---|
| P4-149 STOP | 생성 87fef40 09-02 21:50:59 KST → 결정 A d24bff8 21:59:29 → G1′ 처분 L2256 09-03 00:03:46 → e606eb9 00:07:54 = **G1′ 133분** → 코드 착지 585c9c6 02:32:40 |
| #188 몫 | 149건 중 1건 / G1′ 6축 중 1축(STOP L102~107) / 지침 8항 중 1항(L179) / 명세 diff 9425653→e606eb9 387행 중 citation_validation·validate_citations 언급 **42행(10.9%)** |
| 실비용 상한 | 명세 몫 0.109×133 ≈ 15분 + 코드 접기(5파일 이동·OHS service·composition_root·테스트 import 재지향, WIP 상태) 10~30분 = **25~45분** |
| 실비용 하한 | 명세 몫 1/8×(133×소요 비례)≈8분 + 경로 이동 최소 10분 = **≈18분** |
| G1에서 따랐을 때 | run 2~4(09-02 08:43~08:53 KST) 시점 P4 코드 부재(P4 첫 STOP 15:13 KST) → file-plan 6행 경로 개명 + 산문 ≈ **3~8분** |
| 절감분 | **10~40분**. ledger ③형 기준선 ≈56분/레인 대비 0.2~0.7 ③형 — «③형 재발» 라벨은 성격상 옳고 크기는 STOP-149의 소분율 |

### (c) «add→update 전환 → 표면 0 수렴»은 reading 특수성인가

| 레인 | 유형 | 최종 file-plan | 수렴 |
|---|---|---|---|
| reading(R) | 신규 BC + 브라운필드 rag 이관 · P1~P4/L1~L3 단계 착지 · 명세 커밋 32회 | add 0 · update 73 · remove 19 · empty 3 | **수렴**(42→0, 09-03 00:07~03:47 사이 31→0) |
| 레인 1 media-library | 신규 BC | add **69** · update 2 · empty 17 | 없음 |
| 레인 2 notification | 신규 BC | add **34** · update 7 · remove 12 · empty 53 | 없음 |
| 레인 3 email-template | 기존 BC 확장 | add **20** · update 5 · remove 10 | 없음(G1′ 델타만 update-only — 다른 기전) |
| 카탈로그 | 신규 BC(v2.17.16) | add **44** · update 1 · empty 55 | 없음 |

- 결론: 수렴은 **reading 고유**다. 기전은 브라운필드 이관(초기 update 30·remove 19를 설명)이 아니라 **기실현 add 충돌을 피하려는 Coordinator의 add→update 수동 재라벨**(run 37 L2555 «24경로 update로 교정», 이후 7→0) — v2.17.14에 `--base` 재발화 판형이 없어서 생긴 우회. 배치 2 Part 1 ⑥이 정확히 이 우회를 없애는 수리다.
- **추가 실측(add 행 보존 시 수리판 표면)**: C = spec e606eb9(add 31)·`--base d64890f`(P4 착지 전) → **예보 red 1건(#107) · 실존 결손 2건** · exit 2 / D = spec 78e616a(add 7)·`--base 61b56ef` → **예보 green 0 · 실존 결손 2건** · exit 5. 결손 2건 = `prepare_fortune_evidence_use_case/prepare_fortune_evidence_failure` 승격 패키지(update 행 → 렌더러 미실체화 → ⑴ 모듈 부재) — **R-5d 계열 그 자체**가 v2.17.16 실존 채널에 이미 관측된다(권고·비차단). 즉 «update-only 침묵»은 예보 채널에 한정된 서술이고, 실존 채널은 침묵하지 않는다.
- 따라서 R-5d 후보의 «2레인·구조적 충족» 논거는 재구성이 필요하다: reading 예보 표면 0은 반은 자초(재라벨), 실존 채널은 이미 발화. R-5d의 실체는 «update 대상 symbols가 예보 채널(#107류)에 미반영 + 승격 패키지 update가 실존 채널에서 결손으로만 보임»이다.

## 3. 표본 외 결과

- kkebi-server 실물(`~/Desktop/kkebi-server`, HEAD 6608fb0 08-26 23:21): dddjango 런 20개 전부 구형(기계 블록 0·pregate-report 0) — 최신 런 08-26·규범 최초 커밋 09-01 17:58. `.dddjango-web/` 10런은 자매 플러그인(pre-gate 없음). 결론 «pre-gate 고유 계열 대조 구조적 불충족»은 유지·강화되나 ⓪ 기록 «1/1»은 미러(동결 08-24) 한정 관찰 — 정정해야 한다.
- «수리의 오차단 0 대조» 표본이 1→20으로 늘어난다(장점). 단 kkebi 명세는 machine 블록이 없어 실행기가 즉시 skip하므로 오차단 대조로도 «skip 사유 문면» 이상을 검증하지 못한다 — 대조 가치는 제한적.
- `~/.herdr/worktrees/kkebi-server/` 비어 있음 확인. `~/Desktop/kkebi`는 앱 저장소(.dddjango 없음).
- 메모리 `kkebi-read-access.md`(«Desktop TCC 차단 우회») 갱신 필요 — 현재 직접 읽기 가능.

## 4. ⓪ 필터(≥2 레인) 타당성 — R-5a #392

- ⓪ 표는 #392를 «레인 1 = 1 ID · 미달(1레인)»으로 계수했고 카탈로그를 세지 않았다 → **타당**.
- 카탈로그를 2레인째로 세는 것은 **오류**다: 레인 1 #392는 스텁 형태 결함(factory_boy 팩토리를 계획했으나 스텁이 DjangoModelFactory 베이스를 못 그려 발화 — 실코드 G2 통과), 카탈로그 #392는 설계 위반(turtle 빌더를 `factories/`에 배치 — 스텁 문법을 아무리 확장해도 계속 발화해야 옳다). 같은 규칙 번호일 뿐 계열(«스텁 문법 한계»)이 다르다. 카탈로그 건은 오히려 «수리 후에도 진탐이 남아야 함»의 무손실 대조 픽스처로 쓸 수 있다.
- 부기: 필터의 «계열» 정의를 «규칙 번호»가 아니라 «오탐 기전»으로 명문화하지 않으면 다음 배치에서 같은 혼동이 재발할 수 있다(MINOR).

## 5. 심각도

| 등급 | 항목 |
|---|---|
| BLOCKER | 없음 |
| MAJOR | **주장 3 해석 / R-5d 근거**: reading «add 0 → 구조적 침묵»은 24+7경로 수동 재라벨의 결과이고(run 37 L2555), add 보존 재실행 C/D는 표면 ≠ 0(예보 1·결손 2). R-5d는 살아남되 근거를 «실존 채널 결손 2건(승격 패키지 update) + 예보 채널 #107 미반영»으로 다시 써야 한다 — 효과 과대 추정 |
| MINOR | 주장 4a «20회 재기재» → 처분 8회(메모 포함 13회) · 노동 6~40분 |
| MINOR | 주장 7 «kkebi 1/1» → 실물 20/20(미러만 읽음) · 메모리 TCC 메모 stale |
| MINOR | 주장 4b «run 30 소멸» → run 29 마지막·run 31 첫 부재(run 30은 형식 red) |
| MINOR | 주장 1 부기: 44 = 리포트 절 수, 캐시 적중 무기록 호출 ≥1(L1266) |
| MINOR | §4 부기: 필터 «계열» 정의를 오탐 기전 기준으로 명문화 |
| 검증됨 | 주장 1·2·3(수치)·4b·5·6·8 · ⓪ 필터 계수(#392 1레인) · 소급 재실행 A/B byte 재현 |
| 강화 | N-1: #188은 e6fb491 file-plan 기준 G1 시점부터 진탐(api/evidence_provisioning add 5행 실재) · STOP-149 L165의 «P4가 활성화» 서술은 오류 · 선행 STOP 4건 #188 언급 0 |

## 6. 10줄 요약

1. 44회 분포(red 29·green 4·형식 6·skip 5)·안정 ID 22·규칙 13은 grep/awk 독립 재산출로 **전건 일치**; 파서 신뢰 가능.
2. 형식 red 6/6 «add 충돌(실존)» 일치; 명세 e6fb491(add 42/update 30)·19b27df(add 0/update 73/remove 19) 수치 일치.
3. **정정** #107 «20회 재기재» → 예보 발화 20 run, 명시 처분 8회(+메모 5) — 실노동 **6~40분**(행 166~322자·복사 동일 행 2쌍).
4. #188: 발화 26 run·처분 13회·STOP-149 L76/L165/L179 확인·최종 코드 부재 확인; **G1 시점부터 진탐**(e6fb491에 api/evidence_provisioning add 5행) → N-1 강화, STOP의 «P4가 활성화» 서술은 오류.
5. #188 실비용 **18~45분**(149건 중 1·G1′ 133분의 ≈11%·코드 접기), G1 추종 시 3~8분 → 절감 **10~40분** = ③형 기준선 56분의 0.2~0.7.
6. **MAJOR** «add 0 수렴 = 구조적»은 reading 고유: 레인 1·2·3·카탈로그 최종 add 69/34/20/44. reading의 42→0은 run 37 «add 24경로 update 교정»(기실현 충돌 회피 재라벨)이 기전 — 브라운필드 이관 탓 아님.
7. add 보존 소급 C(e606eb9·base d64890f) = 예보 1(#107)+**실존 결손 2** / D(78e616a·base 61b56ef) = 예보 0+**결손 2**; 결손 = 승격 패키지 update 미실체화 = R-5d 계열이 v2.17.16 실존 채널에 이미 발화 — R-5d 근거를 이것으로 재작성해야 한다.
8. 소급 A/B 독립 재실행 결과 ⓪ 파일과 **byte 동일**(A exit 2·67 s / B exit 4·8 s); R-5 스텁 계열 reading 0·레인 1 #392 1·#160/#484 2·레인 2·3 0 일치.
9. **정정** kkebi «1/1 구형» → 실물 `~/Desktop/kkebi-server/.dddjango` **20/20 구형**(pregate-report 0·규범 09-01 이전), ⓪는 동결 미러(1런)만 읽음; 결론(구조적 불충족)은 유지·강화, TCC 메모리 stale.
10. ⓪ 필터 #392 1레인 계수는 타당 — 카탈로그 #392(turtle 빌더)는 진탐, 레인 1(factory_boy 스텁)은 아티팩트로 기전이 달라 2레인 합산은 오류; 필터 «계열»을 규칙 번호가 아닌 오탐 기전으로 정의할 것.

---
Serena: skipped — 읽기 전용 증거 재산출·스크래치 실행이라 기본 도구로 충분.
