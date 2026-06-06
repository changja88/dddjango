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

## 현재 위치 = R5 첫 조각 ✅ 완료 (소스-미러 동기) — 2026-06-06
**설계·리뷰·검증·재동기 전부 끝남.** 상세 = `R5-mirror-sync-design.md`(§6 리뷰결정·§7 검증·§8 완료).

**한 일:**
1. **검사/동기 도구 `workspace/tools/corpus_mirror_sync.py`** — fail-CLOSED·`--check`/`--write`·불변식1(소스본문≡배포본문)+불변식2(배포≡codex final.md)·앵커 fail-fast. (리뷰 반영: `dddjango/scripts/` 거부→`workspace/tools/`, `check-` 접두사 제거.)
2. **검증**(사용자가 배선 전제로 요구): 현실 8 drift 정확탐지 + 합성 13/13 PASS(거짓양성0·fail-closed·멱등·P1보존). 실버그(`--check` 미구현) 적발·수정.
3. **재동기 실행**: 소스 미러 **8스킬** ← 배포 본문(api/db/ddd/houserules/tdd/django/ninja/test). 변경 8개에만 국한·P1 보존·본문 byte-exact 8/8·사후 exit0. DR-37/41/42/43/44 소스 복원.

**확정 사실(리뷰가 굳힘):**
- 동기 대상 = **references/final.md 11개**(houserules 포함 — 미러 *보유*, P1만 없음). **SKILL.md·agents·commands는 plugin-native(미러 없음·재생성 경로 없음 → R5 밖)**.
- **자동 빌드 파이프라인 부재**(빌드스크립트0·CI0·pre-commit0) → 회귀는 "자동 되돌림"이 아닌 "byte-identical 계약 잠복 위반". severity 하향.
- 불변식2(codex)는 현재 11/11 byte-identical(액션 불필요, 앞으로 가드).

## ▶ 다음 액션 (R5 잔여 + 그 다음)
- **배선 보류 중**(사용자 결정): pre-commit/CI로 `corpus_mirror_sync.py`를 자동 차단에 묶는 것 — **전제**: 검사 방법 검증(✅완료) **+ 라이브 발화 검증**(아직). 이게 충족되면 밸브 닫음.
- **R5 백로그**: attribution 영역(P1·출처 blockquote) drift는 본 도구 스코프 밖 — 별도 검사 필요 시 후속.
- **그 다음 처방 단계**: ②측정 R2(N≥5 블라인드) → ③프론티어 R1(ACL-EX 등, *백스톱 아닌* 예방레버/테스트진정성) → ④수용 R3·메타.

## 정직 경계
- 진단 전체 N=1·단일조정자(M2). **R5는 코드-diff라 결정적·M2 영향 적음**(독립증거: 합성테스트·git diff·md5).
- R5 첫 조각 외 나머지(배선 라이브검증·R2 측정·R1 프론티어)는 미착수.
