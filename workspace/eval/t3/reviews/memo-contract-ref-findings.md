# 적대 리뷰 — T3 마감 처분 메모 `contract-ref.md` (선행 계약 7종 contract_ref 조인)

- 대상: `workspace/eval/t3/memos/contract-ref.md` (전문 정독 + 재현 실행)
- 리뷰일: 2026-08-22 · 기준 그래프: ontology/ 46,105 트리플 · 베이스라인 `make verify-ontology` 11단 green ·
  `ontology_rulepack.py --check` green (실측)
- 판정: **apply_with_fixes** — 조인 판정표(§3)와 기구 선택(§4 A안)은 실물로 성립하나,
  이행 절차 §5 를 문면 그대로 적용하면 **red 3경로**가 열린다(B1·B2·B3).

## A. 재현·확증된 것 (메모 주장 중 실물 대조 통과)

1. **7종 실물**: `reverse_coverage.py` `PRIOR_CONTRACT_SCRIPTS` 7종 = 메모 §1 표와 일치.
   owner-map ⓒ 행 `grep -c` 실측 7종 전건 0 · 혼성 3종 11·18·4 행 — 메모 수치 그대로.
2. **판정표 §3 의 7 Work 전건 실재**: R-0122·R-1186·R-3191·R-1662·R-0795·R-0091·R-1040 —
   ISSUED 발행 ✓ · `currentExpression` 각 1 ✓ (revision 값까지 메모 표와 동일:
   0122/0091=@2026-08-19, 나머지=@2026-08-22) · Expression 왕복(type·specializationOf·revision) ✓ ·
   `djr:enforcedBy <djr#c/<검사기>>` 간선 ✓. §2 의 `enforcedBy` Work 수 표(17·15·3·13·14·19·12)도 실측 일치.
3. **문면 실재**: R-1186 블록에 `default`·`.filter(status="pending")` 축자 실림(사건 ⓐⓑ 포섭 주장 성립) ·
   R-0122 블록(s017-3.2/b9, 11개 규범 합진술)에 «루트 평면 `<app>/`은 #486·#490 위반» 문장 실재 ·
   R-1662 블록에 «silent하게 필수 서브시스템으로 빌드하지 않는다»+«G1에서 채택을 택하면…» 실재 ·
   R-0795·R-0091·R-1040·R-3191 문면 각 대조 통과. R-0122 는 유일 집행자(enforcedBy 단독) 주장도 실측 ✓.
4. **발화 사건 유형 전수**: 7 검사기의 findings `.add()` 호출 사이트는 메모 §1 표의 8곳이 전부
   (그 외 `.add()` 는 set 연산). 메시지 문면 일치. `_default_checker()` = `Path(argv[0]).name`
   → 레코드 `checker` 가 `contract#<파일명>` 키와 정확히 맞는 것도 확인.
5. **§5-2 문법·검사 확장 재현**: 제안 정규식 `^(rule#[1-9][0-9]*|contract#check-[a-z0-9-]+\.py)$` 은
   7 텍스트 전건 매치·기존 rule# 3건 유지·기형(`#10`·`rule#010`·언더스코어·확장자 이탈) 거부.
   임시 정본 트리에 7 alias 를 넣고 — 현행 도구는 ⑥″ 문법 위반 7건으로 red(1·2단계는 한 변경 집합이어야 한다는
   뜻), 메모 §5-2 대로 패치한 판정(축 분기 + PRIOR 실재 + enforcedBy 실재)은 green. 재현 성립.
6. **셰이프 무개정 주장 성립**: `AliasEntryShape` 에 aliasText 패턴 제약 없음 → 7 alias 병합 그래프
   pySHACL `conforms: True` 실측. 게이트 fragment 검사(§14)도 인코딩만 봐서 신 IRI 통과.
7. **계수 기대표 산식**: `ontology_hierarchy_check --with-golden` 임시 트리 실측 `AliasEntryShape: 12`
   (골든 2 = alias-valid + alias-missing-type-invalid). §5-4 의 5→12 정확.
8. **③ ViolationShape 정합**: `violatesWork maxCount 1`(shapes L266–271) — C안 기각 논거 성립.
   §6 부수 발견도 실물 정합: `_vid` L95–98 키에 검사기 축 없음 + `byChecker minCount 1·maxCount 1`
   (shapes L218–223, 메모 좌표 정확). «오늘의 대장으로 도달 불가» — 조인 10종(rule 3+contract 7)
   전부 상이 Work 실측 ✓. 별건 분리 권고 타당.
9. **문서 좌표 전건 실재**: t2-plan L24·L49·L145(D12) · 블루프린트 L184(개정 4) · overlap-review L22 ·
   L-P.md L15(경로는 `2026-08-19-ontology-t2-1-adversarial/` — 메모는 파일명만 인용) ·
   corpus-manifest 30문서(31행-헤더) · 검사기 docstring «그래프 좌표(T2-2)» 블록 7건 좌표 전건 일치 ·
   codex 쌍둥이(`codex-dddjango/skills/dddjango/scripts/`) 7종 byte 동일(동기 절차 성립 전제 확인) ·
   어댑터 설계 노트 §1 «애초에 Work 가 없다» 문장 실재(L23).

## B. Blocker — 적용하면 red·의미 오류

### B1. §5-3 어댑터 개정안이 **rule# 레인 조인을 끊는다** (verify red — 재현됨)

- 증거: 현행 `load_alias_map()` 은 `"#N"` 키로 반환하고(violation_adapter.py L60–61) `convert()` 의
  rule 레인 조회는 `alias.get(rule)`(L120), 레코드 `rule` 은 무접두 `#N`(같은 파일 docstring L5 ·
  findings.py 레코드 판형). 메모 §5-3 은 «rule# 하드코딩 제거, aliasText **원문 키**로 반환»만 지시하고
  rule 레인 조회 키 변경은 **지시하지 않는다**. 원문 키 맵으로 재현: `alias.get("#488") → None`
  — rule 레인 전건 `rule_unjoined` 강등.
- red 경로 2중: ⓐ 어댑터 `--self-test`(joined==1 단언) exit 2 — §5-7 자체에서 적발.
  ⓑ `query_golden_check.observe()` 가 rule 레인 레코드 3건을 어댑터에 태워
  `nodes != 3 → "어댑터가 실런 3사건을 3노드로 굽지 않았다"` **하드 단언** — 골든 `--emit` 재생성으로도
  안 지워지는 red(verify-ontology 11/11).
- 수정안: `convert()` rule 레인을 `alias.get("rule" + rule)` 로 바꾸는 지시를 §5-3 에 명기하거나,
  `load_alias_map()` 이 rule 공간은 종전 `#N` 키 + contract 공간은 원문 키의 **2형 키**로 반환하게 명기.

### B2. §5 픽스처 목록에 `query-golden.json` 누락 — verify-ontology 11/11 red

- 증거: `workspace/eval/fixtures/rulepack/query-golden.json` 의 `q4.with_alias = ["R-0118","R-0120","R-0124"]`.
  Q4(`q4-injection-order.rq`)는 `OPTIONAL { ?aliasNode djr:aliasFor ?work ; djr:aliasText ?aliasText }` 로
  alias 를 Work 행에 물질화한다 — 7 alias 등재 시 `with_alias` 는 10종이 되어 골든 diff → exit 2.
  메모 §5-4 는 `target-counts.json` 만 갱신 대상으로 든다.
- 수정안: alias 등재와 같은 변경 집합에서 `query_golden_check.py --emit` 재생성(§15 ⑤ 사유 병기 —
  q4.with_alias 3→10)을 §5-4 에 추가.

### B3. **rulepack 사슬 미처분** — verify-base red + naive 재생성 시 C암 주입 문면 왜곡(의미 오류)

- 증거 ⓐ (red): verify-base 가 `ontology_rulepack.py --check` 를 상시 실행(Makefile L78 — 베이스라인
  green 실측). 팩 `built_from` 은 **전 ttl 의 sha256** — `aliases.ttl` 편집만으로 byte 표류 → exit 2.
  메모 §5 는 `dddjango/scripts/rulepack.json`(+codex 미러) 재생성을 어디에도 언급하지 않는다.
  §5-7 의 검증 목록(«make verify-ontology 10/10»)에도 verify-base 가 없어 절차 안에서 적발되지 않는다.
- 증거 ⓑ (의미 오류): naive 재생성 시 생성기 L153 `key = "#" + alias.split("#",1)[1]` 이
  `contract#check-common-container.py` 를 by_alias 키 `#check-common-container.py` 로 접고(위반 레코드가
  절대 방출하지 않는 사각 키), 런타임 `rulepack.py rules()` L230–231 이 Work 의 «번호» 를
  `"#" + aliases[0].split("#",1)[1]` 로 렌더한다 — **R-3191 은 `check-layer-skeleton.py`(규칙 레인,
  C암 selector 도달)의 tier-2 경로로 주입에 실재 도달**하는 Work 인데, 재생성 후 그 번호가
  `R-3191` 이 아니라 `#check-common-container.py` 로 나간다. «위반 목록이 #N 으로 말하므로 같은 번호
  체계» (rules() docstring) 계약 위반 = C암 처치 문면 왜곡. 나머지 6 Work 도 단독 집행이라 오늘은
  잠복이지만 같은 형식이다.
- 수정안: 생성기(또는 `rules()`/by_alias 조립)에서 팩의 aliases·by_alias·번호 렌더를 **`rule#` 공간
  한정**으로 필터(계약 레인 alias 는 그래프 전용 — D12 «위반 그래프의 Work 조인은 규칙 발견 한정» 문면과도
  정합)한 뒤 `make rulepack` 재생성 + codex 미러 동기, 필터에 스모크 단언 1건 추가. §5-7 검증 목록에
  verify-base(최소 `ontology_rulepack.py --check` + `rulepack_smoke.py`) 명기.

## C. Caution — 적용 가능하나 주의·정정 필요

1. **§8ⓐ «restates 간선 0건(실측)» 은 거짓** — 생산 그래프 실측 **616건**(메모가 인용한 @2026-08-22
   판본들과 같은 그래프). 잠정 2행은 지금 재대조 가능하고, 실측 결과 두 선택 모두 생존한다:
   ① R-0091 블록(§6.2)은 §2.2 블록·SKILL 블록이 모두 그것을 restates 하는 종단 — 정본 확인, 선택 유지.
   ② R-1186 블록(§2.5/b5)은 architecture-ddd §3.2(R-0112 블록)를 restates 하지만, R-0112 문면의 주어는
   «도메인 enum **선언**·파생 소유»고 검사기 사건은 «소비 규율»(default/.filter 축자는 R-1186 에만 실림)
   — 메모의 주어 상이 논거가 실물로 성립해 선택 유지. **메모 문면 정정 + «웨이브 4 직후 재대조» 조건을
   «본 처분 적용 시 재대조 완료(본 리뷰 실측 원용)» 로 대체**해야 거짓 전제가 완료 기준에 남지 않는다.
2. **§5-1 IRI 가 authoring L143 규약과 자가모순**: L143 은 `alias-<공간>-<번호>` 인데 제안 IRI 는
   `alias-contract-<검사기 이름>`(비번호). 기계 검사가 없어 red 는 아니나, §5-6 의 1행 신설 때 L143 의
   «번호» 문면 자체를 (예: `alias-<공간>-<식별자>`) 함께 고치지 않으면 문서-실물 표류가 생긴다.
3. **«make verify-ontology 10/10» 은 구판 라벨** — 현행은 11단(질의 카탈로그 골든 11/11 추가). 그 11/11 이
   바로 B1ⓑ·B2 를 무는 단이므로 라벨 정정이 실질 의미를 갖는다.
4. **BK 실험 중 처치 재료 변경**: B3 수정(rulepack 재생성)은 C암 주입 재료(rulepack.json)를 바꾼다.
   실험 런 진행 중이므로 적용 시점을 실험 블록 경계로 잡거나 런별 팩 sha 기록을 남겨야 A/B 교란이 안 된다
   (§6 의 «같은 커밋에 넣지 말 것» 규율과 동형).
5. §5-3 tally 2분(`contract_joined`/`contract_unjoined`) 자체는 무해 확인 — `query_golden_check` 는
   `tally["joined"]` 만 읽는다. 단 어댑터 stderr 보고 문면(L209–211)을 파싱하는 외부 소비자가 있는지는
   본 리뷰 범위 밖(실측 소비자 0건 — workspace/tools 내 grep).

## D. 판정

**apply_with_fixes** — §1~§4·§6~§8 의 판정·논거는 실물 대조를 통과했고(§8ⓐ 실측 오류 1건 제외),
§5 이행 절차는 B1(어댑터 키 회귀)·B2(query-golden 누락)·B3(rulepack 사슬 미처분+번호 렌더 왜곡)
3건을 고치기 전에는 `make verify` 를 red 로 만든다. 세 blocker 는 전부 국소 수정으로 닫힌다.
