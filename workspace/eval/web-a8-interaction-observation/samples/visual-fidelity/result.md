# 표본 ② 이름 등록 대화상자 — `web-a8-visual-fidelity/role-browser-app/source.html` (Task 11 Step 4 · 게이트 아님 · 기록만)

## 절차

1. `source.html`·`source.css`(entrypoint가 참조하는 2파일)를 scratch로 복사한 뒤 `archive_design.py source.html --source-root scratch/samples/visual-fidelity/src --out …/build/design-ref --manifest …/build/source-manifest.json` → exit 0(2파일 보존 · missing 0). entrypoint sha `269d9114…` = 저장소 원본과 동일.
2. `design-ref`를 `python3 -m http.server 8792 --bind 127.0.0.1`로 서빙.
3. 드라이버(백그라운드 · 1슬라이스): `node dddjango-web/scripts/observe_interactions.mjs --url http://127.0.0.1:8792/source.html --root 'main.source-dialog' --viewport 390x844 --crop-root --entrypoint-sha 269d9114… --archive-sha c00fdc8c… --out BUILD/captures/source-interactions.json --captures-dir BUILD/captures --max-minutes 8` (env·Node 동일). `--resume` 불필요.

## 수치(마지막 실행 = 유일 실행 run-1)

| 항목 | 값 |
|---|---|
| exit / elapsed | **0** / 6 s |
| stdout 요약 | `{"targets":2,"executed":8,"residual":[],"surfaces":1,"partial":false,"capsHit":[],"environmentError":null}` |
| collector | snippet `a3c13880…` · driver `4ad627df…` · path `node` |
| `capabilities` | `{react_props: true, cdp_listeners: true}` |
| `discovery_limits` | `[]` |
| 발견(targets) | 2 = textbox «이름○»(input) + button «다음» — 모두 `semantic`, handler 0(JS 없음) |
| 실행 단위(steps) | 8 executed — fill 2 · click 2 · focus 2 · blur 2(빈 값/채운 값 두 문맥) · error 0 |
| 표면(surfaces) | 1 (initial 하나 — 어떤 조작도 표면·state_hash를 바꾸지 않음; fill만 `value_empty` 전이) |
| 캡처 | initial 1 · step 캡처 0 |
| residual / partial / caps_hit | `[]` / false / `[]` |
| served | `source.css`, `source.html` |

## 관찰(기록만 — 판정 없음)

- `:focus-within`으로 테두리·그림자가 바뀌는 focus 상태는 inventory(enabled·checked·face·value_empty·surface·occluded·live) 어느 항목도 바꾸지 않아 state_hash·표면·캡처가 생기지 않는다. 즉 이 드라이버는 조작 **상태**(K1)를 세지 CSS 시각 상태를 세지 않는다 — 이 표본의 원래 평가 축이던 focus 시각 대조(`implementation-*-focus-*.png`)는 여전히 visual 증거의 영역이다.
- textbox 접근 이름이 «이름○»으로 잡힌다 — `aria-hidden="true"` 아이콘 텍스트(○)가 label 텍스트에 합쳐졌다. 이름 규칙이 aria-hidden 자손을 제외하지 않는다는 기록.
- «다음» 버튼의 대상 id `7cbb15a54d37`이 표본 ①의 «다음»과 같다 — 대상 id는 K1대로 {role, name, input_type, owner, owner_items_hash}의 canonical sha 12자이며(이름이 빈 대상만 dom_path 포함) 문서·dom_path와 무관하다.
- raw 산출은 `/tmp/dddjango-web-interaction-evidence-20260913/samples/visual-fidelity/`(저장소 밖). 저장소에는 `summary.json` 집계만.
