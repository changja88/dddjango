# dddjango 2.27.2 — framework 쪽 «어느 BC 든» 검사는 뿌리 `application/` 의 서버 BC 만 센다(F4-122) (10-26)

## 바탕
- 바탕: main(dddjango 2.27.1 봉인 뒤). 2.27.2 는 patch — 검사기가 «서버 BC 이름 · 어휘» 를 모으는 범위 고침(새 규칙 · 새 질문 · 새 기록 칸 · 규범 문면 변경 없음).
  매니페스트 판은 `make release` 가 올린다. dddjango-web 무변.
- 결함(장부 F4-122): `business_vocab.bc_names(root)` · `all_vocab(root)` 가 `bc_dirs(root)` = `root.rglob("application")` 의 모든 하위 폴더를 BC 로 셌다.
  자매 플러그인 dddjango-web 의 화면 구역(`web/application/<단위>` · `web_test/application/<단위>`)과 기록 사본(`.dddjango-web/**/application/<bc>`)의
  이름 · 도메인 어휘가 서버 BC 의 것으로 섞여, httpx 재시도 부품의 매개 `client` 가 #416(«<technology> 모듈에 BC 이름») 으로 붉었다.
- 판정: 결함. 근거 — 규범 트리(discipline-houserules §1) «최상위는 셋이다 — `application/<bounded_context>/` · `framework/` · `<project>/`» ·
  framework 검사기가 보는 `framework/` 도 뿌리 하나 · 같은 모듈 `container_bc_names` docstring(F4-87 · 2.21.1) · plan-2.21.1 «범위 밖» 절이 같은 뿌리로
  framework #52 · #416 · #426 · #365 · #444 · `all_vocab` 을 미리 적어 둠.
- 설계: 1판(재현 · 현장 읽기 대조 · 시제품) → 적대 검토(고친 뒤 구현 · 차단 0 · 중요 1 · 사소 8) → 구현.

## 고침
- `business_vocab.server_bc_dirs(root)` 신설 — `root / "application"`(형제 도구 `checker_target` · `check-app-container` 와 같은 꼴)의 점으로 시작하지 않는
  하위 폴더. 절대 마디 SKIP_DIRS 거름은 `bc_dirs` 와 같다. `rglob` 없음.
- `bc_names(root)` · `all_vocab(root)` 를 `server_bc_dirs` 위로. 부르는 곳은 모두 «어느 서버 BC 든» 판정이다:
  - check-business-vocabulary — BC 이름 #52 · #416 · #426 · 업무 어휘 #47 · #587 · #617 · #562 · 후보 #448 · #425.
  - check-broker-contract — celery packages 식 #444 · broker 업무 어휘 #518.
  - check-naming — framework 칸 이름 물음 ⓓ#36.
  - check-port-adapter-pairing — ACL 상대 «우리 BC» #365(코드 무변 · `bc_names` 의 뜻이 바뀌어 web 구역 이름을 상대로 받던 놓침이 닫힌다).
- check-business-vocabulary 애그리거트 이름(#616) 을 `server_bc_dirs` 로.
- 그대로 둔 것: `bc_dirs`(검사 대상 BC 고르기 — 검사기 여럿과 pre-gate `_checker_bc` 가 같은 뜻으로 맞춘다) · `container_bc_names` · 메시지 글.
- Codex byte 미러 둘 · `pregate_symbol_kinds.json` 재소성(검사기 소스가 바뀜).

## 적대 검토 반영
- 중요 1(#365): 시제품은 «우리 BC» 를 `container_bc_names(bc)` 로 바꿨으나, 뿌리 밖 컨테이너의 BC(기록 사본 · `web_test/`)가 뿌리 서버 BC 를 ACL 상대로 둘
  때 새로 붉었다 → 원래 줄(`bc_names(root)`)을 그대로 둔다. `bc_names` 가 서버 BC 이름이 되므로 web 구역 상대는 잡히고 그 소음은 없다.
- 사소: 뿌리 찾기를 형제 도구 꼴로 · 시험에 broker · naming 쪽 부르는 자리와 기록 사본 ACL 꼴을 더함 · 행동 변화 문구(아래) · 커밋 → 봉인 → verify 순서.
- 그대로(선택): `application/__pycache__` 가 이름에 드는 것은 옛 판과 같아 손대지 않는다.

## 행동 변화 · 받아들인 한계
1. 뿌리 밖 `application/`(web 구역 · `web_test/` · 기록 사본 · 비표준 중첩 컨테이너)의 이름 · 어휘 · 애그리거트는 framework · `<project>/` 쪽 검사에 안 든다.
   뿌리 `application/` 이 없는 저장소는 그 검사의 BC 이름 · 어휘가 0 이다(옛 판은 그 밖 컨테이너의 것을 셌다). 표준 호출 계약(TARGET = `application/` 의 부모)
   밖 배치다.
2. framework 가 web 구역을 import 하거나 그 타입을 자료 필드에 써도 core 검사기는 잡지 않는다 — 옛 판은 #52 · #616 으로 우연히 잡았다(#46 은 `application` 만 본다).
3. #365 는 ACL 상대 이름이 web 구역에만 있으면 이제 위반(통신 import) · 후보(순수 스텁) — 옛 판은 놓쳤다.
4. ⓓ#36(후보)은 framework 칸 이름이 web 어휘에만 있으면 새로 뜬다.
5. 메시지에 찍히는 목록(BC 이름 #52 · #416 · #426 · 업무 어휘 #47 · #518 · #562 · #587 · #617 · 애그리거트 #616 · 후보 #448 · #425)은 줄 수 있고 #444 는 줄이
   사라질 수 있다. 빚 매칭은 앵커 뒤 새로 선 줄에만 걸리므로(registry_gate 귀속 줄 · 앵커 기존분은 앵커 · 현재를 같은 판으로 잰다) 진행 중 레인이 새로 만든
   framework 파일 줄을 목록까지 부분 문자열로 빚에 적었다면 다시 적는다.

## 시험
- `field_report_checker_smoke.FrameworkServerBcNameRegression` 14 건 — 오탐 꼴 11(#416 web 구역 · 기록 사본 · #52 · #426 · #617 · #616 · #562 · #444 · #518 ·
  ⓓ#36 · #365 web 구역 상대) · 유지 꼴 3(서버 BC 이름 #416 · 서버 BC 상대 #365 · 기록 사본 BC 의 서버 BC 상대 #365) — 줄 글자 정확 일치.
  2.27.1 검사기로 돌리면 고친 꼴 11 이 붉고 유지 꼴 3 은 통과, 고친 판에서 14 모두 통과.
- 기존 묶음(시제품 위): fixture_matrix 114/114 · findings_count_matrix 73/73 · checker_cross_matrix 348 차이 0 · field_report_checker_smoke 79 OK.

## 현장 대조(읽기만 — 서비스 저장소의 `.py` · 폴더 모양만 옮긴 사본)
- 서버 BC 이름 36 → 24(빠짐 = web 구역 10 · 기록 사본 2) · 업무 어휘 1583 → 1179.
- 검사기 출력: #416 두 줄 사라짐(이미 있던 web 구역 `admin` 오탐 · 신고 꼴 `client`) · #562 · #518 · 후보 #448 · #425 목록 줄어듦 · naming · port-adapter 차이 0.
- 시간(옛 · 새 번갈아 3 회 평균): business-vocabulary 16.4 → 14.7s · broker-contract 27.8 → 25.5s · naming 20.2 → 14.6s · port-adapter-pairing 46.9 → 32.0s
  (ACL 가진 BC 마다 저장소 `rglob` 을 다시 하던 것이 없어짐). 느려지는 검사기 없음.

## 범위 밖(다음 판 후보)
- BC 마다 도는 검사기(`bc_dirs` → 채택 신호)가 `web/application/<단위>` · `web_test/application/<단위>` 도 서버 BC 로 돈다(현장 naming · port-adapter 에
  `web/` 줄이 있음). G2 · pre-gate 는 작업 트리 사본에서 숨김 경로만 빼므로 `web/` · `web_test/` 몫은 든다. 검사 대상 고르기라 pre-gate `_checker_bc` 와 함께 바꿔야 한다.
- #46 을 `web` 뿌리 import 까지 넓힐지.
