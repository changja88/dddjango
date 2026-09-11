# 현장 보고 4 잔여 12건 — 독립 문제 적대 리뷰 B(규범)

2026-09-11 · 기준 HEAD `3355710dcbaf023a16856cb2f307aa2a03fc0996` · 검토자 B.

검토 입력은 이 디렉터리의 `brief.md` 사용자 결정 12건, 원 보고서, `docs/DEVELOPMENT.md`, `workspace/tools/ontology-authoring.md`, 관련 TTL·Claude 배포 프롬프트·검사기·현행 규칙 대장이다. 이 문서의 증거는 **직접 읽은 정적 구현과 규범 대조**다. 원 보고서의 현장 실행을 재현했다고 주장하지 않는다. 구현·규범·원 보고서는 수정하지 않았다.

심각도는 이번 계획 진입 전에 해결해야 하는 문제 범위의 중요도다. `B`는 방향을 막는 선행 결정, `M`은 계획에서 반드시 닫을 기능·정합성 문제, `m`은 낮은 영향의 후보 소음·안내 문제다. 새 사용자 결정이 반드시 필요한 `B`는 발견하지 않았다. 아래 `M`은 구현 전에 계획과 계획 리뷰에서 해결해야 한다.

## 1. 판정 요약

| 항목 | 판정 | 심각도 | 정적 근거·규범 좌표 | 필요한 계획 범위 |
|---|---|---|---|---|
| F4-1 | 지원 범위 확장 + 명시 입력 계약 보완. 기존 실검사 규범은 유지 | M | architect `s005/b33,b35,b37` (`R-3424/R-3431`, `R-3426`, `R-3428/R-3429`), `design_pregate.py:42-72,524-612,693-728`; 현행 대장 #197:526·#387:704 | read-only와 UoW 선언의 명시 대조; update 테스트 마커의 대상·추가/제거/유지 의미; 새 입력의 hash·사각·프롬프트 동기화 |
| F4-9 | 규범 완화. 현재 #647 후보는 기존 규범 문면에 따른 것이지만 사용자 결정으로 정책을 고쳐야 함 | M | houserules SKILL `s007-4/b1,b5,b7,b8,b10-b16`; checker `check-public-surface-annotation.py:5-58,1146-1169` | #493/#645/#646/#647/#650 각각의 유지/완화 표; admin framework 연결 슬롯과 실제 값 소비 경계; architect·pre-gate·감수자·실검사 일치 |
| F4-10 | 구현상의 후보 계수 오류 | m | `check-context-isolation.py:442-452`; 대장 #153:477 | 실제 표준 composition builder의 반환 use case 실행을 연결해서 센다. 이름만 build인 호출·일반 execute·실제 복수 실행을 구별 |
| F4-11 | 기존 후보 정책의 정밀화. '모든 StrEnum 후보가 결함'이라는 일반화는 기각 | m | `check-domain-model.py:482-486`; 대장 #268:590; 감수자 `discipline-reviewer.md:119`의 Q2 | 표준 닫힌 Enum 출처·별칭·재정의·`_missing_` 등 사용자 동작을 확인한 경우에만 후보 제거 |
| F4-12 | pre-gate 스텁과 실제 본문 검사 적용 범위의 구현 오류 | M | pregate `:857-884`, S1 `:1835`; pairing `:726-756`; 대장 #376:688·#566:888 | 합성한 정확한 after_commit 메서드만 S1 미검증으로 처분. 기존 실코드·새 실제 본문과 #566 전체는 계속 검사 |
| F4-13 | 규범 문면 정합화. #555를 해제하는 구현 버그 수정이 아님 | M | raw 문면 `R-1617/R-2677/R-1037/R-1071/R-0084/R-2941`; 대장 #554:876·#555:877; pairing `:986-1009` | 이미 catch한 IntegrityError의 내부 계약 번역과 외부 HTTP 500을 분리. 일반 저장소 실패 계약의 소유 위치를 명확히 함 |
| F4-14 | 규범의 트랜잭션 단위와 검사기의 함수 단위 사이 구현 오류 | M | domain checker `:779-815`; 대장 #546:868; ddd final `s019/b10` (`R-0508~R-0512`) | 독립 UoW 실행 구간 단위 계수. 중첩·공유·별칭·실행 경계 미확정의 구별 |
| F4-15 | 속성 이름을 출처 증거로 쓰는 구현 오류 | M | pairing `:1165-1171`; 대장 #557:879 | domain/벤더/불명 3분류. except 바인딩만으로 벤더 확정 금지; 도메인 예외의 code도 정당할 수 있음 |
| F4-16 | 사용자 승인 규범 폐지. 원 보고서의 identity 보정안으로 대체하면 범위 위반 | M | houserules SKILL `s004-1/b7`의 `R-3417`; final `s003-0/b10`의 `R-3410`; skeleton `:95,147-149` | 승격 술어의 개별 50행 + 승격 부품 출생 50행 모두 제거; #643·#644와 나머지 승격 규율 유지; 현행 문서·대장까지 동기화 |
| F4-17 | 기능 인스턴스 존재 판정 구현 오류 | M | skeleton `_entries():68-77`, `_check_level():192`; pairing `:187-190,213-217`; `R-3181`(#488 alias) | 캐시뿐인 선택적 기능 인스턴스 제외. 필수 고정 골격·미추적 실제 소스는 계속 검사. 파일 삭제 방식 금지 |
| F4-18 | pre-gate 검출 범위 확장 + 타입 출처 입력 계약 보완 | M | architect `R-3426/R-3427`; pregate `Symbol`·`_parse_symbols`; DTO checker `:429-446`; 대장 #202:529 | 경로+심볼 identity와 명시 출처로 Result/Out→보조 DTO/컨테이너→aggregate/entity 연결; domain import 직접 증거와 추정을 분리 |
| F4-19 | 기존 초기/재발화 정책은 비결함. 충돌 원인 및 file-plan 범위 안내는 개선 필요 | m | architect `R-3425`; command `R-3445`; pregate `:1101,1293-1334,1953-1988` | 기준선 실존·작업 트리 오버레이 실존을 다른 오류로 표시; 작업 기록의 오편입을 안내. 초기 실행 자동 기실현 허용이나 docs 일괄 제외 금지 |

대장 좌표는 `workspace/design/2026-08-08-tree-revision-spec.md`의 현재 행이다. `#N`과 `R-NNNN`은 다른 번호 공간이다. `ontology/wiring/aliases.ttl`에는 #488→R-3181은 있지만 **#197/#387/#647/#642/#202 등 대부분의 해당 #N alias는 현재 없다**. 존재하지 않는 Work 매핑을 추정하지 않았다. 이번 수정을 핑계로 전체 미확정 alias 정리를 요구할 필요도 없다.

## 2. F4-9 — 완화 목록과 업무 경계

### 2.1 현행 규범은 'admin 제외'가 아니다

houserules SKILL §4의 `R-3148~R-3150`은 첫 대입에 타입을 예외 없이 요구한다. `R-3154`는 admin 클래스 선언 속성을 스텁 소유로 인정하지만 **메서드는 면제하지 않는다**. `R-3447`은 framework override의 Any도 object/정확 타입으로 바꾸라고 한다. `R-3448`은 object를 입구 매개변수·즉시 검증 지역 변수에만 허용하고 반환·속성 dict의 object를 차단한다. `R-3451/R-3452`는 리터럴 고정 키 레코드의 TypedDict를 요구한다. 이 문면들은 '값을 읽지 않고 framework에 전달하는 열린 context'를 자체적으로 닫아 주지 못한다.

따라서 현장 후보 3건이 곧 checker 구현 오류라는 판정은 부정확하다. **정본이 그 후보를 요청하고 있어 규범을 완화해야 한다.** 반대로 현행 검사기가 정본에 맞는다는 이유로 사용자 결정 F9를 비결함 종결해도 안 된다.

### 2.2 합의 범위 안에서 제시할 수 있는 구체 목록

루트 코디네이터가 제시한 다음의 좁은 목록은 사용자 결정에 부합한다. 추가 사용자 정책 질문 없이 계획에 고정하고 계획 리뷰로 검증할 수 있다.

| 규칙 | 계획 방향 | 정확한 허용/유지 범위 |
|---|---|---|
| #493 / `R-3148~R-3154` | 유지 | 첫 대입·시그니처 주석 의무와 기존 framework 선언 속성 예외 유지. admin의 무주석 함수/지역 변수 전면 허용까지 약속하지 않음 |
| #645 / `R-3447` | 제한 완화 | 실제 Django framework 계약이 소유하는 admin override/context 전달 슬롯의 Any를 허용할 수 있음. admin 안 임의 business/helper Any로 전파하지 않음 |
| #646 / `R-3458/R-3459` | 유지 | ModelAdmin·Inline·admin ModelForm 등의 런타임 안전한 제네릭 표기 유지. 맨몸 상속·전역 monkeypatch 신규 도입을 해결책으로 쓰지 않음 |
| #647 / `R-3448/R-3451/R-3452/R-3457` | 제한 완화 | admin 렌더링을 위한 framework 소유 열린 context/kwargs의 Any·object 및 단순 조립·병합·전달을 허용. UI에 넘기는 context를 이유만으로 private TypedDict에 닫도록 강요하지 않음 |
| #650 / `R-3448/R-3453` | 유지 | JSON을 파싱해 실제 값을 사용하는 경계의 검증 유지. 'admin이므로 모든 json.loads 후보 제외'를 하지 않음 |

이 목록은 '타입/형식 완화'를 #645/#647에서 실질적으로 수행하면서 이미 구성된 mypy strict와 불필요하게 충돌하지 않는 선택이다. #493/#646까지 풀어야만 합의가 이행되는 것은 아니다. 만약 계획이 나중에 무주석 override나 맨몸 제네릭 허용까지 확대된다면 lint/type-check 기준의 변화도 함께 설명해야 한다. checker만 면제해도 외부 mypy `[no-untyped-def]`/`[type-arg]` 실행이 없어지는 것은 아니다. 그 확대는 현재 좁은 계획의 필수 작업이 아니다.

### 2.3 반드시 유지할 업무 경계

- `extra_context`를 받기, literal UI context 조립, `{**context, ...}`, `.update(extra_context)`, `render_change_form`/Django 렌더 함수에 전달하는 행위는 허용 경계에 들어갈 수 있다. 단 '이름에 context가 있다'만으로 증명하지 않는다.
- 알려진 override 이름만 허용하면 현장 private `_render_failed_submission(extra_context...)`가 남는다. **framework 연결이 확인된 private 전달 helper와 지역 context까지** 범위에 포함해야 원 사례가 닫힌다.
- `cleaned_data`, request 값, JSON 값을 읽어 비교·계산·상태 변경 인자에 쓰는 행위는 실제 소비다. 그때의 입력 검증·좁히기와 도메인 규칙은 그대로 적용한다. pass-through로 받은 context에서 우리 코드가 특정 값을 읽기 시작하면 해당 값에 이 경계를 다시 적용한다.
- admin 파일 안에 화면 조립과 업무 작업이 섞일 수 있으므로 경로 전체, 클래스 전체, `feature/` 전체를 면제하지 않는다. 흐름을 확정할 수 없으면 후보로 넘기며 추정으로 whole-file 면제를 만들지 않는다.
- #342/#343/#344/#345의 panel/form/feature 구조, #347의 공통 use case 경유, #589의 template 업무 판정 금지, ORM·BC import 경계, 저장소 변경의 트랜잭션 규율은 이 완화로 없어지지 않는다. 특히 '공통 업무 동작은 공통 use case 경유'는 유지한다.

설계·pre-gate의 스텁에는 실제 전달 본문이 없을 수 있다. 실제 코드용 데이터 흐름 판정을 스텁에서 통과했다고 가장하지 말아야 한다. 새 정형 선언으로 framework 역할을 명시할지, 실제 구현에서만 결정할지를 계획에 적고 같은 판정의 근거 수준을 구분해야 한다. `panel.py`라는 경로 하나만으로 설계의 모든 타입 진단을 사라지게 만들면 안 된다.

### 2.4 소유 좌표와 최소 변경 면

- `ontology/rules/discipline-houserules-skill.ttl`: `s007-4/b7` (`R-3447/R-3448`), `b8/b10` (`R-3451/R-3452`), `b15` (`R-3457`). 주변 `b1/b5/b16` 및 `s008-4.1/b1`은 유지 문구가 제한 예외와 충돌하는지 확인한다.
- `ontology/rules/agent-discipline-reviewer.ttl`: `s007/b51` (`R-1117/R-1118`), 그 밖의 #645/#647 후보 처분 불릿. 업무 판정과 framework 연결의 처분을 같은 표로 연결한다.
- architect의 machine symbols/alias/decorator 표기(`R-3426`), pre-gate 적용 범위·실검사기, 현행 대장 #645/#647와 owner-map, Claude/Codex 의미 미러를 일치시킨다.
- `implementation-django` final §18은 admin 타이핑 예시다. #493/#646 유지안에서는 이 장 전체를 재작성할 이유가 없다. 필요한 교차 설명만 대조한다.

## 3. F4-13 — 내부 실패 계약과 raw 500

### 3.1 충돌을 없애야 하는 정확한 문장

다음은 단순 인접 키워드가 아니라 직접 정합화해야 할 중복 주장이다.

| 문서 / 블록 | Work | 현행 주장 |
|---|---|---|
| architect `s005/b11` (`design-architect.md:55`) | R-1617 | 승인된 안정 public meaning이 있을 때만 consuming BC internal exception으로 정규화한 뒤 ErrorSchema 생성 |
| API reviewer `s006/b11` (`design-review-api.md:73`) | R-2677 | 위와 같은 정규화 조건을 리뷰 |
| discipline reviewer `s007/b23` (`discipline-reviewer.md:94`) | R-1035~R-1038, 특히 R-1037 | raw는 safe 500, G1 승인 시에만 infra/ACL 정규화 후 controller mapping |
| discipline reviewer `s007/b29` (`:100`) | R-1067~R-1071, 특히 R-1071 | known failure 번역 전수성 밖 unknown raw에는 500 기본과 public meaning 한정 정규화 |
| ninja final `s023-6.2/b33` (`final.md:830-835`) | R-0082~R-0085, 특히 R-0084 | 인프라 오류 경계의 같은 정규화 조건 |
| ninja SKILL `s004/b10` (`SKILL.md:32`) | R-2940/R-2941 | raw 기본 500, 승인 안정 의미만 자기 BC exception 정규화 |

`R-1617` 등은 내부 실패 정규화와 공개 ErrorSchema 생성을 같은 문장에 묶는다. 'public meaning이 없으므로 번역 자체 금지'로 읽히는 것이 원인이다. 원 보고서의 '두 문면은 충돌이 아니라 층이 다름'은 의도에 대한 타당한 설명이지만 **현재 문면만으로 그 층 구분이 충분히 쓰여 있다는 주장은 성립하지 않는다**.

### 3.2 유지할 결과

이미 `except IntegrityError`가 잡은 실패 중 승인된 알려진 제약 의미는 해당 구체 계약 예외로, 나머지는 **승인된 일반 저장소 실패 계약**으로 정규화한다. 그 내부 계약이 있다는 사실만으로 새로운 public meaning, ErrorCode, ErrorSchema, 4xx/503 mapping을 만들지 않는다. 외부 응답은 기존 safe framework 500을 유지한다. 내부 예외는 포트 소비자에게 인프라 타입을 누수하지 않기 위한 계약이며 공개 HTTP 오류 계약과 다른 축이다.

#554에 따라 **계약의 소유 위치**도 지킨다. 애그리거트 repository 계약의 실패는 domain 소유, application capability port 계약의 실패는 그 port 소유다. 일반 저장소 실패를 전역 `Exception/RuntimeError`로 만들거나 모든 BC가 공유하는 새 infrastructure framework 계층을 만드는 것은 이번 해결 범위가 아니다. 'BC별 백스톱 예외 하나'를 모든 BC에 강제 생성하는 작업도 아니다. 대상 계약이 필요로 하는 승인 일반 실패만 사용한다.

잡지 않은 unknown 인프라 예외까지 새로 `except Exception`으로 잡게 만들지 않는다. controller의 vendor/raw 예외 직접 catch, global recognizer, SQLSTATE/string 판정, 새로운 retryable 503 노출도 열지 않는다. 기존 승인 concrete 계약 예외를 잡아 관찰한 뒤 재던지는 경로는 이미 pairing `_handler_declared_error`가 인정하므로 #555 전체 bare-raise 금지로 되돌리면 회귀다.

### 3.3 계획 범위

필수는 위 문면들과 #554/#555의 명시 관계, 설계 실패 계약의 기록 기준이다. pre-gate가 exception 본문을 합성하여 알려진 실패/나머지 분기를 추정하는 기능은 사용자 결정에 필요하지 않다. 현재 `exception-map`은 `<예외명> <raise 창구 파일>` 형식의 파일 수준 helper이고, catch 분기·public mapping 의미를 표현하지 못한다. 이 채널을 예외 처리 DSL로 확대하지 않아도 규범 정합화가 가능하다.

## 4. F4-16 — 50행 의무 제거의 전파 범위

사용자 방향은 숫자 변동에 따른 #642 귀속 문제를 보정하는 것이 아니라 **그 하한 자체를 제거하는 것**이다. registry identity·anchor_diff를 고쳐 #642를 존속시키는 계획은 승인 방향을 바꾼다.

| 대상 | 현재 좌표 | 필요한 처분 |
|---|---|---|
| 승격 판정 술어 | houserules SKILL `s004-1/b7`, R-3417; 배포 SKILL:42 | 역할 밖 응집 술어에서 `(b) 개별 50행 이상` 및 '둘 다 충족' 잔여 문법 제거. 역할/응집·관례 동거·참조처 조사 유지 |
| 승격 부품 하한 | houserules final `s003-0/b10`, R-3410; 배포 final:30 | 출생 50행 문장 제거. 같은 Work에 묶인 부품 0개 환원(#643)은 유지 |
| Work 정체성 | R-3410 및 R-3417의 prefLabel/currentExpression | Work 전체 폐기나 ID 재사용이 아님. 남은 의미에 맞게 개정·label을 고침. ISSUED 이력 보존 |
| 고정 adapter 예외 설명 | final `s003-0/b12`, R-3468; final:33 | 더 이상 없는 '50행 하한의 대상 아님' 비교 삭제/정리. 200행 승격 신호 제외와 고정 패키지 규율 유지 |
| 실검사 | `check-layer-skeleton.py:95,147-149` | `PROMO_PART_MIN_LINES`와 #642 방출 제거. #638/#639/#640/#641/#643/#644 유지 |
| 현행 규칙 대장 | tree revision spec #192:521·#642:1171 | #192 부칙의 50행 조건 제거, #642의 폐지 상태를 대장 규약에 맞춰 표시. #643 행은 유지 |
| 현행 owner-map | `workspace/plan/2026-08-11-rule-owner-map.md:555` | #642를 계속 시행 중인 신설 ast 규칙으로 남기지 않음 |
| alias | `ontology/wiring/aliases.ttl` | #642 alias는 현재 없음. 지울 alias를 가정하지 않음. 관련 Work에 대한 기존 간선도 전건 확인 후 필요한 것만 개정 |
| 현재 사람용 문서 | `docs/file_tree.html:3296,3304`; `docs/mkrev2.py:6679,6687` | 고정 adapter 제외 설명과 새 승격 부품 50행 의무를 동시 수정. 생성원/생성물의 재도입 방지 |
| 배포·출처 미러 | Claude/Codex houserules reference·SKILL, workspace reference mirror | graph-owned는 TTL 렌더, reference는 corpus mirror, scripts는 byte 미러 |

`docs/master.html`은 기존 사용자 변경이 있고 현재 해당 50행 의무 검색 결과가 없다. 이 파일을 재생성하거나 정리할 권한을 F16에서 만들지 않는다. `docs/file_tree.html:1843` 등의 '50행과 같은 자'는 **트리 50번 행 참조**이고, cleancode final §15.1의 '50줄 이상의 함수'는 **수치 스멜 신호**, implementation-test 예시의 '50줄 더'는 발췌 코드다. 모두 이번 하한 폐지 대상이 아니다. 과거 현장/릴리즈 기록을 전역 치환하는 작업도 아니다.

의도적으로 없앨 검출은 #642다. 따라서 전후 전체 검출 집합 동일을 성공 기준으로 삼을 수 없다. 하한 제거 fixture의 기대값을 줄이고, 부품 0개·중첩 폴더·본체 부재·정크드로어·200행 후보가 여전히 살아 있다는 대조를 해야 한다. 기존 줄 수 계산 `_phys_lines`는 #644가 계속 사용한다.

## 5. F4-1/F4-18 — 명시 입력 형식이 문제의 일부다

### 5.1 현재 다섯 채널이 실제로 표현하는 것

`design_pregate.py:34-77`과 architect `R-3424/R-3431`은 file-plan, symbols, boundary-imports, physical-signals, exception-map 다섯 채널을 정의한다. `Symbol.kind`는 Python class/function 구분이며 domain aggregate/entity/result라는 의미 종류가 아니다. symbols는 경로별 클래스·메서드 시그니처·필드·별칭을 담고, **read-only 여부를 선언하는 토큰은 없다**. UoW 타입 매개변수는 서술할 수 있지만 이것만으로 유스케이스의 읽기 전용 여부를 알 수 없다.

현재 `_parse_symbols`는 add 클래스/메서드만 스텁으로 보존하고, update에는 신규 OHS 모듈 함수만 남긴다. 기존 클래스/함수 signature/body 변경은 S5다. `_parse_signals`는 첫 Python 파일 주소에 결합하고 case nodeid는 파일 결합에서 벗기며, `entry.tag != 'add'`면 명시 마커도 미반영한다. `[markers: a,b]`는 렌더 시 파일 수준 `pytestmark` 목록이다. 기존 마커에 대한 add/remove/retain 연산이나 case/class별 변경 의미가 아니다.

`_check_dto_file`의 #202는 **import 모듈의 domain 경로**를 보고 잡는다. 필드에 `AnswerOutline`이라는 이름이 있지만 그 import를 누락한 스텁은 #202를 낼 근거가 없다. 타입 주석은 future annotations 때문에 미해소 이름이어도 스텁 compile을 통과할 수 있다. 현장 F18을 '파서가 Result 필드를 전혀 못 읽는다'로 설명하면 원인을 과장한다. 필드는 읽지만 의미 출처 결합이 없다.

### 5.2 F1 계획이 고정해야 할 계약

1. **유스케이스 식별**: 파일 경로+클래스/실행 메서드와 명시 read-only 선언을 결합한다. get/list/query 이름으로 읽기 전용을 추정하지 않는다.
2. **UoW 선언**: 사용/주입 없음과 특정 계약 사용을 명시하는 형식, 같은 use case의 symbols 시그니처와 불일치할 때 처분을 정한다. 기존 전체 함수 본문을 스텁으로 교체할 필요는 없다.
3. **모순 결과**: read-only로 명시했는데 UoW를 사용/주입하는 설계는 #197 관련 확정 모순이다. 선언 없는 기존 설계는 무조건 read-only도 write도 아니다. 새 채널의 무기재를 '검증 통과'라고 광고하지 않는다. 새 형식의 적용 대상·결손 보고를 문면에 명시한다.
4. **마커 후상태**: update에서 기존 마커를 유지할지/추가할지/지울지와 선언의 완결성 범위를 고정한다. 예를 들어 '완전한 최종 목록 + scope' 또는 'add/remove/retain 연산 + scope' 모두 기술적으로 가능하다. 둘을 모호하게 섞으면 안 된다.
5. **마커 scope**: 파일 전체와 `::test_case`/class 수준을 구별한다. 현재 `.py::case`를 파일로 접는 규칙을 그대로 써 특정 case의 변경을 전체 모듈 pytestmark로 번역하면 다른 테스트 의미를 바꾼다. alias·인자 있는 mark·동적 pytestmark를 정적으로 확정 못 하면 제한을 보고한다.
6. **기존 코드 보존**: 실제 unit 파일의 입력 증거와 명시 변경 재료를 사용해 #387을 예보할 수 있다. update 전체 본문 시뮬레이션을 새 전제로 만들지 않는다. 부분 marker 전사 성공이 기존 body 검증 성공이 되지 않도록 S5를 남긴다.

위 문법의 선택은 합의 방향을 실행 가능한 입력으로 만드는 기술 선택이다. 사용자에게 Python 문법이나 채널 이름을 다시 고르도록 요청할 필수 사안은 아니다. 다만 무기재를 이름 추정으로 채우기, 모든 기존 파일에 새 의무를 소급해 현재 레인 밖 수정 요구하기, update 본문 전체 교체하기는 합의 내 기술 선택이 아니다.

마무리 시 코디네이터가 선택한 **새 채널은 선택형, 미기재는 S5로 병기하여 기존 설계 호환, marker update는 명시된 파일 수준만 지원**하는 범위도 위 조건을 충족한다. case/class marker update를 이번에 구현할 필요는 없다. 대신 기존 `.py::case` 주소를 묵시적으로 파일 전체 marker 교체로 승격하지 않고 지원 밖이라고 표시해야 한다. 이 선택에는 새로운 사용자 정책 결정이 필요하지 않다.

### 5.3 F18 계획이 고정해야 할 계약

- 타입 identity는 **정의/출처 경로+심볼**로 잡는다. 명세 전체에 같은 클래스명이 한 번 나왔다는 사실만으로 다른 파일의 미해소 bare annotation을 그 타입으로 단정하지 않는다.
- 명시 import 바인딩, 명시 type origin, symbols의 정의 경로·현재 실물 등 어디까지를 확정 증거로 쓰는지 닫힌 형식으로 정한다. 기존 boundary-imports에 없는 가짜 domain import를 만들어 checker를 억지로 발화시키지 않는다.
- Result/Out의 필드를 보조 DTO·컨테이너·union·명시 타입 별칭·forward annotation 경유로 연결한다. `_Item` 사설 이름, 같은 이름의 다른 타입, 순환 DTO 그래프, 미해소 generic 인자를 구별한다. 값 객체는 #207의 허용을 유지한다.
- 직접 증명된 aggregate/entity 포함은 #202 관련 확정 예보다. import·출처가 불명한 경우는 타입 미해소/리뷰 후보이며, domain 타입이라는 이름 추정만으로 확정 위반이 아니다.
- OHS가 Result를 소비한다는 사실은 domain import 필수성의 증명이 아니다. Python은 직접 import 없이 이미 받은 객체의 속성을 투영할 수 있다. **명시된 직접 domain 의존**이면 #95/#96 예보, 필드 구조로 유추한 가능성만 있으면 후보 수준을 유지한다.
- 새 후상태 타입 대조가 add에만 적용되는지 update 명시 자료까지 보는지 계획에 적는다. update의 모든 본문/바인딩을 합성해야 F18이 성립하는 것은 아니다.

### 5.4 두 항목의 문서·캐시 전파

최소 변경 좌표는 architect `s005/b33~b37` (`R-3424~R-3429/R-3431`), command의 pre-gate 실행·hash 판형 `R-3432~R-3436/R-3445`, `design_pregate.py` 파서/문법/docstring/`block_hash`/리포트/`BLIND_SPOTS`다. **S2는 현재 '명세 내부 의미 모순은 검출 대상이 아니다'**라고 전면 선언한다(`:1836`). 명시 read-only×UoW 및 DTO 타입 그래프 대조를 도입하면 정확히 지원하는 범위의 예외를 적어야 한다. S3/S5와 '다섯 채널'·'네 블록+입장 표' 해시 설명도 새 형식과 맞춰야 한다. 새 선언의 변경이 hash에 반영되지 않으면 캐시 skip이 검출 자체를 무력화한다.

## 6. 나머지 7건의 적대 경계

- **F10**: 현재 `max(use_case 문자열이 들어간 호출 수, .execute 전체 호출 수)`는 실제 실행 의미와 다르다. 표준 builder를 확인해 준비와 실제 use case 실행을 연결하는 수정은 #153 역할 규범을 바꾸지 않는다. builder 이름을 모두 제외하거나 .execute만 세면 일반 객체 execute·중간 helper·복수 실제 실행의 후보가 달라져 미탐이 생긴다. 0회 호출의 후보도 이유 없이 없애지 않는다.
- **F11**: Enum 예외는 '타입 자체로 잘못된 값이 불가능한가'라는 기존 #268 Q2의 자동 응답이다. 표준 출처가 확인되는 닫힌 Enum만 인정한다. `_missing_`, 사용자 metaclass/new/value 허용 동작·재정의·외부 동명 Enum은 별도 검토 대상이다. 원 보고서의 'Q2 답은 항상 불가능'은 이 사용자 동작 범위를 생략했다.
- **F12**: after_commit에서 on_commit이 없으면 #376, 실제 on_commit은 있으나 robust가 없으면 #566이 나온다. stub는 전자만 만든다. `#376/#566` 두 번호를 스텁 파일 단위로 전부 삭제하는 것은 과도하다. 생성 provenance를 정확한 메서드에 연결한 S1 미검증 처분이면 합의 안에서 해결할 수 있다. on_commit 한 줄을 합성해 검증된 것처럼 꾸미는 것은 사용자 방향과 다르다.
- **F14**: with 블록 두 개와 트랜잭션 두 개는 동의어가 아니다. 같은 UoW 변수의 순차 재진입은 독립 구간일 수 있고, 다른 변수명도 같은 외부 트랜잭션/공유 객체일 수 있다. 중첩 구간을 별도로 세어 동일 실행의 두 aggregate 쓰기를 놓치지 않는다. 확정 분리 가능한 구간을 나누고 불명은 후보/제한으로 명시하는 것은 추가 정책 결정 없이 가능한 기술 범위다.
- **F15**: `except SomeDomainError as error: error.code == ...`도 도메인 값일 수 있다. except-bound라는 이유만으로 벤더 확정은 실패한다. 모듈 import·타입 annotation·할당 출처를 조사하되 출처 불명은 후보로 내려야 한다. domain code라는 확정 증거가 있으면 후보까지 남기지 않는다.
- **F17**: 최상위 `__pycache__` 자체를 건너뛰는 코드가 있어도 상위 capability 디렉터리는 여전히 존재한다. 캐시만 남은 선택적 인스턴스의 실질 내용을 재귀로 판정해야 한다. `git ls-files=0`만으로 제외하면 미추적 실제 코드도 제외되어 사용자 경계를 어긴다. 고정 package의 `__init__.py`·비어도 존재해야 하는 필수 폴더까지 없다고 치면 #488을 무력화한다.
- **F19**: 초기 실행에서 미추적 실제 add를 금지하고 명시 재발화에서만 다루는 정책은 `R-3445`와 구현에 실재한다. 오버레이 add를 update로 재라벨하면 기준선 부재 red가 맞다. 오류는 baseline 충돌과 overlay 충돌을 나누고 어느 모드인지 보여야 한다. REPORT처럼 coordinator 소유 작업 기록이 제품 file-plan에 오편입된 사례를 안내하되, docs라는 이름이나 비-.py라는 사실만으로 모든 산출물을 배제하면 안 된다. 승인 기능이 template·migration·비-Python 파일을 필요로 할 수 있다. 자동 commit/stash나 기준선 이동을 처방 실행으로 만들지 않는다.

## 7. 계획 리뷰에서 닫을 조건과 검증 경계

현재 사용자 결정으로 각 해결 방향은 충분히 정해져 있다. 남은 것은 역할·입력 문법·확정 증거를 계획에서 구체화하는 일이다. 다음은 구현 진입 전에 `M`으로 닫을 조건이다.

1. F9의 위 5규칙 표와 framework helper/실제 소비 경계가 계획·정본·checker의 같은 대상으로 표현돼야 한다.
2. F13의 일반 저장소 실패는 내부 계약이고 HTTP 500 유지라는 결과를 모든 직접 관련 raw 문면에 일관되게 써야 한다.
3. F16이 #642의 앵커 identity 수리로 바뀌지 않아야 하며 R-3410의 #643 부분을 함께 삭제하지 않아야 한다.
4. F1/F18의 새 명시 입력 형식·결손·update scope·cache hash가 정해져야 한다. 산문 추론 또는 이름 추정으로 누락을 메우지 않아야 한다.
5. F10/F11/F12/F14/F15/F17의 정당한 사례와 계속 잡을 사례를 분리한 fixture가 있어야 한다. 현장 한 사례만 통과하고 원래 진탐을 잃는 수정을 받아들이지 않는다.

정본 처리 순서는 `docs/DEVELOPMENT.md` §3 및 저작 규약대로 **TTL → render → rulepack → 미러**다. graph-owned 배포 md 직접 편집은 금지다. 산문 소유 절을 실제로 변경하면 LEDGER append가 필요하고, 새 Work가 필요한 새 규범이면 ISSUED 채번을 따른다. 기존 Work의 문면 개정에 새 ID를 무조건 발급하지 않는다. 검사기와 필요한 스크립트는 Codex byte 미러를 함께 갱신하고, 의미 미러인 role/SKILL은 플랫폼 형식을 보존한다.

검증에는 관련 fixture·규범 투영·소성물/미러 대조와 `make verify`가 필요하다. rulepack/selector 변경 시 개발 가이드의 `make verify-mutation` 적용 여부를 계획에 포함한다. 이번 문제 검증 단계에서는 실행하지 않았다. F16 #642 및 F9/F10/F11의 의도된 후보 축소 때문에 전후 모든 검출 집합 동일을 요구하지 않는다. 삭제된 진단의 이유와 보존해야 할 진단을 각각 증명한다.

Serena/Graphify는 현재 worktree에 opt-in 표식이 없다는 배정 조건에 따라 검색·로드·초기화 없이 생략했다. 추가 위임 없음.
