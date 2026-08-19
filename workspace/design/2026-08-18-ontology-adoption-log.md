# 온톨로지 적용 진행 로그

> **역할**: 적용 조감도 아티팩트(상황판)의 상세판. 조감도에는 사용자 확인 사항·진행도만 남기고, 세부 기록·작업 큐·문서 색인은 이 파일에 쌓는다. Claude가 관리하며 **동결 대상이 아니다**.
>
> **정본 위계** (이중 정본 금지):
> - 규범·결정·절차의 정본 = 블루프린트(현재 v3 재설계 중). 이 로그는 블루프린트 내용을 재진술하지 않고 참조만 한다.
> - 이 로그 = 운영 기록(무엇을 언제 했고, 다음에 무엇을 하는지).
> - 조감도 아티팩트 = 상황판(사용자 확인 사항 + 진행도만). URL: https://claude.ai/code/artifact/34737b9c-4919-4378-9a99-ba90de4e22f3 (2026-08-18 재발행 — 구 아티팩트 소실로 URL 교체. 원본: `workspace/design/ontology-adoption-map.html`)

## 현재 상태 (2026-08-18)

- **블루프린트 v3.2 동결 — 사용자 심의(⑤) 통과.** 준비 사이클 완주: 보강 조사 Q1~Q7(출처 310) → v3 → 적대 리뷰 69건 전건 반영(v3.1) → 검증 패스 2종 반영(v3.2) → **동결 선언(2026-08-18)** → 문서 세트 커밋(8b212d9).
- **T0 세부 실행 계획 작성 완료(2026-08-18)** — `2026-08-18-ontology-t0-plan.md`. **사용자 검토 대기**: 재량 결정 D1~D4(release [2/7] 치환·pre-commit 범위·B트랙 대표 검사기 2종·파이썬 환경) + 검수 절차(동결 기준 4항+계획 추가 2항). 승인 시 작업 묶음 ①(A1~A4 기반·어휘)부터 착수.

## 방향 전환 기록 (2026-08-18 — 사용자 조향)

- **목표 재정의**: 이번 플러그인 업그레이드의 목표는 **온톨로지 최대 적용 실험**. 1차 목표는 **파이프라인 산출물 품질(규칙 준수율) 향상**, 토큰 절약·속도 향상은 부수 효과(사용자 원문 취지 그대로).
- **스택 확정(잠정)**: **표준 스택 전면** — 규칙 정본을 Turtle/RDF로 저작, 스키마·제약 SHACL, 질의 SPARQL, 필요 시 RDFS/OWL 추론. 사용자 «퀄리티 관점에서만 본다면 2번(표준 전면)» + Claude 동의(투영 층 제거·검증기 표준화·저작 마찰은 에이전트 부담).
- **v2.2 폐기 사유**: v2.2는 «규칙 관리(표류 방지·정합성)» 최적화 설계로, 품질·성능을 바꾸는 런타임 층(그라운딩·재생성 루프·렌더)을 S5 맨 끝에 배치 — 재정의된 목표와 우선순위가 정반대.
- **v2에서 이월되는 자산**: P0 센서스 실측(스택 무관), 조사 R1~R7(거버넌스 축 증거), ID·개정 규율 개념, 미러 lint 개념(전환기 가드로), 적대 리뷰→검증→동결 절차 관례.
- **표준 스택이 커밋하는 것 2가지**(v3 동결 전 검증 대상): ① 산문 정본→그래프 정본 전환이 설계의 중심 문제(산문은 장기적으로 렌더 투영물) ② Turtle diff 가독성을 위한 안정 직렬화·문법 lint 선행 구축.
- **v3 지표**: 1차 = 산출물 품질(리뷰까지 새는 위반 수·재작업 왕복 감소·기계 판정 비율), 부수 = 토큰·속도.

## 게이트 로그 (상세)

| 날짜 | 게이트 | 결정 | 근거·산출물 |
|---|---|---|---|
| 2026-08-18 | 학습 충분 판정 | 통과 — 핵심 주제 1·2·3·4·7 (Claude 판정·사용자 수용) | 학습 지도 아티팩트 |
| 2026-08-18 | 준비 절차 승인 | ①현황 실측(P0)→②외부 조사→③블루프린트 v2→④적대 리뷰→⑤심의·동결 5단계 (사용자 «좋아 진행해줘») | — |
| 2026-08-18 | ① P0 센서스 검토 | **통과** (사용자) | `-p0-census.md` + 상세 14편 |
| 2026-08-18 | ② 외부 조사 | 7레인 완료, 출처 182 | `-research.md` + R1~R7 |
| 2026-08-18 | ③ 블루프린트 v2 | 센서스+조사 근거로 작성 | `-blueprint-v2.md` |
| 2026-08-18 | ④ 적대 리뷰 | 6렌즈 54건 전건 중재 반영 → 검증 2회 → v2.2 동결 후보 | `-adversarial/` L1~L6+MEDIATION |
| 2026-08-18 | ⑤ 심의 | **방향 정정** — 목표 재정의(최대 적용·품질 우선·표준 스택 전면), v2.2 폐기·자산 이월, v3 재설계 개시 (사용자) | 위 «방향 전환 기록» |
| 2026-08-18 | ②′ 보강 조사 | 7레인 완료(출처 310) — 수렴 8·긴장 3 정리. 핵심: 품질 이득의 본체=폐루프(포맷 아님), Turtle 소비 표면 부적합→렌더 투영, OWL 추론 배제 권고, 산문 가이드 그래프 정본화는 dddjango가 첫 사례 | `-v3-research.md` + Q1~Q7 |
| 2026-08-18 | ③′ 블루프린트 v3 | 초안 작성 — E1~E8 확정 결정·폐루프 아키텍처·이관 전략·A/B 내장·T0~T5 절차·v2 이월 대조 | `-blueprint-v3.md` |
| 2026-08-18 | ④′ 적대 리뷰 | 6렌즈 69건(blocker 9) 전건 중재 반영 → **v3.1**. 핵심 결함: 잔차 0 이중 구속(→블록 모델)·A/B 번들 처치(→3암)·지표 발화 불능(→주 지표 재정의)·blank node↔SHACL 충돌·CI 집행점 부재·v2.1 운영 자산 이월 탈락 | `-v3-adversarial/` L1~L6+MEDIATION |
| 2026-08-18 | 검증 패스 | V1: 66/69 완전 착지(blocker 9 전건·미착지 0·반쪽 3)+MEDIATION 원장 누락 5건 발견 → 소급 등재. V2: major 4(핫픽스 채무 비차단 부재·B암 오염 위험·지표 ② 비맹검·CNL 무정의)+minor 6 → **전건 반영, v3.2** | `wf_c54f9a00-a42` 결과·블루프린트 §12 |
| 2026-08-18 | **⑤ v3.2 심의·동결** | **동결** (사용자 «오케이 v3.2 동결할게») — 문서 세트 커밋(정본화), 이후 수정은 §10 개정 절차로만 | `-blueprint-v3.md` §10·§12 |
| 2026-08-19 | T0 계획 적대 리뷰 | 사용자 발의(«뒤엎기 어려우니 적대 검증·표준 준수 검토») — 3렌즈(표준 정합·잠금 비용·실물/동결 정합) 32건(blocker 1·major 15·minor 16) **전건 반영 → 계획 v1.1**. blocker: B3 주입 재료가 동결 E8 한정 위반 → 검사기 산출 발췌로 교정 | `-t0-adversarial/` L1~L3+MEDIATION |
| 2026-08-19 | T0 계획 검토 | **통과** — D1~D5 전건 승인(사용자) | `-t0-plan.md` §6 |
| 2026-08-19 | **T0 검수** | **통과** — 기계 기준 6항 green + 계약 실물은 대리 검수(신선한 눈 감사 14건 → 기계 수리 11건 반영·재정 4건 디시전 시트) → 사용자 «전부 승인»: ①블록↔Work 3노드형(블루프린트 **개정 1**) ②규범 소유=검사기∨위임 에이전트 ③alias·RevisionKind 존치 ④표류 6건 EXPECTED 일괄 갱신(유령값 실증·372→371행). **`make verify` 전체 green(온톨로지+기존 세트 — 최초)** | `-t0-adversarial/V-*.md`·블루프린트 §12 개정 1 |
| — | T0 커밋 | **대기** — 사용자 커밋 승인 | — |

## 다음 작업 큐

1. ~~준비 사이클 전체~~ ✓ · ~~T0 계획(v1.1)·D1~D5 승인~~ ✓ · ~~T0 구현(묶음 ①~④)~~ ✓ · ~~T0 검수~~ ✓(대리 검수+디시전 시트 전건 승인 — 개정 1·소유 확장·EXPECTED 갱신 반영, **make verify 전체 green**)
2. **T0 커밋 — 사용자 승인 대기**(전 산출물 미커밋: ontology/·workspace/tools 신설 9종·Makefile·findings.py+개작 2종·codex 동기·픽스처·감사 기록·블루프린트 개정 1)
3. 커밋 후 → **T1 세부 계획** 수립(절 유형 센서스 606절+codex 대응 병행·파일럿 이관(밀집·혼합 대표 포함)·렌더 투영+동기 검증기·절 단위 원장·어휘 v1 안정화 선언·롤백 리허설 — v3.2 §8 T1) → 검토 → T1 착수
4. 이후 T1(절 유형 센서스+파일럿 이관) — T2 세부 계획에는 측정 렌즈 미니 적대 리뷰+18실런 비용 산정 필수(v3.2 §6)

별도 트랙(대기): 표류 실증 2건 수정(codex fat-model·#A~#B — 별도 발주), DR-68 릴리스 후속 2건, push 미실행.

## 문서 색인 (전부 `workspace/design/`)

| 문서 | 역할 |
|---|---|
| `2026-08-18-ontology-blueprint-v2.md` | **폐기된 v2.2** — v3의 개념 자산 출처로만 참조 (ID 체계·개정 규율·미러 판별 자산) |
| `2026-08-18-ontology-p0-census.md` + `-p0-census/` | ① 현황 실측 — 스택 무관, v3에서 그대로 유효 |
| `2026-08-18-ontology-research.md` + `-ontology-research/`(R1~R7) | ② 외부 조사 1차 — 거버넌스 축 |
| `2026-08-18-ontology-v3-research.md` + `-v3-research/`(Q1~Q7) | ②′ 보강 조사 종합+상세 — 표준 스택 운용·품질 증거 (출처 310) |
| `2026-08-18-ontology-blueprint-v3.md` | **동결 정본 (v3.2, 2026-08-18 동결)** — E1~E8·블록 모델·폐루프·3암 A/B·T0~T5·도구 처분표 |
| `2026-08-18-ontology-v3-adversarial/`(L1~L6 + MEDIATION.md) | ④′ v3 적대 리뷰 69건 + 중재·검증 기록 |
| `2026-08-18-ontology-adversarial/` | ④ v2 적대 리뷰 기록 (참고용) |
| `2026-08-18-ontology-t0-plan.md` | T0 세부 실행 계획(비동결·Claude 관리) — A1~A9·B1~B3·검수 절차·재량 결정 D1~D4 |
| `2026-08-18-ontology-adoption-log.md` | 이 파일 — 진행 기록·큐·색인 |

## 세부 기록

- 2026-08-19: **재량 결정 전건 승인**(사용자) — D1(verify 치환)·D2(훅 경량+fail-closed)·D3(분할)·D5(djr: 기저 URI = `https://numchida.com/ns/djr#`) 권고안대로, D4는 기결정(최신 파이썬). **T0 착수.**
- 2026-08-19: **T0 묶음 ① 완료** — A1: python 3.14.7(brew python@3.14)+`.venv`+`ontology-requirements.txt`(전량 핀)+`make ontology-env`+`ontology_env_smoke.py`(RDFC 벡터 3종·pySHACL 왕복 내장) 전부 green. **RDFC-1.0 실사: rdfcanon 1.0.0 채택** — W3C 공식 스위트 61/64(실패 3건은 rdflib 파스 단계 타입 리터럴 정규화 = 사슬 수준 특성, 자체 구현도 동일·채택 판단 중립. SHA-384 1건 별도 통과). rdflib 7.6.0 위 구동 검증(rdfcanon의 7.5.0 정확 핀은 `--no-deps`로 우회, 근거 기록). A2: `ontology/` 골격+`workspace/tools/ontology-authoring.md`(금지 목록·직렬화 규칙 명세·재직렬화 전용 커밋·ISSUED 행 형식·어휘 개정 절차·RDFC 결정·ODRL 봉인/역할 표·훅 루트·A3 열린 결정 3건). A4: `prefixes.ttl`(vann 9접두·djr=D5 값)+빈 `ISSUED`. A3 초안: `vocab/djr.ttl`(클래스 21·프로퍼티 39·개체 12, 149 트리플, 저-공리 준수·파스/NFC/무주석 검사 통과).
- 2026-08-19: **T0 묶음 ②·③ 완료 — A트랙 전체(A1~A9) green.** A5: 정본 직렬화기 `ontology_canon.py`(CANON_VERSION canon/1 — 정렬·NFC·ECHAR 7종·PN_LOCAL 비허용 문자 전체 IRI 고정·cons 셀 인라인 리스트)+4단 게이트 `ontology_gate.py`(gate-report/1 JSON·--write 저작 도우미·--root 스모크 지원·3단 검증용 결함 주입 훅). 개발 중 실결함 1건 잡음: rdflib `Dataset.graph()`가 무작위 genid를 quad에 실어 3단이 전 파일 red — 기본 그래프 적재로 수정(3단이 직렬화기 버그를 실제로 잡는다는 실증이기도 함). A6: `djr-shapes.ttl`(NodeShape 15·PropertyShape 31 — closed+ignoredProperties(rdf:type)·sh:or 규범 유형 완결성·sh:in severity 3값·uniqueLang)+`meta-house.ttl`(하우스 메타셰이프 — closed 말단 한정 SPARQL·ignoredProperties 의무·셰이프 IRI 의무)+골든 12벌(valid 4·invalid 8 — 완결성 4종·미배선·무유형·closed 위반·uniqueLang·sh:in 위반) 12/12 기대 일치+meta-SHACL 2층 green. A7: `ontology_hierarchy_check.py`+계수 기대표(9셰이프 — subClassOf 폐포 계수로 Obligation→Norm→Work 상속 실증). A9: 픽스처 10케이스(`workspace/eval/fixtures/ontology_gate/cases/`)+`ontology_gate_smoke.py` — **매핑 표 전 항목 차단 단 일치 10/10**(green 대조군 포함). A8: `make verify = verify-ontology(0~6, .venv 파이썬) + verify-base(기존 12종+byte-diff, 시스템 python3)` 합성, release [2/7]=`$(MAKE) verify` 치환(D1), pre-commit 훅+`make ontology-hooks` 설치 완료(core.hooksPath — 무변경 즉시 exit 0·불량 ttl 차단·venv 부재 fail-closed 실검증). B트랙은 서브에이전트 병행 중(서버 오류 2회 중단→재개).
- 2026-08-19: **T0 묶음 ④ 완료 — B트랙 전체(B1~B3) green. T0 구현 완료, 검수 대기.** B1: 스냅숏 동결(사본+원본/사본/spec_lint SHA-256+생성 커밋 해시). B2(서브에이전트 — 서버 오류 3회 중단·재개): `findings.py`(findings/0 스키마 — 계획 6핀 전부+sentinel 격리·Candidates ⓓ 채널·ContractFindings 선행 계약) + 대표 2종 개작 + reverse_coverage 등재 + codex byte 동기 + `findings_smoke.py` **단언 15/15**(개작 전후 stdout byte 동일=하위 호환 증명·레코드 내용 대조·green 0건 대조군). B3(메인 직접): `regen_loop_prototype.py`(스냅숏 조인·검사기 산출 발췌만 조립 — E8 규율) + **1왕복 데모 성공**: domain_model red 사본 61레코드 → 범위(order_pricing_service) violation 7건 조인 7/7 → 주입 프롬프트 → headless claude 1회 → 재검사 **7→0**(범위 밖 41건 불변). 기록: `workspace/eval/ab/B3-demo-record.md`.
- 2026-08-19: **대리 검수 2건 완료 + 중재 반영**(사용자 «하나하나 검수 어렵다» → 대리 검수 체제). ① 계약 실물 신선한 눈 감사(`-t0-adversarial/V-contract-audit.md`): blocker 1·major 3·minor 10 — 기계로 닫히는 11건 즉시 수리(직렬화 정렬 문면 정정 M-1·골든 7벌 보강 M-3(19골든)·closed-noignore 스모크 케이스(11케이스)·매핑 표 authoring 실체화 m-1·deprecated/replacedBy 보완 m-5·run_id 정합 m-7·게이트 ④ 위반 상세 m-8·§12 처분 현황 갱신 m-4 등) 후 재검증 전부 green. **재정 2건(B-1 블록↔Work 형상·M-2 비커버 규범)+경량 확인 2건(alias 형상·RevisionKind)은 디시전 시트로 사용자 상정.** ② 표류 6건 판정(`V-drift-verdict.md`): 25faad8 원인설 기각 — EXPECTED가 탄생 시점(3d92b50)부터 더러운 작업 트리 채집 유령값. 4커밋×3파이썬 재실행 실증, 회귀 0건 — **일괄 `--emit-expected` 갱신 안전**(사용자 승인 대기).
- 2026-08-19: **기존 표류 발견(T0 무관 — 별도 트랙)**: `make verify-base`의 checker_cross_matrix 차이 6건(check-layer-skeleton·check-usecase-dto-placement·check-db-table × event_publish/port_adapter_pairing). **청정 HEAD 워크트리에서 동일 재현 — T0 변경과 무관 실증.** 유래 추정: 25faad8(S2 검사기 개정) 후 EXPECTED census 미갱신. 처분(검사기 개정이 의도였는지 판단→`--emit-expected` 갱신)은 사용자 몫 — 이 red가 남는 동안 release [2/7] 차단(기존 [2/7]에서도 동일하게 차단됐을 상태·D1로 악화 아님).
- 2026-08-19: **T0 계획 3렌즈 적대 리뷰**(사용자 발의 — «한번 만들면 뒤엎기 어렵다, 적대 검증·표준 준수 검토 필요») — L1 표준 정합(1차 출처 14곳: RDFC-1.0·SHACL REC·Turtle·vann·PROV-O·pySHACL 등), L2 잠금 비용(계약 실물 8종의 변경 비용·되돌림 경로), L3 실물·동결 정합(§1 좌표 전 행 재확인+§8 T0 항목별 대조·rule-owner-map 재생성 byte-identical 실증). 32건 전건 중재 반영 → **v1.1**. 핵심 교정: ① B3 주입 재료를 검사기 산출 발췌로 한정(blocker — 동결 E8 정합 회복) ② meta-SHACL 2층(표준 SHACL-SHACL은 문법 부분집합만 — 하우스 메타셰이프 신설) ③ RDFC-1.0 성립 조건 명문+기성 구현(rdfcanon) 실사 ④ findings/0 스키마 6핀(버전·run_id·record_id·rule 값 공간·severity 대응·expression 예약) ⑤ verify 2분해(verify-ontology/verify-base — 롤백 한 줄 경로) ⑥ D5 신설(djr: 기저 URI 값) ⑦ 검수 패키지에 계약 실물 문면 검토 행. 파이썬은 사용자 결정으로 최신 안정판 확정(D4 종결).
- 2026-08-18: T0 계획 수립 전 점검(사용자 요청) — 조사 2회(R1~R7 거버넌스 축→v2 / Q1~Q7 표준 스택·품질 축→v3)의 구분, 폐루프·소비 표면(렌더)·산출물 5종·이관 라운드트립·검증 두 축(내용=정답지 있음/배선=신규 저작)을 확인. 사용자가 v3.2 수록 여부 검증 요청 → 동결본 대조 표로 확인(수치는 조사 문서 소재·Turtle 예시 프로퍼티명은 가칭임을 명시).
- 2026-08-18: **T0 세부 실행 계획 작성**(`-t0-plan.md`) — 실물 실측 선행: release [2/7]에 검증 세트 12종+33쌍 byte-diff 기존재(verify 편승 대상), git 훅 부재, python 3.9.6·rdflib/pySHACL 미설치, rule-owner-map=`workspace/plan/2026-08-11-rule-owner-map.md`, 규약 밖 11종 중 최소형=check-common-container(117행). A트랙 9항(A1~A9)·B트랙 3항(B1~B3)·작업 묶음 4개·검수 패키지 6항·재량 결정 D1~D4로 전개.
- 2026-08-18: 심의 지원 — 사용자 요청으로 조감도에 «완성형 — 전체 플로우»(저작→게이트→그래프 정본→렌더/규칙 팩→에이전트→검사기→위반 그래프→재생성·개정 루프)와 «구성요소별 청사진»(8개 구성요소: 코퍼스·에이전트·Coordinator·검사기·도구·codex 쌍둥이·모노레포 명세·픽스처 — 각 지금→완성형→전환 Stage→v3.2 근거 절) 섹션 추가. RDF(데이터 모델·정본)/RDFS(그 안의 어휘 층) 층 관계 설명 제공.

## 운영 규약

- 게이트마다: 이 로그의 게이트 로그에 행 추가 → 조감도의 상태 칩·배너·게이트 로그 갱신. 두 곳의 게이트 로그는 항상 동일 사건을 가리킨다(조감도는 요약, 여기는 근거 포함).
- 조감도 배너는 «지금 사용자가 확인할 것»만 담는다 — 항목이 없으면 «확인 대기 없음 · 진행 중: …»으로 바꾼다.
- 진행 중 세부 기록(중간 산출물, 발견, 재작업)은 이 로그에 날짜순으로 append.
