# 검사기 측정 결함 원인 규명 — billing R1 16건 + saju #545×2 + tarot 후속 2건 (v2.1)

- 작성: 2026-08-25 · 상태: **v2.1 — 1차 패널 처분(§6) + 계획 v1에 대한 2차 패널이 소급 적발한
  본 문서 정오(§7)**. 본문은 v2 그대로 두고 §7이 우선한다. v1 대비 판정 변경:
  **E3 분할(A+B — reconcile 1건은 정당 판정 → kkebi 반송)** · E1 «A+C»(성문 리비전 동반) ·
  E4 실제 트리거 정정(`events` 공개 가변 필드)+성문 충돌 확정 · E5 «성문 미정의»로 격하 ·
  성문 착지 정정(7규칙 전부 그래프 밖 — 정본은 스펙 규칙 대장).
- 발단: kkebi billing 런 `tree-contract-mismatch.md`(G2 EXECUTION_BLOCKED — R1 선행 릴리즈 16건)와
  saju 런 design-spec `Z-35D`(#545×2 플러그인 결함 판정 — registry/G2/commit HOLD). 결정 `pending 0` 동결.
- 인수 계약(kkebi 문면): 「further plugin-owner release in which these 16 are **no longer attributed**,
  followed by the **same anchor** registry rerun」 — 재실행은 현행 제품 코드 기준.
  **v2 정정: 이행 가능한 정직한 목표는 15건 미귀속 + 1건(reconcile #197) 반송이다(§2 E3).**
- 사용자 결정(2026-08-25): ① #543 **검사기 수용**(→ v2: 성문 #543 리비전 동반이 기계적 귀결 — §2 E4)
  ② tarot 후속 ㉮·㉯ **둘 다 이번 릴리즈 편승**.

## 0. 검증 방법론 — 문서 신뢰가 아니라 실물 재현

kkebi 판정문을 그대로 수용하지 않고(판례: tarot 요약본 오진) 3단 실측 후 3인 적대 패널로 반증시켰다.

1. **레코드 원본**: billing `.dddjango/20260823-1637-billing-migration/introduced.json`
   (schema `gate-introduced/0` · records 154 · unmatched 0)에서 대상 17건 file/message 추출.
2. **재현**: 본 저장소 HEAD 검사기(`dddjango/scripts/` — `dddjango--v2.17.3` 태그와 diff 0 byte 동일)를
   kkebi 라이브 워크트리에 직접 실행 — billing 17건 + saju #545×2 = **19/19 문면·좌표 일치 재현**
   (로그 `~/.claude/jobs/48c8a476/tmp/billing-*.out`·`saju-port.out`). 레코드 대차:
   R1 16 = E1(6)+E2(1)+E3(2)+E4(1)+E5(3)+E6(1)+E7(1)+E8(1) · #545 총 10 중 1건 B — 패널 검산 일치.
3. **대조**: 각 판정의 검사기 구현과 kkebi 실물을 정독해 «측정 결함(A) / 정당 판정(B) / 성문 관여(C)» 판정.
   반증 방향은 kkebi와 반대(«검사기가 맞고 코드가 틀렸다» 입증 시도).

접근 경로: kkebi Desktop 원본은 본 세션 환경에서 TCC 차단. 라이브 워킹트리
`~/.herdr/worktrees/kkebi-server/feat-{billing,saju,tarot}-bc`는 파일 읽기 가능. git 명령 가부는
**샌드박스 프로파일 의존**(본 세션 실패·패널 세션 성공 — 패널이 HEAD `2147d55` = introduced.json
anchor 일치를 확인, «동일 앵커·현행 코드» 정합의 추가 증거). 커밋 객체는 `~/kkebi-mirror`로도 조회 가능.

**성문 정본 착지(패널 R1-F8)**: 대상 7규칙(#545·#197·#543·#365·#555·#33·#562)은 **전부 온톨로지
그래프 밖**이다(`ontology/wiring/aliases.ttl` rule# 조인 21종에 부재·rulepack 문면 0건). 성문 정본은
**스펙 규칙 대장 `workspace/design/2026-08-08-tree-revision-spec.md`**(:365 #33 · :526 #197 · :648 #335 ·
:677 #365 · :866-867 #543/#545 · :877 #555 · :884 #562)다. 이하 «성문 리비전»은 그래프가 아니라
**스펙 대장 개정**을 뜻한다(그래프 이관은 장기 별건 «유령 규칙 대사»의 소관 — 이번 릴리즈에서 안 한다).

## 1. 판정표 총괄 (v2)

| 묶음 | 레코드 | 판정 | 수리 소유 |
|---|---|---|---|
| E1 `#545` 적용 술어 | saju×2 + billing×6 | **A+C** — 측정 결함·성문 문면 리비전 동반 | check-port-adapter-pairing + 스펙 대장 |
| E2 `#545` 가드 인식 창 | billing×1 (payment_order) | **A** 측정 결함 | check-port-adapter-pairing |
| — `#545` 정당 1건 | billing_event_stream_repository | **B** — kkebi R4 소유(그들 스스로 분류) | 제품 |
| E3a `#197` import 건 | billing×1 | **A** — factory **호출형** `with` 미인식 | check-transaction-boundary |
| E3b `#197` reconcile 건 | billing×1 | **B — 정당 판정·kkebi 반송**(§2 E3) | 제품 |
| E4 `#543` 저널 관용구 | billing×1 | **A′+C** — 사용자 결정(검사기 수용)+성문 리비전 필수 | check-domain-model + 스펙 대장 |
| E5 `#365` 스냅숏 BC 오분류 | billing×3 | **성문 미정의+A** — ⓒ 구조 순수성 술어 | check-port-adapter-pairing (+스펙 대장) |
| E6 `#555` 재던짐 타입 무시 | billing×1 | **A** 측정 결함(성문 리비전 불요) | check-port-adapter-pairing |
| E7 `#33` 복합 명사 오독 | billing×1 | **A** — #335와 규칙 간 충돌로 강화 | check-naming |
| E8 `#562` 범용 용어 충돌 | billing×1 | **A**(stoplist 경로 한정 — 전체 일치안은 성문 해체) | check-business-vocabulary |
| E9 `final.md #429` celery 문면 | (성문) | **기해소 — 작업 0**(R-3217·v2.17.1) | 통지만 |
| E10 ㉮ canonical framework 경로 | (tarot 후속) | 편승 확정 — 결합점 18곳·«tarot 신규 red는 의도된 회복» | error 계열 3종 |
| E11 ㉯ `--error-profile auto` 침묵 | (tarot 후속) | 편승 확정 — placeholder 술어(#114 정합) | check-error-centralization |

## 2. 항목별 근거 (v2 — 패널 처분 반영)

### E1·E2 — `#545` «안 꺼낸 사실» 가드 (10건 중 8건 A+C·1건 A·1건 B)

**검사기 실물** `check-port-adapter-pairing.py:461-471`: repository `save` AST 전체에서
`Attribute.attr ∈ {"_events","pull_events"}` ∨ `Name.id == "pull_events"` 노드가 하나라도 있으면 통과.
애그리거트 이벤트 채택 여부는 확인하지 않는다.

**실물 증거**:
- 적용 술어 부재(8건 A+C): saju `SajuChart`·billing 6개 애그리거트 — 이벤트 상태/API grep **전수 0**.
  eventless root의 save에 가드를 요구하면 충족 방법이 decoy 토큰 삽입뿐.
  **성문 대조(R1-F3)**: 스펙 대장 #545(:867) 검사 문장 「검사는 「그 가드가 구현 안에 있나」다」는
  무조건 적용을 문면으로 지지 — 따라서 eventless 비적용은 **성문 문면 변경 = 스펙 대장 리비전 동반 확정**
  (의도 근거인 D59 세 걸음·08-15 부칙은 `_events` 실재 전제라 리비전은 의도의 명문화다).
- 가드 인식 창(1건 A): `payment_order_repository.py:73-75`
  `if payment_order.has_pending_events: raise UnpulledPaymentOrderEvents` — D59 의도를 정확히 구현한
  의미 가드 실재(애그리거트 :126 property·:135 `pull_events` 소모 창구 실재). 토큰 창이 못 본다.
- 정당(1건 B): `billing_event_stream_repository.py:74` — save가 pending을 **내부 소비**. kkebi R4 소유.

**kkebi 주장 반증 1건 유지**: saju Z-35D의 «comment/string도 guard 인정»은 틀렸다(주석은 AST 부재·
문자열은 `ast.Constant` — 패널 AST 실험으로 재확인). «죽은 분기·지역 이름(`pull_events = 1`)·
무관 수신자(`self.cache._events`)»는 실제 통과 — 수정 시 3형 각각 **양성 픽스처로 고정**(R3-F9).

**수정 방향(확정 경계 — R3-F1·F4·F5)**:
1. **적용 술어(2원 합집합)**: 「`domain_layer/<agg>/event/`에 비-`__init__` 파일 실재」 **OR**
   「루트 파일에 pending 상태/API 실재」일 때만 #545 적용. kkebi 실측에서 채택/무채택과 정확히 일치
   (payment_order: event/payment_confirmed.py 실재 · 무채택 7종: `__init__`뿐). 흔적을 둘 다 숨기려면
   이벤트 클래스를 비표준 자리에 둬야 해 비용 급등. join-miss(대응 domain 폴더 부재)는 #545 비적용이되
   #351 orphan red 잔존을 픽스처로 고정. 반쪽 채택(event/만 있고 루트 API 없음)은 별도 후보 발화.
2. **의미 가드 창(극성 필수 — R3-F1 blocker)**: 인정 = save **매개변수 수신자**(+동일 함수 내 별칭
   대입 집합)에 대한 pending 질의가 **truthy 경로**에서 raise에 도달하는 형태만.
   `not`/`== 0`/`is None`/`or` 합성으로 «빈-경우-raise»가 되는 형태·판별 불능 형태는 불인정(fail-closed) —
   이 극성 조건이 없으면 정당 판정 B(`if … or not stream.pending_events: raise ValueError`)가 함께
   소멸해 §4 인수 기준을 검사기 스스로 깬다. 보조: raise 타입 판별은 builtin 비상속 기준이 아니라
   **BC 예외 여부**로(§ E6과 동일 원칙 — kkebi 포트 오류가 `ValueError` 서브클래스인 실물 반례).
3. **디코이 차단(R3-F5)**: ⓐ 항상-False pending property → 질의 property가 애그리거트 루트에 실재하고
   body가 pending 저장소를 참조하는 협창(단일 Return의 `bool(store)`/`len(store)`/`store` — R-3401 판형)
   ⓑ raise를 같은 함수 handler로 삼키는 형태 불인정 ⓒ 가드 문장이 save body의 첫 ORM 접촉
   (`objects.*`·`.save`·`.create`·`.update`) 이전이어야 인정. 정적 한계(저장소-참조-항상-False 복합식)는
   픽스처에 한계로 명기.

### E3 — `#197` (2건 → **A 1건 + B 1건 분할**) — v1의 blocker 정정

**v1 오류 2중 정정(R2·R3·R1 3패널 합치)**: ① v1의 «reconcile 쪽도 동형(helper 위임)»은 실물과 다르다 —
reconcile은 `execute:29`가 **직접** `with self._billing_import_run_uow_factory() as unit_of_work:`.
② 기계 원인은 helper가 아니라 **factory 호출형 `with`의 불인식**: `check-transaction-boundary.py:388-393`
With 판별이 context_expr로 Name/Attribute만 받고 `ast.Call`은 `_attr_root`(:307-310)가 None →
import의 `_run_batch:98`도 같은 Call형이라 helper 추적만으로는 둘 다 안 풀린다(AST 실험 확증).

- **E3a import 건 = A**: `execute`가 `run_batch=self._run_batch` 콜백으로 **쓰기 배치를 구동**한다 —
  읽기 전용이 아니므로 UoW 보유는 정당하고, red는 인식 실패다.
  수정 = ① With 판별에 `Call.func` 언랩 추가(factory attr ∈ attr_uows 인정) + ② 공개 메서드에서
  self 메서드 **호출** 1단 추적(사슬 안 With에도 ① 적용). «해당 공개 메서드에서 도달하는 helper»로
  한정(죽은 helper `_legacy_txn` 방패 차단 — R3-F2). 기지 사각(애너테이션 소거로 has_uow 회피)은
  기존 fail-open으로 계획에 기록만.
- **E3b reconcile 건 = B(정당 — kkebi 반송)**: 파일 51행 전체에 쓰기 0 — `execute`는 UoW로
  `unit_of_work.repository.get(command.run_id)` **읽기 1회**뿐(본 세션 직접 재확인). 성문 #197(:526)
  「읽기 전용 유스케이스는 UnitOfWork를 받지 않는다」 문면 그대로의 위반 — **«틀린 이유로 맞은 판정»**.
  Call 언랩만 넣으면 이 위반이 green으로 합법화되므로, 수정은 반드시 「도달 범위 안에 쓰기
  (repo save/remove·after_commit) 실재」 술어와 결합한다 — 결합 후에도 reconcile은 **의도적으로 red 잔존**.
  **귀결: kkebi 인수 목표는 16→15건 미귀속 + 반송문 1건**(제품 수정 소유 — UoW 제거·직접 리포지토리
  또는 domain-bypass query 주입). kkebi R1 표(«current direct `with uow` AST recognizer misses» ×2)의
  reconcile 절반은 오귀속이었다.
- 부기(R1-F9): kkebi UoW가 `repository` 멤버를 노출하는 것 자체가 #246 위반으로 별도 발화 중
  (introduced.json #246×8 — kkebi 소유). E3a 인식 수정은 현행 형상에 과적합하지 않게
  Call 언랩+쓰기 술어의 **형상 중립** 조합으로 설계한다.

### E4 — `#543` 저널형 애그리거트 (1건 · A′+C — 성문 리비전 필수)

**실제 트리거 정정(R2·R1 합치)**: 발화 원인은 v1이 인용한 `_pending_events`(:33)가 아니라
`billing_event_stream.py:32`의 **공개 가변 저널 필드 `events: list[...] = field(default_factory=list)`**다
(`check-domain-model.py:315-326`의 `has_events_attr` 창은 정확히 `_events`/`events` 이름만 본다).
`_pending_events`·`pending_events` property(:41)·`mark_pending_events_persisted`(:43)는 실재하지만
어느 것도 창을 켜지 않는다.

**성문 충돌 확정(R1-F2)**: 스펙 대장 #543(:866) 「꺼내는 창구는 `pull_events()` 하나 — `events`
프로퍼티처럼 «안 비우고 읽는» 길을 함께 두면 위반」. 사용자 결정(검사기 수용)을 이행하려면
**스펙 대장 #543에 저널 애그리거트 carve-out 리비전이 필수**이고, carve-out은 공개 가변 `events`
필드의 취급(불변 표면 요구)까지 정의해야 한다 — 현행 검사기는 `events` **property**(:347-350)만 금지라
평문 list 필드는 기존 사각이기도 하다.

**수용의 전건(5+α — R3-F6, 이름 존재만으로는 no-op mark 디코이가 뚫림)**: ① 사적 pending 저장소 실재
② 조회 property가 **같은 저장소**의 tuple 사본 반환 ③ mark-메서드 body가 **같은 저장소**를 실제로
비움(`clear()`/빈 재대입) ④ 저널 실체 저장소와 pending 저장소가 **서로 다른 두 필드**(실체·큐 이중
구조 — kkebi 실물 형상) ⑤ 대응 repo save가 그 pending 질의로 가드(E2 창과 조인). 전건 미충족은
현행 red 유지. 음성 픽스처에 **kkebi 승인 R4 이후 형상(pull_events 채택)**도 함께 고정(재릴리즈 재발화 방지).
부기: `_pending_events` 명명 단독 채택은 현행도 무발화인 기존 사각 — 이번 완화의 «인정»으로 오인
포장하지 않도록 리비전 문면에 명기.

### E5 — `#365` 스냅숏 BC 오분류 (3건 · 성문 미정의+A — ⓒ 구조 순수성 술어)

**검사기 실물** `:545-552`: `acl/<대상>/`의 대상이 `vocab.bc_names(root)`(현 스냅숏 BC 열거)에 없으면 #365.

**판정 정련(R1-F4)**: 실물 ACL 3종은 자기 BC 포트만 import하는 **스텁**이라, 스냅숏 안에서 «자사 BC행»
임을 뒷받침하는 건 폴더 이름뿐 — 성문 #365(:677) «우리가 못 고치고 계약이 저장소 밖인 상대» 2연언이
병렬 워크트리 개발을 상정하지 않아 **양쪽 독해가 성립하는 미정의**다. 판정: 성문 미정의 + 측정 보강 —
스펙 대장에 «우리 BC»의 병렬 워크트리 기준을 명문화한다.

**수정 방향(R3-F3 — ⓐ·ⓑ 기각, ⓒ 채택)**:
- ⓐ 선언 입력(제품 측 설정) 기각 — «제품 무변경·동일 앵커 재실행» 인수 계약과 기계 충돌.
- ⓑ 무조건 advisory 강등 기각 — 진짜 외부 시스템의 ACL 위장 문이 열림(미등재 벤더 SDK·통신 stdlib는
  #367 SOCKET_LIBS 밖이라 뒷배 없음).
- **ⓒ 구조 순수성 술어 채택**: 대상 BC가 스냅숏에 없을 때, 그 `acl/<대상>/` 모듈들의 import가
  «자기 BC `application.*`·`framework.*`·비통신 stdlib»뿐이면 후보(advisory) 강등, 벤더/통신
  stdlib(`urllib`·`http.client`·`socket`·`ssl`·`subprocess` 포함)/SOCKET_LIBS import가 하나라도 있으면
  #365 blocker 유지. kkebi 실물 3종은 조건 충족(제품 무변경 인수 가능)·위장 경로는 닫힘.

### E6 — `#555` 재던짐 타입 무시 (1건 A — 성문 리비전 불요)

**검사기 실물** `:618-627`: adapter의 모든 try handler에서 bare `raise` 발견 시 무조건 #555 —
handler가 무엇을 잡았는지 안 본다. **실물**: `django_adapter.py:177-185` —
`except LegacyBillingImportError:`(포트 exception 모듈 ImportFrom) → 내구 기록 → bare raise.
성문 #555(:877) 문면은 «벤더·django 예외»만 겨눈다 — 검사기의 과대 근사(A)이고 성문은 그대로다(R1-F5).

**수정 방향(별칭 세탁 4중 차단 — R3-F7)**: bare 재던짐 허용 = handler 이름이 같은 BC
`port/**/exception.py`(리포지토리면 domain exception 모듈)를 가리키는 **ImportFrom 바인딩** ∧
그 심볼이 해당 모듈의 **ClassDef**(Assign 별칭 불인정) ∧ 모듈 내 **재바인딩 부재** ∧ 튜플 handler는
**전 원소** 충족. `except:`·광역 타입은 현행 red. 판별은 import 출처 기준 — builtin 비상속 기준 금지
(포트 오류가 `ValueError` 서브클래스인 실물 — R1-F5). `except Exception` + isinstance 선별 재던짐은
타입 검사에서 자동 차단(R3-F13 확인).

### E7 — `#33` 복합 명사 오독 (1건 A — #335 충돌로 강화)

**검사기 실물** `check-naming.py:214-218`(+:217 조상 startswith 면제): 첫 `_` 토큰이 트리 폴더명인데
조상에 없으면 #33. **강화 근거(R1-F6)**: 성문 #335(:648) «`models/<entity>_model.py`» — 실물
`EventStreamModel`(db_table=`billing_event_stream`) 기준 entity=event_stream이라 **현 파일명이 #335
문면에 정확히 부합** — 규칙 준수 이름을 #33 휴리스틱이 잡는 **규칙 간 충돌**이다(같은 저장소의
`import_run_model.py`는 `import`가 폴더명이 아니라 미발화 — 우연성 방증).

**수정 방향(둘 비교 후 좁은 쪽 — R3-F10·R1-F6)**: 1안 «#335 자리 면제» — `django_<bc>/models/` 아래
`*_model.py`는 #33 첫 토큰 판정에서 면제(가장 결정적·좁음). 2안 «증거 판별» — stem에서 `_model` 제거분이
같은 BC 애그리거트 snake 이름의 **연속 접미 ≥2토큰** ∧ `_camel(stem)` ClassDef 실재. 부분열(subsequence)
방식은 과광폭이라 기각. 계획에서 1안 우선 검토(#335가 자리를 이미 성문으로 소유).

### E8 — `#562` 범용 용어 충돌 (1건 A — stoplist 경로 한정)

**검사기 실물** `check-business-vocabulary.py:474-478` + 어휘 구성 `business_vocab.py:39-42`(토큰화)·
`:26-34`(STOPWORDS — «닫지 않는» 개방 목록·이미 save/find/data 등 동류 포함). 유입원 실측 확정:
`payment_refund_process_repository.py:15` `get_successful_transaction_keys` → 토큰 `keys` →
`jcs.py:29-33`의 JSON 기술 용어와 동음 충돌.

**비대칭 명시(R1-F7 — v1의 등가 제시 정정)**: stoplist 보강은 측정 장치 자기 설계와 정합하는 수리(A).
«식별자 전체 일치»안은 성문 «한 글자라도 나오면 위반»(:884) 문면·의도(Shared Kernel 차단)를 해체 —
성문 리비전 사안이므로 **기각**(신조합 밀수 문 — `refund_settlement_ratio` 반례).

**수정 방향(R3-F11)**: **pure/ 검사 국소 stoplist**(`_check_pure` 전용)를 1안으로 — 전역 STOPWORDS
편입은 #47·#52·#518·#553 등 타 검사기 어휘 판정의 조용한 이동 위험(전/후 전량 diff로만 검증 가능).
초기 목록 최소({`keys`} + 필요시 직렬화 소어휘) — 등재 시 `all_vocab` 교집합 대조로 업무 실어휘
(예: `envelope`) 미포함 확인 절차를 계획에 포함. 잔여(등재 낱말만으로 쓴 업무 규칙은 원래 못 봄)는 명기.

### E9 — `final.md #429` celery 문면 (기해소·통지만)

현행 성문(discipline-houserules final.md:221)은 이미 «celery 채택 전제는 정본 트리(표준) 수준 —
미채택 프로젝트도 빈 파일(#488 정상 상태)». 패널 검증: 수리 커밋 f4124ab(08-24 11:25 KST) ∈
`dddjango--v2.17.1`(08-24 14:46 KST) — billing 기록(08-24 04:54) **이후** 수리 확정. 검사기
`check-layer-skeleton.py:60`과 정합. **작업 0 — kkebi에 «≥2.17.1 기수리» 통지.**

### E10 — ㉮ canonical framework 경로 (편승 확정)

실측: error 계열 scope-render 3종이 kkebi에서 「DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED + provenance 분석
불능 + noncanonical inventory」 사용 오류 exit 1 — 정적 code 모드 실행 불능(v2.17.2 사본과 HEAD의
**실측 결과 동일** — 사이에 R-3401 변경 +71/-1이 있으므로 «판본 동일»이 아니라 «결과 동일»이 정확 문면).
tarot 런은 동적 증명으로 우회했고 그 경로에서 무default Literal이 정적 게이트에 닿지 않았다
(런 기록 review-api-phase2-runtime.md:12·:44 실물 — 패널 재확인).

**수정 방향(R3-F8)**: kkebi 승인 경로(`framework/django_ninja/error_schema.py` ↔
`framework.django_ninja.error_schema` — STOP 승인 08-23 16:44 실재)를 정본 허용 집합에 가산.
- 정본 경로 문자열 결합점 **18곳**(centralization 8 · api-error-controller 6 · openapi 4 —
  `check-openapi-error-declaration.py:2132`는 dict 직접 인덱스 = 누락 시 KeyError) →
  **검사기당 단일 상수 집합**으로 모아 전 지점 그 집합 경유로 개조. 두 경로 **동시 실재 시 red**
  (정본 이중화 금지). codex byte 미러 포함 6파일 동시 갱신.
- 제약 재서술: «기존 통과 무영향»이 아니라 「픽스처·정본 경로 저장소 무영향 + **tarot 정적 런의
  신규 red는 의도된 회복**」 — kkebi 사전 통지에 포함(동적 증명이 놓친 실위반이 드러나는 것이 목적).
- 잔여 명기: 비정본 경로 개명으로 정적 게이트에서 이탈하는 채널(exit 1 → 동적 증명 우회)은 일반형으로
  존치(동적 증명 모드 존치 결정의 귀결).

### E11 — ㉯ `--error-profile auto` 침묵 사각 (편승 확정)

실측 정정(R2): 런 기록 refactor-scope.md:16의 exit 0은 tarot BC 부재 시점 관찰이라 실물 증거로 부적격 —
대신 **직접 실행 재검증**으로 참 확정: HEAD `check-error-centralization.py <dir> --error-profile auto`
(무 selector)가 `bc_error_schema.py` 실재하는 feat-tarot-bc·feat-billing-bc에서 **무출력 exit 0**.

**수정 방향(#114 정합 — R3-F12)**: 대상-후보 술어를 «파일 실재»로 하면 #114(«HTTP 안 여는 BC도 빈
`bc_error_schema.py` 상시 보유» — `check-error-centralization.py:4679`)와 정면 충돌해 모든 표준 트리가
시끄럽게 실패한다. 후보 판별은 기존 helper `_skeleton_placeholder_module`(:638) 재사용 —
「**비-placeholder** bc_error_schema.py 또는 비-placeholder framework error schema 실재 ∧ selector 부재」
일 때만 사용 오류. BC 0인 brownfield(`_tree_bcs` 공집합)·순수 placeholder 트리는 현행 조용한 0 유지.

## 3. 성문(스펙 대장) 리비전 목록 — 이번 릴리즈 동반분

| 규칙 | 리비전 내용 | 근거 |
|---|---|---|
| #545(:867) | 적용 술어 명문화 — 이벤트 채택 애그리거트(event/ 실재 ∨ 루트 pending API)의 repo에만 가드 요구·eventless는 비적용. 인정 가드 = 극성(잔존-시-raise)+수신자 한정 의미 창 | E1 — 문면이 무조건 적용을 지지하므로 개정 필수 |
| #543(:866) | 저널 애그리거트 carve-out — 실체·큐 이중 구조에서 pending 조회 property+mark-persisted 창구의 전건(5조건) 인정·공개 가변 `events` 필드의 불변 표면 요구 명문화 | E4 — «창구 하나» 문면과 충돌 |
| #365(:677) | «우리 BC»에 병렬 워크트리(스냅숏 부재 자사 BC) 기준 명문화 + 구조 순수성 강등 조건 | E5 — 미정의 |
| #197(:526) | (문면 불변 — 확인만) 읽기 전용+UoW 금지 유지. reconcile 반송의 준거 | E3b |

## 4. 공통 수정 제약·인수 판형 (v2 — 패널 보강)

1. 모든 완화는 **좁은 경계 + fail-closed**(R-3401 판형 — 전건 충족만 통과·미충족은 기존 red 경로).
2. 항목마다 **양성 픽스처(기존 위반·디코이 red 유지) + 음성 픽스처(정당 관용구 green)**:
   E1 거짓 양성 3형(죽은 분기·지역 이름·무관 수신자)·E2 디코이 3형(항상-False property·raise 삼킴·
   쓰기 후 가드)·E2 극성 반례(빈-경우-raise = B 형상)·E4 no-op mark 디코이·E4 R4-이후 형상·
   E6 별칭 세탁 4형·E5 위장 ACL(통신 import)·E7 «#335 자리» 정상/비정상·E8 밀수 반례·E11 placeholder 트리.
3. 검사기 수정 = codex **byte 미러** 동시 갱신 · 하네스(checker_baseline_matrix·findings_count_matrix)
   EXPECTED 갱신 · **T2-0b 봉인 재발행** · `make verify` green.
4. **인수 기준(릴리즈 전 — R3-F9 판형 확장)**:
   - **동결 사본**: 라이브 워크트리 3종(billing·saju·tarot)을 rsync 사본+sha256 manifest로 동결,
     전/후 런을 같은 사본에 수행(라이브 편집 오염 차단 — tarot 런이 진행 중이다).
   - **전/후 전량 diff**: 27종 전 검사기 × 3워크트리 — (checker, rule, file, line, message) 레코드 +
     **exit code + stderr**(E10·E11은 발화가 아니라 exit/사용-오류가 변한다) + 후보 라인까지 수집.
     허용 변화 = 대상 19건 중 **18건 소멸**(E3b reconcile 제외) + E10 tarot 정적 모드 활성화分(의도된
     신규 — 목록화해 kkebi 통지) + E11 사용-오류 전환분. 그 외 diff 0.
   - **정당 잔존 확인**: `#545` event_stream 1건·`#197` reconcile 1건이 **red로 남아 있을 것**.
5. **kkebi 통지문**(사용자 경유) 포함 사항: ① 15건 미귀속 이행 + **reconcile #197 반송**(B — 성문 :526
   문면·읽기 전용 실물 51행 근거·제품 수정 소유) ② #429는 ≥2.17.1 기수리 ③ E10로 tarot 정적 게이트가
   살아나며 신규 red(무default Literal 등)는 의도된 회복 ④ 재실행 명령은 기존과 동일(동일 앵커).
6. 릴리즈는 `make release`(사용자 실행) → 양 런타임 설치본 갱신 → kkebi 재실행.

## 5. 미해결 — 수정 계획 문서에서 확정할 것

- E7 1안(#335 자리 면제) vs 2안(증거 판별) 최종 선택(1안 우선 검토).
- E2 별칭 대입 집합 추적의 정확한 범위(정당 코드 오탐 방지 — R3-F13).
- E10 상수 집합 개조의 파일별 결합점 전수 목록(18곳 좌표) 작성.
- 스펙 대장 리비전의 형식(대장 개정 이력 관례 확인 — LEDGER류 절차 존재 여부).

## 6. 패널 처분 대장 (3인 × 28건 — 채택 25 · 부분 2 · 기각 1)

**R1 판정 반증 렌즈** (10건):
| # | 심각도 | 요지 | 처분 |
|---|---|---|---|
| R1-F1 | blocker | reconcile #197은 읽기 전용+UoW = 성문 문면 위반 — «틀린 이유로 맞은 판정»·완화 시 합법화 위험 | **채택** — E3 분할(A+B)·반송·쓰기 술어 결합(본 세션 실물 재확인: 51행·쓰기 0) |
| R1-F2 | blocker | #543 «검사기 수용»은 성문 «창구 하나» 문면과 충돌·공개 가변 `events` 필드 누락 | **채택** — E4 트리거 정정·성문 리비전 필수(§3)·공개 필드 취급 포함 |
| R1-F3 | major | E1 성문 문면은 무조건 적용 지지 — «A»가 아니라 «A+C» | **채택** — §3 #545 리비전 동반 |
| R1-F4 | major | E5 «A 확정» 과함 — 성문 미정의(병렬 워크트리 미상정)·§3-5에 E5 누락 | **채택** — 판정 격하·§3 #365 리비전 |
| R1-F5 | minor | E6 반증 실패(판정 유지)·화이트리스트는 builtin 비상속 기준 금지(ValueError 서브클래스 실물) | **채택** — import 출처 판별 명문화 |
| R1-F6 | minor | E7 반증 실패·#335와 규칙 간 충돌 발견(판정 강화)·«#335 자리 면제»가 더 좁음 | **채택** — 1안 우선 |
| R1-F7 | minor | E8 stoplist 경로만 A — 전체 일치안은 성문 해체(등가 제시 정정) | **채택** — 전체 일치안 기각 명시 |
| R1-F8 | major | 7규칙 전부 그래프 밖 — 성문 정본은 스펙 규칙 대장·«그래프 리비전» 착지 오류 | **채택** — §0 착지 정정·리비전=대장 개정 |
| R1-F9 | minor | kkebi UoW.repository는 #246 위반(별도 발화 중) — 완화는 형상 중립으로 | **부분 채택** — E3a 설계 원칙에 반영(#246 수리는 kkebi 소유라 그 이상 불요) |
| R1-F10 | 확인 | 검사기 서술·좌표·재현 전건 일치·E9 유지 | 기록 |

**R2 실물 정합 렌즈** (5건):
| # | 심각도 | 요지 | 처분 |
|---|---|---|---|
| R2-B1 | blocker | E3 «reconcile 동형» 오진 — 진짜 원인은 factory 호출형 With 불인식·제시 수정으로는 양건 미해소 | **채택** — E3 전면 재서술(R1-F1·R3-F2와 합치) |
| R2-m1 | minor | E10 «v2.17.2·v2.17.3 동일» 과장(사이에 R-3401 +71/-1) | **채택** — «실측 결과 동일»로 정정 |
| R2-m2 | minor | E4 발화 트리거 좌표 누락(`events:` 필드 :32가 has_events_attr 트리거) | **채택** — E4 정정 |
| R2-m3 | minor | E11 인용 증거 시점 오류(스캔 시점엔 tarot BC 부재) — 직접 실행으로는 참 | **채택** — 증거를 직접 실행 재검증으로 교체 |
| R2-m4 | minor | «git 명령 불가» 일반화 오류(패널 세션은 성공 — 환경 의존) | **채택** — §0 문면 완화(+앵커 일치 추가 증거 편입) |

**R3 수정 파급 렌즈** (13건):
| # | 심각도 | 요지 | 처분 |
|---|---|---|---|
| R3-F1 | blocker | E2 극성 조건 부재 시 정당 판정 B가 함께 소멸(인수 자기위반) | **채택** — E1·E2 수정 방향 ②에 극성 필수 |
| R3-F2 | blocker | E3 처방 무효 — Call 언랩+1단 호출 추적 2요소·죽은 helper 방패 차단·애너테이션 사각 기록 | **채택** — E3a 재서술 |
| R3-F3 | blocker | E5 ⓐ 인수 계약 충돌·ⓑ fail-open — ⓒ 구조 순수성 술어 | **채택** — ⓒ 확정 |
| R3-F4 | major | E1 적용 술어는 «event/ 실재 OR 루트 API» 2원 합집합(흔적 숨기기 차단)·join-miss·반쪽 채택 경계 | **채택** — E1 ① |
| R3-F5 | major | E2 디코이 3형(항상-False property·raise 삼킴·쓰기 후 가드) — 양측 조인 필요 | **채택** — E1 ③ |
| R3-F6 | major | E4 이름만 인정이면 no-op mark 디코이 — 5전건+R4-이후 픽스처+기존 `_pending_events` 사각 명기 | **채택** — E4 전건 |
| R3-F7 | major | E6 별칭 세탁 4형 — ImportFrom+ClassDef+재바인딩 부재+튜플 전원소 | **채택** — E6 |
| R3-F8 | major | E10 결합점 18곳·dict 인덱스 크래시·«무해» 반증(tarot 신규 red는 의도)·이탈 채널 잔여 | **채택** — E10 재서술 |
| R3-F9 | major | §3 인수 결손 — 전량 diff 판형·동결 사본·tarot 인수·거짓 양성 3형 픽스처 | **채택** — §4 확장 |
| R3-F10 | minor | E7 부분열 과광폭 — 연속 접미+실물 증거 또는 #335 자리 면제 | **채택** — E7 |
| R3-F11 | minor | E8 국소 stoplist가 정답(전역 STOPWORDS 파급·전체 일치 손실) | **채택** — E8 1안 |
| R3-F12 | minor | E11 «파일 실재» 술어는 #114와 충돌 — placeholder 판별 재사용 | **채택** — E11 |
| R3-F13 | 확인 | 차단 확인 4건(#351 개명 차단·stripe 선언 차단·isinstance 세탁 차단·주석/문자열 위조 불성립)+별칭 집합 필요 | 기록(E2 별칭 추적 §5 이관) |

**기각 1건**: R3-F11의 «전역 STOPWORDS 편입 절대 불가» 취지 중 «향후에도 금지» 부분 — 이번 릴리즈는
국소로 하되, 전역 편입은 전/후 전량 diff 무변화가 증명되는 별건에서 재검토 가능(문 닫지 않음).

## 7. 정오 (v2.1 — 2차 패널 소급 적발분 · 본문보다 우선)

1. **§4-4 산술**: «대상 19건 중 18건 소멸»은 오기 — 정당 잔존 2건(event_stream·reconcile)을 빼면
   **17건 소멸**(billing 15 + saju 2)이 옳다. [인수 F3·성문 m1]
2. **§2 E3a의 «import 건은 green(콜백 helper의 with+쓰기 도달)»은 실물과 다르다** — import 유스케이스
   파일 전체에 쓰기 호출 0(쓰기는 어댑터의 콜백 람다 안·파일 밖). `_run_batch`도 호출이 아니라
   **참조 전달**이라 «호출 1단 추적»으로 도달 불능. import/reconcile의 유일한 정적 구별자는
   `_run_batch:99`의 `work(unit_of_work.repository)` — **repository의 콜러블 인자 탈출(escape)**이다.
   수정 술어는 계획 v2 W2가 재정의한다. [인수 F1·설계 W2-1]
3. **§2 E1① 적용 술어 «루트 pending 상태/API» 2요소로는 부족** — saju `SajuChart`의
   `_snapshots`(사적 list)+`snapshots`(tuple 사본 property)가 그대로 충족해 **오탐 → saju 미해제**.
   pending 판별에는 **«같은 저장소를 실제로 비우는 소거/소모 창구 실재»** 3요소가 필수다
   (SajuChart는 append만 있고 소거 0 — 배제·payment_order `pull_events`·event_stream `clear()`는 충족).
   [설계 W1a-1]
4. **§2 E10 «결합점 18곳(8+6+4)»은 어느 척도와도 불일치** — 실측: 문자열 결합 **라인 12**
   (EC 3·api 5·openapi 4)·상수/파생 사용 표면 **≥37**(EC ≥20·api ≥12·openapi 5 — `:2680` 문자열
   리터럴·`:5398` basename 등호·`COMMON_INIT` 구조 요구 포함). 구현 전 좌표 대장 작성이 완료 조건.
   [인수 F9·설계 W6-1·W6-2]
5. **§2 E10의 성문 착지 누락** — canonical 경로는 스펙 대장 **#417**(:733)과 **그래프 소유 성문**
   (implementation-django-ninja final.md:550 — §6.2 graph-owned)이 명시한다. ㉮는 검사기 수정이 아니라
   **정식 규범 리비전 사슬**(TTL Expression revision → 재투영 → 미러 → rulepack → 계수 → LEDGER 해당분
   + 스펙 대장 #417 부칙)을 동반해야 하며, kkebi 계약이 인용한 #72(«검사기·성문 한 커밋»)가 이를
   요구한다. [성문 B1]
6. **§2 E11 «시끄럽게 실패(exit 1)»는 기각** — Coordinator(`commands/dddjango.md:75·:111·:175`)가
   auto 렌더를 의무화하고 auto에는 selector 전달이 금지라, exit 1은 **파이프라인 교착**을 만든다.
   대체: **stderr 경고 라인**(auto·**None 프로파일 공통** — 비-placeholder 대상 실재 ∧ 인벤토리 해석 0)
   — exit·stdout·finding 레코드 불변(하네스 무파급·침묵만 제거). 원 의도(fail-loud)보다 약함을 명기.
   [설계 W7-1·인수 F2·F8]
7. **§4-4 허용 diff에 ⓕ 추가** — ① #365 blocker→후보(ⓓ) 전환 3건(신규 후보 라인) ② **tarot #545
   2건 소멸**(새 적용 술어로 비적용 전환 — `tarot_reading`(공개 list)·`tarot_import_run`(list 0)):
   같은 측정-결함 부류의 일관 귀결이다. [성문 M5·인수 F4·설계 W1a-5]
8. **§3 «성문 리비전 목록»에 #33 부칙 1건 추가** — #33↔#335 규칙 간 충돌은 대장 판례(C6·C8)대로
   문면 개정으로 해소한다(«#335가 소유하는 `models/<entity>_model.py` 자리의 첫 토큰은 #33의 대상이
   아니다»). [성문 M6]
9. **부칙 문면 보강 의무** — #545 부칙에 «비소모 질의»·«persistence 전 abort»·반쪽 채택(후보) 처분,
   #543 부칙에 5조건 완결·«저널 아닌 애그리거트의 관용구 채택은 위반(관찰)»·`_pending_events` 명명
   기존 사각 명기, 부칙 형식은 `<span>날짜 · **라벨** — …</span>` 판례. [성문 M2·M3·M4·m4·설계 W3-2]
10. **통지문 보강 의무** — reconcile 반송은 kkebi R1-A 문면(«16 no longer attributed»·«product write 0»)
    과 충돌하므로, **kkebi 측 사용자의 R1-A 재결정(16→15 재배치 + 해당 제품 write 허용)이 선행**임을
    통지문이 선제 고지한다(kkebi 자체 표의 «misses ×2» 중 reconcile 절반은 오귀속이라는 반박 인용 포함).
    «billing G2 차단 해제» 표현은 «R1 전제 해소»로 정정. saju에는 3개조↔이행 좌표 대응표 별도 제시.
    [성문 M1·m5]
