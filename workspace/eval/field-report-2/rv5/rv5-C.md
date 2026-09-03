# rv5-C — ⑤ 구현 리뷰 · 리뷰어 C(증거 축 — 무손실 판정식 실측·소급·효과 정직성·표본 외) · 2026-09-04

대상: 브랜치 `fix/field-report-2` 구현(35fc29b 규범 · 95a95cc 검사기 · 421782e 문서 = HEAD). 독립 재계산 — 원본 두 저장소는 읽기만, 실행은 전부 scratchpad `fr2/rv5C/`: 격리 복제본 `spring`@**f5ee428**(현재 HEAD — ③ C 의 c20f525 뒤 docs 3커밋) · `kkebi`@**6608fb0** · `spring-h`@{59d08c7,99253ce,9c8814e}(`git clone -q` + `checkout --detach`) · 검사기 트리 `scripts-old`(= `git archive 35fc29b dddjango/scripts` — 검사기 변경 전) / `scripts-new`(= HEAD 421782e) · 인터프리터 = 각 저장소 `.venv/bin/python` 3.14 · `DJR_FINDINGS_JSON` sink 로 (severity, rule, 상대경로, message) 다중집합 차분(`run.py`·`diff.py`·`e_analyze.py`). 매트릭스·smoke·번들은 저장소 `workspace/tools/*.py` 를 HEAD 에서 그대로 실행, cross census 의 «옛 검사기» 판은 `S` 만 `scripts-old` 로 바꾼 사본(`tools/cross_old.py`). Serena: skipped — 리서치·재계산(저장소 코드 무수정).

## 1. 판정 표

| # | 구현·④ 기록 주장 | 판정 | 근거(요약 · 상세 §2) |
|---|---|---|---|
| E-1 | 기존 규칙 발화 집합 불변(A∖B = 0) · B∖A = #645 계열만 | **검증됨** | spring 3,320 → 4,112 · kkebi 345 → 851 레코드. A∖B = **0/0**, B∖A = `#645` violation **78/121** + `ⓓ#645` **714/385** 뿐. `#493` 3,225/173 · `ⓓ#69` 95/172 byte 동일 · `#358`/`#456` 0/0 불변 · exit 2→2 |
| E-2 | application `[#645]` 10/14 = 프로덕션 8/10 + factories 2/4 · 전 저장소 78/121 | **검증됨** | 파일:줄 24건 전수 §3 — ① C 강도 1 표 8/10 과 동일 · factories spring 2(`character_model_factory.py:44`·`product_model_factory.py:29`) · kkebi 4(`coupon_entitlement_model_factory.py:33`×2·`point_ledger_entry_model_factory.py:33`×2) |
| E-3 | `ⓓ#645` application spring 114 · kkebi 134 | **MINOR(시점 미기재)** | HEAD f5ee428 실측 **134/134**(prod 132/123 + material 2/11). spring 114 는 ⓪ rsync 사본(d2eaafe 워킹트리) 시점 수치 — 그 뒤 fortune_calculation-2 레인이 ⓓ +20(`application/fortune_calculation` 26 중). Δ7 «112/123」·④ «114/134」·HEAD «132/123」(prod) 세 수치가 sha 없이 병존 → ④ 에 측정 sha 1행 |
| E-4 | registry_gate 귀속: 기존 `Any` 파일을 건드려도 파일 전체 red 아님 · Phase 0 빚 스캔 spring 5 BC·kkebi 6 BC | **검증됨** | 키 = `script :: [#645] <상대경로>:N: <msg>`(`_normalize` L145-147 · `_FINDING_RE` L94) — 같은 함수·같은 매개변수는 라인 이동해도 동일 키(실측 `True`), 새 매개변수·이름 변경만 새 키(실측 `False`). BC 분포: spring {fortune_character(factory 만)·fortune_record·product(factory 만)·promotion·service_policy} = 5 · kkebi {billing(factory 만)·identity·product_observability·saju·share·tarot} = 6 |
| E-5 | 현장 보고 E 상태 «소급 … 전부 `object` 치환 가능» | MINOR(과대) | ⓪ 프로브는 Django 스텁 4형만. 미러 13 + factories 6 은 기계 치환이나, 실질 세탁 5(kkebi `decision: Any`×2 · saju JSON 순회 ×3)는 `object` 로 바꾸면 본문에 좁힘 코드가 필요(치환이 아니라 수리) — «미러·factories 19 기계 치환 · 실질 5 좁힘 수리」 로 |
| H-1 | HEAD 양 저장소 두 검사기 차분 0 · 카탈로그 59d08c7 {#219×2,#635×3}→0·exit 0 · 99253ce 두 검사기 몫 7 불변·#488×5 · 9c8814e = 59d08c7 | **검증됨** · «43/43」 MINOR | spring 167→167 · kkebi 291→291 레코드(차분 0/0) · exit 0,0/0,2 무변. 59d08c7 A∖B = 정확히 {#219×2, #635×3}(파일 5 = ⓪ 목록) · exit 2,2→**0,0** · B∖A 0. 99253ce old=new {#218×2, #576×2, #193×3} exit 2,2 + `check-layer-skeleton` #488×5. ④ 의 «kkebi 43/43」 은 어느 계수와도 안 맞는다(레코드 291/291 · violation 27/27 = #189 10+#205 17 · stdout 진단행 27/27) — 차분 0 은 참, 수치 출처 기재 |
| H-2 | 새로 침묵하는 골격 파일 0 | **검증됨** | `skeleton_placeholder` 정의 전체 census: spring 0B 116 · docstring-only 34 · comment-only 0 / kkebi 188 · 32 · 1 — 그중 두 검사기의 내용 규칙 칸(`<cap>_port.py`·`<uc>_use_case.py`) 은 **0/0**(docstring-only 는 전부 DTO·wiring·schema 칸). HEAD 차분 0 이 곧 «새 침묵 0」 |
| H-3 | 픽스처 27종 차이 = skeleton 레인 2행뿐 · fixture 104 · findings 73 · baseline 73 · cross 348 · P0′ 31/31 · 번들 PASS | **검증됨** · «17파일」 MINOR | 옛 검사기 census(현 픽스처) **350행** vs 새 **348행** — diff = `('skeleton','check-port-adapter-pairing.py') (219,1)` · `('skeleton','check-usecase-dto-placement.py') (635,1)` 정확히 2행. HEAD: fixture 104/104 · findings_count 73/73 · baseline 73/73 · cross 348 차이 0 · registry_gate_smoke 31/31 · pregate 번들 PASS(55s · manifest 경로 실재) · spec_lint 규칙 547 위반 0 · bad `#645×8`+`ⓓ#645×1` · good exit 0 — 단 «파일 18개」(④ «17파일」) |
| G-1 | R-3427 rev4 적용 후 spring 명세(현재 판본) 형식 위반 0/7 | **검증됨(0/8)** | HEAD 블록 보유 명세 **8**(⓪ 7 + `20260903-2240-fortune-calculation-2-place-search`). 잎→`application_layer/port/**` 행 0/8 · 산문에서 잎의 port **직접** import 를 계획한 명세 0/8(catalog L186/L511/L541 · reading L337/L1185 명시 0). 재수출 경유를 계획한 2건(notification-bc L41-50 · fc-2 L136/L158/L183)은 그 import 행이 블록에 **있다**(notification 블록 18행 · fc-2 블록 14행) → rev4 ⑵ 기준 위반 아님 |
| G-2 | R-3449 위반 코드 = notification-bc 1건(재수출 경유) · 그 외 BC 전수 0 | **MAJOR(과소 — 4 BC)** | driving 잎의 port 예외 «타입」 의존 전수(직접 import·재수출 import·`except`·`isinstance`): spring **4 BC · 5 파일 · 재수출 이름 12 · `except` 사이트 13**(query_translation 6 · fortune_intent 3 · fortune_calculation 3(2파일) · notification 1) · 직접 import 0 · isinstance 0 / kkebi **0**(port 예외 클래스 보유 11/12 BC → 비공허). 4 BC 전부 레인 산출물(08-31~09-04)이고 **최신 레인 fortune_calculation-2(v2.17.16 · S3 `564091c` 09-04)** 가 명세로 이 패턴을 «선례」 로 채택했다(fc-2 L136 «선례 `calculate_chart_use_case`」 · notification L41-43 «`query_translation` 확립 선례」). «발주측 빚 1 · 소급 없음」 은 검사기(#93) 기준일 뿐 — 규범 기준 소급 = 4 BC · 명세 2건 명문화 |
| G-3 | R-3449 «자기 영역의 예외(`application_layer/<area>/exception.py`)로 번역」 | **MAJOR(따를 수 없는 처방)** | 표준 트리 `<area>/`(row 39) 의 자식은 `<use_case>/`(row 40) 뿐 — area 층 `exception.py` 칸 없음. 실코드 양 저장소 0. 실측: skeleton good_bc 사본에 `application_layer/order/exception.py` 추가 → `[#490] 트리가 이 층에 이름을 준 파일이 아니다` + #487 조기 중단(registry 전체 불실행). 실제 관행 = use case 승격 폴더 부품(`<uc>_use_case/<uc>_source_unavailable.py` ×3 · `prepare_fortune_evidence_failure.py`). 문면대로면 «R-3449 준수 시 예보 0」 이 아니라 #490 red — B 축 소유(문면 교정)이나 효과 주장의 근거가 무너진다 |
| F-1 | R-0719 rev2 문면이 spring HEAD 배선을 준수로 읽는가 | **검증됨** | `fortune_reading/composition_root/dependency_wiring.py:31-47` — `partial(service_runtime.retrieve_release_evidence_with_local_embedder, data_root=data_root)` 가 `build_prepare_fortune_evidence_use_case()` **본문 안**, `data_root` 지역 · 최상단 대입 없음 = 문면의 «팩토리 본문 안 `functools.partial`」 과 일치 |
| F-2 | R-3450 «fake 는 프로세스 밖 경계뿐」 이 `test_composition_root_wiring.py` 를 자격 있는 대상으로 읽는가 | MINOR(③ C 지적 미반영) | fake ① `_FakeQueryTranslationAdapter` 가 `dependency_wiring.QueryTranslationAdapter`(자기 BC ACL 어댑터 → 타 BC OHS `translate_command` → `LlmAccessConceptSelectionAdapter` → LLM)를 **프로세스 안**에서 교체 — 프로세스 밖 경계는 두 홉 아래. fake ② 모델 가중치 verify/load = 디스크 ✓. 문자 그대로면 유일 선례가 반쪽 자격이고 `translate_command` 시그니처는 이 경로가 안 탄다. 자격 항목이라 소급 0, 문면만 «프로세스 밖 경계(그리로 가는 타 BC OHS 소비 자리 포함)」 |
| D | R-3446 문면이 kkebi `payment_processing_adapter.py:437` 을 위반으로 읽는가 · n=2 | **검증됨** | `:437-457 _raise_provider_error(...) -> None` — 경로 5개 전부 `raise`(if / try-except from / if / if / 말미 raise) · staticmethod 도우미 · `__init__` 아님 → 문면 대상. 같은 파일 `:366 -> Never`. spring `_fail`: 43e9628 `service_runtime.py:54 -> None` → 96e8719 `-> NoReturn`(HEAD :635) — 형상 n=2 · 증폭 실효 1 |

## 2. 실측 상세

### 2.1 E — #645 (spring f5ee428 · kkebi 6608fb0)

명령: `DJR_FINDINGS_JSON=out/ps-<repo>-<old|new>.jsonl <repo>/.venv/bin/python scripts-<old|new>/check-public-surface-annotation.py <복제본>` (cwd = 복제본) → `diff.py`/`e_analyze.py`.

| | spring old | spring new | kkebi old | kkebi new |
|---|---|---|---|---|
| exit | 2 | 2 | 2 | 2 |
| `#493` violation | 3,225 | 3,225 | 173 | 173 |
| `ⓓ#69` | 95 | 95 | 172 | 172 |
| `#645` violation | — | **78** | — | **121** |
| `ⓓ#645` | — | 714 | — | 385 |
| A∖B / B∖A | 0 / 792(전부 #645) | | 0 / 506(전부 #645) | |

`#645` violation 분포: spring (root) 9 · framework 59 · **application 10** / kkebi (root) 37 · scripts 17 · web 53 · **application 14**. `ⓓ#645` application 134/134 — spring sig-nested 55 · var-bare 38 · var-nested 41(prod 132 + material 2) · kkebi 26 · 72 · 36(prod 123 + material 11) · 밖: framework 574 · web 165 · scripts 78.

registry_gate 귀속(코드 + 실측): `_run_registry` L228-231 이 `_FINDING_RE`(`^\s*(\[#\d+\].*)$`) 로 라인을 잡아 `script :: _normalize(line)` 키를 만들고, `_normalize` 는 스냅숏 접두사 제거 + `:\d+`→`:N`. `#645` 메시지는 `` `<fn>()` 매개변수 `<label>` 가 `Any` 다 — … `` 이라 키 = 경로+함수명+매개변수명. 실측(`registry_gate._normalize`): 같은 함수·같은 매개변수 라인 이동 → 키 동일(L∩N 잔존) · 새 매개변수 → 새 키. 따라서 신규 레인이 기존 `Any` 파일을 건드려도 «파일 전체 red」 는 아니며, 소급 형태는 ⑴ Phase 0 빚 스캔(루트 실행 → 대상 BC 필터: spring 5 BC · kkebi 6 BC 의 항목) ⑵ 함수·매개변수 이름 변경·파일 이동 시 재귀속 ⑶ G2 배너 legacy 잔존 행(78/121)뿐이다. ⓓ 는 `_FINDING_RE` 밖(`[ⓓ#`)이라 게이트 차분에 없고 R-0284 rev3 감사 입력 채널만 탄다.

표본 외: 최신 레인 fortune_calculation-2(c20f525 머지 · v2.17.16)의 application/fortune_calculation `[#645]` **0** · `ⓓ` 26 — 시그니처 차단 실효 0/1레인, ⓓ 생산은 계속(③ C 와 일치).

### 2.2 H — skeleton_placeholder (#219/#635)

명령: `run.py h-<상태>-<old|new> … check-port-adapter-pairing.py,check-usecase-dto-placement.py` × {spring HEAD, kkebi HEAD, spring-h 59d08c7/99253ce/9c8814e} + `check-layer-skeleton.py`(new) 3커밋.

| 트리 상태 | old 레코드 | new 레코드 | A∖B | exit old→new | 비고 |
|---|---|---|---|---|---|
| spring f5ee428 | 167(violation 0 · info 167) | 167 | 0 | 0,0 → 0,0 | info = #227 9·#485 35·#553 68·#103 4·#140 5·#191 3·#194 8·#68 35 |
| kkebi 6608fb0 | 291(violation 27 · info 264) | 291 | 0 | 0,2 → 0,2 | violation = #189 10·#205 17 |
| 59d08c7(빈 5파일) | 167 | 162 | **{#219×2, #635×3}** 정확히 | 2,2 → **0,0** | 파일 5 = ⓪ 목록(port 2·use_case 3) · B∖A 0 |
| 99253ce(제거) | 169 | 169 | 0 | 2,2 → 2,2 | 두 검사기 몫 #218×2·#576×2·#193×3 = 7 불변 · #488×5(skeleton) |
| 9c8814e(복원) | 167 | 162 | = 59d08c7 | 2,2 → 0,0 | |

왕복 시각 재확인: 13:55:30 → 14:05:40 → 14:09:12 = **13분 42초** ✓.

골격 census(`skel.py` · `skeleton_placeholder` 정의: 0B·공백·주석-only·docstring-only · `__init__.py` 제외): spring 0B 116 · docstring-only 34 · comment-only 0 / kkebi 0B 188 · docstring-only 32 · comment-only 1(`kkebi_server/celery.py`). `application_layer/port/**/<cap>_port.py`·`<uc>_use_case.py` 칸의 placeholder = **0/0**(docstring-only 는 `_command/_query/_result` DTO 61 · kkebi port `exception.py` 2 · `event_wiring.py`·`event_router.py`·`schema_in.py`). → HEAD 에서 새로 침묵하는 파일 0(차분 0 과 정합).

픽스처: 옛 검사기 census(현 픽스처 트리) 350행 ↔ 새 348행 — diff 정확히 skeleton×port-adapter(219,1)·skeleton×usecase-dto(635,1) 2행 = EXPECTED 에서 제거된 2행(결정 2). HEAD 공식 실행: `fixture_matrix` 104/104 · `findings_count_matrix` 73/73 · `checker_baseline_matrix` 73/73 · `checker_cross_matrix` 348/348 차이 0 · `registry_gate_smoke` 31/31(P0′ 포함) · `pregate_fixture_run` PASS(55s) · `spec_lint` 547/0. public_surface good `clean — 파일 18개`(④ «17파일」) · bad `#645×8`(`x: Any`·`-> Any`·`Optional[Any]`·`_Any`·`typing.Any`·`**kwargs: Any`·`Any | None`·`"Any"`) + `ⓓ#645×1`(`y: dict[str, Any]`).

### 2.3 G — R-3427 rev4 · R-3449

명세 8건(`gblocks.py` · HEAD 판본): 블록 행수 record 27 · reading 17 · media 28 · notification-bc 22 · email-template 48 · catalog 5 · chat-relay-2a 1 · **fc-2 26** — `application_layer/port` 행은 전부 driven adapter·test·use case 소비자(reading 5·notification 6·email-template 5·fc-2 6), driving 잎 소비자 **0/8**. 산문: catalog·reading 은 «port import 0」 명시, notification-bc·fc-2 는 «use case 재수출 경유 catch」 를 명시 계획(블록에 그 행 존재). rev4 ⑵ «잎이 port 예외를 잡을 계획이면 그 import 행을 그대로 적어」 기준 형식 red **0/8**.

코드 전수(`gscan.py` · `driving_layer/**` · 테스트 제외 · port/** 의 예외 클래스 이름 집합 대조):

| BC | 파일 | 재수출 import(줄 · 이름) | `except` 사이트 | 레인·커밋 |
|---|---|---|---|---|
| query_translation | `open_host_service/translation/translation_service.py` | :11 · 6(`Glossary*`×4·`TranslationConfiguration*`×2) | :89·91·93·95·97·99 (6) | ad56395 08-31 |
| fortune_intent | `open_host_service/request_understanding/request_understanding_service.py` | :10 · `IntentGenerationConfigurationFailed` | :86·127·160 (3) | e02bb15 08-31 |
| fortune_calculation | `open_host_service/chart_calculation/chart_calculation_service.py` | :35 · `LeapMonthAbsent`·`PlaceCodeUnknown` | :170·172 (2) | 3322846 09-01 |
| fortune_calculation | `open_host_service/place_directory/place_directory_service.py` | :25 · `PlaceCodeUnknown` | :54 (1) | **564091c 09-04 dddjango(fortune_calculation-2) S3** |
| notification | `open_host_service/email_notice/email_notice_service.py` | :6 · `EmailNoticeRenderingError`·`EmailNoticeTransportError` | :40 (1, 2이름) | f521d09 09-02 dddjango S1 |

합계 spring **4 BC · 5 파일 · 이름 12 · except 13** · 직접 import 0 · isinstance 0. kkebi 12 BC **0**(port 예외 클래스 보유 billing 19·identity 12·tarot 9·saju 8·consultation 8·daily 7·notification 5·product_observability 4·review 4·share 4·image 1 · top3 0). 4 BC 의 use case 모듈은 전부 `__all__` 재수출(`translate_use_case.py:62`·`classify_counter_message_use_case.py:59`·`confirm_place_code_use_case.py:35`·`send_email_notice_use_case.py:24`).

번역 자리 실험: `cp -r workspace/eval/fixtures/skeleton/good_bc t490` + `application/orders/application_layer/order/exception.py`(클래스 1) → `check-layer-skeleton.py`: `blocker 1건 — 골격이 어긋나면 나머지 검사를 돌리지 않는다(#487)` · `[#490] …/application_layer/order/exception.py: 트리가 이 층에 이름을 준 파일이 아니다`. `standard_tree.py` rows 38-44: `application_layer/` → `<area>/` → `<use_case>/` → `_use_case/_command/_query/_result` — area 층 파일 칸 없음.

#93 발화 5레인(⓪): spring `.dddjango/**/*.md`(pregate-report·design-spec 제외)에 `#93` 보유 4파일(openai-rag loopback · reading p4 review ×2 · service-policy scope-evidence(인용)) 실재 · kkebi 0(design-spec 안에서만) — ⓪ 정의(spring 3 + kkebi 2 = 5)와 모순 없음, 독립 재계수는 안 함.

### 2.4 F · D

- F-1: `dependency_wiring.py:31-47` 인용 §1. `QueryTranslationAdapter(translate_command=translate_command)` 는 실물 OHS 함수 직접 주입(인자 부족 없음 — ⓪ 정적 대조 HEAD 0).
- F-2: `test_composition_root_wiring.py` — `monkeypatch.setattr(dependency_wiring, "QueryTranslationAdapter", _FakeQueryTranslationAdapter)`(L152) + `_install_pinned_snapshot`(`verify_model_snapshot_ref`·`load_local_embedder`). 실물: `build_prepare_fortune_evidence_use_case()` · reading_bundle/evidence_retrieval/evidence_digest 어댑터 3 · 검색 런타임 · Release 산출물. `query_translation/composition_root/dependency_wiring.py build_translate_use_case` 는 `LlmAccessConceptSelectionAdapter`(→ llm_access → LLM)·`RagGlossaryTranslationAdapter` 를 꽂는다 — fake ① 은 그 두 홉 위.
- D: kkebi `:437-457` 본문 전 경로 raise · `_json_object`/`_required_str` 도우미가 raise 하는 `TypeError` 를 잡아 다시 raise. spring `git show 43e9628:…/service_runtime.py` L54 `-> None`, `96e8719` L635 `-> NoReturn`.

## 3. 소급 24건 분류표 (application `[#645]` · HEAD)

| # | 저장소 | 파일:줄 | 시그니처 | 분류 | ① C 강도 1 표 |
|---|---|---|---|---|---|
| 1 | spring | `fortune_record/driven_layer/django_fortune_record/models/fortune_record_model.py:15` | `update(**kwargs: Any)` | Django Model 스텁 미러 | ○ |
| 2 | spring | `…/fortune_record_model.py:95` | `delete(using: Any)` | Django Model 스텁 미러 | ○ |
| 3 | spring | `promotion/driven_layer/django_promotion/admin/campaign/form/campaign_form.py:100` | `__init__(*args: Any)` | Django Form 스텁 미러 | ○ |
| 4 | spring | 같은 줄 | `__init__(**kwargs: Any)` | Django Form 스텁 미러 | ○ |
| 5 | spring | `service_policy/driven_layer/django_service_policy/admin/limit_rule/form/limit_rule_form.py:54` | `__init__(*args: Any)` | Django Form 스텁 미러 | ○ |
| 6 | spring | 같은 줄 | `__init__(**kwargs: Any)` | Django Form 스텁 미러 | ○ |
| 7 | spring | `service_policy/…/admin/suspension/form/suspension_form.py:43` | `__init__(*args: Any)` | Django Form 스텁 미러 | ○ |
| 8 | spring | 같은 줄 | `__init__(**kwargs: Any)` | Django Form 스텁 미러 | ○ |
| 9 | spring | `fortune_character/test/factories/character_model_factory.py:44` | `translations(**kwargs: Any)` | factories(factory_boy 훅) | — |
| 10 | spring | `product/test/factories/product_model_factory.py:29` | `translations(**kwargs: Any)` | factories | — |
| 11 | kkebi | `identity/driven_layer/django_identity/admin/account_merge/panel.py:48` | `has_change_permission(obj: Any)` | ModelAdmin 스텁 미러(정확 타입 = `<Model> \| None`) | ○ |
| 12 | kkebi | `identity/…/admin/profile/panel.py:39` | `has_change_permission(obj: Any)` | ModelAdmin 스텁 미러 | ○ |
| 13 | kkebi | `share/driven_layer/django_share/admin/content_share/form/content_share_form.py:19` | `__init__(*args: Any)` | Django Form 스텁 미러 | ○ |
| 14 | kkebi | 같은 줄 | `__init__(**kwargs: Any)` | Django Form 스텁 미러 | ○ |
| 15 | kkebi | `tarot/driven_layer/django_tarot/models/insert_only_model.py:9` | `update(**kwargs: Any)` | Django Model 스텁 미러 | ○ |
| 16 | kkebi | `product_observability/driving_layer/api/analytics/analytics_controller.py:130` | `_accepted_rate_limit_or_none(decision: Any)` | **실질 세탁** | ○ |
| 17 | kkebi | `product_observability/driving_layer/api/bug_report/bug_report_controller.py:141` | 같은 도우미 | **실질 세탁** | ○ |
| 18 | kkebi | `saju/domain_layer/domain_service/v3_reading_assembler.py:265` | `_evaluate_condition(condition: Any)` | **실질 세탁**(JSON 순회) | ○ |
| 19 | kkebi | `…/v3_reading_assembler.py:448` | `_graphic_schema(x_axis: Any)` | **실질 세탁** | ○ |
| 20 | kkebi | `…/v3_reading_assembler.py:777` | `_apply_fortune_variables(unse: Any)` | **실질 세탁** | ○ |
| 21 | kkebi | `billing/test/factories/coupon_entitlement_model_factory.py:33` | `_create(*args: Any)` | factories | — |
| 22 | kkebi | 같은 줄 | `_create(**kwargs: Any)` | factories | — |
| 23 | kkebi | `billing/test/factories/point_ledger_entry_model_factory.py:33` | `_create(*args: Any)` | factories | — |
| 24 | kkebi | 같은 줄 | `_create(**kwargs: Any)` | factories | — |

합: 미러 **13**(Form `__init__` 8 · Model 3 · ModelAdmin 2) · 실질 **5** · factories **6** = 24 · ① C 표 18/18 일치.

## 4. 문서 불일치 목록

| # | 위치 | 기재 | 실측 | 심각도 |
|---|---|---|---|---|
| 1 | 루브릭 ④ «소급 실측 … `ⓓ#645` application spring 114 · kkebi 134» · Δ7 «프로덕션 112/123» | 측정 sha 없음 | HEAD f5ee428 application 134(prod 132) — 114/112 는 d2eaafe 워킹트리 시점 · +20 = fortune_calculation-2 | MINOR |
| 2 | 루브릭 ④ «HEAD 양 저장소 두 검사기 old/new 발화 집합 차분 0(spring 0/0 · kkebi 43/43)» | 43 | 레코드 291/291 · violation 27/27 · stdout 진단행 27/27 — 43 의 출처 불명(차분 0 은 참) | MINOR |
| 3 | 루브릭 ④ «good exit 0(17파일)» | 17 | `clean — 파일 18개` | MINOR |
| 4 | 루브릭 ④ 무손실 판정 «발주측 빚 기록: notification-bc … 1» · Δ2 · 현장 보고 상태 G «발주측 빚 1» | 1 BC | R-3449 문면 위반 코드 **4 BC · 5 파일 · except 13**(query_translation·fortune_intent·fortune_calculation×2·notification) · 명세 2건(notification-bc·fc-2)이 이 경로를 «확립 선례」 로 명문화 · 최신 레인(09-04 S3)이 재생산 | **MAJOR** |
| 5 | 루브릭 ④ 규범 «R-3449 … port 예외 번역 = use case» · architecture-ddd final.md:1021 «`application_layer/<area>/exception.py`» | 번역 자리 | 트리 칸 없음(rows 38-44) · 실코드 0 · #490 + #487 red 실측 · 관행 = use case 승격 폴더 부품 | **MAJOR**(B 축 문면 교정 소유 · 효과 주장 근거 결손) |
| 6 | 현장 보고 상태 G «잎→port 행 블록 0/7» · 정정 추기 ⑤ «0/7» | 7 | HEAD 8(fc-2 추가 · 0/8) — «⓪ 시점 7」 표기 | MINOR |
| 7 | 현장 보고 상태 E «소급 … 전부 `object` 치환 가능» · 로드맵 R-19 동일 | 전부 | 미러 13·factories 6 은 기계 치환 · 실질 5 는 좁힘 수리(프로브 범위 밖) | MINOR |
| 8 | 루브릭 ④ «HEAD·픽스처 무변» (H) | — | 참 — 단 «cross EXPECTED 2행 제거」 는 픽스처 census 변화이므로 «픽스처 무변」 옆에 «(cross 2행 제거 제외)」 병기 | MINOR(문구) |
| — | 8/10 · 10/14 · 78/121 · #493 3,225/173 · 5→0 · 7 불변 · #488×5 · 13:42 · n=2 · 5 BC/6 BC · 104/104 · 73/73 ×2 · 348 · 31/31 · PASS · 547/0 · #645×8+ⓓ1 · 정정 추기 ①~④·⑥ | | 전부 실측 일치 | 검증됨 |

## 5. ⓒ 효과 표 (최종 · 정직 문안)

| 항목 | 관측 n | 차단 / 예보 / 문면 | 기대 효과(정직 문안) |
|---|---|---|---|
| D | 형상 2/2저장소(spring 43e9628 `_fail:54` · kkebi `:437`) · 증폭 실효 1(spring 13 · kkebi 0) · 둘 다 Codex | 문면(R-3446 · discipline-reviewer 위임) | «다음 발생 회피(확률) · 검사기 0 · 0~1건/저장소」 |
| E | 정책 공백(사건 0) · 소급 시그니처 10/14(미러 13·factories 6·실질 5) · Phase 0 빚 5/6 BC · 최신 레인 시그니처 0·ⓓ +20 | 차단(시그니처 bare · #645 · 귀속 키 = 경로+함수+매개변수) + ⓓ(R-0284 rev3 감사 입력 · 게이트 차분 밖) | «신규 시그니처 bare `Any` 0 결정적 · ⓓ 는 감수자 판단(집행률 미측정 · 전 저장소 실행당 714/385행 출력) · 소급은 빚 스캔 항목·이름 변경 시 재귀속뿐」 |
| F-1 | 1(reading P4 · 585c9c6) · 정적 검출 가능 | 문면(R-0719 rev2) | «1레인 특이 · HEAD 준수형과 일치 · 검사기 0」 |
| F-2 | 부재 21/28 BC(기본 상태) · 선례 1(fake ① 프로세스 안 → 문자 그대로 반쪽 자격) | 자격 항목(R-3450 · 강제·소급 0) | «강제 없음 · 문면대로 완전 자격인 기존 테스트 0 · 신규 BC 부터 선택」 |
| G | 채널 결손 2(catalog·reading · 둘 다 add 잎) · #93 발화 5레인 · **R-3449 위반 4 BC/13 catch** · 명세 2건 명문화 | R-3427 rev4 예보(직접 import · add 잎만 · S3) + R-3449 문면(design-review-ddd 위임 · #93 은 재수출 사각) | «직접 import 계획은 G1 예보(실효 n=2) · 재수출 경로는 pre-gate·G2 둘 다 못 봄 → 리뷰어 전담 · 규범 소급 4 BC(빚 등재 필요) · 번역 자리 문면은 #490 충돌이라 교정 전 준수 불능」 |
| H | 왕복 1(catalog 13:42) · pre-content #219/#635 red 4레인 | 검사기(내용 없는 골격 파일의 내용 규칙 침묵 · R-3181 rev3) | «pre-content red 소거 결정적 · HEAD·픽스처(cross 2행 외) 무변 · 잔여 위험 = 영구 빈 파일(«하나」 검사 없는 칸은 원래 미검사)」 |

## 6. 미확인

1. ⓓ#645 감사 입력(R-0284 rev3)의 실제 집행률 — 실전 레인 없음(코디 step 5 동봉 여부는 관찰 대상).
2. `#93` 실발화 «5레인」 은 ⓪ 정의를 문서 실재로만 재확인(spring 4파일 · kkebi design-spec 안) — 레인 단위 독립 재계수는 생략.
3. R-3449 위반 4 BC 의 처분(빚 등재 vs 문면 범위 조정 «재수출 경유 허용/금지」)은 사용자 결정 사안 — 재수출 패턴이 «표준 트리에 area 예외 칸이 없다」(notification L39)에서 나온 선택이라, G-3 과 함께 다뤄야 한다.
4. ④ «kkebi 43/43」 의 계수 출처 — 구현자 확인 필요.
5. E-5 실질 5건의 `object` 치환 비용(좁힘 코드 실작성)은 미측정.
