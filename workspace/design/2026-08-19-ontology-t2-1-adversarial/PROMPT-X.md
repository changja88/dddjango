# 재검 레인 X — T2-1 보강 «적용 후» 반영 대조 (혼성 패널·codex)

너는 독립 적대 검증자다. 저장소 `/Users/hyun/Desktop/dddjango`(read-only)에서 T2-1 보강 코드 적용(커밋 `f164dd9..HEAD`)이 동결 설계대로 착지했는지 **반증** 자세로 검증하라. 칭찬·요약 금지 — 결함만.

## 정본 (설계 — 이 문서들이 기준이다)

1. `workspace/design/2026-08-19-ontology-t2-1-attribution-map.md` — 귀속 매핑표 v2(원자 술어 106 = #N 36·계약 64·타 소유자 억제 6·§5 overlap 표·부록 A 필드 명세·A-5 guard 21지점).
2. `workspace/design/2026-08-19-ontology-t2-1-formatter-contract.md` — 포매터 계약 v2(라인=레코드 필드의 순수 함수·emit_all 순서 불변식·의도 변경 열거표·V25 적용 순서·대체 불변식).
3. `workspace/design/2026-08-19-ontology-t2-1-adversarial/MEDIATION-2.md` — 중재 확정(U/V/W 전건).

## 검증 과제 (전부 실측·인용으로)

1. **귀속 착지 전수 대조**: 매핑표 §1(api-error 23)·§2(EC 65)·§3(composition 18)의 각 행 판정(#N/계약/억제)이 실물 검사기(`dddjango/scripts/`)의 방출 코드와 1:1인가. 특히 억제 6건(#117×4 — EC에서 방출 완전 부재 + 소유자 `check-context-isolation.py`의 `_check_canonical_module_containers` 실발화 / #81·#488×2 — composition DI 레인에서 V2/V3 검사 코드 부재 + `check-layer-skeleton.py` 실발화)을 코드·실행으로 재검하라.
2. **의도 변경 열거표 ↔ 기계 diff 대조**: `workspace/eval/ab/T2-construct-drift.md`(기계 생성)의 검사기별 diff 가 포매터 계약 v2 의 의도 변경 열거표 범위 안인가 — 열거표 밖 stdout 변경이 하나라도 있으면 blocker.
3. **EXPECTED 갱신 사슬 정합**: `workspace/tools/checker_baseline_matrix.py`·`findings_count_matrix.py`의 EXPECTED 갱신 행들이 각 이행 커밋 메시지의 사유와 일치하는가(무사유 갱신·사유-값 불일치 탐지). 가드 레인 16종(GUARD_LANES)·fingerprint 6열 병기가 선언·검증 로직과 정합한가.
4. **순서 불변식 실측**: 임의 표본 3종(후보 채널 1·code-profile 1·계약 레인 1)을 red 픽스처에 직접 실행(DJR_FINDINGS_JSON 임시 파일)해 stdout 위반·후보 라인 열과 레코드 열이 완전 동순서인지 실측하라.
5. **하네스 사각**: 68레인·mutation self-test 4종·drift 골든 8종·backstop 684로도 못 잡는 회귀 축이 남아 있는가(예: 조건부 인쇄 경로·UsageError 경로의 레코드·anchor 모드 조합).

## 출력 형식

| # | 심각도(blocker/major/minor) | 결함(파일:행 식별) | 근거(인용·실측 재현 절차) | 수정 제안 |

결함 없는 과제는 «반증 실패 — N건 대조» 한 줄. 저장소 수정 금지(read-only). 실행이 필요한 검증(과제 1 억제 실발화·과제 4)은 임시 디렉터리 사본에서 하라.
