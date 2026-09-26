# 로드맵 3 — pre-gate 수리 구현 기록 (2026-09-27 새벽 · 미커밋)

설계: `step3-pregate-design-v2.md`. 검토: E(코드) · F(규범·현장) · H(계획 — `review-H-step3-plan.md`: blocker 전건 해소 · 새 major 5 · minor 9).

## 1. 구현 완료 — `dddjango/scripts/design_pregate.py` (작업 트리 · Codex byte 미러 **아직 안 함**)

| 수리 | 내용 | 시험 |
|---|---|---|
| S-4 digest | `_pregate_digest()`(scripts `*.py`·`*.json` − `rulepack.json`) · 스탬프 끝 `· 실행 트리 digest <16hex>` · check-report «stale(툴체인)»/«툴체인 증명 불가» · `요약:` 끝 `digest 현재=리포트` · `--block-hash` 둘째 행 · 스탬프 OSError → RunError | 러너 `:255` 단언 개정(첫 행 + 둘째 행 형식) · rcases 2(툴체인 stale · 토큰 없음) · digest 범위 유닛(rulepack 변경 무반응 · 검사기 변경 반응) |
| S-3 오버레이 생략 | HEAD 1회 해석(`rev-parse --verify HEAD^{commit}` · 미탄생 exit 1) · `explicit_base ∧ base≠HEAD` → 오버레이 생략 · 헤더 `- dirty overlay 생략: … N경로` · `_dirty_count` · `in_head` 는 head_sha · 골격 가드를 기준선 트리(`baseline_bcs` · 유입 적용 뒤)로 · 헤더 행 `header_notes` 인자(write_report·stub) · S7/S8·docstring 문면 | E5(F4-23 재현 — 수정 전 exit 2 #488 · 수정 후 0) · E6(기준선=HEAD + WIP 신규 BC — 수정 전 2 · 후 0) — **음성 대조 확인**(HEAD 스크립트로 둘 다 exit 2) |
| S-1 승인 유입 | `--approved-merge-file`(anchor_diff 로더) · `approved_inflow`(참여 머지 · 경로별 마지막 · verbatim 만 · 추가·수정·삭제 · gitlink 건너뜀 · 충돌 해소 제외 목록) · `apply_inflow`(cat-file --batch · 모드·symlink) · 형식 검사 «기준선 ⊕ 유입» · `승인 유입 add 충돌:`(add·empty) · 헤더 `- 승인 유입: N경로(추가·수정·삭제) · 머지 · 불참 · 충돌 해소 제외` · 목록 부재/검증 실패 exit 1(발주자 사안) · `:2647` 메시지 세 갈래 | 러너 `_run_inflow_bundle`(무플래그 3 · 플래그 0 + 추가1·수정1·삭제1·불참1·결손0 · add 충돌 3 · 비머지 목록 1 · 부재 1) · 진단 r21 재현(무플래그 3 → 플래그 0) — **음성 대조**(신규 경로만 반영하면 exit 5 결손 1) |
| S-1b 기대 기준선 | `--expect-base <7~40hex>`(`--check-report` 전용 · 단독이면 exit 1) · 불일치 «기준선 치환» · **명시 재예보 절이면 `--expect-base` 의무(누락 = «기준선 대조 누락»)** · **실행 경계 행 `- 실행 경계 —`(RUN_BOUNDARY_PREFIX) 뒤이면 앞 실행 예보: 블록 해시 같으면 digest·기준선 대조 없이 정합(«앞 실행 예보(명세 불변)»)** — 검토 H-M2·H-M3 의 기계 집행 | 러너 inflow 번들(전체 0 · 7자 0 · 치환 3 · 단독 1) · rcases 3(명시 재예보 누락 3 · 앞 실행 명세 불변 0 · 앞 실행 명세 변경 3) |
| S-3b 결손 안내 | `annotate_post_baseline_defects` — 오버레이 생략(재발화) 때 결손 대상 모듈 파일이 기준선≠HEAD 면 detail 에 처방(update + symbols 선언 · add · 타 BC G0 재승인 · 등재 머지 플래그 · 미등재 STOP) · 유입 경로 제외 · 판정·ID 무변 | 러너(`postbase-defect-spec.md` — 재발화 exit 5 + 안내 · HEAD 실행 skip 4 무안내) |
| S-2 #574 예보 | `_CONTRACT_PATH_RE`·`_IN_DATA_MODULE_RE`(계약 자료 경로 — 부분 문자열 아님 · H-m3) · `_PortTypes`(같은 능력 폴더 유일 클래스 폴백 · 잎 단위) · `check_in_argument_forecast`(선언 메서드만 · update 는 실물 동일 서명 제외 · 반환 우주 = 같은 BC(framework 포트는 framework) 실물 ∪ 선언 · `_in` 필드 닫힘 · U = 반환 주석 `ast.walk` 이름 · 확정/후보) · main 에서 `check_declarations(...) + check_in_argument_forecast(...)` | 유닛 9(현장형 양성 · 컨테이너 안 · _out · 반환 중계 · 필드 중계 · update 부분 선언 · legacy · 후보 · framework) — **음성 대조**(폴백 제거 시 양성 5건 실패) · **현장 재생(실구현)**: catalog · b5 · b7 · h1(2) · counter-room(3 메서드) **전부 확정** · decisive 무(교정판만 존재 — 정답) · **음성 sweep 78 실행: 확정 0 · 후보 0 · 오류 0** (`scratchpad/s2replay/replay.py`) |

- 새 픽스처 파일: `workspace/eval/fixtures/pregate/{inflow-spec.md, inflow-addconflict-spec.md, postbase-defect-spec.md}`.
- 러너: `workspace/tools/pregate_fixture_run.py` — E5·E6 · inflow 번들(+S-3b) · rcases 5 · digest 유닛 · `_in_argument_unit_checks`. 전체 PASS · `pregate_field_report_smoke.py` 38 OK(구현 도중 확인 · S-2 추가 뒤 재실행 필요).

## 2. 남은 일 (검토 H §5 순서)

1. **S-2 사각 문면**: BLIND_SPOTS S2 에 «선언 확정 #574 는 사각이 아니다(filtered·ⓑ 대상 아님)» · docstring «#574 예보» 근거 행(wiring 근거 — authoring §16).
2. **Codex byte 미러**: `codex-dddjango/skills/dddjango/scripts/design_pregate.py` ← cp.
3. **graph-owned 일괄**(규범 매핑표 먼저 — H-M4):
   - houserules final §3: **새 R-3500(Prohibition)** «포트 인자 `_in` 금지» · ISSUED · 새 블록 s011-3/b3 · wiring `enforcedBy c/design_pregate.py, c/check-port-adapter-pairing.py` · 소스 미러 `workspace/reference/discipline-houserules/reference/final.md` 수동 교체 → `corpus_mirror_sync --write`.
   - Coordinator(`command-dddjango.ttl`): ② `--approved-merge-file` 동반 · 발주 `--base` 불수용 · `pre-gate 기준선` 실행 줄 기록(값 = 이번 실행 마지막 예보 절 기준선 · 없으면 첫 파견 직전 `rev-parse HEAD` · override 재실행 뒤 기록) · 명시 재예보 check-report 에 `--expect-base` · 새 실행 G0 승인 때 `pregate-report.md` 에 `- 실행 경계 — <실행 줄 G0 승인 · UTC>` append · 오버레이 문면 정정 · 캐시 skip 에 digest · 선언 확정 #574 filtered 금지 · 재진술 6곳 «② 참조» · H-M5 표 ①~⑦(실행 줄 기계 기록 열거 218·85·122·18행 · 58행 배너 사유 · 102행 S2 · 177·193행 한정) — R-3445 amendment vs 신설은 매핑표에서 결정.
   - architect(`agent-design-architect.ttl`): 90행 «기준선 ⊕ 승인 유입» · 87행 선언 확정에 #574 · symbols 절 포인터 · «격리 사본» 문면.
   - render(3 doc) → LEDGER → target-counts → q4 → `make rulepack` → Codex 의미 미러(Coordinator · architect) .
4. **산문**: REQUEST_GUIDE §4 «`--base`·기준선 이동 지정 금지» 1행(Claude·Codex byte · `request_guide_contract.py --self-test` · `reverse_coverage.py`) · `docs/DEVELOPMENT.md` §6 «릴리즈 전 G1~G2 진행 레인 0 확인(digest 가 진행 중 예보를 stale 로 만든다)».
5. **정정**: `diag-B3-pregate-field-frequency.md` ⑤ decisive 근거 `:408` 은 G1 절이 아니라 S5 재발화 절.
6. 구현 리뷰(독립) → 조감도 행 → `make verify` · `make verify-mutation` → 커밋 → 봉인 chore.

## 3. 사용자 결정 대기

- ~~결정 7~~ → **확정 (가) 규칙대로(09-27 00:52)** — evening-report §5 결정 7. graph 일괄(§2-3)에 반환 절반 문면(houserules §3 · 집행 `delegatedTo agent-discipline-reviewer`)과 #236 «내보내는 자료» 정정을 더한다.
- ~~로드맵 4 규모~~ → **결정 8 확정 (마) 최소한(09-27 00:59)** — evening-report §5 결정 8. 아래는 당시 기록:
- **로드맵 4(동작 보존 장치) 규모**: 재검토 G2(`review-G2-step4-v2.md`) — 앞 발견 해소 8·부분 11·미해소 1 · 새 major 10 · 추정 6~8일. **축소안을 사용자에게 올릴 것**(검토자 제안: 머지 끊기 → 탐지 · env 정적 수집 → 비운 env · 입장 표 파서 → file-plan 짝 · admin alternation 정렬 제외).

## 4. 검토 I 처분 (2026-09-27 · `review-I-step3-impl.md` — blocker 0 · major 1 · minor 9)

| # | 처분 |
|---|---|
| I-M1 | 수용 — 리포트 `- pre-gate 기준선 —` 행(첫 파견 직전 1회 · 마지막 실행 경계 뒤 · 중복 = 불비)을 기대 기준선으로 대조 · 명시 재예보 의무를 «이번 실행 절 가운데 하나라도»로 넓힘 · 러너 8사례(명시→HEAD 판형 치환 · 행 없음 누락 · 일치 · Phase 1 일치/불일치 · 중복 · 형식 불비 · 경계 앞 행 무시) · 규범은 실행 줄 대신 리포트 행 |
| I-m1 | 수용(투명화) — 앞 실행 정합 요약에 «툴체인·기준선 대조 생략»(+ `--expect-base` 를 줬으면 «미대조») · 규범: 앞 실행 예보는 G1/G1′ 배너 근거 아님 |
| I-m2 | 수용 — typing 컨테이너 머리 투명화(import 없이 · Annotated 첫 원소) · 인자 `…In` 이름 `ast.walk` 수집 · 해소된 반환 이름은 «아마»에서 뺌 · 러너 5사례 |
| I-m3 | 수용 — 서명 전체 비교 대신 (인자 이름, 문자열 주석 펼친 정규형) 단위로 실물 legacy 인자 제외 · 새 `_in` 인자만 예보 · 러너 3사례 · 규범: 실물의 기존 `_in` 인자는 의미 빚 |
| I-m4 | 수용 — 선언 확정 `[#574]` ID 의 filtered 불인정(«#574 는 filtered 불인정») · 러너 3사례 |
| I-m5 | 수용 — `apply_inflow` OSError → RunError · 삭제 뒤 빈 조상 rmdir · 조상 symlink 거절 · 남은 디렉터리 쓰기 거절 · `main` 전체를 RunError/OSError → exit 1 로 감쌈 |
| I-m6 | 수용 — 충돌 해소 제외 경로는 «레인의 변경 — file-plan 또는 G2 귀속» 안내 |
| I-m7 | 수용 — 헤더 «승인 유입» 행에 역방향/합성 머지 의심 병기(exit 무변) |
| I-m8 | 수용(규범) — 캐시 skip 은 마지막 예보 절이 마지막 실행 경계 뒤일 때만 |
| I-m9 | ⓐ 수용(«이름 붙인 자료를 돌려주면» · 원시 값·None 밖) · ⓑ 수용(기존 `_out` 자료 재사용 허용 · 새 자료만 `_in` — 결정 7 해석, 사용자에게 알림) · ⓒ 기록(BC 포트 반환 우주에 framework 불포함 — R-3500 문면과 같다) · ⓓ 수용(docstring) · ⓔ 수용(DEVELOPMENT «착륙까지 보류») · ⓕ 수용(문면을 wiring 에 맞춤 — discipline-reviewer) |
