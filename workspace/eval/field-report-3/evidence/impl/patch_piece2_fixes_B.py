"""⑤-2 정정(B 축 · 문서) — MAJOR-1 predicates #648/#649 · MINOR-2/3 spec #63 행·#648 셀 · MINOR-5 DEVELOPMENT.md·루브릭 · MINOR-4 회신 3 문면.
실행: cd /Users/hyun/Desktop/dddjango && python3 <this>
"""
import pathlib


def rep(p: pathlib.Path, old: str, new: str, n: int = 1) -> None:
    s = p.read_text(encoding="utf-8"); assert s.count(old) == n, (p.name, s.count(old), old[:70]); p.write_text(s.replace(old, new), encoding="utf-8")


# MAJOR-1 · predicates #648·#649(#650 행 뒤 · ast 확정 술어 · 파이프 0)
pred = pathlib.Path("workspace/design/2026-08-11-predicates.md"); t = pred.read_text(encoding="utf-8")
a = t.index("| 650 | ast+ |"); e = t.index("\n", a) + 1
rows = ("| 648 | ast | 확정 ⑴표준 트리 슬라이스 대상(api/** 전 파일 + OHS `*_service.py` · 프로필 무관) 함수의 반환 애너테이션을 평탄화(파이프 union·`Optional`·`Union`·문자열 주석 재파싱)한 구성원 중 `Status[…]`(origin `ninja.Status`/`ninja.responses.Status` — 모듈 import 바인딩으로 dotted 해소)가 2개 이상이면 위반 — `check-api-error-controller-contract` 가 def 줄 좌표로 방출(overlap 억제 비대상 · `-> Status[Out 과 Err 의 union]` 또는 `-> Out 과 Status[Err] 의 union` 은 통과) |\n"
        "| 649 | ast | 확정 ⑴ClassDef 기저에 ninja `Schema`(origin `ninja.Schema`/`ninja.schema.Schema`)와 pydantic `RootModel`(`pydantic.RootModel`/`pydantic.root_model.RootModel`)이 함께 있으면 위반 — 파일 한정 없음(트리 슬라이스 대상 파일 전부) · class 줄 좌표 · `RootModel[Annotated[…, Field(discriminator=…)]]` 단독 상속은 통과 |\n")
assert "| 648 | ast |" not in t; pred.write_text(t[:e] + rows + t[e:], encoding="utf-8"); print("predicates: #648·#649 +2")

# MINOR-2 · spec #63 행 — 규칙 문장 원복 + 08-25 span(09-01 span 앞)
spec = pathlib.Path("workspace/design/2026-08-08-tree-revision-spec.md")
rep(spec, "| 63 | 오류 응답은 operation 이 response={status: 그 status 에서 실제 반환하는 오류 타입 그대로(concrete·Union·명시값 base — base 뭉뚱그림 금지 · 2026-08-25 R-0681 rev2/R-0087 rev2)} 로 직접 선언하고 openapi_extra 보충·get_openapi_schema override·monkeypatch·postprocessor 로 사후 변형하지 않는다. <span>09-01",
    "| 63 | 오류 응답은 operation 이 response={status: <Bc>ErrorSchema} 로 직접 선언하고 openapi_extra 보충·get_openapi_schema override·monkeypatch·postprocessor 로 사후 변형하지 않는다. <span>2026-08-25 · **base 뭉뚱그림 금지** — `response=` 값은 그 status 에서 실제 반환하는 오류 타입 그대로(concrete 하나=그 concrete · 둘 이상=`Union` · 명시값 base=base)다(R-0681 rev2·R-0087 rev2 · 검사기 docstring·조치 문면은 09-04 S-5 에서 정합).</span> <span>09-01")
print("spec: #63 행 원복 + 08-25 span")
# MINOR-3 · #648 셀
rep(spec, "성공·오류 union 을 한 `Status[…]` 안에 넣거나(`Status[Out, Err 의 union]`) `Out` 과 `Status[Err]` 의 union 으로 쓴다.",
    "성공·오류 union 을 한 `Status[…]` 안에 넣거나(`Status[…]` 하나 안에 `Out` 과 `Err` 의 union) `Out` 과 `Status[Err]` 의 union 으로 쓴다.")
print("spec: #648 셀")

# MINOR-5 · DEVELOPMENT.md :81 뒤 1문장 · 루브릭 정정 커밋 해시
dev = pathlib.Path("docs/DEVELOPMENT.md"); d = dev.read_text(encoding="utf-8").split("\n")
line81 = d[80]; print("DEVELOPMENT.md:81 =", line81[:100])
d.insert(81, "- **봉인은 커밋 직전 마지막 단계다** — `make verify` 가 RED 여서 봉인 대상(측정 도구·byte 골든 EXPECTED·매트릭스)을 다시 고쳤으면 `manifest_seal.py --write` 를 다시 발행하고 `make verify` 를 처음부터 다시 돈다. 커밋 메시지·기록의 verify 수치는 **마지막 실행 로그**(evidence 경로 병기)의 것만 적는다 — 중간 실행의 green 을 옮겨 적지 않는다(2026-09-04 `d701df8` «verify 6/6» 거짓 표기 · 정정 `cad221b`).")
dev.write_text("\n".join(d), encoding="utf-8"); print("DEVELOPMENT.md +1")
rep(pathlib.Path("workspace/plan/2026-09-04-field-report-repair-3-rubric.md"),
    "봉인 재발행 뒤 **3차 verify 6/6 green**(`evidence/impl/verify4.log`) · 정정 커밋 = 이 문단의 커밋(봉인 manifest·기록·루브릭).",
    "봉인 재발행 뒤 **3차 verify 6/6 green**(`evidence/impl/verify4.log`) · 정정 커밋 = `cad221b`(봉인 manifest·기록·루브릭).")
print("rubric: cad221b")

# MINOR-4 · 회신 3 문면
r3 = pathlib.Path("workspace/plan/2026-09-04-field-report-reply-3.md")
rep(r3, "`application/`·`framework/` 루트만 · 앵커 격리 전 전량).", "`application/`·`framework/` 루트만 · registry_gate 앵커 차분 전 전량).")
rep(r3, "앵커 격리(N∖L)라 손대기 전까진 exit 에 안 들어가고, 손대면(클래스 개명·기저 교체) 그 자리가 귀속된다.",
    "registry_gate 앵커 차분에서 legacy(L∩N · exit 불산입·보고만)라 손대기 전까진 exit 에 안 들어가고, 손대면(클래스 개명·기저 교체) 그 자리가 귀속(N∖L)된다.")
rep(r3, "전부 앵커 격리 — 새 레인 산출물만 막힌다.", "전부 legacy(앵커 차분 · exit 불산입) — 새 레인 산출물만 막힌다.")
rep(r3, "⑥ **오류 응답을 `response=` 에 선언한 컨트롤러의 G2 는 `dddjango-code-json` 프로필로 돌린다** — `auto` 는 #63·#125 를 재운다(리딩 레인 «0건»의 원인). Coordinator 문면(R-0331 rev2)이 이제 «승인 12-slot 없이 오류 status 를 선언했으면 auto 금지 · G1 반송» 으로 못 박았다.",
    "⑥ **오류 응답을 `response=` 에 선언한 컨트롤러의 G2 는 승인 12-slot 의 profile 로 돌린다**(spring 신규 Ninja 표면이면 `dddjango-code-json`) — `auto` 는 #63·#125 를 재운다(리딩 레인 «0건»의 원인). Coordinator 문면(R-0331 rev2)이 이제 «승인 12-slot 없이 오류 status 를 선언했으면 auto 금지 · G1 반송(error profile 미결정)» 으로 못 박았다.")
rep(r3, "| N-1 | notification `obj is None` 재검사 | 기존 규범(R-3443)의 admin 변종 — 새 항목 아님 |",
    "| N-1 | notification `obj is None` 재검사 | R-3443(값 객체 안 선언 타입 재검사 금지) 취지의 admin 변종 — 규범 확장 없음 · 새 항목 아님 |")
rep(r3, "+ 결정표 6행 R-3451~R-3457 ·", "+ §4 레코드 규범 R-3451 + 결정표 6행 R-3452~R-3457 ·")
rep(r3, "1288e4a 에서 붙인 주석은 허용(스텁 타입과 같으면)이되 필수가 아니다.", "1288e4a 에서 붙인 주석은 허용(스텁 타입과 같고 그 타입에 `Any` 가 없을 때 — `inlines` 는 달 수 없다)이되 필수가 아니다.")
rep(r3, "⑦ S-5 legacy: 상자 둘 spring 7 함수(accounts 6 · fortune_record 1) · kkebi 6(identity 2 · review 2 · saju 2) → #648 · kkebi `response=` base 선언 31자리(identity 16 · saju 9 · review 5 · image 1) → code-json 으로 돌리면 #63. 전부 앵커 격리.",
    "⑦ S-5 legacy: 상자 둘 spring 7 함수(accounts 6 · fortune_record 1) · kkebi 6(identity 2 · review 2 · saju 2) → #648 · kkebi `response=` base 선언 31자리(identity 16 · saju 9 · review 5 · image 1) → code-json 으로 돌리면 #63. 전부 legacy(앵커 차분 · exit 불산입).")
print("reply 3: MINOR-4 문면 7곳")
