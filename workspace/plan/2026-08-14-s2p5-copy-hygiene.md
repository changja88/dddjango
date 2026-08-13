# S2.5 — 문면 위생 사이클 (한 릴리즈 v2.7.0 후보 · 2026-08-14)

**상태**: v1 초안 → 정독 스윕·기계 스캔 → 후보 처분(v2) → 적대 리뷰 4렌즈 → 반영 → 구현 → 검증 → 릴리즈.
**입력**: 마스터 로드맵 S2.5 행 · s2-speed-v1.md §2 L9 · 라운드 2~3 STOP 원인 분석(전부 «모순» 축 — 모순 1건≈왕복 30분~1h).
**불변**: eval v5 FROZEN(backstop 675 판정 무변) · 검출 리터럴·앵커 문면 보존(P1″ 전례) · **전면 재작성 스윕 금지 — 문장 단위 최소 수정만** · 성능>속도.

## §0 왜 지금

최근 STOP·오독의 진범이 코드가 아니라 **문면**이었다: 라운드 2′ spec §3.3 명명 충돌 · 라운드 3 #210↔#95 문면 충돌(레인 B G2) · «#15» 번호 공간 혼동(registry 순번 vs 규칙 번호 — 결과지 실증). 코퍼스는 사람이 아니라 **AI가 읽는다** — 판정 가능성·참조 자립·한 개념 한 이름이 산출 품질로 직결된다(기실증 수리 패턴: P1′·F1·H1 = 산문→판정 물음). S3 첫 라운드 «전»에 기계화분을 우선한다(스트릭 보호).

## §1 대상 인벤토리

| 부류 | 파일 | 규모 | 비고 |
|---|---|---|---|
| ⓐ 정본(규칙 문면) | `dddjango/skills/discipline-houserules/references/final.md` | 242행 | 트리 값·규칙 #N 의 배포 정본 |
| 지식 코퍼스 | 나머지 10 스킬 `references/final.md` | ~16.4k행 | 책 기반 지식 + 의사결정 주석 |
| 포인터 | `SKILL.md` 11종 | ~630행 | 값 복제 금지 계약 |
| 파이프라인 | `dddjango/agents/*.md` 7종 · `dddjango/commands/dddjango.md` | 682행 | 에이전트가 통째로 받는 지시문 |
| 검사기 발화 | `dddjango/scripts/check-*.py` 27종의 진단 문면 | — | 세션이 읽고 행동하는 문장 |
| 미러 계약 | `workspace/reference/`(소스) ≡ 배포 ≡ `codex-dddjango/`(쌍둥이) | — | 수정은 배포 → `corpus_mirror_sync --write` |

**대상 밖**: 정본 HTML(mkrev2 재생성만) · `workspace/design` 명세(= spec_lint 기왕 소유 — 이번 주어는 «배포 코퍼스») · eval rubric(FROZEN) · codex 쌍둥이 SKILL(대응표 관례 따라 동기만).

## §2 세 렌즈 설계

### 렌즈 1 — 모순 (기계화 = 교차 fixture 스캔)

각 fixture 레인의 `good/` 은 그 검사기 기준 **정본 모양**이다. 이것을 자기 검사기만이 아니라 **27종 전부**에 돌리면 「한 검사기가 요구한 모양을 다른 검사기가 금지」하는 쌍이 기계로 드러난다 — #210↔#95 부류(SD-6/NJ-7 가 요구한 direct catch 를 #210 이 금지)의 상류 검출.

- 도구: `workspace/tools/checker_cross_matrix.py` 신설(메인테이너/빌드타임 — spec_lint 부류·registry 밖·fail-closed).
- 실행 계약: fixture 는 임시 사본(hermetic — fixture_matrix 전례)·AUTO 3종은 `--error-profile auto`·호출은 fixture 루트 TARGET.
- 잡음 처리(차분 원리): fixture 는 최소 재료라 타 검사기의 **정당한** red 가 난다(예: 다른 골격 칸 부재). 첫 실측에서 전 쌍을 삼분 처분(⑴ 모순 실재 ⑵ 정당 red — 사유와 함께 도구 안 EXPECTED 표에 고정 ⑶ 판정 불능 — fixture 최소성 탓이면 기록만). 이후 실행은 **기대 밖 red 만** 낸다(= 신규 모순 후보). EXPECTED 는 소스 안 표다 — 파일 로드 allowlist 금지(#591㉣ 는 런타임 검사기 규칙이지만 은폐 채널 방지 취지를 따른다: 사유 없는 행 금지).
- 산문 모순: 전수 스윕 비추(STOP 수확 기반 원칙 유지) — 단 이번 정독 스윕에서 후보가 나오면 판정 자 「**두 문면이 같은 자(같은 상황)에 다른 답을 주는가**」로 처분한다.

### 렌즈 2 — 중복

- 판정 자(08-11 «71건 걷기» 재사용): 「**한쪽만 위반인 코드를 제시할 수 있는가**」 — 제시 가능=서로 다른 규칙(존치) · 불가=중복(한쪽을 값에서 포인터로).
- **참조 자립과의 긴장을 먼저 가른다**: 코퍼스 문서는 서브에이전트에 «단독» 주입된다 — 문서 «간» 중복은 부분적으로 설계다(참조 자립). 걷는 대상은 두 부류뿐: ⑴ **같은 문서 안** 중복 ⑵ **값 소유 위반** — houserules 가 소유한 트리 값·규칙 문면을 타 문서가 «값»으로 복제(포인터가 아니라). 중복은 갈라지며 모순으로 자란다(#210 실례)가 걷기의 근거다.
- 기계 검출: corpus lint(§2 렌즈 3 도구와 합침)가 ⑴ 같은 파일 안 정규화-동일 규범 문장 쌍 ⑵ 타 문서의 트리 행 리터럴 복제 후보를 낸다. 산문 근사 중복(문서 간)은 기계화하지 않는다(오탐 과다·참조 자립과 충돌).

### 렌즈 3 — AI-독자

기계화분 — `workspace/tools/corpus_lint.py` 신설(한 도구에 렌즈 2 기계분 동거 · spec_lint 의 코퍼스 판):

| 검사 | 내용 | 씨앗·주의 |
|---|---|---|
| ㉠ 끊긴 참조 | 코퍼스·agents·commands·검사기 발화 안 «#N» 이 명세 생존 번호(538) 밖 · «D N» 이 생존 카드(57) 밖 | **«#N» 번호 공간 충돌 주의**: commands 의 «registry #15» 는 규칙 번호가 아니다 — 문맥 구분(«registry #» 접두는 제외) 필요. 이 충돌 자체가 별칭 혼용 후보(아래) |
| ㉡ 별칭 혼용 | 개명 완료 어휘의 옛 별칭 재등장 — DEAD_PHRASES(spec_lint ⑤) 씨앗: `dto_in/out`·`error_out`·`ErrorOut`·`presentation_layer`·`infra_layer`·`query_repository`·`published_service` 등 | 허용: 이관 절(§4)·개명 표식이 옛 이름을 «데이터»로 인용하는 자리(spec_lint allowlist 전례) |
| ㉢ 재량 낱말 | 규범 문장 안 «적절히·필요시·상황에 따라·알아서·유연하게» — 판정 물음 없는 재량 위임 | «등»은 오탐 과다 예상 — 검출 목록에서 제외(스윕이 본다) |

- red→green 실증: 신설 lint 는 **현행 코퍼스 실검출(red)→수정(green)** 이 1차 실증이고, 현행이 이미 clean 인 검사는 fixture 레인(`workspace/eval/fixtures/corpus_lint/{good,bad_rules}`)으로 red 를 실증해 fixture_matrix 에 checker_lint 전례대로 등재한다.
- 스윕분(에이전트 — 기계화 불가): ⑴ 판정 가능성(산문 권고 → 판정 물음 승격 후보) ⑵ 주어·예외 지역성(주어 유실 — 「못 견딘다」·「형제가 는다」 사고 전례) ⑶ 압축 내성(핵심 판정이 문서 뒤쪽에만 있는 경우) ⑷ 참조 자립(링크 너머 없이는 못 읽는 문장). 처분은 후보별 **최소 문면 수정** — 전면 재작성 금지.

## §3 절차

1. **정독 스윕**(병렬 에이전트): 모순 1·중복 1·AI-독자 3(코퍼스 분할) — 후보를 `파일:행·문면·판정 자 적용 결과`로 수집.
2. **기계 스캔 프로토타입**: 교차 fixture 스캔 + ㉠㉡㉢ 시범 실행 — 실측 잡음률로 검사 설계 확정.
3. **후보 통합·삼분 처분** → 수정 목록 v2 (이 문서 §5).
4. **적대 리뷰 4렌즈**(Goodhart·회귀·답습·동결) → 반영.
5. **구현**: corpus_lint·checker_cross_matrix 신설(red→green) · 코퍼스 최소 문면 수정 · `corpus_mirror_sync --write` · codex 쌍둥이 동기 · (필요시) 검사기 발화 문면 수정 — 판정 로직 무접촉.
6. **검증 세트**: fixture_matrix 전수(신설 레인 포함) · backstop 675/675 무변 · bc_registry_smoke · registry_gate_smoke · checker_lint · spec_lint · corpus_mirror_sync 0 · make release 세트 green.
7. 릴리즈 v2.7.0 · 설치본 양쪽 갱신 실측 · 로드맵·메모리 갱신.

## §4 위험·경계

- **판정 무변이 최상위 제약**: 검사기 «판정 로직»은 이번 사이클 무접촉이다 — 수정 허용 범위는 진단 «문면»과 코퍼스·문서뿐. 교차 스캔이 모순 실재를 내면 그 해소(검사기 수정)는 **별도 결정**으로 표면화한다(F-B 전례 — 이번 릴리즈에 동승할지는 발견의 크기로 판단).
- 코퍼스 수정이 검사기 검출 리터럴(±3줄 창 #규칙 인용 등 checker_lint 앵커)과 겹치면 **행 보존**을 우선한다(P1″ 전례).
- corpus_lint 는 배포 경계 밖(workspace/tools)·check- 접두 금지(corpus_mirror_sync 전례) — 런타임 게이트가 아니다.
- 효과 지표는 다음 라운드 STOP·오독 왕복 수다 — 이번 릴리즈 안에서 증명할 수 없는 것을 증명했다고 적지 않는다.

## §5 수정 목록 v2 (스윕 6종 + 기계 스캔 3종 실측 — 2026-08-14)

실측 요약: 교차 fixture 스캔 31레인×27종 → 비-0 372(가드 red 252·골격 red·최소성 red — **OWN-NONZERO 0**·코퍼스 모순 실재 0·fixture 예시 품질 쌍 소수) · 죽은 경로 23곳 · 끊긴 #N 실질 1(#377 주석) · 별칭(검사기 진단 «ErrorOut») 3곳 · 재량 낱말 규범 스코프 1곳 · 같은-문서 중복(펜스 제외) 1곳(ninja wire 계약 축자 반복 — 의도 존치).

**처분 기호**: A=채택(저위험·문장 단위) · B=채택하되 구현 시 정본(스펙·트리) 대조 후 문면 확정 · D=이월(기록만).

### 5.1 최중대 — 규범 예시가 V1·트리-밖 모양을 시연 (스윕 2종 수렴 — «예시는 산문보다 강한 지시»)

| # | 파일:행 | 내용 | 처분 |
|---|---|---|---|
| E1 | ninja final.md:239·253 | 예시 `driving_layer/registrar.py` → 정본 `driving_layer/api/api_router.py`(트리 9행·#107 — 함수명 `register_<bc>_api` 는 이미 맞음) · :291 «registrar(HTTP 등록)» 낱말도 `api_router.py` 로 | A |
| E2 | ninja final.md:277~289 | composition_root 예시의 import 3줄: `place_order/command/place_order_command`(트리 밖 겹)→`<use_case>_use_case.py` 진입 클래스 · `driven_layer.acl.…`→`adapter/anticorruption_layer/<bc>/…` · `driven_layer.repository.…`→`adapter/persistence/repository/…` (:293 산문과 같은 파일 안 자가 모순 해소) | A |
| E3 | ninja final.md:664~673 | `application_layer/reserve_order/dto/reserve_order_request.py` — `dto` 낱말 금지(#567)·4파일 계약 위반을 예시가 시연 → `reserve_order/reserve_order_command.py`(+클래스명 정렬) | A |
| E4 | ninja final.md:156~159·677~680 | `driving_layer.schema.order_in` vs `schema.schema_in` — 한 문서 두 이름·둘 다 트리 밖 → `driving_layer/api/<area>/schema/schema_in.py`(트리 13~15행) | A |
| E5 | web final.md:404 | `place_order.command.place_order_command import place_order` — 트리 밖 겹+함수형 유스케이스 → 4파일 계약 경로로 | B(예시 코드 최소 치환) |
| E6 | web final.md:290 | «`common/django/` 승격 검토» — 루트 common→framework repoint 잔재 → `framework/django/` | A |
| E7 | django final.md:1633 | outbox 디스패처 예시 `# management/commands/…` — #58 금지 칸 → 예시 앞 «이 플러그인 생성 코드의 자리는 `cron_job/` 칸(discipline-houserules §1)» 한 줄 앵커(코드 재작성 대신) | A |
| E8 | ddd final.md:361 | «승격된 enum은 `common/enum/`에 두며» — **금지 경로 생성을 지시하는 살아 있는 V1 주소** → 구체 주소 삭제·«배치는 discipline-houserules 표준 트리가 정한다» 위임(새 주소 발명 금지) | A |

### 5.2 모순 실재 — 문면 충돌 (판정 자: 같은 자에 다른 답)

| # | 파일:행 | 내용 | 처분 |
|---|---|---|---|
| C1 | django final.md:1593(§16.4)·:1286(§14.1 표) | «add된 테스트에 `TestCase`를 쓰고» ↔ 파이프라인 «새 테스트는 pytest 관용구»(commands Phase 2-1) → §16.4 문장을 pytest 등가(`django_db`/`transaction=True`)로 교정·§14.1 표 아래 «표는 Django 원생 지식 — 신규 add 는 pytest 관용구(등가 매핑)» 한 줄 | A |
| C2 | tdd final.md:204~209(§3.4 표)↔:599(§7.6) | 표 «새 기능 → Outside-In(런던)» ↔ «고전 학파 기본 불변» → 표 아래 «이 표는 배경 지식 — 이 저장소 기본은 고전 학파·Mock 은 외부 의존성 격리만(§7.6)» 한 줄 | A |
| C3 | houserules:212(#429 «조건부다»)↔:21(#491 «조건부는 없다») | 낱말 정면 충돌 — #491 주어(application/** 칸)와 <project>/ 관할(#429) 관계를 한 구로 명시 | B(스펙 #429·#491 문면 대조 후) |
| C4 | houserules:24(touched=골격 실현)↔:230(touched≠작업 대상) | 같은 낱말 두 정의 — :24 에 «touched = G0 스코프의 그 BC(§4 와 같은 자)» 한 구 | B(스펙 대조) |

### 5.3 죽은 참조·별칭·재량 낱말 (기계 검출분 — corpus_lint 가 상시 감시)

| # | 대상 | 내용 | 처분 |
|---|---|---|---|
| R1 | final.md 6파일 23곳 | `workspace/reference/<skill>/reference/final.md` — 설치본에 없는 저작 시절 경로 → 스킬명 표기(«`implementation-test` §7») | A |
| R2 | check-error-centralization.py 3곳(:2654·:3042·:4503) | 진단 문면 «common/BC ErrorOut» → «FrameworkErrorSchema/<Bc>ErrorSchema»(개명 완료 어휘 — 검출 튜플의 "ErrorOut" 리터럴은 보존) | A |
| R3 | check-port-adapter-pairing.py:403 | 주석 범위 «#319~#377» — #377 은 죽은 번호 → 실제 인용 규칙 범위로 교정 | A |
| R4 | commands:66·100·132·134 | registry 순번 무접두 «#16»·«#15·#6·#2·#5·#3» — 규칙 번호 공간과 충돌(라운드 3 «#15» 혼동 실증) → 전부 «registry #N» 접두 | A |
| R5 | commands:80 | «discipline reviewer를 적절히 다시 호출해» — 재량 낱말 → «적절히» 삭제(조건 «바뀌면»이 이미 판정) | A |
| R6 | api final.md:547·db final.md:402 | «P1a» — 무정의 결정 태그로 참조 단절 → 태그 삭제(«§13.3» 지시는 유지) | A |
| R7 | ddd final.md:636 | 옛 절 번호 4곳(§0-1·§0-3·«§2 컨텍스트 간 통신»·§1.1)+옛 칸 열거(«repository/acl/adapter 의미군») → 현행 houserules 절(§0 #486~#492·§1·§4)로 재지정·열거는 «고정·재등장 칸 전부(§1)» 포인터로 | B(문단 정밀 재지정) |
| R8 | agents 4곳 | design-architect:64·design-review-ddd:28 «§632-(2)»→«#632(정본 명세 규칙 번호)» · coder:39 «§7.1»→«`implementation-test` §7.1» · discipline-reviewer:71 «§20.5» 동일 | A |
| R9 | django final.md:289 등 | «그 `reference/final.md`»(단수) → `references/final.md` — 같은 오기 전수 | A |

### 5.4 AI-독자 정밀 수리 (확실 등급 위주 — 문장 단위)

| # | 파일:행 | 내용 | 처분 |
|---|---|---|---|
| P1 | commands:161↔133 | 엣지 절이 «exit 1 무조건 차단»만 말해 68행 떨어진 DYNAMIC…PROOF 예외가 유실 → :161 에 예외 한 문장 | A |
| P2 | commands:66 | 루트 TARGET 실측 → 대상 BC 빚만 남기는 필터 문장 부재 → «위반 경로가 `application/<대상 bc>/` 안인 진단만 빚 목록» 한 문장 | A |
| P3 | commands:67 | «G0 배너 전에 ls .dddjango/» 문장이 step 4 말미 → 첫 문장으로 이동 | A |
| P4 | commands:95 | «coder 파견 전» ↔ acceptance 선행 모호 → «Phase 2 의 첫 서브에이전트(acceptance-tester 포함) 파견 전» | A |
| P5 | coder.md:58 | «정해진 시도» 무정의 → «(Coordinator 입력의 시도 예산 — 없으면 2회: 수렴 회로 «반송 2회» 와 같은 자)» | B(적대 리뷰 확인) |
| P6 | tdd:416 | G1/G1′/Phase 2 미정의 → 괄호 정의 한 줄 | A |
| P7 | cleancode:994 | 라우팅 목적지 미명시 → «(architecture-db·architecture-api·architecture-ddd 스킬)» | A |
| P8 | python:1208 | Literal 재량 술어가 분업 판정보다 앞 → «(분업 판정은 아래 PEP 586 항)» 종속 구 | A |
| P9 | python:2488 | «둘 중 하나만 유지» 방향 미지정 → «독스트링 쪽 타입 서술을 지운다(어노테이션은 항상 유지)» | A |
| P10 | test:2134 | 입장 심사 주어 유실 → «입장 심사는 소유자(§5.5)에게 — 여기서는 정리만» 주어 복원 | A |
| P11 | ddd:1667 | 간소화 구조 허용 문장에 «[A] 원전 이론 — 생성 코드 비적용» 단서 선행 | A |
| P12 | ddd:1014 | «입력을 …Request로» 주석 — 현행 명명(<use_case>_command.py 4파일 계약)과 정합 여부 대조 후 정정 | B(스펙·트리 대조) |
| P13 | api:231 | G1·G2·12-slot·STOP 미정의 → 첫 등장에 괄호 정의 한 줄 | A |
| P14 | houserules:196 | «#7 이 연다» 내용 미상 → 반 문장 풀이 | B(스펙 #7 대조) |
| P15 | tdd·cleancode·test·db 나머지 [후보] 등급 | (weaken 귀속·history-only 처분·.dddjango 정의·§15.1 판정 포인터·db:301 «BC(앱)» 등) — 확실성·위험 대비 선별 | B/D(적대 리뷰에서 확정) |

### 5.5 도구 신설 (red→green)

| 도구 | 검사 | red 실측 → green |
|---|---|---|
| `workspace/tools/corpus_lint.py` 신설 | ① 죽은 저장소 경로(`workspace/reference`) 0 ② 끊긴 #N·D카드(«registry #»·«의사결정 #»·`](#`앵커 제외·스크립트 포함) ③ 별칭(DEAD 어휘 — 문서는 데이터-인용 allow·스크립트는 «긴 문자열(진단)»만) ④ 재량 낱말(규범 4부류 한정) ⑤ 같은-문서 중복(펜스 제외·의도 반복 in-source allow) | ①23→0 ②1→0 ③3→0 ④1→0 ⑤1→allow(사유 기록) — fail-closed·exit 0/2/3 (spec_lint 계약 동형) |
| `workspace/tools/checker_cross_matrix.py` 신설 | 31 good 레인 × 27종 전수 — (레인×검사기)→규칙 ID 집합을 in-source EXPECTED 와 대조 · 기대 밖 red = 신규 모순 후보 exit 2 | 첫 census 를 EXPECTED 로 고정(가드/골격/최소성 분류 사유 병기) — 이후 검사기 개정이 확립 exemplar 를 새로 거부하면 발화(#210↔#95 부류 상류 검출) |
| Makefile [2] 검증 세트 | corpus_lint·checker_cross_matrix 편입(릴리즈 영구 게이트) | — |
| fixture 레인 | `corpus_lint` 레인(good/bad_rules — --root 인자로 미니 코퍼스) fixture_matrix 등재(checker_lint 전례) | red→green 영구 고정 |

### 5.6 의도적 비포함·이월

⑴ commands·agents 문서 «간» 중복 걷기(cmd:47↔172·85↔147·133↔161 등) — 아직 문면 일치 상태라 위험 낮고, 걷기는 파이프라인 문서 대수술이라 별도 사이클로(기록만) ⑵ houserules:219 «명명 규약 편입» — 매핑표 순서의 기왕 트랙(이번에 안 당김·ddd:1014 는 P12 로 정합만) ⑶ fixture 내부 품질 수리(clock.py #561·notify #396·#359 등) — 교차 스캔 EXPECTED 에 사유와 함께 기록·판정 무변 우선 ⑷ #292 응용 예외 홈(기왕 이월 유지) ⑸ 지식 코퍼스의 책-요약 산문 전면 개정 금지(원칙).

### 5.7 모순 렌즈 스윕 결과 (도착 — 확실 11·후보 8 · 검사기 문면 교차 실측 동반)

E1~E4·C1 과 중복 확인된 것 외 신규분:

| # | 파일:행 ↔ 반대 문면 | 내용 | 처분 |
|---|---|---|---|
| M3′ | check-composition-root.py:1849 | 검사기 메시지 «`build_<usecase>_command()` 팩토리» — 어휘 반전(#635: 실행체는 use_case) → «`build_<use_case>_use_case()`» (R2 와 같은 부류 — 진단 문면만) | A |
| M6 | ddd:664 ↔ #546·D50 | «단순 케이스는 복수 애그리거트 수정 용인» — 생성 코드에선 G2 exit 2 → «생성 코드는 「한 트랜잭션=애그리거트 하나」(D50)가 정본 — 이 용인은 배경 이론» 한 문장 | A |
| M7 | ddd:1101(·:1174 예시) ↔ #539~#541 | «커밋 직전 또는 직후 디스패치» — 커밋 전 발행은 위반 → «생성 코드는 `uow.after_commit` 한 경로 — 직전 디스패치는 배경 이론» 한정 | A |
| M8 | django:1569 ↔ #200 | 좋은 예 `transaction.on_commit(…)` 직접 호출 — 응용 계층에선 위반 → «표준 트리 응용 계층은 `uow.after_commit`(#200) — 이 형태는 평면 Django» 주석 | A |
| M9 | discipline-reviewer.md:59 ↔ #114·#488 | «오류 module 을 미리 만들지 않는다» ↔ 빈 `bc_error_schema.py` 는 고정 칸 → «선언(`<Bc>ErrorCode`/`<Bc>ErrorSchema`)을 미리 만들지 않는다(빈 파일 자체는 #114·#488 고정 칸)» | A |
| M10 | ddd:1187·db:412·425·django:1597 ↔ #529·#530·#626 | outbox/브로커 채택 조건 «유실 불허→outbox» ↔ «in-repo 소비자의 유실 불허는 cron_job→OHS·external 은 별도 배포 단위만» → 채택 조건에 그 한정 한 문장씩 | B(세 곳 문면 확정 시 #529·#626 문면 대조) |
| M4′ | django:365(§4.1 «모델에 판정»)·SKILL:22 ↔ discipline-reviewer:76 | C1 과 같은 부류(fat model 예시가 blocker 모양) → §4.1 에 §16.2 동형 한정 문장+SKILL:22 동반 한정 | A |
| M13 | web:294 ↔ ninja §6.2 | «ninja §6.2 대칭» 인용이 실제 반대 규범을 가리킴 → «(HTML 경계 한정 — ninja §6.2 는 반대로 concrete catch 유지)» 정정 | A |
| M14 | api:572 ↔ design-architect:59 | 멱등 «필수» ↔ 파이프라인 «기본 미적용·G0/G1 결정» → «(파이프라인: 채택은 사용자 결정)» 병기 | A |
| M15 | django:869(§9.1 signal 예시) ↔ #89·#90·#502 | BC 간 signal 배선 예시 → «BC 경계 간은 published_event/event_subscription 소유 — 이 예는 같은 BC 내부 한정» 각주 | A |
| M16 | django:888(§9.2 save() 이메일 예시) ↔ §16.4 | 커밋 전 동기 발송 모양 → on_commit 정렬 주석 | A |
| M18 | django:182 | «또는 기존 관례 프로젝트: TextChoices 자체 선언» — «기존 배치는 빚» 결정(08-12)과 충돌 → 그 구 삭제 | A |
| M12 | check-api-error-controller-contract.py:6691(#62 메시지) ↔ concrete-only 규범 | 폴백 처방 «base 단위 catch»가 code-json controller 에선 blocker 모양 → 메시지에 스코프 병기 | B |
| M19 | python:622·cleancode:1562 ↔ #453·#454 | «None 대신 예외» ↔ «부재는 답» — OHS·failed-Result carve-out 한 줄 | B |
| M20 | check-event-publish.py:11 | 헤더 요약행이 #96 의 #95 예외를 생략(진단 문면 :236 은 정상) — 요약행 정리 | A |

**모순 아님 판정 기록**(거짓 안심 방지): §6.1·§3.1 레이아웃 절(중재 각주 기존재)·api §5.4↔§6·«8행 미기재» 규율·web §11 SQLSTATE(표면 분리)·pytest 러너 서술 3곳(같은 답)·#210↔#95(v2.6.0 에서 종결 실측).

## §6 적대 리뷰 4렌즈 반영 (v2→v3 · 2026-08-14 — 성공 21·기각 19 전량 처분)

**Command-어휘 축 대응표(답습 A3 — 흩어진 교정 값의 단일 귀속)**: 입력 자료=`<use_case>_command.py` 의 `<UseCase>Command` · 실행=`<use_case>_use_case.py` 의 `<UseCase>UseCase.execute`(#635) · 팩토리=`build_<use_case>()`(#85·#134 — 스펙·검사기 :1616 계열. 정본 HTML 예시·v5 fixture 는 장형 `build_<x>_use_case()` — **정본 내 두 표기 실재는 후속 결정으로 기록**, 판정은 `startswith("build_")` 라 무변) · `…Request/…Response`=OHS contract 전용(#484). P12·M3′·E2·E5·E9 전부 이 축.

| 렌즈 | 반영 |
|---|---|
| Goodhart | G1: R4 를 grep 전수로(+:106) + **commands 머리에 번호 공간 규약 한 문장**(«registry 순번은 항상 `registry #N`·무접두 #N 은 규칙 번호») — 기계 판별 불가는 정직 기록 · G2: cross_matrix EXPECTED **양방향 동등 + 건수** 대조(결손=«갱신 필요» 발화) · G3: EXPECTED 사유=닫힌 enum(가드-red\|골격-부재\|최소성\|모순-이월)·allow/EXPECTED diff 는 릴리즈 보고 표면화 · G4: 별칭 allow 는 문맥 휴리스틱이 아니라 **위치 기반 in-source allowlist**(토큰→(파일·앵커 문면·기대 건수) — DEAD_PHRASES 방식) · G5: 접두는 제외가 아니라 **자기 명부 검증**(registry 1..27·의사결정=파일 내 `[의사결정 #N]` 선언 집합·D=생존 57) · G6: self-test 에 **목록-밖 변형** 필수(단수 `reference/final.md`·비-reference 죽은 경로·→-줄 별칭·3회 중복) + ① 씨앗에 단수형 추가 · G7: ㉢=«트립와이어(부류 검출기 아님)» 명기·동의어 3(알맞게·적당히·재량껏) 추가·«규범 4부류»=houserules final.md+SKILL.md 11+agents+commands 로 정의 기입 · G8: ⑤ allowlist 에 기대 건수 · G9: 스크립트 별칭=문자열 상수 ≥20자만·주석 제외(검출-자리 주석의 옛 이름 인용은 checker_lint 허용 계약 — 사유 기록) |
| 회귀 | **M3′ 치환어=`build_<use_case>()`**(스펙 #85·#134·:1616 실측 — v2 제안어는 신조어였다) + ninja:274 산문을 E 축에 편입 · **fixture 레인 폐기→corpus_lint 내장 self-test 로 대체**(스펙 의존이 hermetic 을 깨고 fixture_matrix 특례 확장 필요 — self-test 는 매 호출 선행·fail-closed·G6 요구 동시 충족·fixture_matrix 무접촉) · P2 에 «미룰 수 없음 진단은 경로 무관 잔류» 예외 구 · P5 는 숫자 발명 금지 — «시도 예산은 Coordinator 입력이 정한다(없으면 추가 시도 없이 멈추고 보고)»(하드 숫자는 request 재료 소유 — 기왕 결정) · M12=병기(추가)만·기존 문구 보존+«`[#N]` 진단 문면 수정은 활성 빚 파일 대조 동반» 규약 §4 기입 · R1 단서: ①스캔=배포본 한정·preamble blockquote 형태 보존 · R9 는 R1 후행 · M4′/M9 에 codex 쌍둥이 대응 파일 명기 · cross_matrix 비용 기각(실측 ≈70초·결정적) — 편입 유지·레인당 사본 1회 |
| 답습 | **E9 신설**: ninja §2.2 예시 블록(:143~190)+§2.3 산문·본문(:274·:283~292)+:657·:674 — Command-축 전수 교정(E2 의 «import 3줄» 한정을 대체) · E2 표기 `<other_bounded_context>`(트리 98행 축자) · **corpus_lint ⑥ 신설**: final.md 코드 예시의 `application/...` 경로꼴 ↔ standard_tree 자리표시자 대조(red 실증=A1 — 한계 정직 기록: 자리표시자-형태 우연 일치(:147 류)는 못 잡음·별도 수기) · ① 을 `workspace/` 접두로 확장(md 코퍼스 한정) · E8 에 «published service»(공백형) 1치환+㉡ 씨앗 등재 · R4+=:106(+codex 쌍둥이 :129) · E7 범위를 :1630 산문까지 · §5.6⑴ 에 «133↔161 은 P1 후 두 사본 동기 의무 승계» 기입 |
| 동결·정본 | M3′ 두-표기 실재 → 위 대응표의 결정 기록으로 종결(HTML 예시·fixture 장형은 후속 항목) · **R2 에 «선두 토큰 `DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED`·`[#N]` 접두 보존» 명문화**(backstop fragment 64곳·commands 예외 식별자) · C4 괄호=«승인 스코프의 BC(명세가 골격 실현을 지시한 데이터소스 BC 포함)»+**coder.md:34 동반 수정** · M20 목표 문면=#96 열거 축자(«애그리거트·엔티티·리포지토리 선언·도메인 이벤트·포트 선언» — #95 허용분 오포함 제거)·`#96`·카운트 보존 · C3·P12·P14·M10(+#603 동반 인용)·M12 조건부 — 제안 문면 전부 정본 실측 통과 · FROZEN·수정 권한·미러 계약 침범 0 실측 |

**구현 순서**: 도구 2종 먼저(수용 계기로 씀 — red 기준선 실측) → 코퍼스·스크립트 수정 → corpus_lint green 실증 → `corpus_mirror_sync --write` → 쌍둥이(scripts byte-copy·SKILL/agents 대응) → 검증 세트 → 릴리즈 v2.7.0.

## §7 구현·검증 결과 (2026-08-14)

**도구**: `workspace/tools/corpus_lint.py` 신설 — 검사 ①~⑥ + 내장 self-test(합성 red/green·목록-밖 변형 G6 실증·fail-closed exit 3). **red 43 → green 0 실측**: ① 죽은 경로 23 → 0(스킬명 표기 치환) · ② 끊긴 번호 3 → 0(commands «#6» 2곳 registry 접두·#377 주석 #376 교정) · ③ 별칭 6 → 0(«ErrorOut» 진단 3·published service 공백형·단수 오기 2) · ④ 재량 1 → 0 · ⑥ 트리-밖 예시 9 → 0. 구현 중 도구 결함 3 자가 수정(allow 카운터 토큰별 분리·⑥ 산문 슬래시-열거 필터·의사결정 선언 볼드형). «registry #N 리스트 잇기»(`registry #2·#15·#6`)를 번호 공간 규약·lint 어휘 규칙으로 명문화. `workspace/tools/checker_cross_matrix.py` 신설 — census 372행(--emit-expected 로 생성·삼분 자동 분류: 가드-red 252·골격-부재·최소성) EXPECTED 양방향 동등+건수 대조 green. Makefile [2] 검증 세트에 2종 편입.

**코퍼스·스크립트 수정**: §5·§6·§5.7 목록 전부 반영 — 검사기 5종은 진단 문면만(fixture 판정 무변 12/12 표적 실측) · commands 14치환(번호 공간 규약 문단 신설 포함) · agents 9치환 · houserules 4치환 · final.md 8파일(배치 4종 병렬 — ninja 예시 전체 Command-축 정렬(+query 계열 잔여 7치환 직접)·ddd 15곳·django/web 13곳+예외 import 6-성분 2곳·tdd/cc/py/test 25곳). `corpus_mirror_sync --write` 로 소스·codex final.md 11/11 in-sync · scripts 쌍둥이 byte-copy diff 0 · 쌍둥이 SKILL/agents 는 대응 이식(별도 에이전트).

**검증 세트(전부 green · 실측)**: corpus_mirror_sync 11/11 · corpus_lint 0 · checker_cross_matrix 372=372 차이 0 · spec_lint 규칙 538 위반 0 · checker_lint 27종 0 · tree_mirror in-sync(140행) · reverse_coverage 0/0 · **fixture_matrix 92/92** · registry_gate_smoke 6/6 · bc_registry_smoke ✓ · **backstop 675/675 무변**(checker_mismatches 0).
