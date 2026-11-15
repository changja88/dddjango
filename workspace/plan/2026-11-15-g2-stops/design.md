> 설계 정리본 — 구현 전 설계 v2(2026-11-15) 작업본에서 대상 저장소 이름 · 레인 · 대상 코드 이름 · 대상 커밋을 걷은 판. 구현 중 바뀐 것(구현 독립 검토 처분)은 `plan-2.39.0.md` · `plan.md` 가 정본이다. 본문의 `b2/` · `c2/` · `r2/` 같은 경로는 작업 폴더(배포 뒤 지움)다.

# dddjango 2.39.0 — G2 멈춤 여섯 · 글 어긋남 둘 · 도메인 우회 읽기 값 출처 · 설계 v2 (2026-11-15)

상태: 설계 v2 — v1(16:36) 위에 독립 검토 셋(review-b · review-cr · review-text · 차단 1 · 중요 14 · 사소 24) 처분 · 고침 일꾼 셋(b2 · c2 · r2) · F4-165 운영자 글 · 좁은 재확인(C 1회 · R 검사기 1회 · R 글 1회 · F4-165 4회 · B 1회)을 반영. 처분 기록 `op-rev/DISPOSITION.md`. 이 문서는 작업 폴더본이다 — 현장 이름 · 레인 · 현장 커밋이 들어 있다. 커밋할 정리본은 배포 뒤 `workspace/plan/2026-11-15-g2-stops/` 에 현장 이름을 걷어 둔다.

재료: 재현 보고 `<g-baseline|c-checkers|t-tools|r-rule180>/REPORT.md` · 검토 `<review-b|review-cr|review-text>/REVIEW.md` · 재확인 `review-*/RECHECK-*.md` · 고침 보고 `<b2|c2|r2>/REPORT.md` · 설계 v2 절 `drafts/{b2-v2,c2-v2,r2-v2,f165-v2}.md`(이 문서 §1 ~ §4) · 시제품 v2 `<b2|c2|r2>/proto/scripts/`(2.38.0 `rel/` 복사 위).

## 0. 결정

- **사용자**:
  - «나.»(11-15 14:56) — 2.39.0 = G2 멈춤 여섯(F4-160 · F4-162(+F4-56 ②) · F4-171 · F4-168 · F4-169 · F4-179 + 새 정본 ⓓ#607 물음 소음) + 덤 둘(F4-165 · F4-166) + F4-180.
  - F4-179 «나.»(11-15 01:41) — 2.38.0 에 넣지 않고 다음 작은 판(이번 판).
- **운영자 처리**(질문 생략 · 설계 처리 · 이의 시 뒤집음):
  - F4-180 방향 = ORM 모델이 도메인 값 목록에서 만든 이름(모델 클래스 안 `.value` 파생 `Final[str]` 값 속성)을 도메인 우회 읽기 · admin 이 쓴다(#356 목적 D29 ④ «도메인을 모른다» · 11-14 사용자 결정 «admin 은 ORM 값으로 비교 · 필터»).
    - (v2 · 17:02) 처방(쓰는 꼴)은 모델 클래스 속성 하나 · 금지 글의 예외는 «VO 멤버의 `.value` 를 글 · 수 주석(`Final[str]` · `Final[int]` · `str` · `int`)으로 묶은 값(모델 클래스 속성 · 모델 모듈 수준 이름)은 거쳐 가져오기가 아니다» — 검사기와 같은 말.
    - (v2 · 18:12) 클래스 몸 안 주석 없는 `.value` 는 막는다(houserules 첫 대입 어노테이션 의무 · 값 타입 모름 → «모르면 막음» · 사본 0).
  - F4-162 는 «레인이 그 폴더 안을 고친 줄» 까지 유입으로 넓히지 않는다(지금처럼 귀속 · 멈추는 쪽).
  - F4-169 선 = «DB 표 있는 모델은 출처 무관 막기»(Django 기본 User 는 그대로 막힘 · 규칙 문장 «모델 import 금지» 그대로). v2: 판정 셋(모델 / 모델 아님 / 모름) · «모름» 은 막음(review-cr 차단 처분).
  - F4-165 (v2 · 17:07 ~ 18:03):
    - 기준선 = 파견을 받아 편집하기 전의 커밋 · 맞춤 열쇠 = 파일 · 규칙 코드 · 진단 글(줄 · 칸 번호 · 글 안 `line N` 뺌) 개수 · 코드를 바꾼 coder 파견마다 그 끝에.
    - 이 Norm 은 적용 범위 Override 대상이 아니다(G12 N — 보존 몫 근거는 «포매터 서식은 dddjango 표준 밖»).
    - 묶음 창 · nit 치환의 기계 치환 lint 는 넘기지 않고 줄째 보고 → G2 감수(넷째 확인 뒤 줄이는 안 · 조정자 글 고치지 않음).
  - F4-161 보류(계기가 2.38.0 #668 · #188 로 사라짐 · 다시 나면 엶) · F4-172 이미 고쳐짐(2.34.0 · 장부 처분 줄 11-15 14:55).
- 판 번호 **2.39.0**(minor) — 새 규범(coder 완료 조건 · 모델 쪽 파생 값 · #356 첫 그래프 문장 · architect 파일 계획)과 검사기 판정 변경.

## 0-1. 단위 · 고칠 파일

| 단위 | 보고 | 고칠 자리 | 시제품 v2 | 크기 |
|---|---|---|---|---|
| B 기준선 · 귀속 | F4-160 · F4-162(+56 ②) · F4-166 | `anchor_diff.py`(①′ 칸 · 폴더 tree 판) · `registry_gate.py`(폴더 · 없는 폴더 주어 · ⓓ 짝 가드) | `b2/proto/scripts/` | M · M · S |
| C 검사기 오판 | F4-168 · F4-169 · F4-171 · F4-179 | `check-api-error-controller-contract.py`(one-hop 라우트 · 가리키는 라우트는 남김) · `check-business-vocabulary.py`(#53 판정 셋 · #396 · #415 · #607) · `business_vocab.py`(`tech_names` · 새 함수 셋) · `check-naming.py`(#36 후보) · `check-port-adapter-pairing.py`(죽은 인자) | `c2/proto/scripts/` | S · M · M · S |
| R 도메인 우회 읽기 값 출처 | F4-180 | `checker_target.py`(`reexport_bindings` · `reexport_uses` · `star_names` · `_derived_value` · `_value_annotation`) · `check-context-isolation.py`(#668) · `check-port-adapter-pairing.py`(#356) · 그래프 Norm 4 새 + 표현 5 고침 + 새 블록 1 · 배선 넷 · 산문 둘 | `r2/proto/scripts/` | L |
| T 글 | F4-165 | 그래프 coder Norm 1 · Codex coder 짝 · Makefile 문면 대조 한 줄 · G12 분류 | 없음(글만) | 작음 |

### 겹치는 파일 · 합치는 차례
- `check-port-adapter-pairing.py` — R v2 위에 C 덩이(죽은 인자 `tech` 걷음 · 시그니처 넷 + `tech = …` 한 줄)를 얹는다. review-cr 합침 시험(`review-cr/merged2/`)에서 충돌 0 · `_py_files(thin)` #356 고리와 겹치지 않음.
- `checker_target.py` — R 만(모든 검사기가 import → R 덩이를 먼저 넣고 전 검사기 시험).
- `check-business-vocabulary.py` · `business_vocab.py` — C 한 시제품(F4-169 · 171 · 179).
- `anchor_diff.py` · `registry_gate.py` — B 한 시제품(F4-160 · 162 · 166).
- 함께 고치는 시험 파일(구현 때 운영자가 모아 넣음): `field_report_checker_smoke.py`(C · R 클래스) · `fixture_matrix.py`(R 레인 둘 · `_M668` · 변이 옛 셋 다시 겨눔 + 새 · C 변이) · `anchor_diff_smoke.py`(B) · `registry_gate_smoke.py`(B) · `findings_count_matrix.py`(R 지문 둘) · `rulepack_smoke.py`(T G12) · `Makefile`(T 한 줄).
- 그래프 공용(차례로 채번 · 재생성): `ontology/ISSUED`(지금 끝 R-3759 · 새 Norm 다섯 = R 넷 + T 하나) · `target-counts.json` · `LEDGER.tsv` · `rulepack.json` + Codex · q4 골든 · `scope-limit-norms.md`(T N 행).

## 0-2. 그래프 · 글

- 새 Norm 다섯:
  - T 하나 — coder 완료 조건 정적 검사 기준선 대비(`agent-coder.ttl` s004/b10 · 배선 `agent-coder.ttl` delegatedTo command-dddjango).
  - R 넷 — R-새① 모델 쪽 파생 값 Obligation · R-새② domain 무의존 driven 자리의 글 사본 상수 금지 Prohibition(둘 다 `implementation-django` §2.5 새 블록 `s015-2.5/b6` · 배선 `implementation-django-final.ttl` delegatedTo reviewer) · R-새③ #356 Prohibition(houserules §5 b1 · alias `rule#356` · enforcedBy `check-port-adapter-pairing.py`) · R-새④ architect 파일 계획(`agent-design-architect.ttl` s005/b22 · 배선 `agent-design-review-ddd` · `command-dddjango`).
- 표현 고침:
  - R: `discipline-cleancode` §2.14 b13(R-1409) · b8(R-1399 «정의부 우변» 단서) · houserules §5 b1 admin 줄(R-3757) · discipline-reviewer s007/b13(R-0968 · R-0978).
  - B(review-b 사8 · 폴더 주어 F2′ 와 글 맞춤): `commands/dddjango.md` s007/b12(R-0306 «파일 무변·미증명» → «주어(파일 · 폴더) 무변·미증명») · s007/b58(R-3441 «파일 무변 귀속» → «주어(파일 · 폴더) 무변 귀속») · `discipline-houserules/SKILL.md` s004-1/b5(R-3131 같은 고침) · prefLabel 그대로(G12 안 닿음).
- 새 블록: `implementation-django` §2.5 `s015-2.5/b6`(order 5 · 지금 b5 → order 6).
- 산문(그래프 밖):
  - `docs/master/mkrev2.py` — C: #53 괄호(:811 · :454) · #415 괄호(:799) / R(선택): :374 · :385 → `file_tree.html`(mkrev2 를 돌리면 바뀌는 decision-record 는 되돌림).
  - 트리 명세 `workspace/design/2026-08-08-tree-revision-spec.md` — C #53(:381) · #415(:731) span · R #356(:669) · #668(:1197) 행 글 + span.
  - 소유 지도 `workspace/plan/2026-08-11-rule-owner-map.md` — R :308 · :581 비고.
- Codex 짝: 손 고침 = coder SKILL:39(T) · discipline-reviewer SKILL:86(R-0968 · R-0978) · design-architect SKILL:69(R-새④) · dddjango SKILL 두 자리 · dddjango-discipline-houserules SKILL 한 자리(B 표현 셋) / byte 복사(`corpus_mirror_sync --write`) = implementation-django · discipline-cleancode · discipline-houserules final.md. graph 절을 고쳤으면 `workspace/reference/<skill>/reference/final.md` 옛 절을 손으로 바꾼 뒤 `--write` → `--check`(DEVELOPMENT §3 체크리스트 5 · 11-13 교훈).

## 0-3. 검사 · 문서

- 체크리스트 8: Codex byte 미러(검사기 · 도구 아홉 안팎) → 골든 · EXPECTED(`findings_count_matrix` — R 지문 둘 · `checker_baseline_matrix` · `checker_cross_matrix --emit-expected` · `construct_drift_report --emit-expected` — #668 꼬리 글로 대표 레인 stdout 바뀜 · `gen_pregate_symbol_kinds`) → 봉인 → `make verify` + `make verify-mutation`.
- 2.38.0 교훈: 소성물(`pregate_symbol_kinds.json`)은 **마지막 검사기 고침 뒤에** 다시 만든다 · 맡은 사람이 없는 시험 파일(예: `pregate_fixture_run.py`)의 기대값도 바뀐 판정에 닿는지 grep 으로 본다.
- G12: 새 · 고친 이름표 모두 `rulepack_smoke` 로 대 봄 — T 이름표만 적중(«기존» · «새 파일» → DRIFT_REVIEWED + N 행) · R 넷 적중 0.
- 요청 가이드: 바뀔 것 없음(넷 모두 — 요청 칸 · 좋은 예 · 나쁜 예 · 묻는 일 그대로). README · master: 기준 판 줄. work_list: 배포 뒤 F4-160 · 162 · 56 · 165 · 166 · 168 · 169 · 171 · 179 · 180 처분 · 161 보류 표시.

## 0-4. 곁에 본 것(이번 판 밖)

- #2 값 중복 줄은 값마다 첫 주인 모듈 한 줄 → 이미 있는 중복 값에 셋째 주인을 더해도 신규 아님(2.38.0 받아들인 한계와 같음 · 별도 F4 후보).
- 운영자 환경 함정: TMPDIR 를 git 작업 트리 안에 두면 `--anchor` 기준선 재실행이 «git 저장소 TARGET 금지» 로 실패해 더 붉은 쪽(positional)으로 떨어진다 — 도구 기본 임시 폴더를 쓴다.
- 장난감 복사 함정: `cp -R` 한 git worktree 장난감은 `.git` 가리킴 파일이 원래 저장소를 가리켜 커밋 · index 가 원래 쪽에 들어간다 — 홀로 선 저장소로 다시 짓고 `GIT_OPTIONAL_LOCKS=0`(이번 일에서 두 번 닿음 · 운영자가 되돌림).
- F4-168 재측정 곁: 2.34 뒤 생긴 F4-130 «호출 앞 입력 검사» 줄이 레인 판 트리에 8 줄(다른 규칙 · 레인 판 뒤).

---

## 1. 기준선 · 귀속 장치(B)

### 기준선 · 귀속 장치 셋 — F4-160 · F4-162(+F4-56 ②) · F4-166 (설계 v2 · 고침 일꾼 b2 · 11-15 17:05 ~ 18:24)

v1(g-baseline · 14:58 ~ 16:31)에 독립 검토 review-b(차단 0 · 중요 1 · 사소 9)의 처분(`op-rev/DISPOSITION.md` review-b 표 · 11-15 17:03 · 모두 받음)을 반영한 온전한 절이다. 셋 모두 시제품으로 장난감 붉음 → 녹색 · 실데이터도 바라던 변화만 · 대조군 그대로.

폴더 `b2/` — 시제품 `proto/scripts/`(v1 시제품 복사 위에 고침 · diff `proto-anchor_diff.diff` · `proto-registry_gate.diff`(2.38.0 → v2) · `v1-v2-*.diff`(v1 → v2)) · 변이 사본 `mut/<이름>/scripts`(`make_mutants.py`) · 장난감(복사 · 자기 출력 폴더를 옆에 만듦) `f160_cases.py` · `b160_cases.py` · `b160v2_cases.py`(새) · `ladder_unit.py`(새 · `_run_lines` 대역 직접 시험) · `f162_cases.py` · `f162_dirty.py` · `f162_scope.py` · `b162_cases.py` · `b162v2_cases.py`(새) · `f166_cases.py` · `zren/`(검토자 git 장난감 복사) · 로그 `toys-*.log` · `ladder_unit.txt` · 시험 사본 `smoke/`(S · GATE 만 v2) · 로그 `smoke-{gate,anchor}-v2.log` · 실데이터 `real16x-{rel,v2}.out`(`run_real.sh`). 대상 사본은 `--shared` + sparse(그림 · 글꼴 · jsonl · svg · `.dddjango-web` json · 지침 파일 · `.claude` · `env` 뺌)로 `b2/real-{api,sse}` 에 복제해 쓰고 지움. `check-error-centralization.py` 는 2.38.0 그대로(검사기 무변).

#### 결정
- 사용자 «나.»(11-15 14:56) — 2.39.0 에 F4-160 · F4-162(+F4-56 ②) · F4-166.
- 운영자 처리(이의 시 뒤집음): F4-162 는 «레인이 그 폴더 안을 고친 줄» 을 유입으로 넓히지 않는다(귀속 · 멈추는 쪽).
- 검토 처분(운영자 · 17:03): review-b 중1 · 사2 ~ 사10 모두 받음 — 이 절에 반영(끝 «v1 → v2 바뀐 것»).

#### F4-160 — BC 오류 모듈을 비우거나 지우면 #2 앵커 기준선이 서지 못함
- 요점 (가) · (나) 둘 다 아닌 «(나)의 변형»: (가)는 2.22.0 보호 시험 Q19(지운 BC 의 앵커 줄이 레인이 새로 만든 같은 값 중복을 가리지 않게)를 깸(v1 실측) → «넣은 렌더 ∩ 비운 렌더».
- 고칠 설계 — `anchor_diff._baseline_lines` 사다리에 ①′ 칸: registry #2(`check-error-centralization.py` · `_ALIAS_CHECKERS`)만 · ① selector 렌더가 서지 않았을 때만(①이 서면 지금과 같은 실행 · 글자).
  1. 앵커 사본에서 «내용이 있는데 argv 의 `--project-code-error-module` · `--project-preserve-error-module` 에 없는» `application/<bc>/driving_layer/api/bc_error_schema.py` 를 찾음(`_anchor_only_error_modules`) — **BC 이름이 검사기의 정본 후보 꼴(`check-error-centralization` `BC_NAME_RE` · `_candidate_bc` 와 같은 식 `_CANDIDATE_BC_RE`)인 것만**(사3 · 규격 밖 이름 `catalog_` 를 넣으면 넣은 렌더가 noncanonical 분석 오류로 무너져 ①′ 전체가 positional 로 떨어짐).
  2. (a) 그 모듈을 `--project-code-error-module` 로 더한 렌더를 먼저 돌림. **(a) 가 exit 0 · 2 가 아니면 ①′ 은 서지 못하고 (b) 를 돌지 않음**(중1 — v1 은 (a) 실패에도 (b) 를 끝까지 돎).
  3. (b) 사본에서 그 모듈을 0 바이트로 비운 렌더 — `finally` 로 원래 바이트로 되돌림(①′ 이 못 서면 ② · positional 이 같은 사본을 잼).
  4. 둘 다 exit 0 · 2 면 두 렌더 모두에 있는 줄만 기준선 · 표기 `기준선=selector 렌더 재실행(앵커에만 있는 오류 모듈 <bc…>: 넣은 렌더 ∩ 비운 렌더)`.
  5. 하나라도 안 서면 지금 사다리(② 빈 골격 걷기 → ③ positional).
  - 교집합 까닭: (a)만이면 지운 모듈이 앵커에 만든 값 중복 줄(값마다 첫 주인 한 줄)이 레인이 새로 만든 같은 글자 줄을 가림(S2) · (b)만이면 «모듈을 지워서 다른 파일에 생긴 줄» 이 기존분(T1) · 두 쪽 모두 = 그 모듈과 무관한 앵커 줄.
  - 승인 유입 측정(M^1 · M^2 기준선)도 같은 사다리 → main 이 비운 꼴도 풀림. **단 main 이 그 머지로 다른 #2 줄을 함께 들이지 않을 때**(사4 — T2: main 이 catalog 를 비우며 lesson 에 새 위반을 넣으면 그 새 줄은 `측정 무효(M^1)` 로 귀속 · ①′ 이 끼지 않는 T2c 도 같음 = 2.38.0 의 따로 있는 한계).
  - 규칙 글 무변(렌더 계약 «빈 골격은 inventory 제외» commands/dddjango.md:181 · `기준선 오류:` 처방 R-3441 그대로).
- 실행 시간(사10): ①′ 은 «① 이 서지 않고 앵커에만 있는 정본 후보 오류 모듈이 있는» 사본에서만 탄다. 그 사본 하나에 ①′ 이 서면 positional 1 회 대신 렌더 2 회(v1 단독 실측 real160 앵커 한 사본 64 → 84 s) · (a) 가 못 서면 렌더 1 회 더(v1 은 2 회) · (b) 가 못 서면 2 회 더. 사다리를 타는 사본 = 앵커 1 + 승인 머지마다 ^1 · ^2 + 사슬 트리(최대 64) → 최악 (1 + 2m + 64) × 2 렌더 × 렌더 한 번(사본 실측 약 20 s · m = 승인 머지 수). 실제로는 비운 뒤 커밋(main 착륙분 · 레인 커밋)부터는 ① 이 서므로 비우기 앞 사본만 타고, ①′ 이 서서 신규 줄이 줄면 유입 측정 자체가 줄어듦.
- 시제품 `anchor_diff.py` 2.38.0 → v2 +141 −14(F4-160 · F4-162 함께 · v1 +113 −12 · v1 → v2 +44 −18 — `diff -u` 의 `+` · `-` 줄 셈). F4-160 몫: 머리 글 · 사다리 docstring · `_INVENTORY_FLAGS` · `_CANDIDATE_BC_RE` · `_anchor_only_error_modules` · ①′ 칸((a) 문 · 복원 주석) · `_ALIAS_CHECKERS` 주석. v1 → v2: 머리 글 4 줄 · 이름 거름 4 줄 · (a) 문 + 복원 주석 12 줄.
- 장난감(2.38.0 `rel/` · v1 `g-baseline/proto` · v2 `b2/proto` · `python3 -B <장난감> <scripts> <폴더>` · `toys-f160.log` · `toys-b160.log` · `toys-b160v2.log`):
  | 사례 | 2.38.0 | v1 | v2 |
  |---|---|---|---|
  | P 레인이 catalog 모듈 0 바이트 | exit 2 · 신규 1 · positional | exit 0 · 기존분 1 · ①′ | exit 0 · 기존분 1 · ①′ |
  | Q 레인이 catalog BC 통째 지움 | exit 2 · 신규 1 | exit 0 · 기존분 1 | exit 0 · 기존분 1 |
  | U main 이 비움 · 승인 머지로 들임 | exit 2 · 신규 1 | exit 0 · 기존분 1 | exit 0 · 기존분 1 |
  | R [대조] P + lesson 에 새 위반 | exit 2 · 신규 3 | exit 2 · 신규 2(레인 줄만) · 기존분 1 | 같음 |
  | S [대조] 앵커 중복 값 catalog 비움 + 같은 값 새 BC | exit 2 · 신규 2 | exit 2 · 신규 1(새 중복) | 같음 |
  | S2 [가림 시험] S 인데 지운 BC 가 뒤 이름 | exit 2 · 신규 2 | exit 2 · 신규 1 | 같음 |
  | S3 [옛 한계] 지우지 않고 같은 값 셋째 주인 | exit 0 | exit 0 | exit 0 |
  | T1 [한계 · 사2] 앵커 같은 값 주인 셋(lesson · catalog · music) · 레인 catalog 비움 | exit 2 · 신규 2 | exit 2 · 신규 1 · 기존분 1 | 같음 |
  | T2 [사4] main 이 catalog 비우며 lesson 에 새 위반 · 승인 머지 | exit 2 · 신규 3 | exit 2 · 신규 2(`측정 무효(M^1)`) | 같음 |
  | T2c [사4 대조] T2 인데 main 이 비우지 않음(① 섬) | exit 2 · 신규 2(`측정 무효(M^1)`) | 같음 | 같음 |
  | T3 [사3] 앵커에 규격 밖 이름 `catalog_` 오류 모듈 + 레인 catalog 비움 | exit 2 · 신규 1 · positional | exit 2 · 신규 1 · positional(①′ 무너짐) | **exit 0 · 기존분 3 · ①′** |
  | T4 같은 BC 범위 + 컨트롤러가 그 모듈 import 하던 앵커 | exit 2 · 신규 1 | exit 0 | exit 0 |
  | T6 앵커 lesson 이 catalog 를 import(① DYNAMIC) · 레인이 비우고 import 걷음 | exit 2 · 신규 1 | exit 0 | exit 0 |
  | T7 앵커 catalog 가 동적 Enum · 레인 비움 | exit 2 · 신규 1 | exit 0 | exit 0 |
  | T8 앵커 lesson 컨트롤러가 catalog 오류를 raise · 레인이 비우고 고침 | exit 2 · 신규 1 | exit 0 | exit 0 |
  | T9 F4-40 꼴 새 BC relay + 레인 catalog 비움 | exit 2 · 신규 1 | exit 0 | exit 0 |
  - T6 ~ T9 는 «①′ 이 서지 못하는 길» 을 e2e 로 지으려던 꼴인데 넷 모두 섬 — 기준선 모드에서 비운 모듈을 import 하는 쪽은 분석 오류가 아니라 `- DYNAMIC_…` 줄(exit 2)로 나와 (b) 가 무너지지 않는다(`trace_runs.py` 로 렌더마다 exit 확인). 그래서 «(a) 무너짐 · (b) 무너짐» 길과 복원은 아래 직접 시험으로 잰다.
- 사다리 직접 시험 `ladder_unit.py`(손으로 지은 스냅숏 + `_run_lines` 대역 · 부른 차례 · argv · 그때 모듈 바이트를 적음 · `ladder_unit.txt`):
  | 시험 | v2 | v1 | 변이 |
  |---|---|---|---|
  | (a) exit 1 → (b) 안 돎 · 사본 그대로 · positional | OK | FAIL((b) 돎) | `nogate` FAIL · `noprime` FAIL |
  | (a) 0 · (b) 1 → positional 때 모듈이 원래 바이트 | OK | OK | `norestore` FAIL · `noprime` FAIL |
  | 정본 후보 이름만 (a) 에 듦(`catalog` 듦 · `catalog_` 안 듦) | OK | FAIL | `nofilter` FAIL · `noprime` FAIL |
  | #2 밖 검사기(`check-openapi-error-declaration`)는 ①′ 을 안 탐(차례 ① → positional) | OK | OK | `noguard` FAIL |
  - 가드 변이(`noguard`)는 e2e 로 안 보임 — 다른 넷 검사기는 `--project-code-error-module` 를 모르는 인자로 exit 1(`_UsageParser`) 하므로 (a) 가 못 서고 v2 에선 (b) 도 안 돎 → 출력 같음 · 렌더 1 회만 더. 그래서 대역 시험으로만 죽는다.
- 실데이터 — 오류 모듈을 지운 레인 인자(`f160-real-args.txt`) · 앵커 <앵커> · HEAD <레인 HEAD> 사본: 2.38.0 exit 2 · 신규 3(<BC-가> :1 · <BC-나> :81 ×2) · positional → v2 **exit 0 · 신규 0 · 기존분 3** · `기준선=selector 렌더 재실행(앵커에만 있는 오류 모듈 <BC-다>: 넣은 렌더 ∩ 비운 렌더)` · 검사기 본 출력 같음. 정상 꼴(그 모듈이 이미 빈 앵커 <다른 앵커> · real160n): 2.38.0 · v2 byte 같음(exit 0 · 기존분 3). 2.38.0 출력은 v1 재측정과 byte 같고 v2 출력은 v1 시제품 출력과 byte 같음(사본 복제 방식이 달라도 같은 결과 — `exit=` 꼬리 줄만 다름). 시간: 이번은 장난감 · 시험 스위트와 함께 돌아 견주지 않음(2.38.0 119 s · v2 135 s) — v1 단독 실측 64 → 84 s.
- 시험(구현 때 `anchor_diff_smoke.py`):
  - `BaselineLadderHoldsRegression` 에 넣음 — e2e P · Q · U · R · S · S2 · T3(사3) · T1(`test_한계_…` · 남는 붉음 1 줄 고정) + 직접 시험 넷(`ladder_unit.py` 꼴 — `patch.object(ad, "_run_lines", side_effect=…)` 은 이 파일에 이미 있는 꼴(:600 · :795)).
  - 변이(걷으면 붉어지는 것): ①′ 칸 걷음 → P · Q · U · 직접 시험 셋 · 넣은 렌더만(교집합 걷음) → S2 · Q19 · 비운 렌더만 → T1 · 이름 거름 걷음 → T3 · 직접 «정본 후보만» · (a) 문 걷음 → 직접 «(a) 1 → (b) 안 돎» · 복원 걷음 → 직접 «positional 때 원래 바이트» · `_ALIAS_CHECKERS` 가드 걷음 → 직접 «#2 밖 검사기». 모두 `b2/mut/*` 로 실제 죽음 확인(`toys-*.log` · `ladder_unit.txt`).
  - 고칠 기존 시험(시험 사본 `b2/smoke/anchor_diff_smoke.py`(S 만 v2)로 126 중 11 붉음 — v1 과 같은 11 · 모두 아래 글자 · 사유 단언 몫 · exit 판정이 바뀐 것 0 · `smoke-anchor-v2.log`):
    - `test_Q19_removed_preserve_inventory_not_supplemented` ×2(dup · import) — exit 2 그대로 · `"기준선 오류:"` 단언 → `"앵커에만 있는 오류 모듈 zulu: 넣은 렌더 ∩ 비운 렌더"` in out · `기준선 오류:` 없음 · 신규분에 `application/accounts/driving_layer/api/bc_error_schema.py:N: duplicate project code wire value: wire_x`(dup 신규 1 · import 신규 2 — 둘째 줄은 `extra.py` `concrete FrameworkErrorSchema outside canonical module`) · 그 줄 사유 `측정 무효(M^2)`(v2 시험 사본 `capture2.log` 실측). 이름이 동작과 어긋남(사5 — (a) 가 지운 zulu 를 넣어 보충하고 교집합이 그 모듈의 줄을 뺌) → `test_Q19_removed_inventory_supplemented_intersection_keeps_lane_duplicate_new` · docstring «상류가 지운 zulu 오류 모듈을 앵커 사본의 넣은 렌더가 보충하지만 비운 렌더와의 교집합이 zulu 가 만든 값 중복 줄을 빼 레인이 orders 에 만든 같은 값 중복은 신규로 남는다».
    - `RenamedBcBaselineRegression` 8 건(사5 · v1 셈 — A 는 a1 에서 멈춰 셈에 하나 · a1 을 고치면 a2 도 같은 꼴이라 고칠 자리는 아홉) — 모두 exit · 신규 · 기존 · 유입 집합 같고(`renamed-diff.log` · `capture2.log` 줄 차분) 바뀌는 자리는 #2 렌더의 기준선 글 두 자리뿐: ⓐ 머리 줄 `기준선=positional 기준선(selector 렌더 불능 강등 — selector-lane 진단은 전량 신규 취급)` → `기준선=selector 렌더 재실행(앵커에만 있는 오류 모듈 <BC>: 넣은 렌더 ∩ 비운 렌더)` 과 그 밑 `  기준선 오류: … canonical candidate가 project inventory union에 없음: …` 한 줄 빠짐 ⓑ 머지 표 `    ↳ ^k 기준선: positional 기준선(…) — 오류: …` → `    ↳ ^k 기준선: selector 렌더 재실행(앵커에만 있는 오류 모듈 <BC>: 넣은 렌더 ∩ 비운 렌더)`. 옛 판(2.22.2) 출력에 이 대응만 걸어 `assertEqual(new, mapped_old)` — 대응은 사례마다 적어 둔다(정규화로 지우지 않는다 · ①↔③ 칸 바뀜을 보게):
      | 시험 · 사례(CENT 만) | ⓐ BC | ⓑ |
      |---|---|---|
      | A a1 `steered` | lucky_charm | 없음 |
      | A a2 `crossed` | decisive_fortune | ^1 |
      | G1 `tie` | decisive_fortune, lucky_charm | ^1 |
      | G1 `delete-add` | decisive_fortune | ^1 |
      | G1 `lane-rename` | decisive_fortune | ^2 |
      | G1 `anchor-only` | decisive_fortune | 없음 |
      | G1 `tiny-mirror` | lucky_charm | 없음 |
      | G1 `own-side-merge` | decisive_fortune | 없음 |
      | G2 `moves-dup` | decisive_fortune | ^2 |
      그 밖(G1 `recreate` · G1 의 CTX 여섯 · R1 ~ R9 · B · 한계)은 바이트 그대로(v2 녹색). G1 docstring «짝이 서지 않거나 상황 밖이면 2.22.2 와 글자 같음» 에 «— #2 는 앵커에만 있는 오류 모듈이 있으면 기준선 글 두 자리만 ①′ 로(F4-160)» 를 붙임. (a2 는 단언을 멈추지 않는 사본 `smoke/capture2.py` 로 잼.)
    - `test_Q18_Q9_folder_cycle` — F4-162 몫(아래).
    - `BcSelectorPartitionRegression.assert_partition`(:507 · CENT) `assertIn("기준선=selector 렌더 재실행", out)` → `assertIn("기준선=selector 렌더 재실행):", out)`(사6 — 지금 꼴은 ①′ 표기도 통과). 같은 맨 글자 단언 :534 · :3506 · :3524 · :3542 · `field_report_checker_smoke.py` :2872 · :2882 · :2894 는 #2 가 아니라(CONTRACT · OPENAPI · #15) ①′ 을 타지 않음 — 그대로.
  - 체크리스트 8: Codex 미러 `codex-dddjango/skills/dddjango/scripts/anchor_diff.py` · 봉인 · 골든 무관(`_normalize` · `_FINDING_RE` 만) · `field_report_checker_smoke.py` 의 `--anchor` 사례는 위 셋이 #15 라 무관.
- 남는 한계:
  - 값 중복 줄은 값마다 첫 주인 한 줄 → 이미 있는 중복 값에 셋째 주인은 2.38.0 에서도 신규 아님(S3 · 이 고침과 무관 · 별도 F4 후보).
  - T1(사2): 앵커에 같은 값 주인이 셋 이상이고 레인이 첫 주인 모듈을 비우면 남은 둘의 옛 중복이 대표 주어만 옮겨(catalog:1 → lesson:1) 교집합에서 빠져 신규 1 줄로 남음 — fail-closed · 2.38.0(신규 2)보다 덜 붉음 · S2(레인이 만든 중복)와 줄 글자가 같아 못 가름.
  - 사4: U 꼴 풀림은 main 이 그 머지로 다른 #2 줄을 함께 들이지 않을 때만(T2 — 함께 들인 줄은 `측정 무효(M^1)` 로 귀속 · 2.38.0 한계 · T2c).
  - 사3(읽기): 앵커에서 preserve 였던 모듈도 (a) 에 code 로 듦 — code 판정이 더 엄격해 (a) 줄이 늘 뿐 교집합이라 기준선은 좁아지는 쪽(fail-closed) · (a) 가 분석 오류로 못 서면 ①′ 은 서지 못함(지금 사다리).
  - ①′ 와 ② 가 동시에 필요하면 ③(지금과 같음).
  - «(b) 만 무너짐» 길은 장난감으로 못 지음(T6 ~ T9) — 복원은 직접 시험으로만 지킴.
- 버린 갈래: (가) 검사기가 `--anchor-baseline` 에서 union 에 스스로 넣음(Q19 · S2 가림) · 빈 골격도 inventory 에(지금 쪽 #572 새 줄) · 비운 렌더만(T1 꼴 가림 · 위 까닭) · BC 이름 식을 공용 모듈로 뺌(검사기 셋이 제 식을 따로 가짐 — 이번 판에 공용화하지 않음 · 주석으로 출처 표기).
- 맡을 파일: `anchor_diff.py` · Codex 미러 · `anchor_diff_smoke.py`(F4-162 와 겹침). 크기 M · 사용자 결정 아님.

#### F4-162 (+F4-56 ②) — 승인 머지로 들어온 폴더 주어 · 없는 폴더 주어의 유입 증명
- 운영자 처리: «레인이 그 폴더 안을 고친 줄» 은 넓히지 않음(귀속).
- 고칠 설계: `anchor_diff.PathFacts.classify` 가 주어가 HEAD blob 이 아니면 폴더(tree)로 잼(`_classify_dir` · `git ls-tree -r -t` 커밋마다 한 번 캐시 `tree_dirs`) — F1′ = tree(M^1:p) ≠ tree(M:p) = tree(M^2:p) = tree(HEAD:p) → «파일»(주어 verbatim) · F2′ = tree(HEAD:p) = tree(anchor:p) → «상호작용» · 폴더 아래 작업 트리 변경 → `worktree 수정 중` · 그 밖은 파일 판과 같은 last-toucher 사유를 tree 로(`retained_reason(p, entries)`) · 레인이 폴더 안을 고친 줄은 귀속 그대로 · L · P 그대로(이중 원인 걸러짐). registry_gate 부재 주어 G 를 «.py 이거나 점 없는 이름(없는 폴더)» 으로(`absent_file` → `absent_path` · `#488 고정 칸 \`x/\` 부재` 등 = F4-56 ②). 표기 `폴더 verbatim` · `부재(상류에도 없던 폴더)`(`_ProvenanceResult.folders` · `_InflowSplit.folders`) · 머지 표 `파일 n · 상호작용 m[ · 부재 k]` 꼴은 그대로(규칙 글 인용 꼴 · 폴더 줄은 같은 칸). scope 렌더 «^1 에 주어 파일 없음» 지름길은 blob 주어에만.
  - **작업 트리 확인(사7)**: `PathFacts.dirty` 가 `git status --porcelain -z` 의 이름 바꿈 · 복사 항목 `XY 새\0옛\0` 에서 옛 경로를 다음 항목으로 온전히 읽음(`_porcelain_paths` — v1 · 2.38.0 은 옛 경로를 `entry[3:]` 로 깎아 `area/sub/x.py` → `a/sub/x.py`). 파일 판에도 같이 닿음(스테이지한 이름 바꿈의 옛 경로가 주어면 `worktree 수정 중` — 더 닫히는 쪽). docstring 은 «폴더면 그 아래 어느 것이든» → «`git status` 가 적는 경로(미추적 · 수정 · 삭제 · 이름 바꿈 두 쪽) · 빈 폴더 · 무시 파일은 안 보임 — 그 차이로 줄이 달라지면 L ∧ P 가 귀속 유지 · 줄이 같으면 손대지 않은 폴더처럼 판정».
  - 레인이 폴더 안을 커밋으로 고쳤다가 되돌린 꼴(사9 · 검토 G1)은 tree 가 같아져 F1′ 로 유입(`폴더 verbatim`) — 파일 판(blob 이 같아지면 유입)과 같은 뜻.
- 규칙 글(사8 · graph-owned · ttl 은 구현 때 · 표현 고침 = revision-clarification · 새 Norm 없음 · 명칭(prefLabel) 무변이라 G12 무관):
  | 문서 | 블록(절 키) | Norm | 옛 → 새 |
  |---|---|---|---|
  | `dddjango/commands/dddjango.md:173` | `s007/b12`(6. 결정적 백스톱) | R-0306(지금 표현 @2026-10-13) | «**상호작용 위반(파일 무변·미증명)은 귀속 유지·별도 표기(`↳ 귀속 유지: 상호작용 미증명`)**» → «**상호작용 위반(주어(파일 · 폴더) 무변·미증명)은 귀속 유지·별도 표기(`↳ 귀속 유지: 상호작용 미증명`)**» |
  | `dddjango/commands/dddjango.md:233` | `s007/b58`(승인 머지 목록 · provenance 차분) | R-3441(@2026-10-13) | «파일 무변 귀속(게이트 표기 `↳ 귀속 유지: 상호작용 미증명`)은 철회할 변경이 없다» → «주어(파일 · 폴더) 무변 귀속(게이트 표기 `↳ 귀속 유지: 상호작용 미증명`)은 철회할 변경이 없다» |
  | `dddjango/skills/discipline-houserules/SKILL.md:33` | `s004-1/b5`(백스톱 실행 계약) | R-3131(@2026-09-03) | «**상호작용 위반(파일 무변·미증명)은 귀속 유지·별도 표기**» → «**상호작용 위반(주어(파일 · 폴더) 무변·미증명)은 귀속 유지·별도 표기**» |
  - Codex 짝(같은 뜻 · 손으로): `codex-dddjango/skills/dddjango/SKILL.md:192` · `:252` · `codex-dddjango/skills/dddjango-discipline-houserules/SKILL.md:29`.
  - 그래프 차례: ttl 블록 글 셋 + Expression 셋(R-0306 rev 4 · R-3441 rev 3 · R-3131 rev 3) → `ontology_render.py --apply` → `make rulepack` → Codex 짝 · q4 골든 · 봉인(R 단위 그래프 고침과 같은 차례로 묶음).
- 시제품 `anchor_diff.py`(F4-162 몫 — `tree_dirs` · `PathFacts` 폴더 판 · `_porcelain_paths`) · `registry_gate.py` 2.38.0 → v2 +27 −12(F4-162 · F4-166 함께 · v1 +26 −12 · v1 → v2 +2 −1 = 주석 둘 — `absent_path` docstring «점 없는 이름은 없는 파일일 수도 있다 — 판정은 같고 유입 표기만 «폴더»» · 표기 줄 위 «상류에도 없던 = 승인 머지의 상류 쪽(^2)에도 없던 — 앵커에 있었는지는 묻지 않는다»). v1 → v2 `anchor_diff.py`: `_porcelain_paths` 17 줄 · `dirty` 2 줄 · docstring 4 줄.
- 장난감(`toys-f162.log` · `toys-b162.log` · `toys-b162v2.log`):
  | 사례 | 2.38.0 | v1 | v2 |
  |---|---|---|---|
  | A main 이 입구 없는 영역 refund/ 더함(#188 폴더) | exit 2 · `비-blob 경로` | exit 0 · `폴더 verbatim` | 같음 |
  | B main 이 api/refund 지움(영역 폴더 무변) | exit 2 | exit 0 · `상호작용` | 같음 |
  | C main 이 골격 덜 된 BC 더함(#488 고정 칸 부재 8) | exit 2 · 8 `비-blob 경로` | exit 0 · `부재(상류에도 없던 폴더)` 8 | 같음 |
  | D [대조] A 뒤 레인이 영역 안 파일 커밋 | exit 2 | exit 2 · `레인 커밋 수정 …` | 같음 |
  | E [대조] 레인이 스스로 api/refund 지움 | exit 2 | exit 2 · `상호작용 미증명`(L) | 같음 |
  | F [대조] A 뒤 영역에 커밋 안 한 파일 | exit 2 | exit 2 · `worktree 수정 중` | 같음 |
  | Y scope #6 main 역방향 ACL · 머지가 받음(#450 둘) | exit 2 | exit 0 · `상호작용` · `폴더 verbatim` | 같음 |
  | Q18 꼴 머지가 역방향 ACL 떨굼 · 빈 폴더만 | exit 2 | exit 2 · `유입 증명 실패(… 결과에 없음)` | 같음 |
  | G1 레인이 영역 안을 고쳤다 되돌림(사9) | exit 2 | exit 0 · `폴더 verbatim` | 같음 |
  | G3 쌓인 머지 사이 레인 수정 | exit 2 | exit 2 · `충돌 해소분(M≠M^2)` | 같음 |
  | G4 쌓인 머지 · 레인 손 안 댐 | exit 2 | exit 0 · `폴더 verbatim` | 같음 |
  | G5 main 이 영역 이름만 바꿈 | exit 2 | exit 0 · `폴더 verbatim` | 같음 |
  | G6 [대조] 레인이 영역 이름 바꿈 | exit 2 | exit 2 · `비머지 커밋 경유` | 같음 |
  | G7 main 이 앵커에 있던 `billing/test/` 지움(사8 ①) | exit 2 | exit 0 · `부재(상류에도 없던 폴더)` | 같음 |
  | **R7** [사7] A 뒤 레인이 영역 안 파일을 `git mv` 로 index 에서만 영역 밖으로 | exit 2 · `비-blob 경로` | **exit 0 · `폴더 verbatim`(구멍)** | **exit 2 · `worktree 수정 중`** |
  | N1 [사9 대조] 점 없는 부재 경로 · 부모가 HEAD 폴더 아님(합성 줄) | `비-blob 경로` | `비-blob 경로` | 같음 |
  | N2 [사9 대조] 점 없는 파일이 HEAD 에 있음(합성 줄) | 파일 판 `상호작용 미증명` | 파일 판 · `is_dir` 거짓 | 같음 |
  | N3 [사8 ② 한계] 점 없는 파일 이름이 HEAD 에 없음 · 부모는 HEAD 폴더(합성 줄) | `비-blob 경로` | G′ 후보 `부재 미증명`(증명되면 표기 «폴더») | 같음 |
  - 변이 `noren`(rename 짝 파싱 되돌림): R7 exit 0 `폴더 verbatim` — 죽음. 검토자 `zren/`(`git mv area/sub/x.py moved_x.py`): v1 dirty `{a/sub/x.py, moved_x.py}` → v2 `{area/sub/x.py, moved_x.py}`.
- 실데이터(승인 머지 폴더 레인 승인 머지 <승인 머지> 를 HEAD 로 · 앵커 <앵커> · 승인 목록 한 줄): 2.38.0 폴더 줄 7(#188 5 · #450 2 · 모두 `비-blob 경로`) → v2 6 유입(`폴더 verbatim` 4 · `상호작용` 2) · 남는 1 = `#450` 한 BC(`충돌 해소분(M≠M^2)` · 레인이 그 BC 안 파일 고침 → 운영자 처리대로 귀속) · 귀속 41 → 35 · 승인 유입 42 → 48(머지 표 `파일 42 · 상호작용 0` → `파일 46 · 상호작용 2`) · ⓓ 신규 348 → 343(legacy +5 · 해소 −5 · «목록만 줄어 legacy» 2 → 7 = F4-166 몫 ⓓ#547 다섯 줄) · 검사기 재실행 9 → 12(폴더 줄 L 증명) — 그 밖 귀속 사유 글자 같음. 2.38.0 출력은 v1 재측정과 byte 같고 v2 출력은 v1 시제품 출력과 툴체인 줄만 다름(사7 rename 파싱 고침은 이 사본(작업 트리 깨끗)에 닿지 않음).
- F4-56 은 닫힘: ② «폴더 · 없는 파일» = 없는 파일(2.22.0 G) · 있는 폴더(F1′ · F2′) · 없는 폴더(G′) · ① 은 2.19.2 에서 · ③ 할 일 없음 · 남는 것은 «레인이 고친 폴더»(처리대로). work_list F4-56 지울 수 있음.
- 시험:
  - `registry_gate_smoke.py` `ApprovedInflowGateRegression` 에 A ~ F · R7(사7) · `test_G1_subject_guards…` 의 주어 가드 꼴(합성 줄 · `_provenance_split` 직접)에 N1 «점 없는 부재 경로 · 부모가 HEAD 폴더 아님 → `비-blob 경로`» · N2 «점 없는 파일이 HEAD 에 있음 → 파일 판(`is_dir` 거짓 · 폴더 표기 아님)»(사9) · G1 «고쳤다 되돌림 → 유입 `폴더 verbatim`» 사례(사9 — 글 한 줄 + 사례).
  - `anchor_diff_smoke.py` `test_Q18_Q9_folder_cycle` 사유 단언 `비-blob 경로` → `유입 증명 실패(… 결과에 없음)`(exit 2 그대로 · v2 실측 #450 두 줄 모두 `유입 증명 실패(승인 머지 … 결과에 없음)` — 작업 트리의 빈 폴더는 git status 에 안 나오고 줄이 결과에 없어 P 가 막음) · Y 새로(scope #6 역방향 ACL).
  - 변이: `_classify_dir` 를 `"비-blob 경로"` 로 → A · B · Y · G′ `.py` 조건 되돌림 → C · 폴더 dirty 확인 걷음 → F · rename 짝 파싱 되돌림(`noren`) → R7(v2 `worktree 수정 중` exit 2 · 변이 `폴더 verbatim` exit 0) · registry_gate_smoke `_MUTATIONS` 11 지점 그대로 맞음(registry_gate 고침은 주석 · docstring 뿐). Codex 미러 둘 · 봉인 · 골든 무관.
- 남는 한계:
  - BC 폴더 주어(#450)는 레인이 그 BC 안 아무 파일을 고쳐도 귀속(폴더 단위가 큼).
  - 머지 표 «파일 n» 칸에 폴더 verbatim 이 함께 듦 · scope 렌더에 부재 주어 G 없음(지금과 같음).
  - 사8 표기 셋: ① «부재(상류에도 없던 …)» 는 «승인 머지의 상류 쪽(^2)에도 없던» 뜻 — main 이 앵커에 있던 칸을 지운 꼴(G7 `billing/test/`)도 같은 글자(2.22.0 파일 판과 같음 · 글자 그대로 두고 코드 주석으로 뜻 적음) ② 점 없는 «파일» 이름의 부재 주어도 G′ 로 들어 표기가 «폴더»(N3 — 판정은 같음) ③ 폴더 주어의 «이중 원인» 사유에 `미승인 머지 … 경유 가능` 힌트가 붙지 않음(`earlier_unapproved` 가 blob 만 비교 · 사유 글자만 덜 자세함 · exit 같음).
  - 빈 폴더 · 무시 파일만 더한 폴더는 git status 에 안 나와 «손대지 않음» 으로 봄(줄이 같을 때만 유입 · 줄이 달라지면 L ∧ P 가 막음).
- 버린 갈래: 폴더 주어는 L · P 만으로 유입(레인이 고친 폴더도 유입 · 처리와 어긋남) · 머지 표에 «폴더 k» 칸(graph-owned R-3440 표 꼴 고쳐야) · 폴더 아래 파일마다 F1(같은 뜻 · 느림) · rename 걱정을 docstring 만 줄이고 파싱은 두기(사7 의 다른 갈래 — R7 에서 v1 이 레인이 index 로 폴더를 고친 줄을 유입으로 연 것이 드러나 파싱을 고침) · «상류에도 없던» 글자 바꿈(파일 판 2.22.0 글자 · smoke 단언과 함께 바뀜 · 뜻은 맞음).
- 맡을 파일: `anchor_diff.py` · `registry_gate.py` · Codex 미러 둘 · `registry_gate_smoke.py` · `anchor_diff_smoke.py` · 규칙 글 셋(그래프 · Codex 짝 셋)(registry_gate.py 는 F4-166 과 겹침 · 그래프는 R · T 단위와 차례 공용). 크기 M · 사용자 결정 아님(규칙 글은 같은 처방의 낱말 넓힘).

#### F4-166 — ⓓ 줄의 «목록만 줄어든 줄» 짝 짓기
- 고칠 설계: `registry_gate.py` ⓓ 후보 짝(`cand_shrunk`)에서만 `untouched`(앵커 · 지금 byte 같음) 가드를 걷음 → 주어가 바뀌었어도(폴더 포함) 목록이 부분집합인 ⓓ 줄은 legacy · 위반 줄(`shrunk`)은 F4-99 · 판 B #668 조건 그대로 · 머리 글 두 줄 · 주석 · `subjects` 는 위반 줄만. 규칙 글 무변(R-1683 은 위반 줄 꼴).
- 시제품 `registry_gate.py` +6 −4(v1 과 같음 · 검토 지적 없음).
- 장난감 `f166_cases.py`(앵커 [audit, billing, refund] → audit 지움 · 대조 panel.py 금지 import 둘 → 하나 걷음): 2.38.0 exit 2 · 귀속 1(#668 panel.py) · ⓓ 신규 1 → v1 · v2 exit 2 · 귀속 1(#668 그대로) · ⓓ 신규 0 · «목록만 줄어 legacy 로 센 ⓓ 줄 1건»(`toys-f166.log`).
- 실데이터(오류 모듈을 지운 레인 HEAD <레인 HEAD> · 앵커 <앵커> · registry_gate 전체): 2.38.0 · v2 모두 exit 2 · 귀속 1(#668 레인이 고친 admin 파일에서 일부만 걷음 = 판 B 조건 · 두 판 같음) · ⓓ 신규 1 → 0 · legacy 3344 → 3345 · 해소 58 → 57 · «목록만 줄어 legacy 로 센 ⓓ 줄» 1 → 2(더해진 줄 = `[ⓓ#547] application/<BC-다>` `<저장소 이름>` ['<목록 값>', …] → [… 둘] · 짝 앵커 줄이 감수자 추론과 같음) — 2.38.0 대 v2 차이는 이 다섯 자리와 툴체인 줄뿐. 2.38.0 출력은 v1 재측정과 byte 같고 v2 출력은 v1 시제품 출력과 툴체인 줄(digest · 경로)만 다름. 승인 머지 폴더 레인 실측(아래 real162)에서도 ⓓ#547 다섯 줄(main 착륙분 · 폴더 주어)이 신규 → legacy.
- 시험: `registry_gate_smoke.py` `ListShrinkRegression` 에 #547 폴더 주어 사례 · #668 고친 파일 대조 · `test_V4_V5_A1_C3…` a1 · c3 는 v2 에서 붉음(설계대로 — 고친 파일 ⓓ#448 이 legacy 짝) → `assertNotIn("목록만 줄어", out)` → `assertNotIn("목록만 줄어 잔존으로 센 줄", out)` · 이 한 줄만 고친 시험 사본(`b2/smoke/registry_gate_smoke.py`)으로 v2 62 OK · 행 45/45(`smoke-gate-v2.log` · v1 과 같음 · 사7 rename 파싱 고침도 붉음 0). 변이: `cand_shrunk` 에 `untouched` 되돌림. Codex 미러 · 봉인.
- 남는 한계: 레인이 고친 주어의 «좁아진» ⓓ 신호는 감수자에게 안 감(의도) · 폴더 주어 + 목록 칸 위반 줄은 지금도 짝 안 섬(실제 있는지 안 셈).
- 버린 갈래: 폴더면 tree 같을 때만(#547 목록은 BC 안이 바뀌어야 줄어 영원히 짝 안 섬) · 위반 줄도 걷기(판 B #668 결정과 부딪침).
- 맡을 파일: `registry_gate.py` · Codex 미러 · `registry_gate_smoke.py`. 크기 S · 사용자 결정 아님.

#### 함께 알림
- 새 붉음 0(실데이터 registry_gate 둘 · #2 둘 모두 설계한 줄뿐 · real160 · real160n · real166 · real162 넷 모두 v2 = v1 시제품(툴체인 줄 빼고 byte 같음) · 2.38.0 = v1 재측정(byte 같음)). 시험 스위트 붉음은 모두 글자 · 사유 단언 고침 몫 · exit 판정이 바뀐 기존 시험 없음.
- 새로 드러난 것(사7): v1 의 rename 짝 깎기는 «구멍 아님»(검토 판단 · P 가 지킴)이 아니었다 — 줄 글자가 그대로인 꼴(R7: 레인이 `git mv` 로 승인 머지가 들인 영역 안 파일을 index 에서만 밖으로 옮김)에서 v1 은 `폴더 verbatim` 유입 · exit 0 으로 «레인이 그 폴더 안을 고친 줄» 을 열었다(운영자 처리와 어긋남). v2 는 `worktree 수정 중` 귀속 · exit 2(2.38.0 은 `비-blob 경로` exit 2). 2.38.0 대비 새 구멍은 아니다(2.38.0 은 폴더 주어를 늘 막음).
- 별도 F4 후보(범위 밖): #2 값 중복 줄 «값마다 첫 주인 한 줄» → 이미 있는 중복 값에 셋째 주인은 신규 아님(받아들인 한계와 같음 · T1 도 같은 뿌리).
- 임시물: `b2/` 시제품 · 변이 · 장난감 · 출력은 남김 · 사본 복제본 둘(`real-api` · `real-sse`) 지움.

#### v1 → v2 바뀐 것
- 중1 — ①′ 의 (a) 가 exit 0 · 2 가 아니면 (b) 를 돌지 않음(시제품 고침) · 복원 주석 · «①′ 이 서지 못하는 길» 을 직접 시험 넷으로(`ladder_unit.py` — (a) 무너짐 · (b) 무너짐 복원 · 이름 거름 · #2 가드) · 변이 «복원 걷음» · «가드 걷음» · «(a) 문 걷음» 을 적고 모두 죽음 확인 · T3 꼴은 사3 고침 뒤 ①′ 이 서므로 e2e 로는 사3 시험으로 옮김 · e2e 로 «못 섬» 을 지으려던 T6 ~ T9 는 모두 섬(까닭 적음).
- 사2 — T1 남는 붉음을 한계 줄(fail-closed · 2.38.0 보다 덜 붉음)로 · T1 은 «비운 렌더만» 변이를 죽이는 사례로 시험에 넣음(v1 이 «새 사례» 로만 적어 둔 자리).
- 사3 — `_anchor_only_error_modules` 에 정본 후보 BC 이름 거름(`_CANDIDATE_BC_RE`) · T3 2.38.0 · v1 exit 2 → v2 exit 0 · preserve 모듈을 code 로 넣는 것은 한계 줄.
- 사4 — U 풀림 기대치에 «main 이 다른 #2 줄을 함께 들이지 않을 때» · T2 · T2c 표.
- 사5 — RenamedBc 8 건은 #2 렌더의 기준선 글 두 자리만 옮긴 대응을 사례마다 명시하고 나머지 바이트 그대로 · Q19 이름 · docstring 새로.
- 사6 — `assert_partition`(:507) 단언을 `"기준선=selector 렌더 재실행):"` 로 · 같은 맨 글자 단언 나머지가 #2 밖임을 적음.
- 사7 — rename 짝 파싱 고침(`_porcelain_paths`) + docstring 을 «git status 가 적는 경로» 로 · R7 장난감(v1 이 연 구멍 드러남) · 변이 `noren`.
- 사8 — 규칙 글 셋(R-0306 · R-3441 · R-3131 · 블록 키 · 옛 → 새) · Codex 짝 셋 · 표기 셋은 한계 줄 + 코드 주석(«상류에도 없던» 뜻 · 점 없는 이름).
- 사9 — 점 없는 부재 경로 대조군 둘(N1 `비-blob 경로` · N2 파일 판) + N3 한계 · «고쳤다 되돌림 → 유입» 한 줄.
- 사10 — 실행 시간 상한 한 줄(사본마다 렌더 +1 ~ +2 · 최악 (1 + 2m + 64) × 2 × 약 20 s · (a) 문으로 못 설 때 +1).

## 2. 검사기 오판(C)

### 검사기 오판 넷 — F4-168 · F4-169 · F4-171 · F4-179 (설계 v2 · c2 · 11-15)

넷 모두 시제품에서 장난감 2.38.0 붉음 → 녹색 · 대조군 그대로 · 사용자 결정 불필요. v2 는 검토 지적 일곱(review-cr 차1 · 중2 · 중4 · 중5 · 사7 · 사9 · review-text 사1)을 반영했다. 시제품 `c2/proto/scripts/`(v1 `c-checkers/proto/scripts/` 복사 위에 고침 · 링크 없음). 명령은 `c2/` 기준이고 `DJR_VIOLATIONS_DIR=c2/viol` · `GIT_OPTIONAL_LOCKS=0` 을 준다. 세 판(2.38.0 `rel/` · v1 · v2)을 나란히 돌리는 것은 `./run3.sh <이름> <검사기> <장난감> [인자]`(출력 `out/<이름>.{rel,v1,v2}.txt`). 사본 = `리허설 사본` 8fcaa50d49.

- 고친 파일(2.38.0 대비 diff 줄 · 괄호는 v1 대비):
  - `check-api-error-controller-contract.py` +27 −3(+22 −1) — F4-168.
  - `check-business-vocabulary.py` +171 −19(+102 −34) — 머리 글 · 상수 · #53 · #396 · #415 · #607(F4-169 · 171 · 179).
  - `business_vocab.py` +37 −7(+4 −3) — `tech_names` · 새 함수 셋(F4-171).
  - `check-naming.py` +1 −1(v1 그대로) — F4-171.
  - `check-port-adapter-pairing.py` +6 −7(v1 그대로) — 죽은 인자 `tech` 걷음. R 단위(F4-180)가 이 파일을 크게 고치므로 이 덩이는 v1 그대로 두고 R 시제품 위에 얹는다(§0-1).
- 기존 시험(v2 · 고친 검사기 모두):
  - `field_report_checker_smoke.py --scripts c2/proto/scripts` — 165 OK(2.38.0 도 165).
  - `checker_lint.py --scripts-dir c2/proto/scripts` — 27개 · 위반 0(2.38.0 과 출력 같음).
  - `findings_count_matrix.py --scripts-dir c2/proto/scripts` — 레인 73 · 일치 73 · 불일치 0.
  - `checker_baseline_matrix.py --scripts-dir c2/proto/scripts` — 레인 73 · 일치 73 · 불일치 0.
- 저장소 픽스처 `workspace/eval/fixtures/*` · `*/*`(`run-fixtures.sh` · 검사기 셋 · 실행 405): 2.38.0 대 v2 차이 10곳, 모두 ⓓ 후보이고 exit 은 전부 같다(v1 과 같은 10곳).
  - openapi 픽스처 셋: `[ⓓ#607] framework/ninja/pre_route_responses.py:220 · :235` 빠짐.
  - business_vocabulary 픽스처 일곱: check-naming `[ⓓ#36] framework/pydantic` 빠짐.
- 덤: TMPDIR 를 git 작업 트리 안에 두면 `--anchor` 기준선 재실행이 «git 저장소 TARGET 금지» 로 실패해 더 붉은 쪽(신규 59)으로 떨어진다. 앵커 재측정은 TMPDIR 기본값으로 한다.

#### F4-168 — 선택 밖 컨트롤러 모듈의 라우트를 #126 helper 로 세지 않음 · 선택 컨트롤러가 가리키는 라우트는 남김

- 결정: «나.» · F4-150 과 독립. 검토 중4(받음) — 활성 모듈이 가져온 one-hop 라우트는 helper 분석에 남긴다. 사9(받음) — 남은 오탐은 한계 줄에 적는다.
- 설계: `_semantic_findings` helper 단계를 고친다.
  - managed 모듈 가운데 active 가 아닌 것(one-hop · canonical)도 `_discover_operations` 로 라우트를 찾아 operation 으로 친다. 그 라우트 몸은 #126 helper 분석(행15 · 16 · 17)에서 빠진다.
  - 단, 선택 컨트롤러가 import 해 가리키는 라우트는 helper 로 남긴다(2.38.0 과 같은 #126). 가리킴은 선택 컨트롤러 안 `Name` · `Attribute` 를 그 파일의 import 묶음(`_import_bindings` · `_resolve_binding`)으로 푼 점 경로로 잰다. 이름 import(`from …other_controller import get_other`)와 모듈 속성(`other_controller.get_other(…)`)이 모두 이 길이다 — 라우트끼리 위임은 이 렌더의 길이기 때문이다.
  - 라우트 안 중첩 함수와 모듈 수준 함수는 지금처럼 helper 다. 판정 문장 · 규칙 글은 바뀌지 않는다.
  ```python
  referenced_by_active: set[str] = set()   # 선택 컨트롤러가 import 묶음으로 가리키는 점 경로
  for path in active_controllers:
      ...                                   # Import · ImportFrom → active_bindings
      for node in ast.walk(active_source.tree):
          if isinstance(node, (ast.Name, ast.Attribute)):
              resolved = _resolve_binding(node, active_bindings)
              if resolved is not None:
                  referenced_by_active.add(resolved.origin)
  ...
  operations = operations_by_path.get(path)
  if operations is None:   # F4-168 주석 4줄
      module = _module_name(path)
      operations = [o for o in _discover_operations(source, owner, analysis)
                    if f"{module}.{o.node.name}" not in referenced_by_active]
  operation_ids = {id(o.node) for o in operations}
  ```
- 장난감 전 / 후(`ARGS = --error-profile dddjango-code-json --scope public-v1 --api-module config/api.py --controller-module application/lesson/driving_layer/controller.py --scope-bc lesson --error-bc lesson` · 장난감은 `api_error_controller_code/good` + B 컨트롤러 `other_controller.py` · 줄은 `other_controller.py:<줄>`):

  | 장난감 | 꼴 | 2.38.0 | v1 | v2 |
  |---|---|---|---|---|
  | `cr/t168/cases/t1` | B 라우트 + A 가 B 의 모듈 함수 `principal_of` 를 import | 2 `#126 :13` | 0 | **0** |
  | `cr/…/t3` | 라우터 클래스 별칭 | 2 `:13` | 0 | 0 |
  | `cr/…/t4` | 라우터 변수 별칭 | 2 `:14` | 0 | 0 |
  | `op/t168/t8`(중4) | A 라우트가 B 라우트 `get_other` 를 이름 import 로 불러 위임 | 2 `:13` | **0** | **2 `:13`** |
  | `t168m`(새) | 같은 위임을 모듈 속성 `other_controller.get_other(…)` 로 | 2 `:13` | **0** | **2 `:13`** |
  | `cr/…/t0` 대조 | B 의 모듈 수준 helper | 2 `:9` | 2 `:9` | 2 `:9` |
  | `cr/…/t5` 대조 | B 라우트 안 중첩 helper | 2 `:14` | 2 `:14` | 2 `:14` |
  | `cr/…/t2`(사9) | B 가 라우터를 다른 모듈(`routers.py`)에서 가져옴 | 2 `:14` | 2 `:14` | 2 `:14`(오탐 남음 · 한계) |
  | `v1/toyB`(현장 꼴 · 레인 시점 트리) | 내부 컨트롤러가 `<컨트롤러>` 의 `<도우미 함수>`(라우트 아님)을 import | 2 `#126 <컨트롤러>.py:103 · :156` | 0 | **0** |
  | `v1/toyD` 대조 | toyB + 모듈 수준 helper | 2 `:66 · :107 · :160` | 2 `:66` | 2 `:66` |

  - toyB · toyD 는 내부 렌더다(`--scope internal --api-module <프로젝트>/internal_api.py` · 컨트롤러 둘 · `--scope-bc` · `--error-bc <BC-라> <BC-마>` · `--anchor`). 장난감을 홀로 선 저장소로 다시 지어 앵커 SHA 가 바뀌었다(옛 7a3b4e3 → toyB b9ed757 · toyD 32583e0 · 커밋 글에 «옛 7a3b4e3»).
- 사본(`run168-replica.sh` · 앵커 HEAD · 기본 TMPDIR) — 2.38.0 대 v2 byte 동일.
  - 공개 전체 렌더(컨트롤러 58): exit 0 · 기존 63.
  - 내부 렌더: exit 0 · 기존 4.
  - 현장 꼴(`<도우미 함수>` import)은 사본 HEAD 에 없다. 레인 시점 트리 toyB 에서 v2 exit 0 으로 풀림을 확인했다.
- 시험: smoke `CrossScopeControllerHelperRegression`(`api_error_controller_code/good` 사본 + 같은 BC 둘째 컨트롤러 · `field_report_checker_smoke.py` 에 넣음).
  - 사례:
    - t1 — 선택 컨트롤러가 둘째 모듈 함수를 import → #126 0.
    - t0 — 둘째 모듈 모듈 수준 helper → 그 줄만 #126.
    - t5 — 라우트 안 중첩 helper → #126.
    - t8 — 이름 import 위임 → #126 `:13`.
    - t168m — 모듈 속성 위임 → #126 `:13`.
    - t2 — 오탐 남음을 `assertIn` 으로 못 박지 않고 한계로 적기만 한다.
  - 변이(`c2/mut.py` 로 v2 사본에 걸어 «죽음» 확인):
    - «선택 밖 라우트 찾기 걷음»(`for operation in []`) → t1 0 → 2.
    - «가리킨 라우트 남김 걷음»(`not in referenced_by_active` 거름 걷음) → t8 · t168m 2 → 0.
    - «모듈 속성 걷음»(`(ast.Name, ast.Attribute)` → `ast.Name`) → t168m 2 → 0. t8 은 산다(이름 import 라).
  - 골든 무변(위 두 행렬 일치).
- 남는 한계:
  - (사9) 라우터를 다른 모듈에서 가져와 데코레이트한 선택 밖 컨트롤러(t2)는 `_discover_operations` 가 라우트로 못 읽는다. 그래서 2.38.0 처럼 #126 오탐이 남는다 — 막는 쪽이라 새 구멍은 아니다.
  - 같은 scope 위임 — 두 컨트롤러를 함께 선택하면 B 라우트는 operation 이라 위임이 #126 에 안 걸린다. 2.38.0 도 exit 0 인 옛 한계다.
  - 선택 컨트롤러가 글자로 가리키지 않는 위임(문자열 · `getattr` · 동적 import)은 helper 로 안 센다. 2.38.0 은 이것을 셌다.
  - 선택 밖 라우트 자체의 위반은 그 scope 렌더가 본다. 그 scope 가 12-slot 에 없으면 preflight 몫이다. 2-hop 은 범위 밖이다.
- 버린 갈래:
  - one-hop 에서 컨트롤러 모듈을 통째로 빼기 — 모듈 수준 helper 를 놓친다.
  - F4-150 까지 미루기 — 트리 결정과 무관하다.
  - 이름 import 로 가져온 라우트만 남기기(처분 글자 그대로) — 모듈 속성 위임이 2.38.0 대비 새 구멍으로 남는다(t168m: 2.38.0 2 → 이름만 남김 0).
- 맡을 파일: `check-api-error-controller-contract.py` + Codex 미러 · smoke. 크기 S.

#### F4-169 — #53 판정 셋(모델 / 모델 아님 / 모름) · «모델 아님» 이 드러난 이름만 비켜 줌

- 결정:
  - 운영자 선 — «DB 표 있는 모델은 출처 무관 막기»(Django 기본 User 는 그대로 막힘 · 규칙 문장 «모델 import 금지» 그대로).
  - 검토 차1(받음) — 판정 셋 · #53 은 «모름» 을 막음.
  - 사7(받음) — `from <저장소 안 꾸러미> import models` 후보.
  - text 사1(받음) — 괄호 글 · 트리 명세 span.
  - 좁은 재확인 사소(review-cr 11-15 17:44 · 받음) — 표준 라이브러리 · 내장 기저(`Enum` · `NamedTuple` · `Protocol` · `ABC` · `object` · `Exception` …)를 «모델 아님» 고정 목록에 더함 · `sys.stdlib_module_names` 는 쓰지 않음(파이썬 판마다 갈림 — F4-171 과 같은 문제).
- 설계: `_check_framework_test` 를 고친다.
  - 후보 셋:
    - ㉠ 모듈 이름에 `.models` 가 들었거나 `models` 로 끝나는 `from … import`(지금처럼).
    - ㉡ `import x.models`. 단 ORM 도구 모듈 `django.db.models` 와 그 아래는 뺀다.
    - ㉢ 새 — 가져오는 이름이 `models` 인 `from <꾸러미> import models`(상대 포함). 꾸러미가 저장소 안일 때만 후보다 — `<꾸러미>.models` 나 `<꾸러미>` 가 가상환경 · 캐시 폴더 밖 저장소 안 파일이면 막는다. 바깥 꾸러미(`from django.db import models` · `from django.contrib.auth import models`)는 후보가 아니다.
  - ㉠ 의 판정:
    - 상대 import 를 못 풀면 막음.
    - ORM 도구 모듈이면 받음.
    - `*` 는 막음.
    - 저장소 밖 모듈이면 고정 목록 `NON_MODEL_NAMES`(`django.contrib.auth.models`: AnonymousUser) 안 이름만일 때 받음.
    - 저장소 안 모듈이면 이름마다 본다 — 맨 위 클래스가 아니면(함수 · 재수출 · 상수) 막고, 클래스면 판정 셋을 낸다. **«모델 아님» 만 받는다.**
      - 모델 — 안 `Meta` 에 `db_table` · `managed` · `proxy` 가 있거나, 기저 하나라도 모델이다(`django.db.models.Model` · `django.db.models.base.Model` · 저장소 안 기저는 끝까지).
      - 모델 아님 — 기저가 없거나, 모든 기저가 모델 아님이다. 저장소 안 기저는 끝까지 풀어 모델 아님이어야 한다. 바깥 기저는 고정 목록만 모델 아님이다:
        - `django.db.models` 의 `QuerySet` · `Manager` · `Choices` · `TextChoices` · `IntegerChoices`(하위 모듈 경로 `query` · `manager` · `enums` 포함).
        - 표준 라이브러리 `enum`(`Enum` · `StrEnum` · `IntEnum` · `Flag` · `IntFlag`) · `typing`(`NamedTuple` · `TypedDict` · `Protocol` · `Generic`) · `abc.ABC`.
        - 내장 `object` 와 내장 예외 · 경고 클래스 70개(합쳐 71 이름 · `BUILTIN_NON_MODEL_BASES` — 파이썬 3.14 목록을 글자로 박음 · 실행 파이썬에서 읽지 않음). 맨 이름(`Exception`)은 그 모듈에 `*` import 가 없고 맨 위에서 같은 이름을 import · 대입하지 않을 때만 내장이다. `builtins.<이름>` 점 경로도 같다.
        - 첨자 기저(`Generic[T]` · `Protocol[T]` · `models.Manager["Coupon"]`)는 첨자 앞 클래스로 판정한다.
      - 모름 — 그 밖이다. 목록 밖 바깥 기저(`AbstractUser` · `TimeStampedModel` · `collections.abc` · `typing_extensions` …), 식 기저(`_base()`), 못 찾는 기저(재수출 · `*` · `Base = models.Model` 별칭 · 덮인 내장 이름), 키워드(`metaclass=`), 순환(이미 지나온 (파일, 클래스))이 모두 여기다.
      - 기저가 여럿이면 «모델» 이 이기고, 다음이 «모름» 이다 — `Generic[T], models.Model` · `Exception, Coupon` 은 모델이다.
  - 판정 줄 글자는 그대로다. 저장소 안 기저 따라가기는 같은 파일 맨 위 클래스(import 이름이 아닐 때)와 모듈 수준 import 출처의 저장소 안 모듈 맨 위 클래스다.
  - 자가 #664 와 다르다:
    - #664 는 «`cross_context/` 가 정의한 클래스가 확실히 모델인가» 를 묻는다(모델이면 막음 · 프로젝트 기저 한 번).
    - #53 은 «들인 이름이 확실히 모델이 아닌가» 를 묻는다(아니면 막음 · 끝까지).
    - 묻는 쪽이 반대라서 v1 처럼 #664 자를 빌리면 모르는 기저가 받는 쪽으로 샌다(차1). 검사기끼리 import 하지 않는다.
  ```python
  MODEL, NOT_MODEL, UNKNOWN_MODEL = "모델", "모델 아님", "모름"
  BUILTIN_NON_MODEL_BASES = frozenset({"object", "ArithmeticError", …, "ZeroDivisionError"})   # 71 이름 · 3.14 고정
  NON_MODEL_BASES = {django.db.models 다섯(+하위 경로) · enum 다섯 · typing 넷 · abc.ABC} | {f"builtins.{n}" …}
  def _model_verdict(root, path, mod, cls, seen) -> str        # 안 Meta 표지 · keywords → 모름 · 첨자 벗김 · 덮이지 않은 내장 맨 이름 → 모델 아님 · 기저마다 판정 → 모델 > 모름 > 모델 아님
  def _dotted_base_verdict(root, dotted, seen) -> str          # Django 모델 기저 · NON_MODEL_BASES · 저장소 안 맨 위 클래스(끝까지) · 그 밖 모름
  def _repo_module_file(root, dotted) -> Path | None           # 저장소 안(SKIP_DIRS 밖) 모듈 · 꾸러미 파일
  # _imports_db_model: … return any(n not in classes or _model_verdict(...) != NOT_MODEL for n in names)
  ```
- 규칙 글(산문만 · graph · final.md 에 #53 없음 · decision-record 는 mkrev2 를 돌린 뒤 되돌림):
  - `docs/master/mkrev2.py:811`(→ `file_tree.html:2971`):
    - 옛 «(모델 import 금지)».
    - 새 «(모델 import 금지 — 모델은 <code>models.Model</code> 을 잇는 클래스다(추상 · <code>managed = False</code> · 프록시 포함 · 별칭이나 프로젝트 기저를 거쳐도 · 출처 무관 — Django 기본 User 도). 모델인지 알 수 없는 이름(함수 · 재수출 · <code>*</code> · 바깥 기저를 이은 클래스)도 막고, 모델이 아님이 드러난 이름(<code>AnonymousUser</code> · <code>django.db.models</code> 의 <code>Q</code> 같은 ORM 도구 · 기저가 없거나 <code>Enum</code> · <code>NamedTuple</code> · 예외 같은 정해 둔 표준 기저만 이은 클래스)만 막지 않는다)».
  - `mkrev2.py:454` 표 칸:
    - 옛 «(모델 import 금지)».
    - 새 «(모델 import 금지 — 모델인지 모르면 막는다)».
  - `mkrev2.py:5871`(D24 결정 글 «모델 import 금지 → 팩토리는 정의상 못 들어온다»)은 결정 기록이라 그대로 둔다.
  - 트리 명세 `workspace/design/2026-08-08-tree-revision-spec.md:381`(#53 행): 규칙 문장은 그대로 두고, 문장 끝 «(#392·#620).» 뒤에 span 을 더한다 — `<span>11-15 · F4-169 — 모델 = `models.Model` 을 잇는 클래스(추상 · managed=False · 프록시 · 출처 무관 — Django 기본 User 도). 모델 아님이 드러난 이름(AnonymousUser · `django.db.models` 의 ORM 도구 · 기저 없거나 끝까지 풀어 모두 모델 아닌 저장소 안 클래스 — 바깥 기저는 `django.db.models` 의 QuerySet · Manager · Choices 류 · `enum` · `typing` 의 NamedTuple · TypedDict · Protocol · Generic · `abc.ABC` · 내장 `object` · 예외의 고정 목록만)만 비켜 주고, 모델인지 알 수 없는 이름(함수 · 재수출 · `*` · 목록 밖 바깥 기저 · 식 기저)은 막는다 · 후보에 `import x.models` · `from <저장소 안 꾸러미> import models` 를 더함 — `check-business-vocabulary`.</span>`
  - 검사기 머리 글: 27행 «#53 HTTP 로만 구동(모델·팩토리 import 0)» → «… import 0 — 모델 아님이 드러난 이름만 비켜 준다)». #53 머리 주석 6줄.
- 장난감 전 / 후(`./run3.sh <이름> check-business-vocabulary <장난감>` · 모두 exit 2 — 남는 진짜 모델 줄 때문):
  - v1 toy169(a ~ l) — v2 = v1:
    - a AnonymousUser 막힘 → 받음.
    - b Q 막힘 → 받음.
    - c contrib User · d 루트 앱 모델 · k 저장소 안 추상 기저 거친 모델 · i `AnonymousUser, User` — 막힘 그대로.
    - e `from django.db import models` — 받음 그대로.
    - f `import legacy_shop.models` · l `import django.contrib.auth.models` — 놓침 → 막힘.
    - h 같은 models 파일 기저 없는 클래스 · j `django.db.models.functions` — 막힘 → 받음.
  - 차1 `op/t169`(m · n):

    | 꼴 | 2.38.0 | v1 | v2 |
    |---|---|---|---|
    | c1 대조 `Coupon(models.Model)` | 막힘 | 막힘 | 막힘 |
    | m1 `Member(AbstractUser)`(바깥 기저) | 막힘 | **받음** | **막힘** |
    | m2 `Stamp(TimeStampedModel)`(바깥 추상 기저) | 막힘 | **받음** | **막힘** |
    | m3 `Voucher(ShopBase)` → `ShopBase(Stamped)` → `models.Model`(두 단) | 막힘 | **받음** | **막힘** |
    | m4 `Dyn(_base())`(식 기저) | 막힘 | **받음** | **막힘** |
    | m5 다른 모듈 두 단 기저 `Gift` | 막힘 | **받음** | **막힘** |
    | n1 `from legacy_shop import models as shop_models`(사7) | 받음 | 받음 | **막힘** |
    | n2 `from legacy_shop import models`(사7) | 받음 | 받음 | **막힘** |

  - 새 `t169x`(받는 쪽 · 모름 쪽 대조):

    | 꼴 | 2.38.0 | v1 | v2 |
    |---|---|---|---|
    | p1 `models.QuerySet` 기저 | 막힘 | 받음 | 받음 |
    | p2 `models.TextChoices` | 막힘 | 받음 | 받음 |
    | p3 `models.IntegerChoices` | 막힘 | 받음 | 받음 |
    | p4 같은 파일 기저 없는 클래스를 이은 클래스 | 막힘 | 받음 | 받음 |
    | p5 다른 저장소 안 모듈의 기저 없는 클래스를 이은 클래스 | 막힘 | 받음 | 받음 |
    | p6 `from django.db import models` | 받음 | 받음 | 받음 |
    | p7 `from django.contrib.auth import models`(바깥 꾸러미) | 받음 | 받음 | 받음 |
    | q1 순환 기저(`models.Loop` ↔ `cyc.Loop`) | 막힘 | **받음** | **막힘** |
    | q2 `Enum` 기저 | 막힘 | **받음** | 받음(재확인 사소 뒤 · 첫 v2 는 막힘) |
    | q3 `metaclass=` | 막힘 | **받음** | **막힘** |
    | q4 proxy Meta | 막힘 | 막힘 | 막힘 |
    | q5 `managed = False` Meta(기저 없음) | 막힘 | 막힘 | 막힘 |
    | q6 `from ... import models`(저장소 안 상대 · 사7) | 받음 | 받음 | **막힘** |
    | q7 `import *` | 막힘 | 막힘 | 막힘 |

  - 재확인 사소 `cr/t169b`(검토자 장난감 · `shop/models.py` 꼴 14 + 현장 꼴) — 칸은 2.38.0 · v1 · 첫 v2 · v2(이번):

    | 꼴 | 2.38.0 | v1 | 첫 v2 | v2 |
    |---|---|---|---|---|
    | a `Coupon(models.Model)` | 막힘 | 막힘 | 막힘 | 막힘 |
    | b 기저 없음 · c `@dataclass` 기저 없음 | 막힘 | 받음 | 받음 | 받음 |
    | d `Enum` · e `StrEnum` · f `enum.Enum` | 막힘 | 받음 | 막힘 | **받음** |
    | g `NamedTuple` · h `TypedDict` · i `Protocol` · j `ABC` | 막힘 | 받음 | 막힘 | **받음** |
    | k `object` · l `Exception` | 막힘 | 받음 | 막힘 | **받음** |
    | m `models.QuerySet` · n `models.TextChoices` | 막힘 | 받음 | 받음 | 받음 |
    | z 현장 꼴 AnonymousUser | 막힘 | 받음 | 받음 | 받음 |

    exit 은 넷 모두 2(a 때문).
  - 새 `t169c`(목록 대조 · 이긴 판정 · 덮인 내장):

    | 꼴 | 2.38.0 | v1 | 첫 v2 | v2 |
    |---|---|---|---|---|
    | r1 `GenericCoupon(Generic[T], models.Model)` | 막힘 | 막힘 | 막힘 | 막힘(모델이 이김) |
    | r2 `ErrorCoupon(Exception, Coupon)` | 막힘 | 막힘 | 막힘 | 막힘(모델이 이김) |
    | r3 `CouponManager(models.Manager["Coupon"])` | 막힘 | 받음 | 막힘 | **받음** |
    | r4 `Reader(Protocol[T])` · r5 `Box(Generic[T])` | 막힘 | 받음 | 막힘 | **받음** |
    | r6 `Oops(ValueError)` | 막힘 | 받음 | 막힘 | **받음** |
    | r7 맨 위 `Exception = models.Model` 뒤 `Shadowed(Exception)`(`shop/models_shadowed.py`) | 막힘 | **받음** | 막힘 | 막힘 |
    | r8 `from shop.models import *` 뒤 `Starred(ValueError)`(`shop/models_starred.py`) | 막힘 | **받음** | 막힘 | 막힘 |

    exit 은 넷 모두 2.
  - `op/t169`(m1 ~ m5 · n1 · n2) · v1 toy169 · toy53 은 첫 v2 와 같다. `t169x` 는 q2 `Enum` 한 줄만 막힘 → 받음으로 바뀐다(위 표).
  - text 사1 `text/toy53` — v2 = v1:
    - 추상 모델 `AbstractStamp` · 구체 `Coupon` · 함수 `coupon_count` — 막힘 그대로.
    - 기저 없는 `CouponCode` — 막힘 → 받음.
    - 괄호 글을 이 판정에 맞춘다(위).
- 사본(`run-vocab-replica.sh` · 파이썬 넷): `[#53] framework/test/unit/<시험 파일>.py:15` 한 줄만 빠진다. 현장 꼴 AnonymousUser 는 여전히 풀린다. 사본 `framework/test` 의 models import 는 그 한 줄뿐이라 사7 · 차1 로 새로 막히는 줄은 0 이다 → 새 붉음 0. 재확인 사소 뒤 v2 사본 출력은 첫 v2 와 파이썬 넷 모두 byte 동일이다. 저장소 픽스처에서도 vocab 135 실행 모두 첫 v2 와 같다.
- 시험: smoke `FrameworkTestModelImportRegression`.
  - 사례: a ~ l · m1 ~ m5 · n1 · n2 · p1 ~ p7 · q1 ~ q7 · t169b 꼴 14 · r1 ~ r8 · toy53 넷을 subTest 로 넣는다. 루트 앱은 `legacy_shop/{base,models,kinds,cyc}.py` · `legacy_shop/deep/{mid,models}.py` · `accounts/models.py`.
  - 변이(`c2/mut.py` 로 v2 사본에 걸어 모두 «죽음» 확인):
    - «모름을 받음»(`!= NOT_MODEL` → `== MODEL`) → m1 · m2 · m4 풀림.
    - «저장소 안 기저 따라가기 끔»(`_dotted_base_verdict` 끝을 모름으로) → p5 막힘.
    - «순환 가드 걷음» → q1 RecursionError(exit 1).
    - «`NON_MODEL_BASES` 의 QuerySet 줄 걷음» → p1 막힘.
    - «`NON_MODEL_BASES` 의 `enum` 줄 걷음» → t169b d · e · f 막힘.
    - «내장 맨 이름 갈래 걷음» → t169b k · l 막힘.
    - «첨자 벗김 걷음» → r3 · r4 · r5 막힘.
    - «맨 위 대입 가드 걷음» → r7 풀림.
    - «사7 갈래 걷음» → n1 · n2 풀림.
    - «키워드 가드 걷음» → q3 풀림.
    - «`NON_MODEL_NAMES` 비움» → a 막힘.
    - v1 것 «`_orm_tool_module` False» → b · j · «`ast.Import` 갈래 False» → f · l 은 그대로 둔다.
  - 골든 무변(bad_rules `[#53] order_runner.py:3` 그대로 · 행렬 일치) · pregate 로스터 밖.
- 남는 한계:
  - 바깥 기저는 고정 목록만 «모델 아님» 이다(`django.db.models` 다섯 · `enum` 다섯 · `typing` 넷 · `abc.ABC` · 내장 `object` · 예외). 목록 밖 표준 기저(`collections.abc` · `typing_extensions` · `numbers` …)와 바깥 mixin 을 이은 저장소 안 모델 아닌 클래스는 막힌다(2.38.0 과 같음 · 막는 쪽 · 현장에서 나오면 목록에 더함).
  - 내장 예외 목록은 파이썬 3.14 것이다. 그 뒤 판에 생긴 이름(3.15 `ImportCycleError`)은 «모름» 이다.
  - 재수출로 온 이름과, 꾸러미 `models/__init__.py` 재수출로 온 기저는 «모름» 이다(막음).
  - 바깥 모델 아닌 이름은 AnonymousUser 하나다(현장에서 나오면 더함).
  - `.models` 아닌 모듈의 모델은 옛 판처럼 안 잡는다.
  - `from <바깥 꾸러미> import models`(예: `from django.contrib.auth import models`)는 후보가 아니다(사7 선). 그런데 `import django.contrib.auth.models` 는 막는다 — 두 꼴이 비대칭이다.
  - 모듈 수준 import 만 기저 출처로 본다(함수 안 import · `TYPE_CHECKING` 블록 안 클래스는 «모름»).
- 버린 갈래:
  - #664 자 그대로 빌리기(v1) — «확실히 모델» 을 묻는 자라 모르는 기저가 받는 쪽으로 샌다(차1).
  - 프로젝트 모델만 막기 — 지시 선과 다르다.
  - 설치 Django 소스 읽기 — 환경 의존이다.
  - `framework/test/unit/` 을 #53 에서 빼기.
  - `sys.stdlib_module_names` 로 표준 라이브러리 기저를 통째로 받기 — 실행 파이썬 판마다 판정이 갈린다(F4-171 과 같은 문제).
  - 내장 예외를 실행 파이썬의 `builtins` 에서 읽기 — 같은 까닭으로 글자 목록으로 박았다.
- 크기 S~M.

#### F4-171 — 기술 폴더 판정을 저장소 안 글자로만 · 뿌리 가림은 진짜 꾸러미 · 모듈만

- 결정: «나.» · 검토 중5(받음) — 가림 = `(root/lib/"__init__.py").is_file() or (root/f"{lib}.py").is_file()`.
- 설계:
  - `business_vocab.tech_names()` 에서 `packages_distributions()` 를 걷는다(stdlib 모듈명 + 흔한 기술 낱말 목록만).
  - `business_vocab.py` 새 함수 셋:
    - `TECHNOLOGY_LIBRARIES` + `folder_libraries(folder)`(검사기에서 옮김).
    - `imports_library(mod, libraries)` — 절대 import 만 · #415 와 #396 이 함께 쓴다.
    - `technology_folder(root, folder)` — 이름이 `tech_names()` 에 있거나, 폴더 바로 아래 모듈 하나라도 그 이름 라이브러리를 저장소 밖에서 import 하면 기술 폴더다.
  - 저장소 뿌리에 같은 이름의 **꾸러미(`__init__.py` 있는 폴더)나 모듈 `<lib>.py`** 가 있으면 그 import 는 저장소 안이다. `__init__.py` 없는 폴더(이름공간 · 설정 폴더 `docker/` · `jwt/README.md` 같은 것)는 파이썬이 설치 라이브러리를 먼저 잡으므로 가리지 않는다(중5).
  - `#396 is_tech = p.name in CURATED_TECH or vocab.technology_folder(root, p)`.
  - #415 도 `imports_library` 를 쓴다. 상대 ImportFrom 은 더 이상 라이브러리 import 가 아니다 — 픽스처 · 사본 차이 0.
  - 규칙 #396 ③ 원문과 글자 그대로 맞으므로 규칙 글은 바뀌지 않는다.
- 지시와 다르게 한 것(v1 그대로): «stdlib 뺌» 은 안 했다. stdlib 이름 폴더가 지금 기술로 지나가는데(픽스처 good · bad_rules `framework/email/`) 빼면 새 붉음이 난다. stdlib 판은 툴체인 행에 적힌다.
- 다른 자리:
  - check-naming:621(framework ⓓ#36 후보) `d.name not in tech` → `not vocab.technology_folder(root, d)`. :183(BC 쪽)은 그대로다(이제 결정적).
  - check-port-adapter-pairing 의 죽은 인자 `tech` 를 걷는다(R 시제품 위에 얹음).
- 장난감 전 / 후(homebrew python3 3.15.2 · `venv-jwt` 3.15.2 + PyJWT — 칸은 «brew / jwt» exit):

  | 장난감 | 꼴 | 2.38.0 | v1 | v2 |
  |---|---|---|---|---|
  | `op/t171/nsdir`(중5) | toy171-B + 뿌리 `jwt/README.md` 만 | 2 / 0 | **2 / 2** `[#396] framework/jwt` | **0 / 0** |
  | `v1/toy171-B` | `framework/jwt/access_token_codec.py` `import jwt` | 2 / 0 | 0 / 0 | 0 / 0 |
  | `v1/toy171-shadow` 대조 | 뿌리 `jwt/__init__.py`(진짜 꾸러미) | 2 / 0 | 2 / 2 | 2 / 2 `[#396] framework/jwt` |
  | `t171mod`(새) 대조 | 뿌리 모듈 `jwt.py` | 2 / 0 | 2 / 2 | 2 / 2 `[#396] framework/jwt` |
  | `v1/toy171` 대조 C | money/ · httpx/(import 없는 모듈) · av/ · jwt/jwt.py | 파이썬마다 갈림 | 같음 | 같음 `[#396] av · money · [#412] jwt/jwt.py · [#415] httpx/timeouts.py` |

  - check-naming(같은 장난감 · brew): toy171 ⓓ#36 httpx · jwt 두 줄, toy171-B jwt 한 줄 빠짐(exit 0 같음) · port-adapter-pairing 2.38.0 과 byte 동일.
  - 게이트 `registry_gate.py <장난감> --anchor <A pre>`(홀로 선 저장소로 다시 지어 옛 27e29ff → toy171-B 1297b84 · nsdir fae1a59):

    | 장난감 | 2.38.0 brew | 2.38.0 jwt | v2 brew | v2 jwt |
    |---|---|---|---|---|
    | toy171-B | 2 red `[#396]` | 0 | 0 | 0 |
    | nsdir | 2 red `[#396]` | 0 | 0 | 0 |

- 사본(`run-vocab-replica.sh`):
  - v2 는 brew · `.venv` · `venv-jwt` 출력이 byte 동일이다(v1 출력과도 byte 동일).
  - 2.38.0 brew · `.venv` 대비 `[#396] av · httpx · jwt` 셋이 빠지고 `[#415] framework/av/<모듈>.py`(stdlib 만 import) 하나가 선다. venv-jwt 대비로는 `[#396] av · httpx` 둘이 빠진다.
  - 그 #415 는 main 에 이미 있는 줄이라 귀속 0 이고, 설계에 적힌 줄이다(v1 과 같음) → **설계 밖 새 붉음 없음**. 사본 뿌리에 같은 이름 꾸러미 · 모듈이 없어 중5 고침은 사본에 닿지 않는다.
  - `/usr/bin/python3` 3.9.6 은 두 판 모두 exit 1이다(pyproject python>=3.14 가드 · 기존).
  - check-naming ⓓ#36: brew 4줄(av · httpx · jwt · pydantic) · venv-jwt 3줄이 줄어든다(exit 같음).
  - port-adapter-pairing 은 2.38.0 과 byte 동일이다.
- 시험: smoke `TechnologyFolderEnvRegression`(`framework/zz_toylib/` + `import zz_toylib` — 환경 무관).
  - 사례:
    - 기술 판정 0.
    - money #396 · httpx #415 · `<x>/<x>.py` #412.
    - 뿌리 꾸러미 shadow(`zz_toylib/__init__.py`) #396.
    - 새 — 뿌리 모듈 shadow(`zz_toylib.py`) #396.
    - 새 — 뿌리 이름공간 폴더(`zz_toylib/README.md` 만) → 기술 판정 0.
  - 변이(`c2/mut.py` 로 «죽음» 확인):
    - «import 판정 걷음»(→ `p.name in vocab.tech_names()`) — v1.
    - «저장소 안 가림 걷음»(`if True`) → shadow · t171mod #396 사라짐.
    - 새 «`__init__.py` 조건을 폴더 있음으로»(`(root / lib).is_dir()`) → nsdir 0 → `[#396]`.
  - 골든: check-naming ⓓ#36 pydantic 한 줄씩뿐(cross matrix red 행 아님). `findings_count_matrix` · `checker_baseline_matrix` 일치를 확인했다. `checker_cross_matrix --emit-expected` diff 0 은 구현 때 확인한다.
- 남는 한계:
  - stdlib 이름 판정은 파이썬 판에 따른다(3.9 FALLBACK). 파일 없는 stdlib 이름 폴더에서만 갈린다.
  - 모듈 없는 기술 이름 폴더(`__init__.py` 뿐)는 이제 #396 이다(사본 0).
  - 함수 안 import 도 센다(#415 와 같은 자).
  - 뿌리 아닌 `sys.path` 항목(`src/` 배치 등)의 같은 이름 꾸러미는 가림으로 안 본다(사본 · 표준 트리에 없음).
- 버린 갈래:
  - 의존성 선언 읽기 — 배포판 → import 이름 대응이 안 된다.
  - 게이트가 대상 .venv 쓰기 — 여전히 환경 의존이다.
  - 뿌리 폴더면 다 가림(v1) — 이름공간 폴더가 설치 라이브러리를 가린다고 잘못 본다(중5).
- 맡을 파일: `business_vocab.py` · `check-business-vocabulary.py` · `check-naming.py` · `check-port-adapter-pairing.py` + Codex 미러 넷 · smoke. 겹침: port-adapter-pairing 은 F4-180, check-naming 은 다른 단위와 겹칠 수 있다. 크기 M.

#### F4-179 — 플러그인 고정 파일을 #415 · ⓓ#607 에서 뺌(표는 클래스가 없을 때만)

- 결정: «나.»(이번 판) · 검토 중2(받음) — ClassDef 없는 표만 #415 에서 뺀다 · 숨긴 클래스 대조군을 둔다 · 정본의 ⓓ#607 빼기는 그대로.
- 설계: `check-business-vocabulary.py` 에 상수 둘을 둔다(경로 글자는 검사기마다 들고 있는 관례).
  - `PRE_ROUTE_TABLE_FILE = "framework/ninja/pre_route_response_table.py"` 는 **클래스(ClassDef · `ast.walk`)가 하나도 없을 때만** #415 «라이브러리 import» 요구에서 뺀다.
    - #63 b(`_table_findings`)는 표 파일의 함수 · 다른 문장을 막지만, ClassDef 는 내용 검사 없이 지나간다(몸통 Schema 자리라서).
    - 그래서 클래스가 있으면 지금처럼 ninja import 를 요구한다. 몸통 Schema 행이 있는 표는 어차피 `from ninja import Schema` 라 통과한다.
  - `PRE_ROUTE_CANONICAL_FILE = "framework/ninja/pre_route_responses.py"` 는 ⓓ#607 «숫자 임계값 비교» 후보에서 뺀다. #63 이 정본 자산 둘과 모든 프로필에서 파일 전체 AST 를 맞춘다.
  - `_check_technology` 는 F4-171 과 함께 고친다.
- 규칙 글(산문 · 선택): `docs/master/mkrev2.py:799`(→ `file_tree.html:2959`) «`<technology>/<module>.py` — 그 라이브러리의 타입 없이는 문장 자체가 성립하지 않는 코드.» 뒤에 «(플러그인이 자리를 정한 <code>ninja/pre_route_response_table.py</code> 는 클래스가 없으면 이 문장 밖이다 — 몸통 Schema 행이 없으면 ninja 를 import 하지 않는다. 클래스를 두면 지금처럼 ninja 를 import 해야 한다)» 를 더한다.
  - 트리 명세 `2026-08-08-tree-revision-spec.md:731`(#415 행)는 규칙 문장 그대로 두고 문장 끝에 span 을 더한다 — `<span>11-15 · F4-179 — 플러그인이 자리를 정한 `framework/ninja/pre_route_response_table.py` 는 클래스가 하나도 없으면 이 문장 밖(몸통 Schema 행이 없으면 ninja 를 import 하지 않는다 · 칸은 #63 이 본다 · 클래스를 두면 ninja import 를 요구) · F4-171 — 라이브러리 import 는 절대 import 만 센다(상대 import 는 저장소 안) — `check-business-vocabulary`.</span>`
  - graph R-3749(implementation-django-ninja s023-6.2/b37)는 그대로다.
- 장난감 전 / 후(`./run3.sh <이름> check-business-vocabulary <장난감>`):

  | 장난감 | 꼴 | 2.38.0 | v1 | v2 |
  |---|---|---|---|---|
  | `v1/toy179-only` | 2.38.0 정본 + 몸통 없는 text/html 표 | 2 `[#415] …table.py` · `[ⓓ#607] …:220 · :235` | 0 | 0 |
  | `v1/toy179-237` | 2.37.0 정본 | 2 `#415` · `ⓓ#607 :142` | 0 | 0 |
  | `op/t179/hidden`(중2) | toy179-only + 표에 ninja 안 쓰는 `class RefundWindow: allows(days) → days <= 7` | 2 `[#415] …table.py` · `[ⓓ#607] …table.py:17` · 정본 :220 · :235 | **0**(`ⓓ#607 …table.py:17` 만) | **2** `[#415] …table.py` · `[ⓓ#607] …table.py:17` |
  | `t179schema`(새) 대조 | toy179-only + 표에 `from ninja import Schema` · `class HostRejectedBody(Schema)` | 0 · `ⓓ#607 :220 · :235` | 0 | 0 |
  | `v1/toy179` 대조 | + `framework/ninja/page_limit.py`(ninja import 없이 `if size > 100`) | 2 `#415` · `ⓓ#607` page_limit · 표 · 정본 | 2 page_limit 만 | 2 page_limit 만 |

- 사본: 경로 앞 파일이 없어 차이 0이다. openapi 픽스처 셋에서 ⓓ#607 두 줄씩 빠진다(exit 무변).
- 시험: smoke `PreRouteFixedFileRegression`.
  - 사례:
    - 정본 `pre_route_responses_canonical.py` · `_2_37_0.py` 복사 + 몸통 없는 표 → 0.
    - 새 — 숨긴 클래스 표 → `[#415] …table.py`.
    - 새 — 몸통 Schema 표 → 0.
    - 대조군 page_limit.
  - 변이(`c2/mut.py` 로 «죽음» 확인):
    - «표 빼기 걷음»(`if False`) → toy179-only #415.
    - 새 «클래스 가드 걷음»(표면 늘 뺌) → hidden 2 → 0.
    - «정본 #607 빼기 걷음» → ⓓ#607 되살아남(v1).
  - 골든 무변.
- 남는 한계:
  - 경로만 보고 뺀다(내용은 #63 · 모든 프로필).
  - 정본의 다른 어휘 후보(#448 등)는 그대로다.
  - 표에 클래스 없이 숨긴 판정은 #63 b 가 «글자 값만» 으로 막고(함수 · 대입 문장), ⓓ#607 후보도 그대로 뜬다.
- 버린 갈래:
  - 몸통 Schema 없는 표만 받기 — #63 과 소유가 겹친다.
  - 정본 AST 대조 뒤 빼기 — #63 과 중복이다.
  - #63 에서 표 클래스 기저를 Schema 로만 받기 — 다른 검사기 판정 변경이라 이 판 범위를 넓힌다. ClassDef 가드 한 줄로 같은 구멍이 닫힌다.
  - 표를 통째로 빼기(v1) — 숨긴 클래스가 blocker 없이 지나간다(중2).
- 크기 S.

#### DEVELOPMENT §3 체크리스트 8 에서 닿는 것

- Codex byte 미러 다섯: check-api-error-controller-contract · check-business-vocabulary · check-naming · check-port-adapter-pairing · business_vocab.
- 골든 · EXPECTED 무변 예상 — 다시 만들어 diff 0 을 확인한다:
  - `findings_count_matrix` · `checker_baseline_matrix` — v2 로 73/73 일치를 확인했다.
  - `checker_cross_matrix --emit-expected` · `construct_drift_report --emit-expected` · `gen_pregate_symbol_kinds`(원본 지문은 바뀜 — 마지막 검사기 고침 뒤에 다시 만든다).
- 봉인 · `make verify`. rulepack 재소성은 필요 없다(그래프 무변).
- 요청 가이드는 바뀔 것 없음.
- 산문:
  - mkrev2 :811 · :454 · :799 + decision-record 되돌림.
  - 트리 명세 :381 · :731 span.

임시물(`c2/`):
- 시제품 `proto/scripts/`.
- 장난감:
  - `op/`(운영자 재현 복사) · `cr/`(검토자 장난감 복사) · `text/toy53` · `v1/`(v1 장난감 복사).
  - 새로 지은 것: `t169x` · `t168m` · `t171mod` · `t179schema`.
  - 복사해 온 git worktree 는 `standalone.sh` 로 홀로 선 저장소로 다시 지음.
- 실행 스크립트: `run3.sh` · `run-vocab-replica.sh` · `run168-replica.sh` · `run-fixtures.sh` · `mut.py`(+ `mut/`) · `edit*.py`.
- 출력: `out/` · `rep/` · `fx/` · `gate/` · `viol/`.

#### v1 → v2 바뀐 것

- **cr 차1**(F4-169 · 차단): #664 자(«확실히 모델인가»)를 판정 셋(모델 / 모델 아님 / 모름)으로 바꿨다.
  - «모델 아님» 만 받는다 — 기저 없음, 또는 끝까지 풀어 모두 모델 아님. 바깥은 `django.db.models` 의 QuerySet · Manager · Choices · TextChoices · IntegerChoices 만이다. 저장소 안 기저는 끝까지 따라가고, 순환은 «모름» 이다. `metaclass=` 같은 키워드도 «모름» 이다.
  - 결과: m1 ~ m5 v1 받음 → v2 막힘(2.38.0 과 같음). 사본 현장 꼴 `[#53] …:15` 는 여전히 풀린다. 새 대조 `t169x` 에서 v1 이 받던 순환 · metaclass 도 막힌다.
- **cr 중2**(F4-179): 표 파일을 #415 에서 빼는 조건에 «ClassDef 하나도 없음» 을 더했다. `op/t179/hidden` v1 0 → v2 2 `[#415]`(2.38.0 과 같음). 몸통 Schema 표 대조 `t179schema` 는 0 이다. 정본 ⓓ#607 빼기는 그대로다.
- **cr 중4**(F4-168): 선택 컨트롤러가 import 묶음으로 가리키는 라우트(이름 import · 모듈 속성)는 helper 분석에 남긴다.
  - `op/t168/t8` v1 0 → v2 2 `#126 :13`(2.38.0 과 같음).
  - 새 `t168m`(모듈 속성 위임)도 같다. 처분 글자(«이름으로 가져온»)보다 한 꼴 넓다 — 모듈 속성 위임도 2.38.0 대비 같은 구멍이라 같은 방향으로 닫았다.
  - 현장 꼴 toyB 는 여전히 0 이다. 사본 공개 · 내부 렌더는 2.38.0 과 byte 동일이다.
- **cr 중5**(F4-171): 뿌리 가림 조건을 `(root/lib/"__init__.py").is_file() or (root/f"{lib}.py").is_file()` 로 좁혔다. `op/t171/nsdir` v1 brew · jwt 2 / 2 → v2 0 / 0. 꾸러미 · 모듈 shadow 대조는 그대로 #396 이다. 게이트는 v2 두 파이썬 모두 green 이다.
- **cr 사7**(F4-169): `from <저장소 안 꾸러미> import models`(상대 포함)를 #53 후보로 넣었다. 바깥 꾸러미(`django.db` · `django.contrib.auth`)는 뺀다. n1 · n2 · q6 받음 → 막힘. 사본 새 붉음은 0 이다(사본 `framework/test` 에 그 꼴 없음).
- **cr 사9**(F4-168): 라우터를 다른 모듈에서 가져온 선택 밖 컨트롤러(t2)의 #126 오탐 남음을 한계 줄에 적었다.
- **text 사1**(F4-169 글): mkrev2 :811 괄호 글을 #664 정의 글(«`models.Model` 을 잇는 클래스 — 추상 · `managed = False` · 프록시 포함 · 출처 무관»)을 빌려 고쳤다. 여기에 «모델인지 알 수 없는 이름(함수 · 재수출 · `*` · 바깥 기저)은 막는다» 를 더했다. :454 표 칸도 맞췄고, 트리 명세 #53(:381) · #415(:731) 행 span(옛 문장 그대로 · 자리 · 새 span 글)을 적었다.
- **cr 좁은 재확인 사소**(F4-169 · 11-15 17:44): 판정 «모름» 이 표준 라이브러리 · 내장 기저까지 막던 것을 고쳤다.
  - «모델 아님» 바깥 고정 목록에 더한 것: `enum` 다섯 · `typing`(NamedTuple · TypedDict · Protocol · Generic) · `abc.ABC` · 내장 `object` 와 예외 70(3.14 글자 목록 · `sys.stdlib_module_names` · 실행 `builtins` 는 안 씀).
  - 함께 고친 것: 첨자 기저는 첨자 앞 클래스로 판정한다. 맨 이름 내장은 `*` import · 맨 위 대입으로 덮이지 않을 때만 내장이다.
  - `cr/t169b` 꼴 14: 첫 v2 는 모델 + 아홉(d ~ l)을 막았고, v2 는 모델 하나만 막는다(exit 2 같음).
  - 모델이 이기는 대조(`t169c` r1 · r2)와 덮인 내장 대조(r7 · r8)는 막힘 그대로다. m1 ~ m5 · n1 · n2 는 그대로다.
  - 사본 vocab 출력은 첫 v2 와 파이썬 넷 모두 byte 동일이다. 변이 «`enum` 줄 걷음» 은 d · e · f 를 막아 죽는다.

## 3. 도메인 우회 읽기 값 출처(R)

### F4-180 — 도메인 우회 읽기 · admin 의 도메인 값은 모델의 `.value` 파생 값 속성 (설계 v2 · r2 · 11-15 17:45)

v1(`r-rule180` · 11-15 15:28) 위에 독립 검토 지적 «맡김 R» 16 건(review-text 중4 · 5 · 6 · 7 · 8 · 사4 · 5 · 6 · 7 · 8 · 10 · review-cr 중3 · 사6(운영자 중요) · 사8 · 사10 · 사11)을 모두 반영한 온전한 절이다. 경로는 `next-pick-1115/r2/` 기준(시제품 `r2/proto/scripts/` · 장난감 · 제안 픽스처 `r2/fixtures-v2/`). 요지: 쓰는 쪽 길 찾기를 `checker_target.reexport_uses` 한 곳으로 옮겨 #356 · #668 이 한 판정을 쓰고(모듈째 사슬 · 꾸러미 `__init__.py` 다시 내보내기 한 단 풀기 · `import *` 같은 판정), `.value` 받음은 글 · 수 주석(`Final[str]` · `Final[int]` · `str` · `int`)인 대입만(글 주석 `"Final[str]"` 은 풀어 봄 · `Final` 만 · 주석 없음 · 다른 타입은 막음), 모델 모듈의 `import *` 씨앗은 출처 모듈의 이름으로 펴고, #356 은 `domain_bypass_query/` 아래 `.py` 전부를 본다. 사본 검사기 27 · 판정 차이 0(#668 61 줄의 글 꼬리만). 좁은 재확인 1(review-cr · 사소 셋)까지 반영. 사용자 결정 불필요.

#### 결정
- 사용자 «나.»(14:56) · 운영자 설계 처리(이의 시 뒤집음): ORM 모델이 도메인 값 목록에서 만든 이름을 우회 읽기 · admin 이 씀 · 두 자리는 계속 도메인을 모름.
- 꼴(처방 하나): 모델 클래스 안 `Final[str]` 파생 값 속성(`STATUS_READY: Final[str] = CashStatus.READY.value`) — 쓰는 쪽 `.filter(status=CashHistoryModel.STATUS_READY)`.
- 운영자 처분(11-15 17:02 · 설계 처리): 모듈 수준 `.value` 이름은 처방이 아니지만 금지도 아님 — 금지 글의 예외는 «VO 멤버의 `.value` 로 묶은 값(모델 클래스 속성 · 모델 모듈 수준 이름)은 거쳐 가져오기가 아니다» 로 검사기와 맞춤(review-text 중6) · 꾸러미 재수출은 이름 풀기라 한 겹 셈 밖(review-text 중7 = review-cr 중3) · `.value` 받음은 `Final[str]` · `Final[int]` 만(review-cr 사6 · 2.38.0 대비 새 구멍이라 중요로 올림).
- 좁은 재확인 1 처분(review-cr · 운영자 · 설계 처리): 받는 주석을 `Final[str]` · `Final[int]` · `str` · `int`(`typing.` · `t.` · `typing_extensions.` 꼴 · 글 주석 포함)로 넓힘 — `str` · `int` 도 mypy 가 값 타입을 지킨다 · `Final` 만은 mypy 가 값 타입을 그대로 추론하므로 막음 · 처방은 `Final[str]` 하나 · 글 주석은 `ast.parse(…, mode="eval")` 로 풀고 풀리지 않으면 막음 · 모델 모듈의 `import *` 씨앗은 출처 모듈의 맨 위 이름(`__all__` 이 있으면 그것)으로 폄.

#### mypy 실측(v1 그대로 · `.venv-probe` mypy 2.4.1 · django-stubs 6.1.2 · Django 6.1 · strict + `mypy_django_plugin` — 사본 `pyproject.toml [tool.mypy]` 도 strict + 같은 플러그인) · `r-rule180/mypy-toy/`
| 꼴 | mypy | 판정 |
|---|---|---|
| ⓐ 함수형 `models.TextChoices("Status", [...])` | `call-overload` · 쓰는 쪽 `no-any-return` | 버림 |
| ⓑ 모델 클래스 안 `STATUS_READY: Final[str] = CashStatus.READY.value` | 0 | **채택** |
| ⓒ 안긴 `class Status(models.TextChoices): READY = CashStatus.READY.value, …title()` | 0 | 버림 — 멤버 목록이 둘째 목록 |
| ⓒ2 라벨 생략 | 0 | 버림 — 자동 라벨이 밑줄 이름에서 달라 AlterField 마이그레이션 |
| ⓓ `Status = CashStatus` 별칭 | 0 | 막음(검사기) |
- ⓑ · ⓒ choices deconstruct 는 내포 꼴과 같아 마이그레이션 없음.
- 주석 `Final[str]` 가 실제 값 타입과 다르면(`Final[str] = RefundPlan.STANDARD.value` 인데 값이 `RefundRule`) strict mypy 가 막는다 — 실측 `r2/mypy-toy/…/models/e_lie_model.py:9` · `:13` `Incompatible types in assignment (expression has type "RefundRule", variable has type "str") [assignment]`(모듈 수준 · 클래스 안 둘 다) · `:18` `LIE_PLAIN: str = …` · `:19` 글 주석 `"Final[str]"` 도 같은 `[assignment]` · `:20` `BARE_RULE: Final = …` 는 오류 0(값 타입을 그대로 추론 — `Final` 만을 막는 까닭). 검사기가 글 · 수 주석만 믿어도 되는 까닭.
- 모델이 도메인 enum 을 import 해 choices 를 만드는 것은 지금도 허용: `check-db-table.py:243-252` `_vo_derivation_path`(#326 예외 D1′) · §2.5 예시 · #9 driven → domain 허용.

#### 고칠 설계 — 검사기
- **공용 판정 `checker_target`(#356 · #668 이 같이 씀)**:
  - `reexport_bindings(mod, seed_of) -> (이름, 클래스.속성)` — 내보내는 쪽. 씨앗(금지 자리에서 import 로 묶은 이름 · 금지 자리는 부르는 검사기가 정함) · 모듈 수준 대입 별칭과 그 속성 · 맨 위 클래스 몸 안 별칭(`Model.Status = CashStatus` → `Model.Status`)을 옮긴다. **받음은 오른쪽이 `.value` 로 끝나고 주석이 글 · 수 타입인 대입만**(`_derived_value` · `_value_annotation` — `str` · `int` · `Final[str]` · `Final[int]` · `<모듈>.Final[…]` · 글 주석 `"Final[str]"` 은 `ast.parse(…, mode="eval")` 로 풀어 같은 판정 · 풀리지 않으면 받지 않음) — 다른 주석(`Final[RefundRule]`) · `Final` 만(mypy 가 값 타입을 그대로 추론) · 주석 없는 `.value` 는 값이 도메인 객체일 수 있어 옮긴다(review-cr 사6 · 좁은 재확인 1). 씨앗의 `import *` 는 부르는 검사기가 **새** `star_names(bc, 마디)`(출처 모듈의 `__all__` 글 목록 · 없으면 `_` 로 시작하지 않는 맨 위 이름 · 모듈을 못 찾으면 빈 집합)로 편다. 한 겹(다른 `django_<bc>/` 모듈에서 가져온 이름은 안 따라감).
  - **새** `reexport_uses(mod, bc, file_parts, bindings) -> [(줄, 이름이 묶인 모듈, 이름(+속성), import 줄인가)]` — 쓰는 쪽(review-text 중7 · review-cr 중3). 길 넷: 이름 가져옴(`from <모듈> import X` · `import *`) · 가져온 클래스의 속성(`Model.Status`) · 모듈째 가져와 속성 사슬(`m.X` · `m.Model.Status` · 하위 모듈을 따라 `mm.sub.Model.Status`). 꾸러미 `__init__.py` 가 자기 `django_<bc>/` 모듈에서 가져와 다시 내보낸 이름은 그 모듈의 이름으로 **한 단** 푼다(이름 풀기 · 한 겹 셈 밖). `import *` 는 들어오는 이름(그 모듈의 묶은 이름 · 꾸러미가 다시 내보낸 이름 · 별칭 단 클래스) 가운데 금지 이름이 있으면 걸고, 들어온 클래스의 속성은 쓰는 자리에서 본다(review-cr 사10 — 두 검사기 같은 판정). 이름이 묶인 모듈로 적으므로 import 꼴(꾸러미 · 모듈 · 상대 · 모듈째)이 달라도 같은 자리 · 같은 목록 칸.
  - 함께 옮김: `module_level`(context-isolation 에서) · `bc_import_target`(context-isolation `_own_target` 과 v1 pap `_bc_target` 을 하나로) · `bc_module_file`(context-isolation `_bc_module_file` · v1 pap `_bc_module`) · `attr_chain`(context-isolation `_attr_chain`).
- **#356 `check-port-adapter-pairing`**: 대상 = `domain_bypass_query/` 아래 `.py` 전부(`_py_files` — 승격 폴더 부품 · `__init__.py` 포함 · review-cr 사8 · #583 · #359 는 그대로 본체만). 막음 — `from …domain_layer… import`(2.38.0) · `import …domain_layer…` · `from application.<bc> import domain_layer` · 상대 · 함수 안 · 공용 `reexport_uses` 가 찾은 한 겹 길 전부. 받음 — 모델 · 모듈의 글 · 수 주석 `.value` 파생 값. 씨앗: `_is_domain_import` 가 `*` 를 내면 출처를 `bc_import_target` 으로 풀어 `star_names` 로 편다(자기 BC 안 모듈만). 판정 글(줄마다 하나): `Thin Read 가 domain_layer 를 {import 한다 | 자기 \`django_<bc>/\` 모듈을 거쳐 가져온다(\`X\`) | … 쓴다(\`M.attr\`)} — 이 길은 도메인을 «안» 거친다(저장된 도메인 상태 칸은 모델이 VO 멤버의 \`.value\` 를 \`Final[str]\` 로 묶은 값 속성으로 거르고 견준다 — implementation-django §2.5)`.
- **#668 `check-context-isolation`**: 쓰는 쪽을 공용 `reexport_uses` 로(직접 금지 자리 import · 다른 BC · BC 밖 탈출 #12 는 그대로). 새로 막음 — 가져온 모델 클래스 안 별칭(`OrderModel.Status` · `m.OrderModel.Status` · `mm.OrderModel.Status` · 꾸러미 `from …models import OrderModel` 뒤 `OrderModel.Status`) · 꾸러미 다시 내보내기로 들어온 금지 이름(`from …models import Money`) · `Final[RefundRule]` 같은 값 객체 속성(클래스 속성 길). 새로 받음 — 모듈 수준 `X: Final[str] = Vo.M.value` · `X: str = Vo.M.value`(2.38.0 은 막았음 · 주석 없는 `.value` · `Final` 만 · 다른 주석은 2.38.0 처럼 막음). 씨앗에 금지 자리의 `import *` 를 넣고 `star_names` 로 폄(모델 모듈이 `from …domain… import *` 면 admin 의 `from <모델 모듈> import *` · `import CashStatus` · `Model.Status` 도 막음 — #356 과 맞춤 · review-cr 사10 · 좁은 재확인 1). 판정 글(파일당 한 줄 · 정렬 목록 칸 그대로)에 처방 꼬리(review-text 사8): `… 단순 자료는 ORM 값(모델 필드 · 모델의 속성 · 메서드)으로 읽고 쓰고(도메인 값 집합의 값으로 거르거나 견줄 때는 모델이 VO 멤버의 \`.value\` 를 \`Final[str]\` 로 묶은 값 속성 — implementation-django §2.5), DB 로 걸 수 없는 …`.
- 검사기 머리 글(두 파일) — #356 · #668 줄을 위 판정과 같은 말로(모듈 수준 이름 · 모델 클래스 안 별칭 · 꾸러미 `__init__` 풀기(겹 아님) · 글 · 수 주석(`Final[str]` · `str` 등) `.value` 값은 거쳐 가져오기가 아님 · 공용 `reexport_uses`) — review-text 중6. 붉은 줄 꼬리는 처방 `Final[str]` 하나만 적는다.
- check-choices-literal-consumption 그대로(날 글 계속 막음).

#### 고칠 설계 — 규칙 글(ttl 고치지 않음 · R-새①②③④ 는 구현 때 다음 빈 번호 · 지금 끝 R-3759 · T 단위 하나와 차례로 채번 · 이름표 넷은 `rulepack_smoke` DRIFT_RE 적중 0(손으로 대 봄))
1. **`implementation-django` §2.5 — 새 블록 `s015-2.5/b6`**(kind-norm · **order 5** · 지금 b5 «소비 규율» 은 order 6 으로 밂 — 새 블록은 다음 미사용 서수 · 선례 `agent-design-architect` s005 b19~b24 · review-text 사4). 글:
   > **모델 쪽 파생 값**: `domain_layer` 를 import 하지 않는 두 driven 자리 — 도메인 우회 읽기 구현(`adapter/persistence/domain_bypass_query/`)과 admin(`django_<bounded_context>/admin/`) — 이 도메인 값 집합의 값으로 거르거나 견줄 때(저장 칸 거르기 · 견주기 · 내보내는 판별 값)는 그 값을 담은 행의 모델 클래스가 VO 멤버의 `.value` 를 `Final[str]` 로 묶은 값 속성을 쓴다 — `STATUS_PENDING: Final[str] = OrderStatus.PENDING.value` · 쓰는 쪽 `.filter(status=OrderModel.STATUS_PENDING)`. 위 `.value` 평탄화와 같은 단일 출처 파생이고 쓰는 값만 둔다. 저장 칸이 아닌 판별 값(조회 결과의 종류 표지 등)도 그 값을 내는 행의 모델이 든다. 함수형 `TextChoices("…", [...])` 파생은 mypy 가 멤버를 보지 못해 쓰지 않는다. 도메인 이름 자체(VO 클래스 · 멤버 — 모델 모듈 수준 이름이든 모델 클래스 안 별칭이든)를 모델을 거쳐 가져오거나 쓰면 그 자리의 import 금지(#356 · #668) 위반이고, 값을 글로 다시 적은 상수(`_PENDING: Final[str] = "pending"`)는 출처가 둘이 되는 위반이다.
   - statesNorm R-새①(Obligation · 이름표 «domain 무의존 driven 자리(도메인 우회 읽기 · admin)가 도메인 값 집합의 값으로 거르거나 견줄 때는 그 행의 모델 클래스가 VO 멤버 .value 를 Final[str] 로 묶은 값 속성») · R-새②(Prohibition · 이름표 «domain 무의존 driven 자리(도메인 우회 읽기 · admin)의 도메인 값 글 사본 상수 금지» — review-text 사5 로 좁힘 · OHS wire `Literal` · 소비 BC · 마이그레이션 historical value 와 안 부딪침).
   - 배선(review-text 중4): `ontology/wiring/implementation-django-final.ttl` — `djr:R-새① djr:delegatedTo <…#a/agent-discipline-reviewer> .` · `djr:R-새② djr:delegatedTo <…#a/agent-discipline-reviewer> .`(R-1183 ~ R-1185 꼴 · 검사기 없음 — #356 · #668 은 R-새③ · R-3757 몫) → `ontology_structural_check.py` ① 무소유 0.
   - 비저장 판별 값(사본 `<BC>/…/<우회 읽기 파일>.py:26-27` `<판별 값>`)은 «그 값을 내는 행의 모델» 이 든다(review-text 사10).
2. **`discipline-cleancode` §2.14**:
   - `s026-2.14/b13` R-1409 새 Expression(짝 규칙) — «… 선언하고 리터럴로 소비하면 위반이다.» 뒤에 «이 BC 안에서 그 심볼을 import 할 수 없는 두 자리(도메인 우회 읽기 · admin — `discipline-houserules` §5)는 모델이 그 심볼에서 파생한 값 속성으로 참조한다(`implementation-django` §2.5 «모델 쪽 파생 값») — 글로 다시 적은 상수는 리터럴 소비와 같다.»(review-text 사5 — «이 BC 안에서 import 할 수 없는 두 자리»).
   - `s026-2.14/b8` R-1399 새 Expression(허용 목록 «정의부 우변» · review-text 중5): 옛 «- Enum·상수 **정의부 자체**의 우변(리터럴의 유일한 서식지)» → 새 «- Enum·상수 **정의부 자체**의 우변(리터럴의 유일한 서식지 — 단 이 BC 안에서 그 집합을 import 할 수 없는 두 자리(도메인 우회 읽기 · admin)가 이미 선언된 집합의 값을 글로 다시 적은 사본 상수는 정의부가 아니다)».
3. **`discipline-houserules` §5 `s018-5/b1`**(한 블록에 목록 전체 · statesNorm R-3423 · R-3757 + **R-새③**):
   - persistence 줄 옛 «- `adapter/persistence/` 아래 셋 — `repository/`·`domain_bypass_query/`·`unit_of_work/`.» → 새 «- `adapter/persistence/` 아래 셋 — `repository/`·`domain_bypass_query/`·`unit_of_work/`. 그 가운데 `domain_bypass_query/` 아래 파일(승격 폴더 부품 포함)은 `domain_layer/` 를 import 하지 않는다(#356 — 이 길은 도메인을 «안» 거친다 · 함수 안 · `import` 꼴 · 상대 import · 꾸러미에서 층 이름을 가져오는 꼴 포함 · 자기 `django_<bounded_context>/` 모듈이 `domain_layer/` 에서 묶은 이름(모듈 수준 이름 · 모델 클래스 안 별칭)을 그 모듈을 거쳐 가져오거나 써도 같다 — 한 겹 · 자기 `django_<bc>/` 아래 꾸러미 `__init__.py`(`models/` 등)가 다시 내보낸 모델 클래스 · 이름은 그 모듈의 것과 같다(이름 풀기 · 겹 아님) · VO 멤버의 `.value` 를 글 · 수 주석(`Final[str]` · `Final[int]` · `str` · `int`)으로 묶은 값(모델 클래스 속성 · 모델 모듈 수준 이름)은 거쳐 가져오기가 아니다). 도메인 값 집합의 값으로 거르거나 견줄 때는 모델 클래스의 그 값 속성을 쓴다(`implementation-django` §2.5).»
   - R-새③ = #356 을 처음 그래프에 싣음: Prohibition · 이름표 «#356 도메인 우회 읽기 구현(domain_bypass_query/ 아래 .py 전부)은 domain_layer import 금지(함수 안·import 꼴·상대·꾸러미 층 이름·자기 django_<bc> 모듈 다시 내보내기 한 겹 포함 · .value 를 글·수 주석으로 묶은 값은 받음)» · alias `djr:alias-rule-356`(`aliasText "rule#356"` · `alias-unique` · `ontology/wiring/aliases.ttl` — rule-668 꼴) · `djr:R-새③ djr:enforcedBy <…#c/check-port-adapter-pairing.py> .`(`ontology/wiring/discipline-houserules-final.ttl` — R-3757 꼴).
   - admin 줄 R-3757 새 Expression: 옛 «…(함수 안 · 상대 import · 그 BC 꾸러미에서 층 이름을 가져오는 꼴 포함 · 자기 `django_<bounded_context>/` 모듈이 그 다섯 자리에서 묶은 이름을 그 모듈을 거쳐 가져와도 같다 — 한 겹). 단순 자료는 ORM 값(모델 필드 · 모델이 가진 속성 · 메서드)으로 읽고 쓰고, DB 제약으로 …» → 새 «…(함수 안 · 상대 import · 그 BC 꾸러미에서 층 이름을 가져오는 꼴 포함 · 자기 `django_<bounded_context>/` 모듈이 그 다섯 자리에서 묶은 이름(모듈 수준 이름 · 모델 클래스 안 별칭)을 그 모듈을 거쳐 가져오거나 써도 같다 — 한 겹 · 자기 `django_<bc>/` 아래 꾸러미 `__init__.py`(`models/` 등)가 다시 내보낸 모델 클래스 · 이름은 그 모듈의 것과 같다(이름 풀기 · 겹 아님) · VO 멤버의 `.value` 를 글 · 수 주석(`Final[str]` · `Final[int]` · `str` · `int`)으로 묶은 값(모델 클래스 속성 · 모델 모듈 수준 이름)은 거쳐 가져오기가 아니다). 단순 자료는 ORM 값(모델 필드 · 모델이 가진 속성 · 메서드)으로 읽고 쓰고(도메인 값 집합의 값으로 거르거나 견줄 때는 모델 클래스의 그 값 속성 — `implementation-django` §2.5), DB 제약으로 …»(괄호는 «거르거나 견줄 때는» 으로 좁혀 새 쓰기 길을 열지 않음 — review-text 사6 · 11-14 결정 «DB 로 못 거는 규칙 쓰기는 창구»). 이름표(R-3757 prefLabel)는 그대로.
4. **`agents/discipline-reviewer.md` `s007/b13`**:
   - R-0968 새 Expression(②): «…비교식(`x.status == "…"`)·`__in` 변종.» 뒤 «도메인 우회 읽기 · admin 이 모델 파생 값 속성 대신 값을 글로 다시 적은 상수(`_READY: Final[str] = "ready"`)로 거르거나 견주면 같은 ② **important** 다(검사기 사각 — `implementation-django` §2.5 «모델 쪽 파생 값»).»
   - R-0978 새 Expression(거짓지적 방지 · review-text 중5): 목록의 «`.value` 평탄화 파생(`default=OrderStatus.PENDING.value`)» 뒤에 «· 모델 파생 값 속성(`OrderModel.STATUS_PENDING`)» · 목록 끝 «…우연히 같은 값·다른 지식의 미통합(합치면 오히려 위반).» 뒤에 «단 도메인 우회 읽기 · admin 이 이미 선언된 값 집합의 값을 글로 다시 적은 상수는 정의부 · 한 파일 로컬이 아니다(②).»
5. **`agents/design-architect.md` `s005/b22`** — R-1711 표현은 그대로 두고 **새 Norm R-새④**(review-text 사7): «도메인 우회 읽기(`domain_bypass_query`) 채택 여부는 명세 결정으로 남긴다.» 뒤 «채택한 우회 읽기 · admin 이 도메인 값 집합의 값으로 거르거나 견주면 그 값을 내는 행의 모델에 둘 `.value` 파생 값 속성(`implementation-django` §2.5 «모델 쪽 파생 값»)을 파일 계획에 함께 적는다 — 두 자리는 `domain_layer` 를 import 하지 않는다(#356 · #668).» · Obligation · 이름표 «채택한 도메인 우회 읽기·admin 이 도메인 값 집합의 값으로 거르거나 견주면 그 모델의 .value 파생 값 속성을 파일 계획에 적음» · b22 statesNorm 에 R-새④ · 배선 `ontology/wiring/agent-design-architect.ttl` `djr:R-새④ djr:delegatedTo <…#a/agent-design-review-ddd>, <…#a/command-dddjango> .`(R-1711 꼴).
6. **트리 명세 · 소유 지도(그래프 밖 산문 · review-text 중8 · 선례 a028918c)**:
   - `workspace/design/2026-08-08-tree-revision-spec.md:669` #356 행 — 옛 «`driven_layer/adapter/persistence/domain_bypass_query/<capability>_query.py`(Thin Read Layer)는 `domain_layer` 를 import 하지 않는다.» → 새 «`driven_layer/adapter/persistence/domain_bypass_query/` 아래 파일(Thin Read Layer — `<capability>_query.py` · 승격 폴더 부품 포함)은 `domain_layer` 를 import 하지 않는다(함수 안 · `import` 꼴 · 상대 import · 꾸러미에서 층 이름을 가져오는 꼴 포함). 자기 `driven_layer/django_<bounded_context>/` 모듈이 `domain_layer` 에서 묶은 이름(모듈 수준 이름 · 대입 별칭 · 모델 클래스 안 대입 별칭)을 그 모듈을 거쳐 가져오거나 써도 같다(한 겹 — #668 과 같은 판정 · 꾸러미 `__init__.py` 가 다시 내보낸 이름은 그 모듈의 이름으로 푼다 · 겹 아님). VO 멤버의 `.value` 를 글 · 수 주석(`Final[str]` · `Final[int]` · `str` · `int`)으로 묶은 값(모델 클래스 속성 · 모델 모듈 수준 이름)은 묶은 이름이 아니다 — 저장된 도메인 상태 칸은 모델 클래스의 그 값 속성으로 거르고 견준다(`implementation-django` §2.5). <span>11-15 · F4-180 — 옛 문장 «`…/domain_bypass_query/<capability>_query.py`(Thin Read Layer)는 `domain_layer` 를 import 하지 않는다.» · 2.38.0 은 본체 파일의 `from …domain_layer… import` 만 봤다 · 처음 그래프 규범(R-새③ · `rule#356`) · 받아들인 한계: 다시 내보내기 한 겹 · 동적 길 · 호출 · 첨자 · 튜플 안 도메인 멤버 · 글 사본 상수는 감수(discipline-reviewer ②).</span>»(등급 `ast` 그대로).
   - 같은 파일 `:1197` #668 행 — «…묶은 이름(`from … import X` · `as` 별칭 · 모듈째 import · 상대 import · 모듈 수준 대입 별칭)을 그 모듈을 거쳐 가져와도 같다(한 겹 — 이름째 · `import *` · 모듈째 가져와 속성으로 쓰는 꼴).» → «…묶은 이름(`from … import X` · `as` 별칭 · 모듈째 import · 상대 import · `import *` · 모듈 수준 대입 별칭 · 모델 클래스 안 대입 별칭)을 그 모듈을 거쳐 가져오거나 써도 같다(한 겹 — 이름째 · `import *` · 가져온 모델 클래스의 속성 · 모듈째 가져와 속성 사슬로 쓰는 꼴 · 꾸러미 `__init__.py` 가 다시 내보낸 이름은 그 모듈의 이름으로 푼다 — 겹 아님). VO 멤버의 `.value` 를 글 · 수 주석(`Final[str]` · `Final[int]` · `str` · `int`)으로 묶은 값(모델 클래스 속성 · 모델 모듈 수준 이름)은 묶은 이름이 아니다.» · «단순 자료는 ORM 값(…)으로 읽고 쓰고,» → «…으로 읽고 쓰고(도메인 값 집합의 값으로 거르거나 견줄 때는 모델 클래스의 그 값 속성 — `implementation-django` §2.5),» · 기존 span 의 받아들인 한계에 «호출 · 첨자 · 튜플 안 도메인 멤버(`Vo["X"]` · `frozenset({Vo.X})`)» 더함 · 새 span «<span>11-15 · F4-180 — 쓰는 쪽 길 찾기를 #356 과 한 판정(`checker_target.reexport_uses`)으로 · 새로 막음: 모델 클래스 안 별칭 · 꾸러미 다시 내보내기 · 값 객체 `.value`(`Final[RefundRule]`) · 새로 받음: 모듈 수준 글 · 수 주석 `.value` 값(2.38.0 은 막았다) · 옛 문장 «…모듈 수준 대입 별칭)을 그 모듈을 거쳐 가져와도 같다(한 겹 — 이름째 · `import *` · 모듈째 가져와 속성으로 쓰는 꼴)».</span>».
   - `workspace/plan/2026-08-11-rule-owner-map.md:308` #356 행 비고(빈 칸) → «11-15 F4-180 — 폴더 아래 .py 전부 · import 꼴 · 꾸러미 층 이름 · 자기 django_<bc> 모듈 다시 내보내기 한 겹(#668 과 같은 판정 `checker_target.reexport_uses`) · `.value` 를 글 · 수 주석으로 묶은 값은 받음 · 처음 그래프(R-새③)» · `:581` #668 행 비고 끝에 «· 11-15 F4-180 — 모델 클래스 안 별칭 · 꾸러미 `__init__` 다시 내보내기 풀기 · 모듈째 사슬(#356 과 한 판정) · `.value` 글 · 수 주석 값은 받음».
   - (선택) `docs/master/mkrev2.py:374` admin 칸 «…단순 자료는 ORM 값(모델 필드 · 모델이 가진 속성 · 메서드)으로 읽고 쓰고,» 뒤에 «도메인 값으로 거르거나 견줄 때는 모델 클래스의 <code>.value</code> 파생 값 속성(<code>STATUS_PENDING: Final[str]</code>)이고,» · `:385` persistence `domain_bypass_query/` 칸 «<b>도메인을 «우회한다» — <code>domain_layer</code> 를 import 하면 위반</b>» 뒤 «<em>모델 모듈을 거쳐 도메인 이름을 가져와도 같다 — 도메인 값은 모델의 <code>.value</code> 파생 값 속성으로 거른다</em>» → `file_tree.html` 재생성(mkrev2 를 돌리면 바뀌는 `workspace/design/2026-08-07-decision-record.md` 는 되돌림). spec_lint · tree_mirror_check 는 행 글을 안 봄.
- 안 바뀜: coder.md · commands/dddjango.md · 요청 가이드 둘 · README · master(선택 mkrev2 빼고).
- Codex 짝(같은 뜻): 손 고침 = `codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md:86`(R-0968 · R-0978) · `codex-dddjango/skills/dddjango-design-architect/SKILL.md:69`(R-새④). byte 복사(`corpus_mirror_sync --write`) = `codex-dddjango/skills/implementation-django/references/final.md` · `dddjango-discipline-cleancode/references/final.md` · `dddjango-discipline-houserules/references/final.md`. graph 절을 고쳤으므로 `workspace/reference/<skill>/reference/final.md` 의 옛 절을 손으로 바꾼 뒤 `--write` → `--check`(체크리스트 5 · 11-13 교훈 · review-text 사3 — 계획 공용).

#### 시제품 `r2/proto/scripts/`(2.38.0 `rel/` 복사 위)
| 파일 | v1 | v2 | 요지 |
|---|---|---|---|
| `checker_target.py` | +44 −0 | +220 −0 | `module_level` · `bc_import_target` · `bc_module_file` · `_django_parts` · `_django_module` · `attr_chain` · `_value_annotation`(`str` · `int` · `Final[str]` · `Final[int]` · `<모듈>.Final` · 글 주석 풀기) · `_derived_value` · **`star_names`**(별표 씨앗 펴기) · `_name_root` · `reexport_bindings` · **`reexport_uses`**(쓰는 쪽 길 넷 · 꾸러미 한 단 풀기 · `import *` 판정) |
| `check-context-isolation.py` | +41 −40 | +40 −106 | `_own_target = checker_target.bc_import_target` · `_module_level` 별칭 · `_bc_module_file` · `_attr_chain` · `_name_root` 지움 · `_admin_reexports` 씨앗만(`import *` 씨앗 넣고 `star_names` 로 폄) · `_scan_admin_imports` 는 직접 금지 자리 · 다른 BC · #12 만 보고 다시 내보내기는 `reexport_uses` · 판정 글 처방 꼬리 · 머리 글 |
| `check-port-adapter-pairing.py` | +101 −5 | +53 −5 | `_is_domain_import`(`bc_import_target`) · `_bypass_domain_uses`(바로 import + `reexport_uses` · 씨앗 `import *` 는 `star_names` 로 폄) · #356 고리를 `_py_files(thin)` 로 따로 · 판정 글 · 머리 글 |
- `checker_lint --scripts-dir` rel = v2(exit 0 · 위반 0 · `#357` 앵커 그대로). 사본 CPU 시간(`/usr/bin/time -p` user · 부하 평균 35 라 벽시계는 안 믿음): context-isolation rel 19.6 · v1 14.3 · v2 17.7 s · port-adapter-pairing rel 29.8 · v2 26.3 s — 느려짐 없음. 다른 검사기 24 개 무변(장난감 18 꼴 · rel · v1 · v2 셋 모두 #356 · #668 두 검사기 밖 출력 byte 같음).
- 기존 변이 지점: `fixture_matrix` MUTATIONS 가운데 세 파일을 겨눈 38 개 중 35 개는 v2 에서도 한 곳에 맞음 · **3 개는 글이 `checker_target` 으로 옮겨 다시 겨눔**(아래 시험) · `field_report_checker_smoke` `_MUTATIONS` 107 가운데 세 파일 지점 94 개 모두 한 곳.

#### 장난감 전 / 후 — 명령 · exit(`pap` = check-port-adapter-pairing · `ci` = check-context-isolation)
① v1 장난감 18 꼴(`r2/run_cases.sh <scripts> r2/cases-{rel,v1,v2}` · 검사기 27 · `python3 -B r2/summ.py r2/cases-rel r2/cases-v1 r2/cases-v2`) — v2 판정은 v1 과 18 꼴 모두 같음(글만 #356 꼬리 · #668 꼬리):
| 꼴 | 2.38.0 | v1 | v2 |
|---|---|---|---|
| a_domain · i_local(대조군) | pap 2 | 2 | 2 |
| a2_plain · c1_reexport · f_alias · g_modalias | 0 | pap 2 | pap 2 |
| h_pkg | ci 2(#9) | pap 2 · ci 2 | pap 2 · ci 2 |
| e_value · b_final · adm_iv_final · adm_v_value | 0 | 0 | 0 |
| d_literal(대조군) | choices-literal 2 | 같음 | 같음 |
| adm_i_domain · adm_ii_reexport(대조군) | ci 2 | ci 2 | ci 2 |
| adm_iii_alias · adm_vi_modclass | 0 | ci 2 | ci 2 |
| adm_vii_modvalue(모듈 수준 `Final[str]` `.value`) | ci 2 | 0 | 0(의도한 받음) |

② 검토자 · 운영자 장난감(`r2/op-rev/run_r180.sh <scripts> r2/op-rev/r180-{rel,v1,v2} r2/review-cr/r180/cases-all.txt` — `review-cr/r180` 입력 11 꼴 + 새 16 꼴 · `cases-star.txt` 2 꼴):
| 꼴(b = 우회 읽기 #356 · a = admin #668) | 2.38.0 | v1 | v2 |
|---|---|---|---|
| b/a_mod_class_alias(모듈 경로 클래스 별칭) | 0 / 0 | 2 / 2 | 2 / 2 |
| **b/a_pkg_class_alias**(꾸러미 `from …models import CashHistoryModel` + `.Status`) — text 중7 · cr 중3(a) | 0 / 0 | **0 / 0** | **2 / 2** |
| b/a_pkg_rel_class(꾸러미 `__init__` 상대 재수출) | 0 / 0 | 0 / 0 | 2 / 2 |
| b/a_pkg_vo(꾸러미가 다시 내보낸 `CashStatus`) | 0 / 0 | 0 / 0 | 2 / 2 |
| **b_pkgmod_chain**(`mm.cash_history_model.CashHistoryModel.Status`) — cr 중3(b) | 0 | **0**(a 는 2) | **2** |
| b/a_pkgmod_class(`mm.CashHistoryModel.Status`) | 0 / 0 | 0 / 0 | 2 / 2 |
| b/a_pkg_star(꾸러미 `import *` + `.Status`) | 0 / 0 | 0 / 0 | 2 / 2 |
| **a_policy_value**(`STANDARD_RULE: Final[RefundRule] = ….value`) — cr 사6 대조군 | **2** | **0** | **2** |
| b_policy_value | 0 | 0 | 2 |
| b/a_policy_class_attr(`CashHistoryModel.STANDARD_RULE`) | 0 / 0 | 0 / 0 | 2 / 2 |
| b/a_noann_value(주석 없는 `.value`) | 0 / 2 | 0 / 0 | 2 / 2 |
| b/a_pkg_value_ok(꾸러미 + `STATUS_READY` `Final[str]`) | 0 / 0 | 0 / 0 | 0 / 0 |
| b/a_mod_star_use(`import *` + `.Status`) | 0 / 2 | 2 / 2 | 2 / 2(a 목록 칸에 `….CashHistoryModel.Status` 더함) |
| b/a_mod_star_nouse(`import *` · 모델 모듈에 도메인 이름 있음) | 0 / 2 | 2 / 2 | 2 / 2 |
| **b/a_star_domain**(모델 모듈이 `from …domain… import *` · 쓰는 쪽 `import *`) — cr 사10 | 0 / 0 | **2 / 0** | **2 / 2**(맞춤) |
| b_subscript(`CashStatus["READY"]` — cr 사11) | 0 | 0 | 0(한계) |
③ 좁은 재확인 1(review-cr · 검토자 입력 `review-cr/r180/{m,v,a}` 의 `fv_*` · `star_seed*` 를 `r2/review-cr/r180/` 로 복사 · `cases-fix.txt` 23 꼴 · `r2/op-rev/run_r180.sh <scripts> r2/op-rev/r180b-{rel,v1,v2a,v2} r2/review-cr/r180/cases-all2.txt` — 52 꼴 · v2a = 재확인 전 v2 `r2/proto-v2a/` · v2 = 지금 · 표기 pap/ci exit):
| 꼴 | 2.38.0 | v1 | v2a | v2 |
|---|---|---|---|---|
| **a_fv_str**(클래스 `STATUS_READY: str = ….value` · admin) | 0/0 | 0/0 | **0/2** | **0/0** |
| a_fv_str_mod(모듈 `CASH_READY: str`) | 0/2 | 0/0 | 0/2 | 0/0(모듈 수준 받음) |
| **b_fv_str** · **b_fv_string**(글 주석 `"Final[str]"`) | 0/0 | 0/0 | **2/0** | **0/0** |
| b_fv_final · b_fv_int · b_fv_typing · b_fv_t · b_fv_te · b_fv_nofuture | 0/0 | 0/0 | 0/0 | 0/0 |
| a_fv_final(모듈 `Final[str]`) | 0/2 | 0/0 | 0/0 | 0/0 |
| b_fv_bare · a_fv_bare(`Final` 만) — 대조군 | 0/0 · 0/2 | 0/0 · 0/0 | 2/0 · 0/2 | 2/0 · 0/2 |
| b_fv_noann · a_fv_noann(주석 없음) | 0/0 · 0/0 | 0/0 · 0/0 | 2/0 · 0/2 | 2/0 · 0/2 |
| a_policy_value(`Final[RefundRule]`) — 대조군 | 0/2 | 0/0 | 0/2 | 0/2 |
| **b_star_seed** · **a_star_seed**(모델 `from …cash_status import *` + `Status = CashStatus` · 쓰는 쪽 `import CashHistoryModel, CashStatus` + `.Status`) | 0/0 · 0/0 | 0/0 · 0/0 | 0/0 · 0/0 | **2/0 · 0/2** |
| b/a_star_seed_star(같은 모델 · 쓰는 쪽 `import *`) | 0/0 · 0/0 | 2/0 · 0/0 | 2/0 · 0/2 | 2/0 · 0/2 |
| b/a_star_final · b/a_star_all(`__all__`) | 0/0 · 0/2 | 2/0 · 0/2 | 2/0 · 0/2 | 2/0 · 0/2 |
- 52 꼴 가운데 v2a ↔ v2 다른 것은 위 굵은 여섯뿐(46 같음 · `r2/r180b-summary.txt`). v1 장난감 18 꼴(`r2/cases-v2b`)은 v2a 와 판정 같고 두 검사기 밖 출력 byte 같음.
- 운영자 재현 `op-rev/pkgtoy`(꾸러미) · `pkgtoy-mod`(모듈 경로) · 검토자 `review-text/pkgtoy`(`r2/run_pkgtoy.sh`): 2.38.0 모두 0 · v1 꾸러미 둘 0 / 모듈 경로 pap 2 · ci 2 · **v2 셋 모두 pap 2(`cash_history_query.py:10`) · ci 2(`['…models.cash_history_model.CashHistoryModel.Status']` — 꾸러미 · 모듈 경로가 같은 목록 칸)**.
- 승격 폴더 부품(검토자 `promoted_part` + 폴더 바로 밑 도우미 · `r2/run_promoted.sh` · cr 사8): 2.38.0 exit 0 · v1 exit 0 · **v2 exit 2** `[#356] …/cash_history_query/open_statuses.py:3 import 한다` · `[#356] …/helper_in_folder_root.py:3 import 한다`.
- 기존 픽스처 9(`r2/run_fix.sh` · rel 대 v2): context_isolation good · cross_bad · cross_good · app_exception · port_adapter_pairing good · skeleton_placeholder 차이 0 · admin_imports 17 줄 · bad_rules 1 줄(#668 글 꼬리만) · port_adapter_pairing/bad_rules 1 줄(#356 글 꼬리만) — 글을 걷고 견주면(파일 · 목록 칸) 셋 모두 차이 0.

#### 사본 재측정(`r2/run_copy.sh` · `리허설 사본` 읽기만 · 검사기 27 · 2.38.0 대 v2)
- 27 개 exit 같음(`check-api-error-controller-contract` 는 필수 인자 없어 두 판 exit 1 — 비교 밖) · **출력 차이는 check-context-isolation 한 파일 122 줄 = #668 61 줄의 글 꼬리(처방 꼬리 — review-text 사8)뿐** · 글을 걷고 파일 · 목록 칸으로 견주면 **0 줄**(61 줄 61 파일 · 목록 칸 바뀐 줄 0 — G2 앵커 재실행도 같은 검사기라 차분 안 닿음) · 나머지 26 검사기 byte 같음 · #356 0 → 0(이제 `domain_bypass_query/` 아래 `.py` 40 개 — 본체 15 · `__init__.py` 25 — 를 봄 · 부품 모듈 0) · **새 붉음 0**.
- 까닭(v2 판정 함수로 다시 셈): 사본 `django_<bc>/models/` 아래 `.py` 142 · 도메인 이름을 묶은 파일 53 · 클래스 안 도메인 별칭 0 · 글 · 수 주석 `.value` 대입 0 · admin · 우회 읽기 파일의 꾸러미 꼴 import 0(모듈 경로 꼴만 · 꾸러미 `__init__.py` 를 가리키는 import 는 사본 전체에서 시험 파일 2 곳뿐 — `<BC>/test/integration/` 의 admin 꾸러미) · `models/__init__.py` 25 개(빈 것 2 · 재수출 줄 상대 31 · 절대 85 · `import *` 0) — 꾸러미 풀기 길은 이 사본에서 붉음을 내지 않음. 브리프의 «꾸러미 import 5 곳» 은 이 사본에서 같은 뜻의 자리를 찾지 못함(위 셈이 이 사본의 실측).
- **좁은 재확인 1 뒤 다시 잼(`copy-v2b`)**: 2.38.0 대 v2 — 27 개 exit 같음 · 차이는 그대로 check-context-isolation 122 줄(#668 61 줄 꼬리 글 — 꼬리가 `Final[str]` 하나로 바뀌어 v2a 와도 122 줄) · 글을 걷으면 0 줄 · 나머지 26 byte 같음 · #356 0 · **새 붉음 0**. 사본 `django_<bc>/` 아래 `import *` 0 · 주석 단 `.value` 대입 0 이라 받는 주석 넓힘 · 별표 씨앗 펴기는 사본에 닿지 않음.
- 2.38.0 사본 출력은 v1 재측정(`r-rule180/copy-rel`)과 byte 같음(사본 무변 확인). 명령: `./run_copy.sh "$PWD/../rel/dddjango/scripts" "$PWD/copy-rel"` · `./run_copy.sh "$PWD/proto/scripts" "$PWD/copy-v2b"`(`r2/` 에서 · 각 약 7 분).

#### 시험
- 새 픽스처 `workspace/eval/fixtures/port_adapter_pairing/bypass_domain/`(초안 `r2/fixtures-v2/…`): VO `order_status.py` · **`refund_plan.py`(`RefundRule` 값 객체 · `RefundPlan(Enum)`)** · 모델 모듈(`PENDING_VALUE: Final[str]` · **`STANDARD_RULE: Final[RefundRule]`** · `Kind = OrderStatus` · 클래스 안 `STATUS_PENDING: Final[str]` · **`STANDARD_REFUND: Final[RefundRule]`** · `Status` 별칭 · **재확인 1: 클래스 안 `STATUS_SHIPPED: "Final[str]"`(글 주석) · `STATUS_PLAIN: str` · 모듈 `BARE_PENDING: Final`(`Final` 만)**) · **`models/__init__.py` 재수출(`from .order_model import Kind as Kind` · `OrderModel as OrderModel`)** · **재확인 1: `models/star_seed_model.py`(`from …order_status import *` · 클래스 안 `Status = OrderStatus`)**. 레인 `^\[#356\]` **17 줄**: **`bare_final_query.py:1`(`BARE_PENDING`)** · `class_alias_query.py:6` · `import_plain_query.py:1` · `local_relative_query.py:6` · `module_class_alias_query.py:6` · **`package_chain_query.py:6`** · **`package_class_alias_query.py:6`** · `package_layer_query.py:1` · **`package_module_class_query.py:6`** · **`package_name_query.py:1`(`Kind`)** · **`policy_value_query.py:1`(`STANDARD_RULE`)** · **`policy_value_query.py:6`(`OrderModel.STANDARD_REFUND`)** · **`promoted_part_query/open_statuses.py:1`** · `reexport_module_query.py:6` · `reexport_name_query.py:1` · **`star_seed_query.py:1`(`OrderStatus`)** · **`star_seed_query.py:6`(`StarSeedModel.Status`)** · 녹색 `derived_value_query`(`STATUS_PENDING` · `PENDING_VALUE` · **`STATUS_SHIPPED` 글 주석 · `STATUS_PLAIN` `str`**) · `model_only_query` · **`package_derived_value_query`** · **`promoted_part_query/promoted_part_query.py`**. 2.38.0 은 1 줄(`local_relative_query.py:6`) · v1 7 줄 · v2(재확인 전) 17 줄(`derived_value_query` 의 글 주석 · `str` 두 줄이 붉고 별표 씨앗 두 줄이 없음).
- `context_isolation/admin_imports` 더함(초안 `r2/fixtures-v2/…`): VO `order_status.py` · **`refund_plan.py`** · `order_model.py` 에 `PENDING_VALUE` · **`STANDARD_RULE`** · 클래스 안 `STATUS_PENDING` · **`STANDARD_REFUND`** · `Status` · **재확인 1: `STATUS_SHIPPED: "Final[str]"` · `STATUS_PLAIN: str` · 모듈 `BARE_PENDING: Final`** · **`models/__init__.py`(`Money` · `OrderModel` 재수출)** · **재확인 1: `models/star_seed_model.py`** · 기능 열: 붉음 `reexport_class_alias` · `reexport_module_class_alias`(v1) · **`reexport_package_class_alias`** · **`reexport_package_name`(`['…order_model.Money']`)** · **`reexport_package_chain`** · **`reexport_package_module_class`**(셋 `['…order_model.OrderModel.Status']`) · **`policy_value`(`['…order_model.OrderModel.STANDARD_REFUND', '…order_model.STANDARD_RULE']`)** · **재확인 1: `bare_final`(`['…order_model.BARE_PENDING']`) · `star_seed`(`['…star_seed_model.OrderStatus', '…star_seed_model.StarSeedModel.Status']`)** · 녹색 `derived_value`(`STATUS_PENDING` · **`STATUS_SHIPPED` · `STATUS_PLAIN`**) · `module_value`(v1) · **`package_derived_value`**. 레인 `^\[#(668|12|13)\]` 19 → **28 줄**(기존 19 줄 판정 그대로 · `_M668` 글 꼬리만). 2.38.0 은 같은 픽스처에서 22 줄(`module_value` · `policy_value` · `bare_final` 의 모듈 수준 셋) · v2(재확인 전) 28 줄(`derived_value` 붉음 · `star_seed` 없음).
- `fixture_matrix.py`: 레인 둘(새 `port_adapter_pairing/bypass_domain` · `admin_imports` 기대 28) · `_M668` 글(처방 꼬리) · `context_isolation/bad_rules #668` 기대 글. MUTATIONS — **옛 셋 다시 겨눔**(글이 `checker_target.py` 로 옮김 · 검사기 `_CI`): «F4-158 #668 다시 내보내기 한 겹 끔» `                hit = name_hit(base, a.name)\n` → `                hit = None\n` · «… 속성 길 끔(N8)» `        for cut in range(len(chain) - 1, 0, -1):` → `        for cut in ():` · «… import * 끔(셋째 확인)» `                    if any(name_hit(base, n) for n in star):` → `                    if False:`. **새 17**: #356 Import 꼴 끔 · #356 꾸러미 층 이름 끔 · **#356 폴더 전체 범위 걷음**(`for py in _py_files(thin):  # #356` → `slot_glob(thin, "*_query.py")`) · 한 겹 이름 길 끔(→ #356) · 클래스 속성 길 끔(→ #356 · → #668) · 모듈째 속성 길 끔(→ #356) · **모듈째 사슬 하위 모듈 따라가기 끔**(`cur = cur + (attr,)` → `break` · → #356 · → #668) · **꾸러미 `__init__` 다시 내보내기 풀기 끔**(`return [(parts, name)] + ([origin] …)` → `return [(parts, name)]` · → #356 · → #668) · `.value` 파생 받음 걷음(`    return (isinstance(stmt, ast.AnnAssign)` → `    return False and (…` · → #356 · → #668) · **글 · 수 주석 거름 걷음**(`    return isinstance(inner, ast.Name) and inner.id in _DERIVED_VALUE_TYPES` → `    return True` · → #356 · → #668) · **글 주석 풀기 걷음**(`ann = ast.parse(ann.value, mode="eval").body` → `return False` · → #356 · → #668) · **`Final` 벗기기 걷음**(`inner: ast.expr = ann.slice if final else ann` → `= ann` · → #356 · → #668) · **맨 `str` · `int` 받음 걷음**(같은 줄 → `ann.slice if final else ast.Constant(None)` · → #356 · → #668) · **별표 씨앗 펴기 끔**(공용 `star_names` 의 `mod: … = ast.parse(…)` → `mod = None` · → #356 · → #668 · 부르는 자리 #356 `return seeds | (checker_target.star_names(…) …)` → `return seeds` · #668 `seeds |= checker_target.star_names(bc, base)` → `pass`) · 클래스 몸 별칭 끔(→ #356 · → #668). 모두 **새 27 + 옛 3 = 30**. `r2/mutate2.py`(v2 사본에 손으로 하나씩 걸고 제안 픽스처 v2 레인을 돎)로 **30 개 모두 죽음**(exit 0 · 예: 꾸러미 풀기 끔 #356 17 → 14 · #668 28 → 25 · 글 · 수 주석 거름 걷음 17 → 14 · 28 → 26 · 글 주석 풀기 걷음 17 → 18 · 28 → 29 · 맨 `str` 받음 걷음 17 → 18 · 28 → 29 · 별표 씨앗 끔 17 → 15 · 28 → 27 · 폴더 범위 걷음 17 → 16).
- `field_report_checker_smoke.py` F4-180 클래스: 레인 꼴 `Final` 글 사본 → 0 · 도메인 import → #356 · `Final[str]` `.value` 파생 → 0 · 클래스 별칭 → #356 · **꾸러미 `from …models import CashHistoryModel` + `.Status` → #356 · #668** · **`mm.cash_history_model.CashHistoryModel.Status` → #356 · #668** · **`Final[RefundRule]` `.value` → #356 · #668** · **승격 폴더 부품 domain import → #356** · **모델 모듈 `import *` 도메인 · 쓰는 쪽 `import *` → #356 · #668** · **재확인 1: 모델 모듈 `import *` 도메인 · 쓰는 쪽 `from <모델 모듈> import CashStatus` · `Model.Status` → #356 · #668 · `str` · `int` · `t.Final[str]` · `typing_extensions.Final[str]` · 글 주석 `"Final[str]"` `.value` → 0 · `Final` 만 · 주석 없음 → #356 · #668**.
- `findings_count_matrix.py` EXPECTED: check-context-isolation(bad_rules — #668 글 꼬리) · check-port-adapter-pairing(bad_rules — #356 글 꼬리) 지문 해시만(셈 `#668×1` · `#356×1` 그대로). `construct_drift_report --emit-expected` — context-isolation 대표 red 레인 stdout(#668 글) · port-adapter-pairing 대표 레인에 #356 줄이 있으면 그 글. `checker_baseline_matrix`(셈 무변 예상) · `checker_cross_matrix` · `gen_pregate_symbol_kinds`(이번 고침에 뽑는 리터럴 없음) 무변 예상 — 다시 지어 확인. 그래프 바뀜 → `ontology_render.py --apply` · `make rulepack` + Codex · `rulepack_smoke` G12(이름표 넷 DRIFT_RE 적중 0) · 봉인 → `make verify` + `make verify-mutation`. registry_gate_smoke · anchor_diff_smoke 닿지 않음.
- 체크리스트 8: Codex byte 미러 셋(`codex-dddjango/skills/dddjango/scripts/{checker_target,check-context-isolation,check-port-adapter-pairing}.py`) → 골든 · EXPECTED → 봉인 → verify.

#### 남는 한계
- 글 사본 상수(`_READY: Final[str] = "ready"`)는 검사기 밖(discipline-reviewer ② · R-0978 거짓지적 방지 예외 고침) · check-choices-literal 그대로.
- 호출 · 첨자 · 튜플 안 도메인 멤버(`READY_MEMBER = CashStatus["READY"]` · `frozenset({CashStatus.READY})` · `Model.ready()`)는 옮긴 이름으로 안 봄(옛 한계 · 두 판 0 · review-cr 사11).
- 받지 않는 주석(막는 쪽): `Final` 만 · 주석 없음 · 풀리지 않는 글 주석 · 안쪽까지 글인 `Final["str"]` · `builtins.str` · `Optional[str]` 같은 다른 꼴(규칙 글 처방은 `Final[str]` 하나).
- 별표 씨앗 펴기는 출처가 자기 BC 안 모듈일 때만(`bc_import_target` 으로 풀림) · 다른 BC · 바깥 모듈의 `import *` 는 `*` 만 씨앗(쓰는 쪽 `import *` 만 걸림) · `__all__` 은 글 목록 대입일 때만(`+=` · 함수로 짓는 꼴은 안 봄 — 맨 위 이름으로 폄) · 출처가 다시 `import *` 를 하면 한 단만.
- 클래스 몸의 주석 없는 `.value`(`STATUS_READY = CashStatus.READY.value`)를 admin 이 `Model.STATUS_READY` 로 쓰면 2.38.0 대비 새 붉음(장난감 `a_fv_noann` 0 → 2) — 2.38.0 은 클래스 몸을 안 봤다 · houserules «모든 이름의 첫 대입에 타입 어노테이션» 이 이미 요구하는 꼴이라 막는 쪽으로 둠(사본 0).
- 꾸러미 풀기는 한 단 · 꾸러미 `__init__.py` 의 `from .x import *` 재수출은 안 풂(사본 `models/__init__.py` 25 개 · `import *` 재수출 0).
- 한 겹은 `django_<bc>/` 모듈만(저장소 · 리포지토리 구현 모듈을 거친 다시 내보내기 안 봄) · 이름 가림(`for m in …` 로 별칭을 덮음)은 안 봄.
- `import *` 뒤 들어온 클래스의 속성은 쓰는 자리에서 봄 — `getattr` 같은 동적 길은 못 봄.
- 저장 칸 아닌 판별 값(사본 `<BC>/…/<우회 읽기 파일>.py:26-27` `<판별 값>`)은 규칙 글로 덮이나 검사기 밖 · 옛 코드는 grandfather.

#### 버린 갈래
- 함수형 파생 TextChoices(mypy) · 안긴 파생 TextChoices + choices 교체(둘째 목록 · 자동 라벨 마이그레이션) · VO enum import 만 허용(#356 목적 바뀜 · admin 결정과 갈림) · 모델 매니저 · 메서드로 거르기 옮김(평면 모델에 판정 · architecture-ddd §3.2) · #356 · #668 따로 구현(같은 판정 둘 어긋남 — v1 에서 내보내는 쪽만 묶어 쓰는 쪽이 갈렸다 → v2 는 쓰는 쪽까지 `reexport_uses` 하나).
- 꾸러미 재수출을 받아들인 한계로 두기(review-text 중7 의 다른 방향) — 표준 트리가 `models/__init__.py` 재수출을 요구해(mkrev2:370) 꾸러미 꼴이 표준 꼴이라 버림.
- `.value` 받음에 값 타입 추론(enum 멤버 값 리터럴을 따라가 str · int 인지 봄) — 글 · 수 주석은 mypy strict 가 지키므로 주석만 봄(사본 domain 열거 281 중 글자 · 숫자 아닌 멤버 0 · review-cr `scan_enum_values.py`).
- 꾸러미 풀기를 `models` 이름에만 — 이름 풀기는 꾸러미 `__init__.py` 일반의 뜻이라 이름을 붙이지 않음(사본 `admin/__init__.py` 의 panel 재수출은 금지 이름을 안 묶어 영향 0).

#### 맡을 파일
- 검사기: `dddjango/scripts/checker_target.py` · `check-context-isolation.py` · `check-port-adapter-pairing.py` + Codex 미러 셋.
- 그래프: `ontology/rules/{implementation-django-final,discipline-cleancode-final,discipline-houserules-final,agent-discipline-reviewer,agent-design-architect}.ttl` · `ontology/wiring/{aliases,discipline-houserules-final,implementation-django-final,agent-design-architect}.ttl` · `ontology/ISSUED` · `LEDGER.tsv`(재기준선 · 새 블록 `s015-2.5/b6`) · 계수 기대표.
- 투영: `dddjango/skills/{implementation-django,discipline-cleancode,discipline-houserules}/references/final.md` · `dddjango/agents/{discipline-reviewer,design-architect}.md` · Codex 짝(손 둘 · byte 셋) · `workspace/reference` 미러 · rulepack + Codex.
- 산문: `workspace/design/2026-08-08-tree-revision-spec.md`(:669 · :1197) · `workspace/plan/2026-08-11-rule-owner-map.md`(:308 · :581) · (선택) `docs/master/mkrev2.py`(:374 · :385) → `docs/master/file_tree.html`.
- 픽스처: `port_adapter_pairing/bypass_domain/`(새) · `context_isolation/admin_imports/`(더함).
- 도구: `fixture_matrix.py`(레인 둘 · `_M668` · 변이 옛 셋 다시 겨눔 + 새 27) · `field_report_checker_smoke.py` · `findings_count_matrix.py` + EXPECTED 도구 · `rulepack_smoke.py`(G12 — 적중 0 이면 무변) · 봉인.
- 겹침: `checker_target.py`(모든 검사기 import — R 덩이 먼저 넣고 전 검사기 시험) · `check-port-adapter-pairing.py`(C 단위 F4-171 죽은 인자 `tech` — v2 는 #356 고리를 `_py_files(thin)` 따로 돌리므로 C 덩이와 겹치는 줄 다시 볼 것) · `fixture_matrix.py` · `findings_count_matrix.py` · rulepack · 그래프 ttl · R-번호 차례(R 넷 + T 하나).

#### 크기 · 사용자 결정
- L(검사기 셋 · 공용 모듈 +220 · 새 Norm 4 + 표현 5 고침(R-1409 · R-1399 · R-3757 · R-0968 · R-0978) + 새 블록 1 · 배선 넷 · 산문 둘(+선택 하나) · 픽스처 둘 · 변이 옛 3 다시 겨눔 + 새 27). 사용자 결정 불필요(방향 = 14:56 처리 · 꼴 = mypy 실측 + §2.5 «`.value` 평탄화» · 모듈 수준 `.value` 받음 · 글 · 수 주석 좁힘 · 꾸러미 풀기는 운영자 처분 17:02 · 받는 주석 넓힘 · 글 주석 · 별표 씨앗은 좁은 재확인 1 처분).

#### v1 → v2 바뀐 것
- text 중4 — R-새①② 배선 `ontology/wiring/implementation-django-final.ttl` delegatedTo `agent-discipline-reviewer` 를 규칙 글 1 · 맡을 파일에.
- text 중5 — R-0978 새 Expression(«단 … 사본 상수는 정의부 · 한 파일 로컬이 아니다(②)» · 모델 파생 값 속성은 거짓지적 방지) · §2.14 b8 R-1399 새 Expression «사본은 정의부가 아니다»(두 자리로 좁힘).
- text 중6 — 처방은 모델 클래스 속성 하나 · 금지 글 예외 «VO 멤버의 `.value` 를 글 · 수 주석(`Final[str]` · `Final[int]` · `str` · `int`)으로 묶은 값(모델 클래스 속성 · 모델 모듈 수준 이름)은 거쳐 가져오기가 아니다» 를 houserules 두 줄 · 트리 명세 두 행 · 검사기 머리 글 둘에 맞춤.
- text 중7 = cr 중3 — 쓰는 쪽 길 찾기를 `checker_target.reexport_uses` 로 옮김(꾸러미 `__init__` 한 단 풀기 · 모듈째 사슬) · 장난감 꾸러미 꼴 0 → 2 · 두 픽스처에 재수출 `__init__` · 변이 «꾸러미 풀기 끔» · «사슬 하위 모듈 끔» · «한 겹» 글에 꾸러미 한 줄.
- text 중8 — 트리 명세 :669 · :1197 행 글 + span · 소유 지도 :308 · :581 비고 · (선택) mkrev2 :374 · :385.
- text 사4 — §2.5 새 문단을 새 블록 `s015-2.5/b6`(order 5 · b5 → order 6).
- text 사5 — R-새② 이름표 «domain 무의존 driven 자리(도메인 우회 읽기 · admin)의 …» · §2.14 «이 BC 안에서 그 심볼을 import 할 수 없는 두 자리».
- text 사6 — admin 줄 괄호 «거르거나 견줄 때는» 으로 좁힘(읽고 쓰고 → 거르거나 견줄 때).
- text 사7 — architect 문장을 R-1711 표현 고침이 아니라 새 Norm R-새④ · 배선 `agent-design-architect.ttl` delegatedTo `agent-design-review-ddd` · `command-dddjango`.
- text 사8 — #668 판정 글에 #356 과 같은 처방 꼬리.
- text 사10 — §2.5 새 블록에 «저장 칸이 아닌 판별 값도 그 값을 내는 행의 모델이 든다».
- cr 사6(운영자 중요) — `_derived_value`: 주석 `Final[str]` · `Final[int]` + `.value` 만 받음 · a_policy_value 2.38.0 2 · v1 0 · v2 2 · 픽스처 `policy_value` 둘 · 변이 «Final 주석 거름 걷음» · 규칙 글 · 판정 글에 `Final[str]` · `Final[int]`(좁은 재확인 1 에서 받는 주석을 글 · 수 주석으로 넓힘 — 아래).
- cr 사8 — #356 을 `domain_bypass_query/` 아래 `.py` 전부로(`_py_files`) · 장난감 승격 부품 0 → 2 · 픽스처 `promoted_part_query/` · 변이 «폴더 범위 걷음» · 사본 #356 0 → 0(40 파일).
- cr 사10 — `import *` 판정을 `reexport_uses` 하나로(들어오는 이름 중 금지 이름 · 클래스 속성은 쓰는 자리) · #668 씨앗에 금지 자리 `import *` · star_domain 꼴 v1 갈림(2 / 0) → v2 맞춤(2 / 2).
- cr 사11 — 호출 · 첨자 · 튜플 안 도메인 멤버를 남는 한계에.
- **좁은 재확인 1(review-cr · 사소 셋)**:
  - ① `str` · `int` 주석 — `_value_annotation` 으로 `str` · `int` · `Final[str]` · `Final[int]`(`<모듈>.Final` 꼴)를 받음 · `Final` 만은 막음 · a_fv_str 0/0 → v2a 0/2 → v2 0/0 · 대조군 policy_value · `Final` 만 그대로 막힘 · 규칙 글 예외 · 검사기 머리 글 «글 · 수 주석» · 붉은 줄 꼬리와 §2.5 처방은 `Final[str]` 하나 · mypy 실측 `:18` · `:20`.
  - ② 글 주석 — `ast.parse(…, mode="eval")` 로 풀어 같은 판정 · 풀리지 않으면 막음 · b_fv_string 2 → 0 · 픽스처 `STATUS_SHIPPED: "Final[str]"` 녹색 · 변이 «글 주석 풀기 걷음».
  - ③ 별표 씨앗 — 새 `checker_target.star_names`(출처 `__all__` · 없으면 맨 위 공개 이름)로 두 검사기 씨앗을 폄 · star_seed 0 → 2(두 검사기) · 픽스처 `star_seed_model.py` · 변이 셋.
  - 줄 수(v2a 대비): `checker_target.py` +44 −14 · `check-context-isolation.py` +6 −4 · `check-port-adapter-pairing.py` +9 −5.
- «한 겹» 글 — houserules #356 · #668 줄 · 트리 명세 두 행에 «꾸러미 `__init__.py` 가 다시 내보낸 모델 클래스 · 이름은 그 모듈의 것과 같다(이름 풀기 · 겹 아님)».

임시물(`r2/`): `proto/scripts/` · `toy/` · `toy-promoted/` · `variants/` · `admin_variants/` · `fixtures-proposed/`(v1 사본) · `fixtures-v2/` · `cases-{rel,v1,v2,v2b}/` · `work-cases-*/` · `op-rev/{pkgtoy,pkgtoy-mod,r180-*,r180s-*,r180b-*,work-*}` · `proto-v2a/`(재확인 전 v2 사본) · `fixtures-v2a/`(재확인 전 픽스처) · `r180b-summary.txt` · `fix-v2b.txt` · `review-text/pkgtoy` · `review-cr/r180/` · `copy-{rel,v2,v2b}/` · `fix-out/` · `fixv2-out/` · `lint.*` · `viol/` · `scan/` · `build/` · `run_*.sh` · `summ.py` · `cmp_cases.sh` · `mutate.py`(v1 사본) · `mutate2.py` · `mypy-toy/`(v1 사본 + `e_lie_model.py` · `plan_policy.py` · `.mypy_cache`).
- 운영자(17:54) — review-text 둘째 재확인 새 사소: houserules 두 줄 · 트리 명세 두 행의 꾸러미 풀기 글을 «자기 `django_<bc>/` 아래 꾸러미 `__init__.py`(`models/` 등)» 로 넓혀 검사기(`reexport_uses` — `django_<bc>/` 아래 모든 꾸러미 한 단)와 맞춤.

## 4. 완료 조건 정적 검사(T)

### F4-165 — 완료 조건의 정적 검사를 «기준선 대비» 로 (설계 v2 · 운영자 · 11-15 17:07 — v1 t-tools 15:06 + review-text 중1 · 중2 · 중3 · 사9)

글만 고치는 단위 — 그래프 Norm 하나(coder) · Codex 짝 한 문단 · Makefile 문면 대조 한 줄 · G12 분류 한 줄 · 검사기 · 도구 0 · 사용자 결정 불필요.

#### 결정
- 사용자 «나.»(14:56) 덤. 기준 규칙: houserules SKILL §1.1 전파 금지(R-3121 · 적용 범위 분류 T*) · 조정자 «무관/관련의 자는 기준선 실측»(R-0295) · 2.38.0 F4-178 처분(R-2548) · 자매 web coder-web.md:52 «베이스라인 대비 신규 이슈 0».

#### 고칠 설계
| 자리 | 소유 | 처분 |
|---|---|---|
| `dddjango/agents/coder.md:47` | `agent-coder.ttl` 블록 `s/dddjango/agents/coder.md/s004/b10` · R-2524~R-2533 · R-3670 | **고침 — 새 Norm 하나** |
| `design-architect.md:101` | `…/s005/b39` · R-3610 | 안 고침(녹색의 자는 재는 쪽이 정함) |
| `commands/dddjango.md:170` | `…/s007/b9` · R-0295 | 안 고침(같은 자) |
| `commands/dddjango.md:242` | `…/s008/b1` · R-0412 ~ R-0414 | 안 고침(R-0413 이 «기준선부터 m(셈 밖)» 을 받음) |
| `discipline-houserules/SKILL.md:29` | `…/SKILL.md/s004-1/b2` · R-3121 | 안 고침(이미 덮음 · 새 문장이 인용) |

- coder.md:47 b10 — «…Bash로 실행해 Green을 확인한다.» 와 «**내부 루프 실행 범위는 BC-범위가 기본이다(2026-08-13)**» 사이에 새 문장. 새 Norm `R-<ISSUED 끝+1>`(다른 단위와 차례로 채번) · `djr:Obligation` · Expression revision 1 · b10 `statesNorm` · `ontology/wiring/agent-coder.ttl` `djr:delegatedTo <…#a/command-dddjango>`(R-2525 · R-3670 꼴).
- 새 문장(v2):
  > 명세 완료 조건의 정적 검사(린터 · 포매터 · 타입 검사)도 코드를 바꾼 파견마다 그 파견 끝에 돌고(슬라이스 · 반송 회전 · 감사 반영 · 슬라이스 0 창 · 묶음 창 · nit 치환 등 코드를 바꾼 coder 파견 전부), 그 green 은 기준선 대비 새 진단 0 이다. 기준선은 이 파견을 받아 편집하기 전의 커밋이다 — 첫 명령에서 `git rev-parse HEAD` 로 적어 두고(이어 부르기도 새 파견이라 다시 적는다), 파견 중에 커밋이 생겨도 그 값을 쓴다(옮긴 파일은 옛 경로 · 옛 경로를 못 찾은 파일은 완료 보고에 `기준선 못 찾음` 으로 따로 적는다). 진단은 줄 · 칸 번호를 빼고(진단 글 안의 줄 참조 `line N` 도 뺀다) 파일 · 규칙 코드 · 진단 글로 맞추고 같은 진단이 여럿이면 개수로 세며, 기준선보다 많은 몫은 줄이 어디든 이번 몫이다. 파일 하나로 도는 검사는 기준선 판을 표준 입력으로 돌려 잰다(`git show <기준선>:<경로> | ruff check --stdin-filename <경로> -` 꼴 · 기준선과 내용이 같은 파일은 따로 돌리지 않는다). 파일 단위로 판정하는 포맷 검사는 기준선 판도 실패하던 파일을 셈 밖에 두고, 그 실패를 지우려고 그 파일에 포매터를 돌려 기존 줄을 다시 쓰지 않는다(포매터 서식은 dddjango 표준 밖이라 기존 줄의 서식 정리는 어느 모드에서도 이번 일이 아니다 — 승인 스코프가 그 파일 서식 정리를 정한 때 빼고) — 새 파일과 기준선 판이 지나던 파일은 지나야 한다. 기준선 판을 따로 돌릴 수 없는 검사(프로그램 전체를 보는 타입 검사)는 진단이 가리키는 원문 줄이 기준선 판에 글자 그대로 있고 이번 변경이 그 줄이 쓰는 이름 · 타입을 바꾸지 않았을 때만 셈 밖이다. 창 판정이 치환 밖 편집을 막는 파견은 그 판정이 받는 고침만 한다 — 묶음 창은 새 진단을 고치지 않고, nit 치환은 개명에 따라 움직인 import 줄의 차례만(줄 나눔 · 합침 없이) 고치며, 남은 새 진단은 줄(파일 · 규칙 코드 · 진단 글)째 완료 보고에 적는다. 완료 보고에 검사마다 `정적 검사 <명령>: 새 진단 n · 기준선부터 m(셈 밖)` 을 적는다.
- prefLabel 후보(v2): «완료 조건 정적 검사는 코드를 바꾼 파견마다 끝에 · green = 기준선(파견 시작 커밋 · 이어 부르기도 새로) 대비 새 진단 0 — 줄 · 칸 번호 · 글 안 줄 참조 빼고 파일 · 규칙 코드 · 진단 글 개수로 맞춤 · 기준선부터 있던 진단 · 기준선 판도 실패하던 파일의 파일 단위 포맷 실패는 셈 밖 · 그 파일에 포매터로 기존 줄을 다시 쓰지 않음(승인 스코프 빼고) · 새 파일 · 기준선 통과 파일은 통과 · 전체 프로그램 검사는 원문 줄 같음 · 이름 · 타입 무변일 때만 셈 밖 · 완료 보고 한 줄».
- 기준선 = 파견 시작 커밋 까닭(v1 «HEAD · coder 는 커밋하지 않는다» 를 바꿈): coder 커밋 금지 글이 없고(coder.md) 커밋 주체 · 시점은 사용자 지시 · 발주 계약(조정자 글)이라 파견 중 `HEAD` 가 움직일 수 있다 — 움직이면 이번 진단이 기준선에 들어 fail-open(review-text 중2 재현). 파견마다 시작 커밋을 쓰면 파견 사슬이 래칫이 된다 — 단 코드를 바꾼 파견이 모두 정적 검사를 돌 때만이다(앞 파견의 새 진단은 그 파견 완료 보고에서 0 으로 닫혔다). 그래서 «슬라이스 끝» 이 아니라 «코드를 바꾼 파견마다» 다(재확인 새 중요 — `op-rev/t165chain.sh`: 정적 검사를 돌지 않은 파견이 a.py 에 새 진단 둘을 만들고 조정자가 커밋 → 다음 파견 기준선(파견 시작) 새 0 · 실행 시작 기준 새 2). 실행 시작 커밋(build_anchor)을 기준선으로 쓰지 않는 까닭: 승인 머지로 들어온 main 의 진단을 이번 몫으로 세어 옛 줄을 고치게 몬다.
- 맞춤 열쇠 까닭(review-text 중1): 줄 번호를 넣으면 위에 줄을 더한 것만으로 기존 진단이 새 진단이 되어 coder 가 옛 줄을 고친다(= F4-165 의 해 · R-3121 위반).
- mypy · `ruff check` 도 한 문장으로(같은 틈 · R-0295 와 자 하나 — 슬라이스 앞 판) · 파일 단위 포맷만 따로 한 줄 · 타입 검사는 원문 줄 같음 · 이름 · 타입 무변 조건(갈리면 새 진단 · 보수).
- 리팩토링 모드 정합: 보존 몫(포매터로 기존 줄을 다시 쓰지 않음)의 근거는 R-3121(T* — 리팩토링 모드 ⑴ 에서 풀림)이 아니라 «포매터 서식은 dddjango 표준 밖 — 리팩토링 모드 슬라이스 0 의 정리 대상(ⓐ)도 아님» 이고 «승인 스코프가 정한 때 빼고» 를 단다 → 리팩토링 모드에도 그대로 남는 금지라 적용 범위 Override 대상이 아니다(N · 절차 — 녹색의 자 · scope-limit-norms N 행 사유도 같은 말). 사본 application/ 아래 포맷 실패 파일 0 이라 빈도 낮음.
- **묶음 창 · nit 치환(v2.3 — 넷째 확인 뒤 줄이는 안)**: 두 창은 판정이 치환 밖 편집을 막아 기계 치환이 낸 새 진단(import 차례 `I001` · 길이 글 든 `E501` — 동작 무관)을 그 파견이 다 고칠 수 없다(재현 `op-rev/t165bundle/` · `op-rev/t165nit/`). nit 은 판정자가 이름 고침으로 받는 import 줄 차례만 고치고(`discipline-reviewer.md` NIT_DIFF_CHECK «개명에 따라 움직인 것(import 정렬 차례 …)은 이름 고침의 일부» · 줄 나눔 · 합침은 «애매하면 내용 바뀜» 이라 빼고), 남은 것은 두 창 모두 줄째 완료 보고에 적는다 → 한계(G2 감수). 조정자 글 · R-3725 · Codex 조정자 짝 · Makefile 조정자 줄은 고치지 않는다(버린 갈래 «넘김» 참고).
- web: 뜻 같음 · 낱말은 core «기준선» · web 보다 엄격하지 않음 · web 은 고치지 않음.
- 기계 장치 0: `dddjango/scripts/*.py` 에 ruff · mypy 돌리는 자리 없음 · 새 러너 만들지 않음.
- 되돌아옴 막기: Claude 쪽은 그래프(render 동기 · target-counts · rulepack). Codex 짝은 Makefile `verify-base-core` «멈춘 시험 깨우기» 줄(Makefile:197) 꼴로 한 줄(끝 `; \` 로 사슬에 붙임):
  ```
  	for f in dddjango/agents/coder.md codex-dddjango/skills/dddjango-coder/SKILL.md; do grep -qF '기준선 대비 새 진단 0' $$f && grep -qF '줄 · 칸 번호를 빼고' $$f && grep -qF '그 파일에 포매터를 돌려 기존 줄을 다시 쓰지 않는다' $$f || { echo "ERROR: $$f 에 완료 조건 정적 검사의 기준선 대비 글(맞춤 열쇠 · 포매터 전파 금지)이 없다 — Claude · Codex 두 런타임에 둔다"; exit 1; }; done; \
  ```
- G12(review-text 중3): 이름표가 `DRIFT_RE` 의 «기존» · «새 파일» 에 걸린다 → `workspace/tools/rulepack_smoke.py` `DRIFT_REVIEWED` 에 새 ID · `workspace/plan/2026-09-26-refactor-path-repair/scope-limit-norms.md` 표 2 끝 N 행(사유: 절차 — 녹색의 자 · 보존 몫의 근거는 «포매터 서식은 dddjango 표준 밖 — 리팩토링 모드 슬라이스 0 의 정리 대상도 아님» + 승인 스코프 예외라 리팩토링 모드에도 남는 금지 · Override 대상 아님) · 머리 «재검토 N 반영» 줄에 이번 판 G12 대조 건수(대상 56 무변). rulepack_smoke 는 봉인 대상.

#### 장난감 전 / 후
- 전(2.38.0 글): `t-tools/toy165/` `ruff@0.17.3 format --isolated --check legacy.py` 기준선 · 새 줄 뒤 모두 exit 1 · `--diff` 는 손대지 않은 줄만 고침.
- v1 글의 자: `t-tools/f165_toy.sh` exit 0 — 장면 1(레인 꼴) 절대 실패 1 · 기준선 대비 새 실패 0 / 장면 2(대조군) 새 실패 2 · F401 새 1 / 장면 3 새 실패 0.
- v2 글의 자 `sh op-rev/t165v2.sh "$PWD/op-rev/t165v2"`(`ruff@0.17.3 check --select F401,E711`):
  - 장면 1 줄 밀림(docstring 두 줄): 줄 번호 넣은 비교 새 2 · **v2 새 0**.
  - 장면 2 같은 진단 하나 더(E711 두 번째): 집합 비교 새 0 · **v2 다중집합 새 1**.
  - 장면 3 파견 중 coder 커밋 뒤: 기준선 HEAD 새 0(fail-open) · **기준선 파견 시작 커밋 새 1**.
  - 검토자 `review-text/t165commit.sh` 운영자 재실행(`op-rev/t165commit`): 커밋 전 1 · 커밋 뒤 HEAD 0 · 파견 시작 SHA 1.

#### 사본 재측정
- 검사기 출력 차이 0. 계기 빈도: 사본 `ruff format --check application web framework` → 903 files would be reformatted · 모두 `web/` 아래 — `web/` 를 고치는 레인은 늘 만남.

#### 시험
- 픽스처 · 골든 검사기 시험 0. verify 에 닿는 것: 새 Makefile 문면 대조 줄(변이: Codex SKILL 에서 맞춤 열쇠 구절이나 포매터 구절을 걷으면 ERROR) · 온톨로지 단(ontology_gate · render_sync · wiring 구조 · target-counts · q4 골든 · rulepack --check) · rulepack_smoke G12 · 봉인.

#### 남는 한계
- 기준선에서 이미 실패하던 파일은 이번에 쓴 줄의 서식도 기계로 안 잼(감사 · 프로젝트 도구 몫 · `--range` 안 넣음).
- 전체 프로그램 타입 검사 기준선은 판단(갈리면 새 진단).
- 조정자가 슬라이스 사이에 커밋하지 않으면 앞 슬라이스 변경도 이번 몫(보수).
- 다른 파견이 `git mv` 아닌 `mv` 로 옮긴 파일은 커밋하지 않는 실행에서 옛 경로를 못 찾음 → `기준선 못 찾음` 따로 보고(새 진단으로 세지도 셈 밖으로 지우지도 않음 · G2 감수).
- 이번 실행이 검사 도구 설정(ruff 설정 등)을 바꾸면 기준선 판도 새 설정으로 잰다(설정 변경은 명세 · 감수 몫).
- 묶음 창 · nit 치환의 기계 치환이 낸 새 진단(import 차례 · 줄 길이 — 동작 무관)은 그 파견이 고치지 못하고(nit 은 import 줄 차례만 고침) 줄째 완료 보고에만 남는다 — 그 파견 뒤 커밋되면 다음 coder 파견 기준선에 든다(G2 감수 몫 · 조정자 G2 검증 보고 R-0412 는 이 줄을 따로 옮기라고 하지 않음).
- acceptance-tester 가 쓰고 커밋된 시험 쪽 파일의 새 진단은 다음 coder 파견의 기준선에 든다(이 Norm 은 coder 몫 · 감수 몫).
- 같은 열쇠의 진단 개수만 견주므로, 기존 진단 하나를 지우고 같은 글의 새 진단 하나를 다른 줄에 만들면 0 으로 보임(드묾 · 감수 몫).
- 명세가 명령을 흐리게 적는 것은 단위 밖 · 프로젝트 pre-push · CI 절대 판정은 프로젝트 몫(F4-178 과 같은 자리).

#### 버린 갈래
- 묶음 창 몫 넘김(v2.1 창 앞 커밋 · v2.2 진단 줄) — 커밋을 넘기면 승인 머지(main) 진단까지 셈(셋째 확인 B · `op-rev/t165passmerge.sh`) · 줄을 «지금도 있는가» 로 맞추면 같은 열쇠의 옛 줄까지 고치게 됨(넷째 확인 · `review-text/t165passlines.sh` — F4-165 가 막으려던 해) · 열쇠별 개수 넘김은 고칠 수 있으나 조정자 Norm · Codex 짝 · Makefile · R-3725 를 늘림 — 남는 몫이 동작 무관 lint 뿐이라 한계(G2 감수)로 둠(넷째 확인 검토자 권고 «줄이는 안이 낫다»).
- 조정자가 Phase 2 시작에 기준선 캡처(web 꼴) — 파견 시작 커밋으로 충분 · 조정자 단계 늘릴 까닭 없음.
- «coder 는 커밋하지 않는다» 새 규칙 — 커밋 주체는 발주 계약 몫(조정자 글) · 역할 규칙을 늘리지 않고 기준선 정의로 닫음.
- architect R-3610 · houserules R-3121 · 조정자 R-0295 · R-0413 덧말 — 이미 덮음 · 두 번 적지 않음.
- 포맷만 다루는 좁은 문장 — mypy · ruff check 도 같은 틈.
- `ruff format --range` · 슬라이스 완료 러너 새로 — YAGNI · 자리 없음.

#### 맡을 파일
- 그래프: `ontology/rules/agent-coder.ttl` · `ontology/wiring/agent-coder.ttl` · `ontology/ISSUED`.
- 투영 · 재기준선: `dddjango/agents/coder.md`(`ontology_render.py --apply agent-coder`) · `ontology/LEDGER.tsv`.
- 계수 · 골든 · 팩: `target-counts.json`(Norm +1 · Expression +1) · q4 골든 · `rulepack.json` + Codex byte 미러.
- G12: `workspace/tools/rulepack_smoke.py`(DRIFT_REVIEWED · 봉인 대상) · `workspace/plan/2026-09-26-refactor-path-repair/scope-limit-norms.md`(N 행 · 머리 줄).
- Codex 의미 미러: `codex-dddjango/skills/dddjango-coder/SKILL.md:39`.
- `Makefile`(verify-base-core 한 줄 — coder 쪽).
- 겹침: ISSUED · target-counts · LEDGER · rulepack · q4 골든 · rulepack_smoke · scope-limit-norms 는 그래프를 고치는 모든 단위가 같이 씀(채번 · 재생성 · G12 분류 차례로) · `agent-coder.ttl` s004 를 고치는 다른 단위가 있으면 b10 겹침.

#### 크기 · 사용자 결정
- L 꼴(그래프)이지만 양은 작음(Norm 1 · 블록 1 · Codex 1 · Makefile 1 · G12 1 · 검사기 0). 사용자 결정 불필요(기준선 정의 · 맞춤 열쇠는 F4-165 목적 «기존 줄을 고치게 몰지 않는다» 에서 나옴). 요청 가이드 · README · master 바뀔 것 없음.

#### v1 → v2 바뀐 것
- review-text 중1: 맞춤 열쇠(줄 · 칸 번호 뺌 · 파일 · 규칙 코드 · 진단 글 · 개수) 문장 · 타입 검사 «같은 글» → «원문 줄 글자 그대로».
- review-text 중2: 기준선 `HEAD` → 파견 시작 커밋(`git rev-parse HEAD` 적어 둠 · 파견 중 커밋에도 그 값) · 까닭 글 고침 · «R-0295 와 자 하나» → «슬라이스 앞 판».
- review-text 중3: G12 맡을 파일(rulepack_smoke · scope-limit-norms) · N 분류 까닭.
- review-text 사9: Makefile 끝 `; \` · 맞춤 열쇠 grep 더함 · 포매터 금지에 «승인 스코프가 정한 때 빼고» · `mv` 로 옮긴 파일 `기준선 못 찾음` · 기준선과 같은 내용 파일은 따로 안 돎 · 도구 설정 변경 한계.
- 운영자 더함: 리팩토링 모드 정합 · 같은 열쇠 바꿔치기 한계 · «coder 커밋 금지 규칙» 버린 갈래.
- 좁은 재확인(review-text 11-15 17:43 · 맡긴 넷 닫힘) 새 지적 반영(운영자 17:45): 중요 «정적 검사 안 도는 파견 → 다음 기준선에 숨음»(재현 `op-rev/t165chain.sh`) → «코드를 바꾼 파견마다 그 파견 끝에» · 까닭 글 좁힘 · acceptance-tester 한계 줄 / 사소 1 글 안 줄 참조 `line N` 뺌 / 사소 2 보존 몫 근거를 «포매터 서식은 표준 밖» 으로(R-3121 인용 걷음 · N 사유 같은 말) / 사소 3 «이어 부르기도 새 파견 — 다시 적는다».

임시물: `t-tools/` 의 `f165_toy.sh` · `toy165/` · `toy165b/` · `op-rev/t165v2.sh` · `op-rev/t165v2/` · `op-rev/t165commit/`.
- 둘째 재확인(review-text 11-15 17:51) 반영(운영자 17:54 · v2.1): 새 중요 «묶음 창은 새 진단을 고칠 수 없다»(재현 `op-rev/t165bundle/`) → coder 글 «치환 밖 편집이 막힌 파견은 보고만 · 입력의 `정적 검사 기준선` 을 씀» + 조정자 b61 새 Norm(다음 coder 파견에 창 앞 커밋 넘김 · 끝 맞춤이면 감사 앞 coder 한 번) + R-3725 ⑥ 계기(정적 검사 새 진단 · 줄 나눔은 이름 nit 아님) + Makefile 조정자 줄 / 사소: 파견 목록 «… 등 코드를 바꾼 coder 파견 전부» 로 엶 · G12 N 사유를 새 근거 말로.
- 셋째 확인(review-text 11-15 17:57) 반영(운영자 17:58 · v2.2): 둘째의 지적 모두 닫힘 · 새 중요 A(nit 개명의 import 차례 → 빠른 길 철회) → nit 치환은 판정자가 받는 import 차례 고침만 하고 남은 것만 보고 · ⑥ «남은 새 진단» / 새 중요 B(창 앞 커밋 기준선이 승인 머지 진단을 셈) → 커밋 대신 진단 줄(`넘겨받은 정적 검사 진단`)을 넘김 · coder 는 지금도 있는 줄을 이번 몫에 더해 고침 / 사소(«5번 감사 앞» 이 nit 길 끝 맞춤과 안 맞음) → «그 뒤 차례 앞 · nit 길 감사 생략 그대로». Makefile 조정자 grep 글귀 `넘겨받은 정적 검사 진단`.
- 넷째 확인(review-text 11-15 18:01) 반영(운영자 18:03 · v2.3 줄이는 안): 셋째 지적 A · B · 사소 닫힘 · 새 중요(넘겨받은 줄 «지금도 있는가» → 옛 줄 고침 · 커밋 안 하는 실행에서 두 배 셈) → 넘김 장치 걷음 · 조정자 글 · R-3725 · Codex 조정자 짝 · Makefile 조정자 줄 걷음 · coder 글은 «nit 은 import 줄 차례만(줄 나눔 · 합침 없이) · 남은 새 진단은 줄째 완료 보고» · 한계 줄(G2 감수) / 새 사소(I001 고침은 줄 나눔 · 합침까지) → «import 줄의 차례만(줄 나눔 · 합침 없이)».
