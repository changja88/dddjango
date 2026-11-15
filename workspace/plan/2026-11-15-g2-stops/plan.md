# dddjango 2.39.0 — G2 멈춤 여섯 · 글 어긋남 둘 · 도메인 우회 읽기 값 출처 · 계획 v2.1 (2026-11-15)

상태: 계획 v2 — 설계 v2(작업본 · 현장 이름이 들어 있어 scratch 에만 둠 · 배포 뒤 이 폴더에 정리본) 위에 섰다. 설계 독립 검토 셋(차단 1 · 중요 14 · 사소 24)은 모두 받아 고쳤고, 차단 · 중요는 좁은 재확인에서 닫혔다(F4-165 는 넷째 확인 뒤 줄이는 안). 계획 v1 독립 검토(차단 0 · 중요 6 · 사소 8)를 모두 반영했고, 좁은 재확인에서 중요 여섯이 닫혔다(새 사소 여섯도 반영 · v2.1). **사용자 계획 승인 «진행»(11-15 19:57)** → 구현 중.

## 결정

- **사용자**:
  - 2.39.0 묶음 «나.»(11-15 14:56) — G2 멈춤 여섯(F4-160 · F4-162(+F4-56 ②) · F4-171 · F4-168 · F4-169 · F4-179 + 새 정본 ⓓ#607 물음 소음) + 덤 둘(F4-165 · F4-166) + F4-180.
  - F4-179 «나.»(11-15 01:41) — 다음 작은 판(이번 판).
- **운영자 처리**(질문 생략 · 설계 처리 · 이의 시 뒤집음 — 계획 승인 때 밝힌다):
  1. F4-180 — 도메인 우회 읽기 · admin 은 도메인을 모르는 자리로 둔 채, 도메인 값으로 거르거나 견줄 때 **모델 클래스가 VO 멤버의 `.value` 로 묶은 `Final[str]` 값 속성**을 쓴다. 모델을 거쳐 도메인 이름(VO 클래스 · 멤버)을 가져오는 꼴은 막는다. 모듈 수준 `.value` 이름과 `str` · `int` 주석 꼴은 막지 않는다(검사기와 글이 같은 말). 클래스 몸 안 주석 없는 `.value` 는 막는다(houserules 어노테이션 의무).
  2. F4-162 — 레인이 승인 머지로 들어온 폴더 안을 고친 줄은 지금처럼 레인 몫(멈춤). 손대지 않은 폴더의 줄만 유입으로 연다.
  3. F4-169 — «DB 표가 있는 모델은 어디서 왔든 막는다» · 모델인지 알 수 없는 이름도 막는다 · 모델이 아님이 드러난 이름(기저 없는 클래스 · Enum · 데이터클래스 · TextChoices · QuerySet 등)만 받는다.
  4. F4-165 — 정적 검사(린터 · 포매터 · 타입 검사) green = 그 파견을 받았을 때의 커밋 대비 새 진단 0. 묶음 창 · nit 치환 파견은 준 명령 · 치환만 하고 이 검사를 돌지 않는다 — 그 기계 치환이 낸 lint(import 차례 · 줄 길이 · 동작 무관)는 커밋하는 실행이면 다음 파견 기준선에 들어 감수 몫으로 남고, 커밋하지 않는 실행이면 다음 coder 파견의 새 진단으로 세져 그 파견이 고친다(owner 가 아니면 줄째 보고 · 조정자 글은 고치지 않음). owner 가 아닌 파일의 새 진단은 coder 가 고치지 않고 줄째 보고한다.
  5. F4-161 보류 · F4-172 이미 고쳐짐(2.34.0).
- 판 번호 **2.39.0**(minor) — 새 규범(coder 완료 조건 · 모델 쪽 파생 값 · #356 첫 그래프 문장 · architect 파일 계획)과 검사기 판정 변경. dddjango-web 은 바뀌지 않는다.

## 사용자에게 보이는 흐름(전 → 후)

| 보고 | 2.38.0 | 2.39.0 |
|---|---|---|
| F4-160 | BC 오류 모듈을 비우거나 지우면 #2 기준선이 서지 못해 옛 중복 줄이 «신규» 로 G2 를 멈춤 | 앵커에 모듈을 넣은 렌더 ∩ 비운 렌더로 기준선이 섬 → 옛 줄은 기존분 |
| F4-162(+56 ②) | 승인 머지로 들어온 폴더 · 없는 폴더 주어의 줄이 유입 증명을 못 해 G2 멈춤 | 폴더 tree 를 견줘 손대지 않은 폴더의 줄은 유입 · 레인이 고친 폴더는 그대로 멈춤 |
| F4-166 | 목록 칸만 줄어든 줄이 ⓓ «신규» 후보로 섬 | 짝을 지어 legacy(ⓓ 후보 줄만 · 위반 줄 · exit 그대로) |
| F4-168 | 선택 밖 컨트롤러 모듈의 라우트가 #126 helper 로 세져 G2 멈춤 | 선택 밖 라우트는 helper 로 세지 않음 · 선택 컨트롤러가 이름 · 모듈 속성으로 가리켜 부르는 라우트는 남김 |
| F4-169 | 시험이 models 모듈의 모델 아닌 이름을 import 해도 #53 | DB 표 모델 · 모를 이름은 막고 모델 아님이 드러난 이름만 받음 |
| F4-171 | 기술 폴더 판정이 설치 패키지에 따라 갈려 #396 이 섰다 없어졌다 | 저장소 안 import 글자로 판정 · 설치 패키지와 무관(표준 라이브러리 이름 판정만 파이썬 판에 따름) |
| F4-179 | 플러그인이 고정한 오류 표 파일이 #415 · ⓓ#607 에 걸림 | 고정 파일은 뺌(표 파일은 클래스가 없을 때만) |
| F4-165 | 완료 조건의 정적 검사가 «절대 green» 이라 coder 가 옛 파일 서식을 고침 | 파견 시작 커밋 대비 새 진단 0 · 옛 줄 서식은 고치지 않음 |
| F4-180 | 검사기가 «도메인 값을 글로 다시 적은 상수» 로 coder 를 몲 | 모델의 `.value` 파생 값 속성으로 거름 · 모델을 거친 도메인 이름 가져오기는 막음 |

F4-180 쓰는 꼴(`implementation-django` §2.5 새 블록):
```python
class OrderModel(models.Model):
    STATUS_PENDING: Final[str] = OrderStatus.PENDING.value     # 모델이 VO 에서 묶은 값
# 도메인 우회 읽기 · admin
OrderModel.objects.filter(status=OrderModel.STATUS_PENDING)    # 받음
OrderModel.Status.PENDING  # 모델 안 `Status = OrderStatus` 별칭으로 도메인 이름을 쓰면 막음(#356 · #668)
```

**새로 막는 것**(2.38.0 은 통과 · 설계가 일부러 막음):
- F4-169: `import <꾸러미>.models` · `from <저장소 안 꾸러미> import models`(시험이 models 모듈째 가져오는 꼴).
- F4-171: 표준 라이브러리만 import 하는 기술 모듈이 #415(현장 클론 1 줄 · main 에 이미 있는 줄) · 같은 기술 폴더 안 상대 import(`from ..ninja import x`)만 하는 모듈이 #415 · `__init__.py` 만 있는 기술 이름 폴더가 #396.
- F4-180: 모델 클래스 안 도메인 별칭(별칭 없는 `import a.b.c` 로 든 금지 자리 아래 사슬 포함) · 꾸러미 `__init__` 재수출로 가져온 도메인 이름 · 값 타입이 도메인 객체인 `.value`(`Final[RefundRule]`) · 클래스 몸 안 주석 없는 `.value` · 승격된 우회 읽기 폴더의 부품 모듈.
- (그대로 막음 — 2.38.0 도 막던 것: F4-169 기저를 끝까지 풀어도 모르는 클래스 · F4-179 클래스가 든 표 파일 #415.)

**2.38.0 대비 푸는 것**(일부러):
- F4-168 — 선택 컨트롤러가 글자로 가리키지 않는 위임(문자열 · `getattr` · 동적 import · 다른 모듈 함수나 다른 모듈의 별칭(`handler = get_other`)을 거친 위임)은 helper 로 세지 않는다(2.38.0 은 셌다).
- F4-180 — admin 이 모델 모듈 수준의 `.value` 파생 이름(`str` · `int` · `Final[str]` 주석)을 쓰는 꼴은 #668 이 받는다(2.38.0 은 막았다 · 운영자 처리 1). admin 이 모델 모듈을 `import *` 로 들여도 그 모듈의 `__all__` 에 금지 이름이 없으면 받는다(2.38.0 은 모델이 도메인 이름을 import 하면 막았다 · `*` 는 실제로 들어오는 이름만 본다).

## 단위 · 맡은 파일

| 단위 | 보고 | 맡은 파일(+ Codex byte 미러) |
|---|---|---|
| B 기준선 · 귀속 | F4-160 · 162 · 166 | `dddjango/scripts/anchor_diff.py` · `registry_gate.py` — 시제품 v2 + B 재확인 사소 둘(①′ 거름에 검사기의 제외 폴더 이름 · 비우기 단계 쓰기 실패는 아래 칸으로) |
| C 검사기 오판 | F4-168 · 169 · 171 · 179 | `check-api-error-controller-contract.py` · `check-business-vocabulary.py` · `business_vocab.py` · `check-naming.py` · `check-port-adapter-pairing.py` 죽은 인자 덩이(R 위에 얹음) |
| R 값 출처(검사기) | F4-180 | `checker_target.py` · `check-context-isolation.py` · `check-port-adapter-pairing.py` · 픽스처 `port_adapter_pairing/bypass_domain/`(새) · `context_isolation/admin_imports/`(더함) |
| G 그래프 · 글 | F4-180 · F4-165 · F4-162(글) · F4-169 · F4-179(글) | `ontology/rules/*.ttl` 여덟(implementation-django-final · discipline-cleancode-final · discipline-houserules-final · discipline-houserules-skill · agent-discipline-reviewer · agent-design-architect · agent-coder · command-dddjango) · `ontology/wiring/*.ttl` 다섯(aliases · discipline-houserules-final · implementation-django-final · agent-design-architect · agent-coder) · ISSUED · LEDGER · target-counts · rulepack + Codex · q4 골든 · 투영 md · `workspace/reference` 미러 · Codex 같은 뜻 다섯 파일 여섯 자리(coder · discipline-reviewer · design-architect · dddjango 두 자리 · discipline-houserules) · 산문(mkrev2 #53 · #415 괄호 · admin · 우회 읽기 칸 → `file_tree.html` · decision-record 되돌림 · 트리 명세 #53 · #415 span · #356 · #668 행 글 + span · 소유 지도 #356 · #668 비고) · Makefile 한 줄 · G12(`rulepack_smoke.py` DRIFT_REVIEWED · `scope-limit-norms.md` N 행) |
| 시험(운영자가 모음) | 전부 | `field_report_checker_smoke.py` · `fixture_matrix.py` · `anchor_diff_smoke.py` · `registry_gate_smoke.py` · `findings_count_matrix.py` · EXPECTED 도구 · `pregate_symbol_kinds.json` · 맡은 사람 없는 기대값 grep(`pregate_fixture_run.py` 등) |

- 새 Norm 다섯(R 넷 + T 하나 · ISSUED 끝 R-3759 뒤로 차례 채번) · 표현 고침 여덟(R 다섯 — R-1409 · R-1399 · R-3757 · R-0968 · R-0978 · B 셋 — R-0306 · R-3441 · R-3131) · 새 블록 하나(`implementation-django` §2.5) → target-counts NormShape +5 · WorkShape +5 · ExpressionShape +13 · BlockShape +1 · AliasEntryShape +1(`rule#356`).
- 맡은 파일 어림: 검사기 · 도구 아홉(+ Codex 미러 아홉) · ttl 열셋 · 투영 md 여덟 · Codex 같은 뜻 다섯 · 산문 넷 · 픽스처 둘 · 시험 도구 여섯 · 소성물 둘.

## 일하는 법 · 차례

1. **계획 승인** — 10 줄 요약 · «밝힐 것»(위 운영자 처리 1 ~ 4) · 명시적 «진행».
2. **장부 다시 읽기**(계획 확정 때) — 새 F4 가 이 판 범위에 닿으면 범위를 다시 묻는다.
3. **구현 — Claude 구현자 넷(B · C · R · G), 각자 사본에서.** 사본 = `workspace/scratch/next-pick-1115/wt-<단위>/`(main HEAD 에서 뜬 detached git worktree · `.venv` · `.venv-probe` 는 본 저장소 것을 링크하고 `info/exclude` 에 적음 — DEVELOPMENT §7.4 릴리스 클론과 같은 꼴 · 정리 때 `git worktree remove` · `prune`). 구현자는 자기 사본만 고치고 시험한 뒤 diff 를 낸다. 함께 고치는 시험 파일은 패치로 낸다. 시제품 v2 를 출발점으로 쓰되 시제품 주석의 설계 메모는 런타임 글이 아니므로 docstring · 주석을 규칙대로 다시 쓴다.
   - **G 지시문**에는 DEVELOPMENT §3 체크리스트 1 ~ 6 을 그대로 싣는다 — ttl 편집 → 온톨로지 게이트 → `ontology_render.py --apply`(여덟) → LEDGER 재기준선 → target-counts · q4 골든 → `make rulepack`(+ Codex) → graph 절을 고친 skill 의 `workspace/reference/<skill>/reference/final.md` 옛 절을 손으로 바꿈 → `corpus_mirror_sync.py --write` → `--check` → Codex 같은 뜻 여섯 자리 → G12(`rulepack_smoke` 로 새 · 고친 이름표를 대 보고 적중은 DRIFT_REVIEWED + N 행). mkrev2 를 돌리면 바뀌는 `workspace/design/2026-08-07-decision-record.md` 는 되돌린다.
4. **넣기 — 운영자가 차례로**: R(`checker_target` 먼저 · 전 검사기 시험) → C(검사기 넷 + pap 위에 C 덩이) → B → G → 시험 패치. 넣을 때마다 받은 diff 의 파일 목록을 예상 목록과 대조한다(DEVELOPMENT §7.5).
5. **행동 시험** — 단위마다 옛 판(2.38.0 · `6936d053` — `HEAD` 쓰지 않음)이 붉음(또는 놓침)이고 새 판이 녹색 · 대조군 그대로임을 실제로 돌린다(설계 · 검토 · 재확인 장난감 전부 · 아래 수치 표). 넣은 뒤 합친 판으로 합침 시험(smoke · 행렬 · 변이 지점)을 다시 돈다(설계 때 합침 시험은 c2 의 마지막 고침 앞 판이었음).
6. **현장 줄 차이** — 하네스는 설계 때 것을 쓰되 시제품 경로를 박아 둔 스크립트(`b2/run_real.sh` · `c2/run168-replica.sh` · `c2/run-vocab-replica-v2b.sh`)는 scripts 경로를 인자로 바꿔 쓴다(`r2/run_copy.sh` 는 이미 인자):
   - B: `next-pick-1115/b2/run_real.sh`(레인 커밋 둘을 리허설 클론에서 `--shared` sparse 복제로 꺼내 잼 · 인자 `f160-real-args.txt` · 승인 머지 `real-sse-approved.txt` · 클론에서 checkout 하지 않음 · 복제 둘은 설계 때 지웠으므로 운영자가 `run_real.sh` 머리 주석의 두 커밋으로 다시 만듦 · 다 쓴 복제는 지움).
   - C: `c2/run-vocab-replica-v2b.sh`(파이썬 셋 — brew python3 · 클론 `.venv` · `next-pick-1115/c-checkers/venv-jwt` · 수치는 파이썬마다 표대로) · `c2/run168-replica.sh`(컨트롤러 렌더).
   - R: `r2/run_copy.sh`(검사기 27).
   - 검사기 조합: 단위 판 + 2.38.0(구현자 사본 단계) · 합친 main + 2.38.0(넣은 뒤).
   - TMPDIR 는 기본값 그대로(작업 트리 안이면 `--anchor` 재실행이 더 붉은 쪽으로 떨어진다). `DJR_VIOLATIONS_DIR` 은 작업 폴더. 리허설 클론은 읽기만(그 폴더에서 cd · git 안 함).
7. **구현 독립 검토** — Claude 검토자 둘(코드 · 글). 설계를 주지 않고 코드 · 글과 장난감 하네스를 준다. 질문에 «커밋 뒤에도 같은 결과인가»(B 는 HEAD · `git status` 를 읽음)를 넣는다.
8. **고침 · 좁은 재확인** — 차단은 고친 뒤 좁게 다시. 셋째 확인에도 안 닫히면 멈추고 묻는다. 고친 뒤 장난감 · 현장 수치를 다시 돈다.
9. **체크리스트 8** — Codex byte 미러 → 골든 · EXPECTED(`findings_count_matrix` · `checker_baseline_matrix` · `checker_cross_matrix --emit-expected` · `construct_drift_report --emit-expected`) → **`gen_pregate_symbol_kinds` 는 마지막 검사기 고침 뒤에** → 맡은 사람이 없는 시험 파일의 기대값 grep(예: `pregate_fixture_run.py`) → 봉인. `claude plugin validate` 는 필요 없다(매니페스트 · 구조 · 새 설치 파일 0).
10. **커밋 · 검사** — 경로를 하나씩 `git add` · 사용자 로컬 파일 커밋하지 않음 · `make verify` 전체 + `make verify-mutation`(probe old-13 부하 흔들림은 단독 재실행으로 가림).
11. **배포 전 문서** — `docs/master/master.html` 기준 판 줄 · mkrev2 → `file_tree.html`(3 단계에서 G 가 고친 것 확인) · README 는 기준 판 줄이 없어 바뀔 것 없음 · `work_flow.spec.json` 닿는 낱말 없음.
12. **장부 다시 읽기**(배포 직전) → push → 깨끗한 클론 `make release`(2.39.0) → 노트 → 봉인 chore.
13. **배포 뒤** — 판 기록 `plan-2.39.0.md`(검토 처분 · 검사 수치 — 마지막 실행 값만) · 설계 정리본(현장 이름 걷음) · 장부 처분 줄 · `work_list.html`(F4-160 · 162 · 56 · 165 · 166 · 168 · 169 · 171 · 179 · 180 · 172 지움 · 161 보류 표시) · 요청 가이드 확인 한 줄 · 배포 보고에 «pre-gate 재예보 필요» 진행 레인(`dddjango/scripts` 가 바뀌어 툴체인 digest 가 바뀜 — DEVELOPMENT §6 릴리즈 창) · 진행표 둘.
14. **정리**(DEVELOPMENT §7.4) — `next-pick-1115/`(시제품 · 장난감 · 구현 사본 worktree · `plan-review/`) · 릴리스 클론 · `/tmp/djr-verify` · 띄운 프로세스. 리허설 클론은 시험 드라이브 준비 뒤 지운다.

## 검사 · 수치 기준(구현이 설계 v2 와 맞는지)

| 잰 것 | 기대(설계 v2 재측정 · 계획 검토 합친 판 실측) |
|---|---|
| B 장난감 F4-160 | P · Q · U 2 → 0 · R · S · S2 2 → 2 · S3 0 · T1 2(신규 1 · 한계) · T2 · T2c 2(`측정 무효(M^1)` · 옛 한계) · T3 2 → 0 · T4 2 → 0 · T6 ~ T9 2 → 0 · 제외 폴더 이름 BC(generated · tests)에서 ①′ 이 섬 · 비우기 쓰기 실패는 traceback 아닌 아래 칸 |
| B 장난감 F4-162 · 166 | A · B · C · G1 · G4 · G5 · G7 · Y 2 → 0 · D · E · F · G3 · G6 · Q18 · R7 2 → 2 · N1 ~ N3 세 판 같음 · ⓓ 신규 1 → 0 |
| B 변이 | 사다리 직접 시험 넷 OK · `norestore` · `noguard` · `nogate` · `nofilter` · `noprime` · `addonly` · `emptyonly` · `noren` 각자 죽음 · F4-166 `untouched` 되돌림 죽음 |
| B 시험 | registry_gate_smoke 62 OK(행 45/45) + 새 사례 · anchor_diff_smoke 126 — 붉던 11 은 단언 고침 13 자리(Q19 둘 · RenamedBc 아홉 · Q18 하나 · `assert_partition` 하나)로 녹색 + 새 사례 |
| C 장난감 F4-168 | t1 · t3 · t4 · toyB 2 → 0 · 대조 t0 · t5 · t8(이름 위임) · t8a · t8b · t8c · t168m(모듈 속성 위임) 2 그대로 · t2 2(한계) |
| C 장난감 F4-169 | 모델 · 모를 기저 m1 ~ m5 · n1 · n2 · q6 막힘 · 모델 아님 열셋(기저 없음 · 데이터클래스 · QuerySet · TextChoices · Enum 등) 받음 · 모델이 이기는 섞인 기저 막힘 |
| C 장난감 F4-171 · 179 | toy171-B brew/jwt 2/0 → 0/0 · 이름공간 폴더 nsdir 0/0 · 진짜 가림(`__init__.py` · 뿌리 `<lib>.py`) #396 두 파이썬 · toy179-only · toy179-237 2 → 0 · 숨긴 클래스 표 hidden 2(#415) · Schema 표 0 |
| R 장난감 | 52 꼴 표(`r2/r180b-summary.txt`) 그대로 · 새 픽스처 `bypass_domain` 17 줄 · `admin_imports` 28 줄 · 변이 30 죽음 · 기존 픽스처 판정 차이 0 |
| T 장난감 | 줄 밀림 새 0 · 같은 진단 하나 더 새 1 · 파견 중 커밋 뒤 새 1 · Makefile 대조 변이 ERROR |
| 현장 B(`run_real.sh` · B 판 + 2.38.0 검사기 — 구현자 사본 단계의 기대 · 합친 main 단계는 같은 하네스로 다시 재어 차이를 C · R 판정 변화로 설명할 수 있어야 함) | 오류 모듈 비움 레인: exit 2 신규 3 → exit 0 기존분 3 · 같은 레인 다른 판: byte 같음 · ⓓ 목록 레인: ⓓ 신규 1 → 0 · 폴더 레인: 폴더 줄 7 → 유입 6 + 귀속 1(귀속 41 → 35 · 승인 유입 42 → 48) |
| 현장 검사기 | vocab(brew · `.venv`) #396 셋 · #53 한 줄 빠지고 #415 하나 섬 · venv-jwt 는 #396 둘 빠짐 · naming ⓓ#36 넷(venv-jwt 셋) 빠짐 · context-isolation #668 61 줄 꼬리 글만(목록 칸 같음) · 컨트롤러 공개 · 내부 렌더 byte 같음 · 그 밖 2.38.0 대비 차이 0 |
| 전체 | `api_error_backstop_matrix` 928/928 · `fixture_matrix` 170 + R 레인 둘 · smoke 165 + 새 클래스 · findings_count 73(지문 둘 갱신) · checker_baseline 73/73 · checker_cross 차이 0 · construct_drift 대표 하나 갱신(context-isolation) · 변이 지점 기존 302 + 새 변이(R · B · C) 모두 정확히 한 곳(R 옛 셋 다시 겨눔 뒤) · folder_group 567/568 · pregate · refactor_audit 픽스처 PASS · `make verify` 6/6 · `make verify-mutation` 전부 red |

## 멈출 기준

- 구현 중 장난감 · 현장 수치가 위 표와 다르면 그 갈래를 멈추고 보고한다(설계를 고칠지 구현을 고칠지는 그 뒤에).
- 새 판정이 정상 코드를 새로 막으면(위 «새로 막는 것» 밖의 새 붉음) 그 갈래를 멈추고 알린다.
- 검토 차단이 셋째 확인에도 닫히지 않으면 멈추고 묻는다.
- 그래프 글 고침이 이미 정한 결정(11-14 admin 결정 · 리팩토링 적용 범위 Override 56 · #326 D1′)과 부딪치면 멈추고 묻는다.
- 장부 다시 읽기에서 이 판 범위에 닿는 새 보고가 나오면 범위를 다시 묻는다.

## 받아들이는 한계(요지 — 설계 v2 각 절 «남는 한계»)

- F4-160: ①′ 거름이 사본 안 심링크 BC 폴더는 거르지 않아 positional 로 내려감(2.38.0 과 같은 결과) · 다른 BC 가 비운 모듈의 스키마를 상속하는 꼴은 2.38.0 exit 2 → exit 1(①′ 은 서고 지금 트리의 동적 오류 꼴 표지가 exit 를 정함 · fail-closed) · 같은 값 주인이 셋인 앵커에서 하나를 비우면 대표 주어가 옮겨 신규 하나가 남음(2.38.0 보다 덜 붉음 · fail-closed) · main 이 다른 #2 줄을 함께 들이면 `측정 무효` 그대로 · ①′ 이 서면 앵커 렌더가 한 번 → 두 번(최악 (1 + 2m + 64) × 2 × 약 20 s · m = 승인 머지 수).
- F4-162: 빈 폴더 · 무시 파일만 더한 폴더는 `git status` 에 안 보여 손대지 않은 폴더로 봄.
- F4-166: ⓓ 후보 줄만 바뀜(목록이 같으면 고친 파일이어도 legacy — 2.38.0 동작과 같은 결).
- F4-168: 라우터를 다른 모듈에서 가져온 one-hop 컨트롤러는 2.38.0 처럼 #126 이 남음 · 같은 scope 위임은 옛 한계 · 글자로 가리키지 않는 위임은 helper 로 안 셈(2.38.0 은 셌음 — 일부러 푼 것) · 선택 밖 라우트 이름이 선택 컨트롤러가 쓰는 이름(흔한 `get` 등)과 겹치면 2.38.0 처럼 #126 이 남음(풀리지 않을 뿐 · 새 붉음 아님).
- F4-169: 고정 목록 밖 표준 기저는 «모름»(막힘) · `from django.contrib.auth import models` 꼴(바깥 꾸러미에서 models 모듈째)은 두 판 모두 통과.
- F4-171: 표준 라이브러리 이름 판정은 파이썬 판에 따름(파일 없는 표준 이름 폴더에서만 갈림) · `__init__.py` 만 있는 기술 이름 폴더는 이제 #396 · 함수 안 import 도 셈.
- F4-179: 표 파일에 클래스가 있으면 #415 그대로.
- F4-180: 글 사본 상수는 검사기 밖(감수 ②) · 모델 메서드가 도메인 멤버를 돌려주는 길 · 호출 · 첨자 안 도메인 멤버는 안 따라감 · 추상 기저 모델의 별칭을 상속한 꼴 · 클래스 몸 안 import · 튜플 풀기 별칭 · 쓰는 쪽 지역 별칭(`M = OrderModel`) · 부모 꾸러미에서 `from …driven_layer import django_<bc>` 꼴은 안 따라감(모두 2.38.0 도 놓침) · 한 겹은 자기 `django_<bc>/` 모듈만 · 클래스 몸 주석 없는 `.value` 는 막음 · `__all__` 은 글 목록 대입만 봄(`+=` · 함수로 지은 꼴은 «없음» 으로 보고 모든 이름이 들어온다고 봄 — 막는 쪽).
- F4-165: 묶음 창 · nit 치환 파견은 이 검사를 돌지 않아, 커밋하는 실행이면 그 기계 치환 lint 가 다음 파견 기준선에 듦(동작 무관 · 감수 몫 · 조정자 G2 보고가 따로 옮기지 않음 · 커밋하지 않는 실행이면 다음 coder 파견 몫) · owner 가 아닌 파일의 새 진단은 줄째 보고 · acceptance-tester 가 쓰고 커밋된 시험 파일의 새 진단은 다음 파견 기준선에 듦 · 전체 프로그램 타입 검사 기준선은 판단.

## 문서 · 요청 가이드

- `docs/master/master.html` — 기준 판 줄(11 단계) · `file_tree.html` 은 mkrev2 로 C · R 칸이 바뀜(3 단계 G).
- README — 기준 판 줄이 없어 바뀔 것 없음. `work_flow.spec.json` — 닿는 낱말 없음.
- 요청 가이드(`dddjango/REQUEST_GUIDE.md`) — 바뀔 것 없음(요청 칸 · 좋은 예 · 나쁜 예 · 플러그인이 묻는 일 그대로).
- DEVELOPMENT · CLAUDE.md — 바뀔 것 없음.

## 장부(사용자 로컬 · 커밋하지 않음)

- F4-160 · 162 · 56(②) · 165 · 166 · 168 · 169 · 171 · 179 · 180 — 2.39.0 수리 처분 줄.
- F4-161 — 보류(계기가 2.38.0 에서 사라짐 · 다시 나면 엶).

## 되돌릴 수 없는 것

- 없음(배포는 `make release` · push 로 판 이력이 남고 다음 판으로 고칠 수 있다).

## 걸릴 시간(어림)

- 구현(넷 나란히) · 넣기 · 행동 시험 · 현장 재측정 3 ~ 4 시간 · 구현 검토 · 고침 · 다시 잼 1 ~ 2 시간 · 체크리스트 8 · 봉인 · `make verify`(커밋 뒤 약 25 분) + mutation · 배포(릴리스 클론 안 verify 한 번 더) · 기록 1.5 ~ 2 시간 — 모두 7 ~ 8 시간.

## 설계 · 계획 독립 검토 처분(요지)

- 설계 검토 셋(기준선 도구 · 검사기 · 글) — 차단 1(F4-169 모르는 기저를 모델 아님으로 비켜 줌) · 중요 14 · 사소 24 · 받지 않은 것 0. 모두 운영자가 장난감으로 재현한 뒤 받았다.
- 고침 일꾼 셋(B · C · R) + F4-165 운영자 글 → 좁은 재확인: C 1 회 · R 검사기 1 회 · R 글 1 회 · B 1 회 · F4-165 4 회(셋째까지 차단 0 · 넷째 확인 뒤 넘김 장치를 걷는 줄이는 안). 재확인에서 나온 사소는 모두 받았다(B 의 둘은 구현 때 반영).
- 검토 · 고침 중 드러난 시제품 v1 의 2.38.0 대비 새 구멍(모르는 기저 · 숨긴 표 클래스 · one-hop 위임 · `.value` 값 타입 · index 이동 유입)은 모두 막았다. F4-168 의 글자로 안 가리키는 위임은 일부러 푼 것이라 한계에 적었다.
- 계획 v1 검토(차단 0 · 중요 6 · 사소 8) — 표현 고침 수(여덟) · C 산문 맡김 · 그래프 차례와 처분이 넘긴 두 줄 · 주된 고침 기대값 · 새로 막는 것 · 푸는 것 · 한계 · pre-gate 재예보 · 현장 재는 법(하네스 · 파이썬 · 조합 · TMPDIR) · 구현 사본과 넣는 차례 · §7.5 셋 · 배포 뒤 할 일 · 시간 어림을 모두 반영했다. 검토자가 합친 시제품으로 backstop 928 · fixture_matrix 170 · smoke 165 · cross 0 · baseline 73/73 을 직접 돌려 녹색을 확인했다.
