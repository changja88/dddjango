# dddjango 플러그인 개발 제약 규칙

이 문서는 플러그인 개발 중 반드시 지킬 제약만 다룬다. 실행 순서는 [master_plan.md](/Users/hyun/Desktop/dddjango/workspace/plan/master_plan.md)에 둔다.

## 1. 개선 분석과 개선 계획 위치

사람이 작성하는 개선 분석과 개선 계획은 작업 성격에 맞는 `*_lv_up_plan` 폴더 아래에만 둔다.

분류 기준:

| 분류 | 의미 | 분석 위치 | 계획 위치 | 허용 `수정 대상:` |
|---|---|---|---|---|
| skill | runtime skill, skill routing, bundled reference, skill 간 책임 개선 | `workspace/plan/skill_lv_up_plan/<skill-name>/analysis/` | `workspace/plan/skill_lv_up_plan/<skill-name>/plan/` | `skill`, `runtime-sync` |
| reference | source reference, provenance, source gap, reference conflict 개선 | `workspace/plan/reference_lv_up_plan/<reference-area>/analysis/` | `workspace/plan/reference_lv_up_plan/<reference-area>/plan/` | `reference` |
| eval | eval case, answer oracle, evaluator, report, eval runner 개선 | `workspace/plan/eval_lv_up_plan/<bucket>/analysis/` | `workspace/plan/eval_lv_up_plan/<bucket>/plan/` | `case`, `answer`, `evaluator`, `report`, `model-variance` |
| etc | 위 세 범주에 속하지 않는 개발 프로세스, 정리, 운영성, 기타 도구 개선 | `workspace/plan/etc_lv_up_plan/<topic>/analysis/` | `workspace/plan/etc_lv_up_plan/<topic>/plan/` | `process`, `cleanup`, `tooling`, `none` |

폴더 단위:

| 폴더 | 하위 그룹 기준 | 예시 |
|---|---|---|
| `skill_lv_up_plan` | 실제 skill 폴더명 | `architecture-api`, `implementation-django`, `workflow-dddjango-subagents` |
| `reference_lv_up_plan` | `workspace/reference/<reference-area>/` 폴더명 | `architecture-db`, `implementation-test` |
| `eval_lv_up_plan` | eval bucket 이름 | `code`, `plugin`, `response`, `runtime`, `source`, `workflow` |
| `etc_lv_up_plan` | 소문자 topic 이름 | `cleanup-process`, `plan-constraint` |

제약:

- 분석 문서는 해당 범주의 `analysis/` 아래에만 작성한다.
- 개선 계획 문서는 해당 범주의 `plan/` 아래에만 작성한다.
- P1 점검은 source reference 충분성과 skill 반영도를 함께 확인한다.
- P1에서 reference 자체가 부족하다고 판정하면 `reference_lv_up_plan/<reference-area>/analysis/`에 분석을 작성하고, `reference_lv_up_plan/<reference-area>/plan/`에 reference 개선 계획을 작성한다.
- P1에서 reference는 충분하지만 skill 반영이 부족하다고 판정하면 `skill_lv_up_plan/<skill-name>/analysis/`에 분석을 작성하고, `skill_lv_up_plan/<skill-name>/plan/`에 skill 개선 계획을 작성한다.
- P1에서 runtime cache 동기화 문제가 있으면 `skill_lv_up_plan/<skill-name>/analysis/`에 분석을 작성하고, `skill_lv_up_plan/<skill-name>/plan/`에 runtime sync 계획을 작성한다.
- P1에서 수정 대상이 없으면 해당 점검 대상의 `analysis/`에만 근거를 남기고 `plan/` 문서는 만들지 않는다.
- P1에서 `plan/` 문서를 작성한 경우, 개선 방법, 수정 순서, 검증 방법, 완료 조건을 포함하고 독립 리뷰를 반복해 Blocker 0, Major 0, 열린 Minor 0 상태로 닫는다.
- skill 분석과 계획은 반드시 대상 skill 이름을 기준으로 작성한다.
- `skill_lv_up_plan` 하위에는 `dddjango/skills/<skill-name>/`에 실제로 존재하는 skill 이름만 둔다.
- `code`, `plugin`, `response`, `runtime`, `source`, `workflow` 같은 eval bucket 이름은 `skill_lv_up_plan` 하위 그룹으로 쓰지 않는다.
- reference 분석과 계획은 반드시 대상 reference area 이름을 기준으로 작성한다.
- reference area는 `workspace/reference/<reference-area>/`의 폴더명이며, reference 자체의 부족, provenance gap, source conflict, fallback/provisional 보강은 `reference_lv_up_plan/<reference-area>/`에 작성한다.
- eval 분석과 계획은 반드시 대상 bucket 이름을 기준으로 작성한다.
- `eval_lv_up_plan` 하위에는 `code`, `plugin`, `response`, `runtime`, `source`, `workflow` bucket만 둔다.
- skill 이름은 `eval_lv_up_plan` 하위 그룹으로 쓰지 않는다.
- etc 분석과 계획은 반드시 topic 이름을 기준으로 작성한다.
- 분석과 계획은 같은 try 번호, run id, topic, 또는 case id를 파일명이나 본문에 남긴다.
- 계획 문서가 있으면 같은 파일명의 분석 문서가 있어야 한다.
- `analysis/`와 `plan/` 바로 아래에만 `.md` 파일을 둔다.
- `review/`, `notes/`, `draft/` 같은 별도 분류 폴더를 만들지 않는다.
- `skill_lv_up_plan`에는 skill 개선 분석/계획만 둔다.
- `reference_lv_up_plan`에는 reference 개선 분석/계획만 둔다.
- `eval_lv_up_plan`에는 eval pack, evaluator, report 개선 분석/계획만 둔다.
- `etc_lv_up_plan`에는 세 전용 폴더로 분류할 수 없는 개선 분석/계획만 둔다.

금지 위치:

```text
dddjango/skills/**
workspace/reference/**
workspace/develop/eval/**/cases/**
workspace/develop/eval/**/answer/**
workspace/develop/eval/**/fixtures/**
workspace/develop/eval/**/runs/**
workspace/develop/eval/**/latest/**
workspace/develop/eval/**/latest-valid/**
```

예외:

- 평가 도구가 자동 생성하는 `workspace/develop/eval/<bucket>/runs/<run-id>/analysis/`는 실행 증거물이다.
- 자동 생성 증거물은 사람이 작성하는 개선 분석/계획으로 취급하지 않는다.
- 자동 생성 증거물은 손으로 고치거나 커밋 대상으로 삼지 않는다.

완료 조건:

- 사람이 작성한 분석 문서는 성격에 맞는 `analysis/*.md`에만 있다.
- 사람이 작성한 개선 계획 문서는 성격에 맞는 `plan/*.md`에만 있다.
- skill, reference, eval case, answer, fixture, generated run artifact에는 분석/계획 내용이 섞이지 않았다.

## 2. 독립 리뷰 기록

P1처럼 기준을 확정하는 분석 작업은 가능한 경우 독립 관점 리뷰를 포함한다.

제약:

- subagent 리뷰를 실행한 경우 분석 문서 또는 최종 보고에 `Subagent 리뷰/순차 fallback:` 항목을 남긴다.
- subagent 리뷰를 실행하지 못한 경우 `Subagent 리뷰/순차 fallback: 순차 fallback`과 사유를 남긴다.
- `analysis/*.md` 문서에는 `리뷰 방식: real-subagent`, `리뷰 방식: sequential-fallback`, `리뷰 방식: not-run` 중 하나를 적는다.
- `analysis/*.md` 문서에는 `리뷰 결과: Blocker N, Major N, 열린 Minor N` 형식의 요약을 적는다.
- real subagent를 사용할 수 있으면 `skill-creator` 관점 리뷰를 별도 subagent에 맡기는 것을 우선한다.
- subagent에게 의도한 결론, 원하는 수정 대상, 이전 판정 결과를 먼저 주입하지 않는다.
- subagent는 P1 범위에서 파일을 수정하지 않고 Blocker, Major, Minor, Note만 보고한다.
- P1의 skill 점검에는 `skill-creator` 관점 리뷰를 포함한다.
- `skill-creator` 관점 리뷰는 `SKILL.md` 목적 명확성, trigger description, progressive disclosure, reference 중복/누락, validation integrity를 확인한다.
- real subagent를 사용할 수 없으면 `/Users/hyun/.codex/skills/.system/skill-creator/SKILL.md`를 읽고 같은 기준으로 순차 fallback을 수행한다.
- `skill-creator` 리뷰를 실행했거나 fallback으로 수행한 경우 분석 문서 또는 최종 보고에 `skill-creator 리뷰:` 항목을 남긴다.
- 메인 에이전트는 subagent 결과를 그대로 채택하지 않고 충돌 여부를 통합 판단한다.
- 실제로 실행하지 않은 subagent 리뷰를 실행한 것처럼 기록하지 않는다.

완료 조건:

- 기준 확정 분석에는 독립 리뷰 실행 여부와 사유가 남아 있다.
- subagent 결과와 메인 판단이 충돌하면 충돌 내용과 최종 판단 근거가 남아 있다.

## 3. 분석 문서 첫 줄

모든 분석 문서의 첫 줄에는 실제 수정 대상을 적는다.

첫 줄 형식:

```text
수정 대상: skill
```

허용 값:

```text
수정 대상: reference
수정 대상: skill
수정 대상: case
수정 대상: answer
수정 대상: evaluator
수정 대상: runtime-sync
수정 대상: report
수정 대상: model-variance
수정 대상: process
수정 대상: cleanup
수정 대상: tooling
수정 대상: none
```

의미:

| 값 | 의미 | 대표 수정 위치 |
|---|---|---|
| `reference` | 근거 문서가 부족하거나 충돌한다. | `workspace/reference/**` |
| `skill` | skill 설명, routing, runtime rule, bundled reference가 부족하다. | `dddjango/skills/**` |
| `case` | public 평가 요청이 목적을 잘못 유도한다. | `workspace/develop/eval/<bucket>/cases/plugin/public/*.md` |
| `answer` | answer oracle이 잘못되었거나 과도하다. | `workspace/develop/eval/<bucket>/answer/*.yaml` |
| `evaluator` | 평가기 판정, schema, 언어 검증, deterministic check가 잘못되었다. | `workspace/scripts/**` |
| `runtime-sync` | source와 runtime cache가 어긋났다. | runtime cache sync와 검증 |
| `report` | HTML report 또는 latest 포인터가 잘못되었다. | `workspace/scripts/render_eval_review_html.py` |
| `model-variance` | 같은 입력에서도 모델 변동성이 핵심 원인이다. | rerun evidence 또는 blocker |
| `process` | 개발 절차나 의사결정 흐름이 부족하다. | `workspace/plan/**` |
| `cleanup` | 불필요한 산출물, 폴더, 문서, 추적 대상 정리가 필요하다. | 정리 대상 경로 |
| `tooling` | 평가 외 보조 스크립트나 개발 도구가 부족하다. | `workspace/scripts/**` 또는 관련 도구 |
| `none` | 수정 대상이 없고 기록만 필요하다. | 분석 문서 |

제약:

- 첫 줄은 반드시 `수정 대상:`으로 시작한다.
- 허용 값에 없는 표현을 쓰지 않는다.
- 여러 대상이 필요하면 분석 문서에는 주된 수정 대상을 첫 줄에 적고, 본문에 보조 대상을 적는다.
- 첫 줄에서 대상을 정하지 않은 채 원인 분석을 시작하지 않는다.
- `skill_lv_up_plan` 분석 문서의 첫 줄은 `수정 대상: skill` 또는 `수정 대상: runtime-sync`만 허용한다.
- `reference_lv_up_plan` 분석 문서의 첫 줄은 `수정 대상: reference`만 허용한다.
- `eval_lv_up_plan` 분석 문서의 첫 줄은 `수정 대상: case`, `수정 대상: answer`, `수정 대상: evaluator`, `수정 대상: report`, `수정 대상: model-variance` 중 하나만 허용한다.
- `etc_lv_up_plan` 분석 문서의 첫 줄은 `수정 대상: process`, `수정 대상: cleanup`, `수정 대상: tooling`, `수정 대상: none` 중 하나만 허용한다.

예시:

```text
수정 대상: reference
원인 분류: source gap
```

```text
수정 대상: answer
원인 분류: oracle overclaim
```

완료 조건:

- 모든 분석 문서의 첫 줄이 허용 형식이다.
- 개선 계획의 수정 범위가 분석 문서의 첫 줄과 충돌하지 않는다.

## 4. 생성 문서 파일명

새로 작성하는 분석, 계획 문서와 평가 결과 문서는 파일명 또는 상위 실행 식별자에 생성 시각을 포함한다.

적용 대상:

```text
workspace/plan/*_lv_up_plan/**/*.md
workspace/develop/eval/<bucket>/runs/<run-id>/**
```

제약:

- `*_lv_up_plan` 아래 사람이 작성하는 분석/계획 문서는 파일명 접두어로 생성 시각을 붙인다.
- 파일명 형식은 `YYYYMMDD-HHMMSS-<target-name>-topic.md`를 사용한다.
- `<target-name>`은 상위 대상 폴더명과 같아야 한다.
- skill, reference 분석/계획 문서의 `<target-name>`은 대상 skill 또는 reference area 이름이다.
- eval 분석/계획 문서의 `<target-name>`은 bucket 이름이다.
- etc 분석/계획 문서의 `<target-name>`은 topic 이름이다.
- 시간은 파일을 처음 작성한 로컬 시각 기준으로 적는다.
- topic은 소문자 영문, 숫자, 하이픈만 사용한다.
- 같은 작업의 분석과 계획은 같은 파일명을 사용한다.
- eval run 결과는 `runs/<run-id>/`의 run id가 `YYYYMMDD-HHMMSS-...` 형식을 만족해야 한다.
- run 내부의 `analysis/report.html`처럼 고정 이름이 필요한 generated file은 상위 run id의 생성 시각을 따른다.

예시:

```text
workspace/plan/skill_lv_up_plan/architecture-ddd/analysis/20260521-153012-architecture-ddd-p1-skill.md
workspace/plan/skill_lv_up_plan/architecture-ddd/plan/20260521-153012-architecture-ddd-skill-plan.md
workspace/develop/eval/code/runs/20260521-153012-code-try01-full-current-baseline/analysis/report.html
```

예외:

- `workspace/plan/master_plan.md`
- `workspace/plan/constraint_rules.md`
- `eval_goal.md`, `manual_protocol.md`처럼 생성 문서가 아니라 고정 역할을 가진 기준 문서
- public case, answer oracle, fixture처럼 파일명이 평가 case id 또는 도구 계약과 묶인 문서

완료 조건:

- `*_lv_up_plan` 아래 새 `.md` 파일명은 생성 시각 접두어를 가진다.
- eval run 결과는 timestamp run id 아래에 생성된다.

## 5. 문서 언어

모든 개발 문서는 한글 설명문을 기본으로 작성한다.

적용 대상:

```text
workspace/plan/**/*.md
workspace/reference/**/*.md
workspace/develop/eval/**/*.md
workspace/develop/eval/**/*.yaml
dddjango/skills/**/*.md
dddjango/skills/**/agents/*.yaml
```

제약:

- 제목, 절차, 체크리스트, 평가 의도, 판정 설명은 한글로 작성한다.
- 평가 case의 사용자 요청 문장은 한글로 작성한다.
- answer oracle의 관찰 항목과 판정 기준은 한글로 작성한다.
- skill의 runtime rule은 한글을 우선하되, trigger matching에 필요한 영문 기술어는 유지한다.

허용 예외:

- 파일 경로, 명령어, 코드 식별자
- API 이름, HTTP method/status, schema key
- Python, Django, Django Ninja, pytest 같은 고유 기술명
- frontmatter key, YAML key, JSON key
- public-facing 출력이 사용자 요구상 영어여야 하는 경우
- skill trigger vocabulary에 필요한 영어 표현

완료 조건:

- 문서의 설명 문장은 한글 중심이다.
- 영어는 경로, 명령어, 코드, schema, 고유명사, trigger vocabulary처럼 필요한 곳에만 있다.

## 6. 평가지 폴더 역할

평가지는 `workspace/develop/eval/<bucket>/` 아래의 폴더 역할을 지켜 작성한다.

대상 bucket:

```text
response
code
plugin
runtime
source
workflow
```

폴더 역할:

| 위치 | 역할 |
|---|---|
| `eval_goal.md` | bucket 평가 목적, coverage 범위, 완료 기준 |
| `cases/plugin/public/` | 사용자에게 보이는 public 평가 요청 |
| `cases/plugin/*.json` | bucket별 실행 보조 metadata |
| `answer/` | evaluator-only 답안지와 판정 기준 |
| `fixtures/` | 평가 입력 fixture 프로젝트와 보조 파일 |
| `manual_protocol.md` | 자동 평가만으로 부족한 수동 확인 절차 |
| `runs/` | 생성된 평가 실행 결과 |
| `latest/`, `latest-valid/` | 생성된 최신 결과 포인터 |

제약:

- 새 평가는 반드시 하나의 bucket 아래에 작성한다.
- public 요청은 `cases/plugin/public/case-<bucket>-<name>.md`에 작성한다.
- 답안지는 `answer/case-<bucket>-<name>.yaml`에 작성한다.
- public case와 answer 파일의 case id는 1:1로 대응한다.
- public case에는 evaluator-only 기준, private oracle, prior run finding을 쓰지 않는다.
- answer에는 public case에 노출하면 안 되는 판정 기준을 둔다.
- fixture가 필요하면 해당 bucket의 `fixtures/` 아래에 둔다.
- 자동 평가로 판단할 수 없는 절차는 `manual_protocol.md`에 둔다.
- `manual_protocol.md`는 `plugin`, `runtime`, `source`, `workflow` bucket에는 필수이고, `response`, `code` bucket에는 필요할 때만 둔다.
- `runs/`, `latest/`, `latest-valid/` 아래에는 손으로 평가지, 분석, 계획을 작성하지 않는다.

완료 조건:

- `eval_goal.md`가 새 case의 목적을 설명한다.
- public case와 answer가 1:1로 대응한다.
- case, answer, fixture, manual protocol, generated artifact가 각자 역할을 지킨다.

## 7. 자동 검증

문서 제약은 자동 검증이 가능한 범위부터 검증한다. validator 통과가 모든 수동 제약의 통과를 뜻하지는 않는다.

검증 책임:

| 제약 | 담당 검증 |
|---|---|
| `*_lv_up_plan` 위치, section, 파일명, 첫 줄 `수정 대상:` | `validate_plan_constraints.py` |
| public case와 answer 1:1 대응, manual protocol, eval pack 구조 | `validate_eval_bucket_pack.py` |
| skill 문서 구조와 runtime skill 동기화 | `validate_skill_docs.py` |
| eval run artifact, forbidden local path, oracle schema | `validate_eval_run.py` |

검증 명령:

```bash
.venv/bin/python -B workspace/scripts/validate_plan_constraints.py
```

검증 범위:

- `workspace/plan/skill_lv_up_plan/<skill-name>/analysis/*.md` 첫 줄의 `수정 대상:` 형식
- `workspace/plan/reference_lv_up_plan/<reference-area>/analysis/*.md` 첫 줄의 `수정 대상:` 형식
- `workspace/plan/eval_lv_up_plan/<bucket>/analysis/*.md` 첫 줄의 `수정 대상:` 형식
- `workspace/plan/etc_lv_up_plan/<topic>/analysis/*.md` 첫 줄의 `수정 대상:` 형식
- `workspace/plan/*_lv_up_plan/**/*.md` 파일명의 생성 시각 접두어 형식
- 각 `*_lv_up_plan` 아래 허용 section 이름
- `skill_lv_up_plan` 아래 허용 skill 이름
- `eval_lv_up_plan` 아래 허용 bucket 이름
- `reference_lv_up_plan` 아래 허용 reference area 이름
- `etc_lv_up_plan` 아래 topic 이름 형식
- plan 문서와 같은 파일명의 analysis 문서 존재 여부
- `analysis/`와 `plan/` 아래 중첩 디렉터리 금지

수동 확인 범위:

- 문서 설명문이 한글 중심인지 확인한다.
- public case가 private answer나 oracle 내용을 누설하지 않는지 확인한다.
- skill이나 reference에 평가 분석/개선 계획 내용이 섞이지 않았는지 확인한다.
- runtime skill에 source reference 원문을 그대로 복사하지 않았는지 확인한다.

완료 조건:

- 제약을 바꾸면 validator와 테스트를 함께 갱신한다.
- validator가 검증하지 못하는 제약은 문서에서 수동 확인 항목으로 유지한다.
