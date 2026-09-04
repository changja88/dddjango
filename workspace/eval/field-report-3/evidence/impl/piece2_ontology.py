"""조각 2 온톨로지 편집 — S-5 + ⓔ1 (rv1-B §3.10~§3.12 · rv3-B §3-5·§3-7·§3-8(B안)·§3-9·§3-10).
HEAD ttl 을 다시 읽는다(조각 1 문안 보존). 실행: cd /Users/hyun/Desktop/dddjango && .venv/bin/python <this>
"""
import sys
sys.path.insert(0, "/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/d31bf8ef-f45e-4609-badc-3add1039bdb0/scratchpad/fr3/impl")
import ontlib as L
from ontlib import DJR, RDF, URIRef, Literal, S
if "--date" in sys.argv: L.DATE = sys.argv[sys.argv.index("--date") + 1]

def new_block(g, sec, n, text, norms=(), kind="norm"):
    b = URIRef(str(sec) + f"/b{n}"); assert (b, None, None) not in g, b
    prev = URIRef(str(sec) + f"/b{n-1}"); assert (prev, DJR.order, Literal(n - 1)) in g, ("order 불연속", b)
    g.add((b, RDF.type, DJR.Block)); g.add((b, DJR.inSection, sec)); g.add((b, DJR.kind, DJR["kind-" + kind])); g.add((b, DJR.order, Literal(n)))
    for r in norms: g.add((b, DJR.statesNorm, DJR[r]))
    g.add((b, DJR.text, Literal(text) if kind in ("table-row", "code") else Literal(text, lang="ko")))
    return b

# ═══ 1. implementation-django-ninja-final ═══════════════════════════════════
p, g = L.load("rules/implementation-django-ninja-final.ttl")
NF = "dddjango/skills/implementation-django-ninja/references/final.md"
b13 = S(NF + "/s009-2.2/b13"); b1 = S(NF + "/s009-2.2/b1"); sec31 = S(NF + "/s012-3.1")
assert list(g.objects(b13, DJR.statesNorm)) == [DJR["R-0687"]]
L.new_work(g, "R-3463", "Prohibition", "컨트롤러 반환 주석의 Status 상자는 하나 — Status[A] | Status[B](상자 둘) 금지(Status[T] 불변 · concrete 직접 반환이 mypy strict [return-value] · 값 변수를 base 로 주석해 통과시킨 형태도 같은 금지) · -> Status[Out | Err] 또는 -> Out | Status[Err](#648)")
L.set_text(g, b13, "- **반환 타입을 명시한다** — `-> object`처럼 정보 없는 타입을 쓰지 않는다. 직렬화 자체는 `response=`가 결정하지만, 반환 타입 annotation은 사람·mypy를 위한 계약 표현이다. 직접 반환하는 성공 Schema와 BC `ErrorSchema`/`Status`를 실제 흐름에 맞게 표현한다. **반환 주석의 `Status` 상자는 하나다** — `-> Status[Out | ErrA | ErrB]`(성공·오류 union 을 한 `Status` 안에) 또는 `-> Out | Status[Err]`. `Status[A] | Status[B]`(상자 둘)는 쓰지 않는다: `Status[T]` 의 `T` 는 불변이라 concrete 값을 직접 넣는 순간 mypy strict 가 `[return-value]` 로 막히고, 값 변수를 base 로 주석해 통과시킨 형태도 같은 금지다 — 형태 자체를 금지한다(#648).\n")
g.add((b13, DJR.statesNorm, DJR["R-3463"]))
L.new_work(g, "R-3465", "Prohibition", "한 status 의 성공 본문이 둘 이상의 모양이면 response={200: A | B} 익명 union 을 적지 않는다 — 이름 붙은 컴포넌트·discriminator 상실(architecture-api §5.2) · §3.1 의 RootModel 하나를 선언")
L.set_text(g, b1, "\nDjango Ninja operation은 decorator의 HTTP method, path, response 선언,\noperation 함수의 typed parameters로 API contract를 만든다. 여러 status code가\n가능한 경우 `response={status: Schema}` 형태로 성공/오류 schema를 분리한다. 한 status 의\n성공 본문이 둘 이상의 모양이면 `response={200: A | B}` 익명 union 을 적지 않는다 — 이름 붙은\n컴포넌트와 discriminator 를 잃어 계약이 바뀐다(`architecture-api` §5.2) · §3.1 의 `RootModel` 하나를 선언한다.\n\n")
g.add((b1, DJR.statesNorm, DJR["R-3465"]))
L.new_work(g, "R-3464", "Obligation", "성공 응답이 판별 키로 갈리는 union 이면 이름 붙은 RootModel 하나로 선언 — class X(RootModel[Annotated[A | B, Field(discriminator=…)]]) · ninja Schema 병행 상속 금지(메타클래스 충돌 · #649) · 판별 키 규율은 발행 봉투와 같음 · OpenAPI oneOf+discriminator 컴포넌트 하나")
new_block(g, sec31, 9, "- **성공 응답이 판별 키로 갈리는 union 이면 이름 붙은 `RootModel` 하나로 선언한다** — `class XResponseSchema(RootModel[Annotated[A | B, Field(discriminator=\"kind\")]])`. ninja `Schema` 를 함께 상속하지 않는다(`ResolverMetaclass` 와 pydantic `RootModel` 메타클래스 충돌 — mypy `[metaclass]`·`[call-arg] root` · #649). 판별 키의 선언 규율은 위 발행 봉투 불릿과 같다(domain `StrEnum` 파생 `Literal`). OpenAPI 에는 `oneOf` + `discriminator` 를 가진 컴포넌트 하나로 렌더된다(실증: `TarotCardOut(RootModel[Annotated[TarotMajorCardOut | TarotMinorCardOut, Field(discriminator=\"type\")]])` · e2e 가 `oneOf` 2 + `discriminator.propertyName` 을 단언).\n\n", ["R-3464"])
L.save(p, g); print("implementation-django-ninja-final ok")

# ═══ 2. implementation-django-ninja-skill — s004/b12 확장(B안) ═══════════════
p, g = L.load("rules/implementation-django-ninja-skill.ttl")
NS = "dddjango/skills/implementation-django-ninja/SKILL.md"
b12 = S(NS + "/s004/b12")
assert L.text_of(g, b12) == "- operation은 `summary`·`description`·`tags`로 문서화하고 반환 타입을 명시한다(`object` 금지) (§2.2)\n"
L.new_work(g, "R-3466", "Obligation", "SKILL 요약 — 반환 주석의 Status 는 하나(-> Status[Out | Err]) · 성공 union 은 이름 붙은 RootModel 하나(Schema 병행·response={200: A | B} 금지)(§2.2·§3.1 재진술)")
L.set_text(g, b12, "- operation은 `summary`·`description`·`tags`로 문서화하고 반환 타입을 명시한다(`object` 금지) — 반환 주석의 `Status` 는 하나(`-> Status[Out | Err]`) · 성공 union 은 이름 붙은 `RootModel` 하나(`Schema` 병행·`response={200: A | B}` 금지) (§2.2·§3.1)\n")
g.add((b12, DJR.statesNorm, DJR["R-3466"]))
for tgt in ("s009-2.2/b1", "s012-3.1/b9"):
    g.add((b12, DJR.restates, S(NF + "/" + tgt)))
L.save(p, g); print("implementation-django-ninja-skill ok")

# ═══ 3. architecture-api-final — s022-5.2 새 b7 ═════════════════════════════
p, g = L.load("rules/architecture-api-final.ttl")
AF = "dddjango/skills/architecture-api/references/final.md"
b6 = S(AF + "/s022-5.2/b6")
assert L.text_of(g, b6).endswith("응답 계약에 포함한다\n\n")
L.set_text(g, b6, L.text_of(g, b6)[:-1])
L.new_work(g, "R-3467", "Obligation", "한 상태 코드의 성공 본문이 둘 이상의 모양이면 판별 필드(discriminator)를 가진 이름 붙은 schema 하나(oneOf+discriminator)로 계약 — 익명 anyOf 금지 · 오류 union 은 고정 code 로 자기 판별되므로 대상 아님")
new_block(g, S(AF + "/s022-5.2"), 7, "- 한 상태 코드의 성공 본문이 둘 이상의 모양이면 판별 필드(discriminator)를 가진 **이름 붙은 schema 하나**(`oneOf` + `discriminator`)로 계약한다 — 익명 `anyOf` 는 클라이언트가 분기할 이름과 판별 키를 잃는다. 오류 본문의 union 은 각 오류 schema 가 고정 `code` 로 자기 판별되므로 이 요구의 대상이 아니다(§6 에러 프로필)\n\n", ["R-3467"])
L.save(p, g); print("architecture-api-final ok")

# ═══ 4. command-dddjango — b32 R-0349 rev2 · b16 R-0331 rev2 ═════════════════
p, g = L.load("rules/command-dddjango.ttl")
CM = "dddjango/commands/dddjango.md"
L.replace_in(g, S(CM + "/s007/b32"), "표준 트리 슬라이스(#120~#132·#474·#62 — 프로필 무관 선행).", "표준 트리 슬라이스(#120~#132·#474·#62·#648 반환 주석 `Status` 상자 하나·#649 `Schema`+`RootModel` 동시 상속 금지 — 프로필 무관 선행).")
L.revise(g, "R-0349", "registry #15 — narrow try·concrete same-BC catch·direct BC-base ErrorSchema·two-argument Status + 표준 트리 슬라이스(#120~#132·#474·#62 · #648 Status 상자 하나·#649 Schema+RootModel 동시 상속 금지)", "amendment")
L.replace_in(g, S(CM + "/s007/b16"), "`auto` 결과는 `Error response contract 12-slot` 증거가 아니라고 보고한다.", "`auto` 결과는 `Error response contract 12-slot` 증거가 아니라고 보고한다. **«무관»의 판정은 코드 모양이 아니라 승인 12-slot 유무다 — 단 승인 12-slot 없이 이번 산출물의 컨트롤러가 BC 오류 status 를 `response=` 에 선언했으면 `auto` 로 돌리지 않고 G1 반송(`STOP_FOR_USER_APPROVAL` — error profile 미결정 · design-architect «Error response contract 12-slot» 의 적용 조건)이다: `auto` 는 #63·#125 등 code-profile 규칙을 재우므로 오류 응답을 선언한 표면의 G2 증거가 될 수 없다.**")
L.revise(g, "R-0331", "Error response G2 는 승인된 code/preserve scope 마다 command 를 각각 렌더·실행 · «무관» = 승인 12-slot 유무 — 12-slot 없이 BC 오류 status 를 선언한 산출물은 auto 금지·G1 반송", "amendment")
L.save(p, g); print("command-dddjango ok")

# ═══ 4b. ⑤-1 B 정정(in-place · Expression 신설 없음 · MINOR-2/3/4/5) ═══════════
p, g = L.load("rules/discipline-houserules-skill.ttl")
HS = "dddjango/skills/discipline-houserules/SKILL.md"
L.replace_in(g, S(HS + "/s007-4/b16"),
 "`ListView`·`DetailView`·`CreateView`·`UpdateView`·`DeleteView`·`FormView` 및 그 mixin(`View`·`TemplateView`·`RedirectView` 는 기본값이 있어 대상 밖).",
 "`ListView`·`DetailView`·`CreateView`·`UpdateView`·`DeleteView`·`FormView` 및 그 mixin, 그리고 `BaseFormSet`·`ModelChoiceField` 같은 폼셋·폼 필드 기저다(`View`·`TemplateView` 는 기본값이 있고 `RedirectView` 는 제네릭이 아니라 대상 밖 · 전수는 #646 집합 — django-stubs 6.1.0 기준).")
L.replace_in(g, S(HS + "/s007-4/b5"),
 "(적으면 스텁 선언과 같아야 한다 · 선언적 클래스 본문의 메서드는 면제가 아니다)",
 "(달 수 있는 자리라도 스텁 타입과 같아야 하고 그 타입에 `Any` 가 있으면(`inlines`) 달 수 없다 · 선언적 클래스 본문의 메서드는 면제가 아니다)")
L.save(p, g); print("houserules-skill ⑤-1 B 정정(b16·b5) ok")
p, g = L.load("rules/command-dddjango.ttl")
L.replace_in(g, S(CM + "/s007/b28"),
 "`json.load(s)` 무검증 흐름은 ⓓ #650 · 세 규칙은 `application/`·`framework/` 루트만)·Thin Read 반환(#358)·계약 검증 토큰(#456).\n",
 "`json.load(s)` 무검증 흐름은 ⓓ #650)·Thin Read 반환(#358)·계약 검증 토큰(#456) — 신규 3규칙(#646·#647·#650)은 `application/`·`framework/` 루트만.\n")
L.save(p, g); print("command b28 ⑤-1 B 정정(MINOR-4) ok")

# ═══ 5. wiring · ISSUED ═══════════════════════════════════════════════════════
DR, RA, AE = "a/agent-discipline-reviewer", "a/agent-design-review-api", "c/check-api-error-controller-contract.py"
L.wire("implementation-django-ninja-final.ttl", [("R-3463","delegatedTo",DR),("R-3463","enforcedBy",AE),("R-3464","delegatedTo",RA),("R-3464","enforcedBy",AE),("R-3465","delegatedTo",RA),("R-3465","delegatedTo",DR)])
L.wire("implementation-django-ninja-skill.ttl", [("R-3466","delegatedTo",RA),("R-3466","delegatedTo",DR)])
L.wire("architecture-api-final.ttl", [("R-3467","delegatedTo",RA)])
L.issued([("R-3463","rules/implementation-django-ninja-final.ttl"),("R-3464","rules/implementation-django-ninja-final.ttl"),("R-3465","rules/implementation-django-ninja-final.ttl"),("R-3466","rules/implementation-django-ninja-skill.ttl"),("R-3467","rules/architecture-api-final.ttl")])
print("piece2 ontology edit done — next: gate → render 4 docs(ninja-final · ninja-skill · api-final · command-dddjango)")
