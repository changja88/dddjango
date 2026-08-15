# dddart 이름 격리 수리 — 점검·수리 프롬프트 (dddart 저장소 세션에 붙여넣기용)

배경: 형제 플러그인 dddjango 에서 실측된 결함의 거울상을 수리한다. Claude Code 의 스킬 이름
공간은 플러그인 간 전역으로 합쳐지고, **무한정 이름은 동명 충돌 시 어느 플러그인 것이
로드될지 비결정**이다(자기 플러그인 우선 규칙 없음 — 공식: code.claude.com/docs/en/sub-agents
qualified syntax `plugin:skill`). 실측: dddjango 파이프라인의 Django coder 가 dddart 의
Flutter 하우스룰 stub 을 로드받았다. dddjango 쪽은 v2.10.0~2.11.0 에서 수리 완료.
실측 충돌 이름 — 스킬: `architecture-ddd`·`discipline-cleancode`·`discipline-houserules`·
`implementation-test`(+`discipline-tdd` 등 동명이면 추가) · 에이전트: `coder`·
`design-architect`·`design-review-ddd`·`discipline-reviewer`.

## 작업 (읽기 → 수리 → 검증 순 · 커밋은 최종 보고 후 지시받아)

1. **충돌 표면 실측**: 설치된 타 플러그인(특히 `~/.claude/plugins/cache/changja88-dddjango/`)의
   스킬·에이전트·커맨드 이름 목록과 이 저장소의 이름 교집합을 먼저 뽑아 보고에 남겨라.
2. **agents frontmatter 한정**: `agents/*.md` 전수의 `skills:` 항목을 `dddart:<스킬명>` 한정
   표기로 개정한다 — 충돌 여부 무관 **전 항목**(미래 충돌 원천 차단 · dddjango 동형).
3. **commands 디스패치 한정**: `commands/*.md`의 서브에이전트 호출 표기를 전부
   `dddart:<agent>` 꼴로 바꾸고, «서브에이전트 지정은 항상 한정 표기» 규약 1줄을 명문화한다.
4. **문면 인용 한정**: commands·agents 본문과 `skills/*/SKILL.md` description 의 충돌 스킬
   이름 인용을 `dddart:` 한정으로. (frontmatter preload 가 있는 agents 본문 인용은 저위험 —
   description·명시적 로드 지시가 우선 대상.)
5. **codex 미러가 있으면**: ⓐ 충돌 지식 스킬을 `dddart-` 접두 폴더로 개명(+frontmatter
   `name:`·역할 SKILL.md 로드 지시·미러 동기 도구의 경로 매핑 갱신 — dddjango 는
   corpus_mirror_sync 에 «접두 우선·무접두 fallback» 매핑으로 처리) ⓑ `${CLAUDE_PLUGIN_ROOT}`
   류 claude 전용 변수가 codex 문면에 잔존하는지 grep — 있으면 codex 규약 표기로 치환하고
   경로 해소 규칙 1문장을 병기.
6. **검증**: 저장소의 기존 검증 도구 전건 green + `claude plugin validate dddart --strict`
   통과. 개명이 있었으면 미러 동기 도구 재실행으로 경로 매핑 확인.
7. **보고**: 수리 목록(파일:행) + 검증 결과 표 + 잔여 위험. 커밋·릴리즈는 보고 후 지시받아.

불변식: 스킬 **내용**(references 정본)은 무접촉 — 이름·참조 «표기»만 바꾼다. 판정·규칙
의미 무변. 검증이 하나라도 red 면 원인을 보고하고 임의 우회하지 않는다.
