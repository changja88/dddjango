# E06 — discipline-tdd P0 대사 노트 (T1-1)

작성일: 2026-08-19 · 기준: 기계 절 76(sections.tsv) vs P0 절 63(`workspace/design/2026-08-18-p0-census/E06-discipline-tdd.md`, 규범 182)

## §1 문서별 접기 규약

**discipline-tdd-skill (기계 5절 ↔ P0 4절)**

1. 기계 `(전문)` 절(s001, frontmatter)은 P0 «frontmatter (name·description)» 절에 1:1 대응한다.
2. 내용 없는 h1 문서 제목 스텁(s002 «TDD 실천 규율», 헤딩+공백 2행)은 P0가 절로 세지 않았다 — P0는 본문이 있는 헤딩만 절로 계수.
3. h2 본문 절 3개(언제 쓰나·핵심 운영 원칙·상세 레퍼런스)는 1:1.

**discipline-tdd-final (기계 71절 ↔ P0 59절)**

1. 기계 s001(h1 제목 + 직후 인용구, 1–7행)은 P0 «문서 서문(제목 직후 인용구)» 절에 대응한다 — 서두 병합.
2. 본문 없는 순수 h2 장 제목 스텁 12개(§1·§2·§3·§4·§5·§6·§7·§9·§11·§12·§16·§17 — 각 헤딩+공백 2행)는 P0가 절로 세지 않았다. 반면 헤딩 직속 본문이 있는 h2(§8·§10 도입 표·§13·§14·§15·§18·참고 문헌)는 P0에도 절로 존재해 1:1.
3. 모든 h3 절(§1.1~§17.4)은 1:1.

**검산**: 기계 76 = P0 63 + 접힌 스텁 13(skill h1 스텁 1 + final h2 스텁 12). ✓

## §2 P0 절 전건 대사 표

| P0 절 라벨 | 대응 기계 절 키 | 규약 |
|---|---|---|
| SKILL frontmatter (name·description) | discipline-tdd-skill/s001 | (전문)=frontmatter |
| SKILL ## 언제 쓰나 | discipline-tdd-skill/s003 | 1:1 |
| SKILL ## 핵심 운영 원칙 | discipline-tdd-skill/s004 | 1:1 |
| SKILL ## 상세 레퍼런스 | discipline-tdd-skill/s005 | 1:1 |
| final 문서 서문(제목 직후 인용구) | discipline-tdd-final/s001 | 서두 병합(h1+인용구) |
| §1.1 TDD의 목표 | discipline-tdd-final/s003-1.1 | 1:1 |
| §1.2 TDD를 해야 하는 이유: 용기 | discipline-tdd-final/s004-1.2 | 1:1 |
| §2.1 기본 사이클 | discipline-tdd-final/s006-2.1 | 1:1 |
| §2.2 pytest로 보는 TDD 사이클 | discipline-tdd-final/s007-2.2 | 1:1 |
| §3.1 두 학파의 기원과 핵심 차이 | discipline-tdd-final/s009-3.1 | 1:1 |
| §3.2 상태 검증 vs 행위 검증 | discipline-tdd-final/s010-3.2 | 1:1 |
| §3.3 Inside-Out vs Outside-In | discipline-tdd-final/s011-3.3 | 1:1 |
| §3.4 실전 권고: 상황별 선택 | discipline-tdd-final/s012-3.4 | 1:1 |
| §4.1 네 가지 기둥 | discipline-tdd-final/s014-4.1 | 1:1 |
| §4.2 회귀 방지의 위상 | discipline-tdd-final/s015-4.2 | 1:1 |
| §4.3 리팩토링 내성 | discipline-tdd-final/s016-4.3 | 1:1 |
| §4.4 CAP 정리와의 유사성 | discipline-tdd-final/s017-4.4 | 1:1 |
| §4.5 세 가지 테스트 스타일 | discipline-tdd-final/s018-4.5 | 1:1 |
| §4.6 테스트 품질 3대 속성 | discipline-tdd-final/s019-4.6 | 1:1 |
| §5.1 테스트 후보 목록 | discipline-tdd-final/s021-5.1 | 1:1 |
| §5.2 한 단계 테스트 | discipline-tdd-final/s022-5.2 | 1:1 |
| §5.3 시작 테스트 | discipline-tdd-final/s023-5.3 | 1:1 |
| §5.4 설명 테스트 | discipline-tdd-final/s024-5.4 | 1:1 |
| §5.5 영구 테스트 입장 심사와 현행 계약 수명 주기 | discipline-tdd-final/s025-5.5 | 1:1 |
| §6.1 가짜로 구현하기 | discipline-tdd-final/s027-6.1 | 1:1 |
| §6.2 삼각측량 | discipline-tdd-final/s028-6.2 | 1:1 |
| §6.3 명백한 구현 | discipline-tdd-final/s029-6.3 | 1:1 |
| §7.1 테스트 격리 | discipline-tdd-final/s031-7.1 | 1:1 |
| §7.2 AAA 패턴 | discipline-tdd-final/s032-7.2 | 1:1 |
| §7.3 테스트 데이터 | discipline-tdd-final/s033-7.3 | 1:1 |
| §7.4 명백한 데이터 | discipline-tdd-final/s034-7.4 | 1:1 |
| §7.5 테스트 명명 규칙 | discipline-tdd-final/s035-7.5 | 1:1 |
| §7.6 Mock보다 출력·상태 검증 우선 | discipline-tdd-final/s036-7.6 | 1:1 |
| §7.7 깨진 테스트/깨끗한 체크인 | discipline-tdd-final/s037-7.7 | 1:1 |
| §8 테스트 더블 분류 체계 | discipline-tdd-final/s038-8 | 1:1(본문 있는 h2) |
| §9.1 이중 루프 TDD | discipline-tdd-final/s040-9.1 | 1:1 |
| §9.2 Walking Skeleton | discipline-tdd-final/s041-9.2 | 1:1 |
| §9.3 Mock Roles, Not Objects | discipline-tdd-final/s042-9.3 | 1:1 |
| §9.4 Tell, Don't Ask | discipline-tdd-final/s043-9.4 | 1:1 |
| §10 도입(패턴×단계 표) | discipline-tdd-final/s044-10 | 1:1(본문 있는 h2) |
| §10.1 값 객체 | discipline-tdd-final/s045-10.1 | 1:1 |
| §10.2 널 객체 | discipline-tdd-final/s046-10.2 | 1:1 |
| §10.3 팩토리 메서드 | discipline-tdd-final/s047-10.3 | 1:1 |
| §11.1 차이점 일치시키기 | discipline-tdd-final/s049-11.1 | 1:1 |
| §11.2 변화 격리하기 | discipline-tdd-final/s050-11.2 | 1:1 |
| §11.3 데이터 이주시키기 | discipline-tdd-final/s051-11.3 | 1:1 |
| §11.4 메서드 추출하기 | discipline-tdd-final/s052-11.4 | 1:1 |
| §11.5 메서드 인라인 | discipline-tdd-final/s053-11.5 | 1:1 |
| §11.6 인터페이스 추출하기 | discipline-tdd-final/s054-11.6 | 1:1 |
| §11.7 메서드 옮기기 | discipline-tdd-final/s055-11.7 | 1:1 |
| §11.8 메서드 객체 | discipline-tdd-final/s056-11.8 | 1:1 |
| §12.1 행위 냄새 | discipline-tdd-final/s058-12.1 | 1:1 |
| §12.2 코드 냄새 | discipline-tdd-final/s059-12.2 | 1:1 |
| §13 레거시 코드 다루기 | discipline-tdd-final/s060-13 | 1:1(본문 있는 h2) |
| §14 Property-Based Testing | discipline-tdd-final/s061-14 | 1:1(본문 있는 h2) |
| §15 Mutation Testing | discipline-tdd-final/s062-15 | 1:1(본문 있는 h2) |
| §16.1 TDD와 BDD의 관계 | discipline-tdd-final/s064-16.1 | 1:1 |
| §17.1 TDD as Prompt Engineering | discipline-tdd-final/s066-17.1 | 1:1 |
| §17.2 AI 보조 TDD 워크플로우 | discipline-tdd-final/s067-17.2 | 1:1 |
| §17.3 TDD가 AI 코딩에서 더 중요한 이유 | discipline-tdd-final/s068-17.3 | 1:1 |
| §17.4 dddjango Admission을 추가한 TDAID 6단계 | discipline-tdd-final/s069-17.4 | 1:1 |
| §18 Python 테스트 생태계 심화 | discipline-tdd-final/s070-18 | 1:1(본문 있는 h2) |
| final 참고 문헌 | discipline-tdd-final/s071 | 1:1(§ 번호 없는 h2) |

전건 63행. P0에만 있고 기계에 없는 절: 0.

## §3 잔차

기계에만 있고 P0에 없는 절 13개는 전부 §1의 접기 규약으로 설명된다:

- discipline-tdd-skill/s002 — h1 제목 스텁(규약 skill-2)
- discipline-tdd-final/s002-1·s005-2·s008-3·s013-4·s020-5·s026-6·s030-7·s039-9·s048-11·s057-12·s063-16·s065-17 — 순수 h2 장 제목 스텁 12개(규약 final-2)

13개 모두 헤딩+공백 2행·본문 0·규범 0이며 분류는 전부 NAR/none/0으로 P0 합계에 영향이 없다.

**설명 불가 잔차 0.**

## §4 규범 계수 대조

| 구분 | 이번 T1-1 | P0 | 차이 |
|---|---:|---:|---:|
| discipline-tdd-skill | 26 | 26 | 0 |
| discipline-tdd-final | 156 | 156 | 0 |
| **합계** | **182** | **182** | **0** |

차이 0. 원인: 접기 규약 하에서 규범을 가진 P0 절 전부가 기계 절과 1:1 대응하고, 기계에만 있는 13개 절은 모두 내용 0 스텁이라 P0 절 단위 계수를 기계 절에 그대로 배분할 수 있었다(측정 연속성 의무에 따라 P0의 문장 판정 규약 — 코드 펜스 안 절차 지시 포함(§2.1·§17.4), 화이트/블랙리스트 명사구는 지배문만 계수(§5.5), 표 해결책 열 명사구 제외(§12.1), 애매 포함+비고 — 을 그대로 승계했다). P0가 절 단위 집계였음에도 절 경계가 세분(스텁 분리)만 됐을 뿐 병합·분할이 없어 재배분 오차가 생기지 않았다.

부기 — codex 대응: `references/final.md`는 byte-identical(71절 전부 SAME). `SKILL.md`는 frontmatter에서 `user-invocable: false` 부재로 s001만 DIFF이고, «언제 쓰나»의 스킬명 3건 치환(`dddjango-implementation-test`·`dddjango-discipline-cleancode`)은 codex 실제 스킬명과 일치하는 플랫폼 표기 치환이라 SAME 판정(단, codex description 문면의 `implementation-test` 미치환은 s001 비고에 기록).
