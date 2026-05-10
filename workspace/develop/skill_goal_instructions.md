# Skill Goal Instructions

이 문서는 dddjango 개별 skill 구현 goal에서 참조하는 실행 지침이다. Goal objective에는 짧은 목표와 이 파일 경로만 적고, 자세한 작업 규칙은 이 문서를 따른다.

## 범위

`workspace/develop/plan.md`의 2단계 개별 스킬 구현과 5단계 workflow skill 구현을 다룬다.

작성 대상은 다음 runtime 산출물이다.

- `dddjango/.codex-plugin/plugin.json`
- `dddjango/skills/<skill>/SKILL.md`
- `dddjango/skills/<skill>/agents/openai.yaml`
- `dddjango/skills/<skill>/references/*.md`
- 진행 상태 문서: `workspace/develop/plan.md`

이 프로젝트의 runtime target은 standalone Codex skill 위치인 `$CODEX_HOME/skills` 또는 `~/.codex/skills`가 아니다. 최종 산출물은 Codex에서도 동작하는 plugin-bundled skill이므로, 모든 runtime skill은 repo root의 `dddjango/skills/<skill>/` 아래에 생성한다. `dddjango/skills/.gitkeep`은 개별 skill 생성 전 빈 skills 디렉터리를 추적하기 위한 placeholder이며, 실제 skill 구현을 대체하지 않는다.

작성 중 검토 산출물은 다음 위치에 둔다.

- Source Coverage Crosswalk: `workspace/develop/eval/response/source-crosswalks/<skill>.md`

사용할 source 문서는 다음과 같다.

- 플러그인 구조: `workspace/docs/plugin-structure.md`
- skill 책임 계약: `workspace/docs/skill-contracts.md`
- skill 조합 관계: `workspace/docs/skill-hierarchy.md`
- frontmatter 입력: `workspace/docs/skill-authoring.md`
- reference mapping: `workspace/docs/reference-index.md`
- DDD 구현 표준: `workspace/docs/ddd-implementation-standard.md`
- workflow 계약: `workspace/docs/workflow.md`
- 검증 계획: `workspace/docs/validation-plan.md`
- source reference corpus: `workspace/reference`

`workspace/develop/eval/response/rubrics`는 초안 작성 source가 아니다. Rubric은 초안 작성과 source self-review가 끝난 뒤 평가와 개선 단계에서만 사용한다.

## 실행 규칙

- 문서는 반드시 한 skill씩 작성한다.
- 현재 skill이 completed, blocked, accepted-exception 중 하나가 되기 전에는 다음 skill을 시작하지 않는다.
- 이미 유효한 runtime 파일이 있으면 다시 쓰기 전에 먼저 리뷰하고, 필요한 부분만 수정한다.
- 초안 작성 단계에서는 `workspace/develop/eval/response/rubrics` 파일을 열지 않는다.
- 이전 대화나 context에 rubric 내용이 남아 있어도 runtime skill 문서의 작성 재료로 사용하지 않는다.
- Runtime skill 문서는 평가표가 아니라 실제 에이전트가 작업할 때 읽는 절차 문서로 작성한다.
- 각 skill이 completed, blocked, accepted-exception 중 하나가 되는 즉시 `workspace/develop/plan.md`를 갱신한다.
- 실제로 수행하지 않은 테스트, 검증, 리뷰, subagent 실행을 완료했다고 말하지 않는다.
- 실제 subagent를 실행한 경우에만 subagent review라고 부른다.
- 완료 상태는 의도가 아니라 파일 내용과 검증 결과를 다시 확인한 뒤에만 표시한다.

## 구현 순서

먼저 runtime plugin skeleton을 만든 뒤, `workspace/develop/plan.md`의 2단계 체크리스트 순서로 implementation skill을 구현하고, architecture skill과 workflow skill을 뒤에 둔다.

1. `dddjango/.codex-plugin/plugin.json`
2. `implementation-django`
3. `implementation-django-ninja`
4. `implementation-django-web`
5. `implementation-python`
6. `implementation-cleancode`
7. `implementation-tdd`
8. `implementation-test`
9. `architecture-ddd`
10. `architecture-implementation-patterns`
11. `architecture-db`
12. `architecture-api`
13. `workflow-dddjango-subagents`

순서를 바꿀 수 있는 경우:

- 특정 skill의 source reference gap을 먼저 메워야 하는 경우
- user가 명시적으로 특정 skill을 먼저 요청한 경우
- 앞선 skill이 blocked되어 다음 독립 skill로 넘어가야 하는 경우

순서를 바꾼 경우 이유를 완료 보고에 남긴다.

## Skill별 작성 루프

각 skill은 다음 순서를 반복한다.

1. `workspace/docs/skill-contracts.md`에서 skill 책임과 경계를 확인한다.
2. `workspace/docs/reference-index.md`에서 source reference와 source gap을 확인한다.
3. 필요한 `workspace/reference/**/final.md`만 읽는다. `internal.md`, `external.md`, `review.md`는 `final.md`가 애매할 때만 읽는다.
4. `workspace/docs/skill-authoring.md`에서 frontmatter 입력과 agents metadata 입력을 확인한다.
5. `workspace/docs/plugin-structure.md`의 Runtime Reference Split Plan을 기본 파일명과 책임 경계로 삼아 해당 skill의 runtime reference split을 설계한다.
6. Source Coverage Crosswalk를 작성한다.
7. Rubric을 열지 않고 `SKILL.md`, `references/*.md`, `agents/openai.yaml` 초안을 작성한다.
8. Source 문서 기준 self-review를 수행한다.
9. Source self-review finding을 `blocking`, `major`, `minor`로 분류한다.
10. Source self-review finding이 0개가 될 때까지 수정한다.
11. 그 다음에만 해당 rubric과 `common_rubric.md`를 열어 평가 기준과 비교한다.
12. Rubric review finding을 분류하고, runtime 문서 수정 대상인지 평가 자료 수정 대상인지 구분한다.
13. Runtime 문서 finding이 0개가 될 때까지 수정과 리뷰를 반복한다.
14. 구조 검증과 관련 문서 검증을 실행한다.
15. `workspace/develop/plan.md`를 갱신한다.

Rubric과 source가 충돌하면 source 문서를 우선한다. 충돌이 실제로 존재하면 runtime 문서를 source 기준으로 유지하고, 충돌 내용을 보고한다.

### Source Coverage Crosswalk

Crosswalk는 source reference의 모든 heading과 runtime 작업에 관련된 세부사항을 runtime skill에 어떻게 반영했는지 추적하기 위한 작성 중 산출물이다. 기본 위치는 `workspace/develop/eval/response/source-crosswalks/<skill>.md`이며, runtime skill 폴더 안에는 두지 않는다.

각 skill마다 다음을 남긴다.

- 사용한 source 문서 목록
- source 문서의 `##` heading 전체
- runtime 규칙, reference 내용, skill boundary, 또는 명시적 제외 판단에 영향을 주는 `###` heading
- 각 heading의 처리 상태: `included`, `merged`, `delegated-to-other-skill`, `omitted`, `source-gap`
- 반영 위치: `SKILL.md` section, runtime `references/*.md` 파일명, 또는 관련 skill 이름
- 제외 또는 병합 이유

Crosswalk 기준:

- `included`: 해당 주제가 runtime `SKILL.md` 또는 `references/`에 직접 반영됨
- `merged`: 별도 heading은 없지만 더 넓은 runtime reference 주제 안에 반영됨
- `delegated-to-other-skill`: 해당 skill 책임 밖이며 다른 skill의 책임 계약에 속함
- `omitted`: runtime 작업에 필요 없거나 일반 지식이라 제외함. 이유를 반드시 남김
- `source-gap`: 전용 source가 부족해 provisional 처리 또는 fallback source가 필요함

Source self-review를 시작하기 전에 `unreviewed`나 빈 처리 상태가 없어야 한다. `omitted`와 `merged`는 source 내용이 누락되지 않았음을 설명할 수 있을 때만 사용한다.

## SKILL.md 작성 규칙

각 `SKILL.md` frontmatter에는 `name`과 `description`만 둔다.

`description` 규칙:

- Codex가 skill을 사용할지 판단하는 trigger 전용 문장으로 작성한다.
- 어떤 요청에서 이 skill을 써야 하는지 포함한다.
- 관련 skill과의 경계, 우선해야 하는 다른 skill, anti-trigger를 간결하게 포함한다.
- Workflow 요약, 단계 나열, scoring 기준, 평가 문구를 넣지 않는다.
- 한국어 사용자 요청과 한영 혼합 개발자 표현을 trigger로 인식할 수 있게 핵심 한국어 표현을 포함한다.

본문 규칙:

- 핵심 절차, reference loading 기준, 반드시 지킬 runtime 규칙, 관련 skill boundary, 금지 행동만 둔다.
- `SKILL.md` body는 짧게 유지한다. 긴 설명은 `references/`로 분리한다.
- 모든 runtime reference 파일은 `SKILL.md`에서 직접 링크한다.
- 깊은 중첩 reference를 만들지 않는다.
- 명령형으로 작성한다.
- 일반 지식이나 Codex가 이미 아는 내용을 장황하게 설명하지 않는다.
- 실행하지 않은 테스트나 검증을 통과했다고 말하지 말라는 규칙을 포함한다.
- Rubric의 hard gate id, scenario tag, scoring 표현을 runtime 문서에 그대로 넣지 않는다. Source와 제품 문서에서 필요한 규칙만 자연스러운 `must`/`never` 문장으로 바꾼다.

본문에 넣지 않을 내용:

- rubric prompt family
- expected routing
- expected answer
- private grader key
- scoring note
- hidden failure criteria
- 평가표의 문장을 그대로 옮긴 checklist
- README, installation guide, changelog 성격의 설명

## Runtime Reference 작성 규칙

`dddjango/skills/<skill>/references/`에는 해당 skill이 실제 작업 중 필요할 때 읽을 세부 지식을 둔다.

- `workspace/reference/**/final.md`를 그대로 복사하지 않는다.
- Skill이 실제로 읽을 주제 단위로 요약하거나 분할한다.
- 기본 파일명과 분할 단위는 `workspace/docs/plugin-structure.md`의 Runtime Reference Split Plan을 따른다.
- 파일명을 바꾸거나 reference를 합치거나 나누면 Crosswalk와 완료 보고에 deviation reason을 남긴다.
- 각 reference는 한 단계 아래에 둔다.
- 100줄을 넘는 reference에는 상단에 간단한 목차를 둔다.
- `SKILL.md`와 reference 사이에 같은 내용을 중복하지 않는다.
- DRF 내용은 legacy review, DRF-to-Django-Ninja migration, compatibility, comparison 범위로만 둔다.
- 신규 API 구현 기준은 Django Ninja로 둔다.

`references/`로 분리할 내용:

- 긴 비교표
- framework-specific detail
- migration rollout 절차
- API error format 예시
- testing fixture 또는 double 선택 기준
- architecture pattern 선택 기준
- workflow role map과 handoff contract

## Agents Metadata 작성 규칙

`agents/openai.yaml`은 최종 `SKILL.md`를 기준으로 작성하거나 갱신한다.

- `workspace/docs/skill-authoring.md`의 `Agents Metadata Inputs`를 출발점으로 사용한다.
- `display_name`, `short_description`, `default_prompt`가 `SKILL.md`의 책임과 일치해야 한다.
- Optional interface field는 user가 명시적으로 제공한 경우에만 추가한다.
- Provisional skill의 metadata는 전용 source reference가 있는 것처럼 과장하지 않는다.

## 한국어 사용자 기준

dddjango plugin은 한국어 사용자를 우선 고려한다.

- Runtime skill의 trigger와 boundary에는 자연스러운 한국어 개발자 표현을 반영한다.
- 한국어/영어 혼합 표현을 고려한다. 예: `Django Ninja로 주문 API`, `쿠폰 정책 TDD`, `상태 컬럼 backfill`, `ViewSet을 Ninja로 전환`.
- Section heading, skill name, canonical technical term은 영어를 유지할 수 있다.
- 코드, class, function, package, protocol 이름은 번역하지 않는다.
- 한국어 예시는 user-facing trigger 이해를 돕는 범위에서만 사용한다.
- 단순 작업에 DDD, workflow, subagent를 과적용하지 않는 boundary를 반드시 둔다.

## Provisional Skill 처리

다음 skill은 전용 source reference가 부족한 provisional skill이다.

- `architecture-implementation-patterns`
- `implementation-django-ninja`
- `implementation-django-web`

Provisional skill 작성 규칙:

- 작성 전에 `source policy decision`을 남긴다: `create-dedicated-source`, `block-until-source-exists`, `allow-provisional-with-fallback` 중 하나를 선택한다.
- 전용 source reference가 부족하다는 점을 body 또는 reference에 명시한다.
- 어떤 fallback source를 사용했는지 명시한다.
- 완성된 전용 source가 있는 것처럼 표현하지 않는다.
- `agents/openai.yaml`에서도 provisional 상태를 과장 없이 반영한다.
- `allow-provisional-with-fallback`을 선택한 경우 completed 조건은 source limitation과 fallback 범위가 명시됐는지로 판단한다.
- Provisional 상태 때문에 completed 조건을 만족할 수 없으면 accepted-exception 또는 blocked로 기록한다.

## Cross-Skill Routing 기준

복합 작업에서 충돌하면 `workspace/docs/skill-hierarchy.md`와 `skill-contracts.md`를 기준으로 판단한다.

기본 판단:

- 단순 CRUD, 단일 파일 수정, 이미 판단이 끝난 작은 구현은 관련 implementation skill로 직접 처리한다.
- 도메인 규칙, 상태 전이, 정책, 불변식, bounded context가 불명확하면 `architecture-ddd` 판단을 먼저 둔다.
- DB schema, transaction, locking, rollout constraint는 `architecture-db`가 설계하고 `implementation-django`가 migration 구현을 맡는다.
- REST API contract는 `architecture-api`가 설계하고 `implementation-django-ninja`가 구현한다.
- Django template/static/frontend 책임은 `implementation-django-web`이 맡는다.
- TDD 흐름 자체는 `implementation-tdd`, pytest fixture/mock/factory 세부 구현은 `implementation-test`가 맡는다.
- Clean code review와 refactoring 판단은 `implementation-cleancode`가 맡되, Python/Django 세부 구현에는 관련 implementation skill을 함께 고려한다.
- `workflow-dddjango-subagents`는 복합적이거나 위험한 Django/DDD 작업, 또는 user가 subagent/역할 분해를 명시한 경우에 사용한다.

금지:

- 단순 필드 rename이나 작은 Django 구현에 workflow skill을 강제하지 않는다.
- 모든 Django 작업에 DDD tactical pattern을 강제하지 않는다.
- 신규 greenfield API에 DRF `Serializer`, `ViewSet`, `APIView`, `DefaultRouter`를 표준으로 권장하지 않는다.
- Router, view, template에 핵심 비즈니스 규칙을 두라고 안내하지 않는다.

## Review 기준

Source self-review와 rubric review 모두 다음 관점으로 수행한다.

- skill authoring과 progressive disclosure integrity
- dddjango product/docs alignment
- routing, reference, protocol correctness
- Korean user coverage와 한영 혼합 trigger correctness
- anti-overapplication과 simple-case boundary
- Source Coverage Crosswalk completeness

Finding 분류:

- `blocking`: 필수 runtime 파일 누락, frontmatter 규격 위반, public/private eval leakage, source와 정면 충돌, provisional misrepresentation, false validation/subagent claim
- `major`: trigger 또는 anti-trigger 불명확, reference loading 기준 부족, source heading의 반영 또는 제외 근거 누락, skill responsibility conflict, 한국어 trigger coverage 부족, workflow/DDD 과적용 위험
- `minor`: 표현 개선, 예시 보강, 중복 정리, reference 링크 명확화, metadata 문구 개선

일반적인 minor finding은 accepted exception으로 넘기지 않는다. 표현 개선, 예시 보강, 중복 정리, metadata 명확화 같은 minor는 수정한 뒤 다시 리뷰한다.

Rubric review finding은 먼저 다음 중 하나로 분류한다.

- `source-backed runtime issue`: `workspace/docs` 또는 `workspace/reference`에도 근거가 있으므로 runtime 문서를 수정한다.
- `eval-only calibration issue`: 평가 prompt, grader key, scoring 문구 문제이므로 runtime 문서에 반영하지 않는다.
- `rubric defect`: rubric이 source와 충돌하거나 과도한 요구를 하므로 충돌 내용을 보고한다.
- `accepted trade-off`: source limitation 또는 명시적 제품 결정 때문에 runtime 문서를 바꾸지 않는다. 이유를 남긴다.

Runtime 문서는 `source-backed runtime issue`만 반영한다. Rubric의 prompt family, expected route, hidden failure criteria, scoring note, calibration sample 문장을 runtime 문서에 복사하지 않는다.

## Completed 조건

각 skill은 다음 조건을 모두 만족하면 completed로 본다.

- 필수 runtime 파일이 존재한다.
- `SKILL.md` frontmatter가 `name`과 `description`만 포함한다.
- `description`이 trigger/routing 조건 중심이고 workflow 요약이 아니다.
- `SKILL.md`가 concise하고 progressive disclosure 구조를 따른다.
- 필요한 runtime reference가 `SKILL.md`에서 직접 링크된다.
- Source Coverage Crosswalk의 모든 source heading이 `included`, `merged`, `delegated-to-other-skill`, `omitted`, `source-gap` 중 하나로 처리되어 있고 이유가 남아 있다.
- Runtime reference split이 `workspace/docs/plugin-structure.md`의 기본 계획을 따르거나 deviation reason이 기록되어 있다.
- `agents/openai.yaml`이 `SKILL.md`와 의미적으로 일치한다.
- Runtime 문서에 rubric/private grader 정보가 섞이지 않았다.
- Source 문서와 충돌하지 않는다.
- 한국어/한영 혼합 trigger와 anti-trigger가 반영되어 있다.
- 단순 작업에 DDD, architecture, workflow, subagent를 과적용하지 않는 boundary가 있다.
- Provisional skill은 source limitation과 fallback source를 명시한다.
- Provisional skill은 `source policy decision`이 기록되어 있다.
- Source self-review finding이 0개다.
- Rubric review의 blocking, major, minor finding이 0개다.
- 실행한 검증 명령이 통과했거나, 실행하지 못한 명령과 이유가 명확히 보고되어 있다.

Source limitation, docs conflict, 상위 지침 충돌 때문에 completed 조건을 만족할 수 없으면 `plan.md`에 blocked 또는 accepted-exception으로 기록하고 이유를 남긴다.

## 검증

Skill 구현 중 가능한 검증:

- `rg -n "^---$|^name:|^description:" dddjango/skills/<skill>/SKILL.md`
- `rg -n "README|INSTALLATION|CHANGELOG|expected routing|grader key|scoring note" dddjango/skills/<skill>`
- `find dddjango/skills/<skill> -maxdepth 3 -type f | sort`

최종 점검에서 다음을 수행한다.

- `python3 workspace/scripts/validate_skill_docs.py --phase docs`
- `python3 workspace/scripts/validate_skill_docs.py --phase generated --skills-dir dddjango/skills`
- `python3 workspace/scripts/validate_skill_docs.py --phase all --skills-dir dddjango/skills`
- `git diff --check -- dddjango workspace/develop/plan.md workspace/develop/eval/response/source-crosswalks`
- 필요한 경우 `wc -l dddjango/skills/*/SKILL.md`

설치된 runtime cache를 보정한 경우 `python3 workspace/scripts/validate_skill_docs.py --phase runtime`도 실행한다. Runtime smoke는 완료 게이트가 아니며, 실제 skill folder 생성 후 완료 판단은 `--phase all --skills-dir dddjango/skills` 결과를 우선한다.

실행한 명령, 실행하지 못한 명령, 실행하지 못한 이유를 보고한다. 실행하지 않은 검증을 완료했다고 보고하지 않는다.

## 완료 보고

완료 보고에는 다음을 포함한다.

- completed, blocked, accepted-exception skill 목록
- skill별 수정 파일 목록
- source self-review와 rubric review 요약
- Source Coverage Crosswalk 요약과 남은 `omitted`, `source-gap`, deviation reason
- 남은 finding이 없는지, 또는 blocked/accepted-exception의 source limitation
- 검증 결과
- `plan.md` 갱신 내용
- 실제 subagent를 사용했는지 여부
- Serena 사용 여부 또는 생략 이유

## Goal Objective Template

```text
dddjango 개별 스킬 구현을 진행한다.

자세한 실행 지침은 `workspace/develop/skill_goal_instructions.md`를 따른다.
초안 작성 중에는 rubric을 참고하지 말고, `workspace/docs`와 `workspace/reference`를 source of truth로 사용한다.
각 skill은 source 기반 초안 작성, source self-review, rubric 기반 검수, 수정 반복을 거쳐 blocking/major/minor finding이 0개가 된 뒤 완료 처리한다.
```
