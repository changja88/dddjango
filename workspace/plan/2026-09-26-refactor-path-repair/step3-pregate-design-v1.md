# 로드맵 3 — pre-gate 수리 4종 설계 v1 (2026-09-26 밤 · 적대 검토 전)

- 입력: 진단 `diag-B3-pregate.md`(원인·수정안 S-1~S-4 · G-1·G-2·G-4) · 현장 실측 `diag-B3-pregate-field-frequency.md`(분모 79 실행 · 517 절).
- 사용자 결정: 결정 4 «증거를 갖고 정하자» → 실측. 결정 6 «전부다 진행하고 배포» → 4종 전부 포함(`evening-report.md` §5).
- 구현 순서(실제 비용순): **F4-22 → F4-21 → F4-23 + digest**. 한 번에 배포하므로 커밋은 하나로 묶어도 되고, 결함별로 나눠도 된다(구현 편의).
- 공통 제약:
  - `design_pregate.py` 는 Codex byte 미러이자 봉인 pipeline 그룹이다.
  - Coordinator·houserules 문면은 graph-owned 다(ttl → render → LEDGER → rulepack → Codex 의미 미러).
  - houserules `final.md` 절은 소스 미러 수동 교체 뒤 `corpus_mirror_sync --write` 를 거친다.
  - 봉인(`manifest_seal --write`)은 마지막에 하고, 커밋 뒤 chore 로 한다.

## 1. F4-22 — use case 의 `<data>_in` 생성(#574)을 G1 에서 못 잡음

실측: 엄격 4 · 넓은 6 / 79 실행. G1 예보는 517 절 중 0 이다. 6건 모두 명세 개정과 코드 재작업으로 이어졌고, h1 은 STOP 1 과 발주서 개정 4 를 불렀다. 09-03 에 교훈을 공유한 뒤에도 5회 재발했다.
원인은 둘이다.
- (a) 방향 규칙(#573·#574 «들어오면 `_in` · 나가면 `_out` · `_in` 은 어댑터만 만든다»)이 배포 산문에 없다. 내부 설계 문서와 검사기 메시지에만 있다.
- (b) #574 는 본문 `Call` 규칙이라 스텁에서 원리적으로 뜨지 않는다.

### 1.1 G-2 (필수) — 방향 정의를 houserules §3 명명에 올린다

- 정본: `ontology/rules/discipline-houserules-final.ttl` 의 §3 명명 절. 새 규범으로 채번할지 기존 규범 개정으로 할지는 구현 때 wiring 을 보고 정한다.
- 추가할 bullet(안):
  > **포트 자료의 방향(#573·#574)**: `port/<capability>/`·`domain_bypass_query/<capability>/`·`framework/` 의 `<data>_in.py`·`<data>_out.py` 는 «우리 안쪽»을 기준점으로 이름 붙인다. 바깥이 답해 우리에게 **들어오는** 것(포트 메서드의 **반환**)은 `_in`, 우리가 바깥으로 **내보내는** 것(포트 메서드의 **인자**)은 `_out` 이다. `_in` 타입을 만드는 것은 어댑터뿐이다. 유스케이스가 만들면 #574 다. 그래서 포트 인자로만 쓰이는 자료를 `_in` 으로 두면 유스케이스가 그것을 만들 수밖에 없어 위반이 확정된다 — 그 자료는 `_out` 이다(다른 포트가 반환한 `_in` 을 그대로 넘기는 중계는 예외).
- 동반:
  - Coordinator `:96` 부근의 «명시 효과와 출처 결합 DTO의 지원 밖은 S2» 문면을 새 예보 범위와 정합화한다(`command-dddjango.ttl`).
  - Codex 의미 미러와 소스 미러를 갱신한다.

### 1.2 S-2 — `check_declarations` 에 «#574 예보» 선언 검사 추가

- 대상: 계획 `add`·`update` 경로 가운데 포트 계약 모듈(`application/*/application_layer/port/**` · `domain_bypass_query/**` · `framework/**`)의 클래스 메서드.
- 판정:
  1. 메서드 **매개변수** 주석을 `_DeclarationTypes.resolve` 로 해소한다.
  2. 해소된 신원(origin 모듈 · 심볼) 가운데 origin 모듈 마지막 세그먼트가 `_in` 으로 끝나고 경로에 `port` 또는 `framework` 가 있는 것을 고른다. 검사기 `check-port-adapter-pairing.py:1349` 와 같은 술어다.
  3. 그 신원이 사본 전체 포트 계약 모듈(스텁 포함)의 어떤 메서드 **반환** 주석에도 나오지 않으면 → **선언 확정 `#574`**(차단 · 처분 대상).
  4. 반환 주석 해소가 불능이거나 매개변수 해소가 불능이면 → **선언 후보**.
- 출력: `DeclarationFinding("#574", path, f"{Class}.{method}", "포트 인자 `<심볼>`(<data>_in) — 어떤 포트도 반환하지 않으므로 유스케이스가 만들 수밖에 없다(#574 예보) · `_out` 으로", confirmed)`
- 사각 목록 S2 문면(`:2473`)에 «#574 는 포트 인자 선언으로 예보(본문 생성 자체는 여전히 S1)»를 더한다. S1~S9 개수 단언(`pregate_fixture_run.py:841-842`)은 변하지 않는다.
- 픽스처(새 명세 묶음):
  - 양성 1: 인자로만 쓰이는 `_in`
  - 음성 2: `_out` 개명 / 다른 포트가 반환한 `_in` 중계
  - 후보 1: 해소 불능 주석

## 2. F4-21 — 승인 main 머지 유입을 «기준선 이후 실존» 형식 red 로 처리

실측:
- 형식 red 는 1건(b4)이고, 그 1건이 STOP 1 과 발주서 개정 2 를 불렀다.
- 승인 머지 목록이 있는 실행 15 · 머지 뒤 재발화 5 · M^2 우회 3.
- 우회 기준선으로 check-report «정합» 이 2 실행 · 5회, 유입 파일 부재로 인한 거짓 결손이 1 실행이다.

### 2.1 S-1 — `design_pregate.py` 가 승인 머지 목록을 받는다

- 입력: `--approved-merge-file <path>`(`anchor_diff.APPROVED_MERGE_FLAG` 재사용). 검증은 `anchor_diff.load_approved_merges(path, repo, base_sha, head_sha)` 를 그대로 쓴다(사슬 · 2부모 · 구간 — registry_gate 와 같다). 실패 시 exit 1(실행 불능 · 사유 인용).
- 승인 유입 집합 I = { p | ∃ 승인 머지 M: blob(M^1:p) ≠ blob(M:p) = blob(M^2:p) ∧ p ∉ 기준선 트리 }. registry_gate F1 의 앞 절과 같다. 충돌 해소분(M ≠ M^2)은 제외한다.
- ⓐ 형식 검사(`baseline_form_errors`): update·remove 의 실존 판정을 `in_baseline ∪ I` 로 한다. add 가 I 에 들면 «add 충돌(승인 유입 실존)» 형식 red.
- ⓑ 사본: 형식 검사 뒤, 오버레이·앵커 전에 I 의 blob(M:p) 를 사본에 쓴다. 그러면 앵커 L 에 실리므로 타 레인 실물의 위반은 귀속 밖이 된다.
- ⓒ stdout 과 리포트 헤더에 `승인 유입 N경로(머지 <sha12>…)` 행을 싣는다.
- ⓓ `:2647` 메시지에 세 번째 갈래를 더한다: «승인 머지 유입이면 `--approved-merge-file <산출물 폴더>/approved-merges.txt`».
- 플래그가 없으면 경로가 지금과 byte 동일하다(기존 픽스처 무변).

### 2.2 S-1b — check-report 가 기준선 치환을 본다

- 현장 위험: M^2 우회 재발화 뒤 check-report 가 «정합»을 5회 냈다. 기준선을 표시만 하고 대조하지 않기 때문이다.
- `--check-report` 에 선택 입력 `--expect-base <sha>` 를 둔다. 주면 마지막 예보 절의 기준선 SHA(전체 40자 · 접두 12 허용)가 기대값과 다를 때 불비 «기준선 치환 — 마지막 예보 기준선 <x> ≠ 기대 <y>(G1 승인 기준선) · 승인 유입은 `--approved-merge-file` 로 재발화»를 낸다. 안 주면 지금과 같다.

### 2.3 G-1 — Coordinator 문면(graph-owned `command-dddjango.ttl`)

- «캐시 skip·재발화 판형» ②: `approved-merges.txt` 가 있으면 `--base` 재발화 pre-gate 에도 `--approved-merge-file` 로 동반한다.
- ③ 과 «G2 배너 pre-gate 최신성 1행»: G2 직전 `--check-report` 에 `--expect-base <G1 승인 시점 기준선 SHA>` 를 붙인다.
- 산출물 위치 절의 승인 머지 목록 행: 소비자에 pre-gate 재발화를 더한다.

## 3. F4-23 — `--base`≠HEAD 재발화가 dirty 오버레이로 혼합 사본이 됨

실측: 전제(명시 재발화 + dirty)는 흔하다(보존 stdout 30 중 28). 실제로 난 거짓 red 는 1건(h1 · 24항목 · 30분 뒤 green · 오처분 0)이다.

### 3.1 S-3 — 기준선≠HEAD 이면 dirty 오버레이를 하지 않는다

- `main()` `:2908`: `explicit_base ∧ base_sha ≠ rev-parse HEAD` 이면 `_overlay_dirty` 를 부르지 않는다. stdout 과 헤더에 `dirty overlay 생략(기준선≠HEAD · 작업 트리 변경 N경로 — 재발화 사본 = 기준선 트리 + 승인 유입 + 이 명세 스텁)` 1행을 싣는다. N 은 `git status --porcelain` 행 수다.
- 결과는 규약을 지킨 실행(WIP 커밋 또는 stash)과 같다. 기본 모드와 `--base HEAD`(명시 포함) 는 변하지 않는다.
- `lift_realized_adds` 는 오버레이가 없으면 걷을 것이 없다. WIP 에만 있던 기실현 add 는 사본에 없으므로 보통 add 로 스텁이 된다. already-built 기록에서만 빠진다(보고 차이 — 판정 동일).
- 문서 문면: docstring `:106-110` · 사각 S7/S8(`:2483-2490`) 상수를 새 동작에 맞춘다. Coordinator 문면(«미커밋 WIP 는 커밋 또는 stash 후 실행»)은 여전히 참이라 고치지 않는다.
- 기각: 현장 제안 «사본 = 기준선..HEAD + 작업 트리» — E1 계약(`pregate_fixture_run.py:559-573`)과 충돌한다(진단 §4).

### 3.2 S-3b — 변종(fortune-house `:554`)의 안내 문구

- 사건: 재발화 사본에 기준선 이후 **레인 자신의 승인 커밋**(STOP 회신 `dff956cc`)이 만든 계약이 없어 «계약 실존 결손»이 났다. filtered 로 처분한 뒤 file-plan 에 update 3행을 넣어 해소했다.
- 판단: 도구 결함이 아니다. 기준선 이후 레인이 만든 파일은 이번 실행의 델타(G2 귀속 대상)이므로 file-plan 에 적는 것이 정답이다. 현장의 «비틀기»는 사실 올바른 회계다.
- 수정: 계약 실존 결손 행에서, 결손 대상 모듈이 명시 재발화이고 사본에는 없지만 HEAD 에 있으면(`git cat-file -e HEAD:<path>`) 안내를 덧붙인다: «기준선 이후 커밋분 — 레인 자신의 변경이면 file-plan 에 add/update 로 적는다(G2 귀속 대상) · 승인 머지 유입이면 `--approved-merge-file`». 판정은 바뀌지 않고 문구만 바뀐다.

## 4. digest — 툴체인 최신성

실측: 툴체인이 도중에 바뀐 실행 5 / 79. 옛 판 «정합» 통과는 1건이고 실해는 0 이다. 노출은 09-01~09-11 창에만 있었다. 싼 보험이다.

### 4.1 S-4

- `_executor_stamp` 에 `· 실행 트리 digest <registry_gate._tree_digest()[0]>` 을 붙인다. scripts 폴더의 `*.py`·`*.json` 전량이고, Claude·Codex 가 byte 미러라 같은 값이 나온다.
- `check_report`:
  - 마지막 절 헤더의 digest ≠ 현재 → 불비 «stale(툴체인) — 실행 트리 digest <old> ≠ 현재 <now> · 재발화».
  - digest 토큰 없음 → 불비 «툴체인 증명 불가(구판 헤더) · 재발화».
  - 둘 다 fail-closed 다. 릴리즈 창 규칙상 배포 시점에 진행 중 레인은 0 이므로 구판 리포트는 끝난 레인에만 있다.
- `요약:` 행에 `실행 트리 digest <현재>=<리포트>` 를 싣는다.
- `--block-hash` 출력에 둘째 행 `실행 트리 digest <값>` 을 더한다(캐시 skip 대조용).

### 4.2 G-4 — Coordinator 문면

- 캐시 skip 조건: «`--block-hash` 의 블록 해시와 실행 트리 digest 가 둘 다 직전 리포트 헤더와 같을 때».
- G2 최신성 1행: digest 일치를 표기한다.

## 5. 검증 계획

- 결함마다 재현(scratch · 진단 §7 헬퍼 `f4-22/pg.sh` 계열)을 한다. **수정 전 코드 = red 또는 거짓 결과, 수정 후 = 기대 결과**를 나란히 기록한다.
  - F4-22: r22 판형 — 수정 전 exit 0, 수정 후 선언 확정 #574 exit 2 · 음성 2 green.
  - F4-21: r21 판형 — 무플래그 exit 3 · 플래그 exit 0 + «승인 유입 1» · I 에 든 add → exit 3 · 목록 밖 머지 → exit 1 · `--expect-base` 치환 탐지.
  - F4-23: r23 판형 — T2 는 수정 전 exit 2, 수정 후 exit 0(T1·T3 과 동일) + «dirty overlay 생략» 행.
  - digest: digest 불일치 → check-report 3 · 토큰 없음 → 3 · 일치 → 0.
- `pregate_fixture_run.py` 새 묶음을 추가한다. 기존 묶음의 기대값은 변하지 않아야 하고, 변하면 사유를 적는다.
- 구현 리뷰(독립 에이전트) → `make verify` → 커밋 → 봉인 chore.

## 6. 적대 검토에 묻는 것

1. S-2 의 «사본 전체 포트 반환에 없으면 확정» 술어가 오탐·미탐을 내는가? BC 간 포트 · `framework/` · 제네릭 · `Optional[...In]` · 컨테이너 원소 등.
2. S-1 의 I 계산과 사본 쓰기가 registry_gate 의 provenance 의미와 어긋나는가? 앵커 L 에 싣는 것이 귀속을 잘못 숨기는가?
3. S-3 의 «기준선≠HEAD 이면 오버레이 생략»이 이미 쓰이는 흐름(명시 `--base HEAD` · 초기 예보 · 기실현 add 기록)을 깨는가?
4. S-4 의 fail-closed 가 배포 직후 어떤 레인을 부당하게 막는가?
5. G-2 문면이 검사기 #573·#574 술어와 정확히 같은 뜻인가? `domain_bypass_query` · `framework` 범위 · 중계 예외가 검사기와 어긋나지 않는가?
6. 빠진 것 — 현장 실측이 가리키는데 이 설계가 다루지 않는 비용.
