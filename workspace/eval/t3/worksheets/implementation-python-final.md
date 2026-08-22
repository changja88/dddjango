# T3 이관 검수표 — implementation-python-final

- 원문: `dddjango/skills/implementation-python/references/final.md` (2675행 · 센서스 일치 · 드리프트 경고 없음)
- spec: `workspace/eval/t3/specs/implementation-python-final.spec.json`
- 규모: REF 42절 · 블록 114 · Work 80(발주서 규범 81 — 차 1 = 문서 내 재진술 1건, §1 참조)
- 자기 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/implementation-python-final.spec.json` → **exit 0**(검증 전용 · `--write` 미사용)

## 1. census 대사 (발주서 규범 수 ↔ spec Work 수)

| section_key | 헤딩(약) | 발주서 | spec | 대사 |
|---|---|---|---|---|
| `s001` | 서문 | 2 | 2 | 일치 |
| `s004-1.2` | 1.2 Optional과 None | 2 | 2 | 일치 |
| `s005-1.3` | 1.3 Union·합 타입 | 1 | 1 | 일치 |
| `s007-1.5` | 1.5 TypedDict | 1 | 1 | 일치 |
| `s013-1.11` | 1.11 Concatenate | 1 | 1 | 일치 |
| `s014-1.12` | 1.12 TypeIs vs TypeGuard | 2 | 2 | 일치 |
| `s025-3.3` | 3.3 __missing__ | 1 | 1 | 일치 |
| `s032-4.4` | 4.4 None 반환 대신 예외 | 1 | 1 | 일치 |
| `s035-5.1` | 5.1 functools.wraps | 1 | 1 | 일치 |
| `s037-5.3` | 5.3 클래스 데코레이터 | 1 | 1 | 일치 |
| `s039-6.1` | 6.1 디스크립터 프로토콜 | 1 | 1 | 일치 |
| `s040-6.2` | 6.2 디스크립터 검증 프레임워크 | 2 | 2 | 일치 |
| `s042-7.1` | 7.1 평범한 애트리뷰트 | 1 | 1 | 일치 |
| `s045-8.1` | 8.1 __call__ | 1 | 1 | 일치 |
| `s046-8.2` | 8.2 @classmethod 팩토리 | 1 | 1 | 일치 |
| `s048-8.4` | 8.4 __repr__·__str__ | 1 | 1 | 일치 |
| `s049-8.5` | 8.5 보호(_) 애트리뷰트 | 1 | 1 | 일치 |
| `s050-8.6` | 8.6 __init_subclass__ | 1 | 1 | 일치 |
| `s053-8.9` | 8.9 collections.abc | 1 | 1 | 일치 |
| `s061-10.1` | 10.1 Enum/StrEnum | 14 | 14 | 일치 |
| `s063-10.3` | 10.3 dataclass(slots=True) | 1 | 1 | 일치 |
| `s070-11.1` | 11.1 연산자 오버로딩 | 3 | 3 | 일치 |
| `s071-12` | 12. pydantic v2(헤더) | 1 | 1 | 일치 |
| `s072-12.0` | 12.0 pydantic boundary 결정 | 11 | 11 | 일치 |
| `s081-13.5` | 13.5 send·throw 금지 | 1 | 1 | 일치 |
| `s089-15.2` | 15.2 최상위 예외 클래스 | 1 | 1 | 일치 |
| `s090-15.3` | 15.3 @deprecated | 2 | 2 | 일치 |
| `s092-16.1` | 16.1 GIL·스레드 선택 | 2 | 2 | 일치 |
| `s093-16.2` | 16.2 asyncio.TaskGroup | 1 | 1 | 일치 |
| `s094-16.3` | 16.3 Free-Threaded | 1 | 1 | 일치 |
| `s098-17` | 17. 프로파일링(헤더) | 1 | 1 | 일치 |
| `s109-19.4` | 19.4 bytes·str 분리 | 1 | 1 | 일치 |
| `s110-19.5` | 19.5 루프 뒤 else 금지 | 1 | 1 | 일치 |
| `s111-19.6` | 19.6 명명 규칙 | 2 | 2 | 일치 |
| `s112-20` | 20. 디자인 패턴 | 1 | 0 | **불일치** |
| `s116-21` | 21. Repository/UoW | 3 | 3 | 일치 |
| `s118-22.1` | 22.1 pyproject.toml | 1 | 1 | 일치 |
| `s121-23.1` | 23.1 mypy strict | 1 | 1 | 일치 |
| `s122-23.2` | 23.2 pyright strict | 1 | 1 | 일치 |
| `s124-24` | 24. 테스트 | 1 | 1 | 일치 |
| `s126-25.1` | 25.1 repr 활용 | 1 | 1 | 일치 |
| `s129-26.1` | 26.1 독스트링 규칙 | 6 | 6 | 일치 |
| **합계** | — | **81** | **80** | 차 1 |

**`s112-20` 불일치 사유** — **과대 아님 — 축 차이**. 발주서 1은 «규범 문장» 계수, spec 0은 «Work 채번» 계수다. 이 절은 같은 문서 s001/b1(서문 blockquote «클린코드 범용 원칙 → discipline-cleancode»)의 재진술 사본이라 §15 «정본 1곳만 Work 승격 + 사본 블록에 djr:restates»를 적용해 Work 를 채번하지 않고 `restates`로 연결했다. 발주서 재진술 열이 `Y:implementation-python-final/s001`(같은 문서)이라 브리프의 «같은 문서 안 쌍만 spec restates» 조건을 정확히 만족한다. 발주서 계수가 옳고 spec 도 옳다 — 두 수의 차 1이 곧 문서 내 재진술 1건이다.

합계 외 41절은 전건 일치. 계수 판정에서 특히 다툴 만한 절의 승계 근거:

- `s061-10.1` **14** — P0 «항 단위 계수 14»를 승계했다. 다항 문장 분할 실물: 1207·1208·1209·1210 각 1 + 1211 **4**(소유 지정 / 1곳째 승격 / 심볼 소비 / `==` 비교) + 1212 **3**(enum 소유 / 프로퍼티·frozenset 실현 / 재정의 금지) + 1213 **3**(도메인=Enum / 외부 API=Literal / 잠긴 자리 리터럴 허용) = 14.
- `s072-12.0` **11** — 1434 문단은 «경계에서 사용한다» 1만 규범이고 뒤 «…데 적합하다»는 적합성 서술이라 비산입. 1436 문단 3 + 불릿 1438·1439 각 1 + 1440 **2** + 1441 **2** + 1442 1 = 11.
- `s129-26.1` **6** — 대상별 형식 불릿 4(2486~2489) + 2490 **2**(중복 타입 서술 삭제 / 어노테이션 상시 유지).
- `s111-19.6` **2** — P0 방침 승계로 **표 단위 1 규범**(행 단위 아님). 블록은 표 머리행·구분행 포함 행 묶음 1개씩 = `table-row` 2블록.
- `s116-21` **3** — 한 문단이 소유 지정 2(architecture-ddd §5·§6 / implementation-django §16) + 본 문서 범위 한정 1.
- `s040-6.2` **2** — b3 «레거시 참고»가 b1 의사결정 #5 와 요지가 겹치나 **축자 사본이 아니라** 조건부(3.6+ 이후) 권장문이라 별도 Work 로 승계했다(발주서 재진술 열 `N` 과 정합). §4 경계 메모 참조.

## 2. 배선 근거 표 (전 Work 80)

`E` = `enforcedBy`(검사기) · `D` = `delegatedTo`(에이전트). 위임 기본값 표(§16): implementation-* → `agent-discipline-reviewer`.

| # | 절/블록 | Work label | class | E / D | 4원 근거 |
|---|---|---|---|---|---|
| 1 | `s001`/b1 | 클린코드 범용 원칙의 discipline-cleancode 위임 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 문면이 discipline-cleancode 를 소유자로 직접 지목 — 그 문서군 기본값도 discipline-reviewer(§16 표) 라 일치 |
| 2 | `s001`/b1 | Python 3.10+ 도입 기능 적극 채택·최신 패턴 기본 제시 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 3 | `s004-1.2`/b1 | Optional 타입으로 None 가능성 명시 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 4 | `s004-1.2`/b4 | mypy --strict-optional 로 None 처리 강제 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 (mypy 설정 축을 무는 검사기 없음 — check-test-config 관할은 3슬라이스 ⑴pytest↔settings 바인딩 ⑵`test/` 구조(#383~#392) ⑶`<project>/settings/` 환경축(#445~#447)이고 `[tool.mypy]`·`[tool.ruff]`·pyrightconfig.json 은 비관할) |
| 5 | `s005-1.3`/b1 | 합 타입으로 비정상 상태 배제 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 6 | `s007-1.5`/b1 | 이종 데이터 딕셔너리의 TypedDict 사용 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 7 | `s013-1.11`/b1 | Concatenate 용처 — 데코레이터의 매개변수 추가·제거 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 [애매→포함(P0 승계) — 서술문이나 용처 지정이라 규범 채택] |
| 8 | `s014-1.12`/b3 | 대부분의 경우 TypeIs 사용 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 9 | `s014-1.12`/b3 | TypeGuard 는 입력·출력 타입 비호환 특수 경우 한정 | Exception | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 [L-E 준거: 조건 한정 → Exception] |
| 10 | `s025-3.3`/b1 | 키별 디폴트는 dict 상속 + __missing__ 구현 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 11 | `s032-4.4`/b1 | OHS 계약·승인된 failed-Result 경로의 결과 분기(raise 아님) | Exception | E: `check-context-isolation.py`<br>D: `agent-discipline-reviewer` | ①문면이 전역규칙 #453·#454 를 직접 인용 ②check-context-isolation.py docstring OHS 절 «#453/#454 «없다»는 답» 실재 — 기본값 도피 금지(§16 역도) ④«승인된» 경로 판정·OHS 밖 일반 API 경계는 의미 레인이라 reviewer 병기 |
| 12 | `s035-5.1`/b1 | 데코레이터 메타데이터의 @wraps 보존 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 13 | `s037-5.3`/b1 | 메타클래스보다 클래스 데코레이터 사용 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 14 | `s039-6.1`/b1 | 재사용 애트리뷰트 로직의 디스크립터 사용 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 [애매→포함(P0 승계) — 정의 서술에 용처 지정이 붙음] |
| 15 | `s040-6.2`/b1 | 의사결정 #5 — 공식 Descriptor HowTo Guide 패턴 기본 채택 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 16 | `s040-6.2`/b3 | __set_name__(3.6+) 이후 instance.__dict__ 직접 저장 권장(WeakKeyDictionary 레거시) | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 [b1 의사결정 #5 와 요지 중복 — 축자 사본이 아니라 조건부 레거시 대비 권장문이라 별도 Work(P0 계수 2 승계)] |
| 17 | `s042-7.1`/b1 | 평범한 공개 애트리뷰트 시작·필요 시 @property 전환 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 18 | `s045-8.1`/b1 | 상태 유지 훅은 클로저 대신 __call__ 클래스 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 19 | `s046-8.2`/b1 | 대체 생성자의 @classmethod 사용 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 20 | `s048-8.4`/b1 | 모든 클래스의 최소 __repr__ 구현 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 21 | `s049-8.5`/b2 | __var 는 하위 클래스 필드명 충돌 방지 한정 | Exception | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 [L-E 준거: 용도 한정 → Exception] |
| 22 | `s050-8.6`/b1 | 메타클래스 대신 __init_subclass__ 사용 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 23 | `s053-8.9`/b1 | 커스텀 컨테이너의 collections.abc 상속 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 [애매→포함(P0 승계) — 효과 서술이나 조건부 지시로 채택] |
| 24 | `s061-10.1`/b2 | 의미 있는 유한 상태의 Enum·StrEnum 표현 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 승격(미승격) 축은 check-choices-literal-consumption.py docstring 이 «보지 않는 것 — 닫힌 집합의 미승격(의미 레인 = discipline-reviewer 몫)» 으로 명시 배제 — 기본값 유지의 문면 근거 |
| 25 | `s061-10.1`/b3 | 직렬화 문자열 + target 3.11+ 의 StrEnum 우선 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 26 | `s061-10.1`/b4 | StrEnum 불가 제약 시 str, Enum 조합 | Exception | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 [L-E 준거: 제약 조건부 대안 → Exception] |
| 27 | `s061-10.1`/b5 | 작고 지역적인 분기 표현의 Literal 허용(의미·동작 결합 시 Enum·StrEnum) | Permission | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 [L-E 준거: 조건부 허용 → Permission. 판정 소유는 같은 절 1213 분업 항] |
| 28 | `s061-10.1`/b6 | 승격 판정·리터럴 허용 목록·소비 규율의 discipline-cleancode §2.14 소유 지정 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 문면이 discipline-cleancode §2.14 를 소유자로 직접 지목 — 그 문서군 기본값도 discipline-reviewer(§16 표) |
| 29 | `s061-10.1`/b6 | 닫힌 집합의 1곳째부터 집합 단위 타입 승격(낱개 모듈 상수 나열 금지) | Obligation | E: —<br>D: `agent-discipline-reviewer` | check-choices-literal-consumption.py docstring 이 «닫힌 집합의 미승격»을 명시 비대상으로 선언 — 검사기 비커버, 기본값 유지 |
| 30 | `s061-10.1`/b6 | 선언된 값의 비교·분기·대입은 심볼로만 | Obligation | E: `check-choices-literal-consumption.py`<br>D: `agent-discipline-reviewer` | ①문면이 cleancode §2.14 소비 규율 요지를 재진술 ②check-choices-literal-consumption.py docstring «선언된 choices 값의 리터럴 소비 결정적 백스톱(cleancode §2.14 소비 규율)» — 직접형 (a)default 리터럴·(b)filter/exclude 리터럴 한정 ④변수 우회·간접 queryset·비교식은 docstring 이 의미 레인으로 넘김 → reviewer 병기 |
| 31 | `s061-10.1`/b6 | Enum 값 비교의 == 사용(is 금지) | Obligation | E: —<br>D: `agent-discipline-reviewer` | check-choices-literal-consumption.py docstring «보지 않는 것 — 비교식(x.status == "…")» 명시 배제 — 검사기 비커버, 기본값 유지 |
| 32 | `s061-10.1`/b7 | 파생 분류 집합 지식의 enum 소유 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 33 | `s061-10.1`/b7 | 파생 집합 실현 — 프로퍼티 1순위·같은 모듈 frozenset(원소는 심볼) | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 34 | `s061-10.1`/b7 | 소비처 모듈의 임의 frozenset 재정의 금지 | Prohibition | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 35 | `s061-10.1`/b8 | 도메인 개념 값 집합(상태·종류)의 Enum 귀속 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 36 | `s061-10.1`/b8 | 외부 API 값 의존 계약의 Literal 귀속 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 37 | `s061-10.1`/b8 | Literal 로 잠긴 인자 자리의 리터럴 허용 | Permission | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 [L-E 준거: 타입 체커 검증을 조건으로 한 허용] |
| 38 | `s063-10.3`/b1 | 의사결정 #7 — dataclass(slots=True) 권장 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 39 | `s070-11.1`/b3 | 연산자 미지원 시 NotImplemented 반환(raise 금지) | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 40 | `s070-11.1`/b4 | __eq__ 정의 시 해시 가능 객체의 __hash__ 동반 정의 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 41 | `s070-11.1`/b5 | @ 연산자의 __matmul__·__rmatmul__·__imatmul__ 구현 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 42 | `s071-12`/b1 | 의사결정 #1 — pydantic v2 API 사용(v1 지원 중단) | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 43 | `s072-12.0`/b1 | pydantic v2 의 외부 입력·런타임 검증 경계 사용 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 44 | `s072-12.0`/b2 | 도메인 모델 기본 표현의 pydantic 고정 금지 | Prohibition | E: `check-domain-model.py`<br>D: `agent-discipline-reviewer` | ②check-domain-model.py docstring «#8 [ast] domain_layer 의 밖으로 나가는 import 0 — django·다른 층·다른 BC·서드파티» — domain_layer 안의 pydantic(서드파티) 고정은 결정적으로 차단됨. domain_layer 밖 자리의 «기본 표현» 판정은 의미 레인 → reviewer 병기 |
| 45 | `s072-12.0`/b2 | durable domain invariant 의 규칙 소유 경계 배치 | Obligation | E: `check-domain-model.py`<br>D: `agent-discipline-reviewer` | ②check-domain-model.py docstring 이 값 객체·엔티티·애그리거트·도메인 서비스의 자리와 «#8 밖으로 나가는 import 0»를 소유 — **domain_layer «안»의 자리·격리 축 한정** 결정 백스톱(#8·#249~#315). invariant 가 domain 밖(pydantic validator·adapter·application service)에 안착하는 양태와 무엇이 durable invariant 인가의 판정은 검사 공백 — reviewer 병기 몫 |
| 46 | `s072-12.0`/b2 | pydantic validator 의 도메인 규칙 소유 금지(boundary validation·parsing 한정) | Prohibition | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 [ddd 파일럿 L-F 준거: 판정 대행·복제의 의미 동등성은 정적 검사 밖 — reviewer 단독] |
| 47 | `s072-12.0`/b3 | BaseModel 의 외부 DTO·config·런타임 boundary 우선 사용 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 48 | `s072-12.0`/b4 | 기표현 내부 domain object 의 pydantic 중복 domain model 금지 | Prohibition | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 49 | `s072-12.0`/b5 | validation error 의 adapter·API·config 계층 변환 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 50 | `s072-12.0`/b5 | raw pydantic error shape 의 도메인 규칙 편입 금지 | Prohibition | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 51 | `s072-12.0`/b6 | coercion 은닉 시 strict mode 활성화 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 52 | `s072-12.0`/b6 | 외부 계약상 의도한 coercion 필드의 field-level 허용 | Exception | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 [L-E 준거: «단,» 한정 조항 → Exception] |
| 53 | `s072-12.0`/b7 | Ninja Schema 소유 경계의 별도 pydantic DTO 추가 전 implementation-django-ninja 기준 충돌 확인 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 문면이 implementation-django-ninja 기준을 직접 지목 — 그 문서군 기본값도 discipline-reviewer(§16 표) 라 기본값과 일치 |
| 54 | `s081-13.5`/b1 | send·throw 대신 이터레이터 입력 또는 상태 클래스 사용 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 [금지는 헤딩이 지고 본문은 대안 지시 1 — P0 계수 승계] |
| 55 | `s089-15.2`/b1 | API 모듈 최상위 Exception 정의와 모듈 예외 상속 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 27종 전수 실독 — 문면은 «API 모듈» 일반을 말하고 dddjango OHS 자리를 지목하지 않음. 유사 축인 check-context-isolation.py #166·#167·#168(기저 예외·상속·1클래스=1모듈)은 OHS contract/exception 한정이라 문면 근거 없이 배선하면 오배선 — 기본값 유지 |
| 56 | `s090-15.3`/b1 | 의사결정 #4 — Python 3.13+ 의 @deprecated 사용 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 57 | `s090-15.3`/b4 | 3.13 미만의 warnings.warn(DeprecationWarning) 대체 | Exception | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 [L-E 준거: 버전 조건부 대안 → Exception] |
| 58 | `s092-16.1`/b2 | 블로킹 I/O 한정 스레드 사용 | Permission | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 [L-E 준거: 사용 조건 한정 → Permission] |
| 59 | `s092-16.1`/b3 | CPU 병렬화의 multiprocessing·C 확장 기본 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 60 | `s093-16.2`/b1 | 의사결정 #3 — 3.11+ asyncio.TaskGroup 기본 패턴 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 61 | `s094-16.3`/b1 | 의사결정 #2 — 3.13+ Free-threading 반영 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 62 | `s098-17`/b1 | 의사결정 #6 — 3단계 프로파일링 체계 사용 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 63 | `s109-19.4`/b1 | 인코딩·디코딩의 최원거리 경계 수행(유니코드 샌드위치) | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 64 | `s110-19.5`/b1 | for·while 뒤 else 사용 금지 | Prohibition | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 65 | `s111-19.6`/b1 | PEP 8 대상별 명명 스타일 표 준수 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 27종 전수 실독 — check-naming.py 는 dddjango 고유 축(#28 원전 패턴 약어·#30 자리표시자 접미·#41 폴더 패턴 낱말 등)이고 PEP 8 대소문자 관례를 무는 진단이 없음. §22.1 ruff select 에도 pep8-naming("N")이 없음 — 기본값 유지의 문면 근거 |
| 66 | `s111-19.6`/b3 | 밑줄 접두·접미 관례 표 준수 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 동상 — 27종 전수 실독 결과 밑줄 관례를 무는 검사기 없음(check-naming #30·#481 은 트리 폴더·파일 stem 축) |
| 67 | `s116-21`/b1 | 구조 패턴 선택 기준의 architecture-ddd(§5·§6) 소유 | Obligation | E: —<br>D: `agent-design-review-ddd` | 문면이 architecture-ddd §5·§6 을 소유자로 직접 지목 — 문서군 기본값 표의 architecture-ddd(설계 시점)→design-review-ddd 적용(기본값 이탈의 문면 근거) |
| 68 | `s116-21`/b1 | Django ORM 환경 적용의 implementation-django(§16) 담당 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 문면이 implementation-django §16 을 직접 지목 — 그 문서군 기본값도 discipline-reviewer(§16 표) |
| 69 | `s116-21`/b1 | 본 문서 범위의 Python 경계 도구 한정 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 70 | `s118-22.1`/b1 | 권장 pyproject.toml(ruff) 설정 준수 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 (ruff 설정 축을 무는 검사기 없음 — 문서 전체 check-*.py 언급 0건, P0 E03 §7) |
| 71 | `s121-23.1`/b1 | mypy strict 모드 설정 준수 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 72 | `s122-23.2`/b1 | pyright strict 모드 설정 준수 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 73 | `s124-24`/b1 | 테스트·디버깅의 implementation-test 위임 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 문면이 implementation-test 를 소유자로 직접 지목 — 그 문서군 기본값도 discipline-reviewer(§16 표) |
| 74 | `s126-25.1`/b1 | print 디버깅 시 repr 호출 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 75 | `s129-26.1`/b2 | 모듈 독스트링 형식 — 첫 줄 목적 + 공개 함수·클래스 목록 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 76 | `s129-26.1`/b3 | 클래스 독스트링 형식 — 목적 + 중요 공개 애트리뷰트·메서드 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 77 | `s129-26.1`/b4 | 함수 독스트링 형식 — 목적 + Args + Returns + Raises | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 78 | `s129-26.1`/b5 | 스크립트 독스트링 형식 — 사용법 메시지(명령행 구문·환경 변수·입출력 파일) | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 79 | `s129-26.1`/b6 | 어노테이션과 중복된 독스트링 타입 서술 삭제 | Obligation | E: —<br>D: `agent-discipline-reviewer` | 4원 지목 없음 — 위임 기본값 표(implementation-*→discipline-reviewer). check-*.py 27종 로스터 전수 실독 결과 담당 검사기 부재 |
| 80 | `s129-26.1`/b6 | 타입 어노테이션 상시 유지(houserules «모든 이름 첫 대입에 타입») | Obligation | E: `check-public-surface-annotation.py`<br>D: `agent-discipline-reviewer` | ①문면이 houserules «모든 이름 첫 대입에 타입» 을 직접 인용 ②check-public-surface-annotation.py docstring «#493 모든 이름은 «첫 대입»에 타입을 적는다 — 시그니처·속성·지역 변수에 예외가 없다» ③P0 E03 §7 «check-public-surface-annotation.py(§1/§26 어노테이션 규율, #493)가 해당 규칙을 지목» ④문법 없는 여덟 자리·선언적 클래스 본문 면제는 의미 레인 → reviewer 병기 |

### 2-1. 검사기 배선 6건 — 채택 근거 요약

| 검사기 | 배선된 Work | 결정적 근거(docstring 실독) |
|---|---|---|
| `check-context-isolation.py` | `s032-4.4`/b1 | 문면이 **전역규칙 #453·#454 를 축자 인용**하고, docstring OHS 절이 «#453/#454 «없다»는 답»을 자기 담당으로 선언한다. 기본값 도피 시 §16 «역도 성립» 오배선. |
| `check-choices-literal-consumption.py` | `s061-10.1`/b6 «심볼 소비» | docstring 표제가 «cleancode §2.14 소비 규율의 결정적 백스톱»이고, 이 Work 가 바로 그 §2.14 소비 규율 요지의 재진술이다. 커버 범위는 직접형 (a)(b) 뿐이라 reviewer 병기. |
| `check-domain-model.py` | `s072-12.0`/b2 «pydantic 고정 금지» · «invariant 소유 경계» | docstring #8 «domain_layer 의 밖으로 나가는 import 0 — django·다른 층·다른 BC·**서드파티**» — domain_layer 안 pydantic 고정은 결정적으로 차단된다. |
| `check-public-surface-annotation.py` | `s129-26.1`/b6 «어노테이션 상시 유지» | 문면이 houserules «모든 이름 첫 대입에 타입»을 인용하고 docstring #493 이 그 문장을 그대로 진다. P0 E03 §7 이 이 단방향 대응을 이미 기록. |

### 2-2. 배선 «하지 않은» 근거 — 기본값 도피가 아님을 증언하는 5건

로스터 `dddjango/scripts/check-*.py` **27종 전수**의 docstring 선두를 배선 전에 실독했다(§16 L-F 의무). 아래 5건은 «닮은 검사기»가 있으나 문면 근거가 없어 배선하지 않았고, 그 판단 근거를 남긴다.

1. **`s111-19.6` PEP 8 명명 규칙 → `check-naming.py` 비배선**. `check-naming.py` 의 32규칙은 전부 dddjango 고유 축(#28 원전 패턴 약어·#30 자리표시자 접미·#41 폴더 패턴 낱말·#340~#348 admin 자리…)이고 «snake_case/PascalCase/UPPER_SNAKE» 판정이 없다. 교차 확인: `s118-22.1` 의 ruff `select` 에도 pep8-naming(`"N"`)이 없다 — 저장소 어디에도 이 규범의 결정적 집행자가 없다.
2. **`s089-15.2` 최상위 예외 클래스 → `check-context-isolation.py` 비배선**. #166·#167·#168(기저 예외·상속·1클래스=1모듈)은 **OHS `contract/exception/` 한정**이고, 이 절 문면은 «API 모듈» 일반을 말할 뿐 OHS 자리를 지목하지 않는다. `check-business-vocabulary.py` #585(exception.py 필수·도메인 상속 금지)도 `framework/` 계약 자리 한정이라 같은 이유로 비배선.
3. **`s061-10.1` 승격(1207·1211-b)·`==` 비교(1211-d) → `check-choices-literal-consumption.py` 비배선**. 같은 검사기 docstring 이 «보지 않는 것(의미 레인 = discipline-reviewer 몫)»으로 **«닫힌 집합의 미승격»·«비교식(`x.status == "…"`)»을 명시 배제**한다. 같은 절 안에서 한 Work 는 배선하고 세 Work 는 배선하지 않은 것이 이 근거다.
4. **`s004-1.2` `--strict-optional`·`s121-23.1` mypy·`s122-23.2` pyright·`s118-22.1` ruff → 비배선**. 타입 체커·린터 «설정 파일»을 무는 검사기는 `check-test-config.py` 하나뿐이고, 그 docstring 이 자기 관할을 **세 슬라이스로 명시 선언**한다 — ⑴pytest↔Django settings 바인딩 ⑵`test/` 구조(#383~#392 — 직계 자식 5·unit DB 금지·factories 자리) ⑶`<project>/settings/` 환경축(#445~#447). `[tool.mypy]`·`[tool.ruff]`·`pyrightconfig.json` 은 세 슬라이스 어디에도 없다(적대 리뷰 F6 정정 — 옛 문구의 «pytest 바인딩 한정»은 관할을 과소 기술했으나 비배선 결론은 무변).
5. **`s072-12.0` W46(validator 의 도메인 규칙 소유 금지)·W48(중복 domain model 금지) → `check-usecase-dto-placement.py` 비배선**. 27종 중 **가장 닮은 검사기**라 근거를 명시한다(라운드 2 R2-6). docstring 의 인접 축은 #139(«제약 선언은 `schema_in.py` 에 — 컨트롤러의 Field·validator 는 위반»)·#142(«요청 스키마는 도메인 객체를 만들지 않는다»)·#202/#207(«DTO 에 애그리거트·엔티티·ORM 행 금지»)인데, **술어가 어긋난다** — ⑴#139 는 제약 선언의 **자리**(컨트롤러↔`schema_in`)를 묻지 validator 가 무엇을 소유하는지 묻지 않는다. ⑵#142 는 스키마가 **도메인 객체를 생성**하는 형태를 잡고, W46 의 대표 실패(금액 계산·상태 전이를 원시 연산으로 **대행**하는 validator — 도메인 객체를 만들지 않는다)에는 발화하지 않는다. ⑶#202/#207 은 DTO 가 도메인 타입을 **실어 나르는** 것을 막고, W48 의 «pydantic 으로 도메인 모델을 **다시 짓는** 것»과 방향이 반대다. ⑷세 규칙 모두 `application_layer/`·`driving_layer/api/**/schema/` **경로 한정**인데 W46·W48 은 자리를 한정하지 않는 언어 규범이다. — W44·W45 를 `check-domain-model.py` 로 «부분 커버 공개» 배선한 것과의 비대칭은, 저쪽은 문면의 자리(`domain_layer` 안 pydantic 고정)가 검사기 술어(#8 서드파티 import 0)와 **정확히 포개진** 반면 여기는 포개지는 자리가 없다는 차이다.

## 3. 재진술 유예 (다른 문서 상대 — spec 미기재 · T3 소급 패스 대상)

발주서 재진술 열을 좌표 삼아 상대 문서를 **직접 열어 확인**했다(`dddjango/skills/implementation-python/SKILL.md` — s003 «언제 쓰나» 9–17행 위임 4건, s004 «핵심 운영 원칙» 18–31행 요약 11불릿 · `dddjango/skills/discipline-houserules/SKILL.md` — s007-4 «§4 타입 어노테이션» 49–60행).

발주서 재진술 열은 브리프 worksheet 양식 3 문면대로 **«참고»지 한정 열거가 아니다** — 열이 `N` 이어도 실물 대조로 사본 관계가 성립하면 유예로 올리고 «census 과소 후보»를 병기한다(적대 리뷰 F1·F4 준거 — 15·19번, 라운드 2 R2-1·R2-2·R2-4 준거 — 3·4·14번이 그 경우). 역으로 **성립하지 않으면 올리지 않고 §3-1 에 기각 판정을 남긴다** — 기준은 한 방향으로만 쓰지 않는다.

| # | 사본 블록(이 문서) | 상대 문서/절 | 확인한 상대 문면 | 비고 |
|---|---|---|---|---|
| 1 | `s001`/b1 W1(cleancode 위임) | `implementation-python-skill`/s003 | 13행 «네이밍·함수 설계·SOLID 등 기술무관 클린코드 원칙 → `discipline-cleancode`» | 서문·SKILL·§20 3중(§20 은 문서 내라 spec `restates` 로 이미 연결) |
| 2 | `s004-1.2`/b1·b4 | `implementation-python-skill`/s004 | 20행 «타입 어노테이션은 전 코드베이스에 일관 적용, **Optional→X \| None**, 최신 PEP 695 문법 우선 (§1)» | **강도 불일치(P0 특이3)** — final 은 `Optional[X]` 명시를 지시하고 SKILL 은 `X \| None` 을 지시. 소급 연결 시 단순 restates 가 아니라 개정 후보로 다뤄야 함 |
| 3 | `s005-1.3`/b1 W5(합 타입으로 비정상 상태 배제) | `implementation-python-skill`/s004 | 21행 «Union/Literal/NewType으로 상태 공간을 좁혀 잘못된 상태를 타입 레벨에서 차단 **(§1.3–§1.4)**» | **요약 재진술**(SKILL «Union…으로 잘못된 상태 차단» ↔ final 58행 «합 타입(Sum Type)을 사용해 비정상 상태를 배제하라») — 앵커가 §1.3 을 명시 지목. §1.4(NewType) 몫은 REF 범위 밖이라 s005 절반만 대응. 발주서 열 `N` 이나 실물 대조로 성립 → **census 과소 후보** 병기(라운드 2 R2-2). 6·11번과 같은 요약 수준 |
| 4 | `s032-4.4` 절 헤딩(622행 — b1 은 OHS 예외 blockquote) | `implementation-python-skill`/s004 | 27행 **후단** «예외는 도메인 최상위 클래스 정의 후 계층화; **None 반환 대신 예외 발생** (§15)» | **헤딩 축자 사본** — «None 반환 대신 예외 발생»은 원문 grep 유일 등장이 622행 §4.4 헤딩이고 §15(1716–1791행)에는 이 문구가 없다. 10번과 **같은 불릿의 뒤 절반**(세미콜론 분할 — 15·16·17번 선례와 동형). SKILL 앵커 «(§15)»는 **§4.4 를 빠뜨린 오앵커**로 병기 — 소급 시 앵커 개정 후보. 9번(헤딩이 규범을 지는 절)의 등재 선례 준거. spec 무변 |
| 5 | `s039-6.1`/b1 | `implementation-python-skill`/s004 | 24행 «디스크립터·@property는 검증과 지연 계산에만; 단순 필드는 평범한 애트리뷰트로 (§6–§7)» | SKILL 쪽이 «검증·지연 계산에만» 한정을 추가 — 강도 상이 |
| 6 | `s042-7.1`/b1 | `implementation-python-skill`/s004 | 24행 후단 «단순 필드는 평범한 애트리뷰트로 (§6–§7)» | 5번과 같은 불릿이 두 절을 함께 요약 |
| 7 | `s061-10.1`/b6 W1·W2·W3·W4 | `discipline-cleancode`/§2.14 | 이 절 문면 자체가 «소유자는 `discipline-cleancode` §2.14다 — 요지: …»로 **소유 지정 + 요지 재진술**을 자기 선언 | 정본은 cleancode §2.14. 소급 패스에서 이 4 Work 를 cleancode 정본 블록에 restates 로 걸어야 함 |
| 8 | `s072-12.0` 전체(11 Work) | `implementation-python-skill`/s004 | 29행 «pydantic v2는 경계(입력 검증) 전용, 도메인 진리값으로 사용 금지 (§12.0)» | SKILL 1불릿 ↔ final 11 Work — 요약 대 상세(1:N) |
| 9 | `s081-13.5`/b1 | `implementation-python-skill`/s004 | 25행 «제너레이터로 지연 평가, **send/throw 금지** (§13.2, §13.5)» | SKILL 은 «금지»(final 헤딩과 동형), final 본문은 «대안 지시» — 규범 유형이 갈릴 수 있음 |
| 10 | `s089-15.2`/b1 | `implementation-python-skill`/s004 | 27행 **전단** «**예외는 도메인 최상위 클래스 정의 후 계층화**; None 반환 대신 예외 발생 (§15)» | 후단(«None 반환 대신 예외 발생»)은 §15 가 아니라 §4.4 헤딩의 사본이라 4번으로 분리 등재(라운드 2 R2-1) |
| 11 | `s092-16.1`/b2·b3 | `implementation-python-skill`/s004 | 28행 «I/O 병목엔 asyncio.TaskGroup(3.11+), **CPU 병목엔 멀티프로세싱** (§16)» | |
| 12 | `s093-16.2`/b1 | `implementation-python-skill`/s004 | 28행 전단 «I/O 병목엔 asyncio.TaskGroup(3.11+)» | 11번과 같은 불릿 |
| 13 | `s116-21`/b1 W1 | `implementation-python-skill`/s003 | 15행 «repository/UoW/핵사고날/CQRS/outbox 구조 패턴 선택 → `architecture-ddd`» | SKILL 상세 레퍼런스 표에 §21 **미등재**(P0 특이4·6) — 소급 시 표 결번도 같이 봐야 함 |
| 14 | `s116-21`/b1 W2(Django ORM 적용의 implementation-django 담당) | `implementation-python-skill`/s003 | 14행 «Django 모델·ORM·**서비스**·트랜잭션·설정 구현 → `implementation-django`» | **채택(확신 중)** — 같은 문장이 지는 두 위임 중 뒤 절반이고, final 이 지목한 «§16 **서비스 레이어**»가 SKILL 14행의 «서비스»와 겹친다. s003 위임 4불릿(13·14·15·16행) 중 14행만 무배정으로 남아 있던 자리(1·13·18번과 대칭). 다만 SKILL 은 Django 구현 **전반**, final W2 는 «구조 패턴의 Django 적용»이라 **상대 쪽이 넓은 1:N 요약** — 소급 연결 시 축 차이 병기(라운드 2 R2-4) |
| 15 | `s118-22.1`/b1 | `implementation-python-skill`/s004 | 30행 **전단** «**Ruff로 린트·포맷 통합**, mypy/pyright strict 모드로 타입 보장 (§22–§23)» | 요약 1:N(SKILL 1구 ↔ final §22.1 ruff 설정 규범) — s072(8번)와 같은 구조. 발주서 열 `N` 이나 실물 대조로 성립 → **census 과소 후보** 병기(적대 리뷰 F4). 16·17번과 **같은 불릿의 앞 절반** |
| 16 | `s121-23.1`/b1 | `implementation-python-skill`/s004 | 30행 «Ruff로 린트·포맷 통합, **mypy/pyright strict 모드로 타입 보장** (§22–§23)» | |
| 17 | `s122-23.2`/b1 | `implementation-python-skill`/s004 | 30행 후단(16번과 같은 불릿) | |
| 18 | `s124-24`/b1 | `implementation-python-skill`/s003 | 16행 «테스트 코드 작성(pytest·픽스처·mock·더블) → `implementation-test`» | SKILL 상세 레퍼런스 표에 §24 **미등재**(P0 특이6) — §25 디버깅 절 존재와 긴장 |
| 19 | `s129-26.1`/b6 W80(타입 어노테이션 상시 유지) | `discipline-houserules-skill`/s007-4(§4 타입 어노테이션) | 51행 «**모든 이름은 «첫 대입»에 타입을 적는다 — 예외 0.**» | **축자 인용** — 2490행 괄호가 이 문면을 직접 인용하고 spec basis ①도 그렇게 자인한다. houserules `references/final.md` 에는 이 문장이 없어(grep 0건) **정본은 SKILL.md 쪽**. 발주서 열 `N` 이나 실물 대조로 성립 → **census 과소 후보** 병기(적대 리뷰 F1). spec 은 무변 — 교차 문서라 §15 대로 `restates` 미기재가 옳다 |

**비문서 상대 1건(별도 계상)** — `s032-4.4`/b1 ↔ **전역규칙 #453·#454**. 발주서 재진술 열이 `Y:전역규칙#453·#454`인데 이 상대는 문서 절 좌표가 아니라 rule-owner-map 의 규칙 번호다. 재진술이 아니라 **#N↔Work 조인**이므로 `wiring/aliases.ttl`(§14 alias 대장) 소관이고, `check-context-isolation.py` docstring 이 «조인 확정: rule#3 → djr:R-0124 · 미확정 #N 은 T3 이관에서 해소»라고 이미 예고한 자리다. 이 Work 는 `enforcedBy check-context-isolation.py` 로 배선해 뒀으니 소급 패스는 alias 등재만 하면 된다.

**합계: 유예 20건**(문서 상대 19 + 비문서 상대 1). — 라운드 1 반영으로 2행(구 #12·#16), **라운드 2 반영으로 3행**(신 #3 `s005-1.3` · #4 `s032-4.4` · #14 `s116-21` W2) 추가하고 절 순으로 전건 재번호했다.

### 3-1. 유예 미등재 — 후보 판정 기록

«열 `N` 이어도 실물 성립 시 등재»의 반대 방향도 기록으로 남긴다 — **실물 대조 결과 사본 관계가 성립하지 않아 유예에 올리지 않은** 후보다.

| 후보 쌍 | 확인한 상대 문면 | 판정 | 근거 |
|---|---|---|---|
| `s063-10.3`/b1(의사결정 #7 — `dataclass(slots=True)` 권장) ↔ `implementation-python-skill`/s004 23행 전단 | «**dataclass(slots, frozen, kw_only)로 불변 값 객체를 표현**, NamedTuple은 불변 레코드에 (§10)» | **기각**(사본 아님 — 유예 미등재) | ⑴SKILL 불릿의 주술은 «…로 **불변 값 객체를 표현**»이라 정본이 `frozen` 축(§10.4)이고, `slots`·`kw_only` 는 괄호 안 **옵션 열거**다. s063-10.3 의 규범은 «메모리 최적화 목적의 `slots=True` 권장»이라 **술어가 다르다**. ⑵앵커 «(§10)»는 절 지목이 아니라 장 지목이고, 그 장에서 이 불릿이 묶는 §10.4·§10.5·§10.8 은 REF 범위 밖이라 대응 상대가 특정되지 않는다. ⑶15·19번처럼 «실물 대조로 성립»한 축자·요약 사본과 달리 여기는 **기능 열거의 낱말 겹침**뿐이다. — 소급 패스가 «장 앵커 불릿 = 1:N 요약»으로 재해석하기로 하면 재검 대상이므로 좌표만 남긴다(라운드 2 R2-3). |

## 4. 경계 판단 메모

**① 공백 소유 — §13 문면(선행 블록 후행 귀속)을 전건 적용**. 블록 간 빈 줄은 예외 없이 **선행 블록의 후행 스팬**에 넣었고, 절 선두 구분자(헤딩 직후 빈 줄)만 §13 명문 예외대로 **첫 블록의 선두 스팬**에 넣었다. 결과적으로 각 절의 마지막 블록이 절 끝 빈 줄을 지고, `code` 블록은 닫는 펜스 뒤 빈 줄까지 포함한다.
- **파일럿 판형과의 차이를 자인**: `spec-architecture-ddd-final.json`·`spec-implementation-django-ninja-final.json` 및 선행 T3 spec 일부는 구분자를 **후행 블록 선두**에 넣은 사례가 섞여 있다(기계 재검: cleancode spec 비최초 블록 58/199 가 빈 줄로 시작). 본 spec 은 **한 방향으로만** 통일했다 — byte 등가는 도구의 «헤딩+블록 연결 = 절 스팬» 단언이 42/42 통과로 증명한다.
- **펜스 verbatim과의 충돌 처리**: §13 은 «code 리터럴 = 여는 펜스~닫는 펜스 전체 라인 verbatim»도 말한다. 두 규정은 펜스에 인접한 빈 줄에서 필연적으로 충돌하므로, 펜스 규정을 «리터럴 **코어**의 정의»로 읽고 구분자 귀속은 §13 첫 문장을 우선했다. 첫 블록이 곧바로 펜스인 **7절**(`s049-8.5`·`s061-10.1`·`s070-11.1`·`s118-22.1`·`s121-23.1`·`s122-23.2`·`s129-26.1`)에서는 첫 블록이 `code` 이면서 선두 빈 줄을 진다.

**② 불릿 분해 규칙** — 규범을 진 불릿은 **항 단위 1블록**(§13 «리스트 항»)으로 쪼개 Work↔블록 대응을 1:1 에 가깝게 유지했고, **규범이 하나도 없는 연속 불릿 묶음은 1 prose 블록**으로 합쳤다(`s049-8.5`/b3 = 972–974 · `s094-16.3`/b4 = 1887–1892). 쪼갬과 합침의 자는 «Work 가 붙는가» 하나다.

**③ `kind=code` 에 `norms` 를 붙인 3절** — `s118-22.1`(pyproject.toml)·`s121-23.1`(mypy)·`s122-23.2`(pyright)는 **운반체가 펜스뿐**이고 그 설정 블록 자체가 구속 규범이다(P0 «예제 아닌 구속 설정» 방침 승계). 산문 요약을 지어내 `norm` 블록을 만드는 것은 원문에 없는 문장을 창작하는 것이라, kind 는 실물대로 `code` 로 두고 `norms` 만 얹었다. `s129-26.1`/b1(독스트링 예제)은 반대로 **예제**라 규범을 얹지 않았다 — 가르는 자는 «이 펜스가 준수 대상인가, 예시인가»다.

**④ `table-row` 계수 축과 블록 분해 축** — `s111-19.6` 의 두 표는 **표 단위 1 규범**(P0 방침)이므로 표 전체(머리행·구분행 포함)를 `table-row` **1블록**으로 묶고 norms 1 을 얹었다. 파일럿 ddd `s051-8`(의사결정 표)은 행마다 별개 의사결정이라 행 단위로 쪼갰는데, 여기 두 표는 «표 하나 = 관례 한 벌»이라 행을 쪼개면 없는 규범이 7·5개씩 생긴다.
- **«행 단위 분해가 의무»라는 지적(적대 리뷰 F2)은 기각한다** — 근거는 `ontology-authoring.md` 131행 «블록 경계는 언제나 §13 자연 단위(문단·불릿·펜스·**표 행 묶음** — 행 범위)»다. 명문 자연 단위에 «표 행 묶음»이 들어 있으므로 표 한 벌을 1블록으로 묶는 것은 §13 위반이 아니다. §13 128행의 «표 머리행·구분행도 kind=table-row»는 **머리·구분행의 kind 귀속**을 정한 문장이지 1행=1블록을 명하지 않으며, 브리프 kind 정의의 «행 단위»도 스팬이 행 범위라는 뜻으로 읽는 것이 131행과 정합한다.
- 다만 파일럿 ddd `s051-8` 은 행 단위, T3 동료 3건(implementation-django `s067-14.1`·implementation-test `s004-1.1`/`s008-2`/`s034-7.1`)은 표 단위라 **관례가 갈라져 있다**. 가르는 자는 «표 한 벌이 규범 하나인가, 행마다 규범인가»라는 것이 본 spec 의 입장이고, 이 자를 브리프/§13 에 명문화할지는 **T3 총괄 회부 사항**(spec 4파일 공통 쟁점)으로 남긴다 — 블록 분해가 바뀌어도 byte 등가·계수는 불변이므로 소급 정합 비용은 기계적이다.

**⑤ 재진술 판정 — 채택 1건, 기각 1건**
- **채택**: `s112-20`/b1 → `s001`/b1. 같은 문서·같은 취지(«범용 디자인 패턴/클린코드 원칙은 `discipline-cleancode`»)라 §15 대로 사본에 `restates` 만 걸고 Work 는 안 채번했다. 발주서 재진술 열이 `Y:implementation-python-final/s001`(자기 문서)이라 브리프 조건에 정확히 부합한다.
- **기각**: `s040-6.2`/b3(«레거시 참고») → b1(의사결정 #5). 두 블록이 «`instance.__dict__` 직접 저장 권장»을 겹쳐 말하지만 b1 은 **무조건 채택 지시**이고 b3 은 «`__set_name__`(3.6+) 도입 **이후로는**»이라는 **버전 조건부 권장**이다. §15 의 restates 는 «사본 블록»을 위한 장치고 여기 둘은 축자 사본이 아니다. 발주서 재진술 열도 `N` 이다 — 둘 다 Work 로 승격했다(P0 계수 2 승계).
- **기각(적대 리뷰 F7 판정 기록)**: `s111-19.6`/b3(밑줄 관례 표) → `s049-8.5`/b2. 2159행 `__var` 행(«네임 맹글링. 하위 클래스 충돌 방지 전용»)과 971행(«`__var`: 네임 맹글링 발생. 하위 클래스 필드명 충돌 방지에만 사용하라.»)이 **같은 규범의 문서 내 중복**인 것은 사실로 확인했다. 그럼에도 `restates` 를 걸지 않는다 — `ontology_migrate.py` 의 `restates` 는 **블록 대 블록** 술어(대상 IRI = `…/b<order>`)인데, b3 은 5행짜리 관례 한 벌을 지는 블록이고 중복은 그중 **한 행뿐**이라 블록 전체를 «s049 b2 의 재진술»로 선언하면 나머지 4행(`_var`·`var_`·`__var__`·`_`)까지 사본이라 주장하는 과대 진술이 된다. §15 의 사본 장치는 «블록이 통째로 사본»인 꼴을 위한 것이고 여기는 부분집합 포함 관계다. 발주서 재진술 열도 `N`. — **행 단위 재진술이 필요하다면 그것은 spec 스키마의 표현력 문제**이므로 소급 패스 쟁점(§4-④ 표 분해 축과 한 묶음)으로 회부한다.
- **기각(라운드 2 R2-5 판정 기록)**: `s061-10.1`/b8(1213행) → 같은 절 b5(1210행). 1213행 선두 «`Literal` vs `Enum` 분업(PEP 586): **위의 "지역적 분기 표현이면 `Literal` 가능"은 유지하되**»가 b5 의 Permission(«값 집합이 작고 지역적인 분기 표현이면 `Literal`도 가능하지만…»)을 **절 안에서 다시 확인하는 구**임은 사실로 확인했다. 그럼에도 `restates` 를 걸지 않는다 — **F7 과 동형의 부분집합 문제**다. b8 은 자기 Work 3건(도메인=Enum · 외부 API=Literal · 잠긴 자리 리터럴 허용)을 지는 블록이고 b5 재확인은 그중 **선두 종속절 하나**뿐이라, 블록 대 블록 술어(`…/b<order>`)로 b8 전체를 «b5 의 사본»이라 선언하면 나머지 3 Work 까지 사본이라 주장하는 과대 진술이 된다. 게다가 이 구는 **인용이 아니라 유효 범위 조정**(«유지하되 … 로 가른다»)이라 §15 의 «사본 블록» 꼴이 아니고, b5 의 Permission 과 b8 의 세 Work 는 spec 에 모두 별개로 채번돼 있어 규범 자체는 누락이 없다. 발주서 재진술 열도 `N`. — 행 단위 표현력 쟁점 목록에 이 쌍을 F7 과 나란히 올린다.

**⑥ 규범/산문 경계 판정**
- **포함(P0 «애매하면 포함» 승계)**: `s013-1.11`(Concatenate 용처 서술) · `s039-6.1`(디스크립터 정의문 끝의 «재사용 가능한 애트리뷰트 로직에 사용한다») · `s053-8.9`(«상속하면 누락을 방지한다» 효과 서술).
- **제외**: `s004-1.2` 53행(**전단** `Optional[X]`≡`Union[X,None]` 동등성 사실 서술 · **후단** «Python 3.10+에서는 `X | None`을 사용할 수 있다»도 제외 — 아래 명시 판정) · `s014-1.12` 308행(TypeIs↔TypeGuard 기능 차이) · `s063-10.3` 1252행(«주의» 다중 상속 충돌) · `s090-15.3` 1786행(`__deprecated__` 속성 자동 추가) · `s092-16.1` 1796행(GIL 사실) · `s093-16.2` 1857행·`s094-16.3` 1863·1887–1891행(레거시·현재 상태 목록). 전부 **규범 동사가 없고 사실만 진술**한다는 한 가지 자로 걸렀고, 발주서 계수와 전건 일치한다.
- **제외 판정 명시(적대 리뷰 F3)** — `s092-16.1` **1798행 후단** «Free-threaded 빌드(3.13+)에서는 스레드도 가능». Permission 미채번을 유지한다. 자: ⑴«가능»의 주어가 **빌드의 능력**이라 같은 불릿 앞의 «기본적으로 `multiprocessing`이나 C 확장 사용»(채번된 Obligation)과 달리 **지시 동사가 없다** — 1796행 GIL 사실과 같은 층이다. ⑵1797행의 «**스레드 사용**: 블로킹 I/O 시»가 Permission 으로 채번된 것과 비대칭이 아니다 — 저쪽은 «어느 때 쓰라»는 **용처 지정**이고 이쪽은 «되기도 한다»는 **가능성 진술**이다. ⑶ Free-threading 채택 축은 같은 문서 `s094-16.3` 의사결정 #2 가 별도 소유하므로 이 구는 그 요지의 절내 압축이다. ⑷ 발주서 계수 2 와 일치한다. — 다만 «조건부 허용»으로 읽을 여지가 남으므로 **census 과소 후보**로 병기해 소급 개정 판단에 넘긴다.
- **제외 판정 명시(라운드 2 R2-7)** — `s004-1.2` **53행 후단** «Python 3.10+에서는 `X | None`을 사용할 수 있다». Permission 미채번을 유지한다. 자: ⑴«가능»의 주어가 **런타임 문법의 가용성**(3.10+ 에서 이 표기가 문법으로 존재한다)이라 F3(1798행 «빌드의 능력») 과 같은 층이고, 1797행 «**스레드 사용**: 블로킹 I/O 시»처럼 «어느 때 쓰라»는 **용처 지정**이 없다. ⑵같은 불릿 전단이 동등성 사실 서술이라 문장 전체가 **표기 등가 안내** 한 벌로 읽히고, 이 절의 채번된 두 규범은 b1(«Optional 로 None 가능성을 명시하라»)·b4(«`--strict-optional` 로 강제하라»)라는 **지시 동사 문장**이다. ⑶발주서 계수 2 와 일치한다. — 다만 이 자리는 SKILL 20행이 «Optional→`X | None`»을 **지시**하는 것과의 **강도 불일치(P0 특이3 · 유예 #2)**와 얽혀 있다. 소급 개정이 SKILL 쪽 지시를 정본으로 삼으면 이 후단이 그 지시의 final 쪽 근거 자리가 되므로, **P0 특이3 개정 후보와 연동해** census 과소 후보로 병기한다.

**⑦ 규범 유형(class) 판정의 자** — 조건·한정 조항은 L-E 준거로 `Exception`(`s014-1.12` TypeGuard 특수 경우 · `s049-8.5` `__var` 용도 한정 · `s061-10.1` StrEnum 불가 시 대안 · `s072-12.0` 의도한 coercion · `s090-15.3` 3.13 미만), 조건부 «가능/허용»은 `Permission`(`s061-10.1` 지역 분기 Literal · Literal 로 잠긴 자리 · `s092-16.1` 블로킹 I/O 스레드), 금지 동사는 `Prohibition`(`s110-19.5` · `s061-10.1` frozenset 재정의 · `s072-12.0` 4건)로 갈랐다. `Override` 는 이 문서에 우선 규칙 문면이 없어 0건이다.

**⑧ 좌표 재확인** — 발주서에 드리프트 경고가 없고 «현재 2675행 — 센서스와 일치»라 했으나, 42절 전건에 대해 도구가 **센서스 좌표 대조 + 절 스팬 sha256 대조**를 통과했다(불일치 시 exit 1). 헤딩 재확정이 필요한 절은 없었다.
