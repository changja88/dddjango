# 현장 보고 수리 2 — ⑤ 구현 리뷰 · 리뷰어 B(규범 축 — 그래프 정본·문면·투영·미러·저작 규약) (2026-09-04)

독립 리뷰. 대상 = `fix/field-report-2` 규범 커밋 35fc29b(+ 문서 커밋 421782e). 읽은 것: 계획 v2(Δ1~Δ15) → 루브릭(⓪·①·②③·④ 기록) → rv3-B → `git show 35fc29b -- ontology/`(rules 8 · wiring 4 · ISSUED · LEDGER · target-counts · query-golden) → 투영 diff(agents 1 · commands 1 · SKILL.md 1 · final.md 5 · codex 손 미러 3 · workspace/reference 5) → authoring §5·§13·§14·§16 · DEVELOPMENT §3 → `git show 421782e`(현장 보고·로드맵·ledger·조감도·루브릭 ④). 검증 도구 8종 재실행(아래 §5). 표준 트리·검사기(`check-layer-skeleton`·`check-context-isolation`·`check-usecase-dto-placement`)·양 저장소(spring·kkebi 읽기 전용) 로 R-3449 문면의 칸 실존을 대조. 저장소 무수정(이 파일만 신규 · 스크래치 픽스처는 `/private/tmp/…/scratchpad` 에서 생성 후 삭제).

## 1. 판정 표

| 항목 | 판정 | 핵심 근거 |
|---|---|---|
| ①~⑧ 8항 반영(rv3-B «반드시 바꿀 것») | **검증됨(8/8)** | §2 대조표 — 전건 반영. 단 ②는 rv3-B 가 준 경로 자체가 오독이라 아래 MAJOR-1 로 이관 |
| G R-3449 문면 — `application_layer/<area>/exception.py` | **MAJOR-1** | 표준 트리(houserules final.md 38~44행)에 그 칸 없음 · `check-layer-skeleton` 실증 `[#490] 트리가 이 층에 이름을 준 파일이 아니다` exit 2 · 양 저장소 `application_layer/**` 비-port 예외 모듈 0/0 · 실전 번역 칸 = `domain_layer/<aggregate>/exception/<exception>.py`(69~70행 · #92/#95 허용 칸) — §3-G |
| G R-3427 rev4 «(실행기 사각 S3)» | **MINOR-1** | architect md 에 S-id 정의·사각 목록 0(유일 등장 = 이 문장) → 해석 불능. rv3-B 대체 문면 꼬리 «— pregate-report 헤더의 사각 목록» 탈락 |
| 검수표(루브릭 ④) 기록 결손 | **MINOR-2** | §16 4원 근거(R-3447·R-3449 enforcedBy) 0 · §13 문장→Work 대응(b7) 은 계획 Δ3 에만 · R-3450 모델링 선택 사유 0 · Δ11 R-3427 «실효 변화» 사유 0(LEDGER append-only → ④ 에) · «Coordinator 108·150» 행 번호 오기 |
| 문서 수치(현장 보고) | **MINOR-3** | F 행 «spring 27 BC» (증거 F = spring 16·kkebi 12 → 27 은 15+12) · 정정 추기 ④ «`models/**` 제외» 근거 0(증거 DE·원문 L220 모두 없음) |
| R-3449 delegatedTo 단독 design-review-ddd | MINOR-4(병기) | 형제 R-0524~0527 은 enforcedBy 만(구현 시점) · 미커버분(재수출 경유 catch)은 코드에서만 관찰 → discipline-reviewer 병기 권고(R-3421 다중 위임 선례). 기본값 표 준수라 위반은 아님 |
| D R-3446 문면·착지·형 | 검증됨 | b3 = 다음 서수 = order 3 말미 · blockquote «> dddjango 단서:»(«경계 단서» 변형 — 경계 조항 아니라 정확) · «타입 규약»·`Never` 병기 · R-2720 서로소 · 렌더 가독(펜스→빈 줄→인용→§4.5) |
| E R-3447/R-3448 b7 | 검증됨 | rv3-B 대체 문면과 byte 동일 · 문장 1~4/5~6 대응 · 참조 3 실존(§4.1 :81 · python §1.12 :311 · ddd §3.1 :472/R-3443 :485) · b6 «예시 면제» 직후 배치 · wiring 정정형(3447 이중·3448 위임만) |
| E R-0345 rev2 · R-0284 rev3 | 검증됨 | amendment · prefLabel 갱신 · 렌더 133·108 · codex 150·125 손 미러 동일 |
| F-1 R-0719 rev2 | 검증됨 | «(매요청 조립).» 직후 삽입(말미 아님) · «꽂히는 자리가 선언한 Protocol·`Callable` 시그니처» · amendment |
| F-2 R-3450 b24 확장 | 검증됨 | 블록 신설 0 · `statesNorm R-3450` · Permission · 말미 `\n\n` 유지 · 문면 «실배선 정합 … 이 대상의 보호가 아니다» · wiring discipline-reviewer(R-2155/2156 동형) |
| H R-3181 rev3 | 검증됨 | amendment · 문면 = rv3-B 대체 문면 · «error inventory» = Coordinator :117 «내용 없는 골격 파일(빈 모듈)은 inventory에서 제외» 의 inventory(`--project-*-error-module` 목록) 정확 · 함수명 0 · R-0319 인용 |
| 저작 규약(§5·§13·§14·§16) | 검증됨 | §4 |
| 계수·골든 | 검증됨 | Expression +10 · Work +5 · **Block +2**(Δ13 «+3» 은 Δ1 §5.3 새 블록 전제의 잔재 — ④ 정정 정당) · q4 3445→3450 |
| 미러 표면 | 검증됨 | doc_key 8 · final.md 5×3(dddjango·codex·workspace/reference) · codex 손 미러 3(hunk byte 동일 · 전체 diff = 플랫폼 형식 차뿐 → rv3-B 미확인 4 해소: 11행 차 = graph-owned 마커 10 + `user-invocable` 1) · rulepack ×2 byte 동일 · `by_checker` 에 R-3447/R-3449 편입 |
| 검증 도구 | **검증됨(전부 green)** | gate 90/90 · render-sync 540 절 red 0 · structural 7종 · hierarchy 9종 불일치 0 · issued 0 · ledger 0 · corpus_mirror 11/11 · query-golden 7종 |

## 2. 8항 대조표(rv3-B «반드시 바꿀 것» → 35fc29b)

| # | 요구 | 구현 좌표 | 판정 |
|---|---|---|---|
| ① F-2 b24 확장 | 블록 신설 0 · `statesNorm R-3450` · «실배선 정합 … 이 대상의 보호가 아니다» | `discipline-tdd-final.ttl` s025-5.5/b24 — text 2불릿 · `statesNorm djr:R-3450` · Permission · 말미 `\n\n` | ✓ |
| ② R-3449 착지 §3.6 b3 불릿 | «자기 영역의 예외 … 재수출 경유 포함 … #92/#93 은 import 경로만 본다» | `architecture-ddd-final.ttl` s023-3.6/b3 — 불릿 +1 · `statesNorm … R-3449` · 밀림 0 | ✓ 반영 — 단 경로 오독 전파(MAJOR-1) |
| ③ F-1 삽입 위치·어휘 | R-0719 문장 직후 · «꽂히는 자리가 선언한 Protocol·`Callable`» | `implementation-django-ninja-final.ttl` s010-2.3/b18 — «(매요청 조립). `build_<use_case>()` 가 …» → «이벤트 구독 결선은…» 앞 | ✓ |
| ④ E b7 문장 순서·참조 | R-3447 1~4 · R-3448 5~6 · «implementation-python §1.12» · R-3443 참조(§3.1) · `allow-star-arg-any` · «ⓓ 후보(#645)» | `discipline-houserules-skill.ttl` s007-4/b7 — rv3-B 대체 문면과 동일 | ✓ |
| ⑤ wiring 5건 | 3446/3447/3448/3450 → discipline-reviewer · 3447 enforcedBy public-surface · 3449 → design-review-ddd + enforcedBy context-isolation | wiring 4파일 7간선 — 전건 일치 | ✓ (MINOR-4 병기) |
| ⑥ 개정 종류 | R-3427 rev4·R-3181 rev3 = amendment · R-0719/R-0345/R-0284 amendment · D «타입 규약» | Expression 5 노드 전부 `revision-amendment` · b3 «타입 규약이 `-> None` 을 강제하므로» | ✓ |
| ⑦ 미러 표면 | doc_key 8 · final.md 5 · codex 손 미러 3 · 등재 3문서 | stat: rules 8 · final.md 5×3 · codex SKILL 3 · 등재 3문서는 95a95cc(spec 9행·predicates 1·owner-map 1) | ✓ |
| ⑧ R-3181 어휘 | «Coordinator 가 빈 모듈을 error inventory 에서 제외하는 것(R-0319)» · 함수명 0 | `discipline-houserules-final.ttl` s003-0/b3 — 문면 일치 · «내용 없는 골격 파일(0바이트·docstring/주석뿐)» | ✓ |

## 3. 문면별 상세

### D — R-3446 (`s032-4.4/b3` · order 3)
- 형: 코퍼스 blockquote 단서 = «> dddjango 경계 단서:» 2건(python §4.4 b1 :632 · cleancode :1626). 신설은 «> dddjango 단서:» — «경계» 를 뺀 변형이 맞다(경계 조항이 아니라 선언 규범). 렌더 :651 — 코드 펜스 → 빈 줄 → 인용 → 빈 줄 → «### 4.5» 가독 ✓.
- 모순·중복: R-2720(«부재·거절은 답» — 반환 경로 있는 함수) 과 서로소 · 코퍼스 `NoReturn` 언급 이 블록뿐 ✓. «타입 규약이 `-> None` 을 강제» 사실 정정 ✓ · `Never` 동치 ✓.
- wiring: R-2720(같은 절) 이 discipline-reviewer(+context-isolation) → R-3446 discipline-reviewer 동형 ✓.

### E — R-3447 · R-3448 (`s007-4/b7` · order 7) + R-0345 rev2 · R-0284 rev3
- 문면 = rv3-B 대체 문면과 byte 동일(diff 0). 문장 1~4 = R-3447(Prohibition · s3 «`object` 로 쓴다» 는 다문장 Work 선례) · 5~6 = R-3448(Obligation).
- 참조 실존: «§4.1 «시그니처만 강제하므로 나머지는 백스톱과 감수자»» = SKILL.md :81 원문 부분 인용 ✓ · «implementation-python §1.12» = final.md :311 «TypeIs vs TypeGuard: 타입 좁히기» ✓ · «architecture-ddd §3.1 의 경계 규범대로 값 객체를 부르기 전» = :472 §3.1 · :485 R-3443 문장 ✓.
- 배치: b6(«표준 문서군의 코드 예시는 … 적용 대상이 아니다») 직후 → Knowledge Level 예제 `dict[str, Any]` 는 R-3156 면제로 읽힌다(로드맵 R-20 추기와 정합) ✓.
- R-0345 rev2: 소개행 «명시 `Any`(#645 — 시그니처는 차단·변수/제네릭 안은 ⓓ 후보)» 렌더 :133 · codex :150 ✓. R-0284 rev3: step 5 «`check-public-surface-annotation`(registry #11)의 ⓓ 후보(#645 …)를 동봉» 렌더 :108 · codex :125 ✓ · prefLabel «+ ⓓ 후보 동봉(registry #4 200행 신호 · #11 명시 Any)» ✓.
- wiring: R-3150/R-3158 형(이중) · R-3448 위임만(검사기 미커버) ✓ · rulepack `by_checker[public-surface]` 에 R-3447 편입 ✓.

### F-1 — R-0719 rev2 (`s010-2.3/b18`)
- 삽입 위치 = «호출만 한다(매요청 조립).» 직후 · «이벤트 구독 결선은 `event_wiring.py`가 따로 진다.»(R-0720) 앞 → §13 «등장 순 = 채번 순» 유지 ✓. 문면 «꽂히는 자리가 선언한 Protocol·`Callable` 시그니처와 같아야 한다 … 팩토리 **본문 안에서** … (모듈 최상단 대입은 #85 위반 …)» ✓. amendment rev2 · prefLabel 갱신 ✓ · 5 표면 동일 ✓.

### F-2 — R-3450 (`s025-5.5/b24` 확장)
- 블록 신설 0(rv3-B BLOCKER 해소) · b24 text = «- 별도 사용자 승인 … 공개 Python 계약\n- composition root 의 **실배선 정합** — … 이 대상의 보호가 아니다\n\n» · `statesNorm djr:R-3450` · Permission ✓. 렌더 :438 — 화이트리스트 7번째 불릿, 다음 문단 «다음 항목은 그 자체로 영구 테스트 자격이 아니다.» 앞 ✓.
- 어조: 형제 6불릿과 같은 명사구형 · quota 어휘 0 ✓. prefLabel «fake 는 프로세스 밖 경계뿐» — 문면과 일치 ✓.
- 모델링: «불릿 자체에 Work» 는 §5.5 화이트리스트에선 신규 관행(형제 6불릿 Work 0 · R-2155 «목록» Work) — 계획 §0 에서 선택됐으나 ④ 검수표에 «왜 R-2155 amendment 가 아닌가» 사유 0 → MINOR-2(c).

### G — R-3427 rev4 (`s005/b36`) + R-3449 (`s023-3.6/b3`)
- **R-3427 rev4**: 문면 = rv3-B 대체 문면과 동일(«층 규율 검사기가 금지·예외 항목으로 판정하는 것» · #92~#96·#185/#186 = `check-context-isolation.py:10` docstring 정합 · «잎이 port 예외를 잡을 계획이면 그 import 행을 그대로 적어 G1 에서 #93 예보») — 단 꼬리 «(실행기 사각 S3)» 만 남고 «— pregate-report 헤더의 사각 목록» 탈락. `grep -E '\bS[0-9]\b|사각|pregate-report' agents/design-architect.md` = :90 이 문장뿐 → architect 독자는 S3 를 해소할 수 없다(Coordinator 만 S7 1회). amendment rev4 ✓ · prefLabel «경계 3분류(…) 잎→port 예외 import 도 행으로» ✓ · codex architect SKILL.md :84 동일 ✓.
  - **대체(MINOR-1)**: «산문에만 적힌 경계 import 는 예보 표면 밖이다(pre-gate 보고 헤더의 사각 목록 S3).» — 미배포 rev4 라 in-place(LEDGER «in-place · 미배포» 선례) + 렌더 + codex 손 미러.
- **R-3449 — MAJOR-1(칸 실존)**:
  - 표준 트리(`discipline-houserules/references/final.md` 트리 38~58행): `application_layer/<area>/` 의 자식은 `<use_case>/{_use_case,_command,_query,_result}.py` 뿐(40~44행). `exception.py` 칸은 **48행 `port/<capability>/exception.py`**(= #93 이 잎 import 를 금지하는 바로 그 port 예외) · 56행 `port/domain_bypass_query/<capability>/exception.py` · **69~70행 `domain_layer/<aggregate>/exception/<exception>.py`** · 122행 framework `<capability>/exception.py`. `application_layer/<area>/exception.py` 는 없다.
  - 실증: `workspace/eval/fixtures/skeleton/good_bc` 를 스크래치에 복제해 `application_layer/order/exception.py`(0B) 추가 → `check-layer-skeleton.py` exit 2 · `[#490] …/application_layer/order/exception.py: 트리가 이 층에 이름을 준 파일이 아니다`(`<area>/` 는 리프 폐쇄 폴더가 아니라 재량 조항 밖 — :296~300).
  - 실전: spring·kkebi `application_layer/**` 의 비-port 예외 모듈 **0/0**(port `exception.py` 49/76). 번역 실물 = spring `accounts/application_layer/verification_code/request_verification_code/request_verification_code_use_case.py` :13 port 예외 import → :34 **`domain_layer/verification_code/exception/verification_notice_undeliverable`** 로 raise · driving 잎 import 는 `domain_layer/<agg>/exception/…` 만(:27~36). 검사기 준거 = `check-usecase-dto-placement.py:180 _lawful_domain_exception_import`(«#95·#92 driving 잎이 domain 에서 가져올 수 있는 것: exception·값 객체») · #92 문면(houserules final.md :206 «예외는 넷: 도메인 exception·값 객체(#95) …»). architect 의 exception-map 도 «도메인→published» 매핑이다.
  - 근원: rv3-B §2-G «`application_layer/<area>/exception.py`(트리 48행 — #92 가 잎에 허용하는 유일한 예외 칸)» 가 오독(48행 = port 예외) → 계획 Δ2 → 35fc29b 로 전파. 본 리뷰가 정정한다.
  - 효과: 문면대로 짜면 #490 red(코더 왕복) · 또는 48행 port 예외로 오독하면 R-3449 자기모순. 규범이 존재하지 않는 칸을 가리키는 것은 «한 주제 한 소유자»(트리 값 = houserules final.md 단일 출처) 위반.
  - **대체 문면**(b3 불릿 · 나머지 동일): «- port 예외를 **자기 BC 의 예외**(`domain_layer/<aggregate>/exception/<exception>.py` — #92/#95 가 잎에 허용하는 유일한 예외 칸)로 번역한다 — driving 잎(컨트롤러·OHS)은 port 예외 **타입**에 의존하지 않는다(직접 import 든 use case 모듈의 재수출 경유든 같다 · #92/#93 은 import 경로만 본다) — 잎은 번역된 실패만 분기한다(`<use_case>_result.py` 엔 성공 한 벌 · #571)». prefLabel «자기 영역 exception.py» → «domain_layer/<agg>/exception/». 수정 = ttl in-place(미배포 rev1) → 렌더 → LEDGER 재기준선 → 소스 미러 스팬 교체 → `corpus_mirror_sync --write`(codex final.md) · 검사기·wiring 무접촉.
  - 그 밖 정합: «#571 성공 한 벌» 은 python §4.4 b1 :632 · cleancode :1626 과 동일 어구 ✓ · §3.6 형제 불릿 R-0524~0527 이 각 1 Work → «불릿 = Work» 모델 정합 ✓ · 같은 절 펜스 안 «※ … #635 · #484» 가 플러그인 고유 삽입 선례라 검사기 번호 인용 적법 ✓ · 어조(형제 교과서 1행 vs 3절 규범) 는 허용.
  - wiring(MINOR-4): `enforcedBy context-isolation`(#93 import 경로) 4원 — ① 문면 «#92/#93» ② docstring :10 ③ 커버 = import 경로만(재수출 경유 catch 미커버 — 실물 spring `notification/driving_layer/open_host_service/email_notice/email_notice_service.py:40 except (EmailNoticeTransportError, EmailNoticeRenderingError)` · import :6 `send_email_notice_use_case` 경유 `__all__` :24) ④ registry #? context-isolation. 미커버분은 코드에서만 보이므로 discipline-reviewer 병기가 더 정확 — 기본값 표(architecture-ddd 설계 시점 = design-review-ddd) 준수라 오배선은 아님.

### H — R-3181 rev3 (`s003-0/b3`)
- 문면 = rv3-B 대체 문면 byte 동일 · amendment rev3 · prefLabel 갱신 ✓. «error inventory» — Coordinator :117 «내용 없는 골격 파일(빈 모듈)은 inventory에서 제외한다(골격 실현 의무 #114로 만든 빈 칸은 내용이 생긴 뒤부터 검사한다 …)» 의 inventory 는 `--project-code-error-module`/`--project-preserve-error-module` 목록 = 오류 모듈 inventory → 어휘 정확 · R-0319 prefLabel «내용 없는 골격 파일(빈 모듈)은 inventory 에서 제외» ✓.
- 현장 보고 H 행 «다른 검사기 #256/#351/#114 와 정렬» 실물: `skeleton_placeholder` 사용처 = error-centralization(#114) · domain-model(#256) · port-adapter-pairing :643(#351 orphan) ✓.

## 4. 저작 규약 · 문서 정합

- **블록 서수·order**: python §4.4 b1·b2 → **b3 = order 3**(말미) · houserules §4 b6 → **b7 = order 7**(말미 · §4.1 절 앞) — 밀림 0 · IRI = order ✓. 확장 4(b24·ddd b3·ninja b18·houserules-final b3) 는 신설 0.
- **공백 소유(§13)**: b24 말미 `\n\n` 유지 · ddd b3 `\n\n` 유지 · houserules-final b3 `\n`(불릿 목록 중간) 유지 · ninja b18 `\n\n` 유지 · 신설 b3/b7 `\n\n` · 선행 b2(펜스 «```\n\n»)·b6(`\n\n`) 무변 — 문단 블록이라 이관 불요(f2d4df0 `\n\n`→`\n` 은 불릿 연속형) ✓. 렌더 라운드트립 = render-sync red 0.
- **Expression 형**: rev1 5 = `prov:specializationOf` + `djr:revision 1`(기존 R-0719@2026-08-22 동형) · rev N 5 = + `prov:wasRevisionOf <직전>` + `djr:revisionKind djr:revision-amendment` · `currentExpression` 갱신 · 이전 표현 보존 ✓. prefLabel 10건 갱신 ✓(길이는 R-3427 선례 범위).
- **ISSUED**: 5행 `R-NNNN\tYYYY-MM-DD\trules/<doc>.ttl`(`sed -n l` 로 TAB 확인) · 3445 다음 결번 0 · append 순 = D·E·E·G·F-2(문서 간 순서 규약 없음 · §5) · 같은 커밋 rules 등장 ✓ · issued-check 0.
- **LEDGER**: 8행 9필드 · `rebaseline:2026-09-04 현장 보고 수리 2 — …` · doc_key/section_key 8 = 렌더 8 ✓ · ledger-check 0. 사유 결손: Δ11 «R-3427 amendment — 독법 ⓑ 명세가 형식 red 가 되는 실효 변화 병기» 미이행(행 = «경계 3분류·잎→port 행») → append-only 라 ④ 에 기록(MINOR-2).
- **계수**: Expression 3558→3568(+10 = 신설 5 + rev 5) · Norm/Work 3454→3459 · **Block 2901→2903(+2)** — Δ13 «+3» 은 Δ1(«Block +3(2,904)» — G 를 §5.3 새 블록으로 전제)의 잔재이고 Δ2 가 G 를 확장으로 바꿨으므로 ④ «+2 정정» 이 맞다 · q4 3445→3450 ✓ · hierarchy --with-golden 불일치 0.
- **문장 등장 순 = 채번 순**: b7 텍스트 1~4 → R-3447 · 5~6 → R-3448(canon 이 `statesNorm` 목적어를 IRI 순 정렬하므로 그래프엔 순서가 없고 텍스트 대응표만 남는다) — 계획 Δ3 에 있으나 **④ 검수표 미기록**(MINOR-2 b).
- **§16 4원 근거**: ④ 에 «wiring 7(…)» 배선 열거만 · R-3447→public-surface(① «#645 가 차단» ② docstring #645 등재 ③ 시그니처 bare 커버·ⓓ 후보 미커버 ④ registry #11) · R-3449→context-isolation(위 G) 근거 0 → MINOR-2(a).
- **문서 정합**(421782e): 현장 보고 상태 블록 D(n=2/2·효과 n=1 ✓)·E(spring 10(8)·kkebi 14(10) ✓ · «`object` 대체 strict 통과 실측» ✓)·G(0/7·5레인·블록 보유 2 ✓ · 발주측 빚 1 ✓ — 실물 `email_notice_service.py:40` 재수출 경유 확인)·H(5행/12행·13:42·4레인 ✓ · #256/#351/#114 ✓) 일치. **F 행 «정적 대조 spring 27 BC·kkebi 12 BC 불일치 0» 오기** — 증거 F :8 «spring 16 BC · kkebi 12 BC» · :44 «spring 다른 15 BC 불일치 0» → 27 = 15+12 합계 → «27/28 BC 불일치 0(spring 15·kkebi 12 · 리딩 585c9c6 만 1)»(MINOR-3). 정정 추기 ①②③⑤⑥ 실측 일치(⑤ «6행 블록» 원문 :263 ✓) · **④ «ANN401(별표 인자 면제·`models/**` 제외)» 의 `models/**` 는 증거 DE(:64 ruff per-file = `**/{test,tests}/**` 만)·원문 :220 어디에도 없음** → 삭제 또는 출처 병기(MINOR-3). 로드맵 §1 17행·R-18(n=2·효과 n=1)·R-19(10/14)·R-20 추기(R-3156 면제 존치)·§4(v2.17.17 후보 = 승격+수리 1+수리 2)·§8 — 현장 보고와 상호 모순 없음 ✓. ledger 이월 행(⑪⑫ 종결 → R-3427 rev4+R-3449 · #219/#635+R-3181 rev3) ✓ · 조감도 09-04 행 ✓. 발주측 빚 기록 위치 = 현장 보고 G 행 + 루브릭 ④(계획 Δ2 그대로) — 발주자가 읽는 문서의 상태 블록이라 적절 ✓ (MAJOR-1 수정 시 G 행은 경로를 인용하지 않아 무접촉).
- ④ «codex 손 미러 3(Coordinator 108·150 …)» — 108 은 Claude `commands/dddjango.md` 행, codex `SKILL.md` 는 125·150 → 오기(MINOR-2).

## 5. 검증 도구 재실행(2026-09-04 · HEAD 421782e)

| 도구 | 결과 |
|---|---|
| `ontology_gate.py` | 90파일 — green 90 · red 0 |
| `ontology_render_sync.py` | 그래프 소유 절 540 — red 0 · warn 0 · SyncDebt 0 |
| `ontology_structural_check.py` | 7종 조인·순서·datatype·alias·pathGlob 전부 성립 |
| `ontology_hierarchy_check.py --with-golden` | 셰이프 9종 — 불일치 0 |
| `ontology_issued_check.py` / `ontology_ledger_check.py` | 위반 0 / 위반 0 |
| `corpus_mirror_sync.py --check` | 11/11 in-sync |
| `query_golden_check.py` | 질의 7종 양성·음성 전건 일치 |
| `cmp` rulepack.json ×2 | byte 동일 |

## 6. 반드시 고칠 것(⑥ 전)

1. **MAJOR-1** R-3449 b3 불릿의 칸 경로를 `domain_layer/<aggregate>/exception/<exception>.py`(#92/#95 허용 칸) 로 교체(위 대체 문면) + prefLabel · ttl in-place → 렌더 → LEDGER → 소스 미러 → `corpus_mirror_sync --write`. rv3-B 의 «48행» 오독은 이 파일이 정정.
2. **MINOR-1** R-3427 rev4 «(실행기 사각 S3)» → «(pre-gate 보고 헤더의 사각 목록 S3)» — in-place + 렌더 + codex architect SKILL.md.
3. **MINOR-2** 루브릭 ④ 에 1행 추가: 4원 근거 2건 · b7 문장→Work 대응 · R-3450 모델링 선택(불릿 Work — R-2155 amendment 비채택 사유) · R-3427 amendment 실효 변화(독법 ⓑ 명세 소급 형식 red 2) · «Coordinator 108·150» → «Claude 108·133 / codex 125·150».
4. **MINOR-3** 현장 보고 F 행 «spring 27 BC» → «27/28 BC(spring 15·kkebi 12)» · 정정 추기 ④ «`models/**` 제외» 삭제(또는 출처).
5. (병기) MINOR-4 R-3449 delegatedTo 에 discipline-reviewer 추가 여부 — ⑥ 재량.

## 7. 미확인

- MAJOR-1 대체 문면의 «자기 BC 의 예외 = domain 예외» 가 architecture-ddd 의 의미론(응용 실패를 도메인 예외로 표현)과 어긋나는지는 설계 판단 — 코퍼스(exception-map «도메인→published» · #92/#95 · 실전 레인 accounts) 는 전부 그 모델이나, 응용 층 전용 예외 칸을 트리에 신설하는 대안은 트리 개정(tree-revision-spec·tree_mirror_check) 범위라 본 배치 밖.
- `check-context-isolation` 의 registry 번호(4원 ④) 는 rulepack `by_checker` 편입으로만 확인 — Coordinator registry 목록의 행 번호 대조는 생략.
- kkebi 에 notification BC 동형(재수출 경유 catch) 이 있는지는 미조사(발주측 빚은 spring 1건 확인).

Serena: skipped — 읽기 전용 규범 리뷰(코드 편집 없음)라 기본 도구로 충분.
