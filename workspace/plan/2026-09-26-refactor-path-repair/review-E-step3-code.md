# 적대 검토 E — step3 pre-gate 수리 설계 v1 · 코드 대조 (2026-09-26 밤)

- 대상: `step3-pregate-design-v1.md`(S-1·S-1b·S-2·S-3·S-3b·S-4 · G-1·G-2·G-4).
- 대조한 코드: `dddjango/scripts/design_pregate.py`(3002행) · `anchor_diff.py` · `registry_gate.py` · `check-port-adapter-pairing.py` · `workspace/tools/pregate_fixture_run.py` · `pregate_field_report_smoke.py` · `dddjango/commands/dddjango.md` · `dddjango/agents/design-architect.md`.
- 실행: scratch `…/scratchpad/rv3a/` 에서만 했다. `probe_s2.py` 는 저장소의 `design_pregate.py` 를 모듈로 읽어 `parse_spec` → add 스텁 렌더 → `_DeclarationTypes.resolve` 를 돌린다. 이것을 현장 명세 6건(h1 개정 전판은 `git show a1e1635b8:…/design-spec.md`)에 적용했다. 현장 저장소는 `git show`/`log` 와 읽기만 했다. 저장소 쓰기 0 · Serena·Graphify 미사용.

## 0. 결론

| 등급 | 건수 | 요지 |
|---|---|---|
| blocker | 1 | B1 S-2 가 현장 명세에서 거의 해소되지 않는다. #574 확정이 뜨지 않으므로 F4-22 가 닫히지 않는다 |
| major | 4 | M1 update 포트의 부분 선언 · legacy 메서드 → 거짓 확정 · M2 반환 해소 불능 정책 미정 · 중첩 중계 · M3 S-1 의 I 가 신규 경로만 본다(F1 과 다름) · M4 S-4 fail-closed 전제(진행 중 레인 0)가 지금 거짓 |
| minor | 14 | m1~m14 (아래) |

## 1. 설계 §6 질문에 대한 답

1. **S-2 술어의 오탐·미탐**
   - 가장 큰 문제는 술어 이전의 **해소 단계**다(B1). 현장 명세는 포트 파일의 같은 능력 폴더 import 를 boundary-imports 에 적지 않는다. architect 계약이 «⑶ 그 밖은 구현 재량(성문 불요)»이기 때문이다. 그래서 인자 · 반환이 모두 «bare 타입 출처 미해소»로 떨어지고 후보에 그친다.
   - 해소가 된다고 쳐도 거짓 확정 경로가 셋 있다.
     - update 포트 부분 선언이 실물 클래스를 덮어 기존 반환을 지운다(M1).
     - legacy 메서드가 대상에 들어간다(M1).
     - 중첩 필드 중계를 못 본다(M2).
   - 미탐 경로는 반환 해소 불능 처리 방식에 따라 갈린다(M2).
   - 항목별:
     - `Optional[...In]` 은 `Optional` import 가 명세에 없으면 해소되지 않는다. 지원 컨테이너 집합이 `:1624` 이고, 머리 해소 실패는 `:1620`→`:1629` 로 간다.
     - `X | None` · `list/tuple[...]` 는 된다.
     - `Iterator`·`Iterable`·`Annotated`·사용자 제네릭은 해소 불능이다.
     - `Generic[T]` 는 `TypeVar` 호출이라 «타입식 미지원»이 된다.
     - BC 간: 반환 우주가 전 BC 라서 다른 BC 포트의 반환도 «중계 가능»으로 본다. 미탐 방향이다(m12).
     - `framework/`: 우주에 넣지 않으면 framework 포트가 반환한 `_in` 의 중계가 거짓 확정이 된다(m13).
2. **S-1 의 I 와 registry provenance 의 어긋남**
   - 어긋난다. 설계는 «F1 앞 절과 같다»고 하지만 `p ∉ 기준선` 절을 더했다. registry F1(`registry_gate.py:598-601`)에는 이 절이 없다.
   - 그래서 main 이 **수정·삭제한 기준선 경로**가 사본에 반영되지 않는다(M3).
   - 복수 머지의 blob 선택 규칙도 없다(M3). 설계에서 «참여» 한정이 빠졌다(m1).
   - 앵커 L 에 싣는 것 자체는 귀속을 숨기지 않는다. 계획 스텁과 유입의 상호작용 위반은 N∖L 로 남는다.
     - 다만 «기준선의 레인 실물 × 유입» 상호작용 위반은 L∩N 으로 사라진다. G2 registry 는 이것을 L 조건(R(M^2)∖R(M^1)) 미증명으로 귀속 유지한다.
     - 즉 pre-gate 가 G2 red 를 예보하지 않는 새 사각이 생긴다. 우회 판형에서도 같았으므로 회귀는 아니다. S4 사각 문면에 한 줄 적어 둘 것.
3. **S-3 가 기존 흐름을 깨는가**
   - 명시 `--base HEAD` · 초기 예보 · E1~E4 · E1′/E2′ · modes 12조합은 판정이 무변이다. 코드를 읽고 확인했다(§3 표).
   - 깨지는 것은 두 가지다.
     - «보고 차이뿐»이라는 주장. WIP 삭제된 remove 대상과 WIP 에 이미 구현된 update 함수는 **판정이 바뀐다**(m8).
     - Coordinator·architect·Codex 문면의 «dirty overlay 자동 반영»(`dddjango.md:102` · `design-architect.md:92` · Codex `SKILL.md:121`). 재발화 판형에서는 거짓이 된다(m8).
   - 기준선 = HEAD + WIP(첫 슬라이스 미커밋) 경로의 골격 가드 오염은 S-3 로 닫히지 않는다(m7).
4. **S-4 fail-closed 가 부당하게 막는 레인**
   - 막는다(M4). 09-26 에 시작한 워크트리 레인이 2개 있다.
     - `lane-8-B-9/.dddjango/20260926-2053-showcase-server` — 리포트 있음
     - `lane-5-1-4/.dddjango/20260926-2242-carried-request-lifetime`
   - main 에는 v2.18.4 이후 미배포 스크립트 변경이 이미 있다(`check-transaction-boundary.py` · `rulepack.json` · `pregate_symbol_kinds.json`).
   - 이번 배포 뒤 G2 check-report 는 «구판 헤더»로 불비가 된다. 새 검사기와 S-2 로 재발화하면 새 red 가 나올 수 있고, 차단 규범상 **Phase 2 중 architect 반송**이 된다.
5. **G-2 문면과 검사기 술어의 일치**
   - 일치하지 않는다(m12).
     - #573 은 `port/<capability>/` 자료에만 걸린다(`check-port-adapter-pairing.py:188-194`·`:241-242`). `port/domain_bypass_query/<cap>/` 와 `framework/<cap>/` 에는 걸리지 않는다.
     - #574 는 부분 문자열 술어(`"port" in m` · `:1349`)다. 그리고 `from <…_in> import X` 로 가져온 이름을 `X(...)` 로 부르는 경우만 잡는다(`:1352-1356`).
   - `domain_bypass_query` 는 `port/` 아래이므로 #574 범위 안이다. 설계가 따로 나열한 것은 중복이다.
   - 중계 예외는 검사기에 개념이 없다. 검사기는 «생성 호출»만 보므로 중계는 원래 위반이 아니다. 문면이 예외로 적는 것 자체는 무해하다.
6. **빠진 것**
   - ① S-2 가 현장 명세에 실제로 발화하는지 재측정하지 않았다(B1). 검증 판형 r22 는 포트 import 행을 가진 비대표 명세다.
   - ② 확정 뒤 교정 경로. `_out` 으로 개명하면 클래스 접미 `…In` 이 #573 에 걸린다. 파일과 클래스를 함께 바꾸라는 안내가 없다(m12).
   - ③ 수정·삭제된 기준선 경로의 유입. accounts-1 변종의 수정 파일판이다(M3).
   - ④ 배포 게이트(M4).
   - ⑤ 골격 가드 잔여(m7).

## 2. 발견

### B1 [blocker] S-2 가 현장 명세에서 해소되지 않는다 — #574 확정이 나지 않아 F4-22 가 닫히지 않는다

- **근거**
  - 해소 경로: `_DeclarationTypes.identity(local=True)` 는 모듈 표면에 import 가 없으면 `bare 타입 … 출처 미해소`를 반환한다(`design_pregate.py:1693-1694`).
  - 표면이 비는 이유: add 스텁의 표면 = `entry.imports` + `BASE_IMPORTS` 이다(`:1037-1053` · `load` `:1573-1580`).
  - architect 계약은 경계 import 만 성문한다. «⑶ 그 밖은 구현 재량(성문 불요)»(`design-architect.md:92`)이다. 같은 능력 폴더의 `<data>_in.py` import 는 경계가 아니다.
- **실측(probe_s2.py)**
  - h1 개정 전판에서 `OntologyGraphPort.run_select(triples: tuple[GraphTripleIn, ...])` 와 `UpstreamFetchPort.fetch(arguments: UpstreamFetchArguments)` 가 둘 다 «bare 출처 미해소»였다. 반환 `ParsedTriple`·`ShaclOutcome`·`GraphRow`·`FetchedUpstream` 도 전부 미해소였다.
  - 현장 6건 중 5건은 비원시 포트 주석의 해소가 0~2건이다.

    | 명세 | 비원시 포트 주석 해소 |
    |---|---|
    | catalog | 0 |
    | decisive | 0 |
    | b5 | 0 |
    | counter-room | 2 / 42 |
    | h1 | 0 |
    | b7 | 9 / 14 (포트 파일 import 14행이 있는 유일한 명세) |

  - 설계 규칙 4에 따르면 이들은 전부 «선언 후보»(비차단)로 간다. 설계가 근거로 든 h1 이 확정으로 서지 않는다.
  - 검증 계획의 r22 판형(`…/f4-22/spec22.md:48`)에는 포트 파일 import 행이 있다. 그래서 수정 후 exit 2 는 현장을 대표하지 못한다.
- **수정 제안**
  1. S-2 전용 결정적 폴백 해소를 둔다. 포트 계약 모듈(`port/<cap>/*_port.py` · `port/domain_bypass_query/<cap>/*_query.py` · `framework/<cap>/*_port.py`)의 bare 이름 X 를 **같은 능력 폴더**의 두 출처에서 찾는다.
     - 계획 symbols 선언(`plan.entries[*].declarations` 클래스)
     - 사본 실물 최상위 클래스
     - X 를 정의한 모듈이 **정확히 하나**면 그 (모듈, X)를 신원으로 삼는다. 0 또는 복수면 후보로 둔다.
     - 폴백은 S-2 에서만 쓴다. `#197`·`#202` 경로는 무접촉이다.
  2. 반환 쪽에도 같은 폴백을 쓴다.
  3. 픽스처 양성 1을 «포트 파일 import 행 없음»(현장 판형)으로 바꾼다. r22 판형은 보조로 남긴다.
  4. 착수 전에 현장 6건의 **수정 전 판**(`git show <커밋>:…/design-spec.md`)에서 S-2 결과표(확정/후보/무)를 만든다. «6건 모두 술어에 해당»은 지금 [추론]뿐이다.

### M1 [major] update 포트의 부분 선언이 실물 클래스를 덮는다 · legacy 메서드가 대상에 든다 → 거짓 확정(차단)

- **근거**
  - `_DeclarationTypes.load` 는 update 칸에서 symbols 로 선언한 클래스를 **선언본으로 교체**한다(`table.update(declared)` `:1600`).
  - 선언본은 명세가 적은 메서드만 가진다(`:1590-1596`). update 클래스도 `declarations` 에 들어간다(`:662-663`).
  - 결과:
    - 기존 `get(self) -> FooIn` 이 있는 포트에 명세가 `put(self, item: FooIn)` 만 적으면, 반환 우주에서 `get` 이 사라진다. FooIn 은 «어떤 포트도 반환하지 않음»으로 확정된다.
    - 반대로 update 칸에 symbols 가 없으면 `load` 가 실물 클래스를 그대로 준다. 설계 대상 «클래스 메서드»를 그대로 구현하면 **이 명세가 바꾸지 않는 legacy 메서드**도 확정 대상이 된다.
  - 이 확정은 registry 차분(N∖L)이 아니다. 따라서 재발화마다 ignored+빚 처분을 강제한다.
- **수정 제안**
  - 대상은 **명세가 선언한 메서드만**으로 한다(`entry.declarations[*].methods`).
    - add 는 전부다.
    - update 는 선언 메서드만 보되, 실물에 같은 서명이 있는 메서드는 제외한다.
  - 반환 우주는 `load` 를 쓰지 말고 별도 수집기로 **실물 메서드 ∪ 선언 메서드**(합집합 · 교체 아님)를 모은다.

### M2 [major] 반환 해소 불능 정책 미정 · 중첩 중계 미처리 — 무력하거나 거짓 확정이다

- **근거**
  - 설계 §1.2-4 «반환 주석 해소가 불능이면 → 후보»의 범위가 없다.
    - 우주 전체 기준이면: 실저장소 포트에는 해소 불능 반환(`Iterator[...]`·`Callable`·`Annotated`·import 없는 `Optional`, `resolve` `:1618-1629`)이 거의 항상 있다. S-2 는 확정을 한 번도 내지 못한다.
    - 메서드 기준이면: `Iterator[FooIn]` 으로 반환되는 `_in` 의 중계가 거짓 확정된다.
  - 중첩 중계를 못 본다. `search() -> ResultPageIn`(필드 `items: tuple[ItemIn, ...]`) → `detail(item: ItemIn)` 은 G-2 문면상 적법한 중계다. 그런데 반환 신원 집합에 `ItemIn` 이 없으므로 확정이 된다.
- **수정 제안**
  - 반환 해소에서 `resolve(..., referenced_names=names)`(`:1603-1605`·`:1642-1643`)가 모은 **이름**을 «잠재 반환 이름» U 로 둔다.
  - 판정 순서는 셋이다.
    1. 인자 `_in` 신원 ∈ 반환 신원 R → 무
    2. 그 클래스 이름 ∈ U → 후보
    3. 그 밖 → 확정
  - R 은 반환 신원 중 `_in` 모듈 클래스의 필드 주석을 따라 닫는다. `check_declarations` #202 의 `walk`(`:1762-1782`)와 같은 방문 집합 방식이다.

### M3 [major] S-1 의 I 가 «기준선에 없던 경로»뿐이다 — F1 과 다르고, 수정·삭제 유입과 복수 머지 순서가 빠졌다

- **근거**
  - 설계식은 `… ∧ p ∉ 기준선 트리` 이다. registry F1(`registry_gate.py:598-601`)에는 이 절이 없다. «F1 앞 절과 같다»는 서술이 틀렸다.
  - 결과 1 — 수정 경로: main 이 **이미 있던 모듈**을 바꾸거나 거기에 심볼을 더한 경우, 사본은 기준선판을 갖는다. 이어지는 문제:
    - 그 모듈을 소비하는 boundary-imports ⑶ 이 거짓 결손(«심볼 미정의»)이 된다.
    - update 렌더(`_render_service_update` `:1329-`)가 낡은 본문 위에 합성된다.
    - `_DeclarationTypes` 가 낡은 표면으로 해소한다.
  - 결과 2 — 삭제 경로: main 이 **지운** 기준선 경로는 사본에 남는다. 그 경로를 `add` 하는 명세는 «add 충돌(실존)» 형식 red 가 된다.
  - 복수 참여 머지가 같은 p 를 다른 내용으로 들여오면 어느 blob 을 쓸지 정의가 없다. registry 는 `== head_blobs[p]` 로 유일해지지만 S-1 식에는 HEAD 절이 없다.
- **수정 제안**
  - I 를 참여 머지의 «verbatim incoming 변경 전부»(추가·수정·삭제)로 정의한다.
  - 경로마다 **사슬 순서상 그 경로를 마지막으로 바꾼 참여 머지** M* 를 고른다(blob(M*^1:p) ≠ blob(M*:p)).
    - blob(M*:p) = blob(M*^2:p) 이면 I 에 넣는다. M*:p 가 부재면 삭제로 반영한다.
    - 아니면(충돌 해소분) 제외한다.
  - 계산은 머지당 `git diff-tree -r -z --no-renames M^1 M` 과 `… M^2 M` 의 차집합이다(아래 §5).
  - 형식 검사의 실존 판정은 «기준선 ⊕ I» 의 실존으로 바꾼다. 수정은 실존 무변이고, 삭제는 부재가 된다.

### M4 [major] S-4 fail-closed 의 전제 «배포 시점 진행 중 레인 0»이 지금 거짓이다

- **근거**
  - 워크트리 `lane-8-B-9` 에 `20260926-2053-showcase-server`(pregate-report 있음)가 있다. `lane-5-1-4` 에 `20260926-2242-carried-request-lifetime` 이 있다. 두 디렉터리 모두 09-26 20:55 · 22:43 에 갱신됐다.
  - `git diff dddjango--v2.18.4 HEAD -- dddjango/scripts/*.py *.json` 에 3파일이 있다(`check-transaction-boundary.py` 57행 · `rulepack.json` · `pregate_symbol_kinds.json`). 이번 배포로 digest 가 바뀌는 것이 확정이다.
  - 진행 중 레인의 G2 `--check-report` 결과: 구판 헤더 → 불비 → `--base <G1>` 재발화. 그때 새 검사기(F4-20)와 S-2 가 새 red 를 내면, Coordinator 규범(«`--base` 재발화의 red 도 반송 사유» `dddjango.md:102`)상 **Phase 2 중 architect 반송**이 된다. 명세는 바뀌지 않았는데도 그렇다.
  - 현장 실측의 «싼 보험» 평가(툴체인 교체 5/79 · 실해 0)는 이 반송 비용을 넣지 않았다.
- **수정 제안(택일 또는 병행)**
  - ⓐ `make release` 절차에 «G1 뒤 · G2 전 레인 0 확인» 단계를 둔다. 대상 저장소의 `.dddjango/*/` 중 pregate-report 는 있고 G2 승인 흔적이 없는 폴더를 센다. 이것을 문서에 둔다.
  - ⓑ Coordinator 문면에 규칙 1행을 둔다. «툴체인 교체로 인한 재발화에서 새로 생긴 red(명세 불변)는 반송이 아니라 STOP(발주자 판정)».
  - ⓒ 배포를 두 레인 착륙 뒤로 미룬다.
  - fail-closed 자체는 유지할 가치가 있다. 다만 설계 §4.1 의 «부당 차단 없음» 서술은 고쳐야 한다.

### m1 [minor] S-1 «∃ 승인 머지 M»에서 «참여» 한정이 빠졌다

- 진단은 «∃ 참여 M»이었는데 설계 v1 은 «승인 머지 M»이다.
- `load_approved_merges` 는 기준선 이전 머지도 `position=None` 으로 **반환한다**(`anchor_diff.py:312-314`).
- 그런 머지를 거르지 않으면, 기준선 전에 이미 지워진 경로(p ∉ 기준선)가 유입으로 되살아난다.
- `m.participates`(`anchor_diff.py:217-218`)로 거른다. registry 도 같다(`registry_gate.py:548-549`).

### m2 [minor] S-1 재료 I/O 의 fail-closed 와 파일 모드

- 목록 파일 부재는 `path.read_text` 의 `OSError` 라서 `AnchorDiffUsage` 가 아니다. 그대로 두면 트레이스백이 난다.
  - registry 는 사전 `is_file` 로 막는다(`registry_gate.py:737-740`).
  - 설계는 «실패 시 exit 1(사유 인용)»이므로 `(AnchorDiffUsage, OSError)` 를 잡아 `실행 불능`으로 낸다.
- `registry_gate._tree_blobs` 는 두 문제가 있다.
  - 실패하면 `{}` 를 반환한다(`:498-499` — fail-open).
  - 모드를 버린다. symlink(120000)가 일반 파일로 써지고 gitlink 는 조용히 빠진다.
  - 재사용하지 말고 `diff-tree` 출력의 모드·blob 으로 쓴다. 120000 은 symlink, 160000 은 건너뛰고 병기한다. git 실패는 `RunError` 로 한다.
- `anchor_diff.run_git` 는 `core.hooksPath=` 억제가 없다. 읽기 명령뿐이라 훅은 안 돈다. 그러나 모듈 docstring «모든 git 호출은 … 훅 억제»(`design_pregate.py:17-18`)와는 어긋나므로 문면을 조정한다.

### m3 [minor] S-1 형식 검사의 틈 — `empty ∈ I` · 승격 형태

- 설계는 «add 가 I 에 들면 충돌»만 적었다.
- `empty ∈ I` 는 형식 검사를 통과한다. 그다음 `lift_realized_adds` 가 이것을 «기실현 empty»로 걷고 기록한다(`:1233-1235` — `in_baseline` 부재 ∧ 사본 실존). 오기재다. `empty` 도 add 와 같이 충돌로 세운다.
- `_promoted_form(copy, path)`(`:2644`)는 I 를 쓰기 전의 사본을 본다. 유입으로 들어온 승격 폴더는 «update 대상 부재»가 된다.
  - 순서를 «in_baseline 계산 → I 쓰기 → 형식 검사(inflow 집합 인자)»로 한다. 형식 검사는 사본을 `_promoted_form` 에서만 읽는다.
- `_error_kinds`(`:2664-2670`)는 «add 충돌(승인 유입 실존)»을 «add 충돌»로 합산한다. 요약의 종류를 구별하려면 접두를 `승인 유입 add 충돌:` 로 한다.

### m4 [minor] S-1 — 기준선이 first-parent 사슬 밖이면 목록 파일이 있는 한 언제나 exit 1

- `first_parent_chain` 이 None 이면 바로 `AnchorDiffUsage` 다(`anchor_diff.py:283-288`). 해당하는 경우:
  - 우회 기준선 M^2
  - 리베이스된 레인
  - 다른 가지에서 잡은 G1 기준선
- G-1 은 «목록이 있으면 동반»을 의무로 둔다. 그래서 이 레인들은 pre-gate 를 한 번도 못 돌린다. 우회 봉쇄로는 옳다.
- 다만 오류 문면에 처방 한 줄이 필요하다. «기준선이 레인 first-parent 사슬 밖 — 우회 기준선이면 G1 기준선으로 · 리베이스면 STOP».

### m5 [minor] 헤더 · stdout · `요약:` 행 형식 제약(S-1 · S-3 · S-4 공통)

- 새 헤더 행이 피해야 할 형식:
  - `- 기준선 SHA:`·`- 판정:` 로 시작하면 안 된다. `check_report` 가 **첫** 일치 행을 쓴다(`:2717-2718`).
  - 행 머리에 `` `<12hex>` `` 를 두면 안 된다. 소절에 섞이면 `_REPORT_ID_RE`(`:2678`)와 러너 `_FORECAST_RULE_RE`(`pregate_fixture_run.py:99`)가 예보 항목으로 센다.
- `기준선 SHA` 행에 머지 SHA 40자를 백틱으로 실어서도 안 된다. `_REPORT_BASE_RE` 가 첫 일치를 쓰므로 순서에 기대게 된다. 별도 행 `- 승인 유입: N경로 · 머지 <sha12>,…` 로 둔다.
- 예보 실행의 `요약:` 행 제약: 러너가 부분 문자열로 단언한다.
  - `요약: 귀속 0건 · 실존 결손 0건`(`:659`)
  - `요약: 실체화 0 · 실존 결손 1건`(`:686`)
  - 그래서 추가 토큰은 **행 끝**에만 붙인다.
- check-report `요약:` 행 제약:
  - `_SUMMARY_CHECK_RE`(`:699`)는 `요약: check-report <상태> · 블록 해시 X=Y` 접두를 요구한다.
  - 현장 파서(실측 문서 §1.2)는 `블록 해시 X=Y · 마지막 판정` 인접을 요구한다.
  - 그래서 digest 는 행 끝(`기준선 …` 뒤)에 붙인다.
- G2 배너의 Coordinator 판독은 LLM 이라 순서에 덜 민감하다. 그래도 기계 소비자 둘이 위 순서를 전제한다.

### m6 [minor] S-1b `--expect-base` 세부

- 입력 검증: 7~40 hex 만 받는다. check-report 는 git 0회라 ref 이름을 풀 수 없다. 나머지는 exit 1(사용 오류)로 한다.
- 비교는 `report_full.startswith(expected)` 로 한다.
- `--check-report` 없이 주면 사용 오류로 한다.
- 기대값의 출처: Coordinator ② 의 정의(«G1 배너 직전 최종 실행의 pregate-report 헤더 기준선»)는 절이 쌓인 리포트에서 다시 찾아야 한다.
  - 우회 절을 잘못 집으면 S-1b 가 무력해진다.
  - G1 승인 때 `<산출물 폴더>/` 에 기준선 1행 기록을 두는 것을 권한다(`build_anchor` 와 별개 — R-3434).
- 발주자 승인 기준선 이동(graph-slots D21)을 위한 문면 경로도 필요하다. «승인된 이동이면 기대값을 이동 SHA 로 갱신 · 근거 병기».

### m7 [minor] S-3 가 닫지 못하는 잔여 — 골격 가드는 앵커 커밋 기준이다

- 신규 BC 판정은 `git ls-tree HEAD application/<bc>` on **사본 앵커**다(`:1896-1900`).
- 기준선 = HEAD 일 때(첫 슬라이스 미커밋 WIP) 계획 밖 WIP 파일(`test/__init__.py` 등)은 오버레이로 L 에 실린다. 그러면 같은 오판이 난다.
  - 계획 add 만 `lift_realized_adds` 가 걷는다(`:1233`).
  - S-3 은 기준선 ≠ HEAD 만 다룬다. «규약 준수 실행과 같다»는 주장은 기준선 ≠ HEAD 에서만 참이다.
- 권고: 신규 BC 판정을 **기준선 트리**(오버레이 전 사본 · `in_baseline` 계산 시점)로 옮긴다.
  - `materialize_skeleton` 은 없는 칸만 만든다(`:1188-1196` — 파일은 `if not tgt.exists()`). 부분 실존 BC 에서도 안전하다.
  - 판정은 E1~E4 · E2′ 와 같다. 오버레이 판정이 달라지지 않고 골격 칸만 N 에 더해지기 때문이다. 이 불변을 E2 변형 픽스처로 고정해야 한다.

### m8 [minor] S-3 은 «보고 차이뿐»이 아니다 · 문면 3곳이 거짓이 된다

- 판정이 바뀌는 경로:
  - ⓐ WIP 에서 지운 `remove` 대상
    - 종전: 오버레이가 먼저 지운다(`:1145-1147`). → materialize 가 «remove(실존 없음)» 미시뮬레이션으로 처리한다(`:1860-1861`). → 제거 효과가 L 에 숨는다.
    - S-3 뒤: 실제로 제거된다. 효과가 N∖L 로 드러난다.
  - ⓑ WIP 에 이미 구현된 update OHS 함수
    - 종전: 바인딩 충돌 «새 함수 없음»으로 실체화 0 이다.
    - S-3 뒤: 스텁 함수가 합성되고 S1 보고 대상이 된다.
  - ⓒ `deferred(…; until Sn)` 계약 실존 결손
    - WIP 의 Sn 산출이 더는 사본에 없다. 재발화에서 소멸하지 않는다.
- 셋 모두 «규약 준수 실행»과는 같다. 그러나 설계 문장 «판정 동일»은 틀렸다.
- 거짓이 되는 문면:
  - `dddjango.md:102` «증거는 조건 충족 시점 재실행에서의 소멸이다(dirty overlay·기준선 갱신이 자동 반영)»
  - Codex `SKILL.md:121` 동문
  - `design-architect.md:92` «격리 사본(기준선 + dirty overlay + 이 명세의 add)»
- 앞의 둘은 재발화 판형(기준선 ≠ HEAD)에서 거짓이다. graph-owned 개정 대상에 넣는다. 설계 §3.1 «Coordinator 문면 고치지 않는다»를 정정한다.

### m9 [minor] S-3 구현 세부

- N 계수는 오버레이와 같은 호출(`status --porcelain=v1 -z --untracked-files=all` · `:1120-1121`)로 센다.
  - 설계의 `git status --porcelain`(기본 untracked=normal)은 미추적 폴더를 1행으로 접는다. h1 의 23개 `__init__.py` 가 폴더 수로 줄어든다.
  - rename 은 토큰 2개다.
- HEAD 해석은 `rev-parse --verify HEAD^{commit}` 로 한다.
  - 분리 HEAD 와 연결 워크트리(워크트리별 HEAD)에서 정확하다. 오버레이의 `git status` 도 같은 워크트리 기준이다.
  - 미탄생 HEAD 는 실패한다. `RunError` 로 할지 «≠ 취급»으로 할지 정한다.
- 판정 이후 `in_head`(`:2894`)의 `HEAD:<p>` 와 같은 HEAD 를 쓰도록 한 번만 해석해 재사용한다.
- N = 0 이면 «생략» 행 대신 종전 «dirty overlay 0건»을 유지할지 정한다. E1·E1′ stdout 이 바뀌지만 단언은 무영향이다(`:566`·`:627`).

### m10 [minor] S-3b 경로 매핑과 범위

- 결손 대상은 **모듈**(점 경로)이다. HEAD 조회는 세 후보를 다 봐야 한다.
  - `<rel>.py`
  - `<rel>/__init__.py`
  - 승격 형태 `<rel>/<stem>.py`
- `check_import_existence` 는 사본만 보는 순수 함수다(`:2267-`). 조회는 `main` 에서 결손 목록을 후처리해 detail 에 덧붙인다. 안정 ID 는 detail 과 무관하므로 불변이다.
- ⑶(모듈은 있으나 심볼은 HEAD 판에만 있음)은 이 안내로 안 잡힌다. 범위 밖이라면 문면에 적는다.
- S-1 과 겹치는 경우: 참여 머지 유입이면 이미 사본에 있다. 목록에 없는 머지 경유면 «승인 머지 유입이면 …» 안내가 발주자 목록 편집을 부추길 수 있다. «발주자 목록에 없는 머지 — STOP» 갈래를 분리한다.

### m11 [minor] S-4 가 기존 기대를 바꾼다 — 설계의 «기존 기대 무변»은 틀렸다

- `--block-hash` 둘째 행은 `pregate_fixture_run.py:255` 의 **완전 일치** 단언(`cli.stdout.strip() != f"블록 해시 {h1}"`)을 깬다. 이 단언을 개정하고 사유를 적는다. Codex `SKILL.md` 의 캐시 skip 문면도 같이 고친다.
- `check_report(spec_text, report_text)` 에 필수 인자를 더하면 호출부가 깨진다.
  - `pregate_fixture_run.py:925-927`
  - `pregate_field_report_smoke.py:563`·`:703-718`·`:794`·`:883`
  - 현재 digest 는 함수 안에서 계산하고(선택 인자로 주입 허용), `--expect-base` 도 선택 kwarg 로 둔다.
- 유닛 `head()`(`:885-889`)는 `write_report_stub` 으로 헤더를 만든다. 그래서 digest 가 자동으로 실린다. 기존 rcases(«사유 2» 포함)는 무변이다.
- «구판 헤더» e2e(`:830-831`)와 유닛(`:911`)은 블록 해시 토큰만 지운다. 기대 3·«최신성 증명 불가»가 유지된다. digest 를 블록 해시 **뒤**에 붙일 때만 그렇다.
- digest 판독 정규식은 `실행 트리 digest ([0-9a-f]{16})` 로 base_line 에서만 찾는다. registry 판은 `(N파일)` 을 붙이므로, 같은 문면을 복제하면 정규식이 그것을 허용해야 한다.
- `_tree_digest` 의 `read_bytes` `OSError` 는 미포착이다(`registry_gate.py:233`). check-report 는 트레이스백 대신 exit 1 로 한다.

### m12 [minor] G-2 · S-2 문면과 검사기 술어의 차이

- #573 은 `port/<capability>/` 자료에만 적용된다. `_check_capability_folder` → `_check_port_data`(`check-port-adapter-pairing.py:241-242`)다. `domain_bypass_query` 는 건너뛴다(`:189`). framework 자료는 대상이 아니다.
  - G-2 의 «(#573·#574)»를 세 위치 전부에 걸면 과장이다.
  - «방향 명명은 세 위치 공통 규약 · #573 기계 판정은 port/<capability>/ 만»으로 적는다.
- `domain_bypass_query` 는 `port/` 아래다(houserules 트리 51~56행 = `discipline-houserules/references/final.md:95-100`). 경로 표기는 `port/domain_bypass_query/<capability>/` 로 한다.
- #574 검사기는 좁다. S-2 «확정»은 G2 검사기보다 엄격하다(의도라면 문면에 적는다).
  - 부분 문자열 `"port" in m`(`:1349`)이라 BC 이름 `report`·`support`·`import…` 도 맞는다. S-2 가 «같은 술어»를 주장하려면 부분 문자열 의미 그대로 쓰고 이 특이를 사각에 적는다.
  - `from <…_in> import X` 뒤 `X(...)` 만 잡는다(`:1352-1356`). `module.X()`·classmethod 생성자·재수출 경유 import 는 검사기가 못 본다.
  - 스캔 대상은 «유스케이스»가 아니라 application_layer 전 파일이다.
- BC 간: 반환 우주가 전 BC 라서 다른 BC 포트가 반환한 `_in` 도 중계 근거가 된다. 그 BC 의 포트를 부르면 격리 위반이므로 중계 근거가 될 수 없다. 우주를 **인자 쪽 포트와 같은 BC + framework** 로 좁힌다.
- 교정 안내: `_out.py` 에 `…In` 클래스는 #573(`:296-298`)에 걸린다. S-2 메시지와 G-2 는 «파일 `<data>_out.py` · 클래스 접미 `…Out`(또는 무접미)» 둘 다를 요구해야 한다. 그렇지 않으면 #574 를 #573 으로 바꾸는 반송이 한 번 더 난다.

### m13 [minor] S-2 후보 소음 · 우주 열거의 결정성

- 설계 규칙 4(«매개변수 해소 불능 → 후보»)를 그대로 두면 소음이 된다. h1 의 `Path`·`LoadedServiceOntology`, UoW 포트의 `callback: Callable[[], None]`, `Generic[T]` 가 전부 #574 후보가 된다.
- 후보는 «참조 이름이 `…In` 접미이거나, 폴백이 `_in` 모듈을 가리키는데 유일하지 않음»으로 좁힌다.
- 우주 열거는 셋을 합친다. 합친 뒤 `sorted(set(...))` 로 순서를 정한다.
  - `os.walk(copy, followlinks=False)`(symlink 파일 제외 — archive 사본의 symlink 는 사본 밖을 가리킬 수 있다)
  - 계약 경로 정규식 `^application/[^/]+/application_layer/port/(?:domain_bypass_query/)?[^/]+/[^/]+_(?:port|query)\.py$` · `^framework/(?:broker/(?:internal|external)|[^/]+)/[^/]+_port\.py$`
  - 계획 add/update 칸
- 신원은 `(모듈, 이름)` 집합으로 둔다.
- 스텁 본문은 무관하다. 주석만 본다. `_class_stub` 의 기본 `-> object`(`:991`)는 원시값으로 소거된다.
- 출력은 file-plan 순서 → 클래스 → 메서드 선언 순서다. 기존 `add()` 중복 제거(`:1704-1707`)와 `_declaration_lines` 의 `(rule, path)` 묶음이 안정 ID 를 정한다.
- 우주는 인자 쪽에 `_in` 후보가 있을 때만 수집한다(지연 계산). 모든 명세에 전 포트 파싱 비용을 물리지 않는다.

### m14 [minor] 구현 순서 · 커밋 단위의 함정

- 네 수리가 모두 같은 자리를 건드린다.
  - `main()` `:2881-2913`
  - `write_report`/`write_report_stub` 헤더(`:2533-2600`)
  - `BLIND_SPOTS`(S2·S7·S8 · `:2471-2499`)
  - 결함별로 병렬 구현하면 충돌한다. 설계의 순서 F4-22 → F4-21 → F4-23 은 헤더 형식을 세 번 연다.
- 권고 순서: S-4(스탬프·check-report·러너 `:255` 개정) → S-3(+m7·m9) → S-1·S-1b(+m1~m4) → S-3b → S-2(+B1 폴백·M1·M2) → graph-owned 일괄(G-1·G-2·G-4·m8 문면)
  - 한 번의 render → LEDGER → rulepack 으로 끝낸다.
  - `rulepack.json` 재생성은 digest 를 바꾼다. 무해하지만 digest 픽스처는 같은 실행 안에서 만들고 대조해야 한다.
- 커밋을 나누면 커밋마다 다음이 들어가야 한다. `make verify` 가 커밋마다 green 이어야 하기 때문이다.
  - `codex-dddjango/skills/dddjango/scripts/design_pregate.py` byte 미러
  - 러너 기대 개정
- `design_pregate.py` 가 `anchor_diff` 를 새로 import 하면 최상단 `try/except ImportError`(`:135-143`) 안에 둔다.
- 사용 문면도 같은 커밋에서 갱신한다.
  - docstring «사용:»(`:88-90`)
  - exit 규약(`:91-95` — `--approved-merge-file` 실패 exit 1 · `--expect-base` 불비 3)
- S-1 픽스처를 S-3 전에 쓰면, dirty 상태 기대값이 S-3 뒤에 바뀐다. 순서를 지킨다.

## 3. 기존 픽스처 기대값 영향표

| 위치 | 단언 | 영향 | 근거 |
|---|---|---|---|
| `pregate_fixture_run.py:255` | `--block-hash` stdout == `블록 해시 <h>` | **깨짐**(S-4 둘째 행) | m11 |
| `:699` `_SUMMARY_CHECK_RE` | 요약 접두 | digest 를 행 끝에 붙이면 무변 | m5 |
| `:659`·`:671`·`:686` | 예보 `요약:` 부분 문자열 | S-1 토큰을 행 끝에 붙이면 무변 | m5 |
| mid E1·E1′(`:557-573`·`:612-634`) | exit 0/2 · already-built 0 · 같은 ID | 무변(clean · 기준선 ≠ HEAD → N=0 «생략») · stdout 1행 추가 | m9 |
| mid E2·E2′·E3·E4 | 기준선 = HEAD 또는 미지정 | 무변 | — |
| `:636` mid 헤더 6 | 절 계수 | E5 를 별도 리포트에 쓰면 무변 | 설계 §5 |
| `:841` BLIND_SPOTS 9 | 번호 S1~S9 | 무변(문면만) | — |
| enforce 유닛 `baseline_form_errors` 5 인자 | 서명 | inflow 를 선택 kwarg 로 두면 무변 | m3 |
| checkreport 묶음 · 유닛 rcases | exit·needle·«사유 2» | 무변(헤더를 실행기가 만들고 digest 는 현재 값) | m11 |
| `pregate_field_report_smoke.py` `check_declarations` 완전 일치 목록 | `[('#197', False)]` 등 | 현 픽스처는 포트 인자 무주석이라 무변. 규칙 4 를 좁히지 않으면 주석 달린 UoW 포트에서 `('#574', False)` 가 섞일 위험이 있다 | m13 |
| modes 12조합(`:935-969`) | `--base HEAD` | 무변 | — |

## 4. S-2 반환 신원 수집의 결정적 구현

위 B1·M1·M2·m13 을 합친 절차다.

1. **인자 대상**: file-plan 순서로 add/update 계약 칸을 돈다. `entry.declarations` 의 클래스 → 선언 메서드 순서로 간다. 매개변수(posonly·args·kwonly·vararg·kwarg, 선두 `self`/`cls` 제외)의 주석을 본다.
   - 해소는 `types.resolve(module, ann, referenced_names=names)` 로 한다.
   - 실패하면 B1 폴백(같은 능력 폴더 · 유일)을 적용한다.
2. **`_in` 신원 선별**: `m.endswith("_in") and ("port" in m or "framework" in m)` — 검사기 문자열 그대로다(m12).
3. **반환 우주 R · 잠재 이름 U**: m13 열거 순서대로 같은 BC 계약 모듈과 framework 계약 모듈을 모은다. 메서드 반환은 **실물 ∪ 선언**이다(M1). 해소와 폴백을 거친 신원이 R 이고, 미해소 참조 이름이 U 다.
   - R 은 `_in` 클래스 필드 주석을 따라 닫는다(M2 · 방문 집합 · 순환 차단).
4. **판정**: (m, n) ∈ R → 무 · n ∈ U → 후보 · 그 밖 → 확정.
   - 인자 해소 불능은 `…In` 참조나 비유일 폴백일 때만 후보이고, 그 밖은 무보고다.
5. **출력**: `DeclarationFinding("#574", path, f"{Class}.{method}", detail, confirmed)` 를 기존 `add()` 로 중복 제거한다. detail 은 심볼 이름을 정렬해 쓴다.

## 5. S-1 의 git 호출 · 비용 · 비조상 거동

- **호출**
  - `rev-parse --verify HEAD^{commit}` 1회.
  - `load_approved_merges`:
    - `log --first-parent` 1회. HEAD 부터 전 이력을 캡처하므로 비용은 이력 길이에 비례하지만 수 MB 이하다.
    - 줄마다 `rev-parse`·`show`·`name-rev`·`for-each-ref --contains`·`merge-base --is-ancestor` 5회. `for-each-ref --contains` 는 ref 가 많은 저장소(herdr 워크트리 브랜치)에서 가장 느리다.
  - I 계산: 참여 머지당 `diff-tree -r -z --no-renames M^1 M` · `… M^2 M` 2회. 출력은 유입 크기에 비례한다.
  - 사본 쓰기: 머지당 `git archive M -- <경로…>` 1회(모드·symlink 보존). 또는 `cat-file --batch` 1회 + diff-tree 모드.
  - 전형(머지 1~3)은 15~25 회로 1초 이내다.
- **비조상 거동**
  - ⓐ 기준선이 HEAD first-parent 사슬 밖이면(우회 M^2 · 리베이스 · 다른 가지) `AnchorDiffUsage` → exit 1 이다. 목록이 비어 있어도 그렇다(m4).
  - ⓑ 목록 머지가 기준선의 조상이면 `position=None` 이다. 반드시 제외한다(m1).
  - ⓒ 목록 머지가 사슬 밖이고 기준선의 조상도 아니면 exit 1 이다.
  - ⓓ 기준선 = HEAD(Phase 1 기본에 목록 동반)이면 사슬이 공집합이다. 이력 안의 머지는 전부 불참이 되어 I = ∅ · 무해하다.
- registry 는 같은 목록을 `build_anchor` 기준으로, pre-gate 는 G1 기준선 기준으로 검증한다. 같은 파일이 한쪽에서만 불참일 수 있다. 오류는 아니지만 헤더에 불참 머지 수를 병기한다.

## 6. S-3 의 HEAD 의존 지점

- 비교 대상은 `rev-parse --verify HEAD^{commit}` 와 `base_sha`(`:2839-2845` — 이미 `^{commit}` 으로 벗김)다.
  - 주석 태그 기준선도 같은 커밋이면 «같음»이다.
- 분리 HEAD: 문제없다.
- 연결 워크트리: `git -C <워크트리>` 의 HEAD 는 워크트리별이다. `_overlay_dirty` 의 `git status` 도 같은 기준이므로 정합한다.
- 현장은 `.dddjango/` 를 추적하므로, Coordinator 산출물 커밋만으로도 HEAD ≠ 기준선이 된다. 그 결과:
  - Phase 2 재발화는 사실상 항상 «생략» 경로를 탄다.
  - `lift_realized_adds` 는 현장에서 거의 쓰이지 않게 된다. 보고의 already-built «기실현»이 사라진다.
  - 설계 의도와 합치하지만, 릴리즈 노트에 적는다.
- 미탄생 HEAD · `rev-parse` 실패 처리를 정한다(m9).
