# T3 이관 검수표 — architecture-ddd-skill

- 원문: `dddjango/skills/architecture-ddd/SKILL.md` (45행 · 센서스 일치 · 마커 0 — 미이관 문서)
- spec: `workspace/eval/t3/specs/architecture-ddd-skill.spec.json`
- 자기 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/architecture-ddd-skill.spec.json` → **exit 0** (블록 30 · Work 27 · `--write` 미사용 · 수리 루프 0회)
- 배선 준거: `check-*.py` **27종 docstring 선두 전수 실독**(§16 L-F 의무) 후 저작. 요약-복제 관계인 `architecture-ddd-final` 기이관 spec 의 정본 배선을 대조해 같은 규범에 같은 검사기를 달았다. **정본과 갈린 자리는 2건뿐이고 둘 다 §4 에 명시 기록한다**(22행 = 정본보다 넓게 병기 · 25행 = 정본 배선을 의도적으로 승계하지 않음).
- W3 적대 리뷰 수리 반영(2026-08-22): F1(20행 정본 배선 승계) · F3(25행 상충 배선 제거) · F6(분해 규율 우선순위 명문화) · F8(대사 사유 분리 서술) — 상세는 `workspace/eval/t3/reviews/w3-arch-skills-findings.md` «처분» 절.

## 1. census 대사 (절별 규범 수)

| 절 | 헤딩 | 발주서(센서스) | spec | 차 | 판정·사유 |
|---|---|---|---|---|---|
| s001 | (전문) | 2 | 2 | 0 | 일치 — frontmatter `description` 2문(로드 조건 / 경계 위임). `name`·`user-invocable`·종결 `---` 은 런타임·플랫폼 메타라 prose(agent-coder s001 처분과 동형) |
| s003 | 언제 쓰나 | 4 | 4 | 0 | 일치 — 로드 조건 1 + 위임 경계 불릿 3 |
| s004 | 핵심 운영 원칙 | 10 | 19 | **+9** | **⑴ 불릿 단위 센서스의 미해상(과소) + ⑵ 규약 내 하위 문장(독립 종결절) 분해** — 두 사유를 분리해 적는다. ⑴ 센서스는 «불릿 1개 = 규범 1»로 잡았다(10 불릿 = 10) — 불릿 해상도라 §13 «Work 채번 단위 = 문장» 자체를 실현하지 못한 계수다. ⑵ 그 위에 아래 «문장 분해 규율»(독립 종결절)을 적용해 21행 4(문면이 «4가지 규칙»이라 규칙 수를 스스로 선언 — 한 문장 → 4) · 26행 4(선언/수명/제외/소비 BC — 한 문장 → 4 · final §3.7 s026 의 Work 분해와 1:1) · 23·27행 각 2(주어·행위 대상이 갈림) · **25행 2(한 규범 문장 → 2 — ⑴ 이 아니라 순수 ⑵ 사유)**로 나눴다. 나머지 5불릿은 1:1. 분해 결과가 정본 `architecture-ddd-final` 의 Work 분해와 1:1로 맞물리므로 **spec 이 옳다** |
| s005 | 상세 레퍼런스 | 2 | 2 | 0 | 일치 — 32행 라우팅 준거 1 + 45행 한정 독해 1. 표 10행(머리·구분 포함)은 주제→§ 매핑이라 규범 미계수(P0 승계) |
| **계** | | **18** | **27** | **+9** | 불일치 1절 — 사유는 ⑴ 불릿 해상도 과소 + ⑵ 규약 내 하위 문장 분해의 합산 · 과대 산정 판정 0 |

**병합 단계 승계 요청(F8)** — 아래 «독립 종결절» 규율은 §13 «Work 채번 단위 = 문장»의 저작자 확장이다(한 문장 → 복수 Work: 21행 Vernon 4 · 26행 birth-enum 4 · api 23행 에러 프로필 9). 3문서 전건이 정본 final 분해와 1:1로 맞물려 방어되지만 **동결 센서스(REF 539절·3,235문장)를 분모로 쓰는 계수 체계에 무비준으로 확산하면 기대표 드리프트가 누적**된다. 병합 단계에서 ⓐ 이 규율을 T3 공통 규약으로 비준(§13 부기 또는 `T3-EXECUTION.md` 기록)하고 ⓑ 계수 기대표 diff 사유에 **arch-skills 3문서 +23(ddd +9 · db +5 · api +9)** 내역을 승계할 것. 저작 계약 «금지» 조항상 이 에이전트는 `ontology-authoring.md`·`T3-EXECUTION.md` 를 쓰지 않으므로 여기 요청으로만 남긴다.

**문장 분해 규율(이 묶음 3문서 공통 · 명문화)** — §13 «Work 채번 단위가 문장»을 적용할 때 단위는 **독립 종결절**이다. 다음 넷 중 하나면 한 문장 안이라도 분리 채번했다: ⑴ **행위 대상(주어·목적)이 다름** ⑵ **규범 유형(class)이 갈림** ⑶ **문면이 서로 다른 § 또는 규칙 번호를 명시 귀속**(agent-coder 검수표 계수 규율 승계) ⑷ **문면이 스스로 규칙 수를 선언**(«Vernon의 4가지 규칙»). 반대로 다음은 병합했다: 같은 축의 **부정면 재진술**(«…만 담당하고, …두지 않는다»), **근거·결과 서술**(«…하면 …가 된다»), **열거 조각**(콜론 뒤 명사구 나열·체크리스트 항목명), **같은 결정 대상의 기록 의무**(«선택하고 선택 기준을 명시한다»). 이 규율은 3문서에 동일하게 적용했다.

**트리거 충돌의 우선순위(F6 수리 — 3문서 공통 명문화)** — 긍정절 + 부정절이 한 문장에 붙어 ⑵(class 갈림 → 분리)와 «부정면 재진술»(→ 병합)이 동시에 걸릴 때는 **긍정절의 배타 표지(«만»·«한정»·«…뿐») 유무**로 가른다.

- 배타 표지가 **있으면 병합**: 부정절의 금지 대상이 긍정절의 «만»에 이미 함수적으로 배제돼 독자 위반 표면을 만들지 못한다(부정면 재진술).
  - 실물 — ddd 24행 «응용 서비스는 흐름 제어와 트랜잭션 관리**만** 담당하고, 비즈니스 로직을 두지 않는다»: «만»이 이미 비즈니스 로직을 배제하므로 뒷절은 앞절의 부정면 재진술 → **1 Work**.
- 배타 표지가 **없으면 ⑵ 우선 분리**: 부정절이 긍정절로 도출되지 않는 독자 금지 대상·독자 위반 표면을 갖는다.
  - 실물 — api 22행 «URL은 명사·복수형·케밥케이스 리소스로 설계하고 동사 행위를 URL에 포함하지 않는다»: 배타 표지가 없고, `/orders/{id}/cancel` 처럼 세 형식 속성(명사·복수·케밥)을 모두 지키면서 동사를 포함하는 URL 이 성립하므로 부정절이 독자 위반 표면을 갖는다 → **2 Work**.
- 인용 판례와의 정합 — api 정본 `architecture-api-final` s013-3.1/b2 는 «명사 사용 (동사 아님)»을 1 Work 로 접었으나 그것은 **좋은 예/나쁜 예 대조 표의 한 행**이고 괄호는 그 대조의 주석이다(독립 종결절 0). SKILL 22행은 «…포함하지 않는다»라는 독립 종결절이라 판형이 다르다 — 판례 이탈이 아니라 문면 형태 차이다.

이 문서에서 병합한 자리 3건(과대 방지 실증): ⑴ 19행 둘째 문장 «전략 없이 전술 패턴만 적용하면 …결과가 된다» = 근거 서술 → 미채번. ⑵ 24행 «흐름 제어와 트랜잭션 관리만 담당하고, 비즈니스 로직을 두지 않는다» = 같은 축의 부정면 재진술 → 1 Work. ⑶ 28행 «필요가 확인된 시점에 선택하고, 패턴 선택 절차를 통해 … 결정한다» = 같은 결정 대상의 두 면 → 1 Work.

## 2. 배선 근거 표 (전 규범 27건)

> `enforcedBy` 는 «담당 검사기의 문면·docstring 근거가 실재하는가»로만 달았고, 없으면 §16 위임 기본값 표를 따랐다(기본값 이탈·기본값 도피 양쪽 다 근거 병기). 근거 기호 ①문면 역할명 ②docstring § 인용 ③P0 커버 ④registry #N.
>
> **표는 spec JSON 에서 기계 생성한다**(라벨·class·enforcedBy·delegatedTo·basis 전 열이 spec 실물의 사본 — agent-coder 검수표 R2-3 재발 방지 조치 승계). spec 을 고치면 이 표를 다시 생성한다.

| # | 절/블록(행) | Work label | class | enforcedBy | delegatedTo | 4원 근거 |
|---|---|---|---|---|---|---|
| 1 | s001/b2 (3) | 로드 조건 — 도메인 언어·비즈니스 정책·애그리거트/컨텍스트 경계·도메인 이벤트 채택 결정 시 선행 로드 | Obligation | — | `command-dddjango`·`agent-design-review-ddd` | ①문면 «…결정할 때 먼저 로드한다» + 센서스 E01 s001 비고 «frontmatter description = 라우터 트리거 문면» · ②check-*.py 27종 docstring 선두 전수 실독 — 스킬 로드·라우팅 술어 0(검사 공백) · §16 위임 기본값 표(architecture-ddd→agent-design-review-ddd) + 스킬 배분 소유는 Coordinator(agent-coder s004 «작업 축별 스킬 선택 사용»→command-dddjango 선례) 병기 |
| 2 | s001/b2 (3) | 경계 위임 — Django 구현 코드·outbox/트랜잭션 설계·API 계약의 타 스킬 이양 | Obligation | — | `agent-discipline-reviewer`·`agent-design-review-db`·`agent-design-review-api` | ①문면이 implementation-django·architecture-db·architecture-api 를 수임처로 직접 지목 — §16 표의 각 수임 문서군 기본값 병기(implementation-*→discipline-reviewer · architecture-db→design-review-db · architecture-api→design-review-api). ninja s022-6.1 «상태 코드 의미의 architecture-api 위임»→agent-design-review-api 판례 준거 · ②27종 docstring 에 스킬 간 위임 술어 0 |
| 3 | s003/b1 (10–12) | 로드 조건 — 도메인 언어·정책/상태 전이·애그리거트/BC 경계·도메인 이벤트 채택 불명확 시 로드 | Obligation | — | `command-dddjango`·`agent-design-review-ddd` | ①문면 «…불명확할 때 로드한다» — s001 description 의 정본 진술(사본 = s001/b2) · ②27종 docstring 전수 — 스킬 로드 술어 0 · §16 기본값(architecture-ddd→design-review-ddd) + 스킬 배분 Coordinator 병기(s001/b2 와 동일 처분) |
| 4 | s003/b2 (13) | Django ORM·서비스 레이어·outbox 구현의 implementation-django 위임 | Obligation | — | `agent-discipline-reviewer` | ①문면이 화살표로 수임처를 직접 지목 · §16 표 implementation-*→agent-discipline-reviewer(기본값 일치·이탈 아님) · ②27종 docstring 에 스킬 경계 술어 0(implementation-python-final s001 «클린코드 위임»→discipline-reviewer 판례 동형) |
| 5 | s003/b3 (14) | outbox 전달 보장·트랜잭션 격리·Risky Write 설계의 architecture-db 위임 | Obligation | — | `agent-design-review-db` | ①문면이 architecture-db 를 수임처로 직접 지목 · §16 표 architecture-db→agent-design-review-db · ②27종 전수 — 스킬 간 위임 술어 0(db 실체 규범의 집행 배선은 수임 문서 architecture-db-final s043-9.6·s044-9.7 이 진다) |
| 6 | s003/b4 (15–16) | REST API 계약·엔드포인트 설계의 architecture-api 위임 | Obligation | — | `agent-design-review-api` | ①문면이 architecture-api 를 수임처로 직접 지목 · §16 표 architecture-api→agent-design-review-api · ②27종 전수 — 위임 술어 0 |
| 7 | s004/b1 (18–19) | 전략 설계 우선 — 전술 패턴에 앞선 핵심 도메인 식별·BC 설계·컨텍스트 맵 순서 | Override | — | `agent-design-review-ddd` | ①문면 «전술 패턴보다 먼저다» = 다른 규범(전술 패턴 적용)을 눌러 이기는 우선 규칙 → final s051-8/b8 «의사결정 6 — 전략 설계 우선» Override 와 동일 축(L-E 판례) · ②27종 docstring 에 설계 순서 술어 0 · §16 기본값(설계 시점→design-review-ddd). 둘째 문장 «전략 없이 …결과가 된다»는 근거 서술이라 미채번 |
| 8 | s004/b2 (20) | 유비쿼터스 언어의 BC 내 한정 유효 — 컨텍스트가 다르면 다른 언어 | Obligation | `check-business-vocabulary.py` | `agent-design-review-ddd` | ②check-business-vocabulary 격리 절 #47(capability 계약의 업무 어휘 0)·#52(BC 이름 0 — «BC 하나를 지웠을 때 바뀌면 안 올린다»)·#616/#617·#587·#426·#562 가 «업무 어휘는 BC 밖 공용 자리(framework/·pure·test)로 나가지 않는다»는 BC 국지성의 한 면을 집행 — 정본 architecture-ddd-final s009-2.3/b3 W3(«유효 범위는 BC 경계 안» · 같은 basis #47·#52) 배선을 승계한다(§16 «역도 성립» — 담당 docstring 근거가 있는데 기본값 도피는 오배선). 커버 범위는 **공용 자리로의 어휘·BC 이름 유출 1축 한정**이고, 문면 후반 «동일 개념도 컨텍스트가 다르면 다른 언어» = 컨텍스트 간 의미 분기 판정은 검사 공백(check-context-isolation 은 분리 «이후» import 격리라 시점이 달라 겹치지 않음 — final s010-2.4/b2 basis 의 비중첩 논거) → §16 기본값 병기 |
| 9 | s004/b3 (21) | Vernon 규칙 1 — 진짜 불변식만 일관성 경계 안에서 보호 | Obligation | `check-domain-model.py` | `agent-design-review-ddd` | ②check-domain-model #257 «상태 변경은 루트를 지난다»가 불변식 보호의 결정적 축 · 경계 «설정» 판정은 설계 시점(final s019/b1 배선 준거) |
| 10 | s004/b3 (21) | Vernon 규칙 2 — 최소 크기 애그리거트 설계 | Obligation | — | `agent-design-review-ddd` | ②27종 전수 — 크기 판정 술어 0(check-domain-model #547 «루트 비대»는 ⓓ 후보라 exit 불산입 = 집행 아님) · §16 기본값(final s019/b3 동형) |
| 11 | s004/b3 (21) | Vernon 규칙 3 — 타 애그리거트 ID 참조 한정(영속성/ORM 포함 · BC 경계 ORM FK 금지 · 같은 BC FK 허용) | Obligation | `check-domain-model.py`·`check-db-table.py` | `agent-design-review-ddd` | ②check-domain-model #253(<A>/** 는 <B>/ 루트 모듈만 import)·#258(entity 직접 참조 금지) + check-db-table #631 «타 BC 모델을 FK·O2O·M2M 으로 참조 금지(문자열 참조 포함)» 문면 축자 일치 · 같은 BC 허용면 판정은 설계(final s019/b5·b7 배선 종합) |
| 12 | s004/b3 (21) | Vernon 규칙 4 — 경계 밖 일관성은 결과적 일관성으로 달성 | Obligation | `check-transaction-boundary.py` | `agent-design-review-ddd` | ②check-transaction-boundary docstring 선두 «「한 트랜잭션 = 애그리거트 하나」(D50) 축의 결정적 백스톱»(#195·#599)이 경계 «안쪽»을 집행 · 결과적 일관성 전환 판정은 설계(final s019/b8 준거) |
| 13 | s004/b4 (22) | 엔티티의 애그리거트 일부 한정 사용 — 독립 생성·접근 금지 | Obligation | `check-domain-model.py` | `agent-design-review-ddd` | ②check-domain-model #258 «entity/ 직접 참조 금지 — 애그리거트 밖에서 붙잡는 것은 루트뿐»·#252(1차에 entity/ 금지)가 문면과 축자 대응 → §16 «역도 성립»(담당 검사기 docstring 근거가 있는데 기본값 도피 금지) 적용. final s051-8/b3 는 «의사결정 표» 행이라 설계 판정 단독이었으나 이 불릿은 구현 시점 운영 원칙이라 집행 축 병기 · 설계 판정은 기본값 유지 |
| 14 | s004/b5 (23) | 도메인 서비스의 다-애그리거트 무상태 로직 한정 사용 | Obligation | `check-domain-model.py` | `agent-design-review-ddd` | ②check-domain-model #300(<aggregate>/domain_service/ 금지 — BC 레벨 한 칸뿐)·#302(무상태 — __init__ self 상태·모듈 가변 전역 금지)·#310(무상태 규칙 하나=파일 하나) · «여러 애그리거트에 걸치는가» 해당성 판정은 설계(final s022-3.5/b2 준거) |
| 15 | s004/b5 (23) | 애그리거트의 도메인 서비스 직접 인지 금지 | Prohibition | `check-domain-model.py` | `agent-design-review-ddd` | ②check-domain-model #8(domain_layer 밖으로 나가는 import 0)·#303(domain_service import 허용 = 루트·값 객체·예외·형제 서비스)·#301(루트 인자 축) — final s022-3.5/b4 «애그리거트는 외부 의존성을 받지 않는다» 와 같은 축 |
| 16 | s004/b6 (24) | 응용 서비스의 흐름 제어·트랜잭션 관리 한정 — 비즈니스 로직 금지 | Obligation | `check-transaction-boundary.py`·`check-usecase-dto-placement.py` | `agent-discipline-reviewer` | ②check-transaction-boundary #195(루트 메서드 호출을 거치지 않는 쓰기 금지)·#197·#200 + check-usecase-dto-placement #194(유스케이스 안 업무 규칙 — ⓓ 후보) · final s023-3.6/b2 배선과 동일. 긍정면(담당 한정)과 부정면(로직 금지)은 같은 축의 재진술이라 1 Work |
| 17 | s004/b7 (25) | 도메인 이벤트의 애그리거트 수집 | Obligation | `check-domain-model.py` | — | ②check-domain-model #272 «루트는 이벤트를 기록만 한다 — publish/dispatch 호출 금지»·#542(사실은 애그리거트가 만든다)·#543(창구는 pull_events 하나) 문면 일치(final s024-3.7/b3 첫 Work 배선 준거) |
| 18 | s004/b7 (25) | 디스패치 타이밍의 명시 — UoW 커밋 직전(동일 트랜잭션 부수효과) 또는 직후(외부 통합) | Obligation | — | `agent-design-review-ddd` | ②27종 docstring 전수 — «타이밍을 명시한다»(설계 기록) 술어 0. check-usecase-dto-placement #541(커밋 «전» 발행 금지 — `.publish(` 직접 호출은 uow.after_commit 밖)·#539·#540 과 check-transaction-boundary #200(커밋 뒤 부작용은 after_commit)은 정본 final s024-3.7/b3 W2(«디스패치는 uow.after_commit 한 경로 — 커밋 직전은 배경 이론» **Override**)를 집행하는 술어다. 이 Work 의 문면은 «직전 또는 직후» 두 가지를 남기므로 그 검사기를 달면 기계가 문면이 허용하는 «직전» 가지를 위반으로 물게 된다 — 상충 규범의 배선 복사(§16 오배선)라 enforcedBy 를 비우고 §16 기본값(설계 시점→design-review-ddd) 단독으로 둔다. 문면 차이는 §3 유예 #12 에 «부분 재진술이냐 불일치냐» 판정 재료로 남긴다 |
| 19 | s004/b8 (26) | 발행 봉투 discriminator 의 1종째 domain_layer StrEnum 선언(birth-enum) | Obligation | `check-domain-model.py` | `agent-design-review-ddd` | ②check-domain-model #8(domain 소유)·#269(<A>/event/ 는 BC 안에서 읽힘)가 슬롯·소유 축을 집행 · «1종째 승격» 판정은 설계 시점(final s026/b1 배선 준거) |
| 20 | s004/b8 (26) | discriminator enum 멤버의 append-only 유지 | Obligation | — | `agent-discipline-reviewer` | ②27종 docstring 전수 실독 — enum 이력 대조(«추가만인가») 진단 부재(검사 공백) · §16 기본값의 구현 시점 축(final s026/b2 «수명 — 멤버는 추가만» 배선과 동일) |
| 21 | s004/b8 (26) | 버전 태그(payload_schema_version)의 리터럴 동결 — birth-enum 비대상 | Exception | — | `agent-discipline-reviewer` | 짝 조항(비대상 선언)이라 Exception — final s026/b2 «제외 — payload_schema_version 등 버전 태그는 리터럴 동결 유지» Exception 과 동형 · 검사 공백 |
| 22 | s004/b8 (26) | 소비 BC 의 발행 enum 직접 import 금지 | Prohibition | `check-context-isolation.py` | — | ②check-context-isolation 타 BC 절 #12 «부를 수 있는 것은 OHS·published_event 둘»·#13 — final s026/b2 «발행 enum의 타 BC 직접 import 금지» 배선과 동일 |
| 23 | s004/b9 (27) | 아키텍처 기본형 — 4계층+DIP | Obligation | `check-layer-skeleton.py`·`check-context-isolation.py` | `agent-design-review-ddd` | ②check-layer-skeleton #486~#490(4계층 골격 존재·폐쇄) + check-context-isolation 방향 절 #1·#2·#9·#251·#322 · final s051-8/b10(의사결정 8 — check-layer-skeleton)·s036-5.1/b3 배선 준거 |
| 24 | s004/b9 (27) | 도메인 영역 인터페이스 선언·인프라 구현 — 도메인의 인프라 직접 인지 금지 | Obligation | `check-port-adapter-pairing.py`·`check-domain-model.py` | — | ②check-port-adapter-pairing #457(선언은 application_layer/port/ 아래뿐)·#460(구현은 driven_layer/adapter/)·#351(선언↔구현 1:1) + check-domain-model #8(domain_layer 밖으로 나가는 import 0) · final s036-5.1/b3 «DIP»·s037-5.2/b2 배선 준거 |
| 25 | s004/b10 (28–29) | 구현 패턴의 필요 확인 시점 선택 — 패턴 선택 절차 경유(Risky Write 라우팅 포함) 결정 | Obligation | — | `agent-design-review-ddd`·`agent-design-review-db` | ②27종 전수 — 패턴 채택 «시점·절차» 술어 0(check-event-publish #564 saga/·process_manager/ 는 ⓓ 후보라 exit 불산입) · §16 기본값(설계 시점→design-review-ddd) + 문면의 «Risky Write 라우팅»은 architecture-db §9.6 소유 어휘라 db lens 병기(final db s043-9.6/b8 «Idempotency-Key 계약을 architecture-api 와 정합»→design-review-api 병기 판례와 동형). «선택 시점»과 «절차 경유 결정»은 같은 결정 대상의 두 면이라 1 Work |
| 26 | s005/b1 (31–33) | 주제별 라우팅 준거 — references/final.md 해당 절 준수 | Obligation | — | `command-dddjango`·`agent-design-review-ddd` | ①문면 «해당 절을 따른다» — 준거 문서 로드·인용 축 · ②27종 docstring 에 문서 로드·인용 술어 0(검사 공백) · §16 기본값 + 로드 절차 소유 Coordinator 병기(agent-design-architect s005 «로드한 스킬 절 인용에 의한 판단 정당화»→command-dddjango 선례) |
| 27 | s005/b12 (45) | 필요 항목 한정 독해 — 전체 로드 불필요 | Exception | — | `command-dddjango`·`agent-design-review-ddd` | ①문면 괄호 «(전체 로드 불필요)» = 전량 로드 의무의 면제 조문이라 Exception(agent-design-review-api s003 «로드한 스킬 본문·references 참조는 제한 밖» Exception 판례) · ②27종 docstring 에 로드 범위 술어 0 · §16 기본값 + 로드 절차 Coordinator 병기 |

## 3. 재진술

### 3.1 같은 문서 안 쌍 — spec `restates` 에 반영(유예 아님)

| 사본 블록 | 정본 블록 | 판정 |
|---|---|---|
| s001/b2 (3행 `description`) | s003/b1(10–12) · b2(13) · b3(14) · b4(15–16) | 센서스는 s001↔s003 을 «상호 재진술»로 적었으나, §15 «정본 1곳만 Work 승격 + 사본 블록에 `djr:restates`» 규약을 방향 규칙으로 읽어 **사본(frontmatter 요약) → 정본(본문 절)** 한 방향만 걸었다(역방향까지 걸면 사이클). 축자 사본이 아니라 **부분 재진술**이라 양쪽 Work 는 유지했다(discipline-tdd s012-3.4 «Work 유지 + restates» 판례). description 의 위임처 3종이 s003 불릿 3개와 정확히 대응해 4블록 전부 연결 |

### 3.2 교차 문서 유예 (T3-EXECUTION «교차 문서 쌍 전량 유예» 결정 — 소급 패스 재료)

좌표는 **마커 제거본(센서스) 기준**이다(`architecture-ddd-final` 은 기이관 문서라 현재 파일에는 마커 38행이 삽입돼 있다 — 아래 행 번호는 마커 제거본 = 센서스 좌표).

| # | 사본(이 문서) | Work | 상대 정본(센서스 좌표) | 비고 |
|---|---|---|---|---|
| 1 | s004/b1 (19) | 전략 설계 우선 | `architecture-ddd-final` s051-8/b8 (2067 — 의사결정 6) | §9 요약표에는 대응 행 없음 |
| 2 | s004/b2 (20) | 유비쿼터스 언어의 BC 내 한정 유효 | 동 s009-2.3/b3 (175–179 «유효 범위는 BC 경계 안») | §9 사본 s052-9/b4(2078)도 같은 축 — 3중 사본 |
| 3 | s004/b3 (21) | Vernon 규칙 1 | 동 s019/b1 (645–647) | §9 사본 s052-9/b9(2083) |
| 4 | s004/b3 (21) | Vernon 규칙 2 | 동 s019/b3 (650–651) | |
| 5 | s004/b3 (21) | Vernon 규칙 3 | 동 s019/b5 (654–655) + b7 (658–659 — BC 경계 FK 금지) | 괄호 안 ORM 조항이 b7 에 대응 |
| 6 | s004/b3 (21) | Vernon 규칙 4 | 동 s019/b8 (660–661) | |
| 7 | s004/b4 (22) | 엔티티의 애그리거트 일부 한정 사용 | 동 s051-8/b3 (2062 — 의사결정 1) · §3.2 본문 s017-3.2 | §9 사본 s052-9/b8(2082)이 두 곳을 restates |
| 8 | s004/b5 (23) | 도메인 서비스의 다-애그리거트 무상태 한정 | 동 s022-3.5/b2 (903–904) | §9 사본 s052-9/b11(2085) |
| 9 | s004/b5 (23) | 애그리거트의 도메인 서비스 직접 인지 금지 | 동 s051-8/b5 (2064 — 의사결정 3) + s022-3.5/b4 (909–910) | |
| 10 | s004/b6 (24) | 응용 서비스의 흐름 제어·트랜잭션 관리 한정 | 동 s023-3.6/b2 (998–999) | §9 사본 s052-9/b12(2086) |
| 11 | s004/b7 (25) | 도메인 이벤트의 애그리거트 수집 | 동 s024-3.7/b3 (1099–1103 W1) | §9 사본 s052-9/b13(2087) |
| 12 | s004/b7 (25) | 디스패치 타이밍의 명시 | 동 s024-3.7/b3 (1099–1103 W2) + s051-8/b9 (2068 — 의사결정 7) | **문면 차이 주의** — final W2 는 «uow.after_commit 한 경로»를 Override 로 못박았고 SKILL 은 «커밋 직전 또는 직후» 두 선택지를 남긴다. 소급 패스에서 «부분 재진술이냐 불일치냐»를 판정해야 한다. **배선도 갈렸다**: final W2 는 E:[usecase-dto-placement, transaction-boundary], SKILL W2 는 E 0·D:design-review-ddd — 검사기가 «직전» 가지를 위반으로 물기 때문이다(§4 «정본과 갈린 자리» 2 항) |
| 13 | s004/b8 (26) | birth-enum 선언 | 동 s026/b1 (1201–1203) | |
| 14 | s004/b8 (26) | append-only 유지 | 동 s026/b2 (1204–1209 — «수명 — 멤버는 추가만») | |
| 15 | s004/b8 (26) | 버전 태그 리터럴 동결 | 동 s026/b2 (1204–1209 — «제외 — 버전 태그» Exception) | |
| 16 | s004/b8 (26) | 소비 BC 의 발행 enum import 금지 | 동 s026/b2 (1204–1209 — «발행 enum의 타 BC 직접 import 금지») | |
| 17 | s004/b9 (27) | 4계층+DIP 기본형 | 동 s036-5.1/b3 (1438–1442) + s051-8/b10 (2069 — 의사결정 8) | §9 사본 s052-9/b14(2088) |
| 18 | s004/b9 (27) | 도메인 인터페이스 선언·인프라 구현 | 동 s037-5.2/b2 (1447–1448) | |
| 19 | s004/b10 (28–29) | 구현 패턴의 시점·절차 결정 | 동 s049-6.8/b2 (2000–2004 — 절차 1~4) + b4 (2007–2008 — Risky Write 이양) | |

**유예 19건.** 전부 상대가 이미 그래프 안(파일럿·웨이브 1 기이관)이라 기술적으로는 즉시 연결이 가능하나, `T3-EXECUTION.md` 의 «교차 문서 쌍 전량 유예» 결정에 따라 유예했다.

비-재진술로 판정해 목록에서 뺀 것:

- s001/b2·s003/b2~b4 의 «→ `implementation-django` / `architecture-db` / `architecture-api`» 는 **관할 지시(준거 포인터)**이지 규범 사본이 아니다 — 이 문서의 규범은 «그 축은 저 스킬로 넘겨라»라는 별개 의무다(agent-coder 검수표 «값 소유 인용은 준거 지시» 판형 승계).
- s005 의 라우팅 표 행·두 규범(«해당 절을 따른다»·«필요한 항목만 읽는다»)은 문서 소비 절차라 상대 사본이 없다.

## 4. 경계 판단 메모

- **블록 경계 규약**: 블록 = 내용 행 + 후행 빈 줄(§13 «블록 간 구분자는 선행 블록의 후행 스팬에 귀속»). 절 첫 블록만 헤딩 직후 빈 줄을 선두에 흡수(§13 유일 예외 — s003 b1 은 10행 빈 줄부터, s004 b1 은 18행 빈 줄부터, s005 b1 은 31행 빈 줄부터). 도구가 연속·비중첩·전량 커버와 «헤딩 + 블록 = 절 스팬» byte 등가를 단언했고 **exit 0**(수리 루프 0회).
- **s001 헤딩 = 1행 `---`**: 무앵커 선두 절이라 `djr:headingSnapshot` 이 frontmatter 개시 구분자다(도구가 `line_start` 행을 헤딩으로 잘라 간다). 웨이브 2 판례대로 **frontmatter 는 code 가 아니라 행 단위 prose/norm** 으로 분해했다 — `---` 은 펜스가 아니므로 §13 «code = 여는 펜스~닫는 펜스 전체 라인» 에 해당하지 않는다. 종결 `---`(5행)은 후행 빈 줄(6행)과 한 prose 블록이다.
- **kind 판정**: 이 문서에 코드 펜스 0 · 체크박스 0 이라 norm/prose/table-row 3종만 썼다. 백틱 인라인(`implementation-django` 등)은 펜스가 아니라 kind 에 영향이 없다.
- **표 처리**: s005 의 주제→§ 표는 머리행·구분행 포함 행 단위 `table-row`(§13). 데이터 8행은 «어느 주제가 어느 §인가»라는 매핑이라 규범 미계수(발주서·P0 승계). 마지막 데이터 행이 후행 빈 줄(44)을 물어 [43,44]다.
- **class 판정**: `Override` 1곳(19행 «전술 패턴보다 먼저다» — 다른 규범을 눌러 이기는 우선 규칙 · final 의사결정 6 과 동형). `Exception` 2곳(26행 «버전 태그는 리터럴 동결» = birth-enum 비대상 선언 · 45행 «(전체 로드 불필요)» = 전량 로드 의무의 면제). `Prohibition` 2곳(23행 애그리거트의 서비스 인지 금지 · 26행 소비 BC import 금지) — 나머지는 Obligation.
- **기본값 이탈(enforcedBy 병기)의 근거 계열 2종**: ⑴ **docstring 축자 대응** — 22행(#258 «entity/ 직접 참조 금지 — 애그리거트 밖에서 붙잡는 것은 루트뿐»), 21행 규칙 3(#631 «타 BC 모델을 FK·O2O·M2M 참조 금지»), 26행 소비 BC(#12 «부를 수 있는 것은 OHS·published_event 둘»). ⑵ **정본 문서의 기이관 배선 대조** — 20·21·23·24·25행(수집 Work)·27행은 `architecture-ddd-final` spec 이 같은 규범에 이미 단 검사기를 그대로 승계했다. **22행은 정본과 갈린 자리**다: final s051-8/b3(의사결정 표 행)은 설계 판정 단독이었으나, SKILL 의 같은 문장은 «독립적으로 생성·접근하지 않는다»라는 **구현 시점 형태 규범**이고 #258 이 그 형태를 결정적으로 문다 — §16 «역도 성립»(담당 근거가 있는데 기본값 도피 = 오배선)에 따라 집행 축을 병기했다.
- **정본과 갈린 자리 — 전수 2건(F1·F3 수리 후 확정)**:
  1. **22행(정본보다 넓게 병기)** — 위 ⑵ 항 참조. final 은 설계 판정 단독, SKILL 은 E 병기.
  2. **25행 W2 «디스패치 타이밍의 명시»(정본 배선을 의도적으로 승계하지 않음)** — 정본 final s024-3.7/b3 W2 는 **class 가 Override**(«uow.after_commit 한 경로 — 커밋 직전은 배경 이론»)이고 그래서 `check-usecase-dto-placement`·`check-transaction-boundary` 를 진다. SKILL 25행은 같은 축이지만 **«커밋 직전 또는 직후» 두 선택지를 남기는 Obligation** 이라 규범 내용이 정본보다 넓다. #541 은 «커밋 «전» 발행 금지», #200 은 after_commit 강제이므로 그 검사기를 이 Work 에 달면 **문면이 허용하는 «직전» 가지를 기계가 위반으로 무는 오배선**이 된다(집행이 아니라 절반 부정). 게다가 이 Work 의 자기 축은 «타이밍을 명시한다»(설계 기록)라 27종 어디에도 술어가 없다. 그래서 정본 배선을 승계하지 않고 기본값 단독으로 내렸다. 두 문면의 관계(부분 재진술 vs 불일치)는 §3 유예 #12 가 소급 패스 재료로 진다.
- **오배선 회피 기록 3건**(표면상 검사기가 있어 보이나 기본값을 유지한 자리):
  1. **25행 W2 디스패치 타이밍** — 위 «정본과 갈린 자리» 2 항. 상충 규범의 배선을 복사하지 않았다(F3 수리 · 2026-08-22). *(수리 전 이 자리에는 «20행 유비쿼터스 언어»가 있었다 — F1 판정에 따라 §16 «역도 성립» 적용으로 병기 전환했고, 회피 기록에서 이탈 기록으로 옮겼다.)*
  2. **21행 규칙 2(최소 크기)** — `check-domain-model` #547(루트 비대·여러 area 공유)은 **ⓓ 후보 채널**이라 exit 에 불산입한다. 후보 발화는 «집행»이 아니므로 enforcedBy 를 달지 않았다.
  3. **28행 패턴 선택** — `check-event-publish` #564(«진행표 금지» — saga/·process_manager/ 폴더)는 Saga 채택의 인접 신호지만 ⓓ 후보이고, 규범의 자기 축(«언제·어떤 절차로 고르는가»)에는 어느 검사기 술어도 닿지 않는다. 대신 문면의 «Risky Write 라우팅»이 `architecture-db` §9.6 소유 어휘라 db lens 를 병기했다(final db s043-9.6/b8 의 «architecture-api 와 정합»→design-review-api 병기 판례와 동형).
- **로드·라우팅 규범의 소유**: s001·s003·s005 의 로드 조건·라우팅 준거에는 문서군 기본값(`agent-design-review-ddd`)과 함께 `command-dddjango` 를 병기했다 — 스킬 로딩·배분은 Coordinator 호출 계약이라는 문면 근거가 있고(agent-coder s004 «작업 축별 스킬 선택 사용»→`command-dddjango`, agent-design-architect s005 «로드한 스킬 절 인용»→`command-dddjango` 선례), 27종 docstring 에는 스킬 로드 술어가 0이다.
- **위임 경계 규범의 소유**: «X → `skill-y`» 불릿은 **수임 문서군의 기본 Agent** 로 배선했다(implementation-*→`agent-discipline-reviewer` · architecture-db→`agent-design-review-db` · architecture-api→`agent-design-review-api`). ninja s022-6.1 «상태 코드 의미의 architecture-api 위임»→`agent-design-review-api`, discipline-tdd s038-8 «implementation-test 위임»→`agent-discipline-reviewer` 판례가 같은 판형이다.
