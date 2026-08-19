# V — T0 계약 실물 5종 신선한 눈 감사 (2026-08-19)

## 방법

- **입장**: 작성 과정 맥락 없음 — 문서와 실물만 근거로 하는 대리 검수(T0 검수 7항). 읽기 전용 — 파일 수정 0(게이트 실행도 `--write` 없이 1회).
- **대조 정본**: 동결 블루프린트 v3.2(`workspace/design/2026-08-18-ontology-blueprint-v3.md` — E2·E3·E4·E5·E6·E7·E8, §1·§3) · T0 계획 v1.1(`workspace/design/2026-08-18-ontology-t0-plan.md` — §2 A2~A5, §3 B2, §6 D5).
- **확인 실물**: `ontology/vocab/djr.ttl` · `ontology/prefixes.ttl` · `ontology/ISSUED` · `ontology/shapes/djr-shapes.ttl` · `ontology/shapes/meta-house.ttl` · `ontology/shapes/golden/`(13파일 목록) · `workspace/tools/ontology-authoring.md` · `workspace/tools/ontology_gate.py` · `workspace/tools/ontology_canon.py` · `workspace/tools/ontology-requirements.txt` · `dddjango/scripts/findings.py` · `workspace/eval/fixtures/ontology_gate/cases/`(목록).
- **기계 확인**: `.venv/bin/python workspace/tools/ontology_gate.py`(무인자·읽기 전용) → **16파일 green 16 · red 0**. `git ls-files ontology/` → 공집합(트리 전체 커밋 전 상태).

## 판정 요약 (T0 검수 7항 중 항목 7 — 계약 실물 5종)

| # | 항목 | 판정 | 한 줄 |
|---|---|---|---|
| 1 | `ontology/vocab/djr.ttl` | **지적 있음** | E2(subClassOf만·domain/range·owl 0)·E5(seeAlso 3건만·prefLabel 명칭만·definition 0) 전부 준수, A3 체크리스트 전 항목 실재. 다만 계획 밖 RevisionKind 군 추가(m-5)·`djr:alias` 문면 명칭 부재(m-6) |
| 2 | `ontology/prefixes.ttl` | **통과** | 9접두 vann 등재, A4 형식(주어=NS IRI·프리픽스/URI 리터럴 문자 일치) 정확, djr:=`https://numchida.com/ns/djr#`(D5) 일치, vann 자기 등재 포함, 정본 정렬 |
| 3 | ISSUED 행 형식 | **통과** | 빈 대장(T0 등재 0건 — 계획 문면대로), 행 형식 정의(authoring §5)가 A4 문면(TAB 3필드 `R-NNNN·YYYY-MM-DD·경로`)과 자구 일치, append-only·결번 금지·T1 이월 명기 |
| 4 | `workspace/tools/ontology-authoring.md` | **지적 있음** | A2 수록 목록 대부분 이행(금지 목록·게이트·직렬화 규칙·재직렬화 커밋·어휘 개정 절차·ODRL 봉인 표·프로퍼티 역할 표·훅 루트·RDFC 결정 §8은 requirements 실물과 정합). 다만 §3 술어 정렬 명세가 구현과 불일치(M-1), 매핑 표 수록 약속 이탈(m-1), 제3자 등재 주석 누락(m-2), 미갱신 문구(m-3·m-4) |
| 5 | 스키마 2종 findings/0 · gate-report/1 | **지적 있음(경미)** | findings/0: B2 확정 13필드 전부 구현·docstring 선언 일치, severity 3값의 SHACL 대응 선언이 셰이프 `sh:in` 3값과 정확 대응, 하위 호환(라인 채널 불변·환경변수 옵트인) 준수 — m-7. gate-report/1: `schema` 최상위·단/파일/노드/사유·확장 규약 전부 이행 — m-8 |
| — | 교차: 어휘↔셰이프↔스키마 | **지적 있음** | 셰이프가 참조하는 djr 프로퍼티 30종·클래스 18종 전수 어휘에 선언됨(누락 0). severity 값 공간 3자 일치. 역방향 유령은 RevisionKind 군 1건(m-5). 단 셰이프 2건이 상위 설계와 충돌(B-1·M-2), 골든 페어 공백(M-3) |

**지적 수: blocker 1 · major 3 · minor 10.**

## 지적 상세

### B-1 (blocker) — 블록↔Work 연결이 3노드형으로 실장돼 동결 §3 «같은 노드 승격» 문면과 충돌

- **근거**: 블루프린트 §3(콘텐츠 블록 모델): «**규범 블록만 Work로 승격(같은 노드에 타입·유형·배선 추가** — 리터럴 복제 없음)» — 동결 문면이며 §10-3의 «의도적으로 연 결정» 4종(해상도·CNL·#N·문턱값)에 포함되지 않는다. 실물은 3노드형: `ontology/vocab/djr.ttl:207-208`(`djr:statesNorm` «진술 규범»), `ontology/shapes/djr-shapes.ttl:62-65`(BlockShape-statesNorm→`sh:class djr:Work`), 그리고 `djr-shapes.ttl:32-35`의 **BlockShape `sh:closed true`**(허용 술어 6종뿐)가 같은-노드 승격을 **구조적으로 불가능**하게 만든다(승격 노드의 prefLabel·enforcedBy 등이 closed 위반).
- **정황**: `ontology-authoring.md:99`(§12-1)가 이를 열린 결정으로 자인하며 «셰이프 저작에서 확정»이라 했고, 셰이프는 저작 완료됐다 — 즉 3노드형이 **개정 블록 없이** 사실상 확정됨. 블루프린트 §10-2는 «Stage 진행 중 발견이 설계와 충돌하면 작업 중단→개정 먼저»를 요구.
- **수정 방향**: 둘 중 하나를 사용자 재정으로 — ① 3노드형 채택 시 블루프린트 §3에 개정 블록(사유·diff) 기록 후 §12-1 폐기, ② 같은-노드 승격 유지 시 BlockShape의 closed 해제 또는 승격 프로퍼티 허용 목록 확장 + statesNorm 처분. T1 이관 계약의 근간이라 **T1 착수 전 해소 필수**.

### M-1 (major) — 직렬화 규칙 명세(authoring §3)와 직렬화기 구현의 술어 정렬 불일치

- **근거**: `ontology-authoring.md:25`(§3): «술어(**코드포인트 순**)». 구현은 rdf:type 우선: `ontology_canon.py:3`(docstring «술어(rdf:type 우선, 이후 IRI 순)»), `ontology_canon.py:194`(`pred_key = (0, "") if p == RDF.type else (1, …)`).
- **왜 지금은 안 드러나나**: 현 코퍼스의 술어(rdf 1999·rdfs 2000·skos 2004…)는 우연히 rdf:type이 코드포인트 순으로도 선두다. 그러나 E5가 계획한 **DCTERMS**(`http://purl.org/dc/terms/…`)는 코드포인트 순으로 rdf:type(`http://www.w3.org/1999/…`)보다 앞서므로(`p`<`w`), T1에서 dcterms 술어가 등장하는 순간 규약 문서를 믿은 저작이 게이트 ②에서 깨지거나, 문서가 거짓이 된다.
- **수정 방향**: 규약 문서 §3을 구현 실물(«rdf:type 우선, 이후 전체 IRI 코드포인트 순»)로 정정하는 쪽이 저렴(Turtle `a` 관례와도 부합). 문서만 고치면 재직렬화 불요.

### M-2 (major) — NormShape의 `enforcedBy` 의무(minCount 1)가 블루프린트의 «비커버 규범 실존»과 긴장

- **근거**: `djr-shapes.ttl:110-114`(NormShape-enforcedBy `sh:minCount 1`) + 골든 `shapes/golden/work-unwired-invalid.ttl`(담당 검사기 없는 규범=invalid) + 픽스처 `workspace/eval/fixtures/ontology_gate/cases/shacl-unwired-norm` — 의도된 설계로 3중 고착. 그러나 블루프린트 §1은 «기계 판정 비율(enforced 커버리지)»를 진도 지표로 두고(부분 커버 전제), E8은 비커버 축을 실측 명기(«tdd 스킬 완전 공백(스크립트 연결 0)·human 판정 2건(#254·#316)»).
- **귀결**: T1 이관 시 검사기 없는 규범 블록은 전부 게이트 ④ red — 가짜 배선을 유발하거나 이관을 막는다.
- **수정 방향**(사용자 재정 — 아래 «직접 판단» 2번): ① minCount 삭제(커버리지는 계수 리포트로), ② `djr:Checker`에 비기계 판정자(human·reviewer) 개체를 허용하는 규약 명문화 후 유지, ③ sh:severity를 Warning으로 강등. 어느 쪽이든 T1 전 결정 필요.

### M-3 (major) — «셰이프마다 valid/invalid 골든 페어»(E3 동결 문면) 공백 3종

- **근거**: 블루프린트 E3: «셰이프마다 valid/invalid 골든 페어 회귀». `shapes/golden/` 13파일은 Block(1v+3i)·Expression(1v+1i)·Work/Norm(1v+2i)·Violation(1v+1i)·PrefLabel(i만)을 덮으나, **AliasEntryShape·SectionShape·SyncDebtShape는 골든 0건**, PrefLabelShape는 valid 쪽 부재(간접 커버만). A6의 «ignoredProperties 누락 시 rdf:type 위반 재현» invalid 케이스도 골든에 안 보임(extraprop만 실재).
- **수정 방향**: 3셰이프 × valid/invalid 골든 추가(각 5~8행 규모). T0 검수항목 2(하네스 출력)가 «셰이프별» 제시를 요구하므로 게이트 통과 전 보강 권고.

### minor 10건

- **m-1** — A9 매핑 표의 «저작 규약 문서 수록» 약속(계획 `t0-plan.md:102` 및 A2 수록 목록) 대비, `ontology-authoring.md:46`(§6)은 «T0 계획 §2 A9의 표가 원본»으로 참조 갈음. 검수·스모크의 기준 표가 **비동결·가변 계획 문서**에 정본으로 남음. 표를 authoring §6에 실체로 옮기고 계획이 참조하는 방향 권고.
- **m-2** — A4 말미 «제3자 어휘 등재는 자기 선언이 아니라 저장소 등록부임을 저작 규약 문서에 주석» — authoring.md 전체에 해당 주석 부재.
- **m-3** — authoring 미갱신 문구: `:16`(§2 «ontology_gate.py **신설 예정**» — 실물 존재)·`:46`(§6 «③묶음 신설» 시제) — 완료 후 시제 정리 필요.
- **m-4** — authoring §12 열린 결정 3건 중 2건이 실물에서 이미 확정 방향으로 실장됨: severity 값=SHACL IRI(`djr-shapes.ttl:203` sh:in + findings/0 대응 표 — §12-3), 5종⊑Norm⊑Work 계층 유지(vocab 실물 — §12-2). §12가 갱신되지 않아 «열림»과 «실장 확정»이 병존.
- **m-5** — `djr:RevisionKind`+`djr:revisionKind`+개체 3종(`djr.ttl:60-61, 183-193`): A3 체크리스트에 없는 계획 밖 추가이며 셰이프·계획 어디서도 미사용(유일한 유령 군). E6 개정 3분류의 실장으로 선해 가능하나, 정작 E6 ①(지시 대상 변경)이 요구하는 **deprecated/replaced-by(OBO 관례) 프로퍼티는 부재** — 실장이 반쪽. 채택 여부·형상을 T1 어휘 재심에서 명시 처분 권고.
- **m-6** — E6·A3 문면의 `djr:alias` 프로퍼티가 실물에 없음 — `AliasEntry`(aliasFor/aliasText/aliasType) 재이피케이션으로 대체(`djr.ttl:9-13, 87-94`). 유형 3종 부착엔 재이피케이션이 합리적이나 동결 문면의 명명과 다름 — 형상 승인 필요(아래 4번).
- **m-7** — `findings.py:62-72` `_Run.run_id`가 항상 `argv[0]` 기반 `_default_checker()`를 쓰므로, `Findings(checker=…)` 명시 인자와 run_id가 어긋날 수 있음(docstring «검사기 이름+UTC+pid» 정의와 미세 불일치). 실사용(스크립트 직접 실행)에선 무해.
- **m-8** — `ontology_gate.py:184-189` 게이트 ④ 실패 시 «sh:Violation N건»만 보고(노드·사유 공백) — gate-report의 «노드» 필드가 ④에서 비어 LLM 수리 루프 재료로 약함. 부수: `:156-157` `ONTOLOGY_GATE_FAULT` 테스트 훅이 프로덕션 게이트 코드에 상주(A9 동결 문면은 «트리플 조작 **픽스처**» — 주입 훅+픽스처 조합 실장, 검수항목 3에서 확인될 사안).
- **m-9** — `ontology/` 트리 전체 미커밋(`git ls-files` 공집합 — 검수 전이라 자연스러움)이나, `rules/`·`wiring/`는 빈 디렉터리라 **커밋 시 git이 보존하지 못함**(.gitkeep류 부재) — A2 «골격» 문면이 fresh clone에서 깨짐. 게이트 `merged_data_graph`는 결측 디렉터리에 무해하므로 실해는 없음.
- **m-10** — `djr-shapes.ttl:173-175` SyncDebtShape-debtSection에 sh:class/nodeKind 제약 부재 — 다른 참조 프로퍼티(전부 sh:class+sh:nodeKind IRI) 대비 비대칭. 채무 대상 절이 임의 값이어도 통과.

## 사용자 직접 판단 필요 (기계·문서 대조로 닫히지 않는 것만)

1. **블록↔Work 형상**(B-1): 3노드형 승인+블루프린트 §3 개정 블록 vs 같은-노드 승격 복원+셰이프 재작업 — 동결 문면 재정 권한은 사용자에게만 있음.
2. **비커버 규범의 표현**(M-2): 모든 규범에 담당 검사기를 강제할 것인가(비기계 판정자를 Checker로 승인?), 커버리지 지표와의 관계 재정.
3. **D5 승인 기록 확인**: `ontology-authoring.md:42`는 «사용자 승인 2026-08-19»를 주장하나 계획 문서 D5 행(`t0-plan.md:191`)은 권고 상태 그대로다. `https://numchida.com/ns/djr#` 승인이 실제 있었는지 본인 확인 필요(감사자는 문서로 검증 불가).
4. **취향/재량 — 형상 승인 2건**: alias 재이피케이션 형상(m-6)·RevisionKind 군 존치 여부(m-5). 기능상 등가/무해라 취향 결정이며, T1 어휘 안정화 선언 전이 마지막 싼 시점.

## 총평

계약 실물 5종의 **문면 자체는 견실하다**: E2 저-공리(추론 유발 공리 0)·E5 봉인(ODRL seeAlso 3건만, definition 전무)·E6 채번 문면·E7 배포 경계(findings.py 무의존/게이트는 메인테이너 층)·A4 vann 형식·B2 13필드 스키마가 전부 문면 그대로 구현됐고, severity 값 공간은 findings/0↔셰이프↔역할 표 3자가 정확히 맞물린다. 게이트도 현 트리 16파일 green을 재현했다. 지적의 무게중심은 파일 안이 아니라 **실물 사이의 이음새**에 있다: 동결 문면과 셰이프가 다른 형상을 말하는 B-1, 규약 문서와 직렬화기가 다른 정렬을 말하는 M-1, 셰이프가 블루프린트 지표 전제와 다른 의무를 거는 M-2 — 셋 다 T1에서 비용이 폭증하기 전인 지금이 마지막 싼 수리 시점이다. B-1·M-2 재정과 M-1·M-3 수리 후 T0 게이트 통과를 권고한다.
