# A4 — 규칙 주입 경로 실사 (그라운딩 현황)

P0 센서스 · 구조 실사 · 2026-08-18
조사 대상: `dddjango/commands/dddjango.md`(177행) + `dddjango/agents/*.md` 7종 전부(실측 근거는 각 파일 원문).
보조 확인: `dddjango/skills/*/SKILL.md` 11종(45~83행), `skills/*/references/final.md` 11종(242~2,754행·총 16,069행), `dddjango/scripts/*`(checker 27종 + `registry_gate.py`·`checker_registry.py`·`business_vocab.py` 등).

---

## 1. 규칙이 에이전트 컨텍스트에 도달하는 경로 실측

### 1.1 경로 A — 에이전트 frontmatter `skills:` 상시 로드 (27슬롯)

7개 에이전트가 각자 frontmatter에 스킬 목록을 선언하고, 스폰 시 그 SKILL.md 전문이 컨텍스트에 로드된다. 작업 내용과 무관하게 **항상 전부** 로드되므로 이 층은 통짜다.

| 에이전트 | 스킬 수 | 목록 |
|---|---|---|
| design-architect | 5 | architecture-ddd · architecture-api · architecture-db · discipline-houserules · discipline-tdd |
| design-review-ddd | 1 | architecture-ddd |
| design-review-api | 2 | architecture-api · discipline-tdd |
| design-review-db | 2 | architecture-db · discipline-tdd |
| acceptance-tester | 5 | discipline-tdd · implementation-test · architecture-api · architecture-ddd · implementation-django-ninja |
| coder | 8 | implementation-django · implementation-django-ninja · implementation-django-web · implementation-python · discipline-tdd · implementation-test · discipline-cleancode · discipline-houserules |
| discipline-reviewer | 4 | discipline-cleancode · discipline-tdd · implementation-test · discipline-houserules |
| **합계** | **27** | |

단 실측상 이 통짜의 «부피»는 작다. 스킬은 2층 구조다:

- **SKILL.md = 라우터** (45~83행). 값을 두지 않고 «언제 어떻게 읽나»만 담는다. discipline-houserules SKILL.md가 명문화: 「트리·칸·규칙의 «값»은 전부 `references/final.md`가 단일 출처로 소유하고, 이 SKILL.md는 «언제 어떻게 읽나»만 소유한다」.
- **references/final.md = 본체** (242~2,754행). 자동 로드되지 않는다 — 에이전트가 Read로 실독해야 한다. 코디네이터가 Phase 1 리뷰어 입력에 「플러그인 설치 루트 절대 경로를 함께 준다(로드 스킬 references 실독용 · 2026-08-17)」을 넣는 것이 그 증거다(경로 없이는 references를 못 연다).

즉 상시 통짜 로드는 «라우터 27장»이고, 규칙 본체 16,069행은 온디맨드 층에 있다.

### 1.2 경로 B — § 지정 참조 지시 (본문 내 수십 곳)

커맨드·에이전트 본문이 로드 스킬(또는 그 references)의 **특정 절**을 번지수로 가리켜 읽게 한다. 대표 실측:

- design-architect: 「`discipline-houserules` `references/final.md`를 읽고 §0 불변식과 §1 표준 트리(140행)의 고정·재등장 칸을 명세에 그대로 박는다」, `architecture-db` §9.5·§9.6(Risky Write 8행), `architecture-api` §13, final.md §1 트리 22~32행(OHS)·39~44행(use_case 4파일)·§3 명명, `architecture-ddd` references §3.2 항-(1)·항-(2), `implementation-django` §10.4.
- coder: `implementation-django-ninja` §2.1(버전-핀)·§2.3(@api_controller), final.md §0·§1(골격 실현 의무 #488~#490), `implementation-test` §7.1, `implementation-django` §16.4·`architecture-db` §9.5(메커니즘 소유권), houserules SKILL §1.1.
- acceptance-tester: `implementation-django-ninja` §2.1, `implementation-test` 계약 테스트 패턴.
- discipline-reviewer: `discipline-tdd` §5.5, `implementation-test` §16.1·§15.4·§15.5·§20.5, `discipline-cleancode` §2.14·§15.1·§8.1·§8.5·§9.1, `implementation-django` §2.5·§10.4·§16.4, `architecture-ddd` §2.5·§3.2·§3.6·§3.7, `architecture-db` §9.5·§9.6, `implementation-django-web` §11, `architecture-api` §5.1, final.md §0~§4.
- 커맨드(Coordinator 자신): `implementation-django-ninja` §2.1(러너 준비), `discipline-houserules` references §4(brownfield=빚).

이 장치는 «어느 절이 걸리는가»의 선별을 문서 저작 시점에 정적으로 박아 둔 것이다 — 런타임에 diff를 보고 걸리는 절을 뽑아 주는 검색·추출기는 없다.

### 1.3 경로 C — Coordinator의 데이터 발췌 공급 (게이트·phase별)

Coordinator는 문서가 아니라 **판정 재료**를 골라 전달한다. 실측 목록:

| 시점 | 수신자 | 공급물 | 선별 방식 |
|---|---|---|---|
| Phase 1 step 1 | design-architect | 스코프 메모·활성 lens 목록·저장 경로·(있으면) BC 배치 고정·G1 override 입력 | lens 온오프 = 관심사 단위 선별 |
| Phase 1 step 2 | 리뷰어 3종 | architect 명세 초안 **만** (타 노트·코드 없음) + 설치 루트 | 정보 차단(편향 방지)이 명시 규칙 |
| Phase 1 step 3 | discipline-reviewer (lightweight) | 명세 초안 + 입장 표; Error scope**일 때만** project-wide tree/inventory 추가; diff·실행 결과는 «받지 않는다» | scope 조건부 동봉 |
| Phase 2 step 2 | acceptance-tester / coder | 입장 표에서 **네 owner인 행**만 + 관련 기존 anchor | 표의 행 단위 슬라이싱 |
| Phase 2 step 4 | coder | 승인 명세·구조 절·**이번 슬라이스 관련 입장 행**·acceptance 결과(있으면)·설치 루트 | 슬라이스 단위 슬라이싱 |
| Error scope 전 역할 | 전원 | 「승인된 12-slot 전체와 관련 입장 행」 | 명세 중 12-slot 절 발췌 |
| proof 모드 | design-review-api / discipline-reviewer | 12-slot·기준 evidence·exact command/exit/diagnostic·pin·introspection·dump·mounted 증거 묶음 (타 리뷰어 토큰 없음) | 증거 묶음 한정 공급 |

### 1.4 경로 D — 검사기의 규칙 단위 공급 (ⓓ 후보 줄)

27종 checker는 기계로 못 닫는 자리를 `[ⓓ#N] 경로: 사실 — 물음: …` 형식의 후보 줄로 낸다(실측: `check-domain-model.py` 119행 `self.append(f"[ⓓ{rule}] {where}: {msg} — 물음: {question}")`, exit 불산입). 각 checker 파일 헤더에 «담당 규칙 (rule-owner-map · 총 N)» 목록이 있어 규칙 번호→검사기 소유가 고정돼 있다. discipline-reviewer는 이 줄의 유일 판정자로 지정되고(「무응답 금지 — 후보를 흘리면 그 규칙은 판정자가 없다」), 에이전트 문서 안에 물음 여덟 표 + 규칙별 개별 물음 목록(약 60개 규칙 번호의 집행 발췌 문면)이 내장돼 있다.

### 1.5 경로 E — 규칙 본문의 구조적 비공급

커맨드 11행·houserules SKILL.md 공통 명문: 「무접두 `#N` 규칙의 «본문» 정본은 저장소의 정본 명세이고 플러그인 배포본에는 동봉되지 않는다 — 플러그인 문서에는 집행에 필요한 발췌만 실린다(2026-08-15)」. 즉 파이프라인 에이전트는 규칙 번호와 집행 발췌·판정 물음까지만 받고, 규칙 원문 전문에는 **접근 자체가 불가능**하다. 이것은 통짜 로드의 반대 극단 — 강제된 발췌 유통이다.

---

## 2. 판정: «걸리는 규칙만 골라 공급» 장치가 있는가

**판정: 혼합형 — 문서 층은 통짜+정적 라우팅, 데이터 층은 실질 그라운딩.** 런타임에 «이번 작업의 diff·스코프에 걸리는 규칙»을 규칙 코퍼스에서 동적으로 추출·주입하는 장치는 없다. 스킬 선별은 에이전트 저작 시점에 역할별로 고정(frontmatter)이고, 절 선별도 저작 시점의 § 번지수 지시다. 그러나 규칙보다 한 층 아래 — 판정 재료 — 에서는 골라 공급이 촘촘하다.

부분 그라운딩 장치 전수 목록 (13종):

1. **2층 스킬 구조** — SKILL.md 라우터만 상시, 본체 references/final.md는 실독 온디맨드 («요약을 믿지 말고 문서를 읽는다»).
2. **§ 지정 참조 지시** — 로드 문서 안 특정 절 번지수 지시, 본문 수십 곳 (§1.2 목록).
3. **규칙 번호(#N) 발췌 유통** — 본문 정본 미동봉, 집행 발췌만 플러그인 문서에 (경로 E).
4. **ⓓ 후보 줄** — checker가 걸린 자리+규칙 번호+판정 물음만 공급, exit 불산입 (경로 D). «걸리는 규칙만 골라 공급»의 가장 근접 실물.
5. **ⓓ 물음 표·개별 물음 목록** — 규칙 문면의 집행 발췌를 discipline-reviewer 문서에 내장 (검사기가 후보를 아직 안 내는 자리도 같은 물음을 쓰게 함).
6. **rule-owner-map** — 규칙 번호→검사기 소유 매핑 (각 checker 헤더 «담당 규칙» 목록·discipline-reviewer가 「어느 검사기가 내는지는 매핑표가 소유」로 참조).
7. **lens 활성화(G0)** — api·db lens 온오프로 리뷰어 호출·명세 절 자체를 문서 단위 선별 («빠진 lens는 명세에서 다루지 않는다»).
8. **모드 스위치** — discipline-reviewer 3모드(P1 lightweight / P2 implementation / DYNAMIC…), design-review-api 2모드. 모드별로 받는 입력과 적용 체크리스트를 게이팅 («Phase 1에는 구현 감사 전체 묶음을 받지 않았다는 이유로 항목을 실패 처리하지 않는다»).
9. **입장 표 행 슬라이싱** — owner 행·이번 슬라이스 관련 행만 전달 (Phase 2 step 2·4).
10. **12-slot 발췌 전달** — Error scope 전 역할에 명세 중 12-slot 절+관련 입장 행만.
11. **조건부 입력 동봉** — project-wide tree/inventory는 Error scope에서만, acceptance 결과는 있을 때만, 설치 루트는 references 실독·검사기 리터럴 호출용.
12. **면제 조문 번호 목록** — #15 #16 #23 … 16개 번호만 유통 (「문면은 정본 명세 소유」·번호 인용 기각 전용, 새 의무 생성 금지).
13. **정보 차단(역방향 그라운딩)** — 리뷰어에 타 노트·구현 코드 비공급(편향 방지), acceptance-tester에 프로덕션 코드 비공급(블랙박스), P1 discipline에 diff 비공급. 공급 못지않게 «안 주는 것»이 규칙으로 고정됨.

통짜 지점의 잔존: frontmatter 27슬롯(라우터라 부피는 작음)과, 실독 지시가 사실상 전문·전절 로드인 곳 — design-architect·coder의 final.md §0+§1(트리 140행 전체), discipline-reviewer의 final.md §0~§4 직접 대조, Error scope 역할들의 12-slot «전체» 수신. 걸리는 §만 잘라 주는 자동화는 어디에도 없고, 절 안에서의 취사는 에이전트 주의(attention)에 맡겨져 있다.

---

## 3. 게이트 절차 실물 — 결정적 검사 vs 에이전트 판단

### 3.1 스크립트·형식 계약이 결정하는 것 (13)

| # | 게이트 | 검사 | 실물 |
|---|---|---|---|
| 1 | G0 | 빚 스캔 | Phase 2의 6번 registry 27종을 «계약 그대로»(루트 TARGET·`--error-profile auto`) 실행, 27종 각각의 exact command·exit을 `refactor-scope.md`에 기록. 「증거 없는 «빚 0»은 G0 blocker」·차분 도구(`registry_gate.py`) 대체 실행 금지 |
| 2 | G0 | 산출물 폴더 결정화 | `ls .dddjango/` 조회 의무(재빌드 여부를 자동매칭이 아닌 사용자 선택으로), `date +%Y%m%d-%H%M` prefix(LLM 추측 금지) |
| 3 | G1 | 리뷰 노트 구문 검사 | 집행성 판정 1행·(ddd) 판정-소유 대조 표 또는 «판정 없음» 1행의 **존재 검사만** — 「원문 대조는 하지 않는다」. 없으면 반송 |
| 4 | G1 | 12-slot label·순서 검사 | 12개 label 문자열·순서의 정확 일치, G1 제시 전+승인 후 Phase 2 dispatch 직전 2회 재독. 누락·모호·모순이면 승인 입력이 있어도 반송 |
| 5 | G2 | build_anchor | Phase 2 첫 서브에이전트 파견 직전 `git rev-parse HEAD`를 1회만 기록(재기록 금지 — 차분 세탁 방지) |
| 6 | G2 | 27종 auto-렌더 전체 실행 | 순서 고정 registry, positional TARGET=루트(좁힌 TARGET green은 증거 아님) |
| 7 | G2 | registry_gate 귀속 차분 | `registry_gate.py . --anchor $(cat build_anchor)` — 게이트 증거는 «귀속 0 + legacy 잔존 별도 보고». gate 자신의 exit 1(공허 차분·앵커 결손)은 측정 실패 blocker |
| 8 | G2 | scope-렌더 5종 | Error scope마다 registry #2·#15·#6·#5 + composition #16을 `--error-profile/--scope/--api-module/--controller-module/--scope-bc/--error-bc/--anchor/--legacy-debt-file`로 렌더 실행 |
| 9 | G2 | exit 계약 판정 | `0/1/2` 의미 고정. 직접 실행 exit 1=무조건 blocker(warning 강등 금지), scope-렌더 exit 2=검사기 자신의 `--anchor` 차분(신규분만 blocker·전건 기존분이면 exit 0 강등), 앵커 없는 exit 2=직접 blocker |
| 10 | G2 | runtime proof | 잔여 exit 1 전건이 `DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED`일 때만: 실제 dependency pin에서 field/metadata/hook inventory·wire 직렬화·mounted status/body·generated OpenAPI를 기준선과 전수 대조 실행 |
| 11 | G2 | 테스트 실행 | 관련 테스트+기존 전체 suite를 **Coordinator가** 실행. 무관/관련의 자 = «변경 전에도 실패했는가»(기준선 실측) |
| 12 | G2 | 배너 제시 차단 조건 | Red·`pending`·입장-diff 불일치·첫-Green 비계·미해소 exit 1/scope-렌더 exit 2·미해소 귀속 red·contract mismatch가 하나라도 있으면 G2 미제시 |
| 13 | P3 | 마무리 검증 | 관련 테스트·전체 suite·마이그레이션·`manage.py check`·(구성 시) mypy strict — 실행분만 보고, 미실행 사유 명시 의무 |

여기에 사용자 게이트 자체(G0·G1·G2 AskUserQuestion 승인 필수·선택지마다 대가 한 줄·`STOP_FOR_USER_APPROVAL` 기록-정본 절차)가 절차적으로 결정화돼 있다 — 판단은 사람 몫이나 «물어야 한다»는 결정적이다.

### 3.2 에이전트 판단(확률)에 맡겨진 것 (24)

Coordinator:
1. 모드 판별(신규/수정 — «모호하면 G0에서 사용자에게 확인»으로 탈출구만 있음).
2. lens 추론·제안(api·db 활성 여부).
3. 12-slot 값의 «구체적이고 선택 profile에 맞으며 서로 일관» 의미 판정(label 검사 밖의 전부).
4. Error preflight의 inventory 완전성·모호·상충 판정(STOP 여부 — 「checker가 membership을 추론하게 하지 않고」).
5. 무관/관련 실패의 기준선 분류 집행(기준은 결정적으로 정의·측정은 에이전트).
6. G0 빚의 «미룰 수 없음»(해로움) 판정 — 물음 문면은 고정, 답은 판단(«미룰 수 없음»엔 사용자 ⓑ 선택지 자체가 없음).

design-architect:
7. 설계 결정 전반 — BC 배치(미고정 시)·profile 선택·애그리거트 경계·입장 표 7-decision·Risky Write 8행 채움.
8. 절 간 자기모순 1회 스캔.
9. 리뷰어 간 충돌 중재(미해결이면 G1 옵션으로 승격).

리뷰어 3종:
10. lens별 비평·심각도(blocker/important/nit) 부여 — db 리뷰어의 «Risky Write 의미 재분류»(라벨이 아니라 연산 성격으로), 8행의 «의미적 충족» 판정 포함.
11. 집행성 판정(«추론 없이 집행 가능한가» — 인용 3곳 요건으로 형식만 결속).
12. (ddd) 판정-소유 대조 표 작성 — 판정→배정 위치 대조는 전적으로 판단.

discipline-reviewer P1:
13. 입장 표 완결성·근거·독자 failure·중복 감사.
14. change inventory가 승인 스코프 안인지 판정.

discipline-reviewer P2:
15. test diff hunk ↔ decision·독자 failure 대조.
16. 첫-Green 비계 잔존 감사.
17. 빈혈 C형(도메인 규칙 메서드 부재) — 「결정적 백스톱을 두지 않는다 — 적출은 전적으로 너의 의미 점검 몫」 명문.
18. 상수 승격·심볼 소비 5축 — 「백스톱 사각 전담」(변수 우회·간접 queryset·비교식·`__in` 변종 등 checker가 못 잡는 형태).
19. 메커니즘-소유권(이번 diff 신규분의 엔진·격리 의미 변경 — 레드 플래그/화이트리스트 목록은 고정, 판정은 판단).
20. checker별 exit-0 blind spot (a)~(g) 명시 직독 — 「exit 0이어도 semantic compliance의 증거가 아니다」.
21. ⓓ 후보 전건 판정(무응답 금지·기각 사유 1줄 의무).
22. human 판정 둘 — #254 애그리거트 과묶임·#316 판정 쪼개짐(「검사기가 아예 없다」 명문).
23. ACL 실패 번역 전수성·서버렌더 오류 분류(§11)·주석/docstring 언어·final.md 직접 대조의 의미 변종(개명 폴더·빈-정본 위장·lazy 싱글톤 공유 등).

이중 확인:
24. DYNAMIC_ERROR_SHAPE 확인 토큰 — API·discipline 리뷰어가 서로 노트 없이 각자 `RESOLVED_…_API_CONFIRMATION`/`…_DISCIPLINE_CONFIRMATION`을 내야만 성립(확률 판정 2개의 독립 합의로 결정성 근사).

(부수: acceptance-tester·coder의 «새 정보» 충돌 발견→반송 판단, coder의 명세-표준 괴리 감지 `TREE_CONTRACT_MISMATCH`도 판단 위임이나, 반송 «축»은 고정돼 있어 위 24에 접어 세지 않았다.)

### 3.3 경계의 명시성

이 파이프라인의 특징은 결정/확률 경계가 **문서 수준에서 자기 선언**돼 있다는 점이다:
- checker가 못 보는 것: 「checker별 exit-0 blind spot」 절 (a)~(g).
- checker가 아예 없는 것: 「human 판정 둘 — 검사기가 없다」, 빈혈 「결정적 백스톱을 두지 않는다」, ⑤ 발행 봉투 discriminator 「대응 백스톱 없음 — 형태 판정은 FP 불가피」.
- 판단의 출력을 형식으로 결속: 집행성 판정 인용 요건, 대조 표 존재 검사, 보고 5열 형식(`path::test | decision | …`), 확인 토큰 상수 문자열, 배너 상시 필드(«task 리스트»·«슬라이스 감사» — 조건부 자기보고 제거).

---

## 4. 집계

| 항목 | 수 | 비고 |
|---|---|---|
| 통짜 로드 지점 | 27 | frontmatter 스킬 슬롯(7 에이전트) — 단 실체는 45~83행 라우터. 본체 16,069행은 온디맨드 |
| 부분 그라운딩 장치 | 13 | §2 전수 목록 |
| 게이트 결정적 검사 | 13 | §3.1 표 |
| 에이전트 판단 위임 | 24 | §3.2 목록 |

---

## 5. 소결

1. 그라운딩의 실물은 «규칙 검색기»가 아니라 **3중 정적 선별**이다: (역할→스킬) frontmatter, (작업→절) § 번지수 지시, (판정→재료) Coordinator 슬라이싱. 셋 다 저작 시점에 굳힌 선별이라 재현성은 높고, 대신 새 규칙이 생기면 라우팅을 손으로 고쳐야 한다.
2. «걸리는 규칙만 골라 공급»의 유일한 런타임 장치는 검사기 ⓓ 후보 줄(위치+번호+물음)이다 — 규칙 코퍼스 쪽에서 밀어내는 push형이지, 에이전트가 당겨오는 pull형 검색이 아니다.
3. 규칙 «본문»은 의도적으로 유통 금지다(배포본 미동봉) — 그라운딩 이전에, 통짜 로드가 구조적으로 불가능한 축이 하나 존재한다. 에이전트가 규칙 전문을 근거로 삼을 수 없고 발췌·번호·물음으로만 집행한다.
4. 게이트의 무게중심: 형태·경로·배선 위반은 27-checker+앵커 차분이 결정하고, 의미 판정(빈혈·소유권·승격·번역 전수성)은 discipline-reviewer 단일 에이전트에 집중된다 — 확률 판정의 최대 단일 표면이 이 에이전트다(48KB·판단 위임 24건 중 11건 소유).
