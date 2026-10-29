# dddjango-web 2.8.4 — 근거 노드는 좁힌 실행 줄에 더하지 않고 따로 돈다 (F4-128)

## 문제
- 현장 보고 F4-128(높음 · 두 레인에서 같은 결함): coder-web 의 규칙 «근거 노드 id 를 슬라이스 끝 시험 줄의 **모든 단계**에 더해 돈다»를 글자대로 따르면, pytest 가 폴더 인자를 그 노드로 좁혀 나머지 시험을 조용히 빼고도 exit 0 을 낸다. 레인 실측: 수집 15128 → 2651, 16286 → 2996. 녹색처럼 보이지만 슬라이스 끝 시험을 다 돈 것이 아니다.
- 뿌리: pytest 8.4.2 는 겹치는 인자를 좁힌다. 재현(저장소 밖 장난감 — 폴더 `web_test/a` · `web_test/b` · `other_test` 마다 시험 셋):
  - `pytest web_test other_test` → 9 · 여기에 `web_test/a/test_m1.py::test_1` 를 더하면 → 4(`web_test` 가 그 노드 하나로 좁혀지고 `other_test` 셋은 남는다).
  - `pytest web_test web_test/a/test_m1.py::test_1` → 1 · `pytest web_test web_test/a/test_m1.py` → 1 · `pytest web_test web_test/a` → 3(6 아님).
  - 겹치지 않는 인자끼리는 좁히지 않는다. 노드 id 둘끼리도 괜찮다.
- 러너(`backstop.py --test-scope`)가 내는 줄은 스스로 겹치지 않는다(`_ancestors_only` 로 조상만 남김). 겹침은 규칙이 시킨 «더하기»에서만 생긴다.
- 안전한 자리: `refactor_audit.py switch-check` 는 대상 노드를 하나씩 돌리고 대상 밖으로 수집된 노드를 거절한다. core(dddjango)는 근거 시험을 따로 돌리고 더하기 규칙이 없다.

## 고침 (역할 · 조정자 · 지식 글 · scripts 무변)
- **coder-web**(입력 «`test_command` · 시험 범위 실행문» 줄): 좁힌 실행 줄에 시험 경로 · 노드 id 를 더하지 않는다. 근거 노드는 따로 돈다. 근거 시험마다, 실행문이 낸 `[test-scope] 단계 <i>:` 줄마다 `{경로}` 자리를 그 노드 id 하나(셸 따옴표로 감싼다)로 바꾼 줄을 돈다. 다른 낱말은 그대로고, 단계를 빼지 않는다(표식으로 나눈 단계면 노드는 제 표식의 단계에서만 수집된다). 일꾼 지정(`-n` · `--numprocesses`)이 그 단계 줄이나 설정 `addopts`에 있으면 줄 끝에 `-n0`을 붙인다(뒤 값이 이긴다 — 완성 화면 그림 case 실행 · 계층 중 줄과 같은 까닭). 한 pytest 실행에 시험 경로(폴더 · 파일)와 노드 id 를 함께 주지 않는다는 금지와 그 까닭(조용히 좁혀지고 exit 0)을 적는다.
  - 옛 갈래 «슬라이스 끝 줄이 없으면 `test_command` 단계마다 경로를 노드 id 로 바꾼 줄»은 새 규칙 하나에 들어간다(슬라이스 끝 줄이 있든 없든 같은 방법).
  - 노드 하나에 한 번씩 도는 까닭: 그 실행의 `N passed` 줄이 곧 그 노드의 «수집되어 통과» 증거다(매개변수 함수면 N 이 1 보다 크다). 여럿을 한 번에 돌리면 단계마다 어느 노드가 빠졌는지 셈으로 따져야 한다.
  - 보고 증거: `근거 <경로::함수>: 통과(수집됨)` 에 그 노드 id 가 든 실행 줄과 그 실행의 `N passed` 줄을 함께 적는다.
  - «근거 id 문제»(`not found` · `no tests ran` · exit 4)는 모든 단계를 돈 뒤에 정한다 — 표식으로 나눈 단계에서 다른 단계의 `deselected`(exit 5)는 정상이다. 조정자의 커밋 전 확인(Phase 2 step 3.1)도 «어느 단계에서도 수집되지 않았으면»으로 맞춘다.
  - «브라우저 실행 환경»은 근거 노드 실행에도 걸린다(«좁힌 실행 · 근거 노드 실행»).
- **조정자 «시험 범위»의 «근거 노드»**: 같은 방법을 적는다. «어느 단계에서든 수집되어 통과해야 통과 · 모든 단계에서 수집 0 이면 미실행»은 그대로 둔다.
- **design-architect-web «근거 시험 요건»**: «슬라이스 끝에 함께 돈다» → «슬라이스 끝에 따로 돈다(좁힌 실행 줄에 더하지 않는다)». 입장 표 `슬라이스` 칸 설명의 «근거 시험을 함께 돌리는» → «따로 돌리는».
- **조정자 리팩토링 ⑤ 실행 규칙 «요동»**: «같은 단계 명령에 그 노드 id만 붙여 1회 다시 돌려» → «같은 단계 명령의 시험 경로 인자를 그 노드 id 로 바꿔(경로 인자가 없는 단계는 노드 id 만 더한다 — 경로와 노드 id 를 함께 주지 않는다) 1회 다시 돌려 그 노드의 `FAILED`·`ERROR` 줄이 다시 나오면». 겹치지 않는 경로 인자가 있는 단계(`pytest web_test other_test`)에 노드를 붙이면 그 경로 전체가 함께 돌아 기준선 실패가 섞인다.
- **implementation-test §1 실행 문단**(pytest 방법을 맡는 지식): 한 실행에 시험 경로와 노드 id 를 함께 주지 않는다는 문장과 그 까닭 한 줄을 더한다(references byte 미러).
- Claude · Codex 같은 글(조정자 «시험 범위» 문단은 기존 문단 대조 표지로 지킨다).
- `Makefile` verify-web 에 한 덩이를 더한다:
  - 두 조정자 · 두 coder-web 에 «시험 경로(폴더 · 파일)와 노드 id 를 함께 주지 않는다» · «줄 끝에 `-n0`을 붙인다» 문장이 있다.
  - 조정자 · coder-web · architect 여섯 파일에 걷은 말(`에 더해 돈다` · `슬라이스 끝에 함께 돈다` · `근거 시험을 함께 돌리는` · `노드 id만 붙여`)이 다시 들지 않는다.
  - coder-web 입력 줄(`**build-state의 \`test_command\`**`) · architect «근거 시험 요건» 줄은 Claude · Codex 가 같다(플랫폼 낱말 치환 뒤).

## 행동 변화
- 슬라이스 끝 시험 줄이 web 시험 전체(또는 러너가 고른 범위)를 끝까지 돈다. 이 슬라이스가 깨뜨린 다른 시험이 근거 노드 때문에 빠져 녹색으로 보이던 일이 없어진다.
- 근거 노드 실행은 «노드 수 × 단계 수» 만큼 따로 돈다(옛 규칙의 주 경로는 추가 실행이 없었다 — 새 비용이다). 일꾼을 `-n0` 으로 두어 한 번에 짧다(장난감 실측 `-n auto` 2.1초 → `-n0` 0.0초 · 큰 호스트는 일꾼마다 Django import 가 더해진다). 표식으로 단계를 나눈 호스트(예 `-m "not browser"` · `-m browser`)에서는 노드마다 한 단계가 `1 passed`, 다른 단계는 `1 deselected`(exit 5)다.
- `-n0` 이 없으면(일꾼을 띄우면) 표식으로 빠진 노드와 없는 노드가 똑같이 `no tests ran`(exit 5)으로 나와 «근거 id 문제»를 가를 수 없다(실측). `-n0` 이면 빠진 노드 `1 deselected` exit 5 · 없는 노드 `ERROR: file or directory not found` exit 4.

## 행동 시험 (저장소 밖 장난감 프로젝트 · pytest 8.4.2)
- 꼴: `test_command` = `pytest web_test -m "not browser" && pytest web_test -m browser` · 시험 넷(`test_v1.py::test_1` · `test_v1.py::test_p[a-b]` · `test_v2.py::test_2` · 표식 `browser` 의 `test_b.py::test_ui`) · 이번 슬라이스가 `test_v2` 를 깨뜨린다 · 근거 노드 `test_v1.py::test_p[a-b]`(매개변수 · 따옴표 필요) · `test_b.py::test_ui`(browser 단계).
- 러너 출력: `단계 1: pytest {경로} -m 'not browser'` · `단계 2: pytest {경로} -m browser` · `슬라이스 끝 시험 1/2: pytest web_test -m …`.
- 옛 규칙(슬라이스 끝 줄 모든 단계에 노드 둘 더함): 단계 1 `1 passed, 1 deselected` exit 0 · 단계 2 `1 passed, 1 deselected` exit 0 → **깨진 `test_v2` 가 빠지고 녹색**.
- 새 규칙 ① 슬라이스 끝 줄 그대로: 단계 1 `FAILED test_v2.py::test_2` · `1 failed, 2 passed, 1 deselected` exit 1(붉음이 드러남) · 단계 2 `1 passed, 3 deselected` exit 0.
- 새 규칙 ② 근거 노드마다 단계 줄마다: `test_p[a-b]` 단계 1 `1 passed` exit 0 · 단계 2 `1 deselected` exit 5 / `test_ui` 단계 1 exit 5 · 단계 2 `1 passed` exit 0 → 두 노드 모두 «수집되어 통과».

- 일꾼 단계(둘째 장난감 · `test_command` = `pytest web_test -n auto -m "not browser" && pytest web_test -n auto -m browser`): 러너 `단계 1: pytest {경로} -n auto -m 'not browser'` · 슬라이스 끝 줄 `pytest --maxprocesses=6 web_test -n auto -m …`. 새 절차(`{경로}` = 노드 · 줄 끝 `-n0`): `test_p[a-b]` 단계 1 `1 passed` exit 0 · 단계 2 `1 deselected` exit 5 / `test_ui` 단계 1 `1 deselected` exit 5 · 단계 2 `1 passed` exit 0 / 없는 id `test_typo.py::test_ui` 두 단계 모두 `ERROR: file or directory not found` exit 4 → «근거 id 문제»로 갈린다.

## 한계
- 규칙은 글이다. coder-web 이 근거 노드를 다시 줄에 더해도 막는 결정적 장치는 없다. 감수 · 조정자의 근거 노드 확인(«통과(수집됨)» 출력 줄)이 본다. 러너가 근거 노드 줄을 직접 내게 하는 길은 이번 판 밖이다(현장에서 글대로 따로 돌린 두 레인이 모두 맞게 돌았다).
- pytest 의 겹침 좁히기는 8.4.2 에서 잰 동작이다. 다른 판에서 덜 좁혀도 새 규칙(겹치지 않게 따로)은 그대로 맞다.

## 독립 검토 반영(차단 0 · 중요 3 · 사소 5 — 모두 반영)
- 중요 1 요동 재실행이 새 금지를 어김 → ⑤ «요동» 글 고침(위).
- 중요 2 일꾼 단계에서 «표식으로 빠짐»과 «없는 id»가 같은 출력 · 중요 3 비용이 옛 갈래와 같다는 주장 → 근거 노드 실행에 `-n0` · «모든 단계를 돈 뒤에 정한다» · 비용 문장 바로잡음(둘 다 운영자가 장난감에서 다시 재현).
- 사소: 보고 증거 줄(노드 id 가 든 실행 줄 + `N passed`) · architect `슬라이스` 칸 «함께 돌리는» · «제 표식의 단계에서만»을 표식으로 나눈 단계로 좁힘 · 브라우저 실행 환경을 근거 노드 실행에 · verify-web 그물 넓힘(걷은 말 `에 더해 돈다` · `노드 id만 붙여` · architect 줄 대조).
- 받지 않은 것 없음. 설정으로 단계를 나눈 호스트(`--ds=a` · `--ds=b`)에서 노드가 두 단계 모두에서 수집되고 한쪽만 붉은 경우의 판정은 옛 규칙에도 있던 문제라 이번 판 밖이다.

## 검증
- `make verify-web` green.
- 새 verify-web 덩이를 붉게 확인: 옛 글(HEAD) → «따로 돌기 문장이 없다» · Codex coder 줄 한 낱말 어긋남 → «Claude·Codex 불일치» · architect 의 걷은 말 되살림 → «걷은 근거 노드 더하기 말이 다시 들었다».
