# 라운드 1′ 발견 수정 계획 — v2 (적대 리뷰 4렌즈 중재 반영판)

> **최종 확정(2026-08-12 사용자 승인 — 구현 착수)**: 열린 결정 전부 닫힘.
> - **D1′ = ⓐ**: #96×2 는 검사기 오탐 확정(spec #95 가 driving 잎의 exception·value_object import 를 명시 허용 — check-event-publish 의 blanket 검사가 스펙 드리프트) → 검사기를 #95 허용 목록에 정렬(값 무변). **#326 은 「domain VO 값 파생(나열·순회) 전용 import 허용」 좁은 예외**(코퍼스 implementation-django :203·:215 의 파생 요구와 정렬 — 표준 개정 스탬프·spec :640 행+검사기+fixture 동시).
> - **D3 = ㉰ code-json 이주**: 오류 축의 목표 상태 = 플러그인 표준(controller 좁은 try/except → BC ErrorSchema → two-argument Status·catch-all 금지). 플러그인 규칙 변경 없음(code-json 이 이미 표준) — **하네스 쪽 작업**: spec.md 오류 절 재작성(«중앙 소유·api.py 매핑 행» 지시 제거 = 스팩 결함 수정), 라운드 프로토콜 A축 기준 개정(성공 경로 등가 + 오류 경로는 개정 명세 대비), 결과지 「spec 결함 0」 정정. preserve 등록-자리 작업(구 ⓐ)은 소멸. 다음 라운드부터 NJ-7·SD-6 은 code-json 문면으로 판정.
> - **D4 = 조사 종결(결정 없음)**: ⑴ 은 #390 기존 문면(«입구에서 출구까지 한 흐름 통째로»)의 검출 보강 — C1 에 편입(표준 개정 아님·코퍼스 위반 0 실측). ⑵ 는 기존 규칙 조합이 이미 답(#385 검사기 문면 «타 BC 는 입구로 검사한다» + 원칙 06 의 수용된 중복) — 신설 불요, 재라운드 구현 지침만 명확화.
> - D2 = 확정안 유지(이관 빚 채널 — 단 D3 ㉰ 채택으로 인증 축 의존이 유일 잔존 후보).

작성 2026-08-12 · 재료 = 라운드 1′ 판정(`workspace/eval/results/20260812-1747-csrebuildlive-claude.md` · 대장 1′행) · 절차 = 문제 정의→원인→계획→구현→테스트(fixture red 먼저) · **적대 리뷰 4렌즈 완료(§5) — 초안 v1 의 P3′(경로 매칭 게이트)·H2(단일 그림자 스텁)는 리뷰로 반증되어 본판에서 재설계됨** · 사용자 승인 전 구현 착수 금지 · 열린 결정 = D1~D4(§4).

## 0. 문제 정의 — 발견 → 소유 → 수정 유형 (리뷰 교정 반영)

| # | 발견 | 소유(실측) | 수정 유형 | 동결 영향 |
|---|---|---|---|---|
| P1″ | preserve/확립 답습 라이선스가 배선·등록 축에 살아 있음 — 규범 부재가 아니라 **라이선스 문장들이 원칙을 이김**(라운드 1 기전 동일). 무조건 배선 표준은 ninja final.md §2.3 에 이미 있었음(원인론 교정 — 답습 렌즈) | agents 5파일·commands·houserules SKILL + **스킬 코퍼스 2곳**(architecture-ddd `final.md:636`·implementation-django `final.md:203` — §1.1 을 옛 의미로 인용) | 산문(값 무변) — 단 코퍼스 편집은 **행 수 보존** | corpus_mirror·codex 재생성 · eval 이 인용하는 행 앵커(ddd :630·:632) 불이동 확인 |
| P3′ | brownfield 게이트 충족 불가(«루트 전체 green» — legacy 전 스캔 red 영구) → 세션 자체 귀속 발명. 초안의 «변경 집합 경로 매칭»은 Goodhart 5계열 공격에 뚫림(§5.3 재현) | `commands/dddjango.md:95·133` + 신설 도구 2 | **판정 차분 게이트**(도구+계약 — 규칙 값 무변) | 스모크 신설·Makefile 등록·README 문구 |
| C1 | #390 오탐 — pytest-django `client` fixture 관용구 미인식(라운드 1′ 5건+entitlements 1건 = 6건 전부 오탐 실측) | `scripts/check-test-config.py:86·255-264·297-308` | 검사기(오탐 정정 = 기존 규칙 «입구» 문면의 올바른 적용) | «675» 무관 실측(§5.4 R2 — 6종 매트릭스에 불포함) · fixture_matrix 레인이 실검증 |
| H2 | #12 shadow 침묵(이웃 부재로 타 BC 분류 불능). 초안(빈 스텁 단일 그림자)은 skeleton 가짜 blocker 105건으로 자멸 실측 | `workspace/tools/bc_registry_run.py:39-50` | 하네스 — **two-pass** 재설계 | 없음(판정 도구) |
| D1 | 카탈로그 단일 출처 ↔ 잎 규율(#96·#326) 상충 — 실물은 `all_in_order()` **classmethod 호출**이라 «행위 호출 0» 예외로는 교착 미해소(§5.4 R1) | 규칙 값 정본 = `workspace/design/2026-08-08-tree-revision-spec.md:430(#96)·:640(#326)`(**final.md 미편입 — 8번 이관 미래형**·spec_lint 무반응 축) + 검사기 2종 | **열린 결정**(값 변경) | **SH-4 판 이동**(RUBRIC :57 → #17 exit 위임) — «표준 개정» 절차 필수(§5.4 R3) |
| D2 | 미이관 표준 경로 의존(인증 — pairing legacy) — 프로토콜 단서만으론 **세션 층 G2 데드락** 재생(§5.2 반박 4) | 프로토콜 + registry_gate 채널 + commands 단서 | 열린 결정(채널 설계는 확정) | 없음 |
| D3 | **preserve BC 오류-배선 데드락**(§5.2 반박 1) — P1″+게이트 적용 시 preserve BC 도메인 예외를 wire 계약에 잇는 합법 자리가 없음(api.py=#437·registrar 확장=#111·controller-local=coder:47 삼거리 전부 차단) | #111/#437 값 + check-composition-root + agents | **열린 결정**(값 변경) | fixture 레인·«표준 개정» 절차 |
| D4 | e2e 재료 규율 공백 — arrange 합법 경로 부재(타 BC test import=#385 red·framework 승격=#27 red·**통째 복제=불가시**) + «arrange 만 HTTP·act 직접 호출»은 기계 구분 불가(§5.1 R3) | 신규 술어 후보 2문 + check-test-config 확장 | **열린 결정**(규칙 신설) | fixture 레인·«표준 개정» 절차 |

이 밖의 라운드 1′ 귀속 위반(SD-6 #2/#4·#287·#110·#385·#387·#420)은 규칙·검사기 정상 — P1″(답습 차단)+P3′(게이트 강제)가 재발 방지 기전.

## 1. 원인 (리뷰 교정판)

1. **라이선스 > 원칙**: 배선 표준은 이미 무조건 문면으로 존재(ninja §2.3) — 그러나 «보존·확립·관례» 라이선스 문장 5곳+코퍼스 2곳이 그것을 이겼다(라운드 1 «실물 15개 > 원칙»과 동일 기전·축만 이동).
2. **충족 불가 게이트**: 계약 문면(«전체 green»·«exit 1/2 전부 blocker»)이 brownfield 에서 모순 → 자체 귀속 발명 유발. 검사기는 정상 발화했다.
3. **판정기 결손**: #390 관용구 사각(오탐 6)·#12 그림자 한계(누락 1) + preserve BC 오류-배선의 «표준 자리 부재»(D3)는 규칙 공백.

## 2. 수정 설계 (최종판)

### P1″ — 답습 라이선스 발본색원 2차 (산문 — 값 무변)

**규범(닫힌 화이트리스트 — houserules SKILL 에 정본 1곳·나머지는 포인터)**: «기존 관찰이 결정 입력인 축은 열거된 것뿐 — ①오류 wire 계약(12-slot preserve) ②API 스택 **정체**(근거=소비자 의존) ③주석 언어(§5) ④도구·러너(§6.1) ⑤승인 test artifact 의 기존 위치(§1.2) ⑥지원 중 행동 계약. **그 밖 전부 — 파일트리·배선/등록·import 방향·테스트 규율·값 집합 선언·인증 경로·admin 구조·OpenAPI 문서 후가공 — 관찰은 입력이 아니다.** 배선 «값»(#105~#112)은 Ninja 스택 조건부지만, ‹관찰 비입력› 원칙은 무조건이다.»

편집 목록(답습 렌즈 반박 2·3 전수 반영):
- `agents/coder.md` — :44-47 preserve 보존 대상에서 **composition 제외**(오류 wire 산출물로 한정) · :51 배선 문장 profile 밖 무조건 승격 · :54 명세 복종 조항에 «배선/등록이 표준(#105~#112)과 어긋난 명세는 집행하지 않고 `TREE_CONTRACT_MISMATCH` 반송» 연결.
- `agents/design-architect.md` — :58 조건부 배선 서술 무조건화 + preserve-native 보존 목록에서 **registration 제외** · 12-slot 절에 경계 1문.
- `agents/discipline-reviewer.md` — :86 «native registration/API-instance layout 보존» → «오류 wire 산출물 보존»으로 좁힘 · :60·:84 경계 조문.
- `commands/dddjango.md` — :65 «그 관례를» → «(스택 **정체**에 한함 — 등록·배선 형태는 표준)» · :99 «preserve 는 새 registrar slice N/A» 에 «N/A=검사 생략이지 표준 면제 아님» 부기.
- houserules `SKILL.md` — §1 백스톱 실행 계약 옆에 화이트리스트 규범 정본.
- **코퍼스 스윕**: 전 `skills/*/references/*.md` 에서 «§1.1·확립·존중» 인용 전수 grep → 최소 `architecture-ddd/references/final.md:636`(레이아웃 존중 삭제 — «무관 앱 불이동» 의미만 잔류)·`implementation-django/references/final.md:203`(TextChoices 존중 — D1 결정과 정합화). **행 수 보존 편집**(eval 인용 앵커 ddd :630·:632 불이동 — 편집 후 두 행 내용 불변 diff 확인) · corpus_mirror·codex 미러 재생성.

### P3′ — 판정 차분 게이트 (Goodhart 재설계안 채택)

- **`scripts/checker_registry.py` 신설**: 27종 목록+auto 플래그 단일 출처(순서=commands registry) + `assert set(glob("check-*.py")) == set(registry)` 자기 검증(목록↔파일 드리프트 차단 — §5.4 R7③). `bc_registry_run.py`·`fixture_matrix.py` 는 이 모듈 위임으로 재작성(:69 `assert 27` 보존).
- **`scripts/registry_gate.py` 신설 — 판정 차분(N∖L)**: ⑴ 앵커 resolve — actor 비선택: 라운드=`--anchor <대장 해시>`(하네스가 대장에서 읽어 넘김)·파이프라인=Phase 2 진입 직전 기록되는 build-start 앵커 파일(`.dddjango/<scope>/build_anchor`) ⑵ 앵커 상태를 `git archive`로 임시 추출, 현재 working tree 를 비-git 사본으로 복사(hermetic — bc_registry_run 전례) ⑶ 두 사본에 27종 실행 → 위반 라인 집합 **L**(앵커)·**N**(현재) — 라인번호·TARGET 접두 정규화, ⓓ candidate 라인 제외 ⑷ **귀속 = N∖L** → 0=exit 0 · ≥1=exit 2 ⑸ 보고 의무: 귀속 목록 + legacy 잔존(L∩N 건수·검사기별) + 해소(L∖N) — 침묵 금지 ⑹ **이관 빚 채널**: `--legacy-debt-file <승인 목록>`(규칙#+모듈 접두 — 사용자 승인 산출물·자동 판정 금지) 매칭 귀속은 exit 제외하되 «빚» 섹션 보고 필수 ⑺ 출력 머리에 «귀속 0 ≠ 전체 clean — 이 게이트는 legacy 격리용» 명문 ⑻ 비-git 대상=fail-closed(전량 귀속) ⑼ 경로 파싱 실패 라인=fail-closed(귀속 취급).
- **계약 개정**: `commands:95` — 게이트 증거=«앵커 대비 판정 차분 귀속 0 + legacy 잔존 별도 보고»(«전체 1회» 실행 요구는 유지 — 차분의 N 이 그 실행) · `:133` — «미이관 표준 경로 의존이 유일 잔존 귀속이면 STOP_FOR_USER_APPROVAL 표면화» + «빚 분류는 red 기록 근거이지 legacy 모양 추가 복사 근거가 아니다» · Phase 2 진입 직전 build-start 앵커 기록 절차 신설 · houserules SKILL §1 동기.
- **역할 분리 명문**(§5.3 A5c): 파이프라인 게이트(차분·앵커)와 ⑤C 하네스(bc_registry_run 전수 그림자)는 같은 registry 를 쓰되 물음이 다르다 — 전자=«이 런이 위반을 늘렸나», 후자=«이 BC 가 clean 한가». 이웃-내용 필요 규칙(#505 류)은 루트 실행(게이트) 소유(§5.1 R8).
- **검증**: `workspace/tools/registry_gate_smoke.py` 신설(임시 git repo — 케이스: 귀속 red·legacy-only green·위반 선커밋 공격(A1) red·골격 접힘(A2) red·빚 채널) + **Makefile 검증 세트 등록**(§5.4 R7① — fixture_matrix «밖», hermetic 비-git 원칙과 git-필수 레인의 긴장 분리).

### C1 — #390 오탐 정정 (회귀 렌즈 강화판)

- 신호 = **test_* 함수의 자기 인자 `client`/`async_client` 가 본문에서 Call 로 흐름**(수신자 attr 호출 또는 호출 인자 전달) · fixture-param 경로는 **all-판정 + 공허 가드**(top-level test 함수 0 이면 불성립) · 기존 신호(ENTRANCE 토큰·cron_job) OR 유지.
- fixture(red 핀 먼저): bad 4종(미사용 장식 인자·assert-only·헬퍼 정의만·혼합 파일) + good 2종(위임형=실물 미러·직접 verb 형).
- 검증 표적(§5.4 R2 교정): fixture_matrix 레인 + bc_registry_run 귀속 대조(**#390 6건 소멸** — child_settings 5·entitlements 1 수치 명기). «675»(api_error_backstop_matrix — 6종 전용)는 무영향 확인만. 성격=기존 규칙 «입구» 문면의 올바른 적용(EVAL-METHOD :14 부류) — 사용자 승인 기록.

### H2 — bc_registry_run two-pass (회귀 렌즈 재설계안 채택)

- 26종은 스텁 없는 그림자 → 이웃 BC 빈 스텁 mkdir → **check-context-isolation 만** 스텁 그림자에서 실행(로스터 소비 검사기는 이것 하나 — 실측).
- **검증(§5.4 R5 순서 교정)**: H2 를 **다른 검사기 수정보다 먼저 단독 적용**하고 그 시점에 «bc_registry_run 재실행 신규 red = 정확히 {#12×1·#51×2}·그 외 diff 0» 실측(도구 버전 스탬프 동반). #51×2 는 진짜 위반 — 해소 표준 답은 D4.
- docstring 에 분업 명문(#505 류=게이트 소유) + 스모크(합성 미니 루트: skeleton diff 0·#12/#51 발화·26종 diff 0).

## 3. 구현 순서 (승인 후 — R5 반영 재배열)

1. **fixture red 박제**: C1 bad 4(+good 2) · D1 양·음성 레인(event_publish·db_table — §5.4 R6) · registry_gate_smoke 5케이스 · H2 스모크 — 기대 불일치 전부 실측 기록
2. **H2 단독 구현·검증**: two-pass → {#12×1·#51×2} 실측 박제(버전 스탬프)
3. **P3′**: checker_registry → registry_gate(판정 차분) → fixture_matrix/bc_registry_run 위임 재작성 → Makefile 등록 → commands·SKILL 계약 개정 → smoke green
4. **C1**: 구현 → red→green + 귀속 대조(6건 소멸)
5. **P1″**: agents·commands·SKILL 산문 + 코퍼스 스윕(행 수 보존·앵커 불이동 diff 확인)
6. **D1~D4 반영**(사용자 결정대로 — 값 변경은 design spec `:430`/`:640` 행+검사기+fixture 동시·**«#18» 서수 인용 금지**(§5.4 R4 — 명세 #18 은 무관 규칙)·final.md 편입은 8번 이관 몫으로 보류 명기)
7. **검증 총합**: fixture 전수 · api_error_backstop 675 무영향 확인 · checker_lint · spec_lint · reverse_coverage(신설 2파일 등록) · tree_mirror · corpus_mirror · codex 미러 동기(byte-copy)
8. (사용자 승인) **v2.2.0 릴리즈**(D1·D3·D4 값 변경은 «표준 개정 — 신규 산출분부터·라운드 1′ 판정 불소급» 스탬프 — §5.4 R3) → 재라운드(새 앵커)

부수 보고(손대지 않음): EVAL-METHOD:74 «checker 19개»·corpus_mirror_sync:21 «19개» — 27종 정본과 어긋난 동결 문서 내부 선재 stale(§5.4 R8 — 동결 개정이라 사용자 별도 결정 대상).

## 4. 열린 결정 (사용자)

**D1 — 카탈로그 단일 출처 ↔ 잎 규율(#96·#326)** · flip 실측: 현행 위반 #96×2(schema — `all_in_order()` 호출)·#326×1(model — 멤버 순회)
| 옵션 | 내용 | 효과 |
|---|---|---|
| A | 잎에서 enum 제거(스키마 enum·choices 포기) | 규칙 무변 — **wire 계약 후퇴(A축 diff 발생)** |
| B1 | 예외=«값 나열·순회만» | #326 만 해소 — **#96 교착 잔존**(§5.4 R1) |
| **B2(권고)** | 예외=«값 나열·순회 + **인자 없는 카탈로그 조회 classmethod 호출**»(`all_in_order()` 류 — `resolve(raw)` 같은 판정 호출은 계속 위반) | #96·#326 해소(flip 3) — ast 판정 가능(인자 0 제약)·판정 이동 없음 |
| C | driving 상수 복제+동기 검사기 신설 | 규칙 무변 — 중복 도입·비용 |

**D2 — 미이관 의존(권고=확정안)**: 프로토콜 ⑤ 단서 + registry_gate `--legacy-debt-file`(사용자 승인 목록 — 초기 항목: `#12: application.pairing.presentation_layer.authentication`) + STOP_FOR_USER_APPROVAL + 복사 금지 조문. pairing 이관 시 목록에서 제거.

**D3 — preserve BC 오류-배선의 표준 자리**
| 옵션 | 내용 | 효과 |
|---|---|---|
| **ⓐ(권고)** | registrar(`api_router.py`)가 자기 BC **오류 handler 등록까지** 소유(`register_<bc>_api(api)` 안 — #111 값 확장) | api.py 청정 유지(#437 불변)·BC 삭제 내성 유지 — 검사기+fixture+중첩 def 사각 동시 폐쇄 |
| ⓑ | api.py 에 BC-예외 행 좁은 허용(#437 완화) | 확립 실물과 최단 정합 — api.py 가 BC 결합 누적(현행 legacy 문제의 영속화) |
| ⓒ | preserve 에서 controller-local 방출 허용(coder:47 개정) | 중앙 계약과 이중화 — preserve 취지 훼손 |

**D4 — e2e 재료 규율(신규 술어 2문)**: ⑴ «e2e/ 는 자기 BC 구현 칸(4층·composition_root) import 금지»(§5.1 R3 — arrange-HTTP·act-직접호출 봉쇄·코퍼스 소음 0 실측) ⑵ «타 BC 준비는 그 BC 의 HTTP 입구 호출로만 — 타 BC test import·모듈 복제 금지, 얇은 wrapper 는 자기 BC 소유»(§5.2 반박 5 — #51×2 의 표준 해소 경로). 채택 시 check-test-config 확장+fixture — 표준 개정 스탬프.

## 5. 적대 리뷰 반영 (중재 기록)

### 5.1 회귀 렌즈 (완료 — PoC·27종 diff 실측 동반)

**C1 재설계(반영)** — «인자 존재» 신호는 R1(미사용 장식 인자)·R2(assert-only)·R4(헬퍼 정의에만 인자)·R5(혼합 파일 any-판정)로 뚫림(전부 PoC red/green 실측). 강화판 = Call-흐름 사용·all-판정·공허 가드(실물 5파일 13/13 재오탐 0 실측). **R3 한계 명기**: arrange 만 HTTP·act 직접 호출은 «사용» 기준으로 기계 구분 불가 — 신규 술어로 격상(→D4⑴). **H2 전면 재설계(반영)** — 원안 빈 스텁 단일 그림자는 skeleton 가짜 #488 105건(15 BC×7칸) 실측으로 자멸 → two-pass(로스터 소비 검사기는 context-isolation 하나뿐 실측·대안 ⓑⓒⓓ 비교 기각). **R7 수치 교정** — 신규 red 는 {#12×1·**#51×2**}(#51 은 test→타 BC test 전용 규칙). **R8 분업** — 이웃-내용 필요 규칙(#505 류)은 그림자 소유 불가 → 게이트(루트) 소유 명문화.

### 5.2 답습 렌즈 (완료 — 계획 반려·7반박 전부 실물 인용)

**반박 1(blocker→D3 신설)**: preserve 오류-배선 데드락 — 출구 삼거리 전부 차단 실측(api.py=#437·registrar=#111 문면+reviewer:86·controller-local=coder:47). 라운드 1′ api.py +16줄이 실물. 부수: registrar 함수 내부 중첩 def 는 #111 검사기 blind(사각 카드). **반박 2(blocker)**: 편집 목록 밖 답습 라이선스 5곳 — reviewer:86·coder:47(composition)·coder:54(명세 복종—반송 미배선)·architect:58·commands:65 → 전수 개정으로 확장. **반박 3(blocker)**: 코퍼스 2곳이 §1.1 을 옛 의미로 인용(ddd:636 트리 축!·django:203 값 집합 축) — P1′ 회귀·D1 직결 → 코퍼스 스윕 단계 신설. **반박 4(major)**: D2 프로토콜 단서만으론 세션 층 G2 데드락 → 빚 채널+STOP 단서+복사 금지 조문. **반박 5(major→D4⑵)**: e2e arrange 합법 경로 부재(복제=불가시). **반박 6(minor)**: 규범을 닫힌 화이트리스트로(관찰 입력 6축 열거— DRF preserve 반례 격리: 배선 값은 Ninja 조건부·원칙은 무조건). **반박 7(minor)**: admin·OpenAPI 후가공 축을 비입력 예시로·admin 검사기 공백은 ⑦ 재료. **원인론 교정**: 배선 표준은 ninja §2.3 에 이미 무조건 존재 — 본질은 라이선스 제거+복종 사슬 차단.

### 5.3 Goodhart 렌즈 (완료 — 게이트 원안 승인 불가·공격 5계열 재현 실측)

**A1(치명)** base actor 선택 — 위반 선커밋으로 귀속 0 green 재현. **A2(치명)** 부재(#488) 위반은 경로가 없어 exact 매칭 원리상 불가 — 골격 접어도 green 재현. **A3(높음~치명)** 27종 stdout 이질(디렉터리·절대/상대 echo·ⓓ candidate·rename) — 경로 파싱은 조용한 전량 누락면. **A4(높음)** 신 exit 1 ↔ :133 blocker 의미 충돌 — stash·커밋 후 게이트 약화 경로. **A5** (a) .gitignore 은닉 재현 (c) 판정 권위 이원화 (d) 잔존 요약치의 «+1 위장». **→ 판정 차분(N∖L) 채택**: 앵커·현재 두 상태 실행의 위반 라인 차집합=귀속 — base 비선택 바인딩·경로 파싱 소멸로 A1·A2·A3·A4·A5(a)(d) 동시 봉쇄. A5(c)는 역할 분리 조문.

### 5.4 동결 무결성 렌즈 (완료 — 조건부·교정 8건)

**R1(blocker)**: D1-B 원문면(«행위 호출 0»)은 실물 `all_in_order()` classmethod 호출을 못 풀어 **교착 미해소** — B1/B2 로 분해해 사용자 결정(flip 기대치 1 vs 3 수치 명기). **R2(major)**: «backstop 675»의 실체 = `api_error_backstop_matrix.py`(자립형·**6종 전용** — #390/#96/#326 불포함) → C1·D1 의 675 flip 0 은 «구조적 무관»이지 안전 증명이 아님 — 검증 표적을 fixture_matrix+귀속 대조로 교체, 675 는 무영향 확인만. **R3(major)**: D1 값 변경은 RUBRIC :57 위임 경로로 **SH-4 판을 실제로 움직임** + «결과 본 뒤 기준 변경» 모양 → 표준 개정 절차(명시 승인·v2.2.0 스탬프·신규 산출분부터·라운드 1′ 판정 불소급) 필수. **R4(major)**: #96/#326 기계 정본은 final.md 아닌 design spec `:430`/`:640`(final.md 미편입 — spec_lint 이 변경에 무반응·«#18» 서수는 명세 안 무관 규칙과 충돌하니 인용 금지·work_flow.html 재생성 불요 실측). **R5(major)**: H2 검증 «23→24»는 실행 순서와 모순(C1·D1 선반영 시 18 또는 16) → H2 를 최선두 단독 적용으로 재배열+버전 스탬프. **R6(major)**: D1 에 fixture 양·음성 레인 부재 → step 1 에 삽입. **R7(minor~major)**: 675 매트릭스·byte-copy·import 이중성은 안전 실측 — 남는 결정=스모크 레인의 «자리»(fixture_matrix 밖+Makefile 등록 채택)·hermetic(비-git)↔git-필수 긴장 명문화·commands 27목록↔checker_registry 동기 assert·bc_registry_run `assert 27` 보존. **R8(보고만)**: EVAL-METHOD:74 «19개» 등 동결 문서 선재 stale — 이번 범위에서 불수정.
