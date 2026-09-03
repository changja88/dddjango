# rv3-C — pre-gate 차단 승격 배치 ③ 계획 적대 리뷰 · 리뷰어 C(하네스·픽스처·소급 대조)

- 대상: `workspace/plan/2026-09-03-pregate-promotion-plan.md` §1·§3·§4·§5 · 브랜치 `feat/pregate-enforce` HEAD `f369332`(코드 변경 0 — main 대비 docs 6파일).
- 방식: 저장소 읽기 전용(이 파일만 씀) · 라이브 저장소(`~/Desktop/spring_dream_server`·`~/Desktop/kkebi-server`) 읽기만(git 읽기 명령·파일 읽기) · **실행기 소급 실행 0·검사기 실행 0**. 실행한 것은 실행기 모듈의 `parse_spec`/`block_hash` 함수 호출(사본·게이트·git 0회)과 E5 파서 프로토타입뿐 — 스크래치 `scratchpad/rv3C/{e4_precheck.py, e4_reading_versions.py, check_report_proto.py}`.
- 표기: 근거는 `파일:행`. Serena: skipped — 워크트리에 `.serena/project.yml` 없음.

## 0. 판정 요약

| # | 심각도 | 요지 | 근거 |
|---|---|---|---|
| C1 | **MAJOR**(1) + MINOR(3) · 나머지 검증됨 | H2 는 별도 리포트로 추가 가능(base 계수 4 불변). `parse_spec` 이 `(None, [])` 를 내는 조건은 **«마커 부재»뿐**(펜스 유무 무관) — 마커 있음·펜스 부재/언어 불일치/**산문 안 리터럴 마커**는 문법 red(다른 분기), **빈 펜스·주석만 펜스는 `Plan(0행)` → 실체화 0 → exit 4 skip**(E3 «블록 의무»를 빈 블록으로 충족하는 도피 경로 — 픽스처 없음). `update-promoted` 는 mini_repo 를 건드리지 말고 러너가 합성 저장소에 `promo/__init__.py` 를 커밋하는 mid 묶음 판형으로 | `design_pregate.py:634-640,296-330,152` · 실측 표 §1 |
| C2 | 검증됨 + MINOR(2) | `--check-report` 픽스처는 «실제 실행기 출력 + 처분 행 append» 가 옳다(헤더·판정·항목 행은 같은 커밋의 실행기가 만든다 → 형식 드리프트 0). 정규식 초안 5종을 카탈로그 실물 리포트로 13케이스 검증(stale 3 · 해시 패치 0 · 미라벨 3 · corrected 3 · ignored 0 · 표 셀 filtered 0 · 오염 무영향 · 절 이전 처분 3 · 구판 1 · 형식 red 3). MINOR: 절 헤더는 실행기 자기 형식 정규식으로(코디네이터 제목 `## pre-gate 예보 처분` 오인 차단) · 표 셀 형식 수용 여부 성문 | §2 · `scratchpad/rv3C/check_report_proto.py` |
| C3 | **MAJOR**(2) · 나머지 검증됨 | ⑴ §4 «귀속 ID 집합 불변·exit 불변» 의 대조군이 없다 — 최종 명세 해시 ≠ 마지막 절 해시(L4 cb95a1bddb32≠6cf8e2ffdfc3 · L1 ledger:51)라 «현 리포트 마지막 절» 과는 비교 불성립, L3 는 exit 3→비3 이 의도. 대조군 = **구 실행기(설치 cache 2.17.16 = release 5225c57 = 현 HEAD 파일, byte 동일 확인) 동일 입력 A/B** 로 교체. ⑵ reading 기대 좌표 오기 — «승격 부품 update 계획» 이 아니라: 최종본(19b27df)×80431d9 는 **remove 부재 7건**(update 부재 0·승격 예외 1 발동) · update 재라벨 봉쇄 재현은 **78e616a × run 37 기준선 61b56ef4** 에서 **update 부재 24건**. L1~L4 는 정적 사전 계산으로 E4 red 0 확인. 격리 사본 = `git clone` + detached checkout(worktree 불요·라이브 무변경) · `DJR_FINDINGS_JSON` 격리는 `run_gate:1084` 내장(수동 설정 불요) · 라이브 부산물 0 | §3 · `scratchpad/rv3C/e4_*.py` 출력 |
| C4 | 검증됨 + MINOR(2) | 재발행 명령은 `manifest_seal.py --write` **단독**(`--draft` 는 `--check` 전용 플래그 — `main:1401-1404`) · 쓰는 파일 2(`T2-0b-manifest.json` + `2026-08-20-ontology-t2-0b-design.md` FACTS 블록) · `--check --draft` green 조건 7 — 핵심은 «`--write` 가 봉인 대상 마지막 편집 뒤» (initial_state 가 LEDGER/ISSUED/그래프 해시를 품는다 `:811-832`) · «why» 추가는 선택(봉인본에 재방출) | §4 |
| C5 | 검증됨 | E1·E2·E6 문자열에 의존하는 하네스 **0** — `pregate_fixture_run.py` 는 접두 부분일치(`요약: 귀속 0건 · 실존 결손 0건`·`요약: 실체화 0 · 실존 결손 1건`)·`- 판정: 예보 green`·`(권고·비차단)`만 검사, «블록 부재»·exit 4·BLIND_SPOTS 문면 검사 0 · `reverse_coverage.py:139` 는 stdout 산문(골든 없음) · `gen_pregate_symbol_kinds.py` design_pregate 참조 0 · `rulepack_smoke.py:88` 이름만 · `registry_gate.py:153` docstring 만 | §5 |
| C6 | 제안(검증됨 — 자리 있음) | E4 는 **순수 함수**(`Plan` + `in_baseline` + `promoted` frozenset → `list[str]`)로 두면 «계약 실존 유닛 매트릭스 ⓐ~ⓟ» 판형 그대로 유닛 가능(FS·git 0) · E5 는 `check_report(spec_text, report_text)` 순수 함수 + 리포트 본문은 실행기 자신의 `write_report`/`write_report_stub`(`:1535,:1577` — git 무접촉·인자만)로 합성 → 형식 드리프트 0. 매트릭스 초안 E4 12케이스·E5 19케이스 | §6 |

## 1. C1 — H2 «묶음 enforce» 실행 가능성

| 항목 | 판정 | 실측·근거 |
|---|---|---|
| 별도 리포트 파일 | 검증됨 | 러너는 묶음별 리포트 파일 + `_header_count`(`## pre-gate 예보` 부분문자열 계수 `:445`) 판형. base 는 `scratch/pregate-report.md` 계수 4(`:464,:493`) — enforce 를 `scratch/pregate-report-enforce.md` 로 두면 base 4·p1 1/1·mid 6·imports 1/1/1 전부 불변. exit 3 경로도 `write_report_stub` 이 헤더를 append 하므로(`:1655-1660`) 공용 리포트면 계수가 깨진다(rv1-C C-5 재확인) |
| `parse_spec` → `(None, [])` 정확 조건 | **검증됨(정밀화)** | `:639` `if "file-plan" not in blocks and not errors: return None, []`. `_machine_blocks`(`:296-330`)는 `_MARKER_RE.search`(`:152` — 행 어디서나) 로 마커를 찾고, 마커 뒤 첫 비공백 행이 ```` ```paths ```` 가 아니면 errors(`:319-320`). 모듈 호출 실측: **마커 부재(펜스만)** → None · **symbols 마커만** → None · 마커 있음·펜스 부재 → errors 1(문법 분기 exit 3 — E3 아님) · 언어 불일치(```` ```python ````) → 같은 errors · **산문 안 리터럴 `` `<!-- machine: file-plan -->` ``** → 같은 errors(문법) · **빈 펜스 / 주석만 펜스 → `Plan(entries=0)`·errors 0** → `:1696` 실체화 0 → exit 4(결손 0) |
| ⚠ 빈 블록 도피 경로 | **MAJOR** | E3 문면 «차단 모드는 블록이 의무다» 는 빈 ```` ```paths ```` 로 충족된다 — 판정 `skip` → `--check-report` ⑸ «skip 통과» → R-3437 rev3 «실체화 0 — skip» 배너 가능. 사각 S3(«산문에만 적힌 경계 import 는 표면 밖») 의 file-plan 판이며 B BLOCKER(update 재라벨) 와 같은 부류. 하네스: 픽스처 부재(§5-3 «exit 4 픽스처 부재» 이월 항목이 바로 이 경로). 처방: ⓐ `empty-block-spec.md` 픽스처로 현행(exit 4) 고정 + A 축(문면 확정)에 «file-plan 0행 = 형식 red(블록 공허)» 여부 상신 — 채택 시 `_parse_file_plan` 뒤 `if not plan.entries: errors.append(...)` 1행(E3 와 같은 exit 3·다른 사유 종류) |
| ⚠ 산문 리터럴 마커 함정 | MINOR(픽스처 작성 규칙) | `noblock-spec.md` 본문·E3 사유 문면을 인용하는 어떤 픽스처도 `<!-- machine: … -->` 리터럴을 산문에 넣으면 «블록 부재» 가 아니라 «펜스가 없다» 문법 red 로 빠진다(실측). 픽스처는 마커 문자열 자체를 쓰지 말 것(«machine 마커» 라고만) — 실행기 E3 사유행이 리터럴을 품는 것은 무해(리포트는 `_machine_blocks` 대상 아님) |
| `noblock-spec.md` 내용 특정 | 검증됨 | kkebi 판형(rv1-C C5 — 마커 0/20) 그대로: 제목·산문·`## 파일 계획` 산문 표 + 영구 테스트 입장 표(선택) · **machine 마커 0**. 변형 ⓑ «펜스만·마커 없음» 도 None(마커가 열쇠임을 고정 — 선택). `block_hash` 는 블록 0 이어도 결정적 12hex(실측 `bafbbd269256` 류) → «해시 병기» 기대 성립(`write_report_stub` 헤더 `_executor_stamp` `:1589-1590`) |
| `update-missing-spec.md` | 검증됨 | `update application/orders/domain_layer/shared_value_object/promo.py` 1행(mini_repo 부재) → `in_baseline`(`:1674` — 오버레이 «전» `.exists()`) 부재 → E4 → exit 3. E4 를 `materialize` 앞(`:1683` 전)에서 `errors` 목록으로 내면 `:1655-1660` 프레임(«형식 red — N건» + 행)·`요약: 형식 red N건(update 대상 부재)` 이 그대로 붙는다 — FormError 1건 문자열보다 낫다(reading 은 24건: §3) |
| `update-promoted-spec.md` | 검증됨(권고 수정) | **mini_repo 에 폴더를 넣지 말 것** — 빈 폴더는 git 에 안 실리므로 파일이 필요하고, mini_repo 는 4묶음 공유다. 대신 mid 묶음 판형(`:548-551` — `_make_repo` 뒤 파일 write·commit)으로 `repo-enforce` 에 `…/shared_value_object/promo/__init__.py`(0B — mini_repo 의 `__init__.py` 들과 동형 `mini_repo/application/orders/__init__.py`) 커밋 → 기준선 트리에 `promo/` 실존 → 예외 → update 만이라 실체화 0 → **exit 4 고정**(0/4 중 4 — 이로써 §5-3 «exit 4 픽스처 부재» 이월도 닫힌다). 같은 스펙 파일 1개를 두 저장소 상태로 돌리는 것이 두 파일보다 낫다(짝 증거 — 폴더 유무만 다름). 오버레이만(미커밋 폴더) 변형 → red 도 고정 권장(«오버레이 실존은 판정에 넣지 않는다» E4 문면의 기계 증거). 다른 픽스처 기대 무영향: 저장소가 별개고 exit 3/4 경로는 게이트 미호출 |
| `remove-missing-spec.md` | 검증됨 | 비후행 `remove …/nothing.py` → exit 3. 짝으로 `remove@L1 …/nothing.py` → 현행 `unsimulated`(`:1028`) → exit 4 고정 권장 |
| 기존 픽스처의 E4 회귀 | 검증됨(0) | 전 픽스처 `update`/`remove` 행 실측: `imports-green` `update config/settings/base.py`·`update framework/test/frozen_clock.py`(둘 다 `repo-imports` 실존) · `imports-red`·`imports-update-only` `update config/settings/base.py`(실존) · `remove` 행 0. 유닛 매트릭스의 `("remove", gone.py)`·`("update", ghost.py)` 는 `check_import_existence` 직접 호출(`:298-302`)이라 E4 무관 |
| 번호 충돌 | MINOR | 계획 E1~E7(실행기 변경 항목) ↔ 러너 docstring·`_run_mid_bundle` 의 E1~E4(재발화 판형 케이스) 가 같은 표기. ④ 러너 docstring 갱신 시 «계획 E번호» 를 인용하지 말고 항목 이름으로 |
| H4 «exit 3 두 경로» | MINOR | exit 3 코드 경로는 셋(`:1655` errors · `:1661` None→E3 · `:1684` FormError) + E4 를 errors 로 합치면 «errors 경로 2사유». 유닛은 form-red·noblock·update-missing 3픽스처 stdout 에서 `^요약: 형식 red \d+건\(` 접두를 각각 단언 |

## 2. C2 — H3 `--check-report` 픽스처 합성과 E5 ⑷ 정규식

**합성 방식 판정**: 실제 실행기 출력 기반이 옳다. 근거 — 헤더 행(`:1544-1545`/`:1589-1590`)·`- 판정:`·`### 예보 항목` 불릿(`:1550`)은 실행기가 만들고 `--check-report` 도 같은 파일의 정규식으로 읽으므로, 픽스처가 그 출력을 그대로 쓰면 형식이 바뀔 때 생산자·소비자·픽스처가 한 커밋에서 같이 움직인다(손 합성은 옛 형식을 박제해 드리프트 시 거짓 red/green). 처분 행만 코디네이터 소유 형식이라 append 한다 — 그 문법의 정본은 R-3438 rev3(§3-F)이고 카탈로그 133~136행 실물이 예시다. 손 합성은 음성 케이스(구판 리포트=해시 부재·절 부재)에만.

**정규식 초안(프로토타입 검증 — `scratchpad/rv3C/check_report_proto.py`, 카탈로그 실물 리포트·명세로 실행)**:

```python
_SECTION_HEAD_RE = re.compile(r"^## pre-gate 예보 — \d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z · \S+\s*$", re.M)   # 실행기 자기 형식만
_ANY_H2_RE       = re.compile(r"^## ", re.M)                                                                # 절 경계
_BASE_LINE_RE    = re.compile(r"^- 기준선 SHA: `[0-9a-f]{40}` \(--base \S+\).*?블록 해시 ([0-9a-f]{12})\s*$", re.M)
_VERDICT_RE      = re.compile(r"^- 판정: (.+?)\s*$", re.M)
_ITEM_ID_RE      = re.compile(r"^- `([0-9a-f]{12})` .*?\[#[\w-]+\]", re.M)          # 예보 항목(리포트 불릿) — e-ID 는 `e-` 접두라 불일치
_DISPOSITION_RE  = re.compile(r"`([0-9a-f]{12})`[^\n]*?\*\*(ignored|filtered|corrected)\*\*")  # 행 단위 · 불릿/표 셀 무관
```

절차: 마지막 `_SECTION_HEAD_RE` 매치 → `tail = text[start:]`(⑷ «절 이후» = 마지막 헤더부터 EOF — 절 자신은 `**ignored**` 를 내지 않으므로 포함 무해) → `section = tail[:다음 ## 전]` → ⑵ `_BASE_LINE_RE(section)` 없으면 exit 1 · 해시 ≠ `block_hash(spec)` 이면 stale → ⑶ `_VERDICT_RE` startswith `형식 red` → 불비 → `예보 red` 면 `ids = _ITEM_ID_RE(section)`, `labels = {id: {lab}}` from `_DISPOSITION_RE(tail)` → `{ignored, filtered} ∩ labels[id] = ∅` 인 id 전건 열거.

| 케이스(실물 기반) | 기대 | 프로토타입 결과 |
|---|---|---|
| a 카탈로그 리포트 + 현 명세 | 3 stale(cb95a1bddb32 ≠ 6cf8e2ffdfc3) | ✓ 3 — §4 발견 ⑩ 기계 재현 성립 |
| b 마지막 헤더 해시 패치(green) | 0 | ✓ |
| c 절 1(red 1건 `869e0acd832f`)을 끝에 재append·해시 정합 | 3 미라벨 1 | ✓ |
| d + `→ **corrected**` | 3 | ✓ |
| e + `→ **ignored**(빚: legacy-debt.txt:3 · STOP …)` | 0 | ✓ |
| f 표 셀 `\| \`id\` #392 \| **filtered**(ⓐ S6) \|` | 0(수용) | ✓ — reading run 37 실물이 표 형식(`pregate-report.md:2549-2560`) |
| g + 오염 `- 최종본(블록 해시 갱신) 예보 **green** — 기준선 e1294f59c35c` | 0(무영향) | ✓ (`_BASE_LINE_RE` 는 40hex+12hex 요구) |
| h 처분이 마지막 절 «이전»(직전 run 처분)에만 | 3 | ✓ (A 축 질문의 기계 답: 이전 run 처분은 불인정) |
| i 코디네이터 제목 `## pre-gate 예보 처분` 추가 | 0(절 오인 없음) | ✓ — 부분문자열 매칭이었다면 exit 1 |
| j `- \`e-869e0acd832f\` ⑴ → **ignored**` | 무시(여전히 3) | ✓ |
| k 구판 리포트(L2 — 해시 스탬프 0) | 1 | ✓ |
| l 절 부재 | 1 | ✓ |
| m 마지막 절 `형식 red(블록 부재)` | 3 | ✓ |

MINOR ①: 러너 `_header_count` 는 부분문자열(`:446`) — 픽스처 처분 절 제목에 `## pre-gate 예보` 접두를 쓰지 말 것(계수 오염). E5 는 `_SECTION_HEAD_RE` 로 실행기 형식만 인정 권장(R-3438 rev3 에 «코디네이터 절 제목은 `## pre-gate 예보 —` 로 시작하지 않는다» 1구 — B 축). MINOR ②: 표 셀 형식 수용은 위 정규식으로 자동 — 성문(§3-F)에 «행 단위 · 불릿/표 무관» 을 적어 두면 파서·규범이 같은 말.

`--check-report` 의 `main` 착지: `:1630` `--block-hash` 분기와 같은 자리(`.git` 검사 `:1633`·rev-parse `:1639`·인터프리터 probe `:1647` **앞**) — «git 0회» 는 코드 위치로 보장한다. `target` 위치 인자는 유지(§3-A 명령 `.` 정합).

## 3. C3 — §4 소급 대조 실행 가능성

### 3-1 좌표(전부 라이브 읽기로 확정)

| 레인 | 최종 design-spec(블록 해시) | G1 기준선 SHA(리포트 헤더 `- 기준선 SHA:`) | main 도달 | E4 정적 사전 계산(update/remove 부재 · 승격 예외 · add 실존) |
|---|---|---|---|---|
| L1 media-library | `~/Desktop/spring_dream_server/.dddjango/20260902-0128-media-library/design-spec.md`(f3cfad9b1c88 — 88행: add 69·empty 17·update 2) | `138359f7cf6f…`(4회 전부 · 마지막 판정 red 15) | ✓ 조상 | **0 · 0 · 0** |
| L2 notification-bc | `…/20260902-1458-notification-bc/design-spec.md`(f2500315a3b6 — 106행: empty 53·add 34·remove 12·update 7) | `1eb8507424c7…`(4회 전부 · red 19) | ✓ | **0 · 0 · 0** |
| L3 email-template | `…/20260902-1842-notification-email-template/design-spec.md`(d3c86e9a1a4f — 35행: add 20·remove 10·update 5) | G1 = `9ca3dd4929b7…`(1~3차 · 3차 red 2) · 5차 = `99069310e242…`(--base 9906931 · 형식 red) | ✓ 둘 다 | **0 · 0 · 0**(두 기준선 모두 — 5차의 add 충돌은 WIP 오버레이 기인이라 클론 사본에 없다 → 신 실행기 기대 = exit 0/2, **exit 3 아님**) |
| L4 fortune-catalog | `…/20260903-1214-fortune-catalog/design-spec.md`(cb95a1bddb32 — 98행: empty 55·add 42·update 1 · **워킹트리가 HEAD 대비 산문 1행 삭제로 dirty — 해시 동일**) | `e1294f59c35c…`(4회 전부 · 마지막 green · 헤더 해시 6cf8e2ffdfc3) | ✓ | **0 · 0 · 0** |
| R reading 최종본 | `git show 19b27df:.dddjango/20260831-2331-fortune-reading/design-spec.md`(a89de0574a0e — update 73·remove 19·empty 3) | 마지막 run 44 = `80431d9480f7…`(구판 rerun 실물 `workspace/eval/pregate-observe/reading-v21714/rerun-v21716-19b27df-base-80431d9.md` = skip) | ✓ | **update 0 · 승격 예외 1(`prepare_fortune_evidence_use_case.py` — 예외 발동 실증) · remove 부재 7**(`test/e2e/test_crosswalk_candidate_bundle.py` 등) · add 0 → 신 실행기 **exit 3(remove 대상 부재 7건)** |
| R′ reading 재라벨 판형 | `git show 78e616a:…design-spec.md`(7adc9cc6d40f — add 7·update 66·remove 19) | run 37 = `61b56ef4b69e…`(--base HEAD · 16:09Z · green) | ✓ | **update 부재 24**(`driving_layer/api/evidence_provisioning/__init__.py` …) · remove 부재 2 → **exit 3(update 대상 부재 24건)** = ledger:144 «기실현 add 24경로를 update 로 재라벨» 의 정확한 기계 재현 |

**MAJOR ⑴ — 대조군 정정**: §4 «귀속 ID 집합 불변 · exit 불변(카탈로그 0 …)» 은 «현 리포트 마지막 절» 을 대조군으로 전제하지만 L1(ledger:51 — 최종 개정이 블록 변경·재실행 0)·L4(발견 ⑩ — 6cf8e2ffdfc3→cb95a1bddb32) 는 최종 명세의 예보가 **한 번도 실행된 적이 없고**, L3 는 exit 3→비3 이 의도다. 무손실·오차단의 증거는 **구 실행기 × 신 실행기 동일 입력 A/B**(같은 spec 파일·같은 `--base`·같은 클론)여야 성립한다 — 비교 키는 (exit, 안정 ID 정렬 집합, 실존 결손 e-ID 집합)이고 텍스트(모드 문면·요약 행)는 제외. 구 실행기 실물: `~/.claude/plugins/cache/changja88-dddjango/dddjango/2.17.16/scripts/design_pregate.py` = release `5225c57` = 현 HEAD 파일(3자 byte 동일 실측; 형제 스크립트·`plugin.json` 동봉이라 헤더 스탬프 «v2.17.16» 까지 레인 리포트와 같다). ④ 는 E1~E7 편집 **전에** `git archive HEAD dddjango/scripts | tar -x -C <scratch>/old` 로 스냅숏을 떠 두거나 cache 경로를 그대로 쓴다.

**MAJOR ⑵ — reading 기대 좌표 정정**: §4 «E4 로 새로 형식 red 가 되는 레인은 reading(승격 부품 update 계획 · 의도된 판정)뿐» — «reading 뿐» 은 성립(L1~L4 정적 계산 0)하나 사유가 다르다: 최종본×최종 기준선은 **remove 부재 7**(update 부재 0 — 재라벨분은 그 사이 커밋돼 실존 · 승격 부품은 예외로 흡수), 재라벨 봉쇄는 **78e616a × 61b56ef4** 좌표에서만 재현된다(update 부재 24). §4 를 두 행으로 나누어 적을 것. 부수 발견: 장수 레인의 «이미 지워진 파일의 `remove` 행» 이 E4 에서 red 가 된다(R-3425 «`remove` = 기준선 실존 경로» 와 정합 — A 축에 «기준선 이동 시 remove 행 정리 의무» 문면 유무 상신).

### 3-2 격리 사본 절차(라이브 무변경)

- `~/.herdr/worktrees/spring_dream_server/` 는 **비어 있음**(실측) — 런 폴더는 Desktop main 체크아웃에 **git 추적**(`.dddjango/` 448파일)으로 있다. 6개 기준선 SHA 전부 `cat-file -e` ✓·`merge-base --is-ancestor main` ✓ → 일반 클론이 전부 가진다.
- 레시피(worktree 불요): `git clone -q ~/Desktop/spring_dream_server <scratch>/spring && git -C <scratch>/spring checkout -q --detach <G1 SHA>` → `python3 <scripts>/design_pregate.py <spec 파일> <scratch>/spring --base <G1 SHA> --report <scratch>/retro-<레인>.md`. 클론은 status clean → `_overlay_dirty`(`:856`) 0 → 사본 = 기준선 트리만(원 G1 실행의 오버레이 상태는 복원 불능 — A/B 는 두 실행기가 같은 클론을 쓰므로 무관). spec 은 위치 인자라 라이브 워킹트리 파일 경로를 그대로 읽는다(쓰기 0). `git worktree add` 는 라이브 `.git/worktrees` 메타를 만들므로 쓰지 않는다. `--no-checkout` 클론은 금물(전 파일이 ` D` 로 잡혀 `_overlay_dirty` 가 사본에서 지운다).
- 인터프리터: spring·kkebi `requires-python >=3.14` · 로컬 `python3` 3.14.7 → `_interpreter_gap_reason`(`:1056`) 통과(기본 `sys.executable` 가능 · 원 레인 정합을 원하면 `--python ~/Desktop/spring_dream_server/.venv/bin/python`).
- `DJR_FINDINGS_JSON`: 이름 확인 `findings.py:68 ENV_VAR = "DJR_FINDINGS_JSON"` · 소비 `findings.py:134 _sink_mode()`(file 우선) · **실행기가 `run_gate` `:1084` 에서 스크래치 `findings.jsonl` 로 강제 설정**하고 `DJR_VIOLATIONS_DIR`·`DJR_SOURCE_GIT_ROOT` 를 pop → 수동 설정 불요(셸 export 값도 덮인다). registry_gate 는 다시 pop 후 명시 sink(`registry_gate.py:211-215`) · 유일한 sink=None 호출 `:577`(provenance 재실행)은 스냅숏(자기 `TemporaryDirectory` `:680`) 안 `.dddjango/violations/`(spring 은 `.dddjango/` 가 추적돼 archive 에 실린다)에 쓸 수 있으나 스크래치다.
- 부산물 전수: ① `$TMPDIR/design-pregate-*`(`--keep` 아니면 삭제) ② registry_gate `TemporaryDirectory` ③ `--report` 파일(스크래치로) ④ `dddjango/scripts/__pycache__/`(gitignore `:16` · `diff -rq --exclude=__pycache__`) ⑤ 클론의 `.git/index` 갱신. **라이브 저장소 쓰기 0**(target 으로 라이브를 넘겨도 `archive`·`status`·`rev-parse` 읽기뿐이나, dirty overlay(`M design-spec.md`·`?? .claude/`)가 섞이므로 클론이 옳다).
- 카탈로그 `--check-report`: 현 리포트 + 워킹트리 명세 → exit 3 stale(§2 a 로 기계 재현 확인). «run 1(#392 red)·run 2 상태에서 처분 절 기재 후 → 통과» 는 §2 c/e 판형으로 러너 픽스처가 대신한다(라이브 리포트 편집 금지).
- kkebi 1건: `~/Desktop/kkebi-server` git ✓ · 명세 20/20 마커 0 → `parse_spec` None → E3 exit 3 · 경로가 `.git` 검사→rev-parse→인터프리터 probe→parse 라 **사본·게이트 0** · `--report` 는 반드시 스크래치(kkebi 런 폴더에 `pregate-report.md` 를 만들지 않는다 — 현재 0개).
- 구판 리포트(L1·L2·L3·R) 는 헤더 해시 스탬프 0 → `--check-report` 는 exit 1(§2 k) — §4 가 카탈로그에만 적용하는 것이 맞다.

## 4. C4 — manifest 재봉인

| 항목 | 판정 | 근거 |
|---|---|---|
| 명령 | `PYTHONUTF8=1 python3 workspace/tools/manifest_seal.py --write` **단독**. `--draft` 는 `check(draft_ok=args.draft)` 에만 전달(`:1401-1402`) — `--write` 분기(`:1404-1420`)는 읽지 않는다. rv1-C C2 12단 «`--write --draft`» 는 무해하나 오기 → 계획 §5-1 «`--write`(draft)» 는 «status 는 draft 로 남는다(`build:785`)» 의 뜻으로만 | `manifest_seal.py:1347-1349,1401-1420,785` |
| 쓰는 파일 | 2 — `workspace/eval/ab/T2-0b-manifest.json` + `workspace/design/2026-08-20-ontology-t2-0b-design.md`(FACTS 블록 — 그룹 수·`pipeline` 5→6·`packs` 2→3 파일 수 렌더 · 2패스 `:1404-1411`) → 둘 다 커밋 | `:1261-1300` |
| `--check --draft` green 조건 | ① `self_sha256` ② 9그룹 글롭 == 봉인본 ∧ 파일 추가/삭제/변경 0 ∧ tree 해시 ③ `dddjango/scripts` ≡ codex scripts(E7 cp·rulepack.json·`pregate_symbol_kinds.json` 미러 선행) ④ `script_trees[source-*]` == 봉인(cache-* 는 draft 에서 skip) ⑤ B암 재료 ⑥ allocation ⑦ schemas(`findings.py`·`registry_gate.py` 스키마 문자열 — 불변) ⑧ **`initial_state`(`ontology/**/*` tree · `LEDGER.tsv` · `ISSUED` 해시)** — 따라서 `--write` 는 rdflib 편집·ISSUED 채번·LEDGER 재기준선·`make rulepack`·md 재투영·codex 손 미러·실행기 편집·Makefile(protocol 그룹) **전부 뒤**에 1회. §5-2 «기록» 항목(ledger.md·설계 v4·로드맵·조감도·`reverse_coverage.py`)은 봉인 밖이라 뒤에 해도 무해 | `:964-1131,811-832` |
| 현 상태 | status `draft` · `sealed_commit 1e4d8bf` · `cache_parity` claude/codex **drift**(이미 — draft 검사 밖 `:1101-1105`) · `pipeline` 파일 5 · `packs` 2. `design_pregate.py` 는 지금도 `script_trees[source-*]`·미러 동일성으로 간접 봉인 — 편집만으로 재봉인이 강제된다(그룹 추가는 문서화+파일 단위 진단) | 실측 |
| «why» 문면 | 선택(MINOR). 봉인본에 `why` 가 실려 `--write` 로 재방출된다(`build:767`). `pipeline.why` 는 «3암 공유 실행 경로» 서술이라 pre-gate 1구(«G1 전 결정적 예보 — 차단 모드 · Coordinator 6번 게이트와 짝») 추가가 읽는 사람에게 유익 · `packs.why` 는 «규칙 팩과 B암 재료» — `pregate_symbol_kinds.json` 은 검사기 소스 소성물이라 «pre-gate Base 종류 소성물(검사기 소스 추출)» 1구 권장 | `:71-76,99-104` |
| 설치 후 | 설치본 갱신 뒤 엄격 `--check`(verify-runready `Makefile:213`) 를 원하면 `--write` 재발행(cache-* 트리·cache_parity) — 기존 관례(memory «설치 후 봉인 재발행») | `:1017-1030` |

## 5. C5 — E1·E2·E6 문자열 의존 하네스 전수

| 파일 | 실행기 문자열 의존 | 판정 |
|---|---|---|
| `workspace/tools/pregate_fixture_run.py` | `요약: 귀속 0건 · 실존 결손 0건`(`:646`)·`… 실존 결손 3건`(`:658`)·`요약: 실체화 0 · 실존 결손 1건`(`:673`) — **접두 부분일치**라 `· 모드 관찰`→`· 모드 차단` 무해 · `- 판정: 예보 green`·`(권고·비차단)`·`실체화 0건`·`already-built N건`·`add 충돌(실존)` 불변 · «블록 부재»·exit 4·BLIND_SPOTS·헤더 «모드:» 검사 **0**(docstring `:38` 만 갱신 — H1) | 무영향 |
| `workspace/tools/reverse_coverage.py:136-140` | `why` 산문 «관찰 모드» — stdout 출력 전용(골든·파일 쓰기 0 `:180-187`) | H5 교체는 안전·비게이트 |
| `workspace/tools/gen_pregate_symbol_kinds.py` | `design_pregate` 참조 **0**(grep) — 검사기 27종 소스만 스캔 | 무영향 |
| `workspace/tools/rulepack_smoke.py:88` | roster 에 `"design_pregate.py"` **이름**만 | 무영향 |
| `dddjango/scripts/registry_gate.py:153` · `rulepack.json` · `wiring/registry.ttl` | docstring·enforcedBy 이름 | 무영향 |
| codex 미러 | `codex-dddjango/skills/dddjango/scripts/design_pregate.py` 현재 byte 동일(cmp) — E7 후 `verify-base-core` `diff -rq`(`Makefile:158`)·manifest ③ | E7 필수 |
| codex 3어절 | `codex-dddjango/skills/dddjango/SKILL.md:114` 괄호 «리뷰어 spawn 다발을 **전부 띄운 뒤 wait 수집 전에** shell 로 1회 — 조기 신호·codex 병렬 정의와 정합» ↔ Claude `commands/dddjango.md:96` «리뷰 다발과 병렬 1회 — 조기 신호». §3-A 는 제목·문장 4곳 교체라 이 괄호는 건드릴 이유가 없다 — 검사기 0(rv1-C C2 9단) → ④ 산출물에 두 행 diff 첨부 + 리뷰 ⑥ 눈 대조 | 하네스 없음(수용) |

## 6. C6 — 러너 유닛 매트릭스 자리와 기대값

자리: `main:691-692` 의 `failures.extend(_unit_checks())`·`_existence_unit_checks()` 뒤에 `_baseline_form_unit_checks()`·`_check_report_unit_checks()` 2함수 추가(같은 «합성 재료 + 실행기 함수 직접 호출 · git·검사기 비의존» 판형 `:263-441`).

**E4 순수 함수 제안** — `baseline_form_errors(plan: Plan, in_baseline: frozenset[str], promoted: frozenset[str], base_short: str) -> list[str]` (`promoted` 는 `:1674` 와 같은 자리에서 `frozenset(p for p in plan.entries if p.endswith(".py") and (copy / p[:-3]).is_dir())` — 오버레이 «전»). 매트릭스(합성 Plan + frozenset — FS 0):

| # | 엔트리 | in_baseline | promoted | 기대 |
|---|---|---|---|---|
| ⓐ | `update a/x.py` | {a/x.py} | ∅ | [] |
| ⓑ | `update a/x.py` | ∅ | ∅ | 1행 «update 대상 부재: a/x.py — 기준선(<sha12>)에 없는 경로는 add 다(재라벨 도피 금지)» |
| ⓒ | `update a/x.py` | ∅ | {a/x.py} | [](승격 폴더 예외) |
| ⓓ | `update a/x.py` — 오버레이만 실존(in_baseline 계산 규약상 ∅) | ∅ | ∅ | 1행(run 37 판형) |
| ⓔ | `remove a/x.py` | ∅ | ∅ | 1행 «remove 대상 부재» |
| ⓕ | `remove@L3 a/x.py` | ∅ | ∅ | [](후행 — 현행 unsimulated) |
| ⓖ | `remove a/x.py` | {a/x.py} | ∅ | [] |
| ⓗ | `remove a/x.py` | ∅ | {a/x.py} | [](예외 적용 — 문면 확정 필요·아래 잔여) |
| ⓘ | `empty a/x.py` | ∅ | ∅ | [](새 빈 파일) |
| ⓙ | `add a/x.py` | {a/x.py} | ∅ | [](E4 밖 — add 충돌은 `materialize:999` 현행) |
| ⓚ | `update a/x.py` + `update b/y.py` 둘 다 부재 | ∅ | ∅ | 2행(전건 열거 · 순서 = plan 순) |
| ⓛ | `update a/x` (`.py` 아님) | ∅ | ∅ | 1행(승격 예외는 `.py` 에만) |

**E5 순수 함수 제안** — `check_report(spec_text: str, report_text: str) -> tuple[int, list[str], str | None]`(exit · 사유 · 요약 행). 리포트 본문은 `dp.write_report(path, Path("design-spec.md"), "HEAD", "e"*40, verdict, attributed, mat, [], blk_hash, dp.ExistenceReport())`·`dp.write_report_stub(...)` 로 합성(인자만 — git 0 · `ExistenceReport` 기본 생성 가능 `:248-266`). attributed 행은 `"check-x.py :: [#392] application/a/b.py: msg"` 꼴(`_ATTR_LINE_RE:167` — ID 는 `_stable_id`).

| # | 리포트 상태(마지막 절) | 이후 텍스트 | 기대 exit · 사유 |
|---|---|---|---|
| ⓐ | 파일 부재 | — | 1 |
| ⓑ | 절 0(산문만) | — | 1 |
| ⓒ | 헤더 해시 행 결손(손 합성 구판) | — | 1 |
| ⓓ | green · 해시 ≠ | — | 3 stale |
| ⓔ | stub `형식 red` / `형식 red(블록 부재)` / `형식 red` + 해시 ≠ | — | 3 / 3 / 3(사유 2 — 순서 stale→형식 red 고정) |
| ⓕ | green(귀속 0) | — | 0 |
| ⓖ | stub `skip` · `skip · 계약 실존 결손 1건(권고·비차단)` · green+`실존 결손 2건` | — | 0 / 0 / 0(e-ID 는 전건 밖) |
| ⓗ | red 3건 | 처분 0 | 3 «미기재 3건: id1, id2, id3» |
| ⓘ | red 3건 | ignored·filtered·filtered | 0 |
| ⓙ | red 3건 | ignored 2 | 3 «미기재 1건» |
| ⓚ | red 3건 | corrected 3 | 3 |
| ⓛ | red 3건 | 표 셀 형식 3 | 0 |
| ⓜ | red 1건 + 앞 절(같은 ID red)에만 처분 | 마지막 절 이후 0 | 3 |
| ⓝ | red 1건 | `- \`e-<12hex>\` → **ignored**` | 3(무시) |
| ⓞ | red 1건 | 처분 1 + `- 최종본(블록 해시 갱신) 예보 **green**` | 0(⑵ 무영향) |
| ⓟ | 절 3(red·green·red) | 마지막 red 처분 1 | 0(마지막 절만) · 첫 절 ID 미기재 무관 |
| ⓠ | green | `## pre-gate 예보 처분` 제목 추가 | 0(절 오인 0) |
| ⓡ | red 1건 | 같은 ID 처분 2행(ignored·corrected) | 0(어느 한 행에 ignored) |
| ⓢ | red 1건 | ID 행과 `**ignored**` 가 다른 행 | 3(행 단위) |
| ⓣ | 요약 행 형식 | — | `^요약: check-report (정합|불비 \d+건) · 블록 해시 [0-9a-f]{12}=[0-9a-f]{12} · 마지막 판정 ` 정규식 |

## ④ 픽스처·러너 구현 명세(파일별)

- `workspace/eval/fixtures/pregate/noblock-spec.md`(신설) — kkebi 판형: 제목·산문 계획 표·영구 테스트 입장 표 · **machine 마커 리터럴 0**(산문에 `<!-- machine:` 를 절대 쓰지 않는다 — §1 함정) · 기대: exit 3 · stdout `형식 red — 1건` 프레임 + 사유행(«블록 부재») · `요약: 형식 red 1건(블록 부재)` 접두 · 리포트 헤더 1 · `_BLOCK_HASH_RE` 매치 · `- 판정: 형식 red(블록 부재)`.
- `workspace/eval/fixtures/pregate/empty-block-spec.md`(신설 — MAJOR 처방) — `<!-- machine: file-plan -->` + 빈 ```` ```paths ````: 현행 기대 exit 4 · `- 판정: skip` · `요약: 실체화 0 · 실존 결손 0건` 고정(문면 확정에서 «블록 공허 = 형식 red» 채택 시 exit 3 로 기대 교체 — 픽스처는 어느 쪽이든 필요).
- `workspace/eval/fixtures/pregate/update-target-spec.md`(신설 — H2 의 update-missing/update-promoted 를 **1파일**로) — `update application/orders/domain_layer/shared_value_object/promo.py` 1행(+ 선택 symbols 행 `…/promo.py::Promo` → S′ 무영향). 러너가 두 저장소 상태로 돌린다: ⓐ `repo-enforce`(mini_repo 그대로) → exit 3 «update 대상 부재» · ⓑ `repo-enforce-promoted`(`_make_repo` 뒤 `…/promo/__init__.py` 0B write → `git add -A` → commit) → exit 4 · `- 판정: skip` · 미시뮬레이션 1 · ⓒ(선택) 폴더를 write 만 하고 커밋 안 함 → exit 3(오버레이 불인정).
- `workspace/eval/fixtures/pregate/remove-target-spec.md`(신설) — `remove …/shared_value_object/nothing.py` → exit 3 · 짝 `remove-deferred-spec.md`(`remove@L1 …/nothing.py`) → exit 4(현행 unsimulated 유지).
- `workspace/eval/fixtures/pregate/mini_repo/` — **변경 0**. `imports_overlay/` — 변경 0.
- `workspace/tools/pregate_fixture_run.py`:
  - docstring `:38` exit 규약 갱신(계획 §1 문면) + 묶음 enforce·checkreport 항목 · 계획 E번호 인용 금지.
  - `_FORECAST_ID_RE = re.compile(r"^\s*(?:- )?`([0-9a-f]{12})` .*?\[#[\w-]+\]", re.M)` 추가(처분 append 용 ID 추출).
  - `_run_enforce_bundle(scratch, failures)`: 리포트 `scratch/pregate-report-enforce.md` · 위 5픽스처(+상태 변형) 순차 · 각 exit·stdout 접두·`- 판정:` 문면 단언 · 마지막에 `_header_count == 6`(noblock·empty·update ⓐ·update ⓑ·remove·remove@L — ⓒ 선택 시 7).
  - `_run_checkreport_bundle(scratch, failures)`: 전용 `repo-cr` + 리포트 `scratch/pregate-report-cr.md` · 실행 2(red-spec.md → exit 2·ID 3 / green-spec.md 는 base 묶음 재실행 대신 `green3-spec.md` 리포트 재사용 가능 — 결합 회피 위해 전용 권장) · `--check-report` 호출 순서: red 직후(3 미라벨) → ID 2건 ignored append(3 «미기재 1») → 3번째 corrected(3) → 3번째 filtered(0) → 오염 행 append(0) → spec 을 `green-spec.md` 로 바꿔 호출(3 stale) → `form-red-spec.md` 를 별도 리포트에 1회(3 형식 red) → enforce 묶음의 noblock 리포트에 대해(3 형식 red(블록 부재)) → imports-update-only 리포트(0 skip·결손) · 각 호출은 `[sys.executable, EXECUTOR, spec, ".", "--check-report", report]` · stdout `요약: check-report …` 정규식 단언 · 처분 append 문법은 카탈로그 134행 실물 그대로(`- \`<id>\` [#N] <path> → **ignored**(빚: <file:line> · STOP <doc>)`) · 절 제목은 `## pre-gate 처분 라벨`(«pre-gate 예보» 접두 금지).
  - `_baseline_form_unit_checks()`·`_check_report_unit_checks()` §6 매트릭스 · `main` 에 4묶음 뒤 2묶음 추가 · PASS 문구 갱신.
- `dddjango/scripts/design_pregate.py`(하네스 관점 요구만): E4 는 `:1674` 뒤 `errors = baseline_form_errors(...)` → 비면 진행, 있으면 `:1655` 와 같은 프레임으로 `write_report_stub(..., "형식 red", errors)`·`요약: 형식 red N건(update 대상 부재|remove 대상 부재)` → return 3(FormError 단건보다 전건 열거) · `--check-report` 는 `:1630` 옆(git·인터프리터 앞) · E2 요약 행은 exit 3 세 경로 전부 · `MODE="enforce"` 헤더 형식 `· 모드: <라벨>(<MODE>) ·` 유지(러너 미검사이나 리포트 가독).
- `workspace/tools/manifest_seal.py:71-104`: `pipeline.globs += "dddjango/scripts/design_pregate.py"` · `packs.globs += "dddjango/scripts/pregate_symbol_kinds.json"` (+ why 1구 선택) → 모든 봉인 대상 편집 완료 후 `--write` → `make verify`.
- `workspace/tools/reverse_coverage.py:139`: «관찰 모드» → «차단 모드» (비게이트 산문).
- 소급 대조(§4 대체 문안): 구 실행기 스냅숏 확보 → 클론+detached checkout → L1~L4·R·R′ 6좌표 A/B(비교 키 exit·ID 집합·e-ID 집합) → 결과 표를 ledger «승격 집행» 절에 첨부 · 카탈로그 `--check-report` stale 실물 1회 · kkebi 1건 exit 3 실물(`--report` 스크래치).

## 결정 불능 잔여(다른 축·문면 확정 상신)

1. **빈 file-plan 블록(0행) 의 취급** — 현행 exit 4 skip(도피 경로). «블록 공허 = 형식 red» 채택 여부는 A 축·문면 확정. 어느 쪽이든 픽스처는 필요(위 `empty-block-spec.md`).
2. **`remove <p>` 에 승격 폴더 예외 적용 여부**(E4 문면은 update·remove 를 한 문장에서 다루고 예외를 뒤에 둠) — 적용이면 §6 ⓗ 기대 `[]`, 아니면 1행. 파서 구현 전 확정 필요.
3. **기준선 이동 레인의 «이미 제거된 파일 remove 행»** — reading 최종본×최종 기준선 remove 부재 7 이 E4 red 가 된다. R-3425 «`remove` = 기준선 실존 경로» 와 정합이나 «`--base` 이동 시 remove 행 정리(삭제) 의무» 문면이 architect 규범에 없다 — A/B 축.
4. **`--check-report` ⑷ 의 «절 이후» 정의** — 프로토타입은 «마지막 헤더부터 EOF»(이전 run 처분 불인정 — §2 h). 계획 A 질문(«같은 ID 가 다른 run 에서 재발화») 의 답이 되지만 규범 문면(§3-A «명세 개정 승인마다 append»)과 같은 뜻인지 A 축 확정.
5. **§4 A/B 에서 L1·L2 의 재실행 결과가 원 리포트 마지막 절과 다를 때의 처리** — 최종 명세 예보는 미실행분이라 «불일치 = 회귀» 가 아니다. A/B 동일이면 무손실 증거로 충분하며, 원 리포트와의 차이는 «Phase 2 개정 미재실행(발견 ⑩ 계열)» 로 ledger 에 기록만 — ⑥ 감사 기준 합의 필요.
6. **enforce 묶음의 `--report` 경로 규약** — H2 는 «별도 리포트 파일» 만 적었다. 러너 1파일(`pregate-report-enforce.md`·계수 6)로 제안했으나 checkreport 묶음이 noblock 리포트를 재사용하려면 enforce 묶음이 먼저 돌아야 한다(순서 결합) — 전용 실행 1회 추가(exit 3 경로라 비용 0에 가깝다)로 결합을 끊을지 ④ 선택.
