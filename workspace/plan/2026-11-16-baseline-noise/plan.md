# dddjango 2.40.0 — 게이트 기준선 일곱 · 검사기 물음 소음 셋 · 글 둘 · 계획 v1.2 (2026-11-16)

상태: 계획 v1 — 설계 초안 셋(작업본 · 현장 이름이 들어 있어 scratch 에만 둠 · 배포 뒤 이 폴더에 정리본) 위에 섰다. 세 단위 설계가 모두 독립 검토 · 좁은 재확인에서 닫혔다(c 둘째 · b 셋째 · a 넷째 확인 — a 셋째 확인 차단은 사용자 «가.» 로 넷째에서 닫힘). 계획 v1 독립 검토(차단 0 · 중요 5 · 사소 11)를 모두 받아 v1.1 로, 좁은 재확인(차단 0 · 중요 1 · 사소 4)을 받아 v1.2 로 고쳤다 — 끝 절 «계획 검토 처분». **사용자 계획 승인 «진행»(11-16 18:43)** → 구현 → **배포 끝(2.40.0 · 11-16 23:33)** — 판 기록 `plan-2.40.0.md` · 설계 정리본 `design.md`.

## 결정

- **사용자**:
  - 3판 진행 «3판 진행하자.»(11-16 02:56) — `work_list.html` 3판 항목 F4-26 · 27(+136) · 28 · 29 · 32 · 45 · 46 · 95.
  - 범위 넓힘 «가»(11-16 08:42) — 재현 중 찾은 게이트 결함 셋(N1 계약 문법 검사기 줄 가림 · N2 첫 `migrations/` 폴더 놓침 · N3 멱등 검사기 문서 입력 비대칭)을 이번 판에.
  - 게이트 단위 셋째 확인 차단 «가.»(11-16 16:07) — 고치고 넷째 확인 · 넷째에도 안 닫히면 게이트 단위를 다음 판으로.
  - F4-95 «확정»(11-16 13:30) — 포트 메서드 이름 규칙 넷(아래 «사용자에게 보이는 흐름» F4-95 줄) · 검사기는 원시 값 · Enum 반환이고 첫 낱말이 모호 동사(invoke · apply · call · perform …)가 아니면 묻지 않음 · 받아들인 놓침.
- **운영자 처리**(질문 생략 · 설계 처리 · 이의 시 뒤집음 — 계획 승인 때 밝힌다):
  1. F4-27 · 136 — 검사기가 작업 트리 `.dddjango/violations/` 에 기록을 남기는 기본 자리는 온톨로지 A/B 실런(`DJR_EXPERIMENT_RUN_ID` 가 있을 때)에서만 켠다. 실런 밖 직접 실행은 아무것도 남기지 않는다. 이미 추적된 현장 기록 파일은 대상 저장소 주인 몫(알림만).
  2. F4-28 · N2 · N3 — 게이트는 지금 사본의 «건드림» 을 **앵커부터의 변경**(커밋 · 미커밋 같음)으로 센다. 직접 실행(사용자 · 역할)은 지금처럼 HEAD 대비. dddjango-web 백스톱 `--diff-base` 와 같은 꼴이다.
  3. F4-28(R1) — 승인 머지가 그대로 들인 legacy 앱 마이그레이션 · 새 평면 앱은 «승인 유입»(exit 제외 · 기록). 승인 목록 없이 main 머지로 들인 것은 게이트의 «미승인 머지 = 레인 편집» 정책대로 귀속. 레인 몫은 검사기 정의(«새 마이그레이션 · `apps.py` · `models.py` 파일») 그대로 — 승인 머지가 들인 파일(마이그레이션 포함)을 레인이 고친 것은 레인 몫이 아니다(legacy 앱 · main 이 들인 새 앱 같게 · 2.39.0 판정과 같음). 레인이 새로 만든 그 파일만 귀속. 넷째 확인 검토자는 legacy 앱에 들어온 마이그레이션을 레인이 고친 꼴을 «귀속이 맞다» 고 적었다 — 운영자가 다르게 정한 자리다.
  4. N1 — 계약 문법 검사기 일곱도 줄마다 견준다(같은 글 둘째 줄은 순번 · 연산 이름 줄 번호 · 버킷 내용 칸만 다른 줄은 같은 위반으로 짝). 글이 다르면 같은 주어여도 새 위반.
  5. F4-46 — ⓓ 후보 줄의 수 칸(행수 · 폴더 구성원 수)이 줄었을 때는 그 파일이 지움만 했을 때만 legacy 로 짝 짓는다.
  6. F4-26 · F4-32 — 검사기 물음 소음 둘은 검사기 정의에서 답이 나옴(아래 흐름 표).
  7. F4-95 사용자 결정 밖 세부 — 반환 «그 목록 · Optional» 은 list · tuple · set · frozenset · Sequence · Collection(+ typing 대문자 `List` · `Tuple` · `Set` · `FrozenSet`) · Optional · Union · `X | None` · `Annotated` 첫 인자로 읽음(사전 `dict` · `Mapping` · 흐름 `Iterable` · `Iterator` · `Generator` · 시간 길이 `timedelta` · `Any` · `Path` 는 묻는 쪽 — «확신 없으면 묻는다») · Enum 은 `enum` · `django` 의 Enum 을 기저로 둔 클래스만(업무 클래스 이름이 `Flag` · `Choices` 여도 Enum 아님) · cleancode §2.6 은 모든 메서드로 넓히지 않고 houserules 새 칸을 다시 말한다.
  8. F4-29 · F4-45 — 글 둘(아래 흐름 표).
  9. 레인 문서가 «멱등성 미요청» 인데 승인 머지가 멱등 파일을 들인 꼴은 2.39.0 처럼 귀속(이중 원인 — 검사기 정의로는 풀 수 있으나 같은 판정 · 막는 쪽으로 둠).
- 판 번호 **2.40.0**(minor) — 새 규범(포트 메서드 이름 둘) · 규범 고침 여덟 · 게이트 · 검사기 판정 변경. dddjango-web 은 바뀌지 않는다.

## 사용자에게 보이는 흐름(전 → 후)

| 보고 | 2.39.0 | 2.40.0 |
|---|---|---|
| F4-27 · 136 | 검사기를 직접 돌릴 때마다 대상 저장소 작업 트리에 `.dddjango/violations/*.jsonl` 이 쌓여 커밋에 섞임 | 실런이 아니면 남기지 않음(판정 · 출력 무변) |
| F4-28 | 앵커 사본에서만 `check-app-container` 가 2 → 거짓 «legacy 해소 1» · 게이트가 레인의 새 마이그레이션 · 새 평면 앱을 놓침(커밋 · 미커밋 모두) | 앵커 = 커밋 트리 · 지금 = 앵커부터의 변경 → 거짓 해소 0 · 새 것은 귀속 |
| F4-46 | ⓓ#644 진단 글의 행수가 줄면 legacy 가 «신규» 로 다시 뜸 | 지움만인 파일의 수 칸 줄음은 legacy |
| N1 | 계약 문법 검사기 일곱은 exit 값만 견줘서, legacy 가 하나라도 있으면 새 위반이 가려짐 | 줄마다 견줌 · 새 줄은 귀속 |
| N2 | legacy 평면 앱에 첫 `migrations/` 폴더를 더하면 직접 실행이 못 봄 | 봄 |
| N3 | 앵커에 실행 문서가 없으면 멱등 검사기가 거짓 귀속 · 앵커에도 있으면 legacy 멱등 파일 고침을 놓침 | 앵커부터의 변경으로 가름 |
| F4-26 | ⓓ#257 «끝에 불변식 확인 없음» 이 확인 호출 뒤 `return True` 에 뜸 | 확인 호출 뒤 값만 돌려주는 return 은 확인으로 끝난 것(상태를 바꾼 뒤 확인 없이 빠져나가는 다른 return 이 있으면 그대로 물음) |
| F4-32 | ⓓ#191 이 `get_order_detail` 같은 조회 유스케이스 이름의 명사 접미를 물음 | 묻는 동사 머리(get · find · list · count)로 시작하면 묻지 않음(`draw` 는 2.27.3 에서 이미 고쳐짐) |
| F4-95 | ⓓ#485 가 `url()` 같은 조회 포트 메서드 이름을 물음 · 포트 메서드 이름 규칙이 런타임 글에 없음 | 규칙(조회면 명사구도 · 아니면 명령이라 동사구 · 확신 없으면 명령 · 로그 · 캐시는 바뀜 아님 · notify · handle · execute · invoke 류 위반)을 houserules §3 · 감수 물음에 · 원시 값 · Enum 반환 + 모호 동사 아니면 묻지 않음 |
| F4-29 | architect 자기모순 스캔이 «docstring 셋» 같은 수 표기를 명세가 적은 개수와 대조하지 않음 | 대조 거리에 «수를 세는 말 ↔ 명세가 낱낱이 적은 개수» 를 더함 |
| F4-45 | arrange 점검 역할은 git 읽기 0 인데 조정자는 `git show` 를 지정 · Phase 2 뒤 `기준선` 을 작업 트리로 봄 | 조정자가 `기준선 판` · `유입 판` 을 실음 · 역할은 그 판의 시험 쪽만 git 세 꼴로 읽음 |

F4-95 쓰는 꼴(houserules §3 새 칸):
```python
class PhotoStorage(Protocol):
    def url(self, photo_id: PhotoId) -> str: ...          # 조회 — 명사구 됨 · 검사기도 안 물음
    def save_photo(self, photo: Photo) -> PhotoId: ...    # 명령 — 동사구
    def notify(self, photo: Photo) -> None: ...           # 위반(무엇을 시키는지 안 말함)
```

## 단위 · 맡은 파일

| 단위 | 보고 | 맡은 파일(+ Codex byte 미러) |
|---|---|---|
| A 게이트 · 기준선 | F4-27 · 136 · 28 · 46 · N1 · N2 · N3 | `findings.py` · `anchor_diff.py` · `registry_gate.py` · `checker_target.py` · `check-app-container.py` · `check-idempotency-scope-creep.py` — 시제품 v5 + 넷째 확인 처분 둘(아래 3 단계) |
| B 검사기 물음 | F4-26 · 32 · 95 | `check-domain-model.py` · `check-usecase-dto-placement.py` · `check-port-adapter-pairing.py` — 시제품 v3 · 손 글 `workspace/design/2026-08-11-predicates.md`(129 · 144 · 197) |
| G 그래프 · 글 | F4-29 · 45 · 95(글 · R-1123 라벨 포함) · N1(글) | `ontology/rules/*.ttl` 여섯(agent-design-architect · agent-acceptance-tester · command-dddjango · discipline-houserules-final · agent-discipline-reviewer · discipline-cleancode-final) · `ontology/wiring/discipline-houserules-final.ttl` · ISSUED · LEDGER · target-counts · rulepack + Codex · q4 골든 · 투영 md · `workspace/reference` 미러 둘(houserules · cleancode) · Codex 같은 뜻 다섯 자리(design-architect · acceptance-tester · dddjango 두 자리 · discipline-reviewer) · `docs/DEVELOPMENT.md` §3 체크리스트 8 한 줄(아래 «문서») |
| 시험(단위가 패치로 냄 · 운영자가 그 단위와 함께 넣음) | 전부 | `registry_gate_smoke.py`(A 의 새 사례 · 변이 — N2 · S2 사례 포함) · `anchor_diff_smoke.py`(대역 서명 · 변이 표 · F4-27 사례) · `field_report_checker_smoke.py` · `pregate_symbol_kinds.json` · EXPECTED 도구(바뀔 것 없음 예상 — 물음 글을 바꾸면 findings_count 지문 하나) |

- 새 Norm 둘(포트 메서드 이름 — ISSUED 끝 R-3764 뒤로 차례 채번) · 표현 고침 여덟(R-1754 · R-3607 · R-3608 · R-3613 · R-3614 · R-3615 · R-3617 · R-1123) · 새 블록 둘(houserules §3 · cleancode §2.6) → target-counts NormShape +2 · WorkShape +2 · ExpressionShape +10 · BlockShape +2(구현 때 게이트로 확인).

## 일하는 법 · 차례

1. **계획 승인** — 10 줄 요약 · «밝힐 것»(위 운영자 처리 1 ~ 9) · 명시적 «진행».
2. **장부 다시 읽기**(계획 확정 때) — 새 F4 가 이 판 범위에 닿으면 범위를 다시 묻는다.
3. **구현 — Claude 구현자 셋(A · B · G), 각자 사본에서.** 사본 = `workspace/scratch/pan3-1116/wt-<단위>/`(main HEAD 에서 뜬 detached git worktree · `.venv` · `.venv-probe` 는 본 저장소 것을 링크하고 `info/exclude` 에 적음 — DEVELOPMENT §7.4 릴리스 클론과 같은 꼴 · 정리 때 `git worktree remove` · `prune`). 구현자는 자기 사본만 고치고 시험한 뒤 diff 를 낸다. 함께 고치는 시험 파일은 패치로 낸다. 시제품을 출발점으로 쓰되 시제품 주석의 설계 메모는 런타임 글이 아니므로 docstring · 주석을 규칙대로 다시 쓴다.
   - A: 시제품 v5 `a/proto/scripts/`(여섯 파일) + 넷째 확인 · 계획 검토 처분 — ① app-container 줄의 출처 판정을 두 집합으로 가른다: T = 그 줄을 만든, 앵커에 없던 `migrations/*.py`(`__init__.py` 밖) · `apps.py` · `models.py` · S = T 에서 first-parent 사슬의 참여 승인 머지 가운데 **어느** `^2` 에라도 있는 경로를 뺀 것(레인 몫). T 가 있고 S 가 비면 유입 · S 가 있으면 귀속 · 폴더 tree 판정은 T 가 빌 때만(legacy 앱 · main 이 들인 새 앱 같은 규칙 — 레인이 승인 머지가 들인 파일을 고친 것은 레인 몫 아님 · 운영자 처리 3) ② backoffice 줄의 출처 판정은 폴더 tree 로(v4 꼴).
     시험: 대역 서명 둘에 `committed` · `git_base` · `git_tip`(`registry_gate_smoke.py` `SisterGateRegression.measure` · `anchor_diff_smoke.py` `fake`) · 변이 표 «F4-166 ⓓ 후보 짝» 옛 글을 새 호출 꼴로 · 새 사례는 `registry_gate_smoke` 의 unittest 이름 시험(장난감을 지은 이름 그대로 — N2 e · f · 대조 · S2 app-b · idem-new `BASE=TIP=HEAD` 포함 · `git_touched_smoke` 에는 두지 않음 — 옛 코드 골든이라 새 판정을 받을 수 없음) · F4-27 사례는 `anchor_diff_smoke`(a §1 (a) · (c)) · 새 판정마다 죽일 변이 하나 이상(초안 §10 표 전부 + F4-27 두 줄 — 실런 조건 걷기 · `_run_lines` 의 `DJR_VIOLATIONS_DIR` 걷기 · 변이는 `_BASELINE_MUTATIONS` · `_MUTATIONS` 에).
     `registry_gate_smoke` 직렬 대조 R1 · R2(옛 직렬 게이트 `86fc3c24` 사본과 byte 대조 · 저장된 기대값 없음): 시험 머리 유지 규칙대로 같은 변경을 직렬 사본에 덧댄다(a §10 — 덧댈 자리 셋 · 조건 둘: 직렬 sink 를 검사기 이름으로 거름 · 덧댄 자리마다 옛 글이 정확히 한 번 바뀜). 덧대기가 크면 R 을 `DJR_REGISTRY_WORKERS=1` 대조로 낮추고 그 결정을 커밋 메시지에 적는다.
   - B: 시제품 v3 `b/proto/`(세 파일) + 재확인 2 사소 하나(`from enum import Enum as E` 별칭 풀기와 그 시험 — R-1123 라벨 «명사구 · 묻는 꼴도» 는 그 ttl 을 고치는 G 몫). 시험: `field_report_checker_smoke.py` 새 사례 여덟(시험 초안 `b/proposed_smoke.py` v3) · 기존 `test_485_unlisted_first_tokens_stay_questions` 물음 상수 · 손 글 `workspace/design/2026-08-11-predicates.md` 129 · 144 · 197.
   - **G 지시문**에는 DEVELOPMENT §3 체크리스트 1 ~ 6 을 그대로 싣는다 — ttl 편집(rules 여섯 + wiring 하나 · ISSUED 두 줄 · rdflib 편집 뒤 `canon_turtle`) → 온톨로지 게이트 → `ontology_render.py --apply`(agent-design-architect · agent-acceptance-tester · command-dddjango · discipline-houserules-final · agent-discipline-reviewer · discipline-cleancode-final) → LEDGER 재기준선(다시 투영된 절마다) → target-counts · q4 골든 → `make rulepack`(+ Codex) → graph 절을 고친 skill 의 `workspace/reference/<skill>/reference/final.md` 옛 절을 손으로 바꿈(houserules §3 · cleancode §2.6) → `corpus_mirror_sync.py --write` → `--check` → Codex 같은 뜻 다섯 자리 → G12(`rulepack_smoke` 로 새 · 고친 이름표를 대 봄 — 설계 때 새 적중 0 · R-3613 은 이미 `DRIFT_REVIEWED` 등재). 문장 초안은 설계 초안 셋(c · a §4 · b §3.3)의 것을 쓴다.
4. **넣기 — 운영자가 차례로**: A + A 시험 패치(`checker_target` 먼저 · 대역 서명이 같이 들어가야 시험이 돎 · 전 검사기 시험) → B + B 시험 패치 → G. 넣을 때마다 받은 diff 의 파일 목록을 예상 목록과 대조한다(DEVELOPMENT §7.5).
5. **행동 시험** — 단위마다 옛 판(2.39.0 · `f36fa9f9` — `HEAD` 쓰지 않음)이 붉음(또는 놓침)이고 새 판이 녹색 · 대조군 그대로임을 실제로 돌린다(설계 · 검토 · 재확인 장난감 전부 · 아래 수치 표). 넣은 뒤 합친 판으로 다시 돈다.
6. **현장 줄 차이** — 설계 때 하네스를 쓰되 시제품 경로를 박아 둔 스크립트는 scripts 경로를 인자로 바꿔 쓴다. A: 대상 저장소 사본 `--anchor HEAD` · `HEAD~10` 게이트(한 실행 20 ~ 30 분) · B: 검사기 셋 직접 실행. 검사기 조합: 단위 판 + 2.39.0(구현자 사본 단계) · 합친 main + 2.39.0(넣은 뒤). TMPDIR 는 기본값 그대로 · `DJR_VIOLATIONS_DIR` 은 작업 폴더 · 대상 저장소 사본은 읽기만(그 폴더에서 cd · git 안 함 · 복제가 필요하면 작업 폴더에 `--shared` 로 만들고 다 쓴 뒤 지움).
7. **구현 독립 검토** — Claude 검토자 둘(코드 · 글). 설계를 주지 않고 코드 · 글과 장난감 하네스를 준다. 질문에 «커밋 뒤에도 같은 결과인가»(A 는 `git diff <앵커>` · `git status` 를 읽음)를 넣는다. 구현 때로 넘긴 처분의 닫힘을 장난감 이름으로 묻는다 — W1(na-edit · na-add · na-migedit(c) · mm-migedit(c) · mm-two 유입 · mm-apps(c) · mm-lanemig-pre · merge-m3 귀속 — 장난감 만드는 법 `pan3-1116/review-a/bin/mk6.sh` · `mk7.sh` · `pan3-1116/plan-review/mk8.sh`(`COMMIT=1` 이면 커밋 판) · 돌리기 `run5r.sh` · `run8.sh` — 자기 폴더로 복사해 A 경로만 바꿔 씀) · W2(bo-hide(c) · bo-pkg-edit(c) 귀속) · b R1(`Enum as E` 안 물음) · R-1123 라벨.
8. **고침 · 좁은 재확인** — 차단은 고친 뒤 좁게 다시. 셋째 확인에도 안 닫히면 멈추고 묻는다. 고친 뒤 장난감 · 현장 수치를 다시 돈다.
9. **체크리스트 8** — Codex byte 미러(스크립트 아홉) → EXPECTED(`findings_count_matrix` port-adapter 지문 하나 · `checker_baseline_matrix` · `checker_cross_matrix` · `construct_drift_report` 는 무변 확인) → **`gen_pregate_symbol_kinds` 는 마지막 검사기 고침 뒤에** → 맡은 사람이 없는 시험 파일의 기대값 grep → 봉인(스크립트 아홉 · `pregate_symbol_kinds.json` · `rulepack.json` · 투영 md · Codex · ontology). `claude plugin validate` 는 필요 없다(매니페스트 · 구조 · 새 설치 파일 0).
10. **커밋 · 검사** — 경로를 하나씩 `git add` · 사용자 로컬 파일 커밋하지 않음 · `make verify` 전체 + `make verify-mutation`(probe 부하 흔들림은 단독 재실행으로 가림).
11. **배포 전 문서** — 아래 «문서 · 요청 가이드».
12. **장부 다시 읽기**(배포 직전) → push → 깨끗한 클론 `make release`(2.40.0) → 노트 → 봉인 chore.
13. **배포 뒤** — 판 기록 `plan-2.40.0.md`(검토 처분 · 검사 수치 — 마지막 실행 값만) · 설계 정리본 `design.md`(현장 이름 걷음) · 장부 처분 줄 · `work_list.html`(3판 항목 지움 · 다음 판 후보) · 요청 가이드 확인 한 줄 · 배포 보고에 «pre-gate 재예보 필요» 진행 레인(`dddjango/scripts` 가 바뀌어 툴체인 digest 가 바뀜 · N1 로 계약 검사기 줄의 안정 ID 가 바뀜 — DEVELOPMENT §6 릴리즈 창) · 진행표 둘.
14. **정리**(DEVELOPMENT §7.4) — `pan3-1116/`(배포판 사본 · 시제품 · 장난감 · 모래상자 · 구현 사본 worktree · 검토 폴더) · 릴리스 클론 · `/tmp/djr-verify` · 띄운 프로세스. 대상 저장소 사본(리허설 클론)은 시험 드라이브 준비 뒤 지운다.

## 검사 · 수치 기준(구현이 설계와 맞는지)

| 잰 것 | 기대(설계 · 재확인 실측) |
|---|---|
| A F4-27 · 136 | 설치 표식 장난감: 작업 트리 기록 파일 1 → 0 · exit 그대로 · 실런 변수가 있으면 1 그대로 · scope 렌더 직접 실행 `--anchor` 호출자 폴더 2 → 1 파일(지금 실행분 · stdout 은 앵커 sha 빼고 byte 같음) · 게이트 호출자 폴더 0 그대로 |
| A F4-28 · N2 · N3(초안 §8 표) | b · bc · f · fc · k · kc 놓침 → 귀속 · c · e · g · j · newparent(+ 커밋 판) 해당 검사기 줄 귀속 · ch-reg 귀속(의도) · i · ic 거짓 귀속 → 0 · a · ac · l 거짓 해소 → 0 · e 직접 실행 0 → 2 |
| A R1 · R1′ · W1 · W2(승인 머지) | merge-mig · merge-newapp · merge-m +승인 유입 · mm-wt · mm-pre · mm-post · mm-conf · mm-preanchor(+ 커밋 판) 귀속 0 · 유입 1 · mm-two 유입 · na-edit · na-add · na-migedit · mm-migedit(c) 귀속 0 · 유입(구현 때 고침 — v5 는 귀속 1) · mm-lanemig-pre · merge-migx(c) · mm-apps(c) 귀속 · merge-idem +승인 귀속(2.39.0 같음) · bo-hide(c) · bo-pkg-edit(c) 귀속 · 승인 목록 없는 merge-mig · merge-newapp 귀속(새로 막음) · `DJR_SOURCE_GIT_TIP` 은 게이트 사본에서만(git 작업 트리 직접 실행 BASE=TIP=HEAD 에서 app-b · idem-new 2) |
| A N1 · R2 · R3 | to-dup 둘째 위반 귀속 · ch-swap(c) · rs-swap(c) 귀속 · rs-move 귀속 줄이 새 연산 · cc-ign · cc-part · cc-add · rs-moveonly 잔존 · merge-m +승인 유입 · 채널 끊김은 합성 줄 · 단위 `n1_unit.py` 18/18 |
| A F4-46 | s1 · s3 · m3 · skel-cas(c) ⓓ 신규 1 → 0 · m1 · m2 · s2 · s4 · s5 1 그대로 · exit 같음 |
| A 시험 · 변이 | `registry_gate_smoke` 66 + 새 사례 · 표 45 의 R1 · R2 직렬 대조(설계된 변화 5 줄 — 직렬 사본 덧대기 또는 워커 1 대조로 · 기본 TMPDIR 에서 귀속 493 → 495 · 레코드 493 → 497 · 대응 없는 줄 2 → 0 · choices · response-schema-bypass 합성 줄이 계약 줄로) · `anchor_diff_smoke` 142 + 새 · 기존 변이 11 + 16 붉음 · 새 변이(초안 §10 · v5 셋 더함) 붉음 · 시험 하네스는 작업 트리 안 TMPDIR 를 쓰지 않음 |
| B 장난감 | t485 33 → 16 · r485 27 → 16 · r485c 51 → 16 · r485e 13 → 6 · t257 8 → 5 · r257 6 그대로 · r257b 7 → 3 · t191 15 → 11 · r191 9 → 7 · 시험 초안 8 녹색 · 변이 21 붉음 |
| C 글 | 유입 판 글을 옮긴 장난감 R1(40자 · 9자 목록) «v0» · R2 `(지움)` 이 pre-gate `approved_inflow` 와 같음 · 새 · 고친 이름표 G12 새 적중 0(R-3613 은 이미 `DRIFT_REVIEWED` 등재) |
| 현장 A(게이트) | `--anchor HEAD` · `HEAD~10`: 표 `check-app-container.py \| 2 \| 0` → `0 \| 0` · 거짓 해소 1 → 0 · 그 밖 차이 0 · 승인 머지 꼴 복제: 차이는 거짓 해소 하나 |
| 현장 B(검사기) | #485 69 → 38(새로 묻는 이름 0) · #257 120 → 74(더한 줄 0) · #191 4 → 0 · 그 밖 규칙 줄 byte 같음 |
| 전체 | `fixture_matrix` 171 · `field_report_checker_smoke` 172 + 새 · `findings_count` 73(port-adapter 지문 하나 갱신 `b0c0ad90cfce6b9e` → `423cf2d5c9625d1d`) · `checker_baseline` 73/73 · `checker_cross` 차이 0 · `construct_drift` 8/8 · `git_touched_smoke` 90 그대로(골든 다시 뜨지 않음) · pregate · refactor_audit 픽스처 PASS · `make verify` 6/6 · `make verify-mutation` 전부 red |

## 멈출 기준

- 구현 중 장난감 · 현장 수치가 위 표와 다르면 그 갈래를 멈추고 보고한다(설계를 고칠지 구현을 고칠지는 그 뒤에).
- 새 판정이 정상 코드를 새로 막으면(아래 «새로 막는 것» 밖의 새 붉음) 그 갈래를 멈추고 알린다.
- 검토 차단이 셋째 확인에도 닫히지 않으면 멈추고 묻는다.
- 그래프 글 고침이 이미 정한 결정(D39 · 11-16 F4-95 결정 · 11-14 admin 결정)과 부딪치면 멈추고 묻는다.
- 장부 다시 읽기에서 이 판 범위에 닿는 새 보고가 나오면 범위를 다시 묻는다.

## 새로 막는 것 · 푸는 것(2.39.0 대비 · 일부러)

- **새로 막는 것**: 레인이 legacy 평면 앱에 더한 마이그레이션 · 새 평면 앱 · legacy 멱등 파일 고침(2.39.0 게이트는 커밋 · 미커밋 모두 놓침 — 이제 앵커부터의 변경으로 귀속) · 계약 문법 검사기 일곱에서 legacy 가 있는 저장소의 새 위반(같은 주어에 하나 고치고 다른 하나 더함 포함) · 게이트 안 fail-closed 검사기에서 레인 변경이 다른 파일에 만든 새 줄(legacy 없는 저장소에서는 2.39.0 도 같음) · 승인 목록 없이 main 머지로 들인 평면 앱 · 마이그레이션(게이트의 «미승인 머지 = 레인 편집» 정책) · legacy 평면 앱의 첫 `migrations/` 폴더(직접 실행) · arrange 점검에 `기준선 판` 이 왔을 때 작업 트리 시험 파일 · 제품 경로 실존을 `기준선` 근거로 쓰는 것(F4-45 · 지금도 뜻으로는 틀린 일).
- **푸는 것**: 앵커 사본의 거짓 «legacy 해소» · 앵커에 실행 문서가 없을 때 멱등 검사기 거짓 귀속 · 승인 머지가 그대로 들인 계약 위반(승인 유입 기록) · 지움만인 파일의 ⓓ 수 칸 줄음 · ⓓ#257 확인 뒤 값만 돌려주는 return · ⓓ#191 묻는 동사 머리 조회 이름 · ⓓ#485 원시 값 · Enum 반환 이름(모호 동사 아님) · arrange 점검 역할이 받은 판의 시험 쪽 파일을 git 세 꼴로 읽음 · 판을 실은 점검끼리 재사용 때 시험 쪽 해시 대조(㉣) 생략(F4-45).

## 받아들이는 한계(요지 — 설계 초안 각 절 «남는 걱정»)

- F4-27: 대상 저장소에 이미 추적된 기록 파일은 주인 몫(지우기 · 그대로 — 배포 보고에 알림).
- F4-28 · N1: legacy 버킷에 새 파일을 더한 꼴은 게이트 통과(직접 실행은 막음 · 2.39.0 같음) · choices-literal 같은 파일 같은 `모델.필드` · transient-overmapping 같은 파일 핸들러에서 하나 고치고 하나 더한 꼴은 줄 글자가 같아 잔존(2.39.0 같음) · `[#N]` 줄이 있는 검사기의 계약 꼬리는 차분 밖 · 순번 줄은 출처 · 자매 판정에서 귀속 유지(드묾 · fail-closed) · gitignore 된 멱등 파일 · 직접 실행은 HEAD 대비 그대로(커밋한 뒤 직접 실행은 0) · G2 배너의 «legacy 잔존 N건» 이 커질 수 있음(판정 무변).
- F4-46: #547 ⑶ 엔티티 폴더에 새 파일이 생긴 실행은 엔티티 수를 줄였어도 ⓓ 신규(보수 쪽).
- 승인 머지: 레인 문서 «멱등성 미요청» + main 이 들인 멱등 파일은 귀속(2.39.0 같음 · 이중 원인) · 버킷 파일 이름에 `)` 가 든 드문 꼴은 짝이 서지 않아 귀속(막는 쪽) · G2 보고의 «승인 유입» 절에 줄이 새로 뜸(보고가 길어짐 · 판정 무변).
- 승인 머지가 들인 마이그레이션 · `apps.py` · `models.py` 의 **내용**을 레인이 바꾸면(연산을 더해도) 게이트도 직접 실행도 보지 않는다(검사기 정의 «새 파일» · 2.39.0 같음 · v5 시제품은 귀속하던 꼴 · 운영자 처리 3) · 같은 경로를 main 과 레인이 함께 더한 add/add 충돌 해소분 · 레인 작업이 main 을 거쳐 돌아온 꼴도 main 몫으로 봄(드묾).
- 게이트 표지: `DJR_COMMITTED_SNAPSHOT` 은 값이 검사기 뿌리와 같을 때만 믿지만, 사람이 대상 경로 그대로 손으로 주면 fail-closed 가 꺼진다(게이트 밖 수동 지정 · 문서화된 변수 아님).
- F4-26: 도움 메서드 안의 바뀜은 보지 않음 · 묶은 이름은 그대로 묶은 꼴만(첨자 · `or` · 두 번 건넌 별칭 · 원소 별칭은 못 봄 · 현장 0).
- F4-32: 바꾸는 동사 머리(update · change · set · edit · cancel) · 그 밖 머리(search · fetch · show · read · load) + 명사 접미는 계속 물음.
- F4-95: 원시 값 · Enum 을 돌려주는 명사 이름 명령은 검사기가 놓침(사용자 결정 · 감수 몫) · `enum` · `django` 밖 Enum 꾸러미를 기저로 둔 클래스는 물음 · 값 타입 이름(`UUID` · `Decimal`)은 끝 이름만 봄 · 목록 밖 동사 소음(현장 25/38 · 신고 밖).
- F4-29: LLM 자기 스캔이라 효과를 재기 어려움(다시 나면 리뷰어 항목).
- F4-45: 이 실행과 main 이 같은 시험 쪽 파일을 고쳐 자동 머지된 꼴은 기준선 판 그대로(pre-gate 와 같은 사각).

## 문서 · 요청 가이드

- `docs/master/master.html` — 기준 판 줄. 게이트 설명(«이번 런 = 앵커부터» · 계약 검사기 판정)을 싣는 문서가 있는지 grep 하고 있으면 고친다.
- README — 기준 판 줄이 없어 바뀔 것 없음(구현 때 확인).
- 요청 가이드(`dddjango/REQUEST_GUIDE.md`) — 바뀔 것 없음 예상(요청 칸 · 좋은 예 · 나쁜 예 · 플러그인이 묻는 일 그대로 · 포트 메서드 이름 규칙은 설계 · 감수 쪽 글).
- 손 글: `workspace/design/2026-08-11-predicates.md`(B) · 트리 명세는 바뀔 것 없음(구현 때 확인).
- `docs/DEVELOPMENT.md` §3 체크리스트 8 에 한 줄(G) — «계약 문법 검사기의 진단 글에 줄 번호 · 내용 목록처럼 흔들리는 칸을 더하면 `registry_gate` 계약 줄 짝의 정규화(`_contract_stable`)에도 더한다 — 아니면 legacy 가 귀속으로 뜬다». CLAUDE.md — 바뀔 것 없음.

## 장부(사용자 로컬 · 커밋하지 않음)

- F4-26 · 27 · 136 · 28 · 29 · 32 · 45 · 46 · 95 — 2.40.0 수리 처분 줄(설계 초안의 처분 문장 초안).
- N1 ~ N3 은 장부 밖(재현 중 운영자가 찾음) — 판 기록에만.

## 되돌릴 수 없는 것

- 없음(배포는 `make release` · push 로 판 이력이 남고 다음 판으로 고칠 수 있다).

## 걸릴 시간(어림)

- 구현(셋 나란히) · 넣기 · 행동 시험 · 현장 재측정(게이트 한 실행 20 ~ 30 분) 3 ~ 4 시간 · 구현 검토 · 고침 · 다시 잼 1 ~ 2 시간 · 체크리스트 8 · 봉인 · `make verify` + mutation · 배포(릴리스 클론 안 verify 한 번 더) · 기록 2 시간 — 모두 7 ~ 9 시간.

## 설계 독립 검토 처분(요지)

- c(글): 차단 0 · 중요 5 · 사소 9 → 좁은 재확인 1(새 중요 2 · 사소 1) → 닫힘.
- b(검사기): 차단 1(F4-95 — 운영자 «질문 생략» 을 거두고 사용자 결정) · 중요 2 · 사소 5 → 재확인 1(새 중요 2 · 사소 6) → 재확인 2(사소 2 · 구현 때 반영) → 닫힘.
- a(게이트): 차단 1 · 중요 8 · 사소 5 → 재확인 1(새 차단 1 · 중요 1 · 사소 5) → 셋째 확인(R2 ~ R7 닫힘 · 차단 1 남음(승인 머지가 들인 마이그레이션을 레인이 같은 옛 앱 다른 파일을 고친 실행에서 귀속) · 사소 3) → 사용자 «가.» → v5 → 넷째 확인(차단 0 · 중요 1 · 사소 1 — 둘 다 구현 때 고치고 행동 시험 · 구현 검토가 장난감으로 확인) → 닫힘. 처분과 다른 자리에서 고친 둘(승인 머지 출처 재실행에 끝 커밋 · 짝은 흔들리는 칸만)은 셋째 확인이 받아들임.
- 차단 · 중요는 모두 운영자가 장난감 · 사본으로 재현한 뒤 처분했다(`pan3-1116/op-rev/DISPOSITION.md`).

## 계획 검토 처분(v1 → v1.1)

- 계획 v1 독립 검토: 차단 0 · 중요 5 · 사소 11 — 모두 받음(운영자가 시험 머리 · 도구 코드로 근거 확인). 검토자가 a v5 + b v3 를 합친 시제품으로 fixture_matrix 171 · baseline 73/73 · findings_count 72/73(지문 하나) · cross 차이 0 · smoke 172 중 1(물음 상수) · registry_gate_smoke 66 · 표 45 중 5 · 변이 전부 붉음 · anchor_diff_smoke 142 · pregate 셋 녹색을 돌려, 한 단위만 넣었을 때 붉음의 합집합만 남는 것을 확인했다.
- 중요: M1 직렬 대조 R1 · R2 는 저장된 기대값이 아니라 옛 직렬 게이트 대조 → 덧대기 또는 워커 1 대조로(3 단계 A) · M2 N2 · S2 사례 · 변이는 `registry_gate_smoke` unittest 로(`git_touched_smoke` 는 옛 코드 골든) · M3 R-1123 라벨은 G 몫 · M4 승인 머지가 들인 파일을 레인이 고친 꼴을 legacy 앱 · 새 앱 같게 «유입» 으로(운영자 처리 3 · 검사기 정의 «새 파일» · 2.39.0 같음) · M5 밝힐 것 1 ~ 9.
- 사소: B 시제품 판 · F4-27 수치 자리 · 변이 표 수와 F4-27 변이 둘 · 단위 시험 패치를 함께 넣기 · 새로 막는 것 글 · c 의 막는 것 · 푸는 것 · a 한계 둘과 DEVELOPMENT 한 줄 · F4-95 결정 줄 모호 동사 · G12 «새 적중 0» · 감싸개 목록 · 구현 검토에 넘긴 처분 장난감 이름.
- 좁은 재확인(v1.1): 차단 0 · 중요 1 · 사소 4 — 모두 받음(v1.2). R1 승인 머지가 둘이면 «그 머지 ^2» 단수로는 mm-two 가 거짓 귀속(운영자가 장난감 두 머지의 ^2 트리로 확인) → «참여 승인 머지 가운데 어느 ^2 에라도» · R2 T(줄을 만든 새 파일) · S(레인 몫) 두 집합 · 폴더 tree 는 T 가 빌 때만 · R3 옛 글 셋 · R4 운영자가 넷째 확인 검토자와 다르게 정한 자리 · 일부러 여는 꼴 한계 줄 · R5 장난감 만드는 법 경로.
