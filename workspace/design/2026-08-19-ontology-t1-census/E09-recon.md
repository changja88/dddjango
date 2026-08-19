# E09 대사 노트 — T1-1 절 유형 센서스 vs P0 상세 인벤토리

기준: 기계 절 = `sections.tsv` p0_group=E09 46행. P0 정본 = `workspace/design/2026-08-18-p0-census/E09-web-houserules.md`(절 40·규범 276).

## §1 문서별 접기 규약

- **implementation-django-web-skill** (기계 5 ↔ P0 3): P0는 YAML frontmatter(전문)와 본문 없는 h1 제목을 절로 세지 않았다 — 기계 s001(전문)·s002(h1)는 P0 절 목록 밖의 서두 절이다. h2 3개(언제 쓰나·핵심 운영 원칙·상세 레퍼런스)는 1:1 대응.
- **implementation-django-web-final** (기계 12 ↔ P0 12): 완전 1:1. 기계 s001은 h1 제목+출처 약어 인용 블록(1~19행)을 한 절로 묶으며 P0 «머리말(출처 약어 블록)»과 대응(h1은 머리말에 접힘). h2 §1~§11은 그대로 1:1.
- **discipline-houserules-skill** (기계 12 ↔ P0 10): 위와 같은 서두 규약 — s001(전문)·s002(h1)가 P0 밖. 나머지 h2/h3 10개는 1:1 (P0도 §4.1·§6.1·§6.2 h3를 개별 절로 셌으므로 h3 접기는 없음).
- **discipline-houserules-final** (기계 17 ↔ P0 15): 기계 s001은 h1+정본 선언 블록(1~6행)을 한 절로 묶어 P0 «머리말»과 1:1. P0는 «§2·§4는 직속 본문 없이 하위 헤딩만 있어 하위 헤딩을 절로 셈»이라 명문화했고, 기계는 그 h2 헤더 자체를 본문 0의 별도 절(s005-2·s012-4)로 낸다 — 헤더 절 2개가 P0 밖. h3 하위 헤딩 9개(§2 아래 5·§4 아래 4)는 P0 하위 절과 1:1.

요약 규약: **P0 절 40 = 기계 절 46 − 서두 절 4(전문 2·h1 제목 2) − 본문 없는 h2 헤더 절 2.**

## §2 P0 절 전건 대사 표

| P0 절 라벨 | 대응 기계 절 키(범위) | 규약 |
|---|---|---|
| web SKILL: 언제 쓰나 | implementation-django-web-skill/s003 | 1:1 |
| web SKILL: 핵심 운영 원칙 | implementation-django-web-skill/s004 | 1:1 |
| web SKILL: 상세 레퍼런스 | implementation-django-web-skill/s005 | 1:1 |
| web final: 머리말(출처 약어 블록) | implementation-django-web-final/s001 | h1 접힘 |
| web final: §1 책임 범위와 handoff | implementation-django-web-final/s002-1 | 1:1 |
| web final: §2 TemplateView/CBV/FBV 선택 | implementation-django-web-final/s003-2 | 1:1 |
| web final: §3 Context 준비와 표시 값 | implementation-django-web-final/s004-3 | 1:1 |
| web final: §4 Templates·base·includes | implementation-django-web-final/s005-4 | 1:1 |
| web final: §5 Static files·CSS·JS | implementation-django-web-final/s006-5 | 1:1 |
| web final: §6 Web forms·POST flow | implementation-django-web-final/s007-6 | 1:1 |
| web final: §7 HTMX fragment·AJAX | implementation-django-web-final/s008-7 | 1:1 |
| web final: §8 CSRF·XSS·security setting | implementation-django-web-final/s009-8 | 1:1 |
| web final: §9 View auth·permission | implementation-django-web-final/s010-9 | 1:1 |
| web final: §10 Render acceptance checks | implementation-django-web-final/s011-10 | 1:1 |
| web final: §11 서버렌더 에러 처리 | implementation-django-web-final/s012-11 | 1:1 |
| hr SKILL: 무엇이고 왜 | discipline-houserules-skill/s003 | 1:1 |
| hr SKILL: §1 파일트리 결정 순서 | discipline-houserules-skill/s004-1 | 1:1 |
| hr SKILL: §2 충돌 중재 | discipline-houserules-skill/s005-2 | 1:1 |
| hr SKILL: §3 구조 결정이 빠졌다는 신호 | discipline-houserules-skill/s006-3 | 1:1 |
| hr SKILL: §4 타입 어노테이션 | discipline-houserules-skill/s007-4 | 1:1 |
| hr SKILL: §4.1 왜 전부인가 | discipline-houserules-skill/s008-4.1 | 1:1 (h3) |
| hr SKILL: §5 코드 주석·docstring 언어 | discipline-houserules-skill/s009-5 | 1:1 |
| hr SKILL: §6 패키지·의존성 | discipline-houserules-skill/s010-6 | 1:1 (헤더만 — P0도 0규범) |
| hr SKILL: §6.1 부트스트랩·표준 도구셋 | discipline-houserules-skill/s011-6.1 | 1:1 (h3) |
| hr SKILL: §6.2 새 런타임 의존성 버전 선택 | discipline-houserules-skill/s012-6.2 | 1:1 (h3) |
| hr final: 머리말(정본 선언 블록) | discipline-houserules-final/s001 | h1 접힘 |
| hr final: 무엇이고 왜 | discipline-houserules-final/s002 | 1:1 |
| hr final: §0 제1원칙 | discipline-houserules-final/s003-0 | 1:1 |
| hr final: §1 표준 트리 — 140행 | discipline-houserules-final/s004-1 | 1:1 |
| hr final: §2 골격 — BC 직계 일곱뿐 | discipline-houserules-final/s006 | h3 하위 절 1:1 (§2 헤더는 s005-2로 분리) |
| hr final: §2 골격 — 입구 driving_layer | discipline-houserules-final/s007 | h3 하위 절 1:1 |
| hr final: §2 골격 — 만들지 않는 칸 | discipline-houserules-final/s008 | h3 하위 절 1:1 |
| hr final: §2 골격 — migrations 생성물만 | discipline-houserules-final/s009 | h3 하위 절 1:1 |
| hr final: §2 골격 — `<project>/` | discipline-houserules-final/s010 | h3 하위 절 1:1 |
| hr final: §3 명명 | discipline-houserules-final/s011-3 | 1:1 |
| hr final: §4 이관 — 종료 기록 | discipline-houserules-final/s013 | h3 하위 절 1:1 (§4 헤더는 s012-4로 분리) |
| hr final: §4 이관 — brownfield 빚 | discipline-houserules-final/s014 | h3 하위 절 1:1 |
| hr final: §4 이관 — 검사기 가드 계약 | discipline-houserules-final/s015 | h3 하위 절 1:1 |
| hr final: §4 이관 — 규칙 개정 이행 순서 | discipline-houserules-final/s016 | h3 하위 절 1:1 |
| hr final: 배경 | discipline-houserules-final/s017 | 1:1 |

P0 40절 전건 대응 완료.

## §3 잔차

기계에만 있는 절 6건 — 전부 §1 접기 규약이 설명한다:

| 기계 절 | 성격 | 규약 |
|---|---|---|
| implementation-django-web-skill/s001 | YAML frontmatter(전문) | 서두 절 — P0 비계수 |
| implementation-django-web-skill/s002 | h1 제목(본문 0) | 서두 절 — P0 비계수 |
| discipline-houserules-skill/s001 | YAML frontmatter(전문) | 서두 절 — P0 비계수 |
| discipline-houserules-skill/s002 | h1 제목(본문 0) | 서두 절 — P0 비계수 |
| discipline-houserules-final/s005-2 | §2 h2 헤더(직속 본문 0) | 헤더 절 — P0는 하위 헤딩만 절로 셈 |
| discipline-houserules-final/s012-4 | §4 h2 헤더(직속 본문 0) | 헤더 절 — P0는 하위 헤딩만 절로 셈 |

P0에만 있는 절: 0건. **설명 불가 잔차 0.**

## §4 규범 계수 대조

| 문서 | 이번 계수 | P0 | 차이 |
|---|---|---|---|
| implementation-django-web-skill | 22 | 18 | +4 |
| implementation-django-web-final | 129 | 129 | 0 |
| discipline-houserules-skill | 77 | 71 | +6 |
| discipline-houserules-final | 58 | 58 | 0 |
| **합계** | **282** | **276** | **+6** | <!-- adv 중재 정정 2026-08-19: L-D 발견 3 — web 4→2·hr 6→4(주제 설명문 비규범·병렬 위임=1문) -->

차이의 원인은 단일하다: **frontmatter(전문) 절 2건**이 P0 절 목록 밖이라 P0에서 규범 0으로 집계됐고, 이번 센서스는 «(전문) 절의 YAML description은 라우터 트리거 문면 — 애매하면 포함+비고» 규약에 따라 web-skill s001에 4(로드 1+위임 3)·hr-skill s001에 6(로드 1+반드시 사용 1+단일 출처 1+위임 3)을 보수 계상했다. P0가 센 40절의 절 단위 계수는 전 절에서 P0 값과 일치하게 재확인됐다(§11의 24건은 문장 단위 재계수로 검증). h1 제목 절 2건·h2 헤더 절 2건은 규범 0이라 계수 차이에 기여하지 않는다.

부기 — codex 대응: 4파일 모두 codex 쌍둥이 존재(P0 ④축 승계 — houserules 쪽은 `dddjango-discipline-houserules`로 접두 개명). 두 final.md는 codex판과 **byte 동일**, 두 SKILL.md의 차이는 frontmatter `user-invocable: false` 제거와 참조 스킬명의 `dddjango-` 접두 치환뿐 — 전부 플랫폼 표기 치환 이내이므로 46절 전건 SAME. T4 잔차 규모 0 예상.
