# L3 실물·동결 정합 렌즈 — T0 세부 실행 계획 적대 리뷰 (2026-08-19)

> 대상: `workspace/design/2026-08-18-ontology-t0-plan.md` (비동결 — T0 세부 실행 계획)
> 상위 정본: `workspace/design/2026-08-18-ontology-blueprint-v3.md` (v3.2 동결 — 특히 §8 T0·E2~E8·§3·§6·§7)
> 방법: 계획 §1 실물 좌표 표 전 행을 저장소에서 직접 재확인(Read/Grep/Bash 실행 포함 — 재생성 실증 1건, 임시 트리) + 동결본 §8 T0 행·완료 기준·E2~E8·§3·§6·§7을 계획 A1~A9·B1~B3·§4·§5에 항목별 대조. 이미 처분된 v3 리뷰 지적(MEDIATION.md)은 재제기하지 않고, 처분 결과 문면을 계획에 «집행»하는 방향으로만 사용.
> 직접 확인한 실물: `Makefile`(release 전문) · `.git/hooks/` · `git config core.hooksPath` · `.gitignore` · `dddjango/scripts/` 33파일 목록·`check-common-container.py`(전문)·`check-domain-model.py`(Findings·출력부)·`check-naming.py`·`check-composition-root.py`(표본)·`registry_gate.py`(파싱부) · codex 쌍둥이 byte-diff 실행 · `workspace/tools/fixture_matrix.py`(등록부 전문)·`reverse_coverage.py`(분류부 전문)·`spec_lint.py`(emit부) · `workspace/plan/2026-08-11-rule-owner-map.md` + **재생성 diff 실증** · `workspace/eval/fixtures/`(레인 목록·domain_model·common_container 내부) · 파이썬 프로젝트 파일 전 깊이 탐색 · ISSUED 실물 탐색 · 참고 3종(MEDIATION.md·A2-tools.md·L2-repo-reality.md).

---

## 지적 요약 표

| ID | 심각도 | 한 줄 |
|---|---|---|
| L3-1 | **blocker** | B3의 주입 재료 원천(ⓐ final.md 규칙 문장 발췌)이 동결 E8의 무접두 #N 축 한정(«번호+검사기 산출 발췌»)·§6 B암 재료 구성(rule-owner-map+검사기 출력)과 정면 충돌 |
| L3-2 | major | B2 신설 `dddjango/scripts/findings.py`가 reverse_coverage «미설명 파일 0» 검사에 걸려 verify [7]/release가 red — 등재 작업이 계획에 없다 |
| L3-3 | major | D3의 규약-밖 대표 check-common-container는 rule-owner-map에 규칙 0건(선행 계약 7종 소속) — B2 스키마의 rule_no가 비고 B3의 map 조인이 이 검사기 레코드에서 성립 불가 |
| L3-4 | major | 동결 T0 완료 기준 «재료 재사용+내용 단언 하네스 신설»의 유래 몫(위반 어댑터 골든이 기존 fixture 재료 재사용)이 계획에서 소실 — A9 픽스처는 전부 신규 저작, B2에 내용 단언 하네스 없음 |
| L3-5 | minor | §5 row 6(rule-owner-map 스냅숏)을 «계획 추가»로 오표기 — §6 동결 문면 «T0 시점 스냅숏 고정»의 전개다 |
| L3-6 | minor | AUTHORING.md를 `ontology/` 안에 두면서 «§3 트리 그대로» 주장 — §3 문면 «그래프 정본(Turtle, 정본 직렬화본만 존재)»과 충돌 |
| L3-7 | minor | A9 blank node 픽스처가 rules/·wiring/·vocab/ 프롱만 — E4의 shapes/ 셰이프 노드 IRI 의무 red와 cons 셀 예외 green 대조군이 없다 |
| L3-8 | minor | E4 «논리 변경 없는 재직렬화 전용 커밋» 규칙이 AUTHORING.md 수록 목록에 없다 |
| L3-9 | minor | 인터프리터 라우팅 미결 — verify [7]·[8]과 훅의 실행 파이썬(시스템 3.9.6 vs 새 venv) 미지정, 훅의 venv 부재 시 행동 미정 |
| L3-10 | minor | §1의 [2/7] byte-diff 인용에 `--exclude=__pycache__` 누락 — [8] 이동 시 원문대로 옮기지 않으면 가짜 red |
| L3-11 | minor | §4 «A3 ⇄ A6 짝 저작» 선언과 묶음 분할(①=A1~A4 / ②=A5~A7)의 내적 모순 |
| L3-12 | minor | B2 «E8 그래프 스키마와 필드 정합 — T2에서 IRI 치환만» 과잉 주장 — Expression 병기(E6)·위반 개체 채번(실행 ID+서수) 필드가 v0에 없다 |
| L3-13 | minor | A9 매핑 표의 동결-외 행(비정본 직렬화·셰이프 위반·meta-SHACL red)이 «계획 추가» 라벨 없이 §5 row 3 «동결 완료 기준» 근거에 편승 — §0 자기 규율 위반 |

집계: blocker 1 · major 3 · minor 9 (총 13)

---

## L3-1 (blocker) — B3 주입 재료 원천이 동결 E8 한정을 벗어난다

**주장.** 계획 B3의 프롬프트 조립 절차 — «ⓐ 정본(final.md)에서 해당 규칙 문장 발췌 → «위반된 제약+핵심 맥락만» 주입»(계획 108행) — 는 동결본이 무접두 #N 축에 명시한 한정과 충돌한다. 계획 §1 실물 좌표 마지막 행(23행)이 final.md를 «B3 루프 시제품의 «위반 제약 발췌» 원천»으로 규정한 것 자체가 같은 충돌이다.

**근거.**
- 동결 E8(블루프린트 42행): «**무접두 #N 축의 주입 재료는 «번호+검사기 산출 발췌»로 한정**(본문 정본 미동봉 — E6)». 이 문면은 중재 F(L2-1 blocker 처분)의 산물로, 처분 원장(MEDIATION.md 15행)에도 «재생성 주입 재료는 «번호+검사기 산출 발췌»로 한정»으로 등재돼 있다.
- 동결 §6(94행): B암 = «그래프 미경유 — **rule-owner-map+검사기 출력으로 구성한 규칙 팩**+위반 재생성». final.md는 구성 재료 목록에 없다. §6 하중 파라미터는 동결 문면이다(§10-2).
- B3가 다루는 규칙 공간은 무접두 #N이다: B2 스키마의 rule_no는 rule-owner-map의 # 열(무접두 538 공간)이고, 데모 대상 검사기의 위반도 이 공간이다(`check-domain-model.py` 185·190·194행 — `f.add("#249", …)` 등).
- 계획 자신이 «이 계획과 블루프린트가 충돌하면 블루프린트가 이긴다»(3행)고 선언한다.

**성립 조건 검토(재제기 아님).** E8의 한정은 v3 리뷰에서 이미 심의·처분·동결된 결정이다. 이 지적은 그 처분을 뒤집자는 것이 아니라, 계획이 처분된 문면을 그대로 어기고 있음을 지적한다. «final.md는 모노레포 본문 정본(tree-revision-spec)이 아니라 배포측 발췌이니 허용»이라는 관대한 독해를 시도해 봤으나 기각했다 — ① E8 문면은 재료를 «번호+검사기 산출 발췌»로 «한정»한다(원천 예외 없음). ② §6 B암 구성 재료 목록에도 final.md가 없다. ③ B3 시제품의 재료 관례는 T2 3암 실런의 B암 재료 구성으로 직결되므로(§8 T2 «B암 재료는 T0 스냅숏 고정»), 여기서의 일탈은 A/B 판정 설계(동결 하중 파라미터)를 오염시킨다.

**수정 방향.** 둘 중 하나: (a) B3의 «위반된 제약» 문면 원천을 **검사기 산출 발췌**로 한정 — 실물상 충분하다: check-domain-model의 위반 라인은 규칙 번호+사유 문면을 담고, check-common-container도 근거 문단을 출력한다(`check-common-container.py` 101~111행). §1 마지막 행의 «B3 원천» 규정은 삭제하거나 «T1 이후 그래프 발췌의 원천» 참고로 강등. (b) ⓐ 발췌를 정말 원하면 §10 개정 블록(E8 개정)을 먼저 통과시킨다 — 계획 재량으로 할 수 있는 일이 아니다.

## L3-2 (major) — findings.py 신설이 계획 자신의 verify를 red로 만든다

**주장.** B2가 신설하는 `dddjango/scripts/findings.py`(계획 101행)는 릴리즈 검증 세트의 reverse_coverage에 «미설명 파일»로 걸린다. verify [7]이 기존 12종을 전량 편입하므로(A8·D1), 계획을 문면대로 실행하면 T0 완료 기준인 «CI green 스켈레톤»이 자기 산출물에 의해 깨진다. 등재 작업이 계획 어디에도 없다.

**근거.** `workspace/tools/reverse_coverage.py` 103~128행: 플러그인 전 파일을 rglob으로 분류하며, `scripts/` 밑 파일은 ⑴ 인프라 6종 고정 사유(standard_tree·business_vocab·checker_target·checker_registry·registry_gate·anchor_diff — 108~120행 이름 하드코딩) ⑵ 매핑표 ⓒ 규칙 보유 ⑶ `PRIOR_CONTRACT_SCRIPTS` 7종(49~57행) 어디에도 없으면 «미설명: … 매핑표 ⓒ 에 규칙 0건»(128행) → exit 2. findings.py는 셋 다 아니다. 이 검사는 release [2/7]의 7번째 항목(`Makefile` 100행)이고 계획 A8이 verify [7]로 옮긴다.

**부수 확인(같은 신설 파일의 다른 표면).** ① codex 쌍둥이: byte-diff는 «Only in» 도 잡으므로 findings.py를 codex 쪽에도 복사해야 [8]이 green — 계획 B2가 «동기 유지»를 이미 명시(104행) ✓. ② `corpus_lint.py`는 `dddjango/scripts/*.py`의 AST 문자열 상수(≥20자)를 스캔한다 — findings.py 문자열에 workspace/ 경로·별칭 낱말을 넣으면 안 된다. ③ `anchor_integrity_check.py`의 인용자 표면에도 `dddjango/scripts/*.py`가 포함된다 — docstring의 § 앵커는 해소 가능해야 한다. ④ 재저작되는 check-domain-model·check-common-container는 `checker_lint.py`의 문면 자리 검사(#74 가드 등 — check-domain-model 830행의 #74 배너가 실물)를 계속 통과해야 한다.

**수정 방향.** B2 산출물에 «reverse_coverage 설명 등재» 한 항목 추가(인프라 고정 사유 목록에 findings.py 추가 — checker_target.py와 같은 «전 검사기 공용 모듈» 부류가 실물 관례). 위 부수 4점을 B2 완료 확인 목록에 명시.

## L3-3 (major) — 조인 데모의 대표로 «조인 불가능한 검사기»를 골랐다

**주장.** D3가 규약-밖 대표로 고른 check-common-container는 rule-owner-map에 소유 규칙이 0건이다. B2 스키마 v0의 rule_no 필드를 채울 값이 없고, B3의 핵심 단계인 «rule-owner-map 스냅숏 조인(rule_no→담당)»(계획 108행)이 이 검사기의 레코드에서 성립하지 않는다. 폐루프 1왕복 데모의 절반이 조인 공백 위에서 돈다.

**근거.**
- `grep "common-container" workspace/plan/2026-08-11-rule-owner-map.md` → 0건(실측). `reverse_coverage.py` 49~57행이 이유를 명문화: check-common-container는 `PRIOR_CONTRACT_SCRIPTS` — «선행 규약(D38 승격/강등…) 소유·트리 규칙 몫은 business-vocabulary 가 진다». 즉 538 무접두 공간 «밖» 선행 계약 소유 검사기 7종의 하나다.
- 실물 출력에도 무접두 규칙 번호가 없다: `check-common-container.py` 98·101행 — `[컨테이너]` 라인과 «트리 112행»·D38 인용뿐. docstring의 #49는 «검출 리터럴» 언급이고, #49의 매핑표 소유자는 check-context-isolation.py다(rule-owner-map 52행) — 재저작 시 [#49]를 방출하면 소유 충돌까지 생긴다.
- 대안 후보의 실물 규모(규약-밖 11종 중 매핑표 규칙 보유 4종): check-composition-root 1,941행 · check-openapi-error-declaration 3,426행 · check-error-centralization 4,692행 · check-api-error-controller-contract 6,891행 — **«작은 규약-밖+map 보유» 검사기는 존재하지 않는다**(실측). D3의 «117행 최소형» 선택 자체는 B2(모듈 일반성)에는 합리적이다 — 문제는 그 선택이 B3(조인 데모)와 묶여 있는데 계획이 이 공백을 못 봤다는 것.

**수정 방향.** D3를 쪼갠다: B2(모듈 적용 증명)의 대표는 현행 2종 유지 가능하되, B3의 map-조인 데모는 check-domain-model 레코드로 한정함을 명시하고, 선행 계약 검사기 7종의 레코드가 rule-owner-map 조인 공백이라는 사실을 B2 스키마(rule_no 부재 허용 + 계약 참조 표기)와 T2 이슈(E8 «담당-규칙 docstring IRI 재저작 27종 전수»가 이 7종에서 무엇을 가리킬지)로 명시 이월한다.

## L3-4 (major) — 동결 완료 기준 «재료 재사용» 몫이 계획에서 증발했다

**주장.** 동결 T0 완료 기준 네 번째 항목 «픽스처의 fixture 레인 편입(**재료 재사용**+내용 단언 하네스 신설)»(블루프린트 117행)에서 «재료 재사용»의 유래는 위반 어댑터 골든이 기존 fixture 레인의 red 재료를 재사용한다는 처분(L2-13 → 중재 G: «어댑터 골든은 fixture 레인의 fixture 재료를 재사용하되 내용 단언 하네스는 신설», §9 처분표 144행: «fixture_matrix | 존치·확장 — **T0** 픽스처 재료 편입+내용 단언 하네스는 신설»)이다. 계획 A9는 이 문면을 ontology-gate ttl 픽스처에 갖다 붙였는데(91행 «재료 재사용+내용 단언 하네스 신설 — T0 완료 기준 문면»), A9 픽스처는 전부 **신규 저작**이라 재사용할 기존 재료가 없고(기존 레인은 Django 프로젝트 트리다), B2에는 구조화 레코드의 내용을 단언하는 하네스가 아예 없다. 동결 문면의 절반이 어느 항목에서도 이행되지 않는다.

**근거.** 위 인용 3곳 + 계획 B2(99~104행 — 산출물에 하네스 없음) + `workspace/eval/fixtures/domain_model/bad_rules/`·`common_container/bad_rules/` 실재 확인(재사용 가능한 red 재료가 정확히 있다). B3의 데모(109행)가 이 red 재료를 쓰지만, 데모 «기록»은 하네스가 아니고 §5에서도 «계획 추가»로 분류돼 동결 기준 이행으로 계상되지 않는다.

**수정 방향.** B2에 한 항목 추가: 재저작 2종을 자기 fixture 레인 red 재료(사본)에 실행해 구조화 레코드의 내용(rule_no·file·[symbol])을 기대값과 대조하는 스모크(fixture_matrix가 exit만 보는 것과 구분되는 «내용 단언» — registry_gate_smoke 패턴 재사용 가능). 이것이 동결 문면의 «재료 재사용+내용 단언 하네스 신설»을 문자 그대로 닫는다. A9의 ontology-gate 픽스처 편입은 그대로 두되 «재료 재사용» 인용은 제거(신규 저작임을 정직하게). 부수: 레인 이름 `ontology-gate`는 기존 관례(snake_case — common_container 등)와 어긋난다 — `ontology_gate` 권고.

## L3-5 (minor) — §5 row 6의 «계획 추가» 라벨은 오표기다

**주장.** §5 검수 표 row 6(rule-owner-map 스냅숏 동결)의 근거를 «계획 추가(§6 전제의 조기 고정)»로 적었는데, 동결본 §6(97행)은 «B암 규칙 팩은 **T0 시점** rule-owner-map 스냅숏으로 고정»이라 명시하고 §8 T2(119행)도 «B암 재료는 T0 스냅숏 고정»을 반복한다. §6 하중 파라미터는 동결 문면이다(§10-2). T0 시점 스냅숏 실행은 계획의 재량 추가가 아니라 동결 기준의 전개다.

**수정 방향.** row 6 근거를 «동결 문면 전개(§6·§8 T2)»로 정정. 라벨 방향이 보수적(추가 검수)이라 실행 위험은 없지만, «동결이 요구한 것»과 «계획이 더한 것»의 경계 장부가 §0의 존재 이유이므로 정확해야 한다.

## L3-6 (minor) — AUTHORING.md의 자리가 §3 문면과 충돌한다

**주장.** A2는 «§3 트리 그대로»라면서 `ontology/AUTHORING.md`(수기 markdown)를 트리 안에 신설한다(계획 34~35행). 동결 §3(47행)의 디렉터리 주석은 «ontology/ ← 그래프 정본 (Turtle, **정본 직렬화본만 존재**)»이고, 트리 항목에 AUTHORING.md는 없다. 수기 산문 문서가 «정본 직렬화본만 존재»하는 디렉터리에 들어가면 문면 위반이자, «그래프 밖 수기 문서»(E1의 서사 산문 부류)의 배치 선례가 된다.

**수정 방향.** AUTHORING.md를 `workspace/`(메인테이너 문서 층 — 예: workspace/design 또는 workspace/tools 인접)로 옮기거나, ontology/ 안에 두는 일탈을 «계획 추가» 라벨+사유(게이트가 *.ttl만 보므로 무해)로 명시 기록. 전자를 권고 — E7 배포 경계상 ontology/는 어차피 메인테이너 전용이라 수록처 이동의 비용이 없다.

## L3-7 (minor) — blank node 픽스처의 shapes/ 프롱과 green 대조군 부재

**주장.** A9 매핑 표의 blank node 행은 «rules/·wiring/·vocab/ 노드»만 다룬다(계획 83행). 동결 E4(38행)의 blank node 금지는 두 갈래다: ① rules/·wiring/·vocab/ 전 노드 IRI 의무 ② shapes/의 노드·프로퍼티 셰이프 IRI 의무 + SHACL 리스트 인자 cons 셀만 예외. ②의 red 픽스처(셰이프를 blank node로 저작)와, cons 셀 예외가 차단되지 **않음**을 증명하는 green 대조군(sh:in 리스트 보유 valid 셰이프)이 표에 없다 — 후자가 없으면 게이트 과차단(예외 미구현)을 T0 검수가 못 잡는다.

**수정 방향.** A9 표에 2행 추가: «shapes/ 셰이프 노드 blank | red 1 | ②»와 «cons 셀 리스트 인자 | green 1 | 통과(예외 실증)». A6 골든 페어의 valid 쪽에 sh:in 보유 셰이프를 포함시키는 것으로 green 대조군을 겸할 수 있다 — 그렇다면 그 사실을 표 비고로 연결.

## L3-8 (minor) — «재직렬화 전용 커밋» 규칙의 수록처가 없다

**주장.** 동결 E4(38행)의 저작 규약 3요소는 «정렬 직렬화기·버전 고정·**«논리 변경 없는 재직렬화 전용 커밋» 규칙**»인데, 계획에서 앞 둘은 착지(A5·A1)했고 셋째는 어디에도 없다. A2의 AUTHORING.md 수록 목록(35행: 금지 목록·게이트 사용법·수리 루프·ISSUED 절차·매핑 표)에 이 규칙이 빠져 있다. 직렬화기 버전 업그레이드 시 필요한 운용 규칙이라 T0 저작 규약(동결 산출물 «저작 규약»)의 일부다.

**수정 방향.** A2 수록 목록에 «재직렬화 전용 커밋 규칙(직렬화기·버전 변경 시 논리 변경과 분리 커밋)» 한 항목 추가.

## L3-9 (minor) — 인터프리터 라우팅 미결 (D4 이후의 3중 환경)

**주장.** D4로 환경이 셋이 된다: 시스템 python3(3.9.6 — 기존 도구 21종+검사기 27종의 실측 기반) · 새 venv(최신 안정판 — 온톨로지 체인) · 픽스처 서브프로세스(fixture_matrix가 `sys.executable` 상속). 계획 A8은 verify [0]~[6](venv 필요)과 [7]~[8](기존 세트)을 한 타깃에 묶는데 각 단의 실행 파이썬을 지정하지 않았다. [7]을 venv로 돌리면 기존 도구 전체가 미검증 신판 위에서 돌고(제거 API — ast.Str·distutils 류 — 사용은 grep 0건으로 확인했으나 실행 검증은 안 됨), 시스템 python3로 돌리면 Makefile 한 타깃 안에 두 인터프리터가 공존한다(가능하나 명시 필요). pre-commit 훅도 venv 파이썬이 필요한데 venv 부재(신규 클론·워크트리) 시 행동 — ttl 변경 없으면 무마찰 통과, ttl 변경+venv 부재면 차단인지 안내 후 통과인지 — 이 미정이다. D1 치환 후 release가 venv에 의존하게 된다는 사실(§7 «도구 사슬 고장 시 편집 불능 방지»가 훅·릴리즈까지 확장 적용되는지)도 명시가 없다.

**근거.** `python3 --version` = 3.9.6(실측) · `.gitignore`에 `.venv/`·`venv/` 기존재(venv 비커밋 전제 성립 ✓) · Makefile [2/7] 전 항목이 맨 `python3` 호출(94~105행) · fixture_matrix 93행 `sys.executable`.

**수정 방향.** A8에 라우팅 1행 추가: «[0]~[6] = venv 파이썬 고정 경로, [7]~[8] = 기존 `python3` 유지(기존 세트의 실측 기반 보존)». 훅은 «ttl 변경 없으면 즉시 exit 0, venv 부재면 설치 안내+차단(fail-closed)»을 D2에 명기. venv 경로(.venv 등)도 A1에 고정.

## L3-10 (minor) — §1의 byte-diff 인용이 실물과 다르다

**주장.** 계획 §1(17행)은 [2/7]의 byte-diff를 «`diff -rq dddjango/scripts codex-dddjango/skills/dddjango/scripts`»로 인용하나 실물은 `--exclude=__pycache__`가 붙어 있다(`Makefile` 106행). A8 [8]이 «기존 [2/7] 명령 이동»이라 실물 원문을 옮기면 문제없지만, §1 인용을 근거로 재타이핑하면 `__pycache__` 생성 시 가짜 red가 난다.

**수정 방향.** §1 인용에 `--exclude=__pycache__` 보완 + A8 [8]에 «Makefile 원문 그대로 이동» 명시.

## L3-11 (minor) — 짝 저작 선언과 묶음 분할의 내적 모순

**주장.** §4 의존 그래프는 «A3 어휘 ⇄ A6 셰이프·골든 (어휘·셰이프는 짝으로 저작)»(115행)이라 선언하면서, 실행 묶음은 ①(A1~A4) → ②(A5~A7)로 A3와 A6을 다른 묶음에 갈라 «각 묶음 완료 시 adoption-log 기록»(124행)까지 요구한다. A3가 ①에서 «완료»되면 짝 저작이 아니라 선행 저작이고, A6 저작 중 어휘 결함이 나오면 ①이 재개봉된다 — 순환은 아니지만 완료 선언 단위와 저작 규율이 충돌한다. 또한 A6 골든 페어는 게이트 ①~③ 적용 대상(E4)이라 A5 직렬화기 완성 전에 저작한 골든은 ② 안에서 재직렬화가 필요하다 — 묶음 ② 내부의 실행 순서(A5→A6 마감)도 명시가 없다.

**수정 방향.** 묶음 ①을 «A1·A2·A4 + A3 초안»으로, A3 확정을 ②(A6과 동시 마감)로 조정하거나, ①의 완료 기준에 «A3는 초안 상태로 통과(확정은 ②)»를 명기.

## L3-12 (minor) — B2 «T2에서 IRI 치환만» 은 과잉 주장이다

**주장.** B2(101행)는 스키마 v0 {rule_no, checker, file, symbol, severity, message}가 «E8 그래프 스키마와 필드 정합, T2에서 IRI 치환만 하면 되게»라고 주장하나, 동결 E8(42행)의 위반 개체는 «규칙 Work IRI+**Expression**·대상 파일/심볼·심각도·근거»이고 E6(40행)은 «위반 레코드는 Work+판정 시점 Expression 병기», «위반 개체=**어댑터가 채번**(실행 ID+서수)»를 요구한다. v0에는 Expression 자리도 위반 개체 식별자(실행 ID+서수) 자리도 없다 — T2 작업은 치환이 아니라 필드 확장 2종을 포함한다.

**수정 방향.** 문구를 «T2에서 IRI 치환+Expression·채번 필드 확장»으로 정직하게 고치거나, v0에 예약 필드(expression: null, record_id: 실행 ID+서수)를 지금 넣는다 — 후자가 싸다(어차피 어댑터가 채번 주체).

## L3-13 (minor) — A9 표의 동결-외 행이 라벨 없이 동결 기준에 편승한다

**주장.** 동결 T0 완료 기준의 매핑 표 문면(117행)은 «E4 금지 규칙별 픽스처 각 1 — blank node·미등록 접두사·`#` 주석 포함, 해시 단은 재직렬화 전후 트리플 조작»이다. 계획 A9 표(81~89행)의 «비정본 직렬화»·«셰이프 위반 red 4»·«sh:closed 상위 타깃(meta-SHACL 단)» 행은 이 열거 밖이다(셰이프 위반은 별도 동결 기준인 골든 페어와 겹치고, meta-SHACL red는 동결 기준에 없다 — green만 요구). 추가 자체는 보수적 방향으로 좋으나, §0(11행)이 스스로 세운 규율 — «동결 기준 외 추가 확인 항목은 «계획 추가» 라벨로 구분한다» — 을 어기고, §5 row 3이 표 «전 항목»을 «동결 완료 기준» 근거로 묶어 동결 기준의 외연을 부풀린다(Q11 방향 1).

**수정 방향.** A9 표에 라벨 열 추가(동결/계획 추가), §5 row 3 근거를 «동결 완료 기준(+계획 추가 3행 포함)»으로 정정. 셰이프 위반 행은 row 2(골든 페어)와의 관계(동일 재료 여부)를 비고로.

---

## overall

**총평.** 계획의 실물 좌표(§1)는 표 전 행이 실측과 정합한다 — 이번 리뷰가 전 행을 재확인한 결과 §1에서 틀린 것은 byte-diff 인용의 `--exclude` 누락(L3-10) 하나뿐이며, 훅 부재·파이썬 3.9.6·33=27+6·16/27 규약 분포·rule-owner-map 파생 경로·fixture 스모크 관례는 모두 실물 그대로다. 특히 rule-owner-map은 임시 트리 재생성이 현재 파일과 **byte-identical**임을 실증해 «순수 파생물» 전제가 확인됐고(B1의 사본+SHA-256 동결은 충분하다), fixture 레인은 명시 목록 등록 방식이라 신규 디렉터리 편입이 기존 하네스를 깨지 않음도 확인했다. 동결본 §8 T0 행의 내용·산출물 열도 A1~A9·B1~B3에 사실상 전부 착지했다(누락 탐색 결과: ODRL 봉인 목록·프로퍼티 역할 표=A3, 편입 범위 결정=D1, 33쌍 byte-diff=[8], 공용 모듈 착수=B2, map ID 기반=B3 — 전부 확인).

문제는 두 군데에 몰려 있다. **첫째, B트랙의 재료 규율**: 동결본은 B암 재료(§6)와 무접두 #N 주입 재료(E8)를 좁게 봉인했는데, 계획 B3는 그 봉인 밖의 원천(ⓐ final.md)을 중심 절차로 삼았고(L3-1 blocker), 조인 데모의 대표 검사기는 조인이 성립하지 않는 선행 계약 소속이다(L3-3). **둘째, 완료 기준의 장부 정확성**: 동결 문면의 «재료 재사용» 몫이 무이행으로 남고(L3-4), «계획 추가» 라벨 규율이 양방향으로 어긋난다(L3-5·L3-13). 신설 파일 1개가 기존 검증 세트에 걸리는 것(L3-2)은 이 저장소의 «전 파일 설명 의무»라는 실물 규율을 계획이 한 번 덜 센 것이다. 전부 국소 수정으로 닫힌다 — 계획의 골격(A트랙 9단 분해·집행 3점·B트랙 분리)은 동결본과 방향이 맞다.

**자기 기각 목록(시도했으나 성립하지 않은 반박).**
1. «B1 스냅숏이 원본 md 사본으로 불충분(emit 재생성과 표류 가능)» — 기각: 필요 입력 4파일만 담은 임시 트리에서 `spec_lint.py --emit-owner-map` 재생성 결과가 현재 파일과 byte-identical(실측). 현 시점 md는 순수 파생물이며, 향후 표류 요인(명세 개정·spec_lint 라우팅 코드 변경)은 정확히 스냅숏이 방어하려는 대상이다. 잔여 관찰: 스냅숏에 «생성 커밋 해시+spec_lint 버전»을 병기하면 재현 근거가 닫힌다(권고 수준).
2. «ontology-gate 픽스처 디렉터리 신설이 fixture_matrix·checker_cross_matrix를 깨뜨린다» — 기각: 두 도구 모두 명시 목록 기반(fixture_matrix.py 33~84행 PLAIN/AUTO/EXTRA + REGISTRY assert)이고 디렉터리 스캔을 하지 않는다 — 미등록 디렉터리는 무해.
3. «E6 «ISSUED 채번 대장 계승»인데 계획 A4가 «등재 0건»이라 계승 누락» — 기각: v2의 registry/ISSUED는 계획만 있고 실물이 없다(전 저장소 find 0건 — v2는 S3 개시 전 폐기). 계승 대상은 append-only 규약이지 파일이 아니며, A4·A2의 «v2 관례 계승» 문면이 정확하다.
4. «구조화 레코드 추가 채널이 registry_gate 차분을 오염» — 기각: `_FINDING_RE`(registry_gate.py 47행)는 `[#N]` 라인만 추출하고 나머지는 무시하며, 앵커·현재 양쪽 실행이 같은(현재 설치본) 검사기를 쓰므로 메시지 문면 변경도 차분을 깨지 않는다. JSON lines는 정규식 비매치라 무해.
5. «최신 파이썬 venv가 기존 도구를 파손(3.12+ 제거 API)» — 전면 기각 대신 강등: ast.Str·ast.Num·distutils 등 제거 표면 grep 0건(scripts+tools 전체)이라 파손 «실증»은 없다. 다만 실행 검증이 없으므로 인터프리터 라우팅 미결(L3-9)에 잔존 명시.
6. «hooksPath 전환이 기존 훅을 무력화» — 기각: `.git/hooks/`에 샘플 14개뿐(실측), `core.hooksPath` 미설정 — 잃을 훅이 없다. 계획 A8의 실측 문구가 정확하다.
7. «release가 대화형(read -p)·main 전용이라 verify 치환 불가» — 기각: D1의 치환 대상은 [2/7] 검증 단뿐이고 대화형 프롬프트는 그 앞 단계라 무관. (v3 리뷰 L2 overall ④에서 유사 논점이 이미 자기 기각됨 — 재제기 아님을 확인하고 접음.)
8. «저장소에 파이썬 프로젝트 파일이 실은 있다(requirements.txt 발견)» — 기각: 유일한 히트 `workspace/eval/fixtures/api_error_contract/requirements.txt`는 검사 픽스처 재료이지 저장소의 프로젝트 파일이 아니다. §1의 «프로젝트 파일 없음»은 저장소 층위에서 사실.

**미확인으로 남긴 것.** ① 최신 안정판 파이썬에서 기존 도구 21종·검사기 27종의 실제 구동(정적 grep만 수행 — L3-9에 반영). ② rdflib의 RDFC-1.0 기성 구현 유무(계획 §7이 이미 «부재 시 자체 구현» 분기를 갖고 있어 판정 불요). ③ `#` 주석 픽스처가 rdflib 파스(①단)에서 주석이 소실된 «파스 후 재직렬화 diff»로 정말 ②단에서 잡히는지의 기전(주석은 파스 단계에서 버려지므로 ② diff≠0이 맞다고 추론했으나 구현 실증은 T0 몫 — A9 스모크가 검증하게 되어 있어 계획 결함 아님).
