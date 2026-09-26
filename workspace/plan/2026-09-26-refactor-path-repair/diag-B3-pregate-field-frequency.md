# 진단 B3 보강 — pre-gate 결함 4종의 현장 빈도·비용 실측 (spring_dream_server)

- 작성 2026-09-26 · 읽기 전용 실측(대상 저장소·워크트리 쓰기 0 · 검사기/pre-gate/registry_gate/manage.py 실행 0 · git 은 `log`/`show`/`diff`/`cat-file`/`ls-tree`/`merge-base --is-ancestor`/`rev-parse` 만) · Serena·Graphify 미사용(지시).
- 짝 문서: `diag-B3-pregate.md`(원인·수정안). 이 문서는 «얼마나 자주·얼마나 비쌌나»만 잰다.
- 표기: 수치는 센 값이다. **[추론]** = 추정·해석 · «0건» = 찾아봤고 없음 · «측정 불가(이유)» = 증거가 남지 않음.

## 결론 5줄

1. **분모 = pre-gate 리포트가 있는 실행 폴더 79개**(메인 78 + 워크트리 `lane-8-B-9` 전용 1), 예보 절 517개. 네 결함 중 **실제로 가장 자주, 가장 비싸게 터진 것은 F4-22**다. #574 가 G1 예보 없이 구현 뒤 드러난 실행이 엄격 기준 4 · 넓은 기준 6(/79)이다. 6건 모두 명세 개정과 코드 재작업을 불렀고, 그중 STOP 1 · 발주서 개정 1 이다. pre-gate 는 517절 중 #574 를 한 번도 예보하지 않았다.
2. **F4-21** 은 형식 red 로는 1건(b4)뿐이다. 그러나 주변 비용이 크다. 승인 머지 목록이 있는 실행이 15/79 이고, 머지 뒤 재발화는 5 실행이다. M^2 우회를 쓴 실행이 3이고, 우회 기준선으로 check-report 가 «정합»을 낸 경우가 2 실행 · 5회다. 머지 유입 파일이 사본에 없어 거짓 계약 결손이 난 실행이 1이다. b4 한 건이 STOP 1 과 발주서 개정 2(22·23)를 불렀고, 우회는 뒤이은 발주서 2개(b4-2·b6)에 사전 승인 문면으로 굳었다.
3. **F4-23** 은 전제 조건(명시 `--base`≠HEAD + dirty overlay)이 흔하다. 보존된 명시 재발화 stdout 30개 중 overlay>0 이 28개이고, 그중 기준선≠HEAD 로 추정되는 것이 21개 이상이다. 그런데 **실현된 거짓 red 는 1건**뿐이다(h1 · 24항목 · 같은 블록 해시로 30분 뒤 green). 오처분 0 · STOP 0 이다. 신규 BC 이면서 재발화를 한 실행 5개 중에서 1개만 실현됐다.
4. **digest** 는 툴체인이 실행 도중 바뀐 실행이 5/79 이다(스탬프 실측 3 + 레인 REPORT 기록 2). check-report 가 옛 버전 리포트를 «정합»으로 통과시킨 경우는 1건(b3)이고, 실해는 0 이다(15분 뒤 새 판으로 재예보). 노출은 스크립트가 바뀌는 릴리즈가 잦던 09-01~09-11 창에만 있었다(그 창의 24 실행 중 5). 2.18.3 이후 55 실행은 0 이다. 2.18.3→2.18.4 는 버전만 바뀌고 digest 는 같다(`148a9fa2193abb69`).
5. 진단의 권고 순서 digest → F4-23 → F4-22 → F4-21 은 **실현 비용 기준으로는 지지되지 않는다**. 실현 비용 순서는 F4-22 > F4-21 > F4-23 ≈ digest 다. digest 와 F4-23 을 «스크립트만 · 저위험»으로 한 릴리즈에 묶는 것은 여전히 합리적이다. 다만 그 근거는 빈도가 아니라 싼 보험이다. F4-22 는 적어도 그 묶음과 같은 순위로 올려야 한다.

## 1. 방법 (재현 가능)

### 1.1 대상·분모

```sh
# 메인: pregate-report.md 가 있는 실행 폴더
ls -d /Users/hyun/Desktop/spring_dream_server/.dddjango/*/pregate-report.md          # 78
# 워크트리: 같은 이름은 내용 해시로 대조 → 전부 동일(shasum -a 256), 워크트리 전용 1개만 추가
ls -d ~/.herdr/worktrees/spring_dream_server/*/.dddjango/*/pregate-report.md
diff -rq /Users/hyun/Desktop/spring_dream_server/.dddjango ~/.herdr/worktrees/spring_dream_server/<wt>/.dddjango
```

- 워크트리 5개(book-8-0-2 · lane-5-1-1 · lane-5-1-4 · lane-6-3-3 · lane-8-B-9)는 `.dddjango/` 를 추적한다. 겹치는 폴더 78개는 메인과 byte 가 같다(`diff -rq` 에서 «differ» 0). 그래서 메인 사본을 기준으로 셌다.
- 워크트리 전용 폴더는 2개다.
  - `lane-8-B-9/.dddjango/20260926-2053-showcase-server`(리포트 있음 · 분모에 넣음)
  - `lane-5-1-4/.dddjango/20260926-2242-carried-request-lifetime`(리포트 없음 · 제외)
- 리포트가 없는 메인 폴더 19개(2026-08-27~09-01 초기 실행 18 + `20260917-1151-text-library-h2-1-seed-active`)는 분모 밖이다.
- 보조 증거:
  - 각 실행 폴더 전체 파일: check-report 출력 · stdout 캡처 · registry 출력 · approved-merges.txt · 처분 절
  - `docs/superpowers/orders/lane/*.md`(STOP 312 · REPORT 139 · GATE 241)
  - 발주서 `docs/superpowers/orders/*.md`
  - git 이력

### 1.2 정규식(파서와 같은 앵커 — `design_pregate.py:2675-2676`·`:2502-2504`)

```text
절 앵커      ^## pre-gate 예보 — (\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z) · (.*)$
헤더 행      ^- 기준선 SHA: `([0-9a-f]+)` \(--base ([^)]*)\)
스탬프       dddjango v([0-9.]+)            블록 해시 ([0-9a-f]{12})
판정         ^- 판정: (.*)$                  예보 항목  ^- `([0-9a-f]{12})` .*\[#(\d+)\] ([^\s:`]+)
check-report design_pregate --check-report · 모드 차단\(enforce\) · 실행기: design_pregate.py · dddjango v([0-9.]+) · 블록 해시 ([0-9a-f]{12})
             요약: check-report (정합|불비 \d+건) · 블록 해시 (\S+)=(\S+) · 마지막 판정 (.*?) · .*기준선 ([0-9a-f]{12}|-)
stdout 헤더  # design_pregate — 예보 실행 · 기준선 ([0-9a-f]{12}) \(--base ([^)]+)\).*블록 해시 ([0-9a-f]{12})
overlay      dirty overlay (\d+)건
툴체인       툴체인: dddjango v([0-9.]+) · py[0-9.]+ · 실행 트리 digest ([0-9a-f]+)
형식 red     update 대상 기준선 이후 실존 | 타 레인 유입
```

### 1.3 결함별 판정 절차

**digest**
- 실행마다 다음 버전 집합을 모아 비교했다.
  - 리포트 절 스탬프의 버전
  - check-report 출력(72개)의 실행 버전
  - registry `툴체인` 행의 버전과 digest
- 매칭은 check-report 의 블록 해시와 같은 리포트 절끼리 했다.
- 레인 REPORT 의 «적재 이력»과 STOP 문서로 보강했다.
- 릴리즈별 스크립트 변경 여부는 `git diff --name-only dddjango--vA dddjango--vB -- 'dddjango/scripts/*.py' 'dddjango/scripts/*.json'` 으로 확인했다(dddjango 저장소).

**F4-23**
- 명시 `--base` 절(226)마다 그 시각의 HEAD 를 추정했다. 추정 규칙: `git log --all -- .dddjango/<run>` 의 커밋 중 `merge-base --is-ancestor <base> <c>` 이면서 커밋 시각 ≤ 절 시각인 최신 커밋 **[추론 — 머지 커밋은 경로 이력 단순화로 빠질 수 있다]**.
- 같은 (블록 해시, 기준선) 안에서 red → green 전이를 찾았다.
- 귀속 항목 경로가 `git diff --name-only <base> <HEAD(T)>` 안에 있는지 대조했다.
- 같은 안정 ID 가 clean G1(`--base HEAD` 절)에도 있었는지 대조했다.

**F4-22**
- 모든 절의 `#574` 예보 항목과 선언 항목을 셌다.
- `#574` 가 나오는 실행 파일 · 레인 문서 · 커밋 메시지(`git log --all | grep 574`)를 G1 예보 시각과 대조했다.

**F4-21**
- 형식 red 전건의 사유 행을 분류했다.
- approved-merges.txt 의 머지 SHA 로 `git show -s --format='%cI %P'` 를 구해 머지 뒤 예보 절을 찾았다.
- 명시 base 를 머지 부모와 대조했다.
- 우회 기준선이 찍힌 check-report 출력을 찾았다.

## 2. 결함별 표

### 2.1 digest — 툴체인 최신성

| 항목 | 사건 / 분모 | 비용 | 대표 근거 |
|---|---|---|---|
| G1 스탬프 버전 ≠ 뒤 재발화·check-report·G2 버전인 실행 | **5 / 79**. 스탬프 실측 3: media-library(스탬프 이전 판 → 2.17.21) · fortune-types-db(2.18.0 → 2.18.1) · fortune-house-b3(2.18.1 → 2.18.2). REPORT 기록 2: fortune-record-failure-refund = a12(2.18.0 → 2.18.1 → 2.18.2) · fortune-reading(2.17.13 → 2.17.14 → 2.17.15 · 예보 스탬프 없음) | 5건 중 3건(media · types-db · b3)은 새 판으로 pre-gate 를 다시 돌렸다. types-db 는 같은 블록 해시로 재실행해 결과가 같았다. a12 는 G1 예보(2.18.0)를 다시 검증하지 않고 G2(2.18.2)에 갔다. G2 check-report 기록은 없다 | `20260910-1653-fortune-types-db/pregate-report.md:525`(v2.18.0 · `ac36e1535ee6`) → `:591`(v2.18.1 · 같은 해시) · `20260910-2248-fortune-house-b3/pregate-report.md:733` → `:1094` · `20260902-0128-media-library/pregate-report.md:63` → `:124` · `docs/superpowers/orders/lane/REPORT-fortune-record-a12.md:7-10` |
| 그중 check-report 가 옛 버전 리포트를 «정합»으로 통과 | **1** (b3). 보존된 check-report 출력 72개 안에서는 **0**(버전 불일치 0/72) | 실해 0. 2.18.2 check-report 가 2.18.1 5차 리포트(`a4dd44f012a6`)를 «정합»으로 통과시켰고(00:01 KST), 15분 뒤 명세 개정으로 2.18.2 재예보가 돌았다(`:1094`) | `docs/superpowers/orders/lane/REPORT-fortune-house-b3.md:25`(출력은 `/tmp` 로그라 저장소에 없음) |
| 툴체인 교체 계열 STOP(참고) | 6: fortune-reading 3 · a12 2 · b3 1 | 모두 **registry 판 고정·캐시 교체** 문제다. pre-gate 최신성과 무관하고 S-4 로 막히지 않는다 **[추론]**. b3 는 2.18.1 툴체인을 `/tmp` 에 재구성해 G1 턴을 마쳤다 | `STOP-fortune-record-a12-dddjango-2-18-2-cache.md:1-12` · `STOP-fortune-house-b3-plugin-version.md:1-12` · `STOP-fortune-reading-toolchain-path.md:1-4` · `REPORT-fortune-house-b3.md:36` |
| 노출 창 | 스크립트가 바뀐 릴리즈 = 2.17.12~2.18.3 의 13회(09-01~09-11). 그 창의 24 실행 중 5 실현. 2.18.3(09-11 23:04) 이후 55 실행은 **0** | 2.18.3 → 2.18.4 는 스크립트 변경 0(`git diff` 0파일)이고 digest 가 같다 | registry 툴체인 행: `20260925-2203-teller-content-price-room/pregate-run-9.txt:17`(v2.18.3 · `148a9fa2193abb69`) = `20260926-1413-consultation-design-server/g2-registry-gate-final.txt:2`(v2.18.4 · 같은 digest) |

- 해석
  - 설치본 교체는 릴리즈 시각보다 늦다. b3 는 2.18.2 릴리즈 34분 뒤에 G1 을 2.18.1 로 돌렸다. 그래서 «릴리즈 창 안의 실행»은 과대 추정이다. 창 기준으로는 10 실행이 노출됐지만 실현은 5다.
  - 버전 문자열이 아니라 digest 로 판정해야 한다. 2.18.4 같은 문서만 바뀐 릴리즈를 stale 로 오판하지 않는다.

### 2.2 F4-23 — `--base`≠HEAD 재발화 + dirty overlay 혼합 사본

| 항목 | 사건 / 분모 | 비용 | 대표 근거 |
|---|---|---|---|
| 전제: 명시 `--base` 절 | 226/517 절 · 45/79 실행. 그 시각에 기준선≠HEAD 로 추정되는 것은 188 절 · 36 실행이고, 그중 169 절은 기준선 이후 제품 커밋 있음 **[추론]** | — | 방법 1.3 |
| 전제: dirty overlay | 보존된 명시 재발화 stdout 30 중 overlay>0 이 28이고, 기준선≠HEAD 를 겸하는 것이 ≥21. 예: b4 우회 재발화 overlay 273 · 367 | — | `20260912-1312-fortune-house-b4/s4-r22-pregate.txt:13` · `20260925-2203-teller-content-price-room/pregate-run-13.txt:13`(64) |
| 같은 블록 해시로 red → 뒤에 green | **1 사건 / 1 실행**(h1) · 거짓 red **24**(#488 ×22 · #569 ×2 · 전부 S1 커밋 `a1e1635b` 골격) | 재발화 1회 · 약 30분(02:12 → S2 커밋 02:39 → 02:42 green). **오처분 0**(처분 없이 커밋 뒤 재실행) · **STOP 0**. 앞선 F4-22 STOP 처리(명세 rename → 재예보)가 이 red 를 불렀다(연쇄) | `20260916-2112-rag-service-library/pregate-report.md:200-235` → `:291-298` · `REPORT-rag-service-library-h1.md:97` |
| 문자 기준 «귀속 red 경로가 기준선 이후 레인 커밋 파일» | 77 절 · 409 항목 발생 · 8 실행. 그러나 377은 clean G1(`--base HEAD`)에서도 같은 ID 로 red 였다(스텁 본래 한계 · 예: counter-room #473 ×5 가 41절 반복, 206 발생). 나머지 32 = h1 24 + #376 스텁 6 + #307 명세 개정 2 → **F4-23 서명은 h1 24 뿐** | 377건은 S-3 로 바뀌지 않는다(E1 설계대로 커밋분은 사본 밖 → 스텁) **[추론]** | counter-room `pregate-report.md:1354-1362`(«빈-스텁 한계» filtered) |
| 신규 BC 이면서 재발화 한 실행(골격 가드 오판 노출) | 5 실행 · 38 절(fortune-house 0904 · library-b0 · rag h1 · fortune-employee · teller-8a) → 실현 1 | — | 방법 1.3(`git ls-tree -d <base> application/<bc>` 공백) |
| 관련 변종(기준선 이후 **커밋분** 부재 → 거짓 계약 결손) | 1 실행 · 결손 1 | **filtered** 로 처분(«S7/S8 사각»)했고, r3 에서 file-plan 에 update 3행을 넣어 사본에 억지로 싣는 방식으로 명세를 비틀었다. **S-3 으로 닫히지 않는다**(오버레이가 아니라 E1 설계) | `20260904-2109-fortune-house/pregate-report.md:554` · `:606` |

### 2.3 F4-22 — #574(use case 의 `<data>_in` 생성)를 G1 에서 못 잡음

| 항목 | 사건 / 분모 | 비용(반송·슬라이스·명세 개정) | 대표 근거 |
|---|---|---|---|
| pre-gate 가 #574 를 예보한 절 | **0 / 517**(예보 항목 0 · 선언 확정 0) | — | 방법 1.3 |
| G1 **green** → 구현 뒤 #574 | **4 / 79** | 아래 4행 | — |
| ① fortune-catalog(09-03) | `RelationQueryIn` 1 | S3 뒤 정합 커밋 1(12파일 +32/−85) · 명세 6절(§2/4/5/10/12/13) 개정 · STOP 0 | G1 green `20260903-1214-fortune-catalog/pregate-report.md:143` · `git show 75e3672ab` · `REPORT-fortune-catalog.md:48,57` |
| ② fortune-character-b5(09-12) | 요청 DTO `_in` 1 | S3 에서 architect (b) primitive 로 명세 개정 · 요청 DTO 제거 · STOP 0 | G1 green `20260912-0554-…/pregate-report.md:79` · `design-spec.md:198` · `REPORT-fortune-character-b5-prompt-variables.md:18` |
| ③ fortune-house-b7(09-14) | `FortuneFailureIn` 1(S4 registry) | coordinator 가 최소 정합을 배차했다. coder 가 포트 시그니처·fake·ACL 을 고치고 architect 가 계약을 동기화 · STOP 0 | G1 green `20260913-2323-fortune-house-b7/pregate-report.md:332` · `s4-introduced-final.json`(`#574` 레코드 ts 2026-09-14T03:28:33Z) · `s4-architect-report.md:138-146` |
| ④ rag h1(09-17) | `GraphTripleIn` · `UpstreamFetchArguments` 2(S2 registry blocker) | **STOP 1** · 발주서 §9 개정 4 · architect 명세 rename · pre-gate 재발화(→ F4-23 거짓 red 24) · coder rename 2파일 · 재검증 | G1 green `20260916-2112-rag-service-library/pregate-report.md:157` · `STOP-rag-service-library-h1-in-out-naming.md:7-14` · `git show -s 95bb7574c` |
| G1 이 #574 를 예보하지 않음(다른 red 는 filtered) → 구현 뒤 #574 | **+2 → 넓은 기준 6 / 79** | 아래 2행 | — |
| ⑤ decisive-fortune-chart-storage(09-07) | `ChartRequestIn` 1 | S2~S4 커밋 안에서 교정(포트가 도메인 VO 수령) · 명세 갱신 커밋 1 · STOP 0 | G1 red 3(#160/#484/#355) `…/pregate-report.md:408` · `HANDOFF-decisive-fortune-1.md:11` · `git show 2b4edcab7` · `819e4e008` |
| ⑥ fortune-house-counter-room(09-20) | 포트 입력 `_in` 3파일(2 포트) | S3b2 에서 명세 개정(블록 해시 → `e4b29300324b`) · `_in` 3파일 삭제 · 도메인 VO 4 신설 · ACL 2 배선 이관 · 뒤에 산문 정합 커밋 1 | G1 red 5(#473 스텁) `…/pregate-report.md:136` · `:1354` · `git show 452e988e3` · `4b7c0c789` |
| pre-gate 도입 전 이력(참고) | 2: fortune-reading(09-01 · `ReadingBundleIn` · `TranslateQueryIn`) · openai-rag-generation(08-27 · 분모 밖) | fortune-reading: registry STOP(귀속 28 중 #574 ×2). openai: 설계 loopback G1″ | `STOP-fortune-reading-p2-registry-contract.md:4,28` · `20260827-0328-openai-rag-generation/design-loopback-g1-doubleprime.md:35` |

- 진단의 «이력 4회»와 대조하면 엄격 기준(G1 green) 4건과 일치한다. 넓은 기준은 6, 파이프라인 전 이력은 8이다.
- 6건 모두 S-2 술어에 해당한다 **[추론 — 커밋·REPORT 문면 기준, 재실행 안 함]**. 술어는 «포트 메서드 **인자**가 `_in` 이고 어떤 포트도 그것을 반환하지 않음»이다.
- 교훈이 수동으로 퍼졌는데도 재발했다. catalog REPORT(09-03)의 «설계 진화 #574» 뒤 fortune-house(09-04) 리뷰가 «#574 ✓»를 체크했다(`20260904-2109-fortune-house/s0-g1-review-discipline.md:18`). 그 뒤에도 5건(⑤ 09-07 · ② 09-12 · ③ 09-14 · ④ 09-17 · ⑥ 09-20)이 더 났다.
- 발생 간격은 09-03 · 09-07 · 09-12 · 09-14 · 09-17 · 09-20 으로 약 3일에 1건이다.

### 2.4 F4-21 — 승인 main 머지 유입을 «기준선 이후 실존» 형식 red 로 처리

| 항목 | 사건 / 분모 | 비용 | 대표 근거 |
|---|---|---|---|
| 형식 red «update 대상 기준선 이후 실존» | 3 절 / 2 실행 → **승인 머지 유입 1**(b4 · `tests/test_search_term_mapping.py` · 타 레인 `11665bf24` 커밋이 main 경유로 들어옴) · 자기 기실현 add 2(counter-room · 자기 S3b2 커밋 `452e988e3` 이 추가한 파일을 update 로 적음 · 각각 4분 뒤 재예보) | b4: **STOP 1**(89행) · 발주서 개정 22(우회 1회 승인) · 개정 23(우회 1회 추가 승인) · provenance JSON · architect 메모 · 규율 리뷰 | `20260912-1312-fortune-house-b4/pregate-report.md:3549` · `s4-r21-pregate.txt:4-6` · `STOP-fortune-house-b4-s4-pregate-approved-inflow-update.md:3` · `docs/superpowers/orders/2026-09-12-fortune-house-b4-input-bundles.md:180,193` · counter-room `pregate-report.md:1783,4246` |
| approved-merges.txt 가 있는 실행 | **15 / 79**. 09-22 이후 14 실행 중 11(«G2 직전 main→lane» 관행) | 12개는 머지 뒤 재발화 없이 G2 check-report 가 머지 전 리포트를 «정합»으로 통과했다(설계대로 · 판정은 registry `--approved-merge-file`) | 예: `20260922-1714-chat-relay-room-close/g2-postmerge-pregate.log:1-7`(Merged HEAD 68489fe5 · 기준선 f6e3ba60) |
| main 머지 뒤 pre-gate 재발화 | **5 실행**. 승인 목록 15 중 3(accounts-1 · b4 · b6) + 목록 없는 머지 1(b1) + 머지 커밋으로 기준선 이동 1(graph-slots · 구현 전 · 발주서 D21) | — | b4 `pregate-report.md:2572-3803` · accounts-1 `:189` · b1 `:405` · graph-slots `:850` |
| 우회(`--base` = 머지 부모 M^2) | **3 실행**. b1 `507f68af`(09-11) · b4 `97cdb35f`(09-12) · b6 `0570592b`(09-13 · 별도 리포트) | b4 이후 우회가 발주서 문면으로 사전 승인됐다(b4-2 · b6 발주서) | b1 `20260911-1601-…/pregate-report.md:405-407` · b4 `:3559` · `:3803` · b6 `s4-postmerge-pregate-report.md:1817-1824` · `docs/superpowers/orders/2026-09-13-fortune-house-b4-2-legacy-cards.md:82` · `2026-09-13-fortune-reading-b6-search-terms.md:232` |
| 우회로 레인 자기 커밋이 사본에서 빠졌는데 check-report 통과 | **2 실행 · 5회**. b4 3회(기준선 `97cdb35f958e`) · b6 2회(`0570592b7fa5`). b1 은 check-report 출력 보존 0(측정 불가) | 빠진 레인 커밋: b4 3커밋/제품 204파일 · b6 4커밋/97파일 · b1 2커밋/96파일. 대신 들어온 main: 93 · 73 · 33 커밋 | `20260912-1312-fortune-house-b4/s4-r22-check-report.txt:3` · `s4-r23-check-report.txt:3` · `s4-r23-gate-check-report.txt:3` · `20260913-0841-fortune-reading-b6/s4-postmerge-check-report.log:5` · `s4-postmerge-final-check-report.log:5` |
| 유입 파일이 사본에 없어 생긴 거짓 계약 결손(형식 red 이전 판) | 1 실행(accounts-1 · 2.17.16 관찰 모드) · 결손 4~5 | coordinator 가 «예보 기준선 낡음(도구 한계)»으로 corrected 처분했다 | `20260903-2250-accounts-1-saju-input/pregate-report.md:297-302` · `:383` |

- 해석 **[추론]**: «우회가 레인 자기 커밋을 뺐다»는 말은 원 G1 기준선에도 똑같이 성립한다(E1 설계: 기준선 이후 커밋분은 사본 밖). 우회가 실제로 바꾸는 것은 두 가지다.
  - main 유입분(33~93 커밋)이 사본에 들어간다.
  - check-report 가 G1 SHA 가 아닌 기준선을 표시만 하고 대조하지 않는다.

## 3. 우선순위에 주는 함의

| 결함 | 실현 사건(/79) | 실현 비용 | 수리 비용(진단) | 캠페인 노출 **[추론]** |
|---|---|---|---|---|
| digest | 툴체인 교체 5 · 헛 통과 1 · 실해 0 | 거의 0(관련 STOP 6 은 registry 판 고정 문제라 범위 밖) | 스크립트만 · 저위험 | 캠페인 중 스크립트 변경 릴리즈 1회마다 진행 중 레인(파동 규칙상 ≤3)이 노출 |
| F4-23 | 1(거짓 red 24) · 변종 1 | 재발화 1회 · 약 30분 · 오처분 0 · STOP 0 | 스크립트만 · 저위험 | 골격 가드 오판은 신규 BC 조건이라 기존 BC 리팩터 레인에서는 드묾. 전제(명시 재발화 + dirty)는 흔함 |
| F4-22 | 엄격 4 · 넓게 6 | 6건 모두 명세 개정 + 코드 재작업 · STOP 1 · 발주서 개정 1 · F4-23 연쇄 1 | 스크립트(선언 검사 1종) + 선택 graph-owned | 캠페인 빚의 #574 는 0(진단). 다만 포트를 재설계하는 리팩터면 새로 생길 수 있음 |
| F4-21 | 형식 red 1 · 우회 3 · 우회 check-report 통과 5회 · 거짓 결손 1 | STOP 1 · 발주서 개정 2 · 우회 사전 승인 문면 2 | 가장 큼(스크립트 + graph-owned + 미러) | 파동 규칙이 머지 노출을 줄임. 09-22 이후 머지는 «G2 직전 1회» 관행이라 재발화가 드묾(15 중 3) |

- **지지되지 않는 부분**
  - «digest 1순위»의 근거인 «모든 레인 G1 예보의 G2 유효성 보호»는 현장에서 헛 통과 1건 · 실해 0 으로만 관측됐다.
  - 2.18.3 이후 55 실행은 툴체인 변경 0 이다. digest 의 가치는 캠페인이 **도중에 스크립트 변경 릴리즈를 할지**에 전적으로 달려 있다.
  - 진단이 인용한 S2 수리 묶음(plan-v2 `:29`)이 캠페인 중에 나간다면, 그 한 번에 대한 싼 보험으로 정당하다.
- **뒤집히는 부분**
  - F4-22 는 실현 빈도와 비용 모두 1위다. 6/79 이고, 매번 명세 반송과 재작업이 났다.
  - 수동 교훈(09-03) 뒤에도 5회 재발했으므로 문서 공유로는 안 막힌다는 증거다.
  - F4-23 은 전제가 흔해도 실현은 1회였다. 그 1회도 F4-22 가 부른 연쇄였다. F4-22 를 먼저 닫으면 F4-23 의 유일한 현장 사례 경로도 줄어든다 **[추론]**.
- **F4-21**
  - 형식 red 빈도로는 최하위다.
  - 그러나 «check-report 가 기준선 치환을 못 봄»은 5회 실현됐다. 이 가시성 결함은 진단 §2 정정 2 · §6-4 의 권고(발주서 1행 또는 check-report 기대 기준선 대조)만으로 싸게 막을 수 있다.
  - 전체 S-1 은 뒤로 미뤄도 수치와 모순되지 않는다.
- **수치가 가리키는 묶음 [추론]**
  - 1순위 묶음(스크립트만 · 한 릴리즈): **F4-22(S-2) + digest(S-4) + F4-23(S-3)**
  - 2순위: F4-21 의 check-report 기대 기준선 대조(가시성)
  - 3순위: F4-21 본체(S-1 + G-1)
  - digest 를 단독 1위로 둘 근거는 «캠페인 도중 릴리즈 계획»이 확정될 때만 생긴다.

## 4. 측정 한계

- **HEAD(T) 추정 [추론]**: 레인이 `.dddjango/<run>` 을 건드린 커밋으로 추정했다. 경로 이력 단순화 때문에 머지 커밋이 빠진다. b4 · b6 의 우회 재발화는 이 추정에서 «기준선=HEAD»로 잘못 잡혔다. 그래서 188 절 · ≥21 은 하한이다.
- **dirty overlay**: 리포트 본문에는 overlay 수가 남지 않는다. stdout 캡처(74개 · 명시 30개)에만 있다. 나머지 명시 재발화의 dirty 여부는 측정 불가다. fortune-house(0904 · 신규 BC · 재발화 25절)에서 골격 오판이 없었던 이유(clean 이었는지)도 stdout 이 보존되지 않아 측정 불가다.
- **F4-23 의 미탐 방향**(오염된 L 이 진짜 위반을 L∩N 으로 숨김): 현장 증거로는 원리적으로 측정 불가다.
- **check-report**: 보존 출력 72개만 대조했다. `/tmp` 로그(b3 등)와 레인 문서에 문장으로만 남은 실행은 문면으로만 셌다.
- **버전 스탬프**: 스탬프 이전 절 64개(2.17.15 이전 추정)는 버전을 읽을 수 없다. fortune-reading(0831)의 예보 판은 측정 불가이고, 교체 사실은 registry STOP 문서로만 셌다.
- **#574 탐지 경로**: 커밋 메시지 · REPORT · 감사 문서로 확인했다. `violations/*.jsonl` 에는 #574 레코드가 0 이다(레인 registry 가 sink 를 쓰지 않은 것으로 보임 · 측정 불가). S-2 가 6건을 모두 잡았을지는 재실행 없이 문면으로 판단했다 **[추론]**.
- **비용 단위**: STOP · 발주서 개정 · 커밋 · 파일 수 · 경과 시각만 셌다. 사람 시간과 토큰은 측정 불가다.
- **워크트리**: 레인 문서 차이분(웹 레인 11개 등)은 `.dddjango-web` 소관이라 범위 밖이다. `.dddjango/` 는 전용 폴더 2개 외에 메인과 동일하다.
- **작업 스크립트**: 집계에 쓴 스크립트는 세션 scratchpad 에만 있다. 재현은 §1 의 명령 · 정규식 · 판정 절차로 한다.
