# OHS contract 3패키지 승격(folder-from-birth) 규약 개정 계획 (적대 리뷰 반영판 v2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:executing-plans. Steps use checkbox (`- [ ]`) syntax.
> v1 대비: 3축 적대 리뷰(모순 M-1~14·과적합 O-1~11·실효성 E-1~12) 중재 반영 — **RUBRIC :28 "contract 3파일" 실존(v1의 유일한 사실 오류) 교정**(M-1·O-8·E-1), 확정 문안 자기모순 2건 해소(M-2 재노출 불변식 ⒝ 카브아웃 inline·M-3 exception 내 base 상속 import 허용), exception 판단형 잔존 제거(O-2 — **예외 클래스당 1모듈** 채택), exception 연산-축 과일반화 3곳 분기 표기(M-4·O-1·E-6), 부분 이주 조문(M-10 — 3파일형에 새 연산 추가는 물리적으로 kind 승격 강제), `<operation>`=공개 함수명 등식+reviewer 절차·산출 형식(E-5), 방향 규율 reviewer 배정(E-8 — 백스톱 비대상 명시), 공유 타입 3구멍(O-3 — kind 간 공유=response 소유·접미 배타·소비 표면 병기), same-kind 연산 파일 간 직접 import 금지(O-4), response 별칭 1줄 허용·재선언 금지(Q4 — 3축 일치), 통과 불가 grep 2건 교정(M-8/E-3·M-9/E-2), §1.1 단서·안티패턴 캐리어 갱신(M-11/O-7·E-9), "유일한 한시 예외"→"2형" 교체(M-5), DR-62 유지 판정 번복 명시 기록(M-7), 발화 매트릭스 확장(E-7·O-9), check-layer-skeleton 인용 교정(M-13/E-10), diff 대조 방법 명시(E-11).
> **시술 적대 검증(3축) 교정 반영(2026-07-08)**: R-1(부분 승격 시 기존 계약 재배치 명세)·R-2(역대조 — orphan·접미 위장)·R-3(재선언 금지 레인 배정)·R-4~R-6·R-8(캐리어 표현)·C-1~C-4(계획·DEVLOG 기록 정밀화)·T-1/T-2(백스톱 known-limitation — DEVLOG 기록, 코드 수정은 별도 패치 분리)·T-3/T-4(표기).

**Goal:** ① `contract/` 내부를 3파일 고정 → **3패키지 고정**(`request_contract/`·`response_contract/`·`exception_contract/`)으로 개정 — request/response는 연산당 1파일(`<operation>`=공개 함수명), exception은 base 모듈+예외 클래스당 1모듈, folder-from-birth. ② "계약 모듈이 비대해지면 같은 이름의 디렉터리로 승격한다"(판단형) 조문 폐지 + 부분 이주(⒝ 심) 경로 신설. ③ 백스톱 코드 변경 0(S2 깊이 무관 — 실측·3축 교차 확인) + 발화 매트릭스 패키지형 보강.

**Architecture:** 배포본 `dddjango/` 수정 → final.md는 `corpus_mirror_sync --write`가 소스(workspace/reference)·codex로 전파, SKILL.md·agents는 수동 미러(본문 문자열 일치 대조 — 행 오프셋 상이하므로 파일 diff 아님). 집행 4층: 표준(final.md) + 생산자(design-architect) + reviewer 의미 레인 + 백스톱(변경 없음 — 게이트 18 불변).

## 회부 질문 확정 판정 (3축 중재)

1. **공유 값 타입 모듈 명명**: bare명 유지(§4 "파일명=주 클래스명 snake_case"의 적용 — 접미 신설은 §4와 모순이라 기각, 3축 일치). 결정성 보강 2곳: `_contract` 접미 금지(연산 파일 전용 표지 — 이진 분류 성립), 공유 모듈 목록을 architect 명세 1급 결정에 편입.
2. **base 모듈 파일명 고정**: `<service>_published_error.py` 채택 — `<Service>PublishedError`(§4 기고정)의 snake_case 기계 귀결이지 신규 명명 축 아님(병기). reviewer ①에 base presence 점검 편입.
3. **연산↔파일 대응 심각도**: important 유지(3축 일치 — blocker는 경계 붕괴 유보·DR-62 "3파일 미비 important"와 등가). 전제 3건 동시 반영: 국소 수정 면제 교정(M-12/E-4)·절차+산출 형식 강제(E-5)·response 대응 병기(O-5).
4. **response 공유**: 연산당 1파일 유지 + 공유 모듈 import·명시 별칭 1줄 허용·재선언 금지 명문화. 별칭은 연산 축 안정 경로(분화 시 소비자 경로 불변 — 근거 2의 재적용)이지 `__init__` 재노출이 아님을 1구로 구분(3축 일치).
5. **이주 심 ⒝형**: 백스톱 오인 없음 확정(코드 실측 — 상대 import 스킵 `:141`·절대 재노출은 `LAYER_ANY_RE` 계층 한정 비매치, 3축 교차 확인). 카브아웃 3곳 세트 완결(조문 ① inline·reviewer ①·SKILL :63 — DR-62 더블 바인드 처방 동형) + "유일한"→"2형" 교체 + 침묵 픽스처 실측 고정 + 부분 이주 조문(M-10).

## Global Constraints

- 개정 일자 2026-07-08 병기(:150 관례 형식). 백스톱 변경 0(게이트 18 불변). 커밋은 전체 검증 후 사용자 확인.
- §0 오귀속 재발 방지: 3패키지 고정은 OHS 고유 규칙 유지 — 단 M-14대로 "형태·평면 나열 방지 논리가 §0와 겹치더라도 귀속·집행 경로는 §2와 reviewer 불릿"으로 재서술(§0 목록에 추가하지 않는다).
- DEVLOG에 DR-62 과적합 리뷰 "3파일 고정 유지" 판정의 **번복을 명시 기록**(M-7): 판정 오류가 아니라 리뷰 당시 부재하던 신규 증거(운영 관측 — 3연조가 만드는 구조적 비대화)에 의한 번복.

---

## Part A — 플러그인 표준 개정

### Task A1: discipline-houserules final.md — §2 OHS 절 개정 (6곳)

- [x] Step 1: `:139-146` 트리 블록 — 3패키지+연산당 1파일+base/구체 예외 2행으로 교체.
- [x] Step 2: `:150` 조문 ① 전면 개정 — v2 확정 문안(3패키지·folder-from-birth 근거(신생 표면 한정+⒝ 비파괴화)·§0 귀속-집행 재서술·내부 파일 규율(`<operation>`=공개 함수명 등식·공유 모듈 §4 규칙+접미 배타+response 소유·별칭 1줄·exception base 필수+클래스당 1모듈)·빈 패키지·재노출 문장 ⒝ inline 카브아웃·소비자 경로 3형(연산 계약·공유 모듈·published 예외) — 승격 문장 삭제).
- [x] Step 3: `:156` 조문 ④ — import 방향 패키지판: `request_contract/* → response_contract/*` 단방향·same-kind는 연산→공유 방향만(연산 파일 간 직접 금지)·`exception_contract/*`는 타 kind 금지+자기 base 상속 import 허용+계약 타입 비적재.
- [x] Step 4: `:158` 이주 조문 전문 교체 — 대상에 구 3파일형 병기·부분 이주(kind 승격+⒝ 심)·심 2형(⒜⒝)·"유일한 한시 예외"→"한시 예외 2형".
- [x] Step 5: `:231` §3 표 행 — kind 분기 표기(request/response 연산당 1파일·exception base+클래스당 1모듈).
- [x] Step 6: `:273` §4 OHS 행 — 3패키지 고정명·연산 파일명 2종·base 파일명(§4 귀결 병기)·공유 모듈 접미 배타. V1 재량 유지.
- [x] Step 7: 검증 — `grep -n "3파일" final.md` 잔존=이주·개정 표기뿐; `grep -n "비대해지면" final.md`(houserules 한정) 잔존 0; `grep -nE "(^|[^_>])request_contract\.py" final.md` 잔존=이주 조문의 구형 지칭뿐(신문안 `<operation>_request_contract.py`는 비매치 — E-3 교정 패턴).

### Task A2: discipline-houserules SKILL.md — 상시 캐리어 3곳 (codex 미러)

- [x] Step 1: `:29` 요약 — 3패키지·kind 분기(request/response 연산당 1파일·exception base+클래스당 1모듈·folder-from-birth) 반영.
- [x] Step 2: `:28` §1.1 답습금지 단서 — 열거에 "구 3파일형 contract(계약 *모듈*)" 병기 + 부분 승격(⒝ 심) 경로 1구(M-11/O-7).
- [x] Step 3: `:63` 안티패턴 — 심 카브아웃을 2형(⒜⒝)으로 확장(E-9 — 3곳 세트 완결).
- [x] Step 4: codex `codex-dddjango/skills/discipline-houserules/SKILL.md` 동일 반영 — 대조는 편집 구절 문자열 일치(E-11).

### Task A3: discipline-reviewer OHS 불릿 개정 (codex 미러)

- [x] Step 1: `:50` — 스코프 라인 구형 일반화(read/write·3파일형, 국소 수정 면제 — M-12/E-4) + ① 재작성: 3패키지 미비·연산↔계약 파일 대응(공개 함수 목록 추출→파일 존재 대조→**함수별 대응 여부 발견 항목 명시** 절차 — E-5)·base 모듈 presence(Q2)·방향 규율(백스톱 비대상 명시 — E-8)·카브아웃(심 2형·공유 모듈·별칭·0-인자·None).
- [x] Step 2: codex `codex-dddjango/skills/dddjango-discipline-reviewer/SKILL.md` 동일 반영(문자열 일치 대조).

### Task A4: design-architect OHS 레인 (codex 미러)

- [x] Step 1: `:40` — contract 3패키지·계약 파일명 2종(`<operation>`=공개 함수명)·공유 모듈 목록·base 모듈을 명세 1급 결정 목록에 확장(E-12·O-1).
- [x] Step 2: codex `codex-dddjango/skills/dddjango-design-architect/SKILL.md` 동일 반영.

### Task A5: 백스톱 무변경 확인 + 발화 매트릭스 (확장판 — E-7·O-9)

- [x] Step 1: `check-context-isolation.py` 코드 diff 0 확인. docstring·commands ⑥·codex SKILL ⑥의 S2 서술은 깊이 무관 glob이라 유지(3축 실측 일치).
- [x] Step 2: scratchpad 합성 픽스처 매트릭스(7종 실측) — **발화 3**: ⑴ `contract/request_contract/<op>_request_contract.py`→`domain_layer` import=exit2 ⑵ 동 위치→자기 BC `application_layer` import=exit2 ⑶ cross-BC domain 직접 import=exit2(S1 회귀). **침묵 4**: ⑷ 패키지형 clean(표준 라이브러리+same-kind 공유 모듈 import+영수증 cross-kind request→response+exception base 상속)=exit0 ⑸ ⒝ 심 `<kind>_contract/__init__.py` 재노출=exit0(Q5 실측 고정) ⑹ 타 BC published 소비=exit0(회귀) ⑺ cross-kind 역방향(response→request)=exit0 — 백스톱 원리상 비대상(계층 경로만 매치)임을 실측, reviewer ① 몫.
- [x] Step 3: RUBRIC.md `:28` — `contract 3파일`→`contract 3패키지(request/response 연산당 1파일)`·`(2026-07-07 신설)`→`(2026-07-07 신설·2026-07-08 3패키지 개정)` (M-1/E-1/O-8 — workspace 전용이라 미러 불요).

### Task A6: 미러 동기·검증·기록

- [x] Step 1: `corpus_mirror_sync.py --write` → `--check` exit 0.
- [x] Step 2: `claude plugin validate dddjango --strict` PASS. (`--strict` 플래그 아님 — `claude plugin validate dddjango` 형태 확인)
- [x] Step 3: 잔존 grep — `grep -rn "3파일" dddjango/ codex-dddjango/ workspace/eval/` 잔존=이주·개정 표기뿐(E-1 스코프 확장); `grep -rn "비대해지면" dddjango/skills/discipline-houserules/ codex-dddjango/skills/discipline-houserules/` 잔존 0(M-9/E-2 — implementation-django §16 모델 비대 서술은 무관 정당 잔존이라 스코프 제외).
- [x] Step 4: DEVLOG §2 DR-63(발단·확정 규칙·번복 명시(M-7)·비용 유비 2축 분리(O-10)·백스톱 변경 0 근거·매트릭스 결과) + §0 최근 작업 1줄.
- [ ] Step 5: `git diff --stat` 전수 확인 → 사용자 확인 후 단일 feat 커밋.

## Part B — 외부 프로젝트 적용 (미결 — 사용자 확인 대기)

- [ ] DR-62 Part B(delivery 앱)의 적용 여부 확인 → 미적용이면 목표 트리를 3패키지형으로 갱신한 스펙, 적용됐으면 ⒝ 심 2차 이주 스펙(B0 소비처 조사 재사용). 적용은 대상 프로젝트 세션 몫.

## Self-Review (v2)

- 3축 발견 전건 처리: M-1~14 채택 14(M-1 RUBRIC·M-2/M-5 문안·M-3 exception import·M-4 분기 3곳·M-6은 조문 ① 소비자 경로 3형(연산 계약·공유 모듈·published 예외)에 O-3⒝와 합산 반영·M-7 번복 기록·M-8/M-9 grep·M-10 부분 이주·M-11 §1.1·M-12 면제·M-13 인용·M-14 귀속 재서술) · O-1~11 채택 11(O-2 클래스당 1모듈 주안 채택·O-6은 M-2와 동일 처방(재노출 문장 inline 카브아웃)에 흡수·O-10은 DEVLOG 한정·O-11은 이주 조문 전문 교체(A1 Step 4)로 이행) · E-1~12 채택 12(E-8은 reviewer ① 배정으로 이행). 기각 0 — 상호 모순 발견 없음(RUBRIC·exception 분기·⒝ 심은 3축 수렴).
- DR-62 유지 판정 존중(3파일 고정만 명시 번복 — 본 DR의 대상): request 1개 규칙·`<service>_service` 명명·공개 클래스 금지·3연조·예외 번역·transient 짝·birth-enum 카브아웃 불변.
- 게이트 18 불변 — 백스톱 코드 diff 0.
