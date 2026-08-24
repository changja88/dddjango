# 검사기 측정 결함 수리 계획 — v2.17.4 (v2)

- 작성: 2026-08-25 · 상태: **v2 — 2차 적대 패널 3인 처분 반영(대장 §7)**. v1 대비 재설계:
  **W1a 적용 술어 3요소**(SajuChart 오탐 차단) · **W2 escape 술어**(reconcile/import 분리의 유일
  정적 구별자) · **W6 파생 튜플 집합+그래프 리비전 편입** · **W7 stderr 경고 방식**(Coordinator 교착
  회피) · W8 부칙 5건(+#417·#33) · 인수 허용 diff ⓕ 신설.
- 준거: `workspace/design/2026-08-25-checker-measurement-defects-analysis.md` **v2.1**(§7 정오 우선).
- 목표: kkebi billing **R1 전제 해소**(15건 미귀속 + reconcile 1건 반송 — G2 자체는 kkebi 측
  R2~R4+registry green까지 별도)·saju HOLD 해제 전제 충족(#545×2 소멸+3개조 이행 증빙)·
  tarot 후속 ㉮㉯ 동반 — 릴리즈 **dddjango v2.17.4**.

## 1. 작업 분해 (W1~W9)

### W1 `check-port-adapter-pairing.py` — #545·#365·#555

**W1a #545 (:461-471 창 교체)**:
1. **적용 술어(2원 합집합)** — 다음 중 하나일 때만 #545 검사, 아니면 비적용:
   ⓐ `domain_layer/<agg>/event/`에 비-`__init__` `.py` 실재
   ⓑ 루트 `<agg>.py`에 **pending 3요소 전건**: 사적(밑줄) list 필드 + 같은 필드의 tuple 사본/불리언
   조회 표면 + **같은 필드를 실제로 비우는 소거/소모 창구**(`clear()`·빈 재대입·pop-all 반환 — 이름
   불문·행위 판별). 소거 창구 요건이 SajuChart(`_snapshots` — append만·소거 0) 오탐을 차단한다
   [설계 W1a-1]. 반쪽 채택(event/만 실재·루트 3요소 미충족)은 후보(ⓓ) 발화. join-miss는 비적용
   (#351 orphan red 별도 잔존 — 픽스처 고정).
2. **의미 가드 창** — 인정 = 전건 충족:
   ① 질의 수신자 = save의 애그리거트 매개변수(+동일 함수 내 `alias = param` 단순 Name 대입 별칭 집합)
   ② **질의 대상 조인**: 질의된 속성이 적용 술어 ⓑ의 pending 필드이거나, 루트에 실재하고 body가
   그 pending 필드를 참조하는 property(단일 Return의 `store`/`bool(store)`/`len(store)` 협창)
   [성문 B2·설계 W1a-3 — 무관 질의 `is_archived` 디코이 차단]
   ③ **극성**: 질의가 truthy 경로에서 raise에 도달 — 판별은 **부정형 블랙리스트**(`not`·`== 0`·
   `is None`·«빈-경우-raise» `or` 합성·상수-False 분기 하위면 불인정)로 하고, 블랙리스트에 안 걸리는
   pending-질의-포함 test는 truthy 인정(`len(x) > 0`·`!= 0`·`bool(x)` 변형 green — 화이트리스트
   방식의 회귀 차단) [설계 W1a-2]
   ④ raise가 같은 함수의 handler에 삼켜지지 않음 — 판별은 «가드 raise를 포함하는 Try의 handler 타입이
   그 raise 타입(또는 광역)을 잡는 경우 불인정»(무관 타입 handler의 정당 try는 통과) [설계 W1a-6]
   ⑤ 가드 문장이 save body의 첫 ORM 접촉 이전 — ORM 접촉은 **`objects` 체인 하위의**
   `.filter/.create/.update/.delete/.save/...`와 `Model.objects` 정적 판별로 한정(`payload.update()`
   같은 무관 `.update` 오탐 차단) [설계 W1a-4]
   raise **타입**은 판별에 쓰지 않는다(원인 v2 E1② «보조»는 채택 안 함 — 08-15 인정 형태의 builtin
   raise 실물과 충돌 위험·②조인+③극성이 이중 방어. 편차 명시) [성문 m6].
3. 거짓 양성 3형(죽은 분기·지역 이름·무관 수신자)은 창 교체로 배제 — 각각 양성 픽스처.
   `getattr(...,None)` seam·반쪽 채택 형상도 픽스처 등재 [성문 m3].

**W1b #365 (:545-552 보강)** — ⓒ 구조 순수성 술어: 대상이 스냅숏 BC에 없을 때, `acl/<대상>/` 전
모듈의 import가 «자기 BC `application.<bc>.*`·`framework.*`·비통신 stdlib»뿐이면 후보(ⓓ) 강등,
통신 축 import 실재 시 #365 blocker 유지. 통신 축 상수 = `urllib`·`http.client`·`socket`·`ssl`·
`subprocess`·**`importlib`·`asyncio`·`ftplib`·`xmlrpc`** + SOCKET_LIBS·벤더 top-level, 그리고
`__import__` Name 호출 검출 [설계 W1b-1 — 동적 import 누출 차단].

**W1c #555 (:618-627 보강)** — bare `raise` 허용 4중 조건: handler 이름이 ① 같은 BC
`port/**/exception.py` **또는 `domain_layer/<agg>/exception/<snake>.py` 폴더형** [설계 W1c-1]에서의
ImportFrom 바인딩 ② 그 모듈의 ClassDef(Assign 별칭 불인정) ③ 현 모듈 내 재바인딩 부재 ④ 튜플은
전 원소 충족. **판별 순서: 광역 이름 블랙리스트(`Exception`·`BaseException` 등)가 출처 해석보다
우선**(shadow ClassDef 세탁 차단) [설계 W1c-2]. builtin 상속 여부는 쓰지 않는다.

### W2 `check-transaction-boundary.py` — #197 (escape 술어 재설계)

[인수 F1·설계 W2-1 — v1 처방은 실물에서 ⓐⓑ 동시 만족 불능: import 파일에 쓰기 0·`_run_batch`는
참조 전달이라 호출 추적 불가. 유일한 정적 구별자 = **repository의 콜러블 인자 탈출**]

1. **With 인식**: context_expr가 `ast.Call`이면 `func`를 언랩해 기존 Name/Attribute 판별에 위임.
2. **도달 범위**: 공개 메서드에서 ⓐ self 메서드 직접 호출 1단 ⓑ self 메서드가 **호출 인자로 참조
   전달**(`f(cb=self._helper)`)된 경우 그 메서드 — 두 경로의 합집합. 어느 쪽으로도 안 닿는 죽은
   helper는 불산입.
3. **uses_uow_api 확장**: 도달 범위 안에서 ⓐ 기존 쓰기(`save/remove`·`after_commit`) ⓑ **escape** —
   `uow.repository`(또는 uow-별칭 `.repository`)가 **호출 인자로 전달**되는 형태(`work(unit_of_work.repository)`).
   escape는 «외부 콜러블이 쓰기를 수행할 수 있다»의 fail-open 인정임을 주석·계획에 명기.
   `_is_repo_recv` 수신자 확장(`uow.repository.save(...)` 형)도 함께 [설계 W2-1 부기].
4. 판정 귀결(kkebi 실물 시뮬레이션): import = has_uow·escape 실재 → green / reconcile = has_uow·
   `.get` 로컬 읽기만·escape 0 → **red 잔존(의도)**. 픽스처로 양쪽 + 죽은 helper + `list_order`형 고정.
5. 명기: 기지 사각(UoW 애너테이션 소거 시 has_uow 불가시 — kkebi의 실쓰기 유스케이스들이 현재 이
   사각 뒤에 있어 «그 외 diff 0»이 우연 성립 [설계 W2-2])은 이번 범위 밖·후속 별건 등재.

### W3 `check-domain-model.py` — #543 저널 carve-out

(:315-373) `has_events_attr ∧ ¬has_pull` red 전에 **저널 관용구 전건** 검사(전건 충족 시 발화 해제):
① 사적 pending 저장소 필드 실재 ② 그 저장소의 tuple 사본 반환 property ③ **같은 저장소를 실제로
비우는 메서드 실재**(이름 불문 — body의 `clear()`/빈 재대입 행위 판별 [설계 W3-1]) ④ 실체 저장소
(`events` 류)와 pending 저장소가 서로 다른 두 필드. 미충족은 현행 red. `events` property 금지·일반
pull 규칙 불변. **집행 비추가**: 공개 가변 `events` 필드 요구는 부칙 관찰 조항만(신규 발화 금지 —
인수 diff 0 원칙). 일반 애그리거트가 저널 관용구를 기계 채택해 pull_events를 회피하는 창이 그
귀결로 열림 — 부칙에 «저널 아닌 애그리거트의 채택은 위반(관찰)»을 서술해 후속 집행 근거를 남긴다
[설계 W3-2]. 음성 픽스처에 kkebi R4-이후 형상(pull_events 채택)도 고정.

### W4 `check-naming.py` — #33

(:214-218) 면제 = `py.parent.name == "models" ∧ py.parent.parent.name.startswith("django_") ∧
stem.endswith("_model")` [설계 W4-1 — parent 기반·BC-상대 경로 대응]. 그 외 현행 유지.

### W5 `check-business-vocabulary.py` — #562

`_check_pure` 국소 상수 `_PURE_TECH_STOPWORDS = {"keys"}` 차감. 전역 STOPWORDS·타 검사 무영향
(패널 실측: 교집합 `['keys']` 단독·`union` 사용처 2곳 중 pure 국소만 변경). 등재 절차 주석 포함.

### W6 error 계열 3종 — ㉮ canonical 경로 (그래프 리비전 동반)

1. **정본 집합의 파생 튜플 구조** [설계 W6-1]: 원소 = `{dir, init(dir/__init__.py), path, module,
   module_basename}` 파생 가능 구조로 —
   `(framework/ninja, framework_error_schema)` · `(framework/django_ninja, error_schema)`.
   `COMMON_INIT` 구조 요구(:4518-4520)·`:5398` basename 등호·dotted containment 조각까지 전 표면을
   집합 경유로 개조. 클래스명 축(`FrameworkErrorSchema`)은 불변(kkebi 실물 동일 확인).
2. **좌표 대장 선행**: 실측 표면 ≥37(EC ≥20 — `:2680` 문자열 리터럴 포함 · api ≥12 · openapi 5 —
   `:2132` dict 인덱스·`:2139` 룩업)을 **구현 전 전수 대장으로 작성 완료**가 착수 조건 [설계 W6-2].
3. **이중 실재 red**: 두 정본 경로 파일이 모두 실재하면(placeholder 여부 불문 — 정본은 하나
   [설계 W6-3]) **규칙 번호 없는 사용-오류 채널**(DYNAMIC_… 판례의 사용 오류 exit 1)로 발화
   [인수 F10 — registry 파싱 무영향].
4. **규범 리비전 동반** [성문 B1]: ⓐ 그래프 — implementation-django-ninja final.md:550 절(§6.2
   graph-owned)을 소유한 rule의 Expression 리비전(«공통 오류 모듈 정본 경로에 승인 대체 경로
   `framework/django_ninja/error_schema.py` 가산·정본 이중화 금지» — amendment) → `ontology_render.py
   --apply` 재투영 → corpus mirror → `make rulepack` → 계수(ExpressionShape +1) → LEDGER 해당분 —
   R-1699 판형(규범 리비전 4호·구현 시 해당 rule id 특정) ⓑ 스펙 대장 #417 부칙.
5. 제약 재서술: «픽스처·정본 경로 저장소 무영향 + tarot 정적 런의 신규 red는 의도된 회복»(통지 포함).
   ⓒ 인수는 **검사기별 후행표**(전/후 실측 — 무엇이 사라지고 무엇이 남아 exit 몇인지, EC의
   DYNAMIC 잔존 여부 포함)로 판정 [인수 F6].

### W7 `check-error-centralization.py` — ㉯ auto 침묵 (재설계: stderr 경고)

[설계 W7-1 — Coordinator(`dddjango.md:75·:111·:175`)가 auto 렌더를 의무화·auto에 selector 전달
금지라 exit 1은 파이프라인 교착. 인수 F2 — 기존 auto 픽스처 레인 3중 하네스와도 충돌]

재설계: **auto·None 프로파일 공통** [인수 F8·설계 W7-2], «비-placeholder 대상 실재
(`_skeleton_placeholder_module` 재사용 — #114 정합) ∧ 검사 인벤토리 해석 결과 0»일 때 —
exit·stdout·finding 레코드 **불변**, **stderr에 경고 1행**(«[auto] 비-placeholder 오류 스키마 실재·
인벤토리 해석 0 — selector 지정 필요» 취지). 침묵만 제거하는 최소 개입 — 원 의도(fail-loud)보다
약함은 교착 회피의 의도된 트레이드오프(원인 v2.1 §7-6). 하네스·Coordinator 무파급. W6 이후
kkebi에서는 auto가 실제 해석에 성공하므로 경고는 잔여 사각(제3 경로 프로젝트)에만 뜬다.

### W8 성문 리비전 — 스펙 대장 부칙 5건 + 그래프 1건

부칙 형식: `<span>2026-08-25 · **라벨** — …</span>` (08-15 판례) [성문 m4]. 대장 개정 이력 절·LEDGER
연동은 없음을 확인(span 부칙이 유일 관례 — 확인 사실 기록) [성문 m2].
- **#545 «적용 술어와 가드 의미»**: 적용은 이벤트 채택 애그리거트(event/ 비-init 실재 ∨ 루트 pending
  3요소)의 리포지토리에 한함 — eventless는 비적용(가드 강제는 dead seam). 반쪽 채택은 후보. 인정
  가드는 수신자의 pending 상태를 **비소모로** 질의해 **잔존(truthy) 시 persistence 전에** 예외에
  도달하는 형태 — 이름 토큰 존재(죽은 분기·지역 이름·무관 수신자·빈-경우-예외)는 가드가 아니다
  [성문 M2·M3].
- **#543 «저널 애그리거트»**: 실체·큐 분리 이중 구조에서 pending 조회 property + 실소거 창구의
  4전건 인정(+repo 가드 조인은 #545 소관). 실체 저장소의 공개 표면은 불변이어야 한다(관찰 조항 —
  집행 후속). **저널이 아닌 애그리거트의 이 관용구 채택은 위반이다(관찰)**. `_pending_events` 명명
  단독 채택이 현행 창 밖인 것은 기존 사각이며 이번 인정이 아니다 [성문 M4·설계 W3-2].
- **#365 «병렬 워크트리»**: «우리 BC»는 병렬 워크트리 개발로 스냅숏에 없는 자사 BC를 포함 — 대상
  부재 시 구조 순수성(통신 축 import 0)이면 후보 강등, 아니면 위반 유지.
- **#33 «#335 자리 면제»**: #335가 소유하는 `models/<entity>_model.py` 자리의 첫 토큰은 #33의 대상이
  아니다 [성문 M6].
- **#417 «승인 대체 경로»**: 공통 오류 모듈 정본 경로 집합에 `framework/django_ninja/error_schema.py`
  가산·이중 실재 금지 — 그래프 리비전(W6-4ⓐ)과 같은 커밋(#72 «한 커밋» 준수).

### W9 픽스처·하네스·미러·봉인

- **레인 신설**(후보(info) 형상은 good이 아니라 **bad_rules에 진성 red와 병존** — 하네스 green 축이
  «레코드 0»이라 [인수 F7]):
  `port_adapter_pairing_event_guard` — good: 08-15 인정형·has_pending_events 가드·truthy 변형 3형
  (`len>0`·`!=0`·`bool`)·eventless 무가드·SajuChart형(소거 창구 부재 — 비적용) / bad_rules: decoy
  ⓐ(무관 질의·항상-False property)ⓑ(raise 삼킴)ⓒ(쓰기 후 가드)·극성 반례(event_stream형)·거짓 양성
  3형·getattr seam·반쪽 채택(후보 — 진성 red 병존).
  `port_adapter_pairing_acl_snapshot` — bad_rules: 통신 import 위장 ACL red + 순수 스텁(후보 병존)·
  동적 import(`importlib`) red.
  `port_adapter_pairing_rethrow` — good: 선언 오류 재던짐(파일형·폴더형) / bad_rules: 별칭 세탁 4형·광역.
  `transaction_boundary_factory_uow` — good: factory-call with+repository escape / bad_rules: 읽기
  전용+UoW(reconcile형)·죽은 helper.
  `domain_model_journal` — good: 저널 4전건·R4-이후 형상 / bad_rules: no-op mark·일반 애그리거트
  property 창구.
  `naming_model_suffix` · `business_vocab_pure_stoplist` · `error_centralization_canonical_alt`
  (selector argv — django_ninja 경로 / bad: 이중 실재 사용 오류).
- **기존 파급 사전 열거** [인수 F11·설계 W1a-7]: `port_adapter_pairing/bad_rules`의 #545×2
  (order_repository — eventless·billing_repository — join-miss)가 새 술어로 소멸 → default 레인
  EXPECTED·findings 계수·해시 3종 갱신(사유 명기). `findings_smoke.py`의 check-domain-model stdout
  SHA·계수(48/13)는 W3이 기존 `domain_model/bad_rules` 출력을 바꾸는 경우에만 골든 재기록(사유 명기).
  W7은 stderr 방식이라 error 계열 기존 레인 무파급.
- EXPECTED 스키마(패널 실측): baseline 5튜플 `(exit, parsed_raw, normalized_unique, unparsed,
  synthetic)` · findings 7튜플 `(exit, violation, info, dist, ids_sha16, canon_sha16, multiset_sha16)`.
- codex **byte 미러**(수정 검사기 전부 + findings.py 등 공용 모듈 변경분 — 미러 쌍 자체가 봉인 대조
  항목)·그래프 리비전분은 corpus mirror 채널 · `manifest_seal.py --write` 재발행(검사기·findings.py·
  registry_gate.py·findings_count_matrix 전부 봉인 안 — 패널 확인) · `make verify` green ·
  `make rulepack`(W6-4ⓐ 동반).

## 2. kkebi 실물 인수 런북 (릴리즈 전 필수)

1. **동결**: 3워크트리를 rsync 사본화(`.dddjango`·`__pycache__`·**`.git` 제외** — 양측 동일 비-git
   결정 모드·git-affected 검사기 7종도 전/후 동일 조건 [인수 F5]) + sha256 manifest.
2. **전/후 매트릭스**: 27종 × 3사본 — 전 검사기 positional 직접 실행(**무anchor 전량 렌더** — anchor
   분류는 발화 집합에 무관·git 의존 제거) + error 3종은 kkebi 기록의 explicit selector 판형(무anchor).
   수집 = `DJR_FINDINGS_JSON` 레코드 + stdout + **stderr** + exit.
3. **판정 — 허용 diff 전수**:
   ⓐ billing 15건 + saju 2건 소멸(17) ⓑ 잔존: `#545` event_stream·`#197` reconcile red
   ⓒ ㉮ 후행표: 검사기별 전/후 실측 표 작성(EC의 DYNAMIC 잔존 여부 포함) — 신규 red는 전수 목록화
   ⓓ ㉯ stderr 경고 라인 출현(해당 조건 사본에서) ⓔ **ⓕ 후보 전환**: #365 ⓓ 3건 신규·tarot #545
   2건 소멸·반쪽 채택 해당분 ⓖ 그 외 발화·exit·stdout diff 0. 위반 시 원인 규명 회귀.
4. 결과를 릴리즈 커밋·통지문에 첨부.

## 3. kkebi 통지문 요지 (사용자 경유)

① v2.17.4로 R1 16건 중 **15건 미귀속** 이행 ② **reconcile #197 반송** — 성문 :526 문면·실물 51행
쓰기 0(«misses ×2» 표의 절반은 오귀속). **R1-A 문면(«16 no longer attributed»·«product write 0»)과
충돌하므로 kkebi 측 사용자의 R1-A 재결정(16→15 재배치 + 해당 제품 write 허용)이 재개 전제** [성문 M1]
③ #429는 ≥2.17.1 기수리 ④ ㉮로 error 정적 게이트 활성화 — tarot 등 신규 red는 의도된 회복(후행표
첨부) ⑤ saju에는 Z-35D 3개조 ↔ 이행 좌표 대응표(적용 술어=W1a-1·의미 증명=W1a-2·거짓 양성
형태=W1a-3+픽스처) 별도 제시 [성문 m5] ⑥ 재실행 동일 앵커·동일 명령.

## 4. 실행 순서·완료 게이트

1. W6-2 좌표 대장 작성 → W1~W7 구현(TDD — 픽스처 red/green 먼저) → W9 하네스·미러 → verify green
2. W8 부칙 5건 + 그래프 리비전 사슬(재투영·rulepack·계수·LEDGER 해당분) — 검사기와 같은 커밋
3. §2 인수 런북 완주(ⓐ~ⓖ)
4. 대조 리뷰 1인(계획 ↔ 구현 diff — 편차 0)
5. 조감도·메모리 갱신 → 커밋(검사기+픽스처+대장+그래프 / 봉인 분리) → 사용자 `make release`(v2.17.4)
   → 양 런타임 설치본 갱신 → kkebi 통지·재실행

## 5. 비범위 (명시)

공개 가변 `events` 집행(관찰 조항—후속) · #197 애너테이션 사각(kkebi 실쓰기 유스케이스들이 이 사각
뒤에 있음을 명기 [설계 W2-2] — 후속 별건) · W2 escape의 fail-open 폭 · E10 비정본 이탈 채널 ·
전역 STOPWORDS · 7규칙 그래프 이관 · #462 성문 채번·유령 대사.

## 6. (v1 이력) 1차 설계 — §1이 대체. 생략.

## 7. 2차 패널 처분 대장 (3인 — blocker 7·major 13·minor 15 · 채택 33·부분 2·기각 0)

**성문·통지 렌즈**: B1 채택(W6-4 그래프 리비전 편입) · B2 채택(W1a-2② 조인) · M1 채택(§3②) ·
M2·M3·M4 채택(W8 부칙 문면) · M5 채택(§2-3ⓕ) · M6 채택(W8 #33) · m1 채택(원인 §7-1) · m2 채택
(W8 확인 기록·W6-2 선행 승격) · m3 채택(W9 픽스처) · m4 채택(부칙 라벨) · m5 채택(§3⑤) ·
m6 **부분**(raise 타입 판별 비채택 — 편차 사유 명기로 갈음) · m7 채택(ⓓ 관측 채널 명시).

**인수·절차 렌즈**: F1 채택(W2 escape 재설계) · F2 채택(W7 재설계 — 하네스 무파급) · F3 채택
(원인 §7-1) · F4 채택(ⓕ) · F5 채택(.git 제외·무anchor) · F6 채택(ⓒ 후행표) · F7 채택(후보 bad_rules
병존) · F8 채택(None 포함) · F9 채택(원인 §7-4) · F10 채택(사용-오류 채널) · F11 채택(W9 사전 열거) ·
F12 **부분**(트리 실측은 클린+정본 문서 2건 — 커밋 조율은 §4-5에 기존재).

**설계 렌즈**: W1a-1 채택(3요소) · W1a-2 채택(부정형 블랙리스트+변형 픽스처) · W1a-3 채택(조인) ·
W1a-4 채택(objects 체인 한정) · W1a-5 채택(ⓕ tarot 2건) · W1a-6 채택(handler 타입 대조) · W1a-7
채택(W9 열거) · W1b-1 채택(통신 축 확장) · W1c-1·2 채택 · W2-1 채택(escape) · W2-2 채택(§5 명기) ·
W2-3 기록 · W3-1 채택(행위 판별) · W3-2 채택(부칙 관찰 서술) · W4-1 채택(parent 판형) · W6-1 채택
(파생 튜플) · W6-2 채택(좌표 대장 선행) · W6-3 채택(불문 red) · W7-1 채택(stderr 재설계) · W7-2
채택(None) · W7-3 해소(재설계로 무파급).
