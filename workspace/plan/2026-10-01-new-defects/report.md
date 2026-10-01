# 새 결함 3건 수리 보고 (2026-10-01)

작업 브랜치: `fix/new-defects-3` · 기준: `2fffcb22` · 최종: `ed3dd2ea`. 세 결함을 각각 커밋하고 결함 3 리뷰 수정 커밋 하나를 추가했다(총 4개). 모든 `make verify`는 봉인 드리프트 외 통과했으며 봉인은 지시대로 재발행하지 않았다. 기존 두 임시 폴더의 생성 원인은 미확정으로 남긴다.

보고서·지시서·`.venv`는 커밋하지 않았다. 개별 증거 로그의 공통 루트는 `/tmp/dddjango-new-defects-evidence/`다.

## 결함 1 — 멱등성 검사 입력의 스냅숏 누락

- 원인: `dddjango/scripts/registry_gate.py:105`의 `.*` 제외와 `:170`의 `_snapshot_current` 때문에 현재 사본에서 `.dddjango/*/scope.md`, `design-spec.md`가 사라졌다. 검사기는 `check-idempotency-scope-creep.py:182`부터 이 두 문서로 미요청/사용자 승인을 판정한다.
- 수정: 숨김 경로 제외를 유지하고 위 두 이름의 루트 `.dddjango` 직계 작업 폴더 문서만 현재 바이트로 추가 복사했다. Codex 스크립트에도 byte 미러했다.
- pre-gate: `design_pregate.py`의 `_extract_archive`와 `_overlay_dirty`에는 추적/비무시 미추적 문서가 들어간다. `run_gate`의 registry 호출에서 빠지는 공통 원인이므로 registry 수정으로 함께 해결했다.
- 회귀: `workspace/tools/registry_gate_smoke.py`에 직접 검사기/registry 일치, 미추적 scope, 두 문서의 승인 면제, 다른 검사기 exit 보존, 숨김 경로 복사 경계, pre-gate archive/overlay 발화를 고정했다.
- 수정 전: `/tmp/dddjango-new-defects-evidence/defect1-red.log` — 4 tests, failures=4(archive/overlay subtest 포함). 직접 검사기 exit 2지만 registry/pre-gate 멱등성 행은 `0 | 0`; 스냅숏에 문서 없음.
- 수정 후: `/tmp/dddjango-new-defects-evidence/defect1-green.log` — 4 tests OK. 전체 검증에서 보강한 승인/다른 검사기 비교까지 재실행해 통과했다. registry 멱등성 행은 미승인 시 `0 | 2`, scope/design-spec 승인 배너가 있으면 `0 | 0`이다.
- 커밋: `c468223b` (`fix(registry): 현재 스냅숏에 멱등성 scope·승인 문서 보존`).
- 전체 검증: `make verify` exit 2, 303초, `/tmp/djr-verify.z7jzUo`. ontology/cross/backstop/regen green, core는 봉인 드리프트 4건만 red. registry 스모크의 신규·기존 unittest 7개 및 기존 전체 사례, git_touched 90/90, 교차 matrix 347행 차이 0. 봉인 self-test M0도 같은 드리프트로 실패(다른 변이 8개 기대대로 탐지). 봉인 뒤 남은 ab-score/self-test·스크립트 전체 미러·요청 가이드 157/157/실계약 검증은 별도 실행 exit 0. 로그 `/tmp/dddjango-new-defects-evidence/defect1-after-seal.log`.

## 결함 2 — Serena 편집 도구 허용 제거

- 원인: 다섯 Claude 역할의 graph-owned frontmatter `tools:`에 `mcp__serena__*`가 있었다. 정본 위치: `ontology/rules/agent-design-review-api.ttl:990`, `agent-design-review-db.ttl:486`, `agent-design-review-ddd.ttl:423`, `agent-discipline-reviewer.ttl:2792`, `agent-design-architect.ttl:2022`.
- 수정: 위 정본의 wildcard를 아래 7개 명시 도구로 교체 → `ontology_render.py --apply <5 doc_key>` → `make rulepack`. 기존 코드 수정 금지 규범을 도구 설정에 반영한 것으로 새 Work 채번은 하지 않았다. render-sync가 frontmatter의 graph 기준선도 검사하므로 `ontology/LEDGER.tsv`에 해당 `s001` 5행을 append했다. Claude md/frontmatter는 직접 편집하지 않았다.
- 선택 목록(각각 `mcp__serena__` 접두): `initial_instructions`, `get_symbols_overview`, `find_symbol`, `find_referencing_symbols`, `find_declaration`, `find_implementations`, `get_diagnostics_for_file`.
- 정의 출처: 설치된 Serena 소스 `/Users/hyun/.cache/uv/git-v0/checkouts/42910dfe8296368e/93ec0431`, commit `93ec043105f5ee4f5ff64ea0158041500d2cdc65`. `src/serena/tools/symbol_tools.py:36,134,252,342,399,482`의 여섯 클래스는 `ToolMarkerSymbolicRead`; `workflow_tools.py:32`의 InitialInstructionsTool은 안내문 조회다. 이름 생성은 `tools_base.py:193`, 편집 구분은 `:88,110,217,316,466`에서 확인했다. 서버/도구를 호출하거나 import/초기화하지 않고 소스만 읽었다.
- 수정 전후 권한 대조: `/tmp/dddjango-new-defects-evidence/serena_allowlist_audit.py`가 실제 소스 클래스·편집 marker 상속을 AST로 읽어 frontmatter 패턴과 대조한다. 수정 전 5역할 모두 FAIL(정의 클래스 기준 편집·셸·메모리 쓰기 20개 포함), 수정 후 5/5 PASS(각 7개·편집 0·미정의 0). 로그 `defect2-red.log`, `defect2-green.log`. 이는 도구 설정 대조이며 실제 리뷰어 세션을 실행했다는 뜻은 아니다.
- architect 판단: 명세와 부속 기록의 작성자이며 코드 작성자가 아니므로 같은 제한이 맞다. 기존 명세 작성용 `Edit/Write`, 리뷰어 부속 기록용 `Write`는 유지했다. acceptance-tester/coder는 변경하지 않았다.
- Codex: 원래 각 경계에 코드/명세 수정 금지 문장이 있었지만 Serena 편집·메모리 쓰기·셸 도구 금지는 명시돼 있지 않았다. 다섯 역할 `SKILL.md` 경계에 동일 7개 목록과 금지 한 줄씩을 추가했다. 이 의미 미러들은 ontology corpus 밖이며 산문 정본 절은 변경하지 않았다.
- targeted 검증: 렌더 동기 548절 red/warn/SyncDebt 0, ledger 위반 0, rulepack 재생성 전후 SHA-256 동일(차이 0), rulepack 양쪽 `cmp` 일치. `CLAUDE_CONFIG_DIR=/tmp/dddjango-new-defects-evidence/claude-config DISABLE_AUTOUPDATER=1 claude plugin validate dddjango --strict` exit 0 (`Validation passed`), 사용자 ~/.claude에 쓰지 않도록 설정 경로를 격리했다.
- 커밋: `b2339b84` (`fix(agents): 읽기 전용 역할의 Serena 도구를 명시 허용 목록으로 제한`).
- 전체 검증: `make verify` exit 2, 236초, `/tmp/djr-verify.Bgv9Bh`. 봉인 드리프트 25건 외 green. 봉인 self-test는 M0만 같은 이유로 실패, 나머지 8변이 기대 일치. 봉인 뒤 나머지 검증 별도 실행 exit 0. `make verify-mutation` exit 0, 12변이 전건 탐지. pre-commit 원장과 5개 ttl gate green.


## 결함 3 — 자동 maintenance·사본 삭제 경합 / 삭제 실패 은폐

### 확인한 원인과 한계

- 합성 앵커 생성(`design_pregate.py:3556`의 init/add/commit)이 사용자 Git 자동 정리 설정을 그대로 상속했다. `_git`(`:1118`)에는 훅·서명 억제만 있고 maintenance/gc 억제가 없었다. Git 2.54.0 (Apple Git-157)에서 commit → `maintenance run --auto --quiet --detach` → `repack` → `pack-objects` 발화를 실제 Trace2로 확인했다.
- 재현에서만 전용 `GIT_CONFIG_GLOBAL`에 `gc.auto=1`, `gc.autoDetach=true`, `maintenance.auto=true`, `maintenance.autoDetach=true`를 설정해 작은 저장소에서도 자동 정리 조건을 만들었다. 실제 사용자 Git 설정은 바꾸지 않았다.
- 전용 64MiB 픽스처(2,048 × 32KiB, 고정 난수)의 세 실행 모두 사본 삭제와 repack이 경합해 `object … cannot be read`, `failed to perform geometric repack`, `task 'geometric-repack' failed`, child exit 128을 남겼다. 즉 백그라운드 작업과 삭제 경합은 확정했다.
- `finally`의 `shutil.rmtree(..., ignore_errors=True)`(`수정 전 :3644`)는 삭제 실패를 침묵 처리했다. 실제 rmtree의 마지막 rmdir에 ENOTEMPTY를 주입하자 수정 전에는 폴더 1개가 남고 exit 4·stderr 공백이었다. 이것은 삭제 실패 은폐의 결정적 재현이며, 역사적 두 폴더의 생성 원인을 증명하는 자료로 쓰지 않았다.
- 기존 `design-pregate-209fcbgu`(13:32)·`design-pregate-tk6_lff1`(13:13)은 각각 94파일·32,439/32,428 bytes다. 미니 픽스처 원본 15파일이 모두 동일하고 billing 생성 골격이 추가돼 있었다. 이번 자연 재현에서는 잔여 폴더가 0개였으므로 **기존 두 폴더가 GC 경합 때문에 남았다고 확정하지 않는다**. 사용자에게 확인했으나 실행 명령·중단 여부는 모른다는 답변을 받았다. 따라서 기존 폴더 생성 원인은 미확정이다. 기존 폴더는 삭제·수정하지 않았다.
- registry_gate 사본은 `TemporaryDirectory`(`:830`) 안의 copy/archive이며 새 Git 저장소를 init/add/commit하지 않는다. `anchor_diff.snapshot_anchor:97`도 archive만 한다. 따라서 동일 자동 정리 발화 원인이 없어 registry의 수명 관리 코드는 변경하지 않았다.

### 최초 수정과 반복 검증 (`eeed89ca` 시점)

- `_git` 호출에 `-c maintenance.auto=false -c gc.auto=0`을 넣어 이번 명령과 자식에만 적용했다. 사용자/프로젝트 Git config를 쓰지 않는다.
- rmtree의 `ignore_errors=True`를 제거하고 실패를 `RunError`로 바꿔 잔여 사본 절대 경로를 알리며 exit 1로 끝낸다. `--keep`은 의도적 보존 경로 그대로다. Codex 스크립트는 byte 동일 미러했다.
- 영구 회귀: `workspace/tools/pregate_transcription_smoke.py`의 `ScratchLifecycleTest`. fanout 17의 8개 blob과 `gc.auto=1`로 발화를 강제한 pre-gate 3회, 폴더 0·Git 정리 start 0 단언, 삭제 오류 시 exit 1·경로 진단 단언. 수정 전 2 tests / failures=4(반복 subtest 3개 포함), 수정 후 2 tests OK. 로그 `defect3-red.log`, `defect3-green.log`.

| 재현 | 수정 전 | 수정 후 |
|---|---|---|
| 64MiB, skip 경로 3회 | 각 exit 4, 새 잔여 폴더 0, detached maintenance 1 + repack 1 + pack-objects 1 발화, 삭제 경합 오류 | 각 exit 4, 새 잔여 폴더 0, 정리 프로세스 발화 0 |
| mini_repo + green-spec, registry 포함 3회 | 각 exit 0, 새 잔여 폴더 0, detached maintenance 1 + repack 1 + pack-objects 2 발화 | 각 exit 0, registry 실행 확인, 새 잔여 폴더 0, 정리 프로세스 발화 0 |
| ENOTEMPTY 강제 실패 | 잔여 1, exit 4, 무진단 | 잔여 1, exit 1, 정리 실패·절대 경로 진단(시험 종료 뒤 자기 픽스처만 정리) |

여기서 프로세스 수는 전용 `GIT_TRACE2_EVENT`에 남은 **이번 재현이 시작한 프로세스** 수다. 수정 후에는 분리 프로세스의 시작 자체가 0이므로 종료 뒤 이 실행 소유의 분리 git도 0이다. 다른 레인의 프로세스와 기존 두 폴더는 이 수에 포함하지 않으며, 전역 잔여 0이라고 주장하지 않는다. 어떤 프로세스에도 종료 신호를 보내지 않았다.

재현 명령(저장소 루트):

```sh
PYTHONPATH=workspace/tools python3 -m unittest pregate_transcription_smoke.ScratchLifecycleTest
python3 /tmp/dddjango-new-defects-evidence/pregate_gc_probe.py
python3 /tmp/dddjango-new-defects-evidence/pregate_full_probe.py
```

`pregate_full_probe.py`는 `b2339b84`의 수정 전 design_pregate와 현재 scripts 사본을 비교한다. `pregate_gc_probe.py`는 현재 스크립트로 64MiB 재현을 세 번 실행한다. 둘 다 전용 임시 저장소/설정/Trace2를 쓰고 외부 프로젝트에 접근하지 않는다.

증거:

- `/tmp/dddjango-new-defects-evidence/defect3-before-probe.log`, `defect3-after-probe.log`, `defect3-full-probe.log`, `defect3-before-trace-summary.json`, `defect3-existing-folders.json`.
- 원시 Trace2·각 stdout: `$TMPDIR/pregate-gc-probe-zjlsdepw`(수정 전), `$TMPDIR/pregate-gc-probe-_chc4aet`(수정 후), `$TMPDIR/pregate-full-probe-bmfxmq5v`(전체 전후). 디렉터리 안 `trace-*.jsonl` 또는 `*-trace-*.jsonl`·`*-run-*.log`·`results.json`.
- 커밋: `eeed89ca` (`fix(pregate): 사본의 자동 git 정리 억제와 삭제 실패 명시`).
- 전체 검증: `make verify` exit 2, 268초, `/tmp/djr-verify.zvK8n5`. 봉인 드리프트 28건 외 green. registry unittest 7/7 + 기존 사례 42/42, git_touched 90/90, pregate_transcription 17/17(신규 수명 시험 포함), field_report 38/38, field_report_checker 49/49 통과. 봉인 self-test M0만 드리프트로 실패, 봉인 뒤 ab-score·byte 미러·요청 가이드 검증은 별도 실행 exit 0.
- 직접 만든 3개 재현 입력 저장소(`pregate-*-probe-*/repo`)는 실행 종료 후 정리했고 원시 로그·Trace2·결과 JSON은 남겼다. 기존 두 폴더의 최종 파일 수/크기는 최초 측정과 동일하다.

### 리뷰 후속 수정 — 정리 실패 시 원래 판정 보존

- 원인: 최초 수정 `eeed89ca`의 `design_pregate.py:3648`은 `finally`에서 rmtree 실패를 `RunError`로 다시 던졌다. 이 예외가 이미 계산된 pre-gate 반환값을 덮고 `main`의 실행 불능 처리로 넘어가 exit 1이 됐다. 정리 실패 때문에 판정 근거가 사라지는 문제다.
- 수정: 같은 위치에서 예외를 다시 던지는 대신 stderr에 `격리 사본 정리 실패: <절대 경로> — <오류> (수동 삭제 필요)`를 한 줄 출력한다. 이미 계산된 판정 exit는 그대로 반환한다. `--keep`과 `-c maintenance.auto=false -c gc.auto=0`은 변경하지 않았다. 위 최초 수정 표의 ENOTEMPTY 결과는 이 후속 수정으로 **잔여 1, 원래 exit 4 유지, 절대 경로·오류·수동 삭제 안내 출력**으로 바뀐다.
- 영구 회귀: 기존 `ScratchLifecycleTest`의 ENOTEMPTY 주입 시험을 `test_cleanup_failure_preserves_verdict_and_reports_manual_cleanup`으로 바꾸고, 원래 skip 판정인 exit 4와 정확한 stderr 전체 문구를 단언한다. 잔여 사본 존재 단언과 자동 정리 억제 3회 반복 시험은 유지했다.
- red: 생산 코드를 수정하기 전 HEAD `eeed89ca`에서 갱신한 시험을 실행해 `1 != 4`로 실패했다. 2 tests / failures=1, exit 1. 로그 `/tmp/dddjango-new-defects-evidence/review-cleanup-red.log`.
- green: 수정 후 같은 명령 `PYTHONPATH=workspace/tools python3 -m unittest pregate_transcription_smoke.ScratchLifecycleTest`가 2 tests OK, exit 0. 로그 `/tmp/dddjango-new-defects-evidence/review-cleanup-green.log`.
- 전체 검증: `make verify` exit 2, 306초, `/tmp/djr-verify.aOn14q`. 봉인 드리프트 28건 외 green. pregate_transcription 17/17, field_report 38/38, field_report_checker 49/49 통과. 봉인 self-test는 기존 드리프트로 M0만 red(나머지 8변이 탐지), 봉인 뒤 ab-score·전체 스크립트 byte 미러·요청 가이드 self-test 157/157 및 실제 계약은 별도 실행 exit 0. 로그 `review-cleanup-verify.log`, `review-cleanup-seal-selftest.log`, `review-cleanup-after-seal.log`.
- 미러: source/Codex `design_pregate.py`의 `cmp` exit 0, 전체 scripts `diff -rq` 차이 0. `git diff --check` 통과.
- 커밋: `ed3dd2ea` (`fix(pregate): 격리 사본 정리 실패 시 원래 판정 보존`). `eeed89ca`를 amend하지 않고 그 위에 새 커밋 하나를 추가했다. 변경 파일은 source/Codex 스크립트와 기존 스모크 시험의 3개다.


## 커밋별 전체 검증 · 미러 대조

| 커밋 | make verify | 봉인 드리프트 | 전체 로그 |
|---|---|---:|---|
| `c468223b` | exit 2, 봉인 외 통과 · 303초 | 4건 | `/tmp/djr-verify.z7jzUo` |
| `b2339b84` | exit 2, 봉인 외 통과 · 236초 | 25건 | `/tmp/djr-verify.Bgv9Bh` |
| `eeed89ca` | exit 2, 봉인 외 통과 · 268초 | 28건 | `/tmp/djr-verify.zvK8n5` |
| `ed3dd2ea` | exit 2, 봉인 외 통과 · 306초 | 28건 | `/tmp/djr-verify.aOn14q` |

네 실행 모두 `verify-ontology`, `verify-base-cross`, `verify-base-backstop`, `verify-base-regen` green. `verify-base-core`는 manifest 드리프트 검사에서 멈췄다. 뒤에 위치한 검증을 생략하지 않고 각 커밋마다 별도 실행했다: manifest self-test는 M0만 같은 드리프트로 red(나머지 8변이 탐지), ab-score self-test·스크립트 미러·요청 가이드 157개 self-test·실제 계약은 green. 따라서 **make verify 자체가 green이었다고 기록하지 않는다**.

최종 미러 확인은 다음 모두 exit 0이다.

```sh
cmp dddjango/scripts/registry_gate.py codex-dddjango/skills/dddjango/scripts/registry_gate.py
cmp dddjango/scripts/design_pregate.py codex-dddjango/skills/dddjango/scripts/design_pregate.py
cmp dddjango/scripts/rulepack.json codex-dddjango/skills/dddjango/scripts/rulepack.json
diff -rq dddjango/scripts codex-dddjango/skills/dddjango/scripts --exclude=__pycache__
```

추가 확인: 결함 2의 `ontology_render_sync.py`(이 저장소의 렌더 검사 명령; render.py에는 `--check` 없음), ledger, `make rulepack` 재생성 무차이, `make verify-mutation`, `claude plugin validate dddjango --strict`가 통과했다. 모든 커밋에 지시한 공동 작성자 trailer를 넣었다.

## 지시 대비 차이 · 추가 발견 · 남은 일

- 결함 3의 자연 재현에서 폴더 잔류 자체는 재현되지 않았다. 실제로 확인한 것은 자동 분리 maintenance와 삭제 경합이며, 삭제 실패 은폐는 ENOTEMPTY 주입으로 따로 증명했다. 기존 폴더의 생성 명령·중단 여부는 사용자도 모른다고 답했다. 이를 추측으로 GC 누수라고 결론 내리지 않았다.
- 관찰된 약 3.2GB 사본을 복제하는 대신 64MiB 입력과 낮춘 자동 정리 임계값으로 원인을 재현했다. 프로세스 수는 전용 Trace2의 시작 이벤트로 계수했으며 다른 세션의 프로세스를 종료하거나 전역 0이라고 주장하지 않았다.
- 추가로 확인한 같은 결함(미수정): `dddjango-web/agents/design-review-web.md:4`, `discipline-reviewer-web.md:4`, `design-architect-web.md:4`에도 Serena wildcard가 있다. web의 편집 담당 coder wildcard는 결함으로 분류하지 않았다. 두 web 트리는 수정하지 않았다.
- 운영자에게 남은 일: 네 커밋 리뷰, 재검증, 봉인 드리프트 정렬, 사용자 승인 후 main 반영. 이 작업에서는 봉인 chore·push·main 변경을 하지 않았다. 기존 임시 폴더는 생성 이력 증거가 생기면 원인을 추가 판별할 수 있다.

## 범위와 금지 사항

Serena 사용 여부: 사용하지 않음 — 지시서의 사용 금지에 따라 서버/도구 호출 없이 정의 소스만 읽었다. Graphify도 사용하지 않았다. 다른 프로세스·옛 임시 폴더·web 플러그인·main·원격은 변경하지 않았다. `.venv`, 지시서, 이 보고서는 커밋 대상에서 제외한다. 봉인은 재발행하지 않는다.

REPORT-DONE
