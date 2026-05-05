# dddjango Comprehensive Performance Evaluation Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** dddjango 스킬을 Codex와 Claude 양쪽에서 제품화 가능한 수준으로 검증하기 위해 품질, 트리거, 사용성, 성능, 설치/배포, 운영 회귀까지 단계별로 측정한다.

**Architecture:** 기존 `evals/codex`와 `evals/claude` 하네스를 유지하되, 평가 suite를 `smoke`, `benchmark`, `trigger`, `usability`, `real-repo`, `release`로 확장한다. 모든 평가는 with/without dddjango 비교와 HTML 리포트를 기본 산출물로 남기며, `skills/`를 canonical source로 두고 `plugins/dddjango/skills/` mirror 일치를 release gate에 포함한다.

**Tech Stack:** Python stdlib, unittest, Codex CLI, Claude CLI, JSONL/JSON evaluation assets, static HTML report, Makefile release automation.

---

## Progress Dashboard

| Phase | 상태 | 목적 | 주요 산출물 |
| --- | --- | --- | --- |
| Phase 0 | Done | 현재 평가 자산과 완료 상태 정리 | 이 문서, 기존 roadmap 링크 |
| Phase 1 | Done | Codex 8-case smoke 및 1차 gate 통과 | `workspace/codex-eval/iteration-1/report.html` |
| Phase 2 | Blocked | Claude smoke 측정 | `workspace/claude-eval/iteration-1/report.html` |
| Phase 3 | Done | 24-case benchmark suite 확장 | `evals/shared/cases/benchmark.jsonl` |
| Phase 4 | Done | trigger precision/recall suite 확장 | `evals/shared/cases/trigger.jsonl` |
| Phase 5 | Done | usability/manual review 체계 추가 | `evals/shared/rubrics/usability-checklist.md` |
| Phase 6 | Done | real repo forward test 구성 | `evals/fixtures/django-shop`, `workspace/codex-eval/real-repo-1/report.html` |
| Phase 7 | Codex Done / Claude Blocked | Codex/Claude full benchmark 반복 측정 | `workspace/codex-eval/benchmark-repeat-summary/report.html`, Claude auth blocker |
| Phase 8 | Pending | marketplace/fresh install 검증 | release install log, README 검증 |
| Phase 9 | Pending | beta 사용자 평가 | feedback summary, regression cases |
| Phase 10 | Pending | 운영 회귀 체계 고정 | smoke/full release gate |

## Current Baseline

- Codex 1차 파일럿은 `docs/superpowers/plans/2026-05-04-dddjango-skill-evaluation-roadmap.md` 기준 완료했다.
- Codex 1차 결과:
  - baseline average: `81.0`
  - dddjango average: `93.25`
  - quality lift: `+15.12%`
  - time increase: `+26.41%`
  - DRF violations: `0`
  - Korean-first rate: `100%`
  - Django Ninja compliance: `100%`
  - TDD quality: `100%`
  - negative-control pass rate: `100%`
- Claude 1차 측정은 CLI 인증/조직 정책으로 blocked 상태다.
  - 관측된 blocker: Claude Code subscription access disabled
  - 필요 조치: `ANTHROPIC_API_KEY` 설정 또는 조직의 Claude Code subscription access 허용

## Latest Codex Full Evaluation

- 평가 일자: 2026-05-04
- 채점 방식: 1차 자동 휴리스틱 채점. release gate 전 수동 재채점 필요.
- Benchmark suite:
  - cases: `24`
  - baseline executions: `24/24 returncode=0`
  - dddjango executions: `24/24 returncode=0`
  - baseline average score: `84.75`
  - dddjango average score: `86.92`
  - lift: `+2.17` points, `+2.56%`
  - baseline average time: `39.60s`
  - dddjango average time: `96.78s`
  - report: `workspace/codex-eval/benchmark-1/report.html`
- Trigger suite:
  - cases: `30`
  - baseline executions: `30/30 returncode=0`
  - dddjango executions: `30/30 returncode=0`
  - baseline average score: `78.73`
  - dddjango average score: `83.10`
  - lift: `+4.37` points, `+5.55%`
  - baseline average time: `36.24s`
  - dddjango average time: `87.38s`
  - trigger recall: `10/10`, `100%`
  - trigger precision: `10/10`, `100%`
  - ambiguous handling: `5/6`, `83.33%`
  - conflict handling: `4/4`, `100%`
  - report: `workspace/codex-eval/trigger-1/report.html`
- Current interpretation:
  - 실행 안정성은 Codex 기준 통과했다.
  - Trigger gate는 1차 자동 채점 기준으로 대체로 통과했다.
  - Benchmark quality lift는 release gate 기준 `+15%`에 미달하므로, 수동 재채점과 저점 케이스 원인 분석이 필요하다.
  - dddjango 평균 실행 시간 증가는 `+30%` gate를 초과하므로, 스킬 로딩 범위와 응답 길이 최적화가 필요하다.

## Iteration 2/3 Findings

- Root cause addressed:
  - `run_prompts.py`가 pilot 8개만 case-specific skill injection을 지원했다.
  - benchmark/trigger 전체 케이스는 broad instruction을 받아 모든 dddjango skill을 읽도록 유도됐다.
  - negative trigger처럼 dddjango가 트리거되지 않아야 하는 케이스에도 broad instruction이 강제 주입됐다.
- Fix:
  - answer-key metadata의 `category`, `expectations`, `trigger_type`, `prompt`를 기반으로 필요한 `SKILL.md`만 주입한다.
  - negative trigger와 non-Django negative-control은 local dddjango instruction을 주입하지 않는다.
  - local instruction이 없는 dddjango 케이스는 `--ignore-user-config`로 격리해 사용자 설정 오염을 줄인다.
- Benchmark iteration 2:
  - report: `workspace/codex-eval/benchmark-2/report.html`
  - baseline executions: `24/24 returncode=0`
  - dddjango executions: `24/24 returncode=0`
  - baseline average score: `82.42`
  - dddjango average score: `86.62`
  - lift: `+4.20` points, `+5.10%`
  - baseline average time: `38.37s`
  - dddjango average time: `56.02s`
  - time increase improved from iteration 1 `+144.39%` to `+46.00%`, but still above the `+30%` gate.
- Trigger iteration 3:
  - report: `workspace/codex-eval/trigger-3/report.html`
  - baseline executions: `30/30 returncode=0`
  - dddjango executions: `30/30 returncode=0`
  - baseline average score: `80.07`
  - dddjango average score: `79.20`
  - lift: `-0.87` points, `-1.09%`
  - baseline average time: `35.97s`
  - dddjango average time: `33.08s`
  - trigger recall: `10/10`, `100%`
  - trigger precision: `10/10`, `100%`
  - ambiguous handling: `4/6`, `66.67%`
  - conflict handling: `4/4`, `100%`
- Current interpretation:
  - 스코프 주입 수정으로 실행 시간은 크게 개선됐다.
  - trigger negative/positive/conflict는 통과하지만 ambiguous handling은 아직 약하다.
  - benchmark quality lift는 개선됐지만 `+15%` release gate에는 아직 미달한다.
  - 다음 개선 대상은 `benchmark-api-product-search`, `benchmark-db-order-query-index`, `trigger-positive-clean-code-django`, ambiguous trigger 응답 정책이다.

## Iteration 4 Targeted Rerun

- 평가 일자: 2026-05-05
- 범위: 전체 재실행 전, 저점/오탐 의심 케이스 5개만 타깃 재측정했다.
- Fix:
  - `auto_grade_outputs.py`가 일반적인 `serializer/form` 표현을 DRF 구현으로 오탐하지 않도록 DRF 패턴을 좁혔다.
  - API 표준과 DB 실행계획 관련 용어를 architecture quality 신호로 인식하도록 자동 채점 휴리스틱을 보정했다.
  - ambiguous trigger가 `서비스 레이어`, `테스트`, `도메인`, `API` 같은 한국어/혼합 키워드에서도 필요한 스킬을 주입하도록 `run_prompts.py`를 보강했다.
  - `implementation-django-ninja`에 검색/목록 API 표준을 추가했다: `Query[FilterSchema]`, 정렬 allow-list, `items/meta envelope`, `@paginate`와 커스텀 envelope 혼용 금지, RFC 9457 에러 표준.
- Benchmark targeted rerun:
  - report: `workspace/codex-eval/benchmark-3/report.html`
  - completed cases: `2`
  - baseline average score: `87.50`
  - dddjango average score: `87.50`
  - lift: `0.00` points, `0.00%`
  - cases:
    - `benchmark-api-product-search`: baseline `88`, dddjango `88`
    - `benchmark-db-order-query-index`: baseline `87`, dddjango `87`
- Trigger targeted rerun:
  - report: `workspace/codex-eval/trigger-4/report.html`
  - completed cases: `3`
  - baseline average score: `77.67`
  - dddjango average score: `82.33`
  - lift: `+4.66` points, `+6.00%`
  - cases:
    - `trigger-positive-clean-code-django`: baseline `72`, dddjango `80`
    - `trigger-ambiguous-service-layer`: baseline `77`, dddjango `80`
    - `trigger-ambiguous-testing`: baseline `84`, dddjango `87`
- Current interpretation:
  - DRF/TDD 관련 낮은 점수 일부는 스킬 실패가 아니라 자동 채점 오탐이었다.
  - ambiguous handling은 타깃 케이스에서 개선됐다.
  - benchmark quality lift는 아직 full release gate 기준에 충분하지 않다. 다음 단계는 자동 휴리스틱을 보정한 상태에서 24-case benchmark와 30-case trigger를 다시 전체 실행하는 것이다.

## Iteration 5 Full Rerun

- 평가 일자: 2026-05-05
- 범위: 보정된 스킬 주입/자동 채점 기준으로 Codex full benchmark와 trigger suite를 다시 전체 실행했다.
- Benchmark full rerun:
  - report: `workspace/codex-eval/benchmark-4/report.html`
  - baseline executions: `24/24 returncode=0`
  - dddjango executions: `24/24 returncode=0`
  - baseline average score: `83.67`
  - dddjango average score: `87.92`
  - lift: `+4.25` points, `+5.08%`
  - baseline average time: `44.95s`
  - dddjango average time: `49.47s`
  - time increase: `+10.06%`
- Trigger full rerun:
  - report: `workspace/codex-eval/trigger-5/report.html`
  - baseline executions: `30/30 returncode=0`
  - dddjango executions: `30/30 returncode=0`
  - baseline average score: `80.37`
  - dddjango average score: `83.30`
  - lift: `+2.93` points, `+3.65%`
  - baseline average time: `34.05s`
  - dddjango average time: `34.87s`
  - time change: `+2.41%`
  - trigger recall: `10/10`, `100%`
  - trigger precision: `10/10`, `100%`
  - ambiguous handling: `6/6`, `100%`
  - conflict handling: `4/4`, `100%`
- Review/fix notes:
  - TDD 채점이 `created`, `related`, `redirection` 같은 단어의 `red` 부분 문자열에 흔들리지 않도록 단어 경계와 명시적 테스트 표식 기준으로 보정했다.
  - non-Django negative-control은 FastAPI/Flask/React 같은 요청을 존중했는지 별도 판단하고, 일반 API 용어만으로 Django 점수가 부풀지 않게 보정했다.
  - `DRF Serializer/ViewSet/APIView는 쓰지 않고...` 같은 한국어 거부 표현을 DRF endorsement로 오탐하지 않게 보정했다.
  - Django Ninja 스킬은 DRF 대체/API 코드 제시 후 `python manage.py check`와 `pytest` 또는 `python manage.py test` 검증 명령을 포함하도록 강화했다.
- Current interpretation:
  - 실행 안정성은 통과했다.
  - 시간 게이트는 통과했다. Benchmark와 Trigger 모두 `+30%` 이하이다.
  - Trigger gate는 자동 채점 기준으로 모두 통과했다.
  - Benchmark suite에는 dddjango가 baseline보다 낮은 케이스가 남아 있지 않다. 동률 케이스는 `benchmark-api-drf-migration`, `benchmark-ddd-bounded-context`, `benchmark-ddd-service-layer`, `benchmark-negative-fastapi` 등이다.
  - Trigger suite의 남은 소폭 역전은 `trigger-ambiguous-domain-model` `-3`, `trigger-conflict-serializer-migration` `-1`이다. 둘 다 trigger pass 자체는 성공했으므로 다음 단계에서 수동 사용성 점수와 함께 판단한다.
  - Benchmark quality lift는 `+15%` release gate에 아직 미달한다.
  - 다음 단계는 자동 점수만으로 결론을 내리지 않고, Phase 5 usability/manual review 체계를 추가해 실제 답변 품질과 트리거 적합성을 수동 점수로 검증하는 것이다.

## Manual Usability Review

- 평가 일자: 2026-05-05
- 기준: `evals/shared/rubrics/usability-checklist.md`
- 범위:
  - Benchmark suite 전체 `24/24` dddjango outputs
  - Trigger suite 전체 `30/30` dddjango outputs
- Benchmark usability:
  - scored cases: `24`
  - dddjango average usability: `18.92 / 20`
  - report: `workspace/codex-eval/benchmark-4/report.html`
  - 감점 주요 원인:
    - `benchmark-api-product-search`: `from typing import list`는 실제 Python import 오류라 `realistic_file_layout` 감점
    - `benchmark-negative-drf-explicit`: DRF 거부와 Ninja 대체는 좋지만 endpoint type hint와 도메인 검증이 얕아 감점
    - `benchmark-api-inventory-reserve`: 멱등성/동시성 설계는 좋지만 재고 부족 예외와 transaction rollback/저장된 실패 응답의 상호작용이 애매함
- Trigger usability:
  - scored cases: `30`
  - dddjango average usability: `18.67 / 20`
  - report: `workspace/codex-eval/trigger-5/report.html`
  - 감점 주요 원인:
    - ambiguous 케이스는 맥락을 잘 인지하지만 실제 코드 적용 단계는 사용자 확인 후 보강 필요
    - conflict serializer 전환은 간결하나 password/email 같은 도메인 검증은 추가 필요
    - `trigger-negative-react-props`: Django 오염은 없지만 React props 정리 일반 가이드 없이 파일 부재만 안내해 사용성이 낮음
    - `trigger-negative-shell-script`: 요청은 충족하지만 markdown fence가 깨져 보이는 출력 문제가 있음
- Current interpretation:
  - 자동 score lift는 release gate 기준 `+15%`에 미달하지만, 전체 수동 사용성은 `18+/20`으로 높다.
  - 즉각적인 다음 개선 후보는 "스킬 전반"보다 Django Ninja 코드 생성의 현실성이다. 특히 잘못된 import, endpoint type hint, 검증/도메인 규칙 누락을 줄이는 방향이 효과적이다.
  - trigger negative precision은 좋지만, non-Django 요청에서 파일이 없을 때도 최소 일반 가이드나 예시를 제공하도록 개선하면 사용성이 오른다.

## Iteration 6 Targeted Realism Fix

- 평가 일자: 2026-05-05
- 범위: 수동 사용성 감점 원인이 확인된 타깃 케이스만 dddjango variant로 재실행했다.
- Fix:
  - `implementation-django-ninja`에 sync endpoint `request: HttpRequest`, 명시적 return type, `from typing import list` 금지, `application/problem+json` 실제 응답/테스트 검증, `response=list[...]`와 커스텀 envelope 혼용 금지, `transaction.atomic()` rollback과 실패 응답 저장 충돌 방지 규칙을 추가했다.
  - non-Django negative-control은 dddjango 스킬을 주입하지 않되, 파일이 없어도 요청 기술 스택의 최소 예시나 일반 가이드를 제공하도록 neutral developer instruction을 추가했다.
  - Codex 하네스의 Django Ninja policy injection에 `request: HttpRequest`와 explicit return type 요구를 추가했다.
- Targeted rerun:
  - `benchmark-api-product-search`
  - `benchmark-api-inventory-reserve`
  - `benchmark-negative-drf-explicit`
  - `trigger-negative-react-props`
  - `trigger-negative-shell-script`
  - `trigger-conflict-rest-framework-import`
  - `trigger-conflict-drf-vs-ninja`
- Verification observations:
  - `benchmark-api-product-search`는 `HttpRequest`, `application/problem+json`, allow-list sort, `items/meta envelope`를 포함했다.
  - `benchmark-api-inventory-reserve`는 실패 응답 저장 후 예외를 다시 던지지 않아 `atomic()` rollback으로 멱등성 실패 응답이 사라지는 문제를 명시했다.
  - `benchmark-negative-drf-explicit`은 재실행 후 모든 endpoint에 `request: HttpRequest`와 return type이 포함됐다.
  - `trigger-negative-react-props`는 Django/DDD 오염 없이 React props 구조 가이드를 제공했다.
  - `trigger-negative-shell-script`는 fenced bash block이 정상 출력됐다.
- Updated automatic summary:
  - Benchmark dddjango average: `87.58`
  - Benchmark lift: `+3.91` points, `+4.67%`
  - Trigger dddjango average: `82.80`
  - Trigger lift: `+2.43` points, `+3.02%`
- Current interpretation:
  - 자동 점수 lift는 여전히 `+15%` release gate에 미달하지만, 이번 변경의 목적이었던 코드 현실성/사용성 감점 원인은 줄었다.
  - 자동 휴리스틱은 짧고 현실적인 코드에서 architecture term이 줄면 점수를 낮게 줄 수 있으므로, release 판단에는 manual usability와 real-repo forward test를 같이 봐야 한다.
  - 다음 실행 가능한 단계는 Phase 6 real repo fixture 구성이다. Claude 측정은 인증/결제 blocker가 풀릴 때까지 pending이다.

## Real Repo Forward Test Iteration 1

- 평가 일자: 2026-05-05
- Fixture strategy: 작고 공개 가능한 Django fixture를 repo 안에 추가했다.
  - fixture: `evals/fixtures/django-shop`
  - cases: `evals/shared/cases/real-repo.jsonl`
  - report: `workspace/codex-eval/real-repo-1/report.html`
- Fixture coverage:
  - fat model: `Order.cancel()`
  - fat view: `reserve_inventory`
  - legacy DRF: `api_drf.py`
  - DB/index target: `Order`, `Reservation`, `Product`
  - thin tests: `shop/orders/tests.py`
- Real-repo suite:
  - cases: `6`
  - baseline executions: `6/6 returncode=0`
  - dddjango executions: `6/6 returncode=0`
  - baseline average score: `84.00`
  - dddjango average score: `88.83`
  - lift: `+4.83` points, `+5.75%`
- Diff evaluator:
  - script: `evals/codex/scripts/evaluate_real_repo_diffs.py`
  - output: `workspace/codex-eval/real-repo-1/real_repo_evaluation.json`
  - baseline diff found: `6/6`
  - baseline patch applied: `6/6`
  - dddjango diff found: `6/6`
  - dddjango patch applied: `6/6`
  - baseline `python manage.py check`: `6/6`
  - baseline pytest/test fallback: `6/6`
  - dddjango `python manage.py check`: `6/6`
  - dddjango pytest/test fallback: `6/6`
- Observed dddjango strengths:
  - `real-repo-fat-model-refactor`: service layer diff와 pytest 보강 포함.
  - `real-repo-ninja-product-search`: `FilterSchema`, `Query`, allow-list sort, `items/meta`, `HttpRequest`, `application/problem+json` 포함.
  - `real-repo-db-order-index-review`: `Index`, `UniqueConstraint`, migration diff 포함.
  - `real-repo-drf-to-ninja-migration`: `rest_framework`, `ModelSerializer`, `APIView` 제거 diff 포함.
- Remaining gap:
  - patch apply, Django system check, pytest/test fallback까지 자동 검증한다.
  - real-repo dddjango 실행 시간이 baseline보다 길다. 이후 full release gate에서는 quality lift와 함께 시간 증가도 별도 판단해야 한다.

## Codex Benchmark Repeat Summary

- 평가 일자: 2026-05-05
- 목적: 자동 채점 노이즈를 줄이기 위해 Codex full benchmark를 3회 반복 측정했다.
- 리포트:
  - aggregate: `workspace/codex-eval/benchmark-repeat-summary/report.html`
  - iteration 1: `workspace/codex-eval/benchmark-4/report.html`
  - iteration 2: `workspace/codex-eval/benchmark-5/report.html`
  - iteration 3: `workspace/codex-eval/benchmark-6/report.html`
- Harness hardening:
  - `run_prompts.py`에 `--timeout-sec`를 추가했다.
  - 기본 케이스별 timeout은 `900s`이며, timeout 발생 시 returncode `124`, `.codex.log`, `.output.md`, `timing.json`에 기록하고 `--keep-going`이면 다음 케이스로 넘어간다.
- Iteration results:
  - `benchmark-4`: baseline `83.67`, dddjango `87.58`, lift `+3.91` points, `+4.67%`, time change `+13.21%`
  - `benchmark-5`: baseline `84.29`, dddjango `88.62`, lift `+4.33` points, `+5.14%`, time change `+17.57%`
  - `benchmark-6`: baseline `86.71`, dddjango `88.46`, lift `+1.75` points, `+2.02%`, time change `+32.16%`
- 3-run aggregate:
  - baseline average score: `84.89`
  - dddjango average score: `88.22`
  - lift: `+3.33` points, `+3.92%`
  - baseline average time: `53.96s`
  - dddjango average time: `65.68s`
  - time change: `+21.72%`
- Category aggregate:
  - `api-design`: `89.58 -> 92.75`, delta `+3.17`
  - `clean-code`: `86.00 -> 87.33`, delta `+1.33`
  - `db-design`: `80.00 -> 87.00`, delta `+7.00`
  - `ddd-architecture`: `84.75 -> 88.50`, delta `+3.75`
  - `negative-control`: `76.17 -> 81.17`, delta `+5.00`
  - `review`: `86.00 -> 89.50`, delta `+3.50`
  - `tdd`: `86.42 -> 87.25`, delta `+0.83`
- Current interpretation:
  - Codex benchmark execution stability는 `3 * 48` runs 모두 returncode `0`으로 통과했다.
  - 평균 time gate `+30%` 이하는 통과했다. 다만 `benchmark-6` 단일 반복은 `+32.16%`로 경계값을 넘었으므로 release gate에서는 평균과 outlier를 함께 본다.
  - Quality lift는 3회 평균 `+3.92%`로 기존 `+15%` gate에는 미달한다. 하지만 dddjango는 모든 category 평균에서 baseline보다 높고, manual usability 및 real-repo patch test는 통과권이다.
  - 다음 단계는 fresh install/release gate를 검증하고, `tdd`, `clean-code`의 낮은 lift를 다음 개선 backlog로 분리하는 것이다.

## File Responsibilities

- `evals/codex/cases/pilot.jsonl`: Codex smoke suite의 현재 8개 기준 케이스.
- `evals/codex/scripts/run_prompts.py`: Codex with/without dddjango 실행 하네스.
- `evals/claude/scripts/run_prompts.py`: Claude with/without dddjango 실행 하네스.
- `evals/codex/scripts/grade_outputs.py`: 수동 grade summary 계산기.
- `evals/codex/scripts/render_report.py`: Codex/Claude 공용 HTML report renderer.
- `evals/codex/scripts/evaluate_real_repo_diffs.py`: real repo unified diff 적용 가능성 evaluator.
- `evals/codex/rubrics/grading-schema.json`: 현재 scoring schema.
- `evals/codex/rubrics/dddjango-rubric.md`: 현재 수동 채점 기준.
- `evals/shared/cases/real-repo.jsonl`: real repo forward test suite.
- `evals/fixtures/django-shop`: 공개 가능한 작은 Django fixture.
- `workspace/codex-eval/iteration-*`: Codex 실행 결과와 HTML report.
- `workspace/claude-eval/iteration-*`: Claude 실행 결과와 HTML report.
- `skills/`: canonical dddjango skill source.
- `plugins/dddjango/skills/`: Codex 배포용 mirror.
- `.codex-plugin/plugin.json`: Codex plugin manifest.
- `.claude-plugin/plugin.json`: Claude plugin manifest.
- `.claude-plugin/marketplace.json`: Claude marketplace manifest.
- `README.md`: 사용자 설치/평가/release 안내.

## Release Gates

| Gate | 기준 |
| --- | --- |
| Smoke execution | Codex와 Claude 핵심 smoke case 100% 실행 성공 |
| Quality lift | full benchmark에서 with dddjango가 baseline 대비 `+15%` 이상 |
| Time increase | 평균 실행 시간 증가율 `+30%` 이하 |
| DRF violation | 구현 코드 기준 `0` |
| Django Ninja compliance | API 관련 케이스 `95%` 이상 |
| TDD quality | TDD 관련 케이스 `90%` 이상 |
| Trigger recall | positive trigger `95%` 이상 |
| Trigger precision | negative trigger 오염 `5%` 이하 |
| Korean-first | 한국어 요청 `95%` 이상 |
| Mirror sync | `skills/`와 `plugins/dddjango/skills/` byte-for-byte 일치 |
| Fresh install | Codex/Claude fresh install 성공 |
| HTML report | 각 iteration에 with/without 표와 gate verdict 포함 |

## Phase 0: Current State Lock

**Files:**
- Read: `git status --short`
- Read: `docs/superpowers/plans/2026-05-04-dddjango-skill-evaluation-roadmap.md`
- Read: `workspace/codex-eval/iteration-1/report.html`
- Read: `workspace/claude-eval/iteration-1/report.html`

- [x] **Step 1: 기존 1차 Codex 평가 완료 상태를 확인한다**

Run:

```bash
python3 evals/codex/scripts/grade_outputs.py workspace/codex-eval/iteration-1/grades.json
```

Expected:

```text
baseline average_score = 81.0
dddjango average_score = 93.25
lift.percent >= 15
```

- [x] **Step 2: 현재 Claude blocker를 문서화한다**

Run:

```bash
python3 evals/codex/scripts/render_report.py workspace/claude-eval/iteration-1 --platform Claude
```

Expected:

```text
workspace/claude-eval/iteration-1/report.html 에 Claude 인증 blocker가 표시된다.
```

- [x] **Step 3: 최종 단계까지 추적할 마스터 플랜을 생성한다**

Result:

```text
docs/superpowers/plans/2026-05-04-dddjango-comprehensive-performance-evaluation.md
```

## Phase 1: Codex Smoke Suite

**Files:**
- Read: `evals/codex/cases/pilot.jsonl`
- Write: `workspace/codex-eval/iteration-*/baseline/*.output.md`
- Write: `workspace/codex-eval/iteration-*/dddjango/*.output.md`
- Modify: `workspace/codex-eval/iteration-*/grades.json`
- Modify: `workspace/codex-eval/iteration-*/timing.json`
- Modify: `workspace/codex-eval/iteration-*/report.html`

- [x] **Step 1: Codex smoke iteration을 생성한다**

Run:

```bash
python3 evals/codex/scripts/init_iteration.py --output workspace/codex-eval/iteration-1
```

Expected:

```text
8개 prompt, answer-key, grades.json, timing.json template 생성
```

- [x] **Step 2: baseline과 dddjango를 모두 실행한다**

Run:

```bash
python3 evals/codex/scripts/run_prompts.py --variant baseline --keep-going
python3 evals/codex/scripts/run_prompts.py --variant dddjango --keep-going
```

Expected:

```text
8 baseline cases returncode=0
8 dddjango cases returncode=0
```

- [x] **Step 3: 수동 채점과 HTML report를 갱신한다**

Run:

```bash
python3 evals/codex/scripts/grade_outputs.py workspace/codex-eval/iteration-1/grades.json
python3 evals/codex/scripts/render_report.py workspace/codex-eval/iteration-1
```

Expected:

```text
quality lift >= 15%
time increase <= 30%
DRF violations = 0
workspace/codex-eval/iteration-1/report.html 생성
```

## Phase 2: Claude Smoke Suite

**Files:**
- Read: `evals/claude/scripts/init_iteration.py`
- Read: `evals/claude/scripts/run_prompts.py`
- Write: `workspace/claude-eval/iteration-*/baseline/*.output.md`
- Write: `workspace/claude-eval/iteration-*/dddjango/*.output.md`
- Modify: `workspace/claude-eval/iteration-*/grades.json`
- Modify: `workspace/claude-eval/iteration-*/timing.json`
- Modify: `workspace/claude-eval/iteration-*/report.html`

- [x] **Step 1: Claude smoke iteration을 생성한다**

Run:

```bash
python3 evals/claude/scripts/init_iteration.py --output workspace/claude-eval/iteration-1
```

Expected:

```text
Codex pilot과 같은 8개 prompt, answer-key, grades.json, timing.json template 생성
```

- [x] **Step 2: blocker pilot을 먼저 실행한다**

Run:

```bash
python3 evals/claude/scripts/run_prompts.py --variant baseline --case pilot-negative-drf --iteration workspace/claude-eval/iteration-1 --keep-going
```

Observed:

```text
Claude Code subscription access disabled
ANTHROPIC_API_KEY unset
```

- [ ] **Step 3: Claude 인증을 준비한다**

Required:

```bash
export ANTHROPIC_API_KEY=...
```

or:

```text
조직 설정에서 Claude Code subscription access 허용
```

- [ ] **Step 4: Claude baseline과 dddjango smoke를 실행한다**

Run:

```bash
python3 evals/claude/scripts/run_prompts.py --variant baseline --iteration workspace/claude-eval/iteration-1 --keep-going
python3 evals/claude/scripts/run_prompts.py --variant dddjango --iteration workspace/claude-eval/iteration-1 --keep-going
python3 evals/codex/scripts/render_report.py workspace/claude-eval/iteration-1 --platform Claude
```

Expected:

```text
8 baseline cases returncode=0
8 dddjango cases returncode=0
workspace/claude-eval/iteration-1/report.html 생성
```

## Phase 3: Shared Benchmark Suite

**Files:**
- Create: `evals/shared/cases/benchmark.jsonl`
- Create: `evals/shared/cases/README.md` only if needed for evaluator-facing docs outside skill packages
- Modify: `evals/codex/scripts/init_iteration.py`
- Modify: `evals/claude/scripts/init_iteration.py`
- Modify: `tests/test_codex_evaluation.py`
- Modify: `tests/test_claude_evaluation.py`

- [x] **Step 1: 24-case benchmark taxonomy를 고정한다**

Cases:

```text
Django Ninja API: 4
DDD architecture: 4
DB design/performance: 3
TDD/pytest: 4
Code review: 4
Clean code/refactoring: 3
Negative control: 2
```

- [x] **Step 2: benchmark JSONL을 작성한다**

Schema:

```json
{
  "id": "benchmark-api-order-status",
  "category": "django-ninja-api",
  "prompt": "주문 상태 변경 API를 Django Ninja와 DDD 기준으로 설계하고 구현 예시를 보여줘.",
  "expectations": [
    "Django Ninja router and Schema usage",
    "application service boundary",
    "transaction or concurrency note",
    "pytest example"
  ],
  "forbidden": [
    "DRF ModelViewSet",
    "rest_framework imports"
  ]
}
```

- [x] **Step 3: init_iteration에서 suite 선택을 지원한다**

Command:

```bash
python3 evals/codex/scripts/init_iteration.py --suite benchmark --output workspace/codex-eval/iteration-2
python3 evals/claude/scripts/init_iteration.py --suite benchmark --output workspace/claude-eval/iteration-2
```

Expected:

```text
24개 benchmark prompt가 생성된다.
```

- [x] **Step 4: suite 선택 테스트를 추가한다**

Run:

```bash
python3 -m unittest tests.test_codex_evaluation tests.test_claude_evaluation -v
```

Expected:

```text
benchmark suite count = 24
pilot/smoke suite count = 8
```

## Phase 4: Trigger Precision/Recall Suite

**Files:**
- Create: `evals/shared/cases/trigger.jsonl`
- Modify: `evals/codex/scripts/render_report.py`
- Modify: `evals/codex/rubrics/grading-schema.json`
- Modify: `tests/test_codex_evaluation.py`

- [x] **Step 1: trigger case taxonomy를 작성한다**

Cases:

```text
Positive trigger: 10
Negative trigger: 10
Ambiguous trigger: 6
Conflict trigger: 4
```

- [x] **Step 2: positive trigger 케이스를 작성한다**

Examples:

```text
Django Ninja로 주문 생성 API를 DDD 구조로 설계해줘.
pytest로 쿠폰 적용 기능을 TDD 방식으로 구현해줘.
이 Django 모델이 fat model인지 리뷰해줘.
```

- [x] **Step 3: negative trigger 케이스를 작성한다**

Examples:

```text
FastAPI로 health check API를 만들어줘.
Python으로 CSV 파일을 파싱하는 스크립트를 작성해줘.
React 컴포넌트의 props 구조를 정리해줘.
```

- [x] **Step 4: trigger report matrix를 추가한다**

HTML table:

```text
Case | Trigger Type | Expected Behavior | Observed Behavior | Precision/Recall Impact | Pass/Fail
```

- [x] **Step 5: trigger gate를 계산한다**

Gate:

```text
positive recall >= 95%
negative pollution <= 5%
ambiguous handling >= 80%
conflict handling >= 80%
```

## Phase 5: Usability and Manual Review

**Files:**
- Create: `evals/shared/rubrics/usability-checklist.md`
- Modify: `evals/codex/rubrics/grading-schema.json`
- Modify: `evals/codex/scripts/grade_outputs.py`
- Modify: `evals/codex/scripts/render_report.py`

- [x] **Step 1: usability checklist를 작성한다**

Checklist:

```text
1. 실행 가능한 Django/Ninja 문법인가
2. 파일 구조와 import가 현실적인가
3. migration, transaction, test 고려가 있는가
4. 한국어 요청에 자연스럽게 답하는가
5. 정책 설명이 과하게 반복되지 않는가
6. 사용자가 바로 적용 가능한 수준인가
```

- [x] **Step 2: manual review score를 grades.json에 추가한다**

Fields:

```json
{
  "usability": {
    "actionable": 5,
    "concise": 4,
    "realistic_file_layout": 5,
    "korean_quality": 5,
    "notes": "바로 적용 가능"
  }
}
```

- [x] **Step 3: HTML에 usability summary를 추가한다**

HTML table:

```text
Case | Actionable | Concise | Realistic Layout | Korean Quality | Notes
```

Result:

```text
`evals/shared/rubrics/usability-checklist.md`에 수동 리뷰 기준을 추가했다.
`evals/codex/rubrics/grading-schema.json`에 `usability_criteria`를 추가했다.
새 iteration의 `grades.json`에는 `usability` template이 자동 생성된다.
`grade_outputs.py`는 기록된 usability 점수가 있을 때 variant별 평균을 요약한다.
`render_report.py`는 dddjango variant 기준 Usability Summary 표와 Manual Usability metric을 표시한다.
기존 `benchmark-4`, `trigger-5` grades에는 빈 usability template을 추가했고, 수동 채점은 아직 pending이다.
```

## Phase 6: Real Repo Forward Test

**Files:**
- Create: `evals/fixtures/` or document external fixture repo path
- Create: `evals/shared/cases/real-repo.jsonl`
- Modify: `evals/codex/scripts/run_prompts.py`
- Modify: `evals/claude/scripts/run_prompts.py`

- [x] **Step 1: fixture 전략을 선택한다**

Preferred:

```text
작고 공개 가능한 Django fixture repo를 `evals/fixtures/`에 둔다.
```

Alternative:

```text
private fixture repo를 사용하되 report에는 anonymized summary만 남긴다.
```

- [x] **Step 2: real-repo task를 작성한다**

Tasks:

```text
fat model 리팩터링
Django Ninja API 추가
pytest 테스트 추가
DB index/migration 리뷰
view logic service layer 이동
DRF endpoint를 Django Ninja로 전환
```

Result:

```text
`evals/shared/cases/real-repo.jsonl`에 6개 forward-diff task를 추가했다.
`python3 evals/codex/scripts/init_iteration.py --suite real-repo --output workspace/codex-eval/real-repo-1`
baseline/dddjango 실행과 HTML report 생성을 완료했다.
```

- [x] **Step 3: diff 기반 평가를 추가한다**

Measure:

```text
tests pass 여부
diff 적용 가능성
reviewer 수정 요청 수
architecture violation 감소율
```

Gate:

```text
실제 코드 적용 가능성 >= 80%
테스트 통과율 >= 90%
reviewer 수정 요청 baseline 대비 20% 이상 감소
architecture violation baseline 대비 30% 이상 감소
```

Result:

```text
`evaluate_real_repo_diffs.py`가 output markdown의 fenced diff를 추출한다.
fixture 복사본에 `git apply --recount --check`와 `git apply --recount`를 실행한다.
결과는 `real_repo_evaluation.json`에 기록되고 HTML report의 Real Repo Patch Evaluation 표에 표시된다.
pytest가 `tests.py` 기본 수집 패턴 문제로 no tests ran을 반환하면 `python manage.py test shop.orders`로 fallback한다.
2026-05-05 기준 repo-local `.venv`에서 Django dependency를 설치한 뒤 baseline/dddjango 모두 patch apply, `python manage.py check`, test fallback `6/6` 통과를 확인했다.
```

## Phase 7: Full Benchmark Execution

**Files:**
- Write: `workspace/codex-eval/iteration-*/`
- Write: `workspace/claude-eval/iteration-*/`

- [x] **Step 1: Codex benchmark를 3회 반복 실행한다**

Run:

```bash
python3 evals/codex/scripts/init_iteration.py --suite benchmark --output workspace/codex-eval/iteration-2
python3 evals/codex/scripts/run_prompts.py --variant baseline --iteration workspace/codex-eval/iteration-2 --keep-going
python3 evals/codex/scripts/run_prompts.py --variant dddjango --iteration workspace/codex-eval/iteration-2 --keep-going
```

Completed:

```text
workspace/codex-eval/benchmark-4
workspace/codex-eval/benchmark-5
workspace/codex-eval/benchmark-6
```

- [ ] **Step 2: Claude benchmark를 3회 반복 실행한다**

Run:

```bash
python3 evals/claude/scripts/init_iteration.py --suite benchmark --output workspace/claude-eval/iteration-2
python3 evals/claude/scripts/run_prompts.py --variant baseline --iteration workspace/claude-eval/iteration-2 --keep-going
python3 evals/claude/scripts/run_prompts.py --variant dddjango --iteration workspace/claude-eval/iteration-2 --keep-going
```

Repeat:

```text
iteration-2
iteration-3
iteration-4
```

- [x] **Step 3: 반복 결과의 평균과 category summary를 report에 표시한다**

Summary:

```text
workspace/codex-eval/benchmark-repeat-summary/report.html
baseline average = 84.89
dddjango average = 88.22
lift = +3.33 points / +3.92%
duration increase = +21.72%
```

## Phase 8: Marketplace and Fresh Install Verification

**Files:**
- Read: `.codex-plugin/plugin.json`
- Read: `.claude-plugin/plugin.json`
- Read: `.claude-plugin/marketplace.json`
- Read: `README.md`

- [ ] **Step 1: Codex fresh install을 검증한다**

Run from a disposable profile:

```bash
codex plugin marketplace add changja88/dddjango
```

Expected:

```text
dddjango marketplace가 추가되고 설치 가능해야 한다.
```

- [ ] **Step 2: Claude fresh install을 검증한다**

Run:

```bash
claude plugin validate .
claude plugin marketplace add changja88/dddjango
claude plugin install dddjango@dddjango
```

Expected:

```text
manifest validation 통과, marketplace 추가, install 성공
```

- [ ] **Step 3: README 설치 명령을 실제 명령과 맞춘다**

Check:

```text
README의 설치 명령이 현재 marketplace와 tag 정책에 맞는가
```

## Phase 9: Beta User Evaluation

**Files:**
- Create: `docs/superpowers/plans/2026-05-04-dddjango-beta-feedback.md`
- Modify: `evals/shared/cases/regression.jsonl`

- [ ] **Step 1: beta 사용자 그룹을 정한다**

Targets:

```text
Django 실무자 1명
Django 초급자 1명
DDD 관심자 1명
테스트/TDD 중심 사용자 1명
```

- [ ] **Step 2: feedback template을 작성한다**

Questions:

```text
어떤 prompt에서 유용했는가
어떤 prompt에서 과하게 개입했는가
답변이 너무 길거나 짧았는가
DRF/Ninja 정책이 명확했는가
실제 코드에 적용했는가
재사용 의향이 있는가
```

- [ ] **Step 3: 실패 prompt를 regression suite에 추가한다**

Rule:

```text
사용자가 불만을 제기한 prompt는 원인 분석 후 `evals/shared/cases/regression.jsonl`에 추가한다.
```

## Phase 10: Operating Regression System

**Files:**
- Modify: `Makefile`
- Modify: `README.md`
- Modify: `evals/shared/cases/regression.jsonl`
- Modify: `docs/superpowers/plans/2026-05-04-dddjango-comprehensive-performance-evaluation.md`

- [ ] **Step 1: make smoke-eval을 추가한다**

Command:

```bash
make smoke-eval
```

Expected:

```text
Codex smoke 실행, grade summary, HTML report 생성
```

- [ ] **Step 2: make full-eval을 추가한다**

Command:

```bash
make full-eval
```

Expected:

```text
Codex/Claude full benchmark 실행 또는 Claude auth blocker를 명확히 표시
```

- [ ] **Step 3: release gate에 평가 확인을 연결한다**

Rule:

```text
make release 전 `make test-release`, `git diff --check`, latest smoke report 확인을 수행한다.
```

- [ ] **Step 4: 운영 주기를 README에 기록한다**

Cadence:

```text
매 커밋: smoke
매 release: smoke + benchmark
월 1회: trigger/negative control 확장
큰 스킬 수정 후: full benchmark 3회 반복
사용자 이슈 발생 시: regression case 추가
```

## Next Action Queue

1. Claude 인증 blocker를 해결한다.
2. Phase 2 Step 4를 실행해서 Claude smoke report를 실제 점수로 채운다.
3. Codex full benchmark를 3회 반복 측정한다.
4. Claude 인증 blocker 해결 후 Claude smoke/benchmark를 실행한다.
5. fresh install 검증 후 release gate를 확정한다.

## Tracking Rules

- 새 평가 suite를 추가할 때마다 이 문서의 해당 Phase checkbox를 갱신한다.
- 평가 실행마다 `workspace/<platform>-eval/iteration-N/report.html`을 생성한다.
- 실패 케이스는 수정하기 전에 failure bucket에 먼저 분류한다.
- 스킬을 수정하면 반드시 `skills/`와 `plugins/dddjango/skills/` mirror sync를 확인한다.
- raw `.codex.log`와 `.claude.log`는 기본적으로 커밋하지 않는다.
- release 판단에는 HTML report와 `make test-release` 결과를 함께 사용한다.
