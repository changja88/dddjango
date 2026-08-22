#!/bin/zsh
# BK3 감시 v1 — O-5 delivery codex 3런(R07=wZ:p1·R08=w0:p1·R09=w11:p1).
# pane read 기반(codex 에이전트 등록 지연). 감시: ⓐ 질문/입력 대기(알림만)
# ⓑ 오류 문면 ⓒ 주입 발화(R07 snapshot·R09 sparql — BK3 발화 실측 게이트 핵심)
# ⓓ 유휴(완주·정지). 5초 폴링.

EV=/Users/hyun/.claude/jobs/48c8a476/tmp/bk2-events.log
QDIR=/Users/hyun/.claude/jobs/48c8a476/tmp/gate-questions
mkdir -p $QDIR
ev() { print -r -- "[$(date '+%m-%d %H:%M')] $1" >> $EV }

typeset -A PANE TGT pend idle_n seen_inj done_f
PANE=(r07 "wZ:p1" r08 "w0:p1" r09 "w11:p1")
TGT=(r07 /Users/hyun/Desktop/t2ab-R07 r08 /Users/hyun/Desktop/t2ab-R08 r09 /Users/hyun/Desktop/t2ab-R09)
for a in r07 r08 r09; do pend[$a]=0; idle_n[$a]=0; seen_inj[$a]=-1; done_f[$a]=0; done
tick=0

while true; do
  tick=$((tick+1))
  for a in r07 r08 r09; do
    pane=$(herdr pane read ${PANE[$a]} 2>/dev/null)
    [ -z "$pane" ] && continue
    t=$(print -r -- "$pane" | tail -30)

    busy=0
    print -r -- "$t" | grep -qE 'esc to interrupt|Thinking|Working' && busy=1

    # 질문/입력 대기 — 자동 응답 금지, 알림만 (codex request_user_input·선택지 문면).
    # ▶ 는 파이프라인 진행 표시줄([▶ 설계])에도 쓰여 «행 시작 들여쓰기+▶, 대괄호 없음»으로 한정(v1 오탐 수정).
    if print -r -- "$t" | grep -E '^\s+▶ ' | grep -qv '\[' || print -r -- "$t" | grep -qE '^\s*\? |Select an option|awaiting your (answer|input)'; then
      if [ "${pend[$a]}" = "0" ]; then
        print -r -- "$pane" | tail -60 > $QDIR/bk3-$a.txt
        ev "❓ BK3 $a 질문 대기 — $QDIR/bk3-$a.txt"
        pend[$a]=1
      elif [ $((tick % 36)) -eq 0 ]; then
        ev "⏸ BK3 $a 아직 질문 대기"
      fi
      idle_n[$a]=0
      continue
    fi
    pend[$a]=0

    ERRPAT='Unrecognized command|usage limit|rate limit|stream error|connection error|Killed: 9|error sending request'
    if print -r -- "$t" | grep -qiE "$ERRPAT"; then
      ev "⚠️ BK3 $a — $(print -r -- "$t" | grep -iE "$ERRPAT" | head -1 | cut -c1-110)"
    fi

    cnt=$(cat ${TGT[$a]}/.dddjango/*/injection.jsonl 2>/dev/null | wc -l | tr -d ' ')
    [ -z "$cnt" ] && cnt=0
    if [ "$cnt" != "${seen_inj[$a]}" ] && [ "$cnt" != "0" ]; then
      ev "🔬 BK3 $a 주입 발화 — 누적 $cnt (발화 실측 게이트 신호)"
      seen_inj[$a]=$cnt
    fi

    if [ $busy -eq 0 ]; then
      idle_n[$a]=$(( ${idle_n[$a]} + 1 ))
      if [ ${idle_n[$a]} -ge 24 ] && [ "${done_f[$a]}" = "0" ]; then
        ev "🏁 BK3 $a 120초 유휴 — 완주 또는 정지"
        done_f[$a]=1
      fi
    else
      idle_n[$a]=0; done_f[$a]=0
    fi
  done

  if [ $((tick % 180)) -eq 0 ]; then
    ev "· BK3 감시 생존 (주입 R07=${seen_inj[r07]} R08=${seen_inj[r08]} R09=${seen_inj[r09]})"
  fi
  sleep 5
done
