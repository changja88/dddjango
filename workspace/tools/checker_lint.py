#!/usr/bin/env python3
"""검사기의 검사기 — `dddjango/scripts/check-*.py` 가 «검사기 규칙»(어겼을 때=검사기)을 지키는지 재는 린트.

spec_lint.py·corpus_mirror_sync.py 와 같은 부류(메인테이너/빌드타임)라 registry 밖이다.

담당 규칙 (rule-owner-map · 총 21):
  가드   #74 채택 신호가 참인데 대상 0건이면 exit 2 — 채택 신호를 참조하는 검사기는
             그 가드(If adopted … exit(2)/return 2)를 가져야 한다.
        #75 그 가드는 touched 필터 «앞» — 가드 줄이 touched 필터 첫 호출보다 뒤면 위반.
        #78 채택 신호 소스 둘 이상 — 층 폴더·django 마커·application 컨테이너·
             트리 데이터 네 계열 중 2개 미만 참조면 위반.
  이관종결 #73·#77 이중 수용은 2026-08-12 V1 걷기로 끝났다(LEGACY_ALIASES 자체가 없다).
        #76 쌍조건의 오른쪽 항(「검사기 옛 이름 리터럴 0」)을 ㉢ 가 상시 집행한다 —
             옛 층 이름 리터럴은 «검출 자리»(±3줄 창에 #규칙 인용)만 허용.
  면제금지 #591㉣ baseline·allowlist 파일 로드 금지 · #613(=#591㉠) `.git` 부재를 이유로
             exit 0 하는 조기 반환 금지 · ㉢(2026-08-12 켬) legacy·이중 수용·미이관 낱말과
             brownfield 면제 낱말 잔존 = 위반(preserve-established «프로필» 문맥만 허용).
  대상선정 #42(=#221 같은 술어) 접미사 검사는 «자리»가 정한다 — 포트 접미 검사기는
             exception.py·<data>_out/_in 제외 앵커를 가진다(#221 로 진단).
        #79 skeleton 은 repository 를 «파일»로 검사(`_repository.py` 앵커).
        #80 skeleton 필수 폴더에 BC 레벨 schema/ 금지.
        #99 결선 파일(api_router.py)은 잎 검사 대상이 아니다(제외 앵커).
        #204 응용 DTO 백스톱의 대상은 `_command·_query·_result` 전부(앵커 셋).
        #357 domain 미의존 검사는 domain_bypass_query 아래에만(#356 앵커).
        #327 admin 은 driven 화살표·잎 import 검사 스코프 밖 — 대상 층이 driving/domain
             으로 닫혀 있어 구조로 만족(경로 검사로 재확인: 잎 import 검사기가
             django_* 를 스캔 목록에 넣지 않는다 — 진단은 문서 확인 수준 · 진단 0).
  선행게이트 #487 제1원칙 게이트 표식 — rule-owner-map 의 「제1원칙 선행 게이트」 비고.
  파이프라인 #495 mypy 가 registry 문서에 «항상» 있다 · #496 그 호출에 tests 면제가 없다.
  관측    #602 broker 검사기가 실패 리스너 관측(#525·#602) 슬라이스를 가진다(앵커).
  후보    #54[ⓓ] 검사기 안 «주소 목록» 후보 — 경로꼴 문자열 상수가 트리 고정 이름 밖이면
             ⓓ 출력(「이 목록이 규칙인가 주소인가」 · exit 불산입).
  이관    #67 은 대상이 «타깃 코드»(DTO 의 raise)라 check-usecase-dto-placement 로 정정
             이관했다(#609 전례 — 키워드 «백스톱» 오배정). 여기서는 앵커만 확인한다.

메타 지침 (Q0 다섯 — 주어가 코드가 아니라 «판정·이행 절차»라 검사기를 두지 않는다.
  이 절이 그 문면의 자리다 — 검사기·규칙을 만지는 사람이 읽는다 · rule-owner-map
  «메타(6번 지침·checker_lint)» 소유):
  #72  이행 순서 — 규칙을 바꾸면 플러그인 셋(검사 스크립트·리뷰어 지침·표준 문서)을
       «한 커밋에서 먼저» 고치고, 코드(대상 저장소) 이동은 그 다음이다(D32).
       같은 문면이 discipline-houserules final.md §4 에 있다.
  #449 승격 판정에 「몇 개 BC 가 쓰나」를 넣지 않는다 — BC 가 하나여도 그 BC 것이
       아니면 처음부터 framework/ 에 만들고, 두 BC 가 같은 업무 규칙을 갖고 있어도
       각자 갖는다(D38 — 코드 쪽 귀결은 #372·#448 이 ast 로 진다).
  #452 창구 예외의 판정 축은 「이 창구가 «혼자서» 답을 만들 수 있나」 하나다 —
       「부르는 쪽이 그걸 받고 계속 하나」를 묻지 않는다(창구는 부르는 쪽을 모른다 ·
       D36 — 실물 위반은 #451 이 진다).
  #494 「자명하니까 면제」를 열지 않는다 — 조건을 하나라도 열면 「어디까지가
       자명한가」가 되돌아와 규칙이 무너진다(D58 — 코드 쪽 강제는 #493·#495·#496).
  #592 이관 미루기는 AskUserQuestion 으로 사용자 판단을 받아서만 — 「가만 있어도
       해로운」 위반(catch-all 등)은 못 미룬다. 이행 완료: commands/dddjango.md
       Phase 0(빚 스캔·G0 배너)이 상설이다(⑸ · 2026-08-11).

exit: 0=clean · 1=사용/분석 오류 · 2=위반
사용: python3 workspace/tools/checker_lint.py [--scripts-dir DIR]
"""
from __future__ import annotations

import argparse
import ast
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
DEFAULT_SCRIPTS = REPO / "dddjango" / "scripts"

SIGNAL_FAMILIES = {
    "layer-dirs": re.compile(r"driving_layer|application_layer|domain_layer|driven_layer|LAYER"),
    "django-marker": re.compile(r"django_|apps\.py|models\.py|DJANGO_APP_MARKERS|INSTALLED_APPS|MIDDLEWARE|settings"),
    "app-container": re.compile(r"rglob\(\s*[\"']application[\"']\s*\)|/\s*[\"']application[\"']|\bapplication\b 컨테이너"),
    "tree-data": re.compile(r"standard_tree|tree\.ROWS"),
}
TREE_FIXED_HINTS = {
    "driving_layer", "application_layer", "domain_layer", "driven_layer",
    "port", "adapter", "schema", "contract", "exception", "api", "webhook",
    "cron_job", "event_subscription", "open_host_service", "published_event", "composition_root",
    "framework", "pure", "broker", "test", "unit", "integration", "e2e", "factories",
    "fake", "entity", "value_object", "event", "domain_service", "shared_value_object",
    "repository", "unit_of_work", "domain_bypass_query", "persistence", "anticorruption_layer",
    "external_system", "models", "admin", "templates", "form", "feature", "settings",
    "migrations", "application", "internal", "external",
}


class Findings(list):
    def add(self, rule: str, where: str, msg: str) -> None:
        self.append(f"[{rule}] {where}: {msg}")


class Candidates(list):
    def add(self, rule: str, where: str, msg: str, question: str) -> None:
        self.append(f"[ⓓ{rule}] {where}: {msg} — 물음: {question}")


def _parse(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, SyntaxError):
        return None


def _exit2_in(node: ast.AST) -> bool:
    for n in ast.walk(node):
        if isinstance(n, ast.Call) and isinstance(n.func, ast.Attribute) and n.func.attr == "exit":
            if n.args and isinstance(n.args[0], ast.Constant) and n.args[0].value == 2:
                return True
        if isinstance(n, ast.Return) and isinstance(n.value, ast.Constant) and n.value.value == 2:
            return True
    return False


def _mentions_adopt(node: ast.AST) -> bool:
    for n in ast.walk(node):
        if isinstance(n, ast.Name) and "adopt" in n.id.lower():
            return True
        if isinstance(n, ast.Attribute) and "adopt" in n.attr.lower():
            return True
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and "adopt" in n.name.lower():
            return True
    return False


def _check_one(py: Path, text: str, mod: ast.Module, f: Findings, cand: Candidates) -> None:
    name = py.name
    # #78 — 채택 신호 소스 둘 이상. 문면은 «층 폴더 이름 문자열 하나로만 만들지 않는다» —
    # 층 이름을 아예 안 쓰는 검사기(예: choices 의 touched+모델 레지스트리)는 이 위험 밖이다.
    families = sum(1 for rx in SIGNAL_FAMILIES.values() if rx.search(text))
    if families < 2 and SIGNAL_FAMILIES["layer-dirs"].search(text):
        f.add("#78", name,
              f"채택 신호 계열이 {families}개 — 대상 목록을 층 폴더 이름 «하나»로만 만들지 않고 "
              "신호를 둘 이상 쓴다(층 폴더·django 마커·application 컨테이너·트리 데이터)")
    # #74 · #75 — 대상 0건 가드와 그 자리. 가드 모양 둘을 받는다:
    #   ㉠ If 조건이 채택 신호를 직접 본다  ㉡ 앞선 채택 게이트 뒤의 «0건 → exit 2» If
    #      (몸통 문자열에 #74 표식 — db-table·ctx·skeleton 의 확립된 모양).
    if "adopt" in text.lower():
        guard_line = None
        for n in ast.walk(mod):
            if not (isinstance(n, ast.If) and _exit2_in(n)):
                continue
            body_marks = any(
                isinstance(x, ast.Constant) and isinstance(x.value, str)
                and ("#74" in x.value or "0건" in x.value or "무동작" in x.value)
                for x in ast.walk(n))
            if _mentions_adopt(n.test) or body_marks:
                guard_line = n.lineno
                break
        if guard_line is None:
            f.add("#74", name,
                  "채택 신호는 참조하는데 «대상 0건 → exit 2» 가드(If adopted … exit(2))가 없다")
        else:
            touched_lines = [n.lineno for n in ast.walk(mod)
                             if isinstance(n, ast.Call) and (
                                 (isinstance(n.func, ast.Name) and "touched" in n.func.id.lower())
                                 or (isinstance(n.func, ast.Attribute) and "touched" in n.func.attr.lower()))]
            early = [ln for ln in touched_lines if ln < guard_line]
            if early:
                f.add("#75", name,
                      f"touched 필터(:{early[0]})가 0건 가드(:{guard_line})보다 앞에 있다 — "
                      "가드는 «경로로 대상 집합을 만든 직후·touched 필터 앞»이다")
    # #591㉣ — baseline·allowlist 파일 로드.
    for m in re.finditer(r"open\([^)]*(baseline|allowlist)[^)]*\)", text, re.IGNORECASE):
        f.add("#591", name,
              "baseline/allowlist 파일 로드 — brownfield 는 «면제»가 아니라 «아직 안 갚은 빚»이다")
    # #613(=#591㉠) — .git 부재를 이유로 통과.
    for m in re.finditer(r"\.git.{0,120}?(sys\.exit\(0\)|return 0)", text, re.DOTALL):
        window = m.group(0)
        if "notice" in window or "전 후보" in window or "전부" in window:
            continue  # 비-git → «전 후보 검사»(fail-closed) 전환 고지는 정상 모양이다.
        f.add("#613", name,
              "`.git` 부재를 이유로 exit 0 — 검사기는 그 이유로 검사를 건너뛰지 않는다(#591)")
    # #591㉢ · #76 — V1 걷기(2026-08-12 이관 종료) 이후 수용 기계 잔존 금지.
    #   옛 층 이름 리터럴은 «검출 자리»(±3줄 창에 #규칙 인용)만 허용한다(#76 오른쪽 항).
    #   preserve-established 는 프로필 «셀렉터·계약» 낱말이라 그 문맥만 허용한다.
    lines = text.splitlines()
    for i, line in enumerate(lines, 1):
        if re.search(r"LEGACY_ALIASES|LEGACY_LAYERS|이중 수용|미이관", line):
            f.add("#591", f"{name}:{i}", "V1 수용 기계의 낱말 잔존 — 이관 종료 후 위반이다(㉢)")
        elif re.search(r"legacy", line, re.IGNORECASE):
            f.add("#591", f"{name}:{i}", "`legacy` 갈래 잔존 — 이관 종료 후 위반이다(㉢)")
        elif re.search(r"brownfield", line) and "preserve-established" not in line:
            f.add("#591", f"{name}:{i}",
                  "`brownfield` 면제 낱말 — preserve-established 프로필 문맥 밖 사용 금지(㉢)")
        if re.search(r"presentation_layer|infra_layer|published_service", line):
            window2 = "\n".join(lines[max(0, i - 4): i + 3])
            if not re.search(r"#\d", window2):
                f.add("#76", f"{name}:{i}",
                      "옛 층 이름 리터럴 — 검출 자리(#규칙 인용 창) 밖이면 수용 잔존이다")
        # §4 개명 5종 중 나머지 둘(acl·루트 common)의 «수용 꼴» — 낱말 자체는 흔해
        # 오탐이 나므로 수용의 «모양»(별칭 나란히·후보 튜플)만 문다. 검출 자리는 같은 창 허용.
        if '"acl"' in line and "anticorruption_layer" in line:
            window2 = "\n".join(lines[max(0, i - 4): i + 3])
            if not re.search(r"#\d", window2):
                f.add("#76", f"{name}:{i}",
                      "옛 이름 `acl` 별칭 수용 꼴 — 검사기는 anticorruption_layer 하나만 안다(㉢)")
        if re.search(r'\(\s*"framework",\s*"common"\s*\)|\(\s*"common",\s*"framework"\s*\)', line):
            window2 = "\n".join(lines[max(0, i - 4): i + 3])
            if not re.search(r"#\d", window2):
                f.add("#76", f"{name}:{i}",
                      "루트 `common` 수용 튜플 — 이관 종료 후 framework 하나만 안다(㉢)")
    # ㉢ 낱말이 줄바꿈으로 갈라진 잔존(«이중\n수용» 류) — 줄 검사가 못 보는 꼴.
    squeezed = re.sub(r"\s+", "", text)
    for split_word, shown in (("이중수용", "이중 수용"), ("미이관", "미이관")):
        if split_word in squeezed and not re.search(shown, text):
            f.add("#591", name,
                  f"「{shown}」 낱말이 줄바꿈으로 갈라져 잔존 — 이관 종료 후 위반이다(㉢)")
    # #54[ⓓ] — 주소 목록 후보(경로꼴 문자열 상수가 트리 고정 이름 밖).
    for node in mod.body:
        if not isinstance(node, (ast.Assign, ast.AnnAssign)):
            continue
        value = node.value if isinstance(node, ast.Assign) else node.value
        if value is None:
            continue
        for n in ast.walk(value):
            if isinstance(n, ast.Constant) and isinstance(n.value, str):
                s = n.value
                if ("/" in s and s.strip("/").split("/")[0] not in TREE_FIXED_HINTS
                        and not s.startswith(("#", "—", "«", ".", "*"))
                        and re.fullmatch(r"[a-z0-9_/.]+", s or "") and len(s) > 3):
                    cand.add("#54", f"{name}:{n.lineno}",
                             f"경로꼴 문자열 상수 `{s}` 가 트리 고정 칸 밖이다",
                             "이 목록이 «규칙»인가 «주소»인가")


def _check_anchors(scripts: Path, f: Findings) -> None:
    def text_of(fname: str) -> str | None:
        p = scripts / fname
        try:
            return p.read_text(encoding="utf-8")
        except OSError:
            f.add("#487", fname, "검사기 파일이 없다 — registry 계약이 깨졌다")
            return None

    skel = text_of("check-layer-skeleton.py")
    if skel is not None:
        rows_driven = "standard_tree" in skel and re.search(r"\btree\.|ROWS", skel)
        if "_repository.py" not in skel and not rows_driven:
            # 트리 데이터(ROWS)가 <aggregate>_repository.py «파일» 행을 주므로
            # 데이터 구동이면 #79 는 구조로 만족된다.
            f.add("#79", "check-layer-skeleton.py",
                  "repository «파일» 앵커(`_repository.py`)가 없다 — 폴더가 아니라 파일로 검사한다")
        if re.search(r"REQUIRED[^=\n]*=[^\n]*[\"']schema[\"']", skel):
            f.add("#80", "check-layer-skeleton.py",
                  "필수 폴더 목록에 BC 레벨 schema/ — 이 트리에 그 칸은 존재 자체가 없다")
    comp = text_of("check-composition-root.py")
    evp = text_of("check-event-publish.py")
    if not any(t is not None and "api_router.py" in t for t in (comp, evp)):
        f.add("#99", "check-composition-root.py·check-event-publish.py",
              "결선 파일 제외 앵커(`api_router.py`)가 없다 — api_router 는 잎이 아니다")
    dto = text_of("check-usecase-dto-placement.py")
    if dto is not None:
        missing = [s for s in ("_command", "_query", "_result") if s not in dto]
        if missing:
            f.add("#204", "check-usecase-dto-placement.py",
                  f"응용 DTO 대상 앵커 {missing} 이 없다 — 대상은 세 접미 전부다")
        if "#67" not in dto:
            f.add("#67", "check-usecase-dto-placement.py",
                  "«응용 DTO 는 raise 하지 않는다» 슬라이스(#67)가 없다(이관 정정 반영 필요)")
    pap = text_of("check-port-adapter-pairing.py")
    if pap is not None:
        if "exception.py" not in pap or "_out" not in pap:
            f.add("#221", "check-port-adapter-pairing.py",
                  "접미사 검사의 «자리» 앵커(exception.py·<data>_out/_in 제외)가 없다(#42 같은 술어)")
        if "domain_bypass_query" not in pap or "#356" not in pap:
            f.add("#357", "check-port-adapter-pairing.py",
                  "domain 미의존 검사(#356)가 domain_bypass_query 스코프 앵커를 잃었다")
    broker = text_of("check-broker-contract.py")
    if broker is not None and "#602" not in broker:
        f.add("#602", "check-broker-contract.py",
              "실패 리스너 «기록이 가는 곳» 참조(#602)가 없다 — 삼킴 금지(#525)의 실효가 0이 된다")
    # #77 — 이관 종결(2026-08-12): LEGACY_ALIASES 자체가 걷혀 항목 검사는 대상이 없다.
    #        standard_tree 에 그 이름이 되살아나면 ㉢(위 낱말 검사)가 아니라 여기서 문다.
    st = text_of("standard_tree.py")
    if st is not None and "LEGACY" in st:
        f.add("#77", "standard_tree.py",
              "LEGACY 상수가 되살아났다 — 이중 수용은 2026-08-12 이관 종료로 걷었다")
    # #487 — 제1원칙 선행 게이트 표식(rule-owner-map).
    owner_map = REPO / "workspace" / "plan" / "2026-08-11-rule-owner-map.md"
    try:
        if "제1원칙 선행 게이트" not in owner_map.read_text(encoding="utf-8"):
            f.add("#487", str(owner_map.name),
                  "제1원칙 선행 게이트 표식이 없다 — #486~#492 는 다른 모든 검사보다 먼저 돈다")
    except OSError:
        f.add("#487", str(owner_map), "rule-owner-map 이 없다")
    # #495 · #496 — mypy 는 항상, tests 면제 없이.
    cmd = REPO / "dddjango" / "commands" / "dddjango.md"
    try:
        cmd_text = cmd.read_text(encoding="utf-8")
        if "mypy" not in cmd_text:
            f.add("#495", str(cmd.name),
                  "registry 문서에 mypy 가 없다 — strict 는 «항상» 돈다(없으면 타입 강제 0)")
        else:
            for line in cmd_text.splitlines():
                if "mypy" in line and re.search(r"exclude[^\n]*test|tests\.\*", line):
                    f.add("#496", str(cmd.name),
                          "mypy 호출에 tests 면제 — test/·fake/ 가 면제되면 페이크의 리스코프 "
                          "위반이 그대로 통과한다")
    except OSError:
        f.add("#495", str(cmd), "commands/dddjango.md 가 없다")


def main(argv: list[str]) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scripts-dir", default=str(DEFAULT_SCRIPTS))
    args = ap.parse_args(argv)
    scripts = Path(args.scripts_dir)
    if not scripts.is_dir():
        print(f"사용 오류: 디렉터리가 아니다 — {scripts}", file=sys.stderr)
        return 1

    findings = Findings()
    cand = Candidates()
    checkers = sorted(scripts.glob("check-*.py"))
    if not checkers:
        print("사용 오류: check-*.py 가 0건 — 스크립트 디렉터리가 맞나", file=sys.stderr)
        return 1
    for py in checkers:
        text = py.read_text(encoding="utf-8")
        mod = _parse(py)
        if mod is None:
            findings.add("#74", py.name, "파싱 실패 — 검사기 자신이 깨져 있다")
            continue
        _check_one(py, text, mod, findings, cand)
    if scripts == DEFAULT_SCRIPTS:
        _check_anchors(scripts, findings)

    for c in cand[:40]:
        print(c)
    if len(cand) > 40:
        print(f"(ⓓ#54 후보 {len(cand) - 40}건 생략 — 전체는 재실행으로)")
    print(f"검사기 {len(checkers)}개 검사")
    if findings:
        for x in findings:
            print(f"  {x}")
        print(f"위반 {len(findings)}건")
        return 2
    print("위반 0건")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
