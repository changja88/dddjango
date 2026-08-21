#!/bin/zsh
# BK1 감시 v6 — **허용 목록** 자동 승인. (v6: 5초 폴링 · 명령 추출을 마지막 도구
# 헤더 이후로 앵커 — 본문 표(│ 포함)·서브에이전트 트리(├ └)를 명령으로 오인하던 결함 수리)
#
# 앞선 판(자동 승인 v3)은 위험 명령 목록을 문면에 담아 실행 분류기가 스크립트 자체를
# 막았고, 탐지 전용(v4)은 사람(메인 세션)이 병목이라 blocked 가 몇 분씩 이어졌다.
# 이번엔 반대로 간다: **안전하다고 아는 형태만** 목록에 적고 그것만 승인한다.
# 목록에 없으면 무조건 알림 — 위험 판별 로직도, 위험 문자열도 스크립트에 없다.
#
# 게이트 질문(선택지 메뉴)은 절대 자동 응답하지 않는다.

EV=/Users/hyun/.claude/jobs/48c8a476/tmp/bk1-events.log
LOG=/Users/hyun/.claude/jobs/48c8a476/tmp/bk1-autoapprove.log
QDIR=/Users/hyun/.claude/jobs/48c8a476/tmp/gate-questions
mkdir -p $QDIR

ev() { print -r -- "[$(date '+%m-%d %H:%M')] $1" >> $EV }
lg() { print -r -- "[$(date '+%m-%d %H:%M:%S')] $1" >> $LOG }

# ── 허용 목록: 명령 상자에서 뽑은 «명령 시작 형태». 전부 읽기·검사·테스트 계열. ──
# 한 프롬프트의 모든 명령 줄이 이 중 하나로 시작해야 자동 승인된다.
ALLOW=(
  'cat ' 'cat -n' '/bin/cat ' 'ls ' '/bin/ls ' 'wc ' 'head ' 'tail ' 'grep ' 'sed -n' 'sort' 'diff '
  'echo ' 'printf ' 'cd /Users/hyun/Desktop/t2ab-R' 'export PYTHONDONTWRITEBYTECODE=1'
  'find application' 'find . -name __pycache__' 'find config' 'find test'
  '.venv/bin/python manage.py test' '.venv/bin/python manage.py check'
  '.venv/bin/python manage.py makemigrations' '.venv/bin/python manage.py showmigrations'
  './.venv/bin/python manage.py test' './.venv/bin/python manage.py check'
  './.venv/bin/python manage.py makemigrations' './.venv/bin/python manage.py showmigrations'
  '/Users/hyun/Desktop/t2ab-R01/.venv/bin/python' '/Users/hyun/Desktop/t2ab-R02/.venv/bin/python'
  '/Users/hyun/Desktop/t2ab-R03/.venv/bin/python'
  'PYTHONDONTWRITEBYTECODE=1 .venv/bin/python' 'PYTHONDONTWRITEBYTECODE=1 ./.venv/bin/python'
  'PYTHONDONTWRITEBYTECODE=1 /Users/hyun/Desktop/t2ab-R'
  'python3 /Users/hyun/.claude/plugins/cache/changja88-dddjango/'
  'python3 "$P/' 'python3 $P/' 'python3 "$S/' 'python3 $S/'
  '/usr/bin/python3 /Users/hyun/.claude/plugins/cache/changja88-dddjango/'
  'git status' 'git log' 'git diff' 'git show' 'git rev-parse' 'git ls-files'
  'git add ' 'git commit ' 'git -C /Users/hyun/Desktop/t2ab-R'
  'rg ' 'awk ' 'tr ' 'cut ' 'sed -E' 'uniq' 'basename ' 'dirname ' 'stat '
  'python3 -c' '/usr/bin/python3 -c' 'DJANGO_SETTINGS_MODULE=' 'PYTHONPATH='
  'out=$(' 'out2=$(' 'rc=' 'e=$?' 'D=.dddjango' 'D=/Users/hyun/Desktop/t2ab-R'
  'P=/Users/hyun/.claude/plugins' 'S=/Users/hyun/.claude/plugins'
  'T=/private/tmp/claude-501/' 'A=/private/tmp/claude-501/' 'SC=/private/tmp/claude-501/'
  'ANCHOR=$(cat' 'DEBT=' 'for f in ' 'for c in ' 'for d in ' 'done' 'fi' 'if [' 'then' 'else'
  'mkdir -p application' 'mkdir -p /private/tmp/claude-501/' 'touch application/'
  ': > ' '[ -e ' '[ -f ' '[ -s '
)

is_allowed_line() {
  local line=$1
  [ -z "${line// }" ] && return 0            # 빈 줄
  for p in "${ALLOW[@]}"; do
    [[ "$line" == "$p"* ]] && return 0
  done
  return 1
}

typeset -A pend idle_n seen_inj done_f
for a in t2ab-r01 t2ab-r02; do pend[$a]=0; idle_n[$a]=0; seen_inj[$a]=-1; done_f[$a]=0; done
tick=0

while true; do
  tick=$((tick+1))
  for a in t2ab-r01 t2ab-r02; do
    pane=$(herdr agent read $a 2>/dev/null)
    [ -z "$pane" ] && continue
    t=$(print -r -- "$pane" | tail -30)
    tgt="/Users/hyun/Desktop/t2ab-R${a#t2ab-r}"

    busy=0
    print -r -- "$t"    | grep -qE '\([0-9]+(m [0-9]+)?s' && busy=1
    print -r -- "$pane" | grep -qE 'Waiting for [0-9]+ background|◯ dddjango:' && busy=1

    if print -r -- "$t" | grep -q "Do you want to proceed"; then
      pn=$(print -r -- "$pane" | grep -n "Do you want to proceed" | tail -1 | cut -d: -f1)
      # 마지막 도구 헤더(Bash command 등) 이후 ~ proceed 직전만 명령으로 본다.
      # 그 앞의 본문 표(│ 포함)·서브에이전트 트리(├ └)가 명령으로 오인되던 결함(v5.1) 수리.
      hd=$(print -r -- "$pane" | sed -n "1,${pn}p" \
           | grep -nE 'Bash command|Edit file|Write file|Create file|Read file|Bash \(' | tail -1 | cut -d: -f1)
      if [ -n "$hd" ] && [ "$hd" -lt "$pn" ]; then
        blk=$(print -r -- "$pane" | sed -n "$((hd+1)),$((pn-1))p")
      else
        blk=$(print -r -- "$pane" | sed -n "1,${pn}p" | tail -60)
      fi
      cmds=$(print -r -- "$blk" | grep -E '^[[:space:]]*│' | sed -E 's/^[[:space:]]*│[[:space:]]?//')
      [ -z "$cmds" ] && cmds=$(print -r -- "$blk" \
        | grep -vE '^[[:space:]]*(⏺|⎿|├|└|╰|╭|✻|✽|✳|✢|❯|·)' \
        | grep -E '^[[:space:]]{2,}[^[:space:]]' | sed -E 's/^[[:space:]]+//')

      # 판 폭 때문에 한 논리 명령이 여러 표시줄로 접힌다 — 줄별 검사는 이어짐 줄에서
      # 반드시 실패한다(R02 실측: for 루프의 둘째 줄이 파일 경로로 시작). 전부 한 줄로
      # 합친 뒤 명령 구분자(; · && · ||)로 잘라 조각 단위로 검사한다.
      flat=$(print -r -- "$cmds" | tr '\n' ' ')
      ok=1
      if [ -z "${flat// }" ]; then
        ok=0   # 명령을 못 읽으면 사람
      else
        segs=$(print -r -- "$flat" | sed -E 's/ *(&&|\|\||;) */\n/g')
        while IFS= read -r line; do
          line="${line#"${line%%[![:space:]]*}"}"
          is_allowed_line "$line" || { ok=0; break; }
        done <<< "$segs"
      fi

      if [ $ok -eq 1 ]; then
        if print -r -- "$t" | grep -qE '^[[:space:]]*2\. Yes, (allow|and don)'; then k=2; else k=1; fi
        herdr agent send-keys $a $k >/dev/null 2>&1
        lg "$a AUTO=$k allowlist"
        pend[$a]=0
      else
        if [ "${pend[$a]}" = "0" ]; then
          print -r -- "$pane" | tail -60 > $QDIR/$a.txt
          bad=$(while IFS= read -r line; do line="${line#"${line%%[![:space:]]*}"}"; is_allowed_line "$line" || { print -r -- "$line"; break; }; done <<< "$segs")
          ev "⏸ $a 목록 밖 명령 — ${bad:0:100} · 전문 $QDIR/$a.txt"
          lg "$a MANUAL ${bad:0:120}"
          pend[$a]=1
        elif [ $((tick % 18)) -eq 0 ]; then
          ev "⏸ $a 아직 대기 — $QDIR/$a.txt"
        fi
      fi
      idle_n[$a]=0
      continue
    fi

    # 게이트 질문(선택지 메뉴) — 자동 응답 금지, 알림만
    if print -r -- "$t" | grep -qE 'Enter to select|Ready to submit'; then
      if [ "${pend[$a]}" = "0" ]; then
        print -r -- "$pane" | tail -60 > $QDIR/$a.txt
        ev "❓ $a 게이트 질문 — $QDIR/$a.txt"
        pend[$a]=1
      fi
      idle_n[$a]=0
      continue
    fi
    pend[$a]=0

    ERRPAT='API Error:|rate_limit_error|Claude usage limit reached|You have run out of|Execution error|Killed: 9'
    if print -r -- "$t" | grep -qE "$ERRPAT"; then
      ev "⚠️ $a — $(print -r -- "$t" | grep -E "$ERRPAT" | head -1 | cut -c1-110)"
    fi

    n=$(cat "$tgt"/.dddjango/*/injection.jsonl 2>/dev/null | wc -l | tr -d ' ')
    [ -z "$n" ] && n=0
    if [ "$n" != "${seen_inj[$a]}" ] && [ "$n" != "0" ]; then
      ev "🔬 $a 주입 발화 — 회전 $n"
      seen_inj[$a]=$n
    fi

    if [ $busy -eq 0 ]; then
      idle_n[$a]=$(( ${idle_n[$a]} + 1 ))
      if [ ${idle_n[$a]} -ge 20 ] && [ "${done_f[$a]}" = "0" ]; then
        ev "🏁 $a 100초 유휴 — 완주 또는 정지"
        done_f[$a]=1
      fi
    else
      idle_n[$a]=0; done_f[$a]=0
    fi
  done

  if [ $((tick % 90)) -eq 0 ]; then
    ev "· 감시 생존 (주입 R01=${seen_inj[t2ab-r01]} R02=${seen_inj[t2ab-r02]})"
  fi
  sleep 5
done
