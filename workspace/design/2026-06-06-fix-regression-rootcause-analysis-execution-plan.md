# 수정 회귀 근본원인 분석 — 실행 플랜 (진단까지)

> **For agentic workers:** 이 플랜은 *코드 구현*이 아니라 *진단 조사*다. 각 Task는 서브에이전트 디스패치 + 산출 검수 단계로 구성된다. 단계는 체크박스(`- [ ]`)로 추적한다. 실행은 조정자(메인 세션) 인라인 권장(executing-plans) — 각 Phase 산출을 사람이 검토 후 다음 Phase.

**Goal:** "왜 dddjango 수정이 stick 하지 않나"를 전수 증거로 진단 — 실패모드 분류표·에피소드×모드 매트릭스·근본 클러스터·열린발견 매핑·권고 개입 방향까지 산출(처방/구현은 별도 합의).

**Architecture:** 하이브리드 — (1) 실패모드 렌즈별 서브에이전트 병렬 전수 수집 → (2) 조정자 합성 → (3) 독립 적대 서브에이전트 반증 → (4) 진단 문서. 진단 자체의 앵커링/1차진단오류를 적대 검증으로 차단.

**Tech Stack:** 메인 세션 조정 + Agent 서브에이전트(general-purpose, read-only 정독). 산출 = markdown 아티팩트 `workspace/eval/rootcause/`. Workflow/ultracode 미사용(일반 Agent 디스패치).

**정본 신뢰원:** `workspace/DEVLOG.md`(§2 DR-16~45·§3 DO-NOT-RETRY·§4) · `workspace/eval/results/REMAINING-ISSUES.md` · 결과지 `workspace/eval/results/*.md` · 계획서 `workspace/design/2026-06-06-fix-regression-rootcause-analysis-plan.md`.

**라벨 규율:** 렌즈 코드 L1~L6은 *내부 작업 라벨*. 사용자 보고·진단 문서엔 DR 번호·루브릭 코드(NJ-2·SD-6·FC-1 등)로 환원. 새 약칭 발명 금지.

---

## 파일 구조 (생성·산출 아티팩트)

- Create: `workspace/eval/rootcause/episodes.md` — 에피소드 마스터 리스트(Task 0)
- Create: `workspace/eval/rootcause/lens-L1..L6.md` — 렌즈별 수집 산출(Task 1, 6편)
- Create: `workspace/eval/rootcause/synthesis.md` — 합성: 매트릭스·클러스터·가설검정(Task 2)
- Create: `workspace/eval/rootcause/adversarial.md` — 적대 검증 노트(Task 3)
- Create: `workspace/eval/rootcause/DIAGNOSIS.md` — 최종 진단 문서 = deliverable(Task 4)

각 Task 끝에 커밋. 작은 단위·검수 게이트 사이.

---

## Task 0: 증거 코퍼스 동결 + 에피소드 마스터 리스트

**Files:**
- Create: `workspace/eval/rootcause/episodes.md`
- Read: `workspace/DEVLOG.md` (§2 DR-16~45·§3 DO-NOT-RETRY) · `workspace/eval/results/REMAINING-ISSUES.md`

- [ ] **Step 1: 코퍼스 정독 (조정자 직접)**

DEVLOG §2의 DR-16~45 각 엔트리 헤더·상태태그, §3 DO-NOT-RETRY 14항, REMAINING-ISSUES 상태표를 읽는다. 각 "수정 에피소드"를 식별: DR 1건 = 1 에피소드(원칙), 단 한 DR이 여러 독립 처방을 담으면 분할(예: DR-44 = ACL-A/E + reviewer-C1/C2 + api-D1/D2).

- [ ] **Step 2: `episodes.md` 작성**

표 스키마(정확히 이 칼럼):

```markdown
| episode_id | 제목(짧게) | 처방 요약 | 소스 앵커 | 알려진 후속 결과 |
|---|---|---|---|---|
| DR-44 | ACL 예외 전수성 | houserules 전수번역+포트앵커E+reviewer C1/C2 | DEVLOG:359·design 2026-06-06-acl…v2 | DR-45 라이브=부분미완(인프라예외 누수) |
| P1a | ninja 오류 중앙화 | 긍정레시피→v3 결정적 백스톱 | REMAINING-ISSUES P1a·DR-20~24 | 5회 반복·릴리스 보류 |
```

열린 발견(`is_open`)도 에피소드로 포함: ACL-EX·깨진JSON·위장oversell테스트·위장constraint테스트·NJ-4·SD-7·C3·C4·catalog회귀·BC경계·G0-plain.

- [ ] **Step 3: 검수 — 완전성 확인**

Run: `grep -c "^### DR-" workspace/DEVLOG.md` → DR 개수 확인. `episodes.md`의 DR 행 수가 그 이상(분할 포함)인지, REMAINING-ISSUES 상태표의 모든 ID가 매핑됐는지 대조. 누락 0.

- [ ] **Step 4: 커밋**

```bash
git add workspace/eval/rootcause/episodes.md
git commit -m "eval(rootcause): Phase0 에피소드 마스터 리스트 동결"
```

---

## Task 1: 병렬 증거 수집 — 6 렌즈 서브에이전트

**Files:**
- Create: `workspace/eval/rootcause/lens-L1.md` … `lens-L6.md`
- Input: `workspace/eval/rootcause/episodes.md` + 정본 코퍼스

- [ ] **Step 1: 공통 디스패치 프롬프트 확정**

각 렌즈 서브에이전트(subagent_type: general-purpose)에 보낼 프롬프트 = 아래 공통부 + 렌즈 고유부.

공통부(그대로):
```
너는 dddjango 표준 하드닝 작업의 "수정 회귀" 진단을 돕는 독립 조사관이다.
정본을 1차 소스로 직접 읽어라(요약·메모리 불신): workspace/DEVLOG.md(§2 DR-16~45·§3),
workspace/eval/results/REMAINING-ISSUES.md, workspace/eval/results/*.md,
workspace/eval/rootcause/episodes.md(에피소드 마스터 리스트).

너의 임무: episodes.md의 각 에피소드를 검토해 "<렌즈>" 실패모드를 보이는 것을 전수 추출하라.
이 렌즈에 confirm-only로 강요하지 마라 — 이 렌즈에 안 맞으면 적지 마라. 다른/새 모드가 보이면 NEW:<이름>으로 별도 플래그.
모든 주장에 증거 앵커(DR#·file:line·결과지 인용)를 달아라. 추측 금지, 텍스트 근거만.

산출(이 markdown 표만 반환, 산문 최소):
| episode_id | mode | evidence_anchor | severity(critical|major|minor) | is_open(yes|no) | note(한줄) |
```

- [ ] **Step 2: 렌즈 고유부 6종**

```
L1 비결정 — "같은 입력·같은 표준 버전인데 치명 FAIL 레인(또는 BC경계·판정소유 등)이 런마다 갈린 사례. P4③ run-variance. 반전(c4live↔nj2live)·펄럭(catalog 위치)·런타임 교차도 포함."
L2 집행 갭 — "표준 문구·reviewer prose·긍정 레시피가 라이브 파이프라인서 미발화하거나 blocker→권고로 강등된 사례. 사전시뮬 통과했으나 라이브 실패한 것 포함."
L3 백스톱 맹점 — "결정적 백스톱이 exit0(통과)인데 의미 변종이 통과한 사례, 또는 백스톱이 원리상 못 보는 변종, 또는 백스톱 부재로 못 잡은 사례. 고정밀·저recall."
L4 부분 미완 — "처방 스코프를 너무 좁게 앵커해 형제/변종이 누수한 사례(예: 도메인 예외만 잡고 인프라 예외 누수)."
L5 1차 진단 오류 — "첫 진단이 철회·번복되거나 방향이 2번 이상 뒤집힌 사례, DO-NOT-RETRY에 박힌 헛다리, 조정자 자기-정정."
L6 회귀 — "한 번 고쳤다고 본 것이 이후 런/감사서 다시 나타난 사례. 각 건마다 '진짜 회귀인가 vs L1×N=1 오측정인가'를 evidence_anchor로 판별 시도."
```

- [ ] **Step 3: 6 서브에이전트 병렬 디스패치**

Agent 도구로 6개를 **한 메시지에 동시** 디스패치(subagent_type: general-purpose, description: "rootcause lens L#"). 각 반환 표를 받아 `lens-L1.md`…`lens-L6.md`로 저장(각 파일 머리에 렌즈 정의 1줄 + 표).

- [ ] **Step 4: 검수 — 산출 스키마·앵커 확인**

각 lens 파일이 표 스키마 준수, 모든 행에 evidence_anchor 존재, episode_id가 episodes.md에 실재하는지 확인. 앵커 없는 행·환각 에피소드 0. (스팟체크: 무작위 3행의 DR#/file:line을 정본과 대조.)

- [ ] **Step 5: 커밋**

```bash
git add workspace/eval/rootcause/lens-L1.md workspace/eval/rootcause/lens-L2.md workspace/eval/rootcause/lens-L3.md workspace/eval/rootcause/lens-L4.md workspace/eval/rootcause/lens-L5.md workspace/eval/rootcause/lens-L6.md
git commit -m "eval(rootcause): Phase1 6렌즈 병렬 증거수집"
```

---

## Task 2: 합성 — 에피소드×모드 매트릭스·클러스터·핵심가설 검정

**Files:**
- Create: `workspace/eval/rootcause/synthesis.md`
- Input: `lens-L1.md`…`lens-L6.md` + `episodes.md`

- [ ] **Step 1: 매트릭스 구성 (조정자 직접)**

6 렌즈 산출을 병합. 행=에피소드, 열=모드(L1~L6 + 발견된 NEW). 셀=해당 모드 표시(severity). 한 에피소드가 여러 모드를 보이면 다중 표시. 중복 행(같은 에피소드를 여러 렌즈가 잡음) 정리.

```markdown
| episode | L1 | L2 | L3 | L4 | L5 | L6 | (NEW…) |
|---|---|---|---|---|---|---|---|
| DR-44/ACL | | | ● major | ● major | | ● | |
```

- [ ] **Step 2: 클러스터 도출**

어느 모드가 공기(co-occur)하는지, 어느 모드가 상류 원인이고 어느 게 하류 증상인지 분석. 예상 검정: "L6(회귀)·L4(부분미완)가 L1(비결정)·L3(백스톱맹점)과 얼마나 공기하나". 클러스터에 ID 부여(C-a, C-b…)하되 *진단 문서에선 DR/루브릭으로 환원*.

- [ ] **Step 3: 핵심 가설 검정 — 측정문제 vs 수정문제**

L6(회귀)·"안 고쳐짐" 에피소드 각각을 분류: (가) 진짜 수정 실패(처방이 틀렸거나 좁음) vs (나) L1×N=1 오측정(처방은 stick했으나 다른 런이 다른 잠재결함을 우연히 노출). 비율과 근거를 적는다. **이 갈림이 처방 방향(표준 강화 vs 평가방법 개편)을 가른다.**

- [ ] **Step 4: 열린 발견 매핑**

ACL 인프라누수·깨진JSON·위장테스트2건을 각 클러스터에 매핑(어느 근본의 증상인가).

- [ ] **Step 5: `synthesis.md` 작성 + 커밋**

매트릭스·클러스터·가설검정·매핑을 문서화. 이 단계는 **반증 전 초안**임을 명시(Phase 3가 깰 수 있음).

```bash
git add workspace/eval/rootcause/synthesis.md
git commit -m "eval(rootcause): Phase2 합성 초안 — 매트릭스·클러스터·측정vs수정 가설"
```

---

## Task 3: 적대 검증 — 독립 회의론자 반증

**Files:**
- Create: `workspace/eval/rootcause/adversarial.md`
- Input: `synthesis.md` + `episodes.md` + 정본 코퍼스

- [ ] **Step 1: 적대 디스패치 프롬프트 확정**

3개 독립 회의론자(subagent_type: general-purpose). 프롬프트(그대로):

```
너는 dddjango "수정 회귀" 진단 초안(workspace/eval/rootcause/synthesis.md)을 반증하는 독립 회의론자다.
기본 입장 = 반증. 불확실하면 "기각" 쪽으로 판정하라. 동의는 쉽고 반증은 어렵다 — 어려운 쪽을 하라.
정본(DEVLOG·결과지·episodes.md)을 직접 읽어 대조하라.

각 클러스터/근본 주장에 대해 판정하라:
(a) N=1에서 과대일반화했나? (b) 인과 주장이 post-hoc 합리화 아닌가(상관≠인과)?
(c) 합성이 놓친 에피소드/모드가 있나? (d) "근본"이 증상의 재진술에 불과한가?
(e) "측정문제 vs 수정문제" 분류가 각 에피소드서 정당한가?

산출(이 표만):
| cluster_or_claim | verdict(survives|refuted|uncertain) | reason(증거앵커 포함) | missed_or_correction |
```

각 회의론자는 렌즈를 약간 달리: 회의론자1=인과/post-hoc 집중, 회의론자2=N=1/과대일반화 집중, 회의론자3=누락/재진술 집중.

- [ ] **Step 2: 3 회의론자 병렬 디스패치**

한 메시지에 동시 디스패치. 반환 표 3개를 `adversarial.md`로 통합 저장.

- [ ] **Step 3: 검수 — 판정 수렴 분석**

클러스터별로 3 판정 집계. ≥2 refuted = 강등(진단서 기각·사유 보존). survives = 확정. uncertain 다수 = "N≥2 후속 필요"로 표기. 누락 지적(missed)은 episodes.md/synthesis 갱신 트리거.

- [ ] **Step 4: 커밋**

```bash
git add workspace/eval/rootcause/adversarial.md
git commit -m "eval(rootcause): Phase3 적대 검증 — 3 회의론자 반증"
```

---

## Task 4: 진단 문서 산출 (deliverable)

**Files:**
- Create: `workspace/eval/rootcause/DIAGNOSIS.md`
- Input: `synthesis.md`(적대 반영 갱신) + `adversarial.md`

- [ ] **Step 1: 확정 클러스터 반영**

Phase 3서 survives한 클러스터만 본문에. refuted/uncertain은 별도 절에 *기각 사유와 함께* 보존(투명성·DO-NOT-RETRY 후보).

- [ ] **Step 2: `DIAGNOSIS.md` 작성 — 5요소**

```markdown
# dddjango 수정 회귀 — 진단 (N=1 경계)
## 1. 실패모드 분류표 (정의 + 에피소드 증거)
## 2. 에피소드 × 모드 매트릭스
## 3. 근본 클러스터 순위 (가장 체계적인 것부터·신뢰도)
## 4. 열린 발견(ACL·JSON·위장테스트) → 클러스터 매핑
## 5. 근본별 권고 개입 *방향* (설계 아님) + 잔여 N=1·불확실
## 부록. 적대 검증서 기각된 가설 (사유 보존)
```

라벨 규율 적용: 본문 식별자 = DR 번호·루브릭 코드. L1~L6은 분류표 정의 절에서만 내부 라벨로 도입하고 매핑.

- [ ] **Step 3: 셀프 검수**

§1 계획서(spec)의 5 산출 요소가 모두 DIAGNOSIS.md에 있나 대조. 플레이스홀더(TBD/TODO) 0. 각 클러스터 주장에 증거 앵커 존재. 권고가 "방향"에 머무르고 구체 설계로 새지 않았나(경계 준수).

- [ ] **Step 4: 커밋 + 사용자 검토 요청**

```bash
git add workspace/eval/rootcause/DIAGNOSIS.md
git commit -m "eval(rootcause): Phase4 진단 문서 — 분류·클러스터·매핑·권고방향 (deliverable)"
```

진단 문서를 사용자에게 검토 요청. 처방·구현 합의는 별도 턴(이 플랜 경계 = 진단까지).

---

## Self-Review (작성자 체크)

**1. Spec 커버리지:** 계획서 §1의 5 산출 요소 → Task 4 Step 2의 5절로 1:1. 4 Phase(0~4) → Task 0~4로 1:1. ✔
**2. 플레이스홀더:** 서브에이전트 프롬프트·산출 스키마·커밋 메시지 모두 실제 내용. TBD 0. ✔
**3. 일관성:** 산출 파일명(episodes.md·lens-L#.md·synthesis.md·adversarial.md·DIAGNOSIS.md)이 파일구조·각 Task서 동일. 렌즈 코드 L1~L6 정의가 Task1 Step2와 계획서 §4 일치. ✔
**4. 라벨 규율:** 모든 Task가 DR/루브릭 환원 명시. ✔
