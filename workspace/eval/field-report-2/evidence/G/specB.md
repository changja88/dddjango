# 통합 설계 명세 — `fortune_catalog` 신규 BC (점집의 메뉴판·안내 책자)

작성자: design-architect · 산출물 폴더 `.dddjango/20260903-1214-fortune-catalog/`
활성 lens: **ddd 단독** (api·db 비활성 — 발주서 고정: HTTP API 0 · DB 표 0 · migration 0).
근거 스킬: `architecture-ddd`(§2 전략·§3 전술·§3.2 판정소유·§3.5 도메인서비스·§3.6 응용서비스) · `discipline-houserules`(final.md §0 제1원칙·§1 트리 140행·§2 골격·§3 명명·§5 driven 출구면제) · `discipline-tdd`(§5.5 입장심사).

---

## §0 컨텍스트 · BC 배치 (명세에 박는 결정)

- **BC 배치 = 새 독립 BC `fortune_catalog`** (스코프 메모가 고정 — 발주서 D50·D51-3 소유). 코디네이터 판정이 아니라 발주가 고정한 제약이므로 그대로 존중하고 재결정하지 않는다. *왜* — 소유 범위(조회 창구 3종)는 리딩(16행 `fortune_reading`)과 유비쿼터스 언어가 다르다: 리딩은 (work_id, rag_id)를 «입력으로만» 받는 순수 근거 엔진이고(D11), 이 BC는 활성 Service Bundle의 관계표(#7)를 읽어 «무엇을 볼 수 있나»를 판정하는 메뉴판이다. 두 어휘는 한 애그리거트에 응집하지 않는다.
- **이 BC는 BC 중 유일한 SPARQL 소비자**다(온톨로지 가이드의 C11 출판 도구는 `framework/` 잔존 — §8 보고). 관계표 조회의 SPARQL 본문은 이 BC의 driven adapter가 소유한다(D51-1 — 다른 BC가 ORM/SQL을 repository에 두는 것과 동형).
- **직접 선례**: `application/fortune_reading/**` — 신규 BC 표준 트리·OHS·Bundle 고정 주입(`framework/technology/rag/runtime/service_runtime.validate_terminal_active_service_bundle`을 composition에서 driven adapter에 주입)·primitive DTO mirror·닫힌 union 응답을 실물로 답습이 아니라 «형태 규약»으로 참조한다(트리는 무조건 표준 — final.md §1.1).
- **상태 없음**: 자체 DB 표 0 · migration 0 · LLM 0. 단 `INSTALLED_APPS`에는 등록한다(전 BC 선례·mypy 게이트 사각 회피 — D51-3 ⑩).

### BC 간 통신·경계 (context-isolation)
- **소비자 부재**: HTTP API 0, OHS만. 소비자(점집)는 아직 없다 → OHS 계약 fixture + BC 테스트로 완결(발주서 공통 규율).
- **cross-BC 참조 없음**: 이 BC는 다른 BC의 OHS/contract를 import하지 않는다(정적 import 0 — #385/#13). 유일한 외부 의존은 `framework/technology/rag/**`(RAG 런타임 데이터·Bundle 검증 함수)이며 이는 BC가 아니라 프레임워크 기술이라 ACL 대상이 아니다. 따라서 `driven_layer/adapter/anticorruption_layer/`·`external_system/`는 빈 골격으로 존속(§1 트리 97·100행).
- **타 BC와의 정본 관계**: `fortune_character`(#32)의 `work_references[].rag_id`는 비정본이고 (fortune→work,rag) 매핑 정본은 이 BC다(D51-3 ⑫). 그러나 이 발주 범위에서 `fortune_character`와의 배선·통신은 만들지 않는다(소유하지 않음).

---

## §1 활성 lens · API 스택 결정

### API 스택 결정 순서 (신규 표면 여부 → N/A)
1. **신규 HTTP/JSON API 표면이 있나?** — 없다. 발주서가 「HTTP API 0(OHS만)」으로 고정. 이 BC의 유일한 입구는 `open_host_service/`(같은 프로세스 함수 호출 전송)뿐이다(#90 — driving_layer 자식은 전송으로 갈린다).
2. **확립 스택 관찰**: 저장소는 Django Ninja(`ninja_extra.NinjaExtraAPI` + `@api_controller`)를 확립 HTTP 스택으로 쓴다(리딩 `driving_layer/api/api_router.py` 실측 — `register_fortune_reading_api`). 그러나 이 BC는 HTTP 표면을 노출하지 않으므로 **스택 결정 자체가 N/A**다 — Ninja/DRF/plain 택일이 성립하지 않는다(결정의 대상은 새 HTTP/JSON API surface뿐).
3. **결과 제약**: 신규 registrar slice N/A(`register_fortune_catalog_api` 없음) · `<project>/api.py`·`urls.py` mount 변경 N/A. `driving_layer/api/api_router.py`·`bc_error_schema.py`는 고정 칸이므로 **빈 파일**로 실현한다(final.md §0 #488 — 고정 칸은 비어도 실현; HTTP 없는 상태가 규범 준수의 정상 상태 — #429 celery.py 유비). `<area>/`(controller·schema)는 자리표시자라 등장하지 않는다(#489 — HTTP area 접기).
4. **composition_root DI·INSTALLED_APPS는 표준 유지**(profile 무관 표준 — final.md §1.1 관찰 비입력 축): `composition_root/dependency_wiring.py`의 `build_*` 팩토리가 DI를 소유하고, `settings/base.py` INSTALLED_APPS에 `FortuneCatalogConfig` 1줄을 등록한다.

### 오류 wire 계약 / 12-slot
**12-slot error contract는 이 명세의 적법한 부재 레인이다** — 이 BC는 Ninja endpoint/error contract/response Schema를 만들거나 바꾸지 않는다(HTTP surface 0). 따라서 12-slot·framework error profile은 **적용 대상 없음(not applicable)**이며, 오류는 HTTP status/ErrorSchema가 아니라 **OHS 반환형의 닫힌 결과 타입**(§6·§7)으로 표현한다. 12-slot 부재가 적법한 레인에서도 machine block·입장 표 규율은 상시 적용한다(§11·§12).

---

## §2 패키지 · 테스트 구조 결정 (final.md §0·§1)

**소스 파일트리는 언제나 dddjango 표준(final.md §1 트리 140행)이다** — 기존 레이아웃·리딩 실물은 트리 결정의 입력이 아니라 «형태 규약»의 참조일 뿐이다(§1.1). BC 루트 `application/fortune_catalog/`의 골격을 아래대로 실현한다. 고정 칸은 비어도 `__init__.py`/빈 파일로(#488), 자리표시자(`<…>`)는 개념이 실제 있을 때만(#489), BC 직계는 일곱뿐(#81).

### 실현하는 «칸» (값은 §12 file-plan이 정본 · 여기선 개념 배치)
- **`composition_root/`** — `dependency_wiring.py`(concrete: `build_*` 3팩토리) · `event_wiring.py`(빈 — 이벤트 없음).
- **`published_event/`** — 빈 골격(이벤트 없음).
- **`driving_layer/`**
  - `api/` — `api_router.py`·`bc_error_schema.py` **빈 파일**(HTTP 0) · `webhook/` 빈 골격. `<area>/` 없음.
  - `open_host_service/catalog_inquiry/` — `catalog_inquiry_service.py`(concrete: 3 공개 함수) · `contract/request/`(창구2·3 요청) · `contract/response/`(창구1·2·3 응답) · `contract/exception/catalog_inquiry_published_error.py`(**빈** — published 예외 없음, 모든 실패는 응답 union 변형).
  - `cron_job/` — 빈 골격. `event_subscription/` — `event_router.py` 빈 파일 + 빈 골격.
- **`application_layer/`**
  - `catalog_inquiry/` (area) — 3 use_case 폴더(§4). 각 폴더는 `_use_case.py`·`_command.py`·`_query.py`·`_result.py` 네 파일을 갖고, 미사용 입력 파일(command 또는 query)은 **빈 파일**로 둔다(리딩·query_translation 실측 규약 — `translate_query.py`가 빈 파일).
  - `port/` — `active_service_bundle/`(D6 Bundle 고정) · `relation_table/`(Graph 조회·SPARQL) 두 능력 포트 + `domain_bypass_query/` 빈 골격 + `unit_of_work/` 빈 골격.
- **`domain_layer/`** — `<aggregate>/` **없음**(무상태·불변식 트랜잭션 경계 없음 → 애그리거트 부재; 리딩도 애그리거트 없음). `shared_value_object/`(값 객체군) · `domain_service/`(판정 서비스). 표현 부재 근거: 이 BC의 도메인은 관계표의 «투영»이라 상태를 보호할 애그리거트가 없고, 판정(가시성 분류)은 무상태 도메인 서비스가 소유한다(§3.5).
- **`driven_layer/`**
  - `adapter/active_service_bundle/rag_runtime_adapter.py` · `adapter/relation_table/rag_runtime_adapter.py`(concrete) · `adapter/persistence/{repository,domain_bypass_query,unit_of_work}/` 빈 골격 · `adapter/anticorruption_layer/`·`external_system/` 빈 골격.
  - `django_fortune_catalog/` — `apps.py`(concrete: `FortuneCatalogConfig`) · `models/`·`migrations/`·`admin/` 빈 골격(모델 0·migration 0).
- **`test/`** — `unit/`(도메인·use case·adapter·동치·닫힌분기) · `integration/` 빈 · `e2e/` 빈(HTTP 0 → OpenAPI e2e 없음) · `factories/` **빈 골격**(factory_boy 픽스처 없음 — rdflib Graph 빌더는 factory 재료가 아니다·#392) · `fake/`(**포트 페이크 전용 2종** — `active_service_bundle_port.py`·`relation_table_port.py`; 각 능력 포트와 `<capability>_port.py`로 짝 #576/#462). 합성 관계표 turtle은 «포트 페이크»가 아니라 «테스트 데이터»라 `test/fake/`에 두면 #576 위반이므로, 이를 태우는 어댑터/동치 테스트 모듈 안에 test-local helper로 인라인 빌드한다(#392 «테스트 안으로» · C1). 리딩 16행 실측 규약과 일치(`test/fake/`는 포트 페이크 전용 — 리딩은 SPARQL 비소비자라 turtle을 test 어디에도 두지 않음).

### driving 잎 의존 제약 (#92/#93/#96)
- `open_host_service/catalog_inquiry/catalog_inquiry_service.py`는 `application_layer/catalog_inquiry/**`(use case·command/query/result)와 도메인 값 객체·`composition_root`의 `build_*`만 의존한다 — `application_layer/port/**`를 import하지 않는다(#96). 포트는 use case·adapter만 안다.
- `contract/**`(request·response)는 stdlib(`dataclasses`·`typing`)와 같은 BC contract만 import하고 **domain 객체를 담지 않는다**(#472/#162 — primitive DTO mirror). 매핑(도메인→primitive)은 service가 한다.

### 명명 규약 (final.md §3 — 읽고 구체 이름만 결정)
- 능력 포트: `<capability>_port.py`(`active_service_bundle_port.py`·`relation_table_port.py`), 자료 `<data>_out.py`/`<data>_in.py`, `exception.py`. 어댑터: `<technology>_adapter.py`(`rag_runtime_adapter.py`). `Interface`/`Impl` 표식·약어 금지(#3).
- Django: 앱 위치 `driven_layer/django_fortune_catalog/`, `AppConfig` 이름/라벨은 §12 symbols. 모델 없음 → `<entity>_model.py`·`db_table` N/A.

---

## §3 도메인 설계 (ddd)

이 BC의 유비쿼터스 언어: **운세 종류(FortuneType)** · **관계표(relation table)** · **후보 가시성(visibility)** · **지원 자료((work, rag) 쌍 + 필요 입력)** · **세대 표식(bundle_id)** · **닫힌 답(closed answer)**.

### 애그리거트 판단
- **애그리거트 없음.** 보호할 상태·불변식의 트랜잭션 경계가 없다(무상태 조회, 관계표는 외부 불변 CAS). 따라서 `<aggregate>/`·repository·UoW를 만들지 않는다(§3.3 Vernon — 진짜 불변식만 애그리거트로; 없으면 만들지 않는다). 도메인은 **값 객체 + 무상태 도메인 서비스**로 표현한다(§3.5 — 여러 개념에 걸친 무상태 도메인 로직).

### 값 객체 (`domain_layer/shared_value_object/`)
- **`FortuneType`** — `fortune_id: str`(bare) · `labels: tuple[tuple[str, str], ...]`(`(lang, label)` 정렬). 라벨 부재 시 빈 튜플 허용(관계표 SHACL이 라벨 미강제). **라벨 부재 시 도메인은 빈 labels를 그대로(불변) 운반한다 — 라벨을 fabricate하지 않는다.** labels가 비면 fortune_id를 표시 이름으로 쓴다 — 이 **BC 계약이 정한 규칙**(관계표 SHACL이 라벨 미강제)이며, **적용(실제 치환)은 소비자가 한다**. BC는 라벨을 fabricate하지 않고 빈 labels를 그대로(불변) 운반하며, 표시용 언어 선택만 점집 소유다(→ 단일 display_name을 BC가 고르지 않는다). 즉 규칙은 BC 계약 소유이고 적용은 소비자 몫이다(«소비자 규약»이 아니라 «BC 계약이 정한 규칙·소비자 적용»).
- **`FortuneVisibilityStatus(StrEnum)`** — 닫힌 판정 결과: `VISIBLE`·`UNSUPPORTED`·`ABSENT`. 이것이 «닫힌 답»(D13)의 도메인 소유 형태다.
- **`ClassifiedFortuneCandidate`** — `fortune_id: str` · `status: FortuneVisibilityStatus`.
- **`WorkRagRef`** — `work_id: str` · `rag_id: str`(리딩 FR-1 자구 일치 — 평평한 두 목록 금지, 쌍으로 운반).
- **`FortuneSupport`** — `fortune_id: str` · `status: FortuneVisibilityStatus` · `work_rag_refs: tuple[WorkRagRef, ...]` · `required_input_ids: tuple[str, ...]`. status ≠ VISIBLE이면 두 튜플은 빈 값.

### 도메인 서비스 (`domain_layer/domain_service/`)
- **`FortuneVisibilityService`** (`classify_fortune_visibility.py`) — 가시성 «판정»을 소유한다(§3.2 판정소유 — 비즈니스 규칙은 도메인이 실행, 인프라로 복제 금지). 무상태·순수.
  - `classify_candidates(*, candidate_fortune_ids, present_fortune_ids, support_pairs, carried_rag_ids) -> tuple[ClassifiedFortuneCandidate, ...]`
  - `resolve_support(*, fortune_id, present_fortune_ids, support_pairs, required_input_pairs, carried_rag_ids) -> FortuneSupport`
  - **판정 규칙**(닫힌 분기): 후보 fortune_id가 ① `present_fortune_ids`에 없으면 `ABSENT` ② 있으나 `{rag | (fortune, work, rag) ∈ support_pairs ∧ rag ∈ carried_rag_ids}`가 공집합이면 `UNSUPPORTED` ③ 아니면 `VISIBLE`. *왜* — 「지원 판정 = supportsFortune RAG가 활성 descriptor `rag_release_refs`에 포함」(D51-3 ②)은 비즈니스 규칙이므로 도메인이 소유한다. carried_rag_ids(descriptor 탑재 서고)와 support_pairs(관계표 사실)의 교집합 판정을 SQL/adapter로 옮기면 빈혈이 된다(§3.2 — 판정은 도메인, adapter는 사실만 제공).
  - **`resolve_support` VISIBLE 산출 규칙**(A2 확정): status 판정이 `VISIBLE`이면 `work_rag_refs = sorted({WorkRagRef(work, rag) | (fortune, work, rag) ∈ support_pairs ∧ rag ∈ carried_rag_ids})`(**탑재분 필터** — 소비자(리딩 BC)는 Bundle 미탑재 rag를 못 쓰므로 `carried_rag_ids ∩`만 담는다) · `required_input_ids = sorted({input | (fortune, input) ∈ required_input_pairs})`. status ≠ VISIBLE(UNSUPPORTED·ABSENT)이면 두 튜플은 빈 값(값 객체 `FortuneSupport` 계약과 일치). *왜* — 미탑재 rag를 담으면 소비자가 못 쓰는 참조를 넘겨 지원 판정을 오염한다(§3.2 판정 소유·D51-3 ②).
  - **opaque 수용**(D51-3 ⑬): `candidate_fortune_ids`의 개수·≤3 불변식을 재검증하지 않는다(#4·점집 소유). 받은 id를 그대로 분류한다.
- registry availability 필터는 리딩 FR-5 소유이므로 이 BC 판정에 넣지 않는다(descriptor 탑재만 본다).

### 소유권 자기점검 (절 간 일관)
- 판정(가시성·지원)은 **도메인 서비스**가 단일 소유. adapter는 관계표 «사실»(fortune_types·support_pairs·required_input_pairs)과 «carried_rag_ids»만 제공하고 판정하지 않는다. OHS는 도메인 결과를 primitive로 미러만 한다. use case는 순서 조율만(§3.6 — 응용 서비스는 흐름·경계, 비즈니스 로직 없음).

---

## §4 응용 유스케이스 · 자료 계약 (`application_layer/catalog_inquiry/`)

유스케이스는 연산 객체로 명세한다(#635 — 공개 클래스 하나·`execute(<command|query>) → <result>`; #567 — `dto` 낱말 0, 경계 자료는 `_command`/`_query`/`_result`). 3 창구 = 3 use_case(한 area `catalog_inquiry`). 각 use case는 두 포트(`ActiveServiceBundlePort`·`RelationTablePort`)와 도메인 서비스(`FortuneVisibilityService`)를 조율한다. 공통 순서: **pin(D6) → relation_table.load(pinned generation) → 도메인 판정 → result**.

**도메인 서비스 인스턴스화 지점**(A4 확정): use case 생성자는 두 포트만 주입받는다(§12 symbols `__init__`). `FortuneVisibilityService`는 생성자 주입이 아니라 use case `execute` 본문 안에서 인스턴스화·호출한다 — 무상태·순수라 DI가 불요하고, 판정 실행 지점은 `execute`(pin·load로 사실을 모은 뒤 도메인 판정 1회)다.

### `_command`/`_query` 규약 (canonical #633/#567 — §3 명명 소유)
명명 «값»은 canonical #633/#567 소유다(«관찰 저장소 규약»이 아니다 — houserules §1.1 관찰 비입력 닫힌 목록에 명명은 없다; 명명을 관찰로 근거 세우면 향후 답습 통로가 된다). #633: OHS 공개 함수 파라미터는 계약 1개, 0개는 `_query` 위임만 — 따라서 **파라미터 유무**로 갈린다(CQRS read/write 의미가 아님): 파라미터를 받는 연산의 입력 자료는 `_command`, 파라미터 없는 연산은 `_query`(위임). #567: `dto` 낱말 0, 경계 자료는 `_command`/`_query`/`_result`. 각 use_case 폴더는 네 파일을 모두 갖고 미사용 입력 파일은 빈 파일.

1. **`list_fortune_types`** (창구① 운세 종류 전체 목록 · D40 · 입력 0)
   - 입력 파일: `list_fortune_types_query.py` = `ListFortuneTypesQuery`(무필드 frozen — 파라미터 없는 의도). `list_fortune_types_command.py` = **빈 파일**.
   - `list_fortune_types_use_case.py`: `ListFortuneTypesUseCase.execute(query) -> ListFortuneTypesResult`.
   - `list_fortune_types_result.py`: `ListFortuneTypesResult(bundle_id: str, fortune_types: tuple[FortuneType, ...])`.
2. **`select_visible_fortune_candidates`** (창구② #5 후보 조회기 · D50-2 · 입력 = 후보 id 목록)
   - 입력 파일: `select_visible_fortune_candidates_command.py` = `SelectVisibleFortuneCandidatesCommand(candidate_fortune_ids: tuple[str, ...])`. `_query.py` = **빈 파일**.
   - `_use_case.py`: `SelectVisibleFortuneCandidatesUseCase.execute(command) -> SelectVisibleFortuneCandidatesResult`.
   - `_result.py`: `SelectVisibleFortuneCandidatesResult(bundle_id: str, candidates: tuple[ClassifiedFortuneCandidate, ...])`.
3. **`resolve_fortune_support`** (창구③ #8 지원 자료 조회 · D50-1 · 입력 = 선택 운세 id)
   - 입력 파일: `resolve_fortune_support_command.py` = `ResolveFortuneSupportCommand(fortune_id: str)`. `_query.py` = **빈 파일**.
   - `_use_case.py`: `ResolveFortuneSupportUseCase.execute(command) -> ResolveFortuneSupportResult`.
   - `_result.py`: `ResolveFortuneSupportResult(bundle_id: str, support: FortuneSupport)`.

### 실패의 형상 (성공 한 벌 result · 실패는 예외 경로)
- **`_result.py`엔 성공 한 벌만**(#571 — Result variant로 실패를 설계하지 않는다). Bundle 고정 실패(D6 검증 실패)·관계표 계약 불일치는 포트가 `ActiveServiceBundleContractMismatch`/`RelationTableContractMismatch`를 raise하고, **use case는 잡지 않고 전파**한다. **OHS 서비스가 이를 잡아** unavailable 응답 variant로 변환한다(§6 — 경계에서 예외→닫힌 응답). use case 밖(OHS)에서만 예외가 응답으로 접힌다.
- **닫힌 분기(미실존 ABSENT·미지원 UNSUPPORTED)는 실패가 아니라 정상 결과**다 — `ClassifiedFortuneCandidate.status`·`FortuneSupport.status`로 도메인이 표현하고 `_result.py`가 그대로 담는다(예외 fabricate 금지 — D13). 실패(예외 경로)와 닫힌 분기(정상 결과)를 명확히 구분한다.

### DI 조립 위치
- `composition_root/dependency_wiring.py`의 `build_list_fortune_types_use_case()`·`build_select_visible_fortune_candidates_use_case()`·`build_resolve_fortune_support_use_case()`가 adapter 2종을 생성해 use case에 주입(트리 2~4행·#85). presentation(OHS)은 매요청 `build_*` 호출만 하고 인프라 어댑터를 직접 생성하지 않는다.
- **도메인 우회 읽기(`domain_bypass_query`) 미채택** — 관계표는 ORM이 아니라 프레임워크 파일 CAS이고, 조회는 포트/어댑터로 충분하다. `port/domain_bypass_query/`·`adapter/persistence/domain_bypass_query/`는 빈 골격.

---

## §5 포트 · 어댑터 (SPARQL · Bundle 고정 · Graph 주입)

두 능력을 **두 포트**로 가른다 — D6 Bundle 고정(항상 실물·약화 불가)과 관계표 Graph 조회(SPARQL·fixture 주입 가능)를 분리해, 「Bundle 고정 완료 이후의 Graph 주입 포트에서 BC 소유 fixture로 검증」(D51-3 ⑧, scope 라인 23·40)을 D6 약화 없이 실현한다.

### 포트 A — `active_service_bundle` (D6 · 항상 실물)
- `application_layer/port/active_service_bundle/`:
  - `active_service_bundle_port.py`: `ActiveServiceBundlePort(ABC)` · `pin() -> PinnedServiceBundleOut`.
  - `pinned_service_bundle_out.py`: `PinnedServiceBundleOut(bundle_id, carried_rag_ids, ontology_release_id, relation_graph_sha256)` — 전부 primitive.
  - `exception.py`: `ActiveServiceBundleContractMismatch(RuntimeError)`.
- **어댑터** `driven_layer/adapter/active_service_bundle/rag_runtime_adapter.py`: `RagRuntimeActiveServiceBundleAdapter(ActiveServiceBundlePort)`. 주입: `repository_root`·`data_root`·`load_json_object`(Protocol)·`validate_terminal_active_service_bundle`(Protocol — 리딩과 동형). 절차:
  1. `data_root/releases/service-bundles/active.json` 1회 읽기 → `state=="active"` 확인 → `service_bundle_release_id` = bundle_id.
  2. `validate_terminal_active_service_bundle(repository_root, data_root, pinned_bundle_id=bundle_id, require_terminal=True)` 호출(**D6·약화 금지** — 리딩 FR-4 동급 검증 강도).
  3. bundle descriptor(`releases/service-bundles/versions/<bundle_id>/release-descriptor.json`, `descriptor_version=="service-bundle-descriptor-v2"`) 로드 → `rag_release_refs[].rag_id` = `carried_rag_ids`(bare) · `ontology_release_ref.{id, manifest_sha256}`.
  4. ontology release manifest(`releases/ontology/versions/<ontology_release_id>/release-manifest.json`, sha256 == descriptor `ontology_release_ref.manifest_sha256`) 로드 → `artifacts`에서 `path=="graph.ttl"` 항목의 `sha256` = `relation_graph_sha256`(신뢰 사슬: active pointer → 검증된 descriptor → 검증된 manifest → graph.ttl digest).
  5. 계약 불일치는 `ActiveServiceBundleContractMismatch`로 접는다.

### 포트 B — `relation_table` (SPARQL · Graph 주입)
- `application_layer/port/relation_table/`:
  - `relation_table_port.py`: `RelationTablePort(ABC)` · `load(query) -> RelationTableFactsOut`.
  - `relation_query_in.py`: `RelationQueryIn(ontology_release_id: str, relation_graph_sha256: str)` — 포트 A가 준 고정 세대 키.
  - `relation_table_facts_out.py`: `RelationTableFactsOut(fortune_types, support_pairs, required_input_pairs)` — primitive. `fortune_types: tuple[tuple[str, tuple[tuple[str,str],...]], ...]`(fortune_id, ((lang,label),…)) · `support_pairs: tuple[tuple[str,str,str], ...]`(fortune_id, work_id, rag_id) · `required_input_pairs: tuple[tuple[str,str], ...]`(fortune_id, input_id).
  - `exception.py`: `RelationTableContractMismatch(RuntimeError)`.
- **어댑터** `driven_layer/adapter/relation_table/rag_runtime_adapter.py`: `RagRuntimeRelationTableAdapter(RelationTablePort)`. **SPARQL 본문을 소유한다**(D51-1). 주입: `data_root` · `load_relation_graph`(Protocol — `(graph_path: Path, expected_sha256: str) -> rdflib.Graph`; graph.ttl bytes를 sha256 검증 후 rdflib로 turtle 파싱). rdflib(`from rdflib import Graph`)는 어댑터가 직접 import(서드파티 SPARQL 도구, `pyproject.toml` `rdflib==7.6.0` 핀). 절차:
  1. `graph_path = data_root/releases/ontology/versions/<ontology_release_id>/graph.ttl`; `load_relation_graph(graph_path, relation_graph_sha256)` → 검증된 Graph.
  2. 3 SPARQL 질의 실행(§9) → primitive 사실로 정규화. **URN 접두 제거 bare 변환**(D51-3 ⑥): fortune `urn:spring-dream:fortune:` · input `urn:spring-dream:input:` · rag `urn:spring-dream:rag:` · work `urn:spring-dream:work:` 각 접두 제거. 접두 문자열은 **관계표 값 상수가 아니라 URN 스킴(구조)**이다(D51-3 ⑨의 금지 대상은 fortune id·input id 같은 «값» 열거이지 namespace 스킴이 아니다 — SPARQL의 `sd:` prefix와 동류).
  3. 계약 불일치·파싱 실패는 `RelationTableContractMismatch`로 접는다.
- **Graph 주입 seam**: 어댑터가 `load_relation_graph`를 주입받으므로, 필터 케이스 fixture는 «합성 graph.ttl»을 반환하는 fake `load_relation_graph`(또는 fake `RelationTablePort`)로 REAL SPARQL을 합성 관계표에 태워 검증한다(합성 turtle은 해당 어댑터/동치 테스트 모듈이 test-local helper로 인라인으로 빌드 — rdflib · #392 «테스트 안으로» · C1) — **포트 A(D6)는 손대지 않는다**(D6 약화·우회 금지·활성 Release 재생성 금지). 실물 활성표는 운세 1종(대운)뿐이라 못 거르는 «지원 서고 없는 운세·Bundle 미탑재 서고» 분기를 합성표로 실증한다. Graph 주입 seam 설계 자체(`load_relation_graph` 주입·D6 포트 A 불약화)는 불변이며, 이번 교정은 «합성 turtle의 소재 위치»만 포트 페이크(#576 위반)에서 테스트 모듈 인라인(#392)으로 옮긴다.

### 포트↔어댑터 짝·격리 (검사기 대응)
- 능력명 일치: 포트 `active_service_bundle`↔어댑터 `active_service_bundle`, 포트 `relation_table`↔어댑터 `relation_table`(#462 pairing). 어댑터는 `driven_layer/adapter/<capability>/<technology>_adapter.py` 형태(#328 isolation). ORM import 0(관계표는 파일 CAS) → §5 driven 출구 면제 대상 아님(persistence 셋 빈 골격).

---

## §6 OHS 계약 · 서비스 (닫힌 응답 · 세대 표식)

한 OHS 서비스 `catalog_inquiry`가 3 공개 함수를 호스팅한다(리딩 `citation_validation_service`가 2함수를 호스팅하는 실측 선례). 각 함수는 계약 1개(또는 0개, #633)를 받아 **닫힌 union 응답**을 반환한다. 서비스는 도메인 결과를 primitive로 미러만 한다(contract는 domain import 0 — #472/#162).

### 공개 함수 (`open_host_service/catalog_inquiry/catalog_inquiry_service.py`)
- `list_fortune_types_query() -> ListFortuneTypesResponse` — 0-param `_query` 위임(#633). `build_list_fortune_types_use_case().execute(ListFortuneTypesQuery())` 실행 → 미러.
- `select_visible_fortune_candidates_command(request: SelectVisibleFortuneCandidatesRequest) -> SelectVisibleFortuneCandidatesResponse` — 1-param `_command`.
- `resolve_fortune_support_command(request: ResolveFortuneSupportRequest) -> ResolveFortuneSupportResponse` — 1-param `_command`.
- 각 함수는 `ActiveServiceBundleContractMismatch`·`RelationTableContractMismatch`를 잡아 `_CatalogUnavailable` variant로 접는다(«검증 실패는 명시 실패» — 예외를 소비자에 흘리지 않아 반환형이 total). **원인별 리터럴·bundle_id 규칙(A3·B1 확정)**: `ActiveServiceBundleContractMismatch`(pin 단계 실패 — 세대 미확정) → `reason="bundle_unavailable"` · `bundle_id=None`; `RelationTableContractMismatch`(pin 성공 후 관계표 load 실패 — 세대는 확정됨) → `reason="relation_table_unavailable"` · `bundle_id=<고정된 bundle_id>`. 두 원인을 한 리터럴로 접지 않는다 — 진짜 다른 production failure(신뢰 사슬 실패 vs graph 파싱/검증 실패)라 wire가 구분해야 소비자 진단이 가능하다(원칙 07 명시). 이 total-return 접기(두 mismatch·bundle_id 규칙)는 OHS 계약 테스트가 검증한다(§11 «OHS 예외 접기» 행).

### 요청 계약 (`contract/request/`) — primitive
- `select_visible_fortune_candidates_request.py`: `SelectVisibleFortuneCandidatesRequest(candidate_fortune_ids: tuple[str, ...])`.
- `resolve_fortune_support_request.py`: `ResolveFortuneSupportRequest(fortune_id: str)`.
- 창구① 요청 없음(입력 0).

### 응답 계약 (`contract/response/`) — primitive 닫힌 union · `kind` 판별 · 전부 `bundle_id` 포함(D51-3 ①)
- `list_fortune_types_response.py`:
  - `_FortuneTypesListed(kind: Literal["listed"], bundle_id: str, fortune_types: tuple[_FortuneTypeValue, ...])` where `_FortuneTypeValue = tuple[str, tuple[tuple[str, str], ...]]`(fortune_id, ((lang,label),…)).
  - `_CatalogUnavailable(kind: Literal["unavailable"], bundle_id: str | None, reason: Literal["bundle_unavailable", "relation_table_unavailable"])`.
  - `type ListFortuneTypesResponse = _FortuneTypesListed | _CatalogUnavailable`.
  - **모듈 docstring이 라벨 폴백 규칙을 성문화한다**(문면 계획 — 계약 shape·필드 불변): 「labels가 비면 fortune_id를 표시 이름으로 쓴다 — 이 BC 계약이 정한 규칙, 적용은 소비자」. BC는 빈 labels를 fabricate 없이 운반하고 규칙 소유만 하며, 실제 치환·표시 언어 선택은 소비자(점집) 몫임을 이 docstring이 명시한다(§3 값 객체 규칙과 정합).
- `select_visible_fortune_candidates_response.py`:
  - `_CandidateOutcome(fortune_id: str, status: Literal["visible", "unsupported", "absent"], reason: Literal["unsupported", "stale_vocabulary"] | None)`.
  - `_CandidatesClassified(kind: Literal["classified"], bundle_id: str, candidates: tuple[_CandidateOutcome, ...])`.
  - `_CatalogUnavailable(kind: Literal["unavailable"], bundle_id: str | None, reason: Literal["bundle_unavailable", "relation_table_unavailable"])`.
  - `type SelectVisibleFortuneCandidatesResponse = _CandidatesClassified | _CatalogUnavailable`.
- `resolve_fortune_support_response.py`:
  - `_WorkRagValue = tuple[str, str]`(work_id, rag_id).
  - `_SupportResolved(kind: Literal["resolved"], bundle_id: str, fortune_id: str, work_rag_refs: tuple[_WorkRagValue, ...], required_input_ids: tuple[str, ...])`.
  - `_SupportUnavailable(kind: Literal["support_unavailable"], bundle_id: str, fortune_id: str, status: Literal["unsupported", "absent"], reason: Literal["unsupported", "stale_vocabulary"])`.
  - `_CatalogUnavailable(kind: Literal["unavailable"], bundle_id: str | None, reason: Literal["bundle_unavailable", "relation_table_unavailable"])`.
  - `type ResolveFortuneSupportResponse = _SupportResolved | _SupportUnavailable | _CatalogUnavailable`.
- `contract/exception/catalog_inquiry_published_error.py`: **빈 파일** — published 예외 없음(모든 실패는 위 union variant). `<exception>_exception.py` 없음.

### 도메인 status → 응답 reason 매핑 (서비스가 수행)
- `VISIBLE` → `_CandidateOutcome(status="visible", reason=None)` / `FortuneSupport(VISIBLE)` → `_SupportResolved`.
- `UNSUPPORTED` → `status="unsupported", reason="unsupported"` / `_SupportUnavailable(status="unsupported", reason="unsupported")`.
- `ABSENT` → `status="absent", reason="stale_vocabulary"` / `_SupportUnavailable(status="absent", reason="stale_vocabulary")`.
- *왜* — 닫힌 판정 enum은 **도메인 소유**(§3, 비즈니스 규칙), 경계 닫힌 carrier는 **OHS 응답 union의 primitive Literal**(#93 — 구동 층이 예외/결과 분류 소유). 별도 빈혈 application enum을 두지 않아 판정 이중화를 피한다(architect 지시 point 6과의 정합: «application 소유 닫힌 enum·carrier»의 carrier = OHS 응답 union이 그 자리다).
- reason 어휘(`unsupported`·`stale_vocabulary`·`bundle_unavailable`·`relation_table_unavailable`)는 **BC 자신의 닫힌 상태 어휘**이지 관계표 «값»(fortune id·input id)이 아니다 → D51-3 ⑨ 위반 아님(코드 상수 금지의 주어는 관계표 값 열거).

---

## §7 닫힌 응답 분기 (D13) — HTTP status/ErrorSchema N/A

- #5·#8의 **미실존(ABSENT)·미지원(UNSUPPORTED)** id는 예외가 아니라 **닫힌 응답 분기**다 — id별 상태 + 원인 코드로 응답 union에 담는다(위 §6). HTTP surface가 없으므로 HTTP status·`ErrorSchema`·`response` 광고는 **N/A**이고, 오류·닫힌 결과는 OHS 반환형의 닫힌 결과 타입으로만 표현한다.
- 세대 표식 `bundle_id`는 성공·닫힌분기 variant 전부에 포함(D51-3 ①); `_CatalogUnavailable`만 `bundle_id: str | None`이다 — pin 실패(`reason=bundle_unavailable`)는 세대 미확정이라 `None`, 관계표 load 실패(`reason=relation_table_unavailable`)는 pin 성공 뒤라 고정된 `bundle_id`를 담는다(§6 원인별 규칙 · A3). 방문 내 세대 일관성은 점집 책임(불일치 감지 시 창구①부터 재시작 — 리딩 FR-2 `requested_bundle_ref` 공급원).
- 뒤처리(2개↑ 선택지·1개 자동·0개 #9 안내·재시작·질문 문구·폼)는 점집·계산 19행 소유 — 이 BC는 id 목록·상태만 낸다.

---

## §8 레거시 0 (D37) · `ontology_service.py` 잔여 보고 (D51-2 — 보고만)

### 레거시 0 결과 제약
- `application/fortune_catalog/**`에서 `framework/technology/rag/runtime/ontology_service.py` **import 0**. 조회는 전부 신규 구현. Bundle 고정은 별도 모듈 `service_runtime.validate_terminal_active_service_bundle` + `ontology_canonical.load_json_object`만 쓴다(D51-2 ② — 별도 모듈이라 양립).
- **관계표 값 코드 상수 0**: 운세 id·필요 입력 id·rag id를 코드 상수로 박지 않는다(D51-3 ⑨). 모든 값은 런타임에 관계표 SPARQL·descriptor에서 얻는다. 허용되는 구조 상수: URN namespace 스킴 접두(§5), SPARQL 질의 본문의 vocabulary prefix, descriptor/manifest 스키마 키.
- 호환층·이중경로·옛 이름 0(출시 전 레거시 금지).

### `ontology_service.py` 잔여 실측 열거 (import·수정 금지 · 보고 전용)
`framework/technology/rag/runtime/ontology_service.py`(1529행)는 16행 소비부 분리 후에도 **C11 활성화·rollback·fixture 실행 도구**로 잔존한다(가이드 소유, 삭제 없음). 이 BC는 이 파일을 import하지 않는다. 잔여 최상위 심볼(실측):
- **LLM 구조화 출력 provider**: `LLMConfigurationError` · `CitedAnswerProvider`(Protocol) · `ResolvedLLMConfiguration` · `OpenAIResponsesProvider` · `resolve_llm_configuration` · `prepare_openai_structured_output_schema`.
- **C11 검증·fixture 실행**: `execute_shadow_request` · `evaluate_service_registry_boundary` · `execute_service_fixture` · `record_c11_readiness_block` · `ActivationResult` · `C11BlockedAttempt` · `_assert_service_lock_order` · `_validate_citations` · `_not_called`.
- **C11 활성화·rollback(durable CAS)**: `DurableWriteInterrupted` · `_activate_genesis_service_bundle` · `_activate_bundle_service_bundle` · `_recover_desired_pointer` · `_activation_record` · `_recover_or_apply_genesis_rollback` · `_recover_genesis_activation_state` · `_replace_durable` · `_write_recoverable_immutable_json` · `_identity_record`.
- 이 파일은 `rdflib.{Graph, URIRef}`를 import하고 SPARQL을 내부 사용하며(C11 출판 질의 실행), `service_runtime`에서 `validate_terminal_active_service_bundle`·`validate_admitted_service_bundle`·`_unique_record_path`·`_validate_identity_record`를 재수입한다. 잔여는 **온톨로지 가이드 C11 도구**로 존치(발주 범위 밖 — 삭제·이동 없음).

---

## §9 질의 팩 의미 동치 설계 (D51-1)

### BC 소유 SPARQL (driven adapter `relation_table/rag_runtime_adapter.py`)
관계표는 N-Triples/turtle(rdflib `format=turtle` 파싱). 속성 namespace `sd: <urn:spring-dream:ontology:>`, skos `<http://www.w3.org/2004/02/skos/core#>`. 실물 활성표(ontology release `2f833602…`) 트리플 형상(실측): FortuneType `<urn:spring-dream:fortune:saju.luck-cycle>`(prefLabel "대운"@ko · requiresInput birth-datetime/birth-place/sex) · Rag `<urn:spring-dream:rag:saju.theory.yeonhae-japyeong>`(ragForWork `…work:saju.work.yeonhae-japyeong` · supportsFortune `…fortune:saju.luck-cycle`).

- **Q1 운세 종류+라벨** (창구①): `?f a sd:FortuneType ; skos:inScheme sd:fortune-types .` + `OPTIONAL { ?f skos:prefLabel ?label . BIND(LANG(?label) AS ?lang) }`. → (fortune_id bare, ((lang,label),…)).
- **Q2 지원 쌍** (창구②·③ 핵심): `?rag a sd:Rag ; sd:supportsFortune ?fortune ; sd:ragForWork ?work .` → 어댑터가 **`support_pairs` 정본 순서 `(fortune_id, work_id, rag_id)`**로 정규화한다(A1 확정 — §5 `relation_table_facts_out`·§3 판정 규칙·§12 symbols와 튜플 위치 일치; work·rag 스왑 금지). 도메인이 fortune·carried_rag_ids로 필터.
- **Q3 필요 입력** (창구③): `?f a sd:FortuneType ; sd:requiresInput ?input .` → (fortune, input).

### 팩 질의 의미 동치 테스트 (BC 소유 fixture)
- 팩 `spring-dream-saju-service-queries@1.1.0`의 `select-rags-by-fortune.rq`(실측 본문): `SELECT ?rag ?work WHERE { ?rag a sd:Rag ; sd:supportsFortune ?fortune ; sd:ragForWork ?work . FILTER (?fortune = ?fortune_parameter) } ORDER BY STR(?rag) STR(?work) LIMIT 20` — 팩은 **C11 출판 검증 전용**(query_contract_ref). 이 BC는 팩을 실행·수정하지 않는다.
- **동치 테스트**(BC 소유 fixture): 같은 관계표(실물 활성표 + `test_pack_query_equivalence.py`가 test-local helper로 인라인 빌드한 합성 turtle · #392)에 ⓐ BC Q2를 특정 fortune으로 투영한 (rag, work) 집합과 ⓑ 팩 `select-rags-by-fortune.rq`를 그 fortune으로 initBinding 실행한 (rag, work) 집합이 **일치**함을 단언. 팩 질의는 namespace-무관(fortune_parameter 바인딩)이라 BC 소유 fixture(실물 URN 스킴 `urn:spring-dream:fortune:` 등)에서 참조 실행 가능. BC 질의가 출판 검사 기준에서 드리프트하면 **Red**.
- fixture는 팩 질의 파일(`…/query-packs/spring-dream-saju-service-queries/1.1.0/queries/select-rags-by-fortune.rq`)을 **Path로 읽어 참조 실행**만(import·실행 도구 수정 없음).

### SPARQL 실행 도구
- `rdflib==7.6.0`(`pyproject.toml` 실측 핀 — RDF 1.1 strict·SPARQL 1.1·SELECT/ASK/initBindings). 신규 런타임 의존성 추가 없음(이미 있음). 어댑터가 직접 import.

---

## §10 제품 구현 슬라이스 도출 근거 (bottom-up 의존 순서)

계층 의존: domain ← application(port·use case) ← driven adapter(구현 port) + OHS(use case 소비, composition 경유). 아래는 슬라이스 경계 도출 근거이며 실제 슬라이싱은 coordinator가 확정한다.

- **슬라이스 0 — 골격**: BC 표준 트리 빈 골격 전부(고정·재등장 칸 `__init__.py`/빈 파일) + `django_fortune_catalog/apps.py`(`FortuneCatalogConfig`) + `settings/base.py` INSTALLED_APPS 1줄. 검증: `check-layer-skeleton` green(신규 BC 골격). 무의존.
- **슬라이스 1 — 도메인**: `shared_value_object/`(FortuneType·FortuneVisibilityStatus·ClassifiedFortuneCandidate·WorkRagRef·FortuneSupport) + `domain_service/classify_fortune_visibility.py`. 의존: 없음(순수). 테스트: 도메인 서비스 판정(가시성·지원·닫힌분기) 단위(coder).
- **슬라이스 2 — 응용 포트·유스케이스**: `port/active_service_bundle/`·`port/relation_table/`(ABC·out·in·exception) + `catalog_inquiry/{list_fortune_types,select_visible_fortune_candidates,resolve_fortune_support}/`(use_case·command/query/result) + `test/fake/`(**포트 페이크 2종** — `active_service_bundle_port.py`(포트 A 짝)·`relation_table_port.py`(포트 B 짝) · `<capability>_port.py` 명명 #576/#462). 의존: 슬라이스 1. 테스트: use case 조율(fake 포트로 pin→load→판정→result) + 닫힌분기·pin실패 전파(coder).
- **슬라이스 3 — driven 어댑터(SPARQL·Bundle)**: `adapter/active_service_bundle/rag_runtime_adapter.py`(D6 pin·신뢰 사슬) + `adapter/relation_table/rag_runtime_adapter.py`(graph load/verify·3 SPARQL·bare 변환). 의존: 슬라이스 2(포트 구현). 테스트: 실물 활성표 조회 + fixture 필터 케이스(합성 turtle은 `test_relation_table_adapter_synthetic.py`가 test-local helper로 인라인 빌드 · #392 · C1) + 팩 질의 의미 동치(`test_pack_query_equivalence.py`도 합성 graph 인라인 빌드)(coder). 이 슬라이스는 `test/fake/`에 새 파일을 만들지 않는다(포트 페이크 2종은 슬라이스 2 소유).
- **슬라이스 4 — OHS·composition**: `open_host_service/catalog_inquiry/`(service·contract request/response/exception) + `composition_root/dependency_wiring.py`(build_* 3). 의존: 슬라이스 2·3. 테스트: OHS 계약 fixture(primitive mirror·세대 표식·닫힌분기 shape)·소비자 typecheck(acceptance-tester).

---

## §11 영구 테스트 입장 표 (discipline-tdd §5.5)

신규 BC라 대부분 `add`. 각 후보는 보호 계약·독자 production failure·기존 authoritative coverage를 판정. framework/private/test-tool mechanics·migration은 `reject` 방향(해당 없음). 물리 신호 어노테이션(마커·베이스·클라이언트)을 `owner/path` 셀에 병기 — 이 BC 테스트는 **DB 미사용**(관계표는 파일 CAS)이라 `[markers: none] [base: none] [client: no]`(postgresql 마커·django_db 없음). **완료 조건 5종은 ★로 표시된 6 테스트가 분담한다**(B2): 「필터 케이스」완료 조건 1종을 도메인 판정 테스트(row 2)와 SPARQL 경유 테스트(row 3)가 나눠 검증하므로 ★ 6개·조건 5종이다.

| candidate | protected contract/evidence | unique production failure | existing authoritative coverage | decision | owner/path |
|---|---|---|---|---|---|
| ★활성 관계표 실물 조회(대운·yeonhae 지원쌍·필요입력 3종·라벨 대운@ko) | 실물 활성 Bundle(ontology `2f833602…`) 관계표 사실이 BC 조회로 정확히 나온다 · **`support_pairs` 튜플 위치별 단언 `(fortune, work, rag)`**(work·rag 스왑을 Red로 검출 · A1) | 어댑터가 실물 graph.ttl을 잘못 파싱/변환하면 오조회 | 없음(신규 BC) | add | coder · `test/unit/test_active_relation_table_adapter.py` [markers: none] [base: none] [client: no] |
| ★fixture 필터 케이스(지원 서고 없는 운세→UNSUPPORTED · Bundle 미탑재 서고→제외 · 미실존→ABSENT) | 가시성 판정이 carried_rag_ids∩support로 정확히 거른다(D51-3 ②) · **`resolve_support` VISIBLE 시 `work_rag_refs`가 탑재분(rag∈carried_rag_ids)만 담음** — 탑재/미탑재 서고 혼재 fortune 케이스로 검증(A2) | 필터 규칙 오류 시 미탑재 서고 노출/누락 | 없음 | add | coder · `test/unit/test_fortune_visibility_service.py` [markers: none] [base: none] [client: no] |
| ★필터 케이스 SPARQL 경유(합성 graph 주입·D6 불약화 · 합성 turtle은 이 모듈이 #392 인라인 빌드) | REAL SPARQL이 합성 관계표에서 사실을 정확히 추출 · **`support_pairs` `(fortune, work, rag)` 위치 단언**(work·rag 스왑 Red · A1) | 합성표에서 SPARQL/bare 변환 오류 | 없음 | add | coder · `test/unit/test_relation_table_adapter_synthetic.py` [markers: none] [base: none] [client: no] |
| ★팩 질의 의미 동치(BC Q2 ↔ `select-rags-by-fortune.rq`) | BC 질의가 팩 출판 기준에서 드리프트하지 않음(D51-1) | 질의 드리프트 시 출판 검증과 불일치 | 없음 | add | coder · `test/unit/test_pack_query_equivalence.py` [markers: none] [base: none] [client: no] |
| ★세대 표식(3 창구 응답 전부 bundle_id 포함) | D51-3 ① 세대 일관성 공급원 계약 | bundle_id 누락 시 점집 세대 불일치 미감지 | 없음 | add | acceptance-tester · `test/unit/test_catalog_inquiry_contract.py` [markers: none] [base: none] [client: no] |
| ★닫힌 분기 케이스(#5·#8 미실존→stale_vocabulary·미지원→unsupported) | D13 닫힌 답 계약(예외 아님·상태+원인) | 닫힌분기 오류 시 예외 누출/오분류 | 없음 | add | acceptance-tester · `test/unit/test_catalog_inquiry_contract.py` [markers: none] [base: none] [client: no] |
| OHS 계약 primitive mirror(응답에 domain 객체·금지 필드 0) | contract는 stdlib·같은 BC contract만(#472/#162) | domain 누출 시 경계 오염 | 없음 | add | acceptance-tester · `test/unit/test_catalog_inquiry_contract.py` [markers: none] [base: none] [client: no] |
| OHS 소비자 typecheck(계약만으로 소비 가능) | 소비자 부재 상태 계약 완결성(mypy 게이트) | 계약 불완전 시 소비 불가 | 없음 | add | acceptance-tester · `test/unit/typecheck_catalog_inquiry_open_host_service_consumer.py` [markers: none] [base: none] [client: no] |
| Bundle 고정 실패→어댑터 예외 raise(pin 신뢰 사슬 검출) | D6 신뢰 사슬(active→descriptor→manifest→graph.ttl) 위반 시 어댑터 `pin()`이 `ActiveServiceBundleContractMismatch`를 raise(§5 어댑터 — OHS 접기 아님) | pin 실패 은닉 시 stale 조회 | 없음 | add | coder · `test/unit/test_active_service_bundle_adapter.py` [markers: none] [base: none] [client: no] |
| OHS 예외 접기(두 mismatch→`_CatalogUnavailable` total-return) | OHS total-return(§6 예외 비누출): `ActiveServiceBundleContractMismatch`→`bundle_id=None·reason=bundle_unavailable` · `RelationTableContractMismatch`→`bundle_id=고정값·reason=relation_table_unavailable` | 예외가 소비자에 누출되면 반환형 비-total | 없음 | add | acceptance-tester · `test/unit/test_catalog_inquiry_contract.py` [markers: none] [base: none] [client: no] |
| 빈 labels 수용·불변 운반(라벨 fabricate 없음) | 관계표 SHACL 라벨 미강제 시 도메인이 빈 labels를 그대로(불변) 운반 · id 폴백 규칙은 BC 계약 소유(적용은 소비자)(§3 · A5/B3) | 라벨 fabricate 시 BC가 표시 언어를 임의 선택 | 없음 | add | coder · `test/unit/test_fortune_type.py` [markers: none] [base: none] [client: no] |
| use case 조율(pin→load→판정→result 순서·1 pin) | 응용 흐름 계약(§4·§3.6) | 순서/중복 pin 오류 | 없음 | add | coder · `test/unit/test_catalog_inquiry_use_cases.py` [markers: none] [base: none] [client: no] |
| migration/framework mechanics | — | — | — | reject | — (해당 없음 · migration 0) |

**계약 근거 추적**: 위 행들의 현재 계약은 발주서 완료 조건 5종(★) + 공통 규율(세대 표식·닫힌분기·bare id·D6 강도) + primitive mirror 규범(#472/#162)이다. 종료·부재 의무 없음(신규 BC — 종료 대상 계약 0).

**decision별 개수**: `add` 12 · `reject` 1(migration/framework mechanics — 해당 없음) · `pending` 0(입장 심사 완료) · `update`·`reuse`·`retain`·`remove` 0(기존 artifact 없음 — 신규 BC). `pending` 0이므로 G1 요청 가능. (개수는 **영구 test artifact = 위 12 테스트 모듈 행**만 센다 — `test/fake/`의 포트 페이크 2종과 합성 turtle의 test-local 인라인 helper는 테스트 «재료/스캐폴딩»이라 입장 심사 행이 아니다. 따라서 `relation_graph_fake.py` 제거는 개수를 바꾸지 않는다.)

---

## §12 기계가독 채널 (pre-gate 전사 정본)

산문과 별개의 정본. 부재 = fail-closed 부재 전사. 아래 concrete 계획 블록에만 `machine` 마커를 단다.

### 파일 계획

<!-- machine: file-plan -->
```paths
# BC 루트
empty application/fortune_catalog/__init__.py
# composition_root
empty application/fortune_catalog/composition_root/__init__.py
add application/fortune_catalog/composition_root/dependency_wiring.py
empty application/fortune_catalog/composition_root/event_wiring.py
# published_event (이벤트 없음)
empty application/fortune_catalog/published_event/__init__.py
# driving_layer/api (HTTP 0 — api_router·bc_error_schema 빈 파일)
empty application/fortune_catalog/driving_layer/__init__.py
empty application/fortune_catalog/driving_layer/api/__init__.py
empty application/fortune_catalog/driving_layer/api/api_router.py
empty application/fortune_catalog/driving_layer/api/bc_error_schema.py
empty application/fortune_catalog/driving_layer/api/webhook/__init__.py
# driving_layer/open_host_service/catalog_inquiry
empty application/fortune_catalog/driving_layer/open_host_service/__init__.py
empty application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/__init__.py
add application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/catalog_inquiry_service.py
empty application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/contract/__init__.py
empty application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/contract/request/__init__.py
add application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/contract/request/select_visible_fortune_candidates_request.py
add application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/contract/request/resolve_fortune_support_request.py
empty application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/contract/response/__init__.py
add application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/contract/response/list_fortune_types_response.py
add application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/contract/response/select_visible_fortune_candidates_response.py
add application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/contract/response/resolve_fortune_support_response.py
empty application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/contract/exception/__init__.py
empty application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/contract/exception/catalog_inquiry_published_error.py
# driving_layer/cron_job·event_subscription (빈)
empty application/fortune_catalog/driving_layer/cron_job/__init__.py
empty application/fortune_catalog/driving_layer/event_subscription/__init__.py
empty application/fortune_catalog/driving_layer/event_subscription/event_router.py
# application_layer/catalog_inquiry — use cases
empty application/fortune_catalog/application_layer/__init__.py
empty application/fortune_catalog/application_layer/catalog_inquiry/__init__.py
empty application/fortune_catalog/application_layer/catalog_inquiry/list_fortune_types/__init__.py
add application/fortune_catalog/application_layer/catalog_inquiry/list_fortune_types/list_fortune_types_use_case.py
empty application/fortune_catalog/application_layer/catalog_inquiry/list_fortune_types/list_fortune_types_command.py
add application/fortune_catalog/application_layer/catalog_inquiry/list_fortune_types/list_fortune_types_query.py
add application/fortune_catalog/application_layer/catalog_inquiry/list_fortune_types/list_fortune_types_result.py
empty application/fortune_catalog/application_layer/catalog_inquiry/select_visible_fortune_candidates/__init__.py
add application/fortune_catalog/application_layer/catalog_inquiry/select_visible_fortune_candidates/select_visible_fortune_candidates_use_case.py
add application/fortune_catalog/application_layer/catalog_inquiry/select_visible_fortune_candidates/select_visible_fortune_candidates_command.py
empty application/fortune_catalog/application_layer/catalog_inquiry/select_visible_fortune_candidates/select_visible_fortune_candidates_query.py
add application/fortune_catalog/application_layer/catalog_inquiry/select_visible_fortune_candidates/select_visible_fortune_candidates_result.py
empty application/fortune_catalog/application_layer/catalog_inquiry/resolve_fortune_support/__init__.py
add application/fortune_catalog/application_layer/catalog_inquiry/resolve_fortune_support/resolve_fortune_support_use_case.py
add application/fortune_catalog/application_layer/catalog_inquiry/resolve_fortune_support/resolve_fortune_support_command.py
empty application/fortune_catalog/application_layer/catalog_inquiry/resolve_fortune_support/resolve_fortune_support_query.py
add application/fortune_catalog/application_layer/catalog_inquiry/resolve_fortune_support/resolve_fortune_support_result.py
# application_layer/port
empty application/fortune_catalog/application_layer/port/__init__.py
empty application/fortune_catalog/application_layer/port/active_service_bundle/__init__.py
add application/fortune_catalog/application_layer/port/active_service_bundle/active_service_bundle_port.py
add application/fortune_catalog/application_layer/port/active_service_bundle/pinned_service_bundle_out.py
add application/fortune_catalog/application_layer/port/active_service_bundle/exception.py
empty application/fortune_catalog/application_layer/port/relation_table/__init__.py
add application/fortune_catalog/application_layer/port/relation_table/relation_table_port.py
add application/fortune_catalog/application_layer/port/relation_table/relation_query_in.py
add application/fortune_catalog/application_layer/port/relation_table/relation_table_facts_out.py
add application/fortune_catalog/application_layer/port/relation_table/exception.py
empty application/fortune_catalog/application_layer/port/domain_bypass_query/__init__.py
empty application/fortune_catalog/application_layer/port/unit_of_work/__init__.py
# domain_layer
empty application/fortune_catalog/domain_layer/__init__.py
empty application/fortune_catalog/domain_layer/shared_value_object/__init__.py
add application/fortune_catalog/domain_layer/shared_value_object/fortune_type.py
add application/fortune_catalog/domain_layer/shared_value_object/fortune_visibility_status.py
add application/fortune_catalog/domain_layer/shared_value_object/classified_fortune_candidate.py
add application/fortune_catalog/domain_layer/shared_value_object/work_rag_ref.py
add application/fortune_catalog/domain_layer/shared_value_object/fortune_support.py
empty application/fortune_catalog/domain_layer/domain_service/__init__.py
add application/fortune_catalog/domain_layer/domain_service/classify_fortune_visibility.py
# driven_layer/adapter
empty application/fortune_catalog/driven_layer/__init__.py
empty application/fortune_catalog/driven_layer/adapter/__init__.py
empty application/fortune_catalog/driven_layer/adapter/active_service_bundle/__init__.py
add application/fortune_catalog/driven_layer/adapter/active_service_bundle/rag_runtime_adapter.py
empty application/fortune_catalog/driven_layer/adapter/relation_table/__init__.py
add application/fortune_catalog/driven_layer/adapter/relation_table/rag_runtime_adapter.py
empty application/fortune_catalog/driven_layer/adapter/persistence/__init__.py
empty application/fortune_catalog/driven_layer/adapter/persistence/repository/__init__.py
empty application/fortune_catalog/driven_layer/adapter/persistence/domain_bypass_query/__init__.py
empty application/fortune_catalog/driven_layer/adapter/persistence/unit_of_work/__init__.py
empty application/fortune_catalog/driven_layer/adapter/anticorruption_layer/__init__.py
empty application/fortune_catalog/driven_layer/adapter/external_system/__init__.py
# driven_layer/django_fortune_catalog (모델 0·migration 0)
empty application/fortune_catalog/driven_layer/django_fortune_catalog/__init__.py
add application/fortune_catalog/driven_layer/django_fortune_catalog/apps.py
empty application/fortune_catalog/driven_layer/django_fortune_catalog/models/__init__.py
empty application/fortune_catalog/driven_layer/django_fortune_catalog/migrations/__init__.py
empty application/fortune_catalog/driven_layer/django_fortune_catalog/admin/__init__.py
# test
empty application/fortune_catalog/test/__init__.py
empty application/fortune_catalog/test/unit/__init__.py
empty application/fortune_catalog/test/integration/__init__.py
empty application/fortune_catalog/test/e2e/__init__.py
empty application/fortune_catalog/test/factories/__init__.py
empty application/fortune_catalog/test/fake/__init__.py
add application/fortune_catalog/test/fake/active_service_bundle_port.py
add application/fortune_catalog/test/fake/relation_table_port.py
add application/fortune_catalog/test/unit/test_active_relation_table_adapter.py
add application/fortune_catalog/test/unit/test_fortune_visibility_service.py
add application/fortune_catalog/test/unit/test_relation_table_adapter_synthetic.py
add application/fortune_catalog/test/unit/test_pack_query_equivalence.py
add application/fortune_catalog/test/unit/test_catalog_inquiry_contract.py
add application/fortune_catalog/test/unit/test_active_service_bundle_adapter.py
add application/fortune_catalog/test/unit/test_fortune_type.py
add application/fortune_catalog/test/unit/test_catalog_inquiry_use_cases.py
add application/fortune_catalog/test/unit/typecheck_catalog_inquiry_open_host_service_consumer.py
# settings 등록 (INSTALLED_APPS 1줄)
update spring_dream_server/settings/base.py
```

### 공개 심볼

tuple/union 타입 별칭(`type ...Response`, `_*Value`)은 아래 필드에 인라인 전개(별칭 dangling 방지). 응답 union 별칭은 산문 §6이 정의하며, pre-gate 전사 대상 concrete 클래스(변형·필드)를 아래 전수한다. 괄호·대괄호 안 콤마는 필드 구분자가 아니다(bracket-aware).

<!-- machine: symbols -->
```symbols
# domain — shared_value_object
application/fortune_catalog/domain_layer/shared_value_object/fortune_visibility_status.py::FortuneVisibilityStatus(StrEnum) {VISIBLE = "visible", UNSUPPORTED = "unsupported", ABSENT = "absent"}
application/fortune_catalog/domain_layer/shared_value_object/fortune_type.py::FortuneType {fortune_id: str, labels: tuple[tuple[str, str], ...]}
application/fortune_catalog/domain_layer/shared_value_object/classified_fortune_candidate.py::ClassifiedFortuneCandidate {fortune_id: str, status: FortuneVisibilityStatus}
application/fortune_catalog/domain_layer/shared_value_object/work_rag_ref.py::WorkRagRef {work_id: str, rag_id: str}
application/fortune_catalog/domain_layer/shared_value_object/fortune_support.py::FortuneSupport {fortune_id: str, status: FortuneVisibilityStatus, work_rag_refs: tuple[WorkRagRef, ...], required_input_ids: tuple[str, ...]}
# domain — domain_service
application/fortune_catalog/domain_layer/domain_service/classify_fortune_visibility.py::FortuneVisibilityService
application/fortune_catalog/domain_layer/domain_service/classify_fortune_visibility.py::FortuneVisibilityService.classify_candidates(candidate_fortune_ids: tuple[str, ...], present_fortune_ids: frozenset[str], support_pairs: tuple[tuple[str, str, str], ...], carried_rag_ids: frozenset[str]) -> tuple[ClassifiedFortuneCandidate, ...]
application/fortune_catalog/domain_layer/domain_service/classify_fortune_visibility.py::FortuneVisibilityService.resolve_support(fortune_id: str, present_fortune_ids: frozenset[str], support_pairs: tuple[tuple[str, str, str], ...], required_input_pairs: tuple[tuple[str, str], ...], carried_rag_ids: frozenset[str]) -> FortuneSupport
# application — port/active_service_bundle
application/fortune_catalog/application_layer/port/active_service_bundle/active_service_bundle_port.py::ActiveServiceBundlePort(ABC)
application/fortune_catalog/application_layer/port/active_service_bundle/active_service_bundle_port.py::ActiveServiceBundlePort.pin() -> PinnedServiceBundleOut
application/fortune_catalog/application_layer/port/active_service_bundle/pinned_service_bundle_out.py::PinnedServiceBundleOut {bundle_id: str, carried_rag_ids: tuple[str, ...], ontology_release_id: str, relation_graph_sha256: str}
application/fortune_catalog/application_layer/port/active_service_bundle/exception.py::ActiveServiceBundleContractMismatch(RuntimeError)
# application — port/relation_table
application/fortune_catalog/application_layer/port/relation_table/relation_table_port.py::RelationTablePort(ABC)
application/fortune_catalog/application_layer/port/relation_table/relation_table_port.py::RelationTablePort.load(query: RelationQueryIn) -> RelationTableFactsOut
application/fortune_catalog/application_layer/port/relation_table/relation_query_in.py::RelationQueryIn {ontology_release_id: str, relation_graph_sha256: str}
application/fortune_catalog/application_layer/port/relation_table/relation_table_facts_out.py::RelationTableFactsOut {fortune_types: tuple[tuple[str, tuple[tuple[str, str], ...]], ...], support_pairs: tuple[tuple[str, str, str], ...], required_input_pairs: tuple[tuple[str, str], ...]}
application/fortune_catalog/application_layer/port/relation_table/exception.py::RelationTableContractMismatch(RuntimeError)
# application — use cases
application/fortune_catalog/application_layer/catalog_inquiry/list_fortune_types/list_fortune_types_query.py::ListFortuneTypesQuery
application/fortune_catalog/application_layer/catalog_inquiry/list_fortune_types/list_fortune_types_result.py::ListFortuneTypesResult {bundle_id: str, fortune_types: tuple[FortuneType, ...]}
application/fortune_catalog/application_layer/catalog_inquiry/list_fortune_types/list_fortune_types_use_case.py::ListFortuneTypesUseCase
application/fortune_catalog/application_layer/catalog_inquiry/list_fortune_types/list_fortune_types_use_case.py::ListFortuneTypesUseCase.__init__(active_service_bundle_port: ActiveServiceBundlePort, relation_table_port: RelationTablePort) -> None
application/fortune_catalog/application_layer/catalog_inquiry/list_fortune_types/list_fortune_types_use_case.py::ListFortuneTypesUseCase.execute(query: ListFortuneTypesQuery) -> ListFortuneTypesResult
application/fortune_catalog/application_layer/catalog_inquiry/select_visible_fortune_candidates/select_visible_fortune_candidates_command.py::SelectVisibleFortuneCandidatesCommand {candidate_fortune_ids: tuple[str, ...]}
application/fortune_catalog/application_layer/catalog_inquiry/select_visible_fortune_candidates/select_visible_fortune_candidates_result.py::SelectVisibleFortuneCandidatesResult {bundle_id: str, candidates: tuple[ClassifiedFortuneCandidate, ...]}
application/fortune_catalog/application_layer/catalog_inquiry/select_visible_fortune_candidates/select_visible_fortune_candidates_use_case.py::SelectVisibleFortuneCandidatesUseCase
application/fortune_catalog/application_layer/catalog_inquiry/select_visible_fortune_candidates/select_visible_fortune_candidates_use_case.py::SelectVisibleFortuneCandidatesUseCase.__init__(active_service_bundle_port: ActiveServiceBundlePort, relation_table_port: RelationTablePort) -> None
application/fortune_catalog/application_layer/catalog_inquiry/select_visible_fortune_candidates/select_visible_fortune_candidates_use_case.py::SelectVisibleFortuneCandidatesUseCase.execute(command: SelectVisibleFortuneCandidatesCommand) -> SelectVisibleFortuneCandidatesResult
application/fortune_catalog/application_layer/catalog_inquiry/resolve_fortune_support/resolve_fortune_support_command.py::ResolveFortuneSupportCommand {fortune_id: str}
application/fortune_catalog/application_layer/catalog_inquiry/resolve_fortune_support/resolve_fortune_support_result.py::ResolveFortuneSupportResult {bundle_id: str, support: FortuneSupport}
application/fortune_catalog/application_layer/catalog_inquiry/resolve_fortune_support/resolve_fortune_support_use_case.py::ResolveFortuneSupportUseCase
application/fortune_catalog/application_layer/catalog_inquiry/resolve_fortune_support/resolve_fortune_support_use_case.py::ResolveFortuneSupportUseCase.__init__(active_service_bundle_port: ActiveServiceBundlePort, relation_table_port: RelationTablePort) -> None
application/fortune_catalog/application_layer/catalog_inquiry/resolve_fortune_support/resolve_fortune_support_use_case.py::ResolveFortuneSupportUseCase.execute(command: ResolveFortuneSupportCommand) -> ResolveFortuneSupportResult
# driven — adapters
application/fortune_catalog/driven_layer/adapter/active_service_bundle/rag_runtime_adapter.py::_JsonObjectLoader(Protocol)
application/fortune_catalog/driven_layer/adapter/active_service_bundle/rag_runtime_adapter.py::_JsonObjectLoader.__call__(path: Path) -> dict[str, object]
application/fortune_catalog/driven_layer/adapter/active_service_bundle/rag_runtime_adapter.py::_TerminalActiveBundleValidator(Protocol)
application/fortune_catalog/driven_layer/adapter/active_service_bundle/rag_runtime_adapter.py::_TerminalActiveBundleValidator.__call__(repository_root: Path, data_root: Path, pinned_bundle_id: str, require_terminal: bool) -> dict[str, object]
application/fortune_catalog/driven_layer/adapter/active_service_bundle/rag_runtime_adapter.py::RagRuntimeActiveServiceBundleAdapter(ActiveServiceBundlePort)
application/fortune_catalog/driven_layer/adapter/active_service_bundle/rag_runtime_adapter.py::RagRuntimeActiveServiceBundleAdapter.__init__(repository_root: Path, data_root: Path, load_json_object: _JsonObjectLoader, validate_terminal_active_service_bundle: _TerminalActiveBundleValidator) -> None
application/fortune_catalog/driven_layer/adapter/active_service_bundle/rag_runtime_adapter.py::RagRuntimeActiveServiceBundleAdapter.pin() -> PinnedServiceBundleOut
application/fortune_catalog/driven_layer/adapter/relation_table/rag_runtime_adapter.py::_RelationGraphLoader(Protocol)
application/fortune_catalog/driven_layer/adapter/relation_table/rag_runtime_adapter.py::_RelationGraphLoader.__call__(graph_path: Path, expected_sha256: str) -> Graph
application/fortune_catalog/driven_layer/adapter/relation_table/rag_runtime_adapter.py::RagRuntimeRelationTableAdapter(RelationTablePort)
application/fortune_catalog/driven_layer/adapter/relation_table/rag_runtime_adapter.py::RagRuntimeRelationTableAdapter.__init__(data_root: Path, load_relation_graph: _RelationGraphLoader) -> None
application/fortune_catalog/driven_layer/adapter/relation_table/rag_runtime_adapter.py::RagRuntimeRelationTableAdapter.load(query: RelationQueryIn) -> RelationTableFactsOut
# driven — django app config
application/fortune_catalog/driven_layer/django_fortune_catalog/apps.py::FortuneCatalogConfig(AppConfig) {default_auto_field: str = "django.db.models.BigAutoField", name: str = "application.fortune_catalog.driven_layer.django_fortune_catalog", label: str = "fortune_catalog"}
# driving — OHS contract request (published-language · 필드 목록)
application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/contract/request/select_visible_fortune_candidates_request.py::SelectVisibleFortuneCandidatesRequest {candidate_fortune_ids: tuple[str, ...]}
application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/contract/request/resolve_fortune_support_request.py::ResolveFortuneSupportRequest {fortune_id: str}
# driving — OHS contract response (published-language · 닫힌 union 변형 전수)
application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/contract/response/list_fortune_types_response.py::_FortuneTypesListed {kind: Literal["listed"], bundle_id: str, fortune_types: tuple[tuple[str, tuple[tuple[str, str], ...]], ...]}
application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/contract/response/list_fortune_types_response.py::_CatalogUnavailable {kind: Literal["unavailable"], bundle_id: str | None, reason: Literal["bundle_unavailable", "relation_table_unavailable"]}
application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/contract/response/select_visible_fortune_candidates_response.py::_CandidateOutcome {fortune_id: str, status: Literal["visible", "unsupported", "absent"], reason: Literal["unsupported", "stale_vocabulary"] | None}
application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/contract/response/select_visible_fortune_candidates_response.py::_CandidatesClassified {kind: Literal["classified"], bundle_id: str, candidates: tuple[_CandidateOutcome, ...]}
application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/contract/response/select_visible_fortune_candidates_response.py::_CatalogUnavailable {kind: Literal["unavailable"], bundle_id: str | None, reason: Literal["bundle_unavailable", "relation_table_unavailable"]}
application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/contract/response/resolve_fortune_support_response.py::_SupportResolved {kind: Literal["resolved"], bundle_id: str, fortune_id: str, work_rag_refs: tuple[tuple[str, str], ...], required_input_ids: tuple[str, ...]}
application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/contract/response/resolve_fortune_support_response.py::_SupportUnavailable {kind: Literal["support_unavailable"], bundle_id: str, fortune_id: str, status: Literal["unsupported", "absent"], reason: Literal["unsupported", "stale_vocabulary"]}
application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/contract/response/resolve_fortune_support_response.py::_CatalogUnavailable {kind: Literal["unavailable"], bundle_id: str | None, reason: Literal["bundle_unavailable", "relation_table_unavailable"]}
# driving — OHS service (3 공개 함수)
application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/catalog_inquiry_service.py::list_fortune_types_query() -> ListFortuneTypesResponse
application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/catalog_inquiry_service.py::select_visible_fortune_candidates_command(request: SelectVisibleFortuneCandidatesRequest) -> SelectVisibleFortuneCandidatesResponse
application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/catalog_inquiry_service.py::resolve_fortune_support_command(request: ResolveFortuneSupportRequest) -> ResolveFortuneSupportResponse
# composition_root (build_* 3 팩토리)
application/fortune_catalog/composition_root/dependency_wiring.py::build_list_fortune_types_use_case() -> ListFortuneTypesUseCase
application/fortune_catalog/composition_root/dependency_wiring.py::build_select_visible_fortune_candidates_use_case() -> SelectVisibleFortuneCandidatesUseCase
application/fortune_catalog/composition_root/dependency_wiring.py::build_resolve_fortune_support_use_case() -> ResolveFortuneSupportUseCase
```

### 경계 import

프레임워크 공통(in-repo·검사 대상)과 서드파티(`rdflib`·저장소 밖·검사 면제)를 성문한다. 타 BC OHS/published 계약 소비 0(cross-BC import 없음). `ontology_service.py` import 0.

<!-- machine: boundary-imports -->
```imports
application/fortune_catalog/composition_root/dependency_wiring.py    from framework.technology.rag.runtime import ontology_canonical
application/fortune_catalog/composition_root/dependency_wiring.py    from framework.technology.rag.runtime import service_runtime
application/fortune_catalog/composition_root/dependency_wiring.py    from rdflib import Graph
application/fortune_catalog/driven_layer/adapter/relation_table/rag_runtime_adapter.py    from rdflib import Graph
application/fortune_catalog/test/unit/test_pack_query_equivalence.py    from rdflib import Graph
application/fortune_catalog/test/unit/test_relation_table_adapter_synthetic.py    from rdflib import Graph
application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/catalog_inquiry_service.py    from application.fortune_catalog.application_layer.port.active_service_bundle.exception import ActiveServiceBundleContractMismatch
application/fortune_catalog/driving_layer/open_host_service/catalog_inquiry/catalog_inquiry_service.py    from application.fortune_catalog.application_layer.port.relation_table.exception import RelationTableContractMismatch
```

### 예외 번역표

이 BC는 **published 예외가 없다** — 모든 실패(Bundle 고정 실패·관계표 계약 불일치·닫힌 분기)는 OHS 응답 union의 variant(`_CatalogUnavailable`·`_SupportUnavailable`·닫힌 상태)로 표현하고 예외를 소비자에 흘리지 않는다(§6·§7). 포트 내부 예외(`ActiveServiceBundleContractMismatch`·`RelationTableContractMismatch`)는 OHS가 잡아 응답으로 변환하는 «내부» 실패라 published 창구가 raise하지 않는다. 따라서 번역표는 비었다(죽은 published 계약 0 — `contract/exception/catalog_inquiry_published_error.py`는 빈 파일).

<!-- machine: exception-map -->
```exceptions
# published 예외 없음 — 실패는 OHS 응답 union variant로 표현(§6·§7)
```

---

## §13 자기모순 스캔 · 결과 제약 요약

### 절 간 일관 (1회 스캔 완료)
- **판정 소유**: 가시성·지원 판정 = `FortuneVisibilityService`(도메인) 단일 소유. adapter는 사실만(§5), OHS는 미러만(§6), use case는 조율만(§4). 인프라 판정 복제 없음(§3.2). 모순 없음.
- **명명**: area/service `catalog_inquiry`, 포트 `active_service_bundle`·`relation_table`, 어댑터 `rag_runtime_adapter.py`(능력 폴더 짝), use case 3종·command/query/result — §2·§4·§5·§6·§12 전부 일치.
- **`_command`/`_query`**: 창구① 0-param→`_query`(query.py 채움·command.py 빈), 창구②③ 1-param→`_command`(command.py 채움·query.py 빈) — §4·§12 file-plan·symbols 일치(근거 canonical #633/#567 파라미터 유무 규약 · 관찰 저장소 규약 아님).
- **세대 표식**: `bundle_id`가 성공·닫힌분기 variant 전부에 포함, pin 실패만 `str | None` — §6·§7·§12 일치.
- **닫힌 답 vs 실패**: 미실존/미지원 = 정상 결과(도메인 status → 응답 Literal), Bundle/관계표 실패 = 예외 경로(OHS가 unavailable로 접음) — §4·§6·§7 일치(수정 반영).
- **자료 계약 필드**: `PinnedServiceBundleOut`·`RelationTableFactsOut`·`RelationQueryIn`·result·response variant 필드 — §5·§6과 §12 symbols 일치.
- **`support_pairs` 튜플 순서**(A1): 정본 `(fortune_id, work_id, rag_id)` — §3 판정 규칙·§5 `relation_table_facts_out`·§9 Q2·§12 symbols 전부 이 위치로 일치(work·rag 스왑 방지 단언은 §11 row 1·row 3).
- **unavailable 원인 리터럴**(A3): `_CatalogUnavailable.reason`은 `Literal["bundle_unavailable", "relation_table_unavailable"]` 두 값 — `bundle_unavailable`(pin 실패·bundle_id=None) / `relation_table_unavailable`(관계표 load 실패·bundle_id=고정값). §6·§12 symbols 3개 union 정의 일치, OHS 접기는 §11 «OHS 예외 접기» 행이 검증(B1).

### 결과 제약 (coder·acceptance-tester 집행)
- 소스 파일트리는 무조건 dddjango 표준(final.md §1) — §12 file-plan이 정본. 골격 칸 빈 실현(#488), BC 직계 일곱(#81), 트리 밖 칸 0(#490).
- `application/fortune_catalog/**`에서 `ontology_service.py` import 0 · 관계표 값 코드 상수 0 · cross-BC import 0 · 호환층/옛 이름 0(D37).
- Bundle 고정은 `service_runtime.validate_terminal_active_service_bundle`(D6·약화 금지·리딩 FR-4 강도)만 — 별도 모듈이라 D51-2 ②와 양립.
- `spring_dream_server/settings/base.py` INSTALLED_APPS에 `"application.fortune_catalog.driven_layer.django_fortune_catalog.apps.FortuneCatalogConfig",` 1줄 추가(허용 경로).
- 완료 조건 5종(★ 6 테스트가 분담 · B2) green + `make test` 전체 green + registry_gate 레인 귀속 0 + mypy/ruff clean + `saju_taxonomy_interaction.test.js` 44/44(레인 미수정).
- master.html 발주표·`tests/saju_taxonomy_interaction.test.js`·`ontology_service.py`·타 BC·두 가이드는 수정하지 않는다.

### 미해결 옵션·STOP
- 없음. 견고성·비기능 요구(Bundle 검증 강도)는 발주서가 리딩 동급으로 고정(D51-3 ⑦). 스코프·스펙 모순 미발견. 멱등성·미요청 견고성 결정 대상 없음(조회·상태 없음).
- `_command`/`_query` 접미(창구②③가 read인데 canonical #633 param-count 규약상 `_command`)의 근거는 **canonical #633/#567**이다(관찰 저장소 규약 아님 — B4). read 연산을 `_command`로 부르는 의미적 이질감은 G1' 재고 후보로 남긴다 — 단 현 결정의 근거는 canonical #633이며, pre-gate check-naming(#26)이 현행 명명을 fortune_catalog 귀속 0으로 통과(결정적 검사기 준수 확정)해 명명 «값» 변경은 불요다.

