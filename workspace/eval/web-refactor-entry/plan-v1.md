# 로드맵 6b — dddjango-web 리팩토링 입구 · 구현 계획 v1 (2026-09-27)

> 실행은 web 수리 관례대로 한다. 작업 트리에서 그대로 하고 브랜치 커밋은 없다. 순서는 **사용자 승인** → 구현 → 행동 시험 → 구현 리뷰 → verify → 승인 후 커밋이다. 릴리즈는 로드맵 9(`make release` · `make release-web`)이고 push 는 그때만 한다. 이 작업의 커밋이 «6b 착륙 전 push 금지»를 푼다.

- **명세**: `design-v5.md`(정본). 이 계획은 그 설계를 파일·순서·검증으로 옮긴다. 설계와 다르면 설계가 이긴다. 행 번호는 HEAD `c9fcadff` 실측이다.
- **목표**: `/dddjango-web:refactor <대상 단위>`(Codex `$dddjango-web-refactor`)가 대상 단위 하나의 기존 web 코드 전체를 dddjango-web 표준으로 점검한다. 검사기 빚(C)과 의미 항목(M)을 G0 에서 묻고, 슬라이스 0 으로 동작 불변 정리한 뒤 G2 에서 잔존을 판정한다. 6a 기능 요청의 슬라이스 0 에도 ④ `--subst-check` 와 ⑤ 기존 테스트 기준선을 더한다.
- **구조**:
  - 러너 `backstop.py` 에 플래그 셋(`--refactor` · `--subst-check` · `--except`)을 더하고, 계산은 `src/debt.py` 에 둔다.
  - 새 도구 `scripts/refactor_audit.py`(plan · check · check-verdict · residual · self-test)를 둔다. dddjango 판을 import 하지 않는다 — web 은 독립 플러그인이다.
  - 나머지는 Coordinator 끝 절 «리팩토링 모드» 신설, 6a 문면 a~e, 에이전트 4, 가이드·문서 개정이다.
- **커밋 묶음**: 경로를 명시해 add 한다(§12). 사용자 파일(`docs/master.html` · `workspace/eval/field-report-4/…` · `workspace/plan/2026-09-26-refactor-campaign/` · `workspace/plan/2026-09-26-request-guide-audit/synthesis-v2.md`)은 넣지 않는다.

## 0. 기준선

- [ ] `make verify-web` green · `bash dddjango-web/scripts/test/fixtures_debt.sh` 55/55 · `claude plugin validate dddjango-web --strict` 를 기록한다.
- [ ] 현장 재생 사본을 만든다. scratch `6b-impl/sds` 에 `git clone --shared /Users/hyun/Desktop/spring_dream_server` 를 뜨고 HEAD 를 적는다(원본은 clone 읽기만 한다).
- [ ] 현장 `.venv` python 경로와 `make -n testp` 출력을 `impl-log.md` 에 적는다(W6-T13·T14 의 ⑤ 명령 원문).

## 1. 입구 (설계 §1)

- **`dddjango-web/commands/dddjango-web.md`**
  - `:5` `disable-model-invocation: true` 1행을 지운다(D1). 다른 frontmatter 키는 그대로 둔다(dddjango `7718407f` 판형).
  - `:15` `빌드할 화면: $feature` 바로 아래에 1행 `요청 원문: $ARGUMENTS` 를 더한다. 이 계획에서 원문 전체 치환자를 쓰는 곳은 이 1행뿐이다.
  - **문면 작성 규칙**(§3 이하 모든 새 문면): 원문 전체 치환자 · 번호 치환자 · 이름 치환자 리터럴을 쓰지 않는다. 가리킬 때는 «`요청 원문:` 줄»이라고 쓴다. 구현 뒤 `grep -n '\$ARGUMENTS\|\$[0-9]\|\$feature\|\$api_url'` 로 새 줄에 0건인지 확인한다(기존 `:15`·`:17-19` 줄은 무변).
- **`dddjango-web/commands/refactor.md`**(새 파일) — `dddjango/commands/refactor.md` 판형:
  - frontmatter: `description` · `argument-hint: "<대상 단위 — 예: web/home · web/static/images> [불편 서술]"` · `disable-model-invocation: true` · `allowed-tools: Skill(dddjango-web:dddjango-web)`. description 문구는 설계 §1-1 그대로다.
  - 본문: «Skill 도구로 `dddjango-web:dddjango-web` 을 부르고, args 로 아래 줄을 한 글자도 바꾸지 말고 그대로 넘겨라. 다른 일은 하지 않는다.» + 빈 줄 + `리팩토링 모드(입구 /dddjango-web:refactor) · 대상: $ARGUMENTS`. 이 파일은 입구라 치환자가 필요하다(문면 작성 규칙은 Coordinator 본문 규칙이다).
- **Codex**
  - `codex-dddjango-web/skills/dddjango-web-refactor/SKILL.md`(새 파일)는 `codex-dddjango/skills/dddjango-refactor/SKILL.md` 판형을 그대로 따른다. 이름은 `dddjango-web-refactor`, 형제 경로는 `../dddjango-web/SKILL.md`, 첫 줄은 `리팩토링 모드(입구 $dddjango-web-refactor) · 대상: <인자>` 다.
  - `…/dddjango-web-refactor/agents/openai.yaml`(새 파일): `display_name` · `short_description`(«대상 단위 하나의 기존 web 코드 전체를 dddjango-web 표준으로 정리(동작 불변 리팩토링 입구)») · `default_prompt`(dddjango 판 영문 판형 — `$dddjango-web-refactor <web unit> [pain points]`) · `policy.allow_implicit_invocation: false`.
  - Codex Coordinator 에는 `요청 원문:` 행을 두지 않는다. 모드 판별은 요청 첫 줄로 한다(§2 의미 미러 표기 차이).

## 2. Coordinator 일반 절 개정 (설계 §2-1 · §7-1 · §7-3 · §10)

행마다 Claude `commands/dddjango-web.md` 를 먼저 고치고, Codex `skills/dddjango-web/SKILL.md` 의 대응 행(괄호 안 행 번호)을 의미 미러로 고친다. Codex 표기는 `${SKILL_DIR}/scripts/` · «네이티브 셸로» · `request_user_input` · `$dddjango-web-refactor` 다.

| # | 위치 (Claude · Codex) | 할 일 |
|---|---|---|
| 2-1 | 스키마 `:61` · `:86` (Codex `:114`~ · 대응 갱신 시점 행) | `mode` 값에 `refactor` 를 더한다. 필드 `test_baseline`(«⑤ 기존 테스트 기준선 명령 원문과 결과 파일 경로 — 슬라이스 0 이 있을 때») 1개를 더한다. 갱신 시점에 «Phase 2 진입 준비 ④ 직후(슬라이스 0 이 있을 때) test_baseline» 을 넣는다 |
| 2-2 | `:120` 절 제목 (Codex `:142`) | «구조 단위 삼분류» → «구조 단위 사분류»(설계 §10 3번) · 목록에 **리팩토링** 1항(표지로만 들어온다). 첫 문단 앞에 **판별 입력 둘**(설계 §2-1)을 둔다. ① `요청 원문:` 줄(Codex 는 요청 첫 줄) 첫머리의 정확한 표지 — 양끝 짝 따옴표를 떼고 본다. ② step 4 에서 고른 폴더의 build-state `mode: refactor` 이고 끝나지 않음. 이어 «표지 손상» 정지 1문장과 «리팩토링 모드는 끝 절 «리팩토링 모드»를 따른다 — 끝 절이 정한 사항이 앞 절의 같은 사항에 우선한다» 1문장 |
| 2-3 | `:128` (Codex `:150`) | `<대상>` 표기 안내 1구(`web/home` · `web/static/images` 류 단위 경로). «따르지 않는 지시» 목록에 «R2·R3 를 줄이는 지시(렌즈 구성·조각 분할·앞 실행 audit 재사용·판정 생략·일괄 채택·결과 지정)» 를 더한다 |
| 2-4 | `:150` 개명·이동 묶음 (Codex `:172`) | §7-3 b: 참조 줄 grep 을 «`web/`을 grep» 에서 **참조 완전성과 같은 pathspec**(`web '*.py' '*.html' '*.css' '*.js' ':(exclude).dddjango-web'`)으로 넓힌다. «참조 파일의 단위는 스캔 단위에 넣는다» 를 «**web/ 아래** 참조 파일의 단위»로 한정한다. web/ 밖 적중 가운데 비테스트 파일이 있으면 «그 개명·이동은 ⓐ 후보에서 빼고 사유 표시». web/ 밖 테스트 파일은 슬라이스 0 규모와 «충돌» 판정(`:153`)에 올린다. 테스트 파일 판정은 설계 §7-2 규칙을 인용한다 |
| 2-5 | `:151` ⓐ′ 대가 줄 (Codex `:173`) | «ⓐ′ 이 요청은 G0 정지하고 정리 착륙 뒤 다시 시작한다» 에 «(의미 점검 포함)» 1구 |
| 2-6 | `:193` 스캔 단위 확인 (Codex `:216` 부근) | §7-3 c: «web/ 밖 테스트 치환 파일은 단위 판정 대상이 아니다» 1구 |
| 2-7 | `:200` Phase 2 진입 준비 (Codex 대응) | ④ check 베이스라인 직후에 «(슬라이스 0 이 있으면) ⑤ 기존 테스트 기준선 캡처 — 아래 «슬라이스 0 호출»의 실행 규칙 · 결과 `<산출물 폴더>/test-baseline.txt` · 명령 원문은 build-state `test_baseline`» 1문장 |
| 2-8 | `:211` 슬라이스 0 호출 (Codex 대응) | 끝 green 목록을 ①~⑤ 로 적는다(설계 §7-1): ④ `backstop.py <루트> --subst-check <git_snapshot> HEAD [--names <명세 슬라이스 0 절 파일>] [--except <배선 적용 파일>]…` exit 0 — 늘 돈다 · ⑤ 기존 테스트 기준선 대비 새 실패 0. **⑤ 실행 규칙** 문단을 설계 §7-1 그대로 싣는다: 명령 찾기 → 단계로 펼치기 → 끝까지 세기(fail-fast·원문 `-r<문자>` 떼기 · `--continue-on-collection-errors` · `-rfE` 를 줄 끝에) → 실패 식별 → 성립 조건(판정 불가: exit 2·3·4·그 밖 · `stopping after` · 기준선 통과 0) → 요동 → 처분. 이어 **끝 green 뒤 재확인** 문단(모든 재호출 뒤 ①~⑤ · ④ 누적 · ⑤ 같은 기준선 · 6a 기능 슬라이스 뒤 재개봉은 재개봉 직전 재기준선 `test-baseline-<HEAD 약칭>.txt`) |
| 2-9 | `:212` 반송 처리 (가) (Codex 대응) | 배선 적용 뒤 «`refactor-scope.md` 에 `배선 적용: <경로…>` 1행 — 뒤의 ④ 에 `--except` 로 넘긴다» 1구 |
| 2-10 | `:216`·`:217` (Codex 대응) | «감사 반영·백스톱 반송이 슬라이스 0 파일이나 web/ 밖 테스트를 바꾸면 끝 green ①~⑤ 를 다시 돈다(슬라이스 0 호출의 재확인 규칙)» 1구씩. `:217` 끝에 «G2 직전 ④ 1회(`git_snapshot..HEAD` · 배선 적용 파일 `--except`)» |
| 2-11 | `:218` G2 배너 (Codex 대응) | 슬라이스 0 이 있었으면 두 행 — `기존 테스트(HEAD <해시> 기준[ · 재기준선 HEAD <해시>]): 단계 s · 기준선 실패 b · 새 실패 0 · 요동 v · 판정 불가 단계 u(사유)`(또는 «명령 없음 — 해당 없음») · `web/ 밖 치환(<git_snapshot>..<HEAD>): 파일 n · 제외(배선 적용) e · --subst-check exit 0` |
| 2-12 | `:222` Phase 3 (Codex 대응) | `--debt-residual` 재실행이 슬라이스 0 을 재개봉하면 2-10 과 같은 재확인 1구 |
| 2-13 | `:9` 첫 문단 «네가 직접 쓰는 것» · `:266` 경계 (Codex 대응) | 리팩토링 모드 audit 산출(`audit/…` 의 리뷰어 표 보존 · `refactor-scope.md` 의미 행 · `plan-names.md` 는 도구가 씀)을 기록물 목록에 1구 |

- **확인**: 2-4 의 pathspec 과 2-8 의 참조 완전성 명령이 같은 문자열인지 `grep -c` 로 대조한다.

## 3. Coordinator 끝 절 «리팩토링 모드 (입구 `/dddjango-web:refactor`)» (설계 §2~§9)

`## 경계`(`:264`) 뒤에 절을 새로 둔다. Codex `SKILL.md` 끝(`:288` 경계 뒤)에도 같은 절을 의미 미러로 둔다. dddjango 끝 절(`dddjango/commands/dddjango.md:222-247`)의 문단 순서를 따르고, 산문 정본이라 graph-owned 마커는 없다. 문단과 설계 출처는 다음과 같다.

1. **머리 문단**(§2-2): 흐름 `R0 → R0′ → R1 → R2 → R2′ → R3 → G0 → Phase 1(슬라이스 0 명세) → G1 → Phase 2(슬라이스 0 만) → G2 → Phase 3`. 기능 슬라이스 · 자리 질문 · 시안(step 5) · 서버 계약 해소(step 3) · 트리비얼 경로가 없다. **끝 절이 앞 절을 바꾸는 곳**은 스캔 단위 · `:193` 확인 · 배선 미비 적용 · `:212` (가)다(단조성).
2. **R0 대상**(§2-3): 단위 1개 · 표기 규칙 · 6a 단위 목록(`:148`) 대조 · 정지 사유 넷(없음 · 2개 이상 · 단위 안쪽 · 기능 혼입) → 폴더 없이 사용법 안내.
3. **R0′ 폴더 · 새 점검 초기화 · 끝남 · 잇기 · G0 전 끊김 · 표지 없는 잇기**(§2-3): slug `refactor-<단위 케밥>` · 후보는 같은 slug 폴더뿐 · 새 점검의 build-state 실행 필드 초기화(목록 8개를 적는다) · `g2_approved: true` = 끝남.
4. **G0 정지 재개**(§2-3): `의미 audit:` 행 · 재사용 조건 넷(4번은 `plan` 재실행 결과 = 그 audit `plan.md`) · 재사용 거부는 본인 직접 답만.
5. **범위**(§3-1 · §3-2): 범위 파일 = 단위 + (영역이면) 전속 정적 파일(판정표는 `plan.md` 가 싣는다 — 문면은 네 판정 이름과 «이중 범위»만) · 키의 범위 소속 1~4 · 편집 줄 키 · 키 전체 줄.
6. **줄 편집 범위**(§3-3): (가) 로드·include 줄(편집 셋 · 블록 틀 신설까지) · (나) 명세 참조 줄 — **`plan --names` 가 계산 · 맨 이름은 옛 모듈 점 경로 적중 파일에서만 · 편집은 참조 치환만(import · 호출·속성 이름 · 템플릿 이름 문자열 · `{% static %}` 경로)** · (다) 키 전체 줄(내용 교정만) · 경계 교차 소비자 = G2 영향 화면.
7. **스캔 단위 · `:193` 리팩토링 판**(§3-4): 1) `plan --names` 실행·경로·exit 기록 2) 범위 밖 편집 대조 → 밖이면 architect 반송 3) (나) 줄 편집 줄 키만 `## G0 재승인`. 범위 밖 «미룰 수 없음» 은 배너 1행.
8. **R1**(§4-1): `backstop.py <루트> --debt-scan --refactor --json <폴더>/debt-g0.json` · 스캔 기록 절 · 표는 범위 안 키만.
9. **R2**(§4-2): `refactor_audit.py plan <단위> --debt <폴더>/debt-g0.json --out <폴더>/audit/<R2 시각>/` → 렌즈 × 조각마다 `dddjango-web:design-review-web`(screen) · `dddjango-web:discipline-reviewer-web`(discipline) 을 `UNIT_AUDIT` 로 부른다(한 응답 안 병렬 · 런타임 한도 단위 반복 허용). 파견 입력 목록 · 표를 그대로 파일에 쓰고 대화에 다시 내지 않는다.
10. **R2′ · R3**(§4-3): `check` → 재인용 1회 → «인용 불일치» 목록. architect «의미 항목 판정» 호출 → `check-verdict` → red 면 1회 재호출 → `--final`. 배너 계수 출처 = `요약:` 행.
11. **별도 요청 유형 넷**(§4-4): 표 대신 문장 넷으로 쓰고 기계 근거는 `check-verdict` 가 본다고 적는다(판정 세부는 도구 몫 — 문면은 유형·가는 곳만).
12. **적용 범위 규범**(§9): ⑴ ⑵ · 끝 문장(외부 동작 보존 · 정적 자산 경로 예외 `coder-web.md:57`) · 적용 한정 어구 닫힌 목록(§7 분류 결과) · 비위반 이동 정지(`:191`)와의 관계 1구.
13. **G0**(§6): 배너 1행 + 슬라이스 0 규모 · 범위 밖 미룰 수 없음 · 배선 미비(보고만) · ⓐ/ⓑ 만(ⓐ′ 없음) · 사용자 판단 질문(대리 불가) · 수정 요청은 «판정 근거 오류 지적»만 · 정리할 것 0 → G0 정지 · 기록 정형(6a 행 항상 + `의미 ⓐ 키:` · `의미 audit:` · 재상정 절 `의미 재상정 키:`).
14. **배선**(§2-2): step 1 배선 6종 검사는 돌고 미비는 배너 보고만 한다. Phase 2 진입 준비 ②·②′·③ 이 없다. `:212` (가) 도 쓰지 않는다 — 원인이 배선 미비면 그 항목은 `ⓐ 재상정`.
15. **Phase 1**(§7-1): architect 슬라이스 0 명세(정형 행 `경로:`·`이름:` · web/ 밖 테스트 치환 파일) → design-review-web(G1 설계 모드) → discipline-reviewer-web 경량(필수) → 7번 대조 → G1. 파견 입력에 `모드 리팩토링` · `M<n>` ⓐ 목록 · 규범 원문.
16. **Phase 2**(§7-1 · §2-2): 진입 준비 ① · ④ · ⑤ 기준선 · ⑥ · 수정 전 렌더 보존(`:237` 판형 — 영향 화면 = 범위 페이지 · 경계 교차 소비자 · 줄 편집 페이지). 슬라이스 0 만. coder-web 입력 = 6a 슬라이스 0 호출 + `M<n>` ⓐ 목록 + 규범 원문. 끝 green ①~⑤ 는 일반 절 2-8 을 가리킨다. 5번 감사의 조각 분할과 슬라이스 0 대조 2항.
17. **G2**(§8): `M_c`(`--debt-residual` — `debt-g0.json` `mode` 로 같은 의미론) · `M_m`(`refactor_audit.py residual <폴더>` → 렌즈별 «잔존 확인» → `--finalize <시각>`) · M>0 → 1회 재개봉 → ①~⑤ 재확인 → 5번 감사·백스톱·`residual` 재실행 → 그래도 M>0 이면 `ⓐ 재상정` STOP(처분 넷 · C 는 `재상정 키:` · M 은 `의미 재상정 키:` + `재상정 키: -`) · G2 배너(6a 빚 3행 교체 · 다섯 목록 · 기존 테스트 · 치환 확인 · 시각 대조).

- **길이 관리**: 끝 절은 dddjango 끝 절(약 25행 · 문단 13개)보다 길어진다. 판정 세부(판정표 · 기계 근거 · 술어 목록)는 도구와 `plan.md` 에 두고, 문면에는 «무엇을 돌리고 무엇을 기록하고 어디서 멈추는가»만 남긴다. 목표 40행 안팎이다.
- **확인**: 끝 절에서 `의미 ⓐ 키`·`의미 재상정 키`·`의미 audit` 문자열이 `debt.py` 상수(§4)와 같은지 grep 으로 대조한다(6a 가 한 방식 그대로).

## 4. 러너 — `backstop.py` · `src/debt.py` · `src/check_structure.py` (설계 §4-1 · §6 · §7-2)

- **`check_structure.py`**: 공개 함수 `run_skeleton(ctx) -> List[Finding]` 1개를 더한다(`_skeleton(ctx)` 를 그대로 부른다). WS5 게이트(`:163-167`)는 무변이다.
- **`debt.py` — `--refactor`**
  - `scan(root, refactor=False)`: `refactor` 면 `run_structure` 뒤에 `run_skeleton(ctx)` 발견을 더하고(`from_files` 는 비게이트라 `is_added_dir` 가 늘 참 — 모든 기존 단위가 판정 대상), 6a WS5 notice 재작성(`:138-140`)을 하지 않고 `_WS5_NO_BASE` notice 를 떨군다.
  - `_exempt(findings, refactor=False)`: 6a 규칙 그대로에 한 갈래를 더한다. `refactor` 이고 core 중복이 없을 때, WP1 legacy core 경로 p 에 대해 «메시지가 `<WP2 사유> — p` 인 WP2 발견»이 없으면 그 WP1 발견을 면제하지 않는다. 있으면 WP1·WP2 한 쌍 모두 면제 유지다. WP5 와 WP2 legacy 면제는 그대로다.
  - JSON 에 `"mode": "refactor" | "feature"` 를 더한다. `SCHEMA` 는 그대로다(필드 추가 · 없으면 `feature` 로 읽는다).
  - `cli_residual`: `debt-g0.json` 의 `mode` 를 읽어 `scan(root, refactor=(mode == 'refactor'))` 로 다시 스캔한다.
- **`debt.py` — `refactor-scope.md` M 행**(§6)
  - 상수 `ROW_M_A = '의미 ⓐ 키'` · `ROW_M_RESUBMIT = '의미 재상정 키'` · `ROW_M_AUDIT = '의미 audit'`.
  - `_ROW_RE` 이름 목록을 여섯으로 넓힌다. 값 검사는 이름별이다: `C[1-9]\d*` · `M[1-9]\d*` · `\d{8}-\d{6}`.
  - `parse_scope` 는 세 행을 함께 수집한다. `residual_sets` 는 C 행만 접는다(결과 무변).
  - 새 함수 `residual_m_sets(text)`: 마지막 `## G0` 부터 순서대로 `의미 ⓐ 키` 를 더하고 `의미 재상정 키` 를 빼고, 재승인에서 되살린다. 마지막 `## G0` 절에 `의미 ⓐ 키:` 와 `의미 audit:` 가 정확히 1행씩 없으면 `DebtError` 다. `refactor_audit.py residual` 이 import 한다.
- **`debt.py` — 명세 정형 행 · 참조 grep**(§3-3 · §7-2 — `plan` 과 `--subst-check` 가 같은 함수를 쓴다)
  - `parse_spec_pairs(text) -> (paths, names)`: 정형 행 `경로: <옛> → <새>` 와 `이름: <옛 모듈>.<옛 이름> → <새 모듈>.<새 이름>` 을 읽는다. 코드 울타리 안 줄은 건너뛴다(6a `_FENCE_RE`). 형식 어긋남은 `DebtError` 다.
  - `reference_lines(root, needles, word=False) -> List[(path, line, text)]`: 6a 참조 완전성 pathspec 으로 `git grep -n -F [-w] -e …` 를 돌린 적중이다. 꼬리 규칙 함수 `tail_of(path)`(`static/` 접두 제거 · `.py` 면 점 경로 추가)도 여기로 모은다. Coordinator 문면의 grep 명령과 같은 문자열을 상수로 둔다.
- **`debt.py` — `--subst-check`**(§7-2 · 새 함수 `cli_subst_check(root, base, target, names_file, excepts)`)
  - 쌍: 경로 쌍(`git diff -M --name-status <base>..<target> -- web/`) · 폴더 쌍(옛 폴더 전체가 같은 접두 변환 · 대상 트리에 옛 폴더 없음) · 이름 쌍(`--names` 의 `이름:` 행 — `경로:` 행은 무시).
  - 대상 파일: `git diff --name-only <base>..<target>` 중 web/ 밖이면서 `.dddjango-web/` 아래가 아닌 파일. `--except` 경로를 뺀다.
  - 테스트 파일 판정(`test`·`tests` 성분 · `test_*.py` · `*_test.py` · `conftest.py`)이 아니면 exit 2(«테스트 밖 web/ 밖 파일»).
  - `.py`: 원문 `ast` 파싱(`git show <rev>:<path>`) → 블록별 연속 import 구간 바인딩 다중집합(대상 쪽에 역치환 — 점 경로 전체 쌍 · 접두 쌍은 **점 성분 경계로만** · 맨 이름 쌍은 `as` 없는 바인딩 끝 성분) → import 밖은 텍스트 역치환본(긴 것부터 동시에 · 단어 경계)의 `ast.dump` 대조. 그 밖 파일은 줄 다중집합 대조다.
  - exit 0 = 치환만(요약 `[backstop] 치환 확인 — 파일 n · 제외 e`) · 2 = 어긋남(파일:줄 또는 파일:구간 출력) · 1 = 실행 불능(파싱 실패 · 커밋 부재 · `--except` 값이 web/ 아래이거나 테스트 파일).
- **`backstop.py`**
  - 인자 루프(`:141-176`)에 `--refactor` · `--subst-check <기준> <대상>`(두 값) · `--names <파일>` · `--except <경로>`(반복)를 더한다.
  - 배타 검사(`:188-196`): `--refactor` 는 `--debt-scan` 과만 쓴다. `--subst-check` 는 다른 모든 모드 플래그와 배타다. `--names`·`--except` 는 `--subst-check` 전용이다. 위반은 기존 «단독 모드» 오류 문자열로 exit 1 이다.
  - 헤더 주석(`:6-16`)과 `_USAGE`(`:40-43`)를 갱신한다.
- **Codex byte 미러**: `codex-dddjango-web/skills/dddjango-web/scripts/` 로 같은 파일을 복사한다(`verify-web` 의 `diff -rq` 가 본다).

## 5. 도구 — `dddjango-web/scripts/refactor_audit.py` (설계 §5)

- 모양은 dddjango `refactor_audit.py`(1,521행)를 따르되 복사하지 않고 필요한 것만 새로 쓴다. rulepack · outline · sections 는 없다. 목표는 800행 안팎이다.
- **공통**: `--platform claude|codex`(기본: 자기 위치로 판별 — `…/codex-dddjango-web/…` 아래면 codex) · `--plugin-root`. 모든 하위 명령이 `요약:` 1행을 낸다. `src/debt.py` 를 import 한다(`debt_universe` · `tail_of` · `reference_lines` · `parse_scope` · `residual_m_sets` · `parse_spec_pairs`).
- **상수**: 단위 목록 규칙(6a `:148` — 영역 · `static/<하위>` · `design_system` · `base` · 컨테이너 `web/*.py` · `client/<bc>`) · 렌즈별 점검 절 목록(§4-2 — 절 번호 전수는 이 단계에서 문서를 열어 확정한다) · 경로 사상(Claude `skills/<x>/…`·`agents/<n>.md`·`commands/dddjango-web.md` ↔ Codex `skills/<x>/…`·`skills/dddjango-web-<n>/SKILL.md`·`skills/dddjango-web/SKILL.md`) · 적용 한정 어구 · 긍정 술어 · 부정형 · 무효 접미(`는`·`고`·`라는`·`라고`·`면`)(§7 분류 결과).
- **`plan <단위> --debt <json> --out <audit>`**: 범위 파일(판정 순서 무참조 → 비영역 → 경계 교차 → 영역 전속 · 규칙 이름 · 참조 줄) · 경계 교차 · 경계 교차 소비자 · 줄 편집 (가) · 참조 치환 줄 · 편집 줄 키 · (다) 키 전체 줄 · 범위 안 키 문자열(옆에 `C<n>`) · 렌즈 × 조각(화면 폴더 묶음 → 5,000행 문턱) · 점검 절 · `HEAD` · `범위 미커밋 변경 N` · web/ 밖 참조 줄 → `plan.md`. 단위 목록 밖·부재면 exit 1.
- **`plan … --names <명세 파일>`**: §3-3 (나) 계산 → `plan-names.md`(`plan.md` 무변). 맨 이름은 옛 모듈 점 경로(`-w`) 적중 파일의 줄만 쓰고, 범위 파일 줄은 뺀다. 편집 줄 키와 키 전체 줄은 R0 과 같은 함수로 계산한다. 쌍 0 이면 exit 0 «(나) 0» 이다.
- **`check <audit>`**: 리뷰어 표 행마다 ① 인용 실재(dddjango 와 같은 `normalize` — 공백·마크다운 강조 정규화) ② `파일:행` 실재 · 범위 안(범위 파일 또는 줄 편집·참조 치환 줄) → `check.md`. 인용 문서는 그 플랫폼 설치본에서 찾는다.
- **`check-verdict <audit> [--feedback <파일>] [--final]`**: 설계 §5-3 표 다섯 출구 · 문장·문단 분할 · 긍정 술어·부정형·무효 접미 · 제외 ⑤ 같은 문장(괄호 부속절·`예외:` 뒤 예외) · 오탐 같은 문단 · 별도 요청 네 유형 기계 근거(§4-4 — 외부 동작은 `ast` 호출 구간 · 모듈 상수 템플릿 인자 · API 계약 리터럴 결속과 속성 이름 = 키 불성립 · 경계 교차·web/ 밖은 편집할 곳 칸 · import 줄 불성립) · 병합 · 사용자 판단 · 대리 출처 축소 red → `verdict-log.md` append · `요약:` · G0 목록 파일(제외 행 «위반 인용 ↔ 제외 인용»). exit 0 · 2 · 1.
- **`residual <폴더> [--finalize <시각>]`**: §8 — `debt-g0.json` `mode == refactor` 필수 조건(§6) · 무변 파일 결정적 잔존(`git_snapshot` 이후) · 렌즈별 묶음 `residual/<시각>/review-<렌즈>.md` · `--finalize` 는 `result-<렌즈>.md` 를 읽어 새 `파일:행` 근거 없는 «해소»는 잔존.
- **`--self-test`**: 점검 절 실재 · 경로 사상 · 상수 = Coordinator 끝 절 규범 문면 «…» 대조 · 극성 표본(설계 §5-2 표 · «할 수 있다면» 포함).
- **Codex byte 미러**: 같은 파일을 `codex-dddjango-web/skills/dddjango-web/scripts/` 에 둔다.

## 6. 에이전트 4 · 역할 SKILL 4 (설계 §4-2 · §4-3 · §7-1 · §7-2 · §9)

각 파일을 먼저 고치고 Codex `skills/dddjango-web-<역할>/SKILL.md` 를 의미 미러로 고친다.

- **모두**(모드 무관 위치 — `## 입력` 끝): «파견 입력에 적용 범위 규범이 실려 있으면 그 규범이 정한 몫과 때를 따른다» 1행.
- **`design-review-web.md`**: `## 단위 점검 모드`(`UNIT_AUDIT`) 절을 `## G1 설계 모드 산출 형식`(`:27`) 앞에 둔다.
  - 모드는 명시 입력이 있을 때만 켜진다. 기본은 지금의 G0 입력범위·G1 설계 모드다.
  - 렌즈 screen 점검 절 목록은 파견 입력으로 받는다. implementation-ui 는 플러그인 루트 경로로 연다.
  - 산출 표 8열(설계 §4-2 · 위치마다 파일 경로 · 규칙 문구 없는 항목 금지 · `근거 없음(불편 #k)` 행 · 테스트 충분성은 점검 항목 아님).
  - 하위 `잔존 확인`(설계 §8 입력·산출).
  - `## 경계` «구현 표기는 보지 않는다»(`:59`)에 «단위 점검 모드 예외(적용 범위 규범 ⑵)» 1구.
- **`discipline-reviewer-web.md`**
  - 같은 `## 단위 점검 모드` 절을 둔다(렌즈 discipline).
  - `## 점검 항목`(`:51`)에 슬라이스 0 대조 2항을 둔다: «범위 밖 diff = 줄 목록 (가)·(나)·(다) · 참조 치환 줄 · 블록 틀 · web/ 밖 테스트 치환뿐 · (나) 줄은 옛 참조 → 새 참조 치환뿐» · «이름 치환은 정의 본문이 이름 말고 같을 때만(결정 9)».
  - `## 감사 빈도`(`:49`)에 «리팩토링 모드는 R2 조각 단위 분할 · 마지막 홀리스틱은 조각 종합과 경계 교차만» 1구.
- **`design-architect-web.md`**
  - `## 의미 항목 판정 모드` 절: 입력(`check.md` · 키 문자열 목록 · 규범 원문 · 플러그인 루트) · `verdict.md` 형식(`M<n> | 원 행 | 판정 | 근거 | 파일:행 목록`) · 판정 범주 · 근거 칸 규칙(제외·오탐 = 인용 · 별도 요청 = 리뷰어 «아니오» + 편집할 곳 파일:행 / 리터럴 · 병합 = 대상 · 사용자 판단 = 반대 방향 인용) · 비용·일정·규모는 빼는 사유가 아님.
  - `## 경계` 1구: «리팩토링 모드 판정(`verdict.md`)은 예외 — 코드가 아니라 판정 표를 쓴다».
  - `:55` 슬라이스 0 절: 개명·이동은 정형 행 `경로: <옛> → <새>`(web 기준 상대 · 폴더면 `/` 끝) · 정의 이동·이름 변경은 `이름: <옛 모듈>.<옛 이름> → <새 모듈>.<새 이름>` · web/ 밖 테스트 치환 파일(두 모드).
  - `## 경계` «백엔드 내부를 열람하지 않는다»(`:86`)는 무변이다. 테스트 파일은 백엔드 내부가 아니다 — 치환 파일 목록은 Coordinator 가 `plan.md` web/ 밖 참조 줄로 준다.
- **`coder-web.md`**: `:38` 산출에 «(슬라이스 0 의 명세 테스트 치환 포함)» · `:75` 에 «슬라이스 0 에서 명세 슬라이스 0 절이 적은 web/ 밖 **테스트 파일**의 옛 경로·옛 이름 → 새 경로·새 이름 치환만 한다(판정·단언은 바꾸지 않는다)» 1구 · `:57` 슬라이스 0 문단에 «(나) 줄은 참조 치환만» 1구.

## 7. 적용 한정 어구 · 긍정 술어 · 부정형 전수 분류 (설계 §9 · §5-3)

- 대상: Claude `commands/dddjango-web.md` · 에이전트 4 · 스킬 5(SKILL + references — `undecidable-web.md` 포함)의 적용 한정 어휘 줄(진단 2-2 목록 — touched · 신규 단위 · 새 파일 · 레거시 · 브라운필드 · legacy · 기존 코드 · 이번 작업 · added).
- 줄마다 T(적용 조건 한정 → 목록 어구 후보) · N(외부 계약·동작 보존 · 절차 · 무관) · T*(두 몫 — 풀리는 몫만)로 가른다. 어구는 결합형으로만 싣는다.
- 같은 단계에서 긍정 술어·부정형 목록을 렌즈 문서 전수로 돌려 적중 문장 표를 만든다. `(쓸|둘|할) 수 있다` 를 적용할 «규범 문서 목록»을 여기서 확정한다(discipline-cleancode 서술문 5개 포함 여부 명시 · X4 m5).
- 산출: `workspace/eval/web-refactor-entry/phrase-classification.md`(줄 · 분류 · 사유 · 뽑은 어구). 이 표가 §3-12 문면 목록과 §5 상수의 출처다.

## 8. 가이드 · 문서 (설계 §10)

- **REQUEST_GUIDE §6**(`dddjango-web/REQUEST_GUIDE.md:205-207` 문단 교체 · dddjango `REQUEST_GUIDE.md:163-183` 판형): 입구 사용법(대상 단위 표기 · 불편 서술 · 동작 불변 · 기존 테스트가 안전망 — 정리 전후로 Coordinator 가 기존 테스트를 기준선 대비로 돌린다 · 테스트를 고치거나 보태지 않는다 · 축소 지시 불복 · 여러 단위는 단위마다). **§7**: «사용자 판단 항목은 대신 답하지 않는다» 1행. Codex `REQUEST_GUIDE.md` 는 byte 미러다.
- **README**: `:108-109` 사용 예 표에 web 리팩토링 행 1개 · `:318` «커맨드 1» → «커맨드 2(`/dddjango-web:dddjango-web` · `/dddjango-web:refactor <대상 단위>` — Codex `$dddjango-web-refactor`)».
- **AGENTS.md** `:24-25`: «커맨드 1» → «커맨드 2(메인 + 리팩토링 입구)» · 스크립트에 `refactor_audit.py` · 러너 플래그에 `--refactor`·`--subst-check`.
- **plugin.json**: `dddjango-web/.claude-plugin/plugin.json` `description` 과 `codex-dddjango-web/.codex-plugin/plugin.json` `interface.longDescription` 에 리팩토링 입구 1구(로드맵 5 선례). `version` 은 건드리지 않는다(릴리즈 몫).
- **houserules `final.md` §7**(`:197-207`): 명령 판형에 `--debt-scan --refactor` · `--subst-check <기준> <대상> [--names] [--except]` 2행 · 빚 모드 문단에 면제 해제 범위(WS5 · WP1 조건부) 1구 · 치환 확인 1구. Codex byte 미러.
- **6a 기록 정정 메모**: `workspace/eval/web-g0-debt/behavior-tests.md` W-T1r2 행 «참조 완전성 대상 밖» · W-T9 «5줄»에 «6b 설계 §7-3 잠복 모순 참조 — 테스트 2줄이 참조 완전성에 든다» 메모.

## 9. `Makefile` verify-web

- `run_fixtures.sh` 뒤에 `python3 dddjango-web/scripts/refactor_audit.py --self-test --platform claude --plugin-root dddjango-web` 과 Codex 판(`--platform codex --plugin-root codex-dddjango-web`) 2행을 둔다.
- 새 스크립트 byte 미러는 기존 `diff -rq`(scripts 폴더 전체)가 잡는다(확인만 한다). Codex 새 스킬 폴더 `dddjango-web-refactor/` 는 byte 대상이 아니다(의미 미러).
- 봉인: Makefile 을 고치므로 6a 와 같이 `manifest_seal.py --write` → feat 커밋 → 재발행 chore 커밋이다.

## 10. 픽스처 (설계 §11 러너 사례)

- **`fixtures_debt.sh`**(기존 55 무변 확인 + 새 사례)
  - D24 `--debt-scan --refactor`: 합성 골격 미비 단위 → WS5 키(폴더 키 · 컨테이너 빈 경로 키) · notice 없음 · JSON `mode: refactor`.
  - D25 WP1 조건부: defer 없는 legacy 태그 → WP1·WP2 한 쌍 면제 유지 · defer 있는 legacy 태그 → WP1 키.
  - D26 `--debt-residual` 이 `mode` 를 따름(refactor 동결본 → WS5 키 잔존 판정).
  - D27 배타: `--refactor` 단독 · `--refactor --diff-base` · `--names` 단독 · `--except` 단독 → exit 1 «단독 모드».
  - D28 M 행: `의미 ⓐ 키:` 가 있는 절 → 6a C 판정 무변 · `의미 ⓐ 키: C1` 값 형식 어긋남 → exit 1.
- **`fixtures_subst.sh`**(새 파일 · W6-T8 사례 전부): 경로 치환 · 이름 쌍 · import 재정렬 · 교환 쌍 · 폴더 이동 점 경로 · 정의 이동(모듈 머리 · `TYPE_CHECKING` · 함수 안) · 괄호 여러 줄 · 블록 사이 이동 red · 파일 하나 이동 → 폴더 쌍 없음 · 넓은 sed red · 단언 변경 red · 테스트 밖 web/ 밖 red · `import N` 추가 red · `.dddjango-web/` 무시 · 대상 `HEAD` · **접두 성분 경계** · **`--except` 제외 green · `--except` 테스트 파일/web/ 아래 → exit 1**.
- **`fixtures_refactor_audit.sh`**(새 파일 · W6-T5·T6·T7·T10 러너 사례): `plan` 판정 순서·소유자 전이·경계 교차 소비자·줄 편집·편집 줄 키·키 전체 줄(합성 트리) · `plan --names`(옛 모듈 적중 파일 한정 · 호출 줄 · 성분 경계 · 쌍 0 · 형식 어긋남) · `check` · `check-verdict`(W6-T6 사례 전부 · 속성 이름 = 키 · 조건절) · `residual`(W6-T7) · `--self-test` 양 플랫폼 · G0 정지 재개 네 갈래의 `plan` 재계산 대조.
- 현장 모양 사례(W6-T5 의 현장 파일 판정 · W6-T0 의 참조 치환 줄)는 픽스처가 아니라 행동 시험에서 현장 사본으로 확인한다(픽스처에 현장 경로를 박지 않는다).

## 11. 행동 시험 (설계 §11 · 실하네스 = 6a 하네스 · 무거운 실행은 하나씩)

- 하네스: `claude -p --output-format stream-json --verbose --settings '{"enabledPlugins":{"dddjango-web@changja88-dddjango":false}}' --plugin-dir <저장소>/dddjango-web "<요청>"`(W6-T12 는 맨 프롬프트). Codex 는 `codex exec --json --sandbox workspace-write`(플러그인 끔 · 스킬을 사본 `.agents/skills/` 로 복사).
- 순서(싸고 결정적인 것 먼저):
  1. 러너·도구 픽스처(§10) green.
  2. W6-T1 · T2(입구 정지 — 모델 호출 짧음).
  3. W6-T0(`web/static/images` — G0 배너까지).
  4. W6-T5 현장 판정(plan 만 · 모델 호출 없음).
  5. W6-T13 · T14 책상 재생(⑤ 실행 — 현장 DB 없는 단계 약 6분 × 가지 · postgres 단계는 1회만).
  6. W6-T9 책상 재생.
  7. W6-T3(`web/home` R2~R3 실하네스 — 약 $20~40).
  8. W6-T10(G0 정지 재개 네 갈래 — T3 폴더 재사용).
  9. W6-T11 회귀(6a W-T2 · W-T1).
  10. W6-T12 관찰.
  11. W6-C(Codex).
- 합격 기준은 설계 §11 표 그대로다. 결과는 `workspace/eval/web-refactor-entry/behavior-tests.md` 에 행마다 적는다(요청 · 결과 · 합격 · 비용·벽시계 · 원 기록 경로).
- 비용 상한: 모델 호출 합계 약 $80(T3 $20~40 · T0 · T11 · C). 넘을 조짐이면 멈추고 보고한다.

## 12. 구현 리뷰 · verify · 봉인 · 커밋

- **구현 리뷰**: 독립 리뷰어 1(6a 리뷰 Q 판형 — 계획 커버리지 표 · 러너 경계 입력 scratch 실험 · fail-open 은 blocker · 문면 모순 · 미러 · 행동 시험 관찰 판정). 저장소에는 `review-R-impl.md` 1개만 쓴다.
- **verify**: `make verify-web` green · `claude plugin validate dddjango-web --strict` · `make verify`(봉인 전 core red 는 예상 — Makefile 편집) · 미러 `cmp` 전수.
- **봉인**: `manifest_seal.py --write` 가 커밋 전 마지막 쓰기다. 재발행은 따로 chore 커밋으로 한다.
- **커밋 경로**(명시 add): `dddjango-web/commands/` · `dddjango-web/agents/` · `dddjango-web/scripts/`(바이트코드 제외) · `dddjango-web/skills/discipline-web-houserules/references/final.md` · `dddjango-web/REQUEST_GUIDE.md` · `dddjango-web/.claude-plugin/plugin.json` · `codex-dddjango-web/skills/`(`dddjango-web` · `dddjango-web-refactor` · 역할 4 · houserules final) · `codex-dddjango-web/REQUEST_GUIDE.md` · `codex-dddjango-web/.codex-plugin/plugin.json` · `Makefile` · `README.md` · `AGENTS.md` · `workspace/eval/web-refactor-entry/` · `workspace/eval/web-g0-debt/behavior-tests.md` · `workspace/plan/2026-09-26-refactor-path-repair/progress.md` · `workspace/design/ontology-adoption-map.html` · 봉인 manifest.
- **커밋은 사용자 승인 뒤에만** 한다.

## 13. 순서 · 의존 · 작업량

| 단계 | 의존 | 일 |
|---|---|---|
| §0 기준선 | — | 0.1 |
| §7 전수 분류 | — | 0.5~1 |
| §4 러너(스캔 · M 행 · 정형 행 · 참조 grep · `--subst-check`) + §10 debt·subst 픽스처 | §0 | 2~2.5 |
| §5 도구 + §10 audit 픽스처 | §4 · §7 | 5~6 |
| §1 입구 · §2 일반 절 · §3 끝 절 · Codex 미러 | §4 · §5 계약 확정 · §7 | 3.5 |
| §6 에이전트 4 · 역할 SKILL 4 | §3 | 1.5 |
| §8 가이드·문서 · §9 Makefile | §3 | 0.5 |
| §11 행동 시험 | 전부 | 2~2.5 |
| §12 구현 리뷰 · verify · 봉인 | §11 | 0.5~1 |
| **합계** | | **약 16~18.5일** |

- 병렬 가능: §7 과 §4 는 서로 무관하다. §6 은 §3 문면이 잡히면 같이 간다.
- 중간 멈춤점: §4·§5 픽스처 green 뒤와 §3 끝 절 초안 뒤에 진행표·조감도를 갱신한다.

## 부록 A. 설계 → 계획 대응

| 설계 | 계획 |
|---|---|
| §1 입구 | §1 |
| §2-1 모드 판별 | §2-2 · §2-3 · §3-1 |
| §2-2 흐름 · 배선 | §3-1 · §3-14 · §3-16 |
| §2-3 R0 · 폴더 · 재개 | §3-2 · §3-3 · §3-4 |
| §3-1~§3-2 범위 · 키 소속 | §3-5 · §5 plan |
| §3-3 줄 편집 · (나) | §3-6 · §4 정형 행·참조 grep · §5 plan `--names` · §6 architect·DR · §10 |
| §3-4 스캔 단위 · `:193` | §3-7 |
| §4-1 R1 러너 | §4 `--refactor` · §3-8 · §10 D24~D27 |
| §4-2 R2 렌즈 | §3-9 · §5 상수 · §6 리뷰어 2 |
| §4-3 R2′ · R3 | §3-10 · §5 check · check-verdict · §6 architect |
| §4-4 별도 요청 | §3-11 · §5 check-verdict |
| §5 도구 | §5 |
| §6 G0 기록 정형 | §3-13 · §4 M 행 · §10 D28 |
| §7-1 끝 green · ⑤ · 재확인 | §2-7 · §2-8 · §2-10 · §2-12 · §3-16 |
| §7-2 `--subst-check` | §4 · §6 coder · §10 subst |
| §7-3 6a 문면 a~e | §2-4 · §2-6 · §2-8 · §2-9 · §2-10 · §6 coder |
| §7-4 결정 17 | §8 REQUEST_GUIDE §6 · 보고 |
| §8 G2 | §2-11 · §3-17 · §5 residual |
| §9 적용 범위 규범 | §3-12 · §6 모두 · §7 |
| §10 문면 갱신 | §2 · §6 · §8 · §9 |
| §11 행동 시험 | §10 · §11 |
