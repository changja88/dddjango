# E07 — implementation-django-ninja P0 대사 노트 (T1-1)

작성: 2026-08-19 · 기계 절 37(sections.tsv E07) ↔ P0 상세 인벤토리 28절(`workspace/design/2026-08-18-p0-census/E07-implementation-django-ninja.md`, 절 28·규범 319).

## §1 문서별 접기 규약 명문화

**implementation-django-ninja-skill** (기계 5절 ↔ P0 4절):

- P0는 본문 없는 제목 전용 절을 독립 절로 세지 않는다 — h1 제목 절(기계 s002, L7–8)이 P0 목록에 없다.
- frontmatter는 P0도 «frontmatter(description)» 절로 별도 계수했으므로 기계 s001과 1:1 대응한다.
- 나머지 h2 절 3개(언제 쓰나·핵심 운영 원칙·상세 레퍼런스)는 1:1.

**implementation-django-ninja-final** (기계 32절 ↔ P0 24절):

- P0는 본문 없는 h2 컨테이너 스텁(§ 번호 헤딩+빈 줄 2행짜리 — 하위 h3가 실내용을 가지는 §1·§2·§3·§4·§5·§6·§9의 상위 헤딩)을 절로 세지 않는다. 기계 스텁 7개: s003-1·s007-2·s011-3·s015-4·s018-5·s021-6·s027-9.
- P0는 서두를 병합한다 — 기계 s001(h1 제목+blockquote 위임 안내, L1–15)과 s002(목차, L16–32)를 P0 «서두(제목·위임 안내·목차, L1–29)» 1절로 합산. 서두의 규범 3문장은 전부 기계 s001의 blockquote에 있고 목차(s002)는 규범 0이다.
- 경계 미세 차이: P0 서두 끝 L29 vs 기계 s002 끝 L32 — P0가 목차 뒤 공백·`---` 구분선(L30–32)을 제외한 처리 차이. 절 대응에는 영향 없음(규약 내).
- 부록 제외 규약은 없다 — §12 참고 문헌도 P0가 절로 계수(규범 0)했고 기계 s032-12와 1:1.

## §2 P0 절 전건 대사 표

| P0 절 라벨 | 대응 기계 절 키(범위) | 규약 |
|---|---|---|
| [SKILL.md] frontmatter(description) | skill/s001 | 1:1 |
| [SKILL.md] § 언제 쓰나 | skill/s003 | 1:1 (h1 제목 절 s002는 P0 미계수 — 제목 전용 제외) |
| [SKILL.md] § 핵심 운영 원칙 | skill/s004 | 1:1 |
| [SKILL.md] § 상세 레퍼런스 | skill/s005 | 1:1 |
| 서두(제목·위임 안내·목차, L1–29) | final/s001–s002 | 서두 병합(2→1) — 규범 3은 전부 s001 귀속 |
| §1.1 Django Ninja skill의 역할 | final/s004-1.1 | 1:1 (§1 스텁 s003-1은 P0 미계수) |
| §1.2 다른 source reference로 위임할 책임 | final/s005-1.2 | 1:1 |
| §1.3 Router thinness 원칙 | final/s006-1.3 | 1:1 |
| §2.1 Router 등록 | final/s008-2.1 | 1:1 (§2 스텁 s007-2 미계수) |
| §2.2 Operation 선언 | final/s009-2.2 | 1:1 |
| §2.3 클래스 컨트롤러 (ninja-extra) — 신규 표준 | final/s010-2.3 | 1:1 |
| §3.1 Request/response schema 분리 | final/s012-3.1 | 1:1 (§3 스텁 s011-3 미계수) |
| §3.2 ModelSchema 사용 기준 | final/s013-3.2 | 1:1 |
| §3.3 Resolver와 computed field | final/s014-3.3 | 1:1 |
| §4.1 Authentication | final/s016-4.1 | 1:1 (§4 스텁 s015-4 미계수) |
| §4.2 Authorization | final/s017-4.2 | 1:1 |
| §5.1 Filtering과 sorting | final/s019-5.1 | 1:1 (§5 스텁 s018-5 미계수) |
| §5.2 Pagination | final/s020-5.2 | 1:1 |
| §6.1 Status code mapping | final/s022-6.1 | 1:1 (§6 스텁 s021-6 미계수) |
| §6.2 `dddjango-code-json` 오류 프로필 | final/s023-6.2 | 1:1 |
| §6.3 콘텐츠 협상 실패 (406/415) | final/s024-6.3 | 1:1 |
| §7 Idempotency-Key | final/s025-7 | 1:1 (§7은 h2 단독 절 — 스텁 아님) |
| §8 OpenAPI | final/s026-8 | 1:1 |
| §9.1 공개 HTTP 검증 범위 | final/s028-9.1 | 1:1 (§9 스텁 s027-9 미계수) |
| §9.2 검증 보고 기준 | final/s029-9.2 | 1:1 |
| §10 DRF-to-Ninja migration | final/s030-10 | 1:1 |
| §11 라우팅 기준 | final/s031-11 | 1:1 |
| §12 참고 문헌 | final/s032-12 | 1:1 (규범 0 — P0도 0으로 계수) |

대사 결과: P0 28절 전건 대응. 기계 전용 절 9개(skill h1 제목 s002 + final 목차 s002 + h2 스텁 7)는 모두 위 접기 규약(제목 전용 제외·서두 병합)으로 설명되며 전부 규범 0·NAR이다.

## §3 잔차

설명 불가 잔차 0.

- P0에만 있고 기계에 없는 절: 없음.
- 기계에만 있고 규약 밖인 절: 없음 — 기계 전용 9개 절 전부가 §1의 두 접기 규약(제목/컨테이너 전용 절 미계수, 서두 병합)에 귀속된다.
- 경계 잔차(비절 단위): P0 서두 끝행 L29 vs 기계 s002 끝행 L32의 3행 차 — 목차 뒤 공백·구분선 귀속 차이로, 내용·규범 계수에 영향 없어 잔차로 세지 않는다.

## §4 규범 계수 대조

이번 분류 norm_count 합계 **319** (skill 44 + final 275) vs P0 **319** — **차이 0**.

- 방법: 측정 연속성 의무에 따라 P0의 절 단위 계수를 기계 절 granularity에 재배분했다. P0 28절 중 27절이 기계 절과 1:1이라 값을 그대로 승계했고, 유일한 분할 대응인 서두(3문장)는 원문 확인 결과 규범 3문장(위임 기준 문장·greenfield 기본 목표·DRF 보조 근거 한정)이 전부 blockquote(기계 s001)에 있어 s001=3·s002(목차)=0으로 배분했다.
- 표본 재검증: §1.2=4(위임 4문장)·§11=6(불릿 6)·§9.2=3·§10=4를 원문에서 재계수해 P0 값과 일치 확인.
- 기계 전용 9절(제목·목차·스텁)은 전부 규범 0이라 총계에 기여하지 않는다 — 절 수 차(37 vs 28)가 규범 총계 차를 만들지 않는 구조.
- P0 계수 비고 승계: 명사구 체크리스트(§2.1 확인 5·§3.2 확인 4·§6.1 상태코드 13·§8 후보 10·§9.1 후보 8·§9.2 artifact 5·§10 checklist 10)는 지배 문장으로만 계수돼 실제 구속 항목 수는 문장 수보다 크다(55+). 이 관례도 그대로 유지했다.

## 부기 — codex 대응

- `codex-dddjango/skills/implementation-django-ninja/references/final.md`: dddjango판과 **byte 동일**(diff 무출력) → final 32절 전부 SAME.
- `codex-dddjango/.../SKILL.md`(55행): 차이는 ⑴ frontmatter `user-invocable: false` 행 부재(Claude 플러그인 전용 필드) ⑵ 스킬명 표기 `dddjango:architecture-ddd`→`dddjango-architecture-ddd`·`implementation-test`→`dddjango-implementation-test`(s001·s003). 모두 플랫폼 표기 치환 이내로 판정 → skill 5절 전부 SAME. 합계: SAME 37 / DIFF 0 / ABSENT 0.
