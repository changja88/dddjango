# rv1-C — ① 문제 리뷰 · 리뷰어 C(증거 축 — 실측 재현성·표본 외·효과 과대·무손실) · 2026-09-04

독립 재계산. 원본 두 저장소는 읽기만(`git log/show/cat-file/ls-files`·`sed`·`grep`), 실행은 전부 scratchpad `fr2/rv1C/` 복제본(`git clone -q` + `checkout --detach`: `spring`@d2eaafe · `spring-d`@43e9628 · `spring-h`@{59d08c7,99253ce,9c8814e,725fbe0} · `kkebi`@6608fb0). mypy/ruff 는 각 저장소 `.venv` 바이너리(mypy 2.3.1 · ruff 0.16.4)를 복제본 cwd 에서 실행(`--cache-dir` scratchpad). Serena: skipped — 리서치·재계산 작업(코드 수정 없음).

## 1. 항목별 판정 표

| # | 조사자 주장 | 판정 | 재계산 근거(요약) |
|---|---|---|---|
| D-1 | 보고서 «`_fail -> None` → possibly-undefined 13건» | **검증됨** | `spring-d`@43e9628 `mypy service_runtime.py`: 27 errors 중 `possibly-undefined` **13** → `-> NoReturn` 패치 후 **0**(총 11). 호출부 `_fail(` 36곳 |
| D-2 | «프로덕션 도우미형 spring 0 · kkebi 1» | **검증됨** | 독립 방식(블록 끝 도달성 역산·NoReturn 지역 도우미 종단 인정) 재계수: spring prod 2 = `__init__` 가드 2 · kkebi prod 18 = 도우미 **1**(`payment_processing_adapter.py:437`) + `__init__` 1 + `NotImplementedError` 추상 스텁 16 — 조사자 분류와 일치 |
| D-3 | «kkebi `_raise_provider_error` 도 같은 사건(n=2)» | **MAJOR(효과 0)** | 호출 2곳(`:206`·`:260`)이 문장 위치(`try: x=… except: _raise…` 대입 패턴 아님) → strict+possibly-undefined mypy 결과 **before 0 / `-> Never` 후 0**. 형상 n=2 이나 **증폭 실효 n=1** |
| D-4 | n=2 의 «≥2레인» 독립성 | **MAJOR(약함)** | 두 레인 모두 **Codex**(spring fortune-reading 런 md 에 `.codex/plugins/cache/…/2.17.10` ×27 · kkebi billing-migration 런 md `.codex/…/2.17.0`), 같은 작성자(hyun), 하나는 `framework/` 경로(BC 트리 밖·`dddjango(...)` 커밋 표식 없음)·하나는 스쿼시 이관 커밋. Claude 레인 관측 0 |
| E-1 | «application 프로덕션 시그니처 bare `Any` spring 8 · kkebi 10» | **검증됨** | jsonl 재집계 spring 8(bare 7+`Any|None` 1)/파일 4/BC 3 · kkebi 10(8+2)/파일 7/BC 5. ruff `--isolated --select ANN401 application`(prod) 도 정확히 같은 8·10 |
| E-2 | 분류 «spring 미러 8 · kkebi 미러 5+실질 5» | **검증됨(단서)** | 파일 열어 확인: spring 8 = `update(**kwargs)`·`delete(using: Any|None)`·Form `__init__(*args,**kwargs)`×6. kkebi 실질 5 = `_accepted_rate_limit_or_none(decision: Any)`×2(팩토리 반환을 Any 로 받음 · `:327`·`:423`) · `v3_reading_assembler.py` `:265/:448/:777`. 단 kkebi `has_change_permission(obj: Any|None)` 2건은 스텁이 `_ModelT|None` 이라 «미러» 가 아니라 **정확 타입 대체 가능** — «미러 5» 는 실질 3+정확타입가능 2 |
| E-3 | «변수 주석 bare `Any` spring 36 · kkebi 64» | **MINOR(산술)** | jsonl: spring bare 45−sig 8 = **37** · kkebi 71−10 = **61**. 표본 20건(파일 상이) 전부 `object`+좁히기 또는 정확 타입으로 대체 가능(`request.user`·`cleaned.get()`·`getattr`·openai `completion`·`aggregate()[…]`·JSON `parsed.get`·use case `result: Any`). ninja `Schema` 필드 2건(`schema_in.py:25 event_name: Any = Field(...)`·`schema_out.py:50 detail_config: Any`)은 선언적 면제 취급을 새 규칙이 정해야 함(조사자 지적과 일치) |
| E-4 | 보고서 «시그니처 `Any` 47 · application 0» 의 원인 | **검증됨(확정)** | `ruff check --select ANN401 .`(프로젝트 설정): **47** = fabfile 9 · framework 38 · application **0**. 원인 두 가지: ① `allow-star-arg-any = true` 가 `*args/**kwargs` 7/8 면제 ② `lint.exclude "**/models/**"` 가 `fortune_record_model.py:95 using: Any|None` 을 린트에서 통째로 숨김(단일 파일 지정 시엔 발화). `--isolated` 전체 = 114(application 41 = prod 8 + test 33). 보고서 분할 «fabfile 7·framework 40» 은 오기(합 47 동일) |
| E-5 | «`object` 대체 override 호환 오류 0» | 미재검(조사자 프로브 신뢰) | 별도 mypy 프로브 재실행 안 함 — 다만 E-2 의 kkebi 2건은 `object` 도 불필요(정확 모델 타입) |
| F-1 | 표 1 «51/48 · 불일치 1→0» | **검증됨** | `wiring_audit.py` 재실행: spring HEAD callable 51 = 일치 50+판정불가 1 · 8244190 = 49+1+**불일치 1**(`dependency_wiring.py:42` data_root,embedder 미공급) · 585c9c6 = 40+1+1(`:48`) · kkebi 48 = 일치 48 |
| F-2 | «실배선 테스트 있는 BC spring 5/16 · kkebi 2/12» | **MINOR(기준 명시 필요)** | `test_audit.py` 기준 = «같은 파일에서 팩토리 이름을 patch 하지 않은 `build_*()` 호출». 표본: media_library·service_policy(3파일)·fortune_character = monkeypatch **0**·DB-backed 통합 → 진짜 실배선. fortune_reading `test_composition_root_wiring.py` = monkeypatch **7**(wiring 모듈의 어댑터 클래스·embedder 교체) → 팩토리는 진짜지만 **부분 실배선**. chat_relay = `test/fake/process_runtime_port.py` 헬퍼(execute 없음) → 실배선 아님. 엄격 기준 spring **3/16 + 부분 1** |
| F-3 | «테스트 26곳 미재현» | **검증됨** | 8244190 `fortune_reading/test`: `build_prepare_fortune_evidence_use_case` 행 11 · `build_*use_case` 언급 16(+llm_access 22) · `monkeypatch.setattr` 행 21 · 테스트 파일 22 · 테스트 함수 76 — 어느 계수도 26 아님 |
| F-4 | STOP l2-t16 = F 와 같은 부류? | **검증됨(다른 부류)** | STOP 문면: `_ProjectionBackedRunner.__call__() got an unexpected keyword argument 'content_roles'` — **테스트 fake 의 시그니처 drift 를 BC suite 가 잡음**(131 passed/1 failed). F 는 «실물 주입을 아무도 안 탐». 유사 사건 계수에 넣으면 과대 |
| G-1 | «잎→port 행 블록 0/7» | **검증됨** | `blocks.txt` 7건 port 행 = driven/test/재수출 경로만 · `code_survey.txt` driving 잎 `application_layer.port` import 0/8 디렉터리 |
| G-2 | «#93 실발화 5레인(블록 보유 2 + 없는 3)» | **검증됨** | spring openai-rag `design-loopback-g1-doubleprime.md:25-26`(#93·#96, 런 내 machine 블록 0) · fortune-reading STOP-149 `:58/:161`(6+6, 블록 15행·port 행 0) · catalog REPORT «설계 진화 3» · kkebi tarot spec `:241` `#93(3)+#96(3)` · billing-payment-http refactor-scope `:17` context-isolation exit 2 + spec §3.7. kkebi `design-spec.md` 20/20 machine 블록 **0** |
| G-3 | 조항의 실효 n | **검증됨(n=2 채널 / n=5 패턴)** | 조항은 «블록에 적어라» → 블록 없는 3레인엔 당시 무효. 채널 전사 결손 실효 n=**2**(catalog 명시·reading 암묵). 설계 패턴(잎이 port 예외 소비) 재발 n=5 는 별도 사실이며 조항이 아니라 pre-gate 예보로 잡히는 대상 |
| G-4 | 카탈로그 G1 L57↔L167 모순 | **검증됨** | `catalog-spec-G1-9ee721e.md` **L57**: «`catalog_inquiry_service.py`는 … `application_layer/port/**`를 import하지 않는다(#96)» ↔ **L117**: «use case는 잡지 않고 전파 … OHS 서비스가 이를 잡아» ↔ **L167**: «각 함수는 `ActiveServiceBundleContractMismatch`·`RelationTableContractMismatch`를 잡아 `_CatalogUnavailable` variant로 접는다». 블록(L489-497 6행)은 L57 쪽 |
| G-5 | 무손실 «현재 0 · 당시 2» | **검증됨(사람 판정)** | 현재 7판본 산문: catalog L186 «import·catch하지 않는다» · reading L337 «cause type을 import/inspect하지 않는다» → 0. 당시: catalog L167(명시) · reading P4 §5.10 L649-653 `cause` 타입 표에 port 예외 4종(암묵) → 2. 형식 검사기가 산문↔블록 정합을 기계 판정하지 못하므로 «형식 red» 는 architect 자기점검 결과이지 pre-gate 결과가 아님 |
| G-6 | 효과 «Phase 2 왕복 1회 절감» | **MINOR(과대)** | catalog: «설계 진화 3» 은 STOP 없이 S4 내부에서 architect/coder 역할로 집행(REPORT 명시 «STOP … 발화하지 않았다») → 왕복 0, 비용은 S4 내부 재설계 시간 일부(S3→S4 커밋 간격 2h07 은 S4 전체). reading: STOP-149 의 #93/#96 = **12/149** 항목. «왕복 1회» 가 아니라 «예보 시점을 G1 로 당김» |
| H-1 | 재현표(#219/#635 ↔ #218/#193/#576/#488) | **검증됨** | `spring-h` 재실행(dev 검사기 3종): 59d08c7 → #219 2·#635 3 · 99253ce → #218 2·#193 3·#576 2·**#488 5** · 9c8814e → 2·3 · **725fbe0(S2 내용 채움) → 6규칙 전부 0** = «위반 0 상태는 내용 파일뿐» 확정 |
| H-2 | «pre-content red 4레인/2저장소 · 3레인은 수용» | **검증됨** | promotion `review-s2-r2.md:52`(커밋 b2c849a 09-01 02:01): «#219 두 건 … #635 네 건 … time-phased skeleton의 “내용 없음”을 실제 계약/구현으로 해석한 진단 … 승격하지 않았다» · saju `scope.md:79`(2026-08-23 20:12:31 사용자 승인): «아직 내용 구현 전인 S1에서 최종 G2 registry를 조기 실행해 생긴 red … S2+가 … 채운 후 … 최종 G2 귀속 0을 요구» · fortune-reading pregate-report 예보 목록(#219·#576×3·#635·#488·#193 → 교정) · 0바이트 A→D→A 이력 재실행: spring **5경로(전부 catalog)** · kkebi **0** → 삭제 왕복은 1레인 |
| H-3 | «kkebi tarot domain 12 빈 파일 10일째» = ⓑ 위험 실증 | **MAJOR(과대)** | 12파일 추가 `3e97c3d` 08-25 20:13:51 · 저장소 **마지막 커밋 6608fb0 08-26 23:21** · 08-27 이후 커밋 **0** → 활성 개발 중 잔존은 ≈27h, «10일» 은 휴면 기간. dev 검사기 4종(domain-model·layer-skeleton·naming·port-adapter) 을 kkebi 복제본에 실행 → 12파일 발화 **0**(«하나 검사 없는 칸은 안 잡힌다» 는 기계적으로 성립). 영구 잔존 «위험» 의 실증으로는 약함 |
| H-4 | «13분 42초 · 왕복 2회» | **검증됨/표기 MINOR** | 59d08c7 13:55:30 → 99253ce 14:05:40(+10:10) → 9c8814e 14:09:12(+3:32) = 13:42 ✓. «왕복 2회» = 게이트 red 2회, 파일 왕복(삭제→복원)은 **1회** |
| H-5 | fortune-reading pregate «#488×2» | **미확인(MINOR)** | `grep -c "\[#488\]"` = **8행**(#219/#635 4행 — 목록 중복 가능성) — 조사자 ×2 와 불일치 |

## 2. 재계산 상세

### D
- `git clone -q ~/Desktop/spring_dream_server spring-d && git checkout -q --detach 43e9628` · 원문 `:54 def _fail(message: str, error: Exception | None = None) -> None:` · `~/Desktop/spring_dream_server/.venv/bin/mypy --cache-dir … framework/technology/rag/runtime/service_runtime.py` → `Found 27 errors in 4 files` · `grep -c possibly-undefined` = **13**. `from typing import NoReturn, …` + `-> NoReturn` 패치 → `Found 11 errors` · possibly-undefined **0**(부수 소거 3 = `:591 arg-type`·`:592 union-attr` 등 도달성 파생). 원문 보존(`git checkout -- .`).
- kkebi `application/billing/driven_layer/adapter/external_system/toss/payment_processing_adapter.py`: `:366 _raise_transport_failure(...) -> Never` · `:437 _raise_provider_error(...) -> None` · 호출 `:206 self._raise_provider_error(status_code, response, operation="confirm")` · `:260 …"cancel"` (둘 다 `if` 블록 안 문장). `mypy <file>`(pyproject strict·warn_unreachable·possibly-undefined) → `Success: no issues found` · `-> Never` 치환 후 동일. → mypy 관점 무영향.
- 독립 재계수 `rv1C/d_recount.py`(도달성: Raise/Return/exit/NoReturn 지역 도우미 종단·`while True` 무 break 종단): spring `-> None` 미도달 총 12(prod 2: `generation_audit.py:56 __init__`·`serialized_audit_payload.py:464 __init__`) · kkebi 총 42(prod 18: 도우미 1 + `saju_chart.py:76 __init__` + `NotImplementedError` 추상 16).
- 런타임: spring `.dddjango/20260831-2331-fortune-reading/*.md` 에 `.codex/plugins/cache/changja88-dddjango/dddjango/2.17.10` 27회·2.17.14 4회 · kkebi `.dddjango/20260823-1637-billing-migration/` 에 `.codex/plugins/cache/…/2.17.0` 검사기 경로 · 커밋 작성자 둘 다 hyun.

### E
- 재집계(`DE/{spring,kkebi}_any.jsonl` · `top=application ∧ is_test=false`): spring total 120 = sig 50(bare 7·bare_opt 1·nested 42) + var 70(bare 37·nested 33) · kkebi 133 = sig 36(8·2·26) + var 97(61·36).
- 시그니처 전수: spring `fortune_record_model.py:15 update(**kwargs: Any)` · `:95 delete(using: Any | None …)` · `campaign_form.py:100`·`limit_rule_form.py:54`·`suspension_form.py:43` `__init__(*args: Any, **kwargs: Any)` / kkebi `account_merge/panel.py:48`·`profile/panel.py:39 has_change_permission(…, obj: Any | None = None)` · `analytics_controller.py:130`·`bug_report_controller.py:141 _accepted_rate_limit_or_none(decision: Any)`(호출부 `:327 decision: Any = build_request_rate_limiter().attempt(…)`) · `v3_reading_assembler.py:265 _evaluate_condition(condition: Any, …)`·`:448 _graphic_schema(…, x_axis: Any)`·`:777 _apply_fortune_variables(…, unse: Any)` · `content_share_form.py:19 __init__(*args, **kwargs)` · `insert_only_model.py:9 update(**kwargs: Any)`.
- ANN401: `ruff check --select ANN401 --output-format concise .` (spring 설정) = 47(fabfile.py 9 · framework 38) · `--isolated` = 114(application 41 · fabfile 9 · framework 59 · tests 5) · `--isolated … application` prod 필터 = 8(jsonl 과 동일 파일:줄). 단일 파일 `fortune_record_model.py` 설정 실행 → `:95 using` 발화 = 전체 실행 시 `lint.exclude = ["**/models/**"]`(ruff.toml:48-55) 로 제외됨. `[lint.flake8-annotations] allow-star-arg-any = true`(:131). kkebi 설정 실행 = 89(application 7 = 10 − star 3 · fabfile 33 · web 49).
- 변수 표본 20: spring `account_controller.py:357 account_user: Any = request.user` · `time_rule_gate.py:24 period_start: Any = cleaned.get(...)` · `character_form.py:40`·`prompt_set_form.py:49`·`media_asset_writer.py:27` 동형 `cleaned.get` · `product_form.py:58`·`panel.py:55 getattr(...)` / kkebi `compatibility_narrative_generation_adapter.py:101`·`llm_completion_adapter.py:45 completion: Any = self._client.chat.completions.create(...)` · `analytics_controller.py:327`·`bug_report_controller.py:267 decision: Any` · `public_content_reviews_query.py:60 raw: Any = visible.aggregate(...)["value"]` · `v2_reading_assembler.py:395 saju: Any = parsed.get("사주")`(이미 `isinstance` 좁힘 동반) · `v3_reading_assembler.py:266` · `catalog_controller.py:68/84/103 result: Any = build_…().execute(...)`(정확 result 타입 존재) · `schema_in.py:25`·`schema_out.py:50`(ninja Schema 필드).

### F
- `python3 F/wiring_audit.py <repo> <label>` ×4 → `wa_*.json` 집계(scope=callable): spring_head 51{일치 50, 판정불가 1} · spring_pre 51{49,1,불일치 1} · spring_585 42{40,1,1} · kkebi_head 48{48}. 판정불가 = `chat_relay/…/dependency_wiring.py:213`(런타임 값).
- 26곳 후보(`F/snap/spring_8244190/application/fortune_reading/test`): 위 표 F-3.
- 실배선 표본 monkeypatch 계수: `test_save_media_asset.py` 0 · `test_seed_policy_defaults.py` 0 · `test_save_limit_rule.py` 0 · `test_consume_action_race.py` 0 · `test_prompt_set_version.py` 0 · `test_composition_root_wiring.py` **7** · chat_relay 실호출 파일 = `test/fake/process_runtime_port.py`(`has_execute=False`).

### G
- 위 표 G-1~G-6 의 파일:줄. 추가: openai-rag 런 디렉터리 `grep -l "machine: boundary-imports"` = 0 · kkebi `.dddjango/*/design-spec.md` 20개 중 블록 0. 카탈로그 S4 커밋 `854ba47` 09-03 17:33:19(직전 `75e3672` 15:26:29). STOP-149 `:152 RESOLVED — 발주자 결정 A`(시각 문면은 조사자 21:50→21:59 진술 — 파일 내 시각 미기재·미확인).

### H
- `rv1C/run_rules_c.py`(= `H/run_rules.py` + `#488`) · `ONLY=check-usecase-dto-placement.py,check-port-adapter-pairing.py,check-layer-skeleton.py` · dev `dddjango/scripts` · 4커밋 결과 위 표 H-1(records 204/211/204/204). 725fbe0 의 5파일 크기 예: `active_service_bundle_port.py` 408B · `list_fortune_types_use_case.py` 2689B.
- `zero_byte_history.py` 재실행(rv1C 복제본): spring 5(전부 `fortune_catalog` `_port.py`×2·`_use_case.py`×3 A0→D0→A0→M+) · kkebi 0.
- kkebi tarot: `git ls-files application/tarot/domain_layer` 0바이트 12(`tarot_{card,category,prompt_backup,prompt_definition,spread,topic}/{<agg>.py,<agg>_repository.py}`) · `git log --diff-filter=A` 전부 `3e97c3d 2026-08-25 20:13:51` · `git log --since=2026-08-27 | wc -l` = 0. tarot spec `:388` «고정 이름 칸은 … 빈 파일로도 반드시 존재한다(#488)».

## 3. 소급 비용 표 — E 강도 3단 (application/* 프로덕션 · 검사기 #493 격리 기준선 application 0 에 «추가만»)

| 강도 | 규칙 | spring red | 파일 | BC | kkebi red | 파일 | BC | 비고 |
|---|---|---:|---:|---:|---:|---:|---:|---|
| 1 | 시그니처(인자·`*args/**kwargs`·반환) bare `Any`(+`Any|None`) 0 무조건 | **8** | 4 | 3(service_policy 4·fortune_record 2·promotion 2) | **10** | 7 | 5(saju 3·identity 2·product_observability 2·share 2·tarot 1) | 18건 전부 `object`/정확 타입 치환 가능(조사자 프로브 + kkebi 2건은 모델 타입). `*args: object` 는 ruff `allow-star-arg-any` 관례와 다름 → 문면 명시 필요 |
| 2 | 강도 1 + 변수 주석(module/class/local/attr) bare `Any` 무조건 | **45** | 16 | 7(fortune_character 16·promotion 9·product 6·service_policy 5·fortune_record 4·accounts 4·media_library 1) | **71** | 21 | 8(saju 33·tarot 17·product_observability 12·identity 2·share 2·daily 2·top3 2·review 1) | +37/+61. 주류 = Django admin `cleaned.get()`·`request.user`·openai `completion`·JSON 순회·`result: Any`. ninja `Schema` 필드 3건은 선언적 면제 결정 필요 |
| 3 | 강도 2 + 제네릭 인자 안 `Any`(`dict[str, Any]` 등) | **120** | 31 | 11 | **133** | 36 | 10 | +75/+62. Django `Form.clean() -> dict[str, Any]` 스텁 미러·JSON 페이로드·Out DTO 다수 — 기계 치환 불가 자리 포함 |

(강도 1 은 spring `lint.exclude "**/models/**"` 에 숨은 `fortune_record_model.py` 2건을 포함 — 검사기는 ruff 설정과 무관하므로 그대로 red.)

## 4. ⓒ 효과 표

| 항목 | 관측 n(런·저장소) | 레인당 절감(분·왕복) | 과대 추정 | 판단 기준 4 분류 |
|---|---|---|---|---|
| D | 형상 2(spring framework P3·kkebi billing — 둘 다 Codex·동일 작성자) / **증폭 실효 1**(spring 13건) | spring: 발주측 96e8719 49건 배치 안 13건 → 분 단위 · kkebi: **0** | **과대**(n=2 는 형상 기준, 효과·런타임 독립성 모두 1) | «검사가 못 잡는데 ≥2레인» 형식 충족·실효 미달 — 문면 1줄 확률적 |
| E | 사건 0(정책 공백 · 레인 즉석 규칙 «98곳» 은 런 md grep 무히트 → 미확인) | 미측정 | 해당 없음(사용자 결정 사항) | 플러그인이 만든 모양 아님 · 검사 없음 — «결정에 의한 신설» |
| F-1 | 1(spring reading P4) | 프로덕션 결함 1 · 발주측 수리 1회(36258bb) | 아님(단 «26곳» 과대) | 검사가 잡는(mypy `[arg-type]`) 누락 — 훅 범위 밖 → 문면 1줄 |
| F-2 | 부재 21/28 BC(기본 상태) | 미측정(F 유형 1건 조기 검출) | 검증 불가 | 반복 문면 후보 — 소급 강제 시 21 BC 감수자 판단 red |
| G | 채널 결손 2(catalog·reading) / 패턴 5 | catalog: STOP 0·S4 내부 재설계(시간 미분리) · reading: STOP-149 중 12/149 | **과대**(«왕복 1회 절감» → «예보 시점 G1 로 이동») | 검사가 못 잡는(pre-gate 는 블록만) ≥2레인 — 성립 |
| H | 왕복 1(catalog) / red 4레인 | catalog 13:42 · promotion·saju·reading 0(수용·교정) | 수치 정확·일반화 약함(tarot «10일» 은 휴면) | 플러그인 내부 규칙 모순(«빈 채로 실현» ↔ «있으면 하나») — 문면/검사기 수정 대상 |

## 5. 범위 권고

- **D**: 축소 유지 — implementation-python 문면 1줄만(§4.4). 근거 n 은 «형상 2·효과 1·동일 런타임» 이므로 배치 내 우선순위 최하. 검사기·mypy 실행 추가 없음.
- **E**: 강도 1(시그니처 `Any` 0 무조건, `*args/**kwargs` 포함) 채택 가능 — 소급 18건/11파일/8BC 전부 기계 치환 가능. 강도 2(변수 주석) 는 검사기 아닌 문면 «받는 즉시 좁히기» 조건부(소급 +98건) · 강도 3(제네릭 안) 은 기각(소급 253건·Django 스텁 미러 다수). ninja `Schema` 필드는 검사기 선언적 면제로 명시.
- **F-1**: 유지(문면 1줄). **F-2**: 축소 — «신규 BC 부터·소급 강제 없음» 명시(21/28 BC red 방지) · «실배선» 정의를 «팩토리 실호출 + execute 1경로 · 외부 경계 fake 허용» 으로 성문(현 5/16 은 그 정의 기준).
- **G**: 유지 — 조항 문면은 «예외 소비 import» 한정이 아니라 «검사기(#92/#93/#96)가 보는 BC 내부 층 경계 import 도 블록 대상»(조사자 방향) · 효과 서술은 «Phase 2 왕복 절감» 이 아니라 «#93 예보를 G1 로 당김» 으로 정직화.
- **H**: ⓐ/ⓑ 택일의 증거 재료 — ⓑ «영구 잔존 위험» 의 tarot 실증은 휴면 저장소 효과라 근거로 쓰지 말 것 · ⓐ 는 R-2499·R-3188·#488 3곳 동시 개정 비용 실측(조사자) 유지 · 관측 4레인 중 3레인이 «골격 red 는 내용 슬라이스 후 판정» 관행으로 처리했으므로 ⓒ(골격 슬라이스 게이트 유예) 가 데이터와 가장 정합 — 규범 판정은 B 축.

## 6. 미확인 목록

1. 현장 보고 E «리딩 레인 discipline reviewer 가 98곳 교정» — fortune-reading 런 md 에서 «98»+Any/typed grep 무히트.
2. kkebi 실배선 2/12(billing·tarot) 표본 파일 미개봉(monkeypatch 유무).
3. 리딩 P4 위반 코드 원문(미커밋) · 조항 추가 후 architect 형식 반송률.
4. fortune-reading pregate-report `#488` 실제 발견 건수(8행 중 중복 여부).
5. F-1 옛 배선 런타임 `TypeError` 재현(테스트 미실행 — 커밋 메시지 인용만).
6. 카탈로그 S4 «설계 진화 3» 의 분리 소요 시간(커밋 간격 2h07 은 S4 전체).
7. STOP-149 발화·결정 시각(파일 내 시각 미기재 — 조사자 21:50→21:59 진술 의존).
8. kkebi billing-migration 런의 discipline 리뷰가 `_raise_provider_error` 를 못 본 것(조사자 진술 — 런 md 에 `lane-report` 없음).
