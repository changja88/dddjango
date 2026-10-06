# codex-dddjango-web — Codex 미러

`dddjango-web/`(Claude Code 플러그인)의 Codex 배포 미러. **지식 코퍼스(스킬 12종 `references/`)·`scripts/`·`assets/`는 Claude 배포본과 byte-exact 동일**하고(아래 «동기 절차»의 대조로 검사), 커맨드·에이전트는 Codex 실행 모델로 변환됐다.

## 구성

| Claude (`dddjango-web/`) | Codex (`codex-dddjango-web/skills/`) | 변환 |
|---|---|---|
| `commands/dddjango-web.md` | `dddjango-web/SKILL.md` | Coordinator → 사용자 트리거 스킬. scripts(백스톱 러너 — 빚 모드 `--debt-scan`·`--debt-residual`·치환 확인 `--subst-check` 포함 · 추출 도구 4 — extract_contract·extract_design·extract_dc·fetch_images와 그 의존 모듈 asset_io·design_sources·freeze_design · 공식 SDK 등재 도구 `sdk_vendor.py` · 리팩토링 판정 도구 `refactor_audit.py`) 동봉(`scripts/test/` 픽스처는 싣지 않는다) · `assets/sdk_boundary.js`(G2 공식 SDK 경계 확인 스니펫) 동봉 |
| `commands/refactor.md` | `dddjango-web-refactor/SKILL.md` + `agents/openai.yaml` | 리팩토링 입구 → 명시 호출 전용 스킬(`$dddjango-web-refactor <대상 단위> [불편 서술]` · `allow_implicit_invocation: false`). 표지 한 줄 `리팩토링 모드(입구 $dddjango-web-refactor) · 대상: <인자>`를 형제 Coordinator 스킬의 요청 첫 줄로 넘긴다 |
| `agents/<역할>-web.md` ×7 | `dddjango-web-<역할>-web/SKILL.md` ×7 | 서브에이전트 → 역할 스킬(코디네이터가 spawn_agent로 디스패치) |
| `skills/<스킬>/` ×12 | `dddjango-web-<스킬>/` ×12 | 그대로 복사(references — byte-exact). 단 **형제 플러그인(dddart·dddjango)과 이름이 겹치므로 12종 전부** 전역 이름 충돌 회피로 `dddjango-web-<스킬>/` 접두 폴더이며, SKILL.md의 `name`과 스킬 인용도 접두 표기다 |
| `REQUEST_GUIDE.md` | `REQUEST_GUIDE.md`(플러그인 루트 — `skills/` 밖) | byte 동일 미러(사람용 작업 요청 가이드 — 런타임 규범 밖. Claude·Codex 요청 방법을 한 문서에 함께 적는다) |

## 기능 축소표 (Claude → Codex)

| 기능 | Claude | Codex | 영향·완화 |
|---|---|---|---|
| 커맨드 인자 | `arguments` named + `argument-hint` | 스킬 1급 인자 **없음** | claude 위치 인자 `[feature, api_url]` → codex는 본문이 **순서대로 해석**(기능→API). **디자인은 인자 아님** — 양판 다 Phase 0에서 해소(Claude Design 시안·로컬 이미지·자체 설계). 사용 예시는 `default_prompt`/`defaultPrompt`로 표시 |
| 서브에이전트 | `Agent` 도구 + `agents/*.md` 자동 등록 | `spawn_agent`/`wait_agent`/`close_agent` (**`multi_agent` — 기본 on**) | 역할 정의를 `dddjango-web-<역할>-web` 스킬로 분리 — 코디네이터가 명령형으로 로드 지시. (드물게) multi_agent가 꺼져 있으면 안내 후 정지(단일 컨텍스트 역할극 금지) |
| 스킬 자동 주입 | 에이전트 frontmatter `skills:` | **없음** | 역할 스킬 본문의 "로드할 지식 스킬" 절이 대체 — 서브에이전트가 직접 로드 |
| 게이트 승인 UI | `AskUserQuestion`(선택지·multiSelect) | binary approve/deny뿐 | **평문 질문 파싱**으로 대체 — 배너 뒤 "승인하려면 '승인', 고치려면 …" + 번호 목록. 빚 질문·STOP·SDK 문항도 같은 평문 번호 목록 |
| 진행 가시성 | `TodoWrite` | `update_plan` | 동등 치환 |
| 이미지 입력 | `design-ref/` 이미지를 에이전트가 판독 | 판독 **비보장** | 함께 받은 HTML 시안(`.dc.html`)·텍스트 메모(`design-ref/notes.md`)를 시각 근거로 우선(이미지는 보조) |
| 디자인 엔진 | Claude Design 내장 `DesignSync`(claude.ai 로그인+design scope) | **세션 도구 목록에 `DesignSync`가 있을 때만** 가용(Codex 기본 도구셋에는 없다) | 미가용이면 사용자가 Claude Design에서 내려받은 시안 폴더(`.dc.html`·`_ds_manifest.json`·`tokens/*.css`·`screenshots/*.png`)의 로컬 경로를 받아 **같은 동결·추출 경로**(extract_design `--from-ds-manifest` → extract_dc → 화면 확인 게이트)를 탄다 |
| 플러그인 경로 변수 | `${CLAUDE_PLUGIN_ROOT}` | **미해석** | Coordinator 스킬은 `${SKILL_DIR}`(= `skills/dddjango-web/` — 실행 시 절대 경로로 편다)로, 역할 스킬은 "로드한 스킬 폴더의 references/"로 환언 완료. **코퍼스 references/ 안에 남은 `${CLAUDE_PLUGIN_ROOT}`는 byte-exact 불변식 때문에 의도된 잔존** — "이 스킬들이 설치된 플러그인 루트"로 읽는다(공유 reference는 `dddjango-web-discipline-houserules/references/undecidable.md`). references 안의 무접두 스킬 경로(`skills/discipline-houserules/…` 류)는 접두 폴더(`skills/dddjango-web-discipline-houserules/…`)로 해소해 읽는다 |
| 커맨드 호출 제어 | `/dddjango-web:dddjango-web`·`/dddjango-web:refactor`(refactor 는 `disable-model-invocation: true`) | Coordinator 스킬은 description 매칭으로 자가 트리거 가능 · 리팩토링 입구 스킬은 `allow_implicit_invocation: false` | description의 음성 트리거("단순 단일 파일 수정…에는 쓰지 않는다")로 오발동 완화 |
| 공식 SDK 경계 확인(G2) | Playwright MCP `page.context().route(…)`·`newCDPSession` | 가용 브라우저 채널의 컨텍스트 단위 가로채기·CDP 세션 | 채널이 없으면 해당 줄을 «미검증»으로 적는다(통과로 쓰지 않는다) |

## 동기 절차

references·scripts·assets·`REQUEST_GUIDE.md` 수정은 항상 **Claude 배포본(`dddjango-web/`)을 먼저 고친 뒤 codex로 복사**하는 경로다(codex 쪽 직접 수정 금지). 저장소 루트에서 drift 검사·해소:

```bash
# 검사 (출력 없음 = in-sync)
diff -rq --exclude=__pycache__ --exclude=test dddjango-web/scripts codex-dddjango-web/skills/dddjango-web/scripts
diff -rq dddjango-web/assets codex-dddjango-web/skills/dddjango-web/assets
for s in dddjango-web/skills/*/; do n=$(basename "$s"); diff -rq "$s/references" "codex-dddjango-web/skills/dddjango-web-$n/references"; done
cmp -s dddjango-web/REQUEST_GUIDE.md codex-dddjango-web/REQUEST_GUIDE.md || echo "REQUEST_GUIDE drift"

# 해소 (Claude 배포본 → codex)
rsync -a --delete --exclude=__pycache__ --exclude=test dddjango-web/scripts/ codex-dddjango-web/skills/dddjango-web/scripts/
rsync -a --delete dddjango-web/assets/ codex-dddjango-web/skills/dddjango-web/assets/
for s in dddjango-web/skills/*/; do n=$(basename "$s"); rsync -a --delete "$s/references/" "codex-dddjango-web/skills/dddjango-web-$n/references/"; done
cp dddjango-web/REQUEST_GUIDE.md codex-dddjango-web/REQUEST_GUIDE.md
```

커맨드·리팩토링 입구·역할 스킬·지식 스킬의 SKILL.md는 복사 대상 밖이다(plugin-native 단일 파일 — Claude판 수정 시 수동으로 재변환).
