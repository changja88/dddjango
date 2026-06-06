# 구현 계획 — ACL 예외 전수성 + 경계 실패 모드 완전성 (option 1 · v2)

> **설계 근거**: `workspace/design/2026-06-06-acl-exception-exhaustiveness.md` (v2, forks 확정: B 보류·E 채택·C2 blocker).
> **실행 방식**: 표준 *문서* 개정(코드 아님 — Red-Green 없음). 각 Task = 정확 편집 + 미러 + 결정적 검증(diff/grep). **서브에이전트는 개정+검증만, git commit 금지.** 커밋·push는 사용자 명시 승인 후.
> **미러 규율**: **[byte]** = 동일 OLD→NEW 문자열을 claude `dddjango/` + codex `codex-dddjango/` 양쪽에 적용·`diff`로 동일 확인. **[semantic]** = 본문 불릿이 현재 byte-id(frontmatter만 상이)라 동일 append 문자열 적용·내용 일치 확인.
> **섬세 코어**: final.md·agents/* 편집이라 이 계획 자체가 2차 적대 리뷰(plan↔design 충실도) 대상.

**Goal:** ACL이 업스트림 BC 예외를 포트-선언 예외로 *전수* 번역하게 하고(누수→500 차단), 중앙 핸들러 완전성·architect 실패-모드 열거를 표준에 박는다. 특정 status 강제·백스톱·acceptance-tester 변경은 하지 않는다.

**Architecture:** 6개 편집(A1+E·A2·D1 = [byte]; C1·C2·D2 = [semantic]) + B 보류 기록 + 사전 시뮬·게이트. 레버 의존: D2(계약 명명)→E(포트 앵커)→A(전수 번역)→C1·C2(의미 집행).

**범위 잠금(negative-guard):** 이 **6 파일**(houserules·architecture-api `references/final.md` ×2 트리, discipline-reviewer·design-architect ×2 트리) **외 무수정** — `acceptance-tester`(B 보류)·`discipline-tdd`·`coder.md`·`check-*.py`(백스톱 보류)·RUBRIC/EVAL-METHOD(차원 동결)는 건드리지 않는다(설계 비-목표). 구현 후 `git diff --stat`이 이 6 파일에만 변경을 보여야 한다(+ Task7 기록 파일).

---

## Task 1: A1+E — houserules ACL 전수성 + 포트 앵커 **[byte]**

**Files:** `dddjango/skills/discipline-houserules/references/final.md:143` + `codex-dddjango/skills/discipline-houserules/references/final.md`(동일 절)

- [ ] **Step 1: 양 파일에서 아래 OLD 문장을 NEW로 교체**

OLD (현재 :143의 굵은 문장 하나):
```
**업스트림의 모델·예외 번역은 ACL 안에 격리한다 — presentation·application이 타 BC의 예외(`domain_layer` 하위)를 직접 `import`해 잡으면 컨텍스트 결합이 ACL 밖으로 새므로, ACL이 협력 포트가 던지는 우리 쪽 예외로 번역(동일 의미면 명시적 재노출)해 넘긴다.**
```
NEW:
```
**업스트림의 모델·예외 번역은 ACL 안에 격리한다 — presentation·application이 타 BC의 예외(`domain_layer`/`application_layer` 하위)를 직접 `import`해 잡으면 컨텍스트 결합이 ACL 밖으로 새므로, ACL이 협력 포트가 던지는 우리 쪽 예외로 번역(동일 의미면 명시적 재노출)해 넘긴다. 이 번역은 *전수*다 — ACL이 구동하는 업스트림 동작이 그 포트 경로에서 던질 수 있는 예외를 (`domain_layer`·`application_layer` 층 무관) 빠짐없이 잡아 협력 포트가 선언한 우리 쪽 예외로 번역한다. catch되지 않은 업스트림 예외가 ACL을 그대로 통과해 우리 쪽 application·presentation으로 raw 전파되면 포트 계약 위반이다. 협력 포트(`domain_layer/<aggregate>/port/`)의 ABC·docstring이 *이 통합이 노출하는 우리 쪽 예외 전수 목록*의 단일 출처(앵커)이며 ACL은 그 목록을 채운다 — 업스트림에 새 예외가 생기면 포트 선언과 ACL 번역을 함께 갱신한다. 단 '전수'는 *알려진 구체 예외 집합을 빠짐없이 덮으라*는 것이지 `except Exception` 광범위 포괄 catch가 아니다 — 각 구체 예외를 명시 번역한다(`discipline-cleancode` 구체적 예외 처리).**
```

- [ ] **Step 2: 미러 검증** — `diff <(grep -n "이 번역은 \*전수\*다" dddjango/skills/discipline-houserules/references/final.md) <(grep -c "이 번역은 \*전수\*다" codex-dddjango/skills/discipline-houserules/references/final.md)` 대신: 두 파일 모두 NEW 문장 1회 포함 + 한정구 `(\`domain_layer\` 하위)` 잔존 0 확인:
  - `rg -c "domain_layer\` 하위" dddjango codex-dddjango` → 0 (한정구 단독은 사라지고 `domain_layer\`/\`application_layer\` 하위`만 남음).
  - `rg -c "이 번역은 \*전수\*다" dddjango/skills/discipline-houserules/references/final.md codex-dddjango/skills/discipline-houserules/references/final.md` → 각 1.

## Task 2: A2 — houserules acl/ 표 셀 전수 표기 **[byte]**

**Files:** 동 houserules final.md:205 (양본)

- [ ] **Step 1: OLD→NEW 교체(양본)**

OLD:
```
| `acl/` | 외부 컨텍스트 **ACL 어댑터** — domain `port/` ABC 구현, 업스트림 모델·예외를 우리 모델로 번역. 리포지토리와 분리([통합 시]) | `product_lock_adapter.py` → `class DjangoProductLockAdapter`(일반 포트 구현=`Adapter`) |
```
NEW:
```
| `acl/` | 외부 컨텍스트 **ACL 어댑터** — domain `port/` ABC 구현, 업스트림 모델·예외를 우리 모델로 번역(*전수* — 포트 경로의 모든 업스트림 예외를 포트-선언 예외로 빠짐없이). 리포지토리와 분리([통합 시]) | `product_lock_adapter.py` → `class DjangoProductLockAdapter`(일반 포트 구현=`Adapter`) |
```

- [ ] **Step 2: 검증** — `rg -c "포트-선언 예외로 빠짐없이" dddjango/skills/discipline-houserules/references/final.md codex-dddjango/skills/discipline-houserules/references/final.md` → 각 1.

## Task 3: D1 — architecture-api status 표 소진 실패-모드 (비-강제) **[byte]**

**Files:** `dddjango/skills/architecture-api/references/final.md` + codex 동일(§4.2 표 :166[503 행] 직후, §4.3 직전)

- [ ] **Step 1: OLD→NEW 교체(양본)** — 503 표행과 §4.3 헤더 사이에 문단 삽입

OLD:
```
| 503 | Service Unavailable | 일시 과부하/정비. Retry-After 헤더 가능 |

### 4.3 PRG (POST/Redirect/GET) 패턴
```
NEW:
```
| 503 | Service Unavailable | 일시 과부하/정비. Retry-After 헤더 가능 |

**낙관적 동시성/CAS 재시도 루프의 *소진*도 경계 실패 모드다**: 유한 재시도 루프를 설계하면 '재시도 상한 초과(쓰기 경합 미해소)'는 happy-path 밖이지만 *경계로 관찰되는* 결과다 — status 표에서 누락하지 말고 **재시도 가능(retryable) status를 배정**한다(503+`Retry-After` 또는 409+`retryable` 확장 — 둘 다 정당, 선택은 멱등성·재시도 UX 트레이드오프로 §5/G1). *어느 쪽이든 표에서 누락 금지*가 의무이고 둘 중 선택은 설계자가 임의 확정하지 않는다(미매핑 시 기본 500 누수).

### 4.3 PRG (POST/Redirect/GET) 패턴
```

- [ ] **Step 2: 검증** — `rg -c "소진\*도 경계 실패 모드다" dddjango/skills/architecture-api/references/final.md codex-dddjango/skills/architecture-api/references/final.md` → 각 1. 문구에 "권장"이 503 단독에 붙지 않음(대칭 "둘 다 정당") 확인.

## Task 4: C1 — discipline-reviewer 중앙 핸들러 완전성 **[semantic]**

**Files:** `dddjango/agents/discipline-reviewer.md`(line 40 "API 오류 응답 중앙화 규율" 불릿 끝) + `codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md`(동일 본문 불릿)

- [ ] **Step 1: 양본 line40 API-중앙화 불릿 말미에 append.** ⚠️ 앵커 `후자는 코더·implementation-* 몫이다.`는 파일에 **2회**(line40·line50) 존재해 비유일 → Edit `old_string`은 **line40 유일 꼬리** `` deprecated 여부)이 아니다 — 후자는 코더·implementation-* 몫이다.``로 잡는다(line40에만 1회). 라인번호는 claude 기준이며 codex `SKILL.md`는 frontmatter 차로 +1 — **문자열 앵커로** 찾는다.

APPEND (line40 유일 꼬리 뒤, 같은 불릿 안):
```
 **중앙 변환점의 *완전성*(미매핑 누수)**: 부분 중앙화(status 선택이 operation·application에 남음)와 *별개로* — operation이 raise/전파하는 *도메인·애플리케이션 의미를 가진* 예외(협력 포트 업스트림 포함) 중 어느 핸들러에도·ACL 번역에도 안 잡혀 framework 기본 500으로 새는 게 있으면 **important**다. *우선순위*: 그 미매핑 예외의 status 선택이 operation·application `try/except`에 남아 있으면 위 부분-중앙화 **blocker**가 우선하고, 이 important는 *핸들러 커버리지만 빈 깨끗-raise* 케이스에 한정한다. 정확한 status는 명세·§5 트레이드오프 몫이라 '왜 409가 아니냐'로 잡지 않고 '경계 도달 예외에 *어떤* 의도된 status도 없다(미매핑→500)'만 본다. **거짓지적 방지**: 프로그래밍 오류·서버 버그성 예외(`AssertionError`·`KeyError`류 — 클라이언트가 못 고치는 진짜 5xx)를 500으로 두는 건 정당하므로 status 배정을 강요하지 않는다(도메인·애플리케이션 *의미*를 가진 경계 예외의 미매핑만 본다).
```

- [ ] **Step 2: 검증** — `rg -c "중앙 변환점의 \*완전성\*" dddjango/agents/discipline-reviewer.md codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md` → 각 1. 두 append가 문자열 동일(`diff <(rg -o "중앙 변환점의 \*완전성\*.*" dddjango/agents/discipline-reviewer.md) <(rg -o "중앙 변환점의 \*완전성\*.*" codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md)` 빈 출력).

## Task 5: C2 — discipline-reviewer ACL 번역 전수성 (blocker) **[semantic]**

**Files:** 동 discipline-reviewer(line 41 "파일트리/구조 준수" 불릿 끝, "…를 인용한다.") 양본

- [ ] **Step 1: 양본에서 line 41 불릿 말미에 append**

APPEND:
```
 **ACL 번역 *전수성*(포트 계약 누수)**: ACL이 구동하는 업스트림 동작이 그 포트 경로에서 raise하는 예외(=협력 포트 ABC/docstring이 선언한 우리 쪽 예외 집합)를 ACL `try/except`가 빠짐없이 번역하는가 — 포트-선언 밖의 업스트림 예외가 ACL을 *통과해 우리 쪽으로 raw 전파*되면 포트 계약 누수(**blocker**). 결정적 백스톱 `check-context-isolation`은 *import* 결합만 보므로 import 없이 *전파*로 새는 변종은 네가 본다(위 'ACL 밖 직접 import' import-축과 직교). **거짓지적 방지**: (a) 업스트림이 던지나 ACL·리포지토리 내부에서 잡혀 다른 우리 쪽 예외로 번역·소진돼 경계에 raw 도달하지 않는 예외(예: `ProductModel.DoesNotExist`→`ProductNotFoundError` 내부 번역)는 누수가 아니다; (b) 동일 의미를 그대로 재노출(재raise)하는 것도 번역의 한 형태다; (c) `except Exception` 포괄 catch를 강요하는 게 아니라 포트-선언 구체 예외 집합의 누락만 본다.
```

- [ ] **Step 2: 검증** — `rg -c "ACL 번역 \*전수성\*" dddjango/agents/discipline-reviewer.md codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md` → 각 1 + 두 append 문자열 동일(diff 빈 출력).

## Task 6: D2 — design-architect 실패-모드 열거 **[semantic]**

**Files:** `dddjango/agents/design-architect.md`(line 34 "**계약(api)**" 불릿 끝) + `codex-dddjango/skills/dddjango-design-architect/SKILL.md`(동일)

- [ ] **Step 1: 양본에서 계약(api) 불릿 말미("…데이터 측면은 db lens로 넘긴다.") 뒤에 append**

APPEND:
```
 유한 재시도/CAS 등 동시성 메커니즘의 *실패 outcome*(재시도 소진·경합 미해소)도 경계로 관찰되면 상태 코드·에러 형식에 누락 없이 포함한다(미매핑 시 기본 500 누수) — 재시도 가능(retryable) status 배정(503+`Retry-After` 또는 409+확장, 둘 다 정당), 코드 선택은 멱등성·재시도 트레이드오프로 §5/G1에 올리고 임의 확정하지 않는다.
```

- [ ] **Step 2: 검증** — `rg -cF "재시도 소진·경합 미해소" dddjango/agents/design-architect.md codex-dddjango/skills/dddjango-design-architect/SKILL.md` → 각 1(`-F` 고정문자열 — 괄호·별표 regex 크래시 회피) + 두 append 문자열 동일(`diff` 빈 출력).

## Task 7: B 보류 — REMAINING-ISSUES/DEVLOG 기록 **[단일]**

**Files:** `workspace/eval/results/REMAINING-ISSUES.md`(있으면) + `workspace/DEVLOG.md`(DR 항목)

- [ ] **Step 1**: "CAS 소진·협력 포트 실패의 *종단(HTTP status) 인수테스트* 갭 — acceptance-tester에 실패-모드 종단 테스트 의무화는 *보류*(유일 신규 machinery·D2 게이트·N=1 LOW). 라이브 N≥2 재현 시 재개." + "결정적 백스톱 '예외 정의-집합 vs ACL catch 차집합' 변종도 내부-번역 예외 FP로 보류 — 재검토 후보." 기록.
- [ ] **Step 2: 검증** — 해당 파일에 항목 1회 존재 확인. **+ negative-guard**: `git diff --stat dddjango/agents/acceptance-tester.md codex-dddjango/skills/dddjango-acceptance-tester/` **빈 출력**(B는 기록만 — acceptance-tester 파일 무수정).

## Task 8: 사전 시뮬 (DR-22 필수) — C1/C2 발화·거짓-flag 격리 **[검증]**

- [ ] **Step 1: C2 발화 확인** — Claude rcqlive 픽스처(`~/Desktop/dddjango-rcqlive-claude`)에 C2 렌즈를 수기 적용: `application/order/infra_layer/acl/product_stock_adapter.py`가 catalog `StockConflictError`(업스트림 raise 3종 중)를 미번역 → **blocker 발화해야 함**(누수 실재).
- [ ] **Step 2: C2 비발화(거짓양성 0) 확인** — Codex 픽스처(`~/Desktop/dddjango-rcqlive-codex`) ACL이 3종 전수 번역 → **비발화**.
- [ ] **Step 3: carve-out FP 0 확인** — 양 픽스처에서 `DoesNotExist`→내부 번역(리포지토리)·`AssertionError`류가 C1/C2에 **거짓-flag 안 됨** 확인.
- [ ] **Step 4**: 결과를 계획에 메모(0/N이면 문구 보강 — DR-22 분기).

## Task 9: 무회귀·미러·용어 게이트 **[검증]**

- [ ] **Step 1: 13 백스톱 재실행 무회귀** — `for f in dddjango/scripts/check-*.py; do python "$f" <대상> ; done`이 기존과 동일(이 변경은 스크립트 무수정).
- [ ] **Step 2: [byte] 미러 diff** — Task1·2·3 대상의 편집 hunk가 claude↔codex 동일(`git diff` 양 트리 동일 hunk).
- [ ] **Step 3: 용어 일관(수기)** — C1(완전성)·C2(전수성)가 같은 reviewer 파일에 공존하므로 단순 카운트로 혼용 판별 불가 → *수기 검토*로 "ACL/포트 맥락=전수"·"중앙핸들러 맥락=완전성"으로 쓰였는지 확인(자동 grep 강등).
- [ ] **Step 4: 한정구 잔존 0** — `rg -c 'domain_layer` 하위' dddjango/skills/discipline-houserules/references/final.md codex-dddjango/skills/discipline-houserules/references/final.md` → **0**(NEW가 `domain_layer`/`application_layer` 하위`로 바꿔 단독 한정구 인접을 파괴 — lookahead 불요·rg 미지원이라 사용 금지).

---

## 구현 전 적대 리뷰 (이 계획 대상)
이 계획이 설계 v2를 *충실히·완전히* 반영했는지: ① 6 편집 텍스트가 설계 A1·E·A2·C1·C2·D1·D2와 의미·심각도 일치 ② 미러 [byte]/[semantic] 분류 정확 ③ 거짓지적 carve-out 누락 없음 ④ B 보류·백스톱 보류가 계획에 반영 ⑤ 검증 게이트가 falsifiable. → 적대 서브에이전트 검증 후 실행.

## 커밋 정책
커밋·push는 **사용자 명시 승인 시만**. 서브에이전트는 개정+검증만. trailer `Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>`.
