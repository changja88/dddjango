#!/usr/bin/env python3
"""dddjango 업무 어휘·framework 격리 검사기 — «이 낱말의 뜻을 누가 정하나»(D24·D38·D47).

`framework/`는 어느 BC 의 어휘도 모르는 기계 부품의 자리다.
업무 어휘의 정의(#628)는 business_vocab.py(공유 데이터 모듈)가 진다.

담당 규칙 (rule-owner-map · 총 61 — 기계 진단이 있는 것만 요약):
  구조   #393 BC 아래 framework/ 금지 · #35 루트 패키지 ∩ stdlib 금지 · #19 기술 이름
        1차 축은 framework/<technology>/ 뿐 · #395 framework 자식 다섯 · #396 4단 판정
        (port 있으면 capability · 기술 이름이면 technology · 어긋나면 위반) · #398 능력
        하나=폴더 하나 · #401 계약+구현 동거 · #423 뼈대 하나=파일 하나 · #620 test 자식
        셋 · #428 뼈대 테스트는 test/unit/ · #434 <project>/openapi_schema·response_policies 금지
  이름   #402 계약 파일명=폴더명 · #403 <Capability>Port · #407 구현 파일은 기술만 ·
        #408 <기술><Capability>Adapter · #412 <tech>/<tech>.py 금지 · #417 framework 에
        bc_ 접두 금지 · #584 [ast+] capability 이름에 누가·언제·어떻게 금지(확정: 기술
        이름 정확 일치 · 후보: 수단·계기 낱말 — 물음 소유 #595)
  격리   #46 framework→application import 0 · #47 capability 계약의 업무 어휘 0 ·
        #52 BC 이름 0(BC 하나를 지웠을 때 바뀌면 안 올린다) · #616/#617 <data>_out 애그리
        거트·어휘 0 · #587 <data>_in 동일 · #615 계약·자료 파일의 프레임워크 타입 0 ·
        #426 test/ 의 BC 이름 0 · #416 <technology> 모듈은 BC 무관 · #413 은 #8·#7 이
        같은 표면을 이미 물어 참조만 남긴다(중복 진단 금지)
  계약   #585 exception.py 필수·도메인 상속 금지 · #604 계약은 «가산만»(git diff 로
        시그니처 변경 검출) · #606 반환 bool 반송·기본값 인자 · #607 [ast+] 업무 판정
        후보(Q2 — #553 술어 공유) · #618 [ast+] locale 값·채널 설정 금지(후보 물음은
        #590 소유) · #619 [ast+] 원시값 하나로 되는 자료 클래스 후보
  test   #53 HTTP 로만 구동(모델·팩토리 import 0) · #425 [ast+] 재료의 뜻 물음(후보) ·
        #621 framework 포트의 페이크는 framework/test/fake/ · #622 페이크는 선언 상속·
        같은 이름 · #623 선언과 1:1 · #624 페이크가 DB·HTTP·파일이면 위반
  pure   #560 pure 밖 import 0 · #561 부작용 0(datetime·random·os·io…) · #562
        *_port/*_adapter 금지·업무 어휘 0(Shared Kernel 차단 기계)
  기타   #119 401·403·404·422·429·HttpError 는 framework 소유(BC 재선언 금지) ·
        #294 저장 실패의 넷째 예외 자리 금지 · #420 BC 안 인증 파일 금지 ·
        #48·#40·#404·#405·#411·#558(재료 #614 이행 대기)·#559(=#560∧#561∧#562)·
        #614[이행] — 진단 0(다른 행·다른 검사기가 실체를 진다 · 중복 진단 금지)

이관 계약(명세 조각 ⓐ): 대상 0건 가드(#74 — framework 부재·BC 미채택이면 exit 0) ·
ImportError fail-closed · ⓓ 후보 exit 불산입 · #604 는 git 없으면 판정 불가 고지.

사용법: check-business-vocabulary.py [TARGET_DIR]   (기본: 현재 디렉터리)
종료코드: 0=clean(또는 미채택) · 1=사용/분석 오류 · 2=blocker(발견 출력)
구조화 레코드: DJR_FINDINGS_JSON=<경로> 지정 시 findings.py(공용 모듈)가 JSON lines 를
추가 방출한다 — 라인 출력·exit 의미론 무변(T0 B2).
"""
from __future__ import annotations

import ast
import re
import subprocess
import sys

import checker_target
from findings import Candidates, Findings
from pathlib import Path

try:
    import standard_tree as tree
    import business_vocab as vocab
except ImportError:  # 데이터 모듈 없이는 판정 불가 — fail-closed(분석 오류)
    print("분석 오류: standard_tree.py/business_vocab.py 를 찾지 못했다 — 검사기와 같은 폴더에 있어야 한다", file=sys.stderr)
    sys.exit(1)

SKIP_DIRS = vocab.SKIP_DIRS
FIXED3 = {"broker", "test", "pure"}
DATA_STEMS_RE = re.compile(r"(_in|_out)$")
CONTRACT_KIND = {"exception"}  # + *_port·*_in·*_out
PURE_IMPURE = {"datetime", "time", "random", "secrets", "uuid", "os", "io", "socket", "subprocess"}
FRAMEWORK_TYPES = {"ninja", "django", "rest_framework", "pydantic"}
CHANNEL_CONFIG_WORDS = {"host", "port", "url", "endpoint", "api_key", "token", "timeout",
                        "region", "bucket", "template_id"}
MEANS_WORDS = {"client", "cache", "sync", "cron", "queue", "http", "rest", "sdk", "api",
               "nightly", "daily", "hourly", "weekly", "realtime", "driver", "gateway"}
AUTH_TOKENS = {"auth", "authentication", "bearer"}
CURATED_TECH = {"django", "ninja", "celery", "redis", "kafka", "smtp", "stripe", "postgres",
                "postgresql", "mysql", "sqlite", "boto3", "s3", "sqs", "grpc", "drf", "rest"}


def _parse(path: Path) -> ast.Module | None:
    try:
        return ast.parse(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeDecodeError, SyntaxError):
        return None


def _py_files(base: Path) -> list[Path]:
    return [p for p in sorted(base.rglob("*.py")) if not set(p.parts) & SKIP_DIRS]


def _rel(root: Path, path: Path, line: int | None = None) -> str:
    s = path.relative_to(root).as_posix()
    return f"{s}:{line}" if line else s


def _camel(snake: str) -> str:
    return "".join(w.capitalize() for w in snake.split("_"))


def _framework_dirs(root: Path) -> list[Path]:
    fw = root / "framework"
    return [fw] if fw.is_dir() else []


def _identifier_tokens(mod: ast.Module) -> set[str]:
    out: set[str] = set()
    for node in ast.walk(mod):
        if isinstance(node, (ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)):
            out |= vocab.tokens(node.name)
        elif isinstance(node, ast.Name):
            out |= vocab.tokens(node.id)
        elif isinstance(node, ast.arg):
            out |= vocab.tokens(node.arg)
        elif isinstance(node, ast.Attribute):
            out |= vocab.tokens(node.attr)
    return out


def _is_contract_file(py: Path) -> bool:
    return py.stem.endswith("_port") or py.stem in CONTRACT_KIND or DATA_STEMS_RE.search(py.stem) is not None


# ── 구조 — #35 · #393 · #19 · #395 · #396 · #398 · #401 · #434 ─────────────

def _check_structure(root: Path, fw: Path, tech: set, f: Findings, cand: Candidates) -> None:
    for p in sorted(fw.iterdir()):
        if p.name in ("__pycache__",):
            continue
        if p.is_file() and p.suffix == ".py" and p.name != "__init__.py":
            f.add("#395", _rel(root, p),
                  "framework/ 직계 파일 — 자식은 다섯이다: broker/·test/·pure/·<capability>/·<technology>/")
            continue
        if not p.is_dir() or p.name in FIXED3:
            continue
        has_port = any(x.name.endswith("_port.py") for x in p.glob("*.py"))
        is_tech = p.name in tech or p.name in CURATED_TECH
        if has_port:
            _check_capability(root, fw, p, f, cand)
        elif is_tech:
            _check_technology(root, p, f)
        else:
            f.add("#396", _rel(root, p),
                  f"`{p.name}/` — 4단 판정에 안 걸린다: 고정 셋도, *_port.py 있는 <capability>/ 도, "
                  "알려진 <technology>/ 도 아니다(순수 계산이면 pure/ «안»으로 간다)")
    # #584 — capability 이름 판정(확정: 기술 이름 · 후보: 수단·계기).
    for p in sorted(fw.iterdir()):
        if not p.is_dir() or p.name in FIXED3 or p.name in ("__pycache__",):
            continue
        has_port = any(x.name.endswith("_port.py") for x in p.glob("*.py"))
        if not has_port:
            continue
        toks = set(p.name.split("_"))
        if toks & CURATED_TECH:
            f.add("#584", _rel(root, p),
                  f"capability 이름 `{p.name}/` 에 기술 이름 — 「무엇이 필요한가」로 짓고 "
                  "누가·언제·어떻게는 넣지 않는다(smtp_client ✗ → email_sender ✓)")
        elif toks & MEANS_WORDS:
            cand.add("#584", _rel(root, p),
                     f"capability 이름 `{p.name}/` 에 수단·계기 낱말 {sorted(toks & MEANS_WORDS)}",
                     "그것(공급자·계기·수단)이 바뀌어도 이 이름이 그대로인가(#595)")


def _check_capability(root: Path, fw: Path, cap: Path, f: Findings, cand: Candidates) -> None:
    ports = [x for x in sorted(cap.glob("*.py")) if x.name.endswith("_port.py")]
    if len(ports) > 1:
        f.add("#398", _rel(root, cap), f"계약 파일 {len(ports)}개 — «능력 하나 = 폴더 하나»다")
    expected_port = f"{cap.name}_port.py"
    if not (cap / expected_port).is_file():
        f.add("#402", _rel(root, cap),
              f"계약 파일 이름이 폴더와 다르다 — `{expected_port}` 여야 한다({[p.name for p in ports]})")
    impls = [x for x in sorted(cap.glob("*.py"))
             if x.name != "__init__.py" and not _is_contract_file(x)]
    if not impls:
        f.add("#401", _rel(root, cap),
              "구현이 없다 — capability 안에는 계약과 구현이 «함께» 산다(계약만 두고 구현을 "
              "BC 에 남기지 않는다)")
    if not (cap / "exception.py").is_file():
        f.add("#585", _rel(root, cap),
              "exception.py 가 없다 — 필수다. 번역할 대상이 없으면 django·SDK 예외가 "
              "유스케이스로 «샌다»")
    for py in impls:
        if not py.stem.endswith("_adapter"):
            f.add("#407", _rel(root, py),
                  "구현 파일 이름은 «기술만» 말한다 — `<technology>_adapter.py`(폴더가 이미 능력을 말한다)")
        elif cap.name in py.stem.replace("_adapter", "").split("_"):
            f.add("#407", _rel(root, py),
                  f"구현 파일이 능력 `{cap.name}` 을 되풀이한다 — 기술만 말한다(clock/django_adapter.py)")
        mod = _parse(py)
        if mod is None:
            continue
        tech_name = py.stem[: -len("_adapter")]
        want = f"{_camel(tech_name)}{_camel(cap.name)}Adapter"
        for cls in [n for n in mod.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]:
            if not cls.name.endswith("Adapter"):
                f.add("#39", _rel(root, py, cls.lineno),
                      f"`{cls.name}` — 포트를 구현하는 클래스는 …Adapter 로 끝난다")
            elif cls.name != want:
                f.add("#408", _rel(root, py, cls.lineno),
                      f"`{cls.name}` — 구현 클래스는 `<기술><Capability>Adapter`(`{want}`)다")


def _check_technology(root: Path, techdir: Path, f: Findings) -> None:
    if (techdir / f"{techdir.name}.py").is_file():
        f.add("#412", _rel(root, techdir / f"{techdir.name}.py"),
              "폴더 이름과 같은 모듈 — framework/<technology>/ 안에 두지 않는다")
    for p in sorted(techdir.iterdir()):
        if p.is_dir() and p.name != "__pycache__":
            f.add("#414", _rel(root, p),
                  "<technology>/ 아래 하위 폴더 — `<module>.py` 파일만 온다(response/ 같은 방향 축 금지)")
    for py in sorted(techdir.glob("*.py")):
        if py.name == "__init__.py":
            continue
        mod = _parse(py)
        if mod is None:
            continue
        imports_lib = any(
            (isinstance(n, ast.Import) and any(a.name.split(".")[0] == techdir.name for a in n.names))
            or (isinstance(n, ast.ImportFrom) and (n.module or "").split(".")[0] == techdir.name)
            for n in ast.walk(mod))
        if not imports_lib:
            f.add("#415", _rel(root, py),
                  f"`{techdir.name}` 를 import 하지 않는다 — 여기는 «그 라이브러리의 타입 없이는 "
                  "문장이 성립하지 않는 코드»만 온다(아니면 pure/ 나 capability 다)")


# ── 격리 — #46 · #47 · #52 · #416 · #426 · #425 · #615~#619 · #587 ─────────

def _check_isolation(root: Path, fw: Path, union: set, bc_names: set, agg_camels: set,
                     f: Findings, cand: Candidates) -> None:
    for py in _py_files(fw):
        rel_parts = py.relative_to(fw).parts
        in_test = rel_parts and rel_parts[0] == "test"
        in_tech = len(rel_parts) >= 2 and not any(
            x.name.endswith("_port.py") for x in (fw / rel_parts[0]).glob("*.py")) \
            and rel_parts[0] not in FIXED3
        in_broker = rel_parts and rel_parts[0] == "broker"
        if in_broker:
            continue  # broker 의 어휘·격리는 check-broker-contract(#518)가 진다 — 중복 진단 금지.
        mod = _parse(py)
        if mod is None:
            continue
        text = py.read_text(encoding="utf-8")
        # #417 — framework 는 BC 를 모르니 bc_ 접두를 쓰지 않는다.
        if py.stem.startswith("bc_"):
            f.add("#417", _rel(root, py),
                  "framework 파일에 `bc_` 접두 — 프레임워크 오류 스키마는 framework_*_schema.py "
                  "로 짓고 BC 의 오류 언어는 driving_layer/api/bc_error_schema.py 로 따로 산다")
        # #46 — framework → application import 0.
        for node in ast.walk(mod):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mods = [a.name for a in node.names] if isinstance(node, ast.Import) \
                    else [node.module or ""]
                if any(m.split(".")[0] == "application" for m in mods):
                    f.add("#46", _rel(root, py, node.lineno),
                          "framework 가 application/ 쪽을 import 한다 — 나가는 import 는 0 건이다")
        # BC 이름 등장 — 자리별로 #426(test) · #416(technology) · #52(그 밖).
        name_hits = sorted(n for n in bc_names if re.search(rf"\b{re.escape(n)}\b", text))
        if name_hits:
            if in_test:
                f.add("#426", _rel(root, py),
                      f"framework/test/ 에 BC 이름 {name_hits} — 올라온 파일 안에 특정 BC 이름이 "
                      "나오지 않는다")
            elif in_tech:
                f.add("#416", _rel(root, py),
                      f"<technology> 모듈에 BC 이름 {name_hits} — BC 를 다 지워도 그대로 남아야 한다")
            else:
                f.add("#52", _rel(root, py),
                      f"framework 파일에 BC 이름 {name_hits} — BC 하나를 지웠을 때 바뀌는 파일은 "
                      "공용 칸으로 올리지 않는다")
        # 업무 어휘 — 계약 자리는 확정, 그 밖은 후보(#448 — 물음 소유).
        idents = _identifier_tokens(mod)
        hit = sorted(idents & union)
        if hit:
            cap_dir = fw / rel_parts[0] if rel_parts else fw
            is_cap = any(x.name.endswith("_port.py") for x in cap_dir.glob("*.py")) \
                if cap_dir.is_dir() else False
            if is_cap and py.stem.endswith("_out"):
                f.add("#617", _rel(root, py),
                      f"<data>_out.py 에 업무 어휘 {hit[:5]} — 한 글자라도 나오면 위반이다(#628)")
            elif is_cap and py.stem.endswith("_in"):
                f.add("#587", _rel(root, py),
                      f"<data>_in.py 에 업무 어휘 {hit[:5]} — 검사 둘 중 하나(어휘 0)에 걸렸다")
            elif is_cap and _is_contract_file(py):
                f.add("#47", _rel(root, py),
                      f"capability 계약의 이름·시그니처에 업무 어휘 {hit[:5]} — 한 글자도 없어야 "
                      "framework 에 들어온다")
            elif in_test:
                cand.add("#425", _rel(root, py), f"framework/test/ 재료에 업무 어휘 {hit[:5]}",
                         "이 재료의 뜻을 밖(HTTP·pytest·시간)이 정하나")
            else:
                cand.add("#448", _rel(root, py), f"framework 파일에 업무 어휘 {hit[:5]}",
                         "이 낱말의 뜻을 저장소 밖이 정하나")
        # 계약·자료 파일 — #615 프레임워크 타입 · #616 애그리거트 · #618 · #619.
        if _is_contract_file(py) and not in_test:
            for node in ast.walk(mod):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    mods = [a.name for a in node.names] if isinstance(node, ast.Import) \
                        else [node.module or ""]
                    for m in mods:
                        if m.split(".")[0] in FRAMEWORK_TYPES:
                            f.add("#615", _rel(root, py, node.lineno),
                                  f"계약·자료 파일이 `{m}` 를 import 한다 — 유스케이스가 그 타입을 "
                                  "반환값으로 받게 된다(안쪽 원은 바깥 원의 이름을 부르지 않는다)")
        if DATA_STEMS_RE.search(py.stem) and not in_test:
            for node in ast.walk(mod):
                if isinstance(node, ast.ClassDef):
                    fields = [n for n in node.body if isinstance(n, ast.AnnAssign)
                              and isinstance(n.target, ast.Name)]
                    for fld in fields:
                        ann_names = {x.id for x in ast.walk(fld.annotation) if isinstance(x, ast.Name)}
                        if ann_names & agg_camels:
                            f.add("#616", _rel(root, py, fld.lineno),
                                  f"자료 필드에 애그리거트 {sorted(ann_names & agg_camels)} — "
                                  "framework 자료에 애그리거트가 오면 위반이다")
                        if fld.target.id in CHANNEL_CONFIG_WORDS:
                            f.add("#618", _rel(root, py, fld.lineno),
                                  f"채널 설정 낱말 `{fld.target.id}` — 자료에 담지 않는다"
                                  "(설정은 어댑터·composition_root 몫)")
                    if len(fields) == 1:
                        cand.add("#619", _rel(root, py, node.lineno),
                                 f"`{node.name}` 필드가 하나 — 원시값·값 객체로 되면 만들지 않는다",
                                 "이것이 원시값 하나로 되나")
            for node in ast.walk(mod):
                if isinstance(node, ast.Call):
                    name = node.func.id if isinstance(node.func, ast.Name) else \
                        (node.func.attr if isinstance(node.func, ast.Attribute) else "")
                    if name in ("gettext", "gettext_lazy", "format_lazy", "_"):
                        f.add("#618", _rel(root, py, node.lineno),
                              "locale 이 바꾸는 값을 자료가 만든다 — 문구는 여기 없다(#588 술어)")


# ── 계약 강등 신호 — #604 · #606 · #607 ────────────────────────────────────

def _check_contract_evolution(root: Path, fw: Path, f: Findings, cand: Candidates) -> None:
    port_files = [p for p in _py_files(fw) if p.stem.endswith("_port")]
    for py in port_files:
        mod = _parse(py)
        if mod is None:
            continue
        for cls in [n for n in ast.walk(mod) if isinstance(n, ast.ClassDef)]:
            for m in [n for n in cls.body if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
                if m.returns is not None:
                    names = {x.id for x in ast.walk(m.returns) if isinstance(x, ast.Name)}
                    if names == {"bool"}:
                        f.add("#606", _rel(root, py, m.lineno),
                              f"계약 메서드 `{m.name}` 의 반환이 bool — «판정»이라 반송한다"
                              "(판정은 업무 쪽 소유다)")
                if any(d for d in m.args.defaults):
                    f.add("#606", _rel(root, py, m.lineno),
                          f"계약 메서드 `{m.name}` 에 기본값 인자 — 강등 신호로 센다"
                          "(BC 별 분기가 스며드는 자리다)")
    # #604 — 계약은 가산만(git diff 로 기존 시그니처 변경 검출).
    try:
        diff = subprocess.run(
            ["git", "-C", str(root), "diff", "HEAD", "--", *[str(p.relative_to(root)) for p in port_files]],
            capture_output=True, text=True, timeout=30)
        if diff.returncode == 0 and diff.stdout:
            for line in diff.stdout.splitlines():
                if re.match(r"^-\s*def\s+\w+", line) and not line.startswith("---"):
                    f.add("#604", _rel(root, fw),
                          f"계약 메서드 시그니처 변경·삭제(`{line.strip()[1:].strip()}`) — framework "
                          "계약은 «더하기»만 한다(새 메서드를 더하고 옛 것을 남긴 뒤 강등 절차로 걷는다)")
        elif diff.returncode != 0:
            print("notice — git 이 없어 #604(계약 가산만)를 판정하지 못했다(변경 이력이 재료다)")
    except (OSError, subprocess.TimeoutExpired):
        print("notice — git 실행 실패로 #604 판정 불가")
    # #607 — 업무 판정 후보(Q2 · #553 술어 공유).
    for py in _py_files(fw):
        if py.stem.endswith("_port") or "test" in py.relative_to(fw).parts:
            continue
        mod = _parse(py)
        if mod is None:
            continue
        for fn in [n for n in ast.walk(mod) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))]:
            for n in ast.walk(fn):
                if isinstance(n, ast.Compare) and any(
                        isinstance(c, ast.Constant) and isinstance(c.value, (int, float))
                        and not isinstance(c.value, bool) for c in n.comparators):
                    cand.add("#607", _rel(root, py, n.lineno),
                             "framework 함수가 숫자 임계값과 비교한다 — 중립 이름으로 갈아입어도 "
                             "판정은 판정이다", "Q2 — 이 조건이 업무 규칙인가")
                    break


# ── test — #53 · #620 · #621 · #622 · #623 · #624 · #428 · #423 ────────────

def _check_framework_test(root: Path, fw: Path, f: Findings) -> None:
    t = fw / "test"
    if not t.is_dir():
        return
    for p in sorted(t.iterdir()):
        if p.is_dir() and p.name not in ("fake", "unit", "__pycache__"):
            f.add("#620", _rel(root, p), "framework/test/ 의 자식은 셋이다 — <module>.py·fake/·unit/")
        if p.is_file() and p.suffix == ".py" and p.name.startswith("test_"):
            f.add("#428", _rel(root, p),
                  "뼈대 자신을 검사하는 테스트는 framework/test/unit/ 에 둔다(뼈대와 같은 폴더 금지)")
    for py in _py_files(t):
        mod = _parse(py)
        if mod is None:
            continue
        if py.parent == t:
            classes = [n for n in mod.body if isinstance(n, ast.ClassDef) and not n.name.startswith("_")]
            if len(classes) > 1:
                f.add("#423", _rel(root, py), f"공개 클래스 {len(classes)}개 — «공유 뼈대 하나 = 파일 하나»다")
        for node in ast.walk(mod):
            if isinstance(node, ast.ImportFrom):
                m = node.module or ""
                if ".models" in m or m.endswith("models"):
                    f.add("#53", _rel(root, py, node.lineno),
                          "framework/test 가 모델을 import 한다 — HTTP 로만 시스템을 구동한다")
                if m.split(".")[0] == "factory" or "factories" in m:
                    f.add("#53", _rel(root, py, node.lineno),
                          "framework/test 에 팩토리 — 팩토리는 모델을 알아 여기 못 온다(#392·#620)")
    fake = t / "fake"
    if fake.is_dir():
        port_stems = {p.stem for cap in fw.iterdir() if cap.is_dir()
                      for p in cap.glob("*_port.py")}
        for py in sorted(fake.glob("*.py")):
            if py.name == "__init__.py":
                continue
            if py.stem not in port_stems:
                f.add("#623", _rel(root, py),
                      f"`{py.stem}` 에 대응하는 framework 선언이 없다 — fake 와 선언은 1:1 이다")
            mod = _parse(py)
            if mod is None:
                continue
            for cls in [n for n in mod.body if isinstance(n, ast.ClassDef)]:
                bases = {b.id if isinstance(b, ast.Name) else getattr(b, "attr", "") for b in cls.bases}
                if not any(b.endswith("Port") for b in bases):
                    f.add("#622", _rel(root, py, cls.lineno),
                          f"`{cls.name}` 이 포트 선언을 상속하지 않는다 — 페이크는 선언 상속으로 "
                          "리스코프를 진다")
            for node in ast.walk(mod):
                if isinstance(node, (ast.Import, ast.ImportFrom)):
                    mods = [a.name for a in node.names] if isinstance(node, ast.Import) \
                        else [node.module or ""]
                    if any(m.split(".")[0] in ("django", "requests", "httpx", "boto3") for m in mods):
                        f.add("#624", _rel(root, py, node.lineno),
                              "페이크가 DB·HTTP 를 만진다 — 그러면 어댑터다")
                if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                        and node.func.id == "open":
                    f.add("#624", _rel(root, py, node.lineno), "페이크가 파일을 만진다 — 그러면 어댑터다")


# ── pure — #560 · #561 · #562 ──────────────────────────────────────────────

def _check_pure(root: Path, fw: Path, union: set, f: Findings) -> None:
    pure = fw / "pure"
    if not pure.is_dir():
        return
    for py in _py_files(pure):
        if py.stem.endswith(("_port", "_adapter")):
            f.add("#562", _rel(root, py),
                  "pure/ 아래 *_port·*_adapter — 여기는 계약도 구현도 아니라 «순수 계산»의 자리다")
        mod = _parse(py)
        if mod is None:
            continue
        for node in ast.walk(mod):
            if isinstance(node, (ast.Import, ast.ImportFrom)):
                mods = [a.name for a in node.names] if isinstance(node, ast.Import) \
                    else [node.module or ""]
                for m in mods:
                    top = m.split(".")[0]
                    if top in PURE_IMPURE:
                        f.add("#561", _rel(root, py, node.lineno),
                              f"`{m}` — 부작용·2차 행위자다. 판정은 「같은 인자로 두 번 불러 같은 "
                              "답이 나오나」(그건 <capability>/ 다)")
                    elif top in ("application", "framework") and "pure" not in m:
                        f.add("#560", _rel(root, py, node.lineno),
                              f"`{m}` — pure/ 는 밖의 저장소 파일을 import 하지 않는다"
                              "(같은 pure/ 안만 예외)")
        idents = _identifier_tokens(mod)
        hit = sorted(idents & union)
        if hit:
            f.add("#562", _rel(root, py),
                  f"pure/ 에 업무 어휘 {hit[:5]} — 한 글자라도 나오면 위반(Shared Kernel 차단 기계)")


# ── BC 쪽 — #393 · #119 · #294 · #420 ──────────────────────────────────────

def _check_bc_side(root: Path, f: Findings) -> None:
    for bc in vocab.bc_dirs(root):
        for d in bc.rglob("framework"):
            if d.is_dir() and not set(d.parts) & SKIP_DIRS:
                f.add("#393", _rel(root, d),
                      "BC 아래 framework/ — framework 는 저장소 루트에 두고 어느 BC 에도 속하지 않는다")
        # #621 — framework 포트의 페이크가 BC test/fake 에 있다.
        for fake_py in bc.rglob("test/fake/*.py"):
            if set(fake_py.parts) & SKIP_DIRS or fake_py.name == "__init__.py":
                continue
            mod = _parse(fake_py)
            fw_imported: set[str] = set()
            for node in ast.walk(mod) if mod else []:
                if isinstance(node, ast.ImportFrom) and (node.module or "").split(".")[0] == "framework":
                    fw_imported |= {a.asname or a.name for a in node.names}
            for cls in [n for n in (mod.body if mod else []) if isinstance(n, ast.ClassDef)]:
                bases = {b.id if isinstance(b, ast.Name) else getattr(b, "attr", "") for b in cls.bases}
                if bases & fw_imported:
                    f.add("#621", _rel(root, fake_py, cls.lineno),
                          f"framework 포트의 페이크 `{cls.name}` 가 BC test/fake 에 있다 — "
                          "framework/test/fake/ 에 산다(짝이 층을 가로지르면 안 된다)")
        for py in _py_files(bc):
            stem_toks = set(py.stem.split("_"))
            if stem_toks & AUTH_TOKENS:
                f.add("#420", _rel(root, py),
                      "BC 안 인증 파일 — «틀»은 framework/ninja/ 에, 토큰 «해석»은 "
                      "open_host_service/ 로 공개한다(BC 안에 인증 파일이 남지 않는다)")
            mod = _parse(py)
            if mod is None:
                continue
            parts = py.relative_to(bc).parts
            for node in ast.walk(mod):
                if isinstance(node, ast.ClassDef):
                    bases = {b.id if isinstance(b, ast.Name) else getattr(b, "attr", "") for b in node.bases}
                    if "HttpError" in bases:
                        f.add("#119", _rel(root, py, node.lineno),
                              f"`{node.name}` 이 HttpError 를 상속한다 — 401·403·404·422·429·"
                              "HttpError 는 framework 소유라 BC 가 자기 오류 언어로 재선언하지 않는다")
                    if bases & {"Exception"} and (
                            ("persistence" in parts and "adapter" in parts)
                            or "unit_of_work" in parts):
                        if "exception" not in parts:
                            f.add("#294", _rel(root, py, node.lineno),
                                  "«저장이 실패하는 방식»의 넷째 예외 자리 — 업무 의미면 애그리거트 "
                                  "예외로, 재시도 판정이면 framework 로, 그 밖은 선언하지 않는다")


# ── main ────────────────────────────────────────────────────────────────────

def main(argv: list[str]) -> int:
    if len(argv) > 1:
        print(f"사용법: {Path(sys.argv[0]).name} [TARGET_DIR]", file=sys.stderr)
        return 1
    root = Path(argv[0]).resolve() if argv else Path.cwd()
    bad_target_reason = checker_target.bc_shaped_target_reason(root)
    if bad_target_reason is not None:
        print(f"사용 오류: {bad_target_reason}", file=sys.stderr)
        return 1
    if not root.is_dir():
        print(f"사용 오류: 디렉터리가 아니다 — {root}", file=sys.stderr)
        return 1

    findings = Findings()
    cand = Candidates()
    tech = vocab.tech_names()
    union = vocab.all_vocab(root)
    bc_names = vocab.bc_names(root)
    agg_camels = set()
    for bc in vocab.bc_dirs(root):
        domain = bc / "domain_layer"
        if domain.is_dir():
            agg_camels |= {_camel(d.name) for d in domain.iterdir()
                           if d.is_dir() and d.name not in ("shared_value_object", "domain_service", "__pycache__")}

    # #35 — 루트 패키지 ∩ stdlib.
    stdlib = set(getattr(sys, "stdlib_module_names", ())) | set(vocab.STDLIB_FALLBACK)
    for p in sorted(root.iterdir()):
        if p.is_dir() and (p / "__init__.py").is_file() and p.name in stdlib:
            findings.add("#35", _rel(root, p),
                         "저장소 루트 패키지가 표준 라이브러리 모듈명과 겹친다 — import 가 가려진다")

    fws = _framework_dirs(root)
    for fw in fws:
        _check_structure(root, fw, tech, findings, cand)
        _check_isolation(root, fw, union, bc_names, agg_camels, findings, cand)
        _check_contract_evolution(root, fw, findings, cand)
        _check_framework_test(root, fw, findings)
        _check_pure(root, fw, union, findings)
    _check_bc_side(root, findings)

    # #434 — <project>/ 의 접힌 규칙 파일.
    for name in ("openapi_schema.py", "response_policies.py"):
        for p in root.rglob(name):
            if set(p.parts) & SKIP_DIRS or any(fw in p.parents for fw in fws):
                continue
            findings.add("#434", _rel(root, p),
                         f"`{name}` — 접힌 규칙 클래스는 framework/ninja/ 로 간다"
                         "(<project>/ 에 두지 않는다)")
    # #19 — 기술 이름 1차 축은 framework/<technology>/ 뿐.
    for bc in vocab.bc_dirs(root):
        for d in bc.rglob("*"):
            if not d.is_dir() or set(d.parts) & SKIP_DIRS or d.name == "__pycache__":
                continue
            if d.name in CURATED_TECH - {"celery"} and not d.name.startswith("django_"):
                # celery/ 는 #173(check-missable-entrance) 소유 — 중복 진단 금지.
                findings.add("#19", _rel(root, d),
                             f"기술 이름 폴더 `{d.name}/` — 기술을 1차 축으로 쓰는 자리는 "
                             "framework/<technology>/ 하나뿐이다")

    for c in cand:
        print(c)
    if findings:
        print("blocker — 업무 어휘·framework 격리 위반 (이 낱말의 뜻을 누가 정하나 — D24·D38·D47)")
        for x in findings:
            print(f"  {x}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
