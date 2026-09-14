`dddjango-web  [▶ 스코프] → [· 설계] → [· 구현] → [· 마무리]`

```
─────────────────────────────────────
dddjango-web · G0 스코프 승인 (입력 차단 보고 · 사전 승인 범위 = Phase 0까지)
방금 끝낸 것 : 기존 폴더 재사용 · 배선 6종 전부 정상 · 재동결 0 · 조작 상태 수집 채널 신규 동결(관계인 4회차·설정 1회차 · 잔여 0) · v6 case 30건(viewport 390×877) · observation v2 30 · 재생 trace 30 · prepare 2회 exit 0 · 독립 입력범위 리뷰 2회(둘 다 fail) · inputs 실제 실행 exit 2
승인 대기   : ① related/empty ② related/form-error(+value-only 육안 항목) 제외 승인 원문 ③ 신규 case 13건 case 유지 vs 예외 행 ④ viewport 877의 G2 대조 방식
다음에 할 것 : ①② 결정 → scope.md 승인 원문 → prepare 재실행 → 같은 입력범위 독립 재검토 pass → inputs exit 0 → design_status=ready(그 전엔 Phase 1 진입 불가)
─────────────────────────────────────
```

## 실행한 것과 결과

**모드·전제조건** — 폴더 ⓐ 재사용(`.dddjango-web/20260912-1640-web-related-persons/` · 새 폴더 0). 모드는 기존 판별(풀·새 영역)대로. web 배선 6종 전부 정상(INSTALLED_APPS `web.apps.WebConfig` · TEMPLATES DIRS `web/` · STATICFILES_DIRS 두 튜플 · `include("web.urls")` · `testserver` · htmx 2.0.10 단일 설치 + base `defer` 로드 + `block scripts`) → 편집 0. 작업 트리 dirty 아님. 이 저장소는 커밋 1개(`60943b3` scratch)라 build-state가 참조하던 `ace3a9ab`·`edaf0deb`·`54d77167` 등은 존재하지 않음(범위 밖이라 값 유지·기록만).

**현행 검사기 첫 실행(출발점)** — `check_design_evidence.py --phase inputs` → **exit 2**: 12 case 전부 «interaction evidence required (version 2 with interactions)» + coverage reviewed-input 불일치. 즉 plugin 1.1.12가 요구하는 **조작 상태 수집 채널**이 이 폴더에 없었음.

**신규 동결(승인된 «없던 채널»)** — `python3 -m http.server 8747 --bind 127.0.0.1`(design-ref 서빙 · entrypoint sha `cf2fe348…` curl 일치) 위에서 `observe_interactions.mjs`(Node v26.8.2 · Playwright 1.63.0-alpha · `--browser-channel chrome` · 560×1040 · `--crop-root` · `--max-minutes 8`):
- 관계인: run1~4(exit 3·3·3·3 · `--resume` 3회 · 32분) → `captures/related-persons-interactions.json` targets 223 · executed 612 · **잔여 0** · 표면 25 · partial(max_minutes · 잔여 0 상태에서 컨텍스트 큐만 잔존).
- 설정: run1 exit 3 → `captures/preferences-interactions.json` targets 30 · executed 178 · **잔여 0** · 표면 8 · partial. **사건**: 8분 상한 뒤 종료 단계에서 node가 ~8분 0% CPU 정지 → 내 PID(50566)에 SIGTERM → 문서가 정상 작성되고 exit 3(stdout 요약 있음). 손편집 0.
- `--declared`·`--excluded-regions` 미사용(소스 검토: 전 조작 대상이 DS 부품 · declared_unmatched 0 · outside_root 0). 캡처는 드라이버 저장 루트 크롭 PNG(관계인 327+1 · 설정 6+1 장 · captures/ 79MB).
- per-case trace 30건: reached_by 계보를 스니펫 `interaction_audit.js`로 실제 재생 + `render_audit.js` 전문 실행 + fonts/images/응답/실패/콘솔 — state_hash 30/30 일치, 재생 스크린샷 sha 23/30 바이트 일치.

**case 목록 v6** — `design-input.json` 30 case(관계인 25 · 설정 5) · viewport **[390,877]**(루트 rect = 캡션 33px + 844 · plugin 규칙의 기계적 결과). v5 12 중 10 재결속, 신규 16(드라이버 표면 15 + 저장 toast 1). **`interaction_exclusions` 0행**(승인 원문 필요 → 대신 만들지 않음).

**독립 입력범위 리뷰(실제 호출 2회)** —
- 1차 `dddjango-web:design-review-web`: prepare exit 0 · digest `888492ac…` → **fail**(원문 `_history/v6-review-round1/coverage-review.md`). 근거 3 중 Coordinator 소관 2건 반영(설정 variant 2건 서술 정정 — toast 잔상이 실제로 보임 · `related/list-after-save` step 80 결속 추가).
- 2차: prepare exit 0 · digest `5f19cddf…` → **fail**(원문 `coverage-review.md` · sha `8301913f…`). 유일 근거 = 아래 미결 ①②.

**inputs 실제 결과** — `check_design_evidence.py --build … --phase inputs` → **exit 2** · defect 1건 `coverage_review: independent review-result: pass required`(reviewed-input 일치 = 원본·case·관찰 바이트 정합).

**상태 갱신** — `build-state.json`: `design_status: ready → blocked` · `implementation_visual: pass → unverified`(기존 visual-evidence 12 case·844와 현재 30 case·877 불일치) · `g0_reopen_20260914` 기록. `scope.md`(실행 경계·v6 표·미결) · `visual-check.md`(ⓥ′ ①·②). 기존 증거는 `_history/v5/`(덮어쓴 trace 10건은 git HEAD 복원)에 보존. 서버·드라이버 프로세스 정리 완료. 로그: `/tmp/dddjango-web-a8-g0-logs-20260914-2248/`.

## 승인이 필요한 항목(근거와 함께 반환)

1. **related/empty** — 빈 상태는 캔버스 knob(`listState`) 또는 4명 전부 삭제로만 도달. v5는 archive 밖 변형본(`_empty-variant.dc.html`)으로 관찰했는데 현행 규칙(served = archive 바이트)에선 불가. 드라이버 612 step 동안 미도달 → 기계 결속 불가. 검사기를 돌리기 위해 목록에서만 제외했고 **제외 승인 원문 없음**이 blocked 사유. 선택지: ⓐ 제외 승인(육안·명세 항목 유지) / ⓑ 시안에 도달 경로 추가 후 재동결 / ⓒ `--resume` 추가(58분 잔여 · 보장 없음).
2. **related/form-error** — 오류는 텍스트 span만 추가(컨트롤 0) → 캡처 없음 → 현행 채널로 결속 불가. 같은 결정에 value-only 육안 항목(step3 몰라요-체크 · step4 못려요-체크 · 등록 성공 toast 미관찰 · 상세 데이터 변형)을 합쳐 두었음.
3. **신규 case 13건(시·군 메뉴 9 · 설정 Dialog 4)** — plugin 순서(선언→case→예외)대로 case로 이었으나, 시·군 메뉴는 mock `CITIES` vs `korea_places.txt` 데이터 차이, 설정 Dialog는 «상담» 탭·toast 잔상(구현 재현 불가) 성격. 예외 행 전환엔 승인 원문 필요(후보 인용: «PD-3 = ⓐ intake 구조 피커 재사용» · «설정 나머지 무변(…)»).
4. **viewport 390×877** — G2 구현 캡처엔 캡션 33px가 없어 구조적 오프셋 → G2 대조 방식 결정(G0 차단 아님).

비차단 후속: scope.md «16건/15건» 문구 정합(digest 안이라 재검토 없이 손대지 않음) · `design-spec.md` case 표는 G1 architect 갱신 대상 · captures/의 v5 잔재는 보존 원칙상 그대로.

Serena: 미사용 — 산출물 JSON/Markdown/PNG·스크립트 실행 작업이라 심볼 단위 편집이 없었음.
