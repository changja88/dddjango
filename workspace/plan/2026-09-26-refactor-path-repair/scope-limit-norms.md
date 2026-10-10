# 적용 범위 한정·보존 규범 전수 분류 — 리팩토링 모드 Override 대상 (2026-09-27)

- 목적: Coordinator «리팩토링 모드» 절의 Override 규범이 `djr:overrides` 로 가리킬 규범을 **전수**로 정한다(적대 검토 M `review-M-step5-v4.md` M-B1 고칠 것 1). `check-verdict` 가 쓸 **적용 한정 어구 닫힌 목록**도 함께 낸다(M-B1 고칠 것 2).
- 분류: **T** = 리팩토링 모드의 BC 점검·슬라이스 0 에서 통째로 풀리는 적용 한정·보존 규범(리뷰어 행동 범위 조항 포함) · **T\*** = 풀리는 몫과 남는 몫이 한 규범에 섞인 경계 사례 · **N** = 대상 아님(외부 계약·동작 / 절차 / 무관).
- 표기: `—` = 한정 어구가 없는 표준 규범(분류 대상 아님). «후보» = 라벨 정규식 후보 302건 · «보강» = 본문 grep·restates·검토 거명으로 더한 것.
- **재검토 N 반영(09-27 · `review-N-step5-v5.md`)**
  - 대상 **56**: R-3226·R-0186 은 사본 정정으로 N 장부(표 2 끝)로 내렸다(N-m7).
  - 대상을 적용 몫 ⑴ 43 / ⑵ 13 으로 가른다(«적용 몫» 절 · R-0284 는 ⑵ — N-M1·표본 4).
  - 어구 판정을 **인용이 든 문장** 단위로 바꾸고 C 목록을 걷었다(N-M3). A 목록은 40(#40 걷음 — N-m7).
  - 라벨 드리프트 식을 박고, 첫 대조 미분류 3건(R-0408·R-1015·R-3482)을 N 으로 넣었다(N-m3). N 은 361 이 된다(356 + 3 + 사본 정정 2). 로드맵 5 구현 뒤 G12 첫 대조에서 신설·개정 13건(R-3471 · R-3517 · R-3519 · R-3526 · R-3534 · BC_AUDIT 8)을 N 절차로 더했다(374). 속도 개선 K2b(2026-10-01) G12 대조에서 신설·개정 5건을 N 절차로 더했다(379). 속도 개선 K3(2026-10-01) G12 대조에서 신설·개정 13건을 N 절차로 더했다(392 — R-2614 · R-3323 · R-3368 는 표 1 의 T 라 비고만 달았다). 속도 개선 C7(2026-10-01) G12 대조에서 신설·개정 1건을 N 절차로 더했다(393). RD(리팩토링 정의 변경 · 2026-10-04) G12 대조에서 신설 7건(R-3620 · R-3621 · R-3623 · R-3631 · R-3634 · R-3646 · R-3651)·개정 3건(R-3470 · R-3537 · R-3587 — 라벨이 바뀌어 새로 적중)을 N 절차로 더했다(403 · 적용 범위 Override 대상 56 무변).
  - 표 2 사유 오기 2건(R-1030·R-3408)을 고쳤다(N 표본 14·18).
  - 아래 건수 요약·표 1 은 분류 당시 값이다(표 1 의 두 행은 «→ N» 표시).

## 건수 요약

| 구분 | T | T\* | T+T\* | N |
|---|---|---|---|---|
| 후보 302건 | 23 | 12 | 35 | 267 |
| 보강 | 12 | 11 | 23 | 61 + 묶음 28 |
| **합계** | **35** | **23** | **58** | **356** |

- `djr:overrides` 대상 = **T+T\* 58건**(표 1 전부). T\* 는 대상에 넣는다. 남는 몫이 걸린 항목은 제외 검사 ③ 이 T\* R-ID 를 통째로 막고 별도 요청으로 나간다(표 1 비고 · 재검토 N 뒤 대상 56).
- 문서별 T+T\*:

| 문서 | T | T\* | 문서 | T | T\* |
|---|---|---|---|---|---|
| commands/dddjango | 1 | 5 | discipline-houserules/SKILL | 4 | 6 |
| agents/discipline-reviewer | 7 | 2 | discipline-houserules#final | 2 | 1 |
| agents/design-architect | 3 | 4 | implementation-django-ninja#final | 5 | 3 |
| agents/coder | 2 | 1 | implementation-django#final | 2 | 1 |
| agents/design-review-ddd | 2 | 0 | implementation-django/SKILL | 1 | 0 |
| agents/design-review-api | 1 | 0 | architecture-ddd#final | 4 | 0 |
| agents/design-review-db | 1 | 0 | 그 밖 14문서(api·db·cleancode·tdd·test·python·web·ninja SKILL·acceptance-tester) | 0 | 0 |

- 문서별 후보 302건의 N: Coordinator 46 · ninja final 27 · DR 24 · architect 18 · houserules SKILL 16 · coder 15 · tdd final 14 · acceptance-tester 13 · api-reviewer 12 · test final 12 · api final 11 · django final 11 · ninja SKILL 7 · web final 6 · api SKILL 5 · 나머지 12문서 30.
- N 사유 분포(후보 267 + 보강 61 = 328행 · 묶음 제외): 절차 119 · 무관 110 · 외부 계약·동작 84 · 동작 보존·원칙(테스트 고정) 15.

## M-B1 거명 규범의 판정

| R-ID | 판정 | 한 줄 |
|---|---|---|
| R-0965 · R-0982 · R-0123 · R-0125 | T | touched·diff·신규 판정 한정 — 전부 대상 |
| R-0674 | T\* | 함수형 형태 보존(풀림) / 확립 wire 표면(남음) |
| R-0696 · R-0697 · R-0673 | T | «신규 표면»·«기존 형태 보존» 한정 |
| R-0698 | T\* | touched 한정(풀림) / 승인 evidence 함수형 표면은 그 기록 관할(남음) |
| R-1058 · R-1059 · R-3420 · R-1137 | T | BC_AUDIT 해제 조항(diff 한정·기술 정확성 경계) |
| R-1140 | T\* | «보지 않는다»(풀림) / 쿼리·ORM 관용구는 db 렌즈 소유(남음 — 결정 12) |
| R-3368 · R-3323 · R-2614 | T | 구현 코드 열람 금지 — BC_AUDIT 해제 |
| R-3226 | T\* | «리팩터링 대상 = 백스톱 위반» 한정 — m7 대로 사본 셋을 고치면 N 으로 내릴 수 있다(같은 정의의 Coordinator 사본 R-0186 도 T\*) |
| **R-1057** | **N** | 승인 test artifact 의 «기존 테스트 위치»는 houserules §1 «관찰이 결정 입력인 축» ⑤ — 표준 자체의 선택지(대체 표준 없음). 레이아웃 혼용(R-3127)만 위반 |
| **R-0715** | **N** | 소비자 의존 API 인스턴스 보존 — URL·문서 wire(외부 계약). 동작 불변 정리로 바꿀 수 없다 |
| R-3403 · R-0675 · R-0699 | N | 같은 블록 형제지만 함수형 채택·강등을 막는 쪽 — 표준과 같은 방향 |

## 방법

1. **정규식 후보 302건**(`cands.tsv`)마다 rulepack `works[R].block` 으로 블록을 찾고 그래프(`ontology/rules/*.ttl` · rdflib)의 블록 원문(`djr:text` — 배포 md 블록과 같은 본문)과 형제 규범 라벨을 함께 읽어 규범 문면으로 판정했다. 한 블록 다규범이면 그 규범 라벨에 대응하는 문장을 짚어 판정했다.
2. **본문 grep 보강** 세 번:
   - ① `touched·untouched·grandfather·이번 작업·이번 diff·새로 들어온·새로 얹·신규 표면·신규 산출·레거시·legacy·기존 코드/배치/형태/앱/파일/줄/테스트/리터럴·확립·손대는·손대지·brownfield·존중·면제·소급·동결·답습·스코프 밖·새 코드·새 테스트` — 미판정 규범이 있는 블록 158개.
   - ② `이미 있·기존 …(따른|우선|유지|보존|존중|그대로)·관례·established·preserv·greenfield·그대로 둔·고치지 않·옮기지 않` — 새 블록 76개.
   - ③ `새 (표면|surface|모듈|파일|코드|컨트롤러|자료 …)·새로 (만드|쓰|노출|얹)·처음 생기·이번 (슬라이스|delivery)` — 새 블록 9개(해당 없음).
   - 보강으로 T/T\* 23건 · N 61건 · 묶음 N 28건(preserve-established 오류 wire slot 기록)을 더했다. 검토 M-B1 이 거명했으나 정규식이 놓친 R-1137·R-1140·R-3368·R-3323·R-2614·R-3226 도 여기서 들어왔다.
3. **restates 연쇄**: T/T\* 블록을 `djr:restates` 로 재진술한 블록(들어오는 쪽)과 T/T\* 블록이 재진술한 블록(나가는 쪽)의 규범을 전부 확인했다(아래 절). 연쇄로 새로 잡힌 T/T\*: R-2878(implementation-django SKILL → §4.1·§3.2 재진술) · R-0792(ninja §6.3 → §2.3 재진술) · R-1201 · R-3387.
4. **NAR(그래프 밖 산문)**: 배포 md 에서 위 어구가 든 줄 가운데 어떤 그래프 블록 본문에도 없는 줄은 24줄이다 — `REQUEST_GUIDE.md` 11줄(사용자 안내문) · cleancode·tdd·python 의 «레거시» 제목·참고 표기·Factory/Strategy 패턴의 OCP 설명 · houserules final 제목 1줄. 적용 범위를 한정하는 문장은 없었다.
5. 분류 기준 적용 원칙:
   - 한정 어구가 **적용 대상**을 신규·touched·diff·이번 작업으로 좁히거나 기존 코드·형태·배치를 보존·면제하면 T(종류 무관). 트리거로 쓰인 «새 판정이 얹히면»·«처음 생기는 슬라이스» 도 오탐 인용 통로라 T/T\*.
   - «관찰이 결정 입력인 축» 닫힌 목록 여섯(houserules SKILL §1 — R-3134: ① 오류 wire 계약 ② API 스택 정체 ③ 주석 언어 ④ 도구·러너 ⑤ 승인 test artifact 의 기존 위치 ⑥ 지원 중 행동 계약)에서 «기존 관례를 따른다» 류는 **표준 자체의 선택지**라 N(풀어도 대체 표준이 없다). 스택 교체는 확립 스택 STOP(사용자 승인) 사안이라 N(절차).
   - «스코프 밖 기존 코드를 옮기지 않는다» 류는 두 몫으로 갈랐다 — «신규 산출물 한정» 문장(T 몫)과 «이동 권한 = G0 ⓐ→슬라이스 0» 문장(N 절차). 리팩토링 모드도 이동은 G0 ⓐ→슬라이스 0 한 경로이기 때문이다. 판정(verdict) 시점에 «스코프 밖»을 제외 근거로 쓰는 통로는 막아야 하므로, 두 몫이 한 규범에 있으면 T\*, 이동 경로만 말하면 N(R-0183·R-1651·R-2573·R-2589·R-3120·R-3495·R-0844·R-1060).
   - 테스트 «형태» 규범(«새 테스트는 pytest»·«기존 TestCase 스위트 재작성 금지»·«기존 비계 삭제 금지»)은 사용자 원칙 «리팩토링은 기존 테스트 충분 가정 — 테스트 보수를 넣지 않는다»와 0T 창(배치·이름만)에 맞춰 N(동작 보존·원칙)으로 뒀다(경계 — 아래 한계 3).

## 한계

1. **블록 → 규범 문장 대응은 사람 판단이다.** 그래프는 규범별 원문을 따로 갖지 않는다(블록 원문 + 라벨). 다규범 블록(최대 26규범)에서 한정 문장이 어느 R-ID 몫인지는 라벨로 짚었다. 같은 블록에 한정 문장이 있어도 라벨이 다른 몫을 말하는 형제는 N 또는 `—` 로 뒀다(예: R-0983 «테스트 격리 전용 설정 통과»는 R-0982 와 같은 «예외:» 문장이지만 `—`).
2. **검사기 쪽 결속은 블록 단위다.** 그래서 어구 판정은 **인용이 든 문장** 단위로 한다(재검토 N-M3 — 블록 단위나 인용 문자열 단위는 같은 문장의 부분 인용과 형제 허용·예외로 비껴간다). T\* 의 남는 몫은 제외 검사 ③ 이 T\* R-ID 를 통째로 막고, 그 항목은 별도 요청으로 나간다. 그래서 어구 예외 목록(옛 C)은 걷었다.
3. **N 으로 둔 경계 판단**(caller 재확인 권고):
   - 테스트 형태 7건 — R-0263 · R-0941 · R-1304 · R-2521 · R-3311 · R-1354 · R-3310. D4 §3-4 «테스트 코드의 구조 위반(배치·이름 등)은 항목»의 «등»을 넓게 읽어 TestCase→pytest 전환을 항목으로 본다면 T 로 올려야 한다. 그 전환은 0T close 의 «케이스 이름 불변»에서 red 가 난다(`behavior_guard.py` 0T 판정).
   - 확립 스택 5건 — R-0180 · R-1645 · R-0821 · R-1230 · R-2950. DRF·plain → Ninja 전환을 리팩토링 항목으로 보려면 T 로 올려야 한다. 지금 문면은 확립 스택 결정 자체가 STOP(사용자 승인)이다.
   - 관례 위임 — R-2299 · R-2300 · R-2301(static) · R-2296(template 들여쓰기) · R-0661(API namespace·versioning — URL wire) · R-0754(인증 메커니즘). 또 R-1057 · R-3125 · R-1691(기존 테스트 위치 — 축 ⑤) · R-3159~R-3161 · R-1065(주석 언어 — 축 ③)도 여기에 든다.
4. **단어 기반 grep 의 사각**: 한정 뜻을 조사·어미로만 표현한 문장(예: «…할 때만», «…인 경우») 가운데 위 어구를 전혀 쓰지 않는 것은 못 잡았을 수 있다. 세 번째 grep(새 블록 9개)에서 새 T 는 0건이었다.
5. **Codex 미러**: 이 분류는 Claude 정본(그래프·`dddjango/`) 기준이다. Codex 의미 미러의 같은 문장은 R-ID 가 같으므로(그래프 공유) 목록은 그대로 쓰되, 어구 문자열은 Codex 본문에서 표기가 다를 수 있다(M-M3).
6. (정리됨 — 재검토 N-m7) 설계 v5 가 사본 셋을 고치므로 R-3226·R-0186 은 N 장부로 내렸다(표 2 끝).

## 표 1 — T · T\* 전부 (58)

| R-ID | 종류 | 문서 §절 | 라벨 | 한정·보존 어구 원문 | 분류 | 비고(T\* 이면 풀리는 몫 / 남는 몫) | 출처 |
|---|---|---|---|---|---|---|---|
| R-2499 | Obligation | agents/coder ·s004 | 신규·touched BC 의 final.md §0·§1 골격 실현(고정·재등장 칸은 빈 \_\_init\_\_.py·빈 파일) | «승인 스코프의 BC 를 새로 만들거나 touched 하면» | T | touched = G0 스코프의 그 BC — 리팩토링 대상 BC 는 정의상 충족(오탐 인용 차단용) | 후보 |
| R-2572 | Exception | agents/coder ·s004 | 이 표준의 관할 = 승인 스코프가 낳는 산출물(신규 파일·기존 파일에 추가되는 줄) 한정 | «이 표준의 관할은 승인 스코프가 낳는 산출물(신규 파일·기존 파일에 추가되는 줄)이다» | T |  | 후보 |
| R-2586 | Prohibition | agents/coder ·s004 | preserve-established 의 승인 native controller/Router/handler form 변경 금지 | «승인된 native controller/Router/handler form을 바꾸지 않는다» | T* | 풀림: native controller/Router «형태»(함수형→클래스) / 남음: handler·오류 wire 산출물 보존(R-2552 — preserve 는 오류 wire 까지) | 보강 |
| R-1647 | Obligation | agents/design-architect ·s005 | 새 Ninja surface 의 NinjaExtraAPI·class controller 와 profile 별 단일 project API instance | «새 Ninja surface는 `NinjaExtraAPI` + `@api_controller`» | T | «새» 한정만 풀림 | 보강 |
| R-1650 | Prohibition | agents/design-architect ·s005 | 승인 스코프 밖 기존 파일의 이동·개명·재배선 결정 금지 | «이 문장들은 **신규 산출물의 형태**를 정할 뿐 **기존 코드의 처분 권한**이 아니다» | T* | 풀림: 신규 산출물 한정 / 남음: 명세는 G0 ⓐ 승인 항목만 슬라이스 0 으로 옮겨 적는다(R-1651) | 후보 |
| R-1682 | Exception | agents/design-architect ·s005 | 표준 트리 문장의 신규 산출물 한정(스코프 밖 기존 배치 이동 지시 아님) | «(이 문장도 신규 산출물의 형태 문장이다 — 승인 스코프 밖 기존 배치의 이동 지시가 아니다» | T* | 풀림: 신규 산출물 한정 / 남음: 이동 지시는 G0 ⓐ→슬라이스 0 | 후보 |
| R-1688 | Obligation | agents/design-architect ·s005 | HTTP/CLI 진입 보유 BC 의 컨트롤러 메서드·schema 실현 | «컨트롤러 메서드(레거시면 함수형 operation)·schema를 실현한다» | T* | 풀림: «레거시면 함수형 operation» 형태 허용 / 남음: HTTP 진입 BC 의 표현 실현 의무 | 보강 |
| R-1713 | Exception | agents/design-architect ·s005 | 이주 지시의 판정 적재 코드 한정 | «이주 지시는 판정을 얹는 **그 코드**에 한하고» | T* | 풀림: «얹는»(이번 작업) 한정 — 이미 판정을 소유한 평면 코드도 이주 대상 / 남음: 판정 없는 코드는 판정 이주 근거 아님(§3.2 항-(2) 의미 기준) | 보강 |
| R-1714 | Exception | agents/design-architect ·s005 | 데이터소스 실내용 면제의 touched 코드 한정(무관 앱 불이동) | «데이터소스 실내용 면제(골격은 빈 패키지로 실현)는 *이번 작업이 touched한 그 코드*에 한정한다» | T |  | 후보 |
| R-1720 | Prohibition | agents/design-architect ·s005 | touched 데이터소스 앱 루트 평면의 답습 금지 | «*이번 작업이 touched(판정·쓰기경로 적재)한* 데이터소스 앱의 루트 평면은» | T |  | 후보 |
| R-2614 | Prohibition | agents/design-review-api ·s003 | 타 리뷰어 노트·구현 코드 열람 금지(명세만 근거) | «그 명세만 보고 다른 리뷰어의 노트나 구현 코드를 보지 않는다» | T | api 리뷰어 — BC_AUDIT 해제 조항(D4 §3-4) | 보강 · 속도 개선 K3 rev(2026-10-01) 라벨 개정으로 식 적중(«diff») — 분류 T 그대로 |
| R-3323 | Prohibition | agents/design-review-db ·s002 | 명세 한정 열람 — 타 리뷰어 노트·구현 코드 열람 금지(편향 방지) | «너는 그 명세만 본다 — 다른 리뷰어의 노트나 구현 코드를 보지 않는다» | T | db 리뷰어 — BC_AUDIT 해제 조항 | 보강 · 속도 개선 K3 rev(2026-10-01) 라벨 개정으로 식 적중(«diff») — 분류 T 그대로 |
| R-3368 | Prohibition | agents/design-review-ddd ·s002 | 명세 한정 열람 — 타 리뷰어 노트·구현 코드 열람 금지(편향 방지) | «너는 그 명세만 본다 — 다른 리뷰어의 노트나 구현 코드를 보지 않는다» | T | ddd 리뷰어 — BC_AUDIT 해제 조항 | 보강 · 속도 개선 K3 rev(2026-10-01) 라벨 개정으로 식 적중(«diff») — 분류 T 그대로 |
| R-3387 | Obligation | agents/design-review-ddd ·s004 | 평면 모델 위 판정 잔류 금지(항-(1)) 대조 | «판정을 얹는 코드를 평면 모델에 남기지 않았는가» | T |  | 보강 |
| R-0919 | Obligation | agents/discipline-reviewer ·s007 | 구현 체크리스트의 Phase 2 implementation 한정 적용 | «아래 나머지 구현 체크리스트는 **Phase 2 implementation에서만** 적용한다» | T* | 풀림: BC_AUDIT 에도 체크리스트 적용(입장 표·diff 전제 항목 제외 — D4 §3-4) / 남음: Phase 1 lightweight·DYNAMIC 모드 미적용 | 보강 |
| R-0962 | Prohibition | agents/discipline-reviewer ·s007 | 판정·불변식 보유 도메인 메서드의 평면 ORM 모델 직접 부착 금지(domain_layer 이주) | «새로 얹힌 판정·불변식을 담은 도메인 메서드가 평면 Django 모델» | T | «새로 얹힌» 한정만 풀림 — 평면 모델 판정 금지는 그대로 | 보강 |
| R-0965 | Exception | agents/discipline-reviewer ·s007 | touched 코드 한정 관찰(untouched 기존 리터럴 grandfather 면제) | «이번 작업이 touched한 코드만 본다 — untouched 기존 리터럴은 면제(grandfather)» | T |  | 후보 |
| R-0982 | Exception | agents/discipline-reviewer ·s007 | 이번 diff 신규 변경 한정 관찰(기존 코드 존중) | «이번 diff에 새로 들어온 변경만 본다(기존 코드 존중)» | T |  | 후보 |
| R-1058 | Obligation | agents/discipline-reviewer ·s007 | 대조 대상의 이번 diff(승인 스코프 산출물) 한정 | «이 대조의 대상은 **이번 작업의 diff(승인 스코프의 산출물)**다» | T |  | 후보 |
| R-1059 | Prohibition | agents/discipline-reviewer ·s007 | 범위 밖 legacy 잔존의 발견 불산입(빚 보고 채널·수리/이동 지시 금지) | «범위 밖 legacy 잔존은 발견이 아니라 빚 보고 채널이고» | T |  | 후보 |
| R-1137 | Prohibition | agents/discipline-reviewer ·s008 | 기술 특화 구현 정확성 비판정(규율 렌즈 한정) | «기술 특화 구현의 옳고 그름(Django/Python/ORM 관용구, 쿼리 정확성)은 네 몫이 아니다» | T | BC_AUDIT 은 python 규칙을 discipline 렌즈에 분담(결정 12) | 보강 |
| R-1140 | Prohibition | agents/discipline-reviewer ·s008 | 기술 구현 정확성(쿼리·ORM 관용구) 비관찰 | «기술 구현 정확성(쿼리·ORM 관용구의 옳고 그름)은 여전히 보지 않는다» | T* | 풀림: «기술 구현 정확성은 보지 않는다»의 BC_AUDIT 적용(D4 §3-4 «BC_AUDIT 은 예외») / 남음: 쿼리·ORM 관용구는 BC_AUDIT 에서도 db 렌즈 소유(결정 12) — DR 가 판정하지 않음 | 보강 |
| R-3422 | Obligation | agents/discipline-reviewer ·s002 | 캐스케이드 판정 의무 — ⓓ 신호·diff 파일의 ①/②/③ 판정과 반송 발견화 | «이번 diff 가 만들었거나 키운 파일에 대해 houserules §1 의 동명 폴더 승격 캐스케이드» | T |  | 후보 |
| R-0115 | Obligation | architecture-ddd#final §3.2 | 새 판정이 얹히는 코드의 domain_layer 애그리거트 이주(평면 모델 판정 금지) | «새 판정·불변식을 얹게 되면» | T | «얹게 되면» 한정만 풀림 — 평면 모델 판정 금지 의무는 그대로 | 보강 |
| R-0123 | Exception | architecture-ddd#final §3.2 | 골격 실현의 touched 한정(무관 기존 앱은 §4 존중) | «이 골격 실현은 *이번 작업이 touched한* 그 코드에 한정하며» | T |  | 후보 |
| R-0125 | Exception | architecture-ddd#final §3.2 | 이주의 신규 판정 한정(기존 배치 일괄 강제 금지 — 기존 배치는 빚) | «이 이주는 *판정이 새로 얹히는 그 코드*에 한정한다» | T | «무관·미관여 기존 코드를 표준으로 일괄 강제하지 않는다» 포함 | 후보 |
| R-3442 | Obligation | architecture-ddd#final §3.1 | 값 객체 자기 검증은 값의 불변식만 — 거부는 선언 타입의 하위 타입 값(bool⊂int)만 type(x) is \<하위 타입> 형 · 승격 값(float 자리 int) 거부 금지 · 신규 값 객체·손대는 줄에 적용 | «두 규범(R-3442·R-3443)의 적용 대상은 이번 작업이 새로 쓰는 값 객체와 **손대는 줄**이다» | T | R-3443 의 적용 한정도 이 문장이 진술(«소급 대상이 아니며 정리는 발주 소관») | 후보 |
| R-0182 | Prohibition | commands/dddjango ·s005 | «언제나 표준»의 관할 = 승인 스코프 산출물 — 스코프 밖 기존 배선 이동 금지 | «그 «언제나 표준»의 관할은 승인 스코프가 낳는 산출물(신규 파일·기존 파일에 추가되는 줄)이다» | T* | 풀림: 관할의 «승인 스코프 산출물» 한정(BC 점검은 기존 배선·배치를 항목으로 낸다) / 남음: 실제 이동은 G0 ⓐ→슬라이스 0(R-0183) | 후보 |
| R-0186 | Prohibition | commands/dddjango ·s005 | 새 검사 생성 금지(백스톱이 내는 위반이 곧 리팩터링 대상) | «「리팩터링 대상」의 별도 정의는 없다 — 백스톱이 내는 위반이 곧 그것이다» | ~~T\*~~ → N(사본 정정 · 재검토 N-m7) | 풀림: 리팩터링 대상 = 백스톱 위반 한정(BC 점검 의미 항목도 대상 — 결정 1) / 남음: Phase 0 빚 스캔에 새 검사를 만들지 않는다 | 보강 |
| R-0284 | Obligation | commands/dddjango ·s007 | 필수 입력 5종(코드+테스트·승인 입장 표·역할별 최소 조정 보고·test diff·실행 결과·슬라이스 목록) + ⓓ 후보 동봉(registry #4 200행 신호 · #11 #645/#647/#650) — 동봉 범위는 registry_gate 앵커 차분 ⓓ 신규분 | «두 채널 모두 동봉 범위는 registry_gate 가 앵커 차분으로 가른 **«ⓓ 신규(N′∖L′)»**» | T* | 풀림: ⓓ 후보의 앵커 신규분 한정(BC 점검은 ⓓ legacy 도 입력) / 남음: Phase 2 implementation 감사의 필수 입력 규정 | 후보 |
| R-0328 | Exception | commands/dddjango ·s007 | «면제가 아니다»는 신규 산출물 형태 문장 — 스코프 밖 기존 배선 이동 근거 아님 | ««면제가 아니다»는 신규 산출물의 형태 문장이다» | T* | 풀림: «신규 산출물» 한정 / 남음: «스코프 밖 기존 배선을 옮길 근거가 아니다» — 이동은 G0 ⓐ→슬라이스 0 | 후보 |
| R-0351 | Obligation | commands/dddjango ·s007 | registry #17 — 신규 ORM model `db_table`·타 BC FK 금지·`<Name>Model`·apps.py 결선 | «신규 managed ORM model 의 `db_table` 존재+값» | T* | 풀림: «신규» 한정 중 db_table 명시·`<Name>Model`·apps 결선·타 BC FK(기존 모델도 점검) / 남음: 기존 테이블명 «값» 보존(R-1279 — 데이터·마이그레이션) | 후보 |
| R-0352 | Prohibition | commands/dddjango ·s007 | registry #18 — touched direct Enum/choices literal consumption | «touched direct Enum/choices literal consumption» | T |  | 후보 |
| R-3188 | Obligation | discipline-houserules#final §0 | 골격의 실현 주체는 coder — 승인 스코프의 BC 를 새로 만들거나 touched 하면 고정·재등장 칸을 빈 채로라도 실현 | «승인 스코프의 BC 를 새로 만들거나 touched 하면(touched = G0 스코프의 그 BC» | T | 리팩토링 대상 BC 는 정의상 충족(오탐 인용 차단용) | 후보 |
| R-3226 | Obligation | discipline-houserules#final ·s014 | 「리팩터링 대상」을 따로 정의하지 않는다 — 백스톱이 내는 위반이 곧 그것이다 | «「리팩터링 대상」을 따로 정의하지 않는다 — **백스톱이 내는 위반이 곧 그것이다.**» | ~~T\*~~ → N(사본 정정 · 재검토 N-m7) | 풀림: 리팩터링 대상 = 백스톱 위반 한정 / 남음: 없음(형제 R-3227·R-3228 은 N) — review-M m7: 사본 셋 정정 시 대상에서 걷을 수 있음 | 보강 |
| R-3501 | Obligation | discipline-houserules#final §3 | 포트·조회 계약 메서드가 돌려주는 이름 붙인 자료는 \<data>_in(방향 기준점 = 우리 안쪽 · 원시 값·None 밖) · 이 규칙 이전 _out 반환 자료는 의미 빚 — 새 자료는 _in · 기존 _out 자료의 재사용은 허용 | «새로 만드는 자료는 이 규칙을 따르고, 기존 `_out` 자료를 새 메서드가 그대로 돌려주는 것은 허용한다» | T | «개명은 의미 빚 정리에서 한다» = 리팩토링 모드 | 후보 |
| R-3110 | Obligation | discipline-houserules/SKILL §1 | 새 코드·테스트 배치는 아래 결정 순서를 따른다 | «새 코드·테스트를 배치할 때 아래를 따른다» | T |  | 후보 |
| R-3117 | Obligation | discipline-houserules/SKILL §1 | 집행 스코프 판정 물음은 «승인 스코프에 근거가 있는가» — «내가 만들거나 수정하는가»가 아니다 | «판정 물음은 「이 파일(또는 기존 파일 안의 이 줄)을 낳는 근거가 승인 스코프» | T* | 풀림: BC 점검 항목 산출·판정에 이 물음 미적용 / 남음: 슬라이스 0 집행 스코프 = G0 ⓐ·슬라이스 0 목록 | 보강 |
| R-3119 | Prohibition | discipline-houserules/SKILL §1 | 스코프 밖 → 옮기지도 고치지도 않는다(정리·일관성·트리 밖 칸 위반·백스톱 red 어느 것도 이동 근거 아님) | «**없다** → 이 작업의 것이 아니다: 표준 위반으로 보여도 옮기지도 고치지도 않는다» | T* | 풀림: BC 점검·판정에서 기존 코드 면제 효력 / 남음: 실제 이동은 G0 ⓐ→슬라이스 0(R-3120) | 보강 |
| R-3121 | Prohibition | discipline-houserules/SKILL §1 | 기존 파일 수정 시 표준은 추가·변경 줄의 형태만 — 기존 줄 전파·답습 금지 | «기존 파일을 수정할 때 표준이 정하는 것은 **추가·변경되는 줄**의 형태뿐이다» | T* | 풀림: 추가·변경 줄 한정·기존 줄 «전파 금지» / 남음: «답습 금지»(기존 줄을 형태 근거로 쓰지 않음 — 같은 방향) | 후보 |
| R-3126 | Prohibition | discipline-houserules/SKILL §1 | 구조 규칙 자체는 테스트를 만들거나 기존 테스트를 자동 이동하지 않는다 | «test file/case/assertion 을 만들거나 기존 테스트를 자동 이동하지 않는다» | T* | 풀림: 기존 테스트 배치 불이동 효력(0T 항목 — D4 §3-4) / 남음: 구조 규칙만으로 테스트 신설 금지·이동은 G0 ⓐ→0T 창 | 후보 |
| R-3128 | Prohibition | discipline-houserules/SKILL §1 | 혼용 금지 규칙만으로 기존 테스트 이동 권한이 생기지 않는다 | «이 규칙만으로 기존 테스트 이동 권한이 생기지는 않는다» | T* | 풀림: 혼용 위반 기존 테스트의 불이동 효력 / 남음: 이동 권한은 G0 ⓐ→0T 창 | 후보 |
| R-3137 | Prohibition | discipline-houserules/SKILL §1 | ‹관찰 비입력›은 신규 산출물의 형태 문장 — 스코프 밖 실물의 이동·수정 권한을 만들지 않는다 | «그리고 이 원칙은 **신규 산출물의 형태** 문장이다» | T* | 풀림: 신규 산출물 한정 / 남음: «스코프 밖 기존 실물을 옮기거나 고칠 권한을 만들지 않는다» — 이동은 G0 ⓐ→슬라이스 0 | 후보 |
| R-3142 | Prohibition | discipline-houserules/SKILL §3 | 신호 — 새 모듈이 층 구분 없이 한 디렉터리에 모임(평면 답습) | «새 모듈이 층 구분 없이 한 디렉터리에 모인다(평면 답습)» | T |  | 보강 |
| R-3145 | Prohibition | discipline-houserules/SKILL §3 | 신호 — 옛 이름이 새 코드에 재등장(이관 종료 후 트리 밖 칸 위반 #81·#490) | «옛 이름이 새 코드에 다시 나타난다» | T | 기존 코드의 옛 이름도 트리 밖 칸 위반(R-1064·R-3225) | 후보 |
| R-3420 | Obligation | discipline-houserules/SKILL §1 | 승격 감사 신호 — 행위 칸 로스터 200행 무조건 방출·판정 의무만 diff 한정·재판정·신호 밖 판정 명기 | «**판정 의무의 주어만** «이번 diff 가 만들었거나 키운» | T | BC_AUDIT 해제 조항(D4 §3-4) — 신호 무조건 방출은 그대로 | 후보 |
| R-1181 | Obligation | implementation-django#final §2.5 | 도메인 판정 최초 발생 슬라이스의 파생형 전환 | «순수 인프라 필드였던 값에 도메인 판정이 처음 생기는 슬라이스에서 파생형으로 전환한다» | T* | 풀림: «처음 생기는 슬라이스» 시점 한정(이미 판정에 쓰이는 TextChoices 도 점검) / 남음: 순수 인프라 필드는 대상 아님·값 불변 전환 | 보강 |
| R-1201 | Exception | implementation-django#final §4.1 | 절 전체의 평면 Django 맥락 한정 | «이 절은 평면 Django(기존 관례 유지보수) 맥락의 원칙이다» | T | BC 점검은 표준 4계층 기준(R-1202) | 보강 |
| R-1321 | Exception | implementation-django#final §16.2 | 예시의 평면 Django 관례 한정 | «`Order.Status` 참조는 평면 Django(기존 관례) 예시다» | T |  | 보강 |
| R-0673 | Obligation | implementation-django-ninja#final §2.2 | 신규 표준 presentation 표면 = §2.3 ninja-extra 클래스 컨트롤러 | «신규 표준 presentation 표면은 §2.3의 ninja-extra 클래스 컨트롤러다» | T |  | 후보 |
| R-0674 | Permission | implementation-django-ninja#final §2.2 | 기존 함수형 Router의 확립 표면 보존 | «기존 함수형 Router는 확립된 표면을 유지할 때 보존한다» | T* | 풀림: 함수형 «형태» 보존 허용 / 남음: 확립 wire 표면(URL·메서드·상태 코드·응답 형태) 보존 — operationId 변화는 G0 «문서 층 변경» 보고 | 후보 |
| R-0696 | Obligation | implementation-django-ninja#final §2.3 | 신규 표준 표면 = @api_controller 클래스 컨트롤러 | «신규 표준 presentation 표면은 함수형 `@router.post` operation이 아니라» | T | «신규» 한정만 풀림 — 클래스 컨트롤러 의무는 그대로(사용자 예시 2) | 후보 |
| R-0697 | Obligation | implementation-django-ninja#final §2.3 | 함수형 Router operation의 레거시 취급·기존 형태 보존 | «함수형 Router operation(§2.2)은 레거시 경로로 읽고 기존 형태를 보존한다» | T |  | 후보 |
| R-0698 | Obligation | implementation-django-ninja#final §2.3 | touched(신규·수정) 표면의 클래스 컨트롤러화(승인 evidence 함수형 표면은 기록 관할) | «**touched(신규·수정) presentation 표면은 클래스 컨트롤러로 만든다» | T* | 풀림: touched 한정 / 남음: «승인 evidence 참조를 가진 함수형 표면의 보존·수정은 그 기록이 관할» — STOP 기록·사용자 명시 지시 경로를 인용할 때만 | 후보 |
| R-0717 | Prohibition | implementation-django-ninja#final §2.3 | 신규 BC마다 API 인스턴스 생성 금지 | «신규 BC마다 API 인스턴스를 만드는 것은 scope 분리가 아니다» | T | 소비자 의존 인스턴스 보존은 R-0715(N) | 후보 |
| R-0774 | Obligation | implementation-django-ninja#final §5.1 | 신규 표면의 §2.3 클래스 컨트롤러 형태 적용(예시는 원생 함수형) | «이 플러그인의 신규 표면은 §2.3 의 클래스 컨트롤러 형태를 쓴다» | T |  | 후보 |
| R-0792 | Prohibition | implementation-django-ninja#final §6.3 | 오류 이유의 함수형 Router → 클래스 컨트롤러 자동 변환 금지 | «기존 함수형 Router도 오류 때문에 클래스 컨트롤러로 자동 변환하지 않는다» | T* | 풀림: 기존 함수형 Router 불변환 효력(BC 점검은 R-0696 로 이관 항목화) / 남음: 406/415·오류를 이관 근거로 삼지 않는다 | 보강 |
| R-2878 | Obligation | implementation-django/SKILL ·s004 | 비즈니스 로직의 뷰 밖 배치(평면 맥락 fat model) | «평면 Django 맥락은 fat model(§4.1)» | T | R-1201 재진술 — BC 점검은 표준 4계층 기준 | 보강 |

## 표 2 — N 전부 (후보 267 + 보강 61 + 묶음 28)

| R-ID | 종류 | 문서 | 라벨 | 사유 | 근거 한 구 | 출처 |
|---|---|---|---|---|---|---|
| R-3238 | Obligation | agents/acceptance-tester ·s002 | 승인 설계 명세(G1 통과)·최소 열 입장 표·owner 행·관련 기존 test anchor 수령 | 절차 | 입력 수령 | 후보 |
| R-3242 | Prohibition | agents/acceptance-tester ·s002 | 프로덕션 구현 코드 열람 금지(기존 테스트·승인 계약 한정) | 절차 | acceptance-tester 블랙박스(구현 열람 금지) — BC 점검 렌즈 아님·리팩토링 0T 에서도 역할 불변 | 후보 |
| R-3245 | Exception | agents/acceptance-tester ·s003 | 명시 승인된 의미 보존 retain 재조직 한정(새 case·assertion·Red 없이 전후 동일 보호 유지) | 동작 보존·원칙 | retain 재조직 | 후보 |
| R-3258 | Prohibition | agents/acceptance-tester ·s004 | 기존 테스트·구현과의 상이를 이유로 한 현행 계약 약화 금지 | 무관 | 기존 테스트·구현 대비 계약 약화 금지 | 후보 |
| R-3259 | Prohibition | agents/acceptance-tester ·s004 | migration 파일·번호·dependency·operation·과거 model state·forward/reverse·DDL 검증 테스트의 신규 생성·확장 금지 | 무관 | migration 테스트 신규 금지(같은 방향) | 후보 |
| R-3265 | Obligation | agents/acceptance-tester ·s004 | 기존 migration 전용 테스트 삭제(절대 규칙) | 무관 | 기존 migration 테스트 삭제(같은 방향) | 후보 |
| R-3266 | Obligation | agents/acceptance-tester ·s004 | 새 파일·case·migration 시나리오·coverage 필요 시 생성 금지와 검증 공백 보고 | 절차 | 검증 공백 보고 | 후보 |
| R-3273 | Prohibition | agents/acceptance-tester ·s004 | profile·status·shape·header 의 기존 구현·기존 테스트·파일명 추론·발명 금지 | 외부 계약·동작 | profile·shape 를 기존 구현에서 추론 금지(wire 는 승인 slot) | 후보 |
| R-3277 | Obligation | agents/acceptance-tester ·s004 | reuse 의 관찰된 기존 exact-shape evidence 요구 | 외부 계약·동작 | reuse shape evidence | 후보 |
| R-3292 | Obligation | agents/acceptance-tester ·s004 | 기존 RFC 테스트 종료·변경의 승인 설계 명세 기록 product-contract evidence 요구 | 외부 계약·동작 | 기존 RFC 테스트 종료 근거 | 후보 |
| R-3306 | Exception | agents/acceptance-tester ·s004 | add/update 신규·변경 Red 작성 시 한정 테스트 러너 가용성 확인 | 절차 | 러너 확인 | 후보 |
| R-3308 | Obligation | agents/acceptance-tester ·s004 | reuse 의 확립된 기존 러너 anchor 실행 한정 | 절차 | reuse 러너 | 후보 |
| R-3310 | Obligation | agents/acceptance-tester ·s004 | 승인된 새 인수 테스트의 pytest 관용구(함수형 + assert + @pytest.mark.django_db + 픽스처) 작성 | 동작 보존·원칙 | 승인된 새 인수 테스트 pytest — 테스트 형태(원칙) | 보강 |
| R-3311 | Prohibition | agents/acceptance-tester ·s004 | 기존 TestCase 스위트 재작성·빈 tests.py 사유 새 test artifact 생성 금지 | 동작 보존·원칙 | 기존 TestCase 스위트 재작성 금지 — 테스트 형태(원칙) | 후보 |
| R-2490 | Exception | agents/coder ·s003 | 명시 승인된 의미 보존 retain 재조직의 새 case·assertion·Red 없는 동일 보호 유지 | 절차 | retain 재조직 | 후보 |
| R-2492 | Obligation | agents/coder ·s004 | 구현 전 명세의 패키지·테스트 구조 결정 독해와 신규 파일의 결정 레이아웃 배치 | 절차 | 명세 레이아웃 집행 | 후보 |
| R-2493 | Prohibition | agents/coder ·s004 | 구조 신규 결정 금지와 명세 집행 | 절차 | 구조 신규 결정 금지 | 후보 |
| R-2505 | Obligation | agents/coder ·s004 | 조용한 재해석·현장 절충 금지와 기존 반송 축(설계 반송·TREE_CONTRACT_MISMATCH) 즉시 보고 | 절차 | 결정 재방문 금지 | 후보 |
| R-2512 | Obligation | agents/coder ·s004 | 기존 migration 전용 테스트 삭제(절대 규칙) | 무관 | 기존 migration 테스트 삭제(같은 방향) | 후보 |
| R-2515 | Obligation | agents/coder ·s004 | 지원 중 구 API·영속 데이터·발행 이벤트·회귀 불변식 보존 | 외부 계약·동작 | 구 API·영속 데이터·이벤트·불변식 보존 | 후보 |
| R-2521 | Override | agents/coder ·s004 | 기존 manage.py test·Django TestCase 관례 무관 신규 테스트 pytest 작성 | 동작 보존·원칙 | «새 테스트는 pytest»(기존 관례 무관) — 테스트 형태(원칙) | 후보 |
| R-2549 | Obligation | agents/coder ·s004 | 12-slot 과 별도 shape 승인의 보존 | 외부 계약·동작 | 12-slot·shape 승인 보존 | 후보 |
| R-2551 | Obligation | agents/coder ·s004 | preserve-established 의 slot 승인 native schema/controller/handler/helper/runtime behavior·관찰 evidence 순서·artifact·wire 유지 검증과 code profile 암묵 이주 금지 | 외부 계약·동작 | preserve slot 승인 native 오류 behavior 유지(보존 범위는 오류 wire 까지 — R-2552) | 보강 |
| R-2552 | Override | agents/coder ·s004 | preserve 보존 범위의 오류 wire 계약 산출물 한정(파일트리·배선/등록·import 방향·테스트 규율은 언제나 표준) | 무관 | preserve 는 오류 wire 까지(같은 방향) | 후보 |
| R-2553 | Prohibition | agents/coder ·s004 | 승인 RFC/custom handler·helper 의 code-profile 금지 사유 제거·추출·리팩터링 금지 | 외부 계약·동작 | 승인 RFC/custom handler·helper 유지(오류 wire) | 보강 |
| R-2571 | Prohibition | agents/coder ·s004 | preserve native 범위의 오류 wire 산출물 한정과 기존 BC 배선 실물(*_api_router.py 동형)의 배선 결정 입력 배제 | 무관 | 배선 실물은 결정 입력 아님(같은 방향) | 후보 |
| R-2573 | Prohibition | agents/coder ·s004 | 승인 스코프 밖 기존 배선·배치의 이동 금지(강제 전파 금지 — 이동 권한은 G0 사용자 빚 결정→슬라이스 0) | 절차 | 스코프 밖 이동 금지 — 이동 권한 = G0 ⓐ→슬라이스 0(슬라이스 0 집행 규칙) | 후보 |
| R-2585 | Obligation | agents/coder ·s004 | class controller 승인 시 implementation-django-ninja §2.3 @api_controller + @route.* 사용 | 절차 | 명세가 class controller 를 승인하면 @api_controller 사용(슬라이스 0 명세 집행) | 보강 |
| R-2587 | Prohibition | agents/coder ·s004 | 어느 profile 에서도 406/415 사유의 함수형 Router 신규 강제 금지 | 무관 | 406/415 함수형 강제 금지(같은 방향) | 후보 |
| R-2588 | Override | agents/coder ·s004 | 명세 배선/등록 결정의 표준(#105~#112) 위배 시 그대로 집행 금지와 TREE_CONTRACT_MISMATCH 반송 | 무관 | 명세 배선 결정의 표준 위배 반송(같은 방향) | 보강 |
| R-2589 | Override | agents/coder ·s004 | 명세의 승인 스코프 산출물 목록 밖 기존 파일 이동·재배선 결정에 대한 집행 금지와 TREE_CONTRACT_MISMATCH 반송 | 절차 | 명세의 스코프 밖 이동 결정 반송(이동 권한 = G0 ⓐ) | 후보 |
| R-2603 | Obligation | agents/coder ·s006 | '최신'의 기존 프레임워크·핵심 핀 호환 한정 정의 | 무관 | '최신' 핀 호환 | 후보 |
| R-3405 | Override | agents/coder ·s004 | 명세의 승인 evidence 참조 없는 신규 표면 함수형 결정에 대한 집행 금지와 TREE_CONTRACT_MISMATCH 반송 | 무관 | 같은 방향 | 후보 |
| R-1560 | Obligation | agents/design-architect ·s002 | 고정된 BC 배치 존중과 암묵 재결정 금지 | 절차 | 사용자 고정 BC 배치 존중(스코프 메모) | 후보 |
| R-1565 | Obligation | agents/design-architect ·s002 | 명세 착수 전 기존 소스·테스트 구조 현황 조사 | 무관 | 현황 조사(따라갈 규약 찾기 아님 — 같은 방향) | 후보 |
| R-1566 | Obligation | agents/design-architect ·s002 | 조사 결과(이관 빚·배선 복원 지점·기존 test artifact 위치)의 결과 제약 반영 | 절차 | 조사 결과의 결과 제약 기재 | 후보 |
| R-1572 | Obligation | agents/design-architect ·s004 | 신규 Ninja scope 기본 error profile 은 dddjango-code-json | 외부 계약·동작 | 신규 Ninja scope 오류 profile(wire) | 후보 |
| R-1573 | Exception | agents/design-architect ·s004 | evidence 확인 또는 명시 승인 시 preserve-established 채택 | 외부 계약·동작 | brownfield 계약 evidence 시 preserve-established(오류 wire) | 보강 |
| R-1587 | Prohibition | agents/design-architect ·s005 | slot 1 — planned 경로의 신규 산출물 한정(기존은 관찰 경로·타 BC 표준 경로 금지) | 절차 | slot 1 경로 기재 형식(기존 artifact 는 관찰 경로로 적는다) | 후보 |
| R-1595 | Permission | agents/design-architect ·s005 | slot 3 — RFC 9457 wire 의 preserve 보존 허용(파일명·dependency 는 근거 불가) | 외부 계약·동작 | RFC 9457 wire preserve | 후보 |
| R-1598 | Prohibition | agents/design-architect ·s005 | slot 4 — 승인 없는 기존 계약의 종료·변경 금지 | 외부 계약·동작 | 승인 없는 기존 계약 종료·변경 금지 | 후보 |
| R-1603 | Obligation | agents/design-architect ·s005 | slot 6 — 신규 shape 생성·기준선 변경의 별도 명시 사용자 승인 | 외부 계약·동작 | shape 생성·변경 별도 승인 | 후보 |
| R-1606 | Permission | agents/design-architect ·s005 | slot 6 — 관찰 RFC/schema/handler 보존 허용과 새 recipe 일반화 금지 | 외부 계약·동작 | 관찰 RFC/schema/handler 보존 | 후보 |
| R-1644 | Obligation | agents/design-architect ·s005 | 새 HTTP/JSON API surface 의 stack 1급 결정 | 절차 | 새 HTTP/JSON API 표면 스택 결정 — STOP 사용자 승인 | 보강 |
| R-1645 | Obligation | agents/design-architect ·s005 | 신규 HTTP/JSON API 표면 스택 — 확립 스택 존재 시 STOP 표면화·명시 기록 동격·부재 시 Ninja 기본 | 절차 | 신규 표면 스택 결정 — 확립 스택은 STOP 사용자 승인(관찰 입력 축 ②) | 후보 |
| R-1649 | Prohibition | agents/design-architect ·s005 | 기존 배선 실물의 결정 입력 배제와 preserve 의 배선 답습 근거 금지 | 무관 | 기존 배선 실물은 결정 입력 아님(같은 방향) | 후보 |
| R-1651 | Obligation | agents/design-architect ·s005 | G0 ⓐ 승인 항목만 슬라이스 0 으로 전재 | 절차 | G0 ⓐ 항목만 슬라이스 0 전재 | 보강 |
| R-1655 | Obligation | agents/design-architect ·s005 | preserve 의 profile-native controller/handler/schema 보존과 code-profile recipe 미도입 | 외부 계약·동작 | preserve 보존 대상 = 오류 wire 산출물 | 후보 |
| R-1673 | Obligation | agents/design-architect ·s005 | 영구 테스트의 DB 보장·독자 failure·기존 coverage 3축 개별 판정 | 절차 | 입장 3축 | 후보 |
| R-1681 | Obligation | agents/design-architect ·s005 | 소스 파일트리의 dddjango 표준 준수(기존 레이아웃은 결정 입력 아님) | 무관 | 기존 레이아웃은 결정 입력 아님(같은 방향) | 후보 |
| R-1691 | Exception | agents/design-architect ·s005 | 입장 표 승인 test artifact 의 의미군 배치 한정 | 무관 | 승인 test artifact 의 기존·승인 레이아웃 배치 — 관찰 입력 축 ⑤ | 보강 |
| R-1719 | Obligation | agents/design-architect ·s005 | 루트 평면·골격 생략의 G1 트레이드오프 상신(명세 자가 결정 금지) | 절차 | 루트 평면·골격 생략의 G1 트레이드오프 상신 | 보강 |
| R-1721 | Obligation | agents/design-architect ·s005 | 이주 지시 시 마이그레이션 이력 보존 결과 제약 기재(label·db_table·0001) | 외부 계약·동작 | 이주 시 마이그레이션 이력 보존 제약 | 후보 |
| R-1724 | Prohibition | agents/design-architect ·s005 | §10.4 정의 밖 이력 보존 대안의 명세 발명 금지 | 외부 계약·동작 | 이력 보존 대안 발명 금지 | 후보 |
| R-1743 | Obligation | agents/design-architect ·s005 | retain 무편집과 승인된 의미 보존 재조직의 계약·failure 동일 보호 기록 | 절차 | retain·의미 보존 재조직 기록 | 후보 |
| R-1746 | Prohibition | agents/design-architect ·s005 | 기존 테스트·현재 구현의 현재 계약 대체 금지 | 무관 | 기존 테스트·구현은 현재 계약 아님 | 후보 |
| R-3426 | Obligation | agents/design-architect ·s005 | 공개 심볼과 add/update 선언 후상태·본문 미검증 분리 · 포트 자료 방향 포인터 | 절차 | pre-gate 심볼 표기 — 포트 자료 방향 포인터(한정 없음) | 보강 |
| R-2612 | Prohibition | agents/design-review-api ·s002 | 증거 동일성 확인 한정 — shape 신규 승인 금지 | 외부 계약·동작 | shape 증거 동일성 | 후보 |
| R-2615 | Exception | agents/design-review-api ·s003 | 로드한 스킬 본문·references 참조는 제한 밖 | 무관 | 스킬 본문·references 참조는 열람 제한 밖 | 보강 |
| R-2637 | Obligation | agents/design-review-api ·s005 | 입장 표 API/public contract 후보의 4요소 감사(승인·consumer/wire evidence·독자 production failure·기존 권위 coverage) | 절차 | 입장 감사 | 후보 |
| R-2641 | Obligation | agents/design-review-api ·s006 | Ninja 오류 계약 신규·변경 scope의 12-slot 존재·순서·상호 일관·evidence/compatibility 검토 | 외부 계약·동작 | 12-slot 검토 | 후보 |
| R-2652 | Obligation | agents/design-review-api ·s006 | slot 3 — 신규 scope의 dddjango-code-json / 관찰 계약의 preserve-established 확인 | 외부 계약·동작 | slot 3 profile | 후보 |
| R-2657 | Obligation | agents/design-review-api ·s006 | slot 4 — preserve+RFC scope 기존 RFC test 종료·변경의 compatibility evidence·승인 요건 | 외부 계약·동작 | slot 4 호환성 | 후보 |
| R-2661 | Obligation | agents/design-review-api ·s006 | slot 6 — 기존 scope 관찰 shape 기준선·신규 scope의 exact field set/metadata/hook inventory·식별자 field 제안 확인 | 외부 계약·동작 | slot 6 기준선 | 후보 |
| R-2662 | Obligation | agents/design-review-api ·s006 | slot 6 — 신규 shape·기준선 property/type/존재성/변환·의미 변경의 G1 분리 explicit user approval evidence 요구 | 외부 계약·동작 | slot 6 승인 | 후보 |
| R-2663 | Obligation | agents/design-review-api ·s006 | slot 6 — preserve의 observed wire/media type/schema/handler shape·approval 확인과 새 recipe 대체 금지 | 외부 계약·동작 | preserve 관찰 shape 보존(오류 wire) | 보강 |
| R-2671 | Obligation | agents/design-review-api ·s006 | slot 9 — common exact shape 보존+식별자 field 하나의 BC Enum 좁힘 base·public BC error 없는 BC만 none 확인 | 외부 계약·동작 | slot 9 | 후보 |
| R-2692 | Obligation | agents/design-review-api ·s006 | established framework header dependency 보존·테스트 확인 | 외부 계약·동작 | framework 헤더 의존 보존 | 후보 |
| R-2696 | Obligation | agents/design-review-api ·s006 | preserve의 관찰된 profile-native error body·협상 behavior 보존 | 외부 계약·동작 | preserve 오류 body·협상 보존 | 후보 |
| R-2697 | Obligation | agents/design-review-api ·s006 | native download/stream/redirect·schema-less 204 carveout 존중 확인 | 무관 | native carveout 존중 | 후보 |
| R-2698 | Obligation | agents/design-review-api ·s006 | 구조·파일 위치·import DRY·helper-circumvention 물리 판단의 discipline-reviewer 소유와 semantic contract inconsistency 한정 지적 | 절차 | 물리 판단의 discipline-reviewer 소유 — 렌즈 분담 | 보강 |
| R-2702 | Obligation | agents/design-review-api ·s006 | 신규 표준 표면의 최종 URL 합성 독법(@api_controller prefix + @route 메서드 경로) | 무관 | URL 합성 독법 | 후보 |
| R-3324 | Exception | agents/design-review-db ·s002 | 로드한 스킬 본문·references 참조의 제한 밖 인정 | 무관 | 스킬 본문·references 참조는 열람 제한 밖 | 보강 |
| R-3347 | Obligation | agents/design-review-db ·s004 | 영구 테스트 입장 표 DB 후보별 감사(현재 DB 보장·rollout/consumer evidence·독자 constraint/transaction/race failure·기존 권위 coverage) | 절차 | DB 입장 감사 | 후보 |
| R-3354 | Obligation | agents/design-review-db ·s004 | 생성될 마이그레이션 연산의 expand/contract·이력 불변 준수 확인 | 외부 계약·동작 | 생성될 마이그레이션 expand/contract·이력 불변 | 보강 |
| R-3355 | Obligation | agents/design-review-db ·s004 | 기존 앱 표준 구조 이주 명세의 기존 db_table·label·0001 보존(클래스 rename 은 state-only) 기재 확인 | 외부 계약·동작 | 이주 시 db_table·label·0001 보존 | 후보 |
| R-3356 | Obligation | agents/design-review-db ·s004 | 누락 시 brownfield DB 위험의 blocker 판정 | 외부 계약·동작 | brownfield DB 위험 blocker | 후보 |
| R-3369 | Exception | agents/design-review-ddd ·s002 | 로드한 스킬 본문·references 참조의 제한 밖 인정 | 무관 | 스킬 본문·references 참조는 열람 제한 밖 | 보강 |
| R-3389 | Obligation | agents/design-review-ddd ·s004 | 판정 기준의 «판정·불변식 소유» 고정(«레거시냐»가 기준 아님) | 무관 | «레거시냐» 아닌 «판정 소유» 기준(같은 방향) | 후보 |
| R-0840 | Prohibition | agents/discipline-reviewer ·s002 | Phase 1 미수령 4종(구현 diff·테스트 조정 목록·실행 결과·슬라이스) | 절차 | Phase 1 lightweight 미수령 입력(모드 규정) | 후보 |
| R-0841 | Prohibition | agents/discipline-reviewer ·s002 | production tree evidence와 Phase 2 implementation diff 혼동 금지 | 절차 | production tree 와 diff 구분(모드 규정) | 후보 |
| R-0843 | Obligation | agents/discipline-reviewer ·s002 | 명세 change inventory의 승인 스코프(+G0 ⓐ 빚 항목) 내포 확인 | 절차 | 명세 change inventory ⊂ 승인 스코프(+G0 ⓐ) 확인 | 보강 |
| R-0844 | Obligation | agents/discipline-reviewer ·s002 | 스코프 밖 기존 파일 이동·재배선의 G1 전 발견 상신 | 절차 | 스코프 밖 이동 발견(이동 권한 = G0 ⓐ — 리팩토링 모드도 같다) | 후보 |
| R-0848 | Obligation | agents/discipline-reviewer ·s002 | Phase 2 입력 전량 수령(코드·테스트·승인 입장 표·조정 보고·diff·실행 결과·슬라이스) | 절차 | Phase 2 입력 | 후보 |
| R-0886 | Permission | agents/discipline-reviewer ·s005 | 명시 승인된 의미 보존 move/split/rename/reorganization만 무-Red 계약 보존 인정 | 절차 | 의미 보존 재조직 인정 | 후보 |
| R-0887 | Obligation | agents/discipline-reviewer ·s005 | add/update의 3요소 제시 확인(승인 계약·독자 failure mechanism·기존 권위 coverage 차이) | 절차 | 입장 3요소 | 후보 |
| R-0893 | Prohibition | agents/discipline-reviewer ·s005 | 입장 행 없는 테스트 신규 의무화 금지 | 절차 | 입장 행 없는 테스트 의무화 금지 | 후보 |
| R-0896 | Obligation | agents/discipline-reviewer ·s005 | 기존 migration 전용 테스트의 제거 요구(절대 규칙) | 무관 | 기존 migration 테스트 제거(같은 방향) | 후보 |
| R-0897 | Obligation | agents/discipline-reviewer ·s005 | 전 test diff hunk의 승인 행·독자 failure 대조 | 절차 | hunk 대조 | 후보 |
| R-0903 | Prohibition | agents/discipline-reviewer ·s005 | 기존 비계의 이번 실행 산출 간주·임의 삭제 유도 금지 | 동작 보존·원칙 | 기존 비계 임의 삭제 금지 — 기존 테스트 고정 | 후보 |
| R-0908 | Obligation | agents/discipline-reviewer ·s006 | reuse의 관찰된 기존 exact-shape evidence 요구 | 외부 계약·동작 | reuse 관찰 shape evidence | 후보 |
| R-0913 | Obligation | agents/discipline-reviewer ·s006 | preserve-established scope의 승인 artifact evidence대로 유지 | 외부 계약·동작 | brownfield profile 격리 — preserve 오류 artifact 유지 | 보강 |
| R-0920 | Prohibition | agents/discipline-reviewer ·s007 | Phase 1·DYNAMIC 모드에서 묶음 미수령을 이유로 한 항목 실패 처리 금지 | 절차 | Phase 1·DYNAMIC 모드 묶음 미수령 실패 처리 금지 | 보강 |
| R-0925 | Prohibition | agents/discipline-reviewer ·s007 | migration 전용 테스트 부재(기존 포함·절대 규칙) | 무관 | migration 테스트 부재(기존 포함 — 같은 방향) | 후보 |
| R-0941 | Prohibition | agents/discipline-reviewer ·s007 | Django TestCase 회귀 금지(새 테스트는 무조건 pytest·관례 존중 예외 없음) | 동작 보존·원칙 | «새 테스트는 무조건 pytest» — 테스트 형태(원칙 «기존 테스트 충분 가정» · 0T 는 배치·이름) | 후보 |
| R-0947 | Permission | agents/discipline-reviewer ·s007 | 다른 boundary 권위 테스트가 같은 failure를 잡을 때 reuse 유효(신규 요구 금지) | 절차 | reuse 유효 | 후보 |
| R-0994 | Prohibition | agents/discipline-reviewer ·s007 | 승인 preserve-established handler의 범위 한정 보존(새 code-profile 정당화 재사용 금지) | 외부 계약·동작 | preserve handler 보존(오류 wire) | 후보 |
| R-1018 | Obligation | agents/discipline-reviewer ·s007 | preserve-established scope의 승인 native forwarding·handler·body/return form·mapping 보존 | 외부 계약·동작 | preserve scope native 오류 메커니즘 보존(오류 wire) | 후보 |
| R-1030 | Obligation | agents/discipline-reviewer ·s007 | controller 형태의 승인 presentation 계약 보존 | 무관 | 같은 방향 — class controller 를 함수형 Router 로 강등하지 않는다(재검토 N 표본 14 사유 정정) | 후보 |
| R-1032 | Override | agents/discipline-reviewer ·s007 | preserve-established scope의 registration/composition 표준 대조(보존 대상은 오류 wire 산출물) | 무관 | preserve 도 배선은 표준(같은 방향) | 후보 |
| R-1039 | Obligation | agents/discipline-reviewer ·s007 | brownfield handler의 기존 permanent/retryable 구분 보존 | 외부 계약·동작 | permanent/retryable 구분 보존(동작) | 후보 |
| R-1045 | Obligation | agents/discipline-reviewer ·s007 | 복구 가능한 도메인·애플리케이션 오류의 view-local 재렌더·messages.error 보존 | 무관 | «보존»=사용자 입력 보존 | 후보 |
| R-1056 | Override | agents/discipline-reviewer ·s007 | 레이아웃 대조 기준의 표준 트리 고정(기존 배치 일치는 통과 사유 아님) | 무관 | 기존 배치 일치는 통과 사유 아님(같은 방향) | 후보 |
| R-1057 | Exception | agents/discipline-reviewer ·s007 | 승인 test artifact의 기존 테스트 위치(§1.2) 예외 대조 | 무관 | 승인 test artifact 의 기존 테스트 위치 — 관찰 입력 축 ⑤(표준 자체의 선택지) — M-B1 거명이나 N | 후보 |
| R-1060 | Obligation | agents/discipline-reviewer ·s007 | 승인 스코프 밖 기존 파일 이동·재배선 자체의 발견 판정(표준 트리 일치는 통과 사유 아님) | 절차 | 스코프 밖 이동 자체가 발견(이동 권한 = G0 ⓐ) | 후보 |
| R-1065 | Obligation | agents/discipline-reviewer ·s007 | ④ 주석·docstring 언어의 프로젝트 관례(없으면 한국어) 일치 확인 | 무관 | 주석·docstring 언어 프로젝트 관례 — 관찰 입력 축 ③(표준 자체의 선택지) | 보강 |
| R-1133 | Obligation | agents/discipline-reviewer ·s007 | 면제에 정확히 드는 후보·발견의 번호 인용 기각 | 무관 | 면제 조문 16종(설계 재량·관할 밖 — #625 DB 엔진·프레임워크 교체 등) — 기존 코드 면제 아님 | 보강 |
| R-1143 | Prohibition | agents/discipline-reviewer ·s008 | public wire code·HTTP semantics·compatibility·ninja 기술 정확성의 타 소유(API reviewer·coder·implementation-*) | 절차 | wire·HTTP·ninja 기술 정확성의 API reviewer 소유 — 렌즈 분담(BC_AUDIT 도 같다) | 보강 |
| R-3404 | Obligation | agents/discipline-reviewer ·s002 | 신규 표면 함수형 결정의 승인 evidence 참조 대조(미비 시 architect 소유 blocker) | 무관 | 같은 방향 | 후보 |
| R-1975 | Obligation | architecture-api#final §5.4 | ① 배포된 에러 계약·공개 헤더 보존 | 외부 계약·동작 | 배포 오류 계약·헤더 보존 | 후보 |
| R-1976 | Obligation | architecture-api#final §5.4 | ② 신규 dddjango Ninja 범위의 기본 dddjango-code-json 선택 | 외부 계약·동작 | 신규 범위 오류 profile(wire) | 후보 |
| R-1980 | Exception | architecture-api#final §5.4 | wire 계약 한정 — preserve-established 범위의 관할 배제 | 외부 계약·동작 | wire 계약 한정 — preserve 범위 관할 배제 | 보강 |
| R-1981 | Prohibition | architecture-api#final §5.4 | 확립 native 구현·배선의 표준 레시피 이전 근거 불인정 | 외부 계약·동작 | preserve 범위는 오류 wire 관할(이 문단의 자기 한정) | 후보 |
| R-1982 | Obligation | architecture-api#final §5.4 | 신규 RFC wire 범위의 표준 controller 레시피 구현 | 외부 계약·동작 | 신규 RFC wire 범위 레시피(같은 방향) | 후보 |
| R-1987 | Obligation | architecture-api#final ·s025 | 기존 범위 관찰 shape 보존·신규 범위 표면의 분리 명시 승인 | 외부 계약·동작 | 관찰 shape 보존 | 후보 |
| R-2001 | Obligation | architecture-api#final ·s026 | 확립 계약의 WWW-Authenticate·Retry-After 헤더 보존과 별도 설계 | 외부 계약·동작 | 확립 헤더 보존 | 후보 |
| R-2005 | Obligation | architecture-api#final §6 | 신규 RFC 범위 구현 형태의 §5.4 단서 준수 | 외부 계약·동작 | RFC 절 적용 범위(wire profile) | 후보 |
| R-2018 | Obligation | architecture-api#final §8.1 | 확립·공개 요구 계약의 challenge 보존과 G1 별도 설계 복귀 | 외부 계약·동작 | 확립 challenge 보존 | 후보 |
| R-2032 | Obligation | architecture-api#final §8.4 | 확립 Bearer challenge 보존과 기본 401 차이의 G1 별도 설계 | 외부 계약·동작 | 확립 Bearer challenge 보존 | 후보 |
| R-2069 | Obligation | architecture-api#final §12.4 | 확립 429 계약의 Retry-After 헤더 보존 | 외부 계약·동작 | 확립 429 Retry-After 보존 | 후보 |
| R-2080 | Obligation | architecture-api#final §13.3 | Conflict — 다른 request content의 충돌 응답(신규 작업 처리 금지) | 무관 | 멱등 충돌 응답 | 후보 |
| R-2840 | Obligation | architecture-api/SKILL ·s001 | 로드 조건 — REST/HTTP 계약(엔드포인트·상태 코드·에러 프로필·버전/하위 호환성·OpenAPI)의 신규 정의·변경 시 선행 로드 | 무관 | 스킬 로드 조건 | 후보 |
| R-2851 | Obligation | architecture-api/SKILL ·s004 | 확립 배포 계약의 우선 보존 | 외부 계약·동작 | 배포 오류 계약 보존 | 후보 |
| R-2852 | Obligation | architecture-api/SKILL ·s004 | 신규 dddjango Ninja 범위의 dddjango-code-json 선택 | 외부 계약·동작 | 신규 범위 profile | 후보 |
| R-2857 | Obligation | architecture-api/SKILL ·s004 | 신규 범위의 RFC 9457 wire 채택 시에도 표준 controller 레시피 구현 | 외부 계약·동작 | 신규 RFC 범위 레시피 | 후보 |
| R-2858 | Exception | architecture-api/SKILL ·s004 | preserve-established 범위의 관할 배제 — native 보존 관할 | 외부 계약·동작 | preserve 범위 관할 | 후보 |
| R-2397 | Obligation | architecture-db#final §8.1 | Not Null은 기존 데이터 backfill 후 적용 | 외부 계약·동작 | Not Null backfill(데이터) | 후보 |
| R-2398 | Prohibition | architecture-db#final §8.2 | 이력 보존이 중요한 데이터에 무심코 cascade 사용 금지 | 외부 계약·동작 | 이력 데이터 cascade 금지(데이터) | 후보 |
| R-2412 | Obligation | architecture-db#final §9.5 | unique 방어는 충돌 시 예외/재시도/기존 결과 조회 정책을 함께 결정 | 무관 | unique 충돌 정책 | 후보 |
| R-2438 | Obligation | architecture-db#final §9.6 | Test criteria 심사 — 독립 production failure 면 add, 중복이면 reuse(테스트 산출물 미생성)·기존 유효 테스트 보존 | 동작 보존·원칙 | 기존 유효 DB 테스트 보존 | 후보 |
| R-2832 | Obligation | architecture-db/SKILL ·s004 | 입장 결정이 add 일 때만 coder 의 신규 테스트 작성 | 절차 | add 일 때만 테스트 | 후보 |
| R-0480 | Permission | architecture-ddd#final §2.5 | ACL 선택 조건 — 외부·레거시 용어의 도메인 누수 위험 | 무관 | «레거시»=외부 레거시 시스템 용어(ACL 선택 조건) | 후보 |
| R-0580 | Permission | architecture-ddd#final §5.3 | 핵사고날 선택 조건 — 외부·레거시가 도메인 모델을 오염시킬 위험 | 무관 | «레거시 시스템»(핵사고날 선택 조건) | 후보 |
| R-0138 | Prohibition | commands/dddjango ·s002 | 재빌드·수정 모드는 기존 폴더 재사용(새 폴더 생성 금지) | 절차 | 폴더 재사용 | 후보 |
| R-0164 | Obligation | commands/dddjango ·s004 | 신규 파일·계약이면 풀 파이프라인·기존 파일 국소 변경이면 수정 모드 | 절차 | 모드 판별 | 후보 |
| R-0166 | Obligation | commands/dddjango ·s004 | 기존 앱·도메인 접촉 사실 기억·재사용(별도 조사 재실행 금지) | 절차 | 조사 결과 재사용 | 후보 |
| R-0180 | Obligation | commands/dddjango ·s005 | 확립 스택 정체 식별 — 신규 표면 스택 확정은 §API스택 결정 순서(확립 존재 시 STOP 표면화·부재 시 기본 Ninja) | 절차 | API 스택 정체 식별 — 스택 결정은 STOP 사용자 승인(관찰 입력 축 ②) | 후보 |
| R-0183 | Exception | commands/dddjango ·s005 | 이동 권한은 G0 빚 결정→슬라이스 0 뿐 | 절차 | 이동 권한 = G0 빚 결정→슬라이스 0(리팩토링 모드도 같은 경로) | 보강 |
| R-0188 | Obligation | commands/dddjango ·s005 | 각 위반에 「손대지 않아도 해로운가」 판정 → «미룰 수 없음» 표시 | 절차 | 빚 «미룰 수 없음» 판정 | 후보 |
| R-0189 | Prohibition | commands/dddjango ·s005 | brownfield·legacy 는 면제가 아니라 아직 안 갚은 빚 | 무관 | brownfield·legacy 는 면제 아님(같은 방향) | 후보 |
| R-0203 | Prohibition | commands/dddjango ·s005 | ⓐ 목록은 최신 G0 승인 시점 동결(ⓐ 재상정 절 예외) — G2 red 소급 기입 금지 | 절차 | ⓐ 목록 G0 동결·G2 red 소급 기입 금지 | 보강 |
| R-0204 | Obligation | commands/dddjango ·s005 | 기존 영역 접촉 신호 시 «이 기능을 둘 자리» 선택 추가·선택을 스코프 메모에 기록·전달 | 절차 | 배치 갈림길 질문 | 후보 |
| R-0206 | Obligation | commands/dddjango ·s005 | 폴더 목록 선택(기존 폴더 이어서 / 새 기능)·기존 폴더면 실행 판정·확정 구체 경로 전달·이후 재계산 금지 | 절차 | 폴더 선택 | 후보 |
| R-0226 | Obligation | commands/dddjango ·s006 | 입장 표의 열·일곱 decision·protected contract·독자 failure·기존 coverage·owner 독립 감사 | 절차 | 입장 표 감사(기존 coverage) | 후보 |
| R-0227 | Obligation | commands/dddjango ·s006 | pending·부당한 add·의미 보존 재조직의 새 case/assertion/Red 를 G1 전에 포착 | 절차 | 입장 표 감사 — 의미 보존 재조직의 새 case 포착 | 후보 |
| R-0229 | Prohibition | commands/dddjango ·s006 | Phase 1 lightweight 에 구현 코드·테스트 diff·실행 결과·슬라이스 요구 금지 | 절차 | Phase 1 lightweight 모드 입력 규정(BC_AUDIT 은 별도 모드) | 후보 |
| R-0238 | Obligation | commands/dddjango ·s006 | 의미 보존 재조직은 새 case·assertion·Red 없음과 전후 보호 동일 기록까지 제시 | 절차 | G1 배너 — 의미 보존 재조직 기록 | 후보 |
| R-0252 | Prohibition | commands/dddjango ·s006 | plugin 기본 property 목록 없음 — 관찰된/승인된 exact shape 만 사용 | 외부 계약·동작 | 관찰·승인 exact shape 만 사용(오류 wire) | 보강 |
| R-0255 | Prohibition | commands/dddjango ·s006 | preserve-established slots 5–12 는 관찰 artifact·evidence 한정 — code-profile 강제 금지 | 외부 계약·동작 | preserve slots 관찰 artifact 한정(오류 wire) | 보강 |
| R-0257 | Prohibition | commands/dddjango ·s006 | shape 변경은 별도 명시 사용자 승인 evidence 필수 — 일반 G1 승인으로 갈음 금지(신규 최초 shape 동일) | 외부 계약·동작 | shape 변경의 별도 사용자 승인(wire) | 후보 |
| R-0261 | Prohibition | commands/dddjango ·s007 | reuse 는 기존 러너로 지정 anchor 만 실행 — dependency·manifest·runner config 변경 금지 | 절차 | reuse 러너 실행 — 러너 설정 불변 | 후보 |
| R-0263 | Prohibition | commands/dddjango ·s007 | 기존 TestCase 스위트의 pytest 재작성 금지 — 승인 add/update 에만 pytest 관용구 | 동작 보존·원칙 | 기존 TestCase 스위트 재작성 금지 — 테스트 형태(원칙 «기존 테스트 충분 가정» · 0T 는 배치·이름) | 후보 |
| R-0266 | Exception | commands/dddjango ·s007 | 명시 승인된 의미 보존 retain 재조직만 새 case·assertion·Red 없이 전후 보호 기록 | 절차 | 의미 보존 retain 재조직 기록 | 후보 |
| R-0277 | Prohibition | commands/dddjango ·s007 | 작업 전 기존 비계 임의 삭제 금지 | 동작 보존·원칙 | 작업 전 기존 비계 임의 삭제 금지 — 기존 테스트 고정 | 후보 |
| R-0286 | Obligation | commands/dddjango ·s007 | reviewer 감사 항목 — diff hunk 대조·write 0·무편집·종료 근거·전후 보호·비계 잔존·migration lifecycle 보존 | 절차 | 구현 감사 항목(migration lifecycle·테스트 보존) | 후보 |
| R-0291 | Obligation | commands/dddjango ·s007 | reuse/remove/의미 보존 재조직별 기재 항목 준수 | 절차 | 보고 형식 | 후보 |
| R-0293 | Obligation | commands/dddjango ·s007 | 관련 테스트와 기존 전체 suite 를 코디네이터가 직접 실행 | 절차 | 기존 전체 suite 실행 | 후보 |
| R-0297 | Obligation | commands/dddjango ·s007 | 역할별 시야 한정(API reviewer·acceptance-tester·coder·discipline-reviewer) | 절차 | Error scope Phase 2 역할별 시야(DR=입장/diff 일치) — BC_AUDIT 과 별개 모드 | 보강 |
| R-0306 | Obligation | commands/dddjango ·s007 | 게이트 증거 = 귀속 0 + legacy 잔존 별도 보고 | 절차 | G2 판정 차분(legacy 잔존 보고) — 리팩토링 모드도 같은 게이트 | 후보 |
| R-0314 | Exception | commands/dddjango ·s007 | 관찰된 현행 구성 그대로의 inventory 는 완전 — 표준형 registrar 부재는 불완전이 아니다 | 절차 | 관찰 현행 구성 inventory 는 완전(검사기 selector 입력) | 보강 |
| R-0321 | Obligation | commands/dddjango ·s007 | 승인 «이관 빚» 목록이 있으면 `--legacy-debt-file` 동반 | 절차 | 이관 빚 파일 렌더 | 후보 |
| R-0323 | Obligation | commands/dddjango ·s007 | registry #16 에 positional target·common selectors·`--anchor`(+`--legacy-debt-file`) 동일 값 렌더 | 절차 | registry #16 렌더 | 후보 |
| R-0329 | Obligation | commands/dddjango ·s007 | project URLconf/registrar slice 와 기존 BC DI V1 slice 는 별도 책임·DI slice 는 전 mode 상시 실행 | 절차 | 검사 slice 실행 | 후보 |
| R-0339 | Prohibition | commands/dddjango ·s007 | registry #5 — OpenAPI 오류 선언 대조(반환 타입 그대로)·수동 후처리 금지 + 표준 트리 슬라이스(성공 메타데이터 보충 허용·fail-closed) | 절차 | registry #5 측정 범위 서술(preserve touched 전수) | 보강 |
| R-0345 | Obligation | commands/dddjango ·s007 | registry #11 — 타입 전면(#493)·명시 Any(#645 — 시그니처 차단·변수/제네릭 안 ⓓ 후보)·django-stubs 제네릭 기저(#646)·딕셔너리-레코드(#647 · json.load ⓓ #650 · 신규 3규칙은 application/framework 루트만)·Thin Read 반환(#358)·계약 검증 토큰(#456) | 무관 | «신규 3규칙»=검사기 규칙 신설 순서 | 후보 |
| R-0347 | Prohibition | commands/dddjango ·s007 | registry #13 — established preserve-established handler 의 overmapping guard 한정 | 외부 계약·동작 | established preserve handler overmapping guard(오류 wire) | 보강 |
| R-0348 | Obligation | commands/dddjango ·s007 | registry #14 — owning-BC exception normalization/controller mapping·brownfield cause preservation | 무관 | #14 의 brownfield cause 보존=예외 cause 체인 보존 검사 | 후보 |
| R-0363 | Obligation | commands/dddjango ·s007 | registry #6 은 API-error selector 를 수용하되 판정에 쓰지 않음 — 나머지는 각 checker 계약대로 touched/전수 | 절차 | 검사기별 측정 경계 서술(touched/전수) | 후보 |
| R-0364 | Prohibition | commands/dddjango ·s007 | 스물일곱 전부가 touched-only 이거나 커밋 뒤 전부 empty 라는 일반화 금지 | 절차 | 검사기 경계 일반화 금지 | 후보 |
| R-0369 | Obligation | commands/dddjango ·s007 | scope-렌더 exit 2 는 검사기 자신의 `--anchor` 판정 차분 경유 — 신규분 있으면 직접 blocker·일괄 반송 | 절차 | scope-렌더 exit 판정 | 후보 |
| R-0370 | Exception | commands/dddjango ·s007 | 진단 전건이 앵커 기존분이면 검사기가 exit 0 + 기존분 별도 보고로 강등(즉석 수리 금지) | 절차 | 앵커 기존분 강등(G2 판정) | 후보 |
| R-0374 | Prohibition | commands/dddjango ·s007 | legacy 잔존 red 는 이 빌드에서 즉석 수리 금지(테스트 실패 채널과 분리) | 절차 | G2 legacy 잔존 즉석 수리 금지 — 수리 경로는 G0 ⓐ→슬라이스 0(리팩토링 모드도 같다) | 후보 |
| R-0376 | Prohibition | commands/dddjango ·s007 | 미이관 표준 경로 의존 잔존 귀속은 STOP_FOR_USER_APPROVAL 표면화 — 빚 분류는 legacy 복사 근거 아님 | 절차 | 미이관 경로 잔존 STOP | 후보 |
| R-0389 | Obligation | commands/dddjango ·s007 | 루프 대상은 coder 소유 ∧ 승인 명세 안 — 나머지는 기존 처분 그대로 | 절차 | red 분류 | 후보 |
| R-0410 | Obligation | commands/dddjango ·s007 | 기존 27-registry checker 와 12-slot evidence 는 그대로 실행·표시 | 절차 | G2 배너 | 후보 |
| R-0411 | Prohibition | commands/dddjango ·s007 | Red·pending·입장-diff 불일치·첫-Green 비계·미해소 exit·미해소 귀속 red·pre-gate 최신성 불비·contract mismatch·G0 ⓐ 잔존(재상정 제외) M>0 이면 G2 제시 금지(그 밖 legacy 잔존은 별도 보고 항목) | 절차 | G2 차단 조건 | 후보 |
| R-0423 | Obligation | commands/dddjango ·s009 | 프로젝트 기존 전체 suite 도 코디네이터가 실행 후 G2 | 절차 | 수정 모드 suite 실행 | 후보 |
| R-0430 | Prohibition | commands/dddjango ·s009 | Error response 무관 수정은 `--error-profile auto` 경계 적용 — full-tree/touched slice 유지·전부 touched-only 일반화 금지 | 절차 | 수정 모드 G2 적용 | 후보 |
| R-0431 | Obligation | commands/dddjango ·s009 | test diff·승인 remove/weaken·의미 보존 재조직 실행 시 최소 1회 focused discipline-reviewer 호출 | 절차 | 수정 모드 감사 호출 | 후보 |
| R-3435 | Permission | commands/dddjango ·s006 | 격리 사본 결정적 투영물·명시 후상태와 기존 본문 미검증 | 절차 | pre-gate 격리 사본 | 후보 |
| R-3471 | Prohibition | commands/dddjango ·s004 | 정리 요청의 이동 근거는 G0 ⓐ→슬라이스 0 뿐 — 요청·발주 문면을 이동 권한으로 읽기 금지 · 정리 요청엔 배치 질문 금지 | 절차 | 정리 요청의 이동 근거 = G0 ⓐ→슬라이스 0 | 보강 |
| R-3483 | Obligation | commands/dddjango ·s005 | 기존 폴더 실행 판정 ⑴~⑶(실행 줄 없는 이 규칙 이전 폴더 = 끝남 → 새 실행) — 미종료(⑵)면 실행 선택(잇기/승인됨/폐기) 대가와 함께 필수 · 목록 표시는 ⑵ 만 · 출처 없는 폐기 위임 불가 | 절차 | 실행 판정 | 후보 |
| R-3485 | Obligation | commands/dddjango ·s005 | 새 실행: refactor-scope 새로 씀(무커밋이면 앞 실행 절 보존)·ⓑ·이관 빚 이월 없음·file-plan = 이번 실행 델타 명시 | 절차 | 새 실행 | 후보 |
| R-3487 | Obligation | commands/dddjango ·s006 | 비위반 기존 코드 이동 필요 → architect 반송으로 명세 제외·STOP(범위 제외/요청 종료) · 답은 scope.md 범위 아님에 기록 | 절차 | 비위반 이동 STOP | 후보 |
| R-3493 | Obligation | commands/dddjango ·s009 | 수정 모드 슬라이스 0 — Phase 2 3번 선행·혼합 금지·커밋 분리·0T/0C 분할·동작 보존 창 준용 · G2 ⓐ 잔존·동작 보존 1행과 차단 적용 | 절차 | 수정 모드 슬라이스 0 | 후보 |
| R-3497 | Obligation | commands/dddjango ·s005 | G0 무승인 종료(대화형 이어 가기 제외)는 폴더 확정 뒤 refactor-scope.md 끝에 G0 정지 절 append(실행 줄 없음 · 스코프 메모는 신규 폴더면 scope.md · 기존 폴더면 절 안) | 절차 | G0 정지 기록 | 후보 |
| R-3503 | Obligation | commands/dddjango ·s007 | 동작 보존 창 — open(앵커 뒤·열린 창 거부) → 마지막 보고 뒤 close → red 면 파견 금지·철회·close 재실행 · 장치 오탐은 ⓐ 재상정(플러그인 결함) · 승인 머지만 유입 · exit 1 은 철회 또는 STOP · 병렬은 창 안만 · 잇기 verify · 감사 반영은 같은 종류 창 재open · close 보고는 감사 입력 · behavior/ 기계 기록 | 절차 | 동작 보존 창 | 후보 |
| R-3504 | Obligation | commands/dddjango ·s007 | G2 배너 동작 보존 1행 — verify 요약 기계 출처 · exit ≠ 0(열린 창·창 누락)이면 G2 미제시 | 절차 | G2 동작 보존 1행 | 후보 |
| R-1464 | Obligation | discipline-cleancode#final §9.2 | 신규 요구는 추가로만 대응 — 기존 코드 보존 | 무관 | OCP(기능 추가 방식) — 적용 범위 한정 아님 | 후보 |
| R-1525 | Obligation | discipline-cleancode#final §16.3 | 새 기능의 발아 메서드 작성 | 무관 | 발아 메서드 기법(기능 추가 방식) | 보강 |
| R-1526 | Obligation | discipline-cleancode#final §16.4 | 기존 메서드 감싸기로 전후 동작 추가 | 무관 | Wrap Method 기법 | 후보 |
| R-1528 | Obligation | discipline-cleancode#final §16.5 | 특성화 probe의 non-migration 레거시 한정 | 무관 | 특성화 probe 사용처 | 후보 |
| R-3095 | Obligation | discipline-cleancode/SKILL ·s004 | 코드 스멜 감지·리팩토링 제거 — 기능 보존 검증하며 작은 단계 | 무관 | 리팩토링 기법(기능 보존 — 같은 방향) | 후보 |
| R-3096 | Obligation | discipline-cleancode/SKILL ·s004 | 레거시는 Seam 보호 후 개선 — 임시 특성화 probe 의 영구 계약 고정 금지 | 무관 | 레거시 Seam 기법 | 후보 |
| R-3224 | Obligation | discipline-houserules#final ·s013 | 옛 이름 이중 수용은 2026-08-12 에 종료 — 검사기는 옛 이름을 더 알아보지 않는다 | 무관 | 옛 이름 이중 수용 종료(같은 방향) | 보강 |
| R-3225 | Prohibition | discipline-houserules#final ·s013 | 옛 이름 재등장은 별도 진단이 아니라 트리 밖 칸 위반(#81·#490 · 층 이름 위장 #324) | 무관 | 옛 이름 재등장은 트리 밖 칸 위반(같은 방향) | 보강 |
| R-3227 | Obligation | discipline-houserules#final ·s014 | BC 를 작업하면 그 BC 의 백스톱 위반을 먼저 정리하고 시작 · 「가만 있어도 해로운」 위반은 기다리지 않는다 | 절차 | 작업 BC 의 백스톱 위반 먼저 정리(같은 방향) | 보강 |
| R-3228 | Obligation | discipline-houserules#final ·s014 | 미루기는 사용자에게 물어서만 가능하고 .dddjango/ 에 기록된다 | 절차 | 미루기는 사용자에게 물어서만 | 보강 |
| R-3408 | Obligation | discipline-houserules#final §0 | 재수출 표기(as-alias/__all__)·본체 코드 동거 금지·import 표면 불변·git mv 이력 보존 | 무관 | 승격 폴더 형태 규칙 — 적용 범위 한정이 아니다(재검토 N 표본 18 사유 정정) | 후보 |
| R-3410 | Obligation | discipline-houserules#final §0 | 부품 0 승격 폴더 환원 신호·신규 산출/기존 빚 처분 | 절차 | 부품 0 폴더 — 기존분은 G0 빚 경로 | 후보 |
| R-3413 | Obligation | discipline-houserules#final §0 | 승격 배제 목록(사유 4부류)과 배제 칸 비대의 기존 규범 관할 | 무관 | 배제 칸 비대 관할 | 후보 |
| R-3500 | Prohibition | discipline-houserules#final §3 | 포트·조회 계약 메서드 인자를 \<data>_in 으로 두지 않는다 — _in 은 어댑터만 만든다(#574) · 같은 BC 계약이 돌려준 _in 의 중계는 예외 · 실물에 이미 있는 _in 인자는 의미 빚 | 무관 | 실물의 기존 `_in` 인자는 의미 빚(빚 명시 — 같은 방향) | 보강 |
| R-3100 | Obligation | discipline-houserules/SKILL ·s001 | 신규 모듈·BC·테스트·프로젝트 레이아웃·코드 규약 결정 시 필수 사용 | 무관 | 스킬 로드 조건 | 후보 |
| R-3111 | Obligation | discipline-houserules/SKILL §1 | 소스 파일트리는 언제나 dddjango 표준 — 기존 레이아웃은 트리 결정의 입력이 아니다 | 무관 | 기존 레이아웃은 입력 아님(같은 방향) | 후보 |
| R-3115 | Prohibition | discipline-houserules/SKILL §1 | 기존 소스 배치를 «확립된 규약»으로 읽지 않는다 — 옛 층 이름·옛 위치는 아직 안 갚은 빚 | 무관 | 기존 배치는 확립 규약 아님(같은 방향) | 후보 |
| R-3118 | Obligation | discipline-houserules/SKILL §1 | 스코프 안 → 형태는 언제나 표준이고 기존 실물은 형태 결정의 입력이 아니다 | 무관 | 스코프 안 형태는 표준(같은 방향) | 후보 |
| R-3120 | Obligation | discipline-houserules/SKILL §1 | 위반 판정은 빚 기록 권한 · 이동 권한은 G0 사용자 ⓐ 결정→슬라이스 0 한 경로에서만 | 절차 | 위반 판정 = 빚 기록 권한 · 이동 권한 = G0 ⓐ→슬라이스 0 | 보강 |
| R-3122 | Prohibition | discipline-houserules/SKILL §1 | 존치된 legacy 는 동결된 빚 — 신규 산출물의 형태 근거로 되읽기 금지 | 무관 | 존치 legacy 를 형태 근거로 쓰지 않음(같은 방향) | 후보 |
| R-3125 | Obligation | discipline-houserules/SKILL §1 | 승인 artifact 는 기존 프로젝트 테스트 위치나 표준 위치(트리 135~141행)에 둔다 | 무관 | 승인 test artifact 의 기존 테스트 위치 — 관찰 입력 축 ⑤(표준 자체의 선택지) | 후보 |
| R-3131 | Obligation | discipline-houserules/SKILL §1 | 게이트 증거는 판정 차분 — 앵커 대비 귀속 0 + legacy 잔존 별도 보고 · 귀속 red 의 «확립 규약» 수용 금지 | 절차 | G2 판정 차분 | 후보 |
| R-3134 | Obligation | discipline-houserules/SKILL §1 | 관찰이 결정 입력인 축은 닫힌 목록 여섯 | 무관 | 관찰이 결정 입력인 축 닫힌 목록 여섯(표준 자체 — 오류 wire·스택 정체·주석 언어·도구·테스트 위치·행동 계약) | 보강 |
| R-3135 | Prohibition | discipline-houserules/SKILL §1 | 목록 밖 축에서 기존 실물의 관찰은 결정의 입력이 아니다 | 무관 | 관찰 비입력(같은 방향) | 후보 |
| R-3146 | Prohibition | discipline-houserules/SKILL §3 | 신호 — check-layer-skeleton exit 2 를 «기존 코드라 면제»로 읽음 | 무관 | 기존 코드라 면제 아님(같은 방향) | 후보 |
| R-3159 | Obligation | discipline-houserules/SKILL §5 | 기존 코드베이스의 주석 언어 관례를 우선한다 | 무관 | 주석 언어 — 관찰 입력 축 ③(표준 자체가 관례 위임) | 후보 |
| R-3160 | Obligation | discipline-houserules/SKILL §5 | 영어 주석이 지배적이면 영어로 맞춘다(일관성 최우선) | 무관 | 영어 주석 지배 시 영어 — 관찰 입력 축 ③ | 보강 |
| R-3161 | Obligation | discipline-houserules/SKILL §5 | 확립된 관례가 없으면 한국어로 쓴다 | 무관 | 주석 언어 기본값 | 후보 |
| R-3163 | Obligation | discipline-houserules/SKILL §6.1 | 표준 도구셋은 기능 추가 흐름이 직접 다룬다 — 기존 도구 감지·존중, 부재 시 §2.1 버전-핀 규율 셋업(임의 글로벌 설치 금지) · django-stubs-ext monkeypatch 는 전역 패치라 미도입 — 채택 관찰(§1 ④)로 §4 표기(별칭/직접) 결정 | 무관 | 도구 감지·존중 — 관찰 입력 축 ④ | 후보 |
| R-3168 | Obligation | discipline-houserules/SKILL §6.2 | '최신'은 기존 핀과 호환되는 최신이다 | 무관 | 핀 호환 | 후보 |
| R-3169 | Prohibition | discipline-houserules/SKILL §6.2 | 기존 프레임워크·핵심 의존성 핀 상향 금지 — 불가하면 보고(설계 반송) | 무관 | 핀 상향 금지 | 후보 |
| R-3421 | Obligation | discipline-houserules/SKILL §1 | 등가 조항 — 칸 행의 두 실현 승인·명세는 파일 표기·기존 파일 승격은 G0 한정 | 절차 | 기존 파일 승격 = G0 ⓐ 경로 | 후보 |
| R-3447 | Prohibition | discipline-houserules/SKILL §4 | Any 기존 금지/후보와 확인된 framework admin 슬롯 제한 허용 | 무관 | «기존 면제»=Any 면제 목록 | 후보 |
| R-3495 | Prohibition | discipline-houserules/SKILL §1 | 재작성·분할·개명·이관(새 산출물+옛 줄 삭제 포함)으로 이동 권한 우회 금지 — «이동» 정의 · «사용자 ⓐ 결정» = G0 결정 줄 ⓐ 전부 | 절차 | «이동» 정의·이동 권한 우회 금지 | 보강 |
| R-2115 | Obligation | discipline-tdd#final §4.2 | 장애 보고 시 §5.5 candidate 선행 — 계약·독자 failure·기존 coverage 확인 | 절차 | 장애 보고 candidate | 후보 |
| R-2133 | Override | discipline-tdd#final §5.5 | 현재 구현·기존 테스트는 조사 증거에 불과 | 무관 | 현재 구현·기존 테스트는 조사 증거(같은 방향) | 후보 |
| R-2142 | Permission | discipline-tdd#final §5.5 | decision `add` — 독자 production failure 보호 신규 영구 테스트 | 절차 | decision add | 후보 |
| R-2143 | Permission | discipline-tdd#final §5.5 | decision `update` — 승인된 계약 변경에 맞춘 기존 테스트 갱신 | 절차 | decision update | 후보 |
| R-2144 | Prohibition | discipline-tdd#final §5.5 | decision `reuse` — 기존 권위 테스트 중복 시 신규 테스트 금지 | 절차 | decision reuse | 후보 |
| R-2146 | Obligation | discipline-tdd#final §5.5 | decision `retain` — 기존 테스트의 현행 보호 의미 유지 | 동작 보존·원칙 | decision retain — 기존 테스트 보호 유지 | 후보 |
| R-2153 | Prohibition | discipline-tdd#final §5.5 | 재조직이 없으면 기존 artifact 무수정 | 동작 보존·원칙 | 재조직 없으면 기존 test artifact 무수정 | 후보 |
| R-2167 | Prohibition | discipline-tdd#final §5.5 | 정상 import·행동 assertion만 존치·기존 비계 임의 삭제 금지 | 동작 보존·원칙 | 기존 비계 임의 삭제 금지 | 후보 |
| R-2184 | Obligation | discipline-tdd#final §5.5 | 기존 migration 전용 테스트 삭제(절대 규칙) | 무관 | 기존 migration 테스트 삭제(같은 방향) | 후보 |
| R-2228 | Obligation | discipline-tdd#final §11.3 | 이주 2단계 — 기존 세팅 지점에서 새 변수 동시 세팅 | 무관 | 포맷 이주 기법 단계 | 후보 |
| R-2229 | Obligation | discipline-tdd#final §11.3 | 이주 3단계 — 기존 변수 사용처의 새 변수 전환 | 무관 | 포맷 이주 기법 단계 | 후보 |
| R-2230 | Obligation | discipline-tdd#final §11.3 | 이주 4단계 — 기존 포맷 제거 | 무관 | 포맷 이주 기법 단계 | 후보 |
| R-2237 | Obligation | discipline-tdd#final §13 | 레거시 코드 다루기의 `discipline-cleancode` 위임 | 무관 | 레거시 다루기 위임 | 후보 |
| R-2244 | Obligation | discipline-tdd#final §17.4 | TDAID 2단계 Admission — 계약·독자 failure·기존 coverage로 decision 확정 | 절차 | TDAID admission | 후보 |
| R-3065 | Obligation | discipline-tdd/SKILL ·s004 | 전 영구 test artifact 변경 전 §5.5 입장 심사와 의미 보존 재조직의 새 case·Red 0 | 절차 | 입장 심사 | 후보 |
| R-3066 | Obligation | discipline-tdd/SKILL ·s004 | 영구 테스트의 판정 기준 — 승인된 현행 계약·독자 실패·기존 권위 coverage | 절차 | 판정 기준 | 후보 |
| R-3069 | Prohibition | discipline-tdd/SKILL ·s004 | migration 전용 테스트 생성 금지·기존 삭제(절대 규칙) | 무관 | migration 테스트 삭제(같은 방향) | 후보 |
| R-3070 | Obligation | discipline-tdd/SKILL ·s004 | 과거 버그 출신이라도 현행 계약을 검증하는 회귀 테스트 보존 | 동작 보존·원칙 | 회귀 테스트 보존 | 후보 |
| R-1157 | Obligation | implementation-django#final §1.3 | 커스텀 SQL 작성 용이성 보존 | 무관 | 커스텀 SQL 용이성 | 후보 |
| R-1182 | Override | implementation-django#final §2.5 | 기존 TextChoices 배치의 규약 부정(빚 선언) | 무관 | 기존 TextChoices 는 빚(같은 방향) | 후보 |
| R-1202 | Prohibition | implementation-django#final §4.1 | 표준 4계층의 평면 ORM 판정 메서드 blocker | 무관 | 표준 4계층 평면 ORM 판정 메서드 blocker(같은 방향) | 보강 |
| R-1228 | Obligation | implementation-django#final §8 | 신규 REST 계약은 API 계약 문제로 선행 처리 | 무관 | 신규 REST 계약의 API 계약 선행 | 후보 |
| R-1229 | Obligation | implementation-django#final §8 | greenfield 기본 경로는 Django Ninja Router·Schema | 절차 | greenfield 기본 경로 Ninja — 확립 스택은 STOP(관찰 입력 축 ②) | 보강 |
| R-1230 | Exception | implementation-django#final §8 | DRF 내용의 유지보수·기채택 프로젝트 한정 | 절차 | DRF 내용의 유지보수·기채택 프로젝트 한정 — 확립 스택 정체(관찰 입력 축 ②) | 보강 |
| R-1231 | Prohibition | implementation-django#final §8 | 신규 코드의 DRF 기본 권장 금지 | 무관 | DRF 기본 권장 금지(같은 방향) | 후보 |
| R-1263 | Obligation | implementation-django#final §10.2 | squash 시 데이터 마이그레이션 보존 정정 | 외부 계약·동작 | 데이터 마이그레이션 보존(마이그레이션 안전) | 후보 |
| R-1267 | Obligation | implementation-django#final §10.4 | 이주 시점(WHEN)의 architecture-ddd §3.2 소유 분리 | 절차 | 이주 시점(WHEN) 소유 분리 | 보강 |
| R-1268 | Obligation | implementation-django#final §10.4 | AppConfig label의 기존 값 유지 | 외부 계약·동작 | AppConfig label 유지(마이그레이션 이력) | 후보 |
| R-1269 | Obligation | implementation-django#final §10.4 | 기존 테이블명의 db_table 명시 보존 | 외부 계약·동작 | 기존 테이블명 보존(데이터) | 후보 |
| R-1270 | Prohibition | implementation-django#final §10.4 | 기존 0001_initial 불변(재작성·삭제 금지) | 외부 계약·동작 | 0001_initial 불변(마이그레이션 이력) | 후보 |
| R-1274 | Exception | implementation-django#final §10.4 | 이력 전무 legacy 앱 편입 시 조건부 사용 | 외부 계약·동작 | legacy 앱 편입 --fake-initial(마이그레이션 안전) | 후보 |
| R-1279 | Override | implementation-django#final §10.4 | 신규 db_table 규약 대비 이력 보존 우선 | 외부 계약·동작 | 기존 테이블명 이력 보존 우선(데이터) | 후보 |
| R-1280 | Prohibition | implementation-django#final §10.4 | 마이그레이션 historical value 리터럴 동결 | 외부 계약·동작 | 마이그레이션 historical value 리터럴 동결(마이그레이션 이력) | 보강 |
| R-1304 | Obligation | implementation-django#final §14.1 | 신규 add 테스트의 pytest 관용구 의무 | 동작 보존·원칙 | «신규 add» 테스트 pytest — 테스트 형태(원칙) | 후보 |
| R-1322 | Obligation | implementation-django#final §16.2 | 표준 4계층의 상태 판정·전이 도메인 소유 | 무관 | 표준 4계층 상태 판정 도메인 소유(같은 방향) | 보강 |
| R-1354 | Obligation | implementation-django#final §16.4 | add 테스트의 django_db 마커 선택 기준 | 동작 보존·원칙 | «신규 add» 에만 TestCase→pytest 등가 — 테스트 형태(원칙) | 보강 |
| R-0011 | Obligation | implementation-django-ninja#final §6.2 | 배포 범위 계약 보존·신규 범위 기본 dddjango-code-json | 외부 계약·동작 | 배포 범위 관찰 오류 계약 보존(wire) | 후보 |
| R-0013 | Obligation | implementation-django-ninja#final §6.2 | 기존 프로젝트의 관찰 shape 기준선 보존 | 외부 계약·동작 | 관찰 오류 schema exact shape 기준선 보존(wire) | 후보 |
| R-0014 | Obligation | implementation-django-ninja#final §6.2 | 신규 scope shape의 G1 slot 6 선제안·명시 승인 | 외부 계약·동작 | 신규 scope shape 의 별도 명시 승인(wire 계약 승인) | 후보 |
| R-0026 | Prohibition | implementation-django-ninja#final §6.2 | schema 소유 경계 밖 model config mutation의 보존 경로 불인정 | 외부 계약·동작 | shape 보존 경로 정의(boundary 밖 mutation 불인정) | 후보 |
| R-0034 | Override | implementation-django-ninja#final §6.2 | 기존 공용 경로의 승인 동등 계약 우선 재사용 | 외부 계약·동작 | 승인 동등 오류 계약의 공용 경로 재사용(wire) | 후보 |
| R-0040 | Obligation | implementation-django-ninja#final §6.2 | BC base 식별자 field의 공통 metadata 보존·Enum 좁힘 | 무관 | subclass 의 공통 metadata «보존» — 적용 범위 아님 | 후보 |
| R-0044 | Prohibition | implementation-django-ninja#final §6.2 | concrete subclass의 신규 요소·drift 추가 금지·재선언 metadata 반복 | 무관 | «신규 요소»=subclass 추가 필드 — 적용 범위 아님 | 후보 |
| R-0071 | Obligation | implementation-django-ninja#final §6.2 | 승인 common Schema 자체 hook의 exact shape 보존 | 외부 계약·동작 | 승인 common Schema hook = exact shape(wire) | 후보 |
| R-0094 | Exception | implementation-django-ninja#final §6.2 | 소비자 의존 기존 wire의 관찰 계약 그대로 보존 | 외부 계약·동작 | 소비자 의존 wire 보존 | 후보 |
| R-0095 | Obligation | implementation-django-ninja#final §6.2 | 보존 정당 근거 2종 한정(밖의 의존·비가역) | 무관 | 보존 근거를 좁히는 규범(리팩토링과 같은 방향) | 후보 |
| R-0096 | Prohibition | implementation-django-ninja#final §6.2 | brownfield·코드 자리의 보존 근거 불인정(자리는 리팩터링 대상) | 무관 | brownfield 는 보존 근거 아님(리팩토링과 같은 방향) | 후보 |
| R-0097 | Prohibition | implementation-django-ninja#final §6.2 | carveout의 신규 helper 레시피·profile 혼합 제시 금지 | 무관 | carveout 확장 금지 | 후보 |
| R-0650 | Obligation | implementation-django-ninja#final ·s001 | Django Ninja = greenfield API 구현 기본 목표 | 절차 | Ninja = greenfield 기본 — 확립 스택은 STOP 사용자 승인(관찰 입력 축 ②) | 보강 |
| R-0651 | Permission | implementation-django-ninja#final ·s001 | DRF 자료의 보조 근거 한정 사용(legacy review·비교·migration) | 무관 | DRF 자료의 보조 근거 사용 범위 | 후보 |
| R-0661 | Obligation | implementation-django-ninja#final §2.1 | 기존 API namespace·versioning 관례 준수 | 외부 계약·동작 | 기존 API namespace·versioning(URL wire) | 후보 |
| R-0662 | Obligation | implementation-django-ninja#final §2.1 | 신규 도입 시 글로벌 임의 설치 금지·매니페스트 버전 핀 추가 | 무관 | 의존성 신규 도입 절차 | 후보 |
| R-0663 | Obligation | implementation-django-ninja#final §2.1 | 핀 표기의 프로젝트 기존 관례 준수 | 무관 | 핀 표기 관례(관찰 입력 축 ④ 도구) | 후보 |
| R-0670 | Obligation | implementation-django-ninja#final §2.1 | 신규 Router 추가 시 확인 5항 수행 | 무관 | 새 Router 추가 시 확인 절차 | 후보 |
| R-0675 | Prohibition | implementation-django-ninja#final §2.2 | 오류 응답 이유의 클래스→함수형 강등 금지 | 무관 | 클래스→함수형 강등 금지(표준과 같은 방향) | 보강 |
| R-0699 | Prohibition | implementation-django-ninja#final §2.3 | 406/415·오류 응답 이유의 함수형 Router 강등 금지 | 무관 | 함수형 강등 금지(표준과 같은 방향) | 보강 |
| R-0700 | Obligation | implementation-django-ninja#final §2.3 | 클래스 컨트롤러의 함수형 계약 보존(response=·Status·오류 변환 순서) | 외부 계약·동작 | 클래스 이관 시 함수형 operation 계약 보존(wire) | 후보 |
| R-0701 | Obligation | implementation-django-ninja#final §2.3 | 변경 범위의 형태 한정(prefix→클래스 데코레이터·self 메서드) | 무관 | 이관 변경의 형태 한정 | 보강 |
| R-0705 | Obligation | implementation-django-ninja#final §2.3 | response=·Status·controller-owned 오류 처리·반환 타입의 §2.2 동일 보존 | 외부 계약·동작 | response=·Status·반환 동일 보존(wire) | 후보 |
| R-0715 | Permission | implementation-django-ninja#final §2.3 | 소비자 의존 확립 API 인스턴스의 승인 별도 scope 보존 허용 | 외부 계약·동작 | 소비자 의존 API 인스턴스 보존(URL·문서 wire) — M-B1 거명이나 N | 후보 |
| R-0716 | Prohibition | implementation-django-ninja#final §2.3 | 보존 근거의 «소비자 의존» 한정(«먼저 작성돼 있음» 불인정) | 무관 | «먼저 작성돼 있음» 불인정(같은 방향) | 후보 |
| R-0732 | Obligation | implementation-django-ninja#final §2.3 | ③ 분할 시 리소스 일치 컨트롤러 포함·없으면 신규 리소스 컨트롤러 | 무관 | 분할 시 리소스 컨트롤러 선택 | 후보 |
| R-0754 | Obligation | implementation-django-ninja#final §4.1 | 기존 auth mechanism adapter 우선 | 외부 계약·동작 | 기존 인증 메커니즘 우선(인증 동작) | 후보 |
| R-0791 | Prohibition | implementation-django-ninja#final §6.3 | 415 이유의 클래스 컨트롤러 → 함수형 Router 변경 금지 | 무관 | 415 이유 클래스→함수형 변경 금지(표준과 같은 방향) | 보강 |
| R-0796 | Obligation | implementation-django-ninja#final §6.3 | 승인 부재 시 framework 현재 협상/파싱 동작 보존·공개 계약 주장 금지 | 외부 계약·동작 | framework 협상·파싱 동작 보존 | 후보 |
| R-0808 | Prohibition | implementation-django-ninja#final §8 | 미실행 OpenAPI generation·schema diff의 실행 주장 금지 | 무관 | schema diff 실행 주장 금지 | 후보 |
| R-0821 | Obligation | implementation-django-ninja#final §10 | greenfield DRF 요청의 Django Ninja 구현 전환 | 절차 | greenfield DRF 요청 전환 — 확립 스택은 STOP 사용자 승인(관찰 입력 축 ②) | 보강 |
| R-0822 | Obligation | implementation-django-ninja#final §10 | legacy review·migration 시 DRF를 source behavior로 읽고 target 계약과 비교 | 외부 계약·동작 | DRF legacy 이관 시 source behavior 대조 | 후보 |
| R-0823 | Prohibition | implementation-django-ninja#final §10 | DRF-specific abstraction의 greenfield 표준 유지 금지 | 절차 | DRF abstraction 의 greenfield 표준 불유지 — 스택 결정은 STOP | 보강 |
| R-3403 | Obligation | implementation-django-ninja#final §2.3 | 신규 표면 함수형 채택의 승인 evidence 참조 요구 | 무관 | 신규 표면 함수형 채택 제한(표준과 같은 방향) | 후보 |
| R-2916 | Obligation | implementation-django-ninja/SKILL ·s004 | reuse 의 관찰 exact shape 보존 | 외부 계약·동작 | reuse shape 보존 | 후보 |
| R-2919 | Exception | implementation-django-ninja/SKILL ·s004 | 승인 common Schema hook 의 보존(HTTP 오류 변환·handler 금지 대상 제외) | 외부 계약·동작 | 승인 Schema hook 보존 | 후보 |
| R-2921 | Obligation | implementation-django-ninja/SKILL ·s004 | BC·concrete 의 공통 annotation/nullability·Field metadata 보존 | 외부 계약·동작 | 공통 metadata 보존(오류 wire) | 후보 |
| R-2950 | Obligation | implementation-django-ninja/SKILL ·s004 | 신규 API 의 Django Ninja 목표 | 절차 | 신규 API Ninja 목표 — 확립 스택은 STOP 사용자 승인(관찰 입력 축 ②) | 후보 |
| R-2951 | Permission | implementation-django-ninja/SKILL ·s004 | DRF 의 legacy·migration 맥락 한정 보조 | 절차 | DRF 보조 근거 범위 | 후보 |
| R-2952 | Obligation | implementation-django-ninja/SKILL ·s004 | 신규 도입 시 의존성 매니페스트 버전 핀 추가 | 무관 | 의존성 도입 | 후보 |
| R-2954 | Obligation | implementation-django-ninja/SKILL ·s004 | 핀 표기의 프로젝트 기존 관례 준수 | 무관 | 핀 표기 관례(관찰 입력 축 ④) | 후보 |
| R-2296 | Obligation | implementation-django-web#final §4 | HTML template indentation 의 프로젝트 관례 준수 | 무관 | HTML template indentation 프로젝트 관례 — 표준이 관례 위임(대체 표준 없음) | 보강 |
| R-2299 | Obligation | implementation-django-web#final §5 | static asset 의 기존 pipeline 준수 | 무관 | static pipeline — 표준이 프로젝트 관례에 위임(대체 표준 없음 · 정적 URL 은 배포 동작) | 후보 |
| R-2300 | Obligation | implementation-django-web#final §5 | app-specific asset 의 앱 근접 배치(프로젝트가 app/static/app_name 구조를 쓰는 경우) | 무관 | app static 배치 — 표준이 프로젝트 관례 위임 | 보강 |
| R-2301 | Obligation | implementation-django-web#final §5 | shared design-system·global asset 의 기존 shared static 위치 준수 | 무관 | shared static 위치 — 표준이 프로젝트 관례에 위임 | 후보 |
| R-2307 | Obligation | implementation-django-web#final §5 | STATIC_URL·STATIC_ROOT·STATICFILES_DIRS·storage backend·bundler·manifest hashing 의 기존 설정 준수 | 외부 계약·동작 | STATIC·storage 설정(배포 동작) | 후보 |
| R-2330 | Obligation | implementation-django-web#final §8 | security·session·CSRF·auth·message·frame option 미들웨어 ordering 보존 | 외부 계약·동작 | 보안 미들웨어 순서 보존(동작) | 후보 |
| R-2343 | Exception | implementation-django-web#final §10 | 승인 계약·독자 failure 보호 테스트 허용·`reuse/reject` 의 신규 test artifact 생성 금지 | 절차 | reuse/reject 테스트 금지 | 후보 |
| R-2357 | Obligation | implementation-django-web#final §11 | 도메인 예외의 narrow except 포획·폼 재렌더(입력 보존·messages.error·200·PRG) | 무관 | «입력 보존»=폼 재렌더 | 후보 |
| R-2870 | Obligation | implementation-django/SKILL ·s001 | 표현계층·JSON API·신규 REST 계약의 소유 스킬 위임 | 무관 | 스킬 위임 | 후보 |
| R-2874 | Obligation | implementation-django/SKILL ·s003 | 신규 REST API 계약 설계의 architecture-api 위임 | 무관 | 스킬 위임 | 후보 |
| R-2879 | Obligation | implementation-django/SKILL ·s004 | 표준 4계층의 domain_layer 애그리거트 판정 소유 | 무관 | 표준 4계층 domain_layer 판정 소유(같은 방향) | 보강 |
| R-2884 | Obligation | implementation-django/SKILL ·s004 | 도메인 상태 값 집합의 domain Enum 파생 | 무관 | 도메인 상태 값 집합 domain Enum 파생(한정 없음) | 보강 |
| R-2721 | Obligation | implementation-python#final §5.1 | 데코레이터 메타데이터의 @wraps 보존 | 무관 | @wraps 메타데이터 보존 | 후보 |
| R-2725 | Obligation | implementation-python#final §6.2 | __set_name__(3.6+) 이후 instance.__dict__ 직접 저장 권장(WeakKeyDictionary 레거시) | 무관 | «레거시» 디스크립터 패턴 참고 | 후보 |
| R-1769 | Obligation | implementation-test#final §1.1 | 동일 failure 기존 보호 시 reuse·독립 failure 에만 add | 절차 | reuse·add 판정 | 후보 |
| R-1794 | Obligation | implementation-test#final §6 | 기존 핀 상향 요구 시 기존 핀 내 핀 또는 설계 반송 | 무관 | 기존 핀 호환(의존성) | 후보 |
| R-1799 | Prohibition | implementation-test#final §6.3 | 승인된 조직 정책 보존 — 중앙 decision 없는 테스트 추가 금지 | 절차 | 조직 coverage 정책 보존 | 후보 |
| R-1844 | Obligation | implementation-test#final §15.4 | BC 사유 DB 의 기존 행 호환도 계약 | 외부 계약·동작 | BC DB 기존 행 호환(데이터) | 후보 |
| R-1850 | Obligation | implementation-test#final §15.5 | 독자 production failure 확인·기존 미보호 시에만 add | 절차 | add 조건 | 후보 |
| R-1851 | Obligation | implementation-test#final §15.5 | 입장 시 public literal 태그의 boundary 보존 의미 검증 | 절차 | 입장 후 검증 방식 | 후보 |
| R-1852 | Obligation | implementation-test#final §15.5 | 동일 literal·failure 기존 보호 시 reuse | 절차 | reuse | 후보 |
| R-1864 | Obligation | implementation-test#final §17 | 계약·독자 failure 부재·기존 보호 중복이면 reject·reuse | 절차 | reject·reuse | 후보 |
| R-1898 | Prohibition | implementation-test#final §19.2.3 | 미승인·기존 보호 중복 시 새 OpenAPI 테스트 금지 | 절차 | OpenAPI 테스트 중복 금지 | 후보 |
| R-1908 | Obligation | implementation-test#final §20.1 | 동일 key·payload 재전송의 동일 결과 반환·기존 결과 재사용 | 무관 | «기존 결과»=멱등 재전송 결과 | 후보 |
| R-1912 | Permission | implementation-test#final §20.2 | 상이 failure mechanism·기존 DB 보장 부재 시에만 DB-backed add | 절차 | DB-backed add 조건 | 후보 |
| R-1913 | Prohibition | implementation-test#final §20.2 | 동일 계약·boundary·failure 기존 보호 시 별도 테스트 금지 | 절차 | 중복 테스트 금지 | 후보 |
| R-3018 | Obligation | implementation-test/SKILL ·s004 | recipe 적용 범위 한정 — add·update 와 명시 승인된 retain 의미 보존 재조직 | 절차 | recipe 적용 범위(test decision) | 후보 |
| R-3048 | Permission | implementation-test/SKILL ·s004 | 독자 published/wire drift failure + 기존 보호 부재 시에만 add 허용(자명 반복 구조는 reuse·reject) | 절차 | add 조건 | 후보 |
| R-3049 | Obligation | implementation-test/SKILL ·s004 | migration 전용·DB-backed 현행 동작 테스트의 식별·수명 주기 기존 규칙 준수 | 무관 | 기존 규칙 준수 | 후보 |
| R-0408 | Obligation | commands/dddjango ·s007 | preserve-established 면 승인된 native runtime/mounted 증거 표시 | 외부 계약·동작 | preserve-established 오류 wire 증거 표시(묶음과 같은 취지) | 재검토 N(드리프트 식 미분류) |
| R-1015 | Prohibition | agents/discipline-reviewer ·s007 | framework-established header dependency 은닉·명세 밖 header 날조 금지 | 외부 계약·동작 | header wire 보존 | 재검토 N(드리프트 식 미분류) |
| R-3482 | Obligation | commands/dddjango ·s005 | 실행 정의(새 실행 G0 승인~G2 승인)·실행 줄 기록·기준선 행 | 절차 | «새 실행» = 실행 경계 정의 | 재검토 N(드리프트 식 미분류) |
| R-3226 | Obligation | discipline-houserules#final ·s014 | 「리팩터링 대상」을 따로 정의하지 않는다 — 백스톱이 내는 위반이 곧 그것이다 | 절차(사본 정정) | 설계 v5 §4-4 가 «기능 요청의 리팩터링 대상»으로 고친다 — 대상 목록 밖 | 재검토 N-m7 |
| R-0186 | Prohibition | commands/dddjango ·s005 | 새 검사 생성 금지(백스톱이 내는 위반이 곧 리팩터링 대상) | 절차(사본 정정) | 같음 | 재검토 N-m7 |
| R-3471 | Prohibition | commands/dddjango ·s004 | 어느 모드든 기존 코드 이동 근거는 G0 ⓐ→슬라이스 0 뿐 — 요청·발주 문면을 이동 권한으로 읽기 금지 | 절차 | 이동 경로(R-0183 과 같다 — 리팩토링 모드도 G0 ⓐ→슬라이스 0) · 로드맵 5 명칭 개정으로 식 적중 | 로드맵 5 신설·개정(G12 첫 대조) |
| R-3517 | Obligation | commands/dddjango ·s012 | 잇기는 «모드 리팩토링» 미종료 실행만 · 새 실행은 R2·R3 새로 | 절차 | 리팩토링 모드 실행 절차(«새 실행» 적중) | 로드맵 5 신설·개정(G12 첫 대조) |
| R-3519 | Obligation | commands/dddjango ·s012 | G0 정지 재개 — BC 무변일 때만 audit·verdict 재사용 | 절차 | 리팩토링 모드 재개 절차(«새 파일» 적중) | 로드맵 5 신설·개정(G12 첫 대조) |
| R-3526 | Override | commands/dddjango ·s012 | 적용 범위 규범(N-OV) | 절차(적용 범위 규범 자신) | 대상을 푸는 규범 자신 — 대상 아님 · 제외·반대 방향 근거 차단(설계 §4-3 ③) | 로드맵 5 신설·개정(G12 첫 대조) |
| R-3534 | Obligation | commands/dddjango ·s012 | 5번 감사 조각 분할·홀리스틱·diff 대조 | 절차 | 슬라이스 0 감사 절차(«diff» 적중 — 감사 대조 대상 · ⑵ 와 같은 방향) | 로드맵 5 신설·개정(G12 첫 대조) |
| R-3541 | Obligation | agents/design-review-ddd ·s006 | BC_AUDIT 점검 — 대상 BC 기존 코드 전체에 표준 | 절차 | 표준을 기존 코드에 넓히는 쪽(같은 방향) | 로드맵 5 신설·개정(G12 첫 대조) |
| R-3544 | Obligation | agents/design-review-ddd ·s006 | BC_AUDIT 잔존 확인 | 절차 | «새 파일:행» 근거 형식 | 로드맵 5 신설·개정(G12 첫 대조) |
| R-3548 | Obligation | agents/design-review-db ·s006 | BC_AUDIT 점검 — 대상 BC 기존 코드 전체에 표준 | 절차 | 같은 방향 | 로드맵 5 신설·개정(G12 첫 대조) |
| R-3551 | Obligation | agents/design-review-db ·s006 | BC_AUDIT 잔존 확인 | 절차 | 근거 형식 | 로드맵 5 신설·개정(G12 첫 대조) |
| R-3556 | Obligation | agents/design-review-api ·s008 | BC_AUDIT 점검 — 대상 BC 기존 코드 전체에 표준 | 절차 | 같은 방향 | 로드맵 5 신설·개정(G12 첫 대조) |
| R-3559 | Obligation | agents/design-review-api ·s008 | BC_AUDIT 잔존 확인 | 절차 | 근거 형식 | 로드맵 5 신설·개정(G12 첫 대조) |
| R-3564 | Obligation | agents/discipline-reviewer ·s009 | BC_AUDIT 점검 — 대상 BC 기존 코드 전체에 표준 | 절차 | 같은 방향 | 로드맵 5 신설·개정(G12 첫 대조) |
| R-3567 | Obligation | agents/discipline-reviewer ·s009 | BC_AUDIT 잔존 확인 | 절차 | 근거 형식 | 로드맵 5 신설·개정(G12 첫 대조) |
| R-3592 | Obligation | commands/dddjango ·s006 | 재리뷰 상한 확인 1회 — 발견 lens + diff 영역 lens(대응표 · 비활성 lens 영역은 discipline) + 블록 해시 변동 시 discip… | 절차 | 재리뷰·확인 입력 절차(«diff» 적중 — 반영·명세 diff 는 확인 범위의 출발점이지 표준 적용 범위 한정이 아니다) | 속도 개선 K2b 신설·개정(G12 대조) |
| R-3593 | Obligation | agents/design-review-ddd ·s002 | 확인 모드(Coordinator 명시 · 재리뷰 상한 확인 1회) — 명세·반영 diff·이 lens 반영 발견·직전 자기 노트 수령(다른 lens 반영은 d… | 절차 | 재리뷰·확인 입력 절차(«diff» 적중 — 반영·명세 diff 는 확인 범위의 출발점이지 표준 적용 범위 한정이 아니다) | 속도 개선 K2b 신설·개정(G12 대조) |
| R-3594 | Obligation | agents/design-review-api ·s003 | 확인 모드(Coordinator 명시 · 재리뷰 상한 확인 1회) — 명세·반영 diff·이 lens 반영 발견·직전 자기 노트 수령(다른 lens 반영은 d… | 절차 | 재리뷰·확인 입력 절차(«diff» 적중 — 반영·명세 diff 는 확인 범위의 출발점이지 표준 적용 범위 한정이 아니다) | 속도 개선 K2b 신설·개정(G12 대조) |
| R-3595 | Obligation | agents/design-review-db ·s002 | 확인 모드(Coordinator 명시 · 재리뷰 상한 확인 1회) — 명세·반영 diff·이 lens 반영 발견·직전 자기 노트 수령(다른 lens 반영은 d… | 절차 | 재리뷰·확인 입력 절차(«diff» 적중 — 반영·명세 diff 는 확인 범위의 출발점이지 표준 적용 범위 한정이 아니다) | 속도 개선 K2b 신설·개정(G12 대조) |
| R-3596 | Obligation | agents/discipline-reviewer ·s002 | 확인 모드(Coordinator 명시 · 재리뷰 상한 확인 1회) — 명세·반영 diff·이 lens 반영 발견·직전 자기 노트 수령(다른 lens 반영은 d… | 절차 | 재리뷰·확인 입력 절차(«diff» 적중 — 반영·명세 diff 는 확인 범위의 출발점이지 표준 적용 범위 한정이 아니다) | 속도 개선 K2b 신설·개정(G12 대조) |
| R-0220 | Prohibition | commands/dddjango ·s006 | 각 리뷰어에 architect 명세 초안만 제공(타 리뷰 노트·코드 금지 — 편향 방지) · 재리뷰에는 그 lens 처분 파일·직전 자기 노트·명세 diff … | 절차 | 재리뷰·확인 입력 절차(«diff» 적중 — 반영·명세 diff 는 확인 범위의 출발점이지 표준 적용 범위 한정이 아니다) | 속도 개선 K3 신설·개정(G12 대조) |
| R-0862 | Obligation | agents/discipline-reviewer ·s002 | 타 감수 노트 비열람 독립성(비작성자 근거) · 재리뷰에는 이 lens 처분 파일·직전 자기 노트·명세 diff 수령 — 처분 «까닭»은 판정 근거 아님(닻 … | 절차 | 재리뷰·확인 입력 절차(«diff» 적중 — 반영·명세 diff 는 확인 범위의 출발점이지 표준 적용 범위 한정이 아니다) | 속도 개선 K3 신설·개정(G12 대조) |
| R-0863 | Obligation | agents/discipline-reviewer ·s003 | 감수 리포트만 산출 · 부속 기록 경로·기록 토큰을 받으면 그 한 곳에 새 파일로 기록 + 응답 «기록: 경로 · 기록 토큰»(해시 계산 0 · 경로 없으면 … | 절차 | 부속 기록 절차(«새 파일» 적중 — 기록 파일을 새로 만든다는 쓰기 방식이지 표준 적용 범위 한정이 아니다) | 속도 개선 K3 신설·개정(G12 대조) |
| R-2617 | Obligation | agents/design-review-api ·s004 | 계약 리뷰 노트만 산출 · 부속 기록 경로·기록 토큰을 받으면 그 한 곳에 새 파일로 기록 + 응답 «기록: 경로 · 기록 토큰»(해시 계산 0 · 경로 없으… | 절차 | 부속 기록 절차(«새 파일» 적중 — 기록 파일을 새로 만든다는 쓰기 방식이지 표준 적용 범위 한정이 아니다) | 속도 개선 K3 신설·개정(G12 대조) |
| R-3325 | Obligation | agents/design-review-db ·s003 | 데이터 리뷰 노트 한정 산출 · 부속 기록 경로·기록 토큰을 받으면 그 한 곳에 새 파일로 기록 + 응답 «기록: 경로 · 기록 토큰»(해시 계산 0 · 경로… | 절차 | 부속 기록 절차(«새 파일» 적중 — 기록 파일을 새로 만든다는 쓰기 방식이지 표준 적용 범위 한정이 아니다) | 속도 개선 K3 신설·개정(G12 대조) |
| R-3370 | Obligation | agents/design-review-ddd ·s003 | 도메인 리뷰 노트 한정 산출 · 부속 기록 경로·기록 토큰을 받으면 그 한 곳에 새 파일로 기록 + 응답 «기록: 경로 · 기록 토큰»(해시 계산 0 · 경로… | 절차 | 부속 기록 절차(«새 파일» 적중 — 기록 파일을 새로 만든다는 쓰기 방식이지 표준 적용 범위 한정이 아니다) | 속도 개선 K3 신설·개정(G12 대조) |
| R-3597 | Obligation | commands/dddjango ·s002 | 부속 기록 판형 — 경로(회차 = 호출 일련번호)·1회용 기록 토큰은 Coordinator(그 역할 입력에만) · 역할은 받은 경로에만 새 파일(머리 첫 줄 … | 절차 | 부속 기록 절차(«새 파일» 적중 — 기록 파일을 새로 만든다는 쓰기 방식이지 표준 적용 범위 한정이 아니다) | 속도 개선 K3 신설·개정(G12 대조) |
| R-3599 | Obligation | commands/dddjango ·s002 | 쓰기 울타리 대조 — diff-tree --name-status ⊆ 허용(부속 기록 A · 코디네이터 쓰기 목록 · 이번 창에 띄운 pre-gate(캐시 sk… | 절차 | 재리뷰·확인 입력 절차(«diff» 적중 — 반영·명세 diff 는 확인 범위의 출발점이지 표준 적용 범위 한정이 아니다) | 속도 개선 K3 신설·개정(G12 대조) |
| R-3602 | Exception | agents/design-review-ddd ·s003 | 부속 기록 예외 — Coordinator 가 부속 기록 판형으로 준 경로의 기록 파일(리뷰 노트·리포트)은 읽기 전용 규범(R-3367 · R-3398)의 예… | 절차 | 부속 기록 절차(«새 파일» 적중 — 기록 파일을 새로 만든다는 쓰기 방식이지 표준 적용 범위 한정이 아니다) | 속도 개선 K3 신설·개정(G12 대조) |
| R-3603 | Exception | agents/design-review-api ·s004 | 부속 기록 예외 — Coordinator 가 부속 기록 판형으로 준 경로의 기록 파일(리뷰 노트·리포트)은 읽기 전용 규범(R-2609 · R-2707)의 예… | 절차 | 부속 기록 절차(«새 파일» 적중 — 기록 파일을 새로 만든다는 쓰기 방식이지 표준 적용 범위 한정이 아니다) | 속도 개선 K3 신설·개정(G12 대조) |
| R-3604 | Exception | agents/design-review-db ·s003 | 부속 기록 예외 — Coordinator 가 부속 기록 판형으로 준 경로의 기록 파일(리뷰 노트·리포트)은 읽기 전용 규범(R-3322 · R-3361)의 예… | 절차 | 부속 기록 절차(«새 파일» 적중 — 기록 파일을 새로 만든다는 쓰기 방식이지 표준 적용 범위 한정이 아니다) | 속도 개선 K3 신설·개정(G12 대조) |
| R-3605 | Exception | agents/discipline-reviewer ·s003 | 부속 기록 예외 — Coordinator 가 부속 기록 판형으로 준 경로의 기록 파일(리뷰 노트·리포트)은 읽기 전용 규범(R-0834 · R-1135)의 예… | 절차 | 부속 기록 절차(«새 파일» 적중 — 기록 파일을 새로 만든다는 쓰기 방식이지 표준 적용 범위 한정이 아니다) | 속도 개선 K3 신설·개정(G12 대조) |
| R-3606 | Exception | agents/design-architect ·s006 | 부속 기록 예외 — Coordinator 가 부속 기록 판형으로 준 lens 별 review-disposition-<lens>-<n>.md 는 «그 밖 산출물… | 절차 | 부속 기록 절차(«새 파일» 적중 — 기록 파일을 새로 만든다는 쓰기 방식이지 표준 적용 범위 한정이 아니다) | 속도 개선 K3 신설·개정(G12 대조) |
| R-3613 | Obligation | agents/acceptance-tester ·s006 | arrange 점검 입력 — 판정 대상 명세 · Coordinator 측정 sha256 · 슬라이스 계획의 인수 행(판정 대상) · 슬라이스 계획(계획 절 ·… | 절차 | arrange 점검 입력·읽기 범위(«기존» 적중 — 기존 시험·test anchor 를 읽는 범위이지 표준 적용 범위 한정이 아니다) | 속도 개선 C7 신설·개정(G12 대조) |
| R-3470 | Obligation | commands/dddjango ·s004 | 정리 요청(기존 코드를 표준에 맞추는 요청 — 처방이 동작·DB 를 바꿔도 정리 · 규칙 처방 아닌 새 동작·계약은 기능)은 리팩토링 입구가 받음 — … | 절차 | 모드 판별 정의(«기존» 적중 — 정리 요청의 대상을 이르는 말이지 표준 적용 범위 한정이 아니다 · 라벨이 바뀌어 새로 적중한 기존 규범: 전 «정리 요청(동작 유지·구조 정리만)은 리팩토링 입구가 받음 — …» → 후 «정리 요청(기존 코드를 표준에 맞추는 요청 — …)은 리팩토링 입구가 받음 — …») | RD 개정(G12 대조) |
| R-3537 | Obligation | commands/dddjango ·s012 | 리팩토링 모드 G2 배너 = 잔존 M(M_c · M_m)·재상정 제외 K(처분별 — 변경 미승인·지원 안 함 포함)·요지 축소 k + verify 세 줄(동작 보존·바뀐 것 실행·suite) + … | 절차 | G2 배너 행 구성(«보존» 적중 — verify 의 `동작 보존:` 행 이름이지 기존 형태 보존 조항이 아니다 · 라벨이 바뀌어 새로 적중한 기존 규범: 전 «… 잔존 M(M_c · M_m)·재상정 제외 K·요지 축소 k + 다섯 목록 재표시» → 후 «… + verify 세 줄(동작 보존·바뀐 것 실행·suite) + 다섯 목록(다른 BC 몫 포함) 재표시») | RD 개정(G12 대조) |
| R-3587 | Obligation | commands/dddjango ·s012 | 상시 답 미사용 — 파일 읽기·적용 0 · G1 배너 상시 답 행·상시 답 적용 절 없음 · 불가 요지 처분은 재상정 STOP 사용자 답 · 옛 출처 = 상시 답 줄이 # 앞 실행 절 밖이면 … 실행 불능(새 실행) | 절차 | 상시 답 걷기(«새 실행» 적중 — 실행 불능 뒤 다시 시작하는 방식이지 표준 적용 범위 한정이 아니다 · 라벨이 바뀌어 새로 적중한 기존 규범: 전 «상시 답 — 파일(고정 경로·커밋본·문장만·정확히 1줄) · 덮는 범주 닫힌 3 · …» → 후 «상시 답 미사용 — 파일 읽기·적용 0 · … 실행 불능(새 실행)») | RD 개정(G12 대조) |
| R-3620 | Override | commands/dddjango ·s012 | 운영 전 예외 — 리팩토링 모드 ∧ 이 실행 운영 전이면 V 항목에 대상 규범 미적용 · 조건부 대상은 조건 설 때만 · 유지 그대로 · 데이터 미보존(outbox·큐 포함) · … | 절차 | Override 자신(«보존» 적중 — 운영 안전 규범의 예외를 정하는 규범이다 · 적용 한정·기존 형태 보존 조항이 아니라 적용 범위 규범이 풀 대상이 아니다 · R-3526 과 같은 처분) | RD 신설(G12 대조) |
| R-3621 | Obligation | commands/dddjango ·s012 | 리팩토링 모드 정의 — 대상 BC 를 표준에 최대한 · 운영 전이면 처방의 동작·DB 구조 변경(새 마이그레이션 · 데이터 미보존)·시험 수정도 정리 · … · 목록 밖 보존은 시험으로 증명 · … | 절차 | 모드 정의(«보존» 적중 — 데이터 · 목록 밖 동작의 보존을 말한다 · 기존 형태를 남기라는 적용 한정이 아니다) | RD 신설(G12 대조) |
| R-3623 | Obligation | commands/dddjango ·s012 | 시험 명령 기록 — behavior/support/<UTC>/test-commands.md(시험 명령 <n>: argv + 출처: 줄 · 새 시각 폴더 · 덮어쓰기 없음 · 질문 없음) · G0 승인 때 refactor-scope.md 새 실행 기록에 옮김 … | 절차 | 기록 자리(«새 실행» 적중 — `refactor-scope.md` 의 새 실행 기록이라는 자리 이름이다) | RD 신설(G12 대조) |
| R-3631 | Prohibition | commands/dddjango ·s012 | 리팩토링 모드 창 — 기존 마이그레이션 수정·삭제·makemigrations 산출 밖 연산 금지(red) · 변경 창 새 연산 다중집합 = 승인 V 연산 | 외부 계약·동작 | 마이그레이션 이력 불변(«기존» 적중 — 리팩토링 모드 창의 자기 규칙이다 · 적용 범위 규범이 «그대로»라 한 외부 계약·동작(마이그레이션) 쪽이라 풀리지 않는다) | RD 신설(G12 대조) |
| R-3634 | Obligation | commands/dddjango ·s012 | V 연산 = makemigrations 산출 연산 17 한정·호출식 전체(필드·제약·인덱스·조건·이름·preserve_default) · … · 데이터 줄 = 미보존(outbox·큐 포함) | 절차 | 바뀌는 것 목록 판형(«보존» 적중 — V 의 데이터 줄 값이다) | RD 신설(G12 대조) |
| R-3646 | Obligation | agents/discipline-reviewer ·s005 | 리팩토링 모드 창 감사 — 요구 키마다 정확히 한 행(audit-tests-w<n>-<회차>.md · 판정 = 그 키 요구 판정 하나 또는 다름 · …) · … · 자료(diff·단위 원문·옛 이름 자리) · 승인 변경 단위는 후 = V(…) · … | 절차 | 창 감사 자료(«diff» 적중 — 감사자가 받는 파일별 전후 diff 다 · 리뷰어의 diff 한정 관찰 조항이 아니다 — 요구 키 전부를 본다) | RD 신설(G12 대조) |
| R-3651 | Prohibition | agents/coder ·s006 | DB 구조 V — makemigrations 새 파일(승인 연산 호출식과 같게) · 기존 마이그레이션 수정·삭제·RunPython·RunSQL·SeparateDatabaseAndState 금지 | 외부 계약·동작 | 마이그레이션 이력 불변(«기존» · «새 파일» 적중 — 새 마이그레이션 파일만 만들고 기존 파일은 그대로 둔다는 변경 창 규칙이다 · R-3631 과 같은 방향) | RD 신설(G12 대조) |

- 묶음(N · 외부 계약·동작 · 보강 28건): `preserve-established` 오류 wire 의 slot 기록·보존·code-profile 비강제 규범 — R-0325 · R-1583 · R-1596 · R-1601 · R-1605 · R-1608 · R-1610 · R-1613 · R-1618 · R-1625 · R-1629 · R-1636 · R-2543 · R-2577 · R-2583 · R-2632 · R-2642 · R-2643 · R-2644 · R-2656 · R-2659 · R-2665 · R-2670 · R-2673 · R-2678 · R-2685 · R-2689 · R-3290. 사유: 보존 대상이 오류 wire 산출물이다(R-2552 · R-1655 — 트리·배선·import·테스트 규율은 profile 무관 표준이라 이미 리팩토링과 같은 방향이다).
- grep 이 잡았으나 표에 올리지 않은 잡음군(전부 N·무관): pydantic `legacy Config` 표기 · 버전 태그 «리터럴 동결» · 타입 어노테이션·`Any` admin 슬롯 «면제» · 면제 조문 16종의 개별 번호 · pre-gate 기계 블록(R-3424~R-3436)의 «신규 함수»·«기존 본문» · «기존 safe 500 유지»(공개 오류 경계).

## 적용 한정 어구 목록 (닫힌 목록)

`check-verdict` 판정식(재검토 N-M3 — 문장 단위): **인용이 결속된 블록의 `works` ∩ 대상 ≠ ∅ (범위 규범 블록) ∧ 인용이 든 문장(들)이 아래 A 의 어구를 하나라도 포함 → red.** 제외·오탐 인용과 사용자 판단의 반대 방향 규칙 인용에 같은 식을 쓴다. 문장은 결속 범위 원문을 `다.`·`.`+공백·목록 머리·표 칸·원숫자·빈 줄에서 나눈 뒤 각 문장을 정규화(마크업 제거 · 공백류 전부 제거)해 정한다. 인용이 걸친 문장 전부가 판정 대상이다.

### A. 목록 (40개 — T·T\* 원문에서 실제로 쓰인 형태 · 재검토 N 뒤)

| # | 어구 | 출처 R-ID(대표) |
|---|---|---|
| 1 | `touched` (untouched 포함) | R-0123 · R-0352 · R-0698 · R-0965 · R-1714 · R-1720 · R-2499 · R-3188 |
| 2 | `grandfather` | R-0965 |
| 3 | `이번 작업` | R-0123 · R-0965 · R-1058 · R-1714 · R-1720 · R-3442 |
| 4 | `이번 diff` | R-0982 · R-3420 · R-3422 |
| 5 | `새로 들어온` | R-0982 |
| 6 | `기존 코드 존중` | R-0982 |
| 7 | `만들었거나 키운` | R-3420 · R-3422 |
| 8 | `판정 의무의 주어만` | R-3420 |
| 9 | `범위 밖 legacy` | R-1059 |
| 10 | `빚 보고 채널` | R-1059 |
| 11 | `승인 스코프의 산출물` | R-1058 |
| 12 | `승인 스코프가 낳는 산출물` | R-0182 · R-2572 |
| 13 | `신규 산출물` | R-0328 · R-1650 · R-1682 · R-3137 |
| 14 | `추가·변경되는 줄` | R-3121 |
| 15 | `기존 줄은 고치지` | R-3121 |
| 16 | `옮기지도 고치지도` | R-3119 |
| 17 | `이 작업의 것이 아니다` | R-3119 |
| 18 | `낳는 근거가 승인 스코프` | R-3117 |
| 19 | `자동 이동하지 않` | R-3126 |
| 20 | `이동 권한이 생기지` | R-3128 |
| 21 | `무관·미관여` | R-0123 · R-0125 |
| 22 | `새로 얹` (얹히는·얹힌) | R-0125 · R-0962 |
| 23 | `판정을 얹는` / `얹게 되면` | R-1713 · R-3387 · R-0115 |
| 24 | `처음 생기는 슬라이스` | R-1181 |
| 25 | `손대는 줄` / `손대지 않는` | R-3442 |
| 26 | `소급 대상이 아니` | R-3442 |
| 27 | `새로 쓰는 값 객체` | R-3442 |
| 28 | `새로 만드는 자료` / `기존 _out 자료` | R-3501 |
| 29 | `신규 표준 presentation 표면` / `신규 표면` | R-0673 · R-0696 · R-0774 |
| 30 | `새 Ninja surface` | R-1647 |
| 31 | `신규 BC마다` | R-0717 |
| 32 | `신규 managed` | R-0351 |
| 33 | `레거시 경로` / `레거시면` | R-0697 · R-1688 |
| 34 | `기존 형태를 보존` | R-0697 |
| 35 | `확립된 표면을 유지할 때` | R-0674 |
| 36 | `자동 변환하지 않` | R-0792 |
| 37 | `form을 바꾸지 않` | R-2586 |
| 38 | `평면 Django(기존 관례` / `평면 Django 맥락` | R-1201 · R-1321 · R-2878 |
| 39 | `새 코드` / `새 모듈` | R-3110 · R-3142 · R-3145 |
| 40 | 리뷰어 범위 조항: `그 명세만` · `구현 코드를 보지 않` · `네 몫이 아니` · `여전히 보지 않` · `Phase 2 implementation에서만` · `ⓓ 신규(N′∖L′)` | R-2614 · R-3323 · R-3368 · R-1137 · R-1140 · R-0919 · R-0284 |

- 주의 — 범위 규범 블록 안의 N 몫 문장에도 A 어구가 든다: Coordinator `s005/b7`(R-0180 스택 STOP 문장의 «신규 표면») · architect `s005/b17`(R-1645 의 «신규 표면»·«§2.3 touched 조항») · ninja `s010-2.3/b1`(R-3403 의 «신규 표면»). 이 문장을 인용한 제외·오탐·반대 방향 규칙은 red 가 난다(문장 단위 판정에서도 이 6문장 그대로 — 재검토 N 실측). 확립 스택 전환 항목의 경로는 이 문장들이 아니라, 범위 블록 밖 R-1230(예외 · N) 또는 축 ②(R-3134 — 스택 «정체»는 관찰이 결정 입력인 축)를 근거로 한 **제외**다(재검토 N-m2).

### B. 맨 낱말 금지 — 결합형으로만

흔해서 오발화가 큰 낱말은 **단독으로 넣지 않는다.** 위 A 의 결합형으로만 쓴다.

| 낱말 | 허용 결합형(A 번호) | 넣지 않는 이유 |
|---|---|---|
| 기존 | 6 · 15 · 28 · 34 · 38 | 범위 블록 안에도 «기존 테이블명 보존»(R-0351 남는 몫)·«기존 계약» 등 N 몫이 섞인다 |
| 신규 · 새 | 13 · 29~32 · 39 | 오류 wire 규범(«신규 scope shape» — N)·테스트 입장(«새 테스트» — N)과 겹친다 |
| 보존 · 존중 | 6 · 34 | «wire 보존»·«입력 보존»·«이력 보존»(N)이 흔하다 |
| 확립 | 35 | «확립 wire 표면»·«확립 스택»(N)이 같은 블록에 있다 |
| 레거시 · legacy | 9 · 33 | «legacy 잔존 별도 보고»(G2 절차 — N)·pydantic `legacy Config` |
| 면제 | (2 · 1 로 충분) | 타입·Any·면제 조문(N) |
| diff | 4 · 7 | «test diff hunk 대조»(절차 — N) |
| 스코프 · 관할 | 11 · 12 · 18 | «G0 스코프 메모»(절차 — N) |

### C. (걷음 — 재검토 N-M3)

문장 단위 판정으로 바꾸면서 남는 몫 어구 예외를 걷었다.

- 남는 몫 어구가 A 어구와 한 문장에 있으면 red 다. 예: R-0183 «이동 권한은 G0 빚 결정→슬라이스 0 뿐»은 R-0182 의 «승인 스코프가 낳는 산출물»과 한 문장이라, 이 인용으로 이동 항목을 뺄 수 없다.
- T\* R-ID 는 ③ 이 통째로 막는다. 남는 몫(확립 wire·오류 wire·기존 테이블명)이 걸린 항목은 별도 요청(리뷰어 «아니오 — 계약»)으로 나간다.
- R-0698 «그 기록이 관할»은 red → 채택 → G0 ⓐ/ⓑ 로 간다(현장 함수형 0건).
- 도구 상수 자가 시험: A 목록을 Override 규범 문면 한 곳에 «…»로 고정하고 도구 상수와 대조한다.

## 적용 몫 ⑴·⑵ (재검토 N-M1 · 09-27)

적용 범위 Override 문면은 대상 56 을 두 몫으로 나눠 푼다. `djr:overrides` 목록은 하나다(제외 근거 차단 ③ 은 두 몫 모두에 쓴다).

| 몫 | 풀리는 때 | 규범 |
|---|---|---|
| ⑴ 표준 적용 한정·보존(43) | BC 점검(R2)·판정(R3)·그 슬라이스 0(Phase 1 명세·Phase 2 집행) | 표 1 에서 ⑵ 13 과 R-3226·R-0186 을 뺀 전부 |
| ⑵ 리뷰어 행동 조항(13) | BC_AUDIT 모드(R2 점검·G2 잔존 확인)와 R3 판정에서만. 슬라이스 0 감사는 diff 와 `M<n>` ⓐ 대응표 대조 그대로다 | R-2614 · R-3323 · R-3368(구현 코드 열람 금지) · R-0965 · R-0982 · R-1058 · R-1059(diff·touched 한정 관찰 · 범위 밖 legacy 는 빚 보고) · R-3420 · R-3422(캐스케이드 판정 의무 diff 한정) · R-1137 · R-1140(기술 구현 정확성 경계) · R-0919(체크리스트 Phase 2 한정) · R-0284(ⓓ 신규분 동봉 — R2 입력은 설계 §3-2 가 따로 정한다) |

## 라벨 드리프트 식 (재검토 N-m3 · 09-27)

- 식(rulepack `works[*].label` 대상): `신규|touched|레거시|legacy|기존|diff|확립|이번 작업|보존|brownfield|새 코드|새 파일|새 실행|손대|존중|established`
- 적중 319(재검토 N 실측)는 전부 대상 56 또는 N 장부에 있어야 한다. 첫 대조 미분류 3건(R-0408·R-1015·R-3482)은 표 2 끝에 N 으로 넣었다.
- 집행: workspace `rulepack_smoke.py` 에 **검토 완료 ID 집합**(식 적중분만 · 사유 없음)을 둔다. `적중 − 집합 ≠ ∅` 이면 red 로 새 ID 를 출력한다. 사유는 이 문서가 갖는다(배포 스크립트·Codex byte 미러·봉인에 싣지 않는다).

## restates 연쇄

T/T\* 블록마다 `djr:restates` 로 **재진술 받은** 블록(←)과 **재진술한** 블록(→)의 규범을 적었다. 나가는 쪽은 분류된 규범이 있는 블록만 적었다. 규범 옆 표기: T / T\* / N / `—`(한정 없는 표준 규범).

- 연쇄로 새로 잡은 대상: R-2878(implementation-django SKILL — «평면 Django 맥락은 fat model») · R-0792(ninja §6.3 — «기존 함수형 Router도 … 자동 변환하지 않는다») · R-1201(§4.1) · R-3387(ddd 리뷰어 — «판정을 얹는 코드»). 모두 표 1 에 있다.
- 연쇄로 확인하고 N 으로 둔 것: R-0675 · R-0699 · R-0791(함수형 강등 금지 — 같은 방향) · R-2879 · R-1202 · R-1322(표준 4계층 판정 소유 — 같은 방향) · R-3146 · R-3224 · R-3225(«기존 코드라 면제 아님» — 같은 방향) · R-2884(한정 없음) · R-3426(포트 자료 방향 포인터 — 한정 없음) · R-2615 · R-3324 · R-3369(스킬 참조는 열람 제한 밖).
- 규범 없는 재진술 블록(블록만 있고 R-ID 없음): `architecture-ddd#final/s016-3.1/b2` · `s052-9/b7`(→ R-3442 블록) · `implementation-django#final/s029-4.3/b3`(→ R-1181 블록). 곁 문면을 달 때 함께 봐야 한다.

- **agents/coder/s004/b2** (대상: R-2499)
  - → 재진술함 `discipline-houserules#final/s003-0/b8`: R-3188=T · R-3189=—
- **agents/coder/s004/b21** (대상: R-2572)
  - → 재진술함 `agents/design-architect/s005/b17`: R-1644=N · R-1645=N · R-1646=— · R-1647=T · R-1648=— · R-1649=N · R-1650=T* · R-1651=N · R-1652=— · R-1653=— · R-1654=— · R-1655=N · R-1656=— · R-1657=— · R-1658=—
  - → 재진술함 `discipline-houserules/SKILL/s004-1/b2`: R-3111=N · R-3112=— · R-3113=— · R-3114=— · R-3115=N · R-3116=— · R-3117=T* · R-3118=N · R-3119=T* · R-3120=N · R-3121=T* · R-3122=N · R-3123=— · R-3495=N
- **agents/coder/s004/b24** (대상: R-2586)
  - → 재진술함 `agents/design-architect/s005/b17`: R-1644=N · R-1645=N · R-1646=— · R-1647=T · R-1648=— · R-1649=N · R-1650=T* · R-1651=N · R-1652=— · R-1653=— · R-1654=— · R-1655=N · R-1656=— · R-1657=— · R-1658=—
- **agents/design-architect/s005/b17** (대상: R-1647, R-1650)
  - ← 재진술 받음 `agents/coder/s004/b21`: R-2567=— · R-2568=— · R-2569=— · R-2570=— · R-2571=N · R-2572=T · R-2573=N
  - ← 재진술 받음 `agents/coder/s004/b24`: R-2584=— · R-2585=N · R-2586=T* · R-2587=N · R-2588=N · R-2589=N · R-3405=N
- **agents/design-architect/s005/b21** (대상: R-1682, R-1688)
  - → 재진술함 `discipline-houserules/SKILL/s004-1/b2`: R-3111=N · R-3112=— · R-3113=— · R-3114=— · R-3115=N · R-3116=— · R-3117=T* · R-3118=N · R-3119=T* · R-3120=N · R-3121=T* · R-3122=N · R-3123=— · R-3495=N
  - → 재진술함 `discipline-houserules/SKILL/s004-1/b3`: R-3124=— · R-3125=N · R-3126=T*
- **agents/design-review-api/s003/b1** (대상: R-2614)
  - ← 재진술 받음 `agents/design-review-db/s002/b1`: R-3323=T · R-3324=N
  - ← 재진술 받음 `agents/design-review-ddd/s002/b1`: R-3368=T · R-3369=N
  - → 재진술함 `agents/design-review-db/s002/b1`: R-3323=T · R-3324=N
- **agents/design-review-db/s002/b1** (대상: R-3323)
  - ← 재진술 받음 `agents/design-review-api/s003/b1`: R-2614=T · R-2615=N
  - → 재진술함 `agents/design-review-api/s003/b1`: R-2614=T · R-2615=N
- **agents/design-review-ddd/s002/b1** (대상: R-3368)
  - → 재진술함 `agents/design-review-api/s003/b1`: R-2614=T · R-2615=N
- **agents/design-review-ddd/s004/b3** (대상: R-3387)
  - → 재진술함 `architecture-ddd#final/s017-3.2/b9`: R-0115=T · R-0116=— · R-0117=— · R-0118=— · R-0119=— · R-0120=— · R-0121=— · R-0122=— · R-0123=T · R-0124=— · R-0125=T
- **agents/discipline-reviewer/s007/b28** (대상: R-1058, R-1059)
  - → 재진술함 `discipline-houserules/SKILL/s004-1/b2`: R-3111=N · R-3112=— · R-3113=— · R-3114=— · R-3115=N · R-3116=— · R-3117=T* · R-3118=N · R-3119=T* · R-3120=N · R-3121=T* · R-3122=N · R-3123=— · R-3495=N
  - → 재진술함 `discipline-houserules/SKILL/s009-5/b1`: R-3159=N · R-3160=N · R-3161=N · R-3162=—
- **architecture-ddd#final/s016-3.1/b3** (대상: R-3442)
  - ← 재진술 받음 `architecture-ddd#final/s016-3.1/b2`: (규범 없음)
  - ← 재진술 받음 `architecture-ddd#final/s052-9/b7`: (규범 없음)
- **architecture-ddd#final/s017-3.2/b9** (대상: R-0115, R-0123, R-0125)
  - ← 재진술 받음 `implementation-django/SKILL/s004/b1`: R-2878=T · R-2879=N
  - ← 재진술 받음 `agents/design-review-ddd/s004/b3`: R-3386=— · R-3387=T · R-3388=— · R-3389=N
  - ← 재진술 받음 `implementation-django#final/s024-4.1/b1`: R-1201=T · R-1202=N
- **discipline-houserules#final/s003-0/b8** (대상: R-3188)
  - ← 재진술 받음 `agents/coder/s004/b2`: R-2499=T · R-2500=— · R-2501=— · R-2502=—
- **discipline-houserules#final/s011-3/b3** (대상: R-3501)
  - ← 재진술 받음 `agents/design-architect/s005/b35`: R-3426=N
- **discipline-houserules#final/s014/b1** (대상: R-3226)
  - ← 재진술 받음 `discipline-houserules/SKILL/s004-1/b2`: R-3111=N · R-3112=— · R-3113=— · R-3114=— · R-3115=N · R-3116=— · R-3117=T* · R-3118=N · R-3119=T* · R-3120=N · R-3121=T* · R-3122=N · R-3123=— · R-3495=N
  - ← 재진술 받음 `discipline-houserules/SKILL/s006-3/b6`: R-3146=N
  - ← 재진술 받음 `implementation-django#final/s015-2.5/b2`: R-1177=— · R-1178=— · R-1179=— · R-1180=— · R-1181=T* · R-1182=N
- **discipline-houserules/SKILL/s004-1/b2** (대상: R-3117, R-3119, R-3121)
  - ← 재진술 받음 `agents/design-architect/s005/b21`: R-1680=— · R-1681=N · R-1682=T* · R-1683=— · R-1684=— · R-1685=— · R-1686=— · R-1687=— · R-1688=T* · R-1689=— · R-1690=— · R-1691=N · R-1692=— · R-1693=— · R-1694=— · R-1695=— · R-1696=— · R-1697=— · R-1698=— · R-1699=— · R-1700=— · R-1701=— · R-1702=— · R-1703=— · R-1704=— · R-1705=—
  - ← 재진술 받음 `agents/coder/s004/b21`: R-2567=— · R-2568=— · R-2569=— · R-2570=— · R-2571=N · R-2572=T · R-2573=N
  - ← 재진술 받음 `agents/discipline-reviewer/s007/b28`: R-1052=— · R-1053=— · R-1054=— · R-1055=— · R-1056=N · R-1057=N · R-1058=T · R-1059=T · R-1060=N · R-1061=— · R-1062=— · R-1063=— · R-1064=— · R-1065=N · R-1066=—
  - → 재진술함 `discipline-houserules#final/s014/b1`: R-3226=T* · R-3227=N · R-3228=N
- **discipline-houserules/SKILL/s004-1/b3** (대상: R-3126)
  - ← 재진술 받음 `agents/design-architect/s005/b21`: R-1680=— · R-1681=N · R-1682=T* · R-1683=— · R-1684=— · R-1685=— · R-1686=— · R-1687=— · R-1688=T* · R-1689=— · R-1690=— · R-1691=N · R-1692=— · R-1693=— · R-1694=— · R-1695=— · R-1696=— · R-1697=— · R-1698=— · R-1699=— · R-1700=— · R-1701=— · R-1702=— · R-1703=— · R-1704=— · R-1705=—
  - ← 재진술 받음 `agents/coder/s004/b1`: R-2492=N · R-2493=N · R-2494=— · R-2495=— · R-2496=— · R-2497=— · R-2498=—
- **discipline-houserules/SKILL/s006-3/b5** (대상: R-3145)
  - → 재진술함 `discipline-houserules#final/s013/b1`: R-3224=N · R-3225=N
- **implementation-django#final/s015-2.5/b2** (대상: R-1181)
  - ← 재진술 받음 `implementation-django/SKILL/s004/b5`: R-2884=N · R-2885=— · R-2886=— · R-2887=—
  - ← 재진술 받음 `implementation-django#final/s029-4.3/b3`: (규범 없음)
  - → 재진술함 `discipline-houserules#final/s014/b1`: R-3226=T* · R-3227=N · R-3228=N
- **implementation-django#final/s024-4.1/b1** (대상: R-1201)
  - ← 재진술 받음 `implementation-django/SKILL/s004/b1`: R-2878=T · R-2879=N
  - → 재진술함 `architecture-ddd#final/s017-3.2/b9`: R-0115=T · R-0116=— · R-0117=— · R-0118=— · R-0119=— · R-0120=— · R-0121=— · R-0122=— · R-0123=T · R-0124=— · R-0125=T
- **implementation-django#final/s076-16.2/b2** (대상: R-1321)
- **implementation-django-ninja#final/s009-2.2/b2** (대상: R-0673, R-0674)
  - → 재진술함 `implementation-django-ninja#final/s010-2.3/b1`: R-0696=T · R-0697=T · R-0698=T* · R-0699=N · R-3403=N
- **implementation-django-ninja#final/s010-2.3/b1** (대상: R-0696, R-0697, R-0698)
  - ← 재진술 받음 `implementation-django-ninja#final/s009-2.2/b2`: R-0673=T · R-0674=T* · R-0675=N
  - ← 재진술 받음 `implementation-django-ninja#final/s024-6.3/b5`: R-0791=N · R-0792=T*
- **implementation-django-ninja#final/s024-6.3/b5** (대상: R-0792)
  - → 재진술함 `implementation-django-ninja#final/s010-2.3/b1`: R-0696=T · R-0697=T · R-0698=T* · R-0699=N · R-3403=N
- **implementation-django/SKILL/s004/b1** (대상: R-2878)
  - → 재진술함 `architecture-ddd#final/s017-3.2/b9`: R-0115=T · R-0116=— · R-0117=— · R-0118=— · R-0119=— · R-0120=— · R-0121=— · R-0122=— · R-0123=T · R-0124=— · R-0125=T
  - → 재진술함 `implementation-django#final/s024-4.1/b1`: R-1201=T · R-1202=N
