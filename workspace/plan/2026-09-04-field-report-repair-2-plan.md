# 현장 보고 수리 2 — ② 계획 (2026-09-04 · ① 결론 + 결정 1·2 반영 · ③ 리뷰 대상)

루브릭: `2026-09-04-field-report-repair-2-rubric.md`(⓪·① 결과·결정 1·2). 브랜치 `fix/field-report-2`. 실행기 `design_pregate.py` 는 S3 문면 1행 병기 외 무접촉.

## §0 범위(확정)

| 항목 | 최종 형태 | 종류 | 새 Work / 개정 |
|---|---|---|---|
| D | implementation-python §4.4 새 블록 1문장 «항상 `raise` 로 끝나는 도우미는 `-> NoReturn`» (`sys.exit` 없음) | 규범 | **R-3446** 신설(Obligation) |
| E | 하우스룰 §4 새 블록 «`Any` 정책»(무조건형) + 검사기 #493 파일에 **#645** 신설(시그니처 bare `Any` = 위반 · 변수·제네릭 안 = ⓓ#645 후보) + Coordinator registry #11 소개행 병기 | 규범 + 검사기 | **R-3447**(Prohibition `Any` 금지) · **R-3448**(Obligation 경계 `object`/정확 타입·즉시 좁힘) 신설 · R-0345 amendment |
| F-1 | django-ninja §2.3 R-0719 블록에 1문장 «주입 callable ≡ Protocol · 부족 인자는 `build_*()` 본문 안 `partial`/클로저» | 규범 | R-0719 **amendment**(rev) |
| F-2 | discipline-tdd §5.5 «보호할 수 있는 대상» 목록에 불릿 1행 «composition root 실배선 1경로» | 규범 | **R-3450** 신설(Permission — 보호 대상 자격) |
| G | architect R-3427 clarification(경계 3분류) + architecture-ddd §5.3 새 블록 «port 예외 번역 책임 = use case» + 실행기 S3 문면 병기 | 규범(+실행기 문면 1행) | R-3427 **clarification**(rev4) · **R-3449** 신설(Obligation) |
| H | #219/#635 가 `skeleton_placeholder` 파일을 건너뜀 + 하우스룰 #488 블록 R-3181 clarification 1문장 | 검사기 + 규범 | R-3181 **clarification**(rev) |

채번: ISSUED 끝 R-3445 → R-3446(D) · R-3447·R-3448(E) · R-3449(G) · R-3450(F-2) = **신설 5**. 검사기 규칙 번호 **#645**(현행 최대 #644 · 선례 b5f226a 와 같은 표면 등재: `2026-08-08-tree-revision-spec.md` 1행 · `2026-08-11-rule-owner-map.md` 1행). 표현 개정 rev: R-0719 · R-3427 · R-3181 · R-0345 = 4. 새 블록 4(D b3 · E b7 · G arch b6 · F-2 tdd b26) — 블록 IRI 는 «다음 미사용 서수», 위치는 `djr:order` 로(승격 배치 s007/b59 선례) · 공백 소유 규약(§13): 앞 블록의 말미 `\n\n` 을 새 블록이 물려받고 앞 블록은 `\n` 으로.

## §1 항목별 변경 명세

### D — `implementation-python-final.ttl` s032-4.4 새 블록 b3(order: b2 코드 펜스 뒤)
- 문면 초안(R-3446 · Obligation): «항상 `raise` 로 끝나는 도우미는 `-> NoReturn` 으로 선언한다 — `-> None` 이면 호출부의 흐름 분석(`possibly-undefined`·unreachable)이 깨진다. `__init__` 의 생성 차단 가드는 `-> None` 이 문법이라 대상이 아니다.»
- 정합: 경계 단서 R-2720(«부재·거절은 답» — raise 가 아닌 결과 분기)과 무모순(도우미 자체가 raise 로 끝날 때만). `sys.exit` 미포함(트리에 CLI 칸 없음 — ① A·B).
- 표면: ttl → `ontology_render --apply implementation-python-final` → `dddjango/skills/implementation-python/references/final.md` → `corpus_mirror_sync --write`(workspace 소스·codex final.md byte).

### E — 규범 + 검사기
- **규범**: `discipline-houserules-skill.ttl` s007-4 새 블록 b7(order: b6 «pydantic·ninja … 표준 문서군 예시» 뒤). 문면 초안(2 Work):
  - R-3447(Prohibition): «**`Any` 는 타입이 아니라 검사 포기다 — 어디에도 쓰지 않는다.** 함수 시그니처(인자·`*args/**kwargs`·반환)·변수·클래스 속성·제네릭 인자(`dict[str, Any]`) 전부다. 프레임워크 오버라이드가 스텁에서 `Any` 를 쓰더라도 우리 쪽 선언은 `object`(또는 정확 타입)로 쓴다 — mypy 는 이를 호환으로 본다.»
  - R-3448(Obligation): «경계 입력(JSON·폼 `cleaned_data`·`request.user`·무스텁 서드파티)은 `object` 또는 프레임워크가 주는 정확한 타입으로 받아 **받는 즉시** 좁힌다(`TypeIs`·`isinstance`·`type() is` — §1.12). JSON 문서는 `Mapping[str, object]`.»
  - 집행 문장(같은 블록 · R-3447 에 귀속): «시그니처의 `Any` 는 #645 가 차단하고, 변수·제네릭 안의 `Any` 는 ⓓ#645 후보로 표시된다 — 후보는 감수자가 집행한다(§4.1 «시그니처만 강제하므로 나머지는 백스톱과 감수자」와 같은 분담).»
  - R-3150(조건부 면제 금지)과 정합 = 무조건형(결정 1). 23.1 mypy 블록·R-3443·Knowledge Level 예제 무접촉(예시 면제 조항 유지 — ③ 이 «R-20 준수» 로 치환을 요구하면 선택 반영).
  - wiring: `ontology/wiring/discipline-houserules-skill.ttl`(또는 해당 wiring 파일)에 R-3447 `enforcedBy c/check-public-surface-annotation.py` · R-3448 delegatedTo a/agent-coder(기존 §4 Work 의 배선을 따름 — ④ 에서 R-3148 배선 복제).
  - Coordinator `command-dddjango.ttl` s007/b28(R-0345) amendment: registry #11 소개행에 «·명시 `Any`(#645 — 시그니처 차단·변수/제네릭 안은 ⓓ 후보)» 병기 → 렌더 `commands/dddjango.md:133` → codex `SKILL.md` 수동 미러.
- **검사기** `check-public-surface-annotation.py`(+ codex byte 미러):
  - 새 헬퍼 `_explicit_any(ann, bindings) -> str|None`: 문자열 주석 재파싱 → `Optional[...]`/`X | None`/`Union[...]` 언랩 → 루트가 `Any`(Name 이 모듈 바인딩으로 `typing.Any`/`typing_extensions.Any` 로 해소 · Attribute `typing.Any`/`t.Any`) 이면 «bare», 아니면 `_annotation_names` 계열로 하위에 `Any` 가 있으면 «nested».
  - 자리 ①(`_check_signature` 211~226): 인자(posonly·args·vararg·kwonly·kwarg)·반환 각각 — bare → `f.add("#645", …, "시그니처의 `Any` — 검사 포기다: `object`/정확 타입으로 받아 즉시 좁힌다")` · nested → `cand.add("#645", …)`. `self`/`cls`·dunder 는 기존 면제 그대로.
  - 자리 ②(AnnAssign 265~268)·③(클래스 속성 320~322): bare·nested 모두 ⓓ#645 후보(exit 불산입). 선언적 클래스 필드(ninja `Schema` `x: Any`)도 후보(위반 아님 — ① A «② 결정» → 후보로 확정: 계약 `Any` 는 감수자 판단).
  - docstring 헤더: «#645 명시 `Any` 금지 — 시그니처 bare(위반)·그 밖(ⓓ 후보)» 추가. exit 규약 불변(2/0/1).
  - 픽스처 `workspace/eval/fixtures/public_surface/`: good 에 `boundary_narrowing.py`(경계 `object` 입력 → `TypeIs` 좁힘 · Form `__init__(*args: object, **kwargs: object)` 오버라이드 · `Mapping[str, object]`) 1파일 → exit 0 유지 · bad_rules 에 `any_signature.py`(`x: Any`·`-> Any`·`Optional[Any]`·`from typing import Any as _Any`·`typing.Any`·`**kwargs: Any` 6형 + 변수 `y: dict[str, Any]` ⓓ) 1파일 → exit 2 유지·#645×6·ⓓ#645×1 기대.
  - 매트릭스: `findings_count_matrix.py --emit-expected`(public-surface 행: «#493×8 → +#645×6», 사유 커밋 메시지 전건 기록) · `checker_cross_matrix.py`(다른 레인 good 에 시그니처 `Any` 0 — ① A 실측 → 기대 무변 · 변하면 `--emit-expected` 로 원인 분해) · `checker_baseline_matrix`·guard-zero 무변.
  - 규칙 번호 등재: `workspace/design/2026-08-08-tree-revision-spec.md`(#645 1행) · `workspace/plan/2026-08-11-rule-owner-map.md`(1행) — 선례 b5f226a.
- **소급 기대치(무손실 판정식)**: 격리 실행에서 application/* #645 위반 = **spring 8 · kkebi 10**(① C 강도 1 표와 동일해야 함) · ⓓ#645 후보 = 변수 37/61 + nested(시그니처 nested + 변수 nested) — 수치 기록 · `registry_gate` N∖L 귀속으로 legacy 잔존 차단 0(① A). 기존 #493·#358·#456 발화 집합 불변(bare `Any` 도 «주석 존재» 로 계속 인정 — #493 과 #645 는 독립).

### F-1 — `implementation-django-ninja-final.ttl` s010-2.3/b18 · R-0719 amendment(`@2026-09-04`)
- 블록 텍스트 말미에 1문장: «`build_<use_case>()` 가 어댑터 생성자에 꽂는 callable(함수·메서드·`partial`)은 **어댑터가 선언한 Protocol 과 시그니처가 같아야 한다** — 실물 함수가 더 많은 인자(경로·모델·설정)를 요구하면 그 인자는 팩토리 **본문 안에서** `functools.partial`/클로저로 묶어 넘기고 어댑터·use case 는 모른다(모듈 최상단 대입은 #85 위반 · 시그니처가 다른 함수를 그대로 꽂는 것은 «꽂기» 가 아니라 미완성 배선이다).»
- R-0719 는 amendment(의무 확장) — 새 Expression · `currentExpression` 갱신 · 이전 표현 보존. 표면: 렌더 → final.md → corpus_mirror_sync.

### F-2 — `discipline-tdd-final.ttl` s025-5.5 새 블록 b26(order: b24 «별도 사용자 승인 근거 …» 불릿 뒤 · b25 «다음 항목은 … 자격이 아니다» 앞)
- 문면 초안(R-3450 · Permission): «- composition root 의 **실배선 1경로**(진짜 `build_<use_case>()` → 실 어댑터 → 실 함수 · fake 는 외부 I/O 경계뿐) — 주입 callable 의 시그니처 불일치는 이 경로만 잡는다(팩토리를 통째 monkeypatch 하는 테스트는 대체하지 못한다)»
- 성격: 자격 목록 항목 = 강제·소급 없음(① B «quota 비자격·decision 없이 의무화 금지» 정합 · C «신규 BC 부터»). implementation-test 착지 철회(소유 = §5.5). design-review 관점 항목 추가 없음.
- 공백 규약: b24 텍스트 말미 `\n\n` → `\n`, 새 b26 이 `\n\n` 을 가짐.

### G — 규범 2 + 실행기 문면 1행
- **R-3427 clarification**(`agent-design-architect.ttl` s005/b36 · rev4 `@2026-09-04`): «경계 import 전부» 뒤에 경계의 정의를 닫는다 — «**경계란 세 가지다**: ⑴ BC 밖(타 BC OHS/contract·framework 공통·서드파티·테스트 재료) ⑵ **BC 안의 층 경계 중 검사기가 판정하는 것**(driving 잎 → `application_layer/port/**`·domain → 상위 층 등 #92~#96·#185/#186 의 금지·예외 항목 — 잎이 port 예외를 잡을 계획이면 그 import 행을 그대로 적어 G1 에서 #93 예보를 받는다: 적을 수 없는 설계가 드러나는 것이 이 채널의 목적이다) ⑶ 그 밖은 구현 재량(성문 불요). 산문에만 적힌 경계 import 는 예보 표면 밖이다(S3).»
- **architecture-ddd-final.ttl** s038-5.3 새 블록 b6(order: b5 «포트 작성 기준» 뒤 · «어댑터 배치 기준» 앞 — 또는 «어댑터 배치 기준» 블록 뒤; ④ 에서 문맥으로 확정) · R-3449(Obligation): «**port 예외의 번역은 use case 가 진다.** driving 잎(컨트롤러·OHS)은 `application_layer/port/**` 의 예외를 import·catch 하지 않는다(#92/#93) — use case 가 port 예외를 자기 실패(예외)로 번역하고, 잎은 그 실패만 분기한다(`<use_case>_result.py` 엔 성공 한 벌 · #571).» wiring: enforcedBy `c/check-context-isolation.py`(#93 소유 검사기).
- **실행기 S3 문면**(`design_pregate.py` BLIND_SPOTS S3 · byte 미러 · 봉인 draft): «… 산문에만 적힌 경계 import 는 표면 밖 — 전사는 add 소비자 스텁만이다(브라운필드 `update` 잎의 import 는 전사 밖).» 실행 동작 무변(문자열).
- 표면: architect ttl → 렌더 `agents/design-architect.md:90` → codex `dddjango-design-architect/SKILL.md` 수동 미러 · architecture-ddd → final.md → corpus_mirror_sync.

### H — 검사기 2 + 규범 1
- `check-port-adapter-pairing.py` `_check_port_contract`(≈243): 첫 줄에 `if skeleton_placeholder(py): return`(import: `from checker_target import skeleton_placeholder` — #351 이 이미 같은 파일에서 쓰는 경로 확인 후 재사용). 효과: 빈 `<cap>_port.py` 에 #219·#551·… 계약 규칙 전부 침묵(존재 규칙 #218 은 별도 함수라 유지).
- `check-usecase-dto-placement.py` `_check_entry` 호출부(≈379): `if entry is not None and not skeleton_placeholder(entry):` 로 감싼다(#635 및 진입점 내용 규칙 침묵 · #193 존재 규칙 유지).
- 픽스처: `port_adapter_pairing/good` 에 빈 `…/<cap>_port.py` 를 두면 다른 규칙(#576 fake stem 등)이 흔들릴 수 있으므로 **전용 서브 케이스** `port_adapter_pairing/skeleton_placeholder/`(빈 port 1 · docstring-only port 1 → exit 0) 와 `usecase_dto/skeleton_placeholder/`(빈 `_use_case.py` → exit 0) 를 fixture_matrix 삼중(script, fixture, sub) 로 등재. 기존 good/bad 무변. 카탈로그 3커밋 재실행 기대: `59d08c7` #219 0·#635 0(5→0) · `99253ce` 12 불변 · `9c8814e` 0.
- 규범: `discipline-houserules-final.ttl` s003-0/b3 R-3181 clarification(`@2026-09-04` · 현행 `@2026-09-01`): #488 문장 말미에 «빈 파일로 실현된 칸의 **내용 규칙**(진입점·포트 «하나» 등)은 내용이 생긴 뒤부터 선다(registry #2 의 R-0319 와 같은 시점) — 검사기는 내용 없는 골격 파일을 내용 규칙에서 건너뛴다(`skeleton_placeholder`). 빈 파일을 지워 red 를 푸는 것은 #488 위반이다.» 잔여 위험(영구 빈 파일)은 인수 테스트·명세 파일 계획 소관으로 루브릭에 기록(규범화 없음).
- 무손실 판정식: 픽스처 27종 good/bad 무변(0바이트 `_port/_use_case` 없음 — ① A) · 양 저장소 HEAD 격리 실행 #219/#635 발화 집합 무변(0바이트 해당 칸 0) · cross matrix 무변 · pre-gate 픽스처 번들(enforce·checkreport 포함) 무변.

## §2 순서

1. 규범 ttl 5문서 개정(rdflib + `canon_turtle` byte 왕복 · ISSUED +5 · wiring) → `ontology_gate` → `ontology_render --apply` ×5 → LEDGER 재기준선(graph-owned 절 SHA) → target-counts(Expression +9 · Norm/Work +5 · Block +4) → `query_golden_check --emit` → `make rulepack` → corpus_mirror_sync · codex 수동 미러(Coordinator SKILL.md · architect SKILL.md).
2. 검사기 3파일(#645 · #219 · #635) + `checker_target` 재사용 + 픽스처 + 매트릭스 EXPECTED(`--emit-expected` · 사유 기록) + 규칙 번호 등재 2문서 + codex byte 미러.
3. 실행기 S3 문면 1행 + byte 미러 + `manifest_seal.py --write`(draft).
4. `make verify` green · 격리 소급 실행(양 저장소 application/* #645 = 8/10 · #219/#635 무변 · 카탈로그 3커밋) → 결과를 루브릭 ④ 절에 기록.
5. 문서: 현장 보고 상태 블록·추적표 상태 열·«수정 우선순위» 정정 추기(`discipline-test` 부재·26곳·13건·47/0) · 로드맵 R-18/R-19/R-20 · ledger 발견 ⑪⑫ 종결 · 조감도 09-04 행 · 메모리.

## §3 3축 체크(③ 리뷰어 필답)

- 코퍼스 정합: 건드리는 IRI 전수 — R-3446~3450 신설 · R-0719/R-3427/R-3181/R-0345 rev · 블록 4 신설 · wiring 3 · 검사기 3 · 픽스처 2레인+서브 2 · 매트릭스 EXPECTED 2 · 규칙 원장 2 · 실행기 문면 1 · 미러(final.md 4 · SKILL.md 2 · scripts 4).
- 일반화: Claude/Codex 동일(byte·의미 미러) · 프로젝트 플래그 비의존(`object` 대체는 mypy strict 기본에서 성립 · #645 는 mypy 무관) · kkebi 대조(강도 1 표 · #219/#635 무변).
- 무손실: 검출 집합 변화 = **#645 추가만**(E) · **skeleton_placeholder 파일의 #219/#635·계약 규칙 침묵**(H — pre-content 상태만 · HEAD·픽스처 무변 증명) · 그 밖 0. 게이트 강도: G 는 예보 확대(차단 아님) · H 는 pre-content red 소거(설계 의도) · E 는 차단 추가(소급 18 → `object` 치환 안내 문면 동봉).

## §4 리스크·미결(③ 에서 판정)

- E-a: `Any` 를 «주석 존재» 로 계속 인정(#493 독립)하는 것이 옳은가, 아니면 #493 이 `Any` 를 미부착으로 봐야 하는가(① B 는 신설 권고 — 계수 분리).
- E-b: 선언적 클래스 필드(ninja `Schema` `x: Any`)를 ⓓ 후보로 두는 것이 «계약의 `Any`» 를 놓치는가(감수자 집행으로 충분한가).
- E-c: 문면의 «프레임워크 오버라이드도 `object`» 가 `*args: object, **kwargs: object` 관례(ruff `allow-star-arg-any`)와 달라 발주측 툴체인과 마찰하는가 — 마찰해도 규범 우선(결정 1).
- G-a: R-3449 의 착지가 §5.3(핵사고날)인가 §6 구현 패턴인가 — 문맥 판정.
- H-a: `_check_port_contract` 전체 건너뜀이 #551 등 «내용 규칙» 만 침묵하는지(존재·짝 규칙은 다른 함수) — 코드로 확인.
- 채번 순서·블록 order 값·공백 소유는 ④ 에서 레시피대로.

## v2 델타 (③ 계획 리뷰 A 기술·B 규범·C 증거 반영 · 2026-09-04) — §0~§2 문면보다 아래가 우선한다

- **Δ1 F-2 착지(B BLOCKER)**: 새 블록 b26 금지(b26~ 실존 블랙리스트 · 코퍼스 중간 삽입 선례 0). → `s025-5.5/b24` 텍스트를 2불릿 1블록으로 확장 + `statesNorm djr:R-3450`(Permission). 불릿 문면: «- composition root 의 **실배선 정합** — 진짜 `build_<use_case>()` 가 실 어댑터에 꽂는 callable 의 시그니처 일치(fake 는 프로세스 밖 경계뿐) · 팩토리를 통째 monkeypatch 한 테스트는 이 대상의 보호가 아니다». Block +3(2,904).
- **Δ2 G R-3449 착지(B MAJOR)**: `s038-5.3/b6` 실존 → **`s023-3.6/b3`(«응용 서비스의 책임» 불릿 목록) 불릿 +1** + `statesNorm … , djr:R-3449`. 문면(C 재수출 처분 반영): «- port 예외를 **자기 영역의 예외**(`application_layer/<area>/exception.py`)로 번역한다 — driving 잎(컨트롤러·OHS)은 port 예외 **타입**에 의존하지 않는다(직접 import 든 use case 모듈의 재수출 경유든 같다 · #92/#93 은 import 경로만 본다) — 잎은 번역된 실패만 분기한다(`<use_case>_result.py` 엔 성공 한 벌 · #571)». notification-bc(`email_notice_service.py:40` 재수출 경유 catch · G1 승인 09-02)는 **발주측 빚**으로 루브릭 ④·현장 보고 G 추기에 기록(검사기 무발화 · 소급 없음). wiring: delegatedTo a/agent-design-review-ddd + enforcedBy c/check-context-isolation.py(부분 집행 — import 경로만 · 저작 근거 4원 기록).
- **Δ3 E 블록 문면·순서(B MAJOR)**: b7 = rv3-B 대체 문면(문장 1~4 = R-3447 · 5~6 = R-3448 · «§1.12» → «implementation-python §1.12» · 좁히는 자리는 architecture-ddd §3.1 R-3443 참조 · «별표 인자 면제(ruff `allow-star-arg-any`) 관례와 다른 선택이다» 병기 · «ⓓ#645» → «ⓓ 후보(#645)»). wiring: R-3447 enforcedBy public-surface **+ delegatedTo discipline-reviewer** · R-3448 delegatedTo discipline-reviewer 만(coder 오배선 철회).
- **Δ4 E ⓓ 집행 경로(C MAJOR)**: Coordinator step 5 R-0284(`s007/b6` · 필수 입력) **amendment rev3**: «… `check-layer-skeleton`(registry #4)의 ⓓ 후보 채널 출력(…)과 **`check-public-surface-annotation`(registry #11)의 ⓓ 후보(#645 — 변수·제네릭 안의 명시 `Any` · 해당 범위 실행분)** 를 동봉한다». 결정 1 «후보는 감수자 판단» 의 배선(새 결정 아님). R-0345 rev2 는 계획대로.
- **Δ5 E 검사기 설계(A MAJOR)**: `_module_bindings` 재사용 철회 → `_any_bindings(mod) -> (Any 로 바인딩된 이름 집합, typing 계열 모듈 별칭 집합)` 신설(모듈 수준 동명 재정의는 그림자) · `_explicit_any(ann, names, mods) -> "bare"|"nested"|None`(문자열 재파싱 → 루트 Any = bare → `X | None`/`Optional`/`Union` 평탄화 뒤 None 제외 구성원에 Any 있으면 bare · `Annotated[Any, …]` bare · 그 밖 하위 Any = nested · 미해소 `Any` 이름도 Any(fail-closed)) · **별도 패스 `_check_explicit_any(mod, rel, f, cand)`** 를 `main` 의 `_scan_stmts` 다음에 호출(#493 코드 무접촉 · 부모 맵으로 수신자 `self`/`cls` 만 건너뜀 · **함수 dunder 는 면제 아님** · lineno 정렬). 시그니처 bare → `[#645]`(exit 2) · 시그니처 nested·변수/속성 bare·nested → `[ⓓ#645]`. 검출 한계(`TypeAlias` 재별칭·함수 본문 import·`cast`)는 docstring 에.
- **Δ6 E 픽스처·매트릭스(A)**: good = `driven_layer/django_orders/admin/order/form/order_form.py`(Form `__init__(*args: object, **kwargs: object)`·`clean() -> dict[str, object]`·경계 `object` → `TypeIs` 좁힘·`Mapping[str, object]`) **+ 0B `admin/order/panel.py`**(cross census 무변 조건) · bad = `any_signature.py` 8형(`x: Any`·`-> Any`·`Optional[Any]`·`Any | None`·`"Any"` 문자열·`from typing import Any as _Any`·`typing.Any`·`**kwargs: Any`) + 변수 `y: dict[str, Any]` → `#645×8`·`ⓓ#645×1`. `findings_count_matrix --emit-expected`(public-surface 행 «#645×9(위반 8+info 1) · info 열 +1») · **`checker_baseline_matrix --emit-expected`**(public-surface `(2,12,12,4)` → 실측값) · 커밋 메시지에 검사기별 사유 1행.
- **Δ7 E 소급 기대치(A·C)**: application/* `[#645]` = **spring 10 · kkebi 14** = 프로덕션 8/10(① C 목록 전건 — Form `__init__` 6/8·2/10 포함) + `test/factories` 2/4(MATERIAL_DIRS) · ⓓ#645 프로덕션 112/123(시그니처 nested 42/26 · 변수 bare 37/61 · 변수 nested 33/36) · 전 저장소 `[#645]` 78/121 · #493 기준선 3,225/173 불변 · 기존 규칙 A∖B = 0. 진짜 소급 형태 = Phase 0 빚 스캔 항목(spring 5 BC·kkebi 6 BC — 이름 변경·이동 시 재귀속).
- **Δ8 규칙 등재 3문서 6곳(A·B)**: `2026-08-08-tree-revision-spec.md` 규칙 행(7컬럼 · 셀 안 `|` 금지 · 등급 `ast+` · 근거 D58+§4 · blocker) + 집계표 3표(`ast+` 56→57 · 판정×어겼을때 `ast+` 55→56/계 546→547 · 읽는 법 «`ast+` 의 blocker» 55→56) · `2026-08-11-predicates.md` 술어 행(확정·후보·물음) · `2026-08-11-rule-owner-map.md` 1행(`| 645 | ast+ | scripts/check-public-surface-annotation.py | agents/discipline-reviewer.md | 신설 | … |`). spec_lint 0건 확인.
- **Δ9 H 검사기 호출형(A)**: 두 파일이 이미 `import checker_target` → `checker_target.skeleton_placeholder(py|entry)` 속성 호출(port-adapter :641 판형). 침묵 집합 = #219·#551·#220·#241·#212·#485(내용 규칙) · #218/#193/#576/#488 유지. `empty` 스텁 pre-gate 귀속 4→2 · 번들 PASS · fixture 104/104.
- **Δ10 H 무손실 판정식(A·C)**: «cross matrix 무변» 철회 → `checker_cross_matrix --emit-expected` 로 `('skeleton','check-port-adapter-pairing.py')`·`('skeleton','check-usecase-dto-placement.py')` **2행 제거**(사유: 결정 2 — good_bc 의 0B 재등장 칸) · 그 밖 무변. **`registry_gate_smoke` P0′ red**(`34c74a6` scripts 트리째 대조라 good_bc legacy #219/#635 소실) → `_pre_repair_gate` 를 «현행 검사기 트리 + 옛 `registry_gate.py` 덮어쓰기»(게이트 불변만 측정)로 수리 → 31/31. HEAD 양 저장소 #219/#635 차분 0/0 · docstring-only 골격 0/0 · 카탈로그 59d08c7 {#219×2,#635×3}→0·exit 0 · 99253ce 두 검사기 몫 7 불변.
- **Δ11 D·H·R-3427 문면(B)**: D b3 = blockquote 단서 형(«> dddjango 단서: … `-> NoReturn`(3.11+ 는 `Never` 동치) … `__init__` 의 생성 차단 가드는 **타입 규약**이 `-> None` 을 강제하므로 대상이 아니다») · wiring R-3446 delegatedTo discipline-reviewer. H R-3181 = **amendment rev3**(«registry #2» → «Coordinator 가 빈 모듈을 error inventory 에서 제외하는 것(R-0319)과 같은 시점» · 함수명 대신 «내용 없는 골격 파일(0바이트·docstring/주석뿐)»). R-3427 = **amendment rev4**(독법 ⓑ 명세가 형식 red 가 되는 실효 변화 — LEDGER 사유 병기) · 문면 rv3-B 대체안(«층 규율 검사기가 금지·예외 항목으로 판정하는 것» · S3 참조). F-1 = R-0719 문장 **직후** 삽입(말미 아님) · «꽂히는 자리가 선언한 Protocol·`Callable` 시그니처».
- **Δ12 G S3 문면(A)**: «(브라운필드 `update` 잎의 import 는 실존 판정(⑴~⑶)만 받고 스텁 전사 밖)».
- **Δ13 미러·표면(B)**: doc_key **8**(§1 목록 + discipline-houserules-final) · render ×8 · LEDGER 8행 · final.md 5(+houserules final) · codex 손 미러 **3**(`dddjango/SKILL.md` 108·133 · `dddjango-design-architect/SKILL.md` · **`dddjango-discipline-houserules/SKILL.md` §4**) · 계수 Expression +10(신설 5 + rev 5: R-0345·R-0284·R-0719·R-3427·R-3181) · Norm/Work +5 · Block +3.
- **Δ14 §2 순서 보강(A)**: 2단계에 `gen_pregate_symbol_kinds.py` 재소성(+codex JSON byte 미러) · baseline/cross `--emit-expected` · P0′ 수리 · 규칙 등재 3문서 추가. `manifest_seal.py --write` 는 1·2·3 전 변경 뒤 **마지막 1회**. 4단계 검증식 = Δ7·Δ10 수치.
- **Δ15 현장 보고 정정(B·C)**: 원문 보존 · «수정 우선순위» 절 직전 blockquote 1개에 모음(`discipline-test` 부재 · «26곳» 미재현(14+3) · «13건» 은 43e9628 시점(HEAD 0) · «47/application 0» 은 ANN401 기준(재집계 8/10) · «왕복 2회·≈14분» = 게이트 red 2회·파일 왕복 1회·13:42 · G 재수출 빚 1 · H «lane 6» 정의 부재) + 처분 상태 표 상태 열만 갱신.
