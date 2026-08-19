# T0(기반) 세부 실행 계획 (v1.1 — 2026-08-19)

> **역할**: 동결 블루프린트 v3.2 §8 T0 행의 실행 전개. **동결 대상이 아니며** Claude가 관리한다. 규범·결정의 정본은 블루프린트(`2026-08-18-ontology-blueprint-v3.md`) — 이 문서는 재진술하지 않고 참조한다. 이 계획과 블루프린트가 충돌하면 블루프린트가 이긴다.
>
> **T0의 목적** (v3.2 §8): A트랙 — 그래프 저작·검증 스택의 스켈레톤을 CI green 상태로 세운다(실데이터 이관은 T1). B트랙 — 그래프 미경유 폐루프 부품(위반 어댑터·재생성 루프)을 착수한다(§6 B암 재료·독립 가치).
>
> **개정**: v1(2026-08-18 초안, D4는 사용자 결정으로 갱신) → **v1.1(2026-08-19)** — 3렌즈 적대 리뷰 32건(blocker 1·major 15·minor 16) 전건 반영. 중재 기록: `2026-08-18-ontology-t0-adversarial/MEDIATION.md`.

## 0. 범위 밖 (T0가 아닌 것)

- `rules/` 실데이터 이관·절 유형 센서스·렌더러·동기 검증기 → T1
- 검사기 27종 전수 개작·Findings 16벌 공용화 완성·SPARQL 질의 카탈로그·A/B → T2
- 이 계획이 새 규범을 만들지 않는다 — 동결 기준 외 추가 확인 항목은 «계획 추가» 라벨로 구분한다.

## 1. 실물 좌표 (2026-08-18~19 실측 — 계획의 전제)

| 실물 | 좌표 | T0와의 관계 |
|---|---|---|
| release 검증 세트 | `Makefile` release [2/7] — 12검사 + `diff -rq dddjango/scripts codex-dddjango/skills/dddjango/scripts --exclude=__pycache__` | make verify가 편승할 기존 세트. **33쌍 byte-diff는 이미 [2/7]에 존재** — verify로 옮겨 훅·수시 실행 가능하게 한다(**Makefile 원문 그대로 이동**) |
| git 훅 | `.git/hooks/` 설치 훅 없음(샘플만), `core.hooksPath` 미설정 | pre-commit 훅 신설 + 설치 메커니즘 필요 |
| 파이썬 | 시스템 python3 = 3.9.6, rdflib·pySHACL 미설치, 저장소에 파이썬 프로젝트 파일 없음, `.gitignore`에 `.venv/` 기존재 | 메인테이너 전용 환경 신설(D4 결정: 최신 안정판·E7 배포 경계) |
| 검사기 | `dddjango/scripts/` 33파일(검사기 27종+지원 6종), codex 쌍둥이 `codex-dddjango/skills/dddjango/scripts/`. 출력 규약 준수 16/27, 규약 밖 11종(L2-2 실측). **선행 계약 7종(check-common-container 포함)은 rule-owner-map 규칙 0건**(reverse_coverage PRIOR_CONTRACT_SCRIPTS) — B3 조인 공백(§3 B3) | B트랙 개작 대상 |
| rule-owner-map | `workspace/plan/2026-08-11-rule-owner-map.md` (생성: `spec_lint.py --emit-owner-map` — 재생성 byte-identical 실증) | B암 재료 — T0 스냅숏 고정 대상(§6) |
| fixture 레인 | `workspace/eval/fixtures/` + `workspace/tools/fixture_matrix.py`(명시 목록 등록 — 신규 디렉터리 무해), 스모크 관례 = `registry_gate_smoke.py` 패턴 | 게이트 픽스처 편입처·하네스 관례. `domain_model/bad_rules`·`common_container/bad_rules` red 재료 실재 |
| 규범 본문 정본 | `dddjango/skills/discipline-houserules/references/final.md`(ⓐ) 등 | T1 이관·렌더의 원천. **B3 주입 재료로는 쓰지 않는다**(동결 E8 — 무접두 #N 축 주입 재료는 «번호+검사기 산출 발췌» 한정) |

## 2. A트랙 — 그래프 스택 스켈레톤

### A1. 메인테이너 환경·도구 사슬 고정

- **산출물**: `workspace/tools/ontology-requirements.txt`(파이썬·rdflib·pySHACL 정확 버전 고정) · `make ontology-env`(`.venv` 생성 — 비커밋, 경로 고정) · 도구 스모크(임포트+버전 일치 — verify-ontology 선두, §7 «도구 사슬 고장 시 편집 불능 방지»)
- **파이썬 = 최신 안정판 신규 설치**(사용자 결정 2026-08-18 — 시스템 3.9.6은 사용하지 않음). 설치 경로·정확 버전을 실측 기록하고 requirements에 파이썬 버전 요구도 명시.
- **RDFC-1.0 구현 실사**: 기성 파이썬 구현 `rdfcanon`(W3C rdf-canon 구현 리포트 등재 — 공식 스위트 86/86, 단 성숙도 신호 약함)을 실사(공식 테스트 스위트 재실행으로 검증) → 채택 또는 자체 구현 결정 + 저작 규약 문서에 근거 기록. 판정 기준은 어느 쪽이든 공식 스위트 통과로 통일. rdflib 자체 직렬화 경로의 canonical n-quads form 일치 여부도 이 단계에서 실측(rdflib.compare는 RGDA1 — RDFC-1.0 비호환이므로 대안 아님).

### A2. `ontology/` 골격 + 저작 규약 문서

- **산출물**: 저장소 루트 `ontology/{vocab/djr.ttl, shapes/, shapes/golden/, rules/, wiring/, prefixes.ttl, ISSUED}` (§3 트리 그대로 — rules/는 T1까지 빈 디렉터리. **트리 안은 정본 직렬화본만 존재** — §3 문면).
- **저작 규약 문서** = `workspace/tools/ontology-authoring.md`(수기 — §3 문면상 ontology/ 밖 배치, E7상 메인테이너 층). 수록 목록:
  - E4 금지 목록 · 4단 게이트 사용법·수리 루프 절차 · ISSUED 채번 절차+행 형식(A4)
  - 오류 계열→차단 단 매핑 표(A9)
  - **정본 직렬화 규칙 명세**: 정렬 기준(접두·주어·술어·목적어)·개행/들여쓰기·이스케이프·**유니코드 NFC 고정**(macOS NFD 유입 방어)·**PN_LOCAL 비허용 문자 포함 로컬네임은 전체 IRI 표기 고정**(A5)·직렬화기 버전 상수
  - **재직렬화 전용 커밋 규칙**(E4): 직렬화기/규칙 변경은 논리 변경과 분리 커밋 + 같은 커밋에 전 코퍼스 재직렬화 동반
  - **어휘 개정 절차**: 리네임 맵 기록 → 스크립트 일괄 변환(수기 금지) → 전후 그래프가 리네임 맵 적용과 동형임을 확인 → 재직렬화 전용 커밋 관례로 커밋
  - 언어 태그 소문자 규약(RDFC-1.0 REC §1 Note 권고)
  - rdf-toolkit(FIBO 정렬 직렬화기) 선례와 비채택 근거(Java 의존 vs E7 파이썬 단일 사슬) · RDFC-1.0 구현 결정 근거(A1)
  - 훅 단일 루트 안내(core.hooksPath → workspace/hooks — A8)

### A3. djr 어휘 v1 (`vocab/djr.ttl`)

E5·E6에서 도출되는 선언 체크리스트 — 전부 SHACL 셰이프(A6)와 짝으로 저작:

- **클래스**: 문서·절·블록 / 규범 Work·Expression / 규범 유형 5종(의무·금지·허용·예외·우선 — 자체 프로파일, ODRL subClassOf 금지) / 검사기·에이전트·플랫폼 / 위반 개체 / `djr:SyncDebt`(§4-4 — v1 필수 포함) / alias 대장(유형 3종: 유일·문맥 한정·흡수 불가)
- **프로퍼티**: 블록 리터럴(규범 본문의 유일한 자리 — E5 리터럴 우선)·kind(prose|norm|table-row|checklist-item|code)·정수 순서(rdf:List 금지)·헤딩 스냅숏/현행 헤딩·§ 번호 / `djr:restates` / `djr:sectionOwner` / 배선(규칙↔검사기·경로 glob·플랫폼·위임 에이전트 — wiring 층) / `djr:alias` / **PROV-O 개정 연결은 표준 프로퍼티 명시 사용**: 개정 연쇄 `prov:wasRevisionOf` · Expression→Work `prov:specializationOf` · 개정 이벤트 `prov:Activity`(+`prov:wasGeneratedBy`) — 자체 신설 금지 / `rdfs:seeAlso`(ODRL 명명 참조 1종)
- **동봉 표 2종**(E5 명시 산출물): ODRL 봉인 목록 · 프로퍼티 역할 표(`skos:prefLabel`=명칭만, `skos:definition` 미사용)
- **개정·안정화**: 어휘 v1은 T1 파일럿에서 개정될 수 있다(개정은 일반 저작 게이트 + 어휘 개정 절차(A2) 경유). **T1 게이트에서 해상도 확정과 동시에 어휘 v1 재심·안정화 선언** — T1 계획 이월 항목(이후 개정은 절차 의무·비용 절벽 자인).

### A4. `prefixes.ttl` + `ISSUED`

- **prefixes.ttl**: vann 어노테이션 트리플로 전 접두(djr: 포함) URI 바인딩 등재. **형식 확정**: 주어 = 해당 어휘의 네임스페이스 IRI, `vann:preferredNamespacePrefix "접두"`(플레인 리터럴), `vann:preferredNamespaceUri "…IRI"`(리터럴 — @prefix 선언 문자열과 문자 단위 일치). **게이트 대조 규칙**: 각 정본 파일의 @prefix (접두, IRI) 쌍이 vann 등재 쌍과 정확 일치해야 통과 — 미등록 접두사 거부(게이트 ②). 제3자 어휘 등재는 자기 선언이 아니라 저장소 등록부임을 저작 규약 문서에 주석.
- **djr: 기저 URI 값 = D5(사용자 결정 — §6)**.
- **ISSUED**: Work IRI 채번 대장(append-only). **행 형식 확정**: TAB 구분 3필드 `R-NNNN<TAB>채번일(YYYY-MM-DD)<TAB>최초 등재 문서 경로` — 저작 규약 문서 수록. T0 시점 등재 0건(채번은 T1 이관부터). ISSUED↔rules/ Work 정합 검사(v2 registry_lint 동형)는 채번이 시작되는 **T1 산출물로 명시 이월**.

### A5. 정본 직렬화기 + 4단 저작 게이트

- **산출물**: `workspace/tools/ontology_gate.py` (+ 직렬화기 모듈)
- 게이트(E4): ① 파스(rdflib) → ② 정본 재직렬화 diff=0(자체 정렬 직렬화기 — 규칙 명세는 A2 수록. 이 단에서 미등록 접두사(vann 쌍 대조 — A4)·노드 IRI 의무(blank node)도 검사) → ③ RDFC-1.0 해시 전후 비교(트리플 집합 불변) → ④ SHACL(pySHACL `-i none`, 판정은 exit code가 아니라 리포트 그래프 SPARQL — severity별)
- **직렬화기 규약(발췌)**: PN_LOCAL 비허용 문자(`@` 등)를 포함하는 로컬네임(Expression IRI 등)은 접두명 축약 금지 — `<전체 IRI>` 표기 고정(PN_LOCAL_ESC 구현 대신 오류 표면 축소).
- **게이트 ③ 성립 조건 명문**: 해시 산출은 **canonical n-quads form**(RDFC-1.0 REC 부록 A — ECHAR 7종·UCHAR 대문자 HEX·`xsd:string` 생략·리터럴 무정규화·코드포인트 순 정렬) 준수가 요건. 정본 그래프는 blank node 부재라 결과가 정렬 canonical N-Quads와 일치하며, cons 셀(shapes/)은 A1의 구현 결정(기성 채택/전체 알고리즘) 경로를 따른다. W3C rdf-canon 공식 테스트 스위트의 관련 하위집합을 스모크에 편입해 준수를 기계 확인.
- **게이트 ④ 데이터 그래프 정의**: 검증 대상 = **변경 파일 + vocab/*.ttl + wiring/*.ttl 병합**(SHACL 대상 선정·sh:class가 데이터 그래프 안의 subClassOf 경로 기준 — E2와 동일 원리. 파일 단독 검증 금지 — 거짓 green/red 방지). 훅(A8)·하우스 메타셰이프(A6)도 동일 규칙.
- 실패 시 **구조화 되먹임 리포트**(JSON: 최상위 `schema: "gate-report/1"` + 단·파일·노드·사유) — LLM 수리 루프 1~2회의 재료(E4). 확장 규약: 필드 추가=호환 확장, 기존 필드 의미 변경=버전 증가. A9 스모크는 이 리포트의 «단» 필드를 단언(계약 일원화).
- `shapes/golden/`은 ①~③만 + ④는 기대 판정(red/green) 대조로 대체(E4).

### A6. 셰이프 + meta-SHACL 2층 + 골든 페어

- **산출물**: `shapes/*.ttl` — 어휘 v1 대응: 블록·규칙 필수 프로퍼티 완결성(kind·순서·라벨·규범 유형·PROV — §3, T0 산출물로 명시된 검사) · 배선 대상 유형 · `skos:prefLabel`에 `sh:uniqueLang true`(SKOS S14 — **계획 추가**) · alias 함수성은 모순 카탈로그 항목이므로 범위 밖(T2)
- **closed 규율**: sh:closed는 말단 클래스 타깃만(E3) + **`sh:ignoredProperties ( rdf:type )` 의무 동반**(SHACL REC §4.8.1 — rdf:type은 자동 예외가 아님. 추가 무시 프로퍼티는 셰이프별 명시). invalid 골든에 «선언 밖 술어»와 «ignoredProperties 누락 시 rdf:type 위반 재현» 케이스 포함.
- **cons 셀 예외의 명시 열거**(게이트 ② IRI 의무 검사용): sh:in·sh:or·sh:languageIn·**sh:ignoredProperties** 등 SHACL 리스트 인자의 RDF 컬렉션 cons 셀.
- 규율: SHACL 1.0 범위 · shapes/도 셰이프 노드 IRI 의무(cons 셀만 예외)
- **meta-SHACL 2층**(동결 «2단»의 실장 — 표준 1층만으로는 하우스 규율 차단 불능이 실증):
  - 1층 = 표준 SHACL-SHACL(문법 — REC 부록 C, 커버리지는 문법 부분집합임을 자인)
  - 2층 = **하우스 메타셰이프**: E3·E4 규율 집행 — sh:closed 말단 클래스 타깃 한정(클래스 계층 조회 필요 — SHACL-SPARQL 저작, pySHACL SPARQLConstraintComponent 지원 확인)·셰이프 노드 IRI 의무 등. 데이터 그래프에 vocab 병합(A5 ④와 동일 규칙).
  - meta-SHACL(2층 전체) green이 T0 완료 기준.
- **셰이프마다 valid/invalid 골든 페어**(`shapes/golden/`) + red/green 재현 하네스. valid 골든에 sh:in 보유 셰이프 포함(cons 셀 예외 실증 — A9 green 대조군 겸용).

### A7. 계층 병합 검사 + 적용 대상 계수 회귀 하네스 (E2)

- 검증 실행 전 vocab+rules+wiring 병합을 빌드 강제 + 셰이프별 적용 대상 계수를 기대표와 대조(병합 누락·타깃 오타의 침묵 미적용 방어).
- T0 시점 rules/가 비어 있으므로 **골든 픽스처 그래프로 하네스 기전만 증명**(계수 기대표 실가동은 T1부터).

### A8. `make verify` 신설 + pre-commit 훅 + release 편입

- **`make verify` = 하위 타깃 2개의 합성**: `verify: verify-ontology verify-base` (§7 롤백·중단 시 verify-ontology 의존 한 줄 삭제로 되돌림 — «한 줄 되돌림»을 훅과 verify 양쪽에 확보):
  - `verify-ontology`: [0] 도구 스모크(A1) → [1] 온톨로지 4단 게이트(전 ttl) → [2] meta-SHACL 2층 → [3] SHACL 본검증 → [4] 계층 병합·계수 하네스 → [5] 골든 페어 red/green → [6] 게이트 스모크(A9)
  - `verify-base`: [7] 기존 릴리즈 검증 세트 12종 → [8] 스크립트 33쌍 byte-diff(**Makefile [2/7] 원문 그대로 이동 — `--exclude=__pycache__` 포함**)
- **인터프리터 라우팅**: verify-ontology = `.venv` 파이썬 고정 경로 / verify-base = 기존 `python3`(기존 세트의 실측 기반 보존 — 두 인터프리터 공존을 Makefile에 명시).
- **release [2/7]은 `$(MAKE) verify` 호출로 치환** — 검증 세트의 단일 출처화(«기존 릴리즈 검증 세트 편입 범위 결정»의 결정: 전량 편입). → 재량 결정 D1
- **pre-commit 훅**: 변경된 `ontology/**/*.ttl` 한정 — 게이트 ①~③ + meta-SHACL 2층 + ④(변경 파일+vocab+wiring 병합 — A5). 수 초 목표, 전체 verify는 훅에 넣지 않는다. **퇴행 조건**: ttl 변경 없음 → venv 접촉 전 즉시 exit 0(비온톨로지 커밋 무마찰) · venv 부재+ttl 변경 → 명시 오류+설치 안내(fail-closed). 설치: `workspace/hooks/pre-commit` + `git config core.hooksPath workspace/hooks`(make 타깃 제공). 설치 타깃은 `.git/hooks`에 비샘플 훅 존재 시 경고(무증상 미실행 방지). 훅 단일 루트=workspace/hooks(저작 규약 문서 안내). → 재량 결정 D2
- 집행 3점 완성: 훅(경량) + make verify(전체) + 릴리즈(=verify 경유). 릴리즈 사이 잔여 창은 의도적 수용(§3).

### A9. 오류 계열→차단 단 매핑 표 + 픽스처 + 스모크 하네스

- **매핑 표**(저작 규약 문서 수록 — 초안, 구현 시 단 배정 확정. 라벨: 동결=T0 완료 기준 문면 / 계획 추가):

| 오류 계열 | 라벨 | 픽스처 | 예상 차단 단 |
|---|---|---|---|
| blank node(rules/·wiring/·vocab/ 노드) | 동결 | red 1 | ② IRI 의무 검사 |
| blank node(shapes/ 셰이프 노드) | 동결 | red 1 | ② |
| cons 셀 리스트 인자(sh:in 보유 valid 셰이프) | 동결 — 예외 실증 | **green 1** | 통과(과차단 방지 대조군 — A6 valid 골든 겸용) |
| 미등록 접두사 | 동결 | red 1 | ② vann 쌍 대조 |
| `#` 주석 | 동결 | red 1 | ② 재직렬화 diff≠0 |
| 해시 조작(재직렬화 전후 트리플 삽입/삭제) | 동결 | red 1 | ③ |
| 비정본 직렬화(순서·포맷 어긋남) | 계획 추가 | red 1 | ② |
| Expression IRI 접두명 축약 표기(`@` 미이스케이프) | 계획 추가 | red 1 | ① 또는 ②(전체 IRI 표기 규칙 — A5) |
| 셰이프 위반(완결성 누락 — kind·순서·유형·PROV 각 1) | 동결(골든 페어와 재료 공유 — §5 row 2 비고) | red 4 | ④ |
| sh:closed 상위 클래스 타깃 | 계획 추가 | red 1 | meta-SHACL 2층(하우스 메타셰이프) |

- **스모크 하네스** `workspace/tools/ontology_gate_smoke.py`(registry_gate_smoke 패턴 — 픽스처 사본→게이트 실행→gate-report «단» 필드·exit 단언). 픽스처는 `workspace/eval/fixtures/ontology_gate/`(snake_case — 레인 관례)에 편입 — **전부 신규 저작**(ttl 픽스처는 기존 레인에 재료가 없음. 동결 문면 «재료 재사용+내용 단언 하네스 신설»의 이행 실물은 B2의 내용 단언 스모크 — §3).

## 3. B트랙 — 그래프 미경유 폐루프 착수

### B1. rule-owner-map T0 스냅숏 동결 (§6 B암 재료 — 동결 문면 «T0 시점 스냅숏 고정»의 실행)

- `workspace/eval/ab/T0-rule-owner-map-snapshot.md`(사본 + SHA-256 + **생성 시점 커밋 해시·spec_lint.py 파일 해시 병기** — 재현 근거). 이후 원본이 변해도 B암 규칙 팩은 이 스냅숏에서만 구성(§9 배선 재지정과의 순서 고정의 전제).

### B2. 공용 구조화 출력 모듈 v0 + 대표 검사기 2종 적용

- **산출물**: `dddjango/scripts/findings.py` — 공용 Findings + 구조화 위반 레코드 방출. 무의존 표준 라이브러리 구현(E7 — scripts 동봉 가능 경계).
- **스키마 v0 확정**(동결 E6·E8 요구 수용):
  - `schema: "findings/0"`(스트림/레코드 버전 — v0→v1 판별)
  - `run_id`·`ts`(실행 식별·판정 시점 — E6 «판정 시점 Expression» 도출 재료)
  - `record_id`(run_id+서수 — E6 «위반 개체=어댑터가 채번»의 재료)
  - `rule`(**무접두 `"#N"` 문자열 그대로** — Work 조인은 alias 경유(E6), 정수 아님. `[#parse-fail]`류 센티널은 별도 필드로 격리. **선행 계약 검사기 7종은 rule=null + `contract_ref` 표기**)
  - `checker`·`file`·`symbol`
  - `severity`(**값 공간 선언**: SHACL 3값 대응 — blocker→`sh:Violation`·주의→`sh:Warning`·정보→`sh:Info`, 현행 exit 코드 의미론과의 매핑 명시)
  - `message` · `expression: null`(**예약** — T2 어댑터가 실값)
  - T2 작업 = IRI화 + expression 실값 채움(«치환만»이 아님을 자인 — 필드 형상은 지금 고정).
- **하위 호환**: 기존 `[{rule}] {where}: {msg}` 라인 출력 유지(registry_gate `_FINDING_RE`가 `[#N]` 라인만 파싱 — JSON lines 추가 채널은 비매치라 무해, 실측), 구조화 레코드는 추가 채널(JSON lines 옵션).
- **적용 2종**(모듈 일반성의 최소 증명 — 전수는 T2): 규약 준수군 1종 = `check-domain-model.py`(지역 Findings→공용 치환) + 규약 밖 11종 중 최소형 1종 = `check-common-container.py`(117행 — 개작). → 재량 결정 D3(분할 갱신)
- **기존 검증 세트 정합**(신설·개작 파일이 verify-base를 깨지 않게):
  - **reverse_coverage 등재**: findings.py를 인프라 고정 사유 목록에 추가(checker_target.py와 같은 «전 검사기 공용 모듈» 부류) — 미등재 시 «미설명 파일» exit 2.
  - 부수 확인 3점: codex 쌍둥이 복사([8] byte-diff) · corpus_lint AST 문자열 검사(≥20자 문자열에 workspace/ 경로·별칭 낱말 금지) · 재저작 2종의 checker_lint 문면 자리·anchor_integrity docstring § 앵커 보존.
- **내용 단언 스모크 신설**: 재저작 2종을 **자기 fixture 레인 red 재료 사본**(`domain_model/bad_rules`·`common_container/bad_rules` — 실재 확인)에 실행 → 구조화 레코드의 내용(rule·file·symbol)을 기대값과 대조(registry_gate_smoke 패턴, fixture_matrix의 exit 단언과 구분되는 내용 단언). **동결 T0 완료 기준 «재료 재사용+내용 단언 하네스 신설»의 이행 실물.**

### B3. 재생성 루프 시제품 (그래프 미경유)

- **산출물**: `workspace/tools/regen_loop_prototype.py` — 입력: B2 위반 레코드(JSON) → rule-owner-map 스냅숏 조인(rule→담당) → **«위반된 제약+핵심 맥락만» 주입 프롬프트 조립 — 재료는 검사기 산출 발췌 한정**(동결 E8: 무접두 #N 축 주입 재료는 «번호+검사기 산출 발췌», 본문 정본(final.md) 미동봉. 검사기 위반 라인이 번호+사유 문면을 이미 담음 — 실측) → 재생성 1왕복 → 재검사.
- **조인 데모는 check-domain-model 레코드 한정** — check-common-container 레코드는 rule-owner-map 조인 공백(선행 계약 7종 소속·map 규칙 0건 실측)이므로 데모 기록에 공백 사실을 명시. **T2 이월 이슈**: E8 «담당-규칙 docstring IRI 재저작 27종 전수»가 선행 계약 7종에서 가리킬 대상(무접두 공간 밖 규칙의 IRI 처분) 결정.
- **데모**: `workspace/eval/fixtures/`의 기존 위반 픽스처(B2 적용 검사기의 red 재료)에 루프 1왕복 적용 — before 위반 N건 → 주입 프롬프트 실물 → after 위반 감소를 기록으로 남긴다. 재생성 호출은 시제품 단계에선 headless `claude` 1회(또는 수동 1회) — 자동화 배선은 T2(coder 배선).
- 시제품의 기준은 «폐루프 1왕복이 기계 산출물로 재현된다»이지 성능 수치가 아니다(수치는 §6 A/B 전용 — §1 측정원 배정표).

## 4. 실행 순서·의존

```
A1 환경 ─→ A2 골격·저작 규약 ─→ A4 prefixes·ISSUED
                              └→ A3 어휘 초안
A5 직렬화기·게이트 ←─ A3 초안·A4 (어휘 골자·접두 확정 후 게이트 픽스처 저작 가능)
A6 셰이프·골든 ←─ A5 (골든은 게이트 ①~③ 적용 대상 — 직렬화기 완성 후 저작)
A3 확정 = A6과 동시 마감 (짝 저작 — 셰이프 저작 중 어휘 결함 발견 시 A3에 반영)
A7 계층 하네스 ←─ A6
A9 매핑 표·픽스처·스모크 ←─ A5·A6
A8 verify·훅·release 편입 ←─ A5~A9 (전 부품 조립)
B1·B2·B3 — A트랙과 독립 병행 (B3 ← B1·B2)
```

작업 묶음 4개로 진행: ① A1·A2·A4 + **A3 초안** → ② A5→A6(+A3 확정)→A7 → ③ A9→A8(픽스처·조립) → ④ B1~B3(병행 가능, 늦어도 ③과 동시). 묶음 ①의 완료 기준에서 A3는 초안 통과(확정은 ②). 각 묶음 완료 시 adoption-log에 세부 기록 append.

## 5. T0 게이트 — 사용자 검수 절차

검수 패키지로 제출할 것:

| # | 확인 항목 | 근거 | 제시 자료 |
|---|---|---|---|
| 1 | meta-SHACL(2층) green | 동결 완료 기준 | make verify 출력 |
| 2 | 골든 페어 red/green 재현 | 동결 완료 기준 | 하네스 출력(셰이프별 valid=green·invalid=red) |
| 3 | 매핑 표 전 항목 차단(+green 대조군 통과) | 동결 완료 기준(계획 추가 행은 표 라벨로 구분) | ontology_gate_smoke 결과 표(오류 계열별 차단 단 일치) |
| 4 | 픽스처의 fixture 레인 편입 + **내용 단언 스모크**(B2 — 재료 재사용 몫) | 동결 완료 기준 | verify 출력 + 픽스처 디렉터리 + 내용 단언 결과 |
| 5 | B트랙 1왕복 데모 기록 | **계획 추가** | before/주입 프롬프트(검사기 산출 발췌)/after 기록 + 조인 공백 명시 |
| 6 | rule-owner-map 스냅숏 동결 | 동결 문면 전개(§6·§8 T2 «T0 시점 스냅숏 고정») | 스냅숏 파일+해시 3종 |
| 7 | **계약 실물 문면 검토** — vocab/djr.ttl 명명 일람 · prefixes.ttl(djr: 기저 URI=D5) · ISSUED 행 형식 · ontology-authoring.md(직렬화 규칙·개정 절차) · 스키마 2종(findings/0·gate-report/1) | **계획 추가**(잠금 표면 — T1부터 변경 비용 폭증하는 것들의 사용자 검수) | 문면 묶음 |

통과 시: adoption-log 게이트 로그 행 추가 + 조감도 배너·T0 칩 갱신 → T1 세부 계획으로.

## 6. 계획 재량 결정 — **2026-08-19 사용자 전건 승인**(D1·D2·D3·D5 권고안대로, D4는 선행 별도 결정. 원문: «좋아 D5 권고안대로 전부 승인할게 착수해줘»)

| # | 결정 | 권고 | 대안 |
|---|---|---|---|
| D1 | release [2/7]을 `$(MAKE) verify` 호출로 치환(검증 세트 전량 편입) | **치환** — 검증 세트 단일 출처, 릴리즈·수시 실행 동일 보장 | verify를 별도 세트로 두고 [2/7] 병존(이중 유지 비용) |
| D2 | pre-commit = 변경 ttl 한정 경량 게이트(①~③+meta-SHACL 2층+④ 병합 검증), 퇴행 조건 = ttl 없음 즉시 exit 0·venv 부재 fail-closed, 설치 = `core.hooksPath workspace/hooks` | **권고안** — 훅은 수 초, 전체 검증은 verify·릴리즈가 담당 | 훅에서 전체 verify(느려서 우회 유발 위험) |
| D3 | B2(모듈 적용 증명) 대표 = check-domain-model + check-common-container **유지** / B3(조인 데모)는 check-domain-model 레코드 **한정**(common-container는 선행 계약 소속 — 조인 공백 명시) | **권고안** — 준수군·규약 밖 각 1로 모듈 일반성 증명은 유효, 조인 데모만 분리(규약 밖+map 보유 검사기는 전부 1,900행 이상이라 T0 부적합 — 실측) | 규약 밖 대표를 map 보유 대형 검사기로 교체(T0 규모 초과) |
| D4 | ~~파이썬 = 시스템 3.9.6 venv~~ → **결정됨(사용자 2026-08-18): 최신 안정판 신규 설치 + 버전 고정 파일** | — | — |
| **D5** | **djr: 기저 URI 값**(prefixes.ttl에 박히는 순간부터 전 트리플·위반 레코드에 실리는 시스템 최대 팬아웃 문자열 — T0가 마지막 싼 결정 시점) | **`https://numchida.com/ns/djr#`** — 사용자 도메인 귀속, **비역참조 불변 문자열 원칙**(역참조 서버 불요 — 식별자일 뿐. RDF 도구 생태계의 http(s) 관례 부합) | `urn:djr:`(URN — 도메인 무관 영속, 단 접두 관례상 http(s)형이 도구·문서화 친화적) |

## 7. 리스크·중단 처분

- **RDFC-1.0 구현**: 기성 파이썬 구현 `rdfcanon` 실사 우선(A1 — 공식 스위트 재실행 검증 후 채택/자체 구현 결정·근거 기록). 자체 구현 시 범위는 명세 §4.4~4.8 전체+부록 A 직렬화(shapes/ cons 셀의 공유 리스트가 N-Degree 해싱을 요구 — «축약 경로» 없음). 판정 기준은 공식 테스트 스위트 통과로 통일.
- **직렬화 규칙 변경** = 같은 커밋에 전 코퍼스 재직렬화(E4 «재직렬화 전용 커밋» 관례 — A2 수록).
- **환경 재현성**: requirements의 파이썬 버전 명시+도구 스모크(A1)가 방어. 훅·릴리즈의 venv 의존은 퇴행 조건(A8)으로 비온톨로지 작업 무마찰 보장.
- **T0 중단 시 처분**(§7 이월): ontology/ 골격·도구는 무해 존치 가능, 훅은 core.hooksPath 해제 한 줄, **verify는 verify-ontology 의존 한 줄 삭제**(verify-base가 기존 세트 그대로 잔존). B트랙 산출물(findings.py·루프)은 그래프 무관 유지 — 중단에도 독립 가치.
