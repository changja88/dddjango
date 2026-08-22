# T3 이관 검수표 — implementation-django-skill

- 원문: `dddjango/skills/implementation-django/SKILL.md` (53행 · 센서스 일치 · 마커 0 — 미이관 문서)
- spec: `workspace/eval/t3/specs/implementation-django-skill.spec.json`
- 자기 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/implementation-django-skill.spec.json` → **exit 0** (블록 37 · Work 25 · `--write` 미사용)
- 배선 전 `dddjango/scripts/check-*.py` **27종 docstring 선두 전수 실독** 완료(§16 L-F 의무 — 묶음 «django-skills» 3문서 공통 1회).

## 1. census 대사 (절별 규범 수)

| 절 | 헤딩 | 발주서(센서스) | spec | 차 | 판정·사유 |
|---|---|---|---|---|---|
| s001 | (전문) | 2 | 2 | 0 | 일치 — frontmatter description 3행이 «로드 조건 1 + 병렬 위임 1». 주제 나열(«Django 코어 구현 지식 — 모델·ORM…»)은 서술이라 비계수 · `name:`·`user-invocable:`·`---`는 prose |
| s003 | 언제 쓰나 | 7 | 7 | 0 | 일치 — 로드 조건 1 + 경계 불릿 6. 18행(«Python 관용구 → …, 클린코드 원칙 → …»)은 두 라우팅이지만 한 축(인접 소유 스킬 이관)이라 1 Work — ninja-final s005-1.2 b1이 괄호 병기 상대를 1 Work로 처분한 판형과 같다 |
| s004 | 핵심 운영 원칙 | 12 | 14 | **+2** | **센서스 과소** — 센서스는 «문장» 계수(8불릿 = 12문장)라 한 문장 안 다규범이 접힌다. 26행 4(Enum 파생 / TextChoices 한정 / `.value` 평탄화 / 심볼 소비) · 29행 2(환경 분리 / 직접 접근) · 24행 2 · 22행 2. 근거(정본 분리 채번 정합): 같은 규범들이 implementation-django-final에서 s015-2.5 b2·b4·b5(4 Work), s021-3.3+s022-3.4(2 Work), s078-16.4 b1+b7(2 Work), s024-4.1+architecture-ddd §3.2(2 Work)로 **이미 나뉘어 채번돼 있고**, 이 4자리에서 유형(Obligation/Exception)이나 소유(enforcedBy/delegatedTo)가 갈리므로 병합하면 유형·소유가 손실된다 |
| s005 | 상세 레퍼런스 | 2 | 2 | 0 | 일치 — 33행(준거)·53행(한정 로드) 2문. 주제→§ 라우팅 표 15행은 목차라 비계수(P0 규약 승계) |
| **계** | | **23** | **25** | **+2** | 불일치 1절 = «센서스 과소» 판정 — 과대 산정 판정 0 |

> **W3 L3 수리(2026-08-22)**: 초판 사유에 있던 «압축 사본의 해상도가 정본보다 낮을 수 없다»는 계약 문면에 없는 전제라 삭제했다. +2 판정은 위 «정본 분리 채번 정합»(+ 병합 시 유형·소유 손실)만으로 독립 지지된다. §13 «문장 해상도» 조항 대비 처분의 상세 논급은 같은 묶음 `implementation-django-ninja-skill.md` §1 하위 절에 1회 기록했다(3문서 공통 근거).

계수 규율(과대 방지): 한 문장 안이라도 ⑴ 행위 대상이 다르거나 ⑵ 규범 유형 축이 갈릴 때만 분리 채번했다(agent-coder 검수표의 «독립 종결절 + ⑴⑵» 판별자 승계). §N·타 스킬 좌표만 가리키는 **소유 좌표 안내는 비계수**로 통일했다 — 25행 괄호(«채택 기준 `architecture-ddd` §3.7, 전달 보장 `architecture-db` §9.7»)와 s005 표 15행이 같은 규율로 빠졌다. 반대로 22행의 «표준 4계층은 `domain_layer` 애그리거트 소유(`architecture-ddd` §3.2)»는 §3.2가 좌표일 뿐 문장 자체가 배치 규범을 진술하므로 계수했다.

## 2. 배선 근거 표 (전 규범 25건)

> 표는 spec JSON에서 기계 생성(라벨·class·enforcedBy·delegatedTo·basis 전 열이 spec 실물의 사본) — 수리 시 재생성한다. 근거 기호 ①문면 역할명 ②검사기 docstring 인용 ③P0 커버 ④registry #N.
> 기본값: §16 위임 기본값 표 «implementation-* → `agent-discipline-reviewer`». 이탈 병기 — 스킬 로드·부착 결정 축은 `command-dddjango`(절차 층), 계약 축은 `agent-design-review-api`, 도메인 설계 축은 `agent-design-review-ddd`, DB 축은 `agent-design-review-db`.

| # | 절/블록(행) | Work label | class | enforcedBy | delegatedTo | 4원 근거 |
|---|---|---|---|---|---|---|
| 1 | s001/b2 (3) | Django 코어 코드 작성·리팩터링 시 이 스킬 선로드 | Obligation | — | `agent-discipline-reviewer`·`command-dddjango` | ①문면 «…먼저 로드한다» — frontmatter description 은 스킬 로드 트리거(행 단위 prose/norm 판정) · ②check-*.py 27종 docstring 전수 실독: 스킬 로드·라우팅 술어 0(검사 공백) · §16 기본값(implementation-* → discipline-reviewer)에 절차 층 Coordinator 병기 — 스킬 부착 결정은 파이프라인 소유 |
| 2 | s001/b2 (3) | 표현계층·JSON API·신규 REST 계약의 소유 스킬 위임 | Obligation | — | `agent-discipline-reviewer`·`agent-design-review-api` | ①문면 «…로 위임» 3건 · ②27종 전수 — 문서 간 위임 경계 술어 0 · §16 문서군 표(implementation-django-web·-ninja = 구현 규율 → discipline-reviewer · architecture-api = 계약 → design-review-api) · ninja-final s005-1.2 b1·b3 동일 축 배선 준용 |
| 3 | s003/b1 (10–12) | Django 코어 설계·작성 작업의 스킬 로드 조건 | Obligation | — | `agent-discipline-reviewer`·`command-dddjango` | ①문면 «…코드를 설계·작성할 때 로드한다» · ②27종 전수 — 스킬 로드 판정 술어 0 · §16 기본값 + 절차 층 Coordinator(로드 시점 판정 주체) |
| 4 | s003/b2 (13) | 서버렌더 표현계층의 implementation-django-web 위임 | Obligation | — | `agent-discipline-reviewer` | ①문면 «→ implementation-django-web» · ②27종 전수 — 스킬 경계 라우팅 술어 0 · §16 기본값(implementation-* 문서군 → discipline-reviewer) · web-final s002-1 b5 동일 위임 배선 |
| 5 | s003/b3 (14) | JSON API 어댑터의 implementation-django-ninja 위임 | Obligation | — | `agent-discipline-reviewer` | ①문면 «→ implementation-django-ninja» · ②27종 — 동상(검사 공백) · §16 기본값 · web-final s002-1 b5·ninja-final s005-1.2 b3 판형 |
| 6 | s003/b4 (15) | 신규 REST API 계약 설계의 architecture-api 위임 | Obligation | — | `agent-design-review-api` | ①문면 «→ architecture-api» · ②27종 — 계약 설계 소유 판정 술어 0 · §16 문서군 표(architecture-api → design-review-api) · ninja-final s005-1.2 b1 동일 배선 |
| 7 | s003/b5 (16) | 도메인 전략·애그리거트·도메인이벤트 채택의 architecture-ddd 위임 | Obligation | — | `agent-design-review-ddd` | ①문면 «→ architecture-ddd» · ②27종 — 채택 여부 판정 술어 0(check-domain-model 은 구조 폐쇄만) · §16 문서군 표(architecture-ddd 설계 시점 → design-review-ddd) · ninja-final s005-1.2 b2 동일 배선 |
| 8 | s003/b6 (17) | DB 신뢰성·인덱스·격리·outbox 전달 보장의 architecture-db 위임 | Obligation | — | `agent-design-review-db` | ①문면 «→ architecture-db» · ②27종 — 격리 수준·전달 보장 판정 술어 0(check-transaction-boundary 는 경계 형태만) · §16 문서군 표(architecture-db → design-review-db) · ninja-final s025-7 저장소 축 배선 준용 |
| 9 | s003/b7 (18–19) | Python 관용구·클린코드 원칙의 소유 스킬 위임 | Obligation | — | `agent-discipline-reviewer` | ①문면 «→ implementation-python, … → discipline-cleancode» — 한 불릿의 두 인접 라우팅은 같은 축(언어·보편 규율 이관)이라 1 Work(ninja-final s005-1.2 b1 의 괄호 병기 상대 1 Work 처리 판형) · ②27종 — 술어 0 · §16 기본값 |
| 10 | s004/b1 (21–22) | 비즈니스 로직의 뷰 밖 배치(평면 맥락 fat model) | Obligation | — | `agent-discipline-reviewer` | ①문면 «뷰가 아니라 모델·도메인에 — 평면 Django 맥락은 fat model(§4.1)» · ②27종 전수 — 로직 «의미» 배치 판정 술어 0(check-usecase-dto-placement 는 DTO 자리·check-domain-model 은 구조 폐쇄) · §16 기본값 · implementation-django-final s024-4.1 «비즈니스 로직의 모델·서비스 배치»(E 없음·discipline-reviewer)와 동일 배선 |
| 11 | s004/b1 (21–22) | 표준 4계층의 domain_layer 애그리거트 판정 소유 | Obligation | — | `agent-design-review-ddd`·`agent-discipline-reviewer` | ①문면이 «architecture-ddd §3.2»를 명시 지목 · ②27종 전수 — 판정 소유 «의미» 축 미커버(check-app-container 는 §3.2 중 위치 한 축만·docstring 명시) · ③P0 발견 7(final 규칙 압축 재진술) · architecture-ddd-final s017-3.2 b9 «새 판정이 얹히는 코드의 domain_layer 애그리거트 이주»(E 없음·design-review-ddd) 정합 + 구현 시점 축 discipline-reviewer 병기 |
| 12 | s004/b2 (23) | 서비스 레이어 도입 시점과 HackSoft service/selector 패턴 준거 | Obligation | — | `agent-discipline-reviewer` | ①문면 «(§16.1–§16.2)» · ②27종 전수 — 서비스 도입 «시점» 판정 술어 0 · §16 기본값 · django-final s075-16.1·s076-16.2 전 규범 discipline-reviewer 배선 승계 |
| 13 | s004/b3 (24) | 트랜잭션·일관성 경계의 transaction.atomic() 소유 | Obligation | — | `agent-discipline-reviewer` | ①문면 §16.4 · ②check-transaction-boundary docstring 은 #4(application_layer 의 django import 0)·#200(after_commit)만 — «최소 블록 한정» 형태는 미커버 · django-final s078-16.4 b1 «atomic()은 최소 블록에 한정»(E 없음)과 동일 배선 |
| 14 | s004/b3 (24) | 외부 부수효과의 transaction.on_commit() 시점 정렬 | Obligation | `check-transaction-boundary.py` | `agent-discipline-reviewer` | ②check-transaction-boundary docstring «#200 커밋 뒤 부작용은 unit_of_work.after_commit(…) — 응용이 transaction.on_commit·connection.in_atomic_block 을 직접 부르면 위반» — 부수효과 시점 축을 결정적으로 문다 · ①문면 §16.4 · django-final s078-16.4 b7 동일 배선 |
| 15 | s004/b4 (25) | 유실 불가 메시지의 트랜잭셔널 outbox 구현 | Obligation | `check-broker-contract.py` | `agent-discipline-reviewer` | ②check-broker-contract docstring «#603 external 에 내용이 오면 딸림이 함께 선다 — ⑴outbox …»·«#529 듣는 쪽이 다른 배포 단위인가» — outbox 채택면을 문다 · ①문면 §16.5 · django-final s079-16.5 b1 동일 배선. 괄호의 «채택 기준 architecture-ddd §3.7·전달 보장 architecture-db §9.7»은 소유 좌표 안내라 비계수(s005 표와 같은 규율) |
| 16 | s004/b5 (26) | 도메인 상태 값 집합의 domain Enum 파생 | Obligation | — | `agent-discipline-reviewer` | ①문면 «도메인 상태 값 집합은 domain Enum 파생» · ②27종 — 값 집합 «출처» 판정 술어 0(check-choices-literal-consumption 은 선언된 심볼의 소비면만) · django-final s015-2.5 b2 «값 집합 단일 출처는 domain_layer StrEnum»(E 없음) 동일 배선 |
| 17 | s004/b5 (26) | TextChoices 자체 선언의 순수 인프라 필드 한정 | Exception | — | `agent-discipline-reviewer` | ①문면 괄호 «TextChoices 자체 선언은 순수 인프라 필드 한정» — 조건부 허용이라 Exception · ②27종 — 필드의 «도메인/인프라» 성격 판정 술어 0 · django-final s015-2.5 b2 동명 Exception 배선 승계 |
| 18 | s004/b5 (26) | default= 의 .value 평탄화 | Obligation | `check-choices-literal-consumption.py` | `agent-discipline-reviewer` | ②check-choices-literal-consumption docstring «(a) 같은 필드 호출 안에서 choices= 가 심볼 출처인데 default="리터럴" 을 쓴 경우»·«5) default=OrderStatus.PENDING.value(Attribute) 등은 정상(.value 평탄화 — implementation-django §2.5)» — 이 규범을 이름으로 지목 · ①문면 §2.5 |
| 19 | s004/b5 (26) | 비교·.filter() 값의 심볼 참조 한정 | Obligation | `check-choices-literal-consumption.py` | `agent-discipline-reviewer` | ②동 docstring «(b) 심볼-choices 필드가 확인된 모델의 <Model>.objects.filter/exclude(<field>="리터럴")» — .filter() 축 직접 커버(변수 우회·비교식은 의미 레인=discipline-reviewer 몫이라 병기) · django-final s015-2.5 b5 동일 배선 |
| 20 | s004/b6 (27) | QuerySet 최적화·N+1 방지의 selector/QuerySet 메서드 소유 | Obligation | — | `agent-discipline-reviewer` | ①문면 «(§5, §11.1)» · ②27종 전수 — 쿼리 형태·N+1 술어 0(check-transaction-boundary 는 쓰기 경계·check-usecase-dto-placement 는 DTO 자리) · django-final s032-5.1·s054-11.1 discipline-reviewer 배선 승계 |
| 21 | s004/b7 (28) | 마이그레이션의 안전·무중단 순서 준수 | Obligation | — | `agent-discipline-reviewer` | ①문면 «(§10)» · ②27종 전수 — check-mechanism-ownership 은 migrations 의 자리(#336)·이름(#337)·도메인 import(#338)·손편집(#593)만 보고 «무중단 순서» 술어는 0 → 검사 공백 · §16 기본값 · django-final s049-10.1 전 규범 discipline-reviewer 배선 승계 |
| 22 | s004/b8 (29–30) | 설정의 환경별 분리 | Obligation | `check-test-config.py` | `agent-discipline-reviewer` | ②check-test-config docstring ⑶ «<project>/settings/ 환경축 — #445 갈리는 축은 환경 하나뿐(기능별 분할 파일 금지)·#446 환경 하나=파일 하나·#447 공통 설정은 base» — 환경별 분리를 결정적으로 집행 · ①문면 «설정은 환경별 분리»(§3.3) · §16 «기본값 도피 금지» 적용(담당 검사기 docstring 근거 성립) |
| 23 | s004/b8 (29–30) | settings 직접 접근 주의(모듈 최상위 회피) | Obligation | — | `agent-discipline-reviewer` | ①문면 «직접 접근 주의»(§3.4) — «주의»는 약형 요구라 Obligation(정본 s022-3.4 b1 은 같은 축을 Prohibition «모듈 최상위 settings 접근 회피»로 세웠다 · 재진술 쌍이지만 class 는 문면 강도 차이로 갈린다 — 소급 패스 주의) · ②27종 — 모듈 최상위 settings 접근 술어 0 · django-final s022-3.4 b1(E 없음·discipline-reviewer) 동일 배선 |
| 24 | s005/b1 (32–34) | 주제별 references/final.md 해당 절 준거 | Obligation | — | `agent-discipline-reviewer` | ①문면 «주제별로 … 해당 절을 따른다» · ②27종 전수 — 참조 문서 로딩·준거 술어 0 · §16 기본값(implementation-* → discipline-reviewer) |
| 25 | s005/b18 (53) | 절 단위 필요 항목 한정 로드 | Obligation | — | `agent-discipline-reviewer` | ①문면 «필요한 항목만 읽는다(전체 로드 불필요)» · ②27종 — 로드 범위 술어 0 · §16 기본값. 표 15행은 주제→§ 라우팅 목차라 규범 비계수(P0 규약 승계) |

### 기본값 도피/이탈 점검 (27종 전수 실독의 산물)

- **도피 방지로 새로 배선한 것**: 29행 «설정은 환경별 분리» → `check-test-config.py`. docstring ⑶ «`<project>/settings/` 환경축 — #445 갈리는 축은 환경 하나뿐(기능별 분할 파일 금지) · #446 환경 하나=파일 하나 · #447 공통 설정은 base»가 이 규범 그대로다. implementation-django-final s021-3.3/s022-3.4에는 이 규범이 없어(그 절들은 비밀 하드코딩·모듈 최상위 접근 축) 정본 배선에 선례가 없었지만, §16 «담당 검사기의 docstring 근거가 있는데 기본값으로 도피하면 오배선» 조항을 적용했다.
- **과배선 방지로 일부러 비운 것**: 28행 «마이그레이션 안전·무중단 순서» — `check-mechanism-ownership.py`는 migrations의 자리(#336)·이름(#337)·도메인 import(#338)·손편집(#593)만 보고 «순서» 술어가 0이다. 27행 «N+1 방지» — 27종에 쿼리 형태 술어가 없다. 22행 첫 규범 «비즈니스 로직 배치» — `check-domain-model`은 구조 폐쇄, `check-app-container`는 위치 한 축(docstring 명시)이라 «의미» 축은 공백.
- 26행 `.value` 평탄화·심볼 소비 2건에 `check-choices-literal-consumption.py`를 붙인 것은 docstring의 (a)/(b) 두 직접형이 각각 그 두 규범의 위반면이기 때문이다(정본 s015-2.5는 b5에만 붙였으나, SKILL 불릿이 두 축을 한 문장에 합쳐 놓아 둘 다에 귀속된다).

## 3. 재진술 유예 (교차 문서 쌍 — 전 웨이브 후 소급 패스가 연결)

같은 문서 안 쌍 1건은 spec `restates`로 이미 넣었다: `s001/b2`(frontmatter description, 3행) → `s003/b1`(11행)·`s003/b2`(13행)·`s003/b3`(14행)·`s003/b4`(15행). description의 «먼저 로드한다 + 3건 위임»이 «언제 쓰나»의 로드 조건·경계 불릿 3건의 압축 사본이다.

아래는 **미이관/타 문서 상대**라 spec에 넣지 않고 유예한다(좌표는 전부 **마커 제거본=센서스 기준**이며, 상대 블록 서수는 병합된 상대 spec 실물에서 확인했다).

| 사본 블록(행) | 상대 문서/절/블록 | 상대 행(센서스) | 확인 근거 |
|---|---|---|---|
| s004/b1 (22) | implementation-django-final s024-4.1 b1·b2 | 366–368 · 369–370 | «평면 Django 맥락은 fat model(§4.1)» ↔ 정본 «절 전체의 평면 Django 맥락 한정»·«비즈니스 로직의 모델·서비스 배치» |
| s004/b1 (22) | architecture-ddd-final s017-3.2 b9 | 636–637 | «표준 4계층은 `domain_layer` 애그리거트 소유(`architecture-ddd` §3.2)» ↔ 정본 «새 판정이 얹히는 코드의 domain_layer 애그리거트 이주» |
| s004/b2 (23) | implementation-django-final s075-16.1 b1 · s076-16.2 b3 | 1476–1478 · 1521–1522 | 서비스 도입 시점·HackSoft 네이밍 |
| s004/b3 (24) | implementation-django-final s078-16.4 b1·b7 | 1559–1561 · 1585 | atomic 경계 · on_commit 부수효과 정렬 |
| s004/b4 (25) | implementation-django-final s079-16.5 b1 | 1603–1605 | 유실 불허 발행의 outbox 구현 |
| s004/b5 (26) | implementation-django-final s015-2.5 b2·b4·b5 | 203–204 · 220–221 · 222–223 | Enum 파생·TextChoices 한정 / `.value` 평탄화 / 심볼 소비 |
| s004/b6 (27) | implementation-django-final s032-5.1 b2 · s054-11.1 b1 | 572 · 1052–1056 | QuerySet 체이닝·query-count 규율(§5·§11.1) |
| s004/b7 (28) | implementation-django-final s049-10.1 b1 | 919–928 | 마이그레이션 베스트 프랙티스(§10) |
| s004/b8 (29) | implementation-django-final s021-3.3 b2 · s022-3.4 b1 | 339 · 343–358 | 설정 환경 분리(§3.3) · settings 직접 접근(§3.4) |

- s003의 경계 불릿 6건은 상대 문서(`implementation-django-web`/`-ninja`/`architecture-api`/`-ddd`/`-db`/`implementation-python`/`discipline-cleancode`)의 **위임 표를 뒤집은 짝**이지만, 같은 문장을 재진술한 사본이 아니라 각 문서가 자기 경계를 선언한 것이라 restates 후보로 올리지 않았다(발주서 재진술 열도 N).
- s005 표 15행은 목차라 재진술 상대가 없다.

## 4. 경계 판단 메모

1. **frontmatter는 code가 아니다**(웨이브 2 판례 승계) — `---`·`name:`·`description:`·`user-invocable:`을 행 단위 prose/norm으로 분해했다. 1행 `---`는 절 헤딩 라인이라 `djr:headingSnapshot` 소유가 되고(도구 규약), 5행의 닫는 `---`는 6행 빈 줄과 함께 마지막 prose 블록에 귀속했다(§13 «블록 간 구분자는 선행 블록 후행 스팬 귀속»). agent-coder spec의 s001 분해(`[2,2] [3,3] [4,4] … [14,15]`)와 같은 판형이다.
2. **절 선두 빈 줄**은 첫 블록 선두에 귀속(§13 유일 예외) — s003 `b1=[10,12]`, s004 `b1=[21,22]`, s005 `b1=[32,34]`가 그 형태다. 절 끝 빈 줄은 반대로 마지막 내용 블록의 후행 스팬(예: s003 `b7=[18,19]`).
3. **표는 행 단위 `table-row`** — 머리행+구분행을 한 블록(`[35,36]`)으로 묶고 데이터 15행을 각 1블록으로 뒀다(§13 «표 머리행·구분행도 kind=table-row», 파일럿 architecture-ddd-final s051-8 판형). 마지막 데이터 행이 뒤 빈 줄을 흡수(`[51,52]`).
4. **kind=code 0** — 이 문서에 펜스 블록이 없다. 표 뒤 33·53행은 산문 문장이라 `norm`.
5. **class 판정** — 26행 괄호 «TextChoices 자체 선언은 순수 인프라 필드 한정»만 Exception(조건부 허용)이고 나머지 s004는 전부 Obligation이다. 53행 «필요한 항목만 읽는다(전체 로드 불필요)»는 괄호가 면제처럼 보이나 본문이 «한정해서 읽는다»는 의무라 Obligation으로 뒀다(Permission이면 «읽지 않아도 된다»가 되어 문면과 어긋난다).
6. **재진술 쌍의 class 차이 1건**(W3 L12 수리 · 소급 패스 주의) — 29행 «설정은 환경별 분리, 직접 접근 주의»의 둘째 규범을 **Obligation**(«settings 직접 접근 주의(모듈 최상위 회피)»)으로 세웠는데, 재진술 상대인 정본 `implementation-django-final` s022-3.4 b1은 같은 축을 **Prohibition**(«모듈 최상위 settings 접근 회피»)으로 세웠다. 근거: SKILL 문면이 «주의»라는 **약형 요구**라 «하지 마라»(금지)로 읽으면 문면보다 강해진다. 소급 패스가 이 쌍을 «class 불일치 = 배선 표류»로 오판하지 않도록 여기 명시한다 — 유형 차이는 요약 사본의 약형 문면에서 온 것이고 소유(E 없음·discipline-reviewer)는 정본과 같다. 같은 관계가 §3 유예 표 `s004/b8 (29)` 행에도 걸린다.
7. **§13 «문장 해상도» 대비 처분** — 이 절의 +2 재계수가 문장 이하 채번을 쓴 근거는 묶음 공통이라 `implementation-django-ninja-skill.md` §1 하위 절에 1회 기록했다.

## 5. 소급 패스 이월 — 그래프 전역 결정 대기 (W3 적대 리뷰 반영 · 2026-08-22)

묶음 «django-skills» 3문서 공통 이월 2건. 상세 근거는 `implementation-django-ninja-skill.md` §5에 1회 기록하고 여기서는 이 문서의 해당 좌표만 적는다.

1. **§15 «정본 1곳만 Work 승격»의 적용 범위**(W3 L1 · 개별 수리 **기각** · spec 불변) — 이 문서 좌표: `s001/b2`(3행)가 `restates`(→`s003/b1`~`b4`)와 자기 Work 2건을 겸한다. 기각 근거 요지 ⒜ §15 조항의 실물 스코프는 «축자 쌍»(파일럿 예시가 명시)이고 frontmatter description은 축자 사본이 아니다 ⒝ 발주서 센서스가 s001 규범 수 2를 못 박아 사본 판형(`norms` 0)으로 바꾸면 census 대사가 −2로 어긋난다 ⒞ 전 웨이브 `*-skill` 8종이 동형이라 3문서만 되돌리면 비일관이 커진다. **일괄 확정 대상**.
2. **로드 조건 규범의 위임 판형 불일치**(W3 L11 · 이 묶음 결함 아님 · 소급 정합 대상) — 이 문서 좌표: 배선 표 1행(`s001/b2`)·3행(`s003/b1`)의 `agent-discipline-reviewer`+`command-dddjango`. `architecture-*-skill` 3종은 `command-dddjango`+`design-review-*`, `discipline-tdd`·`implementation-python`·`implementation-test`-skill은 `agent-discipline-reviewer` 단독이다. 배선 불변(§16 기본값 표 2행 병용으로 문면 근거 성립) · 판형 통일은 소급 패스 몫.
