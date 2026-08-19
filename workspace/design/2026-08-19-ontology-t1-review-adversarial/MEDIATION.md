# T1 산출물 적대 검증 — 중재 기록 (2026-08-19)

> 리뷰어: codex CLI 4레인(read-only) — L-E Work 정합(전수 117)·L-F wiring(전수 117)·L-G 분해 경계·L-H 도구 코드(correctness). 발의: 사용자(«T1 산출물은 리뷰할 필요 없어?»). 중재자: Claude — 전건 원문·docstring·코드 실측 후 채택/기각. **발견 58건 → 채택 52·부분 채택 3·기각 1·등재(T3 전 정비) 2.**

## L-E (Work 정합 — 발견 13)

- **유형 오판 9건 전건 채택**: Permission 2(R-0010 CQRS 선택 적용·R-0074 지역 중복 인정), **Override 2(R-0014 전략 우선·R-0059 기존 경로 우선 재사용 — 어휘 Override 클래스 첫 실사용)**, Exception 5(R-0026 항-(2)·R-0030 test 조건부·R-0048 add/update 한정·R-0049 해소 조건·R-0114 wire 보존 carveout). 뿌리: 저작이 조건부·허용·우선 양상을 Obligation으로 평탄화.
- **라벨 왜곡 1건 채택**: R-0052 «직접 import한» 한정어 복원(검사기 차단 범위 과대 표시 — 다음 문장이 2-hop을 AST 밖으로 돌림).
- **누락 3건 채택**(«애매하면 포함+비고»): §6.1 b17 framework 소유 선언·§6.2 b15 허용 범위 한정·b29 직접 소유 의무(뒤 2건 재진술 의심 비고).

## L-F (wiring — 발견 21)

- **21건 전건 채택**(조정 2): 코덱스가 검사기 27종 docstring을 실독해 **미사용 검사기 9종의 정확한 담당을 발굴** — response-schema-bypass(R-0111·0112)·choices-literal-consumption(R-0021)·synthetic-infra-exc+context-isolation(R-0105)·transaction-boundary(R-0017)·usecase-dto-placement(R-0085)·app-container(R-0031)·business-vocabulary #119(R-0095)·db-table(R-0028). 오귀속 교정: ninja-boundary(MIDDLEWARE 한정 실독)→controller-contract 4건(R-0004·0096·0102·b17), 순환 배선 해소(R-0037 — 검사기는 자기 입력 전제), preserve-established 의미 미적용(R-0038→design-review-api), 3주체 절차(R-0049), domain-model 범위 정밀화(R-0018·0019 — 복제·SQL predicate 검사 부재 실독 확인).
- **조정 ①** R-0044: 재실측 결과 marker를 **양쪽 공동 발행**(error-centralization 3곳+controller-contract 4곳) — «교체» 아닌 **병기**. **조정 ②** R-0017: check-domain-model #257(루트 경유)이 실재 — «유지+transaction-boundary 병기».
- 기계 대조: spec basis↔ttl 트리플 불일치 0(코덱스 확인) — 결함은 배선 «내용», 조립 «기계»는 무결.
- **뿌리 교훈**: 저작이 4원 ②(docstring)를 §16 매핑 표 재료로만 좁게 적용 — authoring §16에 «배선 전 검사기 로스터 전수 실독 의무» 보강.

## L-G (분해 경계 — 발견 4)

- **채택 3**: ddd §3.2 b2(식별자 동등성 — #259·#260 축)·b3(캡슐화 의무 — 인용 프레임이나 «해야 한다») prose→norm+Work 각 1 / §6.2 b9~b11(BC 오류 언어 리스트 항) Work 3 — b12 유일성 채번과의 일관성 논거 수용. 일관 원칙 수립: «항이 완결 구속 술어를 갖거나 지배 문장의 독립 검사 가능 항목이면 Work·순수 명사구 나열은 지배 Work 귀속».
- **부분 기각 1**: §6.1 매핑 불릿 13항(8→21 주장) — P0·동결 센서스가 정확히 이 13항을 «명사구(문장 아님)»로 명시 판정(측정 연속성·동결 §4-1)+각 항이 이미 **블록 IRI로 개별 좌표화**돼 위반 참조 가능. 항 단위 Work 승격은 T2/T3 재론 논점으로 등재(블록 좌표 보존 — 소급 채번 무손실).
- 잔차 재판정: §6.2 b19·b24 prose 유지(레인 동의) — 정정 후 census 대비 §6.2 88 vs 85(+3: b9~b11)·§3.2 20 vs 23(−3: blockquote restates 1+정의·이유 2).

## L-H (도구 코드 — 발견 20: blocker 12·major 5·minor 3)

**즉시 수정 18건**: #1 path↔manifest 대조(migrate)+Section IRI 경로 검증(render) · #2 재사용 rid의 (label·class) 정합 대조 · #3 Expression 날짜 보존(재실행 멱등) · #4 graph 절 메타 불일치 시 LEDGER 재append · #5 census fail-closed(실패 시 동결본 미기록) · #7 미폐쇄 frontmatter 구조 오류 · #8 빈 파일 0절 · #10 render apply 원자성(전 절 검증 후 일괄 기록) · #11 mirror의 원장 부재 fail-closed(마커 실재 시 StructureError — 소스 원문 파괴 경로 차단) · #12 fragment 정규형 검사(frag_encode 단일 출처화·불필요 인코딩 차단) · #13 LEDGER↔rules 소유권 이중 정본 대조(render_sync) · #14 owner 값 공간 폐쇄 · #15 SyncDebt 전체 IRI 비교 · #16 issued_check 리터럴 제거+djr 네임스페이스 한정 · #17 날짜 실검증+경로 rules/ 제약 · #18 고아 Work 질의 · #19 currentExpression 부재 질의 · #20 미지 kind 차단. **+#9 부분**: 렌더 LF 추가 자체는 미수정이나 «마커 제거==baseline» 상시 검사(render_sync)가 이 계열 원문 변형 전부를 red로 잡음.

**등재 2건(T3 진입 조건)**: #6 절 키 서수 대장 미구현(절 삽입 시 키 재할당 도구 필요 — 현재 코퍼스는 동결 상태라 무해) · #9 잔여(본문 0블록 절 렌더의 개행 정보 손실 — 그런 절은 이관 대상 아님+baseline 검사 방어).

## 반영 결과

- 명세 2벌 정정(`[adv 중재 정정]` 표기 — 유형 9·라벨 1·kind 전환 2·Work 추가 8·배선 21) → **ISSUED 클린 재채번**(미커밋 대장 — R-0001~R-0125) → rules/wiring 재생성·재투영(«이미 동기» — 블록 리터럴 불변 실증) → 기대표 +8 정확 대조 갱신.
- 확정치: **Work 125**(Obligation 다수·Prohibition·Permission 8·Exception 12·Override 2 — 재집계는 구조 검사 리포트) · 배선 트리플 확장(검사기 16종 실사용).
- 도구 수정 18건 전부 self-test 통과·verify 전체 재확정.
