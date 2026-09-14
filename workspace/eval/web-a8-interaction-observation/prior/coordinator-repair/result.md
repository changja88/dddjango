A8 관계인 G0 입력 준비의 보완·독립 재검토·inputs 검사를 마쳤습니다. `design_status`는 **ready**로 갱신했고, G0 배너 승인은 이번 범위 밖이라 열지 않았습니다.

```
─────────────────────────────────────
dddjango-web · G0 스코프 — 입력 상태 보고(r3 · 승인 게이트는 열지 않음)
방금 끝낸 것 : 직전 fail 항목 보완 관찰 37 step → 독립 리뷰어 실제 호출(pass) → inputs exit 0
승인 대기   : 없음(이번 범위 = G0 입력 상태 갱신까지 · 새 제품 결정 0)
다음에 할 것 : 사용자 지시 시 G0 배너 승인 → Phase 1 (현재 기준 독립 검토 pass + inputs exit 0 확보)
─────────────────────────────────────
```

**보완 관찰(원본 UI 조작만 · 바이트 무변 · 변형 파일 0)**
- 직전 검토가 요구한 필수 2건을 해소했습니다. 삭제 확인 Dialog 스크림 click은 상세 복귀(`cancelDelete`), Escape는 무반응입니다. 4개 Select 전부에서 ArrowDown/Up 포커스 순환·Escape·메뉴 밖 mousedown·trigger 재클릭을 조작해 «메뉴만 닫힘»을 확인했습니다.
- 권고 항목도 함께 관찰했습니다. 폼 step2~4 Escape 무반응, 수정 폼 관계·이름 변경 저장 후 목록 행·상세 반영, 빈 목록에서 등록하기 click, 성별 재선택, 윤달 해제, menuitem hover, 설정 Avatar 이니셜의 serif fallback입니다.
- 값이 있는 Select를 재열면 선택 항목이 accent 배경+check로 강조되는 상태가 드러나 신규 case로 승격했습니다(`related/step1-relation-menu-selected`, 34 case).
- 증거는 evidence 9장, 신규 case 캡처·trace·source-observation, 회차 로그 123 step, 16개 case trace의 `supplementary_observations_r3`입니다. r2 바이트와 직전 fail 검토 원문은 `_history/v5-r2/`에 그대로 보존했습니다.
- partF 1차 실행은 스크림 검출기 오판으로 Escape 3행의 결과 문구가 틀려 폐기하고, 검출기를 고쳐 전량 재실행했습니다. 이 사실은 visual-check ② #18에 기록했습니다.

**문서 정정·출처 연결**
- `scope.md`에 r3 실행 경계와 «기존 결정 출처 보완» 절을 추가했습니다. 재동결 v3·v4·v5의 사용자 지시(발주서 개정 9·11·13·14)와 사용자 결정 5(D1·라벨 8종·D7·D3~D5·DS 전역)를 `existing-approval.md`(본문 SHA-256 `556aa8ea…`)에 연결했습니다. 새 제품 승인이 아니라 기존 결정의 출처 연결입니다.
- `visual-check.md`의 폰트 서술을 정정했습니다(설정 Avatar 이니셜만 Gowun Batang fallback · 범위 밖). «미관찰·한계» 표에 해소 항목과 trace `dialogs`/`errors` 필드 한계를 명시했습니다.

**독립 검토·inputs 결과**

| 단계 | 결과 |
|---|---|
| `--phase prepare` | exit 0 · review_digest `db6b7003…` |
| `dddjango-web:design-review-web` G0 입력범위 모드(실제 호출) | `reviewed-input: db6b7003…` · **`review-result: pass`** |
| 반환 원문 보존 | `build/coverage-review.md` sha256 `437406f3…` → `design-input.json.coverage_review` 연결 |
| `--phase inputs` | **exit 0** · input_digest `bc5de8e6…`(문서 정정 후 재실행도 동일) |
| `build-state.json` | `design_status=ready` · `g0_repair_r3` 블록 추가(다른 상태 무변) |

리뷰어의 비차단 권고 중 evidence 개수(22장) 정정과 e23 캡처 한계 병기는 반영했습니다. `scope_refs` 앵커 정리는 scope 바이트를 바꾸면 digest·재검토가 필요해 다음 scope 갱신 시로 미뤘고, PD-3 이탈 표 재기술은 설계 단계 소관으로 기록했습니다.

**경계 준수**: 쓰기는 `coordinator-live/build`·`scratch`뿐이며 메모리·원본 A8·서버·브라우저는 건드리지 않았습니다(발주서 개정은 `git show main:`으로 읽기만). 브라우저·원본 서버는 관찰 후에도 동작 중입니다. 인계된 G2 산출물(`visual-evidence.json`·impl 캡처)은 r1 입력 기준이라 새 digest에 대해 stale이며 손대지 않았습니다. Serena는 문서·관찰 작업이라 사용하지 않았습니다.