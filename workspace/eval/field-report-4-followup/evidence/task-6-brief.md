### Task 6: 규범·현행 문서·미러 정합화 (F4-1/9/13/16/18/19)

**Files/좌표:**
- `ontology/rules/agent-design-architect.ttl`: `s005/b33~b37` R-3424~R-3429/R-3431(채널·명시검증·후상태·사각), `s005/b11` R-1617(내부/외부 오류 분리).
- `ontology/rules/command-dddjango.ttl`: R-3432~R-3436/R-3445(새 hash·미검증·모드). 실제 doc_key/Work를 원문으로 확인하고 존재하지 않는 블록을 만들지 않는다.
- `ontology/rules/discipline-houserules-skill.ttl`: R-3447/R-3448/R-3451/R-3452/R-3457(admin), R-3417(승격 50행 제거). R-3148~R-3154/#493·R-3458/R-3459/#646·#650 유지.
- `ontology/rules/discipline-houserules-final.ttl`: R-3410의 50행 부분만 삭제하고 #643 유지, R-3468의 없어진 하한 비교 문구 정리.
- `ontology/rules/agent-discipline-reviewer.ttl`: R-1117/R-1118(admin 처분), R-1037/R-1071(내부 실패/HTTP), Enum Q2·#546/#557 관련 판정이 새 확정/후보 범위와 충돌하면 해당 문장만 정합화.
- `ontology/rules/agent-design-review-api.ttl`: R-2677.
- `ontology/rules/implementation-django-ninja-final.ttl`: R-0084.
- `ontology/rules/implementation-django-ninja-skill.ttl`: R-2941.
- `workspace/design/2026-08-08-tree-revision-spec.md`: 현행 #192/#642/#645/#647/#546/#557/#197/#202 적용범위 설명.
- `workspace/plan/2026-08-11-rule-owner-map.md`: 현행 #642 폐지, #645/#647/변경 검사범위의 소유 설명.
- `workspace/design/2026-08-11-predicates.md`: #645/#647 admin 허용·후보·기존규칙, #546/#557의 확정/후보/물음. #546/#557은 spec/owner-map/술어를 `ast+`·검사기+감수자 소유로 동기화한다. 새 #197/#202 선언 후보는 architect·해당 설계 리뷰/감수 처분이며 실코드 검사 범위와 구분한다.
- `docs/file_tree.html`, `docs/mkrev2.py`: 승격 50행 하한과 고정 adapter의 50행 비교 문구만 수정. `docs/master.html` 제외.
- 렌더된 Claude/Codex 역할·SKILL·reference, `workspace/reference/**`, 양쪽 `rulepack.json`; 필요한 ledger/census seal.
- Test: `workspace/tools/field_report_checker_smoke.py`의 규범 계약 대조와 이 작업 리뷰 기록.

**F13 문면의 결과(6중복에 같은 의미 적용):**

> 이미 잡은 IntegrityError의 승인된 알려진 제약 실패는 구체 계약 예외로, 나머지는 승인된 일반 저장소 실패 계약으로 번역한다. repository 실패 계약은 domain 소유, capability port 실패 계약은 해당 port 소유다. 이 내부 정규화는 공개 HTTP 오류 승인이 아니므로 일반 저장소 실패의 외부 응답은 기존 safe 500을 유지한다. 새 ErrorCode/ErrorSchema/4xx/503을 만들지 않는다. 잡지 않은 unknown 인프라 오류를 새로 catch-all하지 않는다. 안정된 public meaning이 별도로 승인된 경우에만 그 외부 계약에 맞는 controller mapping을 한다. 이미 선언된 계약 예외의 관찰 후 재던짐은 허용한다.

F13은 #555/계약 예외 소유를 약화하지 않는다. 검사기 변경이 필요 없는 규범 수리이며 exception-map을 catch DSL로 확장하지 않는다.

**F16 현행 대장:** #642를 현행 시행 규칙으로 남기지 않고 대장의 기존 폐지 표현을 따른다. spec #490/#644와 predicates #644의 `#638~#643`을 `#638~#641·#643`으로 맞춰 폐지한 번호의 의미상 잔존도 없앤다. #642 폐지와 #546/#557 grade 변경에 따른 현행 집계표·읽는 법 수치는 실측으로 맞춘다. R-3410 Work 전체를 삭제하지 않으며 기존 ID/ISSUED 이력 보존. R-3417/R-3410 label/currentExpression은 남은 의미로 개정한다. 다른 ‘트리 50행’/함수길이 smell50은 유지한다.

**F1/F18/F9/F12 문면:** 선택형 6번째 입력(use-case-effects, 기존 다섯 채널+효과)을 선언하고 hash 문면을 맞춘다. S2의 ‘내부 모순 전부 사각’은 명시 read-only/UoW와 출처 결합 DTO에 한해 축소한다. S3/S5는 명시 후상태 지원과 기존 본문 미검증을 분리한다. 생성 메서드의 S1은 실제 구현 검증을 대신하지 않는다. F9는 Task3의 다섯 규칙 표·private 전달 helper·실제 소비 경계를 architect와 감수자가 같은 뜻으로 적용한다.

- [ ] **Step 1:** 규범 시나리오의 전후 기대 처분을 기록한다: admin 화면 조립 허용/업무 소비 검증, IntegrityError known→concrete/unknown→일반 내부 계약+500, 20행 응집 부품 허용/부품0 환원, read-only+UoW 모순/미기재 미검증. 기존 문면에서 반송/모순되는 직접 문장을 대조한다. 문구 grep만으로 역할 수행을 증명했다고 주장하지 않는다.
- [ ] **Step 2:** 기존 Work 리터럴을 최소 개정하고 새 Expression을 저작 규약대로 연결한다. 새 독립 의무가 꼭 필요할 경우에만 ISSUED 마지막 번호 뒤 채번한다. TTL을 정본 직렬화하고 게이트를 통과한다.

```bash
PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_gate.py
for doc_key in agent-design-architect command-dddjango discipline-houserules-skill discipline-houserules-final agent-discipline-reviewer agent-design-review-api implementation-django-ninja-final implementation-django-ninja-skill
do
  PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_render.py --apply "$doc_key"
done
make rulepack
python3 workspace/tools/corpus_mirror_sync.py --write
python3 -B workspace/tools/spec_lint.py
```

위 여덟 doc_key의 소유 블록을 개정한다. 통째 재생성·중복 문장 추가로 범위를 넓히지 않는다.
- [ ] **Step 3:** 현재 사람용 문서/생성원/대장과 의미 미러를 맞춘다. NAR을 바꾼 경우 해당 SHA와 사유를 LEDGER에 append한다.
- [ ] **Step 4:** ontology gate/render sync/structural/spec lint·관련 smoke를 실행하고 규범 리뷰로 여섯 raw 문면과 F9/F16 전파를 확인한다.


## Global Constraints (verbatim)

- 사용자가 승인한 범위는 문제 검증 → 계획 적대 리뷰 → 결정 필요 없으면 구현 → 구현 독립 리뷰 3인 → 독립 최종 감사·필수 검증이다. 새로운 정책·범위 선택이 필요하면 계획 리뷰 후 보고한다.
- 현재 변경과 직접 관계없는 사용자 프로젝트, `docs/master.html`, 과거 완료 계획·리뷰는 변경하지 않는다. 보고서는 실제 검증 완료 항목만 제거한다. 커밋·릴리즈는 이 계획의 실행 단계에 넣지 않는다.
- `docs/DEVELOPMENT.md`가 개발 절차 정본이다. graph-owned md 직접 수정 금지. TTL → 저작 게이트 → render → rulepack → corpus/byte/의미 미러를 따른다. NAR 변경 시와 기존 render-sync가 요구하는 개정 graph 절의 기준선에만 LEDGER append, 새 Work가 실제 필요할 때만 ISSUED 채번.
- 설치본 의존성은 표준 라이브러리만. 검사기와 공용 스크립트는 `dddjango/scripts/`와 `codex-dddjango/skills/dddjango/scripts/` byte 동일. reference는 corpus mirror, 역할·SKILL은 플랫폼 형식을 유지한 의미 미러.
- Serena·Graphify opt-in 없음. 검색·로드·초기화하지 않는다. 실사용 spring_dream_server는 읽기만 하며 검사/테스트는 임시 사본에서 실행한다.
- 실제 확인한 출처와 추정을 구분한다. 이름·폴더·except 구문만으로 의미를 확정하지 않는다. 지원 밖 동작은 후보 또는 명시 사각이며 통과 증명이 아니다.
- 먼저 실패하는 동작 테스트를 확인한다. 기존 미러·소성·형식 검사만으로 새 검출 동작을 증명하지 않는다. 전체 검출 집합 보존을 요구하지 않고 아래 항목별 삭제·보존 집합을 검증한다.
- 각 작업의 구현을 검토해 중대한 결함을 닫고 다음 작업으로 간다. 세 작업이 같은 공용 파일을 병렬 편집하지 않는다. 구현 담당자와 리뷰 담당자는 분리한다.


## Start gate, canonical process and current-source descriptions
No implementation before coordinator dispatch after Task5 independent gate. Read docs/DEVELOPMENT.md and workspace/tools/ontology-authoring.md; use graph Work/currentExpression rules and canonical serialization, never edit graph-owned Markdown directly. Preserve existing user docs/master.html. Task1–5 reports/briefs describe implemented support; final review-approved versions will be supplied.
Task4 intentionally deferred its top-level checker descriptions. During this Task6 normative alignment, make only the corresponding docstring/comment updates in check-context-isolation.py (#153 header currently29–30: count0/2 omits unknown/multiplicity), check-domain-model.py (#268 header27, #546 ast header53–54 and honesty description63–64), check-port-adapter-pairing.py (#557 header38), and their byte mirrors. Update actual grade/range/known-vs-candidate limitations, not behavior. This is the directly necessary source-description counterpart of current spec/predicate/owner-map alignment; no new AST scope.
Primary unresolved report received F4-20/#195 during work. It is outside12 approved directions and remains pending; no fix or deletion for it. Report cleanup belongs only Task7 after final audit, using current primary content (initial frozen report is stale).

Task4 review deferred diagnostic wording: check-domain-model.py::_check_value_object_file currently (pre-fix1 line541) emits #268 "__init__/__post_init__ 에 raise 가 없다" even for custom/open Enum whose initializer actually contains raise. During Task6 text alignment distinguish unsupported/open Enum construction from absent ordinary VO validation, retaining the same #268 grade/verdict and byte mirror. Add a focused actual checker diagnostic-message assertion for this distinction in the already-owned checker smoke; no new enum policy.


## Implemented support handoff
Task1–5 code is now present. For exact parser/record/annotation interfaces use the actual code and relevant task-N-report.md targeted sections; earlier reports include later fix appendices. Checkersmoke baseline41 and pregatesmoke36. Task4 review approved after fix3; Task5 source frozen for review (do not start until explicit dispatch). Source headers and #268 reason are your assigned text-only alignment; cache/promotion actual behavior is already Task5. Snapshot task-6-before owns42paths, task-6-start-tracked-hashes.json guards other paths. If generated census/normalization metadata is directly required beyond42, tell coordinator exactpath/reason before edit so baseline can join review package. No seal until finalTask7, no unrelated source or fixture expectation changes.

Task6 directlynecessary report-description counterpart added: design_pregate.py BLIND_SPOTS S2/S3/S5 constants andbyte mirror (2paths). Existingtext contradicts implementedexplicitdeclarations/markerpoststate; text-only alignment, noASTbehavior. Snapshot44 now; no userpolicychoice.

Task6 Ruling: append2source-addressmetadata rows for houserules-final/s003-0 and ninja-final/s023-6.2 — prior migrated_sha256 is missing and newbaseline breaks corpus source-span addressing. Root verified unchangedsourcebytes vsTask6snapshot and uniqueoldbaseline spans. Setmissingfield to verifiedpreTask6sourcehash, preserve existingrealhashes/history; do notclaim originalmigrationdate. Ifwrong costisrevisiting2metadataappendrows; frozen sourcefilesremainunchanged, no toolweakening.
