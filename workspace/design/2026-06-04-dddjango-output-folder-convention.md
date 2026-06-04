# dddjango 산출물 관리 규약 — 폴더 위치·네이밍·생명주기 (DR-40 설계 v2)

> 상태: 설계 승인(브레인스토밍) + 적대 리뷰 4렌즈 반영. 구현 전. 정본 결정 원장은 `workspace/DEVLOG.md` DR-40.
> v2 변경: 사용자 (가) 채택(날짜 prefix 유지) + 적대 리뷰 반영(B1 slug 비결정 완화·M4 검증으로 기각·계획 보강 8건).

## 배경 — 왜 이 변경을 하나

`/dddjango`가 사용자 프로젝트에 남기는 산출물(`.dddjango/<기능-slug>/scope.md`·`design-spec.md`)의 폴더 규약에 두 빈틈이 있다: ① 슬러그만 있어 타임라인·재빌드 식별이 안 되고, ② 커밋/ignore 의도가 명시 안 됐다(spec-driven 주류는 설계문서 *커밋*). 이 둘을 메우되 dddjango의 기존 철학을 존중하는 최소 변경으로 한다.

## 이미 성립하는 것 (재확인 — 추가 작업 아님)

- **design-spec = 그 빌드의 최종 설계 스냅샷**: architect가 리뷰 반영·반송 갱신을 전부 제자리 수정(in-place)으로 하므로(`agents/design-architect.md:43·49`) 중간 버전은 안 쌓이고 폴더엔 최종 design-spec 하나만 남는다. **단 이는 코디가 폴더를 정확히 재사용할 때만 성립한다** — 폴더 재사용 자체는 새로 코디에 요구되는 동작이며 라이브 검증 대상이다(적대 리뷰 m3 반영).
- **확정 시점**: G1 리뷰 반영→G1 승인(1차) → G2 반송 시 재갱신 → G2 통과(최종).
- **drift**: 빌드 직후엔 코드≈명세(reviewer·백스톱이 코드를 명세에 맞춤). 진짜 drift는 빌드 후 수동 수정 — living-doc 동기화는 범위 밖(아래).

## 결정 (확정 — (가) 날짜 prefix 유지)

| 항목 | 결정 |
|------|------|
| ① 위치 | `.dddjango/` 루트 dot-디렉터리 유지 (커밋 대상) |
| ② 파일명 | `scope.md` / `design-spec.md` 유지 |
| ③ 폴더 슬러그 | `<YYYYMMDD-HHMM>-<slug>` — 날짜=**생성일 고정**(신규일 때만 `date` 1회·로컬 시각)·slug=영문 kebab(2~4단어) |
| ④ 생명주기 | **한 기능 = 한 폴더, 최종본만**. 재빌드는 **기존 폴더를 사용자 확인으로 선택·재사용**(B1 완화 — 아래 동작 명세) |
| 커밋 정책 | 기본 커밋(`.gitignore` 안 함)·"설계 결정 기록". **단 민감 레포면 `.gitignore`에 `.dddjango/` 추가 가능**(탈출구·적대 m5 반영) |
| 면책 boilerplate | design-spec 본문에 안 넣음 (날짜 폴더가 시점 표시·boilerplate 가독성 역행) |
| 버전 | plugin.json `1.0.9` → **`1.1.0`**(minor — 사용자 가시 경로 규약 변경·적대 M5 반영) |

```
<project>/
└─ .dddjango/
   ├─ 20260601-0930-product-catalog/
   ├─ 20260603-1410-stock-reservation/
   │  ├─ scope.md
   │  └─ design-spec.md
   └─ 20260604-1530-order-checkout/
```

## 적대 리뷰(4렌즈) 반영 요약

- **B1 (slug 비결정·BLOCKER, skill-creator·devil 수렴)**: 재빌드 시 코디가 slug를 자유 텍스트에서 재계산하면 glob 매칭 키가 비결정 → 폴더 분열. **완화: glob 자동매칭에 의존하지 않고, Phase 0에서 기존 `.dddjango/` 폴더 목록을 사용자에게 보여 고르게 한다**(동작 명세). 이 하나가 B1·M2(마이그레이션)·M3(다중매치)를 동시에 닫는다.
- **M4 (date 결정성·devil) → 검증 후 기각**: 채점은 fixture를 별도 디렉터리(`~/Desktop/dddjango-<round>-<runtime>`)로 구분하고 그 안의 실제 소스 파일 경로로 읽으며(`EVAL-METHOD.md:191`), `.dddjango/` 폴더명으로 두 arm을 짝짓지 않는다 → date prefix가 달라도 eval 비교 무영향. date는 **로컬 시각 유지**(사용자 직관)·TZ 고정 불필요.
- **계획 보강 8건**(변경 범위·검증 절에 반영): 백스톱 실제실행 검증·codex 스크립트 사본·marketplace 확인·design-architect 근거 교정·claude commands:15 grep·minor bump·gitignore 탈출구·미러 게이트 동적범위+백스톱⑩ 명세 줄.

## 동작 명세 (코디네이터)

**폴더 결정은 Phase 0에서 명령형 절차로 한다**(B1 완화 — slug를 발명해 glob하지 않는다):

1. **G0 배너를 내기 전에 항상** `ls .dddjango/`로 기존 폴더 목록을 조회한다(없으면 빈 결과 — 코디가 '재빌드인지'를 스스로 판정하지 않는다). *왜 무조건인가* — 조건부("재빌드면 조회")로 두면 코디가 신규로 오판할 때 조회를 건너뛰고 slug를 발명해 B1이 재발한다(구현 적대 재검증 MAJOR-1).
2. 폴더가 **하나라도 있으면 무조건** → **G0 배너에 목록을 제시하고 "기존 〈폴더〉 이어서 작업 vs 새 기능"을 사용자가 고르게** 한다. 기존 폴더를 고르면 재사용한다(**생성일 prefix·slug 유지·새 폴더 생성 금지**). 폴더가 0개이거나 사용자가 "새 기능"을 고르면 → slug를 영문 kebab(2~4단어)으로 확정하고, **폴더 생성 직전 `date +%Y%m%d-%H%M`(로컬)로 prefix를 얻어** `.dddjango/<prefix>-<slug>/`를 확정한다(LLM 시각 추측 금지 = 결정성). **수정 모드(부분 수정)로 진입해도 이 절차를 거쳐 기존 폴더를 재사용한다**(수정 모드 step 1 cross-ref·구현 적대 재검증 MAJOR-2).
3. 확정한 **구체** 폴더 경로(예 `.dddjango/20260604-1530-order-checkout/`)를 이후 모든 Phase(architect 저장 경로·acceptance·coder)에 그대로 전달한다 — 재계산하지 않는다. design-architect는 이 경로를 입력으로 받기만 하고 폴더 규약을 스스로 만들지 않는다(`design-architect.md:21·27`).

> 이 절차가 구버전 무날짜 `.dddjango/<slug>/` 폴더(마이그레이션)와 동일-slug 다중 폴더도 함께 해소한다 — 둘 다 목록에 나타나 사용자가 직접 고르므로, glob 패턴 매칭의 0개/복수/접두 충돌 문제가 발생하지 않는다.

## 변경 범위

**고치는 곳:**
1. `dddjango/commands/dddjango.md` — 「산출물 위치」 절(L12-18) 경로 패턴·커밋 안내 + **Phase 0(L53-62)에 폴더 결정 절차 step 추가**.
2. `codex-dddjango/skills/dddjango/SKILL.md` — 위 두 곳의 byte-identical 미러(「산출물 위치」 L60-66 + Phase 0 + L87 spawn 경로 예시 `<생성일>-<slug>`).
3. `dddjango/.claude-plugin/plugin.json` + `codex-dddjango/.codex-plugin/plugin.json` — `1.0.9` → `1.1.0`.
4. `workspace/DEVLOG.md` — DR-40 엔트리(백스톱 ⑩ 무변경 근거 = glob `*`가 날짜 폴더 매치 + 명세 본문 `.dddjango/*/scope.md` 줄은 임의 폴더 매치 의도라 정확함, 명시).
5. 개인 메모리 — 신규 슬러그 + `MEMORY.md` 인덱스.

**안 고치는 곳 (의도적·근거):**
- 백스톱 ⑩ 스크립트(claude·**codex 두 사본** — byte-identical 미러) — `.dddjango/*/scope.md` glob의 `*`가 날짜 prefix 폴더를 매치(실제 스크립트 실행으로 실측). 변경 불필요.
- 코디 명세 본문의 백스톱 ⑩ 서술(claude:81·codex:100) `.dddjango/*/scope.md` — 임의 폴더 매치를 의도한 glob이라 `<생성일>-`을 박으면 오히려 오도. **무변경·근거 DEVLOG 명시**. 단 미러 diff 게이트 범위에는 포함(한쪽만 바뀜 방지).
- `design-architect.md` — 저장 경로를 코디 주입 입력으로만 받고 폴더 규약을 만들지 않으므로 무변경(근거 교정: "면책 boilerplate 미도입"이 아니라 "경로 주입").
- 나머지 11개 백스톱·다른 에이전트(`.dddjango`/파일명 미참조, grep 확인).

## 검증 계획

- **미러 diff**: 「산출물 위치」 절 + Phase 0 폴더 결정 절차 + 백스톱 ⑩ 서술 줄(81/100)이 claude↔codex byte-identical. 라인 범위 하드코딩 말고 `## 헤더`~다음 `## ` 동적 추출로 비교(적대 m7 반영). codex L87 spawn 경로는 의도된 미러 비대칭이라 제외 명시.
- **경로 잔존 grep**: claude `commands/dddjango.md`·codex `SKILL.md` 양쪽에서 구 `<기능-slug>/scope`·`<기능-slug>/design-spec` 잔존 0건 단정(claude L15·codex L62-63·L87 모두).
- **백스톱 ⑩ 실제 실행 회귀**: `glob.glob` 재구현이 아니라 **실제 스크립트**(`python3 .../check-idempotency-scope-creep.py <fixture-root>`)를 — (a) 멱등성-미요청+구현 위반 픽스처(날짜 폴더), (b) 구·신 폴더 혼재 픽스처 — 로 돌려 exit code(2=blocker)가 구 폴더와 동일하게 나오는지 확인(적대 plugin-B1 반영). claude·**codex 두 사본** 모두.
- **marketplace.json ×2** version 핀 없음 확인 → bump 불필요 단정(적대 M2 반영).
- **`plugin validate`**(claude) 통과.
- **라이브(릴리스 게이트로 승격·🔴 N=1)**: dual `/dddjango`에서 코디가 (a) 신규 시 `date` prefix 폴더 생성, (b) 재빌드 시 기존 폴더 목록 제시·사용자 선택·재사용을 실제로 하는지 관측. 정적 통과 ≠ 라이브 동작(DR-21).

## 범위 밖 (명시)

- **design-spec living-doc 동기화**(빌드 후 코드 진화 자동 추적) — 큰 변경·단발 철학·"이력 금지"(`design-architect.md:43`) 위반.
- **archive / INDEX.md / 상태 필드** — YAGNI·갱신 주체 부재·"현재 상태" 철학과 충돌.
- **커밋·push** — 사용자 명시 승인 시에만.

## 정본 포인터

- 결정 원장: `workspace/DEVLOG.md` DR-40
- 이 설계: 본 문서 / 구현 계획: `…-convention-plan.md`
- 적대 리뷰: 4렌즈 리포트(skill-creator·plugin-creator·자기정합·devil's advocate)
- 영향 파일: `commands/dddjango.md`·`codex .../SKILL.md`(미러)·`plugin.json`×2
