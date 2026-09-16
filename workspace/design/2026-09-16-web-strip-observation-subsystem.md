# dddjango-web 1.1.20 — 실패한 브라우저 관찰 서브시스템 철거

**정본** · 2026-09-16 · hyun 지시 「깨끗하게 철거하고 진짜 잔재가 없는지 적대적 리뷰로 하고 반영해서 클린한 1.1.20까지 만들어」

## 진단 — 왜 철거인가

A8 관계인 화면(1.1.10 착수)에서 커스텀 드롭다운이 네이티브 `<select>`로 나오고 다이얼로그가 「다음」마다 깜빡이는 결함을 잡으려 했으나, **드롭다운을 시안대로 강제하는 검사기가 애초에 없었다**. 대신 1.1.13~1.1.19에 브라우저로 상호작용을 «관찰»하는 서브시스템(`observe_interactions.pw.js` 드라이버 + `evidence_debt` + `refreeze.py` 트랜잭션 재동결 + `ledger.py` 미검증 원장)이 얹혔고, 그 서브시스템이:

- 8시간 52분 무한 정지(드라이버가 상한을 항목 사이에서만 잰다)
- 루트 셀렉터 ↔ 크롭 규칙 모순으로 v2 관찰 조립 불가
- 정상 abort가 staging을 복사 없이 삭제
- 재동결이 관찰 재수집과 46군데 얽힘

즉 **9개 버전·4일이 이 서브시스템을 고치는 데 갔고 드롭다운 코드는 0줄**이었다.

### 결정적 관찰 — 관찰은 처음부터 불필요했다

시안(`관계인.dc.html`)이 드롭다운 정체를 **정적 HTML 속성으로 선언**한다:

```html
component-from-global-scope="ChunmongDesignSystem_9ad494.Select" label="관계" options="{{ relOptions }}"
```

`_ds_manifest.json`도 `Select`(`components/forms/Select.jsx`)·`Dropdown`을 커스텀 컴포넌트로 선언한다. **JS를 브라우저로 돌려 «관찰»할 이유가 없었다** — 「이 필드는 커스텀 Select다」가 평범한 속성이다. 자매 플러그인 **dddart**(같은 Claude Design HTML을 Flutter로 옮김)는 브라우저 관찰·부채·트랜잭션 재동결이 **하나도 없이**(설계쪽 스크립트 7개) 재동결과 시안 변경을 잘 처리한다. dddjango-web은 옮길 대상이 HTML이라는 이유로 «실물을 브라우저로 관찰»하는 길로 빠졌고 그게 부서졌다.

## 설계 — v1.1.12 기준선 리셋

상호작용 서브시스템은 1.1.13에 들어왔다. 그래서 그것이 얽힌 파일은 **v1.1.12(직전 릴리즈)의 정적 형태로 되돌리고**, 그 뒤 나온 정적 수리(절단 충실도 1.1.16·주석 오탐 1.1.18·포커스 링)만 보존한다. 검증이 명료해진다 — 「1.1.13~1.1.19 서브시스템이 하나도 안 남았나」.

## 실행 (전량 양쪽 미러)

**삭제(신규 파일):** `observe_interactions.pw.js`·`observe_interactions.mjs`·`interaction_audit.js` · `evidence_debt.py`·`evidence_debt_hook.py`·`hooks/hooks.json` · `refreeze.py` · `ledger.py` · 관련 test/fixtures 13 · `scripts/test/fixtures/interaction/` 고아 데이터 · `workspace/tools/web_hooks_contract.py`·`web_refreeze_contract.py`

**v1.1.12 리셋:** `check_design_evidence.py`(1510→정적) · `archive_design.py` · `backstop.py`(legacy_v1·재동결·원장 검사 제거) · 매칭 test 4 · reference 2(`design-acquisition.md`·`design-evidence.md`) · Codex SKILL 3 · **`commands/dddjango-web.md`**(재동결이 v1.1.12에선 「전량 폐기 후 재동결」이라 refreeze.py 없이 성립) — clip·토큰 처분 호출 3곳 재적용

**정적 손 수술:** `design-review-web.md`·`design-architect-web.md`·`discipline-reviewer-web.md`(조작 상태 증거·미검증 원장 구절만) · REQUEST_GUIDE 양쪽(증거 부채 bullet) · Codex discipline SKILL · DEVELOPMENT.md(파일트리·contract·verify-web-browser) · Makefile(verify-web-browser 타깃·contract 호출)

**보존(정적 · 살아남음):** freeze/extract 사슬 · `compare_render_audit`·`render_audit.js` · clip·focus·motion·token 검사 4 · 정적 v1 관찰(`source_observation`·reference_capture) · 재동결 **개념**(= 처음부터 다시 동결)

## 적대적 리뷰 결과

- 런타임 잔재 0 — 삭제 스크립트/산출물/플래그를 부르는 곳 0(유일 매치는 이 철거를 기록한 주석)
- 모든 프롬프트의 스크립트 호출이 실재 스크립트를 가리킴(dangling 0)
- `make verify-web` GREEN — 픽스처 12·Codex `diff -rq`·references cmp·REQUEST_GUIDE byte 전부 통과

## 철거 후 상태 · 다음(1.1.21)

파이프라인이 「정적 설계 증거 + 시각/절단/모션/토큰 검사」로 돌아갔다. **드롭다운은 아직 못 잡는다** — 1.1.20은 부서진 배관 철거다. 실제 강제는 1.1.21: `extract_dc`가 `component-from-global-scope` 선언을 screen-meta에 끄집어내고, 검사기가 **코드로** 「구현이 그 커스텀 컴포넌트를 썼나, 네이티브로 평탄화했나」를 대조해 이탈이면 red. 브라우저 0.
