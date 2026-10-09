#!/usr/bin/env bash
# dddjango-web 치환 확인 픽스처 (--subst-check — 슬라이스 0 끝 green ④).
# (바탕: v1.3.1 fixtures_subst.sh S1~S18 그대로 — 치환 확인은 트리와 무관한 git 대조 · S19 = 2.0.0 web_test/ 테스트 뿌리)
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

# ---------- S14: 커밋별 개명 사슬 — 개명 커밋 뒤 다른 커밋이 같은 파일을 고쳐 쓰면 누적 diff 는 D+A 로 본다
rewrite() { # rewrite <파일> <표지> — 옛 내용과 닮지 않은 새 내용(유사도 50% 미만)
  printf 'PNG-NEW-%s-zzzzzzzzzzzzzzzzzzzzzzzz' "$2" > "$1"
}
P=$(case_repo s14a)
git -C "$P" mv web/static/images/old.png web/static/images/new_image.png
sub "$P/tests/web/test_img.py" images/old.png images/new_image.png
commit_all "$P" s0 >/dev/null
rewrite "$P/web/static/images/new_image.png" s14a; commit_all "$P" feat >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S14a 개명 뒤 다른 커밋의 내용 교체 = green(커밋별 개명 사슬)" 0 "치환 확인 — web/ 밖 변경 파일 1" "[subst]" "$E" "$OUT"
P=$(case_repo s14b)
git -C "$P" mv web/a/q.py web/a/r.py
sub "$P/tests/web/test_m.py" "import web.a.q
" "import web.a.r
"
sub "$P/tests/web/test_m.py" "web.a.q.VALUE" "web.a.r.VALUE"
commit_all "$P" s0 >/dev/null
printf 'from dataclasses import dataclass\n\nVALUE = 3\n\n\n@dataclass\nclass R:\n    x: int\n' > "$P/web/a/r.py"
commit_all "$P" feat >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S14b .py 개명 뒤 다른 커밋의 본문 재작성 = green" 0 "치환 확인 — web/ 밖 변경 파일 1" "[subst]" "$E" "$OUT"
P=$(case_repo s14c)
git -C "$P" mv web/static/images/old.png web/static/images/mid.png; commit_all "$P" c1 >/dev/null
git -C "$P" mv web/static/images/mid.png web/static/images/last.png; commit_all "$P" c2 >/dev/null
rewrite "$P/web/static/images/last.png" s14c
sub "$P/tests/web/test_img.py" images/old.png images/last.png; commit_all "$P" c3 >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S14c 개명 사슬 합성(old→mid→last · 뒤 교체) = green" 0 "치환 확인 — web/ 밖 변경 파일 1" "[subst]" "$E" "$OUT"
P=$(case_repo s14d)
git -C "$P" mv web/static/images/old.png web/static/images/mid.png; commit_all "$P" c1 >/dev/null
git -C "$P" mv web/static/images/mid.png web/static/images/last.png; commit_all "$P" c2 >/dev/null
rewrite "$P/web/static/images/last.png" s14d
sub "$P/tests/web/test_img.py" images/old.png images/mid.png; commit_all "$P" c3 >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S14d 대조: 사슬 중간 이름(대상에 없음)으로 치환 = red" 2 "치환만으로 설명되지 않는다" - "$E" "$OUT"
P=$(case_repo s14e)
git -C "$P" mv web/static/images/old.png web/static/images/new_image.png; commit_all "$P" s0 >/dev/null
rewrite "$P/web/static/images/old.png" s14e
sub "$P/tests/web/test_img.py" images/old.png images/new_image.png; commit_all "$P" feat >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S14e 대조: 개명 뒤 옛 경로가 대상에 되살아나면 쌍 없음 = red" 2 "치환만으로 설명되지 않는다" - "$E" "$OUT"
P=$(case_repo s14f)
git -C "$P" mv web/static/images/old.png web/static/images/tmp.png; commit_all "$P" c1 >/dev/null
git -C "$P" mv web/static/images/other.png web/static/images/old.png; commit_all "$P" c2 >/dev/null
git -C "$P" mv web/static/images/tmp.png web/static/images/other.png; commit_all "$P" c3 >/dev/null
sub "$P/tests/web/test_img.py" 'IMG = "images/old.png"
OTHER = "images/other.png"' 'IMG = "images/other.png"
OTHER = "images/old.png"'
commit_all "$P" c4 >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S14f 대조: 커밋에 걸친 경로 맞바꿈 = red(S5b 와 같은 fail-closed)" 2 "치환만으로 설명되지 않는다" - "$E" "$OUT"
# S14g·S14n 은 사례 전용 기준 커밋(S3 방식) — 테스트가 기준 web/ 에 없는 경로(ghost.png)를 가리킨다
P=$(case_repo s14g)
echo "images/ghost.png" >> "$P/tests/web/refs.txt"; S14GBASE=$(commit_all "$P" s14g-base)
rewrite "$P/web/static/images/ghost.png" s14g; commit_all "$P" c1 >/dev/null
git -C "$P" mv web/static/images/ghost.png web/static/images/ghost_2.png; commit_all "$P" c2 >/dev/null
sub "$P/tests/web/refs.txt" images/ghost.png images/ghost_2.png; commit_all "$P" c3 >/dev/null
OUT=$(run_backstop "$P" --subst-check "$S14GBASE" HEAD); E=$?
assert "S14g 대조: 구간에서 새로 만든 파일의 개명 사슬(옛 경로가 기준에 없음) = red" 2 "치환만으로 설명되지 않는다" - "$E" "$OUT"
P=$(case_repo s14i)
git -C "$P" mv web/static/images/old.png web/static/images/keep.png; commit_all "$P" c1 >/dev/null
rewrite "$P/web/static/images/old.png" s14i; commit_all "$P" c2 >/dev/null
git -C "$P" mv web/static/images/old.png web/static/images/r.png; commit_all "$P" c3 >/dev/null
sub "$P/tests/web/test_img.py" images/old.png images/r.png; commit_all "$P" c4 >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S14i 대조: 비운 옛 이름에 새로 만든 파일의 개명은 기준 파일의 후계가 아니다 = red" 2 "치환만으로 설명되지 않는다" - "$E" "$OUT"
P=$(case_repo s14j)
git -C "$P" mv web/static/images/old.png web/static/images/gone.png; commit_all "$P" c1 >/dev/null
git -C "$P" rm -q web/static/images/gone.png; commit_all "$P" c2 >/dev/null
sub "$P/tests/web/test_img.py" images/old.png images/gone.png; commit_all "$P" c3 >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S14j 대조: 개명 뒤 삭제(새 경로가 대상에 없음) = red" 2 "치환만으로 설명되지 않는다" - "$E" "$OUT"
P=$(case_repo s14k)
git -C "$P" rm -q web/static/images/other.png; commit_all "$P" c1 >/dev/null
git -C "$P" mv web/static/images/old.png web/static/images/other.png; commit_all "$P" c2 >/dev/null
sub "$P/tests/web/refs.txt" images/old.png images/other.png; commit_all "$P" c3 >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S14k 대조: 새 경로가 기준에 있던 경로(other 자리 덮어쓰기) = red" 2 "치환만으로 설명되지 않는다" - "$E" "$OUT"
P=$(case_repo s14l)
git -C "$P" checkout -qb side
git -C "$P" mv web/static/images/old.png web/static/images/new_image.png
sub "$P/tests/web/test_img.py" images/old.png images/new_image.png; commit_all "$P" s0 >/dev/null
git -C "$P" checkout -q -
git -C "$P" -c user.name=t -c user.email=t@t merge -q --no-ff side -m merge
rewrite "$P/web/static/images/new_image.png" s14l; commit_all "$P" feat >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S14l 곁가지 개명 → 머지 → 본선 교체 = green(첫 부모 diff 의 개명)" 0 "치환 확인 — web/ 밖 변경 파일 1" "[subst]" "$E" "$OUT"
P=$(case_repo s14m)
git -C "$P" checkout -qb side
git -C "$P" mv web/static/images/old.png web/static/images/new_image.png
sub "$P/tests/web/test_img.py" images/old.png images/new_image.png; commit_all "$P" s1 >/dev/null
rewrite "$P/web/static/images/new_image.png" s14m; commit_all "$P" s2 >/dev/null
git -C "$P" checkout -q -
git -C "$P" -c user.name=t -c user.email=t@t merge -q --no-ff side -m merge
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S14m 곁가지 안 개명+교체 → 머지 = red(첫 부모 밖 — fail-closed 한계 기록)" 2 "치환만으로 설명되지 않는다" - "$E" "$OUT"
P=$(case_repo s14n)
echo "images/ghost.png" >> "$P/tests/web/refs.txt"; S14NBASE=$(commit_all "$P" s14n-base)
git -C "$P" checkout -q --orphan unrelated
rewrite "$P/web/static/images/ghost.png" s14n; commit_all "$P" root >/dev/null
git -C "$P" mv web/static/images/ghost.png web/static/images/ghost_2.png
sub "$P/tests/web/refs.txt" images/ghost.png images/ghost_2.png; commit_all "$P" c1 >/dev/null
OUT=$(run_backstop "$P" --subst-check "$S14NBASE" HEAD); E=$?
assert "S14n 대조: 무관 이력(구간에 뿌리 커밋) · 뿌리 파일의 개명(옛 경로가 기준에 없음) = red(실행 불능 아님)" 2 "치환만으로 설명되지 않는다" "실행 불능" "$E" "$OUT"
assert "S14n″ 뿌리 커밋 표지는 «뿌리»(미승인 병합 아님 — 등재 대상이 아니다)" 2 "(뿌리)" "(미승인 병합)" "$E" "$OUT"
P=$(case_repo s14n2)
git -C "$P" checkout -q --orphan unrelated
rewrite "$P/web/static/images/old.png" s14n2; commit_all "$P" root >/dev/null
git -C "$P" mv web/static/images/old.png web/static/images/x.png
sub "$P/tests/web/test_img.py" images/old.png images/x.png; commit_all "$P" c1 >/dev/null
OUT=$(run_backstop "$P" --subst-check "$BASE" HEAD); E=$?
assert "S14n′ 대조: 무관 이력의 뿌리가 기준과 같은 경로를 다른 내용으로 들인 뒤 개명 = red(뿌리 경로도 계보를 끊는다)" 2 "치환만으로 설명되지 않는다" "실행 불능" "$E" "$OUT"
# S14o 는 기준이 대상의 첫 부모 줄기 밖(곁가지 커밋)이라 사슬이 기준이 아닌 트리에서 시작한다
P=$(case_repo s14o)
git -C "$P" checkout -qb side
git -C "$P" rm -q web/static/images/other.png; S14OBASE=$(commit_all "$P" side-base)
git -C "$P" checkout -q -
git -C "$P" mv web/static/images/other.png web/static/images/other_2.png
sub "$P/tests/web/refs.txt" images/other.png images/other_2.png; commit_all "$P" c1 >/dev/null
git -C "$P" -c user.name=t -c user.email=t@t merge -q -s ours side -m merge
OUT=$(run_backstop "$P" --subst-check "$S14OBASE" HEAD); E=$?
assert "S14o 대조: 기준이 첫 부모 줄기 밖 · 기준에서 지운 경로의 개명(옛 경로가 기준에 없음) = red" 2 "치환만으로 설명되지 않는다" - "$E" "$OUT"
# S14h 는 사례 전용 기준 커밋(S3 방식) — 공용 기준에 파일을 더하면 다른 사례의 쌍 계수가 바뀐다
P=$(case_repo s14h)
mkdir -p "$P/web/a/x"
printf 'def f():\n    return 1\n' > "$P/web/a/x/f.py"; printf 'def g():\n    return 2\n' > "$P/web/a/x/g.py"
S14HBASE=$(commit_all "$P" s14h-base)
mkdir -p "$P/web/a/z"; git -C "$P" mv web/a/x/f.py web/a/z/f.py; commit_all "$P" c1 >/dev/null
mkdir -p "$P/web/b/x"; git -C "$P" mv web/a/x/g.py web/b/x/g.py; commit_all "$P" c2 >/dev/null
sub "$P/tests/web/test_m.py" "import web.a.q
" "import web.b.q
"
sub "$P/tests/web/test_m.py" "web.a.q.VALUE" "web.b.q.VALUE"
commit_all "$P" c3 >/dev/null
OUT=$(run_backstop "$P" --subst-check "$S14HBASE" HEAD); E=$?
assert "S14h 대조(X2 M3 커밋 분리판): 파일을 커밋마다 다른 폴더로 옮겨도 폴더 거짓 쌍 없음 = red" 2 "import 구간" - "$E" "$OUT"

# ---------- S15: 대조는 레인 편집뿐 — --build <산출물 폴더> 의 approved-merges.txt(발주자 소유)에 적힌 병합의
# 상류 유입 · docs/ · .dddjango/ · 루트의 .md 는 빼고, 슬라이스 0 대조(slices[0] · 기록 없는 커밋 · 미승인 병합 ·
# 앞선 기능 편집을 잇지 않는 승인 병합 안 몫)는 치환만, 기능 슬라이스 커밋의 테스트 변경은 목록으로 낸다(로드맵 8e)
# 사례마다 산출물 커밋(= git_snapshot)을 기준 위에 얹는다 — 상류 가지 up 은 BASE 에서 갈라져 그 후손이 아니다.
snapshot() { # snapshot <저장소> — 산출물 커밋(git_snapshot) 해시 출력 · 재료 폴더 <저장소>.build(build-state: slices[0]
  # 슬라이스 0 · slices[1] 기능 — 사례 사이 가지 이동이 추적 파일에 막히지 않게 저장소 밖에 둔다 · S15b 는 저장소 안 판)
  mkdir -p "$1/.dddjango-web/run" "$1.build"; echo "# scope" > "$1/.dddjango-web/run/scope.md"
  printf '{"slices": [{"name": "slice-0-debt", "commits": []}, {"name": "slice-1-feature", "commits": []}]}\n' \
    > "$1.build/build-state.json"
  commit_all "$1" snapshot
}
feature() { # feature <저장소> <커밋> — build-state 기능 슬라이스 commits 에 더한다(Coordinator 기록)
  python3 - "$1.build/build-state.json" "$2" <<'PY'
import json, sys
p, sha = sys.argv[1:]
d = json.load(open(p, encoding='utf-8')); d['slices'][1]['commits'].append(sha)
json.dump(d, open(p, 'w', encoding='utf-8'))
PY
}
approve() { echo "$2 main 받기 승인" >> "$1.build/approved-merges.txt"; }   # 발주자 등재
record() { # record <저장소> <슬라이스 번호> <커밋> — build-state 슬라이스 commits 에 더한다(Coordinator 기록)
  python3 - "$1.build/build-state.json" "$2" "$3" <<'PY'
import json, sys
p, i, sha = sys.argv[1:]
d = json.load(open(p, encoding='utf-8')); d['slices'][int(i)]['commits'].append(sha)
json.dump(d, open(p, 'w', encoding='utf-8'))
PY
}
slice0() { # 이미지 개명 + web/ 밖 테스트 치환(명세 슬라이스 0 절 판) · slices[0] 에 기록
  git -C "$1" mv web/static/images/old.png web/static/images/new_image.png
  sub "$1/tests/web/test_img.py" images/old.png images/new_image.png
  record "$1" 0 "$(commit_all "$1" slice-0)"
}
upstream_branch() { git -C "$1" checkout -qb up "$BASE"; }   # BASE 에서 갈라진 up 가지(상류)로 옮긴다
merge() { git -C "$1" -c user.name=t -c user.email=t@t merge -q --no-edit "$2" >/dev/null 2>&1; git -C "$1" rev-parse HEAD; }
check() { run_backstop "$1" --subst-check "$2" HEAD --build "$1.build"; }
P=$(case_repo s15a); SNAP=$(snapshot "$P"); slice0 "$P"
upstream_branch "$P"
echo "DEBUG = False" >> "$P/config/settings.py"
sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() + 0 == 1"
printf 'def test_up():\n    assert True\n' > "$P/tests/web/test_up.py"
mkdir -p "$P/docs"; echo "# up" > "$P/docs/UP.md"
commit_all "$P" upstream >/dev/null; git -C "$P" checkout -q -
MRG=$(merge "$P" up)
OUT=$(check "$P" "$SNAP"); E=$?
assert "S15a′ 대조: 미등재 main 받기 = red(유입이 레인 편집 · 승인 목록 밖 알림)" 2 "승인 목록 밖" - "$E" "$OUT"
approve "$P" "$MRG"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S15a 등재한 main 받기 유입(비테스트 · 테스트 단언 · 새 테스트 · 문서) + 슬라이스 0 = green" 0 "병합 유입 제외 4" "[subst]" "$E" "$OUT"
P=$(case_repo s15b); SNAP=$(snapshot "$P"); slice0 "$P"
mkdir -p "$P/docs/orders/lane"; echo "# 보고" > "$P/docs/orders/lane/REPORT-web.md"; commit_all "$P" report >/dev/null
echo "- 게이트" >> "$P/docs/orders/lane/REPORT-web.md"; commit_all "$P" report2 >/dev/null
cp "$P.build/build-state.json" "$P/.dddjango-web/run/"      # 실제 자리(산출물 폴더 · 미커밋 갱신) 판
OUT=$(run_backstop "$P" --subst-check "$SNAP" HEAD --build "$P/.dddjango-web/run"); E=$?
assert "S15b 발주·보고 문서(docs/ 아래 .md) 커밋 = green · 문서 제외 경로 표시" 0 "문서 제외(docs/ · .dddjango/ · 루트 .md) 1: docs/orders/lane/REPORT-web.md" "[subst]" "$E" "$OUT"
echo "notes" > "$P/docs/orders/lane/NOTE.txt"; commit_all "$P" txt >/dev/null
OUT=$(check "$P" "$SNAP"); E=$?
assert "S15c 대조: web/ 밖 비테스트 .txt 는 문서 제외 밖 = red" 2 "NOTE.txt 테스트 밖 web/ 밖 파일 변경(A)" - "$E" "$OUT"
P=$(case_repo s15d); SNAP=$(snapshot "$P"); slice0 "$P"
echo "# 메모" > "$P/tests/web/NOTES.md"; commit_all "$P" test-md >/dev/null
OUT=$(check "$P" "$SNAP"); E=$?
assert "S15d 대조: 테스트 경로의 .md(기록 없는 커밋) 는 문서 제외 밖 = red" 2 "tests/web/NOTES.md 치환이 아닌 변경(A" - "$E" "$OUT"
P=$(case_repo s15e); SNAP=$(snapshot "$P"); slice0 "$P"
upstream_branch "$P"; printf 'X = 1\n' > "$P/tests/web/up_extra.py"; commit_all "$P" upstream >/dev/null; git -C "$P" checkout -q -
git -C "$P" -c user.name=t -c user.email=t@t merge -q --no-commit up >/dev/null 2>&1
sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() == 2"; MRG=$(commit_all "$P" "merge up"); approve "$P" "$MRG"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S15e 등재 병합 안에 끼운 테스트 편집(앞선 기능 편집 없음) = red · 승인 병합 안 표지" 2 "슬라이스 0 대조 커밋 ${MRG:0:12}(승인 병합 안)" - "$E" "$OUT"
P=$(case_repo s15e2); SNAP=$(snapshot "$P"); slice0 "$P"
upstream_branch "$P"; printf 'X = 1\n' > "$P/tests/web/up_extra.py"; commit_all "$P" upstream >/dev/null; git -C "$P" checkout -q -
git -C "$P" -c user.name=t -c user.email=t@t merge -q --no-commit up >/dev/null 2>&1
echo "DEBUG = True" >> "$P/config/settings.py"; MRG=$(commit_all "$P" "merge up"); approve "$P" "$MRG"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S15e′ 등재 병합 안에 끼운 비테스트 편집 = red · 병합 약칭" 2 "config/settings.py 테스트 밖 web/ 밖 파일 변경(M) — 레인 커밋 ${MRG:0:12}" - "$E" "$OUT"
P=$(case_repo s15f); SNAP=$(snapshot "$P"); slice0 "$P"
upstream_branch "$P"; printf '\n\ndef test_upstream():\n    assert OTHER\n' >> "$P/tests/web/test_img.py"; commit_all "$P" upstream >/dev/null; git -C "$P" checkout -q -
MRG=$(merge "$P" up); approve "$P" "$MRG"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S15f 겹침: 슬라이스 0 이 치환한 테스트를 상류도 고침(등재 · 자동 병합) = green · 목록 없음" 0 "기능 테스트 편집 0" "[subst]" "$E" "$OUT"
sub "$P/tests/web/test_img.py" "    assert OTHER" "    assert not OTHER"; TW=$(commit_all "$P" tweak)
OUT=$(check "$P" "$SNAP"); E=$?
assert "S15g 대조: 겹친 파일의 병합 뒤 단언 변경(기능 기록 없음) = red · 슬라이스 0 대조 커밋" 2 "슬라이스 0 대조 커밋 ${TW:0:12}" "대조 커밋 ${MRG:0:12}" "$E" "$OUT"
feature "$P" "$TW"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S15g′ 같은 편집을 기능 슬라이스 커밋으로 기록 = green · 목록" 0 "tests/web/test_img.py(M) — 커밋 ${TW:0:12}" "[subst]" "$E" "$OUT"
P=$(case_repo s15h); SNAP=$(snapshot "$P"); slice0 "$P"
upstream_branch "$P"; sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() + 0 == 1"; echo "DEBUG = False" >> "$P/config/settings.py"
commit_all "$P" upstream >/dev/null; git -C "$P" checkout -q -
git -C "$P" -c user.name=t -c user.email=t@t merge -q --no-commit up >/dev/null 2>&1
sub "$P/tests/web/test_m.py" "assert web.a.q.VALUE == 3" "assert web.a.q.VALUE == 4"; MRG=$(commit_all "$P" "merge up"); approve "$P" "$MRG"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S15h 상류가 바꾼 테스트를 등재 병합이 상류 판과 다르게 만듦(앞선 기능 편집 없음) = red" 2 "슬라이스 0 대조 커밋 ${MRG:0:12}(승인 병합 안)" - "$E" "$OUT"
sub "$P/config/settings.py" "DEBUG = False" "DEBUG = None"; FX=$(commit_all "$P" fix-settings); feature "$P" "$FX"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S15h′ 상류가 바꾼 비테스트를 레인이 고침(기능 기록이어도) = red · 기준 = 상류 판" 2 "config/settings.py 테스트 밖 web/ 밖 파일 변경(M) — 레인 커밋 ${FX:0:12}(slice-1-feature) · 기준 = 상류 판" - "$E" "$OUT"
P=$(case_repo s15i); SNAP=$(snapshot "$P"); slice0 "$P"
git -C "$P" checkout -qb side; sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() == 2"; SIDE=$(commit_all "$P" side)
git -C "$P" checkout -q -; MRG=$(git -C "$P" -c user.name=t -c user.email=t@t merge -q --no-ff --no-edit side >/dev/null 2>&1; git -C "$P" rev-parse HEAD)
feature "$P" "$SIDE"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S15i 레인 곁가지 병합(미등재) 안의 단언 편집 = red(곁가지 커밋을 기능으로 적어도 병합이 슬라이스 0 대조)" 2 "슬라이스 0 대조 커밋 ${MRG:0:12}" - "$E" "$OUT"
P=$(case_repo s15j); SNAP=$(snapshot "$P"); slice0 "$P"
sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() == 2"; FEAT=$(commit_all "$P" feature)
OUT=$(check "$P" "$SNAP"); E=$?
assert "S15j 기능 기록 없는 커밋의 web/ 밖 테스트 단언 편집 = red(슬라이스 0 대조) · 그 커밋 약칭" 2 "슬라이스 0 대조 커밋 ${FEAT:0:12}" - "$E" "$OUT"
feature "$P" "$FEAT"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S15j′ 기능 슬라이스 커밋으로 기록 = green · G2 목록(파일 · 상태 · 커밋 · 슬라이스)" 0 "기능 슬라이스·병합 테스트 편집 tests/web/test_m.py(M) — 커밋 ${FEAT:0:12}(slice-1-feature)" "[subst]" "$E" "$OUT"
upstream_branch "$P"; echo "DEBUG = False" >> "$P/config/settings.py"; commit_all "$P" upstream >/dev/null; git -C "$P" checkout -q -
MRG=$(merge "$P" up); approve "$P" "$MRG"
git -C "$P" -c user.name=t -c user.email=t@t revert --no-edit "$FEAT" >/dev/null; feature "$P" "$(git -C "$P" rev-parse HEAD)"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S15k 기능 편집 → 등재 병합 → 되돌림 = green · 목록 없음(순변화 0)" 0 "기능 테스트 편집 0" "[subst]" "$E" "$OUT"
P=$(case_repo s15l); SNAP=$(snapshot "$P"); slice0 "$P"
upstream_branch "$P"; sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() + 0 == 1"; commit_all "$P" upstream >/dev/null; git -C "$P" checkout -q -
MRG=$(merge "$P" up); approve "$P" "$MRG"; sub "$P/tests/web/test_m.py" "assert f() + 0 == 1" "assert f() == 1"; UNDO=$(commit_all "$P" undo-upstream)
OUT=$(check "$P" "$SNAP"); E=$?
assert "S15l 기록 없는 커밋이 상류 변경을 기준 판으로 되돌림(누적 diff 0) = red(상류 판 대비 슬라이스 0 대조)" 2 "슬라이스 0 대조 커밋 ${UNDO:0:12}" - "$E" "$OUT"
P=$(case_repo s15m); SNAP=$(snapshot "$P"); slice0 "$P"
upstream_branch "$P"; sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() + 0 == 1"; commit_all "$P" up1 >/dev/null; git -C "$P" checkout -q -
M1=$(merge "$P" up); approve "$P" "$M1"; git -C "$P" checkout -q up
sub "$P/tests/web/test_m.py" "assert f() + 0 == 1" "assert f() + 0 + 0 == 1"; commit_all "$P" up2 >/dev/null; git -C "$P" checkout -q -
M2=$(merge "$P" up); approve "$P" "$M2"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S15m 같은 테스트를 등재한 두 번의 main 받기가 차례로 고침 = green(마지막 상류 판이 기준)" 0 "병합 유입 제외 1" "[subst]" "$E" "$OUT"
P=$(case_repo s15n); SNAP=$(snapshot "$P"); slice0 "$P"; S0=$(git -C "$P" rev-parse HEAD)
sub "$P/tests/web/test_img.py" "assert IMG != OTHER" "assert IMG != OTHER and OTHER"; FEAT=$(commit_all "$P" feature); feature "$P" "$FEAT"
sub "$P/tests/web/test_img.py" 'OTHER = "images/other.png"' 'OTHER = "images/else.png"'; BAD=$(commit_all "$P" reopen)
OUT=$(check "$P" "$SNAP"); E=$?
assert "S15n 한 테스트 파일에 슬라이스 0 치환 · 기능 편집 · 기록 없는 비치환 편집 = red 는 마지막 구간만" 2 "슬라이스 0 대조 커밋 ${BAD:0:12}" "대조 커밋 ${S0:0:12}" "$E" "$OUT"
P=$(case_repo s15p); SNAP=$(snapshot "$P"); slice0 "$P"
git -C "$P" checkout -qb fork "$BASE"; sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() == 2"; commit_all "$P" fork-edit >/dev/null
git -C "$P" checkout -q -; MRG=$(merge "$P" fork); git -C "$P" branch -qD fork
OUT=$(check "$P" "$SNAP"); E=$?
assert "S15p 기준 앞에서 갈라진 곁가지의 단언 편집 병합(세탁) · 미등재 = red" 2 "슬라이스 0 대조 커밋 ${MRG:0:12}" - "$E" "$OUT"
approve "$P" "$MRG"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S15p′ 발주자가 그 병합을 등재하면 상류로 본다 · ^2 를 담은 ref 가 HEAD 가지뿐 = 역방향/합성 병합 의심 알림" 0 "역방향/합성 병합 의심" "[subst]" "$E" "$OUT"

# ---------- S16: --build 재료 fail-closed — 승인 목록 형식(dddjango approved-merges 와 같은 뜻) · build-state
P=$(case_repo s16); SNAP=$(snapshot "$P"); slice0 "$P"; S0=$(git -C "$P" rev-parse HEAD); MAIN=$(git -C "$P" symbolic-ref --short HEAD)
echo "not-a-sha 메모" > "$P.build/approved-merges.txt"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S16a 승인 목록 줄 형식 오류 = 실행 불능" 1 "줄 형식 오류" - "$E" "$OUT"
echo "$S0 비병합" > "$P.build/approved-merges.txt"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S16b 승인 목록에 비병합 커밋 = 실행 불능" 1 "두 부모 병합만" - "$E" "$OUT"
git -C "$P" checkout -qb other "$BASE"; git -C "$P" checkout -qb other2; echo x > "$P/docs.txt"; commit_all "$P" o2 >/dev/null
git -C "$P" checkout -q other; OM=$(git -C "$P" -c user.name=t -c user.email=t@t merge -q --no-ff --no-edit other2 >/dev/null 2>&1; git -C "$P" rev-parse HEAD); git -C "$P" checkout -q "$MAIN"
echo "$OM 다른 가지" > "$P.build/approved-merges.txt"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S16c 기준..대상 첫 부모 사슬 밖 병합 등재 = 실행 불능" 1 "사슬 밖" - "$E" "$OUT"
git -C "$P" checkout -qb pre "$BASE"; git -C "$P" checkout -qb pre2; echo y > "$P/pre.txt"; commit_all "$P" p2 >/dev/null
git -C "$P" checkout -q pre; PM=$(merge "$P" pre2); git -C "$P" checkout -q "$MAIN"
printf '// 발주자 주석\n\n%s 다른 가지\n' "$PM" > "$P.build/approved-merges.txt"
OUT=$(run_backstop "$P" --subst-check "$PM" HEAD --build "$P.build"); E=$?
assert "S16d 대조: 기준이 대상 사슬 밖이면 목록 판정 불가 = 실행 불능" 1 "첫 부모 사슬 밖" - "$E" "$OUT"
rm "$P.build/approved-merges.txt"
OUT=$(run_backstop "$P" --subst-check "$SNAP" HEAD --build "$T/no-such-folder"); E=$?
assert "S16e --build 폴더 없음 = 실행 불능" 1 "산출물 폴더가 없다" - "$E" "$OUT"
mkdir -p "$T/s16-empty"
OUT=$(run_backstop "$P" --subst-check "$SNAP" HEAD --build "$T/s16-empty"); E=$?
assert "S16f build-state.json 없음 = 실행 불능" 1 "build-state.json 을 읽을 수 없다" - "$E" "$OUT"
mkdir -p "$T/s16-bad"; echo '{"slices": {"name": "x"}}' > "$T/s16-bad/build-state.json"
OUT=$(run_backstop "$P" --subst-check "$SNAP" HEAD --build "$T/s16-bad"); E=$?
assert "S16g build-state slices 가 목록 아님 = 실행 불능" 1 "객체 목록이 아니다" - "$E" "$OUT"
sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() == 2"; FEAT=$(commit_all "$P" feature)
python3 - "$P.build/build-state.json" "$FEAT" <<'PY'
import json, sys
p, sha = sys.argv[1:]
d = json.load(open(p, encoding='utf-8')); d['slices'][0]['commits'].append(sha); d['slices'][1]['commits'] += [sha, 'deadbeefcafe']
json.dump(d, open(p, 'w', encoding='utf-8'))
PY
OUT=$(check "$P" "$SNAP"); E=$?
assert "S16h 슬라이스 0 과 기능 양쪽에 적힌 커밋 = red(기록 모순)" 2 "build-state 기록 모순 — ${FEAT:0:12} 가 slices[0] 과 slice-1-feature 양쪽에 있다" - "$E" "$OUT"
assert "S16h′ 풀 수 없는 기록 알림" 2 "기록 deadbeefcafe 를 풀 수 없다" - "$E" "$OUT"
OUT=$(run_backstop "$P" --debt-scan --build "$P.build"); E=$?
assert "S16i --build 는 --subst-check 전용 = 사용 오류" 1 "--build 는 --subst-check 전용" - "$E" "$OUT"
P=$(case_repo s16j); git -C "$P" checkout -qb early; echo z > "$P/early.txt"; commit_all "$P" early >/dev/null
git -C "$P" checkout -q -; EM=$(git -C "$P" -c user.name=t -c user.email=t@t merge -q --no-ff --no-edit early >/dev/null 2>&1; git -C "$P" rev-parse HEAD)
SNAP=$(snapshot "$P"); slice0 "$P"
printf '// 발주자 주석 — 앞 실행 병합\n\n%s 기준 이전\n' "$EM" > "$P.build/approved-merges.txt"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S16j 주석 · 빈 줄 · 기준 이전 병합 = 판정 불참 알림 · green" 0 "기준 이전 — 판정 불참" "[subst]" "$E" "$OUT"
P=$(case_repo s16k); SNAP=$(snapshot "$P"); slice0 "$P"
sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() == 2"; ED=$(commit_all "$P" edit)
printf '{"slices": [{"name": "slice-1-data", "commits": ["%s"]}]}\n' "$ED" > "$P.build/build-state.json"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S16k slices[0] 은 이름과 무관하게 슬라이스 0 = red" 2 "슬라이스 0 대조 커밋 ${ED:0:12}(slices[0])" - "$E" "$OUT"

# ---------- S17: 리뷰 R8e 반례(도구 M1·M2·m1~m4·n2) — 병합 안 레인 몫 · 앱 .md · 상류 변경 버림 · 기록 검증 · 표지 · 얕은 이력
refactor_state() { printf '{"slices": [{"name": "slice-0-debt", "commits": []}]}\n' > "$1.build/build-state.json"; }
merge_evil() { # merge_evil <저장소> <편집 명령…> — up 을 --no-commit 으로 받고 편집을 끼워 커밋 · 해시 출력
  local P="$1"; shift
  git -C "$P" -c user.name=t -c user.email=t@t merge -q --no-commit up >/dev/null 2>&1; "$@"; commit_all "$P" "merge up"
}
P=$(case_repo s17a1); SNAP=$(snapshot "$P"); refactor_state "$P"; slice0 "$P"
upstream_branch "$P"; printf 'X = 1\n' > "$P/tests/web/up_extra.py"; commit_all "$P" upstream >/dev/null; git -C "$P" checkout -q -
MRG=$(merge_evil "$P" sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() == 2"); approve "$P" "$MRG"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17a1 리팩토링 판(slices 하나) · 등재 병합 안 끼운 단언 편집 = red" 2 "슬라이스 0 대조 커밋 ${MRG:0:12}(승인 병합 안)" - "$E" "$OUT"
P=$(case_repo s17a2); SNAP=$(snapshot "$P"); refactor_state "$P"; slice0 "$P"
upstream_branch "$P"; sub "$P/tests/web/test_img.py" "assert IMG != OTHER" "assert IMG != OTHER, 'up'"; commit_all "$P" upstream >/dev/null; git -C "$P" checkout -q -
git -C "$P" -c user.name=t -c user.email=t@t merge -q --no-commit up >/dev/null 2>&1
printf 'IMG = "images/new_image.png"\nOTHER = "images/other.png"\n\n\ndef test_img():\n    assert IMG, %s\n' "\"'up'\"" > "$P/tests/web/test_img.py"
MRG=$(commit_all "$P" "merge up"); approve "$P" "$MRG"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17a2 리팩토링 판 · 상류가 바꾼 테스트의 충돌 해소에 단언 변경을 섞음 = red" 2 "슬라이스 0 대조 커밋 ${MRG:0:12}(승인 병합 안)" - "$E" "$OUT"
P=$(case_repo s17a3); SNAP=$(snapshot "$P"); slice0 "$P"
upstream_branch "$P"; echo "DEBUG = False" >> "$P/config/settings.py"; commit_all "$P" upstream >/dev/null; git -C "$P" checkout -q -
MRG=$(merge_evil "$P" sub "$P/tests/web/test_m.py" "assert h() == 2 + marker - 1" "assert h() is not None"); approve "$P" "$MRG"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17a3 슬라이스 0 끝 ④(기능 커밋 0) · 등재 병합 안 단언 편집 = red" 2 "슬라이스 0 대조 커밋 ${MRG:0:12}(승인 병합 안)" - "$E" "$OUT"
sub "$P/tests/web/test_m.py" "assert h() is not None" "assert h() == 2 + marker - 1"; commit_all "$P" undo >/dev/null
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17a3′ 되돌림 커밋(기록 없음) = green(병합 안 몫이 연 구간이 순변화 0)" 0 "기능 테스트 편집 0" "[subst]" "$E" "$OUT"
sub "$P/tests/web/test_m.py" "assert h() == 2 + marker - 1" "assert h() is not None"; FE=$(commit_all "$P" feat); feature "$P" "$FE"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17a3″ 같은 편집을 기능 커밋으로 = green · 목록" 0 "tests/web/test_m.py(M) — 커밋 ${FE:0:12}(slice-1-feature)" "[subst]" "$E" "$OUT"
P=$(case_repo s17fm); SNAP=$(snapshot "$P"); slice0 "$P"
sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() == 1 and h() == 2"; FE=$(commit_all "$P" feat); feature "$P" "$FE"
upstream_branch "$P"; sub "$P/tests/web/test_m.py" 'assert "web.a.m.f".endswith("f")' 'assert "web.a.m.f".endswith("f")  # up'; commit_all "$P" upstream >/dev/null; git -C "$P" checkout -q -
MRG=$(merge "$P" up); approve "$P" "$MRG"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17fm 기능 편집 뒤 상류도 같은 파일을 고쳐 등재 자동 병합 = green · 목록(기능 · 병합 안)" 0 "커밋 ${FE:0:12}(slice-1-feature) ${MRG:0:12}(승인 병합 안)" "[subst]" "$E" "$OUT"
P=$(case_repo s17cf); SNAP=$(snapshot "$P"); slice0 "$P"
upstream_branch "$P"; sub "$P/tests/web/test_img.py" 'IMG = "images/old.png"' 'IMG = "images/old.png"  # up'; commit_all "$P" upstream >/dev/null; git -C "$P" checkout -q -
git -C "$P" -c user.name=t -c user.email=t@t merge -q --no-edit up >/dev/null 2>&1; MRG=$(commit_all "$P" "merge up with markers"); approve "$P" "$MRG"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17cf 충돌 표지를 남긴 테스트 파일을 등재 병합이 들임 = 실행 불능(파싱 실패)" 1 "파싱 실패" - "$E" "$OUT"
P=$(case_repo s17a4); SNAP=$(snapshot "$P"); slice0 "$P"
upstream_branch "$P"; echo "SECURE = True" >> "$P/config/settings.py"; commit_all "$P" upstream >/dev/null; git -C "$P" checkout -q -
MRG=$(merge_evil "$P" git -C "$P" checkout -q HEAD -- config/settings.py); approve "$P" "$MRG"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17a4 등재 병합이 상류의 비테스트 변경을 버림 = red(기준 = 상류 판)" 2 "config/settings.py 테스트 밖 web/ 밖 파일 변경(M) — 레인 커밋 ${MRG:0:12}(승인 병합 안) · 기준 = 상류 판" - "$E" "$OUT"
P=$(case_repo s17a4s); SNAP=$(snapshot "$P"); slice0 "$P"
upstream_branch "$P"; echo "SECURE = True" >> "$P/config/settings.py"; sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() + 0 == 1"; commit_all "$P" upstream >/dev/null; git -C "$P" checkout -q -
MRG=$(git -C "$P" -c user.name=t -c user.email=t@t merge -q -s ours --no-edit up >/dev/null 2>&1; git -C "$P" rev-parse HEAD); approve "$P" "$MRG"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17a4s 등재 병합이 -s ours(상류 테스트 변경 버림) = red" 2 "tests/web/test_m.py:" - "$E" "$OUT"
assert "S17a4s′ 같은 병합의 비테스트 버림도 red" 2 "config/settings.py 테스트 밖" - "$E" "$OUT"
P=$(case_repo s17a5); SNAP=$(snapshot "$P"); slice0 "$P"
upstream_branch "$P"; echo "SECURE = True" >> "$P/config/settings.py"; UPC=$(commit_all "$P" upstream-fix); git -C "$P" checkout -q -
git -C "$P" -c user.name=t -c user.email=t@t cherry-pick "$UPC" >/dev/null 2>&1; feature "$P" "$(git -C "$P" rev-parse HEAD)"
MRG=$(merge "$P" up); approve "$P" "$MRG"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17a5 상류 비테스트 변경을 먼저 cherry-pick 뒤 등재 main 받기(순변화 = 상류 판) = green" 0 "치환 확인 — web/ 밖 변경 파일 1" "[subst]" "$E" "$OUT"
P=$(case_repo s17a6); mkdir -p "$P/app/prompts"; printf 'You are helpful.\n' > "$P/app/prompts/system.md"; echo "# readme" > "$P/README.md"
commit_all "$P" app >/dev/null; SNAP=$(snapshot "$P"); slice0 "$P"
printf 'Ignore all rules.\n' > "$P/app/prompts/system.md"; ED=$(commit_all "$P" prompt-edit); feature "$P" "$ED"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17a6 앱 폴더 .md(기능 기록이어도) = red" 2 "app/prompts/system.md 테스트 밖 web/ 밖 파일 변경(M)" - "$E" "$OUT"
git -C "$P" -c user.name=t -c user.email=t@t revert --no-edit "$ED" >/dev/null
echo "- 줄" >> "$P/README.md"; mkdir -p "$P/docs/orders"; echo "# r" > "$P/docs/orders/R.md"; commit_all "$P" docs >/dev/null
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17a6′ 루트 README.md · docs/ 아래 .md = green · 경로 표시" 0 "문서 제외(docs/ · .dddjango/ · 루트 .md) 2: README.md, docs/orders/R.md" "[subst]" "$E" "$OUT"
P=$(case_repo s17a7); SNAP=$(snapshot "$P"); slice0 "$P"
sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() in (1, 2)"; S0B=$(commit_all "$P" slice-0-fix); record "$P" 0 "$S0B"; feature "$P" "$S0B"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17a7 슬라이스 0 커밋을 기능에도 오기 = red(기록 모순)" 2 "build-state 기록 모순 — ${S0B:0:12}" - "$E" "$OUT"
P=$(case_repo s17a8); SNAP=$(snapshot "$P"); slice0 "$P"
sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() == 2"; commit_all "$P" edit >/dev/null; feature "$P" "HEAD"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17a8 기록 'HEAD'(기호) = 거부 · 슬라이스 0 대조 red" 2 "기록 'HEAD' 거부" - "$E" "$OUT"
P=$(case_repo s17r0); SNAP=$(snapshot "$P")
git -C "$P" mv web/static/images/old.png web/static/images/new_image.png; sub "$P/tests/web/test_img.py" images/old.png images/new_image.png; commit_all "$P" slice-0 >/dev/null
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17r0 slices[0] 기록 없음 = 실행 불능" 1 "슬라이스 0 커밋 기록이 없다" - "$E" "$OUT"
sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() == 2"; FE=$(commit_all "$P" feat); feature "$P" "$FE"
sub "$P/tests/web/test_img.py" "assert IMG != OTHER" "assert IMG != OTHER  # s0"; record "$P" 0 "$(commit_all "$P" slice-0-late)"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17r1 기능 기록이 첫 슬라이스 0 기록보다 앞 = 슬라이스 0 대조 red · 알림" 2 "첫 슬라이스 0 커밋보다 앞" - "$E" "$OUT"
P=$(case_repo s17a14); SNAP=$(snapshot "$P"); slice0 "$P"; S0=$(git -C "$P" rev-parse HEAD)
sub "$P/tests/web/test_img.py" "assert IMG != OTHER" "assert IMG != OTHER and IMG"; FE=$(commit_all "$P" feat)
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17a14 한 구간의 slices[0] 커밋 · 기록 없는 커밋 = 출처 표지로 가름" 2 "슬라이스 0 대조 커밋 ${S0:0:12}(slices[0]) ${FE:0:12}(기록 없음)" - "$E" "$OUT"
feature "$P" "$FE"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17a14′ 기록 없는 쪽을 기능으로 적으면 = green · 목록" 0 "tests/web/test_img.py(M) — 커밋 ${FE:0:12}(slice-1-feature)" "[subst]" "$E" "$OUT"
P=$(case_repo s17a15); SNAP=$(snapshot "$P"); slice0 "$P"
sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() == 2"; FIRST=$(commit_all "$P" c1)
for k in 2 3 4 5 6 7; do echo "# c$k" >> "$P/tests/web/test_m.py"; commit_all "$P" "c$k" >/dev/null; done
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17a15 기록 없는 커밋 7개 = 줄에 첫 커밋도 싣는다(자르지 않음)" 2 "${FIRST:0:12}(기록 없음)" "(기록 없음) 외" "$E" "$OUT"
P=$(case_repo s17j); SNAP=$(snapshot "$P"); slice0 "$P"
upstream_branch "$P"; sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() + 0 == 1"; commit_all "$P" upstream >/dev/null; git -C "$P" checkout -q -
MRG=$(merge "$P" up); feature "$P" "$MRG"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17j 미승인 병합을 기능 기록에 적음 = 버림 알림 · red" 2 "기록 ${MRG:0:12} 는 병합 — 버림" - "$E" "$OUT"
P=$(case_repo s17f1); git -C "$P" checkout -qb lane/x; SNAP=$(snapshot "$P"); slice0 "$P"
git -C "$P" checkout -q --detach "$BASE"; sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() == 2"; FK=$(commit_all "$P" fork-edit)
git -C "$P" checkout -q lane/x; MRG=$(merge "$P" "$FK"); approve "$P" "$MRG"
git init -q --bare "$T/s17f1-remote.git"; git -C "$P" remote add pub "$T/s17f1-remote.git"; git -C "$P" push -q pub lane/x 2>/dev/null
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17f1 푸시된 레인(pub/lane/x 가 ^2 를 담음) · 세탁 병합 등재 = 역방향/합성 알림" 0 "역방향/합성 병합 의심" "[subst]" "$E" "$OUT"
P=$(case_repo s17w); SNAP=$(snapshot "$P"); slice0 "$P"
upstream_branch "$P"; for k in 1 2 3; do echo "U$k = 1" >> "$P/config/settings.py"; commit_all "$P" "up$k" >/dev/null; done; git -C "$P" checkout -q -
MRG=$(merge "$P" up); approve "$P" "$MRG"
SH="$T/s17w-shallow"; git clone -q --depth 3 "file://$P" "$SH" 2>/dev/null; cp -r "$P.build" "$SH.build"
OUT=$(run_backstop "$SH" --subst-check "$SNAP" HEAD --build "$SH.build"); E=$?
assert "S17w 얕은 이력 · 승인 병합 = 실행 불능(unshallow 안내)" 1 "git fetch --unshallow" - "$E" "$OUT"
P=$(case_repo s17w2); SNAP=$(snapshot "$P"); slice0 "$P"; MAIN=$(git -C "$P" symbolic-ref --short HEAD)
git -C "$P" checkout -q --orphan alien; git -C "$P" rm -rqf . >/dev/null; mkdir -p "$P/alien"; echo a > "$P/alien/a.txt"; commit_all "$P" alien >/dev/null
git -C "$P" checkout -q "$MAIN"; MRG=$(git -C "$P" -c user.name=t -c user.email=t@t merge -q --allow-unrelated-histories --no-edit alien >/dev/null 2>&1; git -C "$P" rev-parse HEAD); approve "$P" "$MRG"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17w2 공통 조상 없는 승인 병합 = 실행 불능" 1 "공통 조상을 찾지 못함" - "$E" "$OUT"
P=$(case_repo s17x); SNAP=$(snapshot "$P"); slice0 "$P"
chmod +x "$P/tests/web/test_m.py"; commit_all "$P" chmod >/dev/null
OUT=$(check "$P" "$SNAP"); E=$?
assert "S17x 테스트 파일 실행 비트만 바꿈 = green(git 과 같게 타입 변경 아님)" 0 "치환 확인" "[subst]" "$E" "$OUT"
P=$(case_repo s17w3); echo x1 > "$P/x1.txt"; commit_all "$P" x1 >/dev/null; echo x2 > "$P/x2.txt"; X2=$(commit_all "$P" x2)
SNAP=$(snapshot "$P"); slice0 "$P"
git -C "$P" checkout -qb up "$X2"; echo "DEBUG = False" >> "$P/config/settings.py"; commit_all "$P" upstream >/dev/null; git -C "$P" checkout -q -
MRG=$(merge "$P" up); approve "$P" "$MRG"
SH="$T/s17w3-shallow"; git clone -q --depth 4 "file://$P" "$SH" 2>/dev/null; cp -r "$P.build" "$SH.build"
OUT=$(run_backstop "$SH" --subst-check "$SNAP" HEAD --build "$SH.build"); E=$?
assert "S17w3 얕은 이력(공통 조상은 있음) · 승인 병합 = 실행 불능" 1 "얕은 이력 — 승인 병합 판정 불가" - "$E" "$OUT"
# S17o 는 S14o 처럼 기준이 첫 부모 줄기 밖 — 기준 쪽에서만 바뀐 테스트는 사슬에 걸음이 없어도 기준 판 대비로 대조한다
P=$(case_repo s17o)
git -C "$P" checkout -qb side
sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() == 2"; S17OBASE=$(commit_all "$P" side-base)
git -C "$P" checkout -q -
git -C "$P" -c user.name=t -c user.email=t@t merge -q -s ours side -m merge
OUT=$(run_backstop "$P" --subst-check "$S17OBASE" HEAD); E=$?
assert "S17o 기준이 첫 부모 줄기 밖 · 기준 쪽에서만 바뀐 테스트(사슬 걸음 없음) = red(기준 판 대비)" 2 "import 밖 본문이 치환만으로 설명되지 않는다" "실행 불능" "$E" "$OUT"

# ---------- S18: 리뷰 R8e 구현(도구) 반례 — 사슬 밖 기준 · 리팩토링 mode · 병합 안 삭제 · 문서 자리 경계 · 비테스트 모드 · U 뒤 M
P=$(case_repo s18o); MAIN=$(git -C "$P" symbolic-ref --short HEAD); git -C "$P" checkout -qb side
sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() == 2"; S18OBASE=$(commit_all "$P" side-base)
git -C "$P" checkout -q "$MAIN"; git -C "$P" -c user.name=t -c user.email=t@t merge -q -s ours side -m merge
mkdir -p "$P.build"; printf '{"slices": [{"name": "slice-0-debt", "commits": []}, {"name": "slice-1-feature", "commits": []}]}\n' > "$P.build/build-state.json"
slice0 "$P"; sub "$P/tests/web/test_m.py" 'assert "web.a.m.f".endswith("f")' 'assert "web.a.m.f".endswith("f")  # feat'; feature "$P" "$(commit_all "$P" feat)"
OUT=$(check "$P" "$S18OBASE"); E=$?
assert "S18o --build 인데 기준이 첫 부모 사슬 밖(첫 걸음이 기능) = 실행 불능" 1 "첫 부모 사슬 밖" "기능 슬라이스·병합 테스트 편집" "$E" "$OUT"
P=$(case_repo s18r); SNAP=$(snapshot "$P")
printf '{"mode": "refactor", "slices": [{"name": "slice-0-debt", "commits": []}, {"name": "slice-1-rework", "commits": []}]}\n' > "$P.build/build-state.json"
slice0 "$P"; sub "$P/tests/web/test_img.py" "assert IMG != OTHER" "assert IMG"; record "$P" 1 "$(commit_all "$P" rework)"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S18r build-state mode=refactor 의 둘째 슬라이스 기록 = 슬라이스 0 대조 red" 2 "슬라이스 0 대조 커밋" "기능 슬라이스·병합 테스트 편집" "$E" "$OUT"
assert "S18r′ mode=refactor 재분류 알림" 2 "[info] build-state mode=refactor — slice-1-rework 기록" - "$E" "$OUT"
P=$(case_repo s18d); SNAP=$(snapshot "$P"); slice0 "$P"
upstream_branch "$P"; echo "DEBUG = False" >> "$P/config/settings.py"; commit_all "$P" up >/dev/null; git -C "$P" checkout -q -
MRG=$(merge_evil "$P" git -C "$P" rm -q tests/web/test_m.py); approve "$P" "$MRG"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S18d 등재 병합 안에서 테스트 파일 삭제(상류는 안 건드림) = red" 2 "tests/web/test_m.py 치환이 아닌 변경(D" - "$E" "$OUT"
P=$(case_repo s18m); SNAP=$(snapshot "$P"); slice0 "$P"; mkdir -p "$P/pkg" "$P/app/docs"; echo a > "$P/pkg/README.md"; echo b > "$P/app/docs/P.md"; commit_all "$P" md >/dev/null
OUT=$(check "$P" "$SNAP"); E=$?
assert "S18m 한 단 폴더 README.md · 앱 안 docs/ 의 .md = red(문서 자리 밖)" 2 "pkg/README.md 테스트 밖" "[info] 문서 제외" "$E" "$OUT"
assert "S18m′ 앱 안 docs/ .md 도 red" 2 "app/docs/P.md 테스트 밖" - "$E" "$OUT"
P=$(case_repo s18x); SNAP=$(snapshot "$P"); slice0 "$P"; chmod +x "$P/config/settings.py"; commit_all "$P" chmod >/dev/null
OUT=$(check "$P" "$SNAP"); E=$?
assert "S18x 비테스트 파일 실행 비트만 = red(비테스트는 모드도 변경)" 2 "config/settings.py 테스트 밖 web/ 밖 파일 변경(M)" - "$E" "$OUT"
P=$(case_repo s18u); SNAP=$(snapshot "$P"); slice0 "$P"
upstream_branch "$P"; sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() + 0 == 1"; commit_all "$P" up1 >/dev/null; git -C "$P" checkout -q -
A1=$(merge "$P" up); approve "$P" "$A1"; git -C "$P" checkout -q up; echo "U2 = 1" >> "$P/config/settings.py"; commit_all "$P" up2 >/dev/null; git -C "$P" checkout -q -
A2=$(merge_evil "$P" sub "$P/tests/web/test_m.py" "assert web.a.q.VALUE == 3" "assert web.a.q.VALUE == 4"); approve "$P" "$A2"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S18u 등재 병합 유입(U) 뒤 둘째 등재 병합 안 단언 편집(앞선 기능 없음) = red" 2 "슬라이스 0 대조 커밋 ${A2:0:12}(승인 병합 안)" - "$E" "$OUT"
# S18 구현 리뷰 문면 반례 — 미등재 main 받기의 비테스트는 복원 대상이 아니다 · 루트 에이전트 지침 · (A) 복원 · 병합 안 되돌림 기록
P=$(case_repo s18v); SNAP=$(snapshot "$P"); slice0 "$P"
upstream_branch "$P"; echo "DEBUG = False" >> "$P/config/settings.py"; commit_all "$P" up >/dev/null; git -C "$P" checkout -q -
MRG=$(merge "$P" up)
OUT=$(check "$P" "$SNAP"); E=$?
assert "S18v 미등재 main 받기의 비테스트 = 병합 유입 줄(«테스트 밖» 줄 아님 · 등재 먼저)" 2 "config/settings.py 승인 목록 밖 병합 유입(M) — 레인 커밋 ${MRG:0:12}(미승인 병합) — 등재 먼저(복원하지 않는다)" "테스트 밖 web/ 밖 파일 변경" "$E" "$OUT"
git -C "$P" checkout -q "$SNAP" -- config/settings.py; RS=$(commit_all "$P" restore)
OUT=$(check "$P" "$SNAP"); E=$?
assert "S18v′ 그 줄을 git_snapshot 판 복원으로 풀어도(main 변경 되돌림) = red 로 남는다(병합 줄)" 2 "병합 ${MRG:0:12}(미승인 병합) 승인 목록 밖 병합이 1경로를 들였다(config/settings.py) — 등재 먼저" - "$E" "$OUT"
approve "$P" "$MRG"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S18v″ 등재하면 그 복원이 상류 판 대비 어긋남 = red(기준 = 상류 판)" 2 "config/settings.py 테스트 밖 web/ 밖 파일 변경(M) — 레인 커밋 ${RS:0:12}(기록 없음) · 기준 = 상류 판" - "$E" "$OUT"
git -C "$P" checkout -q "$MRG^2" -- config/settings.py; commit_all "$P" upstream-restore >/dev/null
OUT=$(check "$P" "$SNAP"); E=$?
assert "S18v‴ 줄의 기준 판(상류 판)으로 복원 = green" 0 "병합 유입 제외 1" "[subst]" "$E" "$OUT"
P=$(case_repo s18w); SNAP=$(snapshot "$P"); slice0 "$P"
upstream_branch "$P"; echo "DEBUG = False" >> "$P/config/settings.py"; commit_all "$P" up >/dev/null; git -C "$P" checkout -q -
MRG=$(merge "$P" up); echo "LANE = 1" >> "$P/config/settings.py"; FE=$(commit_all "$P" lane-edit); feature "$P" "$FE"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S18w 미등재 병합 유입 경로를 레인도 고침 = 병합 유입 줄(두 표지) · «테스트 밖» 줄 아님" 2 "config/settings.py 승인 목록 밖 병합 유입(M) — 레인 커밋 ${MRG:0:12}(미승인 병합) ${FE:0:12}(slice-1-feature) — 등재 먼저" "테스트 밖 web/ 밖 파일 변경" "$E" "$OUT"
P=$(case_repo s18t); SNAP=$(snapshot "$P"); slice0 "$P"
upstream_branch "$P"; sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() + 0 == 1"; commit_all "$P" up >/dev/null; git -C "$P" checkout -q -
MRG=$(merge "$P" up); git -C "$P" checkout -q "$SNAP" -- tests/web/test_m.py; commit_all "$P" undo-main-test >/dev/null
OUT=$(check "$P" "$SNAP"); E=$?
assert "S18t 테스트만 들인 미등재 main 받기를 되돌림(문면 위반) = red 로 남는다(병합 줄)" 2 "병합 ${MRG:0:12}(미승인 병합) 승인 목록 밖 병합이 1경로를 들였다(tests/web/test_m.py) — 등재 먼저" - "$E" "$OUT"
P=$(case_repo s18c); echo "# agents" > "$P/CLAUDE.md"; commit_all "$P" agents >/dev/null; SNAP=$(snapshot "$P"); slice0 "$P"
echo "- 새 규칙" >> "$P/CLAUDE.md"; commit_all "$P" claude-md >/dev/null
OUT=$(check "$P" "$SNAP"); E=$?
assert "S18c 루트 에이전트 지침 CLAUDE.md = red(문서 자리 아님)" 2 "CLAUDE.md 테스트 밖 web/ 밖 파일 변경(M)" "[info] 문서 제외" "$E" "$OUT"
P=$(case_repo s18c2); echo "# a" > "$P/AGENTS.md"; echo "# c" > "$P/claude.md"; commit_all "$P" agents >/dev/null; SNAP=$(snapshot "$P"); slice0 "$P"
echo "- 새 규칙" >> "$P/AGENTS.md"; echo "- 새 규칙" >> "$P/claude.md"; commit_all "$P" guides >/dev/null
OUT=$(check "$P" "$SNAP"); E=$?
assert "S18c′ 루트 AGENTS.md = red" 2 "AGENTS.md 테스트 밖 web/ 밖 파일 변경(M)" "[info] 문서 제외" "$E" "$OUT"
assert "S18c″ 루트 지침 이름은 대소문자 무관(claude.md) = red" 2 "claude.md 테스트 밖 web/ 밖 파일 변경(M)" - "$E" "$OUT"
P=$(case_repo s18a); SNAP=$(snapshot "$P"); slice0 "$P"
mkdir -p "$P/docs/orders"; echo "<p>r</p>" > "$P/docs/orders/gate.html"; FE=$(commit_all "$P" gate-html); feature "$P" "$FE"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S18a 레인이 더한 비테스트(A · 비 .md 문서) = red" 2 "docs/orders/gate.html 테스트 밖 web/ 밖 파일 변경(A)" - "$E" "$OUT"
git -C "$P" rm -q -- docs/orders/gate.html; commit_all "$P" rm-added >/dev/null
OUT=$(check "$P" "$SNAP"); E=$?
assert "S18a′ 판에 없는 (A) 경로는 git rm 복원 커밋 = green" 0 "치환 확인" "[subst]" "$E" "$OUT"
P=$(case_repo s18b); SNAP=$(snapshot "$P"); slice0 "$P"
upstream_branch "$P"; echo "DEBUG = False" >> "$P/config/settings.py"; commit_all "$P" upstream >/dev/null; git -C "$P" checkout -q -
MRG=$(merge_evil "$P" sub "$P/tests/web/test_m.py" "assert f() == 1" "assert f() == 2"); approve "$P" "$MRG"
sub "$P/tests/web/test_m.py" "assert f() == 2" "assert f() == 1"; RV=$(commit_all "$P" undo-merge-edit); feature "$P" "$RV"
OUT=$(check "$P" "$SNAP"); E=$?
assert "S18b (승인 병합 안) 되돌림 커밋을 기능으로 기록 = red 로 남는다(구간이 닫히지 않음)" 2 "슬라이스 0 대조 커밋 ${MRG:0:12}(승인 병합 안)" - "$E" "$OUT"
python3 - "$P.build/build-state.json" "$RV" <<'PY'
import json, sys
p, sha = sys.argv[1:]
d = json.load(open(p, encoding='utf-8')); d['slices'][1]['commits'].remove(sha); d['slices'][0]['commits'].append(sha)
json.dump(d, open(p, 'w', encoding='utf-8'))
PY
OUT=$(check "$P" "$SNAP"); E=$?
assert "S18b′ 같은 되돌림을 slices[0](슬라이스 0 반송)으로 기록 = green" 0 "치환 확인" "[subst]" "$E" "$OUT"
P=$(case_repo s18n); SNAP=$(snapshot "$P"); slice0 "$P"
echo "# amend" >> "$P/tests/web/refs.txt"; git -C "$P" add -A; git -C "$P" -c user.name=t -c user.email=t@t commit -q --amend --no-edit
OUT=$(check "$P" "$SNAP"); E=$?
assert "S18n 기록한 슬라이스 0 커밋을 amend = 실행 불능 · 버린 사유를 함께 싣는다" 1 "기록이 없다 — 적은 뒤 다시(build-state slice-0-debt 기록" - "$E" "$OUT"

# ---------- S19: 2.0.0 영구 테스트 뿌리 web_test/ — 그 안의 비 .py 파일도 테스트 파일(치환만 green · 판정 변경 red)
P="$T/s19"; mkdir -p "$P/web/a" "$P/web_test/a"
: > "$P/web/__init__.py"; : > "$P/web/a/__init__.py"; printf 'def f():\n    return 1\n' > "$P/web/a/m.py"
printf 'target: web.a.m.f\nexpect: 1\n' > "$P/web_test/a/cases.yaml"
git -C "$P" init -q; B19=$(commit_all "$P" base)
mkdir -p "$P/web/b"; : > "$P/web/b/__init__.py"; git -C "$P" mv web/a/m.py web/b/m.py
sub "$P/web_test/a/cases.yaml" "web.a.m.f" "web.b.m.f"; commit_all "$P" move >/dev/null
OUT=$(run_backstop "$P" --subst-check "$B19" HEAD); E=$?
assert "S19a web_test/ 비 .py 파일의 경로 치환만 = green(테스트 파일)" 0 "치환 확인 — web/ 밖 변경 파일 1" "[subst]" "$E" "$OUT"
sub "$P/web_test/a/cases.yaml" "expect: 1" "expect: 2"; commit_all "$P" judge >/dev/null
OUT=$(run_backstop "$P" --subst-check "$B19" HEAD); E=$?
assert "S19b 대조: web_test/ 판정 줄 변경 = red(바뀐 줄이 치환만으로 설명되지 않음)" 2 "web_test/a/cases.yaml:1 바뀐 줄이 치환만으로" "테스트 밖 web/ 밖 파일" "$E" "$OUT"

# ---------- S20 (2.1.0 검토 r1 #2): SUT 를 옮기면 web_test/ 미러 테스트도 같은 경로 대응으로 옮긴다 — 내용이 참조 치환뿐이면 green · 단언 변경 · 미러 밖 이동은 red
P="$T/s20"; U="application_layer/use_case"
mkdir -p "$P/web/application/a/$U" "$P/web_test/application/a/$U"
: > "$P/web/__init__.py"; : > "$P/web/application/__init__.py"; : > "$P/web/application/a/__init__.py"
printf 'def f():\n    return 1\n' > "$P/web/application/a/$U/get_a_use_case.py"
printf 'from web.application.a.application_layer.use_case.get_a_use_case import f\n\n\ndef test_f():\n    assert f() == 1\n' \
  > "$P/web_test/application/a/$U/get_a_use_case_test.py"
printf 'SCREEN_PROBES = {"a": "web.application.a"}\n' > "$P/web_test/application/a/_support.py"
git -C "$P" init -q; B20=$(commit_all "$P" base)
git -C "$P" mv web/application/a web/application/b
git -C "$P" mv web_test/application/a web_test/application/b
sub "$P/web_test/application/b/$U/get_a_use_case_test.py" "web.application.a." "web.application.b."
sub "$P/web_test/application/b/_support.py" '"web.application.a"' '"web.application.b"'
commit_all "$P" move-bc >/dev/null
OUT=$(run_backstop "$P" --subst-check "$B20" HEAD); E=$?
assert "S20a BC 이동 + 미러 테스트 같은 대응 이동(참조 치환만) = green" 0 "치환 확인 — web/ 밖 변경 파일" "[subst]" "$E" "$OUT"
sub "$P/web_test/application/b/$U/get_a_use_case_test.py" "assert f() == 1" "assert f() == 2"; commit_all "$P" judge >/dev/null
OUT=$(run_backstop "$P" --subst-check "$B20" HEAD); E=$?
assert "S20b 대조: 옮긴 테스트의 단언 변경 = red" 2 "get_a_use_case_test.py" - "$E" "$OUT"
P="$T/s20c"; git clone -q "$T/s20" "$P" 2>/dev/null; git -C "$P" checkout -q "$B20"
git -C "$P" mv web/application/a web/application/b
mkdir -p "$P/web_test/elsewhere"; git -C "$P" mv web_test/application/a/$U/get_a_use_case_test.py web_test/elsewhere/get_a_use_case_test.py
sub "$P/web_test/elsewhere/get_a_use_case_test.py" "web.application.a." "web.application.b."
commit_all "$P" move-off-mirror >/dev/null
OUT=$(run_backstop "$P" --subst-check "$B20" HEAD); E=$?
assert "S20c 대조: SUT 미러 밖으로 옮긴 테스트 = red(치환이 아닌 변경)" 2 "치환이 아닌 변경" - "$E" "$OUT"

# ---------- I (2.2.3): 승인 병합 유입 — 실제 main/lane · 절별 ID/경로/문장
# 도우미는 이 묶음에만 둔다. HEAD 러너는 별도 임시 사본으로 비교한다.
I_OUT=$(PYTHONDONTWRITEBYTECODE=1 python3 -B - "$SCRIPTS" "$T" <<'PY'
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import time

scripts, temp = map(Path, sys.argv[1:])
runner = scripts / 'backstop.py'
env = dict(os.environ, GIT_OPTIONAL_LOCKS='0', PYTHONDONTWRITEBYTECODE='1')
old = temp / 'i-old'
old.mkdir()
archive = subprocess.run(['git', '-C', str(scripts.parents[1]), 'archive', 'HEAD', 'dddjango-web/scripts'],
                         capture_output=True, check=True, env=env)
subprocess.run(['tar', '-x', '-C', str(old)], input=archive.stdout, check=True)
old_runner = old / 'dddjango-web/scripts/backstop.py'
old_runner.write_bytes(subprocess.check_output(
    ['git', '-C', str(scripts.parents[1]), 'show', 'HEAD:dddjango-web/scripts/backstop.py'], env=env))
BAD = 'from application.models import Item\n'
PAGE = '{% extends "design_system/component/bar/app_bar.html" %}\n'
LEGACY = 'web/old/old_view.py'
VIEW = 'web/application/order/presentation_layer/view/order_view.html'
MSG25 = 'web에서 백엔드 내부 `application.models` import — web 과 백엔드의 계약은 API(URL+JSON)뿐'
MSG26 = '`{% extends %}` 대상 `design_system/component/bar/app_bar.html` — 페이지(그 밖) 템플릿의 상속 대상은 root_view.html 하나'


def git(p, *args, check=True):
    r = subprocess.run(['git', '-C', str(p), '-c', 'user.name=t', '-c', 'user.email=t@t', *args],
                       capture_output=True, text=True, env=env)
    if check and r.returncode:
        raise RuntimeError(r.stderr)
    return r.stdout.strip()


def write(p, name, text):
    f = p / name
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text(text, encoding='utf-8')


def commit(p, msg):
    git(p, 'add', '-A')
    git(p, 'commit', '-qm', msg)
    return git(p, 'rev-parse', 'HEAD')


def project(name, prefix=''):
    p = temp / ('i-' + name)
    p.mkdir()
    git(p, 'init', '-q', '-b', 'main')
    root = p / prefix
    for name in ('__init__.py', 'apps.py', 'urls.py'):
        write(root, 'web/' + name, '')
    write(root, LEGACY, 'pass\n')
    write(root, VIEW.replace('order_view.html', 'order_base_view.html'), '{% extends "root/scaffold/view/root_view.html" %}\n')
    write(root, 'web/root/scaffold/view/root_view.html', '<html></html>\n')
    write(root, 'web/design_system/component/bar/app_bar.html', '<div></div>\n')
    write(root, '.dddjango-web/backstop-baseline.json', '{"cycle_pairs": []}')
    base = commit(p, 'base')
    git(p, 'checkout', '-qb', 'lane')
    write(root, 'lane.txt', 'lane\n'); commit(p, 'lane')
    folder = root / '.dddjango-web/build'
    write(folder, 'build-state.json', json.dumps({'git_snapshot': base, 'slices': []}))
    return p, root, base, folder


def incoming(p, root, changes, approve=True, folder=None, resolve=None):
    git(p, 'checkout', '-q', 'main')
    for path, text in changes.items():
        write(root, path, text)
    commit(p, 'main-change')
    git(p, 'checkout', '-q', 'lane')
    git(p, 'merge', '--no-ff', '--no-commit', 'main', check=False)
    if resolve:
        resolve()
    sha = commit(p, 'receive-main')
    if approve:
        with (folder / 'approved-merges.txt').open('a') as f:
            f.write(sha + ' main\n')
    return sha


def run(root, base=None, only='im', extra=(), script=runner, fault=None):
    args = [str(root)]
    if base:
        args += ['--diff-base', base]
    if only:
        args += ['--only', only]
    args += list(extra)
    if fault:
        # 실제 러너는 유지하고 실패 경계만 주입한다.
        code = "import runpy,sys,tempfile,subprocess; sys.argv=sys.argv[1:]; "
        if fault == 'temp':
            code += "tempfile.mkdtemp=lambda *a,**k: (_ for _ in ()).throw(PermissionError('fixture TMP')); "
        elif fault == 'parent':
            code += "original=subprocess.Popen; subprocess.Popen=lambda a,*x,**k: (_ for _ in ()).throw(OSError('fixture parent')) if '-B' in a else original(a,*x,**k); "
        elif fault == 'output':
            code += "original=subprocess.run; subprocess.run=lambda a,*x,**k: subprocess.CompletedProcess(a,2,b'not a Finding\\n',b'') if '-B' in a else original(a,*x,**k); "
        elif fault == 'status':
            code += "original=subprocess.run; subprocess.run=lambda a,*x,**k: subprocess.CompletedProcess(a,128,b'',b'fixture git failure') if 'status' in a and 'env' in k else original(a,*x,**k); "
        else:
            code += "original=subprocess.run; subprocess.run=lambda a,*x,**k: subprocess.CompletedProcess(a,128,b'',b'fixture chain failure') if '--reverse' in a else original(a,*x,**k); "
        code += "runpy.run_path(sys.argv[0],run_name='__main__')"
        cmd = [sys.executable, '-B', '-c', code, str(script), *args]
    else:
        cmd = [sys.executable, '-B', str(script), *args]
    r = subprocess.run(cmd, capture_output=True, env=env)
    return r.returncode, r.stdout.decode() + r.stderr.decode()


def result(name, ok, detail=''):
    print(('PASS ' if ok else 'FAIL ') + name)
    if not ok:
        print('    ' + detail.replace('\n', '\n    ')[:1600])


def sections(out):
    parts = out.split('== 승인 유입(', 1)
    return re.split(r'^== ', parts[0], maxsplit=1, flags=re.M)[0], parts[1].split('[backstop]', 1)[0] if len(parts) == 2 else ''


def finding(name, got, cid, path, message, inflow=False, reason=None, exitcode=None, merge=None):
    e, out = got
    blocker, approved = sections(out)
    want, other = (approved, blocker) if inflow else (blocker, approved)
    pat = r'\[' + re.escape(cid) + r'\] BLOCKER — ' + re.escape(path) + r'(?::\d+)?\n  위반: ' + re.escape(message)
    ok = bool(re.search(pat, want)) and not re.search(pat, other)
    ok = ok and e == (exitcode if exitcode is not None else (0 if inflow else 2))
    if inflow:
        ok = ok and '(L 증명) · 파일 그대로' in approved and ' · ^1 ' in approved and ' · ^2 ' in approved
    if merge:
        proof = pat + r' \([^\n]+\)\n  교정: [^\n]+\n    ↳ 유입: ' + re.escape(merge[:12]) + r'\(L 증명\) · 파일 그대로\n'
        ok = ok and bool(re.search(proof, want))
    if reason:
        ok = ok and '↳ 이 레인 몫으로 남김: ' + reason in blocker
    result(name, ok, f'exit={e}\n{out}')


def same(name, root, base=None, only='im', extra=(), fault=None):
    now = run(root, base, only, extra, fault=fault)
    before = run(root, base, only, extra, old_runner, fault=fault)
    result(name, now == before, f'현재={now}\nHEAD={before}')


p, root, base, folder = project('good')
m = incoming(p, root, {LEGACY: BAD, VIEW: PAGE}, folder=folder)
started = time.monotonic(); got = run(root, base)
print('I 시간: %.3f초(자동 탐색 가름 1회)' % (time.monotonic() - started))
finding('I1a 자동 IM25 승인 유입', got, 'IM25', LEGACY, MSG25, True)
finding('I1b 자동 IM26 승인 유입', got, 'IM26', VIEW, MSG26, True)
write(root, '.dddjango-web/other/build-state.json', json.dumps({'git_snapshot': base}))
got = run(root, base, extra=['--design-build', str(folder)])
finding('I2a 명시 IM25 승인 유입', got, 'IM25', LEGACY, MSG25, True)
finding('I2b 명시 IM26 승인 유입', got, 'IM26', VIEW, MSG26, True)
shutil.rmtree(root / '.dddjango-web/other')
got = run(root, base, only=None, extra=['--slice-end'])
finding('I3 슬라이스 끝 IM26 승인 유입', got, 'IM26', VIEW, MSG26, True)
finding('I4 --only im26', run(root, base, 'im26'), 'IM26', VIEW, MSG26, True)
finding('I5 검사 ID 선택 im25', run(root, base, 'im25'), 'IM25', LEGACY, MSG25, True)
# 기존 build/status가 끝난 뒤 stat를 낡게 만들어 새 W의 색인 쓰기만 잰다.
sys.path.insert(0, str(scripts))
from src.common import BackstopContext, Finding
ctx = BackstopContext.build(root, base, False)
index = p / '.git/index'; os.utime(root / LEGACY, None)
before = (hashlib.sha256(index.read_bytes()).hexdigest(), index.stat().st_mtime_ns)
try:
    from src.inflow import split_inflow
    split_inflow(ctx, [Finding('IM25', 'old/old_view.py', 1, MSG25, '제1 규약 §3.7', '')], None)
    ok = before == (hashlib.sha256(index.read_bytes()).hexdigest(), index.stat().st_mtime_ns)
except ImportError:
    ok = False
result('I6 새 W 원 색인 hash·mtime 무쓰기', ok)
write(root, 'web/old/lane_view.py', BAD); commit(p, 'own')
finding('I7 레인 자기 파일', run(root, base), 'IM25', 'web/old/lane_view.py', MSG25, reason='비머지 커밋 경유')
write(root, LEGACY, '# lane\n' + BAD)
finding('I8 미커밋 유입 파일 수정', run(root, base), 'IM25', LEGACY, MSG25, reason='작업 트리 수정 중')
commit(p, 'lane-edit')
finding('I9 커밋한 유입 파일 수정', run(root, base), 'IM25', LEGACY, MSG25, reason='레인 커밋 수정')
p, root, base, folder = project('discard')
incoming(p, root, {LEGACY: BAD}, folder=folder, resolve=lambda: (root / LEGACY).unlink())
write(root, LEGACY, BAD); commit(p, 'restore')
finding('I10 병합에서 버린 판 재작성', run(root, base), 'IM25', LEGACY, MSG25, reason='레인 커밋 수정')
p, root, base, folder = project('same')
write(root, LEGACY, BAD); commit(p, 'lane-first')
incoming(p, root, {LEGACY: BAD}, folder=folder)
finding('I11 레인이 먼저 같은 파일 작성', run(root, base), 'IM25', LEGACY, MSG25, reason='비머지 커밋 경유')
p, root, base, folder = project('both')
write(root, LEGACY, BAD); commit(p, 'lane-first')
incoming(p, root, {LEGACY: '\n' + BAD}, folder=folder, resolve=lambda: write(root, LEGACY, '\n' + BAD))
finding('I12 M1에도 있던 지적·줄번호 정규화', run(root, base), 'IM25', LEGACY, MSG25, reason='유입 증명 실패(이중 원인)')
p, root, base, folder = project('unapproved')
m = incoming(p, root, {LEGACY: BAD}, approve=False)
got = run(root, base)
finding('I13a 목록 없음·병합 있음', got, 'IM25', LEGACY, MSG25)
result('I13b 목록 밖 병합 알림', '[info] 승인 목록 밖 병합 ' + m[:9] in got[1])
write(folder, 'approved-merges.txt', '')
finding('I14 빈 목록·미승인 머지', run(root, base), 'IM25', LEGACY, MSG25, reason='미승인 머지 경유')
write(folder, 'approved-merges.txt', 'bad-input\n'); got = run(root, base)
finding('I15a 목록 형식 오류 보존', got, 'IM25', LEGACY, MSG25)
result('I15b 판정 불가 알림', '[info] 승인 유입 판정 불가 — ' in got[1])
shutil.rmtree(folder); got = run(root, base)
finding('I16a 산출물 폴더 없음', got, 'IM25', LEGACY, MSG25)
result('I16b 폴더 지정 안내', '산출물 폴더를 찾지 못함: --design-build 로 준다' in got[1])
p, root, base, folder = project('off-chain')
git(p, 'checkout', '-q', 'main'); write(root, LEGACY, BAD); upstream = commit(p, 'main')
git(p, 'checkout', '-q', 'lane'); git(p, 'merge', '--no-ff', '-qm', 'merge', 'main')
m = git(p, 'rev-parse', 'HEAD'); write(folder, 'approved-merges.txt', m + '\n')
write(root, LEGACY, BAD.replace('Item', 'Other')); got = run(root, upstream)
finding('I17a 기준이 첫 부모 밖', got, 'IM25', LEGACY, MSG25)
result('I17b 사슬 오류 알림', '첫 부모 사슬 밖' in got[1])
p, root, base, folder = project('merging')
git(p, 'checkout', '-q', 'main'); write(root, LEGACY, BAD); commit(p, 'main')
git(p, 'checkout', '-q', 'lane'); git(p, 'merge', '--no-ff', '--no-commit', 'main')
got = run(root, base)
finding('I18a 병합 중 보존', got, 'IM25', LEGACY, MSG25)
result('I18b MERGE_HEAD 알림', '[info] 병합 중(MERGE_HEAD)' in got[1])
p, root, base, folder = project('untracked')
incoming(p, root, {LEGACY: BAD}, folder=folder); git(p, 'rm', '-q', '--cached', LEGACY)
finding('I19 미추적 재작성 W', run(root, base), 'IM25', LEGACY, MSG25, reason='작업 트리 수정 중')
p, root, base, folder = project('parse')
write(root, 'web/old/broken.py', 'def broken(:\n'); commit(p, 'broken')
incoming(p, root, {LEGACY: BAD, 'web/old/broken.py': 'pass\n'}, folder=folder,
         resolve=lambda: write(root, 'web/old/broken.py', 'pass\n'))
finding('I20 부모 파싱 실패 비대칭', run(root, base), 'IM25', LEGACY, MSG25, reason='측정 무효(')
p, root, base, folder = project('link')
write(root, '.dddjango/settings_pkg/settings.py', '')
(root / 'config').symlink_to('.dddjango/settings_pkg'); commit(p, 'link')
incoming(p, root, {LEGACY: BAD}, folder=folder)
finding('I21 제외 폴더를 가리키는 링크', run(root, base), 'IM25', LEGACY, MSG25, reason='측정 무효(')
p, root, base, folder = project('fault')
incoming(p, root, {LEGACY: BAD}, folder=folder)
got = run(root, base, fault='temp')
finding('I22a 임시 폴더 생성 실패', got, 'IM25', LEGACY, MSG25)
result('I22b 임시 폴더 실패 알림', '[info] 승인 유입 판정 불가 — fixture TMP' in got[1])
finding('I23 부모 실행 실패', run(root, base, fault='parent'), 'IM25', LEGACY, MSG25, reason='측정 무효(')
finding('I40 부모 출력 판독 불가', run(root, base, fault='output'), 'IM25', LEGACY, MSG25, reason='측정 무효(')
got = run(root, base, fault='status')
finding('I41a 새 Git 조회 실패 보존', got, 'IM25', LEGACY, MSG25)
result('I41b 새 Git 조회 실패 알림', '[info] 승인 유입 판정 불가 — ' in got[1])
same('I42 병합 있어도 --all byte 동일', root, base, extra=['--all'])
got = run(root, base, fault='chain')
finding('I45a 사슬 조회 실패 보존', got, 'IM25', LEGACY, MSG25)
result('I45b 사슬 조회 실패 알림', '[info] 승인 유입 판정 불가 — ' in got[1])
fakebin = temp / 'i-bin'; fakebin.mkdir()
write(fakebin, 'tar', '#!/bin/sh\nexit 1\n'); (fakebin / 'tar').chmod(0o755)
saved_path = env['PATH']; env['PATH'] = str(fakebin) + ':' + saved_path
finding('I24 스냅숏 실패', run(root, base), 'IM25', LEGACY, MSG25, reason='측정 무효(')
env['PATH'] = saved_path
# 제외 ID 및 비-blob — 실제 검사 발화; 원문은 HEAD 러너에서 잡아 절별 대조한다.
p, root, base, folder = project('excluded')
incoming(p, root, {'web/static/site.css': 'body {}\n',
    'web/application/order/presentation_layer/view/inline.js': 'x=1;\n', VIEW: '<script>x()</script>\n',
    'web/application/alpha/application_layer/use_case/a.py': 'from web.application.beta.application_layer.use_case.b import b\na=1\n',
    'web/application/beta/application_layer/use_case/b.py': 'from web.application.alpha.application_layer.use_case.a import a\nb=1\n',
    'web/static/vendor/probe/probe.js': 'window.probe={};\n'}, folder=folder)
write(root, 'web/sdk_registry.json', '{'); commit(p, 'malformed-sdk')
for n, cid in enumerate(['ST4', 'ST12', 'PU1', 'PU2', 'CY1', 'WV1'], 25):
    only = cid.lower()
    baseline = run(root, base, only, script=old_runner)
    match = re.search(r'\[' + cid + r'\] BLOCKER — ([^\n]+)\n  위반: (.+) \([^\n]+\)\n  교정:', baseline[1])
    if not match:
        result(f'I{n} {cid} 제외/비-blob', False, baseline[1]); continue
    path = re.sub(r':\d+$', '', match[1])
    finding(f'I{n} {cid} 제외/비-blob', run(root, base, only), cid, path, match[2],
            reason='비-blob 경로' if cid == 'ST4' else '가름 제외 검사')
write(root, 'requirements.txt', 'pytest\n')
write(root, 'web_test/order_test.py', 'def test_order():\n    assert True\n'); commit(p, 'pytest-declaration')
baseline = run(root, base, 'pj1', script=old_runner)
match = re.search(r'\[PJ1\] BLOCKER — ([^\n]+)\n  위반: (.+) \([^\n]+\)\n  교정:', baseline[1])
got = run(root, base, 'pj1')
if match:
    finding('I31 PJ1 root_rel 비-blob', got, 'PJ1', match[1], match[2], reason='비-blob 경로')
else:
    result('I31 PJ1 root_rel 비-blob', False, baseline[1])
# 미룸 검사도 G2에서는 발화한다. main의 unchanged 파일은 L 증명 유입, BC 폴더는 blocker.
p, root, base, folder = project('deferred-g2')
incoming(p, root, {
    'web/application/shop/application_layer/view_model/shop_list_vm.py': 'class ShopListVM:\n    pass\n',
    'web/application/shop/presentation_layer/view/shop_detail_view.py': 'def shop_detail_view(request):\n    pass\n',
    'web/static/application/shop/shop_banner_section.css': '.shop-banner { color: var(--color-primary); }\n',
}, folder=folder)
got = run(root, base, only=None)  # --slice-end·--only 없이 전체 G2 실행; ST4·TG1이 남아 exit 2.
finding('I47 G2 NM4 승인 유입', got, 'NM4',
        'web/application/shop/application_layer/view_model/shop_list_vm.py',
        '삼총사 미완 — 같은 접두 shop_list_view.py·shop_list_view.html·shop_list_state.py 부재', True, exitcode=2)
finding('I48 G2 NM18 승인 유입', got, 'NM18',
        'web/application/shop/presentation_layer/view/shop_detail_view.py',
        'view 짝 미완 — 같은 폴더 `shop_detail_view.html` 부재', True, exitcode=2)
finding('I49 G2 NM19 승인 유입', got, 'NM19',
        'web/static/application/shop/shop_banner_section.css',
        '조각 CSS `shop_banner_section.css` — 소유자(BC presentation_layer · root scaffold)에 같은 stem 의 템플릿이 없다',
        True, exitcode=2)
finding('I50 G2 TG1 비-blob 유지', got, 'TG1', 'web/application/shop',
        '신규 BC `shop` 행위검증 테스트 부재 — `web_test/application/shop/`에 `*_test.py` 0건. '
        'green 빌드가 비-vacuous 검증으로 안 이어진다.', reason='비-blob 경로')
p, root, base, folder = project('nested', 'project')
write(p, LEGACY, '# repository root\n'); commit(p, 'same-name')
incoming(p, root, {LEGACY: BAD}, folder=folder)
finding('I32 하위 대상 루트·동명 파일', run(root, base), 'IM25', LEGACY, MSG25, True)
p, root, base, folder = project('accepted-limit')
incoming(p, root, {LEGACY: BAD}, folder=folder)
incoming(p, root, {LEGACY: 'pass\n'}, approve=False)
write(root, LEGACY, BAD); commit(p, 'restore-approved')
finding('I33 수락한 한계·앞 승인 판 복원', run(root, base), 'IM25', LEGACY, MSG25, True)
# 꺼짐: 같은 인자의 2.2.2 HEAD 러너와 exit+출력 byte 대조
p, root, base, folder = project('no-merge')
write(root, LEGACY, BAD); commit(p, 'own')
same('I34 병합 없음 byte 동일', root, base)
same('I35 목록 없음+병합 없음 byte 동일', root, base)
same('I46 무병합 사슬 조회 실패 byte 동일', root, base, fault='chain')
write(folder, 'approved-merges.txt', 'invalid-but-inactive\n')
same('I36 --all byte 동일', root, base, extra=['--all'])
same('I37 기준 없음 byte 동일', root)
non = temp / 'i-nongit'; shutil.copytree(root / 'web', non / 'web')
same('I38 비git byte 동일', non, base)
p, root, base, folder = project('prior')
m = incoming(p, root, {LEGACY: BAD}, folder=folder); base = git(p, 'rev-parse', 'HEAD')
write(folder, 'build-state.json', json.dumps({'git_snapshot': base}))
write(root, 'web/old/new_view.py', BAD); commit(p, 'own-after-base')
same('I39 기준 이전 승인만·무병합 byte 동일', root, base)
# 충돌 해소분은 incoming과 다른 바이트라 F1 실패.
p, root, base, folder = project('conflict')
write(root, LEGACY, BAD + '# lane\n'); commit(p, 'lane-conflict')
incoming(p, root, {LEGACY: BAD + '# main\n'}, folder=folder,
         resolve=lambda: write(root, LEGACY, BAD + '# resolved\n'))
finding('I43 충돌 해소분', run(root, base), 'IM25', LEGACY, MSG25, reason='충돌 해소분(M≠M^2)')
# 첫 전달 병합 측정이 무효여도 다른 승인 병합이 L을 증명하면 유입(∃M).
p, root, base, folder = project('exists')
write(root, 'web/old/broken.py', 'def broken(:\n'); commit(p, 'broken')
incoming(p, root, {LEGACY: BAD}, folder=folder)
(root / 'web/old/broken.py').unlink(); write(root, LEGACY, 'pass\n'); commit(p, 'repair')
proof_merge = incoming(p, root, {'main-again.txt': 'main again\n'}, folder=folder,
                       resolve=lambda: write(root, LEGACY, BAD))
finding('I44 다른 승인 병합이 L 증명', run(root, base), 'IM25', LEGACY, MSG25, True, merge=proof_merge)
PY
); I_STATUS=$?
printf '%s\n' "$I_OUT"
I_PASS=$(printf '%s\n' "$I_OUT" | grep -c '^PASS I' || true)
I_FAIL=$(printf '%s\n' "$I_OUT" | grep -c '^FAIL I' || true)
PASS=$((PASS+I_PASS)); FAIL=$((FAIL+I_FAIL))
[ "$I_STATUS" = 0 ] && [ "$I_PASS" -gt 0 ] || { FAIL=$((FAIL+1)); echo 'FAIL I 묶음 미실행/도우미 오류'; }

echo "fixtures_subst: PASS=$PASS FAIL=$FAIL"
[ "$FAIL" = 0 ]
