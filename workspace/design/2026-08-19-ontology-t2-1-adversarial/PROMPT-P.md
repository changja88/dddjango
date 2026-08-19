# 적대 검증 레인 P — 레코드 귀속 정확성 (T2-1 산출물)

너는 독립 적대 검증자다. 저장소 `/Users/hyun/Desktop/dddjango`(read-only)에서 **T2-1 개작 산출물의 구조화 레코드 귀속이 틀렸음을 실증하라**. 칭찬·요약은 쓰지 마라 — 결함만 쓴다.

## 배경(사실)

dddjango는 결정적 검사기 27종(`dddjango/scripts/check-*.py`, 로스터는 `dddjango/scripts/checker_registry.py`의 REGISTRY)을 운영한다. T2-1에서 27종 전부를 공용 모듈 `dddjango/scripts/findings.py`에 편입했다. 이 모듈은 stdout 라인 채널과 별도로, 환경변수 `DJR_FINDINGS_JSON=<경로>`가 있을 때만 JSON lines 레코드(스키마 `findings/0`)를 방출한다.

공용 모듈 4표면:
- `Findings.add(rule, where, msg, symbol=None)` → 라인 `[{rule}] {where}: {msg}` + violation 레코드
- `Candidates.add(rule, where, msg, question, symbol=None)` → 라인 `[ⓓ{rule}] …` + info 레코드
- `ContractFindings(contract_ref).add(line, where, msg, symbol=None)` → **라인은 호출자 소유 그대로**, 레코드는 `rule=null` + `contract_ref`
- `SliceFindings.add(rule, line, where, msg, symbol=None, severity="violation")` → **라인은 호출자 소유 그대로**, 레코드는 실규칙 `rule="#N"`

레코드 필드: `rule`(무접두 "#N" 또는 null) · `sentinel`("#N" 꼴 밖 표지) · `contract_ref` · `file`(=where) · `symbol` · `severity`(violation/warning/info) · `message`.

규칙 소유의 정본:
- `workspace/plan/2026-08-11-rule-owner-map.md` — 규칙 #N → ⓒ 검사기 / ⓓ 에이전트 매핑표(538규칙)
- `workspace/tools/reverse_coverage.py`의 `PRIOR_CONTRACT_SCRIPTS` — «ⓒ 규칙 0건»이 정당한 선행 계약 검사기 목록
- `workspace/design/2026-08-12-prior-contract-overlap-review.md` — 선행 계약 검사기와 인접 규칙의 겹침·면제 처분 기록
- `workspace/design/2026-08-08-tree-revision-spec.md` — 규칙 문면 정본
- `dddjango/commands/dddjango.md` — 검사기 registry 항목별 «표준 트리 슬라이스(#N…) + 계약» 분리 선언

## 검증 과제 (전부 실측으로)

1. **오귀속 적출**: 27종 각각에서 `SliceFindings.add(rule=…)`/`Findings.add(rule=…)`에 넘기는 #N이 **rule-owner-map에서 그 검사기 소유로 등재된 규칙인가**. 남의 규칙을 쓰거나, 라인 문면의 `[#N]` 리터럴과 `rule=` 인자가 어긋난 곳을 찾아라. 특히 `check-api-error-controller-contract.py`가 code-profile 레인의 2개 category(`custom Ninja exception_handler forbidden`·`custom Ninja add_exception_handler forbidden`)에 **rule="#59"**를 붙인 귀속이 정당한지 집중 검증하라(#59의 owner-map 행·규칙 문면·tree-slice가 #59를 방출하는지 여부).
2. **rule=null 처분의 정당성**: `ContractFindings`로 처분된 검사기·레인(app-container·choices-literal·idempotency-scope-creep·ninja-boundary-middleware·transient-overmapping·response-schema-bypass·common-container, 그리고 error-centralization/composition-root/api-error의 code 레인)이 정말 owner-map 규칙 0건인가. **반대로, 실제로는 owner-map에 소유 규칙이 있는데 rule=null로 처분해 규칙 조인을 잃은 곳**이 있는가.
3. **출력↔레코드 1:1 대응 파괴**: stdout에 인쇄되는 위반 라인 중 레코드가 나가지 않는 것(누락), 또는 인쇄되지 않는데 레코드만 나가는 것(유령)을 찾아라. 특히 필터(예: api-error의 `requires_static_error_shape` 필터)·dedupe(`seen`)·조기 return·예외 경로·`--anchor` 차분 모드에서 어긋나는 지점. 실행으로 확인할 때는 픽스처를 임시 디렉터리로 복사해 쓴다(`workspace/eval/fixtures/<lane>/{good,bad_rules}`; `check-layer-skeleton.py`는 `skeleton/{good_bc,bad_legacy_flat}`; `--error-profile auto`가 필요한 3종은 `checker_registry.REGISTRY`의 auto 플래그 참조).
4. **where/msg/symbol 분해 오류**: `where`가 실제 위치 문자열인가(경로 또는 `경로:행`), `msg`가 라인 문면의 사유 성분과 일치하는가, `symbol`이 엉뚱한 값(예: 사유 문장 전체)인가. 라인 문면과 레코드가 서로 다른 사실을 말하는 곳.
5. **severity 오배정**: ⓓ 후보(`[ⓓ#N]` 라인)는 info, 실위반은 violation이어야 한다. 뒤바뀐 곳·exit 산입 의미와 어긋나는 곳.
6. **센티널 격리**: `#N` 꼴 밖 값(예: "분석"·"합성"·"바인딩")을 rule로 넘긴 곳이 `rule=null + sentinel=<원문>`으로 격리되는가. 격리가 의도된 설계인지, 아니면 규칙을 붙였어야 하는데 놓친 것인지 판정하라.

## 출력 형식

마크다운 표 1개 + 필요한 보충 문단. 각 발견 = 한 행:

| # | 심각도(blocker/major/minor) | 결함 | 근거(파일:행 인용·실행 결과) | 수정 제안 |

- **근거 없는 추정 금지** — 파일:행 또는 재현 명령·실측 출력을 반드시 달아라.
- 결함이 없는 영역은 «반증 실패»로 한 줄만 적어라(장황한 확인 서술 금지).
- 저장소 파일을 수정하지 마라(read-only).
