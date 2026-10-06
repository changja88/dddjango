# dddjango-web 2.1.0 짓기 — 결정 · 소유 (lead · 10-06 13:0x)

## 바탕
- 바탕: 배포된 2.0.0(R main `168b014e`) — `<S>/web-new2/dddjango-web/` · `codex-dddjango-web/` 에 `git archive` 로 풀어 둠(= web-new 얼린 판 + 매니페스트 2.0.0). 여기서 고친다. 매니페스트 version 은 2.0.0 그대로(길 A — 배포 때 minor → 2.1.0).
- 옮길 원본: v1.3.1 판 `<S>/web-new/head/dddjango-web/`(= `git show 0cdb10f5:…`) — 읽기만.
- 2.0.0 의 규약 · 이름은 `<S>/web-new/mapping.md` · `<S>/web-new/build-log.md`(§12 · §13 포함) · `web-new/review/fix-plan-r1.md` · `fix-plan-r2.md` 가 정한다. 그 위에 셋을 더한다.
- 사용자 결정(바꾸지 않음): 09-26 B1 «빚은 예외 없이 항상 먼저 정리» · 10-05 «빚 정리 = 손대는 파일 + 부르는 곳» · 리팩토링 정의는 v1.3.1 그대로 «동작 불변»(2.0.0 영구 테스트는 그대로 통과해야 함 · dddjango 코어의 새 정의는 넣지 않음) · 시안 기계 검사 · 정확값 토큰 · REQUEST_GUIDE 는 되살리지 않음.

## 셋 — 일꾼 · 소유
| | 일 | 일꾼 | 혼자 쓰는 파일(새로 만들거나 이 일꾼만 고침) |
|---|---|---|---|
| X1 | 빚 정리 — G0 빚 스캔 · 빚 질문(ⓐ · ⓑ · ⓐ′) · 슬라이스 0(동작 불변 정리) · 기존 테스트 기준선 · G2 남은 빚 판정(`--debt-residual`) · 치환 확인(`--subst-check`) | ④(scripts 를 지은 일꾼) | `scripts/src/debt.py` · `scripts/src/subst.py` · `scripts/backstop.py` · `scripts/src/common.py` · `scripts/src/check_{imports,naming,cycles,tests,models}.py` · `scripts/test/fixtures_debt.sh` · `scripts/test/fixtures_subst.sh` |
| X2 | 외부 JS 승인 절차 — `sdk_vendor.py` · `src/sdk_registry.py` · `src/check_vendor.py`(WV 패밀리) · `assets/sdk_boundary.js` · G1 SDK 별도 문항. 2.0.0 의 «coder 가 버전 고정 파일을 `web/static/vendor/<라이브러리>/<버전>/`» 길을 이 절차로 바꿈 · htmx 고정 판은 그대로 | ③(implementation-* 를 지은 일꾼) | `scripts/sdk_vendor.py` · `scripts/src/sdk_registry.py` · `scripts/src/check_vendor.py` · `assets/sdk_boundary.js` · `scripts/src/check_{structure,project,purity}.py` 의 vendor · CDN 부분 · `scripts/test/fixtures_sdk.sh`(+ 필요한 보조 `sdk_fixture.py` 등) |
| X3 | 리팩토링 입구 — `commands/refactor.md`(`/dddjango-web:refactor` · Codex `$dddjango-web-refactor`) · Coordinator 리팩토링 모드 R0~R3 · `refactor_audit.py` · UNIT_AUDIT · 의미 항목 판정 모드. 단위 = 새 트리의 BC(area 포함) | ①(Coordinator · 에이전트를 지은 일꾼) | `commands/refactor.md` · `scripts/refactor_audit.py` · `scripts/test/fixtures_refactor_audit.sh`(+ 필요한 보조) |
| C | Codex 판 — 셋을 같은 대응으로(접두 `dddjango-web-*` · 리팩토링 입구는 `skills/dddjango-web-refactor/`) | ⑤ | `codex-dddjango-web/**` — X1~X3 가 끝난 뒤 |
| R | 깨끗한 사본 `<S>/web-rel2`(R main `168b014e` 를 `git clone --shared`) — 넣기 · 문서(AGENTS.md · DEVELOPMENT.md · README) · 검증 · 커밋 | ⑥ | `<S>/web-rel2/**` |
| lead | 이 문서 · `web-new2/build-log.md` · `scripts/test/run_fixtures.sh` 끝의 이어 부르기 줄 · 검증 | | |

## 같이 쓰는 파일 — 규칙
- `commands/dddjango-web.md` · `agents/*.md` · `skills/**/*.md` 는 셋이 같이 고친다. **Edit 도구로만 고친다** — Write · sed · 파이썬 덮어쓰기 금지. 고치기 바로 앞에 그 파일을 다시 Read 한다(다른 일꾼이 바꿨을 수 있음 · Edit 이 «파일이 바뀜» 으로 실패하면 다시 Read 하고 다시 한다). 자기 주제 문단만 고치고, 남의 주제 문단은 고치지 않는다(필요하면 그 일꾼에게 SendMessage — lead 를 거쳐도 됨).
- 절 번호를 바꾸지 않는다. 새 절이 필요하면 맨 뒤에 붙인다.
- `scripts/backstop.py` · `common.py` 는 X1 소유. X2 의 WV 패밀리는 `src/check_vendor.py` 가 `run_vendor(ctx) -> list[Finding]` 과 `VENDOR_CHECK_IDS: tuple[str, ...]` 를 내보내고, X1 이 backstop 의 `FAMILIES` 에 `wv` 를, `CHECK_IDS` 에 `VENDOR_CHECK_IDS` 를 더한다(검사 수는 `len(CHECK_IDS)` 그대로 단일 출처). X2 가 common 에 필요한 것은 자기 모듈 안에 둔다(못 하면 X1 에 요청).
- 새 검사는 자기 픽스처 파일로 막는다. lead 가 `run_fixtures.sh` 끝에서 세 픽스처 파일을 이어 부른다(일꾼은 run_fixtures.sh 를 고치지 않음 — 단 X1 은 backstop 러너 옵션 때문에 F7 류 사용 오류 픽스처가 필요하면 자기 `fixtures_debt.sh` 에 둔다).
- 검사 ID: 새 패밀리 WV(외부 JS) 는 v1.3.1 번호를 쓰되 옮길 수 없는 번호는 비운다. 빚 · 치환은 새 검사 ID 가 아니라 러너 모드(`--debt-scan` · `--debt-residual` · `--subst-check`)다(v1.3.1 처럼). 2.0.0 의 PJ3(vendor `<라이브러리>/<버전>/`)는 X2 가 새 절차에 맞춰 바꾸거나 비운다.

## 일꾼 공통 금지(W3 지시서 그대로)
- 쓰는 곳은 `<S>/web-new2/` 아래 자기 소유 · 같이 쓰는 파일뿐(⑥ 만 `<S>/web-rel2/`). 저장소 R(`/Users/hyun/Desktop/dddjango`) · `/Users/hyun/Desktop/dddart` · spring_dream_server · `~/.herdr/worktrees/**` 는 읽기만. git 은 `GIT_OPTIONAL_LOCKS=0` 읽기 명령(log · show · diff · archive · ls-tree · ls-files)만 · `git status` 금지 · 커밋 · push · 배포 금지(⑥ 의 사본 안 커밋만 예외).
- 열지 않는 곳: `<S>/rq-p0/**` · `<S>/rq-p0r/**` · `<S>/p0-ops/**` · `<S>/web-discard-1006/**` · `<S>/w4/**`(W4 사본 — 운영자가 따로 씀) · `~/.dddjango-testbed/**` · 하네스 tool-results · 서브에이전트 output JSONL · `~/.claude/settings.json` · `.claude/settings.local.json` · `~/.codex/config.toml`.
- Serena · Graphify 금지 · 하위 에이전트 금지 · 검토 바퀴 · 안전 도구 · 채점 도구 · 판정기 새로 만들지 않음 · md 는 Write/Edit 로만(셸 heredoc 금지 — 같이 쓰는 md 는 Edit 만) · 시각은 `date` 출력만 · 어림은 [추정].
- 끝나면: 고친 · 만든 파일(파일:줄) · 바이트 · 검사 ID 변화 · 픽스처 결과 · «2.0.0 · v1.3.1 과 달라진 곳 — 까닭» · `date` 를 보고.

## 결정 덧(13:1x)
- 검사 수 84종 = 72 − PJ3(X2 가 비움 — vendor 버전 폴더 길이 등재 절차로 바뀜) + WV13(WV1~WV13 · 비운 번호 없음). `check_vendor.py` 가 `run_vendor(ctx, debt=False, design_build=None, always_only=False)` · `VENDOR_CHECK_IDS` · `UNDEFERRABLE` · `VendorUndecidable`(→ backstop exit 1) 를 내보냄.
- 리팩토링 · 빚(ⓐ′) 단위 목록(v1.3.1 단위 목록의 1:1 — v1.3.1 «영역» 자리가 BC): BC `web/application/[<area>/]<bc>`(미러 CSS · 그 BC 만 참조하는 정적 파일 포함) · `web/root` · `web/common` · `web/design_system` · `web/static/<칸>`(js · images · fonts · htmx — vendor 제외) · 컨테이너 `web/*.py` · 표준 트리 밖 옛 배치 최상위 폴더 `web/<옛 폴더>`.
- debt.py 가 refactor_audit 에 내보내는 9개 이름 · debt JSON 스키마는 v1.3.1 그대로. 개명 · 이동 묶음 = ST0~ST3 · ST5~ST12 · NM1 · NM2 · NM3 · NM5 · NM6 · NM12 · NM15 · NM19 · NM20 · 편집 줄 키 = IM · PU.
- 일꾼 주소: X1 ④ `a275e6b8bcd5d4484` · X2 ③ `a3dcc256802a6458f` · X3 ① `abc519b6834a5ac0c`.

## 덧 X6 · X7(운영자 발주 13:26 뒤 · 발주서 `web-new2/brief-X6-X7.md`)
| | 일 | 일꾼 | 혼자 쓰는 파일 |
|---|---|---|---|
| X6 | web 작업 요청 가이드 새로 쓰기(2.1.0 동작 · 8절 · 런타임별 디자인 출처) | ⑦ `abb65edd65068050c`(새로 띄움) | `dddjango-web/REQUEST_GUIDE.md` · `codex-dddjango-web/REQUEST_GUIDE.md`(byte 동일) · 두 매니페스트 `homepage` · Codex `websiteURL` |
| X7 | Claude 판 Coordinator 에 «Claude Design 에서 내려받은 시안 폴더» 갈래(Codex 판과 같은 뜻) | ⑤ `a3d878f2f823e6181` | 없음 — `commands/dddjango-web.md` 는 같이 쓰는 파일(Edit 로만) |
- 저장소 쪽(request_guide_contract `GUIDE_PLUGINS` 에 dddjango-web 다시 넣기 · README 표 · README 61줄 · DEVELOPMENT.md)은 ⑥ 이 web-rel2 diff 로 · `codex-dddjango-web/README.md` 가이드 한 줄은 ⑤ 가 Codex 판 옮길 때.

## 변경 — X6 빠짐(운영자 13:4x · 사용자 13:38:12 뒤 · 13:40:24 앞)
- 사용자 원문: «그럼 우선 발주 가이드 문서만 추가해서 배포하자. 발주 가이드는 전면 재작성해야해. … web 플러그인 분석해서 … 필수 제공 요소를 확인하고 발주 가이드 재작성해줘. 그럼 내가 확인하고 문제 없으면 추가배포하자».
- **X6(가이드)는 2.1.0 에서 뺀다** — 운영자가 따로 띄우는 가이드 lane 이 2.0.0 기준으로 전면 새로 쓰고, 사용자 확인 뒤 **2.0.1(가이드만)** 로 먼저 배포한다. 일꾼 ⑦ 멈춤(초안은 지우지 않음). 저장소 쪽 가이드 변경(request_guide_contract `GUIDE_PLUGINS` · README 표 · 매니페스트 homepage · websiteURL · codex README)은 ⑥ 의 web-rel2 diff 와 ⑤ 의 Codex 판에서 뺀다.
- X7 은 2.1.0 에 그대로.
- 2.1.0 은 2.0.1 배포 뒤 그 위로 다시 얹는다 — 얼림 때 운영자가 기준 커밋을 알려 준다. 2.1.0 의 셋(빚 정리 · 리팩토링 입구 · 외부 JS 승인)을 배포된 가이드에 몇 줄 더하는 일은 남겨 둔다.
