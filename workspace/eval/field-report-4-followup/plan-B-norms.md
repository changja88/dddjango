# 현장 보고 4 잔여 12건 — 독립 계획 적대 리뷰 B(규범·절차)

2026-09-11 · 검토자 B · 구현 전 계획 리뷰.

판정은 **보완 후 재대조 필요: B 0 / M 3 / m 0**이다. 세 MAJOR는 이미 합의한 방향을 실행 가능한 규칙·입력·처분·전파면으로 닫는 기술 보완이다. **새 사용자 정책·범위 결정이 필수인 사항은 0건**이다. 보완을 구현 단계로 미룬 채 현재 계획을 승인하지 않는다.

검토한 계획은 `workspace/plan/2026-09-11-field-report-4-followup.md`, SHA-256 `bc3e95b7d0146e917ecbbe70ab5e69fee95cbfb26ed3020a9beb0e7dc5eccdad`다. 요구 정본은 `brief.md`, SHA-256 `4300add6298ba17d3ecb89ee249e8afd6043644209b2af770faff86282908437`다. 아래 행 번호는 이 계획 판본과 검토 시점 실제 파일 기준이다.

## 1. 검토 방식과 한계

`brief.md`, 문제 리뷰 A/B/C(특히 `problem-B-norms.md`), 원 보고서, `docs/DEVELOPMENT.md`, `workspace/tools/ontology-authoring.md`, 관련 TTL·배포 규범·검사기·현행 대장·술어·Make 검증 경로를 읽고 대조했다. F9는 현재 사용 프로젝트의 `application/fortune_character/driven_layer/django_fortune_character/admin/character/panel.py`도 읽었다.

증거는 **정적 원문·구현 대조**다. 새 구현이 없는 계획 단계이므로 미래 기능 테스트 통과나 원 현장 실행 재현을 주장하지 않는다. 검사기·규범·계획·원 보고서·영구 테스트는 수정하지 않았다. 이 리뷰 문서만 작성했다.

## 2. MAJOR 지적

### PB-M1 — F1의 두 번째 #197 판정에 read-only 선행조건이 빠져 있다

**대상:** 계획 Task1:80–81 및 :106, Task6:281. 현행 규칙은 `workspace/design/2026-08-08-tree-revision-spec.md:526`의 “읽기 전용 유스케이스는 UnitOfWork를 받지 않는다”다.

계획은 첫 문장에서 `read-only + uow != none`을 #197 확정으로 두지만, 이어지는 `uow=none`과 생성자/필드의 확인된 UoW 주입 불일치도 #197 확정이라고 적는다. 이 두 번째 조건에는 `effect == read-only`가 없다. 문자 그대로 구현하면 다음 선언도 읽기 전용 규칙 위반이 된다.

```text
SaveBookUseCase  write  uow=none
SaveBookUseCase.__init__(uow: 명시 import로 확인된 BookUnitOfWork)
```

여기에는 효과 선언과 주입 선언의 불일치가 있지만, write가 읽기 전용이라는 근거는 없다. 선언 불일치를 #197에 합치면 사용자가 요청한 “명시 read-only × UoW” 검증 범위를 넘어 정상 쓰기 유스케이스에 확정 차단을 발행한다. “write에 uow 없음 자체를 새 오류로 만들지 않는다”는 마지막 문장만으로 주입이 함께 있는 경우의 처분은 닫히지 않는다.

**최소 보완:** #197 확정의 모든 경로에 `effect == read-only`를 명시한다. write와 `uow=none`/실제 명시 주입의 모순은 별도 선언 후보 또는 채널 메모로 남기고 #197 확정으로 승격하지 않는다. 명시 write+UoW 정상, write+none+UoW 선언 불일치, read-only+none+UoW 확정을 각각 literal 기대값으로 대조한다. 선택형 입력의 무기재 S5 정책은 유지한다.

**추가 사용자 결정:** 불필요. 기존 #197과 `brief.md` F1의 주어를 보존하는 기술적 한정이다. 코디네이터는 이 보완 방향을 수용했으며, 본 리뷰 판본에 반영·검증됐다는 뜻은 아니다.

### PB-M2 — F9의 불명 후보 처분과 실제 열린 context 사례를 판정 계약에 끝까지 연결해야 한다

**대상:** 계획 Task3:155–161, :164–173, Task6:281. 실검사 근거는 `check-public-surface-annotation.py:715–793`이다.

계획의 다섯 규칙 표 자체는 합의와 일치한다. 그러나 인터페이스는 `_admin_context_exemptions(...) -> set[int]`로 허용할 annotation만 반환하고, 문면은 “framework와 연결됐지만 흐름 불명인 경우 #645/#647 후보 유지”를 요구한다. 현행 `judge`는 bare signature Any와 dict 값 Any를 확정 위반으로 내보내므로, 단순 면제 집합만으로는 다음 세 상태를 구별하지 못한다.

1. framework 소유와 단순 조립·전달이 확인돼 허용할 annotation.
2. framework 연결은 확인됐으나 본문 흐름이 불명이라 후보로 남길 annotation.
3. 업무 소비가 확인됐거나 framework와 무관해서 현행 규칙을 그대로 적용할 annotation.

집합에 없다는 이유로 ②를 현행 확정으로 두면 계획 문면과 달라지고, ②까지 집합에 넣으면 불명 흐름이 조용한 통과가 된다. 생성 private helper의 S1과 실제 코드의 불명 후보도 서로 다른 근거다.

또한 원형 fixture를 “override→private helper→update→render”라는 호출 모양만으로 축약하면 현장 사례를 닫았다는 증거가 부족하다. 현재 `panel.py:220–243`의 context에는 다음 UI 조립이 실재한다.

- `request.GET.get(SOURCE_MODEL_VAR)` 및 `request.POST.get(TO_FIELD_VAR, ...)`를 UI context 값으로 전달.
- request POST/GET membership 결과를 `is_popup` UI 플래그로 전달.
- `context.update(extra_context or {})`로 선택형 extra_context 병합.
- 같은 helper 안에 form/inline/media 구성과 UI 표시 처리가 함께 존재.

계획 :160의 “request/cleaned_data/JSON 추출 값은 실제 소비” 또는 :159의 “helper에서도 위 조립/전달만 수행”을 함수 전체·컨테이너 전체에 적용하면 이 정상 원형을 다시 제외한다. context 컨테이너의 열린 전달과, 특정 값의 업무 소비를 구별해야 한다. UI request metadata를 framework에 전달한다는 사실만으로 전체 context annotation을 업무 dict로 취급해서는 안 된다. 이 한정이 JSON 무검증이나 업무 인자 전달까지 허용한다는 뜻도 아니다.

추가로 실제 `panel.py:14,105`는 `parler.admin.TranslatableAdmin`을 import해 직접 상속한다. 로컬 설치 소스 `/Users/hyun/Desktop/spring_dream_server/.venv/lib/python3.14/site-packages/parler/admin.py:41,173`에서 `django.contrib.admin` module binding과 `TranslatableAdmin(BaseTranslatableAdmin, admin.ModelAdmin)`을 확인했다. Task3가 직접 Django base import/같은 파일 alias만 지원하면 이 원형은 framework 클래스라는 출처 증명을 얻지 못한다. `TranslatableAdmin`이라는 이름만 예외에 넣는 것도 출처 검증이 아니다.

**최소 보완:** annotation별 `allow / candidate / ordinary` 또는 동등한 세 상태와 근거를 반환하도록 판정 계약을 고친다. `ordinary`는 현행 #645/#647 처분, `candidate`는 exit 불산입과 확인 질문, 생성 provenance의 S1은 별도 근거로 명시한다. 판정은 해당 context 값의 흐름에 한정하고, None guard/fallback·UI metadata의 렌더 전달을 단순 조립 범위에 명시한다. 실제 외부 base의 정확 module origin과 확인 가능한 소스의 상속 연결을 해소하는 지원 계약도 적는다. 소스 결손·동적 base·rebind는 임의 framework 확정으로 바꾸지 않는다. 원형 fixture에 parler 경유 base와 위 실제 조립을 포함하고, 같은 함수의 업무 dict·JSON 실제 소비·context 값을 use case/ORM 인자로 보내는 대조가 계속 검사되는지 확인한다.

**추가 사용자 결정:** 불필요. framework 열린 context를 허용하면서 업무 경계를 유지하라는 기존 F9 결정을 구체화한다. 코디네이터는 세 상태 계약, 원형의 UI 조립·None fallback, 외부 base의 소스 증거 해소를 기술 보완으로 수용했다. 수정된 계획의 재대조는 아직 별도다.

### PB-M3 — Task6에 현행 술어와 후보 소유·집계 전파면이 빠져 있다

**대상:** 계획 Task6 Files:258–271, Step3–4:294–295. 추가 필수 경로는 `workspace/design/2026-08-11-predicates.md`다.

계획은 현행 spec과 owner-map을 지정했지만, 현행 술어 문서를 지정하지 않았다. 이 문서는 단순 과거 기록이 아니라 `workspace/tools/spec_lint.py:46`의 `PRED_REL` 입력이다. 다음 직접 충돌이 남는다.

| 전파면 | 현재 원문 | 계획과 충돌하는 이유 |
|---|---|---|
| predicates:245 #645 | “프레임워크 계약이라도 우리 선언은 object” | F9가 승인하는 framework 슬롯의 제한 Any 허용과 충돌 |
| predicates:247 #647 | 모든 자리 dict 값 Any 확정, object 반환·속성 확정 및 기존 면제 목록 | 새 admin 허용·불명 후보 경계가 없음 |
| predicates:244 #644 | 형태 확정은 `#638~#643` 소유 | 폐지하는 #642를 계속 현행 형태 조건에 포함 |
| spec:816 #490, :1173 #644 | 동일 `#638~#643` 범위 | #642 행만 제거해도 살아 있는 설명에 하한 규칙의 범위가 남음 |
| spec:868 #546, :879 #557 / owner-map:464, :475 | `ast`, 검사기 소유만 있고 감수자 소유 없음 | Task4는 불명 거래 경계/출처를 후보로 발행하므로 후보의 마무리 물음·소유가 생김 |

`spec_lint.py:258–281`은 술어의 생존 번호와 grade 일치, ast+ 행의 “후보/물음”을 검사한다. :290–329는 실제 grade/어겼을 때 집계와 “읽는 법” 수치를 대조하고, :350–376은 spec/owner-map의 1:1 및 ast+의 검사기+감수자 소유를 대조한다. #642를 폐지하거나 #546/#557을 ast+로 맞추면 관련 집계도 함께 바뀐다. 특히 `#638~#643`은 현재 lint가 끝 번호만 인식하는 문자열 범위이므로 lint green만으로 폐지 #642의 의미상 잔존이 없다고 주장할 수 없다.

**최소 보완:** Task6에 predicates 파일을 명시하고 F9의 #645/#647 예외·불명 처분, F14/F15의 #546/#557 확정/후보/물음 및 감수자 소유를 함께 정합화한다. #546/#557의 grade는 현행 ast+ 계약에 맞추고 spec/owner-map/술어를 같은 범위로 맞춘다. #197/#202의 새 pre-gate 후보도 어느 역할이 마무리하는지 기록해 소스 실검사의 기존 판정 범위와 구별한다. #490/#644와 predicates #644의 범위 참조는 `#638~#641·#643`처럼 남은 규칙만 가리키게 한다. #642 폐지 및 grade 변경에 따른 현행 집계·읽는 법 수치도 계산 결과로 맞추고 `python3 -B workspace/tools/spec_lint.py`를 명시 검증에 넣는다. 과거 완료 기록 전체의 전역 치환은 하지 않는다.

**추가 사용자 결정:** 불필요. 승인된 규칙 변경의 현행 전파·소유권 유지다. 코디네이터가 지적한 추가 전파면을 실제 파일과 lint 구현으로 독립 대조해 확인했다.

## 3. 12건의 정책 일치 판정

| 항목 | 계획 판정 | 근거와 남은 조건 |
|---|---|---|
| F4-1 | 보완 필요 | 선택형 effects, 명시 update 선언 보존, marker 최종 목록/빈 목록/무기재, case/class update S5, hash·실체화0·report 범위는 구체적. PB-M1의 #197 주어 한정 필요 |
| F4-9 | 보완 필요 | #493/#646/#650 유지, #645/#647 제한 완화, private helper·S1·업무 경계 방향 적합. PB-M2 판정 계약 및 PB-M3 현행 술어 전파 필요 |
| F4-10 | 적합 | 표준 builder 준비/실행 분리, alias/rebind/0·2/일반 execute/nested 대조, 실제 복수 실행 후보 및 별도 #153 확정 보존 |
| F4-11 | 적합 | 표준 닫힌 Enum만 인정하고 custom 동작·Flag·rebind 후보 유지. #264/#259 보존 |
| F4-12 | 적합 | 정확한 생성 after_commit provenance만 #376→S1. 기존 본문·다른 위치·#566·실행 오류 보존, 실제 CLI 대조 포함 |
| F4-13 | 적합 | 6개 raw 문면 지정, 이미 잡은 IntegrityError의 내부 정규화와 공개 safe 500 구별, 실패 계약 소유·관찰 후 재던짐·catch-all 금지 보존 |
| F4-14 | 전파 보완 필요 | 순차/중첩/외부 atomic/불명 구간을 구분하고 범위 밖을 확정하지 않음. PB-M3 후보 소유·술어/grade 동기화 필요 |
| F4-15 | 전파 보완 필요 | domain/vendor/unknown 3분류, exact origin 및 except 비증거, 좌·우·chained 비교 대조 적합. PB-M3 필요 |
| F4-16 | 전파 보완 필요 | 승격 술어와 출생 하한 모두 제거, R-3410의 #643·200행·감사/참조 조사 보존. PB-M3의 술어/번호 범위/집계까지 포함해야 완전 폐지 |
| F4-17 | 적합 | 실제 트리의 캐시뿐인 optional instance만 제외, untracked source/empty init/고정 골격 보존, snapshot 전 판정과 원본 무삭제 명시 |
| F4-18 | 적합 | 모듈+심볼 identity, 명시 imports/qualified/alias/forward/container/private DTO 추적, 불명 후보, value_object 허용, update 선언 범위·실체화0·hash/report 명시. OHS 가짜 domain import 금지 유지 |
| F4-19 | 적합 | 초기/명시 재예보와 12조합 exit 보존, baseline/overlay 원인 분리, 자동 초기 add 허용·자동 commit/stash·작업기록 일괄삭제 금지 |

F1의 case/class 주소를 S5로 남기는 한정은 **marker update 지원 범위**로 이해했다. 기존 add의 `.py::case` 물리 신호 결합까지 바꾸는 일반 정책으로 확장하지 않아야 한다. 이는 새 case/class update 구현을 요구하는 지적이 아니다.

## 4. 정본 좌표와 명령 경로 확인

계획에서 구체 경로로 추출 가능한 30개 literal path는 모두 존재했다. 네 smoke/fixture, ontology gate/render/corpus sync/manifest seal/spec lint 및 `.venv/bin/python`도 존재한다. 명령의 경로 존재와 인자 정의를 확인했으며, 이 리뷰에서 `--apply`, `--write`, `make rulepack`, 검증 스위트를 실행한 것은 아니다.

| TTL stem | 계획이 지목한 Work의 실제 소유 블록 |
|---|---|
| agent-design-architect | R-1617=`s005/b11`; R-3424/R-3431=`b33`; R-3425=`b34`; R-3426=`b35`; R-3427=`b36`; R-3428/R-3429=`b37` |
| command-dddjango | R-3432~R-3436=`s006/b9`; R-3445=`s006/b10` |
| discipline-houserules-skill | R-3417=`s004-1/b7`; R-3447/R-3448=`s007-4/b7`; R-3451=`b8`; R-3452=`b10`; R-3457=`b15`; 유지 R-3458/R-3459=`b16` |
| discipline-houserules-final | R-3410=`s003-0/b10`; R-3468=`s003-0/b12` |
| agent-discipline-reviewer | R-1037=`s007/b23`; R-1071=`b29`; R-1117/R-1118=`b51` |
| agent-design-review-api | R-2677=`s006/b11` |
| implementation-django-ninja-final | R-0084=`s023-6.2/b33` |
| implementation-django-ninja-skill | R-2941=`s004/b10` |

F13의 raw 정규화 제한 6문장은 실제로 각 지목 Work의 블록에 존재한다. F16의 두 하한은 R-3417의 “술어 둘 다/개별 50행”과 R-3410의 출생 하한으로 분리돼 있으며, 계획은 둘 다 제거하도록 지정했다. R-3410 전체 삭제·ID 재사용 없이 #643를 보존하고 label/currentExpression을 개정한다는 처분은 적합하다. `docs/file_tree.html:3296,3304`와 생성원 `docs/mkrev2.py:6679,6687`의 현행 설명까지 지정했고, 트리 50번 행 참조나 함수 길이 smell50은 유지한다.

Task1/6은 효과 블록 부재 시 기존 hash 알고리즘 보존, 존재 시 새 원문 포함, S2의 명시 모순 예외, S3/S5의 update 지원 범위, 확정/후보/report-check 구분을 함께 다룬다. F19의 R-3445 변경에서는 현재 남은 “미커밋 WIP는 커밋 또는 stash 후 실행” 문구가 Task2의 무조건 처방 금지와 충돌하지 않도록 같은 소유 블록에서 정합화해야 한다. 원래 baseline/overlay 판정 정책 자체를 바꿀 근거는 없다.

## 5. 절차 판정과 종료 조건

TTL → 저작 게이트 → render → rulepack → corpus/byte/의미 미러의 순서가 `docs/DEVELOPMENT.md` §3–5와 일치한다. NAR를 실제로 바꿀 때만 LEDGER append, 기존 Work 개정과 신규 Work 채번 구별, 표준 라이브러리 배포 경계, `make verify-mutation`, 마지막 봉인 뒤 `make verify`, 변경 시 재봉인·재검증도 계획에 있다. manifest/설치구조 변경 시에만 plugin validate를 실행하는 한정도 적합하다.

최소 닫힘 조건은 PB-M1의 read-only 진리표, PB-M2의 annotation 세 상태와 실제 UI 조립 대조, PB-M3의 predicates/grade/owner-map/번호 범위/집계 전파를 계획에 반영한 뒤 재대조하는 것이다. 이후 구현 검증에서 각 항목의 의도된 진단 삭제와 보존 진단을 입증한다. 전체 검출 집합 동일을 성공 조건으로 되돌리지 않는다.

**사용자 재결정 없이 보완 가능하다.** 검토 범위의 기술 계약을 구체화한 뒤 같은 단계 안에서 재리뷰하면 된다. 이번 리뷰가 구현 완료나 원 보고서 항목 삭제 승인을 대신하지 않는다.

Serena/Graphify는 현재 worktree에 opt-in 표식이 없다는 배정 조건에 따라 검색·로드·초기화 없이 생략했다. 추가 위임 없음.

## 6. 계획 v2 한정 재대조 — 2026-09-11

재대조한 계획 SHA-256은 `a3b0ebb2b309f901afc20d48adee8252e46b1f9cb7ab363c3503b64f82b317c8`이다. 요청에 따라 PB-M1/M2/M3의 수정과 직접 관련된 새 모순만 확인했다. 전체 신규 리뷰·구현 검증을 수행한 것은 아니다.

| 지적 | 처리 상태 | 재대조 근거 |
|---|---|---|
| PB-M1 | **ADDRESSED** | Task1:82에서 #197 확정의 모든 경로에 `effect == read-only`를 명시했다. write+명시 UoW는 정상, write+none+명시 주입 불일치는 비차단 채널 메모로 한정했다. :107–108에 세 경우의 대조와 실제 CLI exit/report 검증을 넣었다. |
| PB-M2 | **ADDRESSED** | Task3:159에 annotation별 allow/candidate/ordinary와 근거, 실제 업무 소비는 현행 검사로 유지하는 계약을 추가했다. :161은 출처를 확인한 Parler 4종을 좁게 인정하고 이름-only·rebind·임의 외부 import/MRO 실행을 제외한다. :163–165는 함수 전체가 아닌 context binding/값 흐름으로 판단하며 UI request metadata·None guard/fallback·form/inline/media 조립을 허용하고 실제 업무 소비·JSON 검사를 유지한다. :166은 생성 슬롯의 원본 record/구체 슬롯 일대일 결합과 실패 시 원진단 유지를 명시한다. :169의 fixture는 Parler 경유 실제 원형과 반대 대조를 포함한다. |
| PB-M3 | **ADDRESSED** | Task6:278에 predicates 파일, #645/#647의 새 처분, #546/#557의 ast+·검사기+감수자 소유·확정/후보/물음, #197/#202 선언 후보의 설계 처분을 포함했다. :289는 spec #490/#644와 predicates #644의 폐지번호 범위 제거, grade/폐지에 따른 집계·읽는 법 실측 갱신을 명시한다. :304에 `spec_lint.py` 검증 경로를 포함했다. |

PB-M2의 새 정적 origin 목록은 현재 설치 소스 `parler/admin.py:173,624,705,719`에서 직접 대조했다. 네 클래스의 실제 상속 연결은 계획의 주장과 일치한다. 이 증거를 임의 동명 클래스나 소스가 불명한 모든 외부 base의 포괄적 허용으로 확대하지 않는 한정도 계획에 있다. Task1:108은 기존 add의 nodeid 결합을 유지하며 새 제한을 update에만 적용한다고 명시해 최초 리뷰의 보존 조건도 닫았다.

**잔여 B 0 / M 0 / m 0 · NOT ADDRESSED 0 · 사용자 결정 필수 0.** 이번 한정 재대조에서 수정으로 새로 생긴 정책·정본 전파 모순은 발견하지 않았다. 세 지적은 계획 수준에서 닫혔다. 실제 구현·규범 반영·기능 테스트 통과 및 보고서 항목 삭제의 증명은 계획에 정한 구현 리뷰와 최종 검증에서 확인해야 한다.

추가 실행은 계획 및 관련 소스의 읽기와 이 절 append에 한정했다. Serena/Graphify는 opt-in 부재로 계속 생략했고 추가 위임은 없다.
