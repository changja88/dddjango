# 적대 리뷰 B — 규범·코퍼스 정합 (현장 보고 typecheck 수리 · 1단계 문제 검증) · 2026-09-03

리뷰어 B(코퍼스 정합). 저장소 무수정. 실측 픽스처: `scratchpad/b3/rv2/fx_alias/`(내가 만든 `_StrEnum` alias 3벌) · 조사자 픽스처 `scratchpad/b3/mypy/fx/`·`repro.py` 재실행.
Serena: skipped — opt-in 표식(`.serena/project.yml`) 없음 · graphify 표식 없음 → 기본 도구.

## (1) 판정 표

| # | 항목 | 판정 | 근거 (파일:행) |
|---|---|---|---|
| 1-A | A 예제 소유·경로 | **검증됨** — graph-owned · Section `…/architecture-ddd/references/final.md/s016-3.1`(`sectionOwner owner-graph`) · 블록 **b4 `kind-code`** — `statesNorm` 없음 → Work/Expression/리비전 번호 **없음**(예제 교체 = 블록 리터럴 편집, ISSUED 불요). 제안 2(«타입 좁히기는 object 경계 소유» 문장)를 넣으면 **신규 kind-norm 블록 + 신규 채번**(다음 번호 R-3442 — ISSUED 마지막 R-3441) | `ontology/rules/architecture-ddd-final.ttl:2195-2222`(s016-3.1 · b1~b4) · 렌더 `dddjango/skills/architecture-ddd/references/final.md:473-548`(마커 473·548) · `ontology/ISSUED` tail R-3441 · `workspace/tools/ontology-authoring.md:38-44`(§5 채번) |
| 1-C | C 문면 소유·경로 | **검증됨(전제 정정)** — 현장 보고의 «§2»는 SKILL description ②이고 실제 절은 **SKILL §4**(s007-4). b1 = R-3148(예외 0)·R-3149·R-3150, b2 = R-3151(«문법이 없는 자리뿐»), b5 = **R-3154 Exception «문법 부재 자리 ③ 프레임워크 선언(모델 필드·class Meta·enum 멤버)»** — 전부 Expression `@2026-08-22` rev 1. Enum 예외 문면은 **이미 존재**(SKILL.md:72 «enum 멤버(`RED = 1`) — 달면 프레임워크 의미가 오작동한다»). 개정 시 형식 = R-3154 **rev 2 in-place**(`prov:wasRevisionOf` + `djr:revisionKind djr:revision-clarification`, 선례 R-3427 rev2 `agent-design-architect.ttl:1725-1735`), 신규 채번 불요 | `ontology/rules/discipline-houserules-skill.ttl:421-423, 445-447, 469-471, 936-967` · `dddjango/skills/discipline-houserules/SKILL.md:63-74` · `ontology/vocab/djr.ttl:192-205`(revision·kind 3종) |
| 1-비용 | 렌더 후 바뀌는 파일 전수 | **검증됨** — 아래 (2) 표. 핵심: ttl 1바이트라도 바뀌면 `rulepack.json`의 `built_from` sha 불일치 → `make rulepack` 필수(Claude·Codex byte 미러 2파일) · LEDGER는 graph 행이 절마다 존재(`s016-3.1 graph`·`s007-4 graph`)하고 관례상 재기준선 행 append(09-03 R-3427 rev2 선례 tail 3행) · SKILL.md는 `corpus_mirror_sync` **스코프 밖**(docstring «SKILL.md · agents · commands 미러 면제») → Codex `dddjango-discipline-houserules/SKILL.md` **수동 의미 미러** | `dddjango/scripts/rulepack.json:3-12` · `ontology/LEDGER.tsv`(grep s016-3.1 / s007-4 · tail) · `workspace/tools/corpus_mirror_sync.py:1-30` · `Makefile:100-131,217-218` |
| 2-A | 같은 관용구 전수 | **검증됨 — 단일 지점** — `isinstance(self.` + `object.__setattr__` + «자기 검증 (Self-Validation)» 문자열은 코퍼스(ontology/rules·skills·agents·commands) 전체에서 **정본 1곳(ttl:2222 b4)+렌더 1곳(final.md:500-502)** 뿐. 한 곳만 고쳐도 남는 모순 없음. 인접 `isinstance` 예제는 전부 정당한 자리: `__eq__(self, other)`(ddd:583 — `other: object`), implementation-python Validator 디스크립터(`validate(self, value)` 무타입 — 디스크립터 경계 785-805), TypeGuard(321), union 분기(428·2414), Vector 연산자(1391-1420), django-web 예외 분기(366-368). §4.2 Money(ttl:2608 s030-4.2/b2)는 `__post_init__` 없음 — 무모순 | grep 결과 · `dddjango/skills/implementation-python/references/final.md:785-805` |
| 2-A' | «값 불변식만·타입은 시그니처 소유» 충돌 여부 | **검증됨 — 충돌 없음, 오히려 내부 모순 해소** — ① cleancode §12.7 «"외부"를 어디로 정할지 결정하고 그 경계에서 검증»(final.md:1726-1730)과 동방향 ② implementation-python §12 «pydantic validator는 boundary validation… 도메인 규칙을 대신 소유하지 않는다 / strict mode = coercion 은폐 방지»(1460-1465)와 동방향 ③ **#69**(«개발자 실수를 막는 검사는 런타임이 아니라 테스트·타입 체커의 몫» — 검사기 `check-public-surface-annotation.py:18-20, 359-376`가 `isinstance` 가드+raise를 ⓓ 후보로 방출, discipline-reviewer.md:117 점검 항목) — **현행 Money 예제가 플러그인 자기 규범 #69와 어긋나 있었다** ④ R-3158 «mypy strict는 시그니처만 강제». «Self-Validation» 용어는 유지하되 «값 불변식»으로 정의하면 DDD 문면과도 무충돌. **MINOR**: 규범 문장에 `redundant-expr`·플래그명을 넣지 말 것(플래그 무관 원칙으로 성문) · 제안 예제의 `isinstance(self.amount, bool)`는 #69 ⓓ 후보를 유발(exit 불산입) — `type(self.amount) is bool`로 쓰면 후보 소음 0 · 같은 블록의 `PhoneNumber.__post_init__(self)`에 `-> None` 부재(R-3156으로 면제되나 손대는 김에 동승) | `dddjango/skills/discipline-cleancode/references/final.md:1726-1752` · `dddjango/scripts/check-public-surface-annotation.py:18-20,359-376` · `dddjango/agents/discipline-reviewer.md:117` · `discipline-houserules-skill.ttl:501-503`(R-3158) |
| 3-C | «예외 0» ↔ «문법 없는 자리 면제» 불일치? | **검증됨 — 불일치 없음 · 규범 공백도 아님** — 5개 표면이 전부 일치: SKILL §4 b2+b5(R-3151·R-3154 «enum 멤버») · Coordinator :133 «문법 없는 자리만 면제»(Codex SKILL:150 동일) · 검사기 docstring :11-12 «선언적 클래스 본문(ORM 모델 필드·ninja Schema 필드·**enum 멤버**)은 면제» + `DECLARATIVE_BASE_NAMES`(:73-82 — Enum·IntEnum·**StrEnum**·Flag·IntFlag·Choices·TextChoices·IntegerChoices) · design_pregate b35 `NAME = "literal"`(enum 멤버)(:43·:139 `StrEnum → from enum import StrEnum`) · rulepack R-3154 `checkers=[check-public-surface-annotation.py]`(:56254-56268). 검사기의 Enum 본문 미검사는 **의도된 면제**(문법 없는 자리 성문의 구현)이지 우연이 아니다 | 위 각 행 |
| 3-C' | 검사기 실동작 | **BLOCKER(조사자 전제 ⓪ 반증)** — 검사기는 base를 **이름 문자열**로만 식별(`_name_of`, :135-143). 실파일은 `from enum import StrEnum as _StrEnum`(book_usage_policy.py:1·abstention_reason.py:1) → `_StrEnum ∉ DECLARATIVE_BASE_NAMES` → 무주석 멤버를 «클래스 변수 첫 대입에 타입 없음»으로 **#493 blocker**(내 픽스처 exit 2·2건), 주석 부착형은 검사기 clean·mypy `[misc]` 2건(plain `--strict`에서도 발생). 즉 **alias 형상에서는 검사기↔mypy가 어느 쪽을 택해도 red**. 조사자 픽스처는 plain `StrEnum`이라 이 충돌을 못 봤다. `enum.StrEnum` 한정 표기는 인식됨(`ast.Attribute.attr`) | `scratchpad/b3/rv2/fx_alias/` 실행 로그(본문 §실측) · `check-public-surface-annotation.py:127-143` |
| 3-C'' | 인과 사슬(레인 기록) | **MAJOR(현장 보고 원인 귀속 오류)** — 레인 자체 STOP `spring_dream_server/docs/superpowers/orders/lane/STOP-fortune-reading-strenum-registry-alias.md`(09-01 10:34, dddjango 2.17.12)가 정확히 이 문제를 기록: `_StrEnum` 3파일 #493 귀속 8건 · «enum member에 annotation을 붙이면 checker만 우회할 뿐 표준 enum 선언과 Pyright 타입 계약을 깨므로 **금지된 workaround**» · 발주자 결정 **C = 3파일을 plain `StrEnum`으로 되돌림**(«checker는 저장소 표준과 일치 — 정정 대상 아님»). 그런데 `book_usage_policy.py`·`abstention_reason.py`는 같은 날 **09:13 WIP 커밋(8216c78)** — STOP 이전 — 에 alias+주석(=금지 workaround) 형상으로 들어가 결정 C 적용에서 **누락**됐다. alias 관행의 출처는 레인 discipline-reviewer의 «one-public-symbol/file = imported binding 포함» 과잉 해석 — 코퍼스에 사설 alias·re-export 규칙 **없음**(grep 0건 · `check-naming.py:413-418` #345는 ClassDef/FunctionDef만 계수) | 해당 STOP §1·§5 · `git log 8216c78`(09-01 09:13) · STOP 파일 커밋 7350c24(10:43) |
| 4-⓪ | «검사기↔mypy 충돌 없음» | **BLOCKER** — 위 3-C'. 조사자 명제는 plain `StrEnum` 한정으로만 참 | — |
| 4-해석 | «reading 주석·카탈로그 미주석 = 해석 불일치» | **MAJOR(반증)** — spring_dream 전 BC(promotion·query_translation·fortune_character·fortune_calculation·fortune_reading의 STOP-C 3파일·카탈로그)가 plain `StrEnum`+무주석. 주석 부착 = alias 2파일뿐(`grep -E '^\s+[A-Z_]+: str = "'` 결과 6행 전부 그 2파일). alias↔주석 상관 100% → 문면 해석 차이가 아니라 **검사기 alias 사각의 산물** | grep 결과(본문 §실측) · `~/.herdr/worktrees/…/fortune_visibility_status.py:1-9` |
| 4-버전 | 두 레인 §4 문면 동일? | **검증됨** — enum 예외 행은 커밋 e954659(DR-39, v1.0.0 태그 포함)부터 존재. 태그 2.17.12~2.17.16 SKILL.md §4 텍스트 동일(행 번호만 71→72) · Claude 캐시 2.11.0→2.17.16 전 판 존재 · Codex 캐시 2.17.16 존재 · Claude↔Codex §4 9행 `diff` IDENTICAL. STOP 기록의 실행 핀 2.17.12/2.17.14 ≠ 보고서 2.17.16이나 문면 동일이라 무관 | `git log -S'enum 멤버'` · `git show <tag>:…SKILL.md` |
| 4-A | A 재현·plain strict 무발화 | **검증됨** — `repro.py` 프로젝트 플래그: `unreachable`:12 · `redundant-expr`:20 · Enum `[misc]`:26·27 = 4건 / plain `--strict`: Enum 2건만(A 0건). 발주 pyproject `[tool.mypy]` strict+warn_unreachable+enable_error_code 확인(:69-77) | mypy 2.3.1(발주 venv) |
| 5-A | 무손실·일반화 | **검증됨(MINOR 부기)** — 예제는 어떤 검사기도 읽지 않음 → 검출 집합 불변. 일반화: kkebi 미러(08-25 동결) application에 frozen dataclass 19파일·`__post_init__` 7곳·`isinstance` 0·`not isinstance(` 0 → **표본 외 발화 0**(효과는 spring_dream 2레인 6VO/13건 한정 — ⓒ 과대 추정 주의). Claude/Codex: final.md byte 미러(md5 동일)·`corpus_mirror_sync --write` 경로 | kkebi grep · md5 |
| 5-C | 무손실·일반화 | **MAJOR** — 문면만 고치면(«Enum 예외 명시») **no-op**(이미 있음) — 결함(alias 사각)은 그대로 남아 Codex형 레인(`_BaseModel`·`_ConfigDict`·`_TypeAlias`·`_EvidenceSet` 등 underscore alias 관행 — design-spec.md:562·1568) 재발. 루브릭 전제 «실행기·검사기 무변경»은 C에 대해 **성립하지 않음** → 결정 게이트 ①에서 범위 재정의 필요. 검사기 alias 해소 수정은 오탐만 제거(alias→원이름 사상은 선언 인식을 늘릴 뿐 비선언 클래스 검사를 줄이지 않음) → 진탐 집합 단조 유지 가능하나 **픽스처 red/green + `findings_count_matrix`·`fixture_matrix` 골든 갱신 + Codex byte 미러** 동반 | `workspace/eval/fixtures/public_surface/`(Enum 픽스처 0건) · `Makefile:135-166` |

## (2) 건드리는 IRI·파일 전수

### A — 값 객체 예제(+선택: 경계 좁히기 문장)

| 구분 | IRI / 파일 | 조치 |
|---|---|---|
| 정본 | `<djr#s/dddjango/skills/architecture-ddd/references/final.md/s016-3.1/b4>` (kind-code) | `djr:text` 리터럴 교체(rdflib 편집 + canon 재직렬화) |
| 정본(선택 · 제안 2) | 신규 `…/s016-3.1/b5` kind-norm + Work `djr:R-3442`(Obligation) + Expression `R-3442@2026-09-03` rev1 | `ontology/ISSUED` append `R-3442<TAB>2026-09-03<TAB>rules/architecture-ddd-final.ttl` · b4 후행 스팬(§13 구분자 귀속) 조정 |
| 렌더 | `dddjango/skills/architecture-ddd/references/final.md:490-548` | `ontology_render.py --apply architecture-ddd-final` |
| byte 미러 | `codex-dddjango/skills/dddjango-architecture-ddd/references/final.md` | `corpus_mirror_sync.py --write`(불변식2) |
| 소스 미러 | `workspace/reference/architecture-ddd/reference/final.md`(P1 헤더 보유 · 본문 splice) | 같은 명령(불변식1) |
| 소성물 | `dddjango/scripts/rulepack.json` · `codex-dddjango/skills/dddjango/scripts/rulepack.json`(byte) | `make rulepack` |
| 원장 | `ontology/LEDGER.tsv` — `architecture-ddd-final s016-3.1 graph` 재기준선 행 | append(관례) |
| 무접촉 | `architecture-ddd/SKILL.md`(Money·자기 검증 언급 0) · agents · Coordinator · 검사기 27종 · `s030-4.2/b2` Money | — |

### C — Enum 멤버

| 구분 | IRI / 파일 | 조치(문면 경로) | 조치(검사기 경로) |
|---|---|---|---|
| 정본 | `djr:R-3154` + `<djr#R-3154@2026-08-22>`(rev1) → 신규 `<djr#R-3154@2026-09-03>` rev2 `revision-clarification`, `currentExpression` 전환 · 블록 `…/discipline-houserules/SKILL.md/s007-4/b5` 리터럴 | rev2 3노드 + b5 텍스트 | 불요 |
| 렌더 | `dddjango/skills/discipline-houserules/SKILL.md:72` | `--apply discipline-houserules-skill` | — |
| 의미 미러(수동) | `codex-dddjango/skills/dddjango-discipline-houserules/SKILL.md:65` | 손 복사(스코프 밖) | — |
| 소성물 | rulepack ×2 | `make rulepack` | — |
| 원장 | `LEDGER.tsv` `discipline-houserules-skill s007-4 graph` | append | — |
| 검사기 | `dddjango/scripts/check-public-surface-annotation.py:73-82,135-143` + `codex-dddjango/skills/dddjango/scripts/check-public-surface-annotation.py`(byte) | — | alias 해소(ImportFrom/Import `asname`→원이름) · docstring :11-12 보강 |
| 픽스처·골든 | `workspace/eval/fixtures/public_surface/{good,bad_rules}` (현재 Enum 케이스 0) · `findings_count_matrix`·`fixture_matrix`·`checker_baseline_matrix` | — | green: `_StrEnum` alias 무주석 / red: 비선언 base alias 무주석 유지 · 골든 재생성 |
| 무접촉 | Coordinator :133(이미 «문법 없는 자리만 면제») · design-architect b35 · discipline-reviewer · implementation-python R-2789(b `restates` s007-4/b1) | — | — |

## (3) 수리 문면 방향 권고

- **A — 채택(단일 지점·내부 모순 해소)**: b4 예제를 «값 불변식만 검증»으로 교체. docstring은 «자기 검증(Self-Validation): 값의 불변식 — 타입은 시그니처가 약속하고 타입 체커가 지킨다(#69)»처럼 플래그명 없이. 제안 2(경계 좁히기 문장)는 신규 채번 1건으로 s016-3.1에 두되 cleancode §12.7·implementation-python §12와 중복 진술이 되지 않게 «값 객체 절 소관 = 어디서 좁히는가(driven adapter 역직렬화·스냅숏 복원·폼 cleaned_data)» 한 문장으로 한정. 제안 3(테스트 규율)은 이번 리비전 밖(discipline-tdd/implementation-test에 `type: ignore` 관련 문면 0건 — 신설이며 결정 게이트 ① 별도 항목). 제안 4(스모크)는 기각 권고(예제는 «표준 문서군 코드 예시 — 적용 대상 밖» R-3156 — 하네스 비용 대비 과적합).
- **C — «규범 공백» 아님 · «문면 불일치» 아님 → 판별 결과: 검사기 alias 사각(구현 결함) + 레인 이탈(STOP-C 미적용 잔재)**. 따라서 (a) 현장 보고 C의 «문면에 Enum 예외 명시»는 **기각**(이미 성문 — R-3154, 09-01 발주자 자신이 «checker 정정 대상 아님»으로 닫은 사안의 재보고). (b) 실질 수리 후보는 검사기 alias 해소 — 결정 게이트 ①에서 «실행기·검사기 무변경» 전제를 풀어야 채택 가능(무손실 조건: 오탐만 제거, 픽스처 red/green·골든 갱신·byte 미러). (c) 문면은 필요 시 R-3154 rev2 **clarification**만: «enum 멤버(`RED = 1` · `StrEnum`의 `NAME = "value"`) — 주석을 달면 typing spec상 멤버가 아니게 된다(검사기 회피용 주석 금지)». (d) 6건 실코드는 발주측 기계 수정(alias 제거 + 주석 제거 = STOP-C 형상). (e) 부기: 레인이 alias를 채택한 근거인 «imported binding도 공개 심볼» 해석은 코퍼스에 없다 — discipline-reviewer 프롬프트에 «공개 심볼 계수는 소유 정의(ClassDef/FunctionDef)만, import binding 제외»를 1줄 성문할지는 별도 항목(발주자 STOP §5가 이미 «해석 명문화 제안»으로 남김).

## 실측 로그(요지)

```
checker on scratchpad/b3/mypy/fx (plain StrEnum)      → clean exit 0
checker on scratchpad/b3/rv2/fx_alias (_StrEnum alias) → blocker 2건 [#493] policy_alias_unannotated.py:5,:6 exit 2
mypy 2.3.1 --strict(+project flags) fx_alias           → policy_alias_annotated.py:5,:6 "Enum members must be left unannotated [misc]"; unannotated·enum.StrEnum 형 clean
mypy --strict(plain) repro.py                          → Enum 2건만 (A 0건) / +warn_unreachable+redundant-expr → unreachable:12 · redundant-expr:20 추가
spring_dream annotated enum members                    → 6행 전부 _StrEnum 2파일 · 그 외 StrEnum 20+파일 무주석
kkebi-mirror application                               → frozen dataclass 19파일 · __post_init__ 7 · isinstance 0
```

## (4) 10줄 요약

1. A 예제(`isinstance(self.amount)`+`object.__setattr__`)는 코퍼스 전체에서 정본 1곳(`architecture-ddd-final.ttl:2222` s016-3.1/b4 kind-code)뿐 — 리비전 번호 없는 블록 리터럴 교체, 남는 모순 없음.
2. A 수리 문면은 cleancode §12.7·implementation-python §12·R-3158과 동방향이고, 현행 예제가 플러그인 자기 규범 #69(런타임 타입 가드는 타입 체커 몫)와 어긋나 있던 내부 모순을 해소한다 — 채택.
3. A MINOR: 규범 문장에 플래그명(redundant-expr) 넣지 말 것 · `isinstance(.., bool)` 대신 `type(..) is bool`(#69 ⓓ 후보 소음 0) · 같은 블록 `PhoneNumber.__post_init__` `-> None` 동승 · 제안 3·4는 이번 범위 밖/기각.
4. C의 «§2 예외 0»는 SKILL §4(s007-4)이고 **Enum 멤버 예외는 이미 성문**(R-3154, v1.0.0 e954659부터 · 캐시 2.11.0→2.17.16 전 판 · Claude/Codex §4 byte 동일) — 규범 공백 아님.
5. Coordinator :133·검사기 docstring :11-12·`DECLARATIVE_BASE_NAMES`(StrEnum 포함)·pregate b35·rulepack R-3154 5표면 전부 일치 — 문면 불일치도 아님. 검사기의 Enum 본문 미검사는 의도된 면제.
6. **BLOCKER(전제 ⓪)**: 실파일은 `from enum import StrEnum as _StrEnum` — 검사기는 base를 이름 문자열로만 보므로 무주석 멤버를 #493 blocker(exit 2)로 오판하고, 주석형은 mypy `[misc]`로 red → alias 형상에선 양쪽 다 red. 조사자 픽스처는 plain `StrEnum`이라 못 봤다.
7. **MAJOR(원인 귀속)**: 레인 STOP `STOP-fortune-reading-strenum-registry-alias.md`(09-01 10:34)가 이 충돌을 이미 기록·«주석 부착 = 금지 workaround»·발주자 결정 C(plain StrEnum 복귀)로 닫았으나, 09:13 WIP 커밋(8216c78)의 2파일이 누락돼 남은 잔재가 이번 6건이다.
8. «reading 주석·카탈로그 미주석 = 해석 불일치» 반증: 전 BC 20+ StrEnum이 무주석, 주석 6행은 alias 2파일뿐(상관 100%) — 문면이 아니라 검사기 alias 사각의 산물. alias 관행의 근거(«imported binding도 공개 심볼»)는 코퍼스에 없음(check-naming #345는 정의만 계수).
9. C 처방: 문면 «Enum 예외 명시»는 no-op → 기각. 실질은 검사기 alias 해소(오탐만 제거·픽스처 red/green·골든·Codex byte 미러) — 루브릭 전제 «검사기 무변경»과 충돌하므로 결정 게이트 ①에서 범위 재정의. 문면은 필요 시 R-3154 rev2 clarification 1건만.
10. 비용: A = ttl b4(+선택 R-3442 신규 채번) → render → final.md·Codex byte·workspace 소스 미러 → rulepack ×2 → LEDGER s016-3.1; C 문면 = R-3154 rev2 → SKILL.md → Codex SKILL 수동 미러 → rulepack ×2 → LEDGER s007-4. 표본 외(kkebi) A·C 발화 0 → 효과는 spring_dream 한정.
