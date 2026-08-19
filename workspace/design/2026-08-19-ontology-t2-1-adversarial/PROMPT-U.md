# 선행 설계 리뷰 레인 U — 귀속 매핑표 반증 (적용 전)

너는 독립 적대 검증자다. 저장소 `/Users/hyun/Desktop/dddjango`(read-only)에서 설계 문서 2건이 **적용되기 전에** 그 오류를 실증하라. 칭찬·요약 금지 — 결함만.

## 리뷰 대상 (아직 코드에 미적용 — 판단표 자체를 검증한다)

1. `workspace/design/2026-08-19-ontology-t2-1-attribution-map.md` — 검사기 code-profile category 91행의 «실규칙 #N vs 선행 계약(rule=null)» 전수 판정표(+부속 A 필드 정정·B 계수 영향).
2. `workspace/design/2026-08-19-ontology-t2-1-formatter-contract.md` — 공용 포매터 이행 표(rule 보유 발견의 라인을 Findings/Candidates 문법으로 이행·SliceFindings 제거·계약 레인 존치).

두 문서의 «저자 판단 요약»·«자인 약점» 절을 먼저 읽어라 — 저자가 가장 자신 없어 하는 판정이 거기 공개돼 있다.

## 검증 과제 (귀속 정확성 — 전부 실측·인용으로)

1. **#N 귀속 26행 전건 반증**: 각 행의 근거 인용(규칙 문면 `workspace/design/2026-08-08-tree-revision-spec.md`·소유 `workspace/plan/2026-08-11-rule-owner-map.md`)이 실제 그 행에 있는지, 인용이 판정을 실제로 지지하는지 대조하라. 특히 저자 자인 약점: ① `caught exception forwarding forbidden`→#474 신규 귀속 ② error-central #572 확장 4행(08-15 승인 예외 문면 근거) ③ composition 11행(#107/#108/#109/#111/#440/#497) ④ blocker 조건부 #114.
2. **계약 유지 65행의 «대응 술어 부재» 반증**: 표본이 아니라 **전수** — 각 행의 category 술어가 정말 어느 소유 규칙 문면에도 없는지. 하나라도 실소유 규칙에 포함되면 그 행은 조인 상실 재발이다(T2-1 리뷰가 잡았던 바로 그 유형). 인접 검사기 소유 규칙과 겹치는 경우(#117 사례처럼) «오귀속 회피» 판정이 맞는지도.
3. **불확실 15행 재판정**: 각 행에 대해 근거를 찾아 {#N 귀속 | 계약 유지}로 확정하거나 «판정 불능 사유»를 명시하라.
4. **이중 방출 방어**: composition의 «tree-slice와 code 레인이 같은 실행에서 같은 사건을 두 번 #N으로 낼 수 있다»는 저자 발굴과 그 dedupe 조건이 충분한가 — 다른 검사기(api-error·error-central·openapi)에 같은 축이 정말 없는지 tree 선점 구조(조기 return)를 코드로 재검하라.
5. **부속 A 검증**: 4종 dataclass «심볼 재료 없음→null» 실측이 맞는가(AST에 실제 이름 재료가 있는데 놓친 곳). 행번호 오배치 11곳 목록이 전수인가. #74 가드 21지점 목록이 전수인가(REGISTRY 27종 grep 대조).

## 출력 형식

| # | 심각도(blocker/major/minor) | 결함(행 식별 포함) | 근거(파일:행 인용·실측) | 수정 제안(판정 교체면 무엇으로) |

결함 없는 과제는 «반증 실패 — N행 대조» 한 줄. 저장소 수정 금지(read-only).
