# 진단 — 조작 상태 증거 의무의 집행이 경로 의존적이다 (2026-09-15)

## 증상 (A8 실환경 · v1.1.13 설치 확인)

- 09-15 13:22 A8 워크트리(`~/.herdr/worktrees/spring_dream_server/a8`) 세션에서 사용자가 «재동결»을 요청. 설치본은 v1.1.13(캐시 `dddjango-web/1.1.13` 09-15 01:06).
- 결과: `refreeze-diff.json` 22행(same 16 · changed 0 · carried 6) 생성, `build-state.json`에 `refreeze: {diff, sha256}` 기록 → «변화 0 · 진행할 구현 없음»으로 종료. **재동결 대조(09-13 문제 ②)는 정상 작동**했다 — 과거 `refreeze_v3~v5` 기록은 사람이 적은 산문(«18 재수집 · 1 DIFF …»)이었고 오늘은 기계 대조 문서와 그 해시다.
- 그러나 같은 빌드 폴더 `20260912-1640-web-related-persons`에는 **조작 상태 증거가 0**이다 — `captures/*-interactions.json` 없음, `design-input.json` case 12개 전부 정적(`reached_by`·`interactions` 없음). 09-13 문제 ①이 그대로인데 세션은 아무 고지도 하지 않았다.

## 검사기는 정상이다 (사본 실측)

A8 빌드 폴더를 scratch 프로젝트로 복제해 새 검사기를 직접 걸었다.

```
check_design_evidence.py --build <copy> --project-root <copy-root> --phase inputs   → exit 2
                                                                    --phase prepare  → exit 2
                                                                    --phase visual   → exit 2
defect 13 = cases[0..11].source_observation: interaction evidence required (version 2 with interactions) ×12
          + coverage_review: reviewed-input does not match current source/cases/observations ×1
```

즉 «못 잡는» 것이 아니라 «불리지 않은» 것이다.

## 원인 — 집행 지점 전수가 «구현으로 가는 길» 위에 있다

`dddjango-web/commands/dddjango-web.md`(Codex `SKILL.md` 동형)에서 증거 검사가 호출되는 지점 전수:

| # | 지점 | 호출 | 어떤 경로에서만 도달하나 |
|---|---|---|---|
| 1 | Phase 0 조작 상태 수집 step(:142) | 수집 후 `--phase inputs` exit 소비 | 신규 수집을 실제로 수행할 때 |
| 2 | Phase 0 ready 직전 입력 게이트(:144-145) | `check_design_evidence --phase prepare/inputs` | 신규 빌드 또는 «이어서 작업»으로 Phase 1에 진입할 때 |
| 3 | Phase 2 매 coder 호출 직전(:177) | `--phase inputs` | 구현 슬라이스를 시작할 때 |
| 4 | G2 배너 직전(:184) | `backstop.py --design-build`(내부 `validate_inputs`·`validate_visual`) | 구현 슬라이스가 끝났을 때 |
| 5 | 마무리 보고 직전(:189) | 같은 backstop | 구현 완료 시 |
| 6 | 수정 모드 G0 freshness(:204) | Phase 0 입력범위/inputs 절차 | 사용자가 화면 수정을 발주했을 때 |
| 7 | 수정 모드 G2 직전(:208) | 같은 backstop | 수정 구현 후 |
| 8 | 트리비얼 패스트트랙 편집 전·후(:211-218) | `--phase inputs` · backstop | 트리비얼 수정을 발주했을 때 |

(1차 적대 검토가 5행 표를 8행으로 정정 — `design-review.md` Q0.) 여덟 지점 모두 구현을 향해 갈 때만 지난다. 재동결만 하고 끝나는 경로(오늘), 스코프 조회·상태 확인만 하는 경로, «변화 0 → 진행 없음»으로 닫히는 경로에는 호출이 하나도 없다. 경로 선택은 LLM Coordinator가 사용자 발화를 해석해 정하므로, 각 경로 안에서는 결정적이지만 전체 집행은 경로 의존적 — 사용자 표현대로 «확률적»이다.

## 왜 09-14 검증이 이걸 못 봤나

- Task 11(native 평가)의 발화는 «기존 화면 관계인 재개 → 증거 검증 → 구현»이었다. 즉 검증자가 관문이 놓인 길을 골라 걷고 «관문이 작동한다»고 결론냈다.
- 조기 종료 경로(재동결만·조회만)는 한 번도 발화하지 않았고, «어떤 경로가 관문을 우회하는가»를 질문한 적이 없다.
- 재동결 3회 시험은 staging을 `design-ref` 복사로 만들어 DesignSync 실재수집을 거치지 않았다. 실재수집에서는 `readme.md`·`_adherence.oxlintrc.json`이 추가로 `carried`(재수집 실패)가 된다(4→6) — 시험이 보지 못한 실제 동작.

## 부수 발견 (별건으로 이관 · 여기서는 기록만)

같은 날 A8 관계인 편집기에서 이름 입력 포커스 링 좌우 절단을 실측했다(`workspace/eval/web-scroll-clip-fidelity/` 예정). 원인은 ⓐ 시안 스크롤 컨테이너의 인라인 `padding: 2px 2px 4px`를 명세가 흘림(전수 연결이 토큰만 대상) ⓑ 포커스 상태가 case 의무 밖(value-only step)이라 구현 대조에 등장하지 않음. 수리 2·3으로 분리한다.

## 이 진단이 요구하는 수리의 형태

호출 지점을 하나 더 얹는 것은 같은 실수의 반복이다(경로 열거). 필요한 것은 **LLM이 어떤 경로를 고르든 먼저 도는 층** — 하네스 hook. 설계는 `workspace/design/2026-09-15-web-evidence-debt-hook.md`.
