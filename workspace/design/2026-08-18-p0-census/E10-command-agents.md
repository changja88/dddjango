# P0 센서스 — E10: command + pipeline agents

담당: `dddjango/commands/dddjango.md` + `dddjango/agents/*.md` 8개 파일 전수.
작성일: 2026-08-18.

**계수 방법**: 절 = 헤딩(`##`/`###`) 단위, 단 커맨드 Phase 2는 번호 step(1~7)이 코퍼스 내 실제 참조 단위(«Phase 2 step 6» 등)라 step 단위로 쪼갬. 규범 문장 = 마침표(또는 불릿) 단위 문장 중 지시·금지·조건 표지를 가진 것 — 한 문장에 지시가 여럿이어도 1로 셈(문장 수 기준). 이유 서술(«*왜* — …»)·역할 정체성 단문·예시는 제외, 애매하면 포함하고 비고에 표시. ④쌍둥이는 파일 단위 판정(`codex-dddjango/skills/` Glob 확인)을 절에 상속.

## 파일별 요약

| 파일 | 행수 | 절수 | 규범 문장수 | codex 쌍둥이 |
|---|---|---|---|---|
| commands/dddjango.md | 176 | 17 | 313 | 있음 (`skills/dddjango/SKILL.md`) |
| agents/acceptance-tester.md | 54 | 5 | 75 | 있음 (`skills/dddjango-acceptance-tester/SKILL.md`) |
| agents/coder.md | 71 | 6 | 103 | 있음 (`skills/dddjango-coder/SKILL.md`) |
| agents/design-architect.md | 96 | 6 | 178 | 있음 (`skills/dddjango-design-architect/SKILL.md`) |
| agents/design-review-api.md | 84 | 6 | 94 | 있음 (`skills/dddjango-design-review-api/SKILL.md`) |
| agents/design-review-db.md | 44 | 5 | 35 | 있음 (`skills/dddjango-design-review-db/SKILL.md`) |
| agents/design-review-ddd.md | 44 | 5 | 28 | 있음 (`skills/dddjango-design-review-ddd/SKILL.md`) |
| agents/discipline-reviewer.md | 130 | 8 | 234 | 있음 (`skills/dddjango-discipline-reviewer/SKILL.md`) |
| **합계** | **699** | **58** | **1060** | 8/8 존재 |

③백스톱 범례: 커버 = 문면이 check-*.py/registry_gate 등 결정적 검사기를 지목하거나 규칙 번호로 명백 대응. 비커버 = 절 규칙이 오케스트레이션 절차·출력 형식·리뷰 행위라 27종 검사기(코드 대상)의 관할 밖임이 명백. 불명 = 코드 산출물 규칙인데 스크립트 무언급·대응 부분적.

## commands/dddjango.md (17절 · 313)

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---|---|---|---|---|
| 전문·번호 공간 규약 (dddjango.md L7–11) | 5 | 없음 | 명시(Coordinator·subagent 위임) | 비커버 | 헤딩 없는 서두. registry #N ↔ 무접두 #N 이중 번호 공간 규약의 유일 정의처. 무접두 #N 본문 정본은 플러그인 미동봉(외부 의존 명시) |
| 산출물 위치 | 9 | 있음 | 명시(코디네이터 소유·architect 제자리 수정) | 비커버 | `.dddjango/` 폴더 규약·한 기능=한 폴더. 검사기 무대응(절차 규칙) |
| 진행 가시성 | 22 | 있음 | 명시(사용자 승인·discipline 권고 인용) | 비커버 | 게이트 배너 형식 블록 = 사실상 앵커화된 출력 계약. 날짜 스탬프(2026-08-13/15/17) 다수 |
| 시작: 모드 판별 | 5 | 있음 | 명시(사용자 확인) | 비커버 | 모드축/배치축 직교 선언 |
| Phase 0 — 요구·스코프 (G0) | 39 | 있음 | 명시(사용자·코디네이터·architect 경계) | 커버 | 빚 스캔 = «Phase 2 step 6 registry 그대로» 실행 + `registry_gate.py` 대체 실행 금지 명시. 절 내부에 스택 판정 소유(architect) 경계 문장 포함 |
| Phase 1 — 설계 (G1) | 52 | 있음 | 명시(architect·리뷰어 3종·discipline·Coordinator) | 비커버 | 12-slot label·순서 리터럴이 여기 재등장(architect 문서와 중복 서술 — 표류 위험). 병렬=«한 응답 안 다발» 정의 소유 |
| Phase 2 step 1 (러너 준비) | 5 | 있음(step 번호) | 명시(`implementation-django-ninja` §2.1 인용) | 커버 | pytest settings binding은 registry #12 `check-test-config.py`와 명백 대응 |
| Phase 2 step 2 (한정 검색·dispatch) | 5 | 있음(step 번호) | 명시(acceptance-tester/coder 라우팅) | 비커버 | 일곱 decision → 소유자 라우팅 표준의 정본 |
| Phase 2 step 3 (슬라이스 도출) | 4 | 있음(step 번호) | 명시(G0 빚 결정 참조) | 비커버 | 슬라이스 0(동작 불변) 선행 규칙 |
| Phase 2 step 4 (coder 호출·슬라이스 감사) | 10 | 있음(step 번호) | 명시(coder·discipline·원작성자) | 비커버 | 홀리스틱 갈음 조건(2026-08-17). discipline-reviewer §감사 빈도가 이 step을 정본으로 역참조 |
| Phase 2 step 5 (규율 감사·suite 실행) | 18 | 있음(step 번호) | 명시(역할 4종 라우팅·너=코디네이터 실행) | 비커버 | 무관/관련 실패의 자=기준선 실측(2026-08-13). G2 blocker 토큰 3종 정의 |
| Phase 2 step 6 (결정적 백스톱 27종) | 81 | 있음(step 번호·registry #1~#27) | 명시(검사기 27종 소유권 표·registry_gate·API/discipline reviewer 토큰) | 커버 | 최대 절. registry 표(27항목) = 검사기↔규칙번호 매핑의 정본. 앵커 차분/귀속 차분 두 계열 판정. exit-0 blind spot 절 포함. 규범 밀도 최고 지점 |
| Phase 2 step 7 (G2 배너) | 6 | 있음(step 번호) | 없음(승인 주체 «승인받는다»로만 암시) | 커버 | 27-registry·12-slot evidence 지목. G2 차단 조건 열거 |
| Phase 3 — 마무리·검증 보고 | 3 | 있음 | 없음 | 커버 | manage.py check·mypy strict 등 결정적 도구 지목 |
| 수정 모드 (부분 수정) | 17 | 있음 | 명시(너=코디네이터·G1′) | 커버 | «Phase 2 step6 그대로 적용» 역참조 — step 번호 앵커의 실사용례 |
| 엣지 처리 | 17 | 있음 | 명시(coder·architect·acceptance 반송처) | 커버 | checker exit 1/2 처리 재서술(step 6과 중복 — 축약판) |
| 경계 | 15 | 있음 | 명시(architect·acceptance-tester·coder) | 비커버 | 게이트 질문·STOP 기록 형식(2026-08-13)이 경계 절 안에 실림 — 절 제목과 내용 불일치(형식 규정이 «경계»에 동거) |

## agents/acceptance-tester.md (5절 · 75)

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---|---|---|---|---|
| 전문 (acceptance-tester.md L13) | 2 | 없음 | 명시(너=인수 테스트 작성자·소유 행) | 비커버 | discipline-tdd decision 우선·implementation-test는 mechanics 한정 |
| 입력 | 5 | 있음 | 명시(Coordinator·설계 반송) | 비커버 | 블랙박스(프로덕션 코드 불가시) 규칙 |
| 산출 | 5 | 있음 | 없음(주어 암시) | 비커버 | 보고 형식 `path::test \| decision \| …` — command step 5와 동일 리터럴(중복) |
| 인수 테스트 작성 규칙 | 57 | 있음 | 명시(coder 영역·discipline 감수자·설계 반송) | 불명 | 23개 불릿. 12-slot 오라클 규칙·URL 합성 규칙·pytest 셋업 — 테스트 산출물 규칙이나 스크립트 무언급(배치만 #12 간접 대응). «결정 재방문 금지(2026-08-15)» — coder와 쌍둥이 문장 |
| 경계 | 6 | 있음 | 명시(coder의 몫·네 소유) | 비커버 | 외부 계약 테스트는 파일 위치 무관 소유 선언 |

## agents/coder.md (6절 · 103)

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---|---|---|---|---|
| 전문 (coder.md L16) | 2 | 없음 | 명시(너=메인 코더·owner 행) | 비커버 | |
| 입력 | 2 | 있음 | 명시(Coordinator) | 비커버 | pending 입력 시 반송 |
| 산출 | 4 | 있음 | 없음(주어 암시) | 비커버 | 보고 형식 리터럴 — acceptance-tester·command와 3중 중복 |
| 작업 방식 (안쪽 루프 TDD) | 82 | 있음 | 명시(architect 소유·Coordinator 전달·설계 반송) | 커버 | 24개 불릿. `check-layer-skeleton` 스크립트명 직접 지목(#487)·검사기 확장-리터럴 호출 규칙(2026-08-15). 배선 표준(#105~#112)·TREE_CONTRACT_MISMATCH 대칭 반송(2026-08-13 라운드 2 실증 인용). 12-slot preflight — architect·command와 병렬 전개 |
| 엣지·보고 | 4 | 있음 | 명시(설계/인수테스트 반송) | 비커버 | |
| 경계 | 9 | 있음 | 명시(acceptance-tester/설계·architect 소유) | 커버 | 메커니즘 대체 금지 = registry #1 `check-mechanism-ownership.py`와 명백 대응(출처-불문 열거) |

## agents/design-architect.md (6절 · 178)

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---|---|---|---|---|
| 전문 (design-architect.md L13) | 0 | 없음 | 명시(너=단일 작성자) | 비커버 | 순수 역할 서술 — 규범 문장 0인 유일 절 |
| 입력 | 6 | 있음 | 명시(Coordinator·ddd 리뷰어·사용자 고정 결정) | 비커버 | BC 배치 존중·G1 override 좁은 재호출(타 절 불변) |
| 산출 | 3 | 있음 | 명시(coder·acceptance 몫) | 비커버 | |
| 명세에 담는 것 | 158 | 있음(내부 `### Error response contract 12-slot` 별도 헤딩) | 명시(final.md·§3.2·db lens 등 값-소유 위임 다수) | 커버(부분) | 최대 밀도 절. 12-slot 1~12 리터럴 label 정본(command·review-api와 3중 병렬). 트리·FK·dto 규칙은 registry #4·#17·#19와 규칙 번호로 명백 대응, 채널 물음 넷은 «검사기 없음·G1 설계 판정·ⓓ» 자기 선언 — 커버/비커버 혼재를 커버(부분)로 기재. Risky Write 8행 블록·산출물-우선 쓰기(2026-08-13)·값 사본 금지(«값 사본은 썩는다») 포함 |
| 리뷰 반영·충돌 중재 | 7 | 있음 | 명시(네가 중재·Coordinator 제시) | 비커버 | 메타 요약 블록 금지·자기모순 1회 스캔 |
| 경계 | 4 | 있음 | 명시(coder 몫·lens 소유) | 비커버 | |

## agents/design-review-api.md (6절 · 94)

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---|---|---|---|---|
| 전문 (design-review-api.md L10) | 1 | 없음 | 명시(Coordinator 지정 모드) | 비커버 | |
| 실행 모드 | 4 | 있음 | 명시(Coordinator) | 비커버 | 2모드(DESIGN / DYNAMIC_ERROR_SHAPE_PROOF) — 후자는 checker exit 1 토큰이 트리거 |
| 입력 | 3 | 있음 | 명시(Coordinator·독립성) | 비커버 | 스킬 references 실독 허용(제한은 타 노트·코드) |
| 산출 | 11 | 있음 | 명시(architect 몫·확인 토큰 계약) | 비커버 | 집행성 판정 1행(2026-08-15) — 인용 없는 «가능» 무효. RESOLVED_…_API_CONFIRMATION 토큰 발화 조건 |
| 점검 항목 (계약 lens만) | 72 | 있음(내부 12-slot 헤딩·slot 번호) | 명시(discipline-reviewer로 물리 판정 이관) | 비커버 | 12-slot 심사판 — architect 작성판과 slot별 병렬(표류 위험). URL 합성 규칙이 acceptance-tester와 중복 서술 |
| 경계 | 3 | 있음 | 명시(ddd·db 리뷰어 몫) | 비커버 | |

## agents/design-review-db.md (5절 · 35)

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---|---|---|---|---|
| 전문 (design-review-db.md L10) | 1 | 없음 | 명시(architect 명세·읽기 전용) | 비커버 | |
| 입력 | 2 | 있음 | 명시(Coordinator) | 비커버 | |
| 산출 | 6 | 있음 | 명시(architect 몫) | 비커버 | 집행성 판정 1행 — 3개 리뷰어 공통 형식(동형 3중 서술) |
| 점검 항목 (데이터 lens만) | 23 | 있음 | 명시(discipline-tdd·acceptance-tester 몫 위임·리뷰어 직접 재분류) | 비커버 | Risky Write 8행 «의미적 충족» 판정(리터럴 '§9.6' 불요) — 구조 완전성만, 적정성은 타 소유 |
| 경계 | 3 | 있음 | 명시(ddd·api 리뷰어 몫) | 비커버 | |

## agents/design-review-ddd.md (5절 · 28)

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---|---|---|---|---|
| 전문 (design-review-ddd.md L9) | 1 | 없음 | 명시(architect 명세·읽기 전용) | 비커버 | 유일하게 discipline-tdd 스킬 미탑재 리뷰어 |
| 입력 | 2 | 있음 | 명시(Coordinator) | 비커버 | |
| 산출 | 9 | 있음 | 명시(architect 몫) | 비커버 | 판정-소유 대조 표(2026-08-17) 의무 — command Phase 1 step 2의 «존재 검사» 반송과 짝(구문 검사 계약) |
| 점검 항목 (도메인 lens만) | 13 | 있음 | 명시(`architecture-ddd` §3.2 항-(1)·(2) 값-소유 인용) | 비커버 | 빈혈 차단·구조 이주 대조 — discipline-reviewer Phase 2 빈혈 항목과 시점 분업(설계/구현) |
| 경계 | 3 | 있음 | 명시(api·db 리뷰어 몫) | 비커버 | |

## agents/discipline-reviewer.md (8절 · 234)

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---|---|---|---|---|
| 전문 (discipline-reviewer.md L12) | 1 | 없음 | 명시(단발 체크포인트 감사) | 비커버 | |
| 입력 | 16 | 있음 | 명시(Coordinator 모드 명시 의무·독립성) | 비커버 | 3모드. Phase 1에 change inventory 스코프 검사(2026-08-13) 포함 |
| 산출 | 11 | 있음 | 명시(반송처 4종 라우팅) | 비커버 | RESOLVED_…_DISCIPLINE_CONFIRMATION 토큰 — api 리뷰어와 대칭 이중 확인 |
| 감사 빈도 (적응형) | 3 | 있음 | 명시(발동 기준 정본=커맨드 Phase 2 step 4·5 역참조) | 비커버 | 문서 간 정본 위임의 명시 사례 |
| 영구 테스트 입장 감사 | 18 | 있음 | 명시(원 소유자·설계 반송) | 비커버 | 일곱 decision·여섯 열 검사 — architect 입장 표와 대응 |
| Phase 1·2 API 오류 scope·소유권 점검 | 13 | 있음 | 명시(API reviewer 소유 경계·Coordinator handback) | 불명 | #114·#488 규칙 번호 대응 있으나 스크립트명 무언급. `bc_error_schema.py` canonical 경로 리터럴 보유 |
| Phase 2 점검 항목 (클린코드·TDD 규율만) | 163 | 있음 | 명시(«네 몫»/타 소유 경계 문장 다수·FC-2 그레이더 언급) | 커버(분업 명시) | 최대 절. `check-choices-literal-consumption`·`check-public-surface-annotation` 스크립트명 직접 지목 + «백스톱 사각 전담» 자기 정의. ⓓ 후보 물음 표 8행+개별 물음 13줄(#N 소유자 번호 체계) — rule-owner-map 별도 문서 언급. 면제 조문 16종 번호 열거. human 판정 둘(#254·#316) «검사기 아예 없음» 명시 |
| 경계 | 9 | 있음 | 명시(코더·implementation-*·API reviewer·acceptance 몫) | 비커버 | 소유권/정확성 구분 반복 명문화 |

## 4축 집계 (절 수 기준, 총 58절)

| 축 | 값 |
|---|---|
| ①앵커 | 있음 50 · 없음 8 (없음 = 각 문서의 헤딩 없는 전문/서두 8개) |
| ②소유자 | 명시 54 · 없음 4 (command step 7·Phase 3, acceptance 산출, coder 산출) |
| ③백스톱 | 커버 11 · 비커버 45 · 불명 2 (acceptance 작성 규칙, discipline API 오류 소유권 점검) |
| ④쌍둥이 | 존재 58 · 부재 0 (8파일 전부 codex-dddjango/skills/에 대응 SKILL.md 존재) |

## 특이 발견

1. **이중(실제로는 다중) 번호 공간이 이미 운용 중** — 커맨드 서두가 «registry #N(1~27) vs 무접두 #N(정본 명세 규칙 번호)» 규약을 명문화했고, 그 외에 12-slot 번호(1~12), Phase step 번호, ⓓ 물음 소유자 번호, 면제 조문 번호까지 이질적 참조 체계가 최소 5종 혼용된다. 무접두 #N의 본문 정본은 플러그인에 미동봉(발췌만) — 온톨로지 레지스트리가 흡수해야 할 1순위 ID 체계.
2. **앵커 공백은 정확히 «전문» 8곳뿐** — 각 문서의 헤딩 이전 서두(역할 선언+핵심 규범)가 참조 불가 지대다. 커맨드 전문은 번호 공간 규약이라는 코퍼스 전역 해석 규칙을 담고 있는데 앵커가 없다.
3. **Error response contract 12-slot이 3중+α 병렬 전개** — architect(작성 계약)·review-api(심사 계약)·command Phase 1(label·순서 리터럴 재독 계약)에 slot별 전문이 각각 실리고, coder(preflight)·acceptance(오라클 규칙)에도 축약판이 실린다. label 리터럴 «구문 검사»로 방어 중이나 slot 본문 의미는 문서 간 자연어 재서술이라 표류 위험 최대 지점.
4. **날짜 스탬프가 사실상 규칙 ID 대용** — (2026-08-12 라운드 1′)·(2026-08-13)·(2026-08-15)·(2026-08-17) 등이 개정 근거 앵커로 문서 횡단 반복 인용된다(같은 날짜가 서로 다른 규칙에 붙어 유일성 없음). 온톨로지 도입 시 규칙 ID로 치환할 후보.
5. **소유자 명시율 93%(54/58)** — «한 주제 한 소유자»가 문면에 관철된 코퍼스. 반면 결정적 백스톱 커버는 19%(11/58)이고, 그 공백을 discipline-reviewer가 «백스톱 사각 전담»으로 명문 흡수한다(ⓓ 후보 무응답 금지·human 판정 둘·면제 조문 16종). 규칙→판정자 매핑표(rule-owner-map) 별도 문서의 존재가 discipline-reviewer 문면에 언급됨 — 온톨로지의 직접 씨앗.
6. **동일 규범의 다중 사본(표류 감시 대상)**: ⓐ 비계 첫-Green 즉시 제거 — command step 4·acceptance·coder·discipline 4곳 동일 서술, ⓑ «결정 재방문 금지(2026-08-15)» — acceptance·coder 쌍둥이 문장, ⓒ 보고 형식 `path::test | decision | …` 리터럴 — command·acceptance·coder 3곳, ⓓ 배선 표준(#105~#112)+«preserve는 wire 산출물까지» — command·coder·architect·discipline 4곳, ⓔ URL 합성(@api_controller prefix+route) — acceptance·review-api 2곳, ⓕ 집행성 판정 1행 — 리뷰어 3종+discipline 4곳 동형.
7. **문서 간 정본 위임이 명시적** — discipline-reviewer §감사 빈도가 «커맨드 Phase 2 step 4·5가 정본»이라 역참조하고, architect·discipline이 트리·명명 «값»을 `references/final.md`에, 판정-이주 값을 `architecture-ddd` §3.2에 위임하며 «값 사본은 썩는다»는 원칙까지 명문. 다만 위임 참조 표기가 절 번호(§)·규칙 번호(#)·트리 행 번호(«22~32행»)로 제각각 — 앵커 표준화 여지.
