#!/bin/zsh
# BK1 무인 완주 감시 v4 — 세션에서 분리(nohup)되어 독립 실행된다.
#
# 자동  : 설치본/타깃 아래 읽기 · 무위험 bash → 즉시 승인
# 알림  : 게이트 질문(선택지 메뉴) · 위험 작업 · 오류·한도 · 주입 발화 · 완료
# 폴백  : 승인형 게이트 질문이 10분 넘게 방치되면 «제안대로/승인» 계열을 고른다(요란하게 기록)
#
# 이벤트는 EV 파일에 한 줄씩. 메인 세션은 그 파일을 tail 해서 받는다.

EV=/Users/hyun/.claude/jobs/48c8a476/tmp/bk1-events.log
LOG=/Users/hyun/.claude/jobs/48c8a476/tmp/bk1-autoapprove.log
QDIR=/Users/hyun/.claude/jobs/48c8a476/tmp/gate-questions
CACHE='/Users/hyun/.claude/plugins/cache/changja88-dddjango'
mkdir -p $QDIR

ev() { print -r -- "[$(date '+%m-%d %H:%M')] $1" >> $EV }
lg() { print -r -- "[$(date '+%m-%d %H:%M:%S')] $1" >> $LOG }

typeset -A pend gate_since gate_warn idle_n seen_inj done_f
for a in t2ab-r01 t2ab-r02 t2ab-r03; do
  pend[$a]=0; gate_since[$a]=0; gate_warn[$a]=0; idle_n[$a]=0; seen_inj[$a]=-1; done_f[$a]=0
done
tick=0

while true; do
  tick=$((tick+1))
  for a in t2ab-r01 t2ab-r02 t2ab-r03; do
    pane=$(herdr agent read $a 2>/dev/null)
    [ -z "$pane" ] && continue
    tail26=$(print -r -- "$pane" | tail -26)
    tgt="/Users/hyun/Desktop/t2ab-R${a#t2ab-r}"

    # 스피너 글리프는 회전한다(✻ ✳ ✽ ✶ · …) — 글리프 대신 «경과·토큰 카운터»를 본다.
    # 그 줄은 작업 중일 때만 뜬다: "… (5m 22s · ↓ 16.8k tokens)"
    busy=0
    print -r -- "$tail26" | grep -qE '\([0-9]+[ms][^)]*· ↓' && busy=1
    print -r -- "$pane"   | grep -qE 'Waiting for [0-9]+ background|◯ dddjango:' && busy=1
    print -r -- "$tail26" | grep -qE 'esc to interrupt|Interrupt' && busy=1

    menu=0
    print -r -- "$tail26" | grep -qE '^[[:space:]]*(❯[[:space:]]+)?1\.[[:space:]]' && menu=1
    perm=0
    print -r -- "$tail26" | grep -q "Do you want to proceed" && perm=1

    # ───────── ① 권한 프롬프트 ─────────
    if [ $perm -eq 1 ]; then
      # 긴 명령(heredoc 등)은 tail26 밖으로 밀려난다 — 프롬프트 위 120줄을 본다.
      blk=$(print -r -- "$pane" | sed -n '1,/Do you want to proceed/p' | tail -120)
      subj=$(print -r -- "$blk" | grep -E "Search\(|Glob\(|Grep\(|Read file|Bash command|Edit file|Write\(|Update\(|WebFetch|WebSearch" | tail -1)
      body=$blk
      safe=0
      if print -r -- "$subj" | grep -qE "Search\(|Glob\(|Grep\(|Read file"; then
        { print -r -- "$body" | grep -qF "$CACHE" || print -r -- "$body" | grep -qF "$tgt"; } && safe=1
      fi
      if print -r -- "$subj" | grep -q "Bash command"; then
        # 산문이 아니라 명령 상자(│ 로 시작하는 줄)만 본다 — 창을 넓히면 산문이 오탐을 낳는다.
        cmd=$(print -r -- "$blk" | grep -E '^[[:space:]]*│' )
        if print -r -- "$cmd" | grep -qE '(^|[^a-zA-Z])(rm|curl|wget|ssh|scp|sudo|chmod|chown|kill|npm|pip|brew)[[:space:]]|git[[:space:]]+(push|reset[[:space:]]+--hard|clean)|pip[[:space:]]+install|>[[:space:]]*/(etc|usr|bin|System|Library)'; then
          safe=0
        else
          safe=1
        fi
      fi
      if [ $safe -eq 1 ]; then
        if print -r -- "$tail26" | grep -qE '^[[:space:]]+2\. Yes, allow'; then k=2; else k=1; fi
        herdr agent send-keys $a $k >/dev/null 2>&1
        lg "$a AUTO=$k $(print -r -- "$subj" | cut -c1-140)"
      else
        if [ "${pend[$a]}" = "0" ]; then
          ev "⛔ $a 위험 판단 필요 — $(print -r -- "$subj" | cut -c1-120)"
          lg "$a MANUAL $(print -r -- "$subj" | cut -c1-140)"
          pend[$a]=1
        fi
      fi
      gate_since[$a]=0; idle_n[$a]=0
      continue
    fi
    pend[$a]=0

    # ───────── ② 게이트 질문(선택지 메뉴 · 권한 아님) ─────────
    if [ $menu -eq 1 ]; then
      qf=$QDIR/$a.txt
      print -r -- "$pane" | tail -45 > $qf
      now=$(date +%s)
      if [ "${gate_since[$a]}" = "0" ]; then
        gate_since[$a]=$now; gate_warn[$a]=0
        ev "❓ $a 게이트 질문 — 봉인된 고정 답 필요 · 전문: $qf"
      else
        elapsed=$(( now - ${gate_since[$a]} ))
        if [ $elapsed -ge 120 ] && [ $(( elapsed / 120 )) -gt ${gate_warn[$a]} ]; then
          gate_warn[$a]=$(( elapsed / 120 ))
          ev "❓ $a 게이트 질문 ${elapsed}초째 미응답 — $qf"
        fi
        # 폴백: 승인형이고 10분 방치면 1번(권고안)을 고른다
        if [ $elapsed -ge 600 ]; then
          if grep -qE '승인|제안대로|무수정|계속|Recommended' $qf; then
            herdr agent send-keys $a 1 >/dev/null 2>&1
            ev "⚠️ $a 게이트 10분 무응답 → 폴백으로 1번(권고안) 제출. 전문 $qf — 사후 검증 필요"
            lg "$a GATE-FALLBACK=1"
            gate_since[$a]=0
          else
            ev "🛑 $a 게이트 10분 무응답 · 승인형 아님 → 폴백 안 함. 사람이 답해야 한다 — $qf"
            gate_since[$a]=$now
          fi
        fi
      fi
      idle_n[$a]=0
      continue
    fi
    gate_since[$a]=0

    # ───────── ③ 오류·한도 ─────────
    # 설계 명세 본문에 «rate limit» 같은 말이 나와 오탐이 났다 — 실제 오류 문면만 좁혀 본다.
    ERRPAT='API Error:|rate_limit_error|Claude usage limit reached|You have run out of|Execution error|Killed: 9|Segmentation fault|Context low · Run /compact'
    if print -r -- "$tail26" | grep -qE "$ERRPAT"; then
      ev "⚠️ $a — $(print -r -- "$tail26" | grep -E "$ERRPAT" | head -1 | cut -c1-120)"
    fi

    # ───────── ④ 주입 발화 ─────────
    n=$(cat "$tgt/.dddjango/injection.jsonl" 2>/dev/null | wc -l | tr -d ' ')
    [ -z "$n" ] && n=0
    if [ "$n" != "${seen_inj[$a]}" ] && [ "$n" != "0" ]; then
      ev "🔬 $a 주입 발화 — 회전 $n"
      seen_inj[$a]=$n
    fi

    # ───────── ⑤ 완료(장기 유휴) ─────────
    if [ $busy -eq 0 ]; then
      idle_n[$a]=$(( ${idle_n[$a]} + 1 ))
      if [ ${idle_n[$a]} -ge 12 ] && [ "${done_f[$a]}" = "0" ]; then
        ev "🏁 $a 60초 유휴 — 완주 또는 정지. 채점 판단 필요"
        done_f[$a]=1
      fi
    else
      idle_n[$a]=0; done_f[$a]=0
    fi
  done

  # 15분마다 생존 신호
  if [ $((tick % 180)) -eq 0 ]; then
    ev "· 감시 생존 (주입 R01=${seen_inj[t2ab-r01]} R02=${seen_inj[t2ab-r02]} R03=${seen_inj[t2ab-r03]})"
  fi
  sleep 5
done
