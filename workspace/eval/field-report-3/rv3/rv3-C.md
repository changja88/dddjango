# rv3-C — ③ 계획 리뷰 · 리뷰어 C(증거·표본 외 축 — 기대 수치·무손실 증명 설계·소급·회신 정직성) · 2026-09-04

대상: `workspace/plan/2026-09-04-field-report-repair-3-plan.md` §5(무손실·검증) · §3(픽스처) · §4-5(회신 3) · §7(리스크) + §2.1/§2.4 의 수치 전제. 실서고 무접촉 — 실행은 전부 격리 사본 `$S/fr3/{spring(7bfe1aa)·spring-d2eaafe·spring-c20f525·spring-f5ee428·kkebi(6608fb0)}` 와 `$S/rv1C/spring-gate`(클린 클론 · 실험 뒤 `git checkout -- .` 복원 확인) 에서, 산출은 `$S/rv3C/`. mypy 는 spring/kkebi 실서고 venv 인터프리터를 cwd=사본으로. 이전 산출 재사용: `$S/rv1A/patch493.py`·`synth493` · `$S/proto/proto_646.py` · `evidence/S4/proto_647.py`(스캔 부품) · `$S/rv1C/s5_count.py`. 자체 스크립트: `lossless.sh`+`lossless_fx.py`+`lossless_diff.py`(무손실 판형) · `c647.py`(#647 루트 필터·반환 object ⓓ·유니온·#645 1:1) · `c646_fold.py`(#646 접기·ⓑ(i) 확장) · `c650.py`. Serena: skipped — 리서치·재계산(코드 수정 없음 · `.serena/project.yml` 부재).

브랜치 상태: `git diff main -- dddjango/scripts` = 0 파일(검사기 미구현) → 무손실 판형은 «구현 전 = old≡new» 로 1회 실행해 판형 동작만 보였다(§3).

## 1. 판정 표

| # | 계획 항목 | 판정 | 근거(요약 · 상세 §2~§4) |
|---|---|---|---|
| C-1 | §5 «#646~#650 이외 라인 byte 동일» 증명 설계 | **MAJOR(설계 미명세 — 명령·정규화·키·열거 출처 없음 → 판형 제공)** | 계획은 판정식만 있고 (i) old/new 트리 확보법 (ii) 인터프리터·cwd·sink (iii) «라인» 의 범위(요약·계수 행은 반드시 달라진다 → 발화 라인 `[ⓓ?#N]` 만) (iv) A∖B 허용의 키(ⓓ#645→#647 1:1 은 **슬롯** 단위여야 — spring 혼재 줄 2) (v) 픽스처 «87루트» 의 열거 출처(fixture_matrix 104 케이스/78 루트 · cross 31 레인 · S5 의 87 은 자기 열거) (vi) #649 검증에 필요한 f5ee428 사본 누락 — 이 여섯을 `$S/rv3C/lossless.sh` 가 고정한다(§3 · 1회 실행 LOSSLESS) |
| C-2 | §5 기대 계수(#646·#647·#650·#648·#649·반환 object ⓓ) | **MAJOR(전 루트 수치는 재현되나 §2.1 루트 필터 뒤 수치와 어긋남 — ④ 검증 기준선 오판)** | §2 표. 계획 수치 600/267·304/436·41/8·«kkebi 157» 은 **루트 필터 전** 값이고 §2.1 은 신규 규칙 3종에 `application/**`·`framework/**` 필터를 건다 → 실제 기대치 = spring 차단 **594**·ⓓ **255** · kkebi **161**·**253** · #650 **40**·**7** · #645→#647 1:1 kkebi **52** · 반환 object ⓓ kkebi **42**(계획 34 — 오라클 미명세) · #646 18/31/21 은 필터 무관(전부 application) |
| C-3 | #645→#647 이동 1:1(spring 518·kkebi 157) | **검증됨(전 루트) + MINOR(키 단위)** | 현 검사기 sink 의 ⓓ#645 nested 줄 ∩ #647 Any 차단 줄 = spring **518/518** · kkebi **157/157**(#647 Any 줄 중 ⓓ#645 없는 줄 0) · «둘 다 남는» 유니온(`dict[str, Any] \| Any`) **0/0** · 단 같은 def 줄에 ⓓ#645 nested 슬롯이 #647 슬롯보다 많은 «혼재 줄» spring **2**(`steps/__init__.py:747` 2:1 · `release_store.py:533` 4:3) → 배타는 노드 단위(계획대로)이되 **증명 키는 (경로, 줄, 슬롯 라벨)** 이어야 한다 · 루트 필터 뒤 kkebi 는 52(scripts 39·web 66 은 #647 밖 → ⓓ#645 nested 로 남음) |
| C-4 | #493 수리 «검출 집합 불변» | **검증됨** | `patch493.py` 재적용(main 검사기 → `$S/rv3C/ps493`) · 6 대상 before/after: spring 3,292/3,292 · d2eaafe 3,303/3,303 · kkebi 294/294 · public_surface good 0/0 · bad 20/20 · naming/bad 4/4 — lost/gained 전부 0 · synth493 **5→0** |
| C-5 | ⓔ2 registry_gate ⓓ 앵커 — «HEAD=앵커 → ⓓ 신규 0» · legacy 규모 · 브라운필드 귀속 | **검증됨(메커니즘) + MAJOR(§7-3 — smoke P0′ byte 동일·sidecar `records` 오염 미설계)** | 게이트 산식을 ⓓ 라인에 그대로 적용(`:\d+`→`:N` · `$S/rv3C/gate/`): 앵커 스냅숏 L′ 805(ⓓ#645 708·ⓓ#69 97) · docs 변경 N′∖L′ **0** · legacy 파일 첫 줄 주석 삽입(줄 밀림) **0** · ⓓ 함수 개명 `_index_entry→_index_entry_rv3c` → N′∖L′ **1**·L′∖N′ 1(메시지의 함수명이 키). 격리 뒤 legacy ⓓ = spring ⓓ#647 255(+반환 object 8 · #650 40) · kkebi 253(+42 · 7). 브라운필드: 최근 40 커밋 중 ⓓ 파일을 손댄 커밋 spring 18·kkebi 21 · 그 파일들의 ⓓ 상한 중앙 **0**/평균 18.3(RAG 상환 머지 163 포함)/kkebi 2.6 — 줄 밀림은 0 이므로 실제 귀속은 «개명·매개변수명 변경한 슬롯 수» 뿐. **그러나** `registry_gate_smoke` P0′ 는 수리 전 게이트(34c74a6)와 출력·sidecar 를 마스킹 뒤 **byte 동일** 단언(:377~378) — 새 «ⓓ 신규/legacy» 절이 ⓓ 0 일 때도 인쇄되거나 sidecar 에 새 키가 항상 실리면 P0′ red · sidecar `records` 에 ⓓ 를 섞으면 재생성 루프(«유일한 입력」)에 후보가 주입된다 — 계획 §2.4 에 둘 다 없음 |
| C-6 | 소급·legacy 표(회신 3용) · 루트 필터의 web/scripts 제외 | **검증됨(필터) + MINOR(회신 항목 ④⑤ 문구가 필터와 모순)** | grep(보고자 패턴·비테스트) kkebi `web/` **111** · `scripts/` **212**(rv1-B «206» 은 시제품 줄 기준 · 내 시제품 213=차단 39+ⓓ 174) · 루트 필터 뒤 kkebi 대상은 application 161/252 + framework 0/1 뿐 · spring 은 docs 1·scripts 4/8·spring_dream_server 2/3 제외 → 594/255. rv1-B §5-13 ④ «web/·scripts/ 앵커 격리» 와 ⑤ «루트 필터 부재 이월 고지» 는 §2.1 루트 필터 채택으로 **거짓** — «대상 밖(루트 필터)」 로 고쳐야 |
| C-7 | 회신 3(§4-5) — 효과 정직화·재분류표·발주측 항목 8 근거 | **MINOR** | §4-5 는 «효과 정직화(rv1-C §5)·legacy 규모」 를 적었으나 **«판단 기준 4 재분류표」 는 명시 없음**(rv1-C §5 의 하위 표라 «포함」 으로 읽을 수는 있음 — 명시 권고). 항목 8 근거: ① 152→124·26 ✓ ② «kkebi 22줄」 → #646 발화는 **21**(22줄 중 `catalog_controller.py:101 Query(None)` 1 은 규칙 밖) ③ 감소분 0 실측 ✓ ④ «1,098줄」 은 grep · 검사기 기준은 594+255 · `Form.clean -> dict[str, Any]` 22 → 루트 안 **18**(spring 15·kkebi 3) ⑤ 모순(C-6) ⑥ 리딩 2건 ✓ ⑦ 13 함수·31 자리 ✓(§2) ⑧ tarot 1 ✓ |
| C-8 | §7 리스크 2 — 반환 `object` ⓓ 오탐(spring 8·kkebi 34) | **MINOR(수치 42 · 형상 5군 — 문면 «입구 밖 자리표시」 만으로는 3군을 설명 못 함 → 물음 문안 제안)** | §5 표 · 형상: ⑴ 도메인 이벤트 `pull_events -> list[object]` kkebi 16(spring 0 · 픽스처는 bare `list` 19 라 대상 밖) ⑵ 프레임워크 콜백 미러(`_reject_json_constant`·pydantic `field_validator` before) 5 ⑶ 좁히기 도우미(`_sequence`·`_require_sequence`) 4 ⑷ JSON 값 변환(`JsonValue` 대체 가능) ≈11 ⑸ 누수 후보(port·wiring·use case·admin display) spring 5·kkebi 6 |
| C-9 | §3 픽스처 신설 «mypy 검증 필수» | **MINOR(관례 없음 · 레시피 미명세 — 실측 레시피 제공)** | 픽스처는 mypy 를 돌리지 않는다(Makefile·tools 에 mypy 0 · 09-03 선례는 **코퍼스 예시** strict 0). 현 good `order_form.py` 는 strict **22 errors**(`**kwargs: object` → `BaseForm.__init__` arg-type) — «good 은 strict 통과」 관례는 없다. 동작하는 레시피: `cd <fixture good 루트> && PYTHONPATH=$S/spring MYPYPATH=$S/spring <spring venv>/python -m mypy --config-file $S/spring/pyproject.toml --follow-imports=silent application`(19 files 검사 · 픽스처 모델 `AccountUser` 해소 ✓ · kkebi venv 동일 결과) → 대상은 **신설 파일만** 이라고 명시 |
| C-10 | §5 «registry_gate 귀속 0(HEAD=앵커)」 | MINOR(문면) | 앵커=HEAD·clean 은 exit 1(공허 차분 — V 케이스) → «앵커=HEAD + 무해 변경(docs)」 또는 «앵커=HEAD~1(docs-only 커밋)」 로 적어야 실행 가능(rv1-C run2 판형) |

## 2. 수치 재검증 표 (계획 §5 vs C 독립 재계수)

| 항목 | 계획 §5 | C 전 루트 | C **루트 필터(app+fw)** | 일치 | 방법 |
|---|---|---|---|---|---|
| #646 spring HEAD | ⓑ 17+1 | ⓐ 0·ⓑ 17·ⓑ′ 1 → **18**(16 파일·8 BC) | 18 | ✓ | `proto_646.py` → `c646_fold.py`(클래스당 1건 접기) |
| #646 d2eaafe | ⓐ 13·ⓑ 17+1 | ⓐ 13·ⓑ 17·ⓑ′ 1 → **31**(25 파일·9 BC) | 31 | ✓ | 〃 |
| #646 kkebi | ⓑ 21 | ⓐ 0·ⓑ 21 → **21**(21 파일·4 BC) | 21 | ✓ | 〃 |
| #646 ⓑ(i) «모든 ClassDef 헤더」 확장 추가 발화 | (미기재) | 기저 집합 밖 **0/0/0** · code 없는 ignore 헤더 ⓓ **0** | — | ✓(확장 비용 0) | AST 헤더 범위 스캔 |
| #647 spring HEAD 차단/ⓓ 줄 | 600 / 267 | 600(Any 518·object 반환 66·속성 18) / 267 | **594**(518·60·18) / **255** | 전 루트 ✓ · 필터 뒤 ✗ | `c647.py` |
| #647 c20f525 | — | 609 / 273 | 603 / 261 | — | 〃 |
| #647 kkebi | 304 / 436 | 304(Any 157·반환 90·속성 59) / 436 | **161**(52·59·52) / **253** | 전 루트 ✓ · 필터 뒤 ✗ | 〃 |
| #647 루트별(kkebi) | — | web 104/7 · scripts 39/174 · application 161/252 · framework 0/1 | 제외 web·scripts | — | 〃 |
| #645 nested ⓓ → #647 1:1 | spring 518 · kkebi 157 | **518/518 · 157/157**(#647 Any 줄 ⊂ ⓓ#645 줄 · 나머지 ⓓ#645 nested spring 5·kkebi 58 잔존) | spring 518 · **kkebi 52** | 전 루트 ✓ | 현 검사기 sink × `c647.py --sink` |
| 유니온 «둘 다 남는」(`dict[str, Any] \| Any`) | (미기재) | **0 / 0** | 0 / 0 | — | 〃 |
| 혼재 줄(ⓓ#645 슬롯 > #647 슬롯) | (미기재) | spring **2** · kkebi 0 | — | — | 〃 |
| 반환 object ⓓ(델타) | spring ≈8 · kkebi 34 | spring **8** · kkebi 67 | 8 · **42**(root 18·list 19·tuple 4·Sequence 1) | spring ✓ · kkebi ✗(오라클 미명세) | `c647.py` `return_object_shape` |
| Form.clean `-> dict[str, Any]` 차단 잔존 | (rv1-B ④ 22) | spring 15 · kkebi 6 | spring 15 · kkebi **3** | — | 〃 |
| Form.clean `-> dict[str, object]` 면제 | — | kkebi 1(spring 0) | 〃 | ✓ | 〃 |
| #650 spring / kkebi | 41 / 8 | 41(annassign 12·comprehension 25·direct 4) / 8(literal 6·annassign 2) | **40 / 7**(docs 1·scripts 1 제외) | 전 루트 ✓ | `c650.py` |
| #648 spring HEAD / f5ee428 / kkebi | 7 / — / 6 | **7 / 8 / 6** | 〃 | ✓ | `s5_count.py` |
| #649 f5ee428 / HEAD / kkebi | 1 | **1 / 0 / 0** · RootModel 단독 spring 5·kkebi 1 | 〃 | ✓ | 〃 |
| #493 6 대상 lost/gained | 0/0 | **0/0** ×6 · synth 5→0 | — | ✓ | `patch493.py` 재적용 |
| ⓓ 채널 총량 추정(public-surface · 줄) | — | spring 666 → **≈451**(ⓓ#645 51+#647 255+#650 40+반환 8+#69 97) · kkebi 551 → **≈801**(327+253+7+42+172) | — | — | 위 표 합성 |

## 3. 무손실 증명 판형 (`$S/rv3C/lossless.sh` · 구현 전 1회 실행)

판형(fr2 rv6 `run_iso.sh`+`diff.py` 재현 + 이번 허용 규칙):
- old = `git archive main dddjango/scripts` → `$S/rv3C/scripts-old` · new = 브랜치 working tree(또는 ref) → `scripts-new` · `diff -rq` 로 바뀐 파일 목록을 먼저 고정(«나머지 24 검사기 byte 동일」 의 근거).
- 대상: `spring`·`spring-d2eaafe`·`spring-f5ee428`·`kkebi`(cwd=사본 · target `.` · 인터프리터 = 각 실서고 venv · `env -u DJR_VIOLATIONS_DIR -u DJR_SOURCE_GIT_ROOT DJR_FINDINGS_JSON=<sink>`) × 3 검사기(`check-public-surface-annotation.py` · `check-api-error-controller-contract.py --error-profile auto` · `check-openapi-error-declaration.py --error-profile auto`) + 픽스처 = `fixture_matrix.build_cases()` 중 3 검사기 케이스 **9** (argv 그대로 · 스크립트 경로만 치환) + `checker_cross_matrix.lanes()` good 루트 **31** × 3 검사기(registry argv) = 93 → 102 판정.
- 판정(`lossless_diff.py`): (severity, rule, 상대경로, message) 다중집합 차분 — B∖A 는 {#646,#647,#648,#649,#650} 만 허용 · A∖B 는 (info,#645) 이고 같은 (경로,줄) 에 B 의 (violation,#647) 가 있을 때만 허용(→ **구현 시 (경로,줄,슬롯 라벨) 로 격상** — C-3) · 그 밖은 RED · #493 old/new 계수 · exit · stdout 은 `[ⓓ?#N]` 발화 라인만 다중집합 비교(요약·계수 행 제외) · 사본의 타 조사자 untracked `mp_probe_*` 는 양쪽에서 제외.
- 실행 결과(run 2 · `$S/rv3C/lossless-run2.log` · `out/verdict.txt`): scripts diff **0 파일** · spring 4,097/4,097(#493 3,216) · d2eaafe 4,083/4,083(3,225) · f5ee428 4,112/4,112(3,225) · kkebi 851/851(173) · api-error 7/6/7/27 · openapi 0 · exit 전부 동일 · 픽스처 **102 OK · 0 RED** → `VERDICT: LOSSLESS`(구현 전이므로 판형 동작 확인 = 기대대로 차분 0). 구현 뒤 기대 판형: B∖A = #646 18/31/—/21 + #647 594(+ⓓ 255+8)/…/161(+253+42) + #650 40/…/7 + #648 7/…/8/6 + #649 —/—/1/0 · A∖B = ⓓ#645 518/…/52 전부 matched · 비허용 0.

## 4. 소급·legacy 표 (회신 3용 · 루트 필터 뒤 · 앵커 격리 전 전량)

| 규칙 | spring HEAD | kkebi HEAD | 격리 채널 | 루트 필터로 빠지는 것 |
|---|---|---|---|---|
| #646 | **18**(클래스 17+속성줄 1 · 16 파일 · 8 BC) | **21**(21 파일 · 4 BC) | N∖L(exit) · 개명·기저 교체 시 귀속 | 0(전부 application) |
| #647 차단 | **594**(Any 518 · object 반환 60 · 속성 18) — rag 449 · fortune_character 27 · fortune_calculation 24 · chat_relay 17 · promotion 14 · fortune_reading 11 · product 10 | **161**(Any 52 · 반환 59 · 속성 52) — saju 54 · billing 36 · product_observability 23 · tarot 20 · share 11 · identity 7 | N∖L(exit) | spring docs 1·scripts 4·server 2 · kkebi web 104·scripts 39 |
| #647 ⓓ(object 매개변수/변수) | **255** — rag 127 · fortune_reading 42 · llm_access 35 · chat_relay 19 · fortune_record 11 | **253** — billing 116 · product_observability 30 · tarot 27 · identity 26 · saju 21 · notification 13 · daily 12 | ⓔ2 N′∖L′(보고) — 줄 밀림 0 · 개명 시 그 슬롯만 | spring scripts 8·docs 1·server 3 · kkebi scripts 174·web 7 |
| #647 반환 object ⓓ(델타) | **8** | **42**(오라클: 루트·시퀀스 원소 · `\| None` 포함) | ⓔ2 | kkebi 25(scripts/web) |
| #650 ⓓ | **40**(framework 32 · application 8) | **7** | ⓔ2 | docs 1 · scripts 1 |
| #648 | 7 함수(accounts 6 · fortune_record 1) | 6 | N∖L | 0 |
| #649 | 0(f5ee428 시점 1) | 0 | — | — |
| #63 code-json(기존) | 2(리딩 400·503) | 31(identity 16·saju 9·review 5·image 1) | 이미 legacy | — |
| `Form.clean -> dict[str, Any]`(#647 차단 legacy · 회신 안내) | 15 | 3(+web 2·전 루트 6) | N∖L | web 2 |
| 브라운필드 update 잎 노출 상한 | 최근 40 커밋: ⓓ 파일 손댄 커밋 18 · ⓓ 상한 중앙 0/평균 18.3/최대 163(RAG 상환 머지) | 21 · 중앙 0/평균 2.6/최대 30 | 줄 밀림 0 실증 → 실제 귀속 = 개명 슬롯 수 | — |

## 5. §7 리스크 2 — 반환 `object` 형상 판정 · ⓓ 물음 문안

| 군 | 형상(예) | spring | kkebi | 판정 | «입구 밖 자리표시」 문면이 설명하는가 |
|---|---|---|---|---|---|
| ⑴ 도메인 이벤트 컬렉션 | `pull_events(self) -> list[object]`(«이 BC 는 이벤트를 발행하지 않아 항상 빈 리스트 · #545」) | 0 | 16 | 정당에 가까움 — 이벤트 기저 타입이 없어 `object` 를 골랐다(코퍼스 예시는 `List[DomainEvent]` · 픽스처는 bare `list`) | ✗ — «이름 붙일 이벤트 타입이 있는가」 물음 필요 |
| ⑵ 프레임워크 콜백 미러 | `_reject_json_constant(value: str) -> object`(`json.loads(parse_constant=)`) · pydantic `field_validator(mode="before") -> object` · admin `@display -> object` | 1 | 5 | 정당(스텁 시그니처 미러 · R-3447 «우리 선언은 object」 와 같은 결) | ✗ — 프레임워크 미러 예외 언급 필요 |
| ⑶ 좁히기 도우미 | `_sequence(value: object, field) -> list[object]` · `_require_sequence -> list[object] \| tuple[object, ...]` | 2 | 3 | 재구성(`TypeIs[list[object]]` 반환 면제형) — rv1-C §6-4 와 같은 처방 | △ |
| ⑷ JSON 값 변환 | `sanitize(value: object) -> object` · `_redact_phone` · `_freeze/_thaw/to_python` · `_json_object_to_raw -> object \| None` | 1 | ≈11 | 누수 — `JsonValue`(결정표 5행) 대체 | ✓ |
| ⑸ 누수 후보 | Protocol property `role/content -> object` · `run_source_boundary/_run_key -> tuple[object, ...]` · port `fetch_merge_journal -> object`(«opaque port」) · wiring `build_get_shared_reading -> object` · use case `_generate_core_report -> object \| None` | 4 | 6 | 누수 — 실제 클래스/튜플 타입(결정표 6행) | ✓ |

제안 물음(계획 §2.1 #647 델타 ⓓ 메시지): «반환의 `object`(또는 컬렉션 원소)가 입구 밖 자리표시인가 — 이벤트 컬렉션이면 이벤트 기저 타입(`list[<Bc>Event]`)을, JSON 값이면 `JsonValue` 를, 포트·와이어링·유스케이스·속성 반환이면 실제 클래스를 적을 수 있다. 예외는 둘 — 스텁이 `object`/`Any` 로 강제하는 프레임워크 콜백·오버라이드(`parse_constant`·`field_validator(mode="before")`·admin display)의 미러, 그리고 `TypeIs[...]` 로 바꿀 수 있는 좁히기 도우미(면제형으로 재구성).» — 결정표 6행 «입구 밖」 한정 문면에 ⑴⑵ 예외를 한 구절로 병기해야 kkebi 21/42 가 매 레인 «오탐 물음」 으로 남지 않는다(ⓔ2 로 legacy 는 접히지만 새 BC 의 `pull_events` 는 매번 새 ⓓ 다).

## 6. Δ 목록 (계획 v2 델타)

- **ΔC-1(§5 · MAJOR)**: 무손실 판정을 `$S/rv3C/lossless.sh` 판형으로 명세 — old/new 트리(`git archive main` vs 브랜치) · 4 사본(f5ee428 추가 — #649 1건의 B∖A 확인) × 3 검사기(registry argv) + 픽스처 = `fixture_matrix.build_cases()` 9 케이스 + `checker_cross_matrix.lanes()` 31 good 루트 × 3(«87루트」 삭제 · 열거 출처 명기) · 비교 = 레코드 다중집합 + `[ⓓ?#N]` 발화 라인(요약행 제외) · 허용 규칙 2(B∖A 신규 5 규칙 · A∖B ⓓ#645→#647 **슬롯 키**) · `diff -rq scripts-old scripts-new` 로 «나머지 24 검사기 byte 동일」 닫기 · 산출을 `workspace/eval/field-report-3/evidence/…`(또는 ⑤ 리뷰 입력)에 표로.
- **ΔC-2(§5 · MAJOR)**: 기대 계수를 **루트 필터 뒤** 값으로 교체 — #647 spring 차단 594·ⓓ 255(+반환 object 8 · #650 40) · kkebi 차단 161·ⓓ 253(+42 · 7) · #645→#647 1:1 spring 518·kkebi **52** · #646 18/31/21 무변 · #648 7/8/6 · #649 1 · 반환 object ⓓ 오라클을 «반환 주석 루트 `object` · `tuple/list/Sequence/Iterable/Iterator/set/frozenset` 원소 `object` · 유니온 구성원 포함(`\| None`) · `TypeIs/TypeGuard` 루트 제외 · dict/Mapping 값 자리는 #647 본체」 로 명세하고 kkebi 42 를 기대치로.
- **ΔC-3(§2.4·§7-3 · MAJOR)**: registry_gate ⓔ2 에 두 조건 추가 — ① «ⓓ 신규/legacy」 절과 sidecar 의 ⓓ 키는 **ⓓ 라인이 하나라도 있을 때만** 방출(없으면 출력·sidecar 현행과 byte 동일 → smoke P0′ 유지) 또는 P0′ 재기준선(`_PRE_REPAIR_COMMIT` 갱신) 중 택일을 명기 ② sidecar 의 ⓓ 신규 레코드는 `records`(재생성 루프 입력)가 아니라 별도 키(예 `candidate_new_lines`/`candidate_records`)에 — «귀속 0 ≠ ⓓ 0」 과 «ⓓ 는 exit 불산입」 이 sidecar 소비자에게도 성립하도록 · smoke ⓓ 케이스 1 은 «앵커에 있던 ⓓ = legacy(절에 계수만) · 새 파일의 ⓓ = 신규 라인 인쇄 · exit 무변(0)」 3 단언.
- **ΔC-4(§5 · MINOR)**: «registry_gate 귀속 0(HEAD=앵커)」 → «앵커=HEAD + 무해 변경(docs) · 또는 앵커=HEAD~1 docs-only 커밋 → exit 0 · 귀속 0 · ⓓ 신규 0(N′∖L′) · legacy ⓓ n 보고」 로 실행 가능한 문면.
- **ΔC-5(§2.1 #647 · MINOR)**: #647 메시지에 #645 와 같은 슬롯 라벨 어휘(`` `fn()` 매개변수 `x` `` · `` `fn()` 반환 타입 `` · `` `target` 주석 ``)를 실어 1:1 증명이 슬롯 단위로 대조되게 — 혼재 줄(spring 2)에서 노드 단위 배타가 맞게 동작했는지 이 키로만 보인다.
- **ΔC-6(§4-5 회신 3 · MINOR)**: 발주측 항목 8 문구 정정 — ② «`# type: ignore[type-arg]` 18줄(spring)·**21 발화**(kkebi · 22줄 중 `Query(None)` 1 은 규칙 밖)」 ④ «legacy = 검사기 기준 spring 594(+ⓓ 255)·kkebi 161(+253) — grep 1,098 은 참고 · `Form.clean -> dict[str, Any]` **18**(spring 15·kkebi 3)」 · «kkebi `web/` 111·`scripts/` 212 는 **루트 필터로 대상 밖**(격리가 아니라 제외 · dddjango-web 경계)」 ⑤ «루트 필터 부재 이월 고지」 **삭제**(모순) → 대신 «신규 3 규칙만 루트 필터 · #493/#645 기존 규칙은 무변(web/scripts 의 #645 ⓓ nested 는 그대로 남음 — kkebi 105 줄)」 고지 · «판단 기준 4 재분류표(rv1-C §5)」 를 회신 3 목차에 명시 · ⓓ 감수 부담 문장을 «ⓔ2 격리 뒤 legacy 0 · 새 BC 산출분만(kkebi 새 BC 의 `pull_events` 형상은 매번 ⓓ — §5 ⑴)」 으로.
- **ΔC-7(§7-2 · MINOR)**: ⓓ 물음 문안을 §5 제안대로 확정하고 결정표 6행(또는 b7 R-3448 rev2 말미)에 «프레임워크 콜백 미러·이벤트 컬렉션 기저 타입」 두 예외 구절 병기 · 리스크 2 의 수치를 «spring 8·kkebi 42(이벤트 16·콜백 5·도우미 3·JSON ≈11·누수 ≈6)」 로.
- **ΔC-8(§3·§1.2 · MINOR)**: 픽스처·정본 예시 mypy 검증 레시피 명기 — «cwd=픽스처 good 루트 · `PYTHONPATH=MYPYPATH=<spring 사본>` · `--config-file <spring>/pyproject.toml --follow-imports=silent application`(spring venv mypy 2.3.1·django-stubs 6.1.0)」 · 대상 = **신설 파일만**(기존 good `order_form.py` 는 strict 22 errors — 관례상 픽스처는 mypy 밖 · 무변 원칙과 충돌하지 않게 «신설 파일 0 errors」 로 한정) · 정본 예시(§1.2 b2)는 같은 레시피로 `mp_probe`-류 임시 디렉터리에서 1회.
- **ΔC-9(§5 · MINOR)**: 픽스처 무손실 항목에 «cross 31 good 루트 × 3 검사기 B∖A = 0(신설 good 파일이 다른 검사기에 걸리지 않음)」 과 «`findings_count_matrix` public_surface good 의 info 열 +1(ⓓ#647 `order_form.py:21`)」 을 기대치로 적어 regen 이 «소실」 이 아니라 «의도」 임을 남긴다.

## 7. 사각 · 미확인

1. 무손실 판형은 구현 전이라 «차분 0」 만 봤다 — 허용 규칙 분기(B∖A 신규·ⓓ#645 1:1)는 코드 경로만 있고 데이터로 검증되지 않았다(구현 뒤 ④ 에서 첫 실데이터).
2. ⓔ2 실측은 게이트 산식을 ⓓ 라인에 **모사**(`_normalize` 동형 sed)한 것이지 `registry_gate.py` 를 고쳐 돌린 것이 아니다 — 27종 전체 앵커 실행(≈70s×2)은 하지 않았다(rv1-C run1~4 가 게이트 본체 판형).
3. 반환 object ⓓ 오라클은 내 정의(§6 ΔC-2)다 — rv1-B «34」 의 정의를 찾지 못해 8 건 차이의 출처(`\| None` 6 · `Sequence` 1 · 기타)를 대응시키지 못했다.
4. 브라운필드 «ⓓ 상한」 은 손댄 파일의 ⓓ 줄 합(상한)이고 커밋 diff 가 그 def 줄을 실제로 바꿨는지는 보지 않았다 — 줄 밀림 0·개명 1 실증으로 방향만 닫았다.
5. 픽스처 mypy 레시피는 spring settings 를 쓴다(픽스처 `django_orders` 앱은 INSTALLED_APPS 밖) — 19 files 검사·모델 관련 오류 0 이었으나 django 플러그인이 미등록 앱 모델을 어떻게 다루는지(`[misc]` 무발화 이유)는 확인하지 않았다.
6. `$S/spring` 에 타 세션의 untracked `mp_probe_18/`·`mp_probe_s1/` 이 남아 있어 실검사기 레코드가 run1 4,117 → run2 4,132 로 움직였다(제외 뒤 4,097 불변) — 판형은 `mp_probe_` 접두 제외로 막았으나 ④ 실행 전 사본 정리를 권고.
7. kkebi `web/` 이 dddjango-web 산출이라는 것은 S1 진술 의존(커밋 표식 미확인) — 루트 필터 근거 자체는 «표준 트리 값」 이라 이 사실에 좌우되지 않는다.
