# dddjango 산출물 관리 규약 구현 계획 (DR-40 v2)

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** `.dddjango/` 산출물 폴더를 `<생성일 YYYYMMDD-HHMM>-<slug>`(생성일 고정)로 바꾸고, 재빌드는 코디가 기존 폴더 목록을 사용자에게 보여 고르게 해 "한 기능 한 폴더"를 결정적으로 보장하며, 커밋 대상임을 명문화한다.

**Architecture:** claude `commands/dddjango.md`와 codex `skills/dddjango/SKILL.md`의 「산출물 위치」 절 + Phase 0(G0 배너) 절차를 byte-identical 미러로 개정한다. 재빌드 재사용은 glob 자동매칭이 아니라 **Phase 0에서 기존 폴더 목록을 사용자에게 제시·선택**하게 한다(적대 리뷰 B1 완화 — slug 재계산 비결정 회피). 백스톱·design-architect·다른 에이전트는 무변경(실제 스크립트 실행으로 회귀 실측).

**Tech Stack:** Markdown 명세 편집, `plugin.json`(JSON), bash glob/`date`, `plugin validate`(claude), Python 백스톱 스크립트(회귀 실측).

---

## File Structure

| 파일 | 책임 | 작업 |
|------|------|------|
| `dddjango/commands/dddjango.md` | claude 코디 명세 — 「산출물 위치」(L12-18) + Phase 0 G0 배너(L62) | Modify |
| `codex-dddjango/skills/dddjango/SKILL.md` | codex 코디 명세 — 「산출물 위치」(L60-66) + Phase 0(L81) + spawn 경로(L87) | Modify |
| `dddjango/.claude-plugin/plugin.json` | claude 매니페스트 version | Modify |
| `codex-dddjango/.codex-plugin/plugin.json` | codex 매니페스트 version | Modify |
| `workspace/DEVLOG.md` | 결정 원장 DR-40 | Modify |
| 개인 메모리 `memory/dddjango-output-folder-convention.md` + `MEMORY.md` | 세션 회상 | Create/Modify |

검증만(편집 없음): `dddjango/scripts/check-idempotency-scope-creep.py` + codex 사본 glob 회귀 / `.claude-plugin/marketplace.json`·`.agents/plugins/marketplace.json` version 핀 부재.

---

### Task 1: claude 「산출물 위치」 절 + Phase 0 폴더 결정 절차

**Files:**
- Modify: `dddjango/commands/dddjango.md:12-18` (산출물 위치)
- Modify: `dddjango/commands/dddjango.md:62` (Phase 0 step 3, G0 배너)

- [ ] **Step 1: 편집 전 미러 baseline 확인**

Run:
```bash
diff <(sed -n '12,18p' /Users/hyun/Desktop/dddjango/dddjango/commands/dddjango.md) \
     <(sed -n '60,66p' /Users/hyun/Desktop/dddjango/codex-dddjango/skills/dddjango/SKILL.md)
diff <(sed -n '53,62p' /Users/hyun/Desktop/dddjango/dddjango/commands/dddjango.md) \
     <(sed -n '72,81p' /Users/hyun/Desktop/dddjango/codex-dddjango/skills/dddjango/SKILL.md)
```
Expected: 두 diff 모두 빈 출력(산출물 위치 절·Phase 0 절이 현재 byte-identical).

- [ ] **Step 2: 「산출물 위치」 절(L12-18)을 교체**

신규(claude/codex 동일 바이트):
```markdown
## 산출물 위치

- 스코프 메모 → `<산출물 폴더>/scope.md`
- 설계 명세 → `<산출물 폴더>/design-spec.md` (이 경로를 design-architect에 전달)
- 인수 테스트·구현 코드 → acceptance-tester·coder가 **승인된 명세의 패키지·테스트 구조 결정 절**에 맞춰 배치한다(네가 그 구조 절을 전달한다 — 위치·규약은 설계에서 결정되어 명세에 담겨 있다).

`<산출물 폴더>`는 `.dddjango/<생성일>-<기능-slug>/`다 — `<생성일>`은 이 기능을 *처음 빌드하는 시각*을 폴더 생성 직전 `date +%Y%m%d-%H%M`(로컬)로 얻은 값이고(LLM이 추측하지 않는다 = 결정성), `<기능-slug>`는 기능 설명을 영문 케밥케이스로 줄인 것이다(한글 요청이어도 영문, 2~4단어). 폴더를 확정하는 절차는 Phase 0을 따른다.

**한 기능 = 한 폴더**다. 같은 기능을 다시 빌드(수정 모드 포함)하면 새 폴더를 만들지 말고 기존 폴더를 재사용한다(생성일 prefix·slug 유지). design-architect가 명세를 제자리 수정하므로 폴더엔 늘 최종본 하나만 남고, 폴더를 정렬하면 기능별 생성 타임라인이 보인다.

이 `.dddjango/` 산출물은 빌드 부산물이 아니라 그 기능의 **설계 결정 기록**이다 — 코드와 함께 커밋해 PR 리뷰·이후 확장의 근거로 남기고 `.gitignore`에 넣지 않는다(단 내부 설계 노출이 민감한 레포면 `.dddjango/`를 ignore해도 된다 — 기본은 커밋이다).
```

- [ ] **Step 3: Phase 0 step 3(G0 배너, L62)에 폴더 결정 절차를 통합**

기존 step 3 문장 끝(`...재현 불가).`) **다음에 이어** 아래를 추가(claude/codex 동일 바이트):
```markdown
 **그리고 이 작업이 기존 기능의 재빌드·수정이거나 `.dddjango/`에 관련 폴더가 이미 있으면**, 먼저 `.dddjango/` 폴더 목록을 조회해 승인 질문에 "산출물 폴더" 선택을 평이한 말로 더한다 — 기존 폴더 목록을 보여주고 ⓐ **기존 〈폴더〉 이어서 작업**(그 폴더 재사용) / ⓑ **새 기능**(신규 폴더) 중 고르게 한다. ⓐ면 그 폴더를 재사용한다(생성일 prefix·slug 유지·새 폴더 생성 금지). ⓑ거나 기존 폴더가 없으면 새 기능이며, 승인 뒤 slug를 영문 케밥(2~4단어)으로 확정하고 폴더 생성 직전 `date +%Y%m%d-%H%M`로 prefix를 얻어 `.dddjango/<prefix>-<slug>/`를 폴더 경로로 확정한다. 확정한 **구체** 경로(예 `.dddjango/20260604-1530-order-checkout/`)를 Phase 1~2(architect 저장 경로·acceptance·coder)에 그대로 전달하고 이후 재계산하지 않는다 — slug를 다시 만들어 폴더를 새로 찾지 않는다(같은 기능이 매 실행 다른 slug로 갈려 폴더가 분열되는 것을 막는다·재현성). *왜* — 폴더 재사용을 glob 자동매칭이 아니라 사용자 선택으로 닫으면, slug 재계산 불일치·구버전 무날짜 폴더·동일 slug 다중 폴더가 모두 목록 선택으로 해소된다.
```

- [ ] **Step 4: 교체 확인**

Run: `sed -n '12,24p;62p' /Users/hyun/Desktop/dddjango/dddjango/commands/dddjango.md`
Expected: 산출물 위치 절에 `<산출물 폴더>`·`<생성일>-<기능-slug>`·gitignore 탈출구, Phase 0 step 3에 "산출물 폴더" 선택 절차가 보임.

---

### Task 2: codex 미러 동기화 (산출물 위치 + Phase 0 + spawn 경로)

**Files:**
- Modify: `codex-dddjango/skills/dddjango/SKILL.md:60-66` (산출물 위치)
- Modify: `codex-dddjango/skills/dddjango/SKILL.md:81` (Phase 0 step 3)
- Modify: `codex-dddjango/skills/dddjango/SKILL.md:87` (spawn 경로 예시)

- [ ] **Step 1: 「산출물 위치」 절(L60-66)을 Task 1 Step 2 신규 블록과 동일 바이트로 교체**

- [ ] **Step 2: Phase 0 step 3(L81)에 Task 1 Step 3 절차를 동일 바이트로 추가**

- [ ] **Step 3: L87 spawn 경로 예시 동기화**

`design-architect` spawn 지시의 `설계 명세 저장 경로(`.dddjango/<slug>/design-spec.md`)`를 `…(`.dddjango/<생성일>-<slug>/design-spec.md`, Phase 0에서 확정한 구체 경로)`로 바꾼다.

- [ ] **Step 4: codex 잔존·동기 확인**

Run: `grep -n 'design-spec.md\|scope.md\|<기능-slug>/' /Users/hyun/Desktop/dddjango/codex-dddjango/skills/dddjango/SKILL.md`
Expected: 산출물 위치(L62-63)·spawn(L87) 모두 `<생성일>-` 형태(L87은 `<생성일>-<slug>`), 구 `<기능-slug>/scope`·`<기능-slug>/design-spec` 잔존 0건. (백스톱 ⑩ 서술의 `.dddjango/*/scope.md`는 잔존 0건과 무관 — 그건 무변경 대상.)

> 미러 비대칭(의도): claude `commands/dddjango.md:68`은 "설계 명세 저장 경로"라고만 쓰고 구체 경로를 박지 않아 무변경. codex만 L87에 경로 예시를 박아 동기화한다.

---

### Task 3: 미러 diff 게이트 (동적 범위, 3개 영역)

**Files:** 없음(검증).

- [ ] **Step 1: 「산출물 위치」 절 byte-identical (동적 범위)**

Run:
```bash
cd /Users/hyun/Desktop/dddjango
awk '/^## 산출물 위치/{f=1} f{print} f&&/^`<산출물 폴더>`도 아닌데.*/{}' /dev/null  # (참고용 — 아래 실범위로)
# 실제: 각 파일에서 '## 산출물 위치'부터 다음 '## ' 직전까지 추출해 비교
diff <(awk '/^## 산출물 위치/{f=1;next} /^## /{f=0} f' dddjango/commands/dddjango.md) \
     <(awk '/^## 산출물 위치/{f=1;next} /^## /{f=0} f' codex-dddjango/skills/dddjango/SKILL.md)
```
Expected: 빈 출력.

- [ ] **Step 2: Phase 0 절 byte-identical (동적 범위)**

Run:
```bash
cd /Users/hyun/Desktop/dddjango
diff <(awk '/^## Phase 0/{f=1;next} /^## /{f=0} f' dddjango/commands/dddjango.md) \
     <(awk '/^## Phase 0/{f=1;next} /^## /{f=0} f' codex-dddjango/skills/dddjango/SKILL.md)
```
Expected: 빈 출력.

- [ ] **Step 3: 백스톱 ⑩ 서술 줄이 양쪽 미러인지(한쪽만 바뀜 방지)**

Run:
```bash
cd /Users/hyun/Desktop/dddjango
diff <(grep -o '`\.dddjango/\*/scope\.md`가 멱등성을 미요청으로 단정' dddjango/commands/dddjango.md) \
     <(grep -o '`\.dddjango/\*/scope\.md`가 멱등성을 미요청으로 단정' codex-dddjango/skills/dddjango/SKILL.md)
```
Expected: 빈 출력(둘 다 동일 문자열 1건 — 무변경 확인).

---

### Task 4: 경로 잔존 grep (claude 측)

**Files:** 없음(검증).

- [ ] **Step 1: claude에 구 패턴 잔존 0건**

Run: `grep -n '<기능-slug>/scope\|<기능-slug>/design-spec\|\.dddjango/<기능-slug>' /Users/hyun/Desktop/dddjango/dddjango/commands/dddjango.md`
Expected: 출력 없음(구 `<기능-slug>/` 경로 0건 — 산출물 위치 절·L68 모두 새 패턴 또는 추상). exit 1.

---

### Task 5: 백스톱 ⑩ 실제 실행 회귀 (claude + codex 사본, 혼재 픽스처)

**Files:** 없음(검증). 두 스크립트 무변경 확인.

- [ ] **Step 1: 두 스크립트가 byte-identical 미러인지**

Run: `diff /Users/hyun/Desktop/dddjango/dddjango/scripts/check-idempotency-scope-creep.py /Users/hyun/Desktop/dddjango/codex-dddjango/skills/dddjango/scripts/check-idempotency-scope-creep.py`
Expected: 빈 출력.

- [ ] **Step 2: 날짜 prefix 폴더에서 실제 스크립트 발화 확인 (위반 픽스처)**

Run:
```bash
cd /tmp && rm -rf dr40probe && mkdir -p dr40probe/.dddjango/20260604-1530-orders/application/orders
printf '멱등성: 사용자가 요청하지 않음 — 범위 아님\n' > dr40probe/.dddjango/20260604-1530-orders/scope.md
cat > dr40probe/.dddjango/20260604-1530-orders/application/orders/idem.py <<'PY'
class IdempotencyRecord:  # 미요청 멱등성 발명
    pass
def process(idempotency_key): ...
PY
python3 /Users/hyun/Desktop/dddjango/dddjango/scripts/check-idempotency-scope-creep.py /tmp/dr40probe; echo "exit=$?"
```
Expected: exit=2 (날짜 prefix 폴더의 scope.md를 정상 인식해 blocker 발화 — 회귀 없음). exit 형태·메시지는 스크립트 구현에 따름; **핵심은 날짜 폴더에서 0이 아닌 2가 나오는 것**. (실제 위반 조건이 스크립트와 안 맞아 exit 0이면, 스크립트의 실제 탐지 조건에 맞춰 픽스처를 조정 — 목적은 "날짜 폴더의 scope.md/코드를 못 읽는 회귀가 없음"을 실제 실행으로 확인.)

- [ ] **Step 3: 구·신 폴더 혼재에서도 동작**

Run:
```bash
cd /tmp && mkdir -p dr40probe/.dddjango/orders   # 구버전 무날짜 폴더
printf '멱등성: 채택함\n' > dr40probe/.dddjango/orders/scope.md
python3 /Users/hyun/Desktop/dddjango/dddjango/scripts/check-idempotency-scope-creep.py /tmp/dr40probe; echo "exit=$?"
```
Expected: 스크립트가 두 폴더의 scope.md를 모두 순회하므로 충돌 없이 실행됨(크래시 없음). exit code는 OR 동작 결과(구 폴더 "채택"이 신 폴더 "미요청"을 가리지 않음 — 어느 하나라도 위반이면 2). **핵심: 혼재해도 스크립트가 크래시·미인식 없이 돈다.**

- [ ] **Step 4: codex 사본도 동일 픽스처로 1회 실행**

Run: `python3 /Users/hyun/Desktop/dddjango/codex-dddjango/skills/dddjango/scripts/check-idempotency-scope-creep.py /tmp/dr40probe; echo "exit=$?"`
Expected: claude 사본과 동일 exit(byte-identical이므로).

- [ ] **Step 5: 정리**

Run: `rm -rf /tmp/dr40probe`

---

### Task 6: plugin.json 1.1.0 + marketplace 확인 + plugin validate

**Files:**
- Modify: `dddjango/.claude-plugin/plugin.json` (version)
- Modify: `codex-dddjango/.codex-plugin/plugin.json` (version)

- [ ] **Step 1: marketplace에 version 핀 없음 확인(bump 불필요 단정)**

Run: `grep -rn '"version"\|1\.0\.9' /Users/hyun/Desktop/dddjango/.claude-plugin/marketplace.json /Users/hyun/Desktop/dddjango/.agents/plugins/marketplace.json 2>/dev/null`
Expected: 출력 없음(두 marketplace에 version 필드 없음 → plugin.json만 bump하면 됨).

- [ ] **Step 2: 두 plugin.json version `1.0.9` → `1.1.0`**

`"version": "1.0.9"` → `"version": "1.1.0"` (양 파일).

- [ ] **Step 3: 확인**

Run: `grep -h '"version"' /Users/hyun/Desktop/dddjango/dddjango/.claude-plugin/plugin.json /Users/hyun/Desktop/dddjango/codex-dddjango/.codex-plugin/plugin.json`
Expected: 두 줄 다 `"version": "1.1.0"`.

- [ ] **Step 4: claude plugin validate**

Run: `cd /Users/hyun/Desktop/dddjango && claude plugin validate dddjango 2>&1 | tail -5`
Expected: valid/PASS. (실패 시 출력 보고하고 멈춤.)

---

### Task 7: DEVLOG DR-40 + 메모리

**Files:**
- Modify: `workspace/DEVLOG.md` (DR-39 엔트리 다음에 DR-40)
- Create: `~/.claude/projects/-Users-hyun-Desktop-dddjango/memory/dddjango-output-folder-convention.md`
- Modify: `~/.claude/projects/-Users-hyun-Desktop-dddjango/memory/MEMORY.md` (인덱스 한 줄)

- [ ] **Step 1: DEVLOG에 DR-40 추가** (DR-39 엔트리 끝 다음)
```markdown
### DR-40 ✅ 산출물 폴더 규약 — `.dddjango/<생성일>-<slug>/`·재빌드 사용자선택·커밋 명문화 (1.1.0·미커밋)

발단: 사용자 "플러그인이 만든 문서를 어떤 폴더·네이밍으로 관리할지" 브레인스토밍. 조사(spec-kit `.specify/`·Kiro `.kiro/specs/`·OpenSpec — 설계문서 *커밋* 주류, gitignore는 override·local 전용)로 사용자 첫 직감(gitignore 자동등록)을 *커밋 추적*으로 반전.

결정: ① `.dddjango/` 유지(커밋 대상·민감 레포 ignore 탈출구) ② `scope.md`/`design-spec.md` 유지 ③ 폴더 `<YYYYMMDD-HHMM>-<slug>`·날짜=생성일 고정(신규만 `date` 1회·로컬) ④ 한 기능 한 폴더·최종본만(architect in-place L43/49라 이미 동작·단 폴더 재사용이 성립할 때만). 면책 boilerplate 미도입. 버전 minor 1.1.0.

적대 4렌즈 반영: **B1 slug 비결정**(재빌드 시 코디가 slug 재계산→glob 키 비결정→폴더 분열; skill-creator·devil 수렴) = **Phase 0에서 기존 폴더 목록을 사용자에게 제시·선택**(glob 자동매칭 폐기)으로 닫음 — B1·구버전 마이그레이션·다중매치 동시 해소. **M4 date 결정성 = 검증 후 기각**(eval은 fixture 디렉토리+소스경로로 채점·`.dddjango` 폴더명 짝짓기 안 함 `EVAL-METHOD.md:191` → date 로컬 무해). 보강: 백스톱 ⑩ **실제 스크립트 실행** 검증(glob.glob 재구현 폐기)+codex 사본+혼재 픽스처·marketplace version 핀 부재 확인·design-architect 무변경 근거 교정(경로 주입, *면책 boilerplate 아님*)·미러 게이트 동적범위+⑩ 서술 줄 포함.

변경: claude `commands/dddjango.md`(산출물 위치 절+Phase 0 G0 배너)+codex `SKILL.md` 미러+L87 spawn 경로+plugin.json×2. **백스톱 ⑩ 무변경**(`.dddjango/*/scope.md` glob `*`가 날짜 폴더 매치·명세 본문 서술도 임의폴더 매치 의도라 정확)·**design-architect 무변경**(경로 주입).

🔴 라이브 미검증(코디가 신규 date 폴더 생성·재빌드 시 폴더 목록 제시·사용자 선택·재사용하는지 dual `/dddjango` — 릴리스 게이트)·N=1. 정본=`workspace/design/2026-06-04-dddjango-output-folder-convention{,-plan}.md` + 적대 4리포트.
```

- [ ] **Step 2: 메모리 신규 + 인덱스** (DR-39 메모리 패턴; type: project)

- [ ] **Step 3: DEVLOG 헤더 "마지막 갱신" 2026-06-04로**

---

## Self-Review (writing-plans)

- **Spec coverage**: v2 결정 표 7항목 → Task 1·2(③폴더·④재사용·커밋·gitignore탈출구·면책)·Task 6(버전). 동작 명세 Phase 0 절차 → Task 1 Step 3·Task 2 Step 2. 적대 반영(B1·M4·보강 8) → B1=Task 1·3, M4=설계 결정(date 로컬, 코드 무관), 백스톱 실행=Task 5, codex 사본=Task 5 Step 4, marketplace=Task 6 Step 1, design-architect 근거=Task 7 DEVLOG, claude grep=Task 4, 미러 동적+⑩줄=Task 3, minor=Task 6, 탈출구=Task 1 Step 2. 갭 없음.
- **Placeholder scan**: TBD/TODO 없음. 산출물 위치 절·Phase 0 절차·DEVLOG 본문 모두 실제 텍스트. Task 5 Step 2에 "스크립트 실제 조건에 맞춰 픽스처 조정" 단서는 placeholder가 아니라 실행자 재량 가드(스크립트 탐지 로직이 픽스처와 다를 수 있음 — 목적[회귀 부재 실측]은 고정).
- **Type/경로 consistency**: `<산출물 폴더>`=`.dddjango/<생성일>-<기능-slug>/`가 Task 1·2·7·DEVLOG 일관. 재빌드=사용자선택(glob 자동매칭 폐기)이 Phase 0·DEVLOG·spec 일치. 백스톱 ⑩ `*/`(전체 폴더 순회)와 재빌드 폴더선택은 서로 다른 용도로 정합.

## 구현 적대 재검증(3렌즈) 정정 반영

구현 후 적대 재검증에서 (A)계획대로·(B)미러 PASS·(C) skill-creator가 **B1 부분완화 MAJOR 2건** 발견 → 정정 완료(최종 명세 = commands/SKILL byte-id):
- **MAJOR-1**: Phase 0 폴더조회가 *조건부*("재빌드이거나 관련폴더 있으면")라 코디 신규오판 시 우회→slug 발명 재발(비결정이라 라이브 N=1로 미포착). → **무조건화**: "G0 전 항상 `ls .dddjango/`·폴더 있으면 무조건 ⓐ/ⓑ·코디 재빌드판정 제거".
- **MAJOR-2**: 수정 모드가 Phase 0 폴더 절차 미참조. → 수정 모드 step 1에 **cross-ref** 추가("Phase 0 폴더 절차 수행·기존 폴더 재사용").

## 미해결 / 라이브 검증 대상 (🔴)

- 코디가 Phase 0에서 실제로 폴더 목록을 제시·사용자 선택을 받는지(B1 완화의 라이브 발화) — dual `/dddjango` 릴리스 게이트.
