# 리비전 10호 원인 파악 — v2.17.12 첫 다레인 야간 가동 마찰 7건 실물 검증

2026-09-01. spring_dream_server 야간 다레인 가동(v2.17.11 설치 시점)에서 보고된 검사기·규범
마찰 5건 + 참고 2건을 플러그인 정본(검사기 소스·트리 개정 명세·산문 코퍼스)과 발주측 산출물
(`.dddjango/` 레인 기록·STOP 문서)로 교차 검증한 결과다. **발주측 임시 처리 5건은 전부 규범이
제공하는 정규 채널(계약 축소+검증 유지·binding 제거·오탐 분리 보고·이동 철회·--legacy-debt-file)로
적법 — 되돌릴 것 없음.**

검증 방법 요약: 각 주장에 대해 ① 소유 검사기의 방출 경로 전수 추적(rule-owner-map →
`dddjango/scripts/check-*.py` 실물) ② 트리 개정 명세 행 대조 ③ 발주측 사고 원문
(`spring_dream_server/.dddjango/<레인>/` · `docs/superpowers/orders/lane/STOP-*.md`) 확인.

## A1. #396 — framework/pydantic/ 미인식 (검사기 결함 · 환경 의존 비결정)

- **증상**: 발주 명세 FR-10이 `framework/pydantic/`을 강제했는데 registry가 «4단 판정에 안
  걸린다» red. 발주측은 `--legacy-debt-file` 정확히 1줄로 우회(레인 가동 중).
- **근인**: `check-business-vocabulary.py:141` — `is_tech = p.name in tech or p.name in CURATED_TECH`.
  - `tech` = `business_vocab.tech_names()`(115~127행) = stdlib 모듈명 ∪ **`packages_distributions()`
    (검사기를 실행한 python의 설치 배포판!)** ∪ 고정 낱말 목록(pydantic 없음).
  - `CURATED_TECH`(81~82행)에도 pydantic 없음.
  - 같은 파일 72행 `FRAMEWORK_TYPES = {"ninja", "django", "rest_framework", "pydantic"}`에는
    **있음**(용처 상이 — 307행 import 판정) — 파일 내 비일관.
  - 결과: 프로젝트 venv python으로 돌리면 pydantic이 `packages_distributions()`에 잡혀 green,
    다른 python이면 red — **판정이 실행 환경에 묶인 비결정**. 이것이 «registry가 인식 못 함»의 실체.
- **처방**: `CURATED_TECH`에 `pydantic` 추가(결정적 축으로 봉인). 발주측 빚 1줄 제거는 그쪽 소관.

## A2. DECLARATIVE_BASE_NAMES 결손 — 커스텀 유저 모델 (검사기 결함)

- **증상**: 계정 BC에서 annotation 빚 11건(발주측 보고 — accounts 레인, `AbstractBaseUser` 기반
  커스텀 유저 모델).
- **근인**: `check-public-surface-annotation.py:73` `DECLARATIVE_BASE_NAMES`에 `Model`은 있으나
  `AbstractBaseUser`·`PermissionsMixin`·`AbstractUser` 부재. 커스텀 유저 모델
  (`class User(AbstractBaseUser, PermissionsMixin)`)은 base가 `Model`이 아니라서 137행의
  선언적 클래스 분기(`{_name_of(b)} & DECLARATIVE_BASE_NAMES`)를 못 타고 일반 클래스로 분류 →
  프레임워크 필드 선언(`email = models.EmailField(...)` 등)에 annotation을 요구. 그런데
  houserules §4는 Django 모델 필드에 annotation을 **달면 안 된다**고 정한다(달면 프레임워크
  오작동) — 해소 불가능한 협공이라 빚으로만 남는다.
- **처방**: 세 이름 추가. (같은 계열 `AbstractUser`는 `AbstractBaseUser`의 하위지만 base 이름
  직접 대조 방식이라 셋 다 명시 필요.)

## A3. #416·#426·#52 — BC 이름 오탐 (검사기 결함 · 탐지 방식)

- **증상**: **무변경** framework 파일(`framework/technology/rag/runtime/yeonhae_release.py`,
  diff 0)이 일반 영단어 "promotion" 때문에 신설 BC `promotion` 참조로 #416 red. 발주측은
  경로 밖 diff 0 증명 + 오탐 분리 보고로 G2 통과(정규 채널).
- **근인**: `check-business-vocabulary.py:264` — `re.search(rf"\b{re.escape(n)}\b", text)`.
  **파일 raw text 전체**(주석·docstring·문자열 리터럴 포함)에 BC 이름 낱말 대조. BC 이름이
  일반 영단어면(promotion·product·wallet …) 산문 언급마다 발화. 같은 함수 바로 아래
  업무 어휘 검사(277행~)는 `_identifier_tokens(mod)`(AST 식별자 토큰) 기반 — 정밀 판형이
  같은 파일에 이미 있다. 이 스캔 하나가 자리별로 **#426(test)·#416(technology)·#52(그 밖)**
  셋을 먹인다(263행 주석).
- **처방**(사용자 확정 — 셋 동일 정밀화 · 계획 v2에서 «순수 축소» 노선으로 확정): 스캔
  대상을 주석·산문 문자열을 공백 치환한 스크럽 사본으로 바꾸고 `\b` 정규식은 유지 —
  기존 발화의 부분집합 보장. fail-closed 유지 목록: dotted-path 문자열·BC 이름 정확 일치
  단독 낱말(앱 라벨·라우팅 키)·f-string 통째(버전 비결정 차단)·tokenize 실패 원문.
  (v1의 identifier 토큰 전환안은 적대 리뷰 레인2가 brownfield 신규 red를 실증해 기각.)

## B1. #328 ↔ #462 — django_adapter.py 면제 비대칭 (플러그인 내부 모순 · 성문 채번 미상환)

- **증상**: promotion 레인에서 `driven_layer/adapter/campaign_usage_history/django_adapter.py`의
  ORM import가 #462(port-adapter-pairing)는 green(면제)인데 #328(context-isolation)은 red —
  처음 승인했던 파일 이동을 철회하고 현 경로 유지 + 오탐 분리 보고로 마감.
- **근인**: `check-port-adapter-pairing.py:1007~1015`에 `adapter/<capability>/django_adapter.py`
  면제가 성문화돼 있고(동명 폴더 승격 꼴 대응 포함), 주석에 **«성문 채번은 별건(houserules
  출구 절 신설 필요 — 절 삽입은 section-key 마이그레이션 선행)»** 미상환 TODO 명기(2호 실증 ·
  사용자 A안 승인). 반면:
  - `check-context-isolation.py` — django_adapter 언급 **0건** (#328 «`django_<bc>/` import는
    `driven_layer/adapter/persistence/` 아래뿐» 그대로 집행).
  - 트리 개정 명세 행 #328(642행)·#462(691행) — 둘 다 면제 미기재(성문 공백).
  - 즉 면제가 검사기 한 곳에만 살아 있는 «집행이 성문을 앞선» 드리프트. 이번 야간 가동에서
    실비용(승인 이동→철회 소동) 실증.
- **처방**(사용자 확정 — 완주): ① `check-context-isolation.py` #328에 동일 면제(+승격 꼴)
  동기화 ② 명세 행 #328·#462 부칙 ③ houserules 출구 절 성문 채번(section-key 마이그레이션
  선행 조건 이행 포함) — 미상환 TODO 상환.

## C1. #63 — openapi_extra 성공 200 헤더 메타데이터 (검사기 결함 + 문안 공백 · **1차 판정 정정**)

- **증상**: `promotion_pricing_controller.py`가 `response={200: PromotionPriceListOut}` 직접
  선언 위에 `openapi_extra.responses[200].headers`(Cache-Control·Vary 문서화)만 보충 — G2에서
  #63 red 1건(STOP 문서 «checker #5의 #63은 status와 내용의 구분 없이 openapi_extra.responses
  자체를 금지» — 실측 표 51·123행). 발주측 결정 2: 문서 메타데이터만 제거, runtime 헤더와
  e2e 검증 유지.
- **근인** (2겹):
  1. **검사기 레인 비대칭**: code 레인 둘(`_openapi_extra_findings` 2709~·
     `_scan_openapi_extra_statuses` 668~)은 **400≤status≤599 게이트**가 있으나, tree 레인
     `_tree_slice63`(3440~3444행)은 `_dict_has_key(kw.value, "responses")` — **status 무관**하게
     `openapi_extra`에 `responses` 키만 있으면 #63 방출. 200-only 보충은 code 레인에 대응
     사건이 없어 overlap 억제도 못 탄다. 발주측 문제 진술이 정확했다.
     (⚠️ 본 조사 1차 패스는 code 레인 둘만 보고 «검사기는 무죄»로 오판정 — tree 레인 전수
     추적에서 정정. 방출 경로 전수 확인 전 무죄 판정 금지를 재확인한 사례.)
  2. **문안 공백**: 명세 행 #63(387행)·ninja 산문(final.md 128·835행 — 둘 다 graph-owned 절)
     모두 주어가 «오류 응답»이지만, 성공 응답 메타데이터 보충의 **허용을 명시하지 않아**
     보수 해석(전면 금지)이 유일한 안전 독해였다.
- **처방**(계획 v2 확정): ① `_tree_slice63` 게이트 — 키 전부 **리터럴**·전부 **100–399
  화이트리스트**·집합 **⊆ `response=` 선언**(extra로 status 신설 우회 차단 — 적대 리뷰
  레인3 BLOCKER 반영)·splat 은 해석 불가 취급, 그 밖 전부 fail-closed 방출 ② graph-owned
  문안 amendment 4건(R-0089·R-0683·R-2932·R-0339) ③ 명세 행 #63 부칙. 반영 후 발주측
  계약 재추가는 사소 증분 발주(그쪽 소관).

## C2. #267 — StrEnum 계수 해석 (버그 아님 · 명문화)

- **증상**: promotion 레인 g2에서 «target/discount 다중 공개 값 타입 2» — 파일 분리로 해소
  (one-public-value-type-per-file). 참고 6건째로 «StrEnum one-public-symbol 해석 명문화» 제안.
- **근인**: `check-domain-model.py:454~456` — `_public_classes(mod)` 전수 계수라 StrEnum도
  공개 클래스로 **암묵** 포함. 규칙 문면(#267 «값 객체 하나 = 파일 하나», 589행)은 StrEnum
  (값 집합)이 «값 객체»로 계수되는지 명시하지 않는다. 동작은 일관·발주측 처리도 규칙대로 —
  해석 여지만 있다.
- **처방**(계획 v2 정정): 명세 행 #267 부칙 — «값 집합 Enum 계열(StrEnum·Enum·IntEnum·
  Choices 류)도 값 객체다(공개 클래스 계수 포함)». 참고: ErrorSchema+ErrorCode 동거는
  #572 소관(`bc_error_schema.py`는 driving_layer라 #267 대상 밖 — «예외»가 아니라 소관
  구분·적대 리뷰 레인4 정정). 검사기 무변.

## C3. 승격 스코프 조사 의무 부재 (리비전 9호 보강 — 규범 공백)

- **증상**: chat_relay `turn_controller` 동명 폴더 승격 G0 제안이 «turn/** 만 · 공개 표면
  불변»을 주장했으나, 실측 결과 `test/fake/process_runtime_port.py:198~213`이
  `monkeypatch.setattr(turn_controller, "build_*_use_case", …)` 4건으로 **모듈 객체를 패치** —
  승격 시 핸들러의 전역은 본체 모듈로 옮겨가 패치가 무효화(테스트가 진짜 composition root를
  탐). turn/** 밖 1파일 동반 수정이 필수인데 스코프 밖.
- **근인**: 리비전 9호 캐스케이드 규범(R-3415~R-3418 — `discipline-houserules-skill.ttl`
  s004-1/b7)에 승격 슬라이스 스코프 산정 시 **대상 모듈을 «모듈 객체로» 참조하는 곳**
  (monkeypatch·settings dotted path·동적 import)의 조사 의무가 없다. 재수출 `__init__`의
  import 표면 불변 리트머스는 **읽기 표면**만 보증하고 **패치 표면**은 보증하지 않는다.
- **처방**: 캐스케이드 절 amendment — 승격 판정·집행 전 모듈 객체 참조처 조사와 스코프 편입
  의무 신설(온톨로지 개정).

## D. #474 — 기각 확정 (변경 없음 · 기록)

- 발주측 제안: 입구 파일에서 one-call try·exact catch·즉시 `raise Published() from error` 꼴의
  좁은 binding 허용.
- 검증: 명세 행 #474(771행 «묶은 이름을 그 파일 안에서 참조하면 위반»)와 검사기
  (`check-api-error-controller-contract.py:7183~7192` — `as` 바인딩 이름의 Load 참조 탐지,
  `from e`의 cause도 Load 참조) 완전 정합 — 오탐 아님. 발주측 임시 처리(binding 제거 —
  implicit `__context__`가 진단 보존)도 정확.
- 경계 비대칭은 의도된 설계: **driving 공개 표면**은 도메인 예외를 타입으로만(누출 방지 —
  #474), **driven 내부**(persistence 어댑터)는 explicit `raise … from error`·`__cause__`
  identity 계약(promotion 레인 design-spec §4.2 실증). `__cause__` vs `__context__`는
  traceback 문구 차이뿐이라 허용 개정의 실익이 없고, 허용 꼴 판별 복잡화·누출 표면 재개방
  비용이 더 크다.
- **사용자 기각 확정**(2026-09-01) — 본 문서가 기각 기록이다.

## 부칙 — 판정 요약표

| 항목 | 분류 | 검사기 | 성문 | 실영향 잔존 |
|---|---|---|---|---|
| A1 #396 | 결함(환경 의존) | `CURATED_TECH` +pydantic | — | ✅ 빚 1줄 |
| A2 선언 베이스 | 결함(목록 결손) | 3이름 추가 | — | ✅ 빚 11건 |
| A3 #416·#426·#52 | 결함(탐지 방식) | identifier+import 기반 | — | 소멸(분리 보고 완료) |
| B1 #328↔#462 | 내부 모순 | #328 면제 동기화 | 행 부칙 2 + houserules 절 신설 | 소멸(철회 완료) |
| C1 #63 | 결함(레인 비대칭)+문안 공백 | tree 레인 status 게이트 | graph 문안 + 행 부칙 | 계약 재추가 대기 |
| C2 #267 | 해석 여지 | 무변 | 행 부칙 | — |
| C3 승격 스코프 | 규범 공백 | 무변 | 캐스케이드 amendment | G0 스코프 보정 권고 중 |
| D #474 | 정합(오탐 아님) | 무변 | 무변(기각 기록) | — |
