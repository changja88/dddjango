# 축소 재리뷰 (2026-09-15)

대상: 수정 라운드(`c578b9c1` 구현 리뷰 반영 · `22fcc0d0` 봉인 재발행 · `b8c1db75` B3 4회차 기록) — 1차 독립 구현 리뷰(`impl-review.md`, MAJOR 3·MINOR 11) 발견 14건이 실제로 닫혔는지만 본다. 파일 수정 0 · 서브에이전트 0 · git 쓰기 0. 코드는 읽기·실행만 했다(테스트·스크립트 실행 — git/설치/네트워크 없음). Serena·Graphify는 이 워크트리에 opt-in 표식이 없어 미사용.

| 1차 발견 | 판정 | 근거 |
|---|---|---|
| [MAJOR] Q1 — B4(Codex) 미실행인데 §7이 «B4에서 확인 후 H2 확정»으로 적어 근거 0 | 사유 있는 미반영 | 설계 §3 B4 행·§8을 «이번 배치 미실행 — 배포 후 첫 Codex 세션의 active 줄로 확인(릴리즈 노트에 확인 요청)»으로 정직하게 재작성(문서 불일치라는 지적 자체는 해소). `.codex-plugin/plugin.json`에 미검증 `hooks` 필드를 억지로 추가하지 않은 판단도 타당(문서 근거 없는 키 삽입이 더 위험). 다만 Codex 실제 경로(`${PLUGIN_ROOT}` 치환·`hooks.json` 자동 발견)는 여전히 미검증 — 사용자 `~/.codex` 상태를 건드리는 부작용을 피하려는 사유(behavior.md B4)가 타당하므로 미반영을 수용 |
| [MAJOR] Q1 — 빌드 0이면 SessionStart도 무출력 → 첫 빌드 종료마다 거짓 «미작동» | 닫힘 | `evidence_debt_hook.py:146-149` `run()`이 `roots`(=`.dddjango-web/` 발견 여부)만으로 분기하고 `builds`가 비어도 SessionStart는 always active(코드 확인). `test_session_start_active_even_with_zero_builds` 통과(실행 기록 ①). Coordinator `:154`·SKILL `:151`·REQUEST_GUIDE 양쪽 모두 «폴더가 없는 첫 실행은 무출력이 정상»으로 한정 문구 추가 확인(diff 직접 대조) |
| [MAJOR] Q6 — behavior.md는 설계 §3 B3 ②(리터럴 앵커) 미충족을 정직히 적었지만 §3을 고치지 않아 명세·기록 불일치 | 사유 있는 미반영 | 설계 §3 B3 행이 «①/② 결정 요구+수치·사유 일치/③ 금지 tool_use 0»으로 합격 조건을 재정의하고 원문 인용은 «규범(N1-2) 요구로 두되 합격 조건 아님»으로 명시(§3·§8 동일 문구). behavior.md B3 4회차 «판정과 기준 조정(정직 기록)» 문단이 무엇을 낮췄고 왜인지 명시(행동 목표 2회 연속 성립·표기 목표만 미달). 4회차 결과를 `b3r4_final.py`로 직접 재실행해 재현(실행 기록 ③) — 앵커 문자열은 두 assistant 블록 어디에도 없고(`ANCHOR` 플래그 모두 공백), 결정 요구·defer 허용 재구성(«완료 빌드 G2 승인은 유보 가능»)은 정확히 옮겨짐. 조정 자체 타당성 의견: 안전 특성(재동결 전 결정 게이트)은 2회 연속 성립했고 grep 가능성은 부차 목표이므로 합격 조건에서 빼고 규범 요구로 낮춘 것은 합리적 |
| [MINOR] Q1 — D1 헤더 «검사기가 읽는다»가 실제와 다름(검사기는 안 읽음) | 닫힘 | D1 헤더가 «Coordinator가 쓴다 · hook이 읽는다 · 검사기는 읽지 않는다 — inputs 게이트 불변이 곧 defer의 한계»로 수정(설계 §2 D1, diff 직접 대조) |
| [MINOR] Q1 — 봉인 순서 어긋남(sealed_commit이 Makefile 변경 전 커밋을 가리킴 → strict RED) | 닫힘 | `manifest_seal.py --check`(strict) 재실행 결과 «sealed_commit 의 내용이 봉인값과 다르다 — protocol/Makefile» 항목 소멸(실행 기록 ②, 18건 잔존은 전부 `external_annex` — 1차 리뷰가 이미 "이 브랜치 무관"으로 확인한 기존 draft 항목). `22fcc0d0`가 Makefile 변경 커밋(`bcc8ef16`)·수정 커밋(`c578b9c1`) **뒤**의 별도 chore 커밋으로 재봉인(`sealed_commit=c578b9c1`, `git show --stat` 확인). DEVELOPMENT.md §6에 재봉인 순서 1줄 추가 확인 |
| [MINOR] Q2 — 술어가 검사기보다 관대(포인터 키 집합·필드 집합·`interactions: null`) | 닫힘 | `evidence_debt.py`에 `has_interaction_evidence`(엄격) 신설 — 정확 필드 집합 + `interactions`가 정확 `{path,sha256}` dict 요구. `check_design_evidence.py`가 `OBSERVATION_V1/V2_FIELDS`를 evidence_debt에서 import(단일 출처), 검사기 자체 `INTERACTION_FIELDS`와 비충돌 확인(`test_checker_imports_predicate_and_field_sets` — `assertNotEqual` 통과). `rv_q2_parity.py` 재실행 결과 1차 MISMATCH 4행(필드 누락·미지 필드·포인터 extra key·포인터 missing sha256) 전부 MATCH로 전환(실행 기록 ④). `interactions: null`은 픽스처의 `sync()`가 포인터를 자동 재결속해 원 스크립트로는 재현 불가하다는 걸 발견했고, 1차 리뷰가 쓴 우회 스크립트 `rv_q2_null.py`(직접 파일 기록)로 재실행하니 checker DEFECT · predicate 1 undecided로 일치(이전 0 clear에서 개선, 실행 기록 ⑤) |
| [MINOR] Q3 — `user-prompt`가 error 빌드도 매 프롬프트 출력(영구 소음·off 스위치 없음) | 닫힘 | `run()`의 user-prompt 분기가 `if not undecided: return 0`로 바뀌어 error는 SessionStart 전용(제안한 두 대안 중 첫째를 채택). `test_error_build_reported_on_session_start_only` 통과(실행 기록 ①) — user-prompt에서 error 빌드 존재해도 무출력, session-start에서만 `error 1` 표기 |
| [MINOR] Q3 — 예외 경로 미검증·침묵(EACCES 등) | 닫힘(테스트 한계는 정직히 기재) | `_candidates`·`_has_builds`가 `OSError`를 흡수하도록 코드 변경 확인(`evidence_debt_hook.py:62-66`·`70-74`). `main()`의 최상위 except가 SessionStart면 오류를 JSON(`additionalContext`/`systemMessage`)으로도 내보내도록 변경(코드 확인). §8이 «예외를 외부에서 유발하는 테스트는 없음 — 3.14에서 `is_dir`가 raise하지 않아 재현 불가, 코드 검토로 대신»이라고 한계를 숨기지 않고 적음 — 타당한 사유 |
| [MINOR] Q5 — 수정 모드 :205 step-4 합류 목록에 증거 부채 결정 누락 | 닫힘 | Coordinator `commands/dddjango-web.md`·Codex `SKILL.md` 수정 모드 step 1 모두에 «**hook이 고지한 폴더의 증거 부채 결정 포함**» 문구 추가 확인(diff 직접 대조, 양쪽 동형) |
| [MINOR] Q5 — defer 허용 집합이 부정 정의라 G2 승인·마무리 backstop이 «구현 재진입»인지 불명 | 닫힘 | D1·N1-1(step 4)에 **허용 집합**(재동결·조회·보고 + 완료 빌드 G2 승인·마무리 backstop, K3 legacy 조건 불변 명기) / **구현 재진입**(Phase 1·수정 모드 편집·트리비얼 편집·coder 호출)을 열거로 명문화(diff 직접 대조). B3 4회차 실세션에서 Coordinator가 «유보를 선택해도 G2 승인 → 병합 진행은 막히지 않습니다. 다만 구현 재진입은 이후 ⓐ를 거쳐야»라고 정확히 이 구분대로 설명함을 `b3r4_final.py` 배너 전문으로 확인(실행 기록 ③) — 규범뿐 아니라 실제 발화로도 검증 |
| [MINOR] Q5 — 결정을 scope.md 제약 절에도 기록하면 scope 바이트 변경 → 포인터 sha·review digest 불일치 | 닫힘 | step 4 문구가 «결정은 `build-state.json.evidence_debt`에만 기록한다(인용은 `quote` 필드 — `scope.md`에는 적지 않는다: scope 바이트가 바뀌면 `design-input.json.scope` 포인터·review digest가 어긋난다)»로 변경(diff 직접 대조, Coordinator·SKILL 동형). D1도 «기록처는 build-state 한 곳» 명시 |
| [MINOR] Q6 — hook 문구 «(observation v1/absent)»의 «v1»이 규범 어휘(interactions.json v1)와 충돌해 오독 유발 | 닫힘 | undecided 줄 판형이 `static-only <a> · missing <b> · unreadable <c>` 구조로 교체되고 «v1» 어휘 제거(코드 확인). `test_user_prompt_reports_undecided`에 `self.assertNotIn('v1', context)` 추가·통과. B3 4회차 실세션에서 3회차의 오독(«v1 표준 포맷 부재»)이 사라지고 «static-only» 그대로 옮겨짐을 `b3r4_final.py`로 직접 재현 확인(실행 기록 ③) |
| [MINOR] Q6 — B3 3회차가 설계가 요구한 격리(`CLAUDE_CONFIG_DIR`) 없이 돌았는데 behavior.md가 override 로그·init `plugins[].source` 근거를 인용 안 함 | 닫힘 | behavior.md B3 절에 «3회차 격리 주석(독립 구현 리뷰 지적)» 문단이 추가되어 `:33 Plugin "dddjango-web" from --plugin-dir overrides installed version`과 init `plugins[0] = {source: 'dddjango-web@inline', …}`을 직접 인용함을 확인(behavior.md 원문 읽음) |
| [MINOR] Q7 — DEVELOPMENT §6 «Codex 재신뢰 1줄» 규칙이 `_release`에 배선 안 됨·REQUEST_GUIDE에 Claude 쪽 줄 없음 | 사유 있는 미반영 | REQUEST_GUIDE 양쪽(Claude·Codex, byte 미러 `cmp` exit 0)에 «Claude Code는 플러그인을 갱신하면 다음 세션부터 자동으로 켜집니다(추가 조치 없음)» 추가 확인 — 비대칭 문제는 닫힘. `_release` 자동 배선은 §8이 «릴리즈 스크립트 변경 → 재봉인 연쇄 위험»을 사유로 명시적으로 보류하고 실제 릴리즈 시 `gh release edit` 수동 추가로 대체한다고 적음 — 수정 라운드 범위(스크립트 자체를 건드리면 이번 수리와 무관한 재봉인이 또 발생)를 고려하면 타당한 판단 |

## 실행 기록

① 단위 테스트 4종 실제 실행
```
$ cd dddjango-web/scripts && python3 test/test_interaction_evidence.py
Ran 45 tests in 13.398s — OK
$ python3 test/test_design_evidence.py
Ran 40 tests in 32.594s — OK
$ python3 test/test_evidence_debt.py
Ran 19 tests in 0.083s — OK   (1차 리뷰 시점 15 → 19, 신규 4건: 엄격 술어·필드 집합 정확성·검사기 상수 비충돌)
$ python3 test/test_evidence_debt_hook.py
Ran 17 tests in 1.148s — OK   (1차 리뷰 시점 16 → 17, 신규: session-start 빌드 0 active 줄)
```
mirror·byte 대조:
```
$ diff -rq --exclude=__pycache__ dddjango-web/scripts codex-dddjango-web/skills/dddjango-web/scripts
mirror exit=0
$ cmp dddjango-web/REQUEST_GUIDE.md codex-dddjango-web/REQUEST_GUIDE.md
guide exit=0
$ grep -c "evidence debt\|evidence_debt\|증거 부채\|evidence hook" dddjango-web/commands/dddjango-web.md
5
$ grep -c "evidence debt\|evidence_debt\|증거 부채\|evidence hook" codex-dddjango-web/skills/dddjango-web/SKILL.md
5
```
`make verify-web` 전체 재실행(스크립트 실행 — git/네트워크 없음): exit=0. `fixtures_evidence_debt.sh` 내부에서도 19/17 OK 확인. `codex 미러 byte 대조`·`REQUEST_GUIDE byte 미러 대조`·`hooks.json 계약(Claude·Codex)` 전부 PASS. `claude plugin validate dddjango-web --strict` → ✔ Validation passed.

② 봉인 재확인
```
$ python3 workspace/tools/manifest_seal.py --check
[manifest] RED · 지적 18건 — 전부 external_annex.orders.* PENDING (이 브랜치 무관, 1차 리뷰가 이미 확인한 기존 draft 항목)
   ※ "sealed_commit 의 내용이 봉인값과 다르다 — protocol/Makefile" 행 소멸(1차 리뷰 시점 19건 중 1건이었던 이 항목이 이번엔 없음)
$ python3 workspace/tools/manifest_seal.py --check --draft
green · 그룹 10 · 봉인 파일 261 · 배정 18런
$ git show --stat 22fcc0d0
chore: verify 봉인 재발행 (Makefile verify-web hooks 계약 배선 커밋 이후 — sealed_commit 정렬)
 workspace/eval/ab/T2-0b-manifest.json | 4 ++--
$ python3 -c "import json; print(json.load(open('workspace/eval/ab/T2-0b-manifest.json'))['sealed_commit'])"
c578b9c1b7a826b960766653c5e1fa0cb3622880   (수정 커밋 이후 — bcc8ef16(T2, Makefile 변경) 뒤)
```

③ Q6 — B3 4회차 재현(`b3r4_final.py`, `b3r4-stream.jsonl` 직접 실행)
```
$ python3 b3r4_final.py
assistant text blocks: 2 · [0] 57자 · [1] 1772자(배너) · 앵커(`[dddjango-web] evidence debt`) 포함 블록: 0/2
마지막 텍스트 발췌: "증거 부채 훅이 이 폴더를 미결정으로 플래그하고 있습니다: 12/12 case가 조작 상태(dropdown/dialog/toggle)
관찰 없이 static-only입니다. 규율상 이 폴더에서 재동결을 포함한 어떤 실행도 이 결정 전에는 할 수 없습니다 …
① 증거 부채 — ⓐ 지금 관찰(…) vs ⓑ 유보(defer — 비구현 실행만 허용, 지금 상황엔 재동결·완료 빌드 G2 승인이 해당)…
이 화면은 이미 G2가 완료된 빌드이므로, ⓑ 유보를 선택해도 "G2 승인 → 병합" 진행은 막히지 않습니다.
다만 유보를 선택하면 구현 재진입(새 코드 수정)은 이후 언젠가 ⓐ를 거쳐야 합니다."
결정 요구(ⓐ/ⓑ) 포함: True
```
— «v1» 어휘 없음(static-only로 대체) · defer 허용/재진입 구분이 규범 문구와 일치 · 리터럴 앵커는 여전히 의역(설계 §3·§8이 이를 합격 조건에서 뺀 것과 일치).

④ Q2 parity 재실행(`rv_q2_parity.py`, 수정된 코드 대상)
```
$ python3 rv_q2_parity.py
v2 missing required field trace  | checker: DEFECT ['…exact version 1 or 2 fields required']  | predicate: debt 1/1 status=undecided   (1차: 0/1 clear ← MISMATCH 해소)
v2 extra unknown field           | checker: DEFECT ['…exact version 1 or 2 fields required']  | predicate: debt 1/1 status=undecided   (해소)
pointer extra key                | checker: DEFECT ['…exact path/sha256 object required']     | predicate: debt 1/1 status=undecided   (해소)
pointer missing sha256           | checker: DEFECT ['…exact path/sha256 object required']     | predicate: debt 1/1 status=undecided   (해소)
```
(참고: 같은 실행에서 `pointer absolute path`행이 스크립트 자체의 `checker_debt` 판정 substring 목록에 "nonempty relative path required"가 빠져 있어 `<== MISMATCH`로 잘못 표시됨 — checker·predicate 둘 다 그 case를 문제로 보는 것은 동일하므로 실제 동작 불일치는 아니고 재사용한 1차 리뷰 스크립트 자체의 분류 누락이다.)

⑤ Q2 — `interactions: null` 재실험(1차 리뷰가 남긴 우회 스크립트 `rv_q2_null.py` — 픽스처 `sync()`의 포인터 자동 재결속을 우회해 직접 기록)
```
$ python3 rv_q2_null.py
checker: ['cases[related/list].interactions: exact path/sha256 object required']
predicate: 1 undecided   (1차 리뷰 시점: 0 clear ← MISMATCH 해소)
```
(원래 `rv_q2_parity.py`의 `set_obs(t, interactions=None)` 시나리오는 `InteractionEvidenceTests.write_observation`이 `'interactions' in observation`이면 포인터를 자동 재결속해 null이 실제로는 기록되지 않는 픽스처 한계가 있음을 확인 — 이번 재리뷰에서 새로 발견했으나 구현 결함이 아니라 재사용 스크립트의 픽스처 한계이므로 별도 미해결 항목으로 세지 않았다.)

## 부기 — 재리뷰 중 발견한 스크립트 한계(구현 결함 아님)

`rv_q2_parity.py`의 `checker_debt` substring 목록 누락(④)과 `write_observation`의 포인터 자동 재결속(⑤)은 1차 리뷰가 남긴 **재사용 스크립트 자체의 한계**이며 수정 라운드의 코드·문서 어디에도 새 결함을 내지 않았다. 참고로만 남긴다.

판정: 승인
