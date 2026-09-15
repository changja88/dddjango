# 구현 리뷰 2 — 규범·미러 (절단 충실도 수리 A·B)

검토 시각 2026-09-15 · 커밋 전 작업 트리(HEAD `cd1d07af`) · 파일 수정 0.

BLOCKER 2 · MAJOR 7 · MINOR 4.

---

### [BLOCKER] `make verify` RED — 새 G1 명령줄이 재동결 경로 치환 불변식(D1)을 깬다

**무엇이 어긋났나.** 새로 넣은 토큰 처분 점검 명령줄이 폐기·교체 대상 산출물을
`<산출물 폴더>`로 가리킨다. `web_refreeze_contract.py`의 D1은 이 자리표시자가 재동결 중
staging(`<대상 폴더>`)을 가리킬 것을 요구하므로 양 런타임 정본에서 red다. 같은 줄의 기존
모션 점검은 이미 `--audit <대상 폴더>/render-audit.json`으로 치환돼 있어 새 문장만 규약을
어겼다.

**근거.**

```
$ make verify
  ✓ verify-base-core green (67초)      ✓ verify-ontology green (76초)
  ✓ verify-base-backstop green (109초) ✖ verify-web RED (117초)
  ✓ verify-base-cross green (230초)    ✓ verify-base-regen green (247초)
  ✖ verify RED — verify-web (247초 · 전체 로그: /tmp/djr-verify.TYfbr2)

[web-refreeze-contract] D1 dddjango-web/commands/dddjango-web.md:168: 재동결 중 staging을
  가리켜야 한다 — <대상 폴더>로 바꾼다 (<산출물 폴더>/design-tokens.json)
[web-refreeze-contract] D1 codex-dddjango-web/skills/dddjango-web/SKILL.md:191: (동일)
[web-refreeze-contract] 위반 2건
```

검사기는 줄당 첫 히트만 보고하므로 보고된 2건이 전부가 아니다. `web_refreeze_contract.py:50`
의 `DISCARD_NAMES` 정규식을 새 문장에 직접 적용하면 파일당 3건이다:

```
dddjango-web/commands/dddjango-web.md 168 → ['design-tokens.json', 'design-ref', 'screen-meta.json']
codex-dddjango-web/skills/dddjango-web/SKILL.md 191 → ['design-tokens.json', 'design-ref', 'screen-meta.json']
```

**수정 방향.** 두 파일의 새 문장에서 `<산출물 폴더>/design-tokens.json` ·
`<산출물 폴더>/design-ref` · `<산출물 폴더>/screen-meta.json`를 모두 `<대상 폴더>/…`로
바꾼다(총 6곳). `<설계 명세>`는 보존 대상(design-spec.md)의 추상 자리표시자라 D2에 걸리지
않으므로 그대로 둔다. 고친 뒤 `python3 workspace/tools/web_refreeze_contract.py`가 green인지
확인한다.

---

### [BLOCKER] `--screen-meta` 무조건 전달 — 참조 HTML/URL·이미지 시안 빌드에서 새 검사가 exit 1(미실행)로 끝난다

**무엇이 어긋났나.** 발동 조건은 `has_design_tokens ∧ design-ref 존재`인데 명령줄은
`--screen-meta <…>/screen-meta.json`을 **항상** 붙인다. `screen-meta.json`은 `extract_dc.py`
(dc 동결 경로, Coordinator step 5-4)만 만든다. 참조 HTML/URL·이미지 시안 경로(step 5-5)는
`extract_design.py`를 쓰는데 이 스크립트에는 `--meta`가 없다. 그 빌드들은 `has_design_tokens`
가 true인데 `screen-meta.json`이 없고, 검사기는 그 자리에서 `die()` → exit 1이다. Coordinator
문면상 exit 1은 «미실행 취급»이므로 **그 빌드 계열 전체에서 T1a/T1b/T1c 집행이 한 번도 서지
않는다**.

**근거.**

- `dddjango-web/scripts/check_token_disposition.py:157-174` — `design_bodies()`가
  `read_text(screen_meta)` → `check_token_disposition.py:68-70` `die(f"파일 없음: {path}")`.
- 실행 확인(scratchpad 임시 빌드, `screen-meta.json` 부재):
  ```
  $ python3 …/check_token_disposition.py --spec-only design-spec.md design-tokens.json \
      design-ref --screen-meta screen-meta.json
  [token-disposition] 파일 없음: screen-meta.json
  exit=1
  ```
- `dddjango-web/scripts/extract_design.py:469-487` — 인자는 `--out`·`--manifest`·
  `--from-ds-manifest`뿐, `--meta` 없음. `screen-meta.json`을 쓰는 스크립트는
  `extract_dc.py:277` 하나다.
- `screen-meta.json`이 선택 산출물이라는 반대 증거: `check_design_evidence.py:758-759`가
  `if isinstance(root, dict) and meta.is_file():`로 **존재할 때만** 본다.
- 상충 신호(판단 재료로만 적는다): `refreeze.py:39-40` `REQUIRED_STAGING`에는
  `screen-meta.json`이 무조건 들어 있다 — 재동결 쪽은 전 빌드에 있다고 전제한다. 두 전제가
  어긋나 있으므로 «항상 있다»로 넘기지 말고 한쪽으로 정리해야 한다.

**수정 방향.** 바로 옆 모션 점검이 이미 쓰는 판형을 그대로 따른다 —
«(동결 실측이 v2면 `--audit …` 부가)»처럼 «(`screen-meta.json`이 있으면 `--screen-meta …`
부가)»로 조건부화한다. 양 런타임 정본 모두. (대안: 검사기가 screen-meta 부재를 `warn` +
전 파일 대조로 강등 — 이미 «일치하는 시안 파일이 없다» 경로에 같은 강등이 있으므로 판형이
있다. 다만 검사기 수정은 픽스처·byte 미러 동반이라 규범 조건부화가 더 싸다.)

---

### [MAJOR] Codex 미러에 Claude 어휘 «Bash로 실행한다»가 2곳 누출

**무엇이 어긋났나.** `codex-dddjango-web/skills/dddjango-web/SKILL.md`는 전 문서가
«네이티브 셸로 실행한다»로 쓰여 있는데(Codex에는 `Bash` 도구 이름이 없다), 이번에 추가된
두 문장만 Claude 정본 문구를 그대로 복사해 «Bash로 실행한다»로 남았다.

**근거.**

```
$ grep -rn "Bash로 실행" codex-dddjango-web/
codex-dddjango-web/skills/dddjango-web/SKILL.md:191   ← 토큰 처분 집행 점검(신규)
codex-dddjango-web/skills/dddjango-web/SKILL.md:210   ← 절단 여유 정적 검사(신규)
```

두 줄에 남아 있던 기존 문장들은 모두 «네이티브 셸로 실행한다»다(정규화 diff에서 그 4곳만
차이로 뜨고, 신규 문장은 «Bash로»로 **일치**해 차이가 뜨지 않았다 — 즉 미러가 Claude 어휘를
그대로 받았다는 뜻이다).

**수정 방향.** Codex SKILL.md의 신규 두 문장에서 «Bash로 실행한다» → «네이티브 셸로
실행한다». (경로 변수 자체는 정상이다 — 신규 3개 명령줄 모두 Claude는
`${CLAUDE_PLUGIN_ROOT}`, Codex는 `${SKILL_DIR}`를 쓴다. `grep -rn CLAUDE_PLUGIN_ROOT
codex-dddjango-web/` 히트는
`skills/discipline-web-houserules/references/final.md:196` 하나이고 이번 변경 밖의 기존
byte 미러다.)

---

### [MAJOR] G1 step 6의 «이 단계를 생략한다»가 새 점검 **앞**에 있어 정적 화면 빌드에서 통째로 건너뛸 수 있다

**무엇이 어긋났나.** step 6은 한 문단이고 순서가 ① server-contract 절단 → ②
«동결본이 없으면(정적 화면 한정 진행) **이 단계를 생략한다**» → ③ «같은 시점 — 모션 처분
표 기계 점검» → ④ «같은 시점 — 토큰 처분 집행 점검»이다. openapi 동결본이 없는 빌드는
Coordinator가 «이 단계 = step 6»으로 읽고 ③④까지 건너뛸 수 있다. 하필 **openapi 동결본이
없는 정적 화면 빌드가 시안 토큰을 가진 대표 사례**라 새 검사의 주 대상과 생략 분기가 겹친다.

**근거.** `dddjango-web/commands/dddjango-web.md:168` ·
`codex-dddjango-web/skills/dddjango-web/SKILL.md:191` — 한 줄 안의 문장 순서가 위와 같다.
모션 점검(2026-08-25 배치)도 같은 구조를 물려받았으나, 이번 검사는 발동 조건이
`has_design_tokens`라 생략 분기와의 겹침이 훨씬 넓다.

**수정 방향.** 생략 문장을 «동결본이 없으면(정적 화면 한정 진행) **이 절단만** 생략하고
아래 두 점검은 그대로 수행한다»로 좁히거나, 생략 문장을 문단 맨 끝으로 옮긴다. 양 런타임
동일 수정.

---

### [MAJOR] «탈출구 대칭 가드»가 공전한다 — «토큰 전수 처분» 절 제목이 규범 어디에도 없다

**무엇이 어긋났나.** 검사기는 «절은 있는데 고정 헤더가 없으면 FINDING(판형 위반), 절 자체가
없으면 warn+exit 0»으로 갈리는데, 그 «절»의 판별이 heading 문자열
`토큰 전수 처분`에 걸려 있다. 그런데 플러그인 규범(architecture-web §8 · design-architect-web ·
Coordinator) 어디에도 설계자에게 그 제목으로 절을 만들라는 지시가 없다. 결과적으로 architect가
고정 헤더 없이 산문으로 쓰면 절 제목이 무엇이든 **거의 항상 «절도 없다» 가지로 빠져 warn+0**
이 된다 — D14가 약속한 대칭 가드가 실전에서 서지 않는다.

**근거.**

- `dddjango-web/scripts/check_token_disposition.py:47`
  `SECTION_RE = re.compile(r"^#{1,6}\s.*토큰\s*전수\s*처분", re.M)` ·
  `:268-272`가 그 매치로 FINDING/warn을 가른다.
- `grep -n "토큰 전수 처분" dddjango-web/skills/architecture-web/references/final.md
  dddjango-web/agents/design-architect-web.md dddjango-web/commands/dddjango-web.md`
  → **히트 0**. (`architecture-web/references/final.md:142`는 «크기 전수 연결»이라는
  다른 이름이고, architect md는 «§8의 기계가독 표 판형»이라고만 한다.)
- 그 문자열이 존재하는 곳은 픽스처뿐이다 —
  `dddjango-web/scripts/test/fixtures_token_disposition.sh:33` `echo "## 9. 토큰 전수 처분"`.
  즉 TD10 green은 픽스처가 스스로 만든 제목에 대한 green이다.
- 실행 확인(절도 헤더도 없는 레거시 산문 명세):
  ```
  [warn] 고정 헤더 «| 축 | 처분 | 토큰 |» 미검출 · 전수 처분 절도 없다 — 레거시 산문 판형(미검증)
  exit=0
  ```

**수정 방향.** architecture-web §8과 design-architect-web의 새 문장에 절 제목을 못박는다 —
«처분 표는 «토큰 전수 처분» 제목의 절에 둔다(검사기의 절 판별 앵커)». 양 런타임 + Codex
byte 미러(architecture-web final.md)까지.

---

### [MAJOR] «경미»의 지위가 Coordinator와 discipline-reviewer-web에서 정반대다

**무엇이 어긋났나.** 같은 사실(링 확장보다 패딩이 작다)에 대해 두 경로가 상반된 처분을 지시한다.

- Coordinator G2: «지위는 compare와 같은 **판단 자료(비차단)**다 — «확정»(여유 0)은 반송
  근거로, **«경미»(0<여유<확장)는 수락 가능한 이탈**로 구분해 제시한다.»
- discipline-reviewer-web: «패딩이 링 확장(spread + |offset|)보다 작으면 **blocker**다»
  — 여유 0과 «경미»를 가르지 않는다.

리뷰어 blocker는 Coordinator가 «게이트 거부와 동일하게 반송»으로 처리하는 급이므로, 「경미」
한 건이 있는 빌드는 배너에서는 «수락 가능», 감사에서는 «반송»이 된다.

**근거.** `dddjango-web/commands/dddjango-web.md:187`(Codex `…/SKILL.md:210`) ↔
`dddjango-web/agents/discipline-reviewer-web.md:62`(Codex
`skills/dddjango-web-discipline-reviewer-web/SKILL.md`). 검사기 쪽 등급 계산은
`check_clip_clearance.py:334` `grade = "확정" if have == 0 else "경미"`로 두 말이 같은 조건을
가리킴이 확정된다. 선례인 «고정 배치 무력화»(`discipline-reviewer-web.md:61`)에는 대응하는
기계 검사가 «경미 = 수락 가능»을 말하지 않아 이 충돌이 없었다.

**수정 방향.** 한쪽으로 정렬한다 — 리뷰어 문장에 «여유 0(확정)이면 blocker, 0<여유<확장은
발견으로 올리되 이탈 결정 유무를 본다»를 넣거나, Coordinator에서 «경미»도 반송 대상으로
올린다. 감사 범위(touched 파일)와 기계 범위(web/ 전체)가 다르다는 점도 한 구로 적어두면
좋다.

---

### [MAJOR] 빌드 스펙 D14 행이 표 판형을 깬다 — 4열 표에 12셀

**무엇이 어긋났나.** D14 셀 본문의 `` `| 축 | 처분 | 토큰 |` ``과 `` `spread+|offset|` ``의
파이프가 이스케이프되지 않아 마크다운 표가 그 자리에서 쪼개진다. 나머지 전 행은 4열인데
D14만 10셀(양끝 포함 12조각)이라, GFM 렌더에서 4열 뒤의 내용이 잘려 나간다 — 즉 **결정
대장에 적힌 D14 본문의 대부분이 표로 안 보인다**.

**근거.**

```
$ awk 'NR>=28 && NR<=45 {n=gsub(/\|/,"|"); printf "%d cols=%d\n", NR, n-1}' \
    workspace/design/2026-08-23-web-presentation-layer-spec.md
28 cols=4  (헤더)   …   42 cols=4 (D13)   43 cols=10 (D14)   44 cols=4   45 cols=4

셀 분해: [' D14 ', ' 절단 충실도 … ', ' **결정 (사용자 · …)** ',
 ' **수리 A 토큰 처분 집행**: … ', ' 축 ', ' 처분 ', ' 토큰 ',
 '`(절은 있는데 헤더가 없으면 …', 'offset', '`(blur 제외 — …']
```

**수정 방향.** D14 행 안의 파이프를 `\|`로 이스케이프한다 —
`` `\| 축 \| 처분 \| 토큰 \|` `` · `` `spread+\|offset\|` ``. (같은 문자열을 담은
`ontology-adoption-map.html`은 HTML `<span class="mono">`이라 무해하고, architecture-web
final.md·agents md는 표 밖 산문이라 무해하다 — 실제 확인함.)

---

### [MAJOR] `docs/master.html`에 이번 작업과 무관한 오타 `}2`가 섞여 들어갔다

**무엇이 어긋났나.** CSS 규칙 끝에 문자 `2`가 붙어 다음 규칙의 셀렉터가 `2 .side-foot a`가
된다 — CSS 파서가 그 qualified rule을 통째로 버리므로 `.side-foot a { color: var(--ink-3) }`
가 사라진다. 이번 수리와 아무 관계 없는 파일의 유일한 변경이며 오타로 보인다.

**근거.**

```
$ git diff -- docs/master.html
-  .side-foot code { font-family: var(--mono); font-size: 10px; }
+  .side-foot code { font-family: var(--mono); font-size: 10px; }2
```

`docs/master.html:78-79`. `make verify`는 `docs/`를 보지 않으므로
(`grep -rn master.html workspace/tools/*.py Makefile` → 히트 0) 기계가 잡지 못한다.

**수정 방향.** 문자 `2`를 지워 원상 복구한다. 커밋 전에 `git diff -- docs/`를 한 번 더 눈으로
확인한다.

---

### [MAJOR] 생산측 규범 누락 — `implementation-ui` §7에 링 여유 표기가 없다

**무엇이 어긋났나.** 이번 배치는 감사·집행 경로(코디네이터 2곳 + 규율 리뷰어)만 세우고,
coder-web이 실제로 코드를 쓸 때 보는 표기 정본에는 규칙을 넣지 않았다. 선례인 «고정 배치
무력화»는 `discipline-reviewer-web.md:61`이 «implementation-ui §7 배치 거동 판형»을 인용하고
그 §7에 실제 생산 규칙이 있다(`implementation-ui/references/final.md:212-214` — sticky 중간
조상 overflow 금칙·`overflow-x: clip`·사슬 밖 말줄임 예외). 새 링 항목은 인용할 §가 없다 —
`grep -n "box-shadow\|포커스\|focus" dddjango-web/skills/implementation-ui/references/final.md`
는 `:203` 상태 규칙 한 줄뿐이고 클리핑과의 관계는 없다. 계획서가 pr-1 B2에서 «생산자
프롬프트에 판형을 안 실으면 검사가 영구 미발동»이라고 논증한 바로 그 대칭을, 수리 B에서는
적용하지 않았다.

**근거.** `workspace/plan/2026-09-15-web-clip-fidelity-plan.md:165-173`의 T3 표에
`implementation-ui`가 없다. `workspace/design/2026-09-15-web-clip-fidelity.md`에도
`implementation-ui`·`coder-web` 언급이 0건(`grep -n` 히트 없음) — 의식적 제외가 아니라
검토되지 않은 축이다.

**수정 방향.** `implementation-ui/references/final.md` §7 배치 거동 절(212~214행 이웃)에
한 불릿 — «바깥 링(`:focus-visible` 등의 바깥 `box-shadow`)을 지는 요소는 가장 가까운
`overflow ≠ visible` 조상의 패딩으로 `spread + |offset|`만큼의 여유를 확보한다. 한 축이
`visible`이 아니면 다른 축도 `auto`로 계산되므로 `overflow-y: auto`만 준 컨테이너도 가로로
자른다». 이 파일은 verify-web의 `cmp -s` byte 미러 대상이므로 Codex 쪽을 같이 갱신해야
한다(`codex-dddjango-web/skills/implementation-ui/references/final.md`). 그리고
`discipline-reviewer-web.md:62`가 그 §를 인용하게 한다.

---

### [MINOR] 절단 여유 검사의 «exit 1» 문구가 선례보다 축약됐다

**무엇이 어긋났나.** 같은 배너 안의 compare·백스톱·신규 토큰 점검은 모두
«**exit 1은 백스톱과 동일하게 미실행 취급이다**(통과로 간주 금지 — stderr 원인을 배너
사유로)»인데, 절단 여유만 «**exit 1은 미실행 취급**이다.»로 끝난다 — «통과로 간주 금지»와
«stderr 원인을 배너 사유로»가 빠졌다.

**근거.** `dddjango-web/commands/dddjango-web.md:187` 안에서 세 문구를 나란히 비교.
Codex 미러도 동일.

**수정 방향.** 선례 문구를 그대로 복사한다. 양 런타임.

---

### [MINOR] 트리비얼 패스트트랙 ③에는 새 검사의 지위·종료코드 처리 지시가 없다

**무엇이 어긋났나.** 공통 절차 ③에 명령만 추가됐고, 발견이 나왔을 때 «확정/경미»를 어떻게
처리하는지(반송인지 보고인지)·exit 1을 어떻게 볼지가 없다. ④는 «조건별 검증 결과 보고»뿐이다.
트리비얼은 G2도 감사도 없는 레인이라 판단 지시가 여기 말고 갈 곳이 없다.

**근거.** `dddjango-web/commands/dddjango-web.md:221`(Codex `…/SKILL.md:244`).

**수정 방향.** ③ 괄호 안에 한 구 — «발견은 판단 자료로 ④에 보고하고 «확정»은 수정 전
사용자 확인 · exit 1은 미실행 취급».

---

### [MINOR] CSS가 아직 없는 `web/`에서 exit 1 — 미실행 사유가 배너에 상시로 뜬다

**무엇이 어긋났나.** 검사기는 CSS 규칙이 하나도 없으면 «읽기 실패»로 보고 exit 1을 낸다.
첫 슬라이스처럼 템플릿만 있고 CSS가 아직 없는 G2에서 배너에 «미실행 + 사유»가 뜬다 —
통과 위장은 아니지만(지위상 안전) 소음이고, «발견 0»과 구분이 필요하다.

**근거.**

```
$ python3 …/check_clip_clearance.py ./no-such-web
[clip-clearance] web 루트가 디렉터리가 아니다: no-such-web   exit=1
$ python3 …/check_clip_clearance.py ./emptyweb     # 빈 디렉터리
[clip-clearance] CSS 규칙이 없다: emptyweb          exit=1
```

**수정 방향.** 규범 쪽만 손대도 된다 — «CSS 0·web 부재는 미실행 사유로 1줄 적고 넘어간다»를
G2 문장에 붙인다. (검사기에서 CSS 0을 exit 0 + 인벤토리로 강등하는 편이 깨끗하지만 픽스처·
byte 미러 동반이다.)

---

### [MINOR] 무관한 `workspace/eval/field-report-4/…` 수정이 같은 작업 트리에 섞여 있다

**무엇이 어긋났나.** `2026-09-10-spring-dream-overhaul-lanes.md`에 F4-21(dddjango pre-gate
`--approved-merge-file` 현장 보고)이 7줄 추가돼 있다 — 이번 절단 충실도 수리와 무관한
내용이라 그대로 커밋하면 릴리즈 커밋에 다른 트랙의 기록이 섞인다.

**근거.** `git diff -- workspace/eval/field-report-4/2026-09-10-spring-dream-overhaul-lanes.md`
— 추가 7줄 전부 B4 레인/`registry_gate.py` 이야기.

**수정 방향.** 별도 커밋으로 분리하거나, 의도된 동반 기록이면 커밋 메시지에 그 사실을 적는다.

---

## 발견이 아닌 것 (확인한 것)

- **scripts byte 미러 green**: `diff -rq --exclude=__pycache__ dddjango-web/scripts
  codex-dddjango-web/skills/dddjango-web/scripts` → 출력 없음(byte 동일). 신규 4파일
  (`check_clip_clearance.py`·`check_token_disposition.py`·`test/fixtures_*.sh`) 각각 `cmp -s`
  OK. `run_fixtures.sh`가 글롭으로 자동 수집해 14파일 실행, `fixtures_clip_clearance:
  PASS=15 FAIL=0` · `fixtures_token_disposition: PASS=17 FAIL=0`.
- **references byte 미러 green**: `architecture-web/references/final.md`의 `cmp -s`가
  verify-web에서 통과(에러 출력 없음). `dddjango-web`은 온톨로지 코퍼스 밖이라
  `corpus_mirror_sync`·`ontology/LEDGER.tsv` 대상이 아니다(`grep -c dddjango-web
  ontology/LEDGER.tsv` → 0). `workspace/reference/` 아래에도 web 소스 미러가 없다.
- **에이전트 3종 의미 미러 동일**: 세 파일의 추가 문단을 Claude/Codex 양쪽에서 뽑아 diff —
  전부 동일.
- **경로 변수 정상**: 신규 3개 명령줄이 Claude `${CLAUDE_PLUGIN_ROOT}`, Codex `${SKILL_DIR}`.
  `<타깃 프로젝트 루트>/web`은 저장소 관례와 일치한다(`scripts/src/common.py:318,399`
  `root / 'web'` · `extract_dc.py:32` `web/static/images`).
- **CLI 계약 일치**: `check_token_disposition.py:244-254`·`check_clip_clearance.py:256-260`의
  인자 판형이 커맨드 문면과 정확히 같다. 배너 어휘(«확정»·«경미»·«인벤토리»·«조인 실패»·
  «발견 N건»)도 검사기 출력과 일치(`check_clip_clearance.py:318,334,342,349`).
- **«반송 근거» vs «판단 자료» 지위**: G1 토큰 점검의 «FINDING은 architect 반송 근거다»는
  `check_motion_spec --spec-only` 판형과 같고, G2 절단 여유의 «판단 자료(비차단)»는
  `compare_render_audit` 판형과 같다. 발동 플래그 `has_design_tokens`는 실재한다
  (`commands/dddjango-web.md:65` build-state 스키마).
- **`docs/DEVELOPMENT.md` 파일 지도 정상**: `├──`/`└──` 사용과 연결선(`│` vs 공백)이 맞고,
  설명 계속 줄의 열(28)이 기존 항목과 같다. 신규 두 항목이 dddjango-web 블록의 마지막이라
  `└──`가 `check_clip_clearance.py`에 붙은 것도 맞다.
- **조감도 HTML 유효**: `workspace/design/ontology-adoption-map.html`을 `html.parser`로
  전수 파싱 — 미닫힘 0 · 짝 오류 0. 신규 타임라인 행은 `<tr><td>×3`로 표 판형 준수.
- **`REQUEST_GUIDE.md` 무변경이 맞다**: 사람용 가이드는 게이트·배너 항목이나 검사기 이름을
  열거하지 않는다(`grep -n "실측 대조\|모션 처분\|배너\|G1\|G2" dddjango-web/REQUEST_GUIDE.md`
  → 히트 0). 양 런타임 byte 미러도 verify-web에서 green.
- **`architecture-web/SKILL.md` 요약 무변경이 맞다**: §8 요약 불릿에 모션 전수 처분도 없다
  (렌더 실측만 있다) — 이번 누락은 선례와 일관된다.
- **플러그인 매니페스트 무관**: `dddjango-web/.claude-plugin/plugin.json` ·
  `codex-dddjango-web/.codex-plugin/plugin.json` 둘 다 파일 목록을 열거하지 않아 신규 스크립트
  등재가 필요 없다.
- **다른 verify 타깃 무영향**: `make verify` 6타깃 중 verify-web만 RED. `spec_lint.py`는
  dddjango의 트리 스펙만 본다(`SPEC_REL = workspace/design/2026-08-08-tree-revision-spec.md`).
