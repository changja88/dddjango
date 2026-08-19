# T0 계획 적대 리뷰 중재 기록 (2026-08-19)

> 3렌즈(L1 표준 정합 · L2 잠금 비용 · L3 실물·동결 정합) 32건 — **blocker 1 · major 15 · minor 16**. 상세: L1-standards.md·L2-lockin.md·L3-reality.md.
> 처분 원칙(v3 관례 계승): 증거 기반 지적은 수용, 복수 수정안 중 선택 시 사유 기록. **기각 0건** — 각 렌즈의 자기 기각(L1 6건·L2 8건·L3 8건, 각 overall 수록) 외 성립 지적 중 기각할 것 없음. **L2-3과 L3-12는 동일 결함**(findings 스키마 v0의 «치환만» 과잉 주장)으로 병합.
> 반영: t0-plan.md **v1.1**(2026-08-19) — 아래 표의 반영 위치는 v1.1 절 번호.

| # | 클러스터 (지적) | 처분 | v1.1 반영 위치 |
|---|---|---|---|
| A | **B3 재료 규율** — 주입 재료 원천(ⓐ final.md 발췌)이 동결 E8 한정(«번호+검사기 산출 발췌»)·§6 B암 재료 구성과 정면 충돌 (**L3-1 blocker**) | 수용 — **수정안 (a)**: 주입 재료를 검사기 산출 발췌로 한정, §1의 «B3 원천» 규정을 «T1 이관·렌더의 원천, B3 비사용»으로 강등. 선택 사유: (b) E8 개정은 불요 — 검사기 위반 라인이 번호+사유 문면을 이미 담아(실측) 시제품 요건 충족. T2 B암 재료 정의(동결 하중 파라미터)의 오염 차단 | §1·B3 |
| B | **B트랙 실물 정합** — findings.py가 reverse_coverage에 걸려 자기 verify red(L3-2), 조인 데모 대표가 조인 불가 검사기(선행 계약 7종·map 규칙 0건 — L3-3), 동결 «재료 재사용+내용 단언 하네스» 몫 무이행(L3-4), 스키마 v0 «IRI 치환만» 불성립 — 판정 시점·실행 식별자·rule 값 공간(`"#N"` 문자열·센티널)·severity 값 공간·스키마 버전 결손 (L2-3=L3-12 병합) | 수용 — reverse_coverage 인프라 사유 등재+부수 확인 4점(corpus_lint 문자열·anchor docstring·checker_lint 문면·codex 복사), D3 분할(B2 대표 2종 유지 / B3 조인 데모는 check-domain-model 한정+7종 공백 명시·T2 이월), **내용 단언 스모크 신설**(자기 fixture red 재료 재사용 — 동결 문면의 이행 실물), 스키마 v0 6핀(schema 필드·run_id/ts·record_id·rule 값 공간(alias 경유·contract_ref)·severity SHACL 3값 대응·expression 예약) | B2·B3·§6 D3 |
| C | **RDFC-1.0·직렬화기** — 동치 성립 조건(canonical n-quads form) 미등재(L1-2), cons 셀 «축약 경로» 과소평가 — 공유 리스트면 전체 알고리즘 필요·«§4.4 축약 경로»는 무존재 명칭(L1-3), 기성 파이썬 구현 실존 미실사(L1-4), rdf-toolkit 선례·house 포맷 사양 고정 의무(L1-5), 직렬화 규칙 명세 수록처·버전·변경 절차·유니코드 NFC 침묵(L2-4), 재직렬화 전용 커밋 규칙 수록 누락(L3-8) | 수용 — A1에 rdfcanon 실사(공식 스위트 재실행 후 채택/자체 구현 결정+근거 기록), 게이트 ③에 canonical n-quads form 준수 명문+W3C 스위트 하위집합 스모크 편입+언어 태그 소문자 규약, §7 «축약 경로» 문구 삭제(자체 구현 시 전체 알고리즘 자인), 저작 규약 문서에 직렬화 규칙 명세(정렬·이스케이프·NFC·버전 상수)+재직렬화 전용 커밋 규칙+rdf-toolkit 비채택 근거 수록, «규칙 변경=전 코퍼스 재직렬화 커밋» 1행 | A1·A2·A5·§7 |
| D | **SHACL 의미론** — SHACL-SHACL은 문법 부분집합만 검증: 하우스 규율(closed 말단 한정) 차단 불능·«부정형 셰이프» 무정의(L1-1), sh:closed가 rdf:type 자동 무시 안 함 — valid 골든까지 red(L1-7), 게이트 ④·훅의 데이터 그래프 합성 미정의 — 파일 단위 검증은 거짓 green/red(L1-8) | 수용 — meta-SHACL **2층 명문화**(1층 표준 SHACL-SHACL+2층 하우스 메타셰이프 — closed 말단 한정은 SHACL-SPARQL(pySHACL 지원 확인)), «부정형 셰이프» 행은 정의 불능으로 **삭제**(선택 사유: 정의·근거 없는 항목의 존치보다 삭제가 정직 — 필요 시 T1에서 정의해 추가), closed 셰이프에 `sh:ignoredProperties (rdf:type)` 의무+누락 재현 골든, cons 셀 예외 명시 열거에 sh:ignoredProperties 포함, 게이트 ④=«변경 파일+vocab+wiring 병합» 정의(훅 포함 — E2와 동일 원리) | A5·A6·A8·A9 |
| E | **Turtle·어휘 표준 세부** — Expression IRI `@`는 PN_LOCAL 비허용(L1-6), vann 트리플 주어·형식·게이트 대조 규칙 미확정(L1-9), PROV-O 프로퍼티 미특정·prefLabel 유일성 미집행(L1-10) | 수용 — 직렬화기 규약 «PN_LOCAL 비허용 문자 포함 로컬네임은 전체 IRI 표기 고정»(선택 사유: PN_LOCAL_ESC 구현보다 오류 표면 작음)+A9 픽스처 1행, vann 형식 확정(주어=네임스페이스 IRI·리터럴 2종·@prefix 쌍 정확 일치 대조)+제3자 등재는 등록부 주석, A3에 prov:wasRevisionOf·specializationOf·Activity(+wasGeneratedBy) 명시·자체 신설 금지, A6에 prefLabel sh:uniqueLang(계획 추가 라벨) | A3·A4·A5·A6·A9 |
| F | **계약 실물·잠금** — djr: 기저 URI 값 선택이 재량 결정 표 밖(L2-1), 어휘 개정 비용 절벽·절차 부재(L2-2), verify 온톨로지/레거시 분해 불능 — §7 롤백 «한 줄 되돌림» 부재(L2-5), ISSUED 행 형식 미명세(L2-6), 게이트 리포트 무버전(L2-7), 훅 루트 전유 암묵·퇴행 조건 미명세(L2-8) | 수용 — **D5 신설**(djr: 기저 URI 값 — 사용자 결정 항목), 저작 규약 문서에 어휘 개정 절차(리네임 맵→일괄 변환→동형 확인→전용 커밋)+T1 게이트 어휘 안정화 선언 이월, `verify = verify-ontology + verify-base` 합성+중단 처분에 의존 삭제 1행, ISSUED 행 형식 확정(TAB 3필드)+정합 검사 T1 이월, `gate-report/1` 버전 필드+확장 규약+스모크 계약 일원화, 훅 단일 루트 안내+설치 경고+퇴행 조건(ttl 없음 즉시 exit 0·venv 부재 fail-closed) | A2·A3·A4·A5·A8·§6 D5·§7 |
| G | **장부 정확성·라벨** — §5 row 6 «계획 추가» 오표기(동결 §6 문면 전개 — L3-5), AUTHORING.md 위치가 §3 «정본 직렬화본만 존재»와 충돌(L3-6), 인터프리터 라우팅 미결(L3-9), byte-diff 인용 --exclude 누락(L3-10), 짝 저작 선언 vs 묶음 분할 모순(L3-11), A9 동결-외 행의 라벨 누락·§5 row 3 외연 부풀림(L3-13), 검수 패키지가 잠금 표면(계약 문면)을 미검수(L2-9) | 수용 — row 6 근거 정정, 저작 규약 문서를 `workspace/tools/ontology-authoring.md`로 이동(선택 사유: ontology/ 내 존치+사유 기록보다 §3 문면 그대로가 낫고 E7상 이동 비용 0), 라우팅 명문화(verify-ontology=.venv 파이썬 / verify-base=기존 python3), 인용 보완+«원문 그대로 이동» 명시, 묶음 재편(①에 A3 초안·②에서 A6과 동시 확정+A5→A6 순서), A9 표에 라벨 열+row 3 근거 정정, §5에 «계약 실물 문면 검토» row 7 신설(계획 추가) | A2·A8·A9·§1·§4·§5 |

## 반영 대조 (32건 전수)

- L1: 1→D · 2→C · 3→C · 4→C · 5→C · 6→E · 7→D · 8→D · 9→E · 10→E — 10/10 반영
- L2: 1→F · 2→F · 3→B(=L3-12 병합) · 4→C · 5→F · 6→F · 7→F · 8→F · 9→G — 9/9 반영
- L3: 1→A · 2→B · 3→B · 4→B · 5→G · 6→G · 7→(A9 표 2행 — shapes/ red·cons 셀 green 대조군, D·G에 걸침) · 8→C · 9→G · 10→G · 11→G · 12→B(병합) · 13→G — 13/13 반영

잔여 권고(지적 아님 — 렌즈 overall의 관찰): B1 스냅숏에 생성 커밋 해시+도구 기준 병기(L3 자기 기각 1 잔여 관찰) → B1에 반영. L1 «미검증 잔여» 4건은 A1·T0 실행 중 실측 항목으로 계획에 이관(rdflib 직렬화의 canonical form 일치 실측·rdfcanon 스위트 재현).
