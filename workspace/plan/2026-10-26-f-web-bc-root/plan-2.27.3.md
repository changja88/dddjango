# dddjango 2.27.3 — BC 마다 도는 검사기는 뿌리 `application/` 의 서버 BC 만 잰다 (10-26)

## 바탕
- 바탕: 2.27.2 배포 뒤 main 에서 지었고, 같은 검사기 파일을 고치는 다른 항목과 한 판(2.27.3)으로 낸다. 2.27.3 은 patch — 검사 대상 BC 를 고르는 범위 고침
  (새 규칙 · 새 질문 · 새 기록 칸 · 규범 문면 변경 없음). 매니페스트 판은 `make release` 가 올린다. dddjango-web 무변.
- 결함(F4-122 «범위 밖» 관찰): BC 마다 도는 검사기 11곳과 `business_vocab.bc_dirs` 가 `rglob("application")` 로 저장소 안 모든 `application/` 의 하위 폴더를 BC 로 셌다.
  자매 플러그인 dddjango-web 의 화면 구역(`web/application/<단위>` · `web_test/application/<단위>`) · 기록 사본(`.dddjango-web/**/application/<bc>`) · 뿌리 밖 중첩
  컨테이너가 서버 BC 로 재어졌다.
- 판정: 결함. 근거 —
  - 서버 경로에 거짓 지적이 난다(주어가 서버 경로라 자매 가름 · Phase 0 경로 거름이 못 막는다):
    - #331: 기록 사본의 `baseline/application/<bc>/driven_layer/django_<bc>` 가 서버 앱과 같은 이름이라 서버 앱에 «label 이 저장소 안 다른 앱과 겹친다». 현장 사본 직접 실행에서
      서버 경로 3줄 · 진행 레인의 빚 목록에 항목으로 들어가 미룸 결정까지 받은 기록이 있다. G2 사본은 숨김 폴더를 빼서 G2 에서는 안 난다.
    - #505: web 구역이 서버 BC 와 같은 이름이면 «다른 BC» 를 경로로 가르는 `_check_domain_wide` 가 서버 BC 를 «타 BC» 로 보고, 서버 응용 층의 자기 BC 이벤트 import 를 잡는다.
      작은 저장소 재현에서 G2 귀속 → red. 현장 사본에 서버 BC 와 같은 이름의 web 구역이 셋 있다(지금은 그 BC 에 자기 이벤트 import 가 없어 잠복).
  - 자매 판정(R-3617)이 안 서는 저장소(`.dddjango-web/` 를 git 무시로 두는 저장소의 새 워크트리 등)에서 web 구역 하나를 병합하면 web 폴더 · 없는 파일 꼴 57줄이
    비-blob 귀속으로 남아 G2 가 멈춘다(작은 저장소 재현 · 2.19.2 가 고친 멈춤과 같은 꼴). 새 판은 레인 몫 1 만 귀속.
  - 규범 트리(discipline-houserules §1) «최상위는 셋 — `application/<bounded_context>/` · `framework/` · `<project>/`» · 형제 도구(`check-app-container._root_application`
    «레포 루트 직속 · rglob 금지» · `checker_target` · F4-122 `server_bc_dirs`)가 이미 뿌리 하나다.
- 설계: 1판(재현 · 현장 사본 대조 · 시제품) → 적대 검토(고친 뒤 구현 · 차단 0 · 중요 3 · 사소 7) → 구현 → 구현 검토(고친 뒤 배포 · 차단 0 · 중요 1 · 사소 4) → 덧고침.

## 고침
- `business_vocab.bc_dirs` 를 지우고 부르는 곳 6줄(business-vocabulary ×2 · domain-model · naming · missable-entrance · port-adapter-pairing)을 `server_bc_dirs` 로 —
  같은 뜻 함수 둘을 두지 않는다. `server_bc_dirs` docstring 을 새 뜻으로.
- 스스로 BC 를 찾는 검사기 11곳: `rglob("application")` → `(X / "application",)` 한 줄(나머지 거름 그대로) — context-isolation · composition-root · api-error-controller-contract ·
  event-publish · error-centralization · layer-skeleton · db-table · test-config · openapi-error-declaration · usecase-dto-placement · transaction-boundary.
- context-isolation: «import 경로가 BC 를 가리키나» 의 이름 모음(`_import_target_names`)은 검사 대상과 떼어 점으로 시작하는 마디 밖 모든 `application/` 컨테이너의
  폴더 이름으로 둔다 — 서버 BC 파일이 web 구역을 import 하는 것(#12)을 계속 잡고, 점 폴더를 빼서 직접 실행과 G2 · pre-gate 사본이 같은 이름을 쓴다.
  점 폴더 · SKIP_DIRS 는 걸을 때 들어가기 전에 잘라 낸다.
- `design_pregate._checker_bc`: 계획 경로가 사본 뿌리 직계 `application/<bc>/…` 일 때만 고른다(조상 링크 확인은 뿌리 직계라 지움) · docstring 셋을 새 뜻으로.
- Codex byte 미러 · `pregate_symbol_kinds.json` 재소성(검사기 소스가 바뀜).
- 그대로 둔 것: 채택 여부만 묻고 저장소 전체를 훑는 검사기 7종 · 8 자리의 `rglob("application")`(BC 고르기가 아님 · idempotency-scope-creep 에 둘) · `registry_gate._snapshot_cache_instances` · `container_bc_names` ·
  메시지 글 · SKIP_DIRS.

## 적대 검토 반영
- 중요 1(#74 가드): web 구역의 층이 «채택 신호는 있는데 층 0건» 가드를 가리던 것이 사라진다 — 행동 변화 2 · 시험으로 고정.
- 중요 2(«미채택 (clean)» 설명): 실제 출력대로 적고, 뿌리 밖 배치가 조용히 0 이 되는 것을 받아들일 한계로(행동 변화 1).
- 중요 3(실제 검사기 출력으로 자매 가름을 지나던 시험 둘):
  - registry_gate 쪽은 web 줄의 출처를 저장소 전체를 훑는 public-surface 검사기(타입 없는 함수 → #493)로 바꿔, 실제 출력 → 레코드 → 주어 → 자매 절 끝까지를 그대로 지킨다
    (#6 의 web 줄 없음 · 서버 #12 레코드 · 계약 레코드 단언과 함께).
  - anchor_diff 쪽은 같은 방법이 안 된다 — 범위 렌더 다섯(#2 · #5 · #6 · #15 · #16)은 이제 web 주어 줄을 실제로 내지 않는다(현장 사본에서도 다섯 모두 0). 그 시험은 새 동작
    (web 파일만 바뀐 실행은 직접 · 앵커 실행 모두 exit 0 · 자매 절 없음)을 고정하고, 범위 렌더의 자매 가름은 같은 묶음의 문자열 주입 시험이 지킨다.
  - 기록 사본에만 있는 이름의 import 를 #12 로 고정하는 시험(설계의 «유지 3»)은 넣지 않는다.
- 사소 1: 행동 변화 4 · 다음 판 후보.
- 사소 2(같은 이름 web 구역 import 가 옛 판부터 «같은 BC» 로 읽힘 · #95 만): 범위 밖 관찰로 남긴다(회귀 아님).
- 사소 3: 행동 변화 3 문구(web/ 는 web 백스톱 IM25 · web_test/ 는 두 플러그인 규칙 밖).
- 사소 4: 고침(이름 모음에서 점 폴더 뺌).
- 사소 5(`_snapshot_cache_instances` 뿌리만): 재 보고 바꿀 일이라 다음 판 후보.
- 사소 6: 지운 함수를 가리키던 docstring 둘을 고침. 한 원소 튜플 돌기 11곳은 최소 diff 로 두고 다음 정리 후보.
- 사소 7(다른 파이썬 판에서 pre-gate 번들 검사기 로드 실패): 같은 판의 다른 항목이 고친다 — 이 몫은 손대지 않는다.

## 구현 검토 반영
- 중요 1(시험 빈틈 — 고친 17 자리 가운데 7 자리는 되돌려도 아무 시험도 붉지 않았다): 첫 시험이 더하던 web · 중첩 구역은 깨끗한 파일뿐이라 옛 판에서도 13종 가운데
  6종만 출력이 달랐고, 오류 검사기 셋은 목록에 없었다. 시험 저장소 둘을 더해 검사기마다 새 판 출력을 글자까지 고정한다.
  - 중첩 컨테이너 저장소: 뿌리 깨끗한 BC 에 더해 `src/application/<재료>_<bc>/` 에 bad_rules BC 일곱 재료(composition-root · api-error-controller-contract ·
    error-centralization · openapi-error-declaration · business-vocabulary · naming · missable-entrance)를 둔다. 새 판은 다섯이 빈 출력이고, 저장소 전체를 훑는
    composition-root #653 · openapi-error-declaration #63 은 중첩 코드 줄(3 · 6)을 낸다 — 그 줄도 정확 일치로.
  - web 구역만 있는 저장소: BC 검사기 13종 + 오류 검사기 셋 모두 exit 0(다섯은 «표준 레이아웃 미채택 — 검사 대상 없음 (clean)» 한 줄 · 나머지 빈 출력).
    api-error-controller-contract 는 `--error-profile auto`.
  - 변이 확인: 고친 17 자리를 하나씩 옛 꼴(`rglob("application")` · `bc_dirs`)로 되돌리면 17 모두 새 묶음(`RootBcSelectionRegression`)이 붉다. 이름 모음을
    검사 대상 이름으로 되돌림 · 이름 모음의 점 폴더 거름 지움도 새 묶음이 붉고, pre-gate `_checker_bc` 를 중첩 허용으로 되돌림은 `SelectionEquivalenceTest` 가 붉다.
    변이 없음은 통과.
- 사소 1: 기록 사본에만 있는 이름을 서버 BC 가 import 해도 #12 가 나지 않음을 고정(설계 «유지 3» 의 반대쪽 — G2 · pre-gate 사본과 같음).
- 사소 2: 행동 변화 1 · 5 에 한 줄씩(web 구역만 있는 저장소의 오류 검사기 #74 가드 · 중첩 코드를 재는 저장소 전체 훑기 두 검사기).
- 사소 3: 고침 «그대로 둔 것» 을 «검사기 7종 · 8 자리» 로.
- 사소 4: 이름 모음이 점 폴더 · SKIP_DIRS 안까지 걷고 버리던 것을 들어가기 전에 잘라 낸다. 옛 걷기와 이름 집합이 같음을 확인했다(시험 저장소 · 현장 사본 ·
  이 저장소 · 링크 폴더 · SKIP_DIRS 아래 · 이름이 `application` 인 파일 꼴). 현장 사본에서 이름 모으기 0.5 ~ 0.6s → 0.2s.

## 행동 변화 · 받아들인 한계
1. 뿌리 밖 `application/`(web · web_test 구역 · 기록 사본 · 비표준 중첩 컨테이너)은 BC 마다 도는 검사기의 대상이 아니다. 그 경로 줄이 Phase 0 빚 스캔 · G2 legacy ·
   자매 절 · ⓓ 후보에서 사라진다. 뿌리 `application/` 없이 다른 곳(`src/application/` 등)에만 BC 가 있는 저장소는 검사기마다 «표준 레이아웃 미채택 — 검사 대상 없음 (clean)»
   또는 빈 출력으로 exit 0 이고(뿌리 `framework/` 가 있으면 layer-skeleton 은 #74 가드) — 조용히 0 이 될 수 있다. 받아들인다: 부르는 쪽(코디네이터 · Codex 스킬 · pre-gate ·
   refactor_audit)이 모두 프로젝트 뿌리(= `application/` 의 부모)를 TARGET 으로 넘기고 registry_gate 사본도 그 TARGET 그대로다. check-app-container 는 이미 뿌리만 본다.
   web 구역만 있는 저장소에서는 오류 검사기 셋(api-error-controller-contract · error-centralization · openapi-error-declaration)의 driving 층 0건 가드(#74)도
   사라진다(2.27.2 exit 2 → 새 판 exit 0 · 빈 출력) — web 만 쓰던 프로젝트에서 core 를 처음 돌리는 Phase 0 의 거짓 가드가 없어진다.
2. 뿌리 BC 가 층 폴더 없이 장고 표지(`models.py` 등)만 가진 저장소에 web 구역(층 있음)이 있으면, 층 0건 가드(#74)가 domain-model · port-adapter-pairing ·
   transaction-boundary · event-publish · usecase-dto-placement 직접 실행에서 선다(exit 0 → 2 · web 이 없는 저장소와 같은 출력). G2 는 앵커 · 현재 같은 줄이라 legacy(green).
3. web 쪽 파일이 서버 BC 도메인을 import 하는 것을 core 가 더는 자매 절에 «보고만» 하지 않는다. `web/` 은 dddjango-web 백스톱 IM25 가 게이트(더한 줄) · 빚 스캔에서 잡는다.
   `web_test/` 는 두 플러그인 규칙 밖이다(옛 core 줄은 서버 규칙을 시험 폴더에 건 것). 서버 쪽에서 web 구역을 import 하는 것은 #12 · #186 · #326 그대로.
4. 서버 `composition_root/` 의 web 구역 도메인 이벤트 import 는 이제 아무 검사기도 잡지 않는다(옛 판은 web 구역을 BC 로 센 우연으로 #505 가 잡았다 · 이 꼴을 막는 core 규칙은
   원래 없다).
5. 저장소 전체를 훑는 검사기(public-surface 등)의 web · web_test 줄은 그대로다(G2 에서는 자매 절 · ⓓ 신규로 감수자 입력에 든다).
   뿌리 밖 중첩 컨테이너의 코드도 composition-root #653 · openapi-error-declaration #63 이 저장소 전체 코드 훑기로 여전히 잰다.
6. 규칙 건수 요약 줄과 exit 가 바뀐다(현장 사본에서 db-table · naming · transaction-boundary 직접 실행 exit 2 → 0) — exit 2 를 «빚 있음» 근거로 적은 기록은 다시 잰다.
7. 진행 중 레인: 앵커 · 현재를 같은 판으로 재므로 거짓 귀속은 안 생긴다. 빚 파일은 신규분 거름에만 쓰여 줄이 사라져도 오류가 없고, ⓐ 잔존은 사라진 줄을 «잔존 아님» 으로만
   옮긴다. 판을 올리면 검사기 digest 가 바뀌어 pre-gate 재예보(G1 ~ G2 레인은 Phase 2 재발화)가 든다(`docs/DEVELOPMENT.md` §6).

## 시험
- `field_report_checker_smoke.RootBcSelectionRegression` 8건 —
  - 첫 커밋 5건: 고친 꼴 4(같은 이름 web 구역 · 자기 이벤트 #505 · 기록 사본 #331 · web · web_test 구역 + 기록 사본 + 중첩 컨테이너(깨끗한 파일)를 더해도
    BC 검사기 13종 출력 그대로 · 층 없는 뿌리 BC 의 #74 가드가 web 없는 저장소와 같음) · 유지 꼴 1(서버 → web 구역 import #12 줄 글자 일치).
    2.27.2 검사기로 돌리면 고친 꼴 4 가 붉고(하위 시험 포함 실패 9 · 첫 시험에서 옛 판 출력이 달라지는 것은 13종 가운데 6종) 유지 꼴은 통과.
  - 덧커밋 3건(구현 검토 반영): 중첩 컨테이너 bad_rules 저장소 7종 출력 글자 일치 · web 구역만 있는 저장소 16종 출력 글자 일치 · 기록 사본에만 있는 이름 import 는 #12 없음.
  - 변이 확인은 «구현 검토 반영» 중요 1.
- `registry_gate_smoke.SisterGateRegression` 1건 고침(web 줄 출처 = public-surface) · `anchor_diff_smoke.SisterAnchorRegression` 1건 새 동작으로 ·
  `pregate_transcription_smoke.SelectionEquivalenceTest` 모의 이름 둘(`server_bc_dirs`).
- 재료가 중첩 컨테이너에 기대던 시험 둘:
  - `registry_gate_smoke` R1 ~ R6(병렬 게이트 ↔ 옛 직렬 게이트 대조)의 «레코드 수백 건 저장소»: bad_rules 재료를 `fx_<재료>/` 에 통째로 두던 것을, 재료의 BC 는 뿌리
    `application/<재료>_<bc>` 로 옮기고 나머지는 `fx_<재료>/` 에 두게 바꿈(중첩 BC 를 안 재면 레코드가 300 아래로 떨어져 전제가 깨진다 · 바꾼 뒤 레코드 477).
  - `anchor_diff_smoke.HiddenSnapshotRegression.test_A10`(직접 실행 앵커는 숨김 경로까지 푼다): 숨김 경로 줄의 출처를 기록 사본 BC(이제 BC 아님)에서 뿌리 BC 안
    숨김 폴더(`driving_layer/.old/api_router.py` → context-isolation #113)로 바꿈 — 지키는 성질은 그대로(앵커 기존분 · 신규분 0).
- 좁은 실행(구현 사본 · 봉인 전): field_report_checker_smoke 98 OK · registry_gate_smoke 48 OK + 케이스 45/45 · anchor_diff_smoke 121 OK + 케이스 14/14 ·
  pregate_transcription_smoke `SelectionEquivalenceTest` 2 OK · fixture_matrix 114/114 · findings_count_matrix 73/73 · checker_baseline_matrix 73/73 · checker_lint 위반 0 ·
  gen_pregate_symbol_kinds `--check` in-sync · Codex 미러 scripts 폴더 전체 byte 같음. 봉인 · `make verify` 는 통합 때.
- 덧커밋 뒤 좁은 실행: `RootBcSelectionRegression` 8 OK · field_report_checker_smoke 101 OK · registry_gate_smoke 48 OK + 케이스 45/45 ·
  anchor_diff_smoke 121 OK + 케이스 14/14 · fixture_matrix 114/114 · findings_count_matrix 73/73 · checker_lint 위반 0 · gen_pregate_symbol_kinds `--check` in-sync ·
  Codex 미러 `diff -rq` 차이 없음.

## 현장 사본 대조(읽기만 — 서비스 저장소의 `.py` · 폴더 모양만 옮긴 사본)
- 서버 주어 지적 줄: 직접 실행 2,853 → 2,850(빠진 3 = #331 거짓) · 숨김 폴더를 뺀 G2 꼴 사본 2,850 → 2,850(글자까지 같음).
  자매 뿌리 주어 지적 줄: 32,048 → 27,264(남는 몫은 모두 public-surface).
- 작은 저장소 G2: legacy 138 → 42 · 승인 유입 증명 대상(web 구역 하나 병합) 207 → 0 · ⓓ 신규 34 → 26.
- 시간(G2 꼴 사본 · 옛 · 새를 검사기마다 동시에 · 회차마다 순서 바꿈 · 다른 일과 함께 돌아 절대값은 흔들림): 27종 합 586 → 371s · domain-model 314 → 156s(비 0.42 ~ 0.60 —
  G2 · pre-gate 벽시계를 묶는 검사기) · business-vocabulary 0.64 · context-isolation 0.80 · naming 0.83 · composition-root 0.87. 느려지는 검사기 없음.

## 범위 밖(다음 판 후보)
- 저장소 전체를 훑는 검사기(public-surface 등)의 web · web_test 줄과 그 ⓓ 후보(서버 규범의 적용 범위 질문).
- 서버 `composition_root/` 의 web 구역 import(행동 변화 4).
- `registry_gate._snapshot_cache_instances` 를 뿌리만으로(재 보고).
- 한 원소 튜플 돌기 11곳 정리 · `container_bc_names` 와 `bc_names` 합치기(BC 가 늘 뿌리라 같아짐).
- 같은 이름 web 구역 import 가 옛 판부터 «같은 BC» 로 읽히는 것.
- #46 은 넓히지 않는다(규범 글이 «`framework/` 에서 `application/` 쪽» 만 말한다) · R-3617 문면 그대로.
