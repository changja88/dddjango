# T2-1 보강 8단계 혼성 패널 중재 (2026-08-20)

> 레인 X(codex — 반영 대조 5과제·`log-X.txt`) 5건 + 레인 Y(신선 Claude — 열린 스코프) 8건 = 13건.
> 중재: **채택 13·기각 0**(blocker 2축은 부모 독립 재현으로 확증). 수리 배치 R1~R7 전건 집행 후 재선언.
> 정합 확증(반증 실패): 귀속 106/106·drift 열거표 정합(단 Y#5 오봉인 2건 제외)·EXPECTED 사슬 무사유 갱신 0·
> 순서 불변식 3종 실측·#117/#81/#488 이관 쌍·UsageError 무이중방출·가드 exit 경로 21지점.

| 통합 # | 출처 | 심각도 | 결함 | 처분 |
|---|---|---|---|---|
| M1 | X#2·Y#1·Y#2·Y#3 | **blocker** | CR overlap 억제가 파일 단위 활성 기반 — code 미포섭 tree 실위반(#107 사설 함수·#108 임의 import·#440 spec 밖 registrar) 소거 = false negative. 부모 재현 확증(#108 requests import: tree exit 2 → code exit 0) | **R2**: 억제를 code 실발화 «사건 단위 키»(#108/#109=rel:lineno·#107=파일×category 대응·#440=fn 이름)로 재작성 — code 가 대응 사건을 실제 발화했을 때만 그 tree 엔트리 억제. «code 활성·미적중이면 tree 유지» 회귀 픽스처 rule 별 추가 |
| M2 | X#1 | **blocker** | EC 의 §5 억제 3행(#114·#572·#636 — anchor 모드 tree 억제) 미구현 — ② 이행 누락+부모 접합 대조 누락. codex 재현: #636 이중 방출 | **R3**: openapi `_suppress_overlapped_tree` 판형으로 구현(대상 집합 교집합·code 실발화 기준)+합성 anchor 억제 골든 |
| M3 | Y#4 | **major(회귀)** | 가드 발화∧수집 비공집합에서 defer 컬렉션 미방출 — 레코드 유실 3종(transaction-boundary·event-publish·usecase-dto). 11종 순서 이행(e8f4ce0)이 만든 회귀(구판 즉시 모드는 레코드 보존) | **R4**: 가드 return 전 수집분 레코드 방출(라인 무변 — 구판 동작 복원)+«가드∧수집» 조합 골든. 27종 전수에서 같은 모양 감사 |
| M4 | Y#5 | **major** | drift SEALED 오봉인 2건(CR=e245b1e·openapi=faea9d3 — 변경 커밋의 자손 = 자기 비교·«byte 무변» 허위 기록). 부모의 커밋 순서 착각 | **R1**: CR=faea9d3·openapi=ee62c5c 교정+`git merge-base --is-ancestor` 프로그램 검증+리포트 재생성·허위 기록 정정 |
| M5 | X#4·Y#6 | major | ordered 대조가 (severity,rule) 열만 — message/file/계약/guard 문면 drift 무검출(변이 실증: 전 하네스 green). docstring 예고 미이행·5c12f62 서술 과대 | **R5**: 레코드→라인 재구성(4종 판형 전부) ordered 대조 확장+mutation `stdout-message-drift` 등 추가+서술 정정 |
| M6 | X#5 | major | guard 21지점 중 5지점 골든 밖(code-profile 4종 미등재·context-isolation 도달 불능) | **R6**: 4종 selector 조합 guard-zero 레인 추가(GUARD_LANES argv 지원)·context-isolation 은 A-5 에 «도달 불능(사도) — 골든 제외» 확정 주기(가드 코드는 방어적 존치) |
| M7 | X#3 | major | 즉시 모드 잔존 5종(mechanism-ownership·db-table·layer-skeleton·synthetic-infra-exc·test-config) — «add=수집·emit_all=유일 방출» 불변식 미완 | **R7**: 5종 defer 이행(byte 무변) 후 findings.py 즉시 모드(_defer 분기) 제거 |
| M8 | Y#7 | minor | CR DI blocker 헤더가 이관 전 3종 모양을 광고(실동작=#497 단독) | R2 동승: 헤더 문면 개정+의도 변경 열거표 등재 |
| M9 | Y#8 | minor | context-isolation #117 신설 판별 FP 축(맨 이름 시드·임의 Attribute 매치) | R6 동승: import binding 존재 요구 보강 |
| M10 | Y사각4 | minor | #117 이관 쌍이 별개 fixture 기반 — pair-케이스 부재 | R6 동승: 같은 파일 셋으로 EC 침묵+context 발화를 함께 단언하는 backstop pair 케이스 |

수리 순서: R1(직접·즉시) → R2·R3·R4·R7 병렬 에이전트 → 접합 → R5·R6(직접·하네스 소유) → 전체 재검증(verify·68+α레인·backstop·mutation·drift 재생성) → 결과 append → **T2-1 완료 재선언**.
