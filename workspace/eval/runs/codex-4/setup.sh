#!/usr/bin/env bash
# dddjango 스모크/비교평가 타깃 셋업 (멱등).
# sample 또는 그 복제본(claude-index·codex-index)에서 실행 → 바로 런 가능한 상태로 만든다.
#   - venv(.venv) 생성 + Django==4.2.30 설치 (requirements.txt 핀)
#   - migrate (Product 스키마)
#   - 시드: Widget(stock 10)·Gadget(stock 3) — db.sqlite3 에만(테스트 DB 비오염)
#   - check
# 시드를 마이그레이션이 아니라 런타임 데이터로 넣는 이유: manage.py test 가 만드는 테스트 DB에
# 시드가 섞이면 인수 테스트가 오염되므로. 개발 db.sqlite3 에만 적재한다.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$HERE"

if [[ ! -x .venv/bin/python ]]; then
  echo "==> venv 생성 (.venv)"
  /usr/bin/python3 -m venv .venv
fi
echo "==> 의존성 설치 (requirements.txt)"
.venv/bin/python -m pip install --quiet --upgrade pip
.venv/bin/python -m pip install --quiet -r requirements.txt

echo "==> migrate"
.venv/bin/python manage.py migrate --noinput >/dev/null

echo "==> 시드 (Widget 10 / Gadget 3)"
.venv/bin/python manage.py shell -c "
from catalog.models import Product
Product.objects.get_or_create(name='Widget', defaults={'price': 1000, 'stock': 10})
Product.objects.get_or_create(name='Gadget', defaults={'price': 2000, 'stock': 3})
print('seeded:', list(Product.objects.values_list('name', 'stock')))
"

echo "==> check"
.venv/bin/python manage.py check

echo ""
echo "✓ setup 완료 — $HERE (PROMPT.md 의 §1 프롬프트로 런 시작)"
