# 로드맵 3 — pre-gate 수리 4종 설계 v2 + 구현 계획 (2026-09-27 · 적대 검토 E·F 반영)

- v1 → v2: 검토 E(코드 · `review-E-step3-code.md` — blocker 1 · major 4 · minor 14)와 F(규범·현장 · `review-F-step3-norms.md` — blocker 2 · major 7 · minor 15)를 처분했다(§9 표).
- 두 검토가 따로 같은 blocker 를 냈다: v1 의 S-2 는 현장형 명세(같은 능력 폴더 import 를 적지 않음)에서 타입을 해소하지 못해 «후보»로만 떨어지고, #574 를 막지 못한다.
- **사용자 결정 필요 1건**(§8 · 새 결정 7): 포트가 돌려주는 자료의 이름(`_in` 대 `_out`). 이 결정은 G-2 의 «반환» 절반에만 걸린다. 나머지는 결정과 무관하게 진행한다.

## 0. 구현 순서와 커밋

검토 E m14 의 권고를 따른다. 네 수리가 `main()` · 리포트 헤더 · 사각 목록을 함께 건드리므로, 헤더 형식을 한 번만 연다.

1. S-4 digest: 스탬프 · check-report · `--block-hash` · 러너 `:255` 단언 개정
2. S-3 오버레이 생략 + 골격 가드 기준선화(m7) + N 계수·HEAD 해석(m9)
3. S-1 승인 유입 + S-1b 기대 기준선
4. S-3b 결손 안내
5. S-2 #574 예보(폴백 해소 · 선언 메서드 한정 · 잠재 반환 이름 · 필드 닫힘)
6. graph-owned 일괄: G-1 · G-2(인자 절반) · G-4 · 문면 정정(m8 · m10 · M-6) → render → LEDGER → rulepack 1회
7. 현장 재생 시험 · 픽스처 · 구현 리뷰 · `make verify` · 커밋(스크립트와 graph 를 한 커밋) → 봉인 chore

- 스크립트를 바꿀 때마다 Codex byte 미러를 같이 갱신한다.
- `anchor_diff` import 는 최상단 `try/except ImportError` 안에 둔다.
- docstring «사용:»·exit 규약을 같은 커밋에서 갱신한다.

## 1. S-4 — 툴체인 digest

- pre-gate 전용 digest = registry `_tree_digest` 와 같은 방식(scripts 폴더 `*.py`·`*.json` 전량)이되, **`rulepack.json` 은 뺀다**(m-9). rulepack 은 검사기의 판정 입력이 아니다(읽는 곳은 `rulepack.py` · `regen_core.py` 뿐). 이렇게 해야 graph 문면만 바뀐 배포가 진행 중 예보를 stale 로 만들지 않는다.
- 스탬프: `_executor_stamp` 끝에 `· 실행 트리 digest <16hex>` 를 붙인다. 블록 해시 **뒤**다(구판 헤더 판별 무변 — E m11).
- check-report:
  - 마지막 절 digest ≠ 현재 → 불비 «stale(툴체인) · 재발화».
  - digest 토큰 없음 → 불비 «툴체인 증명 불가(구판 헤더) · 재발화».
  - digest 는 함수 안에서 계산한다(선택 인자로 주입 허용 · 호출부 서명 무변).
  - `_tree_digest` 의 `OSError` 는 exit 1 로 낸다(트레이스백 금지).
- `요약:` 행 끝(기준선 뒤)에 `· 실행 트리 digest <현재>=<리포트>` 를 붙인다(러너 `_SUMMARY_CHECK_RE` · 현장 파서 순서 보존 — E m5).
- `--block-hash`: 둘째 행 `실행 트리 digest <값>` 을 더한다. 러너 `:252-256` 의 완전 일치 단언을 «첫 행 일치 + 둘째 행 형식»으로 개정하고 사유를 적는다.
- **M-3(F) 폴더 재사용 경로**: 결정 5 로 끝난 폴더는 새 실행이 된다. 명세 변경이 없는 수정 모드는 옛 실행의 마지막 예보 절(구판 헤더)을 만나 G2 에서 막힌다.
  - 규범에 한정을 넓힌다: «이번 실행(실행 줄의 G0 승인 이후)에 pre-gate 예보 절이 없고 design-spec 변경이 0 이면 최신성 행은 `미실행(명세 변경 0 · 앞 실행 예보)` 이고 `--check-report` 를 부르지 않는다».
  - 명세가 바뀌면 재실행이 의무이므로 새 절(digest 포함)이 생긴다.
- **M-4(E) 진행 중 레인**: 배포 뒤 진행 중 레인은 구판 헤더로 재발화가 강제되고, 새 검사기 red 가 Phase 2 반송을 부를 수 있다. 대책은 **배포 절차**다. 로드맵 9 에서 «G1 뒤 · G2 전 레인 0» 을 확인한다(대상 저장소 `.dddjango/*/` · herdr 워크트리 · 발주 상태). 남아 있으면 착륙을 기다린다. 설계 v1 의 «부당 차단 없음» 서술은 삭제한다.

## 2. S-3 — 기준선 ≠ HEAD 재발화의 오버레이 생략

- HEAD 는 `rev-parse --verify HEAD^{commit}` 로 **한 번** 해석한다. `in_head`(`:2894`)와 같은 값을 재사용한다. 미탄생 HEAD 는 RunError(exit 1)다.
- `explicit_base ∧ base_sha ≠ head_sha` 이면 `_overlay_dirty` 를 부르지 않는다.
  - N 은 오버레이와 같은 호출(`status --porcelain=v1 -z --untracked-files=all`)로 센다(E m9).
  - stdout 과 헤더에 `- dirty overlay 생략: 기준선≠HEAD · 작업 트리 변경 N경로(재발화 사본 = 기준선 트리 + 승인 유입 + 이 명세 스텁)` 행을 싣는다. 행 머리는 `- 기준선 SHA:`/`- 판정:`/백틱 12hex 가 아니다(E m5).
- **골격 가드 기준선화(E m7)**: 신규 BC 판정을 앵커 커밋이 아니라 **기준선 트리**(오버레이 전 · `in_baseline` 계산 시점)로 옮긴다. `materialize_skeleton` 은 없는 칸만 만드므로 부분 실존 BC 에서도 안전하다. 이것으로 «기준선 = HEAD + 첫 슬라이스 미커밋 WIP» 경로도 닫힌다. E1~E4 · E2′ 판정이 변하지 않음을 E2 변형 픽스처로 고정한다.
- 판정 변화의 정직 표기(E m8): WIP 에서 지운 remove · WIP 에 구현된 update 함수 · `deferred(… until Sn)` 결손은 **판정이 바뀐다**. 모두 «규약 준수 실행(WIP 커밋/stash)»과 같은 쪽으로 바뀐다.
- 거짓이 되는 문면 3곳을 graph 개정에 넣는다: `dddjango.md` pre-gate 절 «dirty overlay·기준선 갱신이 자동 반영» · ② «명시 `--base HEAD` 포함 … 오버레이 실존 add = 기실현» · `design-architect.md` «격리 사본(기준선 + dirty overlay + …)». Codex 대응도 함께 고친다.

## 3. S-1 — 승인 머지 유입 · S-1b 기대 기준선

### 3.1 S-1

- 입력 `--approved-merge-file <path>`.
  - 부재 · 검증 실패(`AnchorDiffUsage` · `OSError`)는 exit 1 이다. 사유는 «발주자 사안 → STOP»(승인 머지 절과 같은 라우팅 — F m-6)이다.
  - 기준선이 레인 first-parent 사슬 밖이면 처방 한 줄을 적는다: «우회 기준선이면 G1 기준선으로 · 리베이스면 STOP»(E m4).
- 참여 머지만 쓴다(`m.participates` — E m1). 기준선 이전 머지는 제외한다.
- **I = 참여 머지의 verbatim 유입 변경 전부(추가·수정·삭제)**(E M3 · F m-5).
  - 경로마다 사슬 순서상 그 경로를 마지막으로 바꾼 참여 머지 M* 를 고른다(blob(M*^1:p) ≠ blob(M*:p)).
  - blob(M*:p) = blob(M*^2:p) 이면 I 에 넣는다. 부재면 삭제다.
  - 충돌 해소분은 제외한다.
  - 계산은 머지당 `diff-tree -r -z --no-renames M^1 M` 과 `… M^2 M` 이다. 모드는 diff-tree 출력에서 쓴다(120000 = symlink · 160000 = 건너뛰고 병기). `registry_gate._tree_blobs` 는 재사용하지 않는다(fail-open · 모드 소실 — E m2).
- 순서: `in_baseline` 계산 → **I 를 사본에 적용**(쓰기·삭제) → 형식 검사 → 오버레이 결정(S-3) → 기실현 걷기 → 앵커.
  - 형식 검사의 실존 판정은 «기준선 ⊕ I» 다.
  - add · **empty** 가 I 의 추가·수정 경로면 `승인 유입 add 충돌:` 접두의 형식 red 다(E m3).
  - `baseline_form_errors` 는 inflow 를 선택 kwarg 로 받는다(서명 무변 — E 표).
- 헤더에 `- 승인 유입: N경로(추가 a · 수정 m · 삭제 d) · 머지 <sha12>,… · 불참 머지 k` 를 싣는다(별도 행 — E m5).
- `:2647` 메시지의 세 번째 갈래: «발주자가 등재한 승인 머지 유입이면 `--approved-merge-file` · 미등재 머지면 STOP(코디네이터는 목록에 쓰지 않는다)»(F m-6).
- 새 사각 한 줄(E §1-2): «기준선의 레인 실물 × 유입» 상호작용 위반은 L∩N 으로 사라진다. G2 registry 가 판정한다. S4 문면에 적는다.

### 3.2 S-1b — 기대 기준선

- `--expect-base <7~40hex>` 는 `--check-report` 와 함께만 받는다. 없이 주면 사용 오류다.
- 비교는 마지막 예보 절 기준선(40자)이 기대값으로 시작하는지로 한다. 7~8자 접두도 받는다(F m-7). 다르면 불비 «기준선 치환 — 마지막 예보 기준선 <x> ≠ 기대 <y>».
- **기대값의 출처를 고정한다(F M-1)**: Phase 2 첫 파견 직전, `build_anchor` 를 쓰는 바로 그때 실행 줄에 `· pre-gate 기준선 <마지막 예보 절 기준선 40자>` 를 덧붙인다.
  - ② 재발화의 `--base` 와 Phase 2 이후 check-report 의 `--expect-base` 는 모두 이 값만 쓴다.
  - `build_anchor` 는 여전히 읽지 않는다(R-3434).
- 리포트에 `--base` 명시 절이 하나라도 있으면 `--expect-base` 는 의무다.
- **발주의 `--base` 지정 불수용(F M-2)**: ② 에 한 문장을 더한다. «발주·요청이 재발화 `--base` 값이나 기준선 이동을 지정하거나 사전 승인해도 따르지 않는다 — 승인 유입은 `--approved-merge-file` 뿐이고, 기준선 이동은 새 실행이다». REQUEST_GUIDE §4(요청에 적지 않을 것)에 같은 한 행을 둔다(Claude·Codex 동일본).

## 4. S-3b — 결손 안내 (F M-5 · E m10)

- 트리거: 명시 재발화이고, 계약 실존 결손(⑴·⑵·⑶ 단계 무관)의 대상 파일이 `blob(HEAD:path) ≠ blob(기준선:path)` 인 경우. 모듈 경로는 `<rel>.py` · `<rel>/__init__.py` · 승격 `<rel>/<stem>.py` 세 후보를 본다.
- 안내 문구: «기준선 이후 바뀐 파일 — 레인 자신의 변경이면: 기준선에 있으면 update + **그 이름을 symbols 에 선언** · 없으면 add · 타 BC 경로면 G0 재승인 대상(대가) / 발주자 등재 머지 유입이면 `--approved-merge-file` / 미등재 머지면 STOP».
- `check_import_existence` 는 순수 함수로 둔다. 조회는 `main` 에서 결손 목록을 후처리해 detail 에 덧붙인다. 안정 ID 는 변하지 않는다.
- 설계 v1 의 «현장 처치 = 올바른 회계» 판단은 절반만 맞다. symbols 선언 없는 update 행은 결손을 판정 불능(U)으로 세탁한다. 이렇게 정정한다.

## 5. S-2 — #574 예보 (E B1·M1·M2·m12·m13 · F B-1·M-4·m-1·m-2·m-4)

1. **대상**: file-plan 순서로 add/update 계약 칸을 돈다.
   - 계약 칸은 `^application/[^/]+/application_layer/port/(?:domain_bypass_query/)?[^/]+/[^/]+_(?:port|query)\.py$` · `^framework/(?:broker/(?:internal|external)|[^/]+)/[^/]+_port\.py$` 이다.
   - **명세 symbols 가 선언한 클래스의 선언 메서드만** 본다. update 는 실물에 같은 서명이 있는 메서드를 제외한다(손대지 않은 legacy 제외).
   - 매개변수(`self`/`cls` 제외) 주석을 본다.
2. **해소**: `types.resolve(module, ann, referenced_names=names)` 를 쓴다. 실패하면 **S-2 전용 폴백**을 쓴다.
   - bare 이름 X 를 **같은 능력 폴더**의 두 출처(계획 symbols 선언 클래스 · 사본 실물 최상위 클래스)에서 찾는다.
   - X 를 정의한 모듈이 정확히 하나면 그 신원으로 삼는다. 0 또는 복수면 미해소다.
   - 폴백은 S-2 에서만 쓴다. #197 · #202 경로는 건드리지 않는다.
3. **`_in` 선별**: `m.endswith("_in") and ("port" in m or "framework" in m)` 을 쓴다. 검사기 문자열 그대로다. 부분 문자열 특이(`report` 등)는 사각에 적는다.
4. **반환 우주 R · 잠재 이름 U**: 인자 쪽에 `_in` 후보가 있을 때만 모은다(지연 계산).
   - 범위는 **인자 쪽 포트와 같은 BC + framework** 의 계약 모듈이다(BC 간 중계는 격리 위반이라 근거가 안 된다).
   - 메서드 반환은 **실물 ∪ 선언**(교체 아님)이다.
   - 해소·폴백된 신원이 R, 미해소 참조 이름이 U 다.
   - R 은 `_in` 클래스의 필드 주석을 따라 닫는다(방문 집합 · 순환 차단 — 필드 중계).
   - 열거는 `os.walk(followlinks=False)` + 정규식 + 계획 칸을 합친 뒤 `sorted(set())` 로 한다.
5. **판정**: 인자 `_in` 신원 ∈ R → 무 · 그 클래스 이름 ∈ U → 후보 · 그 밖 → **확정**.
   - 인자 해소 불능은 참조 이름이 `…In` 이거나 폴백이 `_in` 모듈을 가리키는데 비유일일 때만 후보다. 그 밖은 무보고다(소음 제거).
6. **출력**: `DeclarationFinding("#574", path, f"{Class}.{method}", detail, confirmed)`.
   - detail: «포트 인자 `<심볼>`(`<data>_in`) — 같은 BC 의 어떤 포트도 돌려주지 않으므로 유스케이스가 만들 수밖에 없다(#574 예보) · 파일 `<data>_out.py` 와 클래스 이름을 함께 바꾼다(클래스 `…In` 을 남기면 #573)».
7. **처분 제한(F M-4)**: 사각 S2 문면은 «선언 확정 #574 는 사각이 아니다»로 적는다. Coordinator 의 path 규칙 filtered 금지 문장과 같은 꼴로 «선언 확정 #574 는 S1·S2 인용 filtered 와 재수출 경유 검사기 exit 0 의 ⓑ 대상이 아니다 — corrected 또는 ignored(빚)만»을 둔다.

## 6. graph-owned 일괄

| 문서 | 변경 |
|---|---|
| `command-dddjango` | ② 에 `--approved-merge-file` 동반 · 발주 `--base` 불수용 · `--expect-base` 의무와 출처(실행 줄 `pre-gate 기준선`) · 오버레이 문면 정정(m8 · m10) · 캐시 skip 조건에 digest(G-4) · skip 행에 digest 칸 · ③·G2 최신성 1행에 digest·expect-base · 한정 확장(M-3) · 선언 확정 #574 filtered 금지 · 산출물 위치 승인 머지 행의 소비자에 pre-gate 추가 · **재발화 판형 요약 재진술 3곳(Phase 2 감사 반송 · 수정 모드 G1′ · Contract mismatch)을 «② 참조»로 통일**(F M-6) · 실행 줄 기계 기록 목록에 `pre-gate 기준선` 추가 |
| `agent-design-architect` | «격리 사본» 문면 정정 · symbols 절에 «포트 자료 방향 — houserules §3» 한 행 포인터 |
| `discipline-houserules-final` §3 | G-2 **인자 절반**(아래) |
| Codex | `dddjango/SKILL.md` 대응 절 전부 · `dddjango-design-architect/SKILL.md` |
| REQUEST_GUIDE §4 | 발주 `--base` 지정 불수용 한 행(Claude·Codex 동일본) |

- G-2 인자 절반 문안: «**포트 자료의 방향 — 인자**: 포트·조회 계약(`port/<capability>/` · `port/domain_bypass_query/<capability>/` · `framework/<capability>/`) 메서드의 **인자** 타입을 `<data>_in` 으로 두지 않는다. `_in` 은 어댑터만 만든다(#574). 같은 BC 의 다른 계약이 돌려준 `_in`(그 필드 포함)을 그대로 넘기는 것은 만드는 것이 아니다. 기계 판정은 G1 pre-gate 예보(선언 확정 #574)와 G2 #574(생성 호출)이고, 파일 접미와 클래스 접미의 교차는 #573(`port/<capability>/` 만)이다.»
- wiring(F M-7): `enforcedBy` 는 `design_pregate.py` 와 `check-port-adapter-pairing.py`(#574)만 둔다. #573 을 방향 규칙의 집행자로 적지 않는다.

## 7. 검증

- **현장 재생(착수 조건 — E B1-4 · F B-1)**: F4-22 6건(catalog · b5 · b7 · h1 · decisive · counter-room)의 **수정 전 G1 판** 명세를 `git show <커밋>:…/design-spec.md` 로 뽑는다. scratch clone(해당 G1 기준선 체크아웃)에서 수정 후 pre-gate 를 돌려 결과표(확정/후보/무)를 만든다. 목표는 6건 모두 확정 또는 후보이고, 엄격 4건은 확정이다. 미달이면 폴백을 고치고 다시 잰다.
- 결함별 재현(수정 전 = red·거짓, 수정 후 = 기대):
  - F4-22: 현장형(포트 import 행 없음) 양성 1 · r22 판형 보조 · 음성 3(`_out` 개명 · 같은 BC 반환 `_in` 중계 · 필드 중계) · update 부분 선언 음성 1(M1) · 후보 1.
  - F4-21: 무플래그 exit 3 · 플래그 exit 0 + «승인 유입» 행 · 수정 유입 · 삭제 유입 · I 에 든 add/empty → exit 3 · 목록 밖 머지 → exit 1 · 기준선 이전 머지 불참 · `--expect-base` 치환 탐지 · 7자 접두 일치.
  - F4-23: r23 T2 → 수정 전 exit 2 · 수정 후 exit 0(T1·T3 과 동일) + «생략» 행. 기준선 = HEAD + WIP 신규 BC → 골격 가드 정상.
  - digest: 불일치 → 3 · 토큰 없음 → 3 · 일치 → 0 · rulepack.json 만 바뀜 → 일치.
- `pregate_fixture_run.py` 새 묶음을 둔다. 기존 기대값 변화는 `:255` 한 곳뿐이어야 하고, 사유를 적는다(E §3 표).
- 구현 리뷰(독립 에이전트) → `make verify` → 커밋 → 봉인 chore.

## 8. 사용자 결정 필요 — 결정 7: 포트가 돌려주는 자료의 이름

- 규칙 원문(#573 설계 · 검사기 메시지): «방향 기준점은 우리 안쪽 — 들어오면 `_in`, 나가면 `_out`». 그러면 포트 **반환**(바깥의 답이 들어옴)은 `_in`, 포트 **인자**(우리가 내보냄)는 `_out` 이다.
- 현장 main 에서 포트·조회 계약의 반환 타입은 `_out` 이 102곳(15 BC · bypass 6/6 전부), `_in` 이 20곳이다.
- 발주자가 h1 STOP 에서 «어댑터-반환은 그대로 `_out`»을 승인한 적이 있다. 사용자 원문은 아니다.
- 정본 안에서도 한 곳(#236 · bypass «내보내는 자료» = `_out` 칸)이 어긋난다.
- 검사기는 반환 이름을 보지 않는다. 그래서 102곳이 G2 를 통과해 왔다.
- 선택지:
  - (가) **규칙대로 반환 = `_in`**. 현장 102곳은 의미 빚이 되어 리팩토링 커맨드가 정리한다. #236 을 정정한다. #574(`_in` 은 어댑터만 만든다)와 한 쌍으로 일관된다.
  - (나) **현장대로 규칙을 바꾼다**. 반환도 `_out` 을 허용한다. 대신 `_in`/`_out` 이 무엇을 뜻하는지가 흐려지고 #574 의 근거가 약해진다.
- 이 결정은 G-2 의 반환 절반과 #236 정정에만 걸린다. 인자 절반은 결정과 무관하게 이번에 넣는다.

## 9. 검토 처분

| 발견 | 처분 | 위치 |
|---|---|---|
| E B1 · F B-1 S-2 해소 불능 | 수용 — 같은 능력 폴더 폴백 · 현장 재생을 착수 조건으로 | §5-2 · §7 |
| F B-2 반환 명명 충돌 | 수용 — G-2 를 인자 절반으로 줄이고 반환은 사용자 결정 7 | §6 · §8 |
| E M1 · F m-4 update 부분 선언 · legacy | 수용 — 선언 메서드만 · 반환은 실물 ∪ 선언 | §5-1 · §5-4 |
| E M2 · F m-2 반환 해소 불능 · 필드 중계 | 수용 — U 후보 · R 필드 닫힘 | §5-4 · §5-5 |
| E M3 · F m-5 I 신규 경로만 | 수용 — 추가·수정·삭제 · 마지막 참여 머지 | §3.1 |
| E M4 진행 중 레인 | 수용 — 배포 절차(로드맵 9)에서 G1~G2 레인 0 확인 · v1 서술 삭제 | §1 |
| F M-1 expect-base 출처 | 수용 — 실행 줄 `pre-gate 기준선` · 의무화 | §3.2 |
| F M-2 발주 `--base` 지정 | 수용 — 불수용 문장 · REQUEST_GUIDE | §3.2 · §6 |
| F M-3 폴더 재사용 구판 헤더 | 수용 — 한정 확장(이번 실행 예보 0 ∧ 명세 변경 0) | §1 |
| F M-4 filtered 탈출 | 수용 — 선언 확정 #574 filtered 금지 · S2 문면 | §5-7 |
| F M-5 S-3b 트리거·안내 | 수용 — blob 비교 트리거 · symbols 선언 · 타 BC 대가 | §4 |
| F M-6 요약 재진술 6곳 | 수용 — «② 참조» 통일(Claude 3 · Codex 3) | §6 |
| F M-7 인용·wiring 과대 | 수용 — 인용 정정 · enforcedBy 한정 | §6 |
| E m1 참여 한정 | 수용 | §3.1 |
| E m2 I/O fail-closed · 모드 | 수용 | §3.1 |
| E m3 empty ∈ I · 승격 순서 · 요약 종류 | 수용 | §3.1 |
| E m4 사슬 밖 기준선 | 수용 — 처방 한 줄 | §3.1 |
| E m5 헤더·요약 형식 | 수용 — 별도 행 · 행 끝 토큰 | §1 · §2 · §3.1 |
| E m6 · F m-7 expect-base 세부 | 수용 | §3.2 |
| E m7 골격 가드 | 수용 — 기준선 트리로 | §2 |
| E m8 · F m-10 판정 변화 · 문면 3곳 | 수용 — 정직 표기 · graph 개정 | §2 · §6 |
| E m9 N 계수 · HEAD | 수용 | §2 |
| E m10 S-3b 경로·범위 | 수용 | §4 |
| E m11 · F m-8 기존 기대 변화 | 수용 — `:255` 개정 · 서명 무변 | §1 · §7 |
| E m12 · F m-1 검사기 술어 차이 · 클래스 접미 | 수용 — 메시지에 클래스 · 사각 명기 | §5-3 · §5-6 |
| E m13 후보 소음 · 결정성 | 수용 | §5-4 · §5-5 |
| E m14 순서 | 수용 | §0 |
| F m-6 목록 라우팅 · 새 실행 이월 | 수용 — 발주자 사안 STOP. 새 실행의 옛 목록은 참여 한정(기준선 이전 머지 불참)으로 대부분 무해하다 · 사슬 밖 옛 SHA 는 exit 1 → 발주자 목록 갱신 | §3.1 |
| F m-9 digest 과민 | 수용 — rulepack.json 제외 | §1 |
| F 그 밖 minor | 구현 때 반영 · 구현 리뷰에서 대조 | — |
