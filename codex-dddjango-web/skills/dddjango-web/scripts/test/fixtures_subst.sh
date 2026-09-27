#!/usr/bin/env bash
# dddjango-web 치환 확인 픽스처 (--subst-check — 슬라이스 0 끝 green ④).
# mktemp 임시 git 프로젝트 · 사례마다 새 사본 · 각 red 에 양성 대조 짝.
set -u
SCRIPTS="$(cd "$(dirname "$0")/.." && pwd)"
PASS=0; FAIL=0

run_backstop() { python3 "$SCRIPTS/backstop.py" "$@" 2>&1; }

assert() { # assert <이름> <기대exit> <있어야 할 문자열|-> <없어야 할 문자열|-> <실제exit> <출력>
  local name="$1" wantexit="$2" want="$3" unwant="$4" gotexit="$5" out="$6" ok=1
  [ "$gotexit" != "$wantexit" ] && ok=0
  [ "$want" != "-" ] && ! grep -qF -- "$want" <<<"$out" && ok=0
  [ "$unwant" != "-" ] && grep -qF -- "$unwant" <<<"$out" && ok=0
  if [ $ok = 1 ]; then PASS=$((PASS+1)); echo "PASS $name"; else
    FAIL=$((FAIL+1)); echo "FAIL $name (exit=$gotexit want=$wantexit)"; echo "$out" | head -20 | sed 's/^/    /'
  fi
}

commit_all() { # commit_all <dir> <msg> — HEAD 해시 출력
  git -C "$1" -c user.name=t -c user.email=t@t add -A >/dev/null
  git -C "$1" -c user.name=t -c user.email=t@t commit -qm "$2"
  git -C "$1" rev-parse HEAD
}

T="$(mktemp -d)"
trap 'rm -rf "$T"' EXIT

# 기준 저장소: web 모듈 + 이미지 + web/ 밖 테스트(모듈 머리 · TYPE_CHECKING · 함수 안 지역 import · 문자열 참조)
B="$T/base"
mkdir -p "$B/config" "$B/web/a" "$B/web/static/images" "$B/tests/web" "$B/tests/fixtures"
echo "SECRET_KEY = 'x'" > "$B/config/settings.py"
: > "$B/web/__init__.py"; : > "$B/web/a/__init__.py"
printf 'def f():\n    return 1\n\n\ndef h():\n    return 2\n' > "$B/web/a/m.py"
printf 'VALUE = 3\n' > "$B/web/a/q.py"
printf 'z = 4\n' > "$B/web/a/q2.py"
printf 'X' > "$B/web/static/images/old.png"
printf 'Y' > "$B/web/static/images/other.png"
printf 'PNG\0bin' > "$B/tests/fixtures/pic.png"
cat > "$B/tests/web/test_m.py" <<'EOF'
from typing import TYPE_CHECKING

from web.a.m import f, h
import web.a.q
from web.a.q2 import z

if TYPE_CHECKING:
    from web.a.m import f as typed_f


def test_f():
    assert f() == 1
    assert web.a.q.VALUE == 3 and z == 4


def test_local():
    marker = 1
    from web.a.m import h
    assert h() == 2 + marker - 1


def test_patch_target():
    assert "web.a.m.f".endswith("f")
EOF
cat > "$B/tests/web/test_img.py" <<'EOF'
IMG = "images/old.png"
OTHER = "images/other.png"


def test_img():
    assert IMG != OTHER
EOF
printf 'images/old.png\nimages/other.png\n' > "$B/tests/web/refs.txt"
git -C "$B" init -q
BASE=$(commit_all "$B" base)

case_repo() { # case_repo <이름> — 기준 저장소 새 사본 경로 출력
  local d="$T/$1"
  git clone -q "$B" "$d"
  echo "$d"
}

sub() { # sub <파일> <옛> <새> — 문자열 치환(파이썬 — sed 방언 차이 회피)
  python3 - "$1" "$2" "$3" <<'PY'
import sys
p, a, b = sys.argv[1:]
t = open(p, encoding='utf-8').read()
open(p, 'w', encoding='utf-8').write(t.replace(a, b))
PY
}

names_md() { # names_md <파일> <이름 행…>
  local f="$1"; shift
  { echo "# 명세"; echo; echo "## 슬라이스 0"; for r in "$@"; do echo "이름: $r"; done; } > "$f"
}

# ---------- S1: 경로 치환만 green · 줄 파일 재정렬 green
P=$(case_repo s1)
git -C "$P" mv web/static/images/old.png web/static/images/new_image.png
sub "$P/tests/web/test_img.py" images/old.png images/new_image.png
printf 'images/other.png\nimages/new_image.png\n' > "$P/tests/web/refs.txt"
commit_all "$P" s1 >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S1 경로 치환 + 줄 재정렬 = green" 0 "치환 확인 — web/ 밖 변경 파일 2" "[subst]" "$E" "$OUT"

# ---------- S2: 정의 이동(이름 쌍) — 모듈 머리 import 가 둘로 갈라짐 · 문자열 참조 · TYPE_CHECKING
P=$(case_repo s2)
mkdir -p "$P/web/b"; : > "$P/web/b/__init__.py"
printf 'def f():\n    return 1\n' > "$P/web/b/n.py"
printf 'def h():\n    return 2\n' > "$P/web/a/m.py"
sub "$P/tests/web/test_m.py" "from web.a.m import f, h" "from web.a.m import h
from web.b.n import f"
sub "$P/tests/web/test_m.py" "    from web.a.m import f as typed_f" "    from web.b.n import f as typed_f"
sub "$P/tests/web/test_m.py" '"web.a.m.f"' '"web.b.n.f"'
commit_all "$P" s2 >/dev/null
names_md "$T/s2.md" "web.a.m.f → web.b.n.f"
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD --names "$T/s2.md"); E=$?
assert "S2a 정의 이동(모듈 머리 분할 · TYPE_CHECKING · 문자열) = green" 0 "치환 확인 — web/ 밖 변경 파일 1" "[subst]" "$E" "$OUT"
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S2b 대조: 이름 쌍(--names) 없으면 red" 2 "import 구간" - "$E" "$OUT"

# ---------- S3: 함수 안 지역 import 의 정의 이동 green · 이름 바뀐 개명의 속성 참조(vm.<이름>) green
P=$(case_repo s3)
printf 'def f():\n    return 1\n\n\ndef h2():\n    return 2\n' > "$P/web/a/m.py"
sub "$P/tests/web/test_m.py" "from web.a.m import f, h" "from web.a.m import f, h2"
sub "$P/tests/web/test_m.py" "    from web.a.m import h
    assert h() == 2" "    from web.a.m import h2
    assert h2() == 2"
printf 'import web.a.m as vm\n\n\ndef test_attr():\n    assert vm.h2() == 2\n' > "$P/tests/web/test_attr.py"
commit_all "$P" s3-tmp >/dev/null
# test_attr.py 는 기준에 없던 새 파일이라 따로 뺀다 — 기준에 넣고 다시 비교한다
git -C "$P" reset -q --hard "$BASE"
printf 'import web.a.m as vm\n\n\ndef test_attr():\n    assert vm.h() == 2\n' > "$P/tests/web/test_attr.py"
S3BASE=$(commit_all "$P" s3-base)
printf 'def f():\n    return 1\n\n\ndef h2():\n    return 2\n' > "$P/web/a/m.py"
sub "$P/tests/web/test_m.py" "from web.a.m import f, h" "from web.a.m import f, h2"
sub "$P/tests/web/test_m.py" "    from web.a.m import h
    assert h() == 2" "    from web.a.m import h2
    assert h2() == 2"
sub "$P/tests/web/test_attr.py" "vm.h()" "vm.h2()"
commit_all "$P" s3 >/dev/null
names_md "$T/s3.md" "web.a.m.h → web.a.m.h2"
OUT=$(run_backstop "$P" --subst-check "$S3BASE" HEAD --names "$T/s3.md"); E=$?
assert "S3 지역 import · 개명 속성 참조 = green" 0 "치환 확인 — web/ 밖 변경 파일 2" "[subst]" "$E" "$OUT"

# ---------- S4: import 재정렬 · 괄호 여러 줄 green
P=$(case_repo s4)
sub "$P/tests/web/test_m.py" "from web.a.m import f, h" "from web.a.m import (
    h,
    f,
)"
commit_all "$P" s4 >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S4 import 재정렬·괄호 여러 줄 = green" 0 "치환 확인" "[subst]" "$E" "$OUT"

# ---------- S5: 교환 쌍(이름 맞바꿈 f↔h) green — 동시 치환 · 경로 맞바꿈은 git 이 개명으로 못 봐 red(fail-closed)
P=$(case_repo s5)
python3 - "$P/web/a/m.py" "$P/tests/web/test_m.py" <<'PY'
import re, sys
for p in sys.argv[1:]:
    t = open(p, encoding='utf-8').read()
    open(p, 'w', encoding='utf-8').write(re.sub(r'\b(f|h)\b', lambda m: 'h' if m.group(1) == 'f' else 'f', t))
PY
commit_all "$P" s5 >/dev/null
names_md "$T/s5.md" "web.a.m.f → web.a.m.h" "web.a.m.h → web.a.m.f"
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD --names "$T/s5.md"); E=$?
assert "S5a 이름 교환 쌍 = green(동시 치환)" 0 "치환 확인 — web/ 밖 변경 파일 1" "[subst]" "$E" "$OUT"
P=$(case_repo s5b)
git -C "$P" mv web/static/images/old.png web/static/images/tmp.png
git -C "$P" mv web/static/images/other.png web/static/images/old.png
git -C "$P" mv web/static/images/tmp.png web/static/images/other.png
sub "$P/tests/web/test_img.py" 'IMG = "images/old.png"
OTHER = "images/other.png"' 'IMG = "images/other.png"
OTHER = "images/old.png"'
commit_all "$P" s5b >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S5b 경로 맞바꿈은 git 이 개명 쌍으로 못 봄 = red(fail-closed 한계 기록)" 2 "치환만으로 설명되지 않는다" - "$E" "$OUT"

# ---------- S6: 폴더 전체 이동(점 경로 접두) green · 파일 하나 이동은 폴더 쌍 없음
P=$(case_repo s6)
git -C "$P" mv web/a web/c
sub "$P/tests/web/test_m.py" "web.a." "web.c."
commit_all "$P" s6 >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S6a 폴더 전체 이동 = green" 0 "치환 확인" "[subst]" "$E" "$OUT"
P=$(case_repo s6b)
mkdir -p "$P/web/c"; git -C "$P" mv web/a/q.py web/c/q.py
sub "$P/tests/web/test_m.py" "web.a.q" "web.c.q"
sub "$P/tests/web/test_m.py" "from web.c.q2 import z" "from web.a.q2 import z"
commit_all "$P" s6b >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S6b 파일 하나 이동 = 파일 쌍만(쌍 2 · 폴더 쌍 없음) green" 0 "쌍 2" "[subst]" "$E" "$OUT"

# ---------- S7: 접두 쌍은 점 성분 경계로만 — web.a.q 쌍이 web.a.q2 를 삼키지 않는다
P=$(case_repo s7)
git -C "$P" mv web/a/q.py web/a/r.py
printf 'z = 4\n' > "$P/web/a/r2.py"
sub "$P/tests/web/test_m.py" "web.a.q" "web.a.r"
commit_all "$P" s7 >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S7a web.a.q→web.a.r 쌍이 web.a.q2→web.a.r2 편집을 덮지 않음 = red" 2 "web.a.r2.z" - "$E" "$OUT"
P=$(case_repo s7b)
git -C "$P" mv web/a/q.py web/a/r.py
sub "$P/tests/web/test_m.py" "import web.a.q
" "import web.a.r
"
sub "$P/tests/web/test_m.py" "web.a.q.VALUE" "web.a.r.VALUE"
commit_all "$P" s7b >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S7b 대조: web.a.q 만 치환하면 green" 0 "치환 확인" "[subst]" "$E" "$OUT"

# ---------- S8: 블록 사이 import 이동 red · 같은 블록 안 문장 건너 이동 red
P=$(case_repo s8)
sub "$P/tests/web/test_m.py" "    marker = 1
    from web.a.m import h
" "    from web.a.m import h
    marker = 1
"
commit_all "$P" s8 >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S8a 같은 블록 안 문장 건너 import 이동 = red" 2 "import 구간" - "$E" "$OUT"
P=$(case_repo s8b)
sub "$P/tests/web/test_m.py" "    marker = 1
    from web.a.m import h
" "    marker = 1
"
sub "$P/tests/web/test_m.py" "import web.a.q
" "import web.a.q
from web.a.m import h as local_h
"
commit_all "$P" s8b >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S8b 블록 사이 import 이동 = red" 2 "import 구간" - "$E" "$OUT"

# ---------- S9: 넓은 영역 치환 red · 단언 변경 red · 별칭 import 추가 red(fail-closed)
P=$(case_repo s9)
git -C "$P" mv web/static/images/old.png web/static/images/new_image.png
sub "$P/tests/web/test_img.py" images/ pictures/
commit_all "$P" s9 >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S9a 넓은 영역 치환(images/ 전체) = red" 2 "치환만으로 설명되지 않는다" - "$E" "$OUT"
P=$(case_repo s9b)
sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() == 2"
commit_all "$P" s9b >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S9b 단언 변경 = red" 2 "import 밖 본문" - "$E" "$OUT"
P=$(case_repo s9c)
sub "$P/tests/web/test_m.py" "import web.a.q
" "import web.a.q
import web.a.m as extra
"
commit_all "$P" s9c >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S9c 모듈 별칭 import 추가 = red(fail-closed)" 2 "import 구간" - "$E" "$OUT"

# ---------- S10: 테스트 밖 web/ 밖 파일 red · --except 로 배선 파일 제외 green · --except 거부
P=$(case_repo s10)
echo "DEBUG = True" >> "$P/config/settings.py"
commit_all "$P" s10 >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S10a 테스트 밖 web/ 밖 파일 = red" 2 "테스트 밖 web/ 밖 파일" - "$E" "$OUT"
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD --except config/settings.py); E=$?
assert "S10b --except 배선 파일 제외 = green · 요약에 제외 표시" 0 "제외 1 — config/settings.py" "[subst]" "$E" "$OUT"
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD --except tests/web/test_m.py); E=$?
assert "S10c --except 에 테스트 파일 = 실행 불능" 1 "web/ 밖 비테스트 파일만" - "$E" "$OUT"
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD --except web/a/m.py); E=$?
assert "S10d --except 에 web/ 아래 경로 = 실행 불능" 1 "web/ 밖 비테스트 파일만" - "$E" "$OUT"
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD --except config); E=$?
assert "S10e --except 에 폴더 = 실행 불능(테스트가 새어 빠지지 않게)" 1 "파일 경로만 받는다" - "$E" "$OUT"
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD --except '*'); E=$?
assert "S10f --except 에 글롭 = 실행 불능" 1 "파일 경로만 받는다" - "$E" "$OUT"
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD --except 'config/*.py'); E=$?
assert "S10g --except 에 글롭(파일 모양) = 실행 불능" 1 "파일 경로만 받는다" - "$E" "$OUT"

# ---------- S11: 미커밋 web/ 밖 변경 = 실행 불능(④ 는 슬라이스 0 커밋 뒤) · .dddjango-web 무시
P=$(case_repo s11)
sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() == 2"
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S11a 미커밋 테스트 단언 변경 = 실행 불능" 1 "미커밋 web/ 밖 변경" - "$E" "$OUT"
git -C "$P" checkout -q -- tests/web/test_m.py
mkdir -p "$P/.dddjango-web/run"; echo "note" > "$P/.dddjango-web/run/refactor-scope.md"
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S11b 대조: .dddjango-web 미추적 기록은 가드 밖 green" 0 "치환 확인" - "$E" "$OUT"
commit_all "$P" records >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S11c 커밋된 .dddjango-web 기록은 대조 밖 green" 0 "web/ 밖 변경 파일 0" - "$E" "$OUT"

# ---------- S12: 치환이 아닌 상태(A 새 파일 · D 삭제 · 개명) · 이진 파일 변경 = red
P=$(case_repo s12)
printf 'def test_new():\n    assert True\n' > "$P/tests/web/test_new.py"
commit_all "$P" s12 >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S12a 새 테스트 파일 = red" 2 "치환이 아닌 변경(A" - "$E" "$OUT"
P=$(case_repo s12b)
git -C "$P" rm -q tests/web/refs.txt
commit_all "$P" s12b >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S12b 테스트 파일 삭제 = red" 2 "치환이 아닌 변경(D" - "$E" "$OUT"
P=$(case_repo s12c)
git -C "$P" mv tests/web/test_img.py tests/web/test_image.py
commit_all "$P" s12c >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S12c 테스트 파일 개명 = red" 2 "치환이 아닌 변경" - "$E" "$OUT"
P=$(case_repo s12d)
printf 'PNG\0changed' > "$P/tests/fixtures/pic.png"
commit_all "$P" s12d >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S12d 이진 fixture 변경 = red" 2 "이진 파일 변경" - "$E" "$OUT"

# ---------- S13: 실행 불능 — 없는 커밋 · 파싱 실패
P=$(case_repo s13)
OUT=$(run_backstop "$P" --subst-check deadbeef HEAD); E=$?
assert "S13a 없는 기준 커밋 = 실행 불능" 1 "치환 확인 실행 불능" - "$E" "$OUT"
printf 'def broken(:\n' >> "$P/tests/web/test_m.py"
commit_all "$P" s13 >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S13b 대상 파일 파싱 실패 = 실행 불능" 1 "파싱 실패" - "$E" "$OUT"

echo "fixtures_subst: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" = 0 ]
