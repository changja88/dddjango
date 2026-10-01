# 수정 지시서 — W8 작은 판 구현 리뷰 반영 (2026-10-01)

독립 Claude 구현 리뷰 `./review-impl-claude.md` 판정은 «수정 후 승인»이다. 사용자 원칙 «새 결함은 배포 전에 고친다»에 따라 **M1 · M2 와 minor 4건을 모두** 고친다. 한국어로 쓴다. 리뷰 본문의 재현 명령·수치·권고를 먼저 읽는다.

## 고칠 것
- **M1 시트가 있는 토큰을 «신규 등록 필요»로 적음** — 근접 일치가 아니라 **표현 정규화**로 푼다: 브라우저 직렬화 정밀도(Chrome `color(srgb …)` 6자리 · `rgba` 알파)를 거꾸로 맞춰 같은 값인지 판정 · `color-mix(in srgb, X p%, transparent)` 등 흔한 꼴은 정확히 계산 · `#RRGGBBAA` · 서체 스택 토큰 · 해석 못 한 토큰이 걸릴 수 있는 행은 «신규 등록 필요» 대신 «수동 확인». `test_alpha_is_not_rounded_to_eight_bits` 는 관측 표기로 구별할 수 없다는 리뷰 지적대로 고친다. 리뷰가 든 P1 실례(`--shadow-2` · `--glass-tint-strong` · `--success-soft` · `--surface-muted` · `--font-sans`)가 정확 일치로 잡히는지 회귀 시험으로 고정한다.
- **M2 시트 크기·잡음** — 기본값 행 제외 · 후보 토큰을 속성 종류에 맞는 것으로 한정 · 구성원·부모·자식 목록은 개수 + 앞 몇 개 · 맨 앞 «값 → 토큰» 색인 · 크기 상한 시험. 목표: architect·coder 가 읽을 수 있는 크기(P1 시안 기준 수십 KB 수준 — 근거와 함께 상한을 정한다). 실행 시간(P1 46.6초)도 줄일 수 있으면 줄인다.
- **minor 4건** — ① 입력 오류 exit 1 때 이전 `style-report.json` 이 남아 새 결과와 구별 안 됨 → 실패 시 지우거나 실패 표지를 남긴다 ② 두 CLI 가 KeyError·TypeError 같은 도구 결함까지 «미실행» 한 줄로 삼킴 → 입력 문제와 도구 결함을 가르고 결함은 traceback 과 함께 다른 exit 로 ③ 시트가 G0 `tokens.css` 로 고정 — 토큰 등록 뒤 다시 만드는 지점을 문면(reference)에 한 줄로 ④ census 원자료·시트가 레인마다 수 MB 로 빌드 폴더 커밋에 들어감 → 기존 관례(예: 빌드 폴더 `private/` 등 커밋 제외 자리)가 있으면 따르고, 없으면 크기를 줄이는 쪽으로 — 판단 근거를 보고에 적는다.

## 규칙
- 이 가지(`design/w8-v5`)에 작은 커밋으로 올린다. 커밋마다 `make verify-web` green. 끝에 `make verify` 5/5(봉인 `manifest_seal.py --write` 는 하지 않는다 — 착지 때 운영자가 한다).
- byte 미러(scripts · assets · references) · 의미 미러(Coordinator · 역할 SKILL)를 함께 맞춘다.
- 범위를 넓히지 않는다(차단 · 입력 결속 · 재렌더 등은 여전히 밖).
- P1/P2 보관 6회차 판정 보존과 결정성(해시 시드 0~3 byte 동일)을 다시 확인한다.
- 보고 `./impl-w8-small-fix.md`: 발견별 처분(고침 위치 · 시험 · 수정 전 실패 → 수정 뒤 통과) · 시트 크기 전후(P1 · P2) · 검증 명령과 exit · 남은 일. 마지막 줄 `REPORT-DONE`.

## 금지
- push · main 변경 · 릴리즈 금지. 이 워크트리 밖에 쓰지 않는다($TMPDIR 사본 제외).
- `/Users/hyun/Desktop/dddjango` · `/Users/hyun/Desktop/spring_dream_server` · `~/.herdr/worktrees/spring_dream_server/**` · `~/.codex` · `~/.claude` 는 읽기만(쓰기 · `git status` 금지). scratch 자료는 읽기만.
- 서버 · DB · 네트워크 금지(로컬 헤드리스 브라우저 fixture 는 괜찮다). 다른 프로세스를 건드리지 않는다. Serena · Graphify 를 쓰지 않는다.
- 판단이 막히면 추측하지 말고 질문한다.
