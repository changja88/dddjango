# dddjango Codex 포트 평가 — 런 프로토콜 (고정 입력)

> 목적: Claude 1회 + Codex 2~3회가 **동일한 입력·동일한 의사결정**에서 출발해야 비교가 성립한다.
> 사람이 게이트에서 주는 답이 흔들리면 결정성·동등성 결론이 오염된다. 아래를 매 런 그대로 따른다.

## 0. 매 런 시작 전 — 리셋 (필수)

```bash
# Codex 런 타깃 (2차 = dddjango-codex)
bash workspace/eval/reset.sh /Users/hyun/Desktop/dddjango-codex
# Claude 런 타깃 (2차 = dddjango-claude)
bash workspace/eval/reset.sh /Users/hyun/Desktop/dddjango-claude
# → 각 타깃을 Product-only baseline 으로 초기화 (.venv 보존)
```
> 2차 검증용 깨끗한 프로젝트는 `dddjango-codex`/`dddjango-claude`(Python 3.9.6·Django 4.2.30, baseline+venv+git init). 구 `dddjango-smoke*`는 1차 잔재 — 사용 안 함.
`✓ 리셋 완료` 와 baseline 트리(catalog: __init__/admin/apps/migrations/0001/models/tests/views)가 보이면 OK.

## 1. 고정 기능 프롬프트 (토씨 동일)

> ⚠️ 정정(2026-05-28): 1차 실제 비교 런(codex-2·claude-1)은 **API 프롬프트(api 렌즈 ON)**로 돌렸다. 정본은 `RESULTS.md` 헤더. 2차(codex-3·claude-2)가 진짜 복제가 되려면 아래 API 프롬프트를 그대로 쓴다. (이전 비-API 문구는 폐기.)

```
재고가 부족하면 409로 거절하고, 충분하면 재고를 차감하며 주문을 생성하는 API.
```

## 2. 고정 게이트 답 (런마다 동일하게)

| 게이트 | 사람이 줄 답 | 이유 |
|---|---|---|
| **G0 배치** | **기존 `catalog` 안, 최소 변경** | 구조 비교를 위해 배치 결정을 고정. (4계층 강제 여부는 Q2에서 평가, 여기선 변수 제거.) |
| **G0 렌즈** | **ddd + db + api 활성** | 기능에 HTTP 계약(409·주문 생성 API) 있음. |
| **G0 스코프** | 제안 스코프 그대로(주문 1건·단일 상품·수량, 재고 충분 시만 생성·차감) | 스코프 확장 금지. |
| **API 프레임워크** | **plain Django** (Ninja 미사용) | 의존성 최소 스택으로 통제 일치(codex 무언 기본과 맞춤). |
| **테스트 러너** | **Django test** (pytest 미사용) | 〃 |
| **G1 설계** | **명백한 결함이 없으면 수정 없이 승인** | 설계 내용은 런마다 다를 수 있음(그게 결정성 관찰 대상). 사람이 손대면 변수 유입. 결함이 보여도 *반려 사유만* 적고 동일 기준으로. |
| **G2 구현** | 동일 기준으로 승인 | 〃 |

> 핵심 원칙: **같은 선택지가 있으면 같은 선택을 한다.** 런마다 architect가 다른 설계를 내놓는 것은 막지 않는다(그 변동이 Q1′ 결정성 데이터다). 사람은 *결정 축*만 고정한다.

## 3. 런 종료 후 — 산출물 캡처 (리셋 전에!)

```bash
# 2차: RUN=codex-3 → SRC=dddjango-codex / RUN=claude-2 → SRC=dddjango-claude
RUN=codex-3
SRC=/Users/hyun/Desktop/dddjango-codex
DEST="workspace/eval/runs/$RUN"
mkdir -p "$DEST"
rsync -a \
  --exclude='.venv' --exclude='.idea' --exclude='.git' \
  --exclude='db.sqlite3' --exclude='__pycache__' \
  "$SRC/" "$DEST/"
find "$DEST" -name '*.pyc' -delete
```
(rsync exclude가 zsh glob과 충돌하면 복사 후 `rm -rf "$DEST"/.venv "$DEST"/.idea` 로 정리.)

## 4. 런 종료 후 — 메타 기록 (수기)

각 런 디렉터리에 `meta.md` 를 만들어 런타임이 출력한 요약값을 적는다(파서 없음):

```markdown
# <RUN> meta
- 런타임/모델: Codex CLI 0.134.0 (GPT-5.5) | Claude Code (모델)
- 일시:
- 총 토큰(런타임 출력 요약):
- 소요 시간(체감/요약):
- spawn_agent 호출(Codex) 또는 서브에이전트 디스패치 정황:
- 게이트에서 사람이 벗어난 답을 준 적 있나(없어야 정상):
- 빌드 결과: migrate __ / check __ / test __ (개수)
- 비고(중간 막힘·재시도·우회 등):
```

## 5. 모든 런 완료 후

`RUBRIC.md` 기준으로 `workspace/eval/RESULTS.md` 작성:
- Q1 비교 행렬(claude-1 기준), Q1′ 결정성, Q2 체크, 토큰·시간 표, 결론.

## 런 목록·순서

**1차(완료, N=1씩)** — API 프롬프트:
1. `claude-1` — Claude 기준 런. (Claude Code, `/dddjango`)
2. `codex-2` — Codex 깨끗한 런 1. (Codex CLI, multi_agent=true)

**2차(결정성 검증, N=2 목표)** — 1차와 토씨 동일 입력으로 복제:
3. `codex-3` — Codex 복제 런. (`dddjango-smoke`)
4. `claude-2` — Claude 복제 런. (`dddjango-smoke-claude`)

> 매 런 사이 **반드시 reset.sh**(해당 타깃). `codex-1`(PoC, 구 프롬프트)은 보존됨 — 참고용, 비교에서 제외.
