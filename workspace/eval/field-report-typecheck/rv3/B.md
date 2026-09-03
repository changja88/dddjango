# 적대 리뷰 B — 규범·코퍼스 정합 (현장 보고 typecheck 수리 · 3단계 계획 v1 문면 반증) · 2026-09-03

리뷰어 B(규범·코퍼스 정합). 대상 = `workspace/plan/2026-09-03-field-report-repair-plan.md` v1. 저장소 무수정(읽기·해시 계산만).
Serena: skipped — opt-in 표식(`.serena/project.yml`) 없음 · graphify 표식 없음 → 기본 도구.

## (1) 판정 표

| # | 항목 | 판정 | 근거 (파일:행) |
|---|---|---|---|
| 1-a | b3 불릿 추가 + Obligation 신설의 저작 적법성 | **검증됨(MINOR 1)** — §13 «블록 내 여러 규범 문장은 `statesNorm` 다중 연결 — 행 중간 분할 불요» · 리스트 항은 마커 포함 verbatim으로 norm 블록 귀속 · b3 후행 구분자 `\n\n`는 마지막 불릿 뒤에 유지 · 채번 다음 번호 R-3442(ISSUED 말미 R-3441) · 행 형식 `R-3442<TAB>2026-09-03<TAB>rules/architecture-ddd-final.ttl` · NormShape는 `sh:or(HasChecker HasDelegate)`라 둘 중 하나로 족함. **MINOR**: 같은 블록 b3의 선례가 «반드시 불변이어야 한다 (setter 금지)» 한 불릿을 **R-0495(Obligation)+R-0496(Prohibition)** 로 deontic 분할했다 — 새 불릿의 «재검사·강제 변환은 두지 않는다»는 Prohibition이므로 동일 판형이면 R-3442(Obligation)+R-3443(Prohibition) 2건이 정합. 단일 Obligation도 R-3154(복합 절 1 Exception) 선례로 허용 — 택일하되 prefLabel에 금지 취지 명기. §13 «문장→Work 대응 검수표»·§16 «enforcedBy 근거 검수표» 기록 위치가 계획에 없음 | `workspace/tools/ontology-authoring.md` §5·§13·§16 · `ontology/rules/architecture-ddd-final.ttl:2198-2222`(b3 statesNorm R-0494/0495/0496) · `:493-515` · `ontology/shapes/djr-shapes.ttl:120-122` · `ontology/ISSUED` tail |
| 1-b | 중복 규범 여부 | **검증됨 — 중복 아님, 신설 정당** — 후보 전수: cleancode §12.7 R-1504~1507(«외부» 경계 결정·경계 검증 — 주어 일반, 값 객체 문장 없음) · impl-python §12.0 R-2752~2762(pydantic = boundary validation·도메인 규칙 소유 금지 — **역방향·상보**) · R-3158(mypy strict는 시그니처만 강제 — 타입 «부착» 규율이지 «재검사 금지» 아님) · R-1066/R-1098(reviewer의 #69 «물음» — 절차 층, 답의 기준 아님) · #69 자체는 트리 명세 ast+ 후보(스킬 규범 없음) · impl-python :1194 «정적 타입 체커에 의존하라»는 kind-code 주석. → «값 객체는 선언 타입을 재검사·강제 변환하지 않는다»는 스킬 층 성문 **0** → amendment/restates 대상 IRI 없음. b3→cleancode s097-12.7/b1 `djr:restates`는 가능하나 b3 전체가 재진술이 아니라 비권장 | `dddjango/scripts/rulepack.json` works R-1504~1507·R-2752~2762·R-3158·R-1066·R-1098 · `workspace/design/2026-08-08-tree-revision-spec.md:94` · `implementation-python/references/final.md:1194` |
| 1-c | wiring `enforcedBy` #69(ⓓ) 인정 여부 | **검증됨(조건부)** — 선례: R-1066(«ⓓ#69 후보») · R-1098 → `check-public-surface-annotation.py` enforcedBy + delegatedTo 동반 · R-0494 → `check-domain-model.py`(#268 ⓓ) + delegatedTo. §16 4원: ① 문면 역할명 없음 ② docstring #69 «isinstance 가드 뒤 TypeError/ValueError» ③ 커버 **부분**(isinstance+raise 형만 — `object.__setattr__` coercion·`type() is` 형 무검출) ④ registry #69. → enforcedBy 허용하되 검수표에 «부분 커버·exit 불산입» 명기 · delegatedTo discipline-reviewer가 주 채널(§16 기본값 표: architecture-ddd 구현 시점 규범). 새 예제 `type(x) is bool`은 #69 무발화(`_name_of(c.func)=="isinstance"`만 판정) | `ontology/wiring/architecture-ddd-final.ttl:139-144` · `ontology/wiring/agent-discipline-reviewer.ttl`(R-1066·R-1098) · `check-public-surface-annotation.py:18-20,359-376` · `ontology_structural_check.py:256-264`(① 무소유 0) |
| 1-d | 대안(docstring만·채번 0) | **기각 권고** — R-3156 «표준 문서군의 코드 예시는 개념 전달용 발췌라 적용 대상이 아니다» → 코드 블록 안 문장은 코퍼스 자기 규범상 **비규범** → 집행선 0 + rulepack `by_section` 3.1 불변(R-0494/0495/0496만) → C암·reviewer가 인용할 R-id 없음 → rv1 C가 실증한 «레인마다 즉흥 결정(무처리/ignore/우회)» 그대로. 채번 비용은 ISSUED 1행·계수 3·q4 1·wiring 1 — 미미 | `discipline-houserules-skill.ttl:485-487`(R-3156) · rulepack `by_section` s016-3.1 · rv1 C §2 |
| 2-a | «타입 체커가 지킨다» vs Coordinator 172 | **검증됨(MINOR 문면)** — 코퍼스 전제 = R-3163(§6.1 표준 도구셋 uv·ruff·**mypy strict**… 부재 시 셋업) + R-3158. Coordinator 172 «구성돼 있으면 보고»는 **보고** 규칙(기존 긴장·이번 변경 무관). 새 규범은 방어를 «제거»가 아니라 «경계로 이동» — 타입 체커 부재 프로젝트에서도 0이 아님. 문면은 #69/R-1098 문면 «**테스트·**타입 체커」로 정렬(타입 체커 미가동 시 테스트가 명명된 수호자) | `discipline-houserules/SKILL.md:91`(R-3163) · `:79`(R-3158) · `commands/dddjango.md:172` · `agents/discipline-reviewer.md:117` |
| 2-b | «타입 좁히기는 경계» 소유 충돌 | **검증됨(MINOR 어휘)** — R-0579/R-0594(§5.3 «어댑터는 입력 검증 담당 가능·핵심 정책 소유 금지») 동방향 · R-2752/2755/2756 상보 · R-1505/1506 일반 원칙의 값 객체 특수화 · architecture-api Request validation/422 · ninja Schema 경계 · django-web `form.cleaned_data`→command(:95·:426) 일치 · impl-django :725 «form/model 공유 durable invariant는 model/DB 경계에서도 보장»은 값 불변식이라 무충돌 · cleancode §12.6 DbC 사전조건 예제(:1718)는 값 조건. **어휘**: «스냅숏 복원»은 코퍼스 0회 — «Data Mapper 복원/역직렬화(driven adapter)·요청 Schema(driving adapter)·폼 `cleaned_data`»로 정렬 | `architecture-ddd/references/final.md:1542` · `implementation-python/references/final.md:1459-1465` · `architecture-api/references/final.md:218` · `implementation-django-web/references/final.md:95,426` |
| 2-b′ | **int→float 문장의 내부 모순** | **MAJOR-1** — 초안 «타입 체커가 통과시키는 값(`bool`⊂`int`·`int`→`float`)의 거부는 값 검사에 속한다»: `int`→`float`는 PEP 484 수치 탑으로 **시그니처 `float`가 int 수용을 약속**한 것 → 같은 불릿 1문장 «타입은 시그니처가 약속한다»와 자기 모순(시그니처가 수용을 약속한 값을 런타임이 거부). rv1 A 처방 3은 «int→float 승격은 시그니처 계약 — 값 객체가 거부하지 않는다»였고 계획은 사유 없이 반대 선택. 이 «허가»가 낳는 형상이 `translation_generation_settings.py:40` `type() is not float`(rv1 A 반례 ②). `bool`은 다르다 — 하위 타입이지만 «금액이 True」는 도메인 값 집합 밖 → 값 검사 정당. 문면 확정 게이트 사안 — 초안 그대로는 불가 | rv1 A §(1) A-2(a)·§(3) 3 · `workspace/plan/…-repair-plan.md:34` |
| 2-c | `type(self.amount) is bool` 주석·`!r` | **검증됨(MINOR)** — «bool⊂int → 타입 체커 통과» 충분. `isinstance` 대신 `type() is`인 이유(`isinstance(x, int)`도 True)는 코드 주석 1구로(규범 문면에 검사기 형상 금지 유지). `!r` 적절(True → `True`). docstring이 b3 문장을 그대로 복제 — 단일 출처 위해 «값의 불변식만 — 타입 좁히기는 경계(§3.1 핵심 원칙)»로 축약 권고 | 계획 :19-28 |
| 3-a | R-3154 문면 vs 수리 후 동작 | **검증됨 — clarification 불요** — R-3154 «enum 멤버(`RED = 1`) — 달면 프레임워크 의미가 오작동한다»는 **의미 층**; alias는 멤버 의미를 바꾸지 않음 → 검사기 수리는 문면 쪽으로 **수렴**. 코퍼스에 import alias 금지·`as _X` 규범 0(«별칭» 검색: cleancode aliasing 문제만) → alias 형상 자체 적법. 문면 무변경 주장 성립 | `discipline-houserules/SKILL.md:72` · `discipline-houserules-skill.ttl:469-471` |
| 3-b | docstring 사각 병기 vs Coordinator 133 | **검증됨(MINOR 문구)** — :133 «문법 없는 자리만 면제» 불변. 병기는 «면제 규칙»이 아니라 «검출 한계(오탐 가능 형상)»로 적을 것 — 초안 «전이 면제는 하지 않는다»는 규범처럼 읽힘. 추가: 역방향 중 «중간 선언적 base를 선언적 이름으로 별칭(`from base import TimestampedModel as Model`)»은 수리 후 red(전엔 우연 green) → «오차단 0»은 census·픽스처 한정으로 서술하고 같은 중간-base 사각 분류로 docstring에 포함 | `commands/dddjango.md:133` · 계획 :58·:61-63 |
| 3-c | rulepack #493 항목 문면 | **검증됨 — 변경 0** — `by_alias` 21건에 #493·#69 없음(alias 대장 rule# 공간 미등재) · R-3154 항목 `checkers`는 wiring 파생(자동) · #493 문면은 rulepack에 없음 | rulepack `by_alias` keys · works R-3154 |
| 3-d | **Part 2 §2.4 픽스처 매트릭스 갱신 지시** | **MAJOR-2(계획 오류)** — «`fixture_matrix.py:111` `("bad_rules", 2)` → 3»: 그 `2`는 **기대 exit 코드**(`(라벨, argv, 경로, 기대 exit)` · exit 2=위반)이지 건수가 아니다 → 3으로 바꾸면 매트릭스 red(exit 3=재료 결손). 건수는 `findings_count_matrix.py:130` EXPECTED `(2, 11, 2, "#358×2,#456×2,#493×7,#69×2", sha×3)` — 새 bad_rules 픽스처가 **census 대상 그 자체**이므로 반드시 변한다(#493×8·findings 12·sha 3열 재실측). «census에 없으면 불변» 분기는 성립 안 함. 경로도 `workspace/tools/fixture_matrix.py`(계획 `workspace/eval/` 아님) | `workspace/tools/fixture_matrix.py:103,111` · `workspace/tools/findings_count_matrix.py:130` |
| 4-i | 소스 미러 절 수동 교체 | **검증됨(계획 정확·순서 주의)** — `corpus_mirror_sync._excise_graph_sections`는 LEDGER **유효 행** `baseline_sha256`으로 소스 절을 찾고 매칭 1건 아니면 exit 3. 실측: sha256(렌더 span − marker) = sha256(소스 span) = LEDGER `1e38254c…`(s016-3.1) · s017-3.2·s051-8 동일. → 재기준선 행 sha = 새 렌더 span − marker, 소스 `workspace/reference/architecture-ddd/reference/final.md:481-554` span을 새 span(마커 없음)으로 손교체 → `--write`. LEDGER append와 소스 교체는 **같은 단계**(어긋나면 STRUCTURE) | `corpus_mirror_sync.py:158-190,236-249` · 스크래치 sha 실측 |
| 4-ii | codex byte 미러 경로 | **검증됨** — `codex-dddjango/skills/dddjango-architecture-ddd/references/final.md` 실존 · md5 `61fc99f0…` 배포본과 동일 · `paths_for`가 `dddjango-` 접두 우선. 검사기 미러 `codex-dddjango/skills/dddjango/scripts/check-public-surface-annotation.py` byte 동일(cmp) | `corpus_mirror_sync.py:107-118` |
| 4-iii | target-counts 변화량 | **MINOR(계획 누락)** — NormShape 3450→3451 · **WorkShape 3450→3451(계획에 없음 — `sh:targetClass djr:Work`·Norm⊂Work)** · ExpressionShape 3544→3545(`--with-golden` 계수, 골든 9 포함). 분할 채택 시 각 +2 | `workspace/eval/fixtures/ontology_gate/target-counts.json` · `djr-shapes.ttl:73-75,273-275` · `ontology_hierarchy_check.py` |
| 4-iv | q4 골든 | **검증됨(경로 명시 권고)** — `workspace/eval/fixtures/rulepack/query-golden.json` q4 `distinct_works`/`rows` 3441→3442 (`query_golden_check.py --emit`). 계획 «q4 골든» 언급 ✓ | `query_golden_check.py:24-25` |
| 4-v | spec_lint·rule-owner-map·귀속 매핑표 | **검증됨 — 불요** — spec_lint ⑦⑧과 `_rule_numbers`는 검사기 규칙 **#N** 대장(`2026-08-11-rule-owner-map.md`) · structural ⑥″는 `rule#N` alias 문법만 → R-3442(alias 없음) 행 0. Part 2도 #N 신설 없음. 레시피 §7은 «검사기 규칙 번호 신설 시»로 한정돼 있어 정합 | `spec_lint.py:8-18` · `ontology_structural_check.py:75-80` |
| 4-vi | manifest 봉인 대상 | **MINOR(§1.4 누락 표기)** — Part 1이 `plugin_payload`(`dddjango/skills/**/*.md`·codex md)·`packs`(rulepack.json)·`graph`(`ontology/**/*`) 3그룹, Part 2가 `scorer`(`check-*.py`) → 봉인 draft는 두 파트 뒤 1회(통합 ④에 있음·§1.4엔 없음) | `manifest_seal.py:55-125` |
| 4-vii | 기타 계획 누락 | **MINOR** — `workspace/design/ontology-adoption-map.html` 갱신(사용자 상시 지침) · 검수표 위치 · `make rulepack`이 codex `codex-dddjango/skills/dddjango/scripts/rulepack.json`도 씀(MIRROR_OUT — 별도 rsync 불요, 계획 «rulepack» 1행이면 족함) | `ontology_rulepack.py:37-39` |

## (2) 문면 수정안 (초안 대비 diff)

### b3 «핵심 원칙» 불릿

```diff
-- 자기 검증은 **값의 불변식만** 검사한다 — 선언 타입의 재검사·강제 변환은 두지 않는다(타입은 시그니처가 약속하고 타입 체커가 지킨다). 타입 체커가 통과시키는 값(`bool`⊂`int`·`int`→`float`)의 거부는 값 검사에 속한다. `object`/`Any`/JSON 입력의 타입 좁히기는 값 객체를 부르기 **전**에 경계(역직렬화·스냅숏 복원·폼 `cleaned_data`)가 담당한다.
+- 자기 검증은 **값의 불변식만** 검사한다 — 선언 타입의 재검사·강제 변환은 두지 않는다(타입은 시그니처가 약속하고 테스트·타입 체커가 지킨다). 타입 체커가 통과시키지만 도메인 값 집합 밖인 값(`bool`⊂`int`)의 거부는 값 검사다; `int`→`float` 승격은 시그니처 계약의 일부라 거부하지 않는다 — 표현·정밀도가 규칙이면 시그니처의 타입을 바꾼다. `object`/`Any`/JSON 입력의 타입 좁히기는 값 객체를 부르기 **전**에 어댑터 경계(역직렬화·Data Mapper 복원·요청 Schema·폼 `cleaned_data`)가 담당한다.
```

변경 사유: ① «테스트·» — #69/R-1098 문면 정렬(2-a) ② int→float 자기 모순 해소(MAJOR-1) ③ «스냅숏 복원»→코퍼스 어휘(2-b). MAJOR-1 은 사용자 결정 — 초안 유지 시엔 최소한 «시그니처를 `float`로 둔 계약과 충돌함을 안다»(rv1 A)를 병기해야 모순이 은폐되지 않는다.

### Work·wiring

```diff
-R-3442 Obligation «값 객체 자기 검증은 값 불변식만 — 타입 좁히기는 경계 소유»
-  enforcedBy check-public-surface-annotation.py · delegatedTo agent-discipline-reviewer
+(권고 — 같은 블록 R-0495/R-0496 판형) 
+R-3442 Obligation «값 객체 자기 검증은 값 불변식만(타입 체커가 통과시키는 도메인 밖 값의 거부 포함) — 타입 좁히기는 어댑터 경계 소유»
+  delegatedTo agent-discipline-reviewer
+R-3443 Prohibition «값 객체의 선언 타입 재검사·강제 변환 금지»
+  enforcedBy check-public-surface-annotation.py(#69 ⓓ 부분 커버 — 검수표 명기) · delegatedTo agent-discipline-reviewer
+(단일 유지 시) R-3442 prefLabel «값 객체 자기 검증은 값 불변식만 — 선언 타입 재검사·강제 변환 금지 · 타입 좁히기는 어댑터 경계 소유» + 위 두 간선
```

### b4 코드 블록

```diff
     def __post_init__(self) -> None:
-        """자기 검증 (Self-Validation): 값의 불변식만 강제한다 — 타입은 시그니처가 약속하고 타입 체커가 지킨다"""
-        if type(self.amount) is bool:  # bool 은 int 의 하위 타입이라 타입 체커가 통과시킨다 — 값 검사에 속한다
+        """자기 검증 (Self-Validation): 값의 불변식만 강제한다 — 타입 좁히기는 경계 소유(§3.1 핵심 원칙)"""
+        if type(self.amount) is bool:  # bool 은 int 의 하위 타입 — isinstance(x, int) 도 타입 체커도 통과시킨다 · 값 검사
             raise ValueError(f"금액은 정수여야 합니다: {self.amount!r}")
```
(나머지 초안 그대로 — `object.__setattr__` 2행 삭제 · `PhoneNumber.__post_init__(self) -> None` · add/subtract/multiply/Address 불변.)

### Part 2 검사기 docstring 병기

```diff
-로컬 중간 base(`class _Base(StrEnum)` → `class X(_Base)`)의 전이 면제는 하지 않는다(기존과 동일) · Attribute base는 receiver 무검사
+검출 한계(오탐 가능 형상 — 면제 규칙이 아니다): 로컬 중간 base(`class _Base(StrEnum)` → `class X(_Base)`)와 선언적 이름으로 별칭한 중간 base(`from base import TimestampedModel as Model`)는 비선언으로 판정 · Attribute base는 receiver 무검사(`x.Model`의 attr만 대조). Name base는 import 바인딩(asname→원명)으로 해소한다.
```

### Part 2 §2.3·§2.4 문면

```diff
-오차단 0: 선언적 base를 alias로 들여온 실코드가 오탐이던 것이 green이 되는 것뿐
+오차단 0(census·픽스처 한정): … 단 «중간 선언적 base를 선언적 이름으로 별칭»한 형상은 수리 후 red(전엔 우연 green) — 중간-base 사각과 같은 분류(docstring 병기)
-`fixture_matrix.py:111` `("bad_rules", 2)` → 3으로 갱신
+`workspace/tools/fixture_matrix.py:111`의 `("bad_rules", 2)`는 기대 exit(불변). 건수는 `findings_count_matrix.py:130` EXPECTED(#493×7→×8·findings 11→12·sha 3열) 재실측 — 새 bad_rules 픽스처가 census 대상이므로 필변
```

## (3) 건드리는 IRI·파일 전수 (★ = 계획 누락/오기)

### Part 1 — A

| 구분 | IRI / 파일 | 조치 | 계획 |
|---|---|---|---|
| 정본 | `<djr#s/…/architecture-ddd/references/final.md/s016-3.1/b3>` `djr:text` + `djr:statesNorm` +R-3442(+R-3443) | rdflib 편집 + canon 재직렬화 | ✓ |
| 정본 | `…/s016-3.1/b4` `djr:text`(kind-code · 리비전 없음) | 리터럴 교체 | ✓ |
| 정본 | `djr:R-3442`(a Obligation · prefLabel@ko · currentExpression) + `<djr#R-3442@2026-09-03>`(revision 1) [+R-3443 Prohibition] | 신설 | ✓(분할은 권고) |
| 대장 | `ontology/ISSUED` append `R-3442\t2026-09-03\trules/architecture-ddd-final.ttl` | append-only | ✓ |
| wiring | `ontology/wiring/architecture-ddd-final.ttl` — `djr:R-3442 djr:delegatedTo <…a/agent-discipline-reviewer> ; djr:enforcedBy <…c/check-public-surface-annotation.py>` | canon 정렬 | ✓(파일명 미기재 → 명시) |
| 검수표 ★ | §13 문장→Work 대응 · §16 enforcedBy 4원 근거(«#69 ⓓ 부분 커버») | 계획 §1.2 또는 LEDGER note에 기록 | ★ 위치 미지정 |
| 렌더 | `dddjango/skills/architecture-ddd/references/final.md:473-548` | `ontology_render.py --apply architecture-ddd-final` | ✓ |
| 원장 | `ontology/LEDGER.tsv` `architecture-ddd-final\ts016-3.1\t<sha256(span−marker)>\tgraph\t-\t-\t-\t-\trebaseline:2026-09-03 …` | append | ✓(sha 산식 명시 권고) |
| 계수 | `workspace/eval/fixtures/ontology_gate/target-counts.json` NormShape+1 · **WorkShape+1** · ExpressionShape+1 | 편집 | ★ WorkShape 누락 |
| 골든 | `workspace/eval/fixtures/rulepack/query-golden.json` q4 3441→3442 | `query_golden_check.py --emit` | ✓(경로 미기재) |
| 소성물 | `dddjango/scripts/rulepack.json` + `codex-dddjango/skills/dddjango/scripts/rulepack.json`(MIRROR_OUT 자동) | `make rulepack` | ✓ |
| 소스 미러 | `workspace/reference/architecture-ddd/reference/final.md:481-554` span → 새 span(마커 없음) | 손교체(LEDGER append와 동시) → `corpus_mirror_sync --write` | ✓ |
| byte 미러 | `codex-dddjango/skills/dddjango-architecture-ddd/references/final.md` | `--write`(복사) | ✓ |
| 봉인 ★ | manifest 그룹 plugin_payload·packs·graph | draft(Part 2 뒤 1회) | ★ §1.4 미기재(통합 ④엔 있음) |
| 조감도 ★ | `workspace/design/ontology-adoption-map.html` | 갱신(사용자 상시 지침) | ★ 누락 |
| 무접촉 | Coordinator·agents 7·architecture-ddd `SKILL.md`·codex SKILL 의미 미러·검사기 27종·spec_lint·rule-owner-map·귀속 매핑표·`s030-4.2/b2` Money | — | ✓ |

### Part 2 — C′

| 구분 | 파일 | 조치 | 계획 |
|---|---|---|---|
| 검사기 | `dddjango/scripts/check-public-surface-annotation.py:127-143`(+`_import_bindings` 신설·docstring 병기) | 함수 단위 | ✓ (부기: `_record_syntax_bindings` :170-180의 `asname or name` 집합은 방향이 반대(바인딩 이름 집합)라 재사용 불가 — 리뷰 A 중복 지적 예방용 명시) |
| byte 미러 | `codex-dddjango/skills/dddjango/scripts/check-public-surface-annotation.py` | rsync | ✓ |
| 픽스처 | `workspace/eval/fixtures/public_surface/good/application/orders/domain_layer/shared_value_object/…`(신규 domain_layer) · `bad_rules/…/aliased_shadow.py` | 추가 | ✓ |
| 매트릭스 ★ | `workspace/tools/fixture_matrix.py:111` — **불변**(기대 exit 2) | — | ★ «→3» 오기(MAJOR-2) |
| 계수 ★ | `workspace/tools/findings_count_matrix.py:130` EXPECTED — **필변**(#493×8·12건·sha×3) | 재실측 | ★ «불변 가능» 분기 오류 |
| 봉인 | scorer 그룹(`check-*.py`) | draft | ✓ |
| 무접촉 | R-3154·R-3151·Coordinator :133·rulepack(#493 alias 부재)·design_pregate b35(`from enum import StrEnum` plain 렌더) | — | ✓ |

## (4) 10줄 요약

1. R-3442 신설은 저작 규약상 적법(§13 statesNorm 다중·§5 채번 R-3442·NormShape sh:or) — 단 같은 블록 b3의 선례가 «불변 (setter 금지)» 한 불릿을 R-0495 Obligation+R-0496 Prohibition으로 갈랐으므로, «재검사·강제 변환 금지»는 R-3443 Prohibition 분할이 정합(단일 Obligation도 R-3154 선례로 허용 — 택일).
2. 중복 아님: cleancode R-1504~1507·impl-python R-2752~2762·R-3158·R-1066/R-1098·#69 전수 대조 — «값 객체는 선언 타입을 재검사·강제 변환하지 않는다»는 스킬 층 성문 0 → amendment/restates 대상 IRI 없음, 신설 정당.
3. enforcedBy #69(ⓓ)는 R-1066/R-1098·R-0494(#268) 선례로 인정되나 «부분 커버(isinstance+raise 형만·exit 불산입)»를 검수표에 명기하고 delegatedTo discipline-reviewer를 주 채널로; docstring-only 대안은 R-3156(«코드 예시는 적용 대상 밖»)에 의해 비규범이라 기각.
4. **MAJOR-1(문면 내부 모순)**: «`int`→`float` 거부는 값 검사」는 «타입은 시그니처가 약속한다»와 충돌(PEP 484 수치 탑 — 시그니처 `float`가 int 수용을 약속) · rv1 A 처방 3의 반대를 사유 없이 채택 → `bool`⊂`int`만 값 검사로 두고 int→float는 거부하지 않는 문면으로(diff 제시).
5. 2-a·2-b 무충돌: 코퍼스 전제 R-3163(표준 도구셋 mypy strict)·R-3158, R-0579/R-0594 어댑터 입력 검증, R-2752/2755 pydantic 경계, django-web `cleaned_data`→command 예제와 동방향 — MINOR: «테스트·타입 체커»(#69 문면)·«스냅숏 복원»→«Data Mapper 복원·요청 Schema» 어휘 정렬.
6. Part 2 규범 무변경 성립: R-3154는 의미 층(alias가 멤버 의미를 바꾸지 않음) → 검사기 수리가 문면 쪽으로 수렴 · Coordinator :133 불변 · rulepack에 #493/#69 alias 항목 없음(변경 0) · alias 금지 규범 0. docstring 병기는 «면제 규칙»이 아니라 «검출 한계(오탐 가능 형상)»로 문구 수정.
7. **MAJOR-2(계획 오류)**: §2.4 «`fixture_matrix.py:111` `("bad_rules", 2)`→3»의 2는 기대 **exit 코드**(3=재료 결손) — 불변. 건수는 `findings_count_matrix.py:130` EXPECTED(#493×7→8·11→12·sha×3)이며 새 픽스처가 census 그 자체라 «불변 가능» 분기는 성립 안 함.
8. 소스 미러 손교체는 실제 필요(실측: sha256(렌더 span−marker)=sha256(소스 span)=LEDGER 유효 행) — LEDGER append와 소스 span 교체를 같은 단계에서(어긋나면 corpus_mirror_sync exit 3). codex byte 미러 경로·md5·검사기 cmp 모두 실존·동일.
9. 계수·골든: target-counts NormShape+1·**WorkShape+1(계획 누락)**·ExpressionShape+1(분할 시 각 +2) · q4 골든 `fixtures/rulepack/query-golden.json` 3441→3442 · spec_lint/rule-owner-map/귀속 매핑표는 #N 대장이라 R-work 신설엔 불요(정합).
10. 계획 누락 3: 봉인 draft가 §1.4에 없음(Part 1도 plugin_payload·packs·graph 3그룹 접촉 — 통합 ④ 1회면 족함) · 검수표(§13·§16) 기록 위치 · `ontology-adoption-map.html` 갱신(사용자 상시 지침). `make rulepack`은 codex rulepack도 씀(별도 복사 불요).
