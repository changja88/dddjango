# rv3-C — ③ 계획 리뷰 · 리뷰어 C(증거 축 — 무손실 판정식·소급 비용·효과 정직성·표본 외) · 2026-09-04

대상: `workspace/plan/2026-09-04-field-report-repair-2-plan.md`(② 계획). 독립 실측. 원본 두 저장소는 읽기만(`git log/show/ls-files`·`sed`·`grep`), 실행은 전부 scratchpad `fr2/rv3C/`: 격리 복제본 `spring`@**c20f525**(현재 HEAD — ⓪ 측정 시점 d2eaafe 이후 fortune_calculation-2 레인 10커밋이 들어왔다) · `spring-h`@{59d08c7,99253ce,9c8814e,d2eaafe} · `kkebi`@6608fb0 · 검사기 사본 `scripts-orig`(dev main) / `scripts-patched`(② 명세대로 프로토타입 3파일 — H 가드 2 + #645) · 인터프리터 = 각 저장소 `.venv/bin/python` 3.14(requires-python 게이트) · `DJR_FINDINGS_JSON` sink 로 (rule,file,message) 다중집합 차분. 매트릭스 4종 + pre-gate 픽스처 번들은 `workspace/tools/*.py` 를 `S`/`F` 경로만 바꾼 scratch 사본으로 patched 검사기에 대해 실행. Serena: skipped — 리서치·재계산(저장소 코드 무수정).

## 1. 판정 표

| # | 계획 주장 | 판정 | 근거(요약) · 판정식 수정안 위치 |
|---|---|---|---|
| E-a 기대치 «application/* #645 = spring 8 · kkebi 10» | **MAJOR(불완전 → 수정)** | 8/10 은 «application 프로덕션» 한정 수치. 검사기 파일 집합(`_is_target_file` — `test/{factories,fake}` 포함·migrations 제외)으로 프로토타입 실측: application **10/14**(factories 2/4 추가) · 전 저장소 **78/121**(spring (root) 9·framework 59 / kkebi (root) 37·scripts 17·web 53). ⓓ#645 = spring **714**(application 134) · kkebi **385**(application 134). 파일:줄 8/10 목록은 ① C 강도 1 표와 동일(검증). → §2.E |
| E-a 문면 «`self`/`cls`·dunder 는 기존 면제 그대로» | **MAJOR(모호 → 핀)** | `_check_signature` 에 dunder 면제는 **없다**(`_is_dunder` 는 변수·속성 이름용). 함수 이름 dunder 를 면제로 읽으면 Form `__init__(*args: Any, **kwargs: Any)` spring 6/8·kkebi 2/10 이 빠져 기대치가 2(+2)/8(+4) 로 바뀐다. 문면을 «함수 이름 dunder 는 면제 아님» 으로 핀 |
| E-b legacy 차단 0(`registry_gate` N∖L) | **검증됨(코드) · 소급 형태 MINOR 보충** | 키 = `script :: [#645] <path>:N: <msg>`(`_normalize` L145-147 이 `:\d+`→`:N`) → 앵커에 있던 `Any` 는 L∩N(잔존). 재귀속 조건 = 함수·매개변수 **이름 변경·파일 이동**(메시지·경로가 키). 진짜 소급 형태 3: ⑴ Phase 0 빚 스캔(직접 실행·설정 무관) 에 spring 5 BC·kkebi 6 BC 의 빚 항목 ⑵ 손대는 시그니처의 `Any` 는 그 자리에서 치환 ⑶ G2 배너 «legacy 잔존» 행 78/121(노이즈). «차단 0» 은 참이나 ⑴⑵ 를 계획에 적어야 정직 |
| E-c `object` 안내 문면 | MINOR | 메시지에 «정확 타입» 사례(kkebi `has_change_permission(obj)` 는 `object` 가 아니라 스텁 `<Model> \| None`)·`Mapping[str, object]`·TypeIs 좌표(§4 새 블록)가 없다. 치환 자체는 프로브대로 가능(18 전건). `*args: object` 는 양 저장소 ruff `allow-star-arg-any=true` 와 무마찰(ANN401 자체가 ignore) |
| E ⓓ «후보는 감수자가 집행» | **MAJOR(효과 무근거)** | ⓓ 라인은 `registry_gate._FINDING_RE`(`^\s*(\[#\d+\].*)$`) 에 안 걸려 G2 차분 출력에 없고, Coordinator step 5 는 **#4 의 ⓓ 만** 감사 입력에 동봉(`commands/dddjango.md:108`). #11 ⓓ#645 는 어느 채널에도 안 실린다 → 집행 0. 게다가 전 저장소 실행당 spring 714 행(framework 574) 출력. 처방: R-0345 amendment 에 «step 5 입력에 #11 ⓓ#645(대상 BC 범위) 동봉» 1행 추가하거나, 효과 표에 «ⓓ = 관찰 채널(집행 경로 없음)» 으로 적는다 |
| E 표본 외(최신 레인) | 검증됨(보강) | d2eaafe→c20f525 사이 fortune_calculation-2 레인(v2.17.16·09-04·S1~S4): 시그니처 bare `Any` **0** · ⓓ **+20**(`regenerate_place_tables.py` 19 · `packaged_table_adapter.py` 1) + 발주측 1288e4a 1. → 강도 1 의 «신규 레인 차단» 실효는 0/1레인, `Any` 생산은 ⓓ 자리에서 계속됨(위 라우팅 결손이 곧 효과 결손) |
| H 판정식 «HEAD #219/#635 무변 · 59d08c7 5→0 · 99253ce 12 불변» | **검증됨(직접 실측)** | 두 검사기 전 레코드: spring HEAD 167→167 · kkebi 291→291(차분 0) · 59d08c7 167→162 = 정확히 {#219×2, #635×3} · 9c8814e 동일 · 99253ce 169→169(두 검사기 몫 #218×2·#193×3·#576×2 = 7 불변 — «12» 는 #488×5 포함 계수, #488 은 #4 몫·무접촉). exit 59d08c7·9c8814e 2/2→0/0. docstring/comment-only 골격 파일(`skeleton_placeholder` 전체 정의) HEAD spring 0·kkebi 0 → 새 침묵 0 |
| H-a «전체 건너뜀이 내용 규칙만 침묵» | 검증됨 | `_check_port_contract` 의 #551/#220/#212/#241/#485 는 전부 `for cls in classes` 안 → 골격 파일엔 공허. 차분에 #219/#635 외 규칙 0 |
| H «픽스처 27종·cross matrix 무변» | **MAJOR(거짓 → 수정)** | `skeleton/{good_bc,bad_missing,bad_promoted}` 에 **0바이트** `email_sender_port.py`·`place_order_use_case.py` 가 있다(#488 레인 재료). fixture_matrix 102/102 ✓(자기 검사기만) · findings_count 73/73 ✓ · baseline 73/73 ✓ · **cross 348 vs 350 — «기대 red 소멸» 2행**(`('skeleton','check-port-adapter-pairing.py'): (2,((219,1),),…)` · `('skeleton','check-usecase-dto-placement.py'): (2,((635,1),),…)` L476-477) → `--emit-expected` + 사유 «결정 2» 릴리즈 보고 표면화 의무 |
| G 효과 «예보 시점 Phase 2 → G1 이동» | 검증됨(정직 · 조건 병기) | 차단 모드라 = G1 반송 1회. 적용 조건 = 잎이 file-plan **add**(catalog OHS add · reading P4 controller/OHS add — 2/2 해당) · 브라운필드 update 잎(kkebi tarot·billing)은 S3 표면 밖 → 실효 n=2(spring)·kkebi 0. R-3449 를 지키는 architect 는 행을 안 쓰므로 예보 자체가 안 뜬다(효과 = 규범 R-3449 + 채널 조항의 합) |
| G 무손실 «규범 신설 = 검출 집합 무변 · 기존 명세 형식 red 0» | **MAJOR(규범 위반 1 BC 누락)** | 검출 집합 무변은 참(검사기·실행기 무접촉 → 형식 red 판정식 무변 · 사람 판정 현재 7판본 0 = rv1-C G-5). 그러나 R-3449 초안 «잎은 port 예외를 import·catch 하지 않는다» 는 **notification-bc OHS**(`email_notice_service.py:6-10,40` — use case `__all__` 재수출 경유로 `EmailNoticeTransportError`·`EmailNoticeRenderingError` = `application_layer/port/**/exception.py` 정의 를 catch · G1 승인 설계 09-02) 를 문면 위반으로 만든다(#93 은 import 경로만 봐 침묵). 표본 3 BC: fortune_catalog(`catalog_inquiry_service.py:103/125/145` `_source_unavailable` catch)·fortune_reading(`prepare_fortune_evidence_failure`)·fortune_record 는 정합, notification 만 충돌. enforcedBy `#93` 은 **부분 집행**(import 경로만 · 재수출·use case 미번역은 못 잡음) → wiring 주석 필요. 처방 §2.G |
| F-1 «팩토리 본문 안 `partial`» = HEAD 모양 | 검증됨 | `dependency_wiring.py:31-47`: `partial(service_runtime.retrieve_release_evidence_with_local_embedder, data_root=data_root)` 가 `build_prepare_fortune_evidence_use_case()` 본문 안, `data_root` 는 지역. 최상단 `Assign` 은 #85 red(`_check_dependency_wiring` L1871-1875) ✓ |
| F-2 «fake 는 외부 I/O 경계뿐» | **MINOR(문면 · 선례 자격 밖)** | spring `test_composition_root_wiring.py` fake 2: ① `dependency_wiring.QueryTranslationAdapter`(자기 BC ACL driven 어댑터 — 타 BC OHS `translate_command` 소비 · 프로세스 내) ② 모델 가중치 verify/load(디스크). 문자 그대로면 ①은 외부 I/O 가 아니라 **유일 선례가 자격 미달**. ①로 인해 주입 callable `translate_command` 는 이 경로가 안 탄다(«이 경로만 잡는다» 는 교체 안 한 어댑터 3에 한함). kkebi: billing 4파일 patch 0(진짜·DB) · tarot 2파일 patch 4~5(부분) — rv1-C 미확인 2 해소 |
| D «0~1건/저장소·확률» 표기 | 검증됨 | 형상 n=2(spring 43e9628 `_fail :54` · kkebi `payment_processing_adapter.py:437`) · 증폭 실효 n=1(spring 13→0 · kkebi 0) · 둘 다 Codex. 문면 효과는 다음 발생의 회피(확률) — 계획 §3 에 D 효과 서술이 없으므로 이 문안을 넣는다 |
| 현장 보고 정정 목록 | — | §3 |
| ⓒ 효과 표 | — | §4 |

## 2. 판정식 수정안 — 항목별 «측정 절차 · 기대치»

### E — #645 (검사기 차단 추가)

측정 절차: 격리 복제본(`git clone -q <원본> && git checkout -q --detach <sha>` — spring **c20f525** · kkebi **6608fb0**; 원본 무접촉) · `DJR_FINDINGS_JSON=<sink> <repo>/.venv/bin/python <scripts>/check-public-surface-annotation.py <복제본 루트>` 를 orig/patched 각 1회 · `(rule,file,message)` 다중집합 차분.

| 기대치 | spring c20f525 | kkebi 6608fb0 | 비고 |
|---|---|---|---|
| A∖B(기존 규칙 소멸) | **0** | **0** | #493·#358·#456·#69 발화 집합 불변 — 실측 |
| B∖A = #645 violation 전 저장소 | **78** | **121** | (root)=fabfile 등 |
| └ application | **10** = prod 8 + `test/factories` 2 | **14** = prod 10 + factories 4 | prod 8/10 파일:줄 = ① C 강도 1 표 · `Any \| None` 1/2 포함 |
| └ 그 밖 | (root) 9 · framework 59 | (root) 37 · scripts 17 · web 53 | 레인 밖 — legacy 잔존 |
| ⓓ#645 전 저장소 | **714** (application 134 = prod 132 + material 2) | **385** (application 134 = prod 123 + material 11) | d2eaafe 기준 application 113 — jsonl 재집계 114(±1 분류 경계) 와 정합 |
| exit | 2 → 2 | 2 → 2 | 규약 2/0/1 불변 |
| 매트릭스 | findings_count public-surface 행 `#493×8` → `+#645×6` · info `#69×2` → `+ⓓ#645×1`(새 bad 픽스처) · cross **무변**(현 픽스처 318 케이스 실측 public-surface 차이 0) · fixture 102 · baseline 73 | | |

핀 5: ⑴ 함수 이름 dunder(`__init__`) 면제 **없음**(6/8·2/10 이 여기 있다) ⑵ `Optional[Any]`·`Any | None`·`Union[Any, …]`·문자열 `"Any"`·별칭 `_Any`·`typing.Any` = bare ⑶ 선언적 클래스(ninja `Schema`) 본문의 메서드 시그니처도 대상(현행 `_scan_class` → `_check_signature` 경로 그대로) ⑷ `registry_gate` 소급 = 귀속 0 · 재귀속 조건 = 이름 변경·파일 이동 · 직접 실행 채널(Phase 0 빚 스캔·G2 배너 legacy 행)엔 그대로 표시 ⑸ 표본 외 = fortune_calculation-2(최신 레인) 시그니처 0·ⓓ +20 을 ④ 결과에 기록.

수정 문안(계획 §1 E «소급 기대치»): «격리 실행 #645 = 전 저장소 spring 78 · kkebi 121, 그중 application/* spring 10(프로덕션 8 + factories 2) · kkebi 14(10 + 4) — 프로덕션 8/10 은 ① C 강도 1 표 파일:줄과 동일. ⓓ#645 = spring 714(application 134) · kkebi 385(application 134). 기존 규칙 발화 집합 A∖B = 0. `registry_gate` 는 경로+메시지 키(라인 정규화)라 앵커 잔존은 귀속 0 — 단 이름 변경·이동은 재귀속, Phase 0 빚 스캔에는 spring 5 BC·kkebi 6 BC 빚 항목으로 선다.»

### H — skeleton_placeholder 가드 (#219/#635)

측정 절차: 두 검사기(orig/patched) × 5 트리 상태(spring HEAD · kkebi HEAD · spring-h 59d08c7/99253ce/9c8814e) · sink 차분 + exit · 골격 파일 계수(`count_skeleton.py` — `skeleton_placeholder` 정의 전체: 0바이트·공백·주석-only·docstring-only).

| 기대치 | 실측 |
|---|---|
| HEAD spring/kkebi 두 검사기 전 레코드 차분 | **0/0** (167→167 · 291→291) · exit 0,0/0,2 무변 |
| 59d08c7 | A∖B = {#219×2, #635×3} **정확히** · 다른 규칙 0 · exit 2,2→**0,0** |
| 99253ce | 차분 0 · 두 검사기 몫 7 불변(#218×2·#193×3·#576×2) — «12» 중 #488×5 는 #4 몫 |
| 9c8814e | = 59d08c7 |
| 새로 침묵하는 골격 파일 | HEAD spring **0** · kkebi **0**(docstring/comment-only 포함) · 59d08c7 정확히 5(전부 0바이트) |
| fixture_matrix / findings_count / baseline | 102/102 · 73/73 · 73/73 |
| **checker_cross_matrix** | **348 vs 350 — 기대 red 소멸 2행**(skeleton × port-adapter-pairing #219×1 · skeleton × usecase-dto-placement #635×1) → `--emit-expected` · 사유 «결정 2 — skeleton fixture 의 0바이트 port/entry 는 내용 규칙 밖» · 릴리즈 보고 표면화 |
| pre-gate 픽스처 번들(`pregate_fixture_run.py` · EXECUTOR/GATE = patched) | 케이스 전건 «기대 일치»(enforce·check-report 계열 포함) · FAIL 1 = `plugin_version() '(unknown)' ≠ '2.17.16'` — scratch 경로에 `.claude-plugin/plugin.json` 이 없어서 생긴 아티팩트(패치 무관) |

수정 문안(계획 §1 H «무손실 판정식»): «픽스처: fixture_matrix 102 · findings_count 73 · baseline 73 무변, **cross matrix 는 skeleton 레인 0바이트 port/entry 로 인해 EXPECTED 2행 소멸**(`--emit-expected` · 사유 기록). 양 저장소 HEAD 두 검사기 전 레코드 차분 0 · 카탈로그 59d08c7/9c8814e 정확히 {#219×2,#635×3} 소거·exit 2→0 · 99253ce 두 검사기 몫 7 불변 · docstring-only 골격 HEAD 0/0.»

### G — R-3427 clarification + R-3449 + S3 문면

측정 절차(판정식을 «검출 집합 무변» 에서 «규범 위반 조사» 로 바꾼다 — 검사기 무접촉이라 기계 차분은 항등): 7 BC(+kkebi 12 BC) driving 잎의 port 예외 catch 를 ⑴ 직접 import ⑵ use case 모듈 재수출 경유 로 계수.
기대치: ⑴ 0/0 ⑵ spring **1**(notification `email_notice_service.py:40`) · kkebi 0. → R-3449 문면에 처분 명시: «use case 모듈이 port 예외를 재수출해 잎이 잡는 것도 같은 위반(#93 은 못 본다)» + notification 을 발주측 빚(레인 산출물 · G1 승인 09-02)으로 루브릭 ④ 절에 기록, 또는 문면을 «잎은 port 예외 **타입**에 의존하지 않는다» 로 써서 재수출을 명시적으로 포함. wiring: enforcedBy `c/check-context-isolation.py` 에 «부분 집행 — import 경로만» 주석.
효과 문안: «#93 예보를 G1(차단 반송)로 당긴다 — 잎이 file-plan add 인 레인만(브라운필드 update 잎은 S3 표면 밖) · 실효 n=2(catalog·reading, 둘 다 add) · R-3449 준수 시 예보 자체가 0(그것이 목적)».

### F — 문면 2

F-1: 무변(HEAD 모양과 일치 실증). F-2 문안 수정: «fake 는 **프로세스 밖 경계**(외부 I/O·타 BC OHS 소비·모델 가중치 소재)뿐 — 자기 BC 의 use case·어댑터 생성자·주입 callable 은 실물» (spring 선례가 자격 안에 들도록). 기대치: 자격 있는 기존 테스트 = spring 4(media_library·service_policy·fortune_character·fortune_reading) · kkebi 1(billing) — 강제·소급 없음이므로 수치는 기록용.

### D — 문면 1

효과 문안(계획 §3 에 추가): «기대 효과 = 다음 발생 시 mypy 증폭 회피 — 관측 형상 2/2저장소·증폭 실효 1(spring 13건 · kkebi 0) · 둘 다 Codex · 검사기 0 · 확률적».

## 3. 현장 보고 정정 문안(원문 보존 · «정정(09-04 ③ C)» 추기)

| 위치 | 원문 | 정정 추기 |
|---|---|---|
| 추적표 A·F «고칠 곳» · §A 제안 3 · §F-2 | `discipline-test`/`implementation-test` | «dddjango 에 `discipline-test` 스킬은 없다(dddart 전용). F-2 착지 = `discipline-tdd` §5.5 보호 대상 자격(R-3450) · A 제안 3 은 종결» |
| 추적표 F · §F «왜 통과했나» 3 | «테스트 26곳 전부 팩토리 fake» | «미재현 — 36258bb^ 실측: 팩토리 patch 14지점/5파일(+llm_access 3) · 실 `build_*()` 호출 0. 실배선 부재는 1레인 특이가 아니라 기본 상태(spring 11/16·kkebi 10/12 BC)» |
| 상태 블록 D · 추적표 D · §D | «13건 증폭» | «13건 = spring 1사건(43e9628 `_fail :54` · mypy 13→0 실측 · 발주측 96e8719 로 해소). kkebi 동형 1건(`payment_processing_adapter.py:437`)은 증폭 0. 문면 1줄의 기대 효과 = 다음 발생 회피(확률)» · §D `:635` → 43e9628 기준 `:54`(HEAD `:642`) |
| 추적표 E · §E 규모·판정 | «시그니처 `Any` 47(RAG 런타임 38·fabfile 7) · application 0» | «47 은 프로젝트 ruff 설정(ANN401 select→ignore · `allow-star-arg-any` · `lint.exclude **/models/**`) 효과 — 분할은 framework 38·fabfile **9**. 검사기 규칙(설정 무관) 기준 application 시그니처 bare `Any` = spring 프로덕션 **8**(+factories 2) · kkebi **10**(+4) · 전 저장소 78/121» |
| §E 관찰 | «98곳을 교정» | «미확인 — fortune-reading 런 md 에 근거 없음» |
| 상태 블록 H · §H | «왕복 2회·≈14분» · «#218/#193/#576 캐스케이드» · «1레인 관측» | «게이트 red 2회 = 파일 왕복(삭제→복원) **1회** · 13분 42초 · 부재 시 #488×5 포함 12행 · pre-content #219/#635 red 는 **4레인/2저장소**(promotion-pricing·fortune-reading·saju·catalog) 반복, 삭제 왕복만 1레인» |
| §G·H 머리 | «lane 6» | «정의 없음(발주서·orders 부재) — ledger 레인 4» |
| §G | «블록(6행)» · «Phase 2 슬라이스에서 #93 발화» | 6행 정확(G1 판본 · 현재 5행) — 무정정 · «catalog 는 STOP 0 · S4 내부 재설계(REPORT «설계 진화 3»)» |
| 루브릭 ⓪ H | «tarot domain 12 … 10일째» | «활성 개발 중 ≈27h(마지막 커밋 08-26 23:21 · 이후 커밋 0 = 휴면) · 그 칸엔 «하나» 규칙이 없어 ⓑ 근거 부적합» |
| 루브릭 ⓪ F | «실배선 spring 5/16 · kkebi 2/12» | «엄격 기준 spring 3/16 + 부분 1(fortune_reading) · kkebi billing 진짜(patch 0)·tarot 부분(patch 4~5)» |

## 4. ⓒ 효과 표 재확정

| 항목 | 관측 n | 절감(레인당) | 표기 문안 |
|---|---|---|---|
| D | 형상 2(spring framework P3·kkebi billing · 둘 다 Codex) / 증폭 실효 1 | spring 형 13건급 mypy 소음 회피 · kkebi 0 | «문면 1줄 · 확률 · 0~1건/저장소» |
| E | 정책 공백(사건 0) · 소급 = 시그니처 8/10(+factories 2/4) · 최신 레인(fortune_calculation-2) 시그니처 0·ⓓ +20 | 차단: 신규 시그니처 `Any` 0 결정적 · ⓓ: **집행 경로 없음**(라우팅 전까지 관찰 채널) | «결정에 의한 신설 · 차단 효과는 시그니처 자리만 · ⓓ 는 Coordinator 라우팅 추가 시에만 효과» |
| F-1 | 1(reading P4) · 정적 검출 실증 | 결함 1 · 발주측 수리 1회 | «문면 1줄 · 1레인 특이» |
| F-2 | 부재 21/28 BC(기본 상태) | 미측정 | «자격 항목 · 강제·소급 없음 · 기존 자격 spring 4·kkebi 1» |
| G | 채널 결손 2(catalog·reading, 둘 다 add) / 패턴 5 | 예보 시점 → G1 차단 반송 · 왕복 절감 아님(catalog STOP 0 · reading 12/149) | «예보 시점 G1 이동 · add 잎 한정 · 실효 1~2레인» |
| H | 왕복 1(catalog 13:42) / pre-content red 4레인 | catalog 13분 42초 · 타 3레인 0(수용) · 이후 레인 pre-content red 0(결정적) | «pre-content red 소거(결정적) · 잔여 위험 = 영구 빈 파일(인수 테스트·명세 소관)» |

## 5. 미확인

1. pre-gate 픽스처 번들 patched 실행 — 케이스 전건 기대 일치(§2.H 표). 단 ④ 에서는 실제 `dddjango/scripts` 위치에서 재실행해 `plugin_version` 대조까지 green 을 확인해야 한다(scratch 실행은 manifest 부재로 그 1항만 FAIL).
2. #645 프로토타입은 ② 명세의 독해라 ④ 구현과 세부(메시지 문구·`Union[Any, X]` 취급)가 다를 수 있다 — 기대치 78/121·10/14 는 «루트 `Any`(Optional/`| None`/Union 언랩)» 정의 기준.
3. notification-bc 재수출 경유 catch 의 처분(빚 vs 문면 범위 조정)은 사용자 결정 사안 — ④ 전 결정 게이트 브리프에 1행 상신 권고.
4. 현장 보고 «98곳» 원자료 · D §204 `:635` 의 스냅숏 기준.
5. ⓓ#645 라우팅 처방의 소유(Coordinator R-0345 amendment 범위 안인지)는 B 축 판정.
