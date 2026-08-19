# 적대 검증 레인 S — 검증 하네스 자체의 신뢰성 (T2-1)

너는 독립 적대 검증자다. 저장소 `/Users/hyun/Desktop/dddjango`(read-only)에서 **T2-1이 «green»을 주장하는 근거인 하네스들이 실제로는 결함을 못 잡는다는 것을 실증하라**. 칭찬·요약은 쓰지 마라 — 결함만 쓴다.

## 배경(사실)

T2-1은 두 하네스를 신설해 `make verify`(정확히는 `verify-base` 레시피 — `Makefile` 참조)에 편입했고, 이 둘이 «검사기 개작이 안전하다»는 주장의 근거다:

1. `workspace/tools/checker_baseline_matrix.py` — 27종 × 자기 red 픽스처에서 `{exit·parsed·unparsed·synthetic}`을 실측해 내장 `EXPECTED`와 대조. `parsed`는 `dddjango/scripts/registry_gate.py`의 `_FINDING_RE`를 import해 계수한다. 산출 표는 `workspace/eval/ab/T2-checker-baseline.md`.
2. `workspace/tools/findings_count_matrix.py` — 27종 × red 픽스처에서 findings/0 레코드의 `{exit·violation 수·info 수·rule 분포·violation_id 집합 sha16}`을 실측해 내장 `EXPECTED`와 대조하고, green 픽스처에서 «exit 0·레코드 0»을 단언. `CONVERTED`는 REGISTRY 파생이며 27 assert가 걸려 있다.

기존 하네스도 참고: `workspace/tools/fixture_matrix.py` · `workspace/tools/findings_smoke.py` · `workspace/tools/api_error_backstop_matrix.py` · `workspace/tools/checker_cross_matrix.py` · `dddjango/scripts/registry_gate.py`.

**핵심 의심**: 두 신설 하네스의 `EXPECTED`는 **저자가 만든 도구로 저자가 실측한 값**을 그대로 내장한 것이다(자기 참조). 도구가 틀렸으면 틀린 값이 «정답»으로 동결된다.

## 검증 과제 (전부 실측으로)

1. **EXPECTED의 독립 재현**: 두 하네스의 내장 기대값을, 그 하네스를 쓰지 않고 **직접** 재현하라(검사기를 직접 실행해 라인을 세고 레코드를 파싱하는 별도 스크립트를 `/tmp`에 작성). 값이 다른 항목을 적출하라. 특히 `parsed`/`unparsed` 정의(빈 줄 처리·stderr 병합·정규화)가 `registry_gate`의 실제 계수 방식과 정말 같은지, `violation_id` 집합 sha가 의미 있는 동일성 축인지.
2. **하네스가 못 잡는 회귀 구성**: 검사기에 **의도적 결함**을 넣었을 때(예: 위반 1건을 레코드에서 누락, rule을 남의 번호로 바꿈, severity를 뒤집음, where를 빈 문자열로, 라인은 그대로 두고 레코드만 조작) 두 하네스가 red가 되는가. `/tmp`에 검사기 사본을 만들어 변조하고 하네스를 그 사본에 겨눌 수 있는지 조사하라. **red가 되지 않는 변조 유형**이 곧 하네스의 사각이다 — 전부 열거하라.
3. **fail-open 적출**: 두 하네스에서 재료 결손·예외·타임아웃·픽스처 부재 시 «조용히 통과»하는 경로가 있는가(exit 0인데 실제로는 검사가 안 돈 경우). `EXPECTED.get(script)`가 None일 때, `CONVERTED`와 `EXPECTED` 키 집합이 어긋날 때, 레코드 파일이 안 생겼을 때의 거동을 코드로 확인하고 실행으로 실증하라.
4. **hermetic 가정의 타당성**: 두 하네스가 픽스처를 임시 디렉터리로 복사해 실행하는데(비-git), 이 «비-git이라 fail-closed 레인을 탄다»는 가정이 27종 전부에 성립하는가. git 유무로 결과가 갈리는 검사기에서 하네스가 실제 사용 환경(git 저장소 안)의 동작을 검증하지 못하는 갭을 적출하라.
5. **verify 편입의 실효성**: `Makefile`의 `verify-base` 레시피에서 두 하네스가 실패했을 때 정말 전체가 실패하는가(`set -euo pipefail`·`$(MAKE)` 체인·exit 전파). 편입 순서·환경변수(`PYTHONUTF8`) 차이로 인한 침묵 통과 가능성을 확인하라. 또한 `DJR_FINDINGS_JSON`이 **사용자 환경에 이미 설정돼 있는 경우** 하네스·검사기·verify가 오염되는지 실측하라.
6. **기존 하네스와의 모순**: 신설 하네스의 기대값이 기존 하네스(`fixture_matrix`·`findings_smoke`·`checker_cross_matrix`·`api_error_backstop_matrix`)의 기대값과 논리적으로 모순되는 지점이 있는가(같은 사실을 다르게 세는 곳). 예: cross_matrix의 `FIND_ID`는 `[ⓓ?#N]`을 잡지만 baseline의 `_FINDING_RE`는 `[#N]`만 잡는다 — 이런 정의 불일치가 어느 쪽 수치를 틀리게 만드는지 판정하라.
7. **문서화된 갱신 규율의 실효성**: 두 도구의 docstring이 «EXPECTED 갱신은 검사기별 사유와 함께·무사유 일괄 갱신 금지»를 규율로 적었는데, 이를 기계적으로 강제하는 장치가 있는가(없다면 그 사실을 결함으로 적어라 — `--emit-expected`가 사유 없이 값을 덮어쓸 수 있는 구조인지).

## 출력 형식

마크다운 표 1개 + 필요한 보충 문단. 각 발견 = 한 행:

| # | 심각도(blocker/major/minor) | 결함 | 근거(재현 명령·실측 출력·파일:행) | 수정 제안 |

- **재현 없는 주장 금지**. 특히 과제 2는 «어떤 변조가 안 잡히는가»를 실행으로 보여라.
- 결함이 없는 영역은 «반증 실패»로 한 줄만.
- 저장소 파일을 수정하지 마라(read-only). 임시 파일은 `/tmp` 아래에만.
