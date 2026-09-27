# 로드맵 6b 계획 §7 — 적용 한정 어구 · 긍정 술어 · 부정형 전수 분류 (2026-09-27)

> 근거: 계획 `plan-v2.md` §7 · §3-12 · §5(상수) · 설계 `design-v5.md` §9 · §5-3 · 진단 `diagnosis.md` 2-2 · dddjango 선례 `dddjango/commands/dddjango.md:239`.
> 행 번호는 HEAD `c9fcadff` blob 실측이다. 분석하는 동안 병행 구현 작업이 작업 트리의 Coordinator·에이전트 4·러너를 고치기 시작했다. 그래서 전 스캔(§0-2~§0-6)을 `git archive c9fcadff` 사본에서 다시 돌렸고, 같은 결과(59 · 145 · 150 · 33 · 51 · 43)를 확인했다. 작업 트리의 새 문면(끝 절 · 단위 점검 모드 절 등)은 이 분류 밖이다. 읽기·분석만 했고 이 파일 말고는 쓰지 않았다.

**결론 요약**

- 적용 한정 어휘 줄 161개를 T 16 · T\* 21 · N 124 로 갈랐다(§1). 진단 2-2 의 9어휘 줄 수(touched 6 · 신규 단위 7 · 새 파일 6 · 레거시 18 · 브라운필드 12 · legacy 12 · 기존 코드 12 · 이번 작업 3 · added 3 · 합집합 59줄)는 그대로 재현됐다.
- **닫힌 목록은 32개 어구**다(§2). 목록은 51문장을 잡는다. 외부 동작 보존 문장 79개 가운데 잡는 것은 0개다. 1개가 걸리는데, `계약 소비` 낱말 때문에 걸린 리뷰어 관찰 범위 문장이고 ⑵ 대상이다. 32개 모두 Codex 미러의 같은 문장에 있다.
- ⑵ 조항의 실재 위치를 확인했다(§3). web 리뷰어 문면에는 «diff 한정» 조항이 없다. 설계가 이름 붙이지 않은 `design-review-web.md:17`(구현 코드를 보지 않는다)도 ⑵ 몫이다.
- 긍정 술어는 렌즈 문서에서 33문장에 걸린다(유효 30 · 무효 3). 유효 30 가운데 거짓 허용은 8개다. cleancode 의 `(쓸|둘|할) 수 있다` 서술 6개는 적용 문서 목록에서 빼서 풀고, «처음에는 길고 복잡해도 좋다» 는 어구로 막는다. 남는 하나는 제한형 «…만 허용» 이다. 목록 밖 참 허용은 6묶음이다. 목록 확장 5개와 «만 » 무효 규칙 1개를 권한다(§4-6).
- `(쓸|둘|할) 수 있다` 는 렌즈 문서 가운데 **discipline-cleancode 2개를 뺀 9개 문서**에 적용한다(§5). cleancode 의 이 술어 적중은 모두 서술·메타·조건절이고 참 허용이 0이다.
- «리팩터링 대상 = 백스톱 위반» 류 사본을 전수 grep 했다(§6). houserules 두 곳과 Coordinator `:128` 은 이미 입구로 보낸다. 그런데 **에이전트 문면 5곳**이 슬라이스 0 을 `C` ⓐ 로만 읽는다(`coder-web.md:33` · `design-architect-web.md:31`·`:55` · `design-review-web.md:50` · `discipline-reviewer-web.md:36`). 설계 §9 의 «고칠 것 없음» 은 houserules 에만 맞다. 규범 원문 안에 1문장을 둬서 푼다(§7 F1).

---

## §0. 실행한 명령과 적중 수

### 0-1. 대상 문면 18 파일

`dddjango-web/commands/dddjango-web.md` · `dddjango-web/agents/{coder-web,design-architect-web,design-review-web,discipline-reviewer-web}.md` · `dddjango-web/skills/{architecture-web,discipline-cleancode,discipline-web-houserules,implementation-javascript,implementation-ui}/SKILL.md` · `dddjango-web/skills/architecture-web/references/final.md` · `dddjango-web/skills/discipline-cleancode/references/final.md` · `dddjango-web/skills/discipline-web-houserules/references/{final,undecidable-web}.md` · `dddjango-web/skills/implementation-javascript/references/final.md` · `dddjango-web/skills/implementation-ui/references/{final,design-acquisition,design-evidence}.md`

### 0-2. 진단 9어휘 (진단 2-2 재현)

```sh
for w in 'touched' '신규 단위' '새 파일' '레거시' '브라운필드' 'legacy' '기존 코드' '이번 작업' 'added'; do
  git grep -n -F -e "$w" -- dddjango-web/commands/dddjango-web.md 'dddjango-web/agents/*.md' \
    'dddjango-web/skills/*/SKILL.md' 'dddjango-web/skills/*/references/*.md' | wc -l; done
# 합집합
git grep -n -F -e touched -e '신규 단위' -e '새 파일' -e 레거시 -e 브라운필드 -e legacy -e '기존 코드' -e '이번 작업' -e added -- <위 pathspec> | wc -l
```

| 어휘 | touched | 신규 단위 | 새 파일 | 레거시 | 브라운필드 | legacy | 기존 코드 | 이번 작업 | added | **합집합** |
|---|---|---|---|---|---|---|---|---|---|---|
| 줄 | 6 | 7 | 6 | 18 | 12 | 12 | 12 | 3 | 3 | **59** |

### 0-3. 확장 어휘 (결합형 넓히기)

같은 18 파일에 줄 단위 정규식 45개를 돌렸다(python `re.search`). 진단 9개에 더한 것과 줄 수는 다음과 같다.

`brownfield`1 · `이번 diff`0 · `새로 들어`0 · `새로 만(드|든)`4 · `새 코드`3 · `범위 밖`7 · `손대`1 · `소급`3 · `면제`10 · `존중`0 · `grandfather`0 · `신규분`1 · `신규 파일`3 · `이번 요청`11 · `이번 산출`2 · `이번 실행`3 · `이번 범위`4 · `이번 슬라이스`4 · `이번 (변경|수정)`2 · `기존 파일`8 · `기존 위반`3 · `기존 단위`2 · `기존 (HTMX|htmx|legacy|설치|static/js)`5 · `기존 (관례|화면의 확립|확립)`1 · `확립`1 · `기존 프로젝트`2 · ``기존 `?web``9 · `그대로 소비`3 · `보지 않`5 · `diff`27 · `변경 (범위|영향)`8 · `새 줄|added 줄|추가.변경된`5 · `신규 (이슈|위반)`5 · `허용 규범`3 · `기존 (이슈|경고)`4 · `이미 있는`1 · ``기존 (구조|`web/` 구조)``2 · `신규 (화면|영역|static|core|HTMX|BC)`6 · `새 (화면|영역|단위)`7

→ 합집합 **145줄**이고, 0-2 에 없던 줄은 **86줄**이다. dddjango 목록 어휘 가운데 `이번 diff`·`새로 들어온`·`기존 … 존중`·`grandfather` 는 web 에서 0건이다.

### 0-4. 2차 훑기

`기존|신규|새로|새 |이번|그대로` 가 든 문장 가운데 0-3 에 걸리지 않은 것을 전부 읽었다. 적용 한정 몫이 있거나 경계에 걸린 **16줄**을 §1-C 에 더했다. 나머지는 절차·무관이다.

### 0-5. 문장 분할 · 술어 스캔

- 문장 분할은 dddjango `refactor_audit.py:256-300` 판형을 옮겨 썼다. 경계는 `.`+공백/줄끝 · 목록 머리 `^\s*([-*+]|\d+[.)])\s` · 표 칸 `|` · 원숫자 · 빈 줄 · 제목 줄이다. 코드 울타리는 건너뛰지 않는다(dddjango 와 같다).
- 술어 판정은 강조(`**`)와 백틱을 지우고 공백류를 한 칸으로 접은 문장에 건다.

```python
POS = [r'허용(한다|된다|이다|하되|하며|하고)', r'허용\)', r'허용:',
       r'(명시 )?예외(다|이다|로 둔다)', r'[아어여해]도 (된다|좋다)', r'(쓸|둘|할) 수 있다', r'무방']
NEG = r'허용하지 않|허용되지 않|예외가 아니|예외 없|예외를 두지 않'    # 같은 문장에 있으면 무효
BAD = ('라는', '라고', '는', '고', '면')                                  # 술어 바로 뒤면 무효
# 허용\)·허용: 바로 앞 두 글자가 '널 ' 이면 무효
```

- 렌즈 문서 13 파일(§4 머리)을 돌린 결과: 술어 적중 **33문장**(유효 30 · 무효 3) · 부정형 적중 4문장. 렌즈 밖 5 파일은 15문장이다.
- 목록 밖 허용 후보는 `허용|예외|면제|가능하다|정당|비대상|비적용|해당 없|필요 없|충분하|강제하지 않|요구하지 않|괜찮|재량|아도 |어도 |해도 |지 않아도|수 있` 가 들었지만 술어는 없는 문장이다. **150문장**을 전부 읽었다.

### 0-6. 어구 대조

- 어구는 dddjango `normalize`(강조·백틱·인용 줄머리 제거 + 공백 전부 제거)로 문장과 비교했다. 18 파일 문장 가운데 §2 의 32어구가 잡는 것은 **51문장**이다.
- 외부 동작 보존 문장은 `밖에서 보이는|외부에서 보이는|라우트 URL|fragment 라우트|API 계약|URL\+JSON|HTMX 응답|렌더 결과|렌더·동작|동작 불변|동작 보존|외부 관찰|바뀌지 않|바뀌어도|동작을 바꾸|외부 계약|계약 소비|응답 모양|swap 경계` 로 골랐다. **79문장**이 나왔고, 어구 적중은 1문장뿐이다(`design-review-web.md:59` «화면 분해·계약 소비 설계만 본다». `계약 소비` 낱말 때문에 걸렸고, 리뷰어 관찰 범위라 ⑵ 대상이다 — 동작 보존 규범이 아니다).
- Codex 미러: 32어구 각각을 `codex-dddjango-web/skills/**/*.md` 에서 찾았다. Claude 쪽과 같은 문장에 모두 있다. `touched` 는 Codex Coordinator `SKILL.md:263·271·272` · DR `:50` · coder `:52` 다.

---

## §1. 적용 한정 어휘 줄 분류

분류 기준: **T** = 적용 조건 한정(신규·touched·이번 작업·새로 만드는 것에만, 또는 기존·레거시·브라운필드 형태를 보존·면제·존중)이라 어구 후보다. **T\*** = 한 줄에 두 몫이 있어 풀리는 몫만 든다. **N** = 외부 계약·동작 보존 · 절차 · 무관이다. «어구» 칸은 §2 목록에서 그 줄을 잡는 어구다. «—» 는 싣지 않는 경우이고 사유를 적었다.

### 1-A. 진단 9어휘 59줄

| # | 파일:행 | 분류 | 사유 | 어구 |
|---|---|---|---|---|
| 1 | coder-web.md:31 | N | 골격 생성 플래그 — coder 입력 절차(«이번 작업이 신설하는 골격 단위») | (적중 무해: 이번 작업) |
| 2 | coder-web.md:50 | N | 새 파일을 명세 레이아웃대로 배치 — 집행 절차 | — |
| 3 | coder-web.md:52 | N | green 래칫(py_compile touched · check 베이스라인 신규분) — 동작 보존 기준선. 리팩토링도 같다(설계 §7-1 ①) | (적중 무해: touched) |
| 4 | design-architect-web.md:55 | T\* | 슬라이스 0 절 «ⓐ 키가 아닌 기존 코드의 이동 … 명세에 넣지 말고». 풀리는 몫: 리팩토링의 `M<n>` ⓐ 이동. 남는 몫: «동작 불변으로 정리할 수 없는 항목 … 반환»(동작 보존) | — 같은 문장에 동작 보존 몫이 있다 → §7 F1 규범 원문 1문장 |
| 5 | discipline-reviewer-web.md:49 | T | ⑵ 수정 모드 touched 한정 감사 | touched |
| 6 | dddjango-web.md:73 | N | `check_baseline` 브라운필드 기존 경고 불발화 — 동작 보존 기준선 | — |
| 7 | dddjango-web.md:136 | T\* | 풀리는 몫: «기존 `static/js/htmx…`는 브라운필드 설치로 그대로 소비·조용한 이동/업그레이드 하지 않음». 남는 몫: «새 이중 설치 금지»(core 중복은 모든 코드에 금지). 배선 미비 적용은 리팩토링에 없다(설계 §2-2) | 브라운필드 설치 · 그대로 소비 · 조용한 이동 |
| 8 | dddjango-web.md:146 | N | «brownfield·legacy는 면제가 아니라 아직 안 갚은 빚» — 반-면제 선언 · 빚 스캔 절차 | — |
| 9 | dddjango-web.md:147 | T\* | 러너 «브라운필드 허용 규범은 빚으로 내지 않는다». 풀리는 몫: WS5 · WP1(조건부 — `--refactor`). 남는 몫: motion.js 판형 · WP1·WP2 legacy 쌍(설계 §4-1) | 브라운필드 허용 |
| 10 | dddjango-web.md:150 | N | 개명·이동 묶음 절차(G2 diff 게이트에서 새 파일로 보이는 이유) | — |
| 11 | dddjango-web.md:151 | N | 빚 질문 대가 줄 «legacy 잔존» | — |
| 12 | dddjango-web.md:152 | N | 결정 출처 «기존 코드 정리를 미룬다는 뜻» | — |
| 13 | dddjango-web.md:164 | N | 시안 추출 «label 없는 legacy 후보» — 무관 | — |
| 14 | dddjango-web.md:191 | T\* | 풀리는 몫: «백스톱 위반이 아닌 기존 코드의 이동 → 반송·정지»(설계 §9 «`:191` 관계 1구»). 남는 몫: 앞 문장 «동작 불변 불가 → 정지»와 재상정 기록 | 백스톱 위반이 아닌 |
| 15 | dddjango-web.md:196 | N | 명세 판형 «레거시 산문» warn — 설계 명세 문서이지 코드가 아님 | — |
| 16 | dddjango-web.md:200 | N | 진입 준비 ④ check 베이스라인 — 동작 보존 기준선 | — |
| 17 | dddjango-web.md:218 | N | G2 배너 «legacy 잔존»·«레거시 산문 판형» — 절차·명세 판형 | — |
| 18 | dddjango-web.md:240 | T | ⑵ 수정 모드 «코드 규율 감사 = touched 파일 한정 경량 1회» | touched |
| 19 | dddjango-web.md:248 | N | 트리비얼 «touched 백스톱»(= diff 게이트) · 독립 영향 감사 입력 «구현 diff» — 절차(⑵ 인접 · §3) | (적중 무해: touched) |
| 20 | dddjango-web.md:249 | N | 트리비얼 시안 없음 절차 | (적중 무해: touched) |
| 21 | architecture-web/references/final.md:85 | N | 규범 «fragment 진입점은 소속 view — 새 파일 유형을 만들지 않는다»는 모든 코드에 적용된다. 맨 «새 파일» 을 목록에 싣지 않는 이유 | — |
| 22 | architecture-web/references/final.md:142 | N | 토큰 처분 표 «절이 없으면 레거시 산문으로 보아 warn» — 명세 판형 | — |
| 23 | discipline-cleancode/SKILL.md:3 | N | description 주제 이름 «레거시 코드» | — |
| 24 | discipline-cleancode/SKILL.md:29 | N | «레거시 코드는 Seam을 찾아 보호한 후 개선 … 동작 보존 안전망은 …» — 기법·동작 보존 | — |
| 25 | discipline-cleancode/SKILL.md:53 | N | 라우팅 표 | — |
| 26 | discipline-cleancode/references/final.md:39 | N | 목차 | — |
| 27 | discipline-cleancode/references/final.md:998 | T\* | OCP «새로운 요구사항이 생기면 … 기존 코드는 그대로 유지해야 한다». 풀리는 몫: 기능 추가 조건의 기존 코드 보존(리팩토링엔 새 요구가 없다). 남는 몫: 확장 설계 원칙 자체(위반 인용으로는 그대로 쓰인다) | 기존 코드는 그대로 유지 |
| 28 | discipline-cleancode/references/final.md:1097 | T\* | Factory Method «새로운 타입 추가 시 기존 코드를 수정하지 않는다» — 27과 같다 | 기존 코드를 수정하지 않 |
| 29 | discipline-cleancode/references/final.md:1267 | T\* | Strategy «새로운 전략 추가 시 기존 코드를 수정하지 않는다» — 27과 같다 | 기존 코드를 수정하지 않 |
| 30 | discipline-cleancode/references/final.md:2267 | N | §16 제목 | — |
| 31 | discipline-cleancode/references/final.md:2269 | N | 소절 제목 | — |
| 32 | discipline-cleancode/references/final.md:2271 | N | WELC 정의 «레거시 코드란 테스트가 없는 코드다» — 용어이지 적용 범위가 아님 | — |
| 33 | discipline-cleancode/references/final.md:2273 | N | 같은 정의 서술 | — |
| 34 | discipline-cleancode/references/final.md:2328 | T\* | Sprout «새 기능을 추가할 때, 기존 코드를 수정하지 않고 새 메서드로 …» — 기능 추가 조건 | 기존 코드를 수정하지 않 |
| 35 | discipline-cleancode/references/final.md:2331 | N | 예시 코드 주석 | — |
| 36 | discipline-cleancode/references/final.md:2387 | N | 특성화 probe — 동작 보존 기법 | — |
| 37–41 | discipline-cleancode/references/final.md:2392·2394·2396·2397·2398 | N | probe 예시 코드 | — |
| 42 | discipline-cleancode/references/final.md:2406 | N | Seam 서술 | — |
| 43 | discipline-cleancode/references/final.md:2551 | N | 요약표 | — |
| 44 | discipline-web-houserules/SKILL.md:15 | T\* | 풀리는 몫: «새로 만드는 코드는 표준을 따른다» · «새 코드의 적용 경계 … 폴더 구조는 신규 단위부터» · «빚의 교정이 아닌 이동을 기능 작업에 섞지 않는다». 남는 몫: «기존 코드의 위반은 면제가 아니라 빚» · 리팩토링 입구 안내(§6) | 새로 만드는 · 새 코드 · 신규 단위 · 기능 작업에 섞지 |
| 45 | discipline-web-houserules/SKILL.md:16 | T | «신규 단위는 표준 트리를 적용한다» — 리팩토링은 기존 단위에도(결정 18 · WS5 해제) | 신규 단위 |
| 46 | discipline-web-houserules/SKILL.md:24 | T | «새로 만드는 단위들 사이 …» · «레거시 단위 내부 추가는 §2의 경계 규칙» | 새로 만드는 · 레거시 단위 |
| 47 | discipline-web-houserules/SKILL.md:29 | T\* | 풀리는 몫: (가) 새로 만드는 파일의 표준 표기 · (나) 폴더 구조는 신규 단위부터 · 레거시 화면 내부에 표준 폴더를 강제하지 않음 · 브라운필드 허용 규범. 남는 몫: «그 밖의 기존 파일 위반은 빚 — 개명·이동은 두 경로로만»(리팩토링이 그 경로) | 새로 만드는 · added · 신규 단위 · 레거시 화면 · 그대로 소비 · 브라운필드 허용 |
| 48 | discipline-web-houserules/SKILL.md:49 | N | §4 백스톱 연동 — 두 게이트의 분업 서술(기존 위반은 빚 스캔이 본다) | (적중 무해: added · 이번 작업 · 신규 단위) |
| 49 | discipline-web-houserules/SKILL.md:62 | N | 라우팅 표 «브라운필드 관행 교정 사전» | — |
| 50 | discipline-web-houserules/references/final.md:17 | N | 목차 | — |
| 51 | discipline-web-houserules/references/final.md:95 | T | «신규 단위를 만들면 표준 폴더를 항상 생성» — WS5 해제 | 신규 단위 |
| 52 | discipline-web-houserules/references/final.md:166 | T\* | 풀리는 몫: «신규 HTMX core는 … 한 파일»의 «신규» 한정 · «기존 … 브라운필드 설치로만 소비» · «조용한 이동/업그레이드 금지». 남는 몫: «이중 설치 금지» · 누락 시 설치(배선 — 리팩토링엔 없다) | 신규 HTMX core · 브라운필드 설치 · 조용한 이동 |
| 53 | discipline-web-houserules/references/final.md:205 | N | 게이트 의미론 서술 + «기존 코드의 위반은 면제가 아니라 빚» | (적중 무해: touched · added · 신규 단위 · 이번 작업) |
| 54 | discipline-web-houserules/references/final.md:206 | T\* | 빚 모드 «브라운필드 허용 규범 … 은 빚으로 내지 않는다» — 9와 같다. 문면 갱신은 계획 §8 houserules §7 몫 | 브라운필드 허용 |
| 55 | discipline-web-houserules/references/final.md:207 | N | `--all` 용도 «레거시 프로젝트에서 발견 폭주가 정상» | — |
| 56 | discipline-web-houserules/references/final.md:215 | N | §8 제목 | — |
| 57 | discipline-web-houserules/references/final.md:217 | T\* | 풀리는 몫: «새 코드의 적용 경계 … 신규 단위부터» · «기능 작업이 기존 파일을 이 사전대로 옮기거나 개명하지는 않는다». 남는 몫: «기존 코드에 남은 관행은 면제가 아니라 빚 … 리팩토링 입구로»(§6) | 새 코드 · 신규 단위 · 기능 작업이 기존 파일 |
| 58 | implementation-ui/references/design-evidence.md:32 | N | «legacy Claude Design pointer» — 무관 | — |
| 59 | implementation-ui/references/final.md:127 | T\* | 풀리는 몫: «신규 HTMX core …» 한정 · «기존 … 브라운필드 설치로만 소비» · «조용한 이동/업그레이드». 남는 몫: «중복 설치·CDN 실행 태그 금지» · motion.js 판형 유지 | 신규 HTMX core · 브라운필드 설치 · 조용한 이동 |

### 1-B. 확장 어휘 86줄 (0-3 에서 새로 걸린 줄)

**T · T\* (12줄)**

| 파일:행 | 분류 | 사유 | 어구 |
|---|---|---|---|
| coder-web.md:33 | T\* | 슬라이스 0 입력 «G0에서 «지금 정리»로 결정된 기존 위반(빚)의 교정» — `C` ⓐ 한정. 리팩토링은 `M<n>` ⓐ 포함(§6) | — 에이전트 입력 서술이라 인용 근거가 아니다 → §7 F1 |
| design-architect-web.md:31 | T\* | 같은 사본(«기존 위반(빚) 키 목록») | — §7 F1 |
| design-architect-web.md:34 | T\* | 사전 조사 ② «기존 화면의 확립된 관례 — 배치·명명 결정의 근거로 쓴다». 풀리는 몫: 확립 관례를 근거로 삼는 것(리팩토링은 표준이 근거). 남는 몫: 사전 조사 의무 | 확립된 관례 |
| design-review-web.md:17 | T\* | 풀리는 몫: ⑵ «구현 코드를 보지 않는다». 남는 몫: «타 리뷰 노트» 독립성 | 구현 코드를 보지 않 |
| design-review-web.md:39 | T | G1 점검 2 «명세가 **새로 만들겠다는** component·토큰» — 신설분 한정. 단위 점검은 기존 중복 component 도 본다 | 명세가 새로 만들겠다는 |
| design-review-web.md:59 | T | ⑵ «구현 표기 … 구현 영역이다 — 보지 않는다» + «화면 분해·계약 소비 설계만 본다» | 구현 영역이다 · 설계만 본다 |
| discipline-reviewer-web.md:36 | T\* | Phase 1 경량 «G0 ⓐ 키 밖의 기존 파일 이동 = «승인 목록 밖 기존 파일 이동»». 리팩토링은 `M<n>` ⓐ 이동도 승인이다. 같은 문장에 «동작 불변 정리인가»(보존)가 있다 | — §7 F1 |
| dddjango-web.md:148 | T\* | «이번 요청의 스캔 단위»(끝 절 리팩토링 판이 바꾼다 — 설계 §3-4) · «미룰 수 없음» 해로움 = «**이번 산출물**의 동작·안전» — 리팩토링엔 기능 산출물이 없다 | — 절차 문장 → §7 F7 |
| discipline-web-houserules/references/final.md:104 | T | 골격 절 «신규 core는 `static/htmx/…`, 기존 … 기존 설치로만 소비한다» | 신규 core |
| discipline-web-houserules/references/undecidable-web.md:63 | T\* | 끝 문장 «신규 core 참조는 …, 기존 js 경로는 설치된 파일을 그대로 소비한다». 같은 줄 첫 문장 «…화면 어휘 금지 위반이 아니다»는 참 허용이다(§4-3) | 신규 core · 그대로 소비 |
| discipline-web-houserules/SKILL.md:13 | T | «새 코드를 배치할 때 위에서부터» — 결정 순서의 적용 조건 | 새 코드 |
| discipline-web-houserules/SKILL.md:18 | T | «신규 static 골격은 css/·js/·htmx/·images/» — 기존 static 골격 미비도 WS5(결정 18) | 신규 static 골격 |

**N (74줄)**

| 파일:행 | 사유 |
|---|---|
| coder-web.md:3 · :12 · :66 | 역할 서술 · 반송 규율(«이번 슬라이스 밖 수정 필요 → 보고») — 절차 |
| coder-web.md:16 · design-architect-web.md:14 · design-review-web.md:13 · discipline-reviewer-web.md:19 | 사용자 실행 경계(«범위 밖 임시 경로») — 절차 |
| coder-web.md:30 | 입력 «기존 web/ 트리 요약 — 중복 생성 방지» |
| coder-web.md:32 | check 베이스라인 — 동작 보존 기준선 |
| coder-web.md:42 · :46 | 입장 검사 면제 불가 · 소급 해소 금지 — 절차 |
| coder-web.md:55 | 기존 타입/린트 검사의 신규 위반 — 동작 보존 green 판정 |
| coder-web.md:74 | 메커니즘 대체 금지(«승인 범위 밖 JS 우회») |
| design-architect-web.md:32 | 반송 재호출 산출 diff — 절차 |
| design-architect-web.md:51 | 시각 연결표 «이번 범위에서 쓰는 실제 부품» — 시안 재현(리팩토링엔 시안 없음) |
| design-review-web.md:44 | 시안 이탈 행 «실제 변경 범위» — 시안 대조 |
| discipline-reviewer-web.md:15 | 백스톱 분업(«러너가 보는 것을 재검하지 마라» · «백스톱 통과가 의미 점검을 면제하지 않는다») — C·M 분업은 리팩토링에서도 유지(R1 몫) |
| discipline-reviewer-web.md:27 | Phase 2 감사 입력 «현재 완료 슬라이스(=감사 범위)» — 모드 입력 정의. 단위 점검 모드는 조각 목록이 범위다(⑵ 인접 · §3) |
| discipline-reviewer-web.md:32 | 독립성 «다른 감수 노트는 보지 않고» — 유지 |
| dddjango-web.md:24 · :26 · :27 · :87 · :262 | 기존 화면 재개 입구 · 세션 재개 — 절차 |
| dddjango-web.md:67 · :82 | build-state 필드(diff 게이트 기준 · g2_visual) |
| dddjango-web.md:124 · :125 · :126 · :246 · :251 | 모드 판별 기준 · 트리비얼 정의·공통 절차 |
| dddjango-web.md:128 | 정리 요청 → 리팩토링 입구 안내(§6) |
| dddjango-web.md:130 · :144 · :179 | 배치축 신호 · 폴더 선택 · G0 배너 폴더·자리 질문 |
| dddjango-web.md:138 · :158 · :172 | 시안 대조 범위 · 시안 입력 · 자체 설계 |
| dddjango-web.md:155 · :209 | ⓐ 동결·소급 기입 금지 · 입장 위반 소급 금지 — 절차 |
| dddjango-web.md:187 · :208 | architect·coder 입력(기존 web/ 구조 조사 · 트리 요약) |
| dddjango-web.md:193 | 스캔 단위 확인 — 끝 절 리팩토링 판이 바꾼다(설계 §3-4) |
| dddjango-web.md:211 · :212 · :213 · :217 · :222 · :224 · :229 | 슬라이스 0 참조 완전성 · 반송 · 구현 화면 검증 · 잔존 판정 · Phase 3 — 절차 |
| dddjango-web.md:235 · :237 · :239 · :241 · :242 | 수정 모드 절차(:241 «새 줄은 diff 게이트, 기존 위반은 빚 조사» 분업 포함) — 끝 절이 리팩토링 흐름을 따로 정한다 |
| dddjango-web.md:259 · :261 | 엣지 — 범위 밖 발주 · 설계 반송 재진입 |
| discipline-cleancode/references/final.md:325 | 숫자 부칙 «…는 면제» — 규칙 내용의 예외다. 같은 문단이라 오탐 경로로 풀린다 |
| discipline-cleancode/references/final.md:994 | «이 플러그인 범위 밖» — 소관 경계 |
| discipline-web-houserules/references/final.md:107 | «영구 test/ 없음 — 생성 앱의 web/에 … 만들지 않는다 … 기존 프로젝트의 적용 가능한 검사는 함께 실행한다» — 생성 금지 · 기존 검사 실행(⑤ 근거). «생성 앱»은 싣지 않는다(§2-3) |
| discipline-web-houserules/references/final.md:196 · :209 | 러너 명령 판형 · green 판정(WP6 «추가/변경된» — 러너 게이트 서술) |
| discipline-web-houserules/references/undecidable-web.md:41 · :43 | 영역 귀속 «새 영역 신설» 선택지 |
| implementation-javascript/SKILL.md:26 | «기존 HTMX 표현만으로 충족되는지» — HTMX 기능 표현 · 무관 |
| implementation-javascript/references/final.md:85 · :111 | «동일 타이밍으로 보지 않음» · «해제되었다고 보지 않는다» — 무관(맨 «보지 않» 을 싣지 않는 이유) |
| implementation-ui/references/design-acquisition.md:36 · design-evidence.md:5 · :16 · :37 · :143 | 시안 수집·증거 — 무관 |
| implementation-ui/references/final.md:41 · :45 | §2 시안 재현 «현재 변경 범위» — 렌즈 밖 절(설계 §4-2 제외) |

### 1-C. 2차 훑기 추가 16줄

| 파일:행 | 분류 | 사유 | 어구 |
|---|---|---|---|
| discipline-web-houserules/references/final.md:99 | T | 골격 표 «`web/` 컨테이너 최초» — 적용 시점 한정(WS5 컨테이너 키) | 컨테이너 최초 |
| discipline-web-houserules/references/final.md:100 · :101 · :102 | T | 골격 표 «신규 `<screen_area>/`» · «신규 `<view>/`» · «신규 `client/<bc>/`» | 같은 세 어구 |
| implementation-javascript/references/final.md:19 | T | «새 웹 트리가 적용된 환경의 경로는 …» · «기존 트리가 다르면 이 문서만으로 파일을 옮기지 않는다» | 새 웹 트리가 적용된 · 기존 트리가 다르면 |
| discipline-cleancode/references/final.md:2422 | T | «처음에는 길고 복잡해도 좋다» — 초안 작성 조건. 이 한정이 없으면 기존 긴 함수를 빼는 거짓 허용이 된다(§4-4) | 처음에는 길고 복잡해도 |
| discipline-web-houserules/references/final.md:168 · implementation-ui/references/final.md:153 | N | «classic은 `defer`, 기존 module 방식은 허용» — **호스트 로드 정책** 조건이다. 신·구 코드가 모두 호스트 방식을 따르므로 신·구 한정이 아니다(`implementation-javascript/references/final.md:27` «기존 module 정책이면 그 방식을 따른다»가 정책 단위임을 확인) | — |
| implementation-javascript/references/final.md:27 | N | 같은 호스트 정책 조건 | — |
| implementation-ui/references/final.md:90 | N | «대상 프로젝트의 기존 포매터 관례를 따른다(없으면 PEP 8)» — 호스트 설정 · 신·구 공통 | — |
| implementation-javascript/references/final.md:136 | N | «기존 motion 러너의 판형·`data-motion` 계약을 바꾸지 않는다» — 플러그인 판형 불변(모든 코드) | — |
| implementation-javascript/references/final.md:156 | N | «검사 실패를 피하려 기존 금지 규칙이나 테스트 기대값을 변경하지 않는다» — 동작 보존 | — |
| discipline-web-houserules/SKILL.md:21 | N | «영구 test/ 없음 — 생성 앱의 테스트 폴더·파일을 만들지 않는다» — 생성 금지(§2-3) | — |
| dddjango-web.md:188 | N | G1 파견 «코드·타 노트는 주지 않는다 — 편향 방지» — Coordinator 파견 규칙이다. 끝 절 R2 파견이 바꾼다(⑵ 인접 · §3) | — |
| architecture-web/references/final.md:141 · discipline-web-houserules/references/final.md:87 | N | «새 부품을 만들기 전에 기존 component/를 대조 — 두 번째 구현은 만드는 순간 빚» · «기존 화면 폴더에 section·state를 얹지 않는다» — 모든 코드에 적용되는 규범(기존 중복·증축도 빚) | — |

### 1-D. 계수

| 묶음 | T | T\* | N | 합 |
|---|---|---|---|---|
| 1-A 진단 9어휘 | 5 | 14 | 40 | 59 |
| 1-B 확장 | 5 | 7 | 74 | 86 |
| 1-C 2차 | 6 | 0 | 10 | 16 |
| **합** | **16** | **21** | **124** | **161** |

T·T\* 37줄 가운데 어구 없이 두는 5줄(coder-web:33 · design-architect-web:31·:55 · discipline-reviewer-web:36 · Coordinator:148)은 인용 근거 문서가 아니거나 같은 문장에 동작 보존 몫이 있는 줄이다. 이 줄들은 §7 F1·F7 로 푼다.

---

## §2. 닫힌 목록 (32어구)

### 2-1. 끝 절 문면에 그대로 싣는 한 줄

적용 한정 어구(닫힌 목록): «touched» · «added» · «이번 작업» · «새 코드» · «새로 만드는» · «신규 단위» · «신규 `<screen_area>/`» · «신규 `<view>/`» · «신규 `client/<bc>/`» · «컨테이너 최초» · «신규 static 골격» · «레거시 단위» · «레거시 화면» · «브라운필드 허용» · «브라운필드 설치» · «그대로 소비» · «조용한 이동» · «신규 core» · «신규 HTMX core» · «기능 작업에 섞지» · «기능 작업이 기존 파일» · «새 웹 트리가 적용된» · «기존 트리가 다르면» · «기존 코드는 그대로 유지» · «기존 코드를 수정하지 않» · «처음에는 길고 복잡해도» · «백스톱 위반이 아닌» · «확립된 관례» · «명세가 새로 만들겠다는» · «구현 코드를 보지 않» · «구현 영역이다» · «설계만 본다».

### 2-2. 도구 상수 (`refactor_audit.py`)

```python
SCOPE_PHRASES: "tuple[str, ...]" = (
    "touched", "added", "이번 작업", "새 코드", "새로 만드는", "신규 단위",
    "신규 `<screen_area>/`", "신규 `<view>/`", "신규 `client/<bc>/`", "컨테이너 최초", "신규 static 골격",
    "레거시 단위", "레거시 화면", "브라운필드 허용", "브라운필드 설치", "그대로 소비", "조용한 이동",
    "신규 core", "신규 HTMX core", "기능 작업에 섞지", "기능 작업이 기존 파일", "새 웹 트리가 적용된",
    "기존 트리가 다르면", "기존 코드는 그대로 유지", "기존 코드를 수정하지 않", "처음에는 길고 복잡해도",
    "백스톱 위반이 아닌", "확립된 관례", "명세가 새로 만들겠다는", "구현 코드를 보지 않", "구현 영역이다",
    "설계만 본다",
)
```

비교는 dddjango `phrase_hit` 판형이다(`normalize(p) in 문장 정규화본`). 백틱·공백은 비교에서 사라지므로 `신규 \`<view>/\`` 는 `신규<view>/` 로 맞는다. self-test 는 끝 절 문면에서 `«적용 한정 어구»` 뒤의 `«…»` 를 뽑아 상수와 집합 대조한다(dddjango `refactor_audit.py:1449` 판형). Codex Coordinator 끝 절도 같은 32개를 같은 글자로 싣는다.

### 2-3. 어구별 포착 문장 (51문장)

| 어구 | 포착 문장 파일:행 |
|---|---|
| touched | coder-web.md:52 · discipline-reviewer-web.md:49 · dddjango-web.md:240(2문장) · :248 · :249 · houserules final.md:205 |
| added | houserules final.md:205 · SKILL.md:29 · :49 |
| 이번 작업 | coder-web.md:31 · houserules final.md:205 · SKILL.md:49 |
| 새 코드 | houserules final.md:217 · SKILL.md:13 · :15 |
| 새로 만드는 | houserules SKILL.md:15 · :24 · :29 |
| 신규 단위 | houserules final.md:95 · :205 · :217 · SKILL.md:15 · :16 · :29 · :49 |
| 신규 `<screen_area>/` · 신규 `<view>/` · 신규 `client/<bc>/` | houserules final.md:100 · :101 · :102 |
| 컨테이너 최초 | houserules final.md:99 |
| 신규 static 골격 | houserules SKILL.md:18 |
| 레거시 단위 · 레거시 화면 | houserules SKILL.md:24 · :29 |
| 브라운필드 허용 | dddjango-web.md:147 · houserules final.md:206 · SKILL.md:29 |
| 브라운필드 설치 | dddjango-web.md:136 · houserules final.md:166 · implementation-ui final.md:127 |
| 그대로 소비 | dddjango-web.md:136 · undecidable-web.md:63 · houserules SKILL.md:29 |
| 조용한 이동 | dddjango-web.md:136 · houserules final.md:166 · implementation-ui final.md:127 |
| 신규 core · 신규 HTMX core | houserules final.md:104 · undecidable-web.md:63 · houserules final.md:166 · implementation-ui final.md:127 |
| 기능 작업에 섞지 · 기능 작업이 기존 파일 | houserules SKILL.md:15 · final.md:217 |
| 새 웹 트리가 적용된 · 기존 트리가 다르면 | implementation-javascript final.md:19(2문장) |
| 기존 코드는 그대로 유지 · 기존 코드를 수정하지 않 | cleancode final.md:998 · :1097 · :1267 · :2328 |
| 처음에는 길고 복잡해도 | cleancode final.md:2422 |
| 백스톱 위반이 아닌 | dddjango-web.md:191 |
| 확립된 관례 | design-architect-web.md:34 |
| 명세가 새로 만들겠다는 | design-review-web.md:39 |
| 구현 코드를 보지 않 · 구현 영역이다 · 설계만 본다 | design-review-web.md:17 · :59(2문장) |

- 잡힌 51문장 가운데 **유효 긍정 술어가 든 문장은 1개**다(cleancode:2422 «해도 좋다» — 막아야 할 거짓 허용). 나머지는 제외 근거가 될 수 없는 문장이다. 이 문장들을 막는 효과는 오탐 요건 인용과 «사용자 판단» 반대 방향 인용을 막는 데 있다.
- 잡혀도 무해한 N 문장(절차 — 인용 근거가 아님): coder-web.md:31 · :52 · dddjango-web.md:248 · :249 · houserules final.md:205 · SKILL.md:49.

### 2-4. 외부 동작 보존 문장 대조

- 동작 보존 문장 79개(0-6) 가운데 어구 적중은 0이다. `design-review-web.md:59` «설계만 본다» 1건은 `계약 소비` 낱말 때문에 걸렸고, ⑵ 대상인 리뷰어 관찰 범위 문장이다.
- 대표 보존 문장이 잡히지 않음을 확인했다: `coder-web.md:57`(렌더·동작·페이지·fragment 라우트 URL · 정적 자산 경로 예외) · `architecture-web/references/final.md:18`·`:121`(URL+JSON · client 격리) · `design-review-web.md:46`(응답 모양) · `dddjango-web.md:128`(밖에서 보이는 동작 유지) · `:191` 앞 문장(동작 불변 불가 정지) · `implementation-javascript/references/final.md:156`.

### 2-5. 싣지 않은 후보와 사유

| 후보 | 사유 |
|---|---|
| 맨 «기존» · «신규» · «새» · «레거시» · «새 파일» · «보지 않» · «diff» | 맨 낱말 금지다. «새 파일»은 `architecture-web final.md:85` 규범(«새 파일 유형을 만들지 않는다»)을, «보지 않»은 JS `:85`·`:111` 규범을, «diff»는 절차 27줄을 잡는다 |
| «ⓐ 키가 아닌 기존 코드» (architect:55) · «승인 목록 밖 기존 파일» (DR:36) | 같은 문장에 동작 보존 몫(«동작 불변으로 정리할 수 없는 항목 …» · «슬라이스 0 절이 동작 불변 정리인가»)이 있어 보존 문장을 잡는다. §7 F1 규범 원문 1문장으로 푼다(Coordinator:191 은 «백스톱 위반이 아닌»이 잡는다) |
| «생성 앱» · «만들지 않» · «신설 금지» | 생성 금지 조항은 신·구 한정이 아니다. 목록에 넣으면 «native로 충분하면 JS를 만들지 않는다» 같은 정당한 반대 방향 근거까지 막는다(§7 F8) |
| «기존 module 방식» · «기존 … 정책이면» · «기존 포매터 관례» | 호스트 정책 조건이다(신·구 코드 공통 · 1-C) |
| «이번 요청의 스캔 단위» · «이번 산출물» (Coordinator:148) | Coordinator 절차 문장이고 끝 절 단조성이 바꾼다(§7 F7) |
| «새로 만든» · «기존 설치로만» | 잡는 문장이 모두 다른 어구에도 걸려 단독 포착이 0이다(«added»·«신규 core» 와 중복) |
| dddjango 목록의 «이번 diff»·«새로 들어온»·«기존 코드 존중»·«grandfather» 등 | web 문면 0건이다(0-3) |

---

## §3. ⑵ 조항 파일:행

| ⑵ 항목 (설계 §9) | Claude | Codex | 실재 문장 | 판단 |
|---|---|---|---|---|
| 리뷰어의 **diff** 한정 관찰 | **없음** | 없음 | web 리뷰어 2종 문면의 `diff` 는 DR `:15` 러너 서술(«git diff 게이트»)뿐이다. 관찰 범위와 가장 가까운 것: DR `:27` «슬라이스 계획과 현재 완료 슬라이스(=감사 범위)» · `:49` 첫 문장 «너는 받은 범위를 감사한다» · Coordinator `:248` 트리비얼 독립 영향 감사 입력 «구현 diff» | dddjango 판을 옮긴 낱말이다. web 에서 그 자리는 «감사 범위(현재 완료 슬라이스) 한정»이다 |
| 리뷰어의 **touched** 한정 관찰 = **수정 모드 touched 한정 감사** | `agents/discipline-reviewer-web.md:49` 끝 문장 «수정 모드에서는 touched 범위 한정 경량 1회다» · 호출 규칙 `commands/dddjango-web.md:240` «코드 규율 감사 = touched 파일 한정 경량 1회» | `skills/dddjango-web-discipline-reviewer-web/SKILL.md:50` · `skills/dddjango-web/SKILL.md:263` | — | 설계의 두 항목은 같은 조항이다(에이전트 문면과 Coordinator 호출 규칙) |
| **구현 표기 열람 금지**(design-review-web) | `agents/design-review-web.md:59` (`## 경계` 둘째 항목 — «구현 표기(…)는 구현 영역이다 — 보지 않는다.» + «너는 화면 분해·계약 소비 설계만 본다.») | `skills/dddjango-web-design-review-web/SKILL.md:62` | — | 두 문장 모두 ⑵ 대상이다 |
| (설계 ⑵ 에 이름 없음) **구현 코드 열람 금지** | `agents/design-review-web.md:17` (`## 입력` 셋째 문단 끝 «너는 그것만 본다 — 타 리뷰 노트나 구현 코드를 보지 않는다(편향 방지).») | `skills/dddjango-web-design-review-web/SKILL.md:20` | — | ⑵ 몫이다(«타 리뷰 노트» 독립성은 남는다). 계획 §6 의 1구 자리는 `:59` 뿐이라 빠져 있다 → §7 F2 |
| (참고 · Coordinator 파견 규칙) | `commands/dddjango-web.md:188` «코드·타 노트는 주지 않는다 — 편향 방지» | `skills/dddjango-web/SKILL.md:211` | — | 리뷰어 조항이 아니다. 끝 절 R2 파견 입력이 단조성으로 바꾼다 |

- ⑵ 문장 web 판 제안: «리뷰어의 감사 범위(현재 완료 슬라이스)·touched 한정 관찰, 구현 코드·구현 표기 열람 금지와 «설계만 본다»(design-review-web), 수정 모드 touched 한정 감사 조항은 단위 점검(점검과 잔존 확인)과 그 판정에서만 적용하지 않는다. 슬라이스 0 의 리뷰와 감사는 이 조항을 그대로 따른다.» 목록 어구 «touched»·«구현 코드를 보지 않»·«구현 영역이다»·«설계만 본다»가 이 조항 문장을 모두 잡는다.

---

## §4. 긍정 술어 · 부정형 전수

렌즈 문서 13 파일은 설계 §4-2 렌즈 2 의 점검 문서다: `architecture-web/SKILL.md`·`references/final.md` · `implementation-ui/SKILL.md`·`references/final.md` · `discipline-web-houserules/references/undecidable-web.md` · `discipline-cleancode/SKILL.md`·`references/final.md` · `discipline-web-houserules/SKILL.md`·`references/final.md` · `implementation-javascript/SKILL.md`·`references/final.md` · `agents/design-review-web.md` · `agents/discipline-reviewer-web.md`. implementation-ui 의 `design-acquisition.md`·`design-evidence.md` 는 §1·§2(제외 절) 부속이라 렌즈 밖이다(4-5).

### 4-1. 적중 표 (33문장)

| # | 파일:행 | 문장(요지) | 술어 | 판정 | 참/거짓 허용 |
|---|---|---|---|---|---|
| 1 | architecture-web/SKILL.md:27 | 패키지 타입 직노출 금지(예외: 검증 실패 재렌더용 Django Form 1종 허용) | `허용)` | 유효 | 참 — 괄호 예외라 제외 ⑤ 단서 판형 |
| 2 | architecture-web/references/final.md:72 | 단 예외로 Django Form 1종을 허용한다 | `허용한다` | 유효 | 참 |
| 3 | implementation-ui/SKILL.md:31 | 승인된 UI 동작 계약의 기능 JS**만** 허용하며 native로 충분하면 파일 없음 | `허용하며` | 유효 | **거짓(제한형)** — 4-4 |
| 4 | implementation-ui/references/final.md:35 | 같은 선언을 옮기는 것은 허용한다 | `허용한다` | 유효 | 참 |
| 5 | implementation-ui/references/final.md:47 | 다른 토큰 이름·등가 CSS 구성도 같은 외형이면 허용한다 | `허용한다` | 유효 | 참 |
| 6 | implementation-ui/references/final.md:153 | classic은 defer, 기존 module 방식은 허용하고 … | `허용하고` | 유효 | 참(호스트 정책) |
| 7 | implementation-ui/references/final.md:168 | 단일 값은 … quoted data-* 속성으로 충분할 수 있다 | `할 수 있다` | 유효 | 참(약한 선택 허용) |
| 8 | implementation-ui/references/final.md:204 | custom property 정의 금지 — …(중간값 리터럴은 허용) | `허용)` | 유효 | 참 |
| 9 | implementation-ui/references/final.md:215 | 시각적으로 숨긴 입력(sr-only)은 … 예외다 | `예외다` | 유효 | 참 |
| 10 | undecidable-web.md:23 | static_only도 승인된 로컬 UI 동작을 허용한다 | `허용한다` | 유효 | 참(모드 서술 — 리팩토링과 무관) |
| 11 | undecidable-web.md:25 | 정적 화면은 view+페이지 템플릿만으로 허용한다 | `허용한다` | 유효 | 참 |
| 12 | discipline-cleancode/SKILL.md:57 | 장절은 `### N.M` 소절 헤더로 더 좁게 grep할 수 있다 | `할 수 있다` | 유효 | **거짓(읽기 안내 메타)** — §5 로 풀림 |
| 13 | discipline-cleancode/references/final.md:152 | 좁은 범위의 지역 변수는 짧아도 된다 | `아도 된다` | 유효 | 참 |
| 14 | discipline-cleancode/references/final.md:295 | `# 허용: 짧은 루프에서 관례적 이름`(코드 블록 주석) | `허용:` | 유효 | 참(예시 라벨) |
| 15 | discipline-cleancode/references/final.md:333 | … 추출할 수 있다**면**, 그 함수는 여러 작업을 하고 있다 | `할 수 있다` | **무효** — 무효 접미 «면» | (조건절 — 위반 판별 기준) |
| 16 | discipline-cleancode/references/final.md:391 | 같은 문장 | `할 수 있다` | **무효** — «면» | (조건절) |
| 17 | discipline-cleancode/references/final.md:625 | … 파일로도 커다란 시스템을 구축할 수 있다 | `할 수 있다` | 유효 | **거짓(서술)** — §5 로 풀림 |
| 18 | discipline-cleancode/references/final.md:1057 | `# 어떤 클래스는 둘 중 하나만 필요할 수 있다`(코드 블록 주석) | `할 수 있다` | 유효 | **거짓(서술)** — §5 |
| 19 | discipline-cleancode/references/final.md:1144 | … 제품군 전체를 일관되게 교체할 수 있다 | `할 수 있다` | 유효 | **거짓(효과 서술)** — §5 |
| 20 | discipline-cleancode/references/final.md:1355 | … 세부 동작을 유연하게 변경할 수 있다 | `할 수 있다` | 유효 | **거짓(효과 서술)** — §5 |
| 21 | discipline-cleancode/references/final.md:1506 | 내부에서는 직접 접근을 허용하되, 외부에서는 메서드를 통해 접근하라 | `허용하되` | 유효 | 참 |
| 22 | discipline-cleancode/references/final.md:2221 | 거의 모든 논리적 선택을 테이블 조회로 대체할 수 있다 | `할 수 있다` | 유효 | **거짓(서술)** — §5 |
| 23 | discipline-cleancode/references/final.md:2422 | 1. 처음에는 길고 복잡해도 좋다 | `해도 좋다` | 유효 | **거짓(초안 조건)** — 어구 «처음에는 길고 복잡해도»가 막는다 |
| 24 | discipline-web-houserules/references/final.md:105 | 두 마커 파일은 «직속 파일 금지»의 명시 예외다 | `명시 예외다` | 유효 | 참(`금지` 가 든 명시 예외 판형) |
| 25 | discipline-web-houserules/references/final.md:114 | 예외: 고정 이름 파일 … 은 주 클래스 규칙의 예외다 | `예외다` | 유효 | 참 |
| 26 | discipline-web-houserules/references/final.md:130 | OrderListViewModel(모듈 수준 조립 함수 허용) | `허용)` | 유효 | 참 |
| 27 | discipline-web-houserules/references/final.md:139 | custom property 정의 금지(… keyframes 중간값 리터럴**만** 허용) | `허용)` | 유효 | 참(표 칸 안 괄호 예외) |
| 28 | discipline-web-houserules/references/final.md:168 | classic은 defer, 기존 module 방식은 허용하고 … | `허용하고` | 유효 | 참(호스트 정책) |
| 29 | implementation-javascript/references/final.md:27 | 기존 classic 정책이면 defer와 파일 내부 범위를 쓸 수 있다 | `쓸 수 있다` | 유효 | 참(호스트 정책) |
| 30 | implementation-javascript/references/final.md:117 | 세대 번호 또는 현재 작업 객체의 동일성으로 표현할 수 있다 | `할 수 있다` | 유효 | 참(수단 선택) |
| 31 | implementation-javascript/references/final.md:120 | 새 작업·사라진 UI의 결과 표시는 무효화할 수 있다 | `할 수 있다` | 유효 | 참 |
| 32 | implementation-javascript/references/final.md:126 | 단일 값은 … data 속성으로 충분할 수 있다 | `할 수 있다` | 유효 | 참(약한 선택 허용) |
| 33 | design-review-web.md:46 | 응답 모양(중첩·페이징·**널 허용**)을 … | `허용)` | **무효** — 앞이 `널 ` | (nullable 표기 — 설계 예상대로) |

계: 유효 30 · 무효 3. 유효 30 가운데 **거짓 허용은 8개**(#3 · #12 · #17–#20 · #22 · #23)이고 참 허용은 22개다.

### 4-2. 부정형 적중

렌즈 문서에서 부정형은 4문장에 걸린다: cleancode `:1562` «예외가 아니라 «답»이다» · cleancode `:1606` «광범위 catch를 허용하지 않으며» · undecidable `:21` «승격 신호이지 예외가 아니다» · implementation-ui final `:53` «쓰기가 허용되지 않으면». 네 문장 모두 긍정 술어가 없어 판정 결과는 바뀌지 않는다. `예외 없`·`예외를 두지 않` 은 web 에서 0건이다(dddjango 대칭으로 둔다). 렌즈 밖에서는 Coordinator `:11`·`:208` 이 걸린다(술어 없음).

### 4-3. 목록 밖 참 허용 (놓치는 것)

| 파일:행 | 문장 | 풀리는 길 |
|---|---|---|
| undecidable-web.md:63 | 범용 scripts block 자체와 공통 기능의 외부 파일명은 화면 어휘 금지 **위반이 아니다** | 규칙(`:57` §6 «화면 어휘 금지»)과 문단이 달라 오탐이 막힌다 → **과잉 차단** |
| discipline-cleancode/references/final.md:1604–1606 | VM 안의 작은 구체 catch와 준비된 표시 상태의 직접 반환은 이 분리 원칙의 **위반이 아니며** … | 문단이 다르다 → **과잉 차단** |
| implementation-ui/references/final.md:216 | 말줄임·카드 이미지 클립처럼 사슬 밖 사용은 그대로 **정당하다** — 금칙은 … 중간 조상에만 | 금칙(`:212`)과 목록 항목이 달라 문단이 다르다 → **과잉 차단** |
| implementation-ui/references/final.md:212 | 스크롤포트 자신의 scroll은 **정당하다** | 금칙과 같은 문단이라 오탐 경로로 풀린다 |
| implementation-javascript/SKILL.md:45 · references/final.md:32 · :90 | 감수 때 리스너 위임·인스턴스 초기화 중 하나를 정답 형태로 **강제하지 않는다** · 특정 마크업을 … 강제하지 않는다 · 단순 기능에 init/destroy 틀을 강제하지 않는다 | `:90` 은 같은 문단(오탐). SKILL:45 · final:32 는 **과잉 차단** |
| implementation-javascript/SKILL.md:28 | 단순 동작은 한 번 설치한 이벤트 위임으로 **충분하다** | 다른 문서 규칙을 인용하면 **과잉 차단** |
| discipline-cleancode/SKILL.md:20 · references/final.md:315–320 | **허용 목록**(사람 대상 서술·정의부·외부 프로토콜 소유 문자열 등)은 리터럴 유지 · «리터럴 허용 목록 (승격하지 않는다):» + 항목 | 항목이 규칙(1·2번)과 다른 목록 항목이다 → **과잉 차단** |
| discipline-cleancode/references/final.md:325 | …수식의 본질적 구성 숫자는 **면제** | 같은 문단이라 오탐 경로 |
| discipline-web-houserules/references/final.md:80 · :116 · :74/:101/:102 | 마커 파일은 «명시 예외 — §3» · 정적 화면은 view+템플릿만으로 **허용(** · form/·exception.py «골격 완비 비대상/골격 대상 아님» | 같은 문단·같은 표 행이라 오탐 경로(`:105` 는 술어로 잡힘) |
| implementation-ui/SKILL.md:27 · references/final.md:71 | 예외로 Django Form 1종(… 허용( | 같은 문단이라 오탐 경로. architecture-web #1·#2 가 제외 근거로 남는다 |
| implementation-ui/SKILL.md:30 · references/final.md:120 | **허용 htmx 속성**은 … | 허용 목록 자체가 규칙이라 뺄 필요가 없다 |
| architecture-web/references/final.md:145 | …형상·마크업 불서술 원칙의 **명시 예외(** 모션 좌표 한정 | 명세 작성 규범이다(코드 점검과 무관) |

과잉 차단은 설계 §5-3 에 따라 fail-closed 로 «채택»에 떨어진다. 사용자 ⓑ 나 «사용자 판단»으로 풀리므로 새지는 않는다. 확장 권고는 4-6 이다.

### 4-4. 오적중 (거짓 허용)과 처리

| 문장 | 처리 |
|---|---|
| cleancode SKILL:57 · final:625 · :1057 · :1144 · :1355 · :2221 (`(쓸\|둘\|할) 수 있다` 서술·메타 6개) | §5 적용 문서 목록에서 cleancode 를 뺀다 → 적중 0 |
| cleancode final:2422 «처음에는 길고 복잡해도 좋다» | 적용 한정 어구 «처음에는 길고 복잡해도»(초안 조건)로 막는다. 이 처리가 없으면 긴 함수 M 항목을 §17 인용으로 뺄 수 있다(술어 유효 · 부정형 없음 · 위반과 다른 문장 → 제외 통과) |
| implementation-ui SKILL:31 «승인된 UI 동작 계약의 기능 JS**만** 허용하며» | 제한형이다. 이 문장을 근거로 «업무 판정 JS» 같은 M 항목을 뺄 수 있다(위반 인용이 다른 문서면 ⑤ 가 걸리지 않는다). 리팩토링 대상 기존 코드에는 «승인된 UI 동작 계약»이 없으므로 근거가 서지 않는다 → 4-6 «만 » 무효 규칙 |

### 4-5. 렌즈 밖 문서 (보조 · 15문장)

Coordinator `:49`(해도 된다) · `:125`(허용이다) · `:143`(허용)) · `:152`(«ⓑ는 앞 둘**만** 쓸 수 있다») · `:155`(적어도 된다) · `:168`(축소할 수 있다) · `:174`(«설명할 수 있다는» — 무효 «는») · `:179`·`:191`·`:200`(예외다) · coder-web `:45`(할 수 있다) · `:57`(«정적 자산 경로는 … 바뀌어도 된다» — 규범 끝 문장이 가리키는 동작 보존 예외) · design-architect-web `:22`(허용하며) · design-acquisition `:100`(어도 된다) · `:113–114`(허용하며). 모두 절차·명세 작성 규범이라 코드 점검 제외 근거로 쓸 일이 없다. v3 가 잘못 잡던 `:176` «…현행 G0의 예외 승인으로 취급하지 않는다»는 v5 정규식으로는 0건이다(확인).

### 4-6. 확장 권고 (도구 상수 · 극성 표본)

| 추가 | 적중(18 파일) | 참/거짓 | 극성 표본 |
|---|---|---|---|
| 긍정 `위반이 아니(다\|며)` (`아니라` 는 안 잡힌다) | undecidable:63 · cleancode:1604–1606 | 2/2 참 | 유효 «…금지 위반이 아니다» · 무 적중 «위반이 아니라 빚이다» |
| 긍정 `정당하다` | implementation-ui final:212 · :216 | 2/2 참 | 유효 «사슬 밖 사용은 그대로 정당하다» · 무 적중 «정당화하지 않는다» |
| 긍정 `강제하지 않는다` | JS SKILL:45 · final:32 · :90 · coder-web:54 · houserules SKILL:29 | 5/5 참(SKILL:29 는 어구 «신규 단위»·«레거시 화면»이 막는다) | 유효 «정답 형태로 강제하지 않는다» · 무효 «강제하지 않는다고» |
| 긍정 `충분하다` | JS SKILL:28 | 1/1 참 | 무 적중 «충분하면»(조건 — 정규식 밖) |
| 긍정 `허용 목록` | cleancode SKILL:20 · final:315 | 2/2 참 | — |
| 무효 규칙: 술어 바로 앞이 `만 ` | implementation-ui SKILL:31 · houserules final:139 · Coordinator:152 | SKILL:31 은 거짓 허용 제거. final:139 는 참 허용을 잃지만 금지와 같은 표 칸이라 오탐 경로로 풀린다(implementation-ui final:204 «중간값 리터럴은 허용)»이 제외 근거로 남는다) | 무효 «기능 JS만 허용하며» · 유효 «중간값 리터럴은 허용)» |

12문장이 새로 걸리고 모두 참 허용이다. 거짓 허용은 0이다. 제외 ④·⑤·적용 한정 어구·부정형 관문은 그대로다.

---

## §5. `(쓸|둘|할) 수 있다` 적용 문서 목록

**적용** — 렌즈 문서 가운데 cleancode 를 뺀 9개와 그 Codex 대응이다.

| Claude | Codex |
|---|---|
| `skills/architecture-web/SKILL.md` · `skills/architecture-web/references/final.md` | `codex-dddjango-web/skills/architecture-web/SKILL.md` · `…/references/final.md` |
| `skills/implementation-ui/SKILL.md` · `skills/implementation-ui/references/final.md` | `codex-dddjango-web/skills/implementation-ui/SKILL.md` · `…/references/final.md` |
| `skills/implementation-javascript/SKILL.md` · `skills/implementation-javascript/references/final.md` | `codex-dddjango-web/skills/implementation-javascript/SKILL.md` · `…/references/final.md` |
| `skills/discipline-web-houserules/SKILL.md` · `…/references/final.md` · `…/references/undecidable-web.md` | `codex-dddjango-web/skills/discipline-web-houserules/…` 같은 3개 |
| `agents/design-review-web.md` · `agents/discipline-reviewer-web.md` | `codex-dddjango-web/skills/dddjango-web-design-review-web/SKILL.md` · `…/dddjango-web-discipline-reviewer-web/SKILL.md` |

**비적용** — `skills/discipline-cleancode/SKILL.md` · `skills/discipline-cleancode/references/final.md`(Codex 대응 포함). 렌즈 밖 문서(Coordinator · coder-web · design-architect-web · design-acquisition · design-evidence)도 비적용이다(절차 문장뿐 — 4-5).

- **cleancode 서술문 5개(`final.md:625·1057·1144·1355·2221`)는 넣지 않는다.** 규범 허용이 아니라 능력·효과 서술이다(`:1057` 은 코드 블록 주석). 같은 이유로 SKILL `:57`(«grep할 수 있다» — 읽기 안내 메타, 설계가 들지 않은 여섯째 적중)도 넣지 않는다. 조건절 `:333`·`:391` 은 어느 쪽이든 무효 접미 «면»으로 무효다.
- 빼서 잃는 것은 없다. cleancode 의 참 허용은 모두 다른 술어로 잡힌다(`:152` «짧아도 된다» · `:1506` «허용하되» · `:295` «허용:» — 이 술어들은 cleancode 에도 계속 적용된다). 빼는 방향은 제외 출구가 줄어드는 fail-closed 쪽이다.
- 적용 9개 문서의 현재 적중은 참 허용 5개다(implementation-ui final:168 · JS final:27 · :117 · :120 · :126).
- 상수 형태: 문서 키 집합 `CAN_DOCS`(위 9개 · 플랫폼 경로 사상은 §5 공통 사상표를 쓴다). 목록 밖 문서에서는 이 항만 끄고 나머지 술어는 그대로 건다.

---

## §6. «리팩터링 대상 = 백스톱 위반» 류 사본 grep

```sh
git grep -n -E -e '리팩터링|리팩토링|refactor' -- <0-1 의 18 파일>   # 43줄(Coordinator 19 · cleancode 18 · coder-web 2 · architect 1 · houserules 3)
git grep -n -F -e 'ⓐ 키' -e '기존 위반(빚)' -e '승인 목록 밖' -- <같은 pathspec>
```

| 사본 | 파일:행 | 판정 |
|---|---|---|
| 관행·의미 정리는 리팩토링 입구로 | houserules SKILL `:15` «검사기가 내지 않는 관행·의미 정리는 리팩토링 입구 `/dddjango-web:refactor`로» · final §8 `:217` «백스톱이 내지 않는 관행 교정은 리팩토링 입구(Claude `/dddjango-web:refactor` · Codex `$dddjango-web-refactor`)로» · Coordinator `:128` «정리 요청은 … 리팩토링 입구 `/dddjango-web:refactor <대상>`» + G0 배너 «의미 정리는 `/dddjango-web:refactor`» | **이미 입구로 보낸다 — 무변**(설계 §9·§10 5행 확인) |
| 러너 절 안의 «기존 위반 = 빚 스캔» | houserules SKILL `:49` · final `:205` · Coordinator `:146` | 백스톱 연동 절의 문맥 한정이다(검사기 빚만 말한다) — 무변 |
| **슬라이스 0 = `C` ⓐ(빚) 교정** | coder-web `:33` «G0에서 «지금 정리»로 결정된 기존 위반(빚)의 교정이다» · design-architect-web `:31` «기존 위반(빚) 키 목록» · `:55` «ⓐ 키마다 교정할 파일 계획 … ⓐ 키가 아닌 기존 코드의 이동 … 명세에 넣지 말고» · design-review-web `:50` «G0 ⓐ 키마다 파일 계획이 있는가» · discipline-reviewer-web `:36` «G0 ⓐ 키 밖의 기존 파일 … «승인 목록 밖 기존 파일 이동» — 발견» | **리팩토링 모드와 어긋난다.** 6a 의 `ⓐ 키:` 행은 `C<n>` 만 받고, 의미 항목은 `의미 ⓐ 키:` 다(설계 §6). 에이전트는 이 문면으로 `M<n>` ⓐ 의 이동·개명을 «승인 목록 밖»으로 읽는다 → DR 경량 발견 → Coordinator `:191` 정지. 설계 §9 의 «`:191` 관계 1구»는 Coordinator 끝 절에만 있어 에이전트에 닿지 않는다 → §7 F1 |
| Coordinator 쪽 같은 한정 | `:155` «ⓐ 항목은 … «슬라이스 0 = 리팩터링(동작 불변)»» · `:187` · `:191` · `:205` · `:211` | 끝 절 단조성이 바꾼다(계획 §3-1 · §3-12 · §3-15 · §3-16) — 무변. `:191` 은 목록 어구 «백스톱 위반이 아닌»도 막는다 |
| 보편 문장 | cleancode SKILL `:28` · final `:2500` 등 | 무관 |

---

## §7. 계획·설계에 되돌릴 발견

| # | 등급 | 발견 | 처리(도출 근거) |
|---|---|---|---|
| F1 | major | 에이전트 문면 5곳(§6)이 슬라이스 0 을 `C` ⓐ 로만 읽는다. 리팩토링 모드의 `M<n>` ⓐ 이동·개명이 DR 경량 점검(`:36`)에서 발견이 되고 architect(`:55`)가 명세에서 빼면 Coordinator `:191` 정지로 간다. 설계 §9 «고칠 것 없음»은 houserules 사본에만 맞다 | 파견되는 **적용 범위 규범 원문 안에** 1문장을 둔다: «리팩토링 모드의 슬라이스 0 ⓐ 목록은 `C<n>` ⓐ 와 `M<n>` ⓐ 이고 그 이동·개명은 승인 목록이다 — 파견 받는 문면의 «ⓐ 키»·«기존 위반(빚)»·«승인 목록»은 둘 다를 가리킨다». 설계 §9 «`:191` 관계 1구»를 규범 문단 안으로 옮기는 것이다. 계획 §6 «모두» 1행(«규범이 정한 몫과 때를 따른다»)이 받고, 계획 §3-15·§3-16 입력(`M<n>` ⓐ 목록 · 규범 원문)과 맞물린다. 5곳 개별 1구는 불요 |
| F2 | minor | ⑵ 의 «diff 한정» 은 web 리뷰어 문면에 없다. 대신 `design-review-web.md:17`(Codex `:20`) «구현 코드를 보지 않는다»가 ⑵ 몫인데 계획 §6 은 `:59` 에만 1구를 둔다 | ⑵ 문장을 §3 web 판으로 적는다. 계획 §6 design-review-web 1구 자리를 `:59` 와 `:17` 둘로 한다(`:17` 은 «타 리뷰 노트» 독립성을 남긴다) |
| F3 | minor | 목록 밖 참 허용 6묶음이 과잉 차단된다. 제한형 «…만 허용» 1건은 거짓 허용이다(§4-3·§4-4) | 긍정 술어 5개(`위반이 아니(다\|며)` · `정당하다` · `강제하지 않는다` · `충분하다` · `허용 목록`)와 무효 규칙 «술어 바로 앞 `만 `» 1개를 도구 상수와 극성 표본에 더한다(§4-6 — 새 적중 12 모두 참 · 거짓 0). 설계 §5-3 «목록 확장은 계획의 전수 분류가 본다»의 집행이다 |
| F4 | minor | dddjango `normalize` 는 공백을 전부 지운다. 그대로 술어 판정에 쓰면 `(명시 )?예외` · `[아어여해]도 (된다\|좋다)` · `(쓸\|둘\|할) 수 있다` · `널 ` 앞 조건이 모두 깨진다. 줄을 넘는 문장(cleancode `:1604–1606` «위반이⏎아니며»)도 있다 | 술어·부정형·무효 접미·`만 ` 규칙은 «강조·백틱 제거 + 공백류(줄바꿈 포함)를 한 칸으로 접은 문장»에 건다. 적용 한정 어구만 dddjango `normalize` 비교를 쓴다. 계획 §5 check-verdict 에 1구  · **구현 정정(09-27 리뷰 R m6)**: 처음 구현은 공백 없는 본문을 «같은 효과»로 보고 두었으나 사실이 아니었다 — 이 처분대로 `normalize_spaced` 문장에 건다(`impl-log.md` §2 10 · §3 m6) |
| F5 | minor | `(쓸\|둘\|할) 수 있다` 적용 문서 목록이 계획에 비어 있다(X4 m5) | §5 표 그대로 확정한다: cleancode 비적용. 설계가 든 서술문 5개 외에 SKILL `:57` 이 여섯째다 |
| F6 | minor | 어구 목록이 브라운필드 core 문면(«브라운필드 설치» 등)을 푸는데, 러너 `--refactor` 는 WP1·WP2 legacy 쌍(태그에 defer 없음)의 면제를 유지한다(설계 §4-1). 그 쌍을 겨누는 의미 항목은 «외부 동작» 기계 근거(§4-4 — urls·`{% url %}`·`HX-`·render)에 script 로드 태그가 없어 채택 → G0 ⓐ → Phase 1 동작 불변 불가 정지 → 재상정으로 두 번 묻는다 | 설계 §5-3 «과잉 차단의 처리»(fail-closed · 새지 않음)로 받아들인다. 현장은 core 가 canonical 이라 영향 0 이다(진단 4-2). 구현 리뷰 관찰 항목으로만 둔다 |
| F7 | minor | Coordinator `:148` «미룰 수 없음» 의 해로움이 «**이번 산출물**의 동작·안전»으로 정의돼 있다. 리팩토링엔 기능 산출물이 없다 | 끝 절(계획 §3-13 G0)에 «리팩토링 모드의 «해로움»은 대상 단위의 현재 동작·안전이다» 1구를 두고, «끝 절이 앞 절을 바꾸는 곳» 목록(§3-1)에 더한다 |
| F8 | note | 생성 금지 조항(«만들지 않는다» · «신설 금지»)을 «새로 만들 때만»으로 읽고 오탐으로 빼는 것은 기계 관문 밖이다. 오탐 출구는 요건 인용이 위반과 같은 문장이어도 받는다 | 목록에 싣지 않는다(정당한 반대 방향 근거를 막는다 — §2-5). 오탐 출구에 «같은 문장 red» 를 더하면 같은 문장의 요건절(«…분기·판정·필터하면»)이 막혀 과잉 차단이 된다 — 걷음. 규범 ⑴ 문면과 architect 판정 모드가 막는다(구현 리뷰 관찰) |
| F9 | note | dddjango 쪽에도 같은 OCP·Sprout 문장과 «처음에는 길고 복잡해도 좋다»가 있는데(`dddjango/skills/discipline-cleancode/references/final.md:1047·1149·1321·2408·2506`) dddjango 닫힌 목록 52개에 해당 어구가 없다 | 이 작업 범위 밖이다 — 보고만 한다 |
