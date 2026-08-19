# E08 — P0 대사 노트 (T1-1 절 유형 센서스)

담당 문서군: architecture-db-skill · architecture-db-final · architecture-api-skill · architecture-api-final
기계 절 145 (sections.tsv E08 행 수와 동수) ↔ P0 39절 · 규범 310문장 (`workspace/design/2026-08-18-p0-census/E08-architecture-db-api.md`)

## §1 문서별 접기 규약 명문화

- **architecture-db-skill / architecture-api-skill (공통 규약)**: P0 절 = frontmatter 1절 + h2 3절. 기계 절의 `(전문)`(s001)이 P0 frontmatter 절에 1:1 대응하고, h2 3절(언제 쓰나·핵심 운영 원칙·상세 레퍼런스)은 1:1 대응한다. **h1 제목 절(s002, 본문 0행)은 P0가 절로 계수하지 않았다**(제목 전용 — 서두 병합이 아니라 미계수). 따라서 기계 5절 = P0 4절 + h1 제목 절 1.
- **architecture-db-final / architecture-api-final (공통 규약)**: P0 절 = 목차(h2) 1절 + 최상위 §N(h2) 절. **h3 소절(§N.M)은 전부 상위 §N에 접는다**(P0 집계 방식 메모 «소절(§N.M)은 상위 절에 귀속» 그대로). api-final의 **h4 2절(s025 `dddjango-code-json`·s026 framework 경계)은 §5.4(h3)에 접히고, §5.4는 다시 §5(h2)에 접힌다.** h1 제목 절(s001)은 SKILL과 같은 규약으로 P0 미계수. 부록 제외 규약은 없다 — §14/§15 참고 문헌도 P0 절로 계수됐다(규범 0).
- 검산: db-final 기계 68 = h1 1 + P0 15절(목차 1 + h2 14 + 접힌 h3 52). api-final 기계 67 = h1 1 + P0 16절(목차 1 + h2 15 + 접힌 h3 48 + 접힌 h4 2). SKILL 각 5 = h1 1 + P0 4절. 합 145 = P0 39 + h1 제목 절 4 + 접힌 h3/h4 102.

## §2 P0 절 전건 대사 표 (39건)

| P0 절 라벨 | 대응 기계 절 키(범위) | 규약 |
|---|---|---|
| db-skill frontmatter | architecture-db-skill/s001 | (전문) 1:1 |
| db-skill 언제 쓰나 | architecture-db-skill/s003 | h2 1:1 |
| db-skill 핵심 운영 원칙 | architecture-db-skill/s004 | h2 1:1 |
| db-skill 상세 레퍼런스 | architecture-db-skill/s005 | h2 1:1 |
| db-final 목차 | architecture-db-final/s002 | h2 1:1 |
| db-final §1 | s003-1 + s004-1.1 + s005-1.2 | h3→h2 접기 |
| db-final §2 | s006-2 + s007-2.1…s011-2.5 | h3→h2 접기 |
| db-final §3 | s012-3 + s013-3.1…s016-3.4 | h3→h2 접기 |
| db-final §4 | s017-4 + s018-4.1…s020-4.3 | h3→h2 접기 |
| db-final §5 | s021-5 | h2 단독(소절 없음) 1:1 |
| db-final §6 | s022-6 + s023-6.1…s026-6.4 | h3→h2 접기 |
| db-final §7 | s027-7 + s028-7.1…s031-7.4 | h3→h2 접기 |
| db-final §8 | s032-8 + s033-8.1…s036-8.4 | h3→h2 접기 |
| db-final §9 | s037-9 + s038-9.1…s044-9.7 | h3→h2 접기 |
| db-final §10 | s045-10 + s046-10.1…s050-10.5 | h3→h2 접기 |
| db-final §11 | s051-11 + s052-11.1…s056-11.5 | h3→h2 접기 |
| db-final §12 | s057-12 + s058-12.1…s061-12.4 | h3→h2 접기 |
| db-final §13 | s062-13 + s063-13.1…s067-13.5 | h3→h2 접기 |
| db-final §14 | s068-14 | h2 단독 1:1 |
| api-skill frontmatter | architecture-api-skill/s001 | (전문) 1:1 |
| api-skill 언제 쓰나 | architecture-api-skill/s003 | h2 1:1 |
| api-skill 핵심 운영 원칙 | architecture-api-skill/s004 | h2 1:1 |
| api-skill 상세 레퍼런스 | architecture-api-skill/s005 | h2 1:1 |
| api-final 목차 | architecture-api-final/s002 | h2 1:1 |
| api-final §1 | s003-1 + s004-1.1…s007-1.4 | h3→h2 접기 |
| api-final §2 | s008-2 + s009-2.1…s011-2.3 | h3→h2 접기 |
| api-final §3 | s012-3 + s013-3.1…s015-3.3 | h3→h2 접기 |
| api-final §4 | s016-4 + s017-4.1…s019-4.3 | h3→h2 접기 |
| api-final §5 | s020-5 + s021-5.1…s024-5.4 + s025 + s026 | h3→h2 접기 + **h4 2절→§5.4→§5 이중 접기** |
| api-final §6 | s027-6 + s028-6.1…s030-6.3 | h3→h2 접기 |
| api-final §7 | s031-7 + s032-7.1…s034-7.3 | h3→h2 접기 |
| api-final §8 | s035-8 + s036-8.1…s039-8.4 | h3→h2 접기 |
| api-final §9 | s040-9 + s041-9.1…s043-9.3 | h3→h2 접기 |
| api-final §10 | s044-10 + s045-10.1…s047-10.3 | h3→h2 접기 |
| api-final §11 | s048-11 + s049-11.1…s051-11.3 | h3→h2 접기 |
| api-final §12 | s052-12 + s053-12.1…s056-12.4 | h3→h2 접기 |
| api-final §13 | s057-13 + s058-13.1…s061-13.4 | h3→h2 접기 |
| api-final §14 | s062-14 + s063-14.1…s066-14.4 | h3→h2 접기 |
| api-final §15 | s067-15 | h2 단독 1:1 |

## §3 잔차

**설명 불가 잔차 0.**

기계에만 있고 P0에 없는 절은 h1 제목 절 4건(architecture-db-skill/s002, architecture-db-final/s001, architecture-api-skill/s002, architecture-api-final/s001)뿐이며, 전부 §1의 «h1 제목 절 미계수» 규약으로 설명된다(각 절은 제목+공백 2행 이하, 규범 0). P0에만 있고 기계에 없는 절은 없다. 그 외 기계 절 전건이 §2의 접기 규약 안에서 P0 39절에 귀속된다.

## §4 규범 계수 대조

| 구분 | 이번(기계 절 합) | P0 | 차 |
|---|---:|---:|---:|
| architecture-db-skill | 18 | 18 | 0 |
| architecture-db-final | 106 | 106 | 0 |
| architecture-api-skill | 20 | 20 | 0 |
| architecture-api-final | 167 | 166 | **+1** |
| **합계** | **311** | **310** | **+1** |

차이의 원인:

1. **+1의 단일 원인 — api-final s020-5(§5 서두)**: «클라이언트가 의존할 수 있는 항목은 명시적으로 기록한다»는 기록 의무 지시다. P0 §5=45의 구성 명세(§5.1=9 + §5.2=6 + §5.3=1 + §5.4=29)에 서두 몫이 없어 P0는 이 문장을 계수하지 않은 것으로 추정된다(P0는 db §8·§11 서두 지시는 계수했으므로 비일관 지점). 이번 센서스는 «애매하면 포함+비고» 규약을 적용해 1로 계수했다.
2. **P0는 절 단위 집계였고 이번은 기계 절 단위 배분**이라, h3/h4로 쪼개진 소절별 수치는 이번 센서스의 신규 산출이다. 배분은 P0 비고의 구성 명세를 그대로 따랐다(§9: 9.4=1/9.5=18/9.6=12/9.7=12, §5: 5.1=9/5.2=6/5.3=1/5.4=29, §8: 8.1=3/8.2=3/8.3=3/8.4=12, §13: 13.2=6/13.3=12/13.4=6 등).
3. **P0 내부 불일치 1건 승계 처리**: api §5.4의 P0 비고 내부 합(우선순위 4+혼합 금지 2+관할 4+code-json 15+framework 3 = 28)이 절 합(29)과 1 어긋난다. 이번 배분에서는 관할 문단을 문장 단위로 재검해 5문장(wire 계약 주어 선언·preserve 비대상·신규 범위 레시피·G1 표면화 STOP·혼합 금지 주어)으로 계수, s024-5.4=11 + s025=15 + s026=3 = 29로 절 합을 유지했다.
4. 표 행 계수의 P0 비일관(예: §7.4·§8.1·§11.3 표 행은 계수, §9.4·§11.4·§5.3 표 행은 미계수)은 그대로 승계하고 각 행 note에 표기했다 — 수치 연속성을 우선했다.

부기(codex 대사): 4파일 전부 SAME — final.md 2건은 codex판과 바이트 동일, SKILL.md 2건은 `architecture-ddd`→`dddjango-architecture-ddd` 개명(콜론→대시 접두 포함)과 `user-invocable: false` 제거뿐(플랫폼 표기 치환 이내, P0 특이 발견 6 «표류 아님» 재확인). DIFF 0 · ABSENT 0.
