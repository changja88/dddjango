`dddjango-web  [▶ 스코프] → [· 설계] → [· 구현] → [· 마무리]`

```
─────────────────────────────────────
dddjango-web · G0 스코프 승인 (2026-09-14 재확인 회차 · 사전 승인 소비 · 입력 준비 결과 보고)
방금 끝낸 것 : 기존 폴더 ⓐ 재사용 · 배선 6종 검사(전부 충족·변경 0) · 기존 채널 현행 검증 · 
              조작 상태 수집기 신규 실측(관계인 11회차 88분 · 설정 2회차) · v2 관찰 12 case 재구성 · 
              독립 입력범위 검토 실호출·원문 보존 · prepare/inputs 실행
승인 대기   : design_status = blocked — 사용자 결정 D-A~D-E(+motion-notes 헤더) 없이는 inputs exit 0 불가
다음에 할 것 : 사용자 결정 → scope.md 승인 원문 기재 → design-input 재조립 → prepare → 독립 재검토 → inputs
─────────────────────────────────────
```

## 실행 결과(명령 · exit · 산출)

폴더 `.dddjango-web/20260912-1640-web-related-persons/` 밖 쓰기 0(`git status`로 확인 · HEAD `60943b3` 불변 · 서버·브라우저 잔존 0).

| # | 명령 | exit | 결과/산출 |
|---|---|---|---|
| 1 | `check_design_evidence.py --phase prepare`(회차 시작 상태) | **2** | 12 case 전부 «interaction evidence required (version 2 with interactions)» — 현행 plugin에서 기존 관찰 채널 미충족 |
| 2 | `compare_render_audit.py --validate --require-version 2 render-audit.json` | 0 | 재사용(warn: cross-origin 시트 4) |
| 3 | `check_motion_spec.py --spec-only … --audit render-audit.json` | 0 | **[warn] 레거시 판형** — 헤더 `재현 분류` ≠ 현행 앵커 `재현 분류(예상)` → 모션 축 미검증(재사용 승인대로 미수정 · 결정 항목) |
| 4 | `python3 -m http.server 8733 --bind 127.0.0.1`(design-ref) | — | 서빙 sha = 동결 sha 확인 · 종료·포트 반납 |
| 5 | `observe_interactions.mjs` 관계인(`--root '[data-screen-label="관계인"]' --viewport 560x1040 --crop-root --max-minutes 8` + `--resume` ×10) | 3 ×11 | `captures/related-interactions.json`(steps 1602 · targets 223 · 잔여 0 · partial · 예산 90분 소진) + 루트 크롭 캡처 |
| 6 | 동일 · 설정(`[data-screen-label="설정"]`) ×2 | 3 ×2 | `captures/settings-interactions.json`(steps 484 · 잔여 0). **두 회차 모두 상한 도달 뒤 마무리 단계에서 정지(0% CPU)** → SIGTERM으로 브라우저 닫히며 문서 정상 기록 |
| 7 | staging 조립 스크립트(수집기 문서 → case별 `-trace.json`·`-source-observation.json` v2 · `design-input.json`) | 0 | 14 case(v2 12 + v1 잔존 2) · 예외 6행 |
| 8 | `check_design_evidence.py --phase prepare`(최종) | **2** | defect 18 = 새 표면 미연결 16 + v1 잔존 2 · digest 미산출 |
| 9 | `dddjango-web:design-review-web` 입력범위 모드(독립·읽기 전용) | — | 반환 원문 → **`coverage-review.md`**(직전 검토는 `_history/coverage-review/2026-09-13-v5-reviewed-input-25b5b078.md`) · **review-result: fail** · reviewed-input: none |
| 10 | `check_design_evidence.py --phase inputs`(최종) | **2** | defect 20(18 + coverage_review 2) → **`design_status = blocked`** |
| 진단 | 가상 승인 적용 staging 사본에 prepare | 0 | digest `24b2baa6…` — 증거 사슬 자체는 온전 · 남은 건 사용자 결정뿐(사본 삭제 · 실제 입력 아님) |

원문 보존: 검사기 출력 `_staging-20260914-2112-interactions/{prepare-final,inputs-final}.err`, 회차 로그 `related-run{1..11}.log`·`settings-run{1,2}.log`, 조립 스크립트, 이전 산출물 백업.

## 갱신한 상태

- `scope.md`: 이번 회차 실행 경계(`#exec-boundary-20260914`) · case 표 v2 재구성(`#design-cases` · viewport **390×877** = 루트 크롭이 캡션 33px을 포함 — 검사기 규칙) · 결정 대기 절(`#pending-decisions-20260914` · 승인 아님) · 헤딩 앵커 3개.
- `design-input.json`: 14 case — v2 12(기존 10 + 신규 `related/form-step4-sigungu`·`related/register-step4`), v1 잔존 2(`related/empty`·`related/form-error`), `interaction_exclusions` 6(설정 다이얼로그 · 기존 원문 «설정 나머지 무변…» 인용).
- `build-state.json`: `design_status=blocked` · `implementation_visual=unverified`(기존 visual-evidence의 input_digest·case 집합이 현재 입력과 불일치) · `g0_recheck_20260914` 기록. `phase`·슬라이스·G1 결정은 손대지 않음.
- `visual-check.md` ⓦ절: 명령·exit·수집 결과·제안 문안·최종 결과.

## 승인이 필요한 항목(근거와 함께 반환 · 대신 결정하지 않음)

수집기는 **새 조작 대상이 생긴 step에만 캡처**하고 **그런 step마다 표면을 만들어 case 또는 승인 예외를 요구**합니다. 그 결과:

- **D-A `related/empty`** — 빈 목록은 캔버스 knob(`listState`)이나 4명 전원 삭제로만 도달하며 어느 쪽도 수집기 캡처가 생기지 않음. 2026-09-13의 `_empty-variant.dc.html` 관찰은 현행 규칙상 원본 관찰 아님. 선택: ① case 삭제(범위변경 원문 필요) / ② 빈 상태 기본값 별도 export 제공(archive 변경 → 14 case 전부 재관찰 88분+) / ③ blocked 유지.
- **D-B `related/form-error`** — 오류 문구는 텍스트만 바뀌어 캡처 없음. 선택: ① case 삭제 / ② 리뷰어 제안 `--declared` 선언 경로 재시도(전체 재실행 필요 · 비조작 span 선언이 계약 취지에 맞는지 유보) / ③ blocked 유지.
- **D-C 드롭다운 열림 표면 12** — 승인 명세는 native `<select>`(열린 메뉴 캡처 불가). ① 예외 12행(사용자가 승인 원문을 scope.md에 직접 기재 — 제안 문안은 `visual-check.md ⓦ-④`) / ② case 12 추가 + 커스텀 드롭다운으로 G1′ 재설계.
- **D-D 설정 다이얼로그 표면 6** — 기존 원문으로 예외를 달았음(리뷰어: 해석 타당·확인 필요). 거부 시 제거(→ blocked).
- **D-E 삭제 뒤 3명 목록 4표면** — 같은 목록 상태의 데이터 변형이나 **삭제 toast의 유일한 수집기 캡처**(리뷰어 지적). ① 예외 4행 / ② case 추가(표면 1개당 1 case).
- **motion-notes 헤더 1토큰 정정** 승인 여부(승인 시 G1/G2 모션 축 기계 대조가 실제로 돔).

G2 함의(결정 불요 · 기록): v2 기준 캡처는 390×877(y≥33이 앱 프레임)이라 구현 대조 시 오프셋 규칙이 필요합니다. 리뷰어는 `design-spec.md` 495행의 v2 sha·844 인용 정정(G1 소관)도 남겼습니다.

Serena: 미사용 — 이번 작업은 심볼 편집이 아니라 산출물 JSON/Markdown·수집기 실행이라 기본 도구만 썼습니다.
