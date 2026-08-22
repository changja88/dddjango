# T3 저작 워크시트 — command-dddjango

- 원문: `dddjango/commands/dddjango.md` (현재 187행 · 센서스 동결본 176행 — 드리프트 문서)
- spec: `workspace/eval/t3/specs/command-dddjango.spec.json`
- 규모: REF 11절 · 블록 120 · Work 335 (kind: norm 114 · prose 5 · code 1)
- 필독 이행: 발주서 · authoring.md §13~§16 · `ontology_migrate.py` docstring · 파일럿 spec 2건(architecture-ddd-final·implementation-django-ninja-final) · **`dddjango/scripts/check-*.py` 27종 docstring 선두 전수 실독 완료**

## 0. 도구 검증 결과 (제출 조건 기록 — 정직 보고)

```
$ PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py \
    workspace/eval/t3/specs/command-dddjango.spec.json
[migrate] 검증 실패: s007: 좌표 불일치 — 센서스 86-140
EXIT=1
```

**exit 0 미달 — 원인은 spec 이 아니라 «동결 센서스 ↔ 드리프트 원문»의 좌표 충돌이다. spec 측 수리로는 도달 불가.**

- `ontology_migrate.build_graphs()` 는 절마다 ⑴ `sections.tsv` 의 `line_start/line_end` **정확 일치**와 ⑵ 그 스팬의 **sha256 == 센서스 기준선**을 단언한다(도구 주석: «명세 좌표(센서스 동결 시점 기준)»).
- 그런데 원문은 센서스 동결 커밋(`ceb3c6a` · 2026-08-19) 뒤 **6커밋**(`77691d8`·`bdf126c`·`3c03d81`·`bbb8604`·`e18433b`·`4ba4688`)으로 **s007 안에 step 6′ 절이 신설**되며 176→187행이 됐다 — 커밋 열거의 정본은 `ontology/LEDGER.tsv` 의 `command-dddjango/s007` **rebaseline 7행**이고, 6커밋은 `git log -- dddjango/commands/dddjango.md` 실측이다(초판의 «4커밋» 표기는 `77691d8`·`bbb8604` 누락 — 리뷰 F7 수리). 실측 대사:

  | 절 | 센서스 좌표·해시 | 현재 파일 좌표·해시 | 판정 |
  |---|---|---|---|
  | s001~s006 | 1–12 … 73–85 | 동일 | 해시 OK |
  | s007 | 86–140 / `c1f0d29a…` | **86–151 / `faf21286…`** | 본문 개정(+11행) |
  | s008 | 141–144 | **152–155** (해시 동일 `70f81856…`) | 좌표만 +11 이동 |
  | s009 | 145–156 | **156–167** (해시 동일 `9f3b4e3e…`) | 동상 |
  | s010 | 157–168 | **168–179** (해시 동일 `a95172ba…`) | 동상 |
  | s011 | 169–176 | **180–187** (해시 동일 `ccaa3b53…`) | 동상 |

- 즉 **현재 파일 좌표를 쓰면 ⑴에서, 센서스 좌표를 쓰면 ⑵에서** 막힌다(s007 은 어느 좌표로도 해시가 성립하지 않는다). 발주서의 «spec 은 반드시 현재 파일에서 재확정» 지시를 따랐고, 이 충돌은 spec 저작 범위 밖이다.
- 참고: 원장은 이 드리프트를 이미 인지하고 있다 — `ontology/LEDGER.tsv` 에 `command-dddjango/s007` **rebaseline 행 7건**(최신 `faf21286…` = 현재 파일 s007 스팬 해시와 일치)이 append 돼 있다. `sections.tsv`(게이트 1 동결 분모)만 갱신되지 않았다.
- **해소 경로(병합 단계·직렬 소유자 몫, 저작 에이전트 권한 밖)** — 둘 중 하나:
  1. 병합 preflight 에서 `ontology_census.py` 로 이 문서 절 좌표·해시를 **재동결**한 뒤 이 spec 을 그대로 투입(권장 — spec 무수정으로 통과).
  2. `ontology_migrate.load_census_row()` 가 `LEDGER.tsv` 의 최신 rebaseline 행을 기준선으로 받도록 보강.
- **병합 선행 조건(적대 리뷰 F4 확정 — 못박음)**: 이 spec 은 위 ①(또는 ②) **재동결이 끝나고 `ontology_migrate.py` 무수정 재검증이 exit 0 을 내기 전에는 병합 투입 불가**다. 재동결 없이 이 문서를 pass 처리하지 않는다 — 저작 측 수리로 도달 가능한 상태가 아니라는 판정과, 그럼에도 게이트가 미충족이라는 사실을 함께 남긴다.
- **spec 자체의 기계 정합은 별도로 전수 입증했다.** 좌표·해시 기준선만 현재 파일로 치환(=①을 수행한 것과 동치)하고 `build_graphs()` 를 그대로 재생한 결과, 블록 연속·비중첩·절 끝까지 무손실 커버, 헤딩+블록 연결 == 절 스팬(**byte 등가**), kind 5종, 규범 유형 5종, 무소유 0, restates 대상 해소 — **전 단언 통과(exit 0)**:

  ```
  [replay] s001: 블록 4 · Work 6      [replay] s007: 블록 57 · Work 153
  [replay] s002: 블록 7 · Work 9      [replay] s008: 블록 1 · Work 3
  [replay] s003: 블록 12 · Work 22    [replay] s009: 블록 6 · Work 17
  [replay] s004: 블록 1 · Work 5      [replay] s010: 블록 9 · Work 14
  [replay] s005: 블록 9 · Work 39     [replay] s011: 블록 6 · Work 15
  [replay] s006: 블록 8 · Work 52
  [replay] 절 11 · 블록 120 · Work 335 · wiring: enforcedBy 127 · delegatedTo 282
  [replay] ALL ASSERTIONS PASS
  ```

  적대 리뷰 수리 후 재실행값이다(enforcedBy 100→127 — F3·F5 수리분). 재동결 시뮬레이션(`load_census_row` 를 현재 파일 좌표·해시로 대체하고 `build_graphs()` 를 그대로 태운 읽기 전용 실행 — `sections.tsv` 무수정)에서 `ISSUED 신규 335행 · LEDGER 11행 · rules 2992 트리플 · wiring 409 트리플`로 전 단언 통과: **해소 경로 ①을 수행하면 spec 무수정으로 exit 0** 임이 기계 확인됐다.

## 1. census 대사 (발주서 규범 수 ↔ spec Work 수)

| 절 | 헤딩 | 발주서 | spec | 판정·사유 |
|---|---|---|---|---|
| s001 | (전문) | 6 | 6 | 일치. 발주서 «+1 애매» = frontmatter `description` 을 라우터 트리거 규범으로 채번한 것 — 채택. |
| s002 | 산출물 위치 | 9 | 9 | 일치. line 20 의 «`date` 로 얻는다 = 결정성» 은 같은 문장 안 부속절이라 폴더 경로 규범 1 Work 에 병합(§13 문장 해상도). |
| s003 | 진행 가시성 | 22 | 22 | 총계 일치·**분포 상이**. 30~33 4단계 목록은 트래커가 참조하는 목록이라 `prose` 로 판정하고, 그만큼을 line 51(승인 절차) 문단에 배분했다. 배너 코드 펜스에는 «앵커화된 출력 계약» 1 Work 를 부착(발주서 비고 «구속» 채택). |
| s004 | 시작: 모드 판별 | 5 | 5 | 일치(문장 5개 = Work 5). |
| s005 | Phase 0 (G0) | 39 | 39 | 일치. 1차 분해는 52였으나 «— …» 근거절·«*왜*» 리이더·괄호 예외를 **같은 문장 안 부속**으로 보아 본 규범에 병합해 39 로 수렴. 발주서 산정이 옳다. |
| s006 | Phase 1 (G1) | 52 | 52 | 일치(같은 병합 규율). 12-slot 문단(line 84)은 12 Work 로 고정 — slot 수와 우연히 같지만 채번 근거는 문장 단위다. |
| s007 | Phase 2 (G2) | 129 | **153** | **불일치 +24 — 발주서(센서스)가 과소 산정이고 spec 이 옳다.** 발주서 비고의 «step1~7(5+5+4+10+18+81+6)=129» 를 그대로 재현했고(step 별 Work 수 정확 일치), 센서스 동결 뒤 신설된 **step 6′ 재생성 루프**(line 139~149 — 도입 문단 + 하위 불릿 8)에 24 Work 를 추가했다. 6′ 는 센서스 시점에 존재하지 않아 129 에 포함될 수 없다. |
| s008 | Phase 3 | 3 | 3 | 일치. |
| s009 | 수정 모드 | 17 | 17 | 일치. line 166 의 «step6 을 그대로 적용» 은 발주서 비고대로 **정본 역참조(사본 아님)** 라 재진술로 처리하지 않고 자기 Work 3개를 유지했다. |
| s010 | 엣지 처리 | 17 | **14** | **불일치 −3 — spec 이 옳다.** line 176(«checker exit 1/2»)은 센서스 `restate` 열이 «Y:command-dddjango/s007» 로 지목한 **같은 문서 내 재진술 사본**이므로 §15 «정본 1곳만 Work 승격 + 사본 블록에 `djr:restates`» 대로 Work 를 붙이지 않고 `restates → s007/b46`(«실행·종료 계약» 정본) 만 걸었다. 파일럿 판형(architecture-ddd s017-3.2 b1: restates 보유·norms 0)과 동형. 발주서 17 은 사본 3문장을 계수에 포함한 값이다. |
| s011 | 경계 | 15 | 15 | 일치. line 187(게이트 질문·STOP 형식)은 8 Work. |
| **합계** | | **314** | **335** | +21 = **+24**(s007 6′ 드리프트분) **−3**(s010 재진술 사본 미승격) |

## 2. 배선 근거 표 (전 규범)

배선 판정 규율(§16 4원 종합) — 이 문서는 **절차 층(command)** 이라 기본값이 `command-dddjango`(Coordinator)다. 이탈은 넷:

- **(A) registry 27행** → `enforcedBy` = 그 검사기. ①문면이 파일명을 직접 지목 + ④`registry #N` 대응 + ②docstring 선두 문면 일치 — **3원 성립**.
- **(B) 특정 `registry #N` 을 지목해 렌더·selector·차분 계약을 규정한 norm** → 그 #N 검사기(들)에 `enforcedBy`. §16 «담당 검사기의 문면·docstring 근거가 있는데 기본값으로 도피하면 오배선» 의 역방향 적용.
- **(C) `registry_gate.py`·`regen_core.py` 는 `check-*.py` 로스터 27종 밖**(전수 실독으로 확인) → `enforcedBy` 를 걸지 않고 기본값 Coordinator. 도구 이름이 문면에 있다는 사실만으로 배선하지 않는다.
- **(D) 문면이 특정 역할을 «독립 감사»·«소유»·«…가 …한다» 의 주어로 지목** → 그 Agent(기본값 이탈의 문면 근거). 예: 스택 판정=`agent-design-architect`, 입장 표 감사=`agent-discipline-reviewer`, 12-slot=`agent-design-review-api`.

**로스터 전수 자기점검**: 27종 **전부**가 최소 1회 배선에 등장한다(§16 L-F 교훈 — «8종만 보고 9종 오배선» 재발 방지). 초판 계수는 enforcedBy 트리플 100 · delegatedTo 트리플 282 였고, 적대 리뷰 수리(F3 — s007 b12 를 2종→27종 전수, F5 — b46 exit 의미론 대표 3종→5종)로 **enforcedBy 트리플 +27 = 127**, delegatedTo 282 무변이다(Work 총수 335 불변 — 배선 대상만 갈렸다).

| 절 | 블록 | Work label | 유형 | enforcedBy / delegatedTo | 4원 근거 |
|---|---|---|---|---|---|
| s001 | b1 (2–6) | description = 라우터 트리거 선언 | Obligation | D:`command-dddjango` | ①문면 역할명 없음·②27종 docstring 전수 실독에 커맨드 frontmatter 담당 없음·④registry 미대응 — §16 위임 기본값 «command+agents(절차 층)→Coordinator» |
| s001 | b1 (2–6) | allowed-tools 도구 집합 한정 | Permission | D:`command-dddjango` | 동상 — 하네스 도구 허용 집합은 절차 층 계약(검사기 비커버) |
| s001 | b2 (7–8) | Coordinator 역할 — 단계별 게이트 진행 | Obligation | D:`command-dddjango` | ①문면 역할명 «Coordinator» = 절차 소유 주체 자신 — §16 기본값 표 command 행 |
| s001 | b2 (7–8) | 설계 명세·인수 테스트·구현 코드 직접 저작 금지(subagent 위임) | Prohibition | D:`command-dddjango` | ①문면이 위임 대상 3역할을 지목 — 준수 판정은 절차 주체(§16 기본값·s011 경계 절과 동축) |
| s001 | b4 (11–12) | registry #N 접두 표기 규약 | Obligation | D:`command-dddjango` | ④registry #N 공간 자체의 표기 규약 — 검사기는 자기 #N 을 문서 표기로 검사하지 않음(27종 docstring 전수 확인) → §16 기본값 |
| s001 | b4 (11–12) | 무접두 #N = 정본 명세 규칙 번호(범위 표기·본문 미동봉 포함) | Obligation | D:`command-dddjango` | 동상 — 번호 공간 판별은 절차 층 문서 규약 |
| s002 | b1 (14–15) | 스코프 메모 산출 경로 | Obligation | D:`command-dddjango` | ①문면 주어=코디네이터 산출물 · ②27종 docstring 전수에 `.dddjango/` 산출물 경로 담당 없음 → §16 기본값 |
| s002 | b2 (16–16) | 리팩터링 스코프 파일 — 코디네이터 소유·scope.md 와 분리 | Obligation | D:`command-dddjango` | ①문면이 «코디네이터 소유»를 명시 — 소유자 자신이 준수 판정 주체(§16 기본값) |
| s002 | b3 (17–17) | 설계 명세 경로·design-architect 전달 | Obligation | D:`command-dddjango` | ①문면이 전달 주체를 코디로 지정(«이 경로를 design-architect에 전달») → §16 기본값 |
| s002 | b4 (18–19) | 인수 테스트·구현 코드 배치 = 승인 명세의 구조 결정 절 준거 | Obligation | D:`command-dddjango` | ①문면 «네가 그 구조 절을 전달한다» — 전달 의무의 주어가 코디 · 배치 자체의 기계 검사는 check-layer-skeleton 이지만 이 문장은 «전달» 규범이라 절차 층 |
| s002 | b5 (20–21) | 산출물 폴더 경로 규약 — `.dddjango/<생성일>-<기능-slug>/`·생성일은 `date` 로 취득(추측 금지) | Obligation | D:`command-dddjango` | ②27종 docstring 전수 — `.dddjango/` 는 check-idempotency-scope-creep.py 가 «읽는» 입력일 뿐 경로 규약 소유가 아님(docstring (3)(4) 조건절) → §16 기본값 |
| s002 | b6 (22–23) | 한 기능 = 한 폴더 | Obligation | D:`command-dddjango` | 동상 — 산출물 폴더 관리 절차 |
| s002 | b6 (22–23) | 재빌드·수정 모드는 기존 폴더 재사용(새 폴더 생성 금지) | Prohibition | D:`command-dddjango` | 동상 — s005 b9·s009 b2 폴더 절차와 동축 |
| s002 | b7 (24–25) | `.dddjango/` 산출물은 코드와 함께 커밋·.gitignore 금지 | Obligation | D:`command-dddjango` | ②전수 실독 — 커밋·ignore 정책 담당 검사기 없음 → §16 기본값 |
| s002 | b7 (24–25) | 내부 설계 노출이 민감한 레포는 ignore 허용 | Exception | D:`command-dddjango` | 동상 — 위 의무의 명시 예외절 |
| s003 | b1 (27–29) | 1차 진행 신호 = 텍스트 채널 셋(게이트 배너·트래커 라인·한 줄 상태) | Obligation | D:`command-dddjango` | ①문면 주어=코디 출력 채널 · ②27종 docstring 전수에 대화 출력 담당 없음 → §16 기본값 |
| s003 | b1 (27–29) | task 리스트를 보조 채널로 함께 유지 | Obligation | D:`command-dddjango` | 동상 — 하네스 task 도구 사용은 절차 층 |
| s003 | b1 (27–29) | ⓐ 모드 판별 직후·첫 서브에이전트 호출 전 4단계 task 생성 | Obligation | D:`command-dddjango` | 동상 — 발화 시점 계약 |
| s003 | b1 (27–29) | ⓑ 슬라이스 목록 도출 즉시 하위 task 추가 | Obligation | D:`command-dddjango` | 동상 |
| s003 | b1 (27–29) | ⓒ 게이트 배너 직전·단계 전환마다 task 상태 갱신 | Obligation | D:`command-dddjango` | 동상 |
| s003 | b1 (27–29) | task 리스트가 실제 진행과 어긋난 채 승인 질문 금지 | Prohibition | D:`command-dddjango` | 동상 — 게이트 승인 발화 조건 |
| s003 | b6 (35–36) | 전체 트래커 라인·게이트 배너는 게이트(G0·G1·G2)와 마무리에서만 출력 | Obligation | D:`command-dddjango` | ①문면 주어=코디 출력 규율 → §16 기본값(검사기 비커버) |
| s003 | b7 (37–37) | 트래커 라인 형식 | Obligation | D:`command-dddjango` | 동상 — 출력 리터럴 계약 |
| s003 | b8 (38–39) | 게이트 배너는 아래 형식·`{…}` 치환 준수 | Obligation | D:`command-dddjango` | 동상 — 다음 code 블록(앵커화된 출력 계약)의 도입 규범 |
| s003 | b9 (40–49) | 게이트 배너 출력 형식 계약(리터럴 — 상시 필드 포함) | Obligation | D:`command-dddjango` | ①문면 = 앵커화된 출력 계약(구속·발주서 s003 비고) · ②27종 docstring 전수에 배너 형식 담당 없음 → §16 기본값 |
| s003 | b10 (50–52) | 배너 출력 뒤 AskUserQuestion 으로 승인 질의 | Obligation | D:`command-dddjango` | ①문면 주어=코디 게이트 절차 → §16 기본값 |
| s003 | b10 (50–52) | 배너 하단 두 필드(«task 리스트»·«슬라이스 감사»)는 매 게이트 무조건 기재 | Obligation | D:`command-dddjango` | 동상 — 조건부 자기보고 금지 문면 |
| s003 | b10 (50–52) | 닫힌 선택지마다 대가 한 줄 병기 | Obligation | D:`command-dddjango` | 동상 — s011 b6 게이트 질문 형식과 동축(같은 문서 내 상술) |
| s003 | b10 (50–52) | 권고·수정 후보는 AskUserQuestion 선택지로 제시 + 기타=자유입력 상시 유지 | Obligation | D:`command-dddjango` | 동상 |
| s003 | b10 (50–52) | 후보가 도구 옵션 한도 초과 시 전체 번호 목록 선출력 — 후보 무언 탈락 금지 | Prohibition | D:`command-dddjango` | 동상 |
| s003 | b10 (50–52) | 후보 없으면 자유 피드백 수신 후 해당 단계 재실행 | Obligation | D:`command-dddjango` | 동상 |
| s003 | b10 (50–52) | 사용자 승인 전 다음 단계 진행 금지 | Prohibition | D:`command-dddjango` | 동상 — s011 b4 «사용자 승인 없이 게이트 통과 금지»의 상술 |
| s003 | b11 (53–54) | 게이트 사이 전환은 한 줄 상태로만 알린다(형식 `[k/n]`·lens·현재 작업) | Obligation | D:`command-dddjango` | ①문면 주어=코디 출력 규율 → §16 기본값 |
| s003 | b11 (53–54) | 활성 lens 를 한 줄 상태에 포함 | Obligation | D:`command-dddjango` | 동상 |
| s003 | b11 (53–54) | 중계·전체 트래커 재출력 금지(task 상태 갱신은 조용히) | Prohibition | D:`command-dddjango` | 동상 |
| s003 | b12 (55–56) | 서브에이전트 산출물은 경로 + 3~5줄 요지만 — 전문·긴 발췌 재출력 금지 | Prohibition | D:`command-dddjango` | ①문면 주어=코디 · ②전수 실독에 대화 재출력 담당 없음 → §16 기본값 |
| s003 | b12 (55–56) | 사용자 명시 요청 시에만 전문 제시 | Permission | D:`command-dddjango` | 동상 — 위 금지의 명시 예외 |
| s004 | b1 (58–60) | 대상 영역 존재·규모 사전 확인 | Obligation | D:`command-dddjango` | ①문면 주어=코디 모드 판별 절차 → §16 기본값(27종 전수에 담당 없음) |
| s004 | b1 (58–60) | 신규 파일·계약이면 풀 파이프라인·기존 파일 국소 변경이면 수정 모드 | Obligation | D:`command-dddjango` | 동상 |
| s004 | b1 (58–60) | 모호하면 G0 에서 사용자 확인 | Obligation | D:`command-dddjango` | 동상 |
| s004 | b1 (58–60) | 기존 앱·도메인 접촉 사실 기억·재사용(별도 조사 재실행 금지) | Obligation | D:`command-dddjango` | 동상 |
| s004 | b1 (58–60) | 모드 판별축과 배치축의 직교 — 동일시 금지 | Prohibition | D:`command-dddjango` | 동상 |
| s005 | b1 (62–63) | 스코프 메모 작성(무엇/경계/제약) | Obligation | D:`command-dddjango` | ①문면 주어=코디 G0 절차 → §16 기본값 |
| s005 | b1 (62–63) | 미요청 견고성·비기능 요구는 «범위 아님 + 필요 시 G1 제안»으로 기재 | Obligation | D:`command-dddjango` | 동상 — 이 목록이 s006 b5 architect override 앵커가 된다(같은 문서 내 연결) |
| s005 | b1 (62–63) | 무관한 항목의 기계적 나열 금지 | Prohibition | D:`command-dddjango` | 동상 |
| s005 | b2 (64–64) | 스코프에서 활성 설계 lens 추론·제안 | Obligation | D:`command-dddjango` | ①문면 주어=코디 → §16 기본값 |
| s005 | b3 (65–65) | ddd lens 는 항상 활성 | Obligation | D:`command-dddjango` | 동상 — lens 활성 판정은 G0 절차 소유 |
| s005 | b4 (66–66) | api lens 활성 조건 — 외부 관찰 계약의 신설·변경 | Obligation | D:`command-dddjango` | 동상 |
| s005 | b5 (67–67) | db lens 활성 조건 — 스키마·인덱스·제약·트랜잭션·마이그레이션 변화 | Obligation | D:`command-dddjango` | 동상 |
| s005 | b6 (68–68) | 순수 도메인·내부 로직 변경이면 api·db 제외 제안 | Obligation | D:`command-dddjango` | 동상 |
| s005 | b6 (68–68) | 모호하면 활성 쪽으로 제안하고 사용자가 줄이게 한다 | Obligation | D:`command-dddjango` | 동상 |
| s005 | b7 (69–69) | lens 는 관심사(계약·데이터 유무)만 제안 | Obligation | D:`command-dddjango` | ①문면 주어=코디 → §16 기본값 |
| s005 | b7 (69–69) | API 프레임워크는 G0 결정 축이 아니다 — 배너 결정 축 제시·특정 스택 추천 금지 | Prohibition | D:`command-dddjango` | 동상 — «coordinator는 …하지 않는다» 문면 |
| s005 | b7 (69–69) | 스택 판정은 design-architect 소유(경계) | Obligation | D:`agent-design-architect` | ①문면이 소유자를 «design-architect»로 명시(«스택 판정은 design-architect 소유다(경계)») — §16 기본값 이탈의 문면 근거 |
| s005 | b7 (69–69) | 확립 스택 있으면 정체를, 없으면 기본 Django Ninja 를 architect 가 §API스택 결정 순서로 정함 | Obligation | D:`agent-design-architect` | 동상 — 판정 주체가 문면에 명시된 architect |
| s005 | b7 (69–69) | 관찰 입력은 스택 «정체»뿐 — 사용 형태(등록·배선)는 언제나 표준 #105~#112 | Obligation | E:`check-composition-root.py` | ①원문 registry #16 표 행(line 123) «api_router 결선(#105~#112)» + ④registry #16 + ②docstring 실재 문구 «명시적 dddjango-code-json lane은 선택 API object, canonical BC registrar, project URLconf의 직접 import provenance…» + 구현부 방출 실측(#105·#107·#108·#109·#111·#112) — **F2 수리: «api_router 결선(#105~#112)» 는 docstring 문구가 아니라 문서 표 문면**(#105 docstring 0회) |
| s005 | b7 (69–69) | «언제나 표준»의 관할 = 승인 스코프 산출물 — 스코프 밖 기존 배선 이동 금지 | Prohibition | D:`command-dddjango` | ①문면이 승인 스코프(코디 소유)를 관할의 자로 세움 — 이동 권한 판정은 절차 층(§16 기본값) |
| s005 | b7 (69–69) | 이동 권한은 G0 빚 결정→슬라이스 0 뿐 | Exception | D:`command-dddjango` | 동상 — 위 금지의 명시 예외·G0 결정 소유 |
| s005 | b7 (69–69) | 사용자 스택 명시·암시는 표현 그대로 기록·전달(코디 확정 해석 금지·architect 1급 입력) | Obligation | D:`command-dddjango` | ①문면 주어=코디 기록·전달 의무 → §16 기본값 |
| s005 | b8 (70–70) | 리팩터링 스캔 — Phase 2 6번 registry 그대로 타깃 루트 실행해 빚 목록 취득 | Obligation | D:`command-dddjango` | ①문면 주어=코디 스캔 실행 · ④registry 전체를 «그대로» 재사용하는 절차 규범이라 개별 검사기 귀속 없음 → §16 기본값 |
| s005 | b8 (70–70) | 새 검사 생성 금지(백스톱이 내는 위반이 곧 리팩터링 대상) | Prohibition | D:`command-dddjango` | 동상 |
| s005 | b8 (70–70) | API-error-aware checker 와 registry #16 에 `--error-profile auto` 명시 | Obligation | E:`check-error-centralization.py` · E:`check-api-error-controller-contract.py` · E:`check-context-isolation.py` · E:`check-openapi-error-declaration.py` · E:`check-composition-root.py` | ④registry #2·#15·#6·#5·#16 지목 + ②docstring 전수 — 네 checker 는 «profile-gated»(auto 는 schema 의미 미적용) 문면 보유·#16 은 composition selector 소유 |
| s005 | b8 (70–70) | 각 위반에 「손대지 않아도 해로운가」 판정 → «미룰 수 없음» 표시 | Obligation | D:`command-dddjango` | ①문면 주어=코디 판정 절차 → §16 기본값 |
| s005 | b8 (70–70) | brownfield·legacy 는 면제가 아니라 아직 안 갚은 빚 | Prohibition | D:`command-dddjango` | 동상 — houserules §4 역참조이나 판정 시점은 G0 절차 |
| s005 | b8 (70–70) | 스캔 계약 — 도구·TARGET·flag 는 6번 registry 계약 그대로 | Obligation | D:`command-dddjango` | 동상 |
| s005 | b8 (70–70) | 차분 도구(registry_gate.py) 대체 실행 금지 — Phase 0 측정기가 아니다 | Prohibition | D:`command-dddjango` | ①문면이 도구를 지목하나 registry_gate.py 는 check-*.py 로스터 27종 밖(전수 실독 확인) → 절차 층 판정 |
| s005 | b8 (70–70) | 27종 각각의 exact command·exit 기록 — 증거 없는 «빚 0»은 G0 blocker | Obligation | D:`command-dddjango` | ①문면 주어=코디 기록 의무·G0 차단 판정 → §16 기본값 |
| s005 | b8 (70–70) | «실행 불능» 정의 — 정상 exit 1 diagnostic 은 «교정 후 재실행» 대상 | Exception | D:`command-dddjango` | 동상 — exit 의미 해석은 코디 판정(검사기는 자기 exit 만 낸다) |
| s005 | b8 (70–70) | 스캔 범위 = 대상 BC 경로 진단 — «미룰 수 없음»은 경로 무관 잔류 | Obligation | D:`command-dddjango` | 동상 |
| s005 | b8 (70–70) | 타 BC 확장은 스코프 확장·G0 재승인 사안 — «해로움»은 동작·안전 파괴 한정 | Prohibition | D:`command-dddjango` | 동상 |
| s005 | b9 (71–72) | G0 배너 전 항상 `ls .dddjango/` 조회 — 재빌드 여부 자기 판정 금지 | Obligation | D:`command-dddjango` | ①문면 주어=코디 · ②전수 실독에 산출물 폴더 조회 담당 없음 → §16 기본값 |
| s005 | b9 (71–72) | G0 배너로 스코프 메모 + 제안 lens 제시·승인 | Obligation | D:`command-dddjango` | 동상 |
| s005 | b9 (71–72) | 빚 1건 이상이면 배너 기재 + AskUserQuestion ⓐ/ⓑ 필수 발화 | Obligation | D:`command-dddjango` | 동상 — 게이트 질문 채널 계약(s011 b6 과 동축) |
| s005 | b9 (71–72) | «미룰 수 없음» 항목엔 ⓑ 선택지 없음 — 코디 대리 판정 금지 | Prohibition | D:`command-dddjango` | 동상 |
| s005 | b9 (71–72) | 승인 뒤 스캔 결과 표·사용자 결정·슬라이스 0 내용을 refactor-scope.md 에 기록 | Obligation | D:`command-dddjango` | 동상 — 코디 소유 파일 |
| s005 | b9 (71–72) | ⓐ 항목은 스코프 메모에 «슬라이스 0 = 리팩터링(동작 불변)»으로 기재·architect 전달 | Obligation | D:`command-dddjango` | 동상 |
| s005 | b9 (71–72) | 미룬 목록의 다음 작업 이월·누적 금지 | Prohibition | D:`command-dddjango` | 동상 |
| s005 | b9 (71–72) | ⓐ 목록은 G0 배너 승인 시점 동결 — G2 red 소급 기입 금지 | Prohibition | D:`command-dddjango` | 동상 |
| s005 | b9 (71–72) | 기존 영역 접촉 신호 시 «이 기능을 둘 자리» 선택 추가·선택을 스코프 메모에 기록·전달 | Obligation | D:`command-dddjango` | 동상 |
| s005 | b9 (71–72) | 코디는 갈림길 표면화만 — 배치의 설계 근거 생성 금지(architect 소유) | Prohibition | D:`command-dddjango` | ①문면이 경계를 코디 금지로 적음 — 금지의 준수 판정은 절차 주체(s011 경계 절과 동축) |
| s005 | b9 (71–72) | 폴더 목록 선택(ⓐ 재사용 / ⓑ 신규)·확정 구체 경로 전달·이후 재계산 금지 | Obligation | D:`command-dddjango` | 동상 — s002 b6·s009 b2 폴더 절차와 동축 |
| s006 | b1 (74–76) | Phase 1 은 승인된 스코프와 활성 lens 로 진행 | Obligation | D:`command-dddjango` | ①문면 주어=코디 단계 진행 → §16 기본값 |
| s006 | b2 (77–77) | design-architect 호출 — `dddjango:` 한정 표기 | Obligation | D:`command-dddjango` | ①문면 주어=코디 호출 절차 → §16 기본값 |
| s006 | b2 (77–77) | architect 입력 3종(스코프 메모·활성 lens·명세 저장 경로) 전달 | Obligation | D:`command-dddjango` | 동상 — 입력 구성은 코디 소유 |
| s006 | b2 (77–77) | architect 는 패키지·테스트 구조 결정을 명세에 포함 | Obligation | D:`agent-design-architect` | ①문면 주어가 «architect» — 산출 의무의 소유자가 판정 주체(§16 기본값 이탈 문면 근거) |
| s006 | b2 (77–77) | 모든 영구 test artifact 후보의 최소 입장 표(6열) 포함 | Obligation | D:`agent-discipline-reviewer` | ①문면 + s006 b4 «discipline-reviewer 가 입장 표의 열…을 독립 감사» — 판정 주체를 문면이 명시(기본값 이탈 근거) |
| s006 | b2 (77–77) | decision 은 일곱 값만 사용 | Prohibition | D:`agent-discipline-reviewer` | 동상 — «일곱 decision» 독립 감사 대상을 문면이 discipline-reviewer 로 지정 |
| s006 | b3 (78–78) | 활성 lens 별 리뷰어 병렬 호출 | Obligation | D:`command-dddjango` | ①문면 주어=코디 dispatch → §16 기본값 |
| s006 | b3 (78–78) | 병렬의 정의 = 한 응답 안의 서브에이전트 호출 다발 | Obligation | D:`command-dddjango` | 동상 |
| s006 | b3 (78–78) | 순차 호출·연속 «개별» 응답 백그라운드 배차는 병렬이 아니다 | Prohibition | D:`command-dddjango` | 동상 |
| s006 | b3 (78–78) | 입력 준비가 다발보다 앞 — 필수 입력 공백 금지 | Obligation | D:`command-dddjango` | 동상 |
| s006 | b3 (78–78) | 리뷰어 둘 이상 호출 전건에 적용 — 하나만 재호출은 단독 정당 | Exception | D:`command-dddjango` | 동상 — 위 금지의 명시 범위 한정 |
| s006 | b3 (78–78) | 다발 누락 시 늦은 단독 호출로라도 반드시 호출하고 미준수 보고 | Obligation | D:`command-dddjango` | 동상 |
| s006 | b3 (78–78) | G1 배너에 다발 크기 한 줄 기재 | Obligation | D:`command-dddjango` | 동상 |
| s006 | b3 (78–78) | 각 리뷰어에 architect 명세 초안만 제공(타 리뷰 노트·코드 금지 — 편향 방지) | Prohibition | D:`command-dddjango` | 동상 |
| s006 | b3 (78–78) | 리뷰어 입력에 플러그인 설치 루트 절대 경로 동봉 | Obligation | D:`command-dddjango` | 동상 — 발주서 비고: codex 판에 부재한 문장(정본 고유) |
| s006 | b3 (78–78) | API/DB reviewer 는 decision 없이 테스트를 의무화하지 않는다 | Prohibition | D:`agent-design-review-api` · D:`agent-design-review-db` | ①문면 주어가 «API/DB reviewer» — §16 기본값 표 architecture-api/db 행의 리뷰 에이전트와 일치 |
| s006 | b3 (78–78) | 산출 = lens 별 리뷰 노트 | Obligation | D:`command-dddjango` | ①문면 산출 계약 — 수신·검사 주체가 코디 → §16 기본값 |
| s006 | b3 (78–78) | 노트 수신 시 형식 구문 검사·반송(존재 검사만·원문 대조 금지) | Obligation | D:`command-dddjango` | ①문면 주어=코디 반송 판정 → §16 기본값 |
| s006 | b4 (79–79) | discipline-reviewer 를 Phase 1 lightweight 모드로 항상 호출(병렬 다발 합류) | Obligation | D:`command-dddjango` | ①문면 주어=코디 호출 절차 → §16 기본값 |
| s006 | b4 (79–79) | 입장 표의 열·일곱 decision·protected contract·독자 failure·기존 coverage·owner 독립 감사 | Obligation | D:`agent-discipline-reviewer` | ①문면이 감사 주체를 «discipline-reviewer»로 명시 + §16 기본값 표 «rule-owner-map ⓓ 유일 관례» — 기본값 이탈이 아니라 문면·관례 합치 |
| s006 | b4 (79–79) | pending·부당한 add·의미 보존 재조직의 새 case/assertion/Red 를 G1 전에 포착 | Obligation | D:`agent-discipline-reviewer` | 동상 — 감사 항목을 문면이 열거 |
| s006 | b4 (79–79) | Error response contract scope 는 project-wide tree 동봉·물리 소유권·우회 추가 점검 | Obligation | D:`agent-discipline-reviewer` | 동상 — s007 b10 «discipline-reviewer 는 물리 소유권과 입장/diff 일치를 본다»와 동축 |
| s006 | b4 (79–79) | Phase 1 lightweight 에 구현 코드·테스트 diff·실행 결과·슬라이스 요구 금지 | Prohibition | D:`command-dddjango` | ①문면이 입력 구성을 금지 — 입력 구성 주체가 코디 → §16 기본값 |
| s006 | b5 (80–80) | design-architect 재호출로 리뷰 노트 반영·리뷰어 충돌 중재 | Obligation | D:`command-dddjango` | ①문면 주어=코디 재호출 절차 → §16 기본값 |
| s006 | b5 (80–80) | scope.md 의 Y 항목은 기본(미적용) 현재-상태 commit + 배너 override 항목 산출 | Obligation | D:`agent-design-architect` | ①문면 주어가 «architect가 …산출한다» — 산출 의무 소유자가 판정 주체 |
| s006 | b5 (80–80) | architect 의 'Y감이냐' 자체 판정 금지 — scope.md 목록을 앵커로 | Prohibition | D:`agent-design-architect` | 동상 — 금지의 주어가 architect |
| s006 | b5 (80–80) | 스스로 해소 못 하는 트레이드오프(Z)만 미해결 옵션으로 잔류 | Obligation | D:`agent-design-architect` | 동상 |
| s006 | b6 (81–81) | G1 배너로 최종 설계 명세(경로) 제시·승인 | Obligation | D:`command-dddjango` | ①문면 주어=코디 게이트 → §16 기본값 |
| s006 | b6 (81–81) | Y 는 «기본=미적용·추가할래?», Z 는 옵션으로 표시 | Obligation | D:`command-dddjango` | 동상 |
| s006 | b6 (81–81) | 배너에 일곱 decision 을 decision 별로 나열·각 행 owner/path 표시(없으면 «없음») | Obligation | D:`command-dddjango` | 동상 — 배너 필드 계약 |
| s006 | b6 (81–81) | pending 잔존 시 승인 입력을 Phase 2 진입으로 해석 금지·한정 설계 질문 반송 | Prohibition | D:`command-dddjango` | 동상 — s010 b5 «영구 테스트 입장 미확정» 처리와 동축 |
| s006 | b6 (81–81) | 의미 보존 재조직은 새 case·assertion·Red 없음과 전후 보호 동일 기록까지 제시 | Obligation | D:`agent-discipline-reviewer` | ①문면 + s006 b4·s007 b6 «의미 보존 재조직의 전후 보호»를 discipline-reviewer 가 감사 — 판정 주체 문면 명시 |
| s006 | b6 (81–81) | 설계 명세는 이후 테스트·코드의 단일 근거 | Obligation | D:`command-dddjango` | 동상 — s011 b2 «단일 근거» 경계 조항과 동축(같은 문서 내 상술) |
| s006 | b7 (82–83) | ① 기본 수락 → architect 재호출 없이 Phase 2 진행 | Permission | D:`command-dddjango` | ①문면 주어=코디 분기 절차 → §16 기본값 |
| s006 | b7 (82–83) | ② Y 채택 → Coordinator 가 scope.md 를 단독 줄로 갱신(부정 토큰 동거 금지) | Obligation | D:`command-dddjango` | ①문면이 갱신 주체를 «너(Coordinator)»로 명시 → §16 기본값 정확 일치 |
| s006 | b7 (82–83) | ②·③ 은 architect 를 G1 override 입력으로 재호출해 해당 절만 반영 | Obligation | D:`command-dddjango` | 동상 |
| s006 | b7 (82–83) | override 반영 후에는 ①과 동일하게 Phase 2 진행 | Obligation | D:`command-dddjango` | 동상 |
| s006 | b7 (82–83) | design-spec.md 직접 저작 금지 — scope.md 만 예외 | Prohibition | D:`command-dddjango` | ①문면 금지의 주어=코디 → §16 기본값 · s011 b1 경계 조항의 상술 |
| s006 | b7 (82–83) | design-spec 전속은 경로 불문 — 승인문이 지시해도 architect 재호출로 위임 | Prohibition | D:`command-dddjango` | 동상 |
| s006 | b7 (82–83) | scope.md 에는 스코프 결정만 — 설계 결정·입장표 해석 전재·지시문 우회 금지 | Prohibition | D:`command-dddjango` | 동상 |
| s006 | b8 (84–85) | Ninja 계약 변경 scope 는 G1 제시 전·dispatch 직전 current design-spec 재독 | Obligation | D:`command-dddjango` | ①문면 주어=코디 재독 의무 → §16 기본값 |
| s006 | b8 (84–85) | Error response contract 12-slot 의 label 과 순서 정확 준수 | Obligation | D:`agent-design-review-api` | ①문면 = API 오류 계약 슬롯 · §16 기본값 표 architecture-api 행 → design-review-api(s007 b10 «API reviewer 는 public wire/HTTP/OpenAPI evidence» 로 확인) |
| s006 | b8 (84–85) | 12 슬롯 모두 구체·선택 profile 정합·상호 일관 | Obligation | D:`agent-design-review-api` | 동상 |
| s006 | b8 (84–85) | `none \| not applicable` 은 허용 slot + 이유·evidence 동반 시에만 구체값 | Exception | D:`agent-design-review-api` | 동상 — 위 의무의 명시 예외절 |
| s006 | b8 (84–85) | dddjango-code-json 은 slot 5 값 집합과 slot 6 common shape 필수 | Obligation | E:`check-error-centralization.py` | ②docstring «``dddjango-code-json`` validates the canonical common/BC FrameworkErrorSchema modules, project inventory correspondence» + ④registry #2 — **F9 수리 한정 병기: 검사 대상은 슬롯의 «코드 대응물»**(검사기는 design-spec 문서를 읽지 않는다). 슬롯 «기재» 완전성 축은 이웃 slot 규범과 같이 `agent-design-review-api`·코디 소유 |
| s006 | b8 (84–85) | plugin 기본 property 목록 없음 — 관찰된/승인된 exact shape 만 사용 | Prohibition | E:`check-error-centralization.py` | 동상 — #2 의 shape·source contract 판정 축(docstring «wire-code uniqueness, and narrow direct raw-string discriminator forms») |
| s006 | b8 (84–85) | slot 9 의 <Bc>ErrorCode 좁힘에 따른 required 승격은 canon | Permission | E:`check-error-centralization.py` | 동상 — BC ErrorSchema base 계약은 #2 소유(s007 registry #2 문면 «Enum/base/concrete/no-arg source contract») |
| s006 | b8 (84–85) | slots 7–9 는 이유와 함께 none 가능하되 slots 10–12 는 공백 금지 | Obligation | D:`agent-design-review-api` | ①문면 = 12-slot 정합 판정 · §16 기본값 표 architecture-api 행 |
| s006 | b8 (84–85) | preserve-established slots 5–12 는 관찰 artifact·evidence 한정 — code-profile 강제 금지 | Prohibition | E:`check-api-error-controller-contract.py` | ②check-api-error-controller-contract.py docstring «``auto`` and ``preserve-established`` … add no new error-mapping semantics» + ④registry #15 대응 |
| s006 | b8 (84–85) | 누락·모호·모순 시 승인 입력이 있어도 Phase 2 진입 금지·G1/G1′ 반송(코디 대리 결정 금지) | Prohibition | D:`command-dddjango` | ①문면이 «Coordinator는 slot 값을 대신 결정하거나 조용히 보충·수정하지 않는다» — 금지 주어가 코디 → §16 기본값 |
| s006 | b8 (84–85) | shape 변경은 별도 명시 사용자 승인 evidence 필수 — 일반 G1 승인으로 갈음 금지(신규 최초 shape 동일) | Prohibition | D:`command-dddjango` | ①문면이 «G1을 차단한다»로 게이트 차단 주체를 코디로 지정 → §16 기본값(승인 채널은 절차 층 소유) |
| s006 | b8 (84–85) | 재작업으로 API semantic·물리 구조 slot 이 바뀌면 해당 reviewer 재호출 후 새 G1 제시 | Obligation | D:`command-dddjango` | ①문면 주어=코디 재호출 절차 → §16 기본값 |
| s007 | b1 (87–88) | 승인된 입장 표를 먼저 읽는다 | Obligation | D:`command-dddjango` | ①문면 주어=코디 Phase 2 진입 절차 → §16 기본값 |
| s007 | b1 (87–88) | 새 영구 테스트 artifact 가 필요한 add/update 행이 있을 때만 러너 준비·settings 기록 | Obligation | E:`check-test-config.py` | ②check-test-config.py docstring ⑴ «pytest ↔ Django settings 바인딩 … DJANGO_SETTINGS_MODULE·addopts --ds=» + ④registry #12 대응 — 러너 바인딩의 기계 소유자 |
| s007 | b1 (87–88) | reuse 는 기존 러너로 지정 anchor 만 실행 — dependency·manifest·runner config 변경 금지 | Prohibition | D:`command-dddjango` | ①문면 = decision 별 dispatch 규율 · ②전수 실독에 decision 라우팅 담당 검사기 없음 → §16 기본값 |
| s007 | b1 (87–88) | retain·reject·remove 만 있는 변경은 runner setup write 금지 | Prohibition | D:`command-dddjango` | 동상 |
| s007 | b1 (87–88) | 기존 TestCase 스위트의 pytest 재작성 금지 — 승인 add/update 에만 pytest 관용구 | Prohibition | D:`agent-discipline-reviewer` | ①문면 = 테스트 편집 규율 · §16 기본값 표 «discipline-*·implementation-* → discipline-reviewer»(테스트 diff 감사 주체는 s007 b6 문면에서 discipline-reviewer) |
| s007 | b2 (89–89) | 변경 앵커로 관련 테스트만 한정 검색해 existing authoritative coverage 확인 | Obligation | D:`command-dddjango` | ①문면 주어=코디 dispatch 준비 → §16 기본값 |
| s007 | b2 (89–89) | decision 을 다시 만들지 말고 decision 별로 dispatch | Prohibition | D:`command-dddjango` | 동상 |
| s007 | b2 (89–89) | 명시 승인된 의미 보존 retain 재조직만 새 case·assertion·Red 없이 전후 보호 기록 | Exception | D:`agent-discipline-reviewer` | ①문면 + s007 b6 «의미 보존 재조직의 전후 보호»를 discipline-reviewer 가 감사 — 판정 주체 문면 명시 |
| s007 | b2 (89–89) | 소유 라우팅 — 외부 계약은 acceptance-tester·내부는 coder | Obligation | D:`command-dddjango` | ①문면 주어=코디 라우팅 → §16 기본값 |
| s007 | b2 (89–89) | 전체 suite 를 discovery 대용으로 사용 금지 | Prohibition | D:`command-dddjango` | 동상 |
| s007 | b3 (90–90) | 제품 구현 단위로 슬라이스 목록 도출·관련 입장 행 부착 | Obligation | D:`command-dddjango` | ①문면 주어=코디 → §16 기본값 |
| s007 | b3 (90–90) | G0 «지금 정리» 빚은 슬라이스 0(동작 불변)으로 앞에 — 리팩터링·기능 변경 혼합 금지 | Prohibition | D:`command-dddjango` | 동상 — s005 b9 ⓐ 결정의 소비 지점 |
| s007 | b3 (90–90) | 후보·recipe·coverage 목표만으로 test-adjustment/unit-Red 슬라이스 생성 금지 | Prohibition | D:`agent-discipline-reviewer` | ①문면 = 테스트 슬라이스 정당성 감사 · §16 기본값 표 discipline-reviewer(테스트 입장 감사 주체) |
| s007 | b3 (90–90) | add/update Red 와 승인 remove 대상만 test edit 입력 — reuse anchor 는 슬라이스 수 무압박 | Obligation | D:`command-dddjango` | ①문면 주어=코디 입력 구성 → §16 기본값 |
| s007 | b4 (91–91) | 슬라이스마다 coder 호출 — 입력 6종(플러그인 설치 루트 절대 경로 포함) | Obligation | D:`command-dddjango` | ①문면 주어=코디 호출·입력 구성 → §16 기본값 · 발주서 비고: codex 판에 플러그인 루트 부재(정본 고유) |
| s007 | b4 (91–91) | coder 는 자기 소유 add/update 만 단위 Red→Green→Refactor·remove 는 exact target 만 | Obligation | D:`agent-coder` | ①문면 주어가 «coder» — 이행 의무 소유자가 판정 주체(§16 기본값 표 command+agents 절차 층 안의 역할 귀속) |
| s007 | b4 (91–91) | reuse/reject 에서 내부 test write·외부 계약 테스트 수정 금지 | Prohibition | D:`agent-coder` | 동상 — 금지 주어가 coder |
| s007 | b4 (91–91) | 첫 Green 직후 동일 역할이 Red 용 비계를 즉시 제거 | Obligation | D:`agent-discipline-reviewer` | ①문면 + s007 b6 «첫-Green 비계 잔존을 감사한다» — 판정 주체를 문면이 discipline-reviewer 로 지정 |
| s007 | b4 (91–91) | 작업 전 기존 비계 임의 삭제 금지 | Prohibition | D:`agent-coder` | 동상 — 금지 주어가 coder(이행) |
| s007 | b5 (92–92) | 슬라이스 3개 이상이면 슬라이스마다 discipline-reviewer 경량 감사 호출·coder 반영 | Obligation | D:`command-dddjango` | ①문면 주어=코디 호출 절차 → §16 기본값 |
| s007 | b5 (92–92) | 마지막 슬라이스의 홀리스틱 갈음은 조건부 — 입력 명시 + 전량 실독 확인 | Permission | D:`command-dddjango` | 동상 — 갈음 성립 판정은 코디(2026-08-17 DR-68 개정) |
| s007 | b5 (92–92) | 마지막 홀리스틱 1회는 갈음 여부와 무관하게 존치 | Obligation | D:`command-dddjango` | 동상 |
| s007 | b5 (92–92) | 비-마지막 슬라이스 경량 감사 발견은 다음 게이트 전 원작성자 반송으로 완료 | Obligation | D:`command-dddjango` | 동상 |
| s007 | b5 (92–92) | 감사 범위와 다음 슬라이스 작업 파일이 겹치면 감사 완료 후 배차 | Obligation | D:`command-dddjango` | 동상 — «같은 파일 병렬 편집 금지»의 적용 |
| s007 | b6 (93–93) | discipline-reviewer 를 Phase 2 implementation 모드로 호출 | Obligation | D:`command-dddjango` | ①문면 주어=코디 호출 → §16 기본값 |
| s007 | b6 (93–93) | 필수 입력 5종(코드+테스트·승인 입장 표·역할별 최소 조정 보고·test diff·실행 결과·슬라이스 목록) | Obligation | D:`command-dddjango` | 동상 — 입력 구성은 코디 소유 |
| s007 | b6 (93–93) | 기본은 G2 직전 1회·슬라이스 ≥3 이면 슬라이스별 + 마지막 홀리스틱 1회 | Obligation | D:`command-dddjango` | 동상 |
| s007 | b6 (93–93) | reviewer 감사 항목 — diff hunk 대조·write 0·무편집·종료 근거·전후 보호·비계 잔존·migration lifecycle 보존 | Obligation | D:`agent-discipline-reviewer` | ①문면 주어가 «reviewer» + §16 기본값 표 «rule-owner-map ⓓ 유일 관례» — 감사 항목의 판정 주체 |
| s007 | b6 (93–93) | 지적 라우팅 — 외부 assertion=acceptance-tester·내부/일반=coder·입장/설계=architect 경유 반송 | Obligation | D:`command-dddjango` | ①문면 주어=코디 라우팅 → §16 기본값 |
| s007 | b7 (94–94) | 외부·내부 assertion 혼재 파일의 두 역할 병렬 편집 금지 | Prohibition | D:`command-dddjango` | ①문면 주어=코디 배차 규율 → §16 기본값 |
| s007 | b7 (94–94) | acceptance-tester→coder 순 호출·다음 역할은 최신 파일 재독 | Obligation | D:`command-dddjango` | 동상 |
| s007 | b8 (95–95) | 각 작성 역할은 최소 근거만 고정 5필드 형식으로 반환 | Obligation | D:`agent-discipline-reviewer` | ①문면 = 역할 반환 형식 · s007 b6 «역할별 최소 조정 보고»를 reviewer 가 입력으로 감사 — 판정 주체 문면 근거 |
| s007 | b8 (95–95) | reuse/remove/의미 보존 재조직별 기재 항목 준수 | Obligation | D:`agent-discipline-reviewer` | 동상 |
| s007 | b8 (95–95) | 별도 장부·snapshot·receipt·state machine 생성 금지 | Prohibition | D:`agent-discipline-reviewer` | 동상 — 산출물 증식 금지의 감사 주체 |
| s007 | b9 (96–96) | 관련 테스트와 기존 전체 suite 를 코디네이터가 직접 실행 | Obligation | D:`command-dddjango` | ①문면이 실행 주체를 «너(코디네이터)»로 명시 → §16 기본값 정확 일치 |
| s007 | b9 (96–96) | 관련 실패는 해결하거나 pending 으로 설계 반송 | Obligation | D:`command-dddjango` | 동상 |
| s007 | b9 (96–96) | 무관/관련의 자는 기준선 실측 — 무관 실패는 편집 금지·별도 보고·전체 green 주장 금지 | Prohibition | D:`command-dddjango` | 동상 — s009 b4·s010 b8 과 동축(같은 문서 내 재등장) |
| s007 | b10 (97–97) | Error response contract scope 의 모든 역할에 승인 12-slot 전체와 관련 입장 행 전달 | Obligation | D:`command-dddjango` | ①문면 주어=코디 입력 구성 → §16 기본값 |
| s007 | b10 (97–97) | 역할별 시야 한정(API reviewer·acceptance-tester·coder·discipline-reviewer) | Obligation | D:`agent-design-review-api` · D:`agent-discipline-reviewer` | ①문면이 역할별 시야를 열거 — API 축은 design-review-api(§16 표 architecture-api 행)·물리 소유권 축은 discipline-reviewer(ⓓ 관례) |
| s007 | b10 (97–97) | private Pydantic mechanics 의 자동 영구 테스트 변환 금지 | Prohibition | D:`agent-discipline-reviewer` | ①문면 = 영구 테스트 입장 감사 · §16 기본값 표 discipline-reviewer |
| s007 | b11 (98–98) | 세 토큰(TREE/STOP/RUNTIME) 중 하나라도 보고되면 G2 blocker | Prohibition | D:`command-dddjango` | ①문면 = 게이트 차단 판정 → §16 기본값(차단 주체는 코디) |
| s007 | b11 (98–98) | shape·tree·profile·field·return form 의 조용한 변경 금지 — architect 경유 반송·재승인 | Prohibition | D:`command-dddjango` | 동상 — s010 b6 Contract mismatch 처리와 동축 |
| s007 | b12 (99–100) | G2 배너 직전 타깃 프로젝트 루트(manage.py check 와 같은 cwd)에서 registry 실행 | Obligation | D:`command-dddjango` | ①문면 주어=코디 실행 절차 → §16 기본값(개별 검사기가 아니라 registry 전체 운용 규범) |
| s007 | b12 (99–100) | positional TARGET 도 루트(`.`) — BC 폴더·application/ 컨테이너 TARGET 금지 | Prohibition | E:**27종 전수**(registry #1~#27) | ①문면이 거절 주체를 «검사기»로 명시 + ②공유 모듈 `checker_target.py` docstring «27종 전부가 이 모듈을 거치므로 … 조용 통과 대신 소리내어 거절한다» + 구현부 실측(27종 전부 `bc_shaped_target_reason()` 호출 → 사용 오류 exit 1 / `UsageError`) — **F3 수리: 2종 임의 선정 철회·«채택 신호 꺼짐=exit 1» 오설명 삭제**(신호 꺼짐은 exit 0) |
| s007 | b12 (99–100) | 게이트 판정은 «판정 차분»이다 | Obligation | D:`command-dddjango` | ①문면 = 게이트 판정 규약 · registry_gate.py 는 check-*.py 로스터 27종 밖(전수 실독 확인) → §16 기본값 |
| s007 | b12 (99–100) | 첫 서브에이전트 파견 직전 `git rev-parse HEAD` 를 build_anchor 에 기록 | Obligation | D:`command-dddjango` | 동상 — 앵커 기록 주체가 코디 |
| s007 | b12 (99–100) | `registry_gate.py . --anchor $(cat …/build_anchor)` 실행 | Obligation | D:`command-dddjango` | 동상 |
| s007 | b12 (99–100) | 게이트 증거 = 귀속 0 + legacy 잔존 별도 보고 | Obligation | D:`command-dddjango` | 동상 |
| s007 | b12 (99–100) | 귀속 0 ≠ 전체 clean — 좁힌 TARGET·즉석 selector 부분 green 은 게이트 증거 아님 | Prohibition | D:`command-dddjango` | 동상 |
| s007 | b12 (99–100) | Phase 0 빚 스캔과 별개로 여기서 한 번 더 실행(스캔은 이 실행의 «이동»이 아니다) | Obligation | D:`command-dddjango` | 동상 — s005 b8 스캔 계약과 동축 |
| s007 | b12 (99–100) | build_anchor 는 기능 폴더에 한 번만 — 이미 있으면 재기록 금지(차분 세탁) | Prohibition | D:`command-dddjango` | 동상 |
| s007 | b12 (99–100) | 승인 스코프 산출물 목록 밖 파일의 귀속은 1차 처방이 그 변경의 철회 | Obligation | D:`command-dddjango` | 동상 — s011 b6 «규정이 1차 처방을 이미 정한 STOP» 과 동축 |
| s007 | b13 (101–101) | checker command 렌더 전 승인 12-slot inventory 재독·프로젝트 전체 집합 대조 | Obligation | D:`command-dddjango` | ①문면 = 코디의 preflight 절차(«checker 가 membership 을 추론하게 하지 않고») → §16 기본값 |
| s007 | b13 (101–101) | 같은 profile 의 명시적 공유일 때만 동일 project-relative path 를 dedupe | Obligation | E:`check-error-centralization.py` | ②docstring «project inventory correspondence» + ④registry #2 «project-wide code inventory» — **F9 수리 한정 병기: 검사 대상은 selector 가 가리키는 코드 실물의 inventory 대응**이지 preflight 문서 절차가 아니다(절차 축은 같은 블록의 코디 규범) |
| s007 | b13 (101–101) | inventory 불완전·역할 충돌·mixed-profile 공유·다중 API instance 면 STOP_FOR_USER_APPROVAL 로 G1 반송 | Prohibition | D:`command-dddjango` | ①문면 = STOP 발화·반송 판정(절차 소유) → §16 기본값 · s011 b6 STOP 기록 형식과 동축 |
| s007 | b13 (101–101) | 관찰된 현행 구성 그대로의 inventory 는 완전 — 표준형 registrar 부재는 불완전이 아니다 | Exception | D:`command-dddjango` | 동상 — 2026-08-13 명문화된 «불완전» 판정의 한정(오판이 표준형 강제로 번지는 것을 차단) |
| s007 | b13 (101–101) | `error-bc ⊆ scope-bc` 검증 | Obligation | E:`check-error-centralization.py` | ②docstring «``dddjango-code-json`` validates the canonical common/BC … modules, project inventory correspondence» + ④registry #2 — selector 정합의 기계 소유자 |
| s007 | b13 (101–101) | 모든 selector path 는 project-relative · `--scope` 는 membership selector 가 아니다 | Prohibition | E:`check-error-centralization.py` · E:`check-api-error-controller-contract.py` | ②두 docstring 모두 «profile- and source-selected»/«selectors it supplies» 로 selector 계약을 자기 소유로 선언 + ④registry #2·#15 |
| s007 | b14 (102–102) | 승인된 각 error-response scope 마다 registry #2·#15·#6·#5 에 selector 전량 렌더 | Obligation | E:`check-error-centralization.py` · E:`check-api-error-controller-contract.py` · E:`check-context-isolation.py` · E:`check-openapi-error-declaration.py` | ④문면이 registry #2·#15·#6·#5 를 직접 지목 + ②각 docstring 의 selector 계약(«usage or analysis error» exit 1) — 미충족 selector 는 검사기 자신이 exit 1 로 문다 |
| s007 | b14 (102–102) | registry #2 에 dedupe 한 complete project inventories 추가 | Obligation | E:`check-error-centralization.py` | ④registry #2 지목 + ②docstring «project inventory correspondence» |
| s007 | b14 (102–102) | 내용 없는 골격 파일(빈 모듈)은 inventory 에서 제외 | Prohibition | E:`check-error-centralization.py` · E:`check-layer-skeleton.py` | ④#2 inventory + ②check-layer-skeleton.py docstring «#488 고정(·재등장) 칸은 부모가 있으면 반드시 있다 — … 파일도 비면 빈 파일로» — **F9 수리 한정 병기: 두 검사기가 무는 것은 빈 골격 «코드 실물» 의 처분**이고 렌더 목록 기재 행위 자체는 코디 소유 |
| s007 | b14 (102–102) | registry #2·#15·#6·#5 에 `--anchor` 렌더 | Obligation | E:`check-error-centralization.py` · E:`check-api-error-controller-contract.py` · E:`check-context-isolation.py` · E:`check-openapi-error-declaration.py` | ④네 registry 지목 + ②각 docstring 의 exit 2 계약(«contract blocker») — 앵커 차분은 검사기 자신이 수행 |
| s007 | b14 (102–102) | 승인 «이관 빚» 목록이 있으면 `--legacy-debt-file` 동반 | Obligation | D:`command-dddjango` | ①문면 = 코디의 렌더 의무 · 빚 목록 승인은 G0/STOP 절차 소유 → §16 기본값 |
| s007 | b14 (102–102) | 빈 반복 집합에 flag 발명 금지 — inventory 공백의 승인 근거는 12-slot 에 | Prohibition | D:`command-dddjango` | 동상 — 렌더 주체가 코디 |
| s007 | b15 (103–103) | registry #16 에 positional target·common selectors·`--anchor`(+`--legacy-debt-file`) 동일 값 렌더 | Obligation | E:`check-composition-root.py` | ④문면이 registry #16 을 직접 지목 + ②check-composition-root.py docstring «명시적 dddjango-code-json lane은 선택 API object, canonical BC registrar, project URLconf 의 직접 import provenance» |
| s007 | b15 (103–103) | dddjango-code-json 에서만 정확히 하나의 `--urlconf-module` + 반복 `--registrar-module` 필수 | Obligation | E:`check-composition-root.py` | 동상 — #16 의 project URLconf/registrar slice 소유 |
| s007 | b15 (103–103) | preserve-established 는 native selector 전달 가능하되 code-profile selector 발명 금지 | Prohibition | E:`check-composition-root.py` | 동상 — profile 별 slice 판정은 #16 소유 |
| s007 | b15 (103–103) | `auto` 도 새 registrar slice 는 N/A | Obligation | E:`check-composition-root.py` | 동상 |
| s007 | b15 (103–103) | N/A 는 검사 슬라이스 생략이지 배선 표준(#105~#112)의 면제가 아니다 | Prohibition | E:`check-composition-root.py` | ①원문 registry #16 표 행(line 123) 문면 + ④registry #16 + ②docstring 실재 문구(dddjango-code-json lane 의 API object·registrar·URLconf provenance) + 구현부 방출 실측 — **F2 수리(②출처 정정)** |
| s007 | b15 (103–103) | «면제가 아니다»는 신규 산출물 형태 문장 — 스코프 밖 기존 배선 이동 근거 아님 | Exception | D:`command-dddjango` | ①문면이 승인 스코프(코디 소유)를 관할의 자로 세움 — s005 b7 동일 축의 재확인 |
| s007 | b15 (103–103) | project URLconf/registrar slice 와 기존 BC DI V1 slice 는 별도 책임·DI slice 는 전 mode 상시 실행 | Obligation | E:`check-composition-root.py` · E:`check-layer-skeleton.py` | ②check-composition-root.py docstring «DI 레인은 … 단일 파일 composition_root.py 모양만 차단(#497)» + «두 변종은 check-layer-skeleton 소유로 이관(#81/#488)» — 문면의 V2/V3 이관 서술과 정확 일치 |
| s007 | b15 (103–103) | BC `composition_root/` 는 DI owner 이지 URL registrar owner 가 아니다 | Prohibition | E:`check-composition-root.py` | ②docstring «DI 조립(컴포지션 루트)은 BC 루트의 composition_root/(결선은 dependency_wiring.py)가 소유한다(정본)» + ④registry #16 |
| s007 | b16 (104–105) | Error response G2 는 승인된 code/preserve scope 마다 command 를 각각 렌더·실행 | Obligation | D:`command-dddjango` | ①문면 주어=코디 실행 절차 → §16 기본값 |
| s007 | b16 (104–105) | 무관 G2 는 네 checker 와 registry #16 에 positional target·`--error-profile auto` 명시 | Obligation | E:`check-error-centralization.py` · E:`check-api-error-controller-contract.py` · E:`check-context-isolation.py` · E:`check-openapi-error-declaration.py` · E:`check-composition-root.py` | ④registry #2·#15·#6·#5·#16 지목 + ②docstring «Positional-only, ``auto``, and ``preserve-established`` invocations do not apply schema semantics»(#2)·«add no new error-mapping semantics»(#15) |
| s007 | b16 (104–105) | `auto` 결과는 12-slot 증거가 아니라고 보고 | Obligation | D:`command-dddjango` | ①문면 = 코디의 보고 의무 → §16 기본값 |
| s007 | b17 (106–107) | 정확한 checker registry 와 소유권 — 순서 고정 | Obligation | D:`command-dddjango` | ①문면 = registry 전체의 순서·소유 선언(개별 검사기 귀속 불가) · ④registry #1~#27 표 자체 → §16 기본값(운용 주체 코디) |
| s007 | b18 (108–108) | registry #1 — 승인 없는 DB 메커니즘 변경 + migrations 산출물 순수성 | Prohibition | E:`check-mechanism-ownership.py` | ①문면이 파일명 직접 지목 + ④registry #1 + ②docstring «⑴ DB 엔진 메커니즘 교체 … ⑵ migrations 규율 4규칙(#336~#338·#593)» 문면 일치 |
| s007 | b19 (109–109) | registry #2 — ErrorSchema shape·source contract·project inventory + 표준 트리 슬라이스 | Obligation | E:`check-error-centralization.py` | ①파일명 직접 지목 + ④registry #2 + ②docstring «canonical common/BC FrameworkErrorSchema modules, project inventory correspondence, wire-code uniqueness» 일치(파일명과 달리 centralization 판정 아님도 문면 일치) |
| s007 | b20 (110–110) | registry #3 — ordinary JSON 200–203 raw-response bypass 한정 | Prohibition | E:`check-response-schema-bypass.py` | ①파일명 직접 지목 + ④registry #3 + ②docstring «Block direct raw 200-203 returns that bypass a declared Ninja schema» 일치 |
| s007 | b21 (111–111) | registry #4 — standard_tree 140행 골격 + 제1원칙 선행 게이트 | Obligation | E:`check-layer-skeleton.py` | ①파일명 직접 지목 + ④registry #4 + ②docstring «표준 파일트리 골격 검사기 — 제1원칙(#486~#491) … 이 검사는 다른 모든 검사보다 먼저 돌고(#487)» 일치 |
| s007 | b22 (112–112) | registry #5 — OpenAPI 오류 선언 대조·수동 후처리 금지 + 표준 트리 슬라이스 | Prohibition | E:`check-openapi-error-declaration.py` | ①파일명 직접 지목 + ④registry #5 + ②docstring «선택된 operation이 직접 반환하는 BC 오류와 response={status: <Bc>ErrorSchema} 선언의 일치를 검증하고, 선택 API module의 수동 OpenAPI 후처리를 차단» 일치 |
| s007 | b23 (113–113) | registry #6 — BC 간 접근 방향·OHS·ACL·UoW 크로스-BC 포트·경계 애너테이션 | Prohibition | E:`check-context-isolation.py` | ①파일명 직접 지목 + ④registry #6 + ②docstring «BC 경계·층 방향 규율 … #14 with unit_of_work: 안에서 크로스-BC 포트 호출 금지 · #11 경계 애너테이션» 일치(API-error selector 수용·판정 미사용도 일치) |
| s007 | b24 (114–114) | registry #7 — app 의 `application/<bounded_context>/` container 위치 | Obligation | E:`check-app-container.py` | ①파일명 직접 지목 + ④registry #7 + ②docstring «application/ 밖(루트·src/ 등)에 방치된 Django 앱을 적출 … 비-git 은 fail-closed(전 후보 검사)» 일치 |
| s007 | b25 (115–115) | registry #8 — BC HTTP concern 의 global middleware 자가등록 | Prohibition | E:`check-ninja-boundary-middleware.py` | ①파일명 직접 지목 + ④registry #8 + ②docstring «driving 층에서 자가 정의한 Django 미들웨어가 전역 settings.MIDDLEWARE 에 자가등록 되면 적출» 일치 |
| s007 | b26 (116–116) | registry #9 — root `framework/` 배치와 일반 cross-cutting utility | Obligation | E:`check-common-container.py` | ①파일명 직접 지목 + ④registry #9 + ②docstring «framework/(저장소 횡단 공용)는 프로젝트 루트에 둔다 = application/ 의 형제 … application/{framework\|common}/ 만 차단» 일치 |
| s007 | b27 (117–117) | registry #10 — 승인 범위 밖 idempotency 산출물 | Prohibition | E:`check-idempotency-scope-creep.py` | ①파일명 직접 지목 + ④registry #10 + ②docstring «이 checker의 소유는 이번 변경에서 touched된 멱등성 산출물이 G1 채택 승인 없이 accepted scope 밖에 추가되는 것을 막는 데 한정» 일치 |
| s007 | b28 (118–118) | registry #11 — 타입 전면(#493)·Thin Read 반환(#358)·계약 검증 토큰(#456) | Obligation | E:`check-public-surface-annotation.py` | ①파일명 직접 지목 + ④registry #11 + ②docstring «#493 모든 이름은 «첫 대입»에 타입 … #358 Thin Read … #456» 일치(문법 없는 여덟 자리 면제도 문면 «문법 없는 자리만 면제»와 일치) |
| s007 | b29 (119–119) | registry #12 — `test/` 다섯 자식·`settings/` 환경축·pytest Django settings binding | Obligation | E:`check-test-config.py` | ①파일명 직접 지목 + ④registry #12 + ②docstring 세 슬라이스(«pytest ↔ Django settings 바인딩»·«test/ 구조 #383~#392»·«settings/ 환경축 #445~#447 — 목록 열림·약어만 위반») 일치 |
| s007 | b30 (120–120) | registry #13 — established preserve-established handler 의 overmapping guard 한정 | Prohibition | E:`check-transient-overmapping.py` | ①파일명 직접 지목 + ④registry #13 + ②docstring «G1에서 이미 승인된 preserve-established brownfield handler를 보존할 때 … 새 handler/recognizer를 만들 근거가 되지 않는다» 일치 |
| s007 | b31 (121–121) | registry #14 — owning-BC exception normalization/controller mapping·brownfield cause preservation | Obligation | E:`check-synthetic-infra-exc.py` | ①파일명 직접 지목 + ④registry #14 + ②docstring 실재 문면 «⑴ 현행 관할 — 인프라 예외 *합성*(from 없는 raw 생성) · ⑵ 트리 개정 명세 몫 — #129 전수 명시 매핑» — **F1 수리: 후단 «새 recognizer recipe 를 만들지 않는다» 는 이 docstring 에 없다**(grep 0건 · 유사 문장 실물은 #13 check-transient-overmapping.py). 그 절의 근거는 ①문서 표 문면 + ④뿐(② 미성립) |
| s007 | b32 (122–122) | registry #15 — narrow try·concrete same-BC catch·direct BC-base ErrorSchema·two-argument Status + 표준 트리 슬라이스 | Obligation | E:`check-api-error-controller-contract.py` | ①파일명 직접 지목 + ④registry #15 + ②docstring «Enforce direct controller-owned code-profile error mapping … analyzes only selected controllers owned by an error-bc» 일치(§16 매핑 표 «controller checker» 행과도 일치) |
| s007 | b33 (123–123) | registry #16 — `composition_root/` 정본·api_router 결선·닫힌 목록 + BC DI V1·project URLconf/registrar slice | Obligation | E:`check-composition-root.py` | ①파일명 직접 지목 + ④registry #16 + ②docstring «DI 레인은 … 단일 파일 composition_root.py 모양만 차단(#497)»·«두 변종은 check-layer-skeleton 소유로 이관» — 문면의 «기존 BC DI V1(#497)» 표기와 정확 일치 |
| s007 | b34 (124–124) | registry #17 — 신규 ORM model `db_table`·타 BC FK 금지·`<Name>Model`·apps.py 결선 | Obligation | E:`check-db-table.py` | ①파일명 직접 지목 + ④registry #17 + ②docstring «#630 신규 모델 Meta.db_table 존재 + 값 … #631 타 BC 모델 FK 금지 … #632 <Name>Model 상시 … #329~#332·#535~#538» 일치 |
| s007 | b35 (125–125) | registry #18 — touched direct Enum/choices literal consumption | Prohibition | E:`check-choices-literal-consumption.py` | ①파일명 직접 지목 + ④registry #18 + ②docstring «Enum/choices 를 선언해 놓고 소비처가 원시 문자열 리터럴을 쓰는 직접형 두 가지만 … touched 인 파일만» 일치 |
| s007 | b36 (126–126) | registry #19 — `<use_case>/` 4파일 계약·인라인 자료 금지·`dto` 낱말 0·사실 발행 세 걸음·응용 DTO raise 금지 | Obligation | E:`check-usecase-dto-placement.py` | ①파일명 직접 지목 + ④registry #19 + ②docstring «#201 자료는 세 파일 … #567 dto 라는 이름을 쓰지 않는다 … #539~#541 발행 세 걸음» 일치(#67 raise 금지도 «ast+ 후보 채널 #68» 인접 소유로 문면 일치) |
| s007 | b37 (127–127) | registry #20 — 한 트랜잭션=애그리거트 하나 축·리포지토리 파일 계약·UoW 수령·save_all 조건 | Obligation | E:`check-transaction-boundary.py` | ①파일명 직접 지목 + ④registry #20 + ②docstring «#4 application_layer 의 django import 0 … #282/#283 리포지토리 «파일» 계약 … #200 after_commit 위임 … #599 save_all 조건 셋» 일치 |
| s007 | b38 (128–128) | registry #21 — 애그리거트·엔티티·값 객체·도메인 서비스·도메인 이벤트의 자리와 계약 | Obligation | E:`check-domain-model.py` | ①파일명 직접 지목 + ④registry #21 + ②docstring «#8 domain_layer 의 밖으로 나가는 import 0 … #257 상태 변경은 루트를 지난다 … #272 루트는 이벤트를 기록만 한다» 일치 |
| s007 | b39 (129–129) | registry #22 — port 선언 셋과 adapter·test/fake 짝맞춤 | Obligation | E:`check-port-adapter-pairing.py` | ①파일명 직접 지목 + ④registry #22 + ②docstring «port/ … #216 안은 계약·자료·실패 셋 … #319 네 갈래(소켓→external_system) … #621~#624 페이크 규율» 일치 |
| s007 | b40 (130–130) | registry #23 — published_event 단일 표면·구독 껍데기·과거형 이름·BC 간 순환·재발행 금지 | Prohibition | E:`check-event-publish.py` | ①파일명 직접 지목 + ④registry #23 + ②docstring «#502 published_event/ 는 BC 루트 직계뿐 … #271 사실 이름은 과거형 … #600 BC 간 순환 금지 · #601 재발행 금지» 일치 |
| s007 | b41 (131–131) | registry #24 — framework/broker internal/external 계약과 celery.py 결선 | Obligation | E:`check-broker-contract.py` | ①파일명 직접 지목 + ④registry #24 + ②docstring «#442 <project>/celery.py 는 Celery 인스턴스 + autodiscover_tasks 만 … #521 internal 은 바깥 미들웨어 없이 … #533 external 계약은 봉투를 요구» 일치 |
| s007 | b42 (132–132) | registry #25 — cron_job·webhook·event_subscription 입구 규율 | Obligation | E:`check-missable-entrance.py` | ①파일명 직접 지목 + ④registry #25 + ②docstring «#172~#181 cron_job 껍데기·멱등 소유 … #515 webhook schema 겹 … #516 webhook 에 오는 것은 HTTP 뿐» 일치 |
| s007 | b43 (133–133) | registry #26 — 약어·접두/접미 스코프·패턴 낱말·어드민 자리·문구의 자리 | Prohibition | E:`check-naming.py` | ①파일명 직접 지목 + ④registry #26 + ②docstring «#28 원전 패턴 약어 금지 … #34 같은 접두 = 같은 스코프 … #340~#343 어드민 자리» 일치 |
| s007 | b44 (134–135) | registry #27 — framework/ 격리(업무 어휘·BC 이름 0)·capability/technology/pure/test 구조·계약 가산만 | Prohibition | E:`check-business-vocabulary.py` | ①파일명 직접 지목 + ④registry #27 + ②docstring «framework/는 어느 BC 의 어휘도 모르는 기계 부품의 자리 … #52 BC 이름 0 … #604 계약은 «가산만»» 일치 |
| s007 | b45 (136–136) | registry #2·#15·#5 의 structural invariant 는 명시 선택한 production full tree 를 본다 | Obligation | E:`check-error-centralization.py` · E:`check-api-error-controller-contract.py` · E:`check-openapi-error-declaration.py` | ④문면이 #2·#15·#5 를 지목 + ②docstring — #5 «positional/auto/preserve 실행은 기존 openapi_extra.responses 저장소 전수 검사를 보존»·#2 «project inventory correspondence» 로 full-tree 슬라이스 소유 확인 |
| s007 | b45 (136–136) | registry #6 은 API-error selector 를 수용하되 판정에 쓰지 않음 — 나머지는 각 checker 계약대로 touched/전수 | Obligation | E:`check-context-isolation.py` · E:`check-response-schema-bypass.py` | ④#6·#3 지목 + ②docstring — #6 «API-error selector 는 수용하되 이 판정에는 안 쓴다»(문면과 축자 일치)·#3 «The selector-free invocation preserves the historical touched-file gate» |
| s007 | b45 (136–136) | 스물일곱 전부가 touched-only 이거나 커밋 뒤 전부 empty 라는 일반화 금지 | Prohibition | D:`command-dddjango` | ①문면 = 코디의 증거 해석 금지 규범(개별 검사기 귀속 불가 — 27종 횡단) → §16 기본값 |
| s007 | b46 (137–137) | 렌더된 required command 와 나머지 required checker 를 정확히 1회 실행·exact command·exit·diagnostic 수집 | Obligation | D:`command-dddjango` | ①문면 주어=«네가 직접 실행» → §16 기본값(실행·수집 주체는 코디) |
| s007 | b46 (137–137) | exit 의미론 — 0=clean/N-A/help · 1=usage/selectors/incomplete scope/analysis failure · 2=deterministic contract violation | Obligation | E:`check-layer-skeleton.py` · E:`check-context-isolation.py` · E:`check-test-config.py` · E:`check-error-centralization.py` · E:`check-api-error-controller-contract.py` | ②27종 docstring 전수의 exit **의미론** 공통 계약 — **F5 수리: 문면은 2형이다**(한국어 24종 «종료코드: …» · 영문 3종 «Exit codes: …» = registry #2·#3·#15). 대표 5종으로 두 형을 모두 포괄 인용(«전 로스터 동일 문면» 철회) |
| s007 | b46 (137–137) | ⓐ 직접 실행 계열의 exit 1 전부는 차분 비종속 직접 G2 blocker | Prohibition | D:`command-dddjango` | ①문면 = 게이트 판정 규약(검사기는 exit 만 내고 blocker 판정은 코디) → §16 기본값 |
| s007 | b46 (137–137) | 잔여 exit 1 전건이 `DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED` 면 runtime proof 경로 | Exception | E:`check-error-centralization.py` · E:`check-openapi-error-declaration.py` · E:`check-api-error-controller-contract.py` | ④문면이 registry #2·#5·#15 를 토큰 발행자로 지목 + §16 매핑 표(marker `DYNAMIC_ERROR_SHAPE_PROOF_REQUIRED` 발행 = controller checker) — 토큰 발행 실측 승격분 |
| s007 | b46 (137–137) | scope-렌더 exit 2 는 검사기 자신의 `--anchor` 판정 차분 경유 — 신규분 있으면 직접 blocker·일괄 반송 | Obligation | E:`check-error-centralization.py` · E:`check-openapi-error-declaration.py` · E:`check-context-isolation.py` · E:`check-api-error-controller-contract.py` · E:`check-composition-root.py` | ④문면이 registry #2·#5·#6·#15·#16 을 앵커 차분 수행자로 명시 + ②각 docstring 의 exit 2 «contract blocker» 계약 |
| s007 | b46 (137–137) | 진단 전건이 앵커 기존분이면 검사기가 exit 0 + 기존분 별도 보고로 강등(즉석 수리 금지) | Exception | E:`check-error-centralization.py` · E:`check-openapi-error-declaration.py` · E:`check-context-isolation.py` · E:`check-api-error-controller-contract.py` · E:`check-composition-root.py` | 동상 — 강등의 주체가 «검사기»라고 문면이 명시(registry #2 는 토큰-only exit 1 proof 경로를 강등으로 소거하지 않음) |
| s007 | b46 (137–137) | `--anchor` 없거나 미수용 검사기의 scope-렌더 exit 2 는 직접 blocker — 미측정 green 주장 금지 | Prohibition | D:`command-dddjango` | ①문면 = 측정 실패 판정(코디 소유) · registry_gate 차분 시야 밖 서술 → §16 기본값 |
| s007 | b46 (137–137) | ⓑ auto-렌더 위반 red 의 판정 주체는 registry_gate 판정 차분 — 귀속만 blocker·잔존은 보고 의무 | Obligation | D:`command-dddjango` | ①문면이 registry_gate.py 를 지목하나 로스터 27종 밖(전수 실독 확인) — 게이트 운용·보고 주체는 코디 → §16 기본값 |
| s007 | b46 (137–137) | 게이트 자신의 exit 1·[진단 미파싱] fail-closed 귀속은 측정 실패로 반송 | Prohibition | D:`command-dddjango` | 동상 |
| s007 | b46 (137–137) | legacy 잔존 red 는 이 빌드에서 즉석 수리 금지(테스트 실패 채널과 분리) | Prohibition | D:`command-dddjango` | 동상 — 처분 판정 주체가 코디 |
| s007 | b46 (137–137) | 예외 둘 — 슬라이스 0 승인 수리 · G2 시점 «미룰 수 없음»의 G0 재상정 | Exception | D:`command-dddjango` | 동상 — s005 b9 ⓐ/ⓑ 결정 채널과 동축 |
| s007 | b46 (137–137) | 미이관 표준 경로 의존 잔존 귀속은 STOP_FOR_USER_APPROVAL 표면화 — 빚 분류는 legacy 복사 근거 아님 | Prohibition | D:`command-dddjango` | 동상 — s011 b6 STOP 기록 형식과 동축 |
| s007 | b46 (137–137) | runtime proof 수행 의무 — action 별 기준 evidence 와 전 항목(Field metadata·model_config·wire 직렬화) 대조·exact dump·mounted 검증 | Obligation | D:`command-dddjango` | ①문면 = 코디가 target 의존 pin 에서 수행하는 증명 절차(검사기 exit 밖) → §16 기본값 |
| s007 | b46 (137–137) | 두 reviewer 독립 토큰일 때만 RESOLVED_… 기록 — 불일치·혼입·실패는 blocker·shape 승인 갈음 불가·한 실패 뒤 나머지 결과 유지 | Obligation | D:`agent-design-review-api` · D:`agent-discipline-reviewer` | ①문면이 두 토큰의 발화 주체를 «API reviewer»·«discipline reviewer» 로 명시(서로의 노트 미수신 조건) — §16 표 architecture-api 행 + ⓓ 관례 |
| s007 | b47 (138–138) | checker 별 exit-0 blind spot — 각 registry 의 미증명 범위 인지 | Obligation | E:`check-api-error-controller-contract.py` · E:`check-context-isolation.py` · E:`check-composition-root.py` · E:`check-error-centralization.py` · E:`check-openapi-error-declaration.py` | ④문면이 registry #15·#6·#16·#2·#5 의 한계를 열거 + ②각 docstring 의 «보지 않는 것/저-recall» 자기 선언(#15 «profile- and source-selected»·#16 «형태로 못 가르므로 discipline-reviewer 의미 레인 몫») |
| s007 | b47 (138–138) | auth truthy ErrorSchema·hidden framework-header 의존은 acceptance/discipline/API review 가 직접 읽는다 | Obligation | D:`agent-acceptance-tester` · D:`agent-discipline-reviewer` · D:`agent-design-review-api` | ①문면이 세 역할을 직접 지목 — 검사기 비커버 잔여 축의 판정 주체(§16 기본값 이탈 문면 근거) |
| s007 | b47 (138–138) | checker count·exit 0·RESOLVED_… 는 runtime contract test·mounted OpenAPI·role review·shape approval·G2 승인을 대신하지 않는다 | Prohibition | D:`command-dddjango` | ①문면 = 증거 갈음 금지(게이트 판정 주체 코디) → §16 기본값 |
| s007 | b48 (139–140) | 6′ 재생성 루프는 `DJR_LOOP_ENABLED=on` 일 때만 발화 — 없거나 off 면 절 통째 건너뜀 | Permission | D:`command-dddjango` | ①문면 주어=코디 처치 스위치 · ②27종 전수에 루프 담당 없음(regen_core.py 는 로스터 밖) → §16 기본값 |
| s007 | b48 (139–140) | on 이면 귀속 red 를 소유자에게 반송하기 전에 최대 3회전 재생성 시도 | Obligation | D:`command-dddjango` | 동상 — 발화 지점의 주어가 «귀속 red 의 반송»(2026-08-22 동결 개정 10) |
| s007 | b48 (139–140) | 회전 계상은 실행 지점별이 아니라 런 전체 `injection.jsonl` 누적 | Obligation | D:`command-dddjango` | 동상 — 용량 로그가 회전 번호의 단일 출처 |
| s007 | b48 (139–140) | 귀속 red 반송 메시지에 6′ 수행 결과 한 줄 명기 — 없는 반송은 절차 위반 | Obligation | D:`command-dddjango` | 동상 |
| s007 | b49 (141–141) | registry_gate 실행에 `--introduced-json`·`--contract-json` 을 더해 귀속 레코드만 수신 | Obligation | D:`command-dddjango` | ①문면 주어=코디 게이트 호출 · registry_gate.py 는 로스터 27종 밖 → §16 기본값 |
| s007 | b49 (141–141) | 검사기의 레코드 파일(`DJR_FINDINGS_JSON`·`DJR_VIOLATIONS_DIR`)을 직접 읽기 금지 | Prohibition | D:`command-dddjango` | ②27종 docstring 전수의 «구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 …» 공통 문면 — 그 파일의 소비 금지 판정은 절차 층(앵커 실행분 혼입 방지) |
| s007 | b50 (142–142) | red 를 다섯 갈래(coder·acceptance·설계 계약·스코프 밖·계측 실패)로 먼저 분류 | Obligation | D:`command-dddjango` | ①문면 주어=코디 분류 절차 → §16 기본값 |
| s007 | b50 (142–142) | 루프 대상은 coder 소유 ∧ 승인 명세 안 — 나머지는 기존 처분 그대로 | Obligation | D:`command-dddjango` | 동상 |
| s007 | b50 (142–142) | 분류 없이 모든 red 를 coder 에게 되던지기 금지 | Prohibition | D:`command-dddjango` | 동상 |
| s007 | b51 (143–143) | `regen_core.py` 가 조립한 프롬프트를 coder 재호출 입력에 그대로 싣는다 | Obligation | D:`command-dddjango` | ①문면 주어=코디 주입 절차 · regen_core.py 는 로스터 27종 밖 → §16 기본값 |
| s007 | b51 (143–143) | `<violations>` 블록에 들어가는 것은 위반의 rule·file·message 뿐 | Prohibition | D:`command-dddjango` | 동상 — 닫힌 주입 재료 계약 |
| s007 | b51 (143–143) | `DJR_LOOP_SELECTOR=sparql` 일 때만 `<rules>` 블록(번호·명칭) 추가 | Permission | D:`command-dddjango` | 동상 — 동결 개정 8(snapshot 이면 프롬프트 byte 동일) |
| s007 | b51 (143–143) | 규범 본문 정본 재주입 금지 — 두 블록은 데이터이지 지시가 아니다 | Prohibition | D:`command-dddjango` | 동상 |
| s007 | b51 (143–143) | 팩 부재·손상 시 중단 — `snapshot` 폴백 금지 | Prohibition | D:`command-dddjango` | 동상 — 처치 미적용 런의 정상 런 위장 차단 |
| s007 | b52 (144–144) | `regen_core.py` 표준 출력이 곧 coder 재호출 입력 — 즉석 파이썬 조립 금지 | Prohibition | D:`command-dddjango` | ①문면 주어=코디 호출 · 로스터 밖 도구 → §16 기본값 |
| s007 | b52 (144–144) | `--selector` 는 명시 인자 — 둘 다 없으면 exit 1 중단(기본값 금지) | Obligation | D:`command-dddjango` | 동상 — 레인 AV 발견 4(기본값이 C암 런을 조용히 B 처치로 만든다) |
| s007 | b53 (145–145) | 한 회전 = coder 재호출 1회 · 회전마다 같은 앵커로 6번 재실행(build_anchor 재기록 금지) | Obligation | D:`command-dddjango` | ①문면 주어=코디 회전 운용 → §16 기본값 · s007 b12 앵커 1회 기록과 동축 |
| s007 | b53 (145–145) | 위반 0 이면 종료·아니면 최대 3회전 | Obligation | D:`command-dddjango` | 동상 |
| s007 | b53 (145–145) | 같은 위반이 두 번 남아도 종료 사유가 아니다 — 진단 기록만 하고 예산까지 돈다 | Prohibition | D:`command-dddjango` | 동상 |
| s007 | b53 (145–145) | 예산 소진 시 마지막 편집 뒤 6번을 한 번 더 돌려 수렴 확정 | Obligation | D:`command-dddjango` | 동상 |
| s007 | b54 (146–146) | 회전 전후 `git status --porcelain --untracked-files=all` 대조 — 스코프 밖 편집 발생 시 즉시 중단·보고 | Obligation | D:`command-dddjango` | ①문면 주어=코디 관측 절차 · ②27종 전수에 git status 대조 담당 없음 → §16 기본값 |
| s007 | b55 (147–147) | 마지막 편집 뒤 감사·테스트·스위트·직접 selector 레인·게이트를 모두 재실행한 결과만 7번 배너에 올린다 | Obligation | D:`command-dddjango` | ①문면 주어=코디 증거 갱신 → §16 기본값 |
| s007 | b55 (147–147) | 「같은 검사기만 green」으로 옛 감사 증거를 달고 G2 진행 금지 | Prohibition | D:`command-dddjango` | 동상 |
| s007 | b56 (148–149) | 루프가 예산을 다 써도 7번 G2 제시 조건은 그대로 — 루프는 게이트를 대체하지 않는다 | Prohibition | D:`command-dddjango` | ①문면 = 게이트 갈음 금지(승인 전 진행 금지) → §16 기본값 · s011 b4 와 동축 |
| s007 | b57 (150–151) | G2 배너로 코드·테스트·검증 결과 + 감수 리포트 + 일곱 decision 최종 실행 결과 제시·승인 | Obligation | D:`command-dddjango` | ①문면 주어=코디 게이트 → §16 기본값 |
| s007 | b57 (150–151) | dddjango-code-json 이면 canonical common action/path·승인 shape·direct mapping별 승인 HTTP 결과·mounted OpenAPI/public Python 검증 표시 | Obligation | D:`command-dddjango` | 동상 — 배너 표시 항목은 코디 소유 |
| s007 | b57 (150–151) | preserve-established 면 승인된 native runtime/mounted 증거 표시 | Obligation | D:`command-dddjango` | 동상 |
| s007 | b57 (150–151) | 승인되지 않은 framework/private test 를 증거로 발명 금지 | Prohibition | D:`agent-discipline-reviewer` | ①문면 = 영구 테스트 입장 위반 · §16 기본값 표 discipline-reviewer(테스트 증거 감사 주체·s007 b6 문면) |
| s007 | b57 (150–151) | 기존 27-registry checker 와 12-slot evidence 는 그대로 실행·표시 | Obligation | D:`command-dddjango` | ①문면 주어=코디 실행·표시 → §16 기본값 |
| s007 | b57 (150–151) | Red·pending·입장-diff 불일치·첫-Green 비계·미해소 exit·미해소 귀속 red·contract mismatch 잔존 시 G2 제시 금지(legacy 잔존은 별도 보고 항목) | Prohibition | D:`command-dddjango` | 동상 — 게이트 제시 조건 판정 주체가 코디 |
| s008 | b1 (153–155) | 실행한 검증만 보고 | Obligation | D:`command-dddjango` | ①문면 주어=코디 검증 보고(s011 b1 «검증 보고만 직접 쓴다» 와 동축) → §16 기본값 |
| s008 | b1 (153–155) | 관련 검증과 전체 suite 결과 구분 — 무관 실패는 편집 없이 별도 표시 | Obligation | D:`command-dddjango` | 동상 — s007 b9·s009 b4·s010 b8 과 동축 |
| s008 | b1 (153–155) | 미실행을 실행한 것처럼 보고 금지 — 미실행 사유 명시 | Prohibition | D:`command-dddjango` | 동상 |
| s009 | b1 (157–159) | 국소 수정은 전체 파이프라인 재실행 금지 | Prohibition | D:`command-dddjango` | ①문면 주어=코디 모드 운용 → §16 기본값 |
| s009 | b2 (160–160) | 수정 모드 G0 — 영향 범위만 빠르게 확인 | Obligation | D:`command-dddjango` | 동상 |
| s009 | b2 (160–160) | Phase 0 산출물 폴더 절차 그대로 수행해 재사용 폴더 확정(새 폴더 생성 금지) | Obligation | D:`command-dddjango` | 동상 — s005 b9·s002 b6 폴더 절차의 역참조(정본은 Phase 0) |
| s009 | b3 (161–161) | 영향받는 lens 만 재실행 → G1′ 로 바뀐 설계 부분만 승인 | Obligation | D:`command-dddjango` | ①문면 주어=코디 게이트 운용 → §16 기본값 |
| s009 | b3 (161–161) | Phase 1 step 5 와 동일하게 입장 표 갱신·배너에 decision 별 owner/path 나열 | Obligation | D:`command-dddjango` | 동상 — s006 b6 의 역참조(정본은 Phase 1 step 5) |
| s009 | b3 (161–161) | pending 잔존 시 Phase 2 진행 금지 | Prohibition | D:`command-dddjango` | 동상 — s010 b5 와 동축 |
| s009 | b3 (161–161) | Y/Z 처리 동일 — scope.md 갱신·architect override 재호출·design-spec 직접 저작 금지 | Prohibition | D:`command-dddjango` | 동상 — s006 b7 의 역참조 |
| s009 | b4 (162–163) | 같은 한정 검색과 decision 별 소유자 라우팅 적용 | Obligation | D:`command-dddjango` | ①문면 주어=코디 dispatch → §16 기본값 |
| s009 | b4 (162–163) | 프로젝트 기존 전체 suite 도 코디네이터가 실행 후 G2 | Obligation | D:`command-dddjango` | ①문면이 실행 주체를 «너(코디네이터)»로 명시 → §16 기본값 정확 일치 |
| s009 | b4 (162–163) | 무관 실패는 편집 금지·별도 보고·전체 green 주장 금지(기준선 실측) | Prohibition | D:`command-dddjango` | 동상 — s007 b9 «기준선 실측» 자의 재적용 |
| s009 | b5 (164–165) | 순수 구현 수정은 재독·입장 행 확정·pending 0 일 때만 G1′ 생략 가능 | Permission | D:`command-dddjango` | ①문면 = 게이트 생략 허용 조건(코디 판정) → §16 기본값 |
| s009 | b5 (164–165) | 이 경우에도 add/update 만 Red/test edit — reuse/retain/reject 에서 write 금지 | Prohibition | D:`agent-discipline-reviewer` | ①문면 = decision 별 write 규율 · s007 b6 «reuse/reject write 0, 일반 retain 무편집» 을 discipline-reviewer 가 감사 — 판정 주체 문면 근거 |
| s009 | b5 (164–165) | 「테스트 계약 변화 없음」 기재로 심사 생략 금지 | Prohibition | D:`agent-discipline-reviewer` | 동상 — 입장 심사 생략 감사 주체 |
| s009 | b5 (164–165) | 지원 종료·expected result 변경·move/split/rename/remove/weaken·입장 결정 변경이 있으면 G1′ 생략 금지 | Prohibition | D:`command-dddjango` | ①문면 = 게이트 생략 금지 조건(게이트 판정 주체 코디) → §16 기본값 |
| s009 | b6 (166–167) | 두 경로 모두 G2 배너 직전 Phase 2 step6 을 그대로 적용 — 증거 무축약 | Obligation | D:`command-dddjango` | ①문면이 step6 정본을 역참조(사본 아님 — 발주서 비고) · 적용 주체는 코디 → §16 기본값 |
| s009 | b6 (166–167) | Error response 무관 수정은 `--error-profile auto` 경계 적용 — full-tree/touched slice 유지·전부 touched-only 일반화 금지 | Prohibition | E:`check-error-centralization.py` · E:`check-api-error-controller-contract.py` · E:`check-context-isolation.py` · E:`check-openapi-error-declaration.py` · E:`check-composition-root.py` · E:`check-response-schema-bypass.py` | ④문면이 registry #2·#15·#6·#5·#16(+#3 touched slice)을 역참조 + ②각 docstring 의 profile/selector 계약 — s007 b16·b45 와 같은 소유 |
| s009 | b6 (166–167) | test diff·승인 remove/weaken·의미 보존 재조직 실행 시 최소 1회 focused discipline-reviewer 호출 | Obligation | D:`command-dddjango` | ①문면 주어=코디 호출 절차 → §16 기본값(감사 항목 자체의 판정은 s007 b6 discipline-reviewer) |
| s010 | b1 (169–170) | 게이트 거부 시 피드백과 함께 해당 단계 재실행 — 다음 단계 진행 금지 | Prohibition | D:`command-dddjango` | ①문면 주어=코디 게이트 처리 → §16 기본값 · s003 b10 승인 절차와 동축 |
| s010 | b1 (169–170) | 반송 재실행 반복에 변경 범위가 늘면 재실행 대신 배너로 표면화(스코프 증가 신호) | Obligation | D:`command-dddjango` | 동상 |
| s010 | b2 (171–171) | 리뷰어 충돌은 architect 가 중재해 명세에 결정 명시 | Obligation | D:`agent-design-architect` | ①문면 주어가 «architect가 중재해 …명시한다» — 이행·판정 주체 문면 명시 |
| s010 | b2 (171–171) | 미해결이면 G1 배너에 트레이드오프 옵션으로 제시 | Obligation | D:`command-dddjango` | ①배너 제시 주체=코디 → §16 기본값 |
| s010 | b3 (172–172) | 인수 테스트가 계속 Red 면 coder 가 멈추고 보고 | Obligation | D:`agent-coder` | ①문면 주어가 «coder가 멈추고 보고한다» — 이행 주체 문면 명시 |
| s010 | b3 (172–172) | 명세 가정 오류면 설계 반송·구현 난점이면 사용자 제시 | Obligation | D:`command-dddjango` | ①반송·사용자 제시 채널 주체=코디 → §16 기본값 |
| s010 | b4 (173–173) | 잘못된 인수 테스트를 coder 가 임의 수정 금지 — 보고한다 | Prohibition | D:`agent-coder` | ①금지의 주어가 «coder» — 문면 명시 |
| s010 | b4 (173–173) | acceptance-tester·설계로 반송 | Obligation | D:`command-dddjango` | ①반송 라우팅 주체=코디 → §16 기본값 |
| s010 | b5 (174–174) | `pending` 을 유지나 완료로 간주 금지 | Prohibition | D:`agent-discipline-reviewer` | ①문면 = 영구 테스트 입장 미확정 처리 · s006 b4 «pending … 을 G1 전에 잡는다» 로 감사 주체가 discipline-reviewer(§16 ⓓ 관례) |
| s010 | b5 (174–174) | 한정된 설계 질문으로 G1/G1′ 에 반송 | Obligation | D:`command-dddjango` | ①반송 주체=코디 → §16 기본값 · s006 b6 과 동축 |
| s010 | b6 (175–175) | 세 mismatch 토큰은 모두 design-architect/G1 반송·G2 차단 | Prohibition | D:`command-dddjango` | ①문면 = 게이트 차단·반송 판정(코디 소유) → §16 기본값 · s007 b11 과 동축 |
| s010 | b6 (175–175) | role·Coordinator 가 승인 shape·tree·profile·field·return form 을 조용히 변경 금지 | Prohibition | D:`command-dddjango` | 동상 — 금지의 주어에 Coordinator 가 명시 |
| s010 | b8 (177–177) | 전체 suite 의 무관 실패는 관련 범위로 넓혀 수정 금지 — 별도 보고·전체 green 주장 금지 | Prohibition | D:`command-dddjango` | ①문면 주어=코디 보고 규율 → §16 기본값 · s007 b9·s009 b4 와 동축 |
| s010 | b9 (178–179) | 검증 미실행을 실행한 것처럼 보고 금지 — 미실행 사유 명시 | Prohibition | D:`command-dddjango` | 동상 — s008 b1 과 동축(Phase 3 정본의 엣지 재확인) |
| s011 | b1 (181–182) | 설계 명세·인수 테스트·구현 코드 직접 저작 금지 — architect·acceptance-tester·coder 위임 | Prohibition | D:`command-dddjango` | ①문면 = 경계 조항(금지 주어=코디) → §16 기본값 · s001 b2 의 정본 경계 선언 |
| s011 | b1 (181–182) | 코디는 스코프 메모와 검증 보고만 직접 작성 | Obligation | D:`command-dddjango` | 동상 — s006 b7 «scope.md 는 네 소유 파일이라 예외» 와 동축 |
| s011 | b2 (183–183) | 설계 명세가 인수 테스트와 코드의 단일 근거 | Obligation | D:`command-dddjango` | ①문면 = 경계 조항 → §16 기본값 · s006 b6 의 재선언 |
| s011 | b3 (184–184) | 한 주제는 한 소유자 — lens·역할 경계 월권 금지 | Prohibition | D:`command-dddjango` | 동상 — 역할 경계 판정 주체가 절차 층 |
| s011 | b4 (185–185) | 사용자 승인 없이 게이트 통과 금지 | Prohibition | D:`command-dddjango` | 동상 — s003 b10·s007 b56 과 동축(게이트 승인 정본 경계) |
| s011 | b5 (186–186) | 게이트 위임 지시가 있어도 위임되는 것은 승인 입력뿐 | Prohibition | D:`command-dddjango` | ①문면 = 자율 실행 발주의 위임 범위 한정(절차 층 소유) → §16 기본값 |
| s011 | b5 (186–186) | STOP·G0/G2 blocker·shape approved-change·scope 사후 개정은 기록 후 그 지점에서 정지 | Obligation | D:`command-dddjango` | 동상 — s007 b13·b46 STOP 채널과 동축 |
| s011 | b6 (187–187) | 게이트 질문·STOP 기록은 닫힌 선택지마다 대가 한 줄 병기 — 없으면 형식 불비 | Obligation | D:`command-dddjango` | ①문면 = 게이트 질문 형식 정본(코디 발화) → §16 기본값 · s003 b10 «대가 한 줄» 의 정본 |
| s011 | b6 (187–187) | 권고는 STOP 기록 안에서만·선택으로 — 저자 명시 가능할 때만·발주가 답을 고정한 게이트에선 생성 금지 | Permission | D:`command-dddjango` | 동상 — 즉석 설계 근거 제조 금지(갈림길 표면화 경계·s005 b9) |
| s011 | b6 (187–187) | 규정이 1차 처방을 정한 STOP 은 그 처방이 첫 번째 | Obligation | D:`command-dddjango` | 동상 — s007 b12 «귀속=철회» 1차 처방과 동축 |
| s011 | b6 (187–187) | 권고는 결정이 아니다 — 자기 승인 근거·기본값 선반영 금지·«권고 불가 — 사유»로 족하다 | Prohibition | D:`command-dddjango` | 동상 |
| s011 | b6 (187–187) | 밖에서 보이는 결과가 갈리는 물음은 권고 유무·논증 완성도와 무관하게 STOP | Obligation | D:`command-dddjango` | 동상 |
| s011 | b6 (187–187) | 닫힌 선택지는 AskUserQuestion 으로 제시(label=선택지·description=대가·권고는 첫 옵션 «(Recommended)») | Obligation | D:`command-dddjango` | 동상 — 입력 채널 규격(2026-08-13) |
| s011 | b6 (187–187) | 대화형 세션 STOP — 기록 파일 뒤 AskUserQuestion 제시·임의 정지 커밋 금지 | Prohibition | D:`command-dddjango` | 동상 — 커밋은 사용자 지시·발주 계약 소관 |
| s011 | b6 (187–187) | 자율 실행 STOP — 기록 파일 + 정지 커밋이 유효 종료 조건 · 기록이 정본이고 질문은 입력 채널(응답은 기록에 추기·재개 첫 커밋 포함) | Obligation | D:`command-dddjango` | 동상 — 결정 주체 관측의 정본이 기록 파일 |

## 3. 재진술 유예 (교차 문서 쌍 — T3 마감 웨이브 소급 패스로 일괄 연결)

같은 문서 쌍만 spec `restates` 에 실었고(1건), **다른 문서 상대 4건은 전량 유예**한다(T3-EXECUTION §병렬 설계 결정).

| # | 사본 좌표(이 문서) | 상대 문서/절 | 사본 성격 | 처분 |
|---|---|---|---|---|
| 1 | s010 / b7 (line 176) | **command-dddjango / s007 b46**(«실행·종료 계약») | 같은 문서 · checker exit 1/2 처리 축약 재서술 | **spec `restates` 에 실음**(정본=s007 b46, 사본 Work 미승격) |
| 2 | s005 (line 69) | `agent-coder` / s004 | 배선 표준 «#105~#112 · 사용 형태는 언제나 표준» 문장 사본 | **유예** — 상대 절 미이관(그래프 밖) |
| 3 | s006 (line 84) | `agent-design-architect` / s005 | Error response contract **12-slot label·순서 리터럴** 재등장(3중 병렬 — architect·coordinator·reviewer) | **유예** |
| 4 | s007 (line 95·91) | `agent-coder` / s003 | 역할 반환 «최소 근거» 보고 형식 리터럴 + 첫-Green 비계 제거 사본 | **유예** |
| 5 | s011 (line 187) | `agent-design-architect` / s004 | 게이트 질문·`STOP_FOR_USER_APPROVAL` 기록 형식 쌍 | **유예** |

**유예 계수: 4건**(#2~#5). 각 건은 발주서 `재진술` 열의 지목을 원문에서 직접 확인했다.

비-재진술 판정 2건(오분류 방지 기록):
- s009 line 166 «Phase 2 step6 을 그대로 적용한다» — 문장이 정본을 **역참조**할 뿐 문면을 복제하지 않는다(발주서 비고와 동일 판정). 재진술 아님.
- s003 line 51 «대가 한 줄 병기» ↔ s011 line 187 — 같은 문서 안 상술/정본 관계이나 **문면이 서로 다르다**(s003 은 배너 승인 맥락의 1문장, s011 은 STOP 기록 형식 정본 8문장). 축자·축약 사본이 아니라 각각 독립 Work 로 채번하고 `basis` 에 «동축» 표기만 남겼다.

## 4. 경계 판단 메모

**⑴ 공백 소유 — §13 기본(후행 귀속)과 code 예외(선행 귀속)**
§13 «블록 간 구분자는 선행 블록의 후행 스팬에 귀속» 을 전 블록에 적용했다(예: `[16,16]` 불릿 다음이 곧 불릿이면 빈 줄 없음, `[18,19]`·`[20,21]` 처럼 문단 뒤 빈 줄은 그 문단 블록이 먹는다). **단 `kind=code` 는 §13 의 더 좁은 규정 «여는 펜스~닫는 펜스 전체 라인 verbatim» 이 우선**하므로 s003 배너를 `[40,49]`(펜스 정확 스팬)로 자르고 뒤따르는 빈 줄 50 을 다음 블록 `[50,52]` 선두로 넘겼다. 파일럿 판형과 동형이다(architecture-ddd s017-3.2: b4=`[548,581]` 펜스 정확 · b5=`[582,583]` 선두 빈 줄 흡수).

> **§13 개정 제안(리뷰 F6 — 소급 패스 안건 · spec 수정 불요)**: §13 문면상 «구분자 선두 귀속» 의 명시 예외는 «절 선두(선행 블록 없음)» 하나뿐이라, 위 code-후행 빈 줄의 차행 선두 귀속은 문면과 긴장한다. 실무·파일럿 판형·byte 등가가 모두 이 처분을 지지하므로 **§13 에 «`kind=code` 블록의 후행 구분자는 차행 블록 선두에 귀속한다» 를 두 번째 명시 예외로 명문화**하는 개정을 T3 마감 소급 패스에 올린다. 개정 전까지 이 문서의 처분은 유지한다(실해 0 — 좌표·해시·byte 등가 전건 성립).

**⑵ 절 선두 빈 줄**
§13 명시 예외대로 전 절의 첫 블록이 헤딩 직후 빈 줄을 선두에 흡수한다(`[14,15]`·`[27,29]`·`[58,60]`·`[87,88]`·`[153,155]`·`[181,182]` 등).

**⑶ s001 의 «헤딩» = frontmatter 여는 `---`**
도구가 `line_start` 라인을 `djr:headingSnapshot` 으로 소유하므로 (전문) 절의 첫 블록은 line 2 부터다. frontmatter 본문 3행 + 닫는 `---` + 빈 줄을 **한 블록 `[2,6]`** 으로 묶었다 — YAML frontmatter 는 한 구문 단위이고 행 중간 분할은 §13 이 금한다. `description`·`allowed-tools` 두 규범을 이 블록에 다중 `statesNorm` 으로 붙였다(개정 1 3노드형). `argument-hint` 와 line 9 `$ARGUMENTS`(템플릿 치환 자리)는 규범이 아니라 `prose`.

**⑷ registry 27행의 kind — `table-row` 가 아니라 `norm`**
`   1. …` ~ `   27. …` 은 마크다운 **번호 목록**이지 표가 아니다. §13 «리스트 항(`- `·`1. `)은 마커 포함 verbatim 으로 norm/prose 블록에 귀속(kind 확장 불요)» 대로 `norm` 으로 판정했다. 1행=1블록=1Work 로 잘랐다 — 이유 둘: ⓐ 이 27행이 `wiring/aliases.ttl` 의 `#N ↔ Work` 조인 후보라 행 단위 좌표가 필요하다(27종 docstring 전수의 «조인 확정: 없음(대장 미등재 — T3 이월)» 문면이 이 이관을 T3 소관으로 지목한다) ⓑ 검사기별 소유 경계가 곧 규범 경계다.

**⑸ s007 을 57블록으로 분해한 근거**
step 1~7 각 1블록 + step 5/6 의 하위 불릿 각 1블록 + registry 27행 + step 6′ 하위 불릿 8. 절 하나를 통짜 블록으로 두면 s010 의 재진술이 «절 전체» 를 가리켜 정본 지시가 뭉개진다 — 실제로 사본이 지시하는 정본은 `b46`(line 137 실행·종료 계약) **한 행**이다.

**⑹ s003 30~33 을 `prose` 로 판정**
4단계 목록(«요구·스코프(G0)» 등)은 트래커·task 가 참조하는 **목록**이고, 출력 의무 자체는 line 28(task 발화 시점 셋)·35(게이트에서만 출력)·37(트래커 형식)이 진다. 목록 자체에 규범 문장이 없으므로 Work 를 붙이지 않았다.

**⑺ 규범 유형이 갈린 자리(판정 기록)**
- `Permission` — «① 기본 수락 → architect 재호출 없이 진행»(s006 b7), «홀리스틱 갈음»(s007 b5), «6′ 는 on 일 때만 발화»(s007 b48), «`<rules>` 블록은 sparql 일 때만»(s007 b51), «G1′ 생략 가능»(s009 b5).
- `Exception` — 본 의무의 **명시 예외절**만 부여했다(«민감 레포 ignore 허용», «이동 권한은 슬라이스 0 뿐», «전건 앵커 기존분이면 exit 0 강등», «토큰-only exit 1 의 runtime proof 경로» 등). 예외 없는 단서는 본 규범에 병합했다.
- `Override` — **0건**. 이 문서에 «상위 규범을 덮어쓴다» 형태의 문장이 없다(G1 override 는 «사용자 결정 반영 절차» 이지 규범 우선순위 전복이 아니라서 `Obligation` 으로 뒀다).
- **`Prohibition` 독법 채택 기록 — s005 b8 «brownfield·legacy 는 면제가 아니라 아직 안 갚은 빚»**(리뷰 F8 수리): 문면이 부정 선언이라 «면제 취급을 금한다»(Prohibition)와 «빚으로 취급할 의무»(Obligation) 양독이 성립한다. **전자를 채택한다** — ⑴ 문장의 술어 초점이 «면제가 **아니다**» 라는 잘못된 처분의 배제이고(재분류 자체는 §4 houserules 정본이 이미 소유), ⑵ 이 절의 소비 지점이 line 71 «ⓑ 미룬다» 선택지 통제 = 특정 처분의 차단이며, ⑶ 같은 축의 이웃 규범(«무관 항목 기계적 나열 금지»·«차분 도구 대체 실행 금지»)도 처분 배제형 `Prohibition` 이라 절 내부 일관을 지킨다.

**⑻ 배선에서 흔들렸던 자리 3곳**
- **line 99 «positional TARGET 도 루트(`.`)»** — **초판의 2종 귀속(`check-layer-skeleton.py`·`check-app-container.py`)을 철회하고 27종 전수로 고쳤다(리뷰 F3 수리)**. 초판 근거였던 «좁힌 TARGET 이면 채택 신호가 꺼져 사용 오류 exit 1» 은 **기제 오설명**이다 — 채택 신호가 꺼진 경로는 두 docstring 모두 **exit 0**(«표준 미채택 clean» / «없으면 exit 0»)이고, 문면이 말하는 exit 1 거절은 그 **조용한 통과를 막으려고 앞단에 놓인 공유 모듈** `checker_target.py` 가 낸다. 그 docstring 이 실측 근거다 — «검사기 27종의 TARGET 은 «저장소 루트»다 … 라운드 1 실측: 파이프라인이 `check-layer-skeleton.py application/child_settings` 호출로 V1 트리를 전부 green 처리했다. 조용 통과 대신 소리내어 거절한다 … 27종 전부가 이 모듈을 거치므로 여기 한 곳이 직접 실행 채널까지 봉인한다». 구현부 전수 확인: 27종 전부가 `checker_target.bc_shaped_target_reason()` 을 호출하고 사유가 있으면 «사용 오류» exit 1(22종은 `return 1`, 5종은 `UsageError`)로 끝낸다. 공유 모듈 자체는 `check-*.py` 로스터 밖이라 `enforcedBy` 대상이 아니므로, **exit 를 실제로 내는 27종 각각**에 건다(문면의 주어 «검사기» 와 정합 · 리뷰 수정안 ⓑ 채택).
- **line 137 «실행·종료 계약» 14 Work** — «검사기 자신의 `--anchor` 판정 차분» 두 문장만 5개 검사기(#2·#5·#6·#15·#16)에 `enforcedBy` 로 걸고, 나머지 blocker/반송/보고 판정은 Coordinator 에 뒀다. 가르는 자: **판정을 누가 «수행» 하는가** — 문면이 «검사기가 exit 0 + 기존분 별도 보고로 강등한다» 처럼 검사기를 주어로 쓴 곳만 enforcedBy.
- **line 103 «기존 BC DI V1(#497) slice»** — `check-composition-root.py` docstring 이 «한때 이 레인이 함께 잡던 두 변종(#81 off-tree `composition/`·#488 `composition_root/` 부재)은 `check-layer-skeleton` 소유로 이관» 이라 명시하므로 이 규범만 **두 검사기 병기**로 걸었다(문서 line 103 의 «V2/V3 부재 사건은 #81/#488 소유=check-layer-skeleton 로 이관» 과 축자 일치 — 2026-08-20 registry 문서 드리프트 정정분).

**⑼ 검사기 비커버 확인(기본값 도피가 아님을 밝히는 기록)**
`.dddjango/` 산출물 폴더·배너·트래커·task 리스트·AskUserQuestion 채널·게이트 승인·슬라이스 배차·재생성 루프는 27종 docstring 전수에 담당이 없다. `check-idempotency-scope-creep.py` 만 `.dddjango/*/scope.md` 를 **읽지만**, docstring 이 그 소유를 «touched 된 멱등성 산출물이 G1 승인 없이 scope 밖에 추가되는 것» 으로 한정하므로 폴더 규약의 소유자가 아니다 — 그래서 s002 전량이 Coordinator 위임이다.
