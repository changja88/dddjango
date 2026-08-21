#!/bin/zsh
# BK2 감시 v7 — O-5 delivery 3런(t2ab-r04·r05·r06). 전자동(bypass) 봉투라 권한
# 프롬프트가 없다 — 감시 대상은 ⓐ 게이트/STOP 질문(자동 응답 금지·알림만)
# ⓑ 오류 문면 ⓒ 주입 발화 ⓓ 유휴(완주·정지). 5초 폴링.

EV=/Users/hyun/.claude/jobs/48c8a476/tmp/bk2-events.log
QDIR=/Users/hyun/.claude/jobs/48c8a476/tmp/gate-questions
mkdir -p $QDIR

ev() { print -r -- "[$(date '+%m-%d %H:%M')] $1" >> $EV }

typeset -A pend idle_n seen_inj done_f
for a in t2ab-r04 t2ab-r05 t2ab-r06; do pend[$a]=0; idle_n[$a]=0; seen_inj[$a]=-1; done_f[$a]=0; done
tick=0

while true; do
  tick=$((tick+1))
  for a in t2ab-r04 t2ab-r05 t2ab-r06; do
    pane=$(herdr agent read $a 2>/dev/null)
    [ -z "$pane" ] && continue
    t=$(print -r -- "$pane" | tail -30)
    n=${a#t2ab-r}
    tgt="/Users/hyun/Desktop/t2ab-R${n}"

    busy=0
    print -r -- "$t"    | grep -qE '\([0-9]+(m [0-9]+)?s' && busy=1
    print -r -- "$pane" | grep -qE 'Waiting for [0-9]+ background|◯ dddjango:' && busy=1

    # 게이트/STOP 질문 — 자동 응답 금지, 알림만
    if print -r -- "$t" | grep -qE 'Enter to select|Ready to submit|Do you want'; then
      if [ "${pend[$a]}" = "0" ]; then
        print -r -- "$pane" | tail -60 > $QDIR/$a.txt
        ev "❓ $a 질문 대기 — $QDIR/$a.txt"
        pend[$a]=1
      elif [ $((tick % 36)) -eq 0 ]; then
        ev "⏸ $a 아직 질문 대기 — $QDIR/$a.txt"
      fi
      idle_n[$a]=0
      continue
    fi
    pend[$a]=0

    ERRPAT='API Error:|rate_limit_error|Claude usage limit reached|You have run out of|Execution error|Killed: 9|Unknown command'
    if print -r -- "$t" | grep -qE "$ERRPAT"; then
      ev "⚠️ $a — $(print -r -- "$t" | grep -E "$ERRPAT" | head -1 | cut -c1-110)"
    fi

    cnt=$(cat "$tgt"/.dddjango/*/injection.jsonl 2>/dev/null | wc -l | tr -d ' ')
    [ -z "$cnt" ] && cnt=0
    if [ "$cnt" != "${seen_inj[$a]}" ] && [ "$cnt" != "0" ]; then
      ev "🔬 $a 주입 발화 — 회전 $cnt"
      seen_inj[$a]=$cnt
    fi

    if [ $busy -eq 0 ]; then
      idle_n[$a]=$(( ${idle_n[$a]} + 1 ))
      if [ ${idle_n[$a]} -ge 24 ] && [ "${done_f[$a]}" = "0" ]; then
        ev "🏁 $a 120초 유휴 — 완주 또는 정지"
        done_f[$a]=1
      fi
    else
      idle_n[$a]=0; done_f[$a]=0
    fi
  done

  if [ $((tick % 180)) -eq 0 ]; then
    ev "· 감시 생존 (주입 R04=${seen_inj[t2ab-r04]} R05=${seen_inj[t2ab-r05]} R06=${seen_inj[t2ab-r06]})"
  fi
  sleep 5
done
