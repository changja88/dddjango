결론(2026-10-01 · 3차): 2회차 마감 확인 두 편의 새 지적(규칙 major 2 · minor 5 · nit 3 · 재현 major 1 · minor 1)을 모두 고쳤다.
- 묶음 커밋은 `d430c620`(Wn · 2차와 같음) · `bd15cae0`(W8e — 3회차 마감 fixup 을 접은 판)이다. 패치는 main `86fc3c24` 위에 차례로 붙고 트리 해시가 같다(`3f6e4762…` · `e866d868…`).
- `make verify-web`: Wn exit 0(16 파일) · W8e exit 0(18 파일) · `claude plugin validate dddjango-web --strict` 통과.
- D13 은 재현 리뷰 **권고 H** 로 바꿨다: 허용치 = 키마다 큰 쪽(기준 판 개수 · 지금도 같은 줄에 살아 있는 main 판 위반 수). 효과는 다음과 같다.
  - 리뷰어의 실제 ruff 합성: 정답 10 · 이번 도구 10(2회차 도구는 14).
  - 현장 P1 48 · P2 225 · P2M 225 그대로.
  - mypy 도 같은 원리다.
- 판정 불가(서식 설정 파일 없음 · mypy 기준선 없음 · 병합 판 실패)는 더 막지 않는다. G2 배너 ③′ «정적 검사 행»으로 올린다.
- 픽스처는 `fixtures_static_delta.sh` 65 · `fixtures_inputs_log.sh` 22 이고, 변이는 도구 22/22 · inputs 12/12 를 모두 잡는다.
- §0 이 3회차 처분이고, 그 아래 §1~§8 은 2차 기록이다(3차로 바뀐 곳은 §0 에 적었다).

# 속도 개선 1순위 — web 구현 기록(Wn · W8e)

- 입력: `design-tier1.md` v3(§3 W1~W4 · §4) · 종결 확인 `review-t1-tool/closure-v3.md`(V1~V3) · 구현 리뷰 둘 `review-impl-web-sem/review.md`(규범 문면 — major 3 · minor 10 · nit 5) · `review-impl-web-mech/review.md`(재현 — major 2 · minor 4 · nit 3) · 사용자 결정(G2 전 린트·서식 범위 «서식만 손댄 파일 전체») · 운영 세션 W1 확인(Codex 0.159.2 `codex exec`).
- 기준: main `86fc3c24`(8e `fd5834c8` 포함). 워크트리 브랜치 `worktree-agent-afbf6bda4bd10a725`(시작 때 옛 커밋 `acbfffda` 에 있어 main HEAD 로 맞췄다).
- 표기: `CL` = `dddjango-web/commands/dddjango-web.md` · `CX` = `codex-dddjango-web/skills/dddjango-web/SKILL.md` · `CW` = `dddjango-web/agents/coder-web.md` · `DR` = `dddjango-web/agents/design-review-web.md` · `DA` = `implementation-ui/references/design-acquisition.md` · scratch = `/private/tmp/claude-501/-Users-hyun-Desktop-dddjango/ed01792c-e467-4a58-a794-ed16237ffb9e/scratchpad/impl-web-t1/`. 줄 번호는 `86bb1792` 기준.
- **[실측]** = scratch 실행·파일에서 직접 셌다.

## 0. 3회차 처분(2회차 마감 확인 두 편)

### 0-1. 규칙 쪽 마감(`review-impl-web-sem/closure.md`) — 앞 18 중 17 닫힘 · n2 미룸 수용

| 지적 | 처분 | 자리 |
|---|---|---|
| **N-M1** 도구 주인 표지 «네가 고친다»(병합 안 레인 편집·이력 밖 병합 유입)가 규범과 어긋남 | 표지를 «— 마지막 기능 슬라이스 재개봉»으로 바꿨다. 픽스처 G1⁵(형제 병합 `pkg/sib.py` 표지 단언)와 변이 S13 으로 지킨다 | `static_delta.py:461-462` |
| **N-M2** coder 가 조건 없이 `ruff format` | 진입 출력이 `<산출물 폴더>/static-entry.txt` 로 남는다. coder 입력에 «정적 검사 진입 기록»을 둔다. coder 는 그 `[static] ruff …` 줄이 «서식 판정 가능»일 때만 그 실행기 그대로 서식을 맞춘다(실행기를 새로 고르거나 설치하지 않는다) | 도구 `main()` · `CL:212`·`CX:235`(입력) · `CW:33`·`:57`(+ Codex 같은 줄) · 픽스처 E1‴ |
| N-m1 배선·골격 `ruff check --fix` | `--fix` 는 빌드 폴더에만 쓴다. 배선·골격은 `ruff format` 과 도구가 찍은 신규 줄 손 수정만 한다(«기존 위반·import 제거로 동작 변경» 명시). 도구 표지도 같다 | `CL:229`·`CX:252` 발견 고치기 · 닫힌 목록 `CL:8`·`:280` |
| N-m2 «기준선 없음»·«병합 판 실패»가 막힘 | 판정 불가로 일관화했다. 신규에 넣지 않고 막지 않는다. 도구 끝 줄 `[static] 배너 정적 검사 행:` 을 G2 배너 **③′ 정적 검사 행(항상)** 으로 옮긴다. «손대지 않은 파일(상호작용)» → 원인 편집의 기능 슬라이스(모르면 마지막) 재개봉 | `CL:232`·`CX:255`(byte 대조 문단 · 동일) · 픽스처 G7·G16b·G18 · 변이 S15·S16 |
| N-m3 «미커밋·미추적» 갈 길 | 표지와 문면을 함께 바꿨다: «만든 슬라이스(모르면 마지막 기능 슬라이스)로 커밋해 그 파견 슬라이스 `commits` 에 적거나, 버릴 파일이면 지운 뒤 다시». 픽스처 G1⁶ | 도구 owner · `CL:229` |
| N-m4 D13 과다 | 재현 리뷰 H 로 처분(0-2) | — |
| N-m5 훅·Makefile 로만 감지된 ruff 의 서식 | 설정 파일(`[tool.ruff]`·`ruff.toml`·`.ruff.toml`)이 없으면 «서식 판정 불가»로 두고 막지 않는다(배너 행). Makefile 감지는 `ruff check|format` 호출 줄과 설치 줄 아닌 `mypy` 줄로 좁혔다. 픽스처 E6·E6′·G16 · 변이 S14·S17 | 도구 `detect`·`tools` · `CL:229` |
| N-n1 슬라이스 0 정의 불일치 | `slice-0*` 이름 · 리팩토링 모드 · **이름 없는 `slices[0]` 은 build-state `test_baseline` 이 있을 때만**(슬라이스 0 이 있을 때만 적는 기록). 필드 P1(`slice-1-data`)·P2(이름 없음 · `test_baseline` 없음)는 기능 슬라이스로 남는다. 픽스처 G15·G17a·G17b · 변이 S12·S18 | 도구 `slice_records` |
| N-n2 verify-web 문단 표지 | 미룸(Makefile 봉인) | — |
| N-n3 `CX:34` 상한 오류 문장 | 그대로 둔다(해 없음 — 리뷰 판단) | — |

### 0-2. 재현 쪽 마감(`review-impl-web-mech/closure.md`) — 앞 9 중 8 닫힘 · NFD/NFC 범위 밖

| 지적 | 처분 | 근거 |
|---|---|---|
| **N1** D13 과다 계산(합성 4/14 · 현장 0) | **권고 H 채택**. ruff: 허용치 = 키마다 max(기준 판 개수, B 판 위반 가운데 difflib 대응 줄이 지금도 있고 그 줄에 같은 키가 있는 것의 개수). mypy: 같은 원리로 B 판 풀어 돈 오류 가운데 살아 있는 줄의 것만 뺀다(환경 재현 확인 유지 · 실패면 B 판에도 그대로 있는 줄의 오류만 판정 불가). 기준은 `pre_run_head`(dirty 면 `git_snapshot`) 그대로 | 리뷰어 실제 ruff 합성(`d13real.sh` — 그 스크립트를 내 scratch 경로로 옮김) → **정답 10 = 도구 10**(2회차 14). 픽스처 G19(F1~F14 판형 정답 10 · 파일별 단언) · G13 · G21(mypy H) · 변이 S19(개수만) · S20(2회차 규칙) · S22(mypy) 검출 · 현장 48/225/225 불변 |
| **N2** 구문 오류 파일이 도구 전체를 «미실행»으로 | `ruff format --check` exit 2 라도 JSON 이 읽히면 받는다. `invalid-syntax` 는 «구문 오류 — 서식 판정 불가» 발견으로 올리고 나머지(mypy 포함)는 계속 돈다. 실제 ruff 0.16.4 출력 형태를 확인했다(`synprobe/`) | 픽스처 G20·G20′ · 변이 S21 |
| nit main 이 깨뜨린 새 파일의 서식 꼬리표 «신규» | 판정은 맞으므로 그대로 둔다 | — |

### 0-3. 운영 세션 W1(3회차 직전 반영분 · 그대로)

- `CX:34`: 결과를 모두 받았으면 `wait_agent` 를 다시 부르지 않는다(남은 대상이 불확실하면 `list_agents`).
- `CX:29`·`:196`·`:213`: `close_agent` 는 도구 목록에 있을 때만.

### 0-4. 3회차 검증 [실측]

| 항목 | 결과 |
|---|---|
| `fixtures_static_delta.sh` | 64/64(Claude · Codex 배치) — 새 사례 E1‴·E6·E6′·G1⁵·G1⁶·G16·G16b·G17a·G17b·G18·G19(+8)·G20·G20′·G21 |
| 도구 변이(`mutate_static_delta.py` → `mutation-static-delta.log`) | **21/21 KILLED**. S1~S22 에서 S3 은 뺐다 — ruff 가 `olds()` 를 더 쓰지 않아 같은 뜻이 S19·S20 으로 옮겨 감 |
| `fixtures_inputs_log.sh` · 변이 | 22/22 · 12/12(2회차와 같음) |
| 현장(독립 gitdir 사본 · `repro_w4_tool.py`) | P1 ruff 48 · 서식 34(기존 4) · mypy 0 / P2 225 · 22(4) · 0 / P2M 225 · 22(4) · 0 · 재제출 같은 출력 · 실행기 부재 STOP · `.venv` 생김 없음 · `uv.lock`·`.venv` 지문 무변 · 배너 행 예: `정적 검사(HEAD ab97d0964): ruff 신규 48 · 서식 34(기존 4) · mypy 신규 0` |
| 사본 뒷정리 | 진입이 새로 남기는 `static-entry.txt` 를 재생 스크립트가 지우게 고쳤다(사본 git status 0) |
| `make verify-web` | Wn(`d430c620` 체크아웃) exit 0 · 16 파일 / W8e(`421dba17`) exit 0 · 18 파일 · 실패 0 |
| validate · 미러 | `--strict` 통과(두 상태) · scripts `diff -rq` 동일 · W4 문단 · ①′ · G2 배너 · coder 입력·`:57` 치환 뒤 동일 |
| 패치 | `86fc3c24` 에 `git am` → 트리 `3f6e4762…` · `ef97c86b…` = 커밋 트리 |

### 0-5. 남은 위험(3차 갱신)

- **(a)** 2차 §5 (a) «넘쳐 세기»는 H 로 닫혔다. 남는 것은 키 개수 비교의 본래 사각이다(새 결함 아님 · 1·2회차 규칙에서도 같았다).
  - 레인이 기준 판 위반 하나를 지우고 같은 키를 새로 만들면 셀 수 없다(리뷰어 확인 · T 와 같다).
  - **main 쪽 변형**[규칙 리뷰 3회차 실측 `review-impl-web-sem/r3/h-probe.txt`]: 기준 판에 E711 하나가 있고 main 이 그 줄을 고치며, 레인이 같은 파일 다른 줄에 E711 을 새로 넣고 병합하면 ruff 신규 0 · exit 0 이다. 기준 판 몫(개수 1)을 줄 대응 없이 허용하기 때문이다.
  - 닫으려면 기준 판 몫도 H 처럼 줄 대응으로 세야 한다. 그 대가로 레인이 고친 줄의 기존 위반이 레인 몫이 되어 «ruff 신규만» 결정의 해석이 걸린다 → 설계 판단으로 넘긴다.
- **(b)** 판정 불가는 막지 않는다. 서식 설정 파일 없음 · mypy 기준선 없음 · 병합 판 환경 재현 실패가 그렇다. 사용자가 G2 배너 ③′ 에서 판단하는데, 그 몫의 레인 위반이 있을 수 있다(운영 지시대로 막힘 대신 표면화).
- **(c)** H 의 줄 대응은 difflib 이다. 작은 파일에서 같은 글자 줄이 가까이 다시 생기면 그 줄을 «살아 있음»으로 볼 수 있다(픽스처는 리뷰어 판형대로 세 함수 16줄 · 실제 ruff 합성은 정답과 같다).
- **(d)** coder 서식은 진입 기록의 실행기 줄에 매인다. 진입 기록이 없는 재개(이 규칙 전 진입)는 coder 가 서식을 돌리지 않는다. 그 몫은 G2 전 정적 검사가 잡는다.

### 0-6. 3회차 마감 확인(`review-impl-web-sem/closure-r3.md`) — 2회차 10 중 9 닫힘 · n2 미룸 · 처분

| 지적 | 처분 | 자리 · 검증 |
|---|---|---|
| **R3-m1** 병합 판 환경 재현 실패 때 손댄 파일 안 mypy 오류까지 판정 불가(막지 않음) | 판정 불가는 **레인이 손대지 않은 파일**에서 병합 판에도 그대로 있는 줄의 오류로만 한정했다. 손댄 파일 안은 신규로 남는다(fail-closed · 2회차와 같은 쪽). H 흡수(재현 성공 때)는 그대로 손댄 파일에도 적용한다 | `static_delta.py` 실패 갈래 한 줄 · `CL:229`·`CX:252` 문면 · 픽스처 G7′·G7‴(env 불일치 판형에서 main 이 손댄 파일 `co.py` 에 넣은 오류 = 신규) · 변이 S23 검출 · G21(H 흡수) 유지 |
| R3-n1 H 설명이 기준 판 몫까지 덮는 것처럼 읽힘 | «병합 판 위반 가운데 레인이 고치거나 새로 만든 줄의 것은 레인 몫»으로 좁혔다 | `CL:229`·`CX:252` |
| R3-n2 main 쪽 변형 사각(새 결함 아님) | 남은 위험 §0-5 (a)에 적었다 · 설계 판단 | — |
| R3-n3 coder 의 타입/린트 확인에 실행기 미정 | «인계된 정적 검사 진입 기록의 `[static] <도구> 실행기 …` 줄의 실행기로 확인한다(그 줄이 없는 도구는 돌리지 않는다)» | `CW:57` + Codex 같은 줄 |

- 검증[실측]: `fixtures_static_delta.sh` 65/65 · 도구 변이 22/22 · `make verify-web` exit 0(18 파일 · 실패 0) · `--strict` 통과 · scripts byte 미러 · W4 문단·coder `:57` 치환 뒤 동일 · 패치 트리 `e866d868…` 일치.

## 1. 묶음별 변경

### 1-1. Wn — 커밋 `d430c620` · `01-Wn.patch`

| 파일 | 변경 |
|---|---|
| `DA` §3 4번(Claude · Codex byte 미러) | 미리보기 장식(기기 틀·노치·상태줄·홈 막대·캔버스 배경·목업 그림자) 판별 단락. 장식 판정은 근거(원본 미리보기 전용 설정 · 발주서·사용자 문장)를 인용한다. **이미지 단독 시안은 Phase 0 에서(입력범위 검토 전) 한 번 «장식인가»를 묻는다**. 근거가 없으면 앱 요소로 남긴다. 비교 기준 = 제품 모드 캡처(없으면 장식을 뺀 앱 경계 크롭 + 기록). 장식은 구현으로 옮기지 않는다 |
| `DR` «G0 입력범위 모드» · Codex 같은 절 | 장식 판별·비교 기준 대조 — **비교 기준 캡처에** 장식이 섞였거나, 판정 근거가 없거나, 기준 기록이 없으면 입력 부족. 원본 미리보기 렌더에 장식이 있다는 사실만으로는 입력 부족이 아니다 |

### 1-2. W8e — 커밋 `86bb1792` · `02-W8e.patch`

| 항목 | 자리 | 변경 |
|---|---|---|
| W1 | `CX:34` | `wait_agent` `timeout_ms` = 300000 · 상한 오류면 그 상한으로 · 끝나면 곧바로 돌아옴 · «30분+ 무진행» 실측은 timeout 반환마다 · **띄운 에이전트의 결과를 모두 받았으면 `wait_agent` 를 다시 부르지 않는다 — 기다릴 에이전트가 없으면 timeout 까지 막힌다 · 남은 대상이 불확실하면 `list_agents` 로 먼저 확인**(운영 세션 실측 반영) |
| W1 | `CX:29` · `CX:196` · `CX:213` | `close_agent` 에 «도구 목록에 있을 때만 / 있으면» 조건(0.159.2 도구 목록에 `close_agent` 없음 — 운영 세션 실측) |
| W2 | `CL:167`·`CX:189`(dc 화면 선택) · `CL:169`·`CX:191`(이미지 단독) | `visual-check.md` 에 장식 판별(근거)·비교 기준 · 이미지 단독은 입력범위 검토 전 한 번 묻는다 |
| W3 | `CL:180`·`CX:203` 판형 ② | inputs 실행 명령(Python·checker·build/project 실제 경로)은 ②에 한 번(바뀌면 다시) · 호출마다 실행 기록은 `inputs-log.tsv`(탭 구분 5칸 = 기록 시각(UTC)·실행자·슬라이스/회차·exit·출력 · 성공 출력 `{"input_digest": "<hex>"}` · coder 행 출력 끝에 순서 준수/위반 · **기록 시각은 두 행 모두 `date -u`**) |
| W3 | `CL:212`·`CX:235` step 3 문단 | 입력 «`inputs-log.tsv:<행>`» · 블록 ① 한 명령(exit = 검사기 exit · **행을 못 쓰면 1**) · 같은 Python·checker·경로를 coder 에 전달 |
| W3 | `CL:213-220`·`CX:236-243` ```sh 블록(Claude·Codex byte 동일) | ① inputs + Coordinator 행(`2>&1` · 탭·줄바꿈 공백화 · 출력은 printf 인자 · `|| { echo "inputs-log 기록 실패"; ec=1; }`) · ② **네 줄** 행 파일 `<산출물 폴더>/.coder-row-<슬라이스>-<회차>.txt` 에 `date -u` 시각을 붙여 `printf '%s\t%s\n'` 으로 넣고 지운다(정확히 네 줄 · 탭 없음일 때만) |
| W3 | `CL:221`·`CX:244` 반환 대조(verify-web byte 대조 문단) | 명령·대상은 ②의 inputs 실행 명령과, 회차·exit·출력은 자기 행과 대조 · digest 일치 · 코더 행은 «셸을 거치지 않는 파일 쓰기(Claude `Write` · Codex `apply_patch`)»로 네 줄 · 시각은 블록이 붙임 |
| W3 | `CW:26`·`:45`·`:48` + Codex 같은 줄 | 입력 행 · 행을 직접 읽어 대조 · «`inputs-log.tsv` 작성 소유는 Coordinator — 너는 쓰지 않는다» |
| W4 | `CL:204`·`CX:227` Phase 2 진입 ①′ | `static_delta.py --phase entry` — ruff·mypy 설정과 실행기를 **함께** 확인하고 버전을 찍은 뒤 `mypy-baseline.txt` 를 남긴다 · exit 3 = STOP · exit 1 = 미실행 · «mypy 대상 미정»이면 `--mypy-args` 로 다시 |
| W4 | `CL:229`·`CX:252` «G2 전 정적 검사» | `static_delta.py --phase g2` 호출 · 판정 규칙 요약 · exit 0/2/3/1 · **발견 고치기**(주인별 — 기능 슬라이스 재개봉 · 빌드 폴더·네 배선·골격은 네가 `ruff format`·`ruff check --fix` 뒤 손으로 · 병합 몫은 마지막 기능 슬라이스 · 슬라이스 0 몫은 슬라이스 0 · 기록 없는 커밋은 기록 뒤 다시) · **정리 커밋은 기능 슬라이스 몫**(리팩토링 모드만 `slices[0]`) |
| W4 | `CW:56` + Codex | 기능 슬라이스에서 손댄 `.py` 는 프로젝트 실행기의 `ruff format` 으로 파일 전체 서식을 맞춘다(슬라이스 0 은 아님) |
| 목록 | `CL:8`·`CX:8` · `CL:280`·`CX:304`(닫힌 «직접 쓰는 것») · `CL:42`·`CX:95`(산출물 위치) | `inputs-log.tsv`(코더 행 임시 `.coder-row-*.txt`) · `mypy-baseline*.txt`(도구 산출) · G2 전 정적 검사 정리(빌드 폴더 `.py`·네 배선·골격 — 동작을 바꾸지 않는 정리만) · 새 기록 파일은 G2 산출물로 폴더에 남는다(별도 커밋 단계 불요 · 마무리 합치기·사용자 커밋 대상 — `render-audit-impl.json` 선례) |
| 도구 | `dddjango-web/scripts/static_delta.py` + Codex byte 미러 | 아래 §1-3 |
| 픽스처 | `scripts/test/fixtures_inputs_log.sh`(22) · `fixtures_static_delta.sh`(39) + Codex byte 미러 | §3-1 · §3-2 |

### 1-3. `static_delta.py` — 규칙

- **entry**: 설정 감지(ruff = pyproject `[tool.ruff]`·`ruff.toml`·`.ruff.toml` · mypy = `mypy.ini`·`.mypy.ini`·pyproject `[tool.mypy]`·`setup.cfg [mypy]` — **또는 `.pre-commit-config.yaml` 훅·`Makefile` 이 그 도구를 돌림**) → 실행기(`uv.lock` 이 있고 **환경(`.venv`/`UV_PROJECT_ENVIRONMENT` 의 `pyvenv.cfg`)이 이미 있을 때만** `uv run --frozen --no-sync <도구>` → `.venv/bin/<도구>`) — 설정은 있는데 없으면 STOP(exit 3). mypy 명령 = `--mypy-args` > pre-commit 훅(`pass_filenames: false` entry 의 `mypy` 뒤) > Makefile 줄. 한 번 돌려 `mypy-baseline.txt`(머리: HEAD · 대상 · 출처 · 실행기 · 버전 · exit) — 실행이 깨지면(exit ∉{0,1} · 요약 줄 없음) STOP.
- **g2 범위 기준**: build-state `pre_run_head`, 없으면 `git_snapshot`(dirty 시작).
- **손댄 파일(W6m 정의)**: 기준..HEAD 첫 부모 비병합 커밋과 미커밋 편집이 바꾼 파일 + main 이력 안 병합의 `git show --cc` 파일 + 둘째 부모가 main 이력 밖인 병합이 들여온 파일 전부. 미추적은 `.dddjango-web/` 밖과 이 산출물 폴더만. 이 산출물 폴더의 동결 원본(`reference_root`)은 검사 밖(줄로 알림). 경로는 전부 `-z`(비ASCII 경로 따옴 없음).
- **병합 판 B**: 첫 부모 병합 가운데 `merge-base --is-ancestor <병합>^2 <기준 가지>`(기본 `main`·`origin/main` · `--base-branch`)가 참인 것 중 **가장 최근 것**의 `^2`.
- **ruff**: `--force-exclude` · 손댄 파일마다 (code · message) 다중집합 차. 옛 판 = 기준 판 — **지금 내용이 B 판과 같은 파일만 B 판**.
- **서식(사용자 결정)**: 손댄 파일 전체가 `ruff format --check`(JSON · 없는 판이면 `Would reformat:`)를 통과해야 한다. **슬라이스 0 커밋만 손댄 파일(빌드 폴더 밖)은 신규만**. 슬라이스 0 = build-state 의 `slice-0*` 이름 슬라이스 기록(리팩토링 모드면 모든 기록) — 이름 없는 `slices[0]` 은 기능 슬라이스, 기록 없는 커밋은 기능 쪽.
- **mypy**: 진입 기준선(머리 HEAD = 이번 실행 진입 HEAD 이고 같은 대상일 때) — 아니면 기준 판을 `git archive -o` + `tar -x -f`(파이프 없음 · 고유 `mkdtemp` · 끝나면 지움)로 풀어 레인 `.venv/bin/mypy` 로 돈 결과. 신규 = (파일 · 코드 · 메시지 `line N` 정규화) 다중집합 차. 남은 신규 가운데 **B 판과 내용이 같은 파일의 것만** B 판을 풀어 돈 결과의 같은 키만큼 뺀다 — 풀어 돈 환경이 기준 판에서 진입 기준선을 그대로 재현할 때만(아니면 «mypy 병합 판 기준선 실패 — <사유>»). 풀어 돈 결과는 `mypy-baseline-{archive,merge}-<약칭>.txt` 로 남겨 재제출 때 다시 돌지 않는다.
- **출력**: `[static]` 요약 줄 · 발견마다 파일과 **고칠 주인**(기능 슬라이스 <이름> · 빌드 폴더 · 진입 산출물 커밋 · 병합 안 레인 편집 · 이력 밖 병합 유입 · 슬라이스 0 · 기록 없는 커밋 · 미커밋) · exit 0/2/3/1. 검사는 아무 파일도 고치지 않는다(쓰는 것은 산출물 폴더의 `mypy-baseline*.txt` 뿐).

## 2. 리뷰·결정 처분

### 2-1. 사용자 결정 — «G2 전 린트·서식 검사는 어디까지 막을까요?» → «서식만 손댄 파일 전체»

| 결정 항목 | 구현 |
|---|---|
| 서식 = 손댄 파일 전체(기존 어긋남 포함) | 도구 서식 판정 · `CL:229` 문면 · 픽스처 G2′(기존 불통과도 막음) · 변이 S2 검출 |
| ruff·mypy = 신규만 | 도구 · 픽스처 G1·G3 |
| 슬라이스 0 은 파일 전체 서식을 다시 쓰지 않음(8e ④ «치환뿐»과 충돌 방지) | 슬라이스 0 전용 파일은 서식도 신규만 · 픽스처 G2″·G8 · 변이 S9 · `CW:56` «슬라이스 0 은 파일 전체를 다시 쓰지 않는다» |
| «손댄 파일» = W6m touched | `design-W5-7.md` v3 §3-4 (2) 정의 그대로(레인 편집 · `--cc` · main 유입 제외 · 이력 밖 병합 유입 포함). **범위 기준만 W4 범위(`pre_run_head`, 없으면 `git_snapshot`)** — W6m 은 `git_snapshot` 이다. 둘 사이는 진입 산출물 커밋(레인 Coordinator 가 쓴 빌드 폴더 산출물·골격·배선)뿐이고, 그 편집도 레인 몫이라 넣었다(fail-closed) |
| 정리 커밋의 슬라이스 | **기능 슬라이스 몫** — 그 파일을 마지막으로 바꾼 기능 슬라이스 재개봉(도구가 주인으로 찍음) · Coordinator 정리(빌드 폴더·배선·골격)는 마지막 기능 슬라이스의 `commits` · 기능 슬라이스가 없는 리팩토링 모드만 `slices[0]`(빌드 폴더는 ④ 밖) · 서식 전체 정리 커밋을 슬라이스 0 몫으로 적지 않음 |

### 2-2. 규범 문면 리뷰(`review-impl-web-sem`) 처분

| 지적 | 처분 |
|---|---|
| **M1** D13 «main 이력 안» 조건 없음 · «마지막 병합» 모호 | 받음: `merge-base --is-ancestor <병합>^2 <기준 가지>` 참인 병합만 · 그중 가장 최근 것 · 이력 밖(형제) 병합 유입은 레인 몫. 도구 + 픽스처 G1(형제 병합 E712 신규) · G14(병합 둘 — 최신) · 변이 S4·S8 |
| **M2** 빌드 폴더 `.py` 발견을 고칠 길이 없다 | 받음: «빌드 폴더(증거·관찰 스크립트 — 누가 썼든)는 네가 같은 실행기로 `ruff format`·`ruff check --fix` 뒤 손으로 · 동작을 바꾸지 않는 정리만» · «검사는 아무 파일도 고치지 않는다 — 고침은 이 단계에서만» · 닫힌 목록에 정리 항목 · 동결 원본(`reference_root`)은 검사 밖 |
| **M3** 다중집합 계산을 레인마다 LLM 이 다시 짠다 | 받음: 도구 `static_delta.py`(byte 미러 · 픽스처 39 · 변이 12/12). 문면은 호출·결과 읽기·고치기만 |
| m1 coder 행 시각 손글씨 | 받음: 행 파일 네 줄 · 블록 ②가 `date -u` 로 붙인다 · 픽스처가 비UTC 시간대(`TZ=Asia/Kathmandu`)에서 분 값으로 UTC 를 확인(변이 R4·R4′ 검출) |
| m2 행 파일이 `$TMPDIR` | 받음: `<산출물 폴더>/.coder-row-<슬라이스>-<회차>.txt`(프로젝트 안) · 붙인 뒤 지운다 · «임시 폴더» 출력 걷음 |
| m3 기준이 B 의 조상이면 B 판 하나 | **바꿔 받음**: 재현 리뷰 M1(F5 — main 위반을 지우고 같은 키를 새로 만들면 «B 판 하나»도 가린다)과 운영 지시에 따라 «지금 내용이 B 판과 같은 파일만 B 판 · 나머지는 기준 판»으로 정했다(§4 D13) |
| m4 mypy 병합 판 «실패» 정의 | 받음: exit ∉{0,1} · 요약 줄 없음 · **풀어 돈 환경이 기준 판에서 진입 기준선을 재현하지 못함**(리뷰 제안 «진입 기준선에 없는 파일 오류 수 비교» 대신 — 그 판형은 진입 오류 0 인 프로젝트에서 main 이 새 파일에 오류 하나만 들여도 실패가 돼 가짜 신규를 만든다). 픽스처 G7 · 변이 S7 |
| m5 dirty 시작 범위 | 받음: 기준 = `git_snapshot` · 픽스처 G9 · 변이 S11 |
| m6 닫힌 목록 | 받음: `CL:8`·`CL:280`·`CL:42`(+ Codex) |
| m7 design-review-web «섞였거나» | 받음: «비교 기준 캡처에» + «원본 미리보기 렌더의 장식만으로는 입력 부족 아님» |
| m8 ①′ 에서 ruff 실행기도 | 받음: entry 가 두 도구 실행기를 확인(픽스처 E1″·E2) |
| m9 pre-commit·Makefile 로만 쓰는 도구 | 받음: 감지에 포함(픽스처 E4) |
| m10 W1 즉시 반환 | 운영 세션이 확인(§2-4) |
| n1 «G0에서» | 받음: «Phase 0 에서(입력범위 검토 전)» |
| n2 verify-web 문단 대조 표지 | 보류: `Makefile` 은 봉인 protocol 그룹이라 이 묶음에서 건드리지 않는다. 새 문단은 픽스처(블록 byte 대조)와 이번 회차 손 대조로 맞췄다 — 다음 protocol 봉인 변경 때 `'**G2 전 정적 검사**'`·`'①′ **정적 검사 진입**'` 표지 추가 권장 |
| n3 블록 ① 기록 실패 | 받음: `|| { echo "inputs-log 기록 실패"; ec=1; }` · 픽스처 I · 변이 N3 |
| n4 미추적 범위 | 받음: `.dddjango-web/` 밖 + 이 산출물 폴더만 · 픽스처 G1″ · 변이 S5 |
| n5 대조 상대 둘 | 받음: 명령·대상 ↔ ② 실행 명령 · 회차·exit·출력 ↔ 자기 행 |

### 2-3. 재현 리뷰(`review-impl-web-mech`) 처분

| 지적 | 처분 |
|---|---|
| **M1** D13 이 F4(서식)·F5(check)에서 레인 위반을 가림 | 받음: 서식은 손댄 파일 전체(사용자 결정)라 병합 판이 끼지 않는다 · ruff·mypy 의 병합 판은 **지금 내용이 그 판과 같은 파일에만**. 실제 ruff 로 F1~F6 재생(§3-4) — F4 E703·서식 · F5 1 모두 센다 · 픽스처 G13 · 변이 S3 |
| **M2** 현장 사본이 원본과 gitdir 공유 | 받음 · §6. 이후 사본은 독립 gitdir(`clone --no-checkout --shared` + `update-ref` + `reset`) |
| m1 픽스처가 출력 칸 내용을 안 봄(R1·R2 생존) | 받음: 사례 B 가 2행 5칸 = stderr 두 줄 원문을 공백으로 이은 값과 **글자 그대로** 같은지(`%s %d \n` 백틱 포함) — R1·R2 검출 |
| m2 실행기 판정이 빈 `.venv` 를 만든다 | 받음: 환경이 있을 때만 `uv run` · 픽스처 E5(uv 프로젝트 모양에서 `.venv` 미생성) · 변이 S6 · 현장 P1·P2·P2M 실행기 부재 판정에서 `.venv` 생김 0 |
| m3 coder 행 시각 | 2-2 m1 과 같음 |
| m4 NFD/NFC | 범위 밖(운영 지시) — §7 |
| n1 픽스처 zsh 직접 실행 | 받음: 셸 목록을 배열로 · 머리 주석에 bash 전용 명시 |
| n2 `-c core.quotepath=off` | 받음: 도구가 git 경로를 전부 `-z` 로 받는다 |
| n3 새 기록 파일 add 시점 | 받음: 산출물 위치에 «G2 산출물로 폴더에 남는다(별도 커밋 단계 불요 · 마무리 합치기·사용자 커밋 대상)» — `render-audit-impl.json` 선례 |

### 2-4. 운영 세션 W1 보강(Codex 0.159.2 실측)

- 반영 위치: `CX:34`(`wait_agent` 를 결과를 다 받은 뒤 다시 부르지 않음 · `list_agents` 확인) · `CX:29`·`CX:196`·`CX:213`(`close_agent` 조건).
- 문장은 운영 지시 취지 그대로이되 «(2026-10-01 실측)» 괄호는 넣지 않았다 — 커맨드 본문은 런타임 프롬프트라 메타 근거를 넣지 않는다(AGENTS.md). core K5 문장도 같은 표현(괄호 없이)으로 맞추기를 권한다: «띄운 에이전트의 결과를 모두 받았으면 `wait_agent` 를 다시 부르지 않는다 — 기다릴 에이전트가 없으면 timeout 까지 막힌다. 남은 대상이 있는지 불확실하면 `list_agents` 로 먼저 확인한다.»

### 2-5. 종결 확인 V1~V3(1차 처분 · 이번 회차 상태)

| 지적 | 상태 |
|---|---|
| V1 대체 경로 `mkdir -p` · 파이프 | 도구 안으로 들어갔다 — `mkdtemp` · `git archive -o` · `tar -x -f` 각 단계 returncode 확인(파이프 없음) · 잘못된 SHA 는 «풀어 돌기 실패» |
| V2 «Write 도구로» Codex | 유지 — byte 대조 문단은 «셸을 거치지 않는 파일 쓰기(Claude `Write` · Codex `apply_patch`)» |
| V3 coder 행 6칸 | 유지 — 로그는 5칸, coder 행 파일은 네 줄(시각은 블록이) |

## 3. 검증

### 3-1. `fixtures_inputs_log.sh` — 22/22 · 변이 12/12 [실측]

- 본문 ```sh 블록 하나를 뽑아(저장소 배치면 Claude·Codex byte 동일 확인) bash·zsh 로 돈다. 사례(셸마다): A 성공(5칸 · digest 칸 · UTC · 임시 파일 삭제) · B 실패(exit 2 · 출력 칸 = stderr 두 줄 원문 · `%s %d \n` 백틱 글자 그대로) · C exit 1 · D coder 행(메타문자 · `$(touch …)` 미실행 · UTC · 행 파일 삭제) · E 다섯 줄 거부 · F 탭 거부 · G1 끝 줄바꿈 없는 네 줄 수용 · G2 행 파일 없음 거부 · H 재제출 · I 로그를 못 쓰면 exit 1.
- 변이(`mutate_inputs_log.py` → `mutation.log`): M1 exit 가림 · M2 탭 미변환 · M3 printf 줄바꿈 보장 제거 · M4 네 줄 검사 제거 · M5 탭 검사 제거 · M6 임시 파일 미삭제 · M7 서식 4칸 · **R1 `2>&1` 제거 · R2 출력을 서식 문자열에 · R4/R4′ `date -u`→`date`(블록 ①·②)** · N3 기록 실패 무시 — 전부 red · 원문 양성 대조 21/21(Codex 미러 없는 배치).

### 3-2. `fixtures_static_delta.sh` — 39/39 · 변이 12/12 [실측]

- 가짜 ruff·mypy(표지 줄 → 발견 · `--force-exclude` 일 때만 exclude · `.fake-env` 가 없으면 생기는 환경 의존 오류)를 임시 git 저장소 `.venv/bin` 에 둔다.
- 사례: E1~E5(진입 기준선·머리 · 두 실행기 버전 · STOP · 설정 없음 · pre-commit 만으로 감지 · uv 프로젝트에서 `.venv` 미생성) · G1(ruff 신규 5 = 다중집합 1 · 빌드 폴더 2 · 미추적 1 · 형제 병합 1 / rename·삭제·migrations·main 유입·다른 빌드 폴더·동결 원본은 아님 · 주인 표지) · G2(서식 = 손댄 파일 기존 불통과 · 슬라이스 0 전용 새 불통과 · 손대지 않은 파일 아님) · G3(mypy — main 판 같은 파일 오류 뺌) · G4(재제출 byte 동일 · 추적 무변) · G5·G6(기준선 없음·머리 불일치 → 풀어 돌기) · G7(환경 불일치 → 병합 판 실패 · 신규 2) · G8(리팩토링 모드) · G9(dirty → `git_snapshot`) · G10(깨끗 exit 0) · G11(기준 가지 못 풂 exit 1) · G12(G2 실행기 없음 STOP) · G13(F5 판형) · G14(병합 둘 — 최신) · G15(이름 없는 `slices[0]` 은 기능 슬라이스 — 필드 build-state 판형).
- 변이(`mutate_static_delta.py` → `mutation-static-delta.log`): S1 `--force-exclude` 빼기 · S2 서식 신규만 · S3 옛 D13(키마다 큰 쪽) · S4 main 이력 검사 없음 · S5 미추적 범위 제한 없음 · S6 `.venv` 확인 없이 uv · S7 환경 재현 확인 없음 · S8 가장 오래된 병합 · S9 슬라이스 0 전용 판정 없음 · S10 집합 · S11 dirty 기준 없음 · S12 `slices[0]` 자리로 슬라이스 0 — 전부 red.
- **필드 판형이 잡은 결함**: 처음 도구는 subst 처럼 `slices[0]` 자리를 슬라이스 0 으로 봤다. P1 의 `slices[0]` 은 `slice-1-data`, P2 는 이름이 없어 첫 기능 슬라이스가 서식 면제를 받을 뻔했다 → 이름(`slice-0*`)·리팩토링 모드로만 정함(G15 · S12).

### 3-3. W3 현장 재현 — `repro_w3.py` → `repro-w3.md` [실측 · 독립 gitdir 사본]

- 대상: `repro/p1`(P1 G2 `ab97d0964` · `.dddjango-web/20260908-1534-web-chart`) · `repro/p2`(P2 G2 `9938cbc48` · `20260922-1647-teller-detail-sheet`). 워크트리 `CL` 블록 ①②를 뽑아 실제 `check_design_evidence.py`(워크트리판)·사본 `.venv/bin/python` 으로 zsh 실행. coder 행 파일은 셸 밖(파이썬)에서 네 줄 · 끝 줄바꿈 없이.
- 결과(P1 · P2 같음): ① 정상 exit 0 · ② exit 0 · ① 훼손(`design-input.json` 한 바이트) exit **2** · ① 재제출 exit 0 · 4행 전부 5칸 · 시각 칸 전부 UTC 모양 · digest coordinator = coder = 재제출(P1 `29f0352e…` · P2 `db171872…`) · coder 칸 메타문자 글자 그대로 · `$(touch …)` 미실행 · 임시 파일·행 파일 남음 0 · 추적 파일 변경 0(새 항목 = `inputs-log.tsv` 하나).
- 사전 조치: checkout 뒤 `design-ref` 한글 이름 53개를 manifest 정규형(NFD)으로 맞춤(`nfd_align.py` · 사본만) — §7.

### 3-4. W4 현장 재현 — 도구 `repro_w4_tool.py` → `repro-w4tool-{P1,P2,P2M}.json` · `repro-w4tool-summary.txt` [실측 · 독립 gitdir 사본]

- 절차: `pre_run_head` 체크아웃 → `--phase entry` → G2 커밋 체크아웃 → `--phase g2` 두 번 → `.venv` 치우고 entry(실행기 부재) → 기준선 파일 지우고 원래 HEAD 로. 필드 build-state 를 그대로 읽는다. P2M = P2 G2 + 발주자 검증 시작(01:57) 때 main `2ec34a79a` 를 사본 안에서 병합한 판.

| | P1 | P2 | P2M | 발주자 |
|---|---|---|---|---|
| 실행기 | `uv run --frozen --no-sync` ruff 0.16.4 · mypy 2.3.1 | 같음 | 같음 | — |
| mypy 명령(자동 감지) | `mypy spring_dream_server framework`(출처 pre-commit 훅) | 같음 | 같음 | 같은 훅 |
| 범위 · 손댄 .py | `pre_run_head` 3b4e37ab2 · 44 | 2ac61e611 · 39 | 2ac61e611 · 39 | 레인 편집 42 · — |
| 병합 판 | 116fd95b0^2 | 6b527036a^2 | 1a8281c0f^2(= 2ec34a79a) | — |
| **ruff 신규** | **48** | **225** | **225** | 48 · 225 |
| **서식 불통과**(그중 기존) | **34**(4) | **22**(4) | **22**(4) | 32 · 17 |
| 신규만 판(1차 결과) 대비 | +4 = 제품·시험 2(`test_chart_view_model.py`·`chart_view_model.py`) + 빌드 폴더 `_history/` 로 옮긴 옛 스크립트 2 | +4 = `test_conversation_{ui_behavior,view,view_model}.py`·`conversation_view_model.py` | +4 | — |
| mypy 신규 · 오류 | 0 · 0 | 0 · 0 | 0 · 0 | P2 «새 2(합친 트리)» |
| 재제출 | 같은 출력 | 같은 출력 | 같은 출력 | — |
| 실행기 부재 | STOP · `.venv` 생김 없음 | 같음 | 같음 | — |
| `uv.lock` · `.venv`(39,086 파일 지문) · git status | 무변 | 무변 | 무변 | — |
| 시간(진입 · G2 첫 · 재제출) | 14.7 · 34.5 · 30.9초 | 15.7 · 39.2 · 23.8초 | 16.6 · 14.6 · 8.5초 | — |

- ruff 는 발주자 수치와 같다. 서식은 «손댄 파일 전체» 정책에서 P1 34 · P2 22 로 리뷰 재계산(§5 정책 B 34 · 22)과 같다. 발주자 실제 값(32 · 17)과의 차이는 모집단 차이다(리뷰 §5 — 발주자의 대상 집합·HEAD 가 다름).
- 서식 목록의 빌드 폴더 밖 파일과 주인: P1 = `slice-2-fragment`·`slice-3-fortune`·`slice-6-visual-preserved-sections` · P2 = `slices[5]`·`slices[8]`(필드 기록에 이름이 없음).
- mypy 0 은 이 환경의 성질이다(main 도 오류 0). 발주자 환경의 «main 기저 8 → 합친 뒤 10»은 재현되지 않았다 — 병합 판 mypy 규칙은 합성(픽스처 G3·G7)으로 확인했다.

### 3-5. D13 합성 — 실제 ruff 0.16.4 · `tool_d13_real.py` [실측]

| 파일 | 상황 | 도구 결과 | 레인 위반 |
|---|---|---|---|
| F1 | main E711 · 레인 병합 뒤 같은 키 E711 | 2(main 몫 함께) | 1 — 가리지 않음(넘쳐 셈) |
| F2 | main E711 · 레인 E712 | 2(E711 main · E712 레인) | 1 — 가리지 않음 |
| F3 | 레인 병합 전 E711 · main E711 | 2 | 1 — 가리지 않음 |
| F4 | main 이 서식 깸 · 레인 E703 + 서식 | check 1(E703) · 서식 1 | 둘 다 셈 |
| F5 | main E711×2 · 레인이 지우고 다른 줄 E711 | 1 | 1 — 셈 |
| F6 | main 만 · 레인 미편집 | 0 | 0 |
| 형제 가지 병합 | 형제 E711 | 1 | 1(레인 몫) |
| 병합 둘 | 가장 최근 main 병합의 `^2` 사용 | ✓ | — |

- 넘쳐 세기(F1~F3): 레인이 고친 파일 안의 main 위반이 함께 세진다(fail-closed). 그 파일은 레인이 손댄 파일이라 «서식 전체»와 같은 쪽의 부담이다.

### 3-6. verify-web · validate · 패치

| 시점 | 결과 |
|---|---|
| 손대기 전(main `86fc3c24`) | exit 0 · 16 파일 · 5분 2초 |
| Wn(`d430c620` 트리) | **exit 0 · 16 파일 실패 0** · validate 통과 |
| W8e(`86bb1792` 트리) | **exit 0 · 18 파일 실패 0** · `fixtures_inputs_log: PASS=22` · `fixtures_static_delta: PASS=39` · validate 통과 |
| 패치 | scratch 클론 `86fc3c24` 에 `git am 01-Wn.patch 02-W8e.patch` → 트리 `3f6e4762…` · `972b6a17…` = 두 커밋 트리 |
| Claude·Codex | 바뀐 문단 전부(verify-web 대조 6종 · 블록 · W4 문단 · ①′ · 판형 ② · 산출물 위치 · W2 두 줄 · coder-web 네 줄 · design-review-web 한 줄)가 치환 둘(`${CLAUDE_PLUGIN_ROOT}`→`${SKILL_DIR}` · `Bash로`→`네이티브 셸로`) 뒤 같다 · scripts(도구·픽스처) `diff -rq` 동일 · `DA` byte 동일 |

## 4. 설계와 다르게 한 것(까닭)

| # | 설계 v3 | 구현 | 까닭 |
|---|---|---|---|
| D1 | 블록 ② `paste -sd '\t' … >>` | `printf '%s\t%s\n' "$(date -u …)" "$(paste -sd '\t' "$row")" >>` | BSD paste 끝 줄바꿈 누락으로 행이 붙음 · 시각은 블록이 찍음(리뷰 m1) |
| D2 | coder 행 6칸(V3) | 로그 5칸 · coder 행 파일 네 줄 | V3 · 시각 손글씨 금지 |
| D3 | 판형 ②에 명령·경로 칸 없음 | ②에 inputs 실행 명령·경로를 한 번(바뀌면 다시) | 옛 ②의 «실행 명령, build/project 대상 실제 경로» 보존 |
| D4 | `$TMPDIR/…` 행 파일 | 검사기 출력 임시만 `${TMPDIR:-/tmp}` · 행 파일은 `<산출물 폴더>/.coder-row-*`(프로젝트 안) | `TMPDIR` 없는 셸 · 파일 쓰기 도구의 프로젝트 밖 쓰기 권한(리뷰 m2) |
| D5 | 블록 ② 검사 없음 | 정확히 네 줄 · 탭 없음일 때만 | 칸 깨짐 fail-closed |
| D6 | 진입 기준선 지시가 3-1 안에만 | Phase 2 진입 ①′ · ⑤ 목록 | 기준선이 실제로 남게 |
| D7 | 기준선 머리 = 명령·버전·exit | + 진입 HEAD · 대상 · 출처 · 다르면 없는 것으로 | 재사용 폴더의 낡은 기준선 차단 |
| D8 | `ruff format --check … <대상>` | JSON(`--output-format json`) · 없는 판이면 `Would reformat:` | ruff 0.16 출력 형식 |
| D9 | W2 Coordinator 줄은 dc 화면 선택만 | 이미지 단독 줄에도 | v3 예외가 실제로 돌게 |
| D10 | `DA` 의 «P2 의 …»·«`CX:190`» | 메타 언급 뺌 | 런타임 프롬프트 |
| D11 | «정한 명령을 실행기로» | 대상·옵션 그대로 · 실행기 부분만 교체(도구가 pre-commit `entry` 에서 `mypy` 뒤를 뽑음) | 훅 명령의 `uv run` 은 `uv.lock` 을 다시 쓴다 |
| D12 | — | «기준선 없음 — 전부 신규»는 배너에 올려 사용자가 판단 | 명시 |
| **D13** | 옛 판 = `pre_run_head` 판만 | 병합 판 B = 레인 안 main 이력 안 병합 중 **가장 최근 것**의 `^2` · **지금 내용이 B 판과 같은 파일만 B 판**, 나머지는 기준 판 · 이력 밖(형제) 병합 유입은 레인 몫 · 서식(손댄 파일 전체)에는 병합 판을 쓰지 않음 · mypy 는 B 판과 같은 파일의 B 판 오류만 뺌(환경 재현 확인 뒤) | v3 는 main 이 들인 파일을 레인 신규로 셌다(P1·P2 `tests/web/intake/*` 둘). 1차 D13(키마다 큰 쪽)은 형제 병합·F4·F5 에서 레인 위반을 가렸다(두 리뷰 M1). 지금 판형은 레인 위반을 가리지 않고(F1~F6 · 픽스처 G13·G14), 레인이 고친 파일 안의 main 위반은 함께 셀 수 있다(넘침 — fail-closed). **설계 소유자 확인 권장** |
| D14 | W4 계산은 Coordinator 가 문면대로 | 도구 `static_delta.py` | 리뷰 M3 — 레인마다 손셈이 흔들림 · 결정적 · 픽스처로 지킴 |
| D15 | 서식 = 신규만 | 손댄 파일 전체 · 슬라이스 0 전용은 신규만 | 사용자 결정 |
| D16 | 빌드 폴더 발견 처리 없음 | 빌드 폴더·네 배선·골격은 Coordinator 가 정리 · 정리 커밋은 기능 슬라이스 몫 | 리뷰 M2 · 사용자 결정(정리 커밋 슬라이스) |
| D17 | — | `CW:56` 기능 슬라이스가 손댄 `.py` 를 파일 전체 서식으로 | 서식 정책을 슬라이스 안에서 미리 맞춰 G2 재개봉을 줄인다(속도 · 같은 정책) |
| D18 | m4 제안 «진입 기준선에 없는 파일 오류 수 비교» | «풀어 돈 환경이 기준 판에서 진입 기준선을 재현» | 제안 판형은 main 이 새 파일에 오류 하나를 들여도 실패로 봐 가짜 신규를 만든다 · 환경 재현 대조는 직접적이다(1회 비용 · 파일로 남겨 재사용 · 레인 신규가 병합 판 같은 파일에 있을 때만 돈다) |

## 5. 남은 위험

- **(a) 넘쳐 세기**: 레인이 고친 파일 안의 main 위반(ruff)은 레인 신규로 함께 세진다(D13). 레인이 범위 밖 수정을 하게 될 수 있다 — 기능 슬라이스가 그 파일을 손댄 경우뿐이고, 서식 전체 정책과 같은 방향의 부담이다.
- **(b) mypy 병합 판**: 풀어 돈 환경(`git archive` — 미추적 설정 없음)이 진입 기준선을 재현하지 못하는 프로젝트에서는 병합 판 오류를 빼지 못해 main 몫이 신규로 남는다(«mypy 병합 판 기준선 실패»로 배너에 올라간다). 이 환경(P1·P2)에서는 재현됐다(1차 대체 경로 = 진입 기준선 · 리뷰 재확인).
- **(c) 다중집합 사각**: 같은 파일에서 레인이 위반 하나를 지우고 같은 키 하나를 새로 만들면(B 판과 내용이 다른 파일 안) 개수 차 0 이다 — 키 단위 비교의 본래 한계.
- **(d) Codex `apply_patch` 의 프로젝트 안 쓰기**: 행 파일을 프로젝트 안(`<산출물 폴더>/.coder-row-*`)으로 옮겨 권한 위험을 줄였지만, Codex 세션에서 `apply_patch` 로 새 점 파일을 만드는 것은 직접 보지 않았다.
- **(e) 도구의 pre-commit 해석은 가벼운 줄 파서다**: `entry`·`args`·`pass_filenames` 만 본다. 감지 못 하면 «mypy 대상 미정»이고 문면이 `--mypy-args` 로 다시 돌게 한다.
- **(f) 도구 시간**: 현장 진입 15~17초 · G2 15~39초 · 재제출 9~31초(두 레인 동시 · verify 와 겹친 부하). 병합 판 mypy 를 풀어 돌아야 할 때는 회당 70~100초가 더해진다(재제출은 파일 재사용).
- **(g) verify-web 문단 대조 표지(n2)**: `Makefile` 봉인 때문에 새 문단(W4 · ①′)은 verify-web 의 Claude·Codex 문단 대조에 아직 들지 않는다(블록은 픽스처가 대조).

## 6. 1차 현장 사본의 gitdir 공유(재현 리뷰 M2) — 정정

- 1차 기록 §3-2·§7 의 «원본 `problem-lanes/field-p{1,2}end` 는 건드리지 않고 `cp -c` 사본만 썼다»·«`.venv` 는 사본에만»은 **사실이 아니었다**. `cp -c` 가 `.git` 파일(→ `problem-lanes/field-clone/.git/worktrees/field-p{1,2}end`)을 그대로 복사해, 사본에서 한 checkout·merge 가 원본 worktree 의 HEAD·index·reflog 에 들어갔다. 원본 `field-p2end` HEAD 가 P2M 병합 `c582da6b6` 으로 남았고, 공유 저장소에 `w4-merged` 가지가 생겼다.
- 복구: 리뷰어(운영)가 `field-p2end` HEAD 를 `611e240eb` 로 되돌리고 `w4-merged` 를 지웠다. 이번 회차 끝에 읽기만 해서 확인했다: `field-p1end` `360cd1531` · `field-p2end` `611e240eb` · `field-clone` 가지 `main`·`syn-s0`·`syn-side`(`w4-merged` 없음).
- 이번 회차: 사본의 `.git` 파일을 지우고 `git clone --no-checkout --shared field-clone` 의 gitdir 로 바꾼 뒤 `update-ref --no-deref HEAD <끝 판>` + `reset --hard`(사본만) 로 맞췄다. 이후 모든 checkout·merge(P2M 병합 `1a8281c0f` 포함)는 사본 자기 gitdir 에만 쓰였다(공유는 objects alternates 읽기뿐).
- 1차 수치(ruff 48·225 · 서식 30·18 · mypy 0)는 리뷰어가 독립 사본에서 같게 재현했다. 그 수치는 그대로 유효하고, 이번 회차 수치는 §3-4 다.

## 7. 설계 밖 발견(고치지 않음)

- **NFD/NFC(운영 지시로 범위 밖 · 별도 일정)**: archive manifest `local_path` 가 원천 NFD 이름이고 git 체크아웃은 NFC 라 `check_design_evidence.py` inputs·`--design-build` 가 새 체크아웃에서 «archive inventory differs from frozen tree»(exit 2)로 막힌다(재현 리뷰 §6 — main 체크아웃 시안 빌드 17 가운데 13). 이번 재현은 사본 이름만 맞춰 돌렸다.
- **ruff 0.16 `format --check` 출력 형식 변경**: web 플러그인 안에서 `Would reformat:` 를 기대하는 곳은 없다(도구는 JSON 우선).

## 8. 산출물

- 패치(scratch `impl-web-t1/`): `01-Wn.patch`(`d430c620`) · `02-W8e.patch`(`86bb1792`). 1차 커밋 `72388e98`·`666dec0b` 는 이번 회차 커밋으로 바뀌었다(같은 묶음 경계).
- 이 기록 파일은 묶음 패치 밖이다(커밋하지 않음).
- 재현·검증 자료(scratch): `repro_w3.py`·`repro-w3.md` · `repro_w4_tool.py`·`repro-w4tool-{P1,P2,P2M}.json`·`.out`·`repro-w4tool-summary.txt` · `tool_d13_real.py`(실제 ruff F1~F6) · `mutate_inputs_log.py`·`mutation.log` · `mutate_static_delta.py`·`mutation-static-delta.log` · `paste_probe.sh` · `verify-web-{base,Wn-r2,W8e-r2}.log` · 1차 자료(`w4ref.py`·`repro_w4.py`·`repro-w4-*.json`·`synth_w4*.py` — 1차 사본은 gitdir 공유 상태에서 돌았다 · §6).
- 사본: `repro/p1`·`repro/p2` — 이번 회차부터 독립 gitdir(alternates 로 `field-clone` 객체만 읽음) · `.venv` 는 사본에만.
- Serena·Graphify 미사용(작업 지시).
