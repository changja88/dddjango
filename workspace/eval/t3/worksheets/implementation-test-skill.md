# T3 저작 검수표 — implementation-test-skill

- 원문: `dddjango/skills/implementation-test/SKILL.md (68행)` · spec: `workspace/eval/t3/specs/implementation-test-skill.spec.json`
- 자기 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/implementation-test-skill.spec.json` → **exit 0** (블록 4·5·19·24 = 52 · Work 46 · exit 0 · `--write` 미사용)
- 필독 이행: 발주서 · authoring.md §13~§16 · `ontology_migrate.py` 선두 docstring · 파일럿 spec 2건 · `dddjango/scripts/check-*.py` **27종 docstring 선두 전수 실독**(묶음 «py-test-skills» 3문서 공통 1회)

## 1. census 대사

| 절 | 헤딩 | 발주서(센서스) 규범 수 | spec 규범 수 | 블록 수 | 판정 |
|---|---|---|---|---|---|
| s001 | (전문) — frontmatter | 2 | 2 | 4 | 일치 |
| s003 | 언제 쓰나 | 8 | 8 | 5 | 일치 |
| s004 | 핵심 운영 원칙 | 34 | 34 | 19 | 일치 |
| s005 | 상세 레퍼런스 | 2 | 2 | 24 | 일치 |
| **계** | — | **46** | **46** | **52** | **불일치 절 0** |

불일치 절 0. 다만 s004(34)는 **문장 수만으로는 31**이라, 계수 규약을 명시해 둔다.
- 기본은 문장 해상도(§13). 여기에 **한 문장이 서로 다른 deontic class 의 절을 병렬로 질 때만 분할**한다 —
  djr 의 Work class 가 단일값이라 한 Work 로는 두 힘을 담을 수 없기 때문이다.
- 분할 3건: 25행(Obligation «mocker 픽스처» + Prohibition «raw unittest.mock 폴백 금지») ·
  32행(Permission «진단 도구로 쓸 수 있지만» + Prohibition «근거는 아니다») ·
  34행(Obligation «기댓값은 리터럴로» + Permission «심볼 단언·arrange 심볼 사용은 허용»).
  31 + 3 = 34 로 센서스와 정확히 일치 → **센서스 산정이 옳다**(내 문장-only 산정이 과소였다).
- 같은 문장 안이라도 **같은 class 의 병렬 절**은 나누지 않았다(20행 3문장 «retain 재조직 …없고, reuse·reject …0이다» =
  둘 다 «쓰기 0» Prohibition 이라 1 Work). 이 비대칭이 위 3건과 20행을 가르는 기준이다.
- 이 기준 문장은 묶음 «py-test-skills» 3문서 공통이다 — implementation-python-skill 검수표 §1 도 같은 문장을 쓰고,
  같은 기준으로 s004 25·29행을 분할해 센서스 11 → spec 13(«센서스 과소») 으로 판정했다. discipline-tdd-skill 은
  분할 대상 문장이 없어 센서스 17 과 일치한다.
- 35행(§19.2)은 센서스 비고대로 한 불릿 5문장 = 5 Work.

## 2. 배선 근거 표 (전 규범)

| # | 절·블록 | class | Work label | enforcedBy | delegatedTo | 4원 근거(① 문면 역할명 ② docstring § 인용 ③ P0 커버 ④ registry·기본값) |
|---|---|---|---|---|---|---|
| 1 | s001/b2 | Obligation | 테스트 코드·픽스처·테스트더블·계약 검증 코드 작성·리팩터링 시 우선 로드 | — | agent-discipline-reviewer | ①문면 — 프론트매터 description 은 스킬 라우터 트리거(«…먼저 로드한다») · ②check-*.py 27종 docstring 선두 전수 실독 — 스킬 로드 라우팅을 집행하는 검사기 0 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 2 | s001/b2 | Obligation | 테스트 수명 주기의 discipline-tdd 위임과 Django 구현의 implementation-django 계열 위임 | — | agent-discipline-reviewer | ①문면이 위임 상대를 직접 지정(«…는 discipline-tdd, Django 구현은 implementation-django 계열로 위임») · ④§16 기본값 — discipline-tdd·implementation-* 문서군 모두 agent-discipline-reviewer |
| 3 | s003/b1 | Obligation | 테스트 코드·계약 검증·커버리지·Mutation·BDD·동시성 테스트 작성 시 로드 | — | agent-discipline-reviewer | ①문면 «…작성할 때 로드한다» · ②check-*.py 27종 docstring 선두 전수 실독 — 스킬 로드 조건 판정 술어 0 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 4 | s003/b1 | Obligation | discipline-tdd §5.5 입장 결정 완료 후 add·update·명시 승인 retain 재조직 mechanics 한정 제공 | — | agent-discipline-reviewer | ①문면 «…입장 결정을 끝낸 뒤 … 작성 mechanics만 제공한다» · ③implementation-test-final s001 b1 «discipline-tdd §5.5 입장 결정 이후 사용» 동일 규범의 3중 사본 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 5 | s003/b1 | Prohibition | retain 재조직의 새 case·assertion·Red 생성 금지(전후 동일 보호 유지) | — | agent-discipline-reviewer | ①문면 «새 case·assertion·Red를 만들지 않고» · ③implementation-test-final s001 b1 동일 라벨 선례 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 6 | s003/b1 | Prohibition | 후보·reuse·reject 의 새 test file·case·assertion·helper 의무 전환 금지 | — | agent-discipline-reviewer | ①문면 «…의무로 바꾸지 않는다» · ③implementation-test-final s001 b1 «candidate·reuse·reject의 테스트 산출물 의무 전환 금지» 동일 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 7 | s003/b2 | Obligation | TDD 방법론·테스트 수명 주기의 discipline-tdd 위임 | — | agent-discipline-reviewer | ①문면 «→ discipline-tdd» · ④§16 기본값 표 discipline-tdd 행 → agent-discipline-reviewer |
| 8 | s003/b3 | Obligation | Django 모델·ORM·서비스 레이어 구현의 implementation-django 위임 | — | agent-discipline-reviewer | ①문면 «→ implementation-django» · ②check-*.py 27종 docstring 선두 전수 실독 — 스킬 간 관할 이관 술어 0 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 9 | s003/b4 | Obligation | Ninja Router/Schema·mounted public HTTP·adapter-local client 계약 구현의 implementation-django-ninja 위임 | — | agent-discipline-reviewer | ①문면 «→ implementation-django-ninja» — 위임 상대가 implementation-* 문서군이라 기본값 유지(architecture-api 를 지목하지 않음) · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 10 | s003/b5 | Obligation | Django 뷰·템플릿·폼·HTMX 구현의 implementation-django-web 위임 | — | agent-discipline-reviewer | ①문면 «→ implementation-django-web» · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 11 | s004/b1 | Obligation | recipe 적용 전 discipline-tdd §5.5 decision row 확인 | — | agent-discipline-reviewer | ①문면 «먼저 discipline-tdd §5.5의 decision row를 확인한다» · ③implementation-test-final s001 b1 동축 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 12 | s004/b1 | Obligation | recipe 적용 범위 한정 — add·update 와 명시 승인된 retain 의미 보존 재조직 | — | agent-discipline-reviewer | ①문면 «…에만 아래 recipe를 적용한다» · ③final s001 b1 «recipe 적용 범위는 add·update·승인된 retain 재조직 한정» 동일 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 13 | s004/b1 | Prohibition | retain 재조직의 새 case·assertion·Red 0 과 reuse·reject 의 test artifact write 0 | — | agent-discipline-reviewer | ①문면 두 절이 같은 «쓰기 0» 축이라 1 Work · ③discipline-tdd-final s025-5.5 b17 동축(단 pending 조항은 여기 없음) · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 14 | s004/b1 | Prohibition | 피라미드·coverage·속도·도구 예시의 add 근거 사용 금지 | — | agent-discipline-reviewer | ①문면 «…는 add의 근거가 아니다» · ③implementation-test-final s004-1.1 b7 «피라미드 모양·coverage 수치·속도만으로 add 금지» 동일 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 15 | s004/b2 | Obligation | 입장된 행동을 증명하는 최소 테스트 범위 선택 | — | agent-discipline-reviewer | ②check-*.py 27종 docstring 선두 전수 실독 — 테스트 범위 선택 술어 0(check-test-config 는 test/ 층 구조·DB 신호 축) · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 16 | s004/b2 | Prohibition | 유효한 domain/application/DB/adapter/public contract 테스트의 상위 계층 사유 강등·생략 금지 | — | agent-discipline-reviewer | ①문면 «…낮추거나 생략하지 않는다» · ③implementation-test-final s004-1.1 b10 동축 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 17 | s004/b3 | Obligation | 오라클 기준의 migration 전용 테스트 ↔ DB-backed 현행 동작 테스트 식별 | — | agent-discipline-reviewer | ①문면이 오라클 기준 2분법을 규정 · ③implementation-test-final s007-1.4 b3·b4 «오라클 기준» 동일 · ②check-*.py 27종 docstring 선두 전수 실독 — 오라클 종류 판정 술어 0 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 18 | s004/b3 | Obligation | 본 절의 기술적 식별 한정 — 수명 주기는 discipline-tdd 소유 | — | agent-discipline-reviewer | ①문면 «…식별만 하고 수명 주기는 discipline-tdd에 넘긴다» · ③final s007-1.4 b1 동일 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 19 | s004/b4 | Obligation | 테스트 러너·작성의 pytest(pytest-django) 기본 — 함수형·assert·@pytest.mark.django_db·픽스처 | check-test-config.py | agent-discipline-reviewer | ②check-test-config.py docstring ⑴ «pytest ↔ Django settings 바인딩»과 ⑵ «#387 test/unit 은 DB 를 켜지 않는다(django_db …)» — pytest-django 채택과 django_db 마커 축을 결정적으로 집행 · ③implementation-test-final s021-4.1 b1 이 같은 축을 check-test-config.py 로 배선한 선례 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) 병기(함수형·assert 스타일은 미커버) |
| 20 | s004/b5 | Obligation | 테스트 더블의 역할·리스크 기준 선택(Stub→상태·Mock→상호작용·Fake→가벼운 협력자) | — | agent-discipline-reviewer | ②check-*.py 27종 docstring 선두 전수 실독 — 더블 종류 선택 술어 0 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) · discipline-tdd-final s038-8 b1 «테스트 더블 분류·Python 구현의 implementation-test 위임» 수임 축 |
| 21 | s004/b6 | Obligation | mock 도구의 pytest-mock mocker 픽스처 사용(자동 teardown) | — | agent-discipline-reviewer | ①문면 «도구는 pytest-mock mocker 픽스처» · ③discipline-tdd-final s036-7.6 b1 «Mock 경계의 도구는 pytest-mock mocker 픽스처» 동일 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 22 | s004/b6 | Prohibition | raw unittest.mock 폴백 금지 | — | agent-discipline-reviewer | ①문면 «raw unittest.mock 폴백 금지» — 앞 절과 deontic class 가 달라 별도 Work · ②check-*.py 27종 docstring 선두 전수 실독 — mock 라이브러리 선택 술어 0 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 23 | s004/b7 | Prohibition | «적극적» 해석의 mock·도구 추가 확대 금지(경계 전용 도구 업그레이드 한정) | — | agent-discipline-reviewer | ①문면 «…더 많이 mock·도구 추가하는 것이 아니다» · ③implementation-test-final s034-7.1 b1 «과도한 Mock(Mockery) 회피» 동축 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 24 | s004/b8 | Obligation | 픽스처의 명시적·격리적 작성과 conftest 계층 공유 범위 최소화 | — | agent-discipline-reviewer | ②check-*.py 27종 docstring 선두 전수 실독 — 픽스처 스코프 술어 0(check-test-config 는 test/ 직계 파일이 conftest.py·__init__.py 뿐이라는 «위치»만 봄) · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) · implementation-test-final s011-3.2 b1 동축 |
| 25 | s004/b9 | Obligation | 상태·결과 우선 검증과 화이트박스(내부 구현) 검증 회피 | — | agent-discipline-reviewer | ③implementation-test-final s034-7.1 b2 «검증 방식 우선순위 준수(출력→상태→통신)»·discipline-tdd-final s036-7.6 b1 동일 축 · ②check-*.py 27종 docstring 선두 전수 실독 — 단언 대상 술어 0 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 26 | s004/b10 | Obligation | 승인된 property-based case 의 Hypothesis 표현과 승인 재현 경계의 @example 고정 | — | agent-discipline-reviewer | ③implementation-test-final s042-8 b1 «PBT 적용은 §5.5 입장된 속성 계약 한정» 동축 · ②check-*.py 27종 docstring 선두 전수 실독 — PBT 술어 0 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 27 | s004/b10 | Prohibition | 도구의 입력 생성 능력을 새 테스트 근거로 사용 금지 | — | agent-discipline-reviewer | ①문면 «…사실은 새 테스트 근거가 아니다» · ③final s042-8 b1 «입력 생성 능력만으로 … 추가 금지» 동일 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 28 | s004/b11 | Obligation | ORM 영속 픽스처 기본의 factory_boy 채택과 최소 필요 상태·DB fixture 최소화 | — | agent-discipline-reviewer | ③implementation-test-final s049-9.1 b3 «ORM 애그리거트·엔티티 영속 픽스처의 기본은 factory_boy» 동일 · ②check-test-config.py 는 팩토리 «위치»(test/factories/) 축만 집행하고 이 규범의 «기본 도구 선택»은 미커버 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 29 | s004/b12 | Obligation | 승인된 동시성·idempotency·CAS case 의 DB-backed mechanics 사용 | — | agent-discipline-reviewer | ③implementation-test-final s100-20 b2 동축 · ②check-idempotency-scope-creep.py 는 프로덕션 멱등성 «산출물»의 미요청 확장 축이라 테스트 mechanics 비커버 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 30 | s004/b13 | Permission | 승인 테스트 유효성 점검의 coverage·mutmut 진단 도구 사용 허용 | — | agent-discipline-reviewer | ①문면 «…진단 도구로 쓸 수 있지만» · ③implementation-test-final s083-17 b1 «절 범위는 입장된 테스트의 감지력 진단 mechanics» 동축 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 31 | s004/b13 | Prohibition | 수치·생존 mutant 자체의 새 case·assertion 근거 사용 금지 | — | agent-discipline-reviewer | ①문면 «…근거는 아니다» — 앞 절과 deontic class 가 달라 별도 Work · ③final s067-13 b1·s083-17 b1 동일 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 32 | s004/b14 | Obligation | AAA·assertion 선택·Free Ride 방지·테스트 분리의 가독성 recipe 지위 | — | agent-discipline-reviewer | ①문면 «…이미 입장된 case의 가독성 recipe다» · ③implementation-test-final s013-3.4 b1·s081-16.1 b10 동축 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 33 | s004/b14 | Prohibition | 가독성 recipe 의 새 case·assertion 승인 금지 | — | agent-discipline-reviewer | ①문면 «새 case/assertion을 승인하지 않는다» · ③final s081-16.1 b10 «assertion 분리 시 별도 테스트 자동 생성 금지» 동일 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 34 | s004/b15 | Obligation | 외부 계약 검증 assert 기댓값의 리터럴 표기(프로덕션 상수 역수입 금지) | — | agent-discipline-reviewer | ①문면 «…기댓값은 리터럴로 — 프로덕션 상수 역수입은 자기참조 오라클» · ③implementation-test-final s078-15.4 b1 동일 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 35 | s004/b15 | Permission | 도메인 내부 단위 테스트의 심볼 단언·arrange 심볼 사용 허용 | — | agent-discipline-reviewer | ①문면 «…허용» — 앞 절과 deontic class 가 달라 별도 Work · ③final s078-15.4 b3 «경계① 도메인 내부 단위 테스트의 심볼 단언 허용»·«경계③ arrange/act 는 심볼 사용 권장» 동일 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 36 | s004/b16 | Obligation | Django Ninja 오류의 입장된 HTTP mapping 한정 — 실제 mount 된 Django client 로 status/body/승인 header 검증 | — | agent-discipline-reviewer | ③implementation-test-final s092-19 b2 «공개 HTTP 계약은 mount 된 endpoint 를 Django test client 로 검증» 동일 · ②check-api-error-controller-contract.py·check-openapi-error-declaration.py 는 프로덕션 컨트롤러·OpenAPI 선언 축이고 테스트 코드 축 술어 0 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 37 | s004/b16 | Obligation | plugin 기본 오류 schema property 목록 부재와 shape 변경의 별도 명시 사용자 승인 요건 | — | agent-discipline-reviewer | ③implementation-test-final s094-19.2 b1 «오류 Schema 존재·직렬화 사실만으로 테스트 생성 금지» 동축 · ②check-*.py 27종 docstring 선두 전수 실독 — 사용자 승인 요건 판정 술어 0 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 38 | s004/b16 | Obligation | 공개 OpenAPI 계약 검증의 실제 mount 생성 문서 관련 operation/status/schema 한정 | — | agent-discipline-reviewer | ②check-openapi-error-declaration.py 는 프로덕션 openapi_extra.responses 선언·operation↔schema 일치를 집행하나 «테스트가 무엇을 검증하는가»는 관할 밖 · ③final s092-19 b1 동축 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 39 | s004/b16 | Prohibition | 미승인 Pydantic private introspection·framework 기본 직렬화·error helper/factory/serializer/mapping/handler 내부 unit test 작성 금지 | — | agent-discipline-reviewer | ①문면 «…만들지 않는다» · ③discipline-tdd-final s025-5.5 b34 «내부 Schema·helper 직접 호출 introspection의 공개 wire 대체 금지» 동축 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 40 | s004/b16 | Obligation | framework 기본 body 의 입장된 public wire 계약 시 consumer 의존 관련 field 한정 검증 | — | agent-discipline-reviewer | ①문면 «…관련 field만 검증한다» · ③final s092-19 b2 동축 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 41 | s004/b17 | Obligation | 발행 이벤트 union-enum 동기 검증의 입장 후 recipe 지위(자동 세트 아님) | — | agent-discipline-reviewer | ①문면 «…자동 세트가 아니라 입장 후 recipe다» · ③implementation-test-final s079-15.5 b1 «union-enum 동기 구조는 테스트 의무가 아닌 candidate signal» 동일 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 42 | s004/b17 | Permission | 독자 published/wire drift failure + 기존 보호 부재 시에만 add 허용(자명 반복 구조는 reuse·reject) | — | agent-discipline-reviewer | ①문면 «…때만 add할 수 있으며» — 조건부 허용 · ③final s079-15.5 b1·b2 동축 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 43 | s004/b18 | Obligation | migration 전용·DB-backed 현행 동작 테스트의 식별·수명 주기 기존 규칙 준수 | — | agent-discipline-reviewer | ①문면이 §1.4 와 discipline-tdd §5.5 를 준거로 지정 · ③discipline-tdd-final s025-5.5 b46·b47 동축 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 44 | s004/b19 | Prohibition | 테스트 안티패턴(복잡한 조건문·프로덕션 로직 재사용·숨겨진 의존성) 회피 | — | agent-discipline-reviewer | ①문면 «…를 피한다» · ③implementation-test-final s081-16.1 계열 동축 · ②check-*.py 27종 docstring 선두 전수 실독 — 테스트 코드 냄새 술어 0 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 45 | s005/b1 | Obligation | 주제별 references/final.md 해당 절 준수 | — | agent-discipline-reviewer | ①문면 «…해당 절을 따른다» — 상세 규범의 정본 위치 지정 · ②check-*.py 27종 docstring 선두 전수 실독 — 문서 라우팅 술어 0 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |
| 46 | s005/b24 | Obligation | 필요한 항목만 부분 로드(전체 로드 불필요) | — | agent-discipline-reviewer | ①문면 «필요한 항목만 읽는다(전체 로드 불필요)» · ②check-*.py 27종 docstring 선두 전수 실독 — 로드 범위 술어 0 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례) |

## 3. 재진술 유예

센서스 restate 열 기준. 문서 내 쌍만 spec `restates` 에 실렸다. 좌표는 **마커 제거본(센서스) 기준**이며
상대 `implementation-test-final`·`discipline-tdd-final` 은 웨이브 2 기이관 문서라 현재 파일에는 마커가 있으나
아래 좌표는 마커 없는 절 키·블록 서수다.

① 문서 내(= spec 수록, 유예 아님)
| 사본 블록 | 정본 블록 | 근거 |
|---|---|---|
| s001/b2 (frontmatter description) | s003/b1 · s003/b2 · s003/b3 · s003/b4 · s003/b5 | description = 로드 트리거 1 + 위임 2(«discipline-tdd» / «implementation-django 계열»)를 압축. «계열»이 b3~b5(django·ninja·web) 셋을 한꺼번에 지시하므로 b3·b4·b5 를 모두 정본으로 지목했다. 센서스 «DIFF→DIFF 정정: 동상» 판정과 정합 |
| s004/b1 (20행 §5.5 게이트 4문장) | s003/b1 (11행 4문장) | **문서 내 재진술 — 초판 미연결을 교정해 spec `restates` 에 수록.** 정본은 완전 진술이자 선행인 s003/b1: s004/b1 의 1·2문장(«decision row 확인» + «add·update·승인 retain 한정»)은 s003/b1 2문장의 분해, 3문장(«retain 새 case·Red 없음 / reuse·reject write 0»)은 s003/b1 3·4문장의 압축이다. **부분 중첩** — s004/b1 의 4문장(«피라미드·coverage·속도·도구 예시는 add 근거가 아니다»)에 대응하는 절이 s003/b1 에는 없다(교차 상대 final s004-1.1 b7 은 아래 ②에 유예). 두 블록이 모두 외부 정본(implementation-test-final s001 b1)의 사본이라는 사실은 **문서 내 쌍을 잇지 않을 사유가 되지 못한다** — 브리프 «같은 문서 안 쌍만 spec restates 에 넣는다»는 문서 내 쌍의 수록을 요구하고, 교차 상대는 별도로 ② 유예에 남긴다 |
| s004/b18 (37행) | s004/b3 (22행) | **문서 내 재진술 — 심사 결과 연결.** b18(«migration 전용·DB-backed 현행 동작 테스트의 식별·수명 주기는 기존 규칙을 그대로 따른다 (§1.4, discipline-tdd §5.5)»)은 같은 절 b3 의 두 규범(오라클 기준 식별 + «식별만 하고 수명 주기는 discipline-tdd 에 넘긴다»)을 «기존 규칙 그대로»로 압축 재지시할 뿐 새 규범 내용을 더하지 않는다. 대상 2종·준거 §1.4 가 b3 과 동일하고, 인용된 §1.4 는 이 스킬 안에서 곧 b3 이다. 준거 지시문이라는 형식만으로 별개 규범으로 두면 문서 내 사본이 미기록으로 남으므로 재진술로 판정(class 는 원문대로 Obligation 유지 — 재진술 연결이 Work 채번을 줄이지는 않는다) |

② 교차 문서(유예)
| 사본 블록 | 상대 문서/절(센서스 좌표) | 대조 결과 |
|---|---|---|
| s003/b1 (4문장) | implementation-test-final / s001 b1 (4 Work) | **축자 3중 사본** — final 머리말·본 스킬 s003·본 스킬 s004 b1 이 같은 §5.5 입장 게이트 문면. 규범 4↔4 정확 대응. 이 중 **문서 내 2본(s003/b1↔s004/b1)은 ① 로 올려 spec 에 수록**했고 여기 남는 것은 final 상대뿐이다 |
| s004/b1 (§1) | implementation-test-final / s001 b1 · s004-1.1 b7 | 위와 같은 문면의 세 번째 사본 + 피라미드 근거 부정(4문장은 s003/b1 에 없어 s004-1.1 b7 이 유일 상대). 문서 내 상대 s003/b1 은 ① 수록 |
| s004/b2 (§1) | implementation-test-final / s004-1.1 b10 | 요약 사본 |
| s004/b3 (§1.4) | implementation-test-final / s007-1.4 b1 · b3 · b4 | 오라클 2분법 축자 요약 |
| s004/b4 (§3, §4, §19.4) | implementation-test-final / s021-4.1 b1 · s099-19.4 b1 | 요약 사본 — 배선도 동일(check-test-config.py) |
| s004/b5 (§2, §7.1) | implementation-test-final / s008-2 b1 · s034-7.1 b3 | 요약 사본 |
| s004/b6 (§7) | implementation-test-final / s033-7 b1 · discipline-tdd-final / s036-7.6 b1 | mocker 도구 지정은 tdd-final s036-7.6 b1 과 동일 문면(교차 2건) |
| s004/b7 | implementation-test-final / s034-7.1 b1 | «Mockery 회피»의 스킬판 재진술 |
| s004/b8 (§3.7, §4.2) | implementation-test-final / s011-3.2 b1 · s022-4.2 b1 | 요약 사본 |
| s004/b9 (§7.1, §15.3) | implementation-test-final / s034-7.1 b2 · s077-15.3 b1 | 요약 사본 |
| s004/b10 (§8) | implementation-test-final / s042-8 b1 (2 Work) | 규범 2↔2 정확 대응 |
| s004/b11 (§9) | implementation-test-final / s049-9.1 b3 | 요약 사본 |
| s004/b12 (§20) | implementation-test-final / s100-20 b2 | 요약 사본 |
| s004/b13 (§13, §17) | implementation-test-final / s067-13 b1 · s083-17 b1 | 규범 2 가 두 절에 나뉘어 대응 |
| s004/b14 (§3.4, §15.2, §16) | implementation-test-final / s013-3.4 b1 · s076-15.2 b1 · s081-16.1 b10 | 요약 사본 |
| s004/b15 (§15.4) | implementation-test-final / s078-15.4 b1 · b3 | 규범 2(의무+허용)가 b1·b3 에 대응 |
| s004/b16 (§19.2, 5문장) | implementation-test-final / s092-19 b1~b3 · s094-19.2 b1 · s095-19.2.1 · s096-19.2.2 · s097-19.2.3 | 5문장이 §19·§19.2 계열 전반의 압축 — 소급 패스에서 문장별 정밀 대응 필요(P0 «표류 위험» 지목 지점) |
| s004/b17 (§15.5) | implementation-test-final / s079-15.5 b1 · b2 | 규범 2↔대응 |
| s004/b18 (§1.4 + discipline-tdd §5.5) | implementation-test-final / s007-1.4 · discipline-tdd-final / s025-5.5 b46 · b47 | 교차 2문서. 문서 내 상대 s004/b3 은 ① 수록(심사 근거는 ① 행) |
| s004/b19 (§16) | implementation-test-final / s081-16.1 · s082-16.2 b1 | 요약 사본 |

s005 는 센서스 restate=N — 확인 결과 유예 대상 0.

## 4. 경계 판단 메모

- **frontmatter kind**: python-skill 과 동일 판형(여는 `---` = 헤딩 라인, 2행부터 블록, description 만 norm).
- **s003 b1 을 한 블록으로 둔 이유**: 11행은 4문장이 한 문단에 이어 붙은 형태다. §13 «블록 경계는 자연 단위(문단)» 규약대로
  문단 1블록으로 두고, 4 Work 를 `statesNorm` 다중 연결로 달았다(행 중간 분할 불요 — 개정 1 3노드형).
- **§19.2 불릿(35행)**: 한 불릿 5문장 = 1블록 5 Work. 블록을 문장별로 쪼개지 않은 것은 같은 이유다.
- **20행 vs 25·32·34행의 분할 비대칭**: 위 census 절에 적은 대로 «같은 문장 안 다른 deontic class»만 분할 기준으로 썼다.
- **26행 «적극적 = …»의 class**: 정의문 형태지만 실질 규범력은 «더 많이 mock·도구 추가하는 것이 아니다»라는 확장 차단이라
  Prohibition 으로 판정했다(implementation-test-final s034-7.1 b1 «과도한 Mock 회피»와 동축).
- **36행 둘째 문장의 class**: «…때만 add할 수 있으며»는 조건부 허용이라 Permission. 뒤따르는 «reuse·reject한다»는
  같은 조건 판정의 반대 분기라 별도 Work 로 세지 않았다(final s079-15.5 b1·b2 대응 관계와 정합).
- **표 블록**: 44~45행(머리행+구분행) 1블록 + 46~66행 1행 1블록, 마지막 66행이 67행 빈 줄 흡수. 68행은 별도 norm 블록.
