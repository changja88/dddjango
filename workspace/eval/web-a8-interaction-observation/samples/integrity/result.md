# 표본 ① 정적 HTML+JS 위저드 — `web-design-source-integrity/2026-09-07/fixture/source-positive` (Task 11 Step 4 · 게이트 아님 · 기록만)

## 절차

1. `archive_design.py source-positive/index.html --source-root …/source-positive --out scratch/samples/integrity/build/design-ref --manifest …/build/source-manifest.json` → exit 0(5파일 보존 · missing 0). 저장소 원본은 읽기만.
2. `design-ref`를 `python3 -m http.server 8791 --bind 127.0.0.1`로 서빙(드라이런 8765와 별개 포트).
3. 드라이버(백그라운드 · 1슬라이스): `node dddjango-web/scripts/observe_interactions.mjs --url http://127.0.0.1:8791/index.html --root 'main[data-flow]' --viewport 390x844 --crop-root --entrypoint-sha a262c5c7… --archive-sha c64134df… --out BUILD/captures/index-interactions.json --captures-dir BUILD/captures --max-minutes 8` (env `DDDJANGO_WEB_PLAYWRIGHT_MODULE`·`DDDJANGO_WEB_BROWSER_CHANNEL=chrome`, Node v26). `--resume` 불필요.

## 수치(마지막 실행 = 유일 실행 run-1)

| 항목 | 값 |
|---|---|
| exit / elapsed | **0** / 268 s |
| stdout 요약 | `{"targets":10,"executed":148,"residual":[],"surfaces":4,"partial":false,"capsHit":[],"environmentError":null}` |
| collector | snippet `a3c13880…`(= `dddjango-web/assets/interaction_audit.js`) · driver `4ad627df…`(= `assets/observe_interactions.pw.js`) · path `node` |
| `capabilities` | `{react_props: true, cdp_listeners: true}` |
| `discovery_limits` | `[]` |
| 발견(targets) | 10 = handler 1(root click listener, `found_by: cdp_listener`) + input 1 + button 5 + radio 2 + link 2(모두 `semantic`) |
| 실행 단위(steps) | 148 executed / 0 실패 — click 124 · fill 8 · focus 8 · blur 8 · navigated 0 · error 0 |
| 표면(surfaces) | 4 (위저드 step1→step2→step3→완료 화면 전부 도달) |
| 캡처 | initial 1 + step 36(고유 sha 15) |
| residual / partial / caps_hit | `[]` / false / `[]` |
| served | `assets/mark.png`, `index.html`, `steps.js`, `styles/base.css`, `styles/effects.css` (5 = 아카이브 전량) |
| outside_root / declared_unmatched | 0 / `[]` |

## 관찰(기록만 — 판정 없음)

- K1 identity 규칙({role, name, input_type, owner, owner_items_hash} canonical sha 12자 · 같은 인벤토리 안 충돌 때만 dom_path 추가)대로, 다른 step에 있어 한 인벤토리에 동시에 나타나지 않는 같은 이름 컨트롤은 한 대상으로 합쳐진다: DOM의 버튼 6개(다음×2·이전×2·완료·다시 시작)가 대상 5개로 잡히고 `dom_path`는 첫 발견 위치만 남는다(«다음» = `section:nth-of-type(1)/button:nth-of-type(1)`). 완료 버튼이 4회 실행됐으므로 step2의 «다음»도 같은 id 아래 실행된 것이 확인된다.
- 각주 링크 2개(`href="#"` + `preventDefault`)는 각 24회 실행·navigated 0 — 상태 변화 없는 대상도 문맥마다 재실행돼 실행 수를 키운다.
- 원본 요구(`requirements.md`)의 «이전은 값 보존·다시 시작은 초기화»는 fill 8·radio 8 실행과 4표면 도달로 관찰 범위 안에 있다.
- raw 산출(interactions.json·PNG·run 로그)은 `/tmp/dddjango-web-interaction-evidence-20260913/samples/integrity/`(저장소 밖). 저장소에는 `summary.json` 집계만.
