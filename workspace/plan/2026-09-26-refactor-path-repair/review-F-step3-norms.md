# 적대 검토 F — 로드맵 3 pre-gate 수리 설계 v1 (규범 문면 · 런타임 흐름 · 현장 증거)

- 대상: `step3-pregate-design-v1.md`. 배경: `diag-B3-pregate.md` · `diag-B3-pregate-field-frequency.md` · `evening-report.md` §5.
- 방법: 읽기와 grep 만 했다. 저장소 수정은 이 파일 하나다.
  - 현장(`spring_dream_server`)은 읽기만 했다. git 은 `show`·`cat-file`·`merge-base` 만 썼다.
  - 집계용 AST 스크립트는 scratchpad 에 있다. 현장 파일을 읽기만 하고, 쓰기는 0 이다.
  - Serena·Graphify 는 쓰지 않았다.
- 등급
  - blocker: 이대로 구현하면 설계 목적이 성립하지 않거나, 사용자 결정 없이 규범을 바꾼다.
  - major: 정상 경로가 막히거나 틀린 신호가 나며, 배포 전에 고쳐야 한다.
  - minor: 정확성·문면 보정.

## 0. 요약

| 등급 | 건수 | 요지 |
|---|---|---|
| blocker | 2 | B-1: S-2 가 현장형 명세에서 «선언 후보»(비차단)로 떨어진다.<br>B-2: G-2 의 «반환 = `_in`»·bypass 포함이 현장 102곳·승인 선례·#236 정본 본문과 충돌한다. 사용자 결정이 없다. |
| major | 7 | M-1: `--expect-base` 기대값 출처 미고정(override 경로 거짓 불비).<br>M-2: 우회를 사전 승인한 발주 문면을 막는 규범이 없다.<br>M-3: digest fail-closed 가 폴더 재사용 정상 경로를 막는다.<br>M-4: S2 문면 추가가 확정 #574 의 filtered 탈출구가 된다.<br>M-5: S-3b 트리거가 동기 사례(⑵)를 못 잡고, 권하는 처치가 결손을 U 로 세탁한다.<br>M-6: 재발화 판형 재진술 6곳이 개정에서 빠진다.<br>M-7: «(#573·#574)» 인용·wiring 이 검사기 범위를 과대 표기한다. |
| minor | 15 | §3 참조 |

## 1. §6-5 답 — G-2 문안은 검사기 #573·#574 술어와 같은 뜻인가

**같은 뜻이 아니다.** G-2 는 검사기보다 넓다. 의미(위치)와 범위(bypass·framework) 둘 다 넓다.

| 항목 | G-2 문안 | 검사기 실제 | 정본 |
|---|---|---|---|
| #573 의미 | 포트 메서드 **반환** = `_in`, **인자** = `_out`(위치 규칙) | 파일 접미 × 클래스 접미 교차만 본다. `_out.py` 안의 `…In`, `_in.py` 안의 `…Out` 이 대상이다(`check-port-adapter-pairing.py:295-300`). 위치(인자/반환)는 보지 않는다 | «들어오면 `_in`, 나가면 `_out`»(spec `2026-08-08-tree-revision-spec.md:895`) |
| #573 범위 | `port/<capability>/`·`domain_bypass_query/<capability>/`·`framework/` | `port/<capability>/` 만 본다(`:189-191`). bypass 는 `_check_bypass` 가 `_check_port_data` 를 부르지 않는다(`:314-360`). `framework/` 는 BC 순회 밖이다(`:1446`) | 정본 #573 도 «트리 49·50행»(port/<capability>/)만 가리킨다 |
| #574 | «유스케이스가 만들면 #574» | `application_layer/**` 의 `ast.Call(func=Name)` 만 본다. 대상은 import 문 모듈이 `endswith("_in")` 이고 `"port"`/`"framework"` 를 부분문자열로 가진 이름이다(`:1345-1358`) | «port/ 쪽과 framework/ 쪽 둘 다»(spec `:896`) |
| 중계 예외 | «다른 포트가 반환한 `_in` 을 그대로 넘기는 중계는 예외» | 명시 예외는 없다. Call 만 보므로 중계는 원래 뜨지 않는다. 예외가 필요한 까닭은 G-2 가 위치 규칙을 새로 도입했기 때문이다 | 없음 |

- #574 검사기의 한계
  - 속성 호출(`XIn.model_validate(...)`·`mod.XIn(...)`)과 패키지 재수출 경유 import 는 잡지 못한다(미탐).
  - BC 경로에 `report`·`support`·`transport`·`export` 가 있으면 `"port"` 부분문자열에 걸린다(과탐).
- 중계 예외는 현장에 실재한다. `query_translation/…/llm_concept_selection_port.py` 의 `select_concepts(GlossaryTranslationIn)` 이 그것이고, GlossaryTranslationPort 가 그 값을 반환한다. 따라서 예외 문장 자체는 필요하다.
- bypass 의 in/out 이 포트와 같은 방향 규칙인지는 정본 안에서 갈린다.
  - `docs/file_tree.html` 이름 줄은 조건 = `_out`(`:2090`), 결과 = `_in`(`:2097`)이다. 포트와 같다.
  - #236 정본 본문은 «`domain_bypass_query/` 가 **내보내는** 자료는 …»이고 근거를 «트리 54행»(= `<data>_out.py`)으로 든다(spec `:556`). 검사기 #236 메시지도 반환을 «내보내는 자료»로 부른다(`:357`).
  - 같은 «내보내는»이 G-2 에서는 인자(`_out`)를, #236 에서는 반환을 가리킨다.
  - 현장 bypass 자료 파일 6개는 전부 `_out` 이고 반환 타입으로 쓰인다(→ B-2).
- 자리(§3 · §1 · architect 계약): §3 이 맞다. 다만 그것만으로는 약하다.
  - R-3222 가 «명명 규약 전수는 칸의 «이름» 줄이 소유하며 §3 에 편입»이라고 정한다(`discipline-houserules-final.ttl:444`).
  - §1 트리는 `tree_mirror_check` 가 쓰는 생성 블록이라 문장을 실을 수 없다(`final.md:43-216`).
  - architect 계약은 포트 명명에 대해 «final.md §1(각 칸의 이름 줄)·§3»을 읽으라고 한다(`design-architect.md:67`).
    - 그런데 배포 final.md §1 에는 이름 줄이 없다. 이름 줄은 미배포 `docs/file_tree.html` 에만 있다.
    - G-2 는 그중 한 줄만 옮긴다. 클래스 접미 규칙 같은 이웃 공백은 남는다(m-1).
  - architect 가 이름을 정하는 지점은 symbols 메서드 행을 쓸 때다(`design-architect.md:91`). 그 절에 1행 포인터를 둔다(m-13).

## 2. §6-6 답 — 현장 실측이 가리키는데 설계가 다루지 않는 비용

1. **F4-22 전 6건의 실제 차단 여부**: S-2 가 현장형 명세를 확정하지 못한다(B-1). 넓은 기준 2건(⑤ chart-storage · ⑥ counter-room)도 여기에 든다.
   - ⑤ 는 포트 파일 import 행이 0/7, ⑥ 은 1/20 이다.
   - 두 실행은 G1 에서 이미 다른 red 를 filtered 로 처분하고 있었다. 확정이 나와도 S2·S1 인용 filtered 탈출(M-4)과 나란히 선다.
2. **현장의 방향 관례**: «반환도 `_out`»이 102곳에 퍼져 있고 발주자가 승인한 선례도 있다. G-2 는 이것을 산문 위반으로 만든다(B-2).
3. **STOP 연쇄**
   - h1: F4-22 STOP → rename → 재발화 → F4-23 거짓 red. S-3 은 뒤쪽 절반을 닫지만, B-1 이 풀리지 않으면 앞쪽 절반은 닫히지 않는다.
   - b4: 형식 red → STOP → 발주 개정 2 → 우회 → check-report 정합 5회. S-1 + `--expect-base` 로 닫으려면 M-1·M-2 가 필요하다.
4. **check-report 치환 경로의 다른 변형**
   - ① `--base HEAD` 명시 재발화: 레인 실물이 L 로 흡수되고, add→update 재라벨이 합법이 된다.
   - ② `--base <build_anchor>` 혼동: R-3434 가 금지하는 바로 그 이유다.
   - ③ Phase 2 기본 모드 재실행.
   - ④ 재발화에서 `--approved-merge-file` 누락(m-12).
   - ①~③ 은 `--expect-base` 가 의무이고 값이 고정될 때만 잡힌다(M-1).
5. **발주 문면에 굳은 우회**(b4-2 `:82` · b6 `:232`): 배포 뒤 G2 에서야 터진다(M-2).
6. **filtered 재기재 churn**: counter-room #473 ×5 가 41절·206회 되풀이됐다. 이번 4종 어느 것도 이 비용을 줄이지 않는다(m-15).

## 3. 발견

### B-1 (blocker) S-2 가 현장형 명세에서 «선언 후보»(비차단)로 떨어진다

- 근거
  - **스텁 import 출처**: 스텁이 싣는 import 는 `BASE_IMPORTS` 와 그 파일의 boundary-imports 행뿐이다(`design_pregate.py:1041-1053`).
  - **architect 계약**: 포트 계약 파일이 같은 폴더의 `<data>_in.py` 를 import 하는 것은 «경계»가 아니라 «⑶ 그 밖은 구현 재량(성문 불요)»이다(`design-architect.md:92`).
  - **해소 결과**: `_DeclarationTypes` 는 로컬 bare 이름을 «bare 타입 `X` 출처 미해소»로 돌려준다(`design_pregate.py:1692-1694`). 설계 §1.2 판정 4에 따라 이것은 **후보**다.
  - **현장 명세 분포**: 포트 메서드 symbols 행이 있는 명세 35개 중 22개가 `_port.py` 를 소비자로 하는 boundary-imports 행을 0개 갖는다.
  - **F4-22 6건** (최종본 기준 — G1 판은 git 이력으로 대조가 필요하다)
    - ① catalog 0/4
    - ② b5 0/2
    - ③ b7 14/9
    - ④ h1 0/13: `.dddjango/20260916-2112-rag-service-library/design-spec.md:441-507` 에 포트 파일 행이 없다.
    - ⑤ chart-storage 0/7
    - ⑥ counter-room 1/20
  - **fixture**: 설계가 재현 기반으로 삼는 green2 fixture 도 boundary-imports 1행이 어댑터 소비뿐이다(`workspace/eval/fixtures/pregate/green2-spec.md`).
- 영향
  - 후보는 Coordinator 규범상 «별도 비차단 보고»다(`dddjango.md:102`).
  - F4-22 수리의 전제는 «교훈 공유로는 안 막힌다»인데, 비차단 후보는 그 교훈 공유와 같은 강도다.
  - 설계 §5 의 «수정 후 선언 확정 #574 exit 2» 기대는 import 행을 넣은 fixture 에서만 성립한다. 그러면 현장 공백이 가려진다.
- 수정
  1. 해소 규칙을 더한다. bare 이름이 **같은 능력 폴더**의 형제 `<data>_in.py`/`<data>_out.py` 에 symbols 로 선언되었거나 사본에 실존하는 클래스와 유일하게 일치하면 그 신원으로 본다(결정적). 대안은 `render_stub` 가 같은 조건에서 import 를 합성하는 것이다.
  2. 양성 fixture 는 import 행 없는 현장형으로 만든다.
  3. F4-22 6건의 **G1 판** 명세(`git show <G1 커밋>:…/design-spec.md`)를 scratch clone 에서 재생해 recall 을 실측·기록한다. 나머지 실행의 G1 판 명세에서 거짓 확정이 0 인지도 함께 기록한다. 지금 «6건 모두 S-2 술어에 해당»은 문면 추론이다(frequency `:122`·`:175`).

### B-2 (blocker) G-2 의 «반환 = `_in`»과 bypass 포함이 현장·승인 선례·#236 정본과 충돌한다 — 사용자 결정 없이 규범화할 수 없다

- 근거
  - **AST 집계**(현장 main · 포트/조회 계약 110 파일, 읽기 전용)
    - 반환 타입이 `_out` 모듈인 곳은 **102** 이다.
      - 포트 96: 계약 파일 47개, 15 BC 에 걸친다.
      - bypass 6: bypass 자료 파일 6/6 전부 `_out` 이다.
    - 반환 타입이 `_in` 모듈인 곳은 20 이다.
    - 인자는 `_out` 10 · `_in` 1(중계)이다.
    - 예: `promotion/…/price_catalog_port.py:13-24` 의 `get_price(...) -> PriceCatalogItemOut | None`. h1 `ontology_graph/` 의 자료 4종은 전부 `_out` 이다.
  - **승인 선례**: h1 STOP 의 선택지 A 는 발주자가 승인했다. 문면은 «어댑터-반환 5종은 **그대로 `_out`**(… promotion 선례 `price_catalog_item_out` 동형)»이다(`docs/superpowers/orders/lane/STOP-rag-service-library-h1-in-out-naming.md:21`).
  - **정본 내부 불일치**: §1 표 아래 설명과 같다. `file_tree.html:2090`·`:2097` 과 spec `:556`(#236 «내보내는 자료» = 트리 54행)이 서로 맞지 않는다.
  - **결정 기록**: 결정 4·6 이 정한 것은 «4종 포함·구현 순서»뿐이다(`evening-report.md:91-107`). 방향 규범의 내용, 특히 반환 명명은 결정 대상으로 올라간 적이 없다(명시적 결정 게이트).
- 영향
  - 배포하면 102곳이 산문 규범 위반이 된다. 검사기는 없다 — #573 은 접미 교차만 본다.
  - 결정 1-b 의 리팩토링 커맨드는 «규칙 문구와 파일:행»으로 의미 위반을 찾는다. 이 커맨드가 곧바로 102건을 올린다.
  - 새 설계에서는 한 BC 안에 기존 `_out` 반환과 신규 `_in` 반환이 섞인다.
  - S-2 는 인자 쪽만 막는다. 따라서 «전부 `_out`» 탈출(현장 관례)은 계속 열려 있다.
- 수정: G-2 를 둘로 가른다.
  1. **이번 배포분**: 집행 가능한 절반만 규범화한다.
     > «포트·조회 계약 메서드의 **인자** 타입을 `<data>_in` 으로 두지 않는다 — `_in` 은 어댑터만 만든다(#574) · 다른 계약이 돌려준 `_in`(필드 포함)을 그대로 넘기는 것은 «만드는» 것이 아니다».
  2. **결정 브리프**: 반환 명명(`_in` 정본 대 현장 `_out` 관례)과 #236 인용 행(54↔55) 정정은 10줄 브리프로 올린다. 수치는 102/20 · bypass 6/6 · 승인 선례 1 이다. 사용자 결정 뒤에 규범화한다.

### M-1 (major) `--expect-base` 기대값의 출처가 고정되지 않는다

- 근거
  - ②는 기대값을 «G1 배너 직전 최종 실행의 pregate-report 헤더»에서 매번 다시 찾게 한다(`dddjango.md:104`).
  - 리포트는 append-only 이고 어느 절이 G1 판형인지 표지가 없다. 현장은 사람 메모로만 적었다(fortune-house `pregate-report.md:606` «G1 승인 판형 = 이 절»).
  - G1 override(②/③) 경로는 «dispatch 전에 pre-gate 를 무조건 재실행»한다(`dddjango.md:98`). 이 실행은 Phase 2 진입 전이라 **기본 모드(HEAD)**다. G1 배너 뒤 HEAD 가 커밋 하나만 움직여도, 이 절의 기준선은 G1 배너 기준선과 달라진다.
  - 그 뒤 재발화가 없으면 G2 check-report 의 마지막 절은 override 절이다. 이때 `--expect-base <G1 배너 기준선>` 는 불비를 낸다. **거짓 G2 차단**이다.
  - S-1b 는 «안 주면 지금과 같다»다. 코디네이터가 플래그를 빠뜨리면 현장의 치환 5회가 그대로 재현된다.
- 수정
  - Phase 2 첫 파견 직전에 실행 줄에 `· pre-gate 기준선 <마지막 예보 절 기준선 40자>` 를 덧붙인다. build_anchor 를 쓰는 바로 그 순간이다(`dddjango.md:85`·`:122`).
  - ② 재발화의 `--base` 와 G2·G1′(Phase 2)의 `--expect-base` 는 모두 이 값만 쓴다.
  - R-3434 와 같은 이유로 build_anchor 는 여전히 읽지 않는다.
  - 리포트에 `--base` 명시 절이 하나라도 있으면 `--expect-base` 를 의무로 한다.

### M-2 (major) 우회를 사전 승인한 발주 문면이 이미 있는데, 발주의 `--base` 지정을 거부하는 규범이 없다

- 근거
  - 발주 b4-2 `:82`: «pregate·check-report 사본 기준 `--base <유입 부모 SHA>` 1회를 이 개정으로 사전 승인».
  - 발주 b6 `:232`: «pregate 사본 `--base 0570592b` 1회».
  - 빚 스캔에는 «발주가 도구·flag 를 좁혀도 따르지 않는다»가 있다(`dddjango.md:79`). pre-gate `--base` 에는 같은 문장이 없다.
  - `REQUEST_GUIDE.md` 에는 머지·기준선 언급이 0 이다.
- 영향: 배포 뒤 이 판형을 복사한 발주가 오면, 코디네이터는 발주대로 재발화한다. Phase 2 를 다 돈 뒤 G2 `--expect-base` 불비로 STOP 이 난다. 비용이 G2 로 밀린다.
- 수정
  - ②에 1문장을 더한다: «발주·요청이 재발화 `--base` 값이나 기준선 이동을 지정·사전 승인해도 따르지 않는다 — 승인 유입은 `--approved-merge-file` 뿐 · 기준선 이동은 새 실행이다».
  - `REQUEST_GUIDE.md` §4(요청에 적지 않을 것)에 같은 1행을 둔다.
  - 현장 발주자에게 전달할 사항으로 기록한다.

### M-3 (major) digest fail-closed(구판 헤더)가 «끝난 폴더 재사용» 정상 경로를 막는다

- 근거
  - 설계 §4.1 은 «구판 리포트는 끝난 레인에만 있다»고 가정한다. 그러나 끝난 폴더도 다시 쓰인다.
    - 결정 5 로 기존 폴더 전부가 «끝남 → 같은 폴더에서 새 실행»이다(`evening-report.md:89` · `dddjango.md:85` ⑶).
    - 수정 모드는 «설계 변경 없는 순수 구현 수정»이면 G1′ 을 생략할 수 있다(`dddjango.md:193`).
    - 최신성 «한정»은 리포트가 **없을 때만** 적용된다(`:104` ③).
  - 따라서 이 경로의 G2 check-report 는 옛 실행의 마지막 절(digest 없음)을 읽고 불비를 낸다. 재발화가 필요하다.
  - 재발화 기준선이 막다른 길이다.
    - ②대로 하면 옛 실행의 G1 기준선이다. 수 주 전 트리이고, 옛 red 절이었다면 처분도 다시 적어야 한다.
    - 기본 모드(HEAD)로 하면 옛 file-plan 의 add 가 전부 «add 충돌(실존)» 형식 red 가 된다. architect 가 필요해지고, 이는 G1′ 생략 규칙과 충돌한다.
- 수정: 규범 결정 1개를 설계에 넣는다.
  - (a) 한정 확장: «새 실행에서 명세 변경 0 이면 최신성 행 `미실행(명세 변경 0 · 앞 실행 예보)` · check-report 생략».
  - (b) 규칙 추가: «새 실행은 G1′ 생략 불가(file-plan = 이번 실행 델타)».
  - 어느 쪽이든 수정 모드 절, ③ 한정, Codex 대응 절을 함께 고친다.
  - 스크립트 쪽 대안: 구판 헤더는 비차단 «툴체인 미증명»으로 두고, digest **불일치만** fail-closed 로 한다.

### M-4 (major) S2 사각 문면 추가가 확정 #574 의 filtered 탈출구가 된다

- 근거
  - 설계 §1.2 는 S2 에 «#574 는 포트 인자 선언으로 예보(본문 생성 자체는 여전히 S1)»를 더한다.
  - filtered ⓐ 는 «사각 목록 항목 번호 인용»만으로 성립한다. check-report 는 라벨만 읽는다(`dddjango.md:102` · `design_pregate.py:2693-2700`).
  - 현장은 filtered 를 넓게 썼다. counter-room 에서 스텁 한계 filtered 가 41절·206회 나왔다(frequency `:102`).
  - 재수출 경유 import 에서는 S-2 가 확정이어도 검사기는 exit 0 이다(m-3). 그래서 ⓑ 근거도 성립해 버린다.
- 영향: 확정 #574 에 «filtered(ⓐ S1 — 본문 생성)»을 달면 G1 배너가 열린다. F4-22 비용이 그대로 남는다.
- 수정
  - Coordinator 의 path 규칙 filtered 금지 문장(`dddjango.md:102` «검사기 소스에서 판정 입력이 … filtered 대상이 아니다»)과 같은 꼴로 쓴다: «선언 확정 #574(포트 인자 `_in`)는 S1·S2 인용 filtered 와 재수출 경유 검사기 exit 0 의 ⓑ 대상이 아니다 — corrected 또는 ignored(빚)만».
  - S2 문면은 «선언 확정 #574 는 사각이 아니다»로 적는다.

### M-5 (major) S-3b 트리거가 동기 사례를 못 잡고, 권하는 처치가 결손을 U 로 세탁하거나 G0 재승인을 부른다

- 근거
  - **트리거 범위**: fortune-house `pregate-report.md:528`·`:554` 의 결손은 ⑵ «자리표시자(0B — 기존 실물)»다. 파일은 기준선에 0B 로 있었다(`git cat-file -s 313f998:…/catalog_inquiry_published_error.py` = 0). S-3b 트리거 «사본에는 없지만 HEAD 에 있으면(`cat-file -e HEAD:<path>`)»는 ⑴ 모듈 부재에만 성립한다. ⑵·⑶ 은 파일이 사본에 있으므로 안내가 뜨지 않는다.
  - **r3 해소의 실체**: 현장 r3 은 update 3행만 넣고 symbols 에 이름을 적지 않았다. 그 결과 결손이 «판정 불능: update 대상 — … symbols 미선언·현재 표면에도 없음»(U, 비차단)으로 바뀌었다(`:576`·`:606`). symbols 없는 update 행은 결손 → U 도피로가 된다(`design-architect.md:92` «미선언이면 … 판정 불능»).
  - **타 BC 파일**: 세 파일은 타 BC(fortune_catalog·fortune_reading) 소속이다. file-plan 에 적으면 09-26 규칙 «스캔하지 않은 BC 에 파일 추가·변경 → 그 BC 추가 스캔·G0 재승인»(`dddjango.md:79`)이 발화한다.
  - **«add/update» 안내의 부정확성**: 기준선에 없는 경로를 update 로 적으면 형식 red 다(`design_pregate.py:2646-2649`).
- 수정
  - 트리거를 «결손 단계 무관 · `blob(HEAD:path) ≠ blob(기준선:path)`»로 바꾼다.
  - 안내 문구를 바꾼다: «기준선에 있으면 update + **그 이름을 symbols 에 선언** · 없으면 add · 타 BC 경로면 G0 재승인 대상(대가) · 그 밖은 filtered(S8) 유지 가능».
  - 설계의 «현장 처치 = 올바른 회계» 판단은 symbols 선언이 빠졌으므로 절반만 맞다고 정정한다.

### M-6 (major) 재발화 판형의 요약 재진술 6곳이 G-1 개정에서 빠진다

- 근거
  - Claude `dddjango.md:116`·`:190`·`:205` 와 Codex `SKILL.md:134`·`:206`·`:220` 이 모두 «재발화 판형: `--base <G1 기준선 SHA>` 명시·WIP 커밋/stash»로 플래그를 열거한다.
  - 설계 §2.3 G-1 은 ②·③·산출물 위치만 고친다.
- 영향
  - 반송 경로(5번 감사·수정 모드 G1′·Contract mismatch)의 코디네이터는 가까운 문면을 따른다.
  - `--approved-merge-file` 이 빠지면 b4 형식 red 가 재발한다.
  - `--expect-base` 누락은 G2 에서야 드러난다.
- 수정: 6곳을 «Phase 1 «캐시 skip·재발화 판형» ②(플래그 전부)» 참조로 바꾸거나, 플래그를 전부 적는다.

### M-7 (major) G-2 의 «(#573·#574)» 인용과 wiring 이 검사기 집행 범위를 과대 표기한다

- 근거: §1 표. #573 검사기는 port/<capability>/ 의 접미 교차만 본다. #574 는 `application_layer` 의 Name 호출만 본다.
- 영향
  - 새 R-ID 를 `enforcedBy check-port-adapter-pairing.py` 로 wiring 하면, 위치 규칙이 G2 에서 기계 집행된다는 거짓 신호가 된다.
  - 현장 102곳은 그 G2 를 통과해 왔다.
- 수정
  - 문안 인용을 «#574(생성) · 트리 49·50·54·55·153·154행 이름 줄»로 바꾼다.
  - wiring 은 다음과 같이 나눈다.
    - 인자 절반: `enforcedBy design_pregate.py`(S-2) + `check-port-adapter-pairing.py`(#574 생성).
    - 반환 절반(B-2 결정 뒤 규범화할 때): `delegatedTo agent-discipline-reviewer`.

### minor

- **m-1 클래스 접미**
  - 정본은 BC 포트 자료에 대해 «클래스에는 접미사를 안 단다 — `CancellationNoticeOut` ✗»(`docs/file_tree.html:2050`)이고, framework 는 «`<Data>Out`/`<Data>In`»(`:3077`·`:3084`)이다.
  - 현장은 BC 포트에서도 접미를 붙인다(h1 은 `GraphTripleIn`→`GraphTripleOut` 로 rename 했다).
  - S-2 메시지 «`_out` 으로»는 파일만 말한다. 클래스 `…In` 을 둔 채 파일만 옮기면 스텁에서 #573 이 red 가 된다(`:296`). 반송 1회가 는다.
  - 수정: 메시지에 클래스 이름도 적는다. B-2 브리프에 접미 현황을 포함한다.
- **m-2 필드 중계**: «반환 주석에 나오지 않으면 확정»은, 반환된 `_in` 의 **필드**로 받은 `_in` 을 넘기는 중계를 거짓 확정한다. 현장에는 0건이다. #202 `walk` 처럼 반환 타입의 필드 도달까지 «반환됨»으로 센다.
- **m-3 신원 기준 차이**: S-2 는 정의 모듈로 해소하고(`identity` 가 import 를 따라간다), 검사기는 import 문의 모듈 문자열만 본다(`:1349`). 패키지 `__init__` 재수출 경유면 S-2 는 확정이지만 G2 검사기는 침묵한다. 규범상 S-2 가 맞다. 다만 M-4 의 ⓑ 탈출과 겹친다.
- **m-4 S-2 update 범위**
  - symbols 에 클래스를 다시 선언하지 않은 update 에서는 `_DeclarationTypes.load` 가 실파일 ClassDef 전체를 쓴다(`design_pregate.py:1523-1600`). 손대지 않은 레거시 메서드도 확정 대상이 된다.
  - 현장에는 지금 `_in` 인자가 1건(중계)뿐이라 당장 위험은 낮다.
  - 수정: «symbols 에 선언된 메서드만»을 명시한다.
- **m-5 I 의 정의**
  - 설계는 «p ∉ 기준선 트리»로 한정한다. registry F1(`registry_gate.py:604-609`)에는 이 한정이 없고, 대신 «= HEAD:p» 조건이 있다.
  - main 이 **기존** 파일을 바꾼 유입은 사본에 실리지 않는다. 그래서 update 시뮬레이션과 실존 ⑶ 이 기준선 판을 본다.
  - 여러 승인 머지가 같은 p 를 건드리면 어느 blob 을 쓸지 정해져 있지 않다. 사슬상 마지막 참여 머지로 정한다.
- **m-6 S-1 실행 불능·소유**
  - 목록 검증 실패(exit 1)의 라우팅이 없다. registry 쪽처럼 «발주자 사안 → STOP» 으로 둔다(`dddjango.md:175`).
  - ⓓ 메시지는 «발주자가 등재한 머지면 `--approved-merge-file` · 미등재면 STOP(코디네이터는 목록에 쓰지 않는다)»로 바꾼다. 지금 안은 파일 생성을 유도할 수 있다.
  - 새 실행이 옛 `approved-merges.txt` 를 물려받는다. `dddjango.md:85` 의 이월 금지 목록에 이 파일이 없다. 조상이 아닌 옛 SHA 가 있으면 pre-gate 까지 exit 1 이 된다.
- **m-7 `--expect-base` 접두 길이**
  - 현장 메모·발주는 7~8자 SHA 를 쓴다(`--base 313f998` · `97cdb35f`).
  - «40자·접두 12 허용»이면 7~8자 값이 거짓 불비를 낸다.
  - 수정: 리포트 안에서 유일한 ≥7자 접두면 일치로 본다.
- **m-8 `--block-hash` 2행 출력**
  - fixture ⑧ 은 stdout 전체가 «블록 해시 <h>» 와 같다고 단언한다(`workspace/tools/pregate_fixture_run.py:252-256`). 설계의 «기존 묶음 기대값 무변»과 어긋난다.
  - skip 행 정형(`dddjango.md:104` ①)에도 digest 칸이 없다.
- **m-9 digest 과민**
  - `_tree_digest` 는 scripts 의 `*.py`·`*.json` 전량이다(`registry_gate.py:227-235`). 판정에 쓰이지 않는 `rulepack.json`(그래프 명칭 투영물)도 들어 있다. 그래서 graph-owned 문면만 바뀐 릴리즈도 digest 가 바뀐다.
  - 실측의 «문서만 바뀐 릴리즈를 stale 로 오판하지 않는다»(frequency `:93`)는 graph 가 무변일 때만 참이다.
  - 수정: 설계에 이 성질을 명시하거나, pre-gate 용 digest 에서 `rulepack.json` 을 뺀다.
- **m-10 좌표·잔여 서술**
  - 설계가 인용한 Coordinator `:96` 은 지금 `:102` 다.
  - S-3 뒤에는 ② 의 «명시 `--base HEAD` 포함 … 오버레이 실존 add = 기실현» 문장(`dddjango.md:104`)이 기준선 = HEAD 일 때만 참이다. «Coordinator 문면 무변» 판단은 이 문장에 대해서는 틀리다. graph 개정 1문장이 필요하다.
- **m-11 G1/G1′ 배너 문면**
  - G-1 은 `--expect-base` 를 G2 에만 붙인다. Phase 2 반송의 G1′ 배너도 check-report 가 근거다(`dddjango.md:102`). 여기에도 같은 플래그를 붙인다.
  - 배너 부재 사유 열거(`dddjango.md:58` «형식 red·stale·처분 미기재»)에 «툴체인 stale·기준선 치환»을 더한다.
- **m-12 `--approved-merge-file` 누락 탐지**
  - check-report 는 재발화가 이 플래그를 빠뜨렸는지 모른다.
  - 수정: 명시 base 절이고, 리포트 폴더에 `approved-merges.txt` 가 있는데 헤더에 «승인 유입» 행이 없으면 경고한다.
- **m-13 architect 결정 지점**
  - 이름은 symbols 메서드 행을 쓸 때 정해진다(`design-architect.md:91`). §3 만으로는 교훈 공유와 같은 강도다.
  - 수정: symbols 절에 1행 포인터를 둔다 — «포트·조회 계약 메서드 인자에 `_in` 금지 — pre-gate 선언 확정 #574».
- **m-14 S-3b «(G2 귀속 대상)»의 근거**
  - 이 근거는 «앵커는 어떤 작업 커밋보다 앞선다»(`dddjango.md:122`)에 기댄다.
  - 동기 커밋 `dff956cc` 는 옛 다단 빌드에서 Phase 1 설계 라운드 중에 들어온 커밋이다. 당시 앵커 `c8b4498` 은 그보다 앞이고, 명시 기준선 `313f998` 은 앵커보다 뒤였다.
  - 현행 모델에서 Phase 1 재실행은 기본 모드(HEAD)라 이 사례는 재현되지 않는다.
  - 수정: S-3b 적용 범위를 «Phase 2 명시 재발화»로 적는다.
- **m-15 설계 밖 비용(기록만)**: 스텁 한계 filtered 는 절마다 다시 적어야 한다(R-3433). counter-room #473 ×5 가 41절·206회 되풀이됐다. 이번 4종 어느 것도 이 비용을 줄이지 않는다. 백로그로 둔다.
