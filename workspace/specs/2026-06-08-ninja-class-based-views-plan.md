# ninja 클래스 기반 뷰(컨트롤러) 도입 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** dddjango 플러그인이 생성하는 ninja API를 함수형 operation에서 ninja-extra 클래스 컨트롤러로 강제하도록 표준·에이전트·평가지·백스톱을 양 런타임(Claude/Codex) 미러로 변경한다.

**Architecture:** spec §8 단계적 집행. **Phase 0** = 변경이 유발하는 백스톱 거짓음성 회귀를 즉시 봉합(결정적·TDD). **Phase 1** = 표준 텍스트·에이전트 렌즈·평가지 기준을 클래스 전제로 개정. 2차 라이브·3차 신설 백스톱은 후속.

**Tech Stack:** Markdown 표준 텍스트(정본+Claude+Codex 미러), Python AST 백스톱 스크립트(`re`/`ast`), JSON plugin manifest. 검증 = `pytest`/직접 실행 픽스처 + `grep` + `cmp`(미러 byte-id) + `plugin validate`.

**정본 = spec:** `workspace/specs/2026-06-08-ninja-class-based-views-design.md`. 모든 task는 spec의 해당 절을 근거로 한다.

**미러 규약:** 각 표준 스킬 = 정본(`workspace/reference/<skill>/reference/final.md`) + Claude(`dddjango/skills/<skill>/references/final.md` + `SKILL.md`) + Codex(`codex-dddjango/skills/<skill>/references/final.md` + `SKILL.md`). 백스톱 = `dddjango/scripts/` + `codex-dddjango/skills/dddjango/scripts/`(byte-identical). 에이전트 = `dddjango/agents/<role>.md` + `codex-dddjango/skills/dddjango-<role>/SKILL.md`. **각 task는 미러 전체를 동시에 바꾸고 `cmp`/`grep`로 동기를 검증한다.**

**커밋 규약:** 프로젝트는 "요청 시에만 커밋". 각 task의 커밋 step은 **사용자 승인 후** 실행한다(서브에이전트는 커밋하지 말고 변경만; 메인이 일괄 커밋 판단). 브랜치 `eval/codex-determinism-n2`(비-기본).

---

## File Structure

**Phase 0 — 백스톱(결정적 패치)**
- `dddjango/scripts/check-response-schema-bypass.py` + Codex 미러 — `NINJA_IMPORT_RE` 확장
- `dddjango/scripts/check-openapi-error-declaration.py` + Codex 미러 — 동일
- `dddjango/scripts/check-error-centralization.py` + Codex 미러 — 동일
- `workspace/eval/tools/check-structure.py` — NJ-1 토큰 확장(단일본, 미러 없음)
- 검증 픽스처(throwaway, `/tmp`) — 커밋 안 함

**Phase 1 — 표준/에이전트/평가지**
- `implementation-django-ninja`(3+2) — 클래스 레시피·§6.2·§6.3·§2.1·§9.1
- `discipline-houserules`(3+2) — §4 `Controller`·파일명·트리/표·SKILL.md bullet·버전핀
- `implementation-test`(3+2) — §19 TestClient
- 에이전트 5종(양판) — architect·reviewer·review-api·tester·coder
- `workspace/eval/rubric/RUBRIC.md` + `EVAL-METHOD.md` — NJ-1 동결해제·어휘·앵커
- `dddjango/commands/dddjango.md` + `codex-dddjango/skills/dddjango/SKILL.md` — 게이트 설명문
- `dddjango/.claude-plugin/plugin.json` + `codex-dddjango/.codex-plugin/plugin.json` — 버전

---

## Phase 0 — 백스톱 회귀 봉합 (즉시·결정적)

### Task 0.1: 세 백스톱의 `NINJA_IMPORT_RE` 확장 (양판 6파일)

**근거:** spec §7 "1차 회귀 봉합 — 대상 3종". 현 정규식 `^\s*from\s+ninja(?:\.\w+)*\s+import\b`는 `from ninja_extra import`를 매치 못 해 클래스 컨트롤러 파일을 스캔조차 건너뜀(거짓음성 회귀, 실측 확인).

**Files:**
- Modify: `dddjango/scripts/check-response-schema-bypass.py` (`NINJA_IMPORT_RE = ...` 라인)
- Modify: `dddjango/scripts/check-openapi-error-declaration.py`
- Modify: `dddjango/scripts/check-error-centralization.py`
- Modify: `codex-dddjango/skills/dddjango/scripts/check-response-schema-bypass.py`
- Modify: `codex-dddjango/skills/dddjango/scripts/check-openapi-error-declaration.py`
- Modify: `codex-dddjango/skills/dddjango/scripts/check-error-centralization.py`

- [ ] **Step 1: 현재 정규식 라인 위치 확인**

Run: `grep -rn "NINJA_IMPORT_RE\s*=" dddjango/scripts/ codex-dddjango/skills/dddjango/scripts/`
Expected: 6개 매치(3종 × 양판), 모두 동일한 현행 정규식.

- [ ] **Step 2: 실패 픽스처로 회귀 재현**

throwaway 픽스처 `/tmp/cbv_fix/order_controller.py` 작성:
```python
from ninja_extra import api_controller, route

@api_controller("/orders")
class OrderController:
    @route.post("", response={201: dict})
    def create_order(self, request):
        from django.http import JsonResponse
        return JsonResponse({"id": 1}, status=201)   # response 우회(위반)
```
Run: `python dddjango/scripts/check-response-schema-bypass.py /tmp/cbv_fix/order_controller.py; echo "exit=$?"`
Expected: **exit=0 (거짓음성 — 위반인데 통과)** ← 회귀 확증.

- [ ] **Step 3: 6파일 정규식 교체**

각 파일의 `NINJA_IMPORT_RE = ...` 한 줄을 **정확히** 아래로 교체(1글자도 다르면 미러 깨짐):
```python
NINJA_IMPORT_RE = re.compile(
    r"^\s*(?:from\s+ninja(?:_extra)?(?:\.\w+)*\s+import|import\s+ninja(?:_extra)?)\b",
    re.MULTILINE,
)
```
(기존이 한 줄 `re.compile(r"...", re.MULTILINE)`이면 동일 형식 유지. flags는 기존 그대로.)

- [ ] **Step 4: 봉합 검증 — 위반 픽스처가 잡히는지**

Run: `for s in check-response-schema-bypass check-openapi-error-declaration; do python dddjango/scripts/$s.py /tmp/cbv_fix/order_controller.py; echo "$s exit=$?"; done`
Expected: 둘 다 **exit=2** (정상 발화).

- [ ] **Step 5: 과매치 없음 검증**

throwaway `/tmp/cbv_fix/decoy.py`:
```python
from ninja_jwt import x
from ninja_extrafoo import y
```
Run: `python dddjango/scripts/check-response-schema-bypass.py /tmp/cbv_fix/decoy.py; echo "exit=$?"`
Expected: **exit=0** (ninja_jwt/ninja_extrafoo는 매치 안 됨 — 거짓양성 없음).

- [ ] **Step 6: 양판 byte-identity 검증**

Run:
```bash
for s in check-response-schema-bypass check-openapi-error-declaration check-error-centralization; do
  cmp -s dddjango/scripts/$s.py codex-dddjango/skills/dddjango/scripts/$s.py && echo "$s IDENTICAL" || echo "$s DIFFERS"
done
```
Expected: 3종 모두 `IDENTICAL`.

- [ ] **Step 7: 커밋(사용자 승인 후)**

```bash
git add dddjango/scripts/check-response-schema-bypass.py dddjango/scripts/check-openapi-error-declaration.py dddjango/scripts/check-error-centralization.py codex-dddjango/skills/dddjango/scripts/check-response-schema-bypass.py codex-dddjango/skills/dddjango/scripts/check-openapi-error-declaration.py codex-dddjango/skills/dddjango/scripts/check-error-centralization.py
git commit -m "fix(backstop): ninja_extra import 게이트 확장 — 클래스 컨트롤러 거짓음성 회귀 봉합 (양판 3종)"
```

---

### Task 0.2: `check-structure.py` NJ-1 토큰 확장 (단일본)

**근거:** spec §7 평가지. 현 `ninja_re`가 `from ninja_extra`를 부분문자열로 우연히 통과시키나 `import ninja_extra`/`NinjaExtraAPI()` 단독은 놓침.

**Files:**
- Modify: `workspace/eval/tools/check-structure.py:251` (`ninja_re` 라인)

- [ ] **Step 1: 현재 라인 확인**

Run: `grep -n "ninja_re\|NinjaAPI\|Router(" workspace/eval/tools/check-structure.py`
Expected: `ninja_re = re.compile(r"\bNinjaAPI\b|\bRouter\(|from ninja")` 류 라인 확인.

- [ ] **Step 2: 토큰 확장**

해당 정규식을 아래로 교체:
```python
ninja_re = re.compile(r"\bNinjaAPI\b|\bNinjaExtraAPI\b|\bRouter\(|@?api_controller\b|register_controllers\b|from ninja")
```

- [ ] **Step 3: 클래스 파일 NJ-1 인식 검증**

throwaway `/tmp/cbv_fix/ctrl_only.py`:
```python
from ninja_extra import api_controller, route
@api_controller("/orders")
class OrderController:
    @route.get("")
    def list_orders(self, request): ...
```
Run: `python workspace/eval/tools/check-structure.py /tmp/cbv_fix/ctrl_only.py 2>&1 | grep -i nj-1 || echo "no NJ-1"`
Expected: NJ-1 PASS-신호 출력(클래스 파일을 ninja 스택으로 인식).

- [ ] **Step 4: 커밋(사용자 승인 후)**

```bash
git add workspace/eval/tools/check-structure.py
git commit -m "fix(eval): check-structure NJ-1 토큰에 NinjaExtraAPI·api_controller 추가"
```

---

## Phase 1 — 표준 텍스트 · 에이전트 · 평가지

> Phase 1 각 task는 markdown 편집이라 "편집 → grep/cmp 검증 → 커밋" 구조다. 최종 산문은 기존 절 맥락에 맞춰 윤문하되, **삽입할 핵심 내용(아래 명시)을 빠짐없이** 담고, 검증 step의 grep이 통과해야 한다.

### Task 1.1: implementation-django-ninja — 클래스 컨트롤러 레시피 절 신설 (3사본)

**근거:** spec §3·§4·§7. coder가 따라 만들 본보기 확보(비결정 차단).

**Files (먼저 glob으로 확정):**
- Modify: `workspace/reference/implementation-django-ninja/reference/final.md`
- Modify: `dddjango/skills/implementation-django-ninja/references/final.md`
- Modify: `codex-dddjango/skills/implementation-django-ninja/references/final.md`

- [ ] **Step 1: 현 §2.2 함수형 operation 절 위치 확인**

Run: `grep -n "router = Router()\|@router.post\|def create_order" workspace/reference/implementation-django-ninja/reference/final.md`

- [ ] **Step 2: 클래스 컨트롤러 레시피 절 추가(3사본 동일 내용)**

함수형 operation 절 뒤(또는 §2 적절 위치)에 신설. **담을 내용:**
- 신규 표준 = 클래스 컨트롤러, 함수형은 레거시(위계 명시).
- AFTER 레시피(spec §4 그대로): 파일 `<aggregate>_controller.py`, `from ninja import Status`, `from ninja_extra import api_controller, route`, `@api_controller("/orders", tags=[...])` + `class OrderController:`(ControllerBase 미상속) + `@route.post("", response={...})` + `def create_order(self, request, payload): ... return Status(201, ...)`.
- 등록: config 단일 `NinjaExtraAPI` 소유 + `<app>_api_router.py`가 `from config.api import api` 후 `api.register_controllers(OrderController)`. 415 격리 시 `api.add_router(...)` 같은 인스턴스.
- 탐색→포함/생성 규칙(spec §6).
- `INSTALLED_APPS += ['ninja_extra']`.

- [ ] **Step 3: 3사본 동기 검증**

Run:
```bash
diff <(sed -n '/api_controller/,/register_controllers/p' workspace/reference/implementation-django-ninja/reference/final.md) <(sed -n '/api_controller/,/register_controllers/p' dddjango/skills/implementation-django-ninja/references/final.md) && echo CLAUDE_OK
cmp -s dddjango/skills/implementation-django-ninja/references/final.md codex-dddjango/skills/implementation-django-ninja/references/final.md && echo CODEX_IDENTICAL || echo "codex differs — 동기 필요"
```
Expected: `CLAUDE_OK` + `CODEX_IDENTICAL`(정본↔Claude는 내용 동일, Claude↔Codex byte-id).

- [ ] **Step 4: 커밋(승인 후)** — `git commit -m "std(ninja): 클래스 컨트롤러 레시피 절 신설 (3사본)"`

---

### Task 1.2: implementation-django-ninja — §6.2/§6.3/§2.1/§9.1 개정 (3사본)

**근거:** spec §3.7·§3.8·§7.

**Files:** Task 1.1과 동일 3사본.

- [ ] **Step 1: 대상 절 확인**

Run: `grep -n "exception_handler\|add_decorator(.*view\|TestClient\|버전" workspace/reference/implementation-django-ninja/reference/final.md`

- [ ] **Step 2: 4개 개정(3사본 동일)**
- **§6.2**: 예외 핸들러를 `NinjaExtraAPI` 인스턴스(`api`)에 등록 — "NinjaAPI든 NinjaExtraAPI든 동일" 명시. 클래스 메서드 raise도 같은 중앙 핸들러 도달.
- **§6.3(`:466` "협상 소유")**: 415 함수형/클래스 분기 — "함수형 Router = `add_decorator(mode="view")`; 클래스 컨트롤러는 add_decorator 부재 → 415 기본 비적용(C 정책), 외부 공개 필요 시 함수형 Router로 격리(같은 api에 add_router)". `payload: Schema` 바인딩은 컨트롤러에서도 강제(raw json.loads 금지 불변).
- **§2.1**: 설치에 `django-ninja-extra` + `INSTALLED_APPS += ['ninja_extra']` + 핀.
- **§9.1**: TestClient 절에 컨트롤러용 `ninja_extra.testing.TestClient(Controller)` 추가(함수형 `TestClient(router)`와 병기).

- [ ] **Step 3: 동기 검증** — Run: `cmp -s dddjango/skills/implementation-django-ninja/references/final.md codex-dddjango/skills/implementation-django-ninja/references/final.md && echo IDENTICAL`
Expected: `IDENTICAL`.

- [ ] **Step 4: 커밋(승인 후)** — `git commit -m "std(ninja): §6.2 NinjaExtraAPI·§6.3 415 분기·§2.1 설치·§9.1 TestClient (3사본)"`

---

### Task 1.3: discipline-houserules — 파일명·`Controller` 접미사·트리/표·SKILL.md (3사본 + SKILL 2벌)

**근거:** spec §3.6·§3.8·§7.

**Files:**
- Modify: `workspace/reference/discipline-houserules/reference/final.md`
- Modify: `dddjango/skills/discipline-houserules/references/final.md` + `dddjango/skills/discipline-houserules/SKILL.md`
- Modify: `codex-dddjango/skills/discipline-houserules/references/final.md` + `codex-dddjango/skills/discipline-houserules/SKILL.md`

- [ ] **Step 1: 대상 위치 확인**

Run: `grep -n "api_<resource>\|api_router\|Router\|파일명\|Controller\|Repository\|Port" workspace/reference/discipline-houserules/reference/final.md`
Run: `grep -n "Command\|Query\|Port\|Repository" dddjango/skills/discipline-houserules/SKILL.md codex-dddjango/skills/discipline-houserules/SKILL.md`

- [ ] **Step 2: final.md 3사본 개정**
- §4 명명에 **`Controller` presentation 역할 접미사** 추가(`<Aggregate>Controller`).
- 파일명 규약: presentation api 컨트롤러 파일 = **`<aggregate>_controller.py`**(주 클래스명 snake_case 규약 정합). 기존 `api_<resource>.py` 언급을 컨트롤러 파일명으로 갱신.
- 트리/표(`api_<resource>.py`·"Router" 셀)를 "Router/`@api_controller` 클래스"로, `<app>_api_router.py` 설명을 "config.api import + `register_controllers`(BC 로컬)"로 갱신.

- [ ] **Step 3: SKILL.md 2벌 명명 bullet에 `Controller` 동기**

`dddjango/skills/discipline-houserules/SKILL.md`·`codex-dddjango/.../SKILL.md`의 R/C/Q·포트/리포 접미사 bullet에 `Controller`(presentation) 한 줄 추가. carve-out 예시에 `api = NinjaExtraAPI()` 병기.

- [ ] **Step 4: 동기 검증**

Run:
```bash
cmp -s dddjango/skills/discipline-houserules/references/final.md codex-dddjango/skills/discipline-houserules/references/final.md && echo FINAL_ID
cmp -s dddjango/skills/discipline-houserules/SKILL.md codex-dddjango/skills/discipline-houserules/SKILL.md && echo SKILL_ID
grep -c "Controller" dddjango/skills/discipline-houserules/SKILL.md
```
Expected: `FINAL_ID` + `SKILL_ID` + `Controller` 매치 ≥1.

- [ ] **Step 5: 커밋(승인 후)** — `git commit -m "std(houserules): Controller 접미사·파일명 _controller.py·register_controllers 배선 (3사본+SKILL 2벌)"`

---

### Task 1.4: 버전-핀 정본 위치 확정 (깨진 §6.2 앵커 복구)

**근거:** spec §7 "버전-핀 정본 위치 확정". `implementation-django-ninja`·`implementation-test`가 존재하지 않는 `discipline-houserules §6.2`를 참조(댕글링).

- [ ] **Step 1: 댕글링 참조 확인**

Run: `grep -rn "houserules.*§6.2\|§6.2.*버전\|버전.*핀" workspace/reference/ dddjango/skills/ codex-dddjango/skills/`

- [ ] **Step 2: 택일 결정 — implementation-django-ninja §2.1로 흡수**

(권장: ninja 설치 규율과 같은 곳) `implementation-django-ninja` §2.1에 "버전-핀 규율"(기억 버전 금지·설치시점 resolve·매니페스트 기록) 본문을 두고, 두 참조의 `discipline-houserules §6.2`를 `implementation-django-ninja §2.1`로 정정(3사본 각각). `django-ninja-extra` 핀도 이 절에 포함.

- [ ] **Step 3: 댕글링 0 검증**

Run: `grep -rn "houserules.*§6.2" workspace/reference/ dddjango/skills/ codex-dddjango/skills/ | grep -v "§2.1" || echo "no dangling"`
Expected: `no dangling`.

- [ ] **Step 4: 커밋(승인 후)** — `git commit -m "std(ninja): 버전-핀 규율 §2.1 흡수 + 댕글링 §6.2 참조 복구"`

---

### Task 1.5: implementation-test — §19 TestClient 컨트롤러 갱신 (3사본)

**근거:** spec §7. §19(19.1~19.3) TestClient 6곳이 함수형 `TestClient(router)` 전제.

**Files:** `implementation-test`(3사본). SKILL.md는 §19 포인터라 불요.

- [ ] **Step 1: 6곳 확인** — Run: `grep -n "TestClient\|from ninja.testing\|import router" workspace/reference/implementation-test/reference/final.md`
- [ ] **Step 2: §19 갱신** — 컨트롤러 테스트는 `from ninja_extra.testing import TestClient; client = TestClient(OrderController)`. 함수형 격리 Router 경로는 기존 `TestClient(router)` 병기. import 경로를 표준 트리(`presentation_layer/api/<feature>/`)로 정합.
- [ ] **Step 3: 동기 검증** — Run: `cmp -s dddjango/skills/implementation-test/references/final.md codex-dddjango/skills/implementation-test/references/final.md && echo IDENTICAL`
Expected: `IDENTICAL`.
- [ ] **Step 4: 커밋(승인 후)** — `git commit -m "std(test): §19 컨트롤러 TestClient(ninja_extra.testing) (3사본)"`

---

### Task 1.6: 에이전트 design-architect (양판)

**근거:** spec §7.

**Files (glob 확정):**
- Modify: `dddjango/agents/design-architect.md`
- Modify: `codex-dddjango/skills/dddjango-design-architect/SKILL.md`

- [ ] **Step 1: 현 operation/Router 언급 확인** — Run: `grep -n "operation\|Router\|Schema\|415" dddjango/agents/design-architect.md`
- [ ] **Step 2: 개정(양판 동일 의미)** — 생산자 규칙 추가: "API 스택은 `NinjaExtraAPI`+`@api_controller` 컨트롤러(애그리거트 단위)로 설계; touched 표면 함수형 잔존 금지; 415 외부공개는 명시 기록(침묵 시 내부전용)". "Router/operation 작성" 문구가 컨트롤러 메서드 포괄.
- [ ] **Step 3: 검증** — Run: `grep -c "api_controller\|컨트롤러\|NinjaExtraAPI" dddjango/agents/design-architect.md codex-dddjango/skills/dddjango-design-architect/SKILL.md`
Expected: 양쪽 ≥1.
- [ ] **Step 4: 커밋(승인 후)** — `git commit -m "agent(architect): 클래스 컨트롤러 생산자 규칙·415 외부공개 명시 (양판)"`

---

### Task 1.7: 에이전트 discipline-reviewer — "무조건 클래스" 렌즈 + NJ 규율 보정 (양판)

**근거:** spec §7. 핵심 렌즈(touched 술어).

**Files:**
- Modify: `dddjango/agents/discipline-reviewer.md`
- Modify: `codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md`

- [ ] **Step 1: 현 NJ 규율·레드플래그 확인** — Run: `grep -n "@router\|@api\|operation\|catch-all\|415" dddjango/agents/discipline-reviewer.md`
- [ ] **Step 2: 개정(양판 동일 의미)**
- "operation 본문" 정의에 "함수형 `@router.*` 또는 클래스 `@route.*` 메서드" 포함 1회.
- 레드플래그 `@router.*/@api.*` 열거를 `@router.*/@route.*`(함수·메서드 무관)로 교체.
- **신설 "무조건 클래스" 렌즈(important)**: "touched(신규·수정) presentation 표면에 함수형 operation 잔존 = 지적; untouched 기존 함수형 = 면제(grandfather)". DR-21 강등 방지 문구.
- 415 비적용 스코프에서 415-부재 비지적. `:41` "우회 방어불가"를 컨트롤러 분기 보정(컨트롤러는 add_decorator 부재이나 `payload: Schema` 바인딩 강제·raw json.loads는 여전히 blocker).
- 레드플래그에 "presentation에 `NinjaAPI()` 2개 이상" 추가.
- [ ] **Step 3: 검증** — Run: `grep -c "touched\|@route\|grandfather\|무조건" dddjango/agents/discipline-reviewer.md codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md`
Expected: 양쪽 ≥1.
- [ ] **Step 4: 커밋(승인 후)** — `git commit -m "agent(reviewer): 무조건 클래스 렌즈(touched 술어)·NJ 규율 컨트롤러 보정 (양판)"`

---

### Task 1.8: 에이전트 design-review-api·acceptance-tester·coder (양판)

**근거:** spec §7.

**Files:** 3 에이전트 × 양판(`dddjango/agents/<role>.md` + `codex-dddjango/skills/dddjango-<role>/SKILL.md`).

- [ ] **Step 1: 경로/현 텍스트 확인** — Run: `ls dddjango/agents/ codex-dddjango/skills/ | grep -i "review-api\|tester\|coder"`
- [ ] **Step 2: 개정(각 양판 동일)**
- `design-review-api`: 컨트롤러 prefix 합성(`@api_controller` prefix + `@route` 경로)·`register_controllers` 등록을 계약 점검에 인지(신규 추가).
- `acceptance-tester`: 최종 URL = prefix 합성 + `ninja_extra.testing.TestClient(Controller)` + operationId 규칙차 인지.
- `coder`: implementation-django-ninja 클래스 레시피 참조(본보기).
- [ ] **Step 3: 검증** — Run: `grep -lc "컨트롤러\|api_controller\|register_controllers\|TestClient(" dddjango/agents/design-review-api.md dddjango/agents/acceptance-tester.md dddjango/agents/coder.md`
- [ ] **Step 4: 커밋(승인 후)** — `git commit -m "agent(review-api·tester·coder): 컨트롤러 등록·URL 합성·레시피 인지 (양판)"`

---

### Task 1.9: 평가지 NJ-1 판정기준 개정 + DR-47식 동결-해제 기록

**근거:** spec §7. **기준 변경**이라 명시 동결-해제 필요.

**Files:**
- Modify: `workspace/eval/rubric/RUBRIC.md` (NJ-1 `:55`, 동결 기록부)
- Modify: `workspace/eval/rubric/EVAL-METHOD.md` (결정 레인 `:66`)

- [ ] **Step 1: NJ-1 기준·결정레인·동결 기록부 확인** — Run: `grep -n "NJ-1\|NinjaAPI.*Router\|동결\|동결 해제" workspace/eval/rubric/RUBRIC.md workspace/eval/rubric/EVAL-METHOD.md`
- [ ] **Step 2: NJ-1 결정 레인 술어 동시 개정**
- RUBRIC `:55` + EVAL-METHOD `:66`: `NinjaAPI`+`Router` → `NinjaAPI`/`NinjaExtraAPI` + (`Router` ∨ `@api_controller`/`register_controllers`). `JsonResponse`/DRF는 여전히 FAIL.
- [ ] **Step 3: DR-47식 동결-해제 항목 기록**
- RUBRIC 동결 기록부(`:169` 인근)에 "동결 해제 N건째: NJ-1 판정기준을 클래스 컨트롤러 허용으로 개정(차원 수 불변, 기준 변경)" 명시. EVAL-METHOD 정직표기.
- [ ] **Step 4: 검증** — Run: `grep -n "NinjaExtraAPI\|api_controller" workspace/eval/rubric/RUBRIC.md workspace/eval/rubric/EVAL-METHOD.md`
Expected: NJ-1 술어에 등장.
- [ ] **Step 5: 커밋(승인 후)** — `git commit -m "eval(nj-1): 판정기준 클래스 컨트롤러 허용 개정 + DR-47식 동결-해제 기록"`

---

### Task 1.10: 평가지 NJ-2/SD-6/NJ-7 어휘 · Q-1 앵커 · 앵커 좌표

**근거:** spec §7.

**Files:** `workspace/eval/rubric/RUBRIC.md` (+ 필요 시 EVAL-METHOD).

- [ ] **Step 1: 대상 확인** — Run: `grep -n "operation 본문\|NJ-2\|SD-6\|NJ-7\|Q-1\|415\|api_order" workspace/eval/rubric/RUBRIC.md`
- [ ] **Step 2: 개정**
- NJ-2·SD-6·NJ-7의 "operation"에 "(함수형 또는 컨트롤러 메서드)" 1회 정의.
- Q-1 앵커(`:143`): 415/406을 C 정책으로 재서술("내부전용 기본 비적용=정상, 외부공개 명시 시만"). "underdetermined" 결정화. (앵커는 freeze 밖.)
- NJ-1/2/5 앵커 좌표: 클래스 메서드 형태(`self`) 병기 또는 단서.
- §4.3.1 EP 매트릭스는 **무변경**(주석으로 "415 EP 없음 → C 정책 무충돌" 명기).
- [ ] **Step 3: 검증** — Run: `grep -c "컨트롤러 메서드\|C 정책\|self" workspace/eval/rubric/RUBRIC.md`
Expected: ≥1.
- [ ] **Step 4: 커밋(승인 후)** — `git commit -m "eval: NJ-2/SD-6/NJ-7 어휘·Q-1 앵커 415 C정책·앵커 좌표 보정"`

---

### Task 1.11: 게이트 설명문 + plugin.json 버전 + 무영향 주석

**근거:** spec §7.

**Files:**
- Modify: `dddjango/commands/dddjango.md` + `codex-dddjango/skills/dddjango/SKILL.md` (스크립트 설명문)
- Modify: `dddjango/.claude-plugin/plugin.json` + `codex-dddjango/.codex-plugin/plugin.json` (version)
- Modify: `architecture-ddd`·`implementation-django` 정본 (무영향 확인 주석, 선택)

- [ ] **Step 1: 현 버전·설명문 확인** — Run: `grep -n "version\|@router.post\|response={201" dddjango/.claude-plugin/plugin.json dddjango/commands/dddjango.md`
- [ ] **Step 2: 개정**
- 게이트 설명문의 함수형 `@router.post` 예시를 "함수형 또는 `@route.post` 클래스 메서드"로 정합(배선 무변경).
- `plugin.json` 양판 `version`을 minor 업(현재 1.8.0 → **1.9.0**).
- [ ] **Step 3: plugin 검증 + 버전 동기**

Run: `grep '"version"' dddjango/.claude-plugin/plugin.json codex-dddjango/.codex-plugin/plugin.json`
Expected: 양쪽 `"1.9.0"`.
(plugin validate 도구가 있으면 실행.)

- [ ] **Step 4: 커밋(승인 후)** — `git commit -m "plugin(nj-cbv): 게이트 설명문 클래스 정합 + 1.9.0 (양판)"`

---

## Self-Review

**Spec coverage** (spec 절 → task 매핑):
- §3.1~3.6(최소사용·진입점·단위·미상속·데코·명명) → Task 1.1·1.3 ✓
- §3.7(415 C정책·외부공개 격리·permission 각주) → Task 1.2·1.7 ✓
- §3.8(등록 위치 단일 인스턴스·BC 로컬) → Task 1.1·1.2·1.3 ✓
- §4 레시피(api import·add_router·Status) → Task 1.1 ✓
- §6 탐색 규칙 → Task 1.1 ✓
- §7 표준(ninja·houserules·test·architecture-api 무변경·무영향) → Task 1.1·1.2·1.3·1.4·1.5·1.11 ✓
- §7 에이전트 5종 → Task 1.6·1.7·1.8 ✓
- §7 백스톱 봉합 3종 + check-structure → Task 0.1·0.2 ✓
- §7 평가지(NJ-1 동결해제·어휘·Q-1·앵커·EP 무변경) → Task 1.9·1.10 ✓
- §7 게이트 설명문·plugin 버전 → Task 1.11 ✓
- §8 0차/1차 → Phase 0/1 ✓ (2차 라이브·3차 백스톱 = 후속, scope 밖 명시)
- §9 리스크 → 표준/주석에 박제(Task 1.2·1.7·1.10) ✓

**Gap:** 없음(2차/3차는 의도적 후속). `use_unique_op_id=False` 결정은 라이브(2차) 후라 이 플랜 밖 — spec §9에 박제됨.

**Placeholder scan:** Task 1.4 버전핀 "택일"은 Step 2에서 "§2.1 흡수"로 결정 박음(placeholder 아님). 표준 산문 윤문은 각 task가 "담을 내용" 불릿 + grep 검증으로 결정성 확보.

**Type consistency:** 정규식 리터럴(Task 0.1)·파일명 `<aggregate>_controller.py`·`register_controllers`·`NinjaExtraAPI`·`api.add_router`·`ninja_extra.testing.TestClient` 전 task 일관 확인.

---

## 후속 (이 플랜 밖)
- **2차 라이브**: dual `/dddjango`로 클래스 생성·reviewer 집행·기존 백스톱 16종 회귀 매트릭스. `use_unique_op_id` 결정. NinjaExtraAPI 기본 핸들러 우선순위 확인.
- **3차 백스톱**: 라이브 N≥2 후 "무조건 클래스"(부재+신규 신호) 백스톱 신설 + reviewer 2중화.
