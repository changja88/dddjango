#!/bin/zsh
# BK2 O-5 인수 — 세 타깃 순차 직렬 전수(RUNSTATE 판형: make test 는 --maxfail=1 이라 불가)
EV=/Users/hyun/.claude/jobs/48c8a476/tmp/bk2-events.log
OUT=/Users/hyun/.claude/jobs/48c8a476/tmp/acceptance
mkdir -p $OUT
ev() { print -r -- "[$(date '+%m-%d %H:%M')] $1" >> $EV }

for n in 04 05 06; do
  tgt=/Users/hyun/Desktop/t2ab-R$n
  ev "🧪 R$n 인수 pytest 시작(직렬 전수)"
  (
    cd $tgt || exit 1
    # 최소 인라인 env(런 코디 판형) — .env.local 전체 source 금지: DJANGO_SETTINGS_MODULE(프로덕션)이
    # pytest-django 의 settings.test 를 오버라이드하고 SSL/HOSTS 설정이 test client 를 오염시킨다.
    # LLM 실키 2개만 .env.local 에서 추출(ai_chat 3건 green 조건 — R06 보고 실측).
    eval $(grep -E '^(CLAUDE_API_KEY|GPT_API_KEY)=' /Users/hyun/Desktop/broccoli-server/.env.local | sed 's/^/export /')
    export SECRET_KEY=test-dummy
    export POSTGRES_HOST=localhost POSTGRES_TEST_HOST=localhost POSTGRES_PORT=5432
    export POSTGRES_USER=hyun POSTGRES_PASSWORD=x
    export POSTGRES_DB=broccoli_r$n POSTGRES_TEST_DB=test_broccoli_r$n
    export POSTGRES_SSLMODE=disable POSTGRES_CONN_MAX_AGE=0
    uv run pytest -q --tb=no -rEf --continue-on-collection-errors > $OUT/R$n-pytest.txt 2>&1
  )
  s=$(grep -E "^[0-9]+ (passed|failed)|passed|failed|error" $OUT/R$n-pytest.txt | tail -1)
  ev "🧪 R$n 인수 pytest 종료 — ${s:0:120}"
done
ev "🧪 인수 pytest 3타깃 전부 종료"
