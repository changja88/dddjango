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
    # 카운터는 «(5m 33s · ↓ 16.8k tokens)» 이기도 «(5m 33s)» 이기도 하다 — 토큰 부분을
    # 필수로 걸었다가 또 유휴로 오인했다. 시간만 있어도 작업 중이다.
    print -r -- "$tail26" | grep -qE '\([0-9]+(m [0-9]+)?s' && busy=1
    print -r -- "$pane"   | grep -qE 'Waiting for [0-9]+ background|◯ dddjango:' && busy=1
    print -r -- "$tail26" | grep -qE 'esc to interrupt|Interrupt' && busy=1

    # 선택지가 길면 메뉴가 스크롤돼 «1.» 이 화면 밖으로 나간다 — 그러면 메뉴를 못 알아보고
    # 유휴로 오인했다(R01 STOP-2). 항상 맨 아래 있는 안내 문구로 잡는다.
    menu=0
    print -r -- "$tail26" | grep -qE 'Enter to select|Ready to submit' && menu=1
    print -r -- "$tail26" | grep -qE '^[[:space:]]*(❯[[:space:]]+)?1\.[[:space:]]' && menu=1
    perm=0
    print -r -- "$tail26" | grep -q "Do you want to proceed" && perm=1

    # ───────── ① 권한 프롬프트 ─────────
    if [ $perm -eq 1 ]; then
      # 좁은 판에서 긴 명령이 줄바꿈되면 헤더가 수십 줄 위로 밀린다 — 창을 넉넉히 잡는다.
      # 그리고 «첫» 프롬프트에서 자르면 안 된다: 스크롤백에 앞 프롬프트 잔상이 남아 있으면
      # 거기서 끊겨 현재 프롬프트의 헤더를 통째로 놓친다(subj 가 비어 MANUAL 로 떨어졌다).
      pn=$(print -r -- "$pane" | grep -n "Do you want to proceed" | tail -1 | cut -d: -f1)
      blk=$(print -r -- "$pane" | sed -n "1,${pn}p" | tail -400)
      # 판이 좁으면 «Bash command» 가 두 줄로 쪼개지고 명령 상자가 │ 없이 들여쓰기만 쓴다.
      # 그래서 헤더는 낱말 단위로 찾는다.
      subj=$(print -r -- "$blk" | grep -E "Search\(|Glob\(|Grep\(|Read file|Bash|Edit file|Write\(|Update\(|WebFetch|WebSearch" | tail -1)
      # 헤더를 끝내 못 찾는 경우가 반복됐다(판 폭·스크롤백·렌더 변형). 그때마다 MANUAL 로
      # 떨어뜨리면 밤새 멈춘다. «모르면 멈춤»을 기본값으로 두지 않되 검사는 그대로 건다 —
      # 아래 bash 분기의 위험 토큰 + 경로 가드를 통과해야 승인된다.
      [ -z "$subj" ] && subj="Bash"
      body=$blk
      safe=0
      if print -r -- "$subj" | grep -qE "Search\(|Glob\(|Grep\(|Read file"; then
        { print -r -- "$body" | grep -qF "$CACHE" || print -r -- "$body" | grep -qF "$tgt"; } && safe=1
      fi
      # 헤더가 «Bash command» 로 붙어 있기도 하고 좁은 판에서 «Bash» / «command» 로
      # 쪼개지기도 한다 — 탐지 패턴만 고치고 이 분기 조건을 안 고쳐서 한 번 더 놓쳤다.
      if print -r -- "$subj" | grep -q "Bash"; then
        # 명령 상자는 판 폭에 따라 «│ …» 이기도 하고 들여쓰기만이기도 하다.
        # │ 가 없으면 프롬프트 직전 40줄을 명령 문면으로 본다 — 비어 있으면 검사가
        # 통째로 건너뛰어 무조건 승인이 되는 구멍이 생긴다(넓은 창의 산문 오탐보다 나쁘다).
        cmd=$(print -r -- "$blk" | grep -E '^[[:space:]]*│')
        [ -z "$cmd" ] && cmd=$(print -r -- "$blk" | tail -40)
        # 경로 가드 — 시스템 경로·홈 설정 파일이 보이면 사람이 본다.
        if print -r -- "$cmd" | grep -qE '(^|[^A-Za-z0-9_./~-])/(etc|usr|bin|sbin|System|Library|Applications|Volumes|opt)/'; then
          guard=1
        elif print -r -- "$cmd" | grep -qE '~/\.[a-z]|/Users/[^/ ]+/\.(ssh|aws|gnupg|config|zshrc|zprofile|gitconfig|npmrc)'; then
          guard=1
        else
          guard=0
        fi
        if [ $guard -eq 1 ]; then
          safe=0
        elif print -r -- "$cmd" | grep -qE '(^|[^a-zA-Z])(rm|curl|wget|ssh|scp|sudo|chmod|chown|kill|npm|pip|brew)[[:space:]]|git[[:space:]]+(push|reset[[:space:]]+--hard|clean)|pip[[:space:]]+install'; then
          safe=0
        else
          safe=1
        fi
      fi
      if [ $safe -eq 1 ]; then
        # 세션 허용 문구는 두 가지다: «2. Yes, allow …» / «2. Yes, and don’t ask again for:»
        # (굽은 아포스트로피 주의). 있으면 2 를 골라 이후 재질문을 없앤다.
        if print -r -- "$tail26" | grep -qE '^[[:space:]]*2\. Yes, (allow|and don)'; then k=2; else k=1; fi
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
