# ACL 예외 전수성 + 경계 실패 모드 완전성 — 설계안 (option 1) · v2

> 트리거: rcqlive Claude런 minor 흠(catalog `StockConflictError`[CAS 소진] 미번역·미매핑→HTTP 500). 4-렌즈 적대 *원인* 검증 + 4-렌즈 적대 *설계* 검증을 통과한 처방. 커밋·적용은 사용자 승인 후. **확정 forks: B 보류 · E 채택 · C2 blocker(E 위).**

## v2 적대-반영 changelog (2차 4-렌즈 설계 검증)
- **D1 "503 권장" → 중립 대칭 열거**(렌즈A+D; Codex가 가이드 없이 409 독립 선택 실증 → 503 기본값화가 underdetermined 중립 깸).
- **C1/C2 거짓지적-방지 carve-out 신설**(렌즈B+D; 내부 번역 소진 예외·프로그래밍 오류 500 정당).
- **C1↔reviewer line40 심각도 우선순위 1줄**(렌즈C; 같은 누수 important/blocker 충돌 봉합).
- **★ 레버 E(포트 계약 완전성 앵커) 신설**(렌즈B; 불완전성의 진짜 구조적 뿌리. C2를 포트+ACL 2파일 결정적 판정으로 재정박 → 발산 해소·② cross-file 재발 차단).
- **C2 재정박·blocker 유지**(렌즈D; 포트 앵커 위 결정적 계약 위반이라 graduated 불필요·DR-21 강등 벡터 회피).
- **B(acceptance-tester) 보류**(렌즈A; 유일 신규 machinery·D 게이트·N≥2까지 DR-37/38 일관).
- **용어 통일("전수"=ACL/포트, "완전성"=중앙핸들러)·D1 삽입 라인 고정(:166 직후)·"중첩 방어" 정직 기술**(렌즈C).
- **백스톱 보류 근거 보강**(렌즈B; "도달성 분석 FP불가"에 더해 "예외 정의-집합 vs ACL catch 차집합" 변종도 내부-번역 예외 FP로 보류 — 재검토 후보로 기록).

## 적대-검증된 원인 (인과 상류→하류)
- **① ACL 번역 비-전수성**: ACL이 업스트림 3종 중 2종만 catch, `StockConflictError` 누락→raw 전파. houserules:205가 "번역"은 명령하나 *전수*를 안 박음.
- **② 코더 자기-규율**: 코더가 그 예외를 직접 발명·raise·단위테스트하고도 경계 처분 누락(포트 계약 `product_stock_port.py:36-42`이 2종으로 닫힘을 위반). "코더 무죄" 철회. *진짜 구조적 뿌리(렌즈B)*: 포트 예외 계약이 업스트림과 1:1 동기화될 의무 부재 → **E로 해소**.
- **③ acceptance-tester 종단 테스트 갭**: CAS 소진→HTTP status 인수테스트가 양 BC 0건. *예방 가치 있으나 D 게이트·신규 machinery라 보류(B)*.
- **④ 표준 텍스트 이중성**: houserules:143 "(`domain_layer` 하위)"는 한정구(검증됨)→ACL 완전성엔 *갭*. ninja:111/341은 "도메인/*애플리케이션* 예외→status 매핑"을 *이미 처방*→500 누수는 그 규칙 *위반*. → 텍스트 갭 수정 + 집행.

## 비-목표 (의도적 미포함)
- **결정적 백스톱 = 보류**: (i) 전파 도달성 정적분석이 FP≈0 계약과 양립 불가(FP 20~40%+·base-handler 다형성·BC 횡단). (ii) 대안 "예외 정의-집합 vs ACL catch 차집합"(import-비의존)도 *내부에서 잡혀 경계로 안 나가는 예외*(예: `DoesNotExist`→내부 번역)를 FP로 양산 → 보류. **재검토 후보**(라이브 N≥2 시).
- **B(acceptance-tester 종단테스트) = 보류**: 유일 신규 machinery·D2 게이트(미선언 시 반송이 갭 표면화)·N=1 LOW. DEVLOG/REMAINING-ISSUES 기록, 라이브 N≥2 재현 시 재개(DR-37/38 일관).
- **특정 status(409/503) 강제 = 안 함**: underdetermined(503>500>409 의미순이나 단일 정답 없음). Codex가 가이드 없이 409 독립 선택 = 중립 실증. "retryable 배정·미매핑 금지"만 의무.
- **층 배치(domain vs application) 처방 = 안 함**: N=1. A의 전수성이 층을 무의미화.
- **discipline-tdd·coder.md 별도 개정 = 안 함**: A(houserules)가 코더 생산자-텍스트라 겸함. 단 ② cross-file은 E(포트 갱신 의무)가 닫음.
- **중대도 LOW**: sqlite 채점환경 자연 도달 ~불가(`design-spec:191`). 처방은 *일반화 규율*이라 가치, 특정 픽스처 패치 아님.

## 변경 (미러: **[byte]** byte-identical claude↔codex / **[semantic]** 의미 동등 / **[보류]** 미적용 기록)
> 정확한 before/after·라인은 동반 *구현 계획*(`workspace/design/2026-06-06-...-plan.md`)이 소유. 이 문서는 결정·근거.

### A. houserules ACL 전수성 — **[byte]** `{dddjango,codex-dddjango}/skills/discipline-houserules/references/final.md`
- **A1 (:143)**: 한정구 "(`domain_layer` 하위)" → "(`domain_layer`/`application_layer` 하위)"; "번역은 *전수* — ACL이 구동하는 업스트림 동작이 그 포트 경로에서 던질 수 있는 예외를 (층 무관) 빠짐없이 잡아 포트 선언 예외로 번역; catch 안 된 raw 전파=포트 계약 위반"; bare-catch 비혼동은 cleancode 포인터로 압축("`except Exception` 포괄 catch 아님·구체 예외 명시 — `discipline-cleancode` 구체적 예외 처리").
- **A2 (:205 표 셀)**: "번역(*전수* — 포트 경로의 모든 업스트림 예외를 빠짐없이)".

### ★E. 포트 계약 완전성 앵커 — **[byte]** houserules `final.md:143` (A1과 같은 절, 결정적 판정 출처)
- 협력 포트 ABC/docstring이 "이 통합이 노출하는 *우리 쪽 예외 전수 목록*"의 **단일 출처(앵커)**가 된다. ACL은 그 목록을 *채운다* — 업스트림 예외를 빠짐없이 포트-선언 예외로 번역. 업스트림에 새 예외가 생기면 **포트 선언 + ACL 번역을 함께 갱신**한다(②의 cross-file 생산자-예방: 누락이 ACL 작성 시점이 아니라 *예외-추가 시점*에 차단). 이로써 C2가 포트+ACL 2파일만으로 결정적 판정(업스트림 BC 독해 불필요).

### B. acceptance-tester 종단 실패-모드 테스트 — **[보류]**
- DEVLOG/REMAINING-ISSUES에 "CAS 소진·협력 포트 실패의 종단(HTTP status) 인수테스트 갭"으로 기록. 라이브 N≥2 재현 시 재개. (D2가 명세에 실패모드를 선언하게 만들고 미선언은 반송으로 표면화하므로 즉시 손실 없음.)

### C. discipline-reviewer 완전성 2렌즈 — **[semantic]** `dddjango/agents/discipline-reviewer.md` + `codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md`
- **C1 (중앙 핸들러 *완전성*, line40 centralization 절에 덧댐)** — **important**:
  > 중앙 변환점의 *완전성*도 본다 — 부분 중앙화(status가 operation/app에 남음)와 **별개로**, operation이 raise/전파하는 *도메인·애플리케이션 의미를 가진* 예외(협력 포트 업스트림 포함) 중 어느 핸들러에도·ACL 번역에도 안 잡혀 framework 기본 500으로 새는 게 있으면 **important**. **우선순위**: 그 미매핑 예외의 status 선택이 operation/application `try/except`에 *남아 있으면* line40 부분-중앙화 **blocker**가 우선하고, C1 important는 *핸들러 커버리지만 빈 깨끗-raise* 케이스에 한정. **정확한 status는 명세/§5 몫 — '왜 409가 아니냐'로 잡지 않고 '어떤 의도된 status도 없다(미매핑→500)'만** 본다. **carve-out**: 프로그래밍 오류·서버 버그성 예외(`AssertionError`·`KeyError`류 — 클라이언트가 못 고치는 진짜 5xx)를 500으로 두는 건 정당(status 배정 강요 아님).
- **C2 (ACL 번역 *전수성*, structure 렌즈 line41에 덧댐)** — **blocker**:
  > ACL이 구동하는 업스트림 동작이 그 포트 경로에서 raise하는 예외(=**포트 계약이 선언한 우리 쪽 예외 집합**[E])를 ACL `try/except`가 빠짐없이 번역하는가 — 포트-선언 밖의 업스트림 예외가 ACL을 *통과해 우리 쪽으로 raw 전파*되면 포트 계약 누수(**blocker**). 결정적 백스톱(`check-context-isolation`)은 *import* 결합만 보므로 import 없이 *전파*로 새는 변종은 네가 본다(line41 import-축과 **직교**). **carve-out**: (a) 업스트림이 던지나 ACL/리포지토리 내부에서 잡혀 다른 우리 쪽 예외로 번역·소진돼 경계에 raw 도달 안 하는 예외(`DoesNotExist`→`ProductNotFoundError` 내부 번역)는 누수 아님; (b) 동일 의미 명시 재노출(재raise)도 번역의 한 형태; (c) `except Exception` 포괄 catch 강요 아님 — 포트-선언 구체 예외 집합의 누락만 본다.

### D. architect status 표 완전성 (실패-모드 열거, 비-강제)
- **D1 (architecture-api `references/final.md`, §4.2 표 :166[503 행] 직후 신설 문단)** — **[byte]**:
  > **낙관적 동시성/CAS 재시도 루프의 *소진*도 경계 실패 모드다**: 유한 재시도 루프를 설계하면 '재시도 상한 초과(쓰기 경합 미해소)'는 happy-path 밖이지만 *경계로 관찰되는* 결과다 — status 표에서 누락하지 말고 **재시도 가능(retryable) status를 배정**한다(503+`Retry-After` 또는 409+`retryable` 확장 — 둘 다 정당, 선택은 멱등성·재시도 UX 트레이드오프로 §5/G1). *어느 쪽이든 표에서 누락 금지*가 의무이고, 둘 중 선택은 architect가 임의 확정하지 않는다(미매핑 시 기본 500 누수).
- **D2 (design-architect.md:34 api lens / dddjango-design-architect)** — **[semantic]**: 기존 ":34 상태 코드·에러 형식" 규율에 1구 덧댐 — "유한 재시도/CAS 등 동시성 메커니즘의 *실패 outcome*(재시도 소진·경합 미해소)도 경계 관찰되면 status·에러 형식에 누락 없이 포함(미매핑→500 누수)·retryable 배정, 코드는 §5/G1." (신규 규율 아님 — :34가 이미 status·에러 형식을 소유·:36 Idempotency G1-표면화 패턴의 동형 특수화.)

## 의존·중첩 방어 (정직 — "단일 실패점 없음" 아님)
- **D2** = 계약이 실패 모드를 *명명* → status 부여(+보류된 B의 테스트 대상). **D 미발화 시 그 클래스의 테스트-집행은 약화**(B 보류라 더욱) — 솔직히 *열거된* 실패 모드엔 다중 방어, *미열거* 모드엔 아래로 수렴.
- **E** = 포트 계약이 *전수 출처* → A·C2의 결정적 앵커 + ② cross-file 차단.
- **A** = 구현이 포트-선언 예외로 *전수* 번역.
- **C1·C2** = A·E·완전성의 의미 집행(백스톱 못 보는 전파 변종). **A→C2, D2→(보류B) 의존 사슬 존재** — 독립 4중이 아니라 *중첩 보강*.

## 미러 범위
- **[byte]**: A(houserules:143·205)·E(houserules:143)·D1(architecture-api §4.2 :166 직후) — claude↔codex byte-identical(현재 일치 실측됨, `diff` 빈 출력 게이트).
- **[semantic]**: C(discipline-reviewer)·D2(design-architect) — codex frontmatter/구조 상이(DR-43), 본문 의미 동등.
- **[보류]**: B. **[불변]**: RUBRIC/EVAL-METHOD(채점 차원 동결 — DR-39).

## 검증 게이트 (구현 시)
- 미러 diff 빈 출력([byte] 4개 대상)·13 백스톱 재실행 무회귀·`rg "domain_layer\` 하위" → houserules 잔존 0.
- **사전 시뮬(DR-22 필수)**: 새 C1/C2 렌즈를 Claude rcqlive 픽스처(누수)·Codex 픽스처(전수 번역·정상)에 적용해 발화/비발화 격리 + carve-out 케이스(`DoesNotExist` 내부 번역·`AssertionError`류) 거짓-flag 0 확인.
- 용어 일관 grep("전수"=ACL/포트·"완전성"=중앙핸들러 혼용 0).
- 🔴 라이브 미검증 — 처방 발화는 N≥1 라이브 재런에서 확인(이 설계 범위 밖).
