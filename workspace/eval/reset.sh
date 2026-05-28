#!/usr/bin/env bash
# dddjango Codex/Claude 평가용 — 타깃 프로젝트를 baseline(Product-only)으로 리셋한다.
#
# 목적: Claude 1회 + Codex 2~3회 런이 "모두 동일한 시작 상태"에서 출발하도록 보장한다.
#       시작 상태가 다르면 결정성·동등성 비교가 오염된다.
#
# 보존: .venv 는 건드리지 않는다(매번 재설치하면 느리고 의미 없음).
# 복원: catalog/ config/ manage.py 를 baseline 으로 덮고, .dddjango/ db.sqlite3 산출물을 지운 뒤
#       migrate 로 DB를 baseline 스키마(Product만)로 재생성한다.
#
# 사용: bash reset.sh [TARGET_DIR]
#   TARGET_DIR 기본값: /Users/hyun/Desktop/dddjango-smoke
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BASELINE="$SCRIPT_DIR/baseline"
TARGET="${1:-/Users/hyun/Desktop/dddjango-smoke}"

if [[ ! -d "$BASELINE" ]]; then
  echo "ERROR: baseline 없음: $BASELINE" >&2; exit 1
fi
if [[ ! -d "$TARGET" ]]; then
  echo "ERROR: 타깃 프로젝트 없음: $TARGET" >&2; exit 1
fi
if [[ ! -x "$TARGET/.venv/bin/python" ]]; then
  echo "ERROR: 타깃 venv 없음: $TARGET/.venv (Django 4.2 설치된 venv가 필요)" >&2; exit 1
fi

echo "==> 산출물 제거 (catalog/ config/ manage.py / .dddjango/ / db.sqlite3)"
rm -rf "$TARGET/catalog" "$TARGET/config" "$TARGET/manage.py" "$TARGET/.dddjango" "$TARGET/db.sqlite3"
find "$TARGET" -path "$TARGET/.venv" -prune -o -name '__pycache__' -type d -print 2>/dev/null | xargs -r rm -rf

echo "==> baseline 복원"
cp -R "$BASELINE/catalog" "$BASELINE/config" "$TARGET/"
cp "$BASELINE/manage.py" "$TARGET/manage.py"

echo "==> DB 재생성 (migrate)"
( cd "$TARGET" && .venv/bin/python manage.py migrate --noinput >/dev/null )

echo "==> 정합성 확인 (check)"
( cd "$TARGET" && .venv/bin/python manage.py check )

echo "==> baseline 트리 확인"
( cd "$TARGET" && find catalog config manage.py -type f | sort )

echo ""
echo "✓ 리셋 완료 — '$TARGET' 는 Product-only baseline 상태."
echo "  이제 새 dddjango 런(Claude 또는 Codex)을 이 디렉터리에서 시작하라."
