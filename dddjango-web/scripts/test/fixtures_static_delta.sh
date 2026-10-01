#!/usr/bin/env bash
# dddjango-web G2 전 정적 검사 도구(static_delta.py) 자기 회귀 픽스처 — bash 전용(러너가 bash 로 부른다).
# 가짜 ruff·mypy(표지 줄로 발견을 낸다)를 임시 git 저장소의 .venv/bin 에 둔다. 네트워크·실제 도구 불요.
#   진입: E1 기준선 파일·머리 · E2 실행기 없음 STOP(exit 3) · E3 설정 없음 생략 · E4 pre-commit 만으로 감지
#         E5 uv.lock 있고 .venv 없음 → .venv 를 만들지 않고 STOP
#   G2: G1 다중집합·rename·삭제·--force-exclude·미추적 범위·동결 원본·형제 병합 유입·main 유입 0·주인 표지
#       G2 서식 = 손댄 파일 전체(기존 불통과 포함) · 슬라이스 0 전용은 신규만 · 손대지 않은 파일 0
#       G3 mypy 진입 기준선 대비 · main 판과 같은 파일의 main 오류 뺌 · G4 재제출 같은 결과 · 추적 파일 무변
#       G5 기준선 없음 → 기준 판 풀어 돌기 · G6 기준선 머리 HEAD 불일치 → 풀어 돌기
#       G7 풀어 돈 환경 불일치 → «병합 판 기준선 실패» · main 오류가 신규로 남음
#       G8 mode=refactor → 모든 기록이 슬라이스 0(기존 서식 불통과 면제) · G9 dirty 시작 → git_snapshot 기준
#       G10 깨끗한 레인 exit 0 · G11 기준 가지를 못 풀면 exit 1 · G12 G2 에서 실행기 없음 exit 3
#       G13 레인이 병합 뒤 main 판 파일을 고쳐 main 위반을 지우고 같은 키를 새로 만듦 → 가리지 않음
#       G14 main 병합 둘 — 병합 판은 가장 최근 것(옛 병합 판이면 가짜 신규)
#       G15 slices[0] 이름이 slice-0 이 아니면 기능 슬라이스(필드 build-state 판형 — 서식 면제 없음)
#       G16 훅·Makefile 로만 감지된 ruff → 서식 판정 불가(막지 않음) · G16b mypy 기준선 없음 → 판정 불가(막지 않음)
#       G17 이름 없는 slices[0] 은 test_baseline 이 있을 때만 슬라이스 0 · G18 배너 정적 검사 행
#       G19 H 규칙(재현 리뷰 합성 F1~F14 — 정답 10) · G20 구문 오류는 발견으로(계속) · G21 mypy H
#       E6 Makefile 설치 줄은 감지 아님 · G1⁵·G1⁶ 주인 표지(형제 병합·미추적 — Coordinator 가 제품 코드를 고치지 않게)
set -u
SCRIPTS="$(cd "$(dirname "$0")/.." && pwd)"
TOOL="$SCRIPTS/static_delta.py"
PASS=0; FAIL=0

assert() { # assert <이름> <기대exit> <있어야 할 문자열|-> <없어야 할 문자열|-> <실제exit> <출력>
  local name="$1" wantexit="$2" want="$3" unwant="$4" gotexit="$5" out="$6" ok=1
  [ "$gotexit" != "$wantexit" ] && ok=0
  [ "$want" != "-" ] && ! grep -qF -- "$want" <<<"$out" && ok=0
  [ "$unwant" != "-" ] && grep -qF -- "$unwant" <<<"$out" && ok=0
  if [ $ok = 1 ]; then PASS=$((PASS+1)); echo "PASS $name"; else
    FAIL=$((FAIL+1)); echo "FAIL $name (exit=$gotexit want=$wantexit)"; echo "$out" | head -40 | sed 's/^/    /'
  fi
}

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

# 가짜 ruff — `# L:<code>:<message>` 줄마다 발견 하나 · `# UNFMT` 가 있으면 서식 불통과 ·
# --force-exclude 일 때만 ruff.toml exclude(fnmatch)를 지킨다(명시 경로는 제외 무시 — 실제 ruff 와 같음)
cat > "$T/fake_ruff" <<'PY'
#!/usr/bin/env python3
import fnmatch, json, os, re, sys
a = sys.argv[1:]
if a == ['--version']:
    print('ruff 0.0.0 (fake)'); sys.exit(0)
force = '--force-exclude' in a
pats = []
if force and os.path.isfile('ruff.toml'):
    for line in open('ruff.toml', encoding='utf-8'):
        if line.strip().startswith('exclude'):
            pats += re.findall(r'"([^"]+)"', line)
def excluded(rel):
    return any(fnmatch.fnmatch(rel, p.replace('**/', '*')) or fnmatch.fnmatch(rel, p) for p in pats)
stdin_name = a[a.index('--stdin-filename') + 1] if '--stdin-filename' in a else None
cmd = a[0]
paths = [x for i, x in enumerate(a[1:], 1) if not x.startswith('-') and a[i - 1] not in ('--output-format', '--stdin-filename')]
items = []
if stdin_name is not None:
    items.append((stdin_name, sys.stdin.read()))
else:
    for p in paths:
        items.append((p, open(p, encoding='utf-8').read()))
out, bad = [], False
for name, text in items:
    if force and excluded(name):
        continue
    if cmd == 'check':
        for n, line in enumerate(text.splitlines(), 1):
            for m in re.finditer(r'# L:([A-Z0-9]+):([^#]*)', line):
                out.append({'code': m.group(1), 'message': m.group(2).strip(), 'filename': os.path.abspath(name),
                            'location': {'row': n}})
            if 'SYNTAXERR' in line:
                out.append({'code': 'invalid-syntax', 'message': 'bad', 'filename': os.path.abspath(name), 'location': {'row': n}})
    elif 'SYNTAXERR' in text:
        out.append({'code': 'invalid-syntax', 'message': 'bad', 'filename': os.path.abspath(name), 'location': {'row': 1}})
    elif '# UNFMT' in text:
        bad = True
        out.append({'code': 'unformatted', 'message': 'File would be reformatted', 'filename': os.path.abspath(name)})
if cmd == 'check' or '--output-format' in a:
    print(json.dumps(out))
if cmd == 'format' and any(o['code'] == 'invalid-syntax' for o in out):
    sys.exit(2)
sys.exit(1 if (out if cmd == 'check' else bad) else 0)
PY
# 가짜 mypy — `# T:<code>:<message>` 줄마다 error 하나 · `# TENV:<code>:<message>` 는 cwd 에 `.fake-env` 가 없을 때만
cat > "$T/fake_mypy" <<'PY'
#!/usr/bin/env python3
import os, re, sys
a = sys.argv[1:]
if a == ['--version']:
    print('mypy 0.0 (fake)'); sys.exit(0)
env = os.path.exists('.fake-env')
files, errors = [], []
for t in a:
    if os.path.isdir(t):
        for d, _s, fs in os.walk(t):
            files += [os.path.join(d, f) for f in sorted(fs) if f.endswith('.py')]
    elif t.endswith('.py'):
        files.append(t)
for f in sorted(files):
    for n, line in enumerate(open(f, encoding='utf-8'), 1):
        m = re.search(r'# T:([a-z-]+):(.*)$', line) or (None if env else re.search(r'# TENV:([a-z-]+):(.*)$', line))
        if m:
            errors.append(f'{f}:{n}: error: {m.group(2).strip()}  [{m.group(1)}]')
for e in errors:
    print(e)
if errors:
    print(f'Found {len(errors)} errors in {len({e.split(":")[0] for e in errors})} files (checked {len(files)} source files)')
    sys.exit(1)
print(f'Success: no issues found in {len(files)} source files'); sys.exit(0)
PY

g() { git -C "$R" -c user.name=t -c user.email=t@t "$@"; }
tool() { python3 "$TOOL" --project-root "$R" --build "$R/.dddjango-web/b1" "$@" 2>&1; }
venv() { mkdir -p "$R/.venv/bin"; cp "$T/fake_ruff" "$R/.venv/bin/ruff"; cp "$T/fake_mypy" "$R/.venv/bin/mypy"; chmod +x "$R/.venv/bin/"*; }
state() { # state <pre_run_head> <git_snapshot> <mode> <slice0 커밋> <S1 커밋…>
  python3 - "$R/.dddjango-web/b1/build-state.json" "$@" <<'PY'
import json, sys
path, pre, snap, mode, zero, *feat = sys.argv[1:]
data = {'pre_run_head': pre, 'git_snapshot': snap, 'slices': [{'name': 'slice-0-debt', 'commits': [zero] if zero else []},
                                                               {'name': 'S1', 'commits': feat}]}
if mode:
    data['mode'] = mode
open(path, 'w', encoding='utf-8').write(json.dumps(data))
PY
}

# ------------------------------------------------------------------ 진입
R="$T/e"; mkdir -p "$R/.dddjango-web/b1" "$R/pkg"; venv
printf '.venv/\n' > "$R/.gitignore"
printf 'exclude = ["**/migrations/**"]\n' > "$R/ruff.toml"
printf '[tool.mypy]\nstrict = true\n' > "$R/pyproject.toml"
printf 'repos:\n  - repo: local\n    hooks:\n      - id: mypy\n        entry: uv run mypy pkg\n        pass_filenames: false\n' > "$R/.pre-commit-config.yaml"
printf 'x = 1  # T:arg-type:pre-existing\n' > "$R/pkg/a.py"
g init -q -b main; g add -A; g commit -qm base
OUT=$(tool --phase entry); E=$?
H=$(head -1 "$R/.dddjango-web/b1/mypy-baseline.txt" 2>/dev/null)
assert "E1 진입 기준선 · 두 실행기 버전 · 출처 pre-commit" 0 "mypy 진입 기준선 mypy-baseline.txt" - "$E" "$OUT"
assert "E1′ 머리 HEAD · 대상 pkg" 0 "# HEAD $(g rev-parse HEAD)" - 0 "$H
$(sed -n 2,3p "$R/.dddjango-web/b1/mypy-baseline.txt")
$OUT"
assert "E1″ ruff 실행기 버전도 찍는다" 0 "ruff 0.0.0 (fake)" - "$E" "$OUT"
assert "E1‴ 진입 출력이 static-entry.txt 로 남는다(서식 판정 가능 줄 — coder 입력)" 0 "· 서식 판정 가능" - 0 "$(cat "$R/.dddjango-web/b1/static-entry.txt" 2>/dev/null)"
rm "$R/.venv/bin/ruff"
OUT=$(tool --phase entry); E=$?
assert "E2 ruff 설정 있음 · 실행기 없음 → STOP" 3 "STOP — ruff 설정 있음" - "$E" "$OUT"
R="$T/e3"; mkdir -p "$R/.dddjango-web/b1"; venv; printf '.venv/\n' > "$R/.gitignore"; printf 'x = 1\n' > "$R/m.py"
g init -q -b main; g add -A; g commit -qm base
OUT=$(tool --phase entry); E=$?
assert "E3 설정 없음 — 둘 다 생략" 0 "mypy 설정 없음 — 생략" "STOP" "$E" "$OUT"
printf 'repos:\n  - repo: https://github.com/astral-sh/ruff-pre-commit\n    hooks:\n      - id: ruff\n' > "$R/.pre-commit-config.yaml"
OUT=$(tool --phase entry); E=$?
assert "E4 pre-commit 훅만으로 ruff 감지" 0 "설정 .pre-commit-config.yaml" "ruff 설정 없음" "$E" "$OUT"
rm -rf "$R/.venv"; : > "$R/uv.lock"
# uv 가 있으면 빈 .venv 를 만들 수 있는 프로젝트 모양(uv 가 없으면 판정만 본다)
printf '[project]\nname = "x"\nversion = "0"\nrequires-python = ">=3.8"\n' > "$R/pyproject.toml"
OUT=$(tool --phase entry); E=$?
[ -e "$R/.venv" ] && OUT="$OUT
.venv 생김"
assert "E5 uv.lock · .venv 없음 → .venv 를 만들지 않고 STOP" 3 "STOP — ruff" ".venv 생김" "$E" "$OUT"
R="$T/e6"; mkdir -p "$R/.dddjango-web/b1"; venv; printf '.venv/\n' > "$R/.gitignore"; printf 'x = 1\n' > "$R/m.py"
printf 'setup:\n\tpip install ruff mypy\n' > "$R/Makefile"
g init -q -b main; g add -A; g commit -qm base
OUT=$(tool --phase entry); E=$?
assert "E6 Makefile 설치 줄은 ruff·mypy 감지가 아니다" 0 "ruff 설정 없음 — 생략" "Makefile:" "$E" "$OUT"
printf 'lint:\n\truff check .\n' > "$R/Makefile"
OUT=$(tool --phase entry); E=$?
assert "E6′ Makefile 의 ruff check 줄은 감지 · 설정 파일 없음 → 서식 판정 불가" 0 "서식 판정 불가(설정 파일 없음" - "$E" "$OUT"
# G16 훅으로만 감지된 ruff — 손댄 파일의 기존 서식 불통과를 요구하지 않는다(판정 불가 · 막지 않음)
R="$T/h"; mkdir -p "$R/pkg" "$R/.dddjango-web/b1"; venv; printf '.venv/\n' > "$R/.gitignore"
printf 'repos:\n  - repo: https://github.com/astral-sh/ruff-pre-commit\n    hooks:\n      - id: ruff-format\n' > "$R/.pre-commit-config.yaml"
printf 'a = 1  # UNFMT\n' > "$R/pkg/a.py"
g init -q -b main; g add -A; g commit -qm base; BASE=$(g rev-parse HEAD)
g checkout -q -b lane; printf 'a = 2  # UNFMT\n' > "$R/pkg/a.py"; g commit -qam lane; L=$(g rev-parse HEAD)
state "$BASE" "$BASE" "" "" "$L"
OUT=$(tool --phase g2); E=$?
assert "G16 훅으로만 감지된 ruff → 서식 판정 불가 · 막지 않음 · 배너 행" 0 "서식 판정 불가 — 설정 파일 없음" "서식 불통과" "$E" "$OUT"

# ------------------------------------------------------------------ G2 기본 저장소
build_main() { # build_main <변형: ok|tenv>
  R="$T/g-$1"; mkdir -p "$R/pkg/migrations" "$R/tests" "$R/.dddjango-web/b1"; venv
  printf '.venv/\n.fake-env\n' > "$R/.gitignore"; : > "$R/.fake-env"
  printf 'exclude = ["**/migrations/**", "**/__init__.py"]\n' > "$R/ruff.toml"
  printf '[tool.mypy]\nstrict = true\n' > "$R/pyproject.toml"
  printf 'repos:\n  - repo: local\n    hooks:\n      - id: mypy\n        entry: uv run mypy pkg\n        pass_filenames: false\n' > "$R/.pre-commit-config.yaml"
  printf 'a = 1  # L:E711:cmp none\nb = 2  # T:arg-type:pre-existing\n' > "$R/pkg/a.py"
  printf 'b = 1\n' > "$R/pkg/b.py"
  printf 'd = 1  # L:F401:gone\n' > "$R/pkg/d.py"
  printf 'o = 1  # L:E501:long\n' > "$R/pkg/old.py"
  printf 'f = 1  # UNFMT\n' > "$R/pkg/fmtold.py"
  printf 's = 1  # UNFMT\n' > "$R/pkg/s0.py"
  printf 's = 1\n' > "$R/pkg/s0new.py"
  printf 'u = 1  # UNFMT  # L:E711:cmp none\n' > "$R/pkg/untouched.py"
  printf 'm = 1\n' > "$R/pkg/mainfile.py"
  printf 's = 1\n' > "$R/pkg/sib.py"
  [ "$1" = tenv ] && printf 'e = 1  # TENV:misc:env only\n' > "$R/pkg/envdep.py"
  [ "$1" = tenv ] && printf 'c1 = 1\nc2 = 2\nc3 = 3\nc4 = 4\nc5 = 5\nc6 = 6\nc7 = 7\nc8 = 8\n' > "$R/pkg/co.py"
  g init -q -b main; g add -A; g commit -qm base
  BASE=$(g rev-parse HEAD)
  g checkout -q -b lane
  tool --phase entry >/dev/null
  # 진입 산출물 커밋(git_snapshot) — 빌드 폴더 관찰 스크립트 · 동결 원본
  mkdir -p "$R/.dddjango-web/b1/design-ref"
  printf 'x = 1  # L:F841:obs\n' > "$R/.dddjango-web/b1/obs.py"
  printf 'y = 1  # L:F841:frozen\n' > "$R/.dddjango-web/b1/design-ref/orig.py"
  g add -A; g commit -qm artifacts; SNAP=$(g rev-parse HEAD)
  # 슬라이스 0 — s0.py(기존 불통과 · 손댐) · s0new.py(새로 불통과)
  printf 's = 2  # UNFMT\n' > "$R/pkg/s0.py"; printf 's = 2  # UNFMT\n' > "$R/pkg/s0new.py"
  g commit -qam slice0; ZERO=$(g rev-parse HEAD)
  # 기능 슬라이스 S1
  printf 'a = 1  # L:E711:cmp none\nb = 2  # T:arg-type:pre-existing\nc = 3  # L:E711:cmp none\n' > "$R/pkg/a.py"
  printf 'b = 1  # T:arg-type:lane error\n' > "$R/pkg/b.py"
  g mv pkg/old.py pkg/new.py; g rm -q pkg/d.py
  printf 'f = 2  # UNFMT\n' > "$R/pkg/fmtold.py"
  printf 'x = 1  # L:F401:excluded\n' > "$R/pkg/migrations/0002.py"
  [ "$1" = tenv ] && sed -i.bak '7s/$/  # lane edit/' "$R/pkg/co.py" && rm -f "$R/pkg/co.py.bak"
  g add -A; g commit -qm s1; S1=$(g rev-parse HEAD)
  # main — 순수 유입 파일(위반·불통과·mypy 오류) · mainfile.py 에 E711
  g checkout -q main
  printf 'i = 1  # UNFMT  # L:E711:cmp none  # T:arg-type:main error\n' > "$R/pkg/main_only.py"
  printf 'm = 1  # L:E711:cmp none\n' > "$R/pkg/mainfile.py"
  [ "$1" = tenv ] && sed -i.bak '2s/$/  # T:arg-type:main in touched/' "$R/pkg/co.py" && rm -f "$R/pkg/co.py.bak"
  g add -A; g commit -qm main1
  # 형제 가지(main 이력 밖)
  g checkout -q -b sibling "$BASE"
  printf 's = 1  # L:E712:sibling\n' > "$R/pkg/sib.py"; g commit -qam sib
  g checkout -q lane
  g merge -q --no-ff --no-edit main
  g merge -q --no-ff --no-edit sibling
  # 미추적 — 이 빌드 폴더 · 다른 빌드 폴더(밖) · 패키지
  printf 'z = 1  # L:F841:scratch\n' > "$R/.dddjango-web/b1/scratch.py"
  mkdir -p "$R/.dddjango-web/other"; printf 'q = 1  # L:F841:other\n' > "$R/.dddjango-web/other/x.py"
  printf 'n = 1  # L:F841:untracked\n' > "$R/pkg/new_untracked.py"
  state "$BASE" "$SNAP" "" "$ZERO" "$S1"
}

build_main ok
STATUS0=$(g status --porcelain --untracked-files=all)
OUT=$(tool --phase g2); E=$?
assert "G1 ruff 신규 5(다중집합 1 · 빌드 폴더 2 · 미추적 1 · 형제 병합 1)" 2 "[static] ruff 신규 5" - "$E" "$OUT"
assert "G1′ --force-exclude · 삭제 · rename · main 유입 · 다른 빌드 폴더 · 동결 원본은 신규 아님" 2 "동결 원본 .py 1개" "excluded" "$E" "$OUT"
for unwant in "pkg/new.py" "pkg/d.py" "pkg/main_only.py" "pkg/mainfile.py" ".dddjango-web/other" "design-ref/orig.py ["; do
  assert "G1″ 목록에 없음: $unwant" 2 - "$unwant" "$E" "$(sed -n '/ruff 신규/,/서식 불통과/p' <<<"$OUT")"
done
assert "G1‴ 주인: 기능 슬라이스 S1 · 빌드 폴더 · 이력 밖 병합" 2 "pkg/a.py [기능 슬라이스 S1 — 재개봉]" - "$E" "$OUT"
assert "G1⁗ 이력 밖 병합 알림" 2 "이력 밖 병합" - "$E" "$OUT"
assert "G1⁵ 형제 병합 유입 주인 = 마지막 기능 슬라이스 재개봉(네가 고치지 않음)" 2 "유입 — 마지막 기능 슬라이스 재개봉]" "— 네가 고친다]" "$E" "$(grep -F 'pkg/sib.py [' <<<"$OUT")"
assert "G1⁶ 미추적 주인 = 만든 슬라이스로 커밋·기록하거나 지운 뒤 다시" 2 "미추적 — 만든 슬라이스(모르면 마지막 기능 슬라이스)로 커밋·기록하거나" - "$E" "$(grep -F 'pkg/new_untracked.py [' <<<"$OUT")"
assert "G18 배너 정적 검사 행" 2 "[static] 배너 정적 검사 행: 정적 검사(HEAD" - "$E" "$OUT"
assert "G2 서식 2(fmtold 기존 불통과 · s0new 신규)" 2 "서식 불통과 2(그중 기존 불통과 1)" - "$E" "$OUT"
assert "G2′ 손댄 파일의 기존 불통과도 막는다" 2 "pkg/fmtold.py [기능 슬라이스 S1 — 재개봉] 기존 불통과" - "$E" "$OUT"
assert "G2″ 슬라이스 0 전용 — 기존 불통과는 면제 · 새 불통과는 신규" 2 "pkg/s0new.py [슬라이스 0 — 재개봉(자기 편집 안)] 신규(슬라이스 0 전용" "pkg/s0.py [" "$E" "$OUT"
assert "G2‴ 손대지 않은 파일·main 유입은 서식 대상 아님" 2 - "untouched.py" "$E" "$OUT"
assert "G3 mypy 신규 1(main 판 같은 파일의 main 오류 뺌)" 2 "[static] mypy 신규 1" "main error" "$E" "$OUT"
assert "G3′ 병합 판 오류를 뺐다는 표지(지금도 같은 줄)" 2 "에서 지금도 같은 줄에 있는 오류 1 뺌" - "$E" "$OUT"
OUT2=$(tool --phase g2); E2=$?
STATUS1=$(g status --porcelain --untracked-files=all | grep -v 'mypy-baseline-')
assert "G4 재제출 — 같은 출력" "$E" - - "$E2" "$OUT2"
[ "$OUT" = "$OUT2" ] && ok=0 || ok=1
assert "G4′ 재제출 출력 byte 동일" 0 - - "$ok" "$(diff <(echo "$OUT") <(echo "$OUT2"))"
[ "$STATUS0" = "$STATUS1" ] && ok=0 || ok=1
assert "G4″ 추적·미추적 파일 무변(기준선 파일만 늘어남)" 0 - - "$ok" "$(diff <(echo "$STATUS0") <(echo "$STATUS1"))"
mv "$R/.dddjango-web/b1/mypy-baseline.txt" "$T/bl.txt"
OUT=$(tool --phase g2); E=$?
assert "G5 기준선 없음 → 기준 판을 풀어 돈 결과" 2 "기준선 기준 판" "mypy 기준선 없음" "$E" "$OUT"
assert "G5′ 같은 신규 수" 2 "[static] mypy 신규 1" - "$E" "$OUT"
sed 's/^# HEAD .*/# HEAD 0000000000000000000000000000000000000000/' "$T/bl.txt" > "$R/.dddjango-web/b1/mypy-baseline.txt"
OUT=$(tool --phase g2); E=$?
assert "G6 기준선 머리 HEAD 불일치 → 풀어 돌기" 2 "기준선 기준 판" - "$E" "$OUT"
cp "$T/bl.txt" "$R/.dddjango-web/b1/mypy-baseline.txt"
state "$BASE" "$SNAP" refactor "$ZERO" "$S1"
OUT=$(tool --phase g2); E=$?
assert "G8 mode=refactor — 기존 불통과 면제(fmtold)" 2 "서식 불통과 1(그중 기존 불통과 0)" "fmtold.py [" "$E" "$OUT"
python3 - "$R/.dddjango-web/b1/build-state.json" "$BASE" "$SNAP" "$ZERO" "$S1" <<'PY'
import json, sys
path, pre, snap, zero, s1 = sys.argv[1:]
json.dump({'pre_run_head': pre, 'git_snapshot': snap,
           'slices': [{'name': 'slice-1-data', 'commit': zero}, {'commit': s1}]}, open(path, 'w', encoding='utf-8'))
PY
OUT=$(tool --phase g2); E=$?
assert "G15 이름이 slice-0 이 아닌 slices[0] 은 기능 슬라이스(서식 면제 없음)" 2 "서식 불통과 3(그중 기존 불통과 2)" - "$E" "$OUT"
for TB in yes no; do
python3 - "$R/.dddjango-web/b1/build-state.json" "$BASE" "$SNAP" "$ZERO" "$S1" "$TB" <<'PY'
import json, sys
path, pre, snap, zero, s1, tb = sys.argv[1:]
data = {'pre_run_head': pre, 'git_snapshot': snap, 'slices': [{'commit': zero}, {'commit': s1}]}
if tb == 'yes':
    data['test_baseline'] = 'pytest -q'
json.dump(data, open(path, 'w', encoding='utf-8'))
PY
OUT=$(tool --phase g2); E=$?
if [ "$TB" = yes ]; then
  assert "G17a 이름 없는 slices[0] + test_baseline → 슬라이스 0(기존 불통과 면제)" 2 "서식 불통과 2(그중 기존 불통과 1)" - "$E" "$OUT"
else
  assert "G17b 이름 없는 slices[0] · test_baseline 없음 → 기능 슬라이스(필드 P2 판형)" 2 "서식 불통과 3(그중 기존 불통과 2)" - "$E" "$OUT"
fi
done
state "" "$SNAP" "" "$ZERO" "$S1"
OUT=$(tool --phase g2); E=$?
assert "G9 dirty 시작 → git_snapshot 기준(obs.py 는 범위 밖)" 2 "범위 기준 git_snapshot" "obs.py [" "$E" "$OUT"
mv "$R/.dddjango-web/b1/mypy-baseline.txt" "$T/bl2.txt"
OUT=$(tool --phase g2); E=$?
assert "G16b 기준선을 못 얻으면 mypy 판정 불가 — 막지 않고 배너 행" 2 "mypy 판정 불가 — 기준선 없음" "[static] mypy 신규" "$E" "$OUT"
mv "$T/bl2.txt" "$R/.dddjango-web/b1/mypy-baseline.txt"
OUT=$(tool --phase g2 --base-branch nosuch); E=$?
assert "G11 기준 가지를 못 풀면 미실행" 1 "기준 가지(nosuch)" - "$E" "$OUT"
state "$BASE" "$SNAP" "" "$ZERO" "$S1"
mv "$R/.venv/bin/mypy" "$T/mypy.off"
OUT=$(tool --phase g2); E=$?
assert "G12 G2 에서 mypy 실행기 없음 → STOP" 3 "STOP — mypy 설정 있음" - "$E" "$OUT"
mv "$T/mypy.off" "$R/.venv/bin/mypy"

build_main tenv
OUT=$(tool --phase g2); E=$?
assert "G7 풀어 돈 환경 불일치 → main 판 같은 파일 오류는 판정 불가(막지 않음)" 2 "mypy 판정 불가 1 — 병합 판 기준선 실패" - "$E" "$OUT"
assert "G7′ 레인 오류 · 손댄 파일 안 main 줄 오류는 신규(가리지 않음 · 판정 불가로 넘기지 않음)" 2 "[static] mypy 신규 2" - "$E" "$OUT"
assert "G7‴ 손댄 파일(co.py)의 오류는 병합 판 실패에도 신규 목록에" 2 "pkg/co.py: arg-type main in touched ×1 [" "판정 불가 — 배너]" "$E" "$(grep -F 'pkg/co.py:' <<<"$OUT")"
assert "G7″ 판정 불가가 배너 행에 실린다" 2 "· mypy 판정 불가 1 — 병합 판 기준선 실패" - "$E" "$(grep -F '배너 정적 검사 행' <<<"$OUT")"

# G10 깨끗한 레인 · G13 main 위반을 지우고 같은 키를 새로
R="$T/c"; mkdir -p "$R/pkg" "$R/.dddjango-web/b1"; venv
printf '.venv/\n' > "$R/.gitignore"; printf 'exclude = []\n' > "$R/ruff.toml"
printf 'a = 1\n' > "$R/pkg/a.py"; printf 'f = 1\n' > "$R/pkg/f5.py"
g init -q -b main; g add -A; g commit -qm base; BASE=$(g rev-parse HEAD)
g checkout -q -b lane; printf 'a = 2\n' > "$R/pkg/a.py"; g commit -qam lane; L=$(g rev-parse HEAD)
state "$BASE" "$BASE" "" "" "$L"
OUT=$(tool --phase g2); E=$?
assert "G10 깨끗한 레인 exit 0" 0 "결과 신규 합 0 — exit 0" - "$E" "$OUT"
g checkout -q main; printf 'f = 1  # L:E711:cmp none\ng = 1  # L:E711:cmp none\n' > "$R/pkg/f5.py"; g commit -qam main
g checkout -q lane; g merge -q --no-ff --no-edit main
printf 'f = 1\ng = 1\nh = 1  # L:E711:cmp none\n' > "$R/pkg/f5.py"; g commit -qam lanefix; L2=$(g rev-parse HEAD)
state "$BASE" "$BASE" "" "" "$L" "$L2"
OUT=$(tool --phase g2); E=$?
assert "G13 main 위반을 지우고 같은 키를 새로 만든 레인 위반을 센다" 2 "[static] ruff 신규 1" - "$E" "$OUT"

# G14 main 병합 둘 — 가장 최근 병합의 ^2 가 병합 판이다
R="$T/o"; mkdir -p "$R/pkg" "$R/.dddjango-web/b1"; venv
printf '.venv/\n' > "$R/.gitignore"; printf 'exclude = []\n' > "$R/ruff.toml"
printf 'm = 1\n' > "$R/pkg/mf.py"; printf 'a = 1\n' > "$R/pkg/a.py"
g init -q -b main; g add -A; g commit -qm base; BASE=$(g rev-parse HEAD)
g checkout -q -b lane; printf 'a = 2\n' > "$R/pkg/a.py"; g commit -qam l1; L1=$(g rev-parse HEAD)
g checkout -q main; printf 'o = 1\n' > "$R/pkg/other.py"; g add -A; g commit -qm x1
g checkout -q lane; g merge -q --no-ff --no-edit main
g checkout -q main; printf 'm = 1\nk = 1  # L:E711:cmp none\n' > "$R/pkg/mf.py"; g commit -qam x2
g checkout -q lane; printf 'm = 1\nk = 1  # L:E711:cmp none\n' > "$R/pkg/mf.py"; g commit -qam l2; L2=$(g rev-parse HEAD)
g merge -q --no-ff --no-edit main
state "$BASE" "$BASE" "" "" "$L1" "$L2"
OUT=$(tool --phase g2); E=$?
assert "G14 가장 최근 main 병합의 ^2 를 병합 판으로(옛 병합 판이면 가짜 신규)" 0 "[static] ruff 신규 0" - "$E" "$OUT"


# G19 H 규칙 — 재현 리뷰 합성 F1~F14 판형(세 함수 16줄 · main 이 func_a 줄에 E711 · 레인이 병합 전후로 고침) — 정답 10
R="$T/hh"; mkdir -p "$R/.dddjango-web/b1"; venv
printf '.venv/\n' > "$R/.gitignore"; printf 'exclude = []\n' > "$R/ruff.toml"
hw() { # hw <파일> <줄=내용>… — 기본 세 함수 16줄에서 줄을 바꿔 쓴다
  python3 - "$R/$1" "${@:2}" <<'PY'
import sys
path, *edits = sys.argv[1:]
lines = ["def func_a(x):", "    if x is None:", "        return True", "    return False", "", "",
         "def func_b(y):", "    if y is None:", "        return True", "    return False", "", "",
         "def func_c(z):", "    if z is None:", "        return True", "    return False"]
for e in edits:
    n, text = e.split("=", 1)
    lines[int(n) - 1] = text
open(path, "w", encoding="utf-8").write("\n".join(lines) + "\n")
PY
}
MAINL='    if x == None:  # L:E711:cmp none'
for f in F1 F2 F3 F5 F6 F7 F8 F12; do hw "app_$f.py"; done
printf 's = 1\n\n\ndef h(v):\n    return v == None and s == %s  # L:E711:cmp none\n' "'a'" > "$R/app_F14.py"
g init -q -b main; g add -A; g commit -qm base; BASE=$(g rev-parse HEAD)
g checkout -q -b lane
hw app_F3.py "8=    if y == None:  # L:E711:cmp none"; g commit -qam pre; S1=$(g rev-parse HEAD)
g checkout -q main
for f in F1 F2 F6 F7 F8 F12; do hw "app_$f.py" "2=$MAINL"; done
hw app_F3.py "2=$MAINL"
hw app_F5.py "2=    if x == None or x == None:  # L:E711:cmp none  # L:E711:cmp none"
g commit -qam main
g checkout -q lane; g merge -q --no-ff --no-edit main
hw app_F1.py "2=$MAINL" "8=    if y == None:  # L:E711:cmp none"
hw app_F2.py "2=$MAINL" "8=    if (y is None) == True:  # L:E712:cmp true"
hw app_F5.py "8=    if y == None:  # L:E711:cmp none"
hw app_F7.py "2=$MAINL" "14=$MAINL" "15=        return x  # L:F821:undefined name"
hw app_F8.py "2=    if x == None:  # keep  # L:E711:cmp none"
hw app_F12.py "8=$MAINL" "9=        return x  # L:F821:undefined name"
printf 's = 1\n\n\ndef h(v):\n    return v == None and s == "a"  # L:E711:cmp none\n' > "$R/app_F14.py"
printf 'x = 1  # L:E711:cmp none\n' > "$R/한글_모듈.py"; g add -A
g commit -qam post; S2=$(g rev-parse HEAD)
state "$BASE" "$BASE" "" "" "$S1" "$S2"
OUT=$(tool --phase g2); E=$?
assert "G19 H 규칙 — 합성 F1~F14 정답 10(main 몫 과다 0 · 레인 위반 누락 0)" 2 "[static] ruff 신규 10" - "$E" "$OUT"
for want in "app_F1.py" "app_F2.py" "app_F3.py" "app_F5.py" "app_F7.py" "app_F8.py" "app_F12.py" "한글_모듈.py"; do
  assert "G19′ 레인 위반 있는 파일: $want" 2 "$want [" - "$E" "$OUT"
done
assert "G19″ 손대지 않은 F6 · 서식만 바뀐 기준 판 위반 F14 는 신규 아님" 2 - "app_F6.py [" "$E" "$(grep -v F14 <<<"$OUT")"
assert "G19‴ F14 없음" 2 - "app_F14.py [" "$E" "$OUT"

# G20 구문 오류 파일 — 서식 판정 불가 발견으로 올리고 나머지(mypy) 계속
R="$T/sx"; mkdir -p "$R/pkg" "$R/.dddjango-web/b1"; venv; printf '.venv/\n' > "$R/.gitignore"
printf 'exclude = []\n' > "$R/ruff.toml"; printf '[tool.mypy]\nstrict = true\n' > "$R/pyproject.toml"
printf 'repos:\n  - repo: local\n    hooks:\n      - id: mypy\n        entry: mypy pkg\n        pass_filenames: false\n' > "$R/.pre-commit-config.yaml"
printf 'a = 1\n' > "$R/pkg/a.py"
g init -q -b main; g add -A; g commit -qm base; BASE=$(g rev-parse HEAD)
g checkout -q -b lane; tool --phase entry >/dev/null
printf 'def broken(:  SYNTAXERR\n' > "$R/.dddjango-web/b1/probe.py"
printf 'a = 2  # T:arg-type:lane error\n' > "$R/pkg/a.py"; g commit -qam lane; L=$(g rev-parse HEAD)
state "$BASE" "$BASE" "" "" "$L"
OUT=$(tool --phase g2); E=$?
assert "G20 구문 오류 → 발견으로 올리고 계속(미실행 아님)" 2 "probe.py [빌드 폴더 — 네가 고친다] 구문 오류 — 서식 판정 불가" "미실행" "$E" "$OUT"
assert "G20′ 구문 오류 뒤에도 mypy 가 돈다" 2 "[static] mypy 신규 1" - "$E" "$OUT"

# G21 mypy H — main 오류 줄이 지금도 살아 있고 레인이 같은 파일 다른 줄에 같은 키를 더함 → 레인 1
R="$T/mh"; mkdir -p "$R/pkg" "$R/.dddjango-web/b1"; venv; printf '.venv/\n.fake-env\n' > "$R/.gitignore"; : > "$R/.fake-env"
printf '[tool.mypy]\nstrict = true\n' > "$R/pyproject.toml"
printf 'repos:\n  - repo: local\n    hooks:\n      - id: mypy\n        entry: mypy pkg\n        pass_filenames: false\n' > "$R/.pre-commit-config.yaml"
python3 - "$R/pkg/m.py" <<'PY'
import sys
open(sys.argv[1], "w").write("\n".join(f"v{i} = {i}" for i in range(1, 13)) + "\n")
PY
g init -q -b main; g add -A; g commit -qm base; BASE=$(g rev-parse HEAD)
g checkout -q -b lane; tool --phase entry >/dev/null
g checkout -q main; sed -i.bak '2s/$/  # T:arg-type:same/' "$R/pkg/m.py"; rm -f "$R/pkg/m.py.bak"; g commit -qam main
g checkout -q lane; g merge -q --no-ff --no-edit main
sed -i.bak '10s/$/  # T:arg-type:same/' "$R/pkg/m.py"; rm -f "$R/pkg/m.py.bak"; g commit -qam lane; L=$(g rev-parse HEAD)
state "$BASE" "$BASE" "" "" "$L"
OUT=$(tool --phase g2); E=$?
assert "G21 mypy H — 살아 있는 main 오류는 빼고 레인 오류 1" 2 "[static] mypy 신규 1" - "$E" "$OUT"

echo "fixtures_static_delta: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" = 0 ]
