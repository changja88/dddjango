# 검토 H — 로드맵 3 설계 v2 · 구현 계획 집행 가능성 (2026-09-27)

- 대상: `step3-pregate-design-v2.md`(§0 순서 · §1~§5 설계 · §6 graph 일괄 · §7 검증 · §9 처분표).
- 대조: 앞 검토 `review-E-step3-code.md` · `review-F-step3-norms.md` · 진단 두 편. 코드는 `design_pregate.py`(HEAD판 + 작업 트리 진행분 diff) · `anchor_diff.py` · `pregate_fixture_run.py` · `pregate_field_report_smoke.py` · Coordinator · design-architect · houserules final · Codex 대응 · `docs/DEVELOPMENT.md` · `ontology/`(rules·wiring·ISSUED·target-counts).
- 실행: scratch `…/scratchpad/rv3c/` 에서만 했다. `probe_s2_v2.py` 는 E 의 probe 를 넓혀 v2 §5 의 S-2(잎 단위 같은 능력 폴더 폴백 · 선언 메서드 한정 · 반환 우주 = 같은 BC + framework · 실물 ∪ 선언 · `_in` 필드 닫힘)만 흉내 낸다. 현장은 `git log`·`git show`·`git ls-tree`·`git archive`(stdout 을 scratch 로 풀기)만 썼다. 저장소·현장 쓰기 0 · 파일 수정은 이 문서 하나 · Serena·Graphify 미사용.

## 0. 결론

| 구분 | 건수 | 요지 |
|---|---|---|
| E·F blocker 3 | 해소 3 | S-2 폴백은 현장에서 실제로 확정을 낸다(§2 — 복구 가능한 5건 전부 확정 · 최신 명세 78건 거짓 확정 0) · G-2 는 인자 절반으로 줄였다 |
| E·F major 11 | 해소 7 · **부분 4** · 미해소 0 | 부분 = E M2(U 수집 방식) · E M4(상시 규칙 없음) · F M-1(수정 모드·Phase 1 에서 값·의무가 어긋남) · F M-3(«이번 실행» 경계를 기계로 가를 수 없음) |
| 새 발견 | major 5 · minor 9 | H-M1 §7 현장 재생 절차·목표 집행 불가 · H-M2 `pre-gate 기준선` 값의 빈자리 · H-M3 한정 확장 경계 판별 불가 · H-M4 §6 규범 매핑·기계 절차 부재 · H-M5 §6 문면 누락 |

## 1. E·F blocker·major 해소표

판정 기준: v2 본문이 발견의 근거 경로를 실제로 닫는가. 처분표의 «수용»은 보지 않았다.

| 발견 | v2 본문 | 판정 | 남은 것 |
|---|---|---|---|
| E B1 · F B-1 S-2 해소 불능 | §5-2 같은 능력 폴더·유일 폴백 · §7 현장 재생 | **해소** | probe 로 확인했다(§2). 단 폴백을 «주석 전체가 실패하면»으로 걸면 8건 중 6건(`tuple[XIn, ...]`)을 놓친다 → H-m2. §7 재생 절차 자체는 H-M1 |
| F B-2 반환 명명 충돌 | §6 G-2 인자 절반만 · §8 결정 7 | **해소** | 인자 절반 문안은 file_tree(bypass 조건 = `_out`)·현장(인자 `_in` 1 = 중계)과 충돌하지 않는다. S-2 의 교정 안내(`_out`)는 결정 7 의 (가)·(나) 어느 쪽과도 맞다 |
| E M1 · F m-4 부분 선언·legacy | §5-1 선언 메서드만 · update 는 실물 같은 서명 제외 · §5-4 실물 ∪ 선언 | **해소** | «같은 서명»의 정규화가 없다(명세 `params` 문자열 대 실물 AST — 공백·기본값·`*` 차이로 legacy 가 되살아난다) → H-m9 |
| E M2 · F m-2 반환 해소 불능 · 중계 | §5-4 U = 미해소 참조 이름 · R `_in` 필드 닫힘 | **부분** | 필드 닫힘은 된다. 그러나 U 를 `resolve(referenced_names=)` 로 모으면 지원 밖 컨테이너 머리(`Iterator`·`Generator`·`Annotated`·사용자 제네릭·import 없는 `Optional`)에서 slice 를 내려가지 않는다(HEAD판 `design_pregate.py:1618-1629` — 머리만 해소하고 `return [], issues`). E M2 의 원 사례 `Iterator[FooIn]` 반환 중계가 그대로 거짓 확정이다. **수정**: U 는 반환 주석의 `ast.walk` Name·Attribute 전수로 모은다. 현장 main 포트 반환 실측: `Iterator` 1 · `Generator` 2 · 사용자 제네릭 4 — 지금은 `…In` 을 감싼 곳이 0 이라 발화 0 |
| E M3 · F m-5 I 신규 경로만 | §3.1 추가·수정·삭제 · 마지막 참여 머지 · verbatim | **해소** | 작업 트리 진행분 `approved_inflow` 가 설계대로다. 가장자리 2건 → H-m6 |
| E M4 진행 중 레인 | §1 배포 절차(로드맵 9) · «부당 차단 없음» 삭제 | **부분** | 이번 배포는 로드맵 9(«G0~G2 사이 0»)가 막는다. 그러나 digest 가 생기면 **이후 모든 스크립트 변경 릴리즈**가 진행 중 레인의 G2 check-report 를 stale(툴체인)로 만든다(09-01~09-11 창에 13회 있었다). 상시 규칙이 없다 — `docs/DEVELOPMENT.md` §6 에 릴리즈 창 확인이 없고, E M4 ⓑ(«명세 불변 · 툴체인 교체 재발화의 새 red 는 반송이 아니라 STOP»)도 채택하지 않았다. **수정**: 둘 중 하나를 상시 문면으로 둔다(DEVELOPMENT §6 한 줄이 가장 싸다) |
| F M-1 expect-base 출처 | §3.2 실행 줄 `pre-gate 기준선` · `--base` 명시 절 있으면 의무 | **부분** | 출처는 고정됐다. 그러나 ① 수정 모드 G1′ 생략(새 실행)에서는 «마지막 예보 절»이 앞 실행 것이라 값이 수 주 전 기준선이 된다 ② 재사용 폴더의 Phase 1 check-report 에서는 옛 명시 절 때문에 «의무»가 서지만 값이 아직 없다 ③ 의무가 산문뿐이라 빠뜨리면 현장 치환 5회가 그대로다 → H-M2 |
| F M-2 발주 `--base` 지정 | §3.2 불수용 문장 · REQUEST_GUIDE §4 | **해소** | REQUEST_GUIDE 는 graph-owned 가 아니다(분류만 틀림 → H-m7) |
| F M-3 폴더 재사용 구판 헤더 | §1 한정 확장(이번 실행 예보 0 ∧ 명세 변경 0) | **부분** | 경계를 Coordinator 가 기계로 가를 수 없다. «명세 변경 0» 판별 수단도 없다. 수정 모드 절(193행)·G2 최신성 행(177행) 표기가 §6 에 명시되지 않았다 → H-M3 |
| F M-4 filtered 탈출 | §5-7 선언 확정 #574 는 S1·S2 filtered·ⓑ 불가 | **해소** | 대가로 도구 오탐의 출구가 없어졌다. §5-3 은 «부분 문자열 특이는 사각에 적는다»인데 그 사각은 인용이 금지된다(자기모순) → H-m3 |
| F M-5 S-3b 트리거·안내 | §4 blob 비교 · 세 경로 후보 · symbols 선언 · 타 BC 대가 | **해소** | 플래그를 이미 동반했는데 충돌 해소분이라 I 에서 빠진 경로에 «`--approved-merge-file`» 안내가 또 뜬다 → H-m6 에 합침 |
| F M-6 요약 재진술 6곳 | §6 «② 참조» 통일(Claude 116·190·205 · Codex 134·206·220) | **해소** | 6곳은 맞다. 재진술이 아닌 다른 누락은 H-M5 |
| F M-7 인용·wiring 과대 | §6 G-2 문안 인용 정정 · enforcedBy 두 검사기 | **해소** | 채번·배선 절차는 §6 에 없다 → H-M4 |

## 2. S-2 폴백 현장 재생 (읽기 전용 흉내)

방법: 각 실행의 G1 절 헤더(기준선 SHA · 블록 해시)를 파싱했다. `git log --all -- <run>/design-spec.md` 의 판마다 현재 `block_hash` 를 계산해 G1 해시와 같은 판을 찾았다. 사본 = `git archive <G1 기준선> -- application/<계획 BC…> framework` + add 스텁이다. 산출물: `rv3c/specs/*.md` · `rv3c/run1.out` · `rv3c/sweep.out`.

| 실행 | 쓴 명세 판 | G1 판과의 관계 | 대상 인자 | 결과 |
|---|---|---|---|---|
| ① catalog | `9ee721e` | 해시 `6cf8e2ffdfc3` 일치 | `RelationTablePort.load(query: RelationQueryIn)` | **확정**(폴백) |
| ② b5 | `feeac19`(S1 커밋) | G1 해시 `42bc2baba4a5` 판은 git 에 없다. 이 판은 Phase 2 재발화 절(143)의 해시다 · #574 교정(S3) 전 | `CustomerItemSupplyPort.supply(requests: tuple[CustomerItemSupplyIn, ...])` | **확정**(폴백 · 컨테이너 안) |
| ③ b7 | `f3ae82d`(S1 커밋) | G1 절 325 해시 `8f0e6cb99fb8` 판은 git 에 없다. 이 판은 Phase 1 마지막 HEAD 절(637)의 해시다 | `FortuneFailurePort.record_failure(failure: FortuneFailureIn)` | **확정**(폴백 불요 — 이 명세만 포트 파일 import 행이 있다) |
| ④ h1 | `a1e1635b` | 해시 `03eb9c96adea` 일치 | `run_select(triples: tuple[GraphTripleIn, ...])` · `fetch(arguments: UpstreamFetchArguments)` | **확정 2**(폴백) |
| ⑤ decisive | `819e4e0`(유일 판) | **G1 판 복구 불가**. 이 판은 S5 재발화 절(408 · `--base 70a16c09`)의 해시이고 교정 뒤 문면이다(«포트는 도메인 VO 를 받는다 · `ChartRequestIn` 을 두지 않는다» `design-spec.md:246`·`:263`) | 없음(`calculate_chart(snapshot: SajuInputSnapshot, window: AnnualWindow)`) | 무 — 이 판에서는 무가 정답이다 |
| ⑥ counter-room | `4b099e7` | 해시 `d32fd746c03e` 일치 | `split_counter`·`split_room`(transcript `SplitTranscriptEntryIn`) · `split_room`(record_summaries `RecordSummaryLineIn`) · `prepare`(live_requests `LiveEvidenceRequestIn`) | **확정 4**(폴백 · 전부 컨테이너 안) |

- **엄격 4건(①②③④)은 전부 확정**이다. 넓은 기준 6건 중 판을 구할 수 있는 5건도 전부 확정이다. U_ref(resolve 이름)와 U_walk(ast.walk) 판정 차이는 6건 모두 0 이었다. 폴백의 비유일 사례도 0 이었다.
- **음성 대조**: `.dddjango/` 78 실행의 현재 `design-spec.md` × 마지막 절 기준선에 같은 probe 를 돌렸다. 인자 `_in` 대상 0 · 확정 0 · 후보 0 · 오류 0 이었다. 한계가 둘 있다. 이것은 교정 뒤 판이다. 그리고 중계(`GlossaryTranslationIn`)를 선언한 명세가 없어서 음성 «무» 경로는 현장으로 검증되지 않았다(픽스처가 맡는다).
- 폴백이 필요했던 인자는 8건이다. 그중 6건이 `tuple[XIn, ...]` 안에 있다. 폴백은 `identity(local=True)` 미해소 분기(잎)에 걸어야 한다(H-m2).
- 빈도 실측 문서의 ⑤ 근거 `pregate-report.md:408` 은 G1 절이 아니라 S5 재발화 절이다. 정정 대상이다.

## 3. 새 발견

### H-M1 [major] §7 현장 재생의 절차와 목표를 그대로 집행할 수 없다

- **근거**
  - §7 은 «F4-22 6건의 수정 전 G1 판 명세를 `git show <커밋>:…/design-spec.md` 로 뽑는다 · 목표는 6건 모두 확정 또는 후보 · 미달이면 폴백을 고치고 다시 잰다»이다.
  - G1 해시와 같은 판이 git 에 있는 것은 3건(①④⑥)뿐이다(§2). ②③ 은 G1 뒤 판뿐이다.
  - ⑤ decisive 는 `design-spec.md` 커밋이 한 번(`819e4e0` · 교정 뒤)이다. `ChartRequestIn` 을 담은 G1 명세는 저장소 어디에도 없다. 그 판으로 재면 무가 정답이다.
  - 따라서 «6건 모두»는 도달할 수 없다. «미달이면 폴백을 고친다»를 문자대로 따르면, 정답인 무를 확정으로 바꾸려고 폴백을 넓히게 된다. 그러면 거짓 확정이 생기고, M-4 로 출구도 없다.
- **수정**
  - 재생 판 선택 규칙을 적는다. «G1 해시 일치판 · 없으면 결함 교정 전 최초 커밋판(판·절 번호 병기) · 교정 전 판이 없으면 재생 불가로 분모에서 뺀다».
  - 목표를 «재생 가능 5건 전부 확정 · 엄격 4건 확정»으로 고친다. 이 기준은 probe 로 이미 충족된다.
  - 음성 대조(78 실행 현재 명세 · 거짓 확정 0)를 §7 에 넣는다. F B-1 수정 3 의 요구였는데 v2 에서 빠졌다.
  - 재생은 S-2 구현 직후에 둔다(H-m8).

### H-M2 [major] `pre-gate 기준선`(§3.2)이 수정 모드·Phase 1·재사용 폴더에서 비거나 틀린다

- **근거**
  - 기록 시점은 «Phase 2 첫 파견 직전 · 값 = 마지막 예보 절 기준선»이다.
  - **수정 모드 G1′ 생략**(193행 — 설계 변경 없는 순수 구현 수정)에서는 이번 실행에 예보 절이 없다.
    - «마지막 예보 절»은 앞 실행의 절이 되고, 값은 수 주 전 G1 기준선이 된다.
    - 앞 실행 리포트가 없으면 값 자체가 없다.
    - 이 실행에서 Phase 2 반송으로 명세가 바뀌면 ② 재발화는 `--base <옛 기준선>` 이 된다. F M-3 이 적은 «막다른 길»(옛 트리 · 이번 실행 변경 전부 사본 밖)이 그대로 되살아난다.
  - **Phase 1 · 재사용 폴더**: «리포트에 `--base` 명시 절이 하나라도 있으면 `--expect-base` 는 의무»다. 새 실행의 G1 배너 check-report 에서 앞 실행의 명시 절 때문에 의무가 서는데, 값은 Phase 2 에서야 생긴다. 지킬 수 없는 의무다.
  - **순서**: G1 override(②/③)의 «dispatch 전 무조건 재실행»과 이 기록은 둘 다 «dispatch 전»이다. 기록이 먼저면 override 절 기준선이 빠진다. `.dddjango/` 는 추적 대상이라, 산출물 커밋만으로 HEAD 가 움직인다.
  - **집행**: 의무가 산문뿐이다. check-report 는 헤더의 `(--base <ref>)` 를 이미 읽을 수 있는데 강제하지 않는다. 플래그 누락은 현장 치환 5회와 같은 경로다.
  - 순수 리팩터 레인(슬라이스 0)은 G1′ 을 생략할 수 없고(193행 끝), Phase 1 에서 예보가 돈다. 그래서 값이 생긴다. 문제는 G1′ 생략 경로뿐이다.
- **수정**
  - 값 규칙을 적는다. «이번 실행에 예보 절이 있으면 그 마지막 절 기준선 · 없으면(G1′ 생략) Phase 2 첫 파견 직전 `git rev-parse HEAD`». 이것은 build_anchor 파일을 읽는 것이 아니다 — R-3434 무저촉.
  - 기록은 override 재실행 **뒤**에 한다.
  - 의무 범위는 «실행 줄에 `pre-gate 기준선` 이 있고 이번 실행 절 중 명시 `--base` 절이 있을 때»로 좁힌다.
  - check-report 가 «마지막 절이 명시 `--base` ∧ `--expect-base` 부재 → 불비»를 내게 하는 방안을 검토한다(기계 집행).

### H-M3 [major] §1 한정 확장의 «이번 실행» 경계를 Coordinator 가 가를 수 없다

- **근거**
  - 경계의 한쪽은 실행 줄 `실행 · G0 승인 <date +%Y%m%d-%H%M 값>`(`dddjango.md:85`)이다. 로컬 시각이고, 시간대가 없고, 분 단위다.
  - 다른 쪽은 예보 절 앵커 `## pre-gate 예보 — <UTC 초>`(`design_pregate.py` `_REPORT_SECTION_RE`)다.
  - KST 에서는 9시간 어긋난다. G0 뒤 9시간 안에 돈 이번 실행 절을 «이전»으로 읽을 수 있다.
  - «design-spec 변경이 0» 도 판별 수단이 없다. 지금 ③ 한정의 «이 세션에서»는 세션 기억에 기댄다. 재개 세션에서는 모른다.
  - 오판하면 두 방향으로 틀린다. check-report 를 불러 구판 헤더로 막히면 M-3 이 재현된다. 반대로 부르지 않아야 할 때 생략하면 G2 최신성 대조가 빠진다.
  - 수정 모드 193행(G1′ 생략 경로 — 이 한정의 실제 사용처)과 G2 최신성 177행(`미실행(구형 명세 · 변경 0)` 만 열거)을 고친다는 말이 §6 에 명시되지 않았다.
- **수정**
  - 판별을 기계 조건으로 적는다. «`--block-hash` 첫 행 = 마지막 예보 절 블록 해시(명세 기계 블록 불변) ∧ 마지막 예보 절이 이번 실행 경계 앞».
  - 경계는 G0 승인 때 `pregate-report.md` 에 경계 행 `- 실행 경계 — G0 승인 <UTC>` 를 append 해서 파일 안 위치로 가른다. 이 행은 `## pre-gate 예보` 문자열을 쓰지 않는다. 대안은 실행 줄 시각을 `date -u` 로 바꾸는 것이다.
  - 177행에 `미실행(명세 변경 0 · 앞 실행 예보)` 를 더한다. 193행에 «최신성 행 = 한정 · pre-gate 기준선 = H-M2 규칙»을 더한다. Codex(195·209행)도 같이 고친다.

### H-M4 [major] §6 에 규범 매핑과 기계 절차가 없다 — 표만으로는 집행할 수 없다

- **근거**
  - 선례 `plan-v2.md` 는 문장마다 «개정 17(revisionKind) · 신설 30(R-3470~R-3499) · 새 블록 · Codex 위치 목록 · 계수표»를 확정했다. 리뷰 C M-8·M-9 가 같은 종류의 빈칸을 major 로 잡았다.
  - v2 §6 은 문서별 «변경» 서술뿐이다.
  - **G-2 는 새 R-ID 여야 한다**. houserules §3 블록 b1 은 R-3221·R-3222 를 진술한다(`discipline-houserules-final.ttl:994`). R-3222 는 «명명 규약 전수는 이름 줄이 소유 · 매핑표 순서로 편입»이라는 소유 규범이고, `delegatedTo agent-discipline-reviewer` 다(`wiring/discipline-houserules-final.ttl:108`). G-2 는 다른 집행자(`c/design_pregate.py` · `c/check-port-adapter-pairing.py` — 둘 다 `wiring/registry.ttl` 에 Checker 로 실재한다)를 가진 Prohibition 이다. 그래서 R-3222 개정으로 담을 수 없다.
  - 필요한 것:
    - ISSUED `R-3500<TAB>2026-09-27<TAB>rules/discipline-houserules-final.ttl`
    - s011-3 새 블록(b3 · statesNorm R-3500)
    - Norm + Expression rev 1
    - 문서별 wiring 파일 1행
  - architect symbols 포인터가 `djr:restates` 인 블록인지, 규범인지도 정해야 한다.
  - Coordinator ②③ 블록(s006/b10)은 **R-3445 하나만** 진술한다(`command-dddjango.ttl:3746`). 그런데 새 의무가 여럿이다: `--approved-merge-file` 동반 · `--expect-base` 의무 · `pre-gate 기준선` 기록 · 발주 `--base` 불수용 · 한정 확장 · digest skip. 신설인지 R-3445 amendment 인지 결정이 없다. 102행 블록(R-3432~R-3436)의 filtered 금지 추가도 같다.
  - 절차 누락은 셋이다. 셋 다 `make verify` red 로 이어진다(기억 «규범 개정 실전 레시피» 4·5단).
    - `target-counts.json`(현재 Block 2926 · Expression 3699 · Norm/Work 3508)
    - q4 골든 `query_golden_check.py --emit`
    - **houserules final.md 소스 미러**: `workspace/reference/discipline-houserules/reference/final.md` 의 옛 §3 span 을 수동 교체한 뒤 `corpus_mirror_sync.py --write` 를 돌린다. 이것이 Codex `dddjango-discipline-houserules/references/final.md` 도 갱신한다. v1 에는 있었는데 v2 §0·§6 에서 빠졌다.
- **수정**: §6 을 plan-v2 형식의 매핑표로 바꾼다. 열은 «문장 · 블록 IRI · 신설/개정(R-ID·revisionKind) · wiring · Codex 행»이다. §0 6단을 «ttl 편집 → gate → render(3 doc) → LEDGER → target-counts → q4 → 소스 미러 교체 → corpus_mirror_sync → rulepack → Codex 의미 미러 → REQUEST_GUIDE byte 미러»로 편다.

### H-M5 [major] §6 이 빠뜨린 문면

재진술 6곳(F M-6)은 들어갔다. 아래는 들어가지 않았다. 모두 수정 뒤 두 문면이 서로 어긋나게 되는 자리다.

| # | 자리 | 왜 바뀌어야 하나 |
|---|---|---|
| ① | Coordinator **218행**(경계 — 실행 줄 기계 기록 «(시각·앵커·G2 승인)» 열거) · **85행** 추기 목록 · **122행** 6번 앵커 기록 절차 · **18행** 산출물 행 · Codex 232·105·140·72행 | `pre-gate 기준선` 추기가 열거 밖이면, 위임 실행에서 «`refactor-scope.md` 사후 개정 — 비위임»으로 읽혀 정지한다. §6 의 «실행 줄 기계 기록 목록»이 어느 행인지 특정되지 않았다 |
| ② | design-architect **90행** «태그의 뜻은 기준선 기준이다(… Phase 2 재발화 시 `--base` 기준선)» · Codex SKILL 84행 | S-1 뒤 형식 판정은 «기준선 ⊕ 승인 유입»이다(유입 추가 경로의 add · 유입 삭제 경로의 update/remove 는 형식 red). architect 계약이 옛 뜻이면 반송이 되풀이된다 |
| ③ | design-architect **87행** 기계 채널 문단(선언 #197·#202 열거 · «선언 확정은 architect·리뷰어가 처분» — `agent-design-architect.ttl:2191` 블록) · Codex 81행 | #574 선언 확정의 처분 주체와 뜻이 architect 계약에 없다. symbols 절 포인터 하나로는 부족하다 |
| ④ | Coordinator **102행** «명시 효과와 출처 결합 DTO의 지원 밖은 S2» | S2 문면이 «선언 확정 #574 는 사각이 아니다»로 바뀐다. v1 §1.1 «동반»에 있던 항목이 v2 에서 빠졌다 |
| ⑤ | Coordinator **58행** 배너 부재 사유 열거(«형식 red(…)·stale·처분 미기재») · G1′ 배너 check-report | F m-11: «툴체인 stale·기준선 치환»과 G1′ 의 `--expect-base` 가 빠졌다. §9 «F 그 밖 minor — 구현 때»로만 넘겼다 |
| ⑥ | Coordinator **193행**(수정 모드 G1′ 생략) · **177행**(G2 최신성 한정 표기) | H-M3 |
| ⑦ | `design_pregate.py` 사각 S8 문면 · 모듈 docstring «2) 사본» | S-1 뒤 사본 = 기준선 + **승인 유입** + … 이다. 진행분 diff 는 S7·S8 을 S-3 만 반영했다. S8 은 filtered ⓐ 인용 근거라 틀리면 처분이 틀린다 |

- **수정**: 위 7개를 §6 표에 행으로 올리고, Codex 행 번호를 병기한다.

### minor

- **H-m1 결정 7 브리프 형식**: §8 은 11행이다. 기억 «결정 브리프 게이트»(10줄 이하 · 수치)에 맞춰 줄인다.
- **H-m2 폴백 걸이 지점**: §5-2 «resolve 실패하면 폴백»을 주석 단위로 구현하면 `tuple[XIn, ...]` 을 놓친다. 현장 폴백 필요 8건 중 6건이 여기에 든다. «`identity(local=True)` 의 bare 미해소 분기에서 잎 단위로 · 별도 인스턴스(#197·#202 무접촉)»로 적는다. §7 재생이 잡기는 한다.
- **H-m3 도구 오탐의 출구 부재**: §5-7 로 선언 확정 #574 는 filtered·ⓑ 가 막힌다. 새 포트에는 legacy-debt 가 없으니 ignored(빚)도 성립하지 않는다. 오탐이면 설계를 바꾸는 수밖에 없다.
  - §5-3 은 «부분 문자열 특이는 사각에 적는다»고 하는데, 그 사각 인용은 §5-7 이 막는다.
  - **수정**: S-2 선별을 검사기 부분 문자열 대신 계약 자료 경로(`…/port/(domain_bypass_query/)?<cap>/<data>_in` · `framework/…/<data>_in`)로 좁힌다. 아니면 도구 오탐을 Phase 2 3번과 같은 «검사기 오탐 STOP(플러그인 결함)» 경로로 명시한다.
  - 현장 실측: port 밖 `_in` 모듈은 `schema_in.py` 19개뿐이고, BC 이름에 `port` 부분 문자열이 없다. 지금 발화는 0 이다.
- **H-m4 framework 포트 인자의 R 범위**: 대상이 `framework/<cap>/…_port.py` 이면 «같은 BC»가 정의되지 않는다. «framework 만»으로 적는다.
- **H-m5 E M4 창 문면**: §1 은 «G1 뒤·G2 전»이고, 로드맵 9 는 «G0~G2»다. digest 에는 앞쪽이 맞다(Phase 1 레인은 싼 재실행으로 끝난다). 두 문서의 뜻 차이를 한 줄로 적는다.
- **H-m6 S-1 가장자리**
  - ① 경로를 마지막으로 바꾼 참여 머지가 충돌 해소분이면, 앞 머지의 verbatim 유입까지 버리고 기준선판이 남는다. accounts-1 형 거짓 결손이 재현될 수 있다. 제외 경로 수를 헤더에 병기하고, S-3b 안내에 «플래그 동반 중이면 충돌 해소 제외 경로 — G2 귀속·STOP» 갈래를 둔다.
  - ② 진행분 `baseline_bcs` 는 I 적용 전에 계산한다. 그래서 유입이 들여온 BC 를 신규로 보고 골격을 겹친다. «기준선 ⊕ I» 로 계산한다.
- **H-m7 REQUEST_GUIDE 분류**: graph-owned 표에서 빼서 산문 byte 미러 절차로 옮긴다. 순서는 편집 → `cmp` → `request_guide_contract.py --self-test` → 계약 → `reverse_coverage.py` 다. 발주자 전달 기록(F M-2 수정 3)을 더한다.
- **H-m8 §0 순서**: 현장 재생은 «착수 조건»인데 §0 7단(graph 뒤)에 있다. S-2 구현 직후(5′)로 올린다.
- **H-m9 검증 목록 누락**
  - `make verify-mutation`(rulepack 재생성 커밋 — DEVELOPMENT §5)
  - 조감도 `ontology-adoption-map.html` 갱신(사용자 상시 지침)
  - E M1 «같은 서명» 정규화: 양쪽을 `def` 로 파싱한 `ast.dump(args)` 비교를 적는다.
  - 진행분 관찰 3건
    - `ApprovedInflow.counts()` 는 `NotImplementedError` 를 던지는 죽은 코드다.
    - 예보 경로의 `_executor_stamp` → `_pregate_digest()` 는 `OSError` 를 잡지 않는다. check-report·`--block-hash` 만 exit 1 처리한다.
    - Codex 미러가 아직 갱신되지 않았다(`diff -rq` 에서 `design_pregate.py` 만 다르다 — 진행 중이라 정상이지만 verify 전 필수).

## 4. 질문별 답

1. **S-2 폴백이 현장 6건에서 확정을 내는가**
   - 복구 가능한 5건은 전부 확정이다. 엄격 4건도 전부 확정이다(§2).
   - ⑤ 는 G1 판이 없어 잴 수 없다.
   - 잎 단위로 걸어야 한다는 조건이 붙는다.
2. **§1 «이번 실행» 경계**: 지금 문면으로는 기계로 판별할 수 없다(로컬 분 단위 대 UTC 초 · «변경 0» 수단 없음). 대안은 H-M3 이다.
3. **§3.2 `pre-gate 기준선`**
   - 순수 리팩터 레인에서는 값이 생긴다(슬라이스 0 이면 G1′ 생략 불가).
   - 수정 모드 G1′ 생략에서는 앞 실행 기준선이 들어가거나 값이 비고, Phase 2 반송 때 옛 트리로 재발화한다.
   - Phase 1 재사용 폴더에서는 의무를 지킬 수 없다(H-M2).
4. **§6 누락**
   - F M-6 6곳은 들어갔다.
   - 수정 모드 193행 · 177행 · 218/85/122/18행 실행 줄 · architect 87·90행 · 102행 S2 문면 · 58행 배너 사유 · 사각 S8 · 각 Codex 대응이 빠졌다.
   - LEDGER 는 있으나 target-counts · q4 · 소스 미러 · `corpus_mirror_sync` 가 빠졌다(H-M4·H-M5).
5. **채번·wiring**
   - houserules §3 bullet 은 **새 R-ID**(R-3500 · Prohibition)여야 한다. R-3222 는 delegatedTo reviewer 인 소유 규범이라 enforcedBy 두 검사기를 실을 수 없다.
   - wiring 은 `ontology/wiring/discipline-houserules-final.ttl` 에 `djr:R-3500 djr:enforcedBy c/design_pregate.py, c/check-port-adapter-pairing.py` 다. 근거는 authoring §16(docstring 근거 — `design_pregate.py` docstring 에 #574 예보를 적어야 근거가 선다)이다.
   - Coordinator 새 의무들은 R-3445 amendment 인지 신설인지 매핑표로 정해야 한다.

## 5. 권고 §0 (수정안)

1. S-4 → 2. S-3(+ S7·S8·docstring) → 3. S-1·S-1b(+ `baseline_bcs` ⊕ I · expect-base 기계 집행 여부 결정) → 4. S-3b → 5. S-2(잎 단위 폴백 · U = ast.walk) → **5′. 현장 재생(판 선택 규칙 · 5건 확정 · 음성 대조 78)** → 6. 규범 매핑표 확정 → ttl 편집 → gate → render(command · agent-design-architect · discipline-houserules-final) → LEDGER → target-counts → q4 → 소스 미러 교체 + `corpus_mirror_sync --write` → `make rulepack` → Codex 의미 미러(Coordinator · architect) → REQUEST_GUIDE byte 미러 → 7. 픽스처 · 구현 리뷰 · 조감도 · `make verify` · `make verify-mutation` · 커밋 → 봉인 chore.
