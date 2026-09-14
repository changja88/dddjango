G0 원본 관찰·동결 checkpoint(r2)를 마쳤습니다. 원본 바이트는 v5 그대로이고(관계인 `cf2fe348…`·설정 `b88e995b…`·서버 제공 바이트와 sha256 일치), 조작 가능한 대상을 전부 실제로 조작해 case를 12개에서 33개로 보강했습니다. `--phase prepare`는 exit 0이며, 독립 검토 전이므로 `--phase inputs`는 exit 2로 `design_status=pending`을 유지합니다. 리뷰어는 호출하지 않았고 pass 판정도 쓰지 않았습니다.

**리뷰어에게 보낼 입력**
- build: `/tmp/dddjango-web-a8-interactions-20260913/coordinator-live/build` · project-root: `/tmp/dddjango-web-a8-interactions-20260913/coordinator-live`
- review_digest(prepare): `23908d43d49a0c2aca8604466080f9b73c114c0409ff8e7e3469cc492c5915de`
- `design-input.json`(33 case · `coverage_review: null`) · `scope.md`(사용자 요구·확정 이탈 원문 유지 + r2 실행 경계 + case 표) · `source-manifest.json`(archive 1) · `design-ref/` · `captures/*-original.png` 33 · `*-trace.json` 33 · `*-source-observation.json` 33 · `*-evidence.png` 13 · `captures/original-interaction-log.json`(86 step) · `render-audit.json`(r2 재실측 · validate OK · r1 대비 diff 0) · `motion-notes.md` · `visual-check.md`(①-원본 관찰 표 `| 진입 상태 | 조작 대상·동작 | 실제 결과·새로 드러난 대상 | 관찰 근거 | 연결 case·미관찰 사유 |` · ② 실행 기록 · ⑤ 인계 목록)
- 명세 이탈 표: 인계된 `design-spec.md`(미수정)

**보강된 관찰(원본 컨트롤만 · 변형 파일 0 · knob 미사용)**
- 빈 목록을 r1의 변형 파일 대신 원본 UI 삭제 4회로 도달했습니다.
- 새 case 21개: 상세 데이터 변이 3(음력 윤달·시·군 / 시간 모름 / 곳 모름), 삭제·등록·저장 toast 3, Select 메뉴 열림 4(관계 8·태어난 시 12·시·도 17·시·군 31), disabled 2(몰라요·못려요), 시·군 활성 1, 포커스·입력 중 3, 단계별 오류 문구 5.
- 동작 사실(설계 판단 후보, `visual-check.md` §④): 스크림 클릭은 onCancel(상세 닫힘·폼 step1 닫힘·step≥2는 이전 단계), Escape 무반응, 메뉴가 Dialog 카드 밖으로 넘침, Toast가 떠있는 버튼과 8px 겹침, 몰라요 해제 시 값 미복원, 시·도 변경 시 시·군 소거. 오타 3종은 design-spec에 정정 처분이 이미 있어 새 제품 결정은 필요하지 않습니다.

**미관찰(조용한 생략 없음)**
- knob 4 variant(사용자 결정 유지), 설정의 다른 행(범위 밖), 키보드 focus-visible 캡처(활성 요소만 기록), Dialog 내부 스크롤·긴 목록 스크롤 고정(원본 데이터로 미도달), 모션 duration 실측(reduce 모드 캡처 · 스캔값 소유).

**실행 경계 보고**
- 제공 Playwright MCP는 `EPERM ~/Library/Caches/ms-playwright/b/browser@…`로 초기화 2회 실패했습니다. 같은 headless Chrome의 CDP(50234)에 이미 설치된 playwright-core로 연결해 관찰했고 설치·서버 기동·중지는 없었습니다.
- A8 project 쓰기 0. 다만 A8 워크트리의 `build-state.json`이 git 대비 수정 상태인데 mtime 12:31로 이번 실행(14:10 시작) 이전이며 이번 checkpoint의 흔적이 없습니다. 인계 시점의 미커밋 상태로 판단합니다.
- 인계된 G2 산출물(`visual-evidence.json`·`render-audit-impl.json`·`*-impl.png`)은 r1 입력 기준이라 r2 digest에 대해 stale입니다. 손대지 않았습니다.
- r1 자료는 `build/_history/v5-r1/`에 보존했고, stale한 r1 `coverage-review.md`는 루트에서 제거했습니다.
- 메모리 파일 저장은 EPERM으로 실패해 기록하지 못했습니다.

**다음 단계**: 별도 실행자가 위 입력으로 입력범위 모드 검토를 수행해 `reviewed-input: 23908d43…`과 `review-result`를 반환하면, Coordinator가 원문을 `coverage-review.md`로 보존하고 포인터를 연결한 뒤 `--phase inputs`를 실행합니다. exit 0일 때만 `design_status=ready`가 됩니다.

Serena·Graphify는 opt-in 표식이 없어 사용하지 않았습니다.