#!/bin/zsh
# BK1 세 런 감시 v3 — 범위 한정 자동 응답 (사용자 승인 2026-08-21)
#
# 자동 승인: 설치본 캐시/타깃 아래 «읽기»(Search·Read·Glob·Grep) + 위험 토큰 없는 bash
# 알림만  : 그 외 전부 — 쓰기·삭제·네트워크·작업폴더 밖 수정·파이프라인 게이트 질문
#
# 파이프라인 게이트 질문(BC 배치·lens·프레임워크 등)은 «Do you want to proceed?» 가 아니라
# 별도 문구로 뜬다. 그건 절대 자동 응답하지 않고 봉인된 고정 답을 사람이 넣는다.

LOG=/Users/hyun/.claude/jobs/48c8a476/tmp/bk1-autoapprove.log
CACHE='/Users/hyun/.claude/plugins/cache/changja88-dddjango'
typeset -A prompted seen_inj gate
for a in t2ab-r01 t2ab-r02 t2ab-r03; do prompted[$a]=0; seen_inj[$a]=-1; gate[$a]=0; done
fails=0

while true; do
  any=0
  for a in t2ab-r01 t2ab-r02 t2ab-r03; do
    pane=$(herdr agent read $a 2>/dev/null | tail -26)
    [ -z "$pane" ] && continue
    any=1
    tgt="/Users/hyun/Desktop/t2ab-R${a#t2ab-r}"

    if print -r -- "$pane" | grep -q "Do you want to proceed"; then
      # 승인 대상 요약 = 프롬프트 위쪽 동작 줄
      subj=$(print -r -- "$pane" | grep -E "Search\(|Glob\(|Grep\(|Read file|Bash command|Edit file|Write\(|Update\(|WebFetch|WebSearch" | head -1)
      body=$(print -r -- "$pane" | sed -n '/Do you want to proceed/q;p' | tail -12)

      safe=0
      # ① 순수 읽기 — 설치본 캐시 또는 타깃 아래
      if print -r -- "$subj" | grep -qE "Search\(|Glob\(|Grep\(|Read file"; then
        if print -r -- "$body" | grep -qF "$CACHE" || print -r -- "$body" | grep -qF "$tgt"; then safe=1; fi
      fi
      # ② bash — 위험 토큰 없을 때만
      if print -r -- "$subj" | grep -q "Bash command"; then
        if print -r -- "$body" | grep -qE '(^|[^a-z])(rm|mv|curl|wget|ssh|scp|sudo|chmod|chown|kill|dd|npm|pip|brew)[ ]|git (push|commit|reset --hard|clean)|>[ ]*/|install'; then
          safe=0
        else
          safe=1
        fi
      fi

      if [ $safe -eq 1 ]; then
        if print -r -- "$pane" | grep -qE '^[[:space:]]+2\. Yes, allow'; then k=2; else k=1; fi
        herdr agent send-keys $a $k >/dev/null 2>&1
        print -r -- "[$(date '+%m-%d %H:%M:%S')] $a AUTO=$k $(print -r -- "$subj" | cut -c1-140)" >> $LOG
        prompted[$a]=0
      else
        if [ "${prompted[$a]}" = "0" ]; then
          echo "[$(date '+%H:%M')] ⛔ $a 수동 판단 필요 — $(print -r -- "$subj" | cut -c1-110)"
          print -r -- "[$(date '+%m-%d %H:%M:%S')] $a MANUAL $(print -r -- "$subj" | cut -c1-140)" >> $LOG
          prompted[$a]=1
        fi
      fi
    else
      prompted[$a]=0

      # 파이프라인 게이트 질문 — 선택 UI 인데 권한 프롬프트가 아니면 사람이 답한다
      if print -r -- "$pane" | grep -qE '^[[:space:]]*❯[[:space:]]+1\.' ; then
        if [ "${gate[$a]}" = "0" ]; then
          echo "[$(date '+%H:%M')] ❓ $a 게이트 질문 — 봉인된 고정 답 필요"
          gate[$a]=1
        fi
      else
        gate[$a]=0
      fi
    fi

    # 오류·한도 신호
    if print -r -- "$pane" | grep -qiE "API Error|rate limit|usage limit|Execution error|crashed|context low"; then
      echo "[$(date '+%H:%M')] ⚠️ $a — $(print -r -- "$pane" | grep -iE "API Error|rate limit|usage limit|Execution error|crashed|context low" | head -1 | cut -c1-110)"
    fi

    # 주입 발화 — 이 실험의 핵심 관측
    n=$(cat "$tgt/.dddjango/injection.jsonl" 2>/dev/null | wc -l | tr -d ' ')
    [ -z "$n" ] && n=0
    if [ "$n" != "${seen_inj[$a]}" ] && [ "$n" != "0" ]; then
      echo "[$(date '+%H:%M')] 🔬 $a 주입 발화 — 회전 $n"
      seen_inj[$a]=$n
    fi
  done

  if [ $any -eq 0 ]; then
    fails=$((fails+1))
    [ $fails -ge 3 ] && { echo "[$(date '+%H:%M')] herdr 응답 없음 3회 — 감시 불능"; fails=0; }
  else
    fails=0
  fi
  sleep 5
done
