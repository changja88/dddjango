# 처방(remediation) 진행 상황 — 재개용 (2026-06-06)

> 컴팩트/세션 재개 시 **이 파일 + `DIAGNOSIS.md`(v2)부터 읽어라.** 진단은 끝났고 처방 *기반 단계* 진행 중.

## 큰 그림
**진단(완료) → 처방(진행중).** 질문이었던 "왜 수정이 회귀하나"는 `DIAGNOSIS.md` v2로 답함(근본 5·증폭기 2·메타제약 3). 지금은 그 진단대로 *고치는* 단계.

## 산출물 (전부 커밋됨 · `workspace/eval/rootcause/`)
- `episodes.md`(Phase0) · `lens-L1~6.md`(Phase1) · `synthesis.md`(Phase2) · `adversarial.md`(Phase3) · `DIAGNOSIS.md` **v2**(Phase4 deliverable) · `review-plugin-lens.md`(plugin-전문 검증)
- 계획: `workspace/design/2026-06-06-fix-regression-rootcause-analysis-{plan,execution-plan}.md`
- 커밋 트레일: `b70dff5`→`ce48491`→`c68f4b8`→`98919d3`→`50e804c`→`cbd742d`→`d39fae8`→`8af110c`→`53b4cae`→`9eb8fea`

## 처방 전략 (사용자 확정)
**"기반 먼저"**: ① 기반(R5 빌드배선+A1/M2 규율) → ② 측정(R2 N≥5) → ③ 프론티어(R1 열린발견·*백스톱 아닌* 예방레버/테스트진정성) → ④ 수용/우회(R3·메타제약).
*근거*: R5(소스-미러 drift)가 *회귀 메커니즘 그 자체* — 안 닫으면 텍스트 수정이 다음 빌드에 되돌려짐("새는 바구니"). 결정적·LLM무관이라 가장 싸고 확실.

## 현재 위치 = R5 첫 조각 (소스-미러 동기)
**완료한 스코핑(내용 확인):** `workspace/reference/<skill>/reference/final.md`(재생성 출처)가 배포본 `dddjango/skills/<skill>/references/final.md` 대비 **stale**.
- **내용 직접 확인**: architecture-ddd(DR-37 BC-FK 문단 누락)·discipline-houserules(DR-41/43 옛 명명).
- **키워드 강확신**: implementation-test(~200줄 DR-42)·ninja(DR-35/41)·db·django(DR-37)·tdd(DR-42).
- **방향 확정**: 소스 stale / 배포본 current. cleancode·django-web·python은 인트로 blockquote 구조차이(DR drift 아닐 가능성).
- ⚠️ **측정 주의**: hand-rolled awk(P1 블록 처리)가 두 번 깨짐(과대/과소) — 정확한 per-skill 줄수는 *결정적 스크립트*로 내야 함(아래 처방이 그것).

## ▶ 다음 액션 (사용자 go 대기였음)
**R5 처방 = "결정적 백스톱 + 생산자 예방"을 R5에 적용**(R5는 백스톱이 *구조적으로 가능*한 영역):
1. `dddjango/scripts/check-corpus-mirror-sync.py` **설계**(P1 Source Sufficiency 블록만 정확 제외하고 소스↔배포 본문 byte 비교; codex 미러도) — 이게 *권위 있는 drift 목록*을 한 번에 주고 동시에 **영구 가드(게이트 14종)**.
2. 그 목록대로 **소스 미러 ← 배포본 본문 재동기**(소스 P1 블록 보존).
3. 검증: 동기 후 exit0.
- ⚠️ **작업 방식**: 2부 코퍼스 + 게이트 신설 = 섬세 변경 → **구현 전 skill-creator·plugin-creator 서브에이전트 리뷰** 필수.

## 정직 경계
- 진단 전체 N=1·단일조정자(M2). 처방은 독립증거(R5는 코드-diff라 결정적·M2 영향 적음).
- R5 외 나머지(R2 측정·R1 프론티어)는 아직 미착수.
