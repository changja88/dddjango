# 검사 술어 — `human` 158건 재분류의 산출물

**2026-08-11 · ㉰** · 대상 명세 `2026-08-08-tree-revision-spec.md` (531규칙)

이 문서는 **6번(플러그인 개발)이 그대로 받는 재료**다. 명세는 «무엇이 참이어야 하나»만 적고, 여기는 **«어떻게 재나»**를 적는다.

재분류의 규칙은 하나였다 — **「`ast`/`path`/`ast+` 로 내리려면 술어를 «실제로 써라». 못 쓰면 `human`」.**

```
human 158  →  path 11 · ast 63 · ast+ 57 · human 27
                                            └ 면제 16 + 실질 11
```

**08-11 · Phase 0 린트** — #390·#603 은 술어가 «확정»만으로 서서 `ast` 로 한 단계 더 내려갔고(전수는 ast 281 · ast+ 55 가 됐다), ㉰ 밖에서 이미 `ast+` 였던 #512·#584·#594·#595 의 항목을 더했다.

`ast+` 행은 반드시 셋을 함께 적는다 — ⑴ **확정 위반** 술어 ⑵ **후보** 술어 ⑶ 사람이 답할 **한 물음**.

---

## ★ 술어를 쓰기 전에 읽을 것 넷

### ⓐ `#628`(업무 어휘 토큰 집합)을 «쓰면 안 되는» 자리가 있다

```
#518 #562 #587 #617 (framework·pure)   업무 어휘가 «0이어야» 한다   →  토큰 검사가 선다
#228 (port/<capability>/<data>_*)      «정의 위치»가 금지선이다     →  애너테이션이 가리키는 «파일»을 본다
```

`#228` 에 토큰 검사를 걸면 「펴서 싣는」 `child_id` 가 **전부 오탐**이 된다.

### ⓑ 불용어 목록이 없으면 framework 검사가 무너진다

`Id`·`Status`·`Name`·`Item`·`Type`·`Value` 는 어느 BC 에나 있다. `#628` 에 「불용어 목록도 «저장소가 유지하는 데이터»다」를 박아 뒀다(㉰ 반영).

### ⓒ 목록은 «닫지» 않는다

`#367` 이 세운 방식 — 의존성·기술 이름·계기 낱말 목록은 **«저장소가 유지하는 데이터»**이지 규칙 문장 안의 닫힌 열거가 아니다. 닫으면 새 항목이 들어올 때 검사가 **조용히 통과**한다.

### ⓓ 「무엇이 X 인가」는 «이름»이 아니라 «타입이 온 파일»로 가른다

**08-11 · C7** — `#546`(한 트랜잭션 = 애그리거트 하나)의 검사가 오탐 셋을 낸 원인이 이것이었다.

```
✗  이름이 .save(…) 인 호출을 센다          → audit_log.save · order.lines.remove 가 걸린다
✓  타입이 domain_layer/<aggregate>/<aggregate>_repository.py 에서 온 것만 센다
```

**별칭도 이 방식이 옳게 다룬다** — `repo = self._order_repository` 는 타입이 같으므로 «하나»로 세어져 배치 면제가 산다.

이름 규칙(`#597` 의 `save`·`remove`)은 **그 타입 «안에서» 무엇이 쓰기인지 가르는 데만** 쓴다. 거꾸로 쓰면(「`save` 라는 이름을 리포지토리만 쓴다」) 새 금지가 하나 늘고 **얻는 것은 0이다.**

---

## 물음이 모이는 자리 — 소유자를 하나로

독립 술어를 새로 써야 하는 것은 절반이 안 된다.

| 물음 | 쓰는 규칙 | **소유자** |
|---|---|---|
| 두 번 받아도 같은 결과인가(멱등) | #181 · #532 · #603⑵ | **#181** |
| 그것이 바뀌어도 이 이름이 그대로인가 | #584 · #594 · #512 | **#595** |
| 이 조건이 업무 규칙인가(Q2) | #553 · #607 · #589 · #475 · #316 | **#553** |
| 업무가 이 단계 이름을 입으로 부르나 | #564 · #565 | **#565** |
| 이 값이 사람이 읽을 문구인가 | #590 · #618 | **#590** |
| 업무 어휘 토큰 집합 | #47 · #372 · #463 · #617 · #518 · #562 · #587 | **#628** |
| 이 손잡이를 «연 쪽»이 «닫기»까지 하나 | #11 · #203(걷힘) | **#11** |
| 주어가 애그리거트인가 화면인가 | #355 · #285 | **#355** |

**술어가 이미 다른 행에 있는 것** — #559(=#560∧#561∧#562) · #580(=#579) · #556㉡(=#557) · #530(=#529) · #591(=#613 슬라이스) · #567 폴더겹(=#201) · #618㉠(=#588) · #470(=#606⑵) · #366(=#367) · #178(=#179∧#509∧#490)

---

# 묶음 1 — `#5` ~ `#103`

| # | 바꿈 | 술어 |
|---|---|---|
| 5 | ast | `domain_layer/**`·`application_layer/**` 의 import 집합 − 허용목록(#7 넷 · #8 0) ≠ ∅ 이면 위반. **더해서** 그 검사에 파일·줄 단위 면제 표식(`# noqa`, `# check-*: allow/skip`, 검사기 skip 상수)이 하나라도 붙으면 위반 |
| 11 | ast+ | 확정: 경계 파일의 애너테이션 타입이 ⑴`django.db.models.Model` 하위 ⑵`domain_layer/<aggregate>/{<aggregate>.py,entity/}` 정의 ⑶`QuerySet` / 후보: 스칼라·`Iterator[bytes]`·같은 층 dataclass 가 아닌 타입 / 물음: 「이 손잡이를 «연 쪽»이 «닫기»까지 하나」 |
| 14 | ast | `With` 노드 중 item 애너테이션이 `*UnitOfWork` 인 것의 body 안 모든 `Call` 리시버 타입이 **크로스-BC 포트 집합**(= `adapter/anticorruption_layer/<other_bc>/` 클래스가 상속하는 `port/**/*_port.py` 클래스)에 들면 위반 |
| 17 | ast+ | 확정: `domain_layer/*/`·`application_layer/*/` 에서 고정 이름을 뺀 폴더 이름이 **종류 낱말 deny-list** 에 들면 위반 / 후보: deny-list 밖인데 #628 토큰 집합에 없는 이름 / 물음: **Q1** |
| 18 | ast+ | 확정: #490 이 이미 잡는다 / 후보: `<aggregate>/`·`<area>/` 자신의 이름이 종류 낱말 deny-list 에 들 때 / 물음: **Q1** |
| 19 | path | 폴더 이름 N 이 **기술 이름 집합**(`sys.stdlib_module_names` ∪ `packages_distributions()` 최상위 모듈명)에 **정확히 일치**하면서 `framework/` 직계가 아니면 위반 (`django_<bc>` 는 정확 일치가 아니라 통과) |
| 20 | path | 트리 고정 칸이 **아닌** 폴더 중 자식이 정확히 1개이고 그것이 파일이면 위반 (**#21 이 같은 술어로 이미 `path`**) |
| 28 | path | 경로 마디·파일 stem 을 `_` 로 토큰화해 **원전 패턴 약어 deny-list**{repo,uow,acl,vo,ohs,agg,spec,svc,ctrl,impl,mgr,cfg,service(단독)} 에 들면 위반. 예외는 #148 의 `api` |
| 33 | path | 파일 stem 의 첫 `_`-토큰 T 가 **트리 폴더 이름 집합**에 속하는데 조상 경로에 `T/` 가 없으면 위반 |
| 34 | path | 같은 접두 토큰 P 를 가진 파일 전부의 «부모 칸 id» 집합 크기 > 1 이면 위반 ※ **괄호의 `dto_*` 예시는 죽은 문면**(D40·D55 가 `<use_case>_command.py` 로 바꿨다) |
| 36 | ast+ | 확정: 이름이 **정도 낱말 deny-list**{common,shared,base,core,util(s),helper(s),misc,etc,general,lib,support} / 후보: deny-list 밖인데 #628·트리 고정 이름에도 없는 새 칸 / 물음: 「이 이름에 예/아니오로 답하는 물음이 붙나」 |
| 44 | path | BC 마다 `vo = stem(domain_layer/*/value_object/*.py) ∪ stem(shared_value_object/*.py)`, `ds = stem(domain_service/*.py)`. `vo ∩ ds ≠ ∅` 이면 위반 |
| 47 | ast | `framework/<capability>/<capability>_port.py` 의 {클래스명 ∪ 함수명 ∪ 인자명 ∪ 애너테이션 식별자} 토큰 ∩ **#628 전 BC 합집합** ≠ ∅ 이면 위반 (docstring·주석 제외 — 「이름에도 시그니처에도」 축자) |
| 49 | ast | ⑴`application/*` 에 트리 밖 BC 폴더 ⑵`framework/` 아래 `shared_kernel/`·`common/`·`domain/` ⑶타 BC import 가 OHS·`published_event/` 밖(=#12) ⑷`pure/` 에 업무 어휘(=#562) |
| 52 | ast | `framework/**` 각 파일의 식별자·문자열 리터럴·import 경로 토큰 ∩ (**BC 이름 집합** ∪ #628 전 BC 합집합) ≠ ∅ 이면 위반 |
| 54 | ast+ | 후보: `scripts/check-*.py` 에서 «대상·예외 선정»에 쓰이는 문자열 리터럴 중 트리 고정 칸 화이트리스트 밖의 것 / 물음: 「이 목록이 규칙인가 주소인가」 ※ **실측 위반 있음** — `check-layer-skeleton.py:80` 의 `LAYER_DIRS` |
| 68 | ast+ | 후보: 검증 목적 `raise`(`if not <cond>: raise` · validator · `__post_init__`)가 허용 두 자리(`schema_in.py` · `domain_layer/**`) 밖 / 물음: **Q2** |
| 69 | ast+ | 후보: 프로덕션 코드의 `assert` · `isinstance` 가드 뒤 `raise TypeError/ValueError` / 물음: **Q2** |
| 72 | **human** | **Q0** — 재료가 «커밋 순서»라 한 시점의 파일트리에 참·거짓이 없다 |
| 73 | ast | `application/*/` 에 옛 층 이름 폴더가 1건 이상인데 `check-*.py` 의 층 이름 상수에 옛 이름이 없으면 위반 |
| 74 | ast | 각 `check-*.py` 에서 채택 신호 분기가 참인 경로의 «대상 목록이 빈» 갈래가 `sys.exit(2)` 로 끝나지 않으면 위반 |
| 75 | ast | 진입 함수 statement 리스트에서 «가드 호출» 인덱스 > «touched 필터 호출» 인덱스면 위반 |
| 76 | ast | 쌍조건 — 옛 층 폴더 수 = 0 ⟺ 검사기의 옛 이름 리터럴 수 = 0. 어긋나면 위반 |
| 77 | ast | ⑴`application/*/driven_layer/port/` 가 1건이라도 있으면 위반 ⑵검사기 이중 수용 목록에 `port` 항목이 있으면 위반 |
| 78 | ast | 각 `check-*.py` 의 **채택 신호 소스 개수**(경로 glob · 트리 데이터 존재 · 설정·마커 · import 그래프) < 2 이면 위반 ※ **실측 위반** — `_is_adopted` 가 신호 1개 |
| 82 | ast+ | 후보: BC 폴더 이름 토큰이 그 BC 의 #628 집합에 0회 / 확정: 이름이 기술 이름 집합(#19)에 들면 / 물음: **Q1** |
| 85 | ast | `dependency_wiring.py` 최상위에 `Import`/`ImportFrom`·`def build_*` 밖 노드가 있으면 위반 + `build_X` 마다 `<X>_use_case.py` 없으면 위반 |
| 86 | ast+ | 후보: `dependency_wiring.py` 의 `If`/`Match`/`Compare`/`BoolOp`/산술 `BinOp` / 물음: **Q2**(업무를 가르나 어댑터를 꽂나) |
| 89 | ast | `application/<bc>/` 밖의 모든 파일에서 `application.<bc>.` import 의 둘째 마디가 `driving_layer`·`published_event` 밖이면 위반 |
| 91 | path | `glob('application/*/driving_layer/*/')` 이름이 {api, open_host_service, cron_job, event_subscription} 밖이면 위반 (**#90 의 닫힌 목록 그대로**) |
| 103 | ast+ | 후보: `driving_layer/**` 에서 import 한 값 객체의 사용 중 생성자 호출·`str()`·f-string 밖의 것 / 물음: 「이것이 «되돌려 굽기»인가 업무 사용인가」 |
| 15 16 23 24 25 26 27 56 100 | human | **면제라 대상 밖** |

---

# 묶음 2 — `#111` ~ `#294`

| # | 바꿈 | 술어 |
|---|---|---|
| 111 | ast | `api_router.py` 모듈 AST 에 ①자기 BC 컨트롤러 import ②`def register_<bc>_api(api)` 하나 ③그 본문의 `api.register_controllers(...)`·리터럴 — 이 셋 밖 노드가 있으면 위반 |
| 124 | ast | `@api_controller` 클래스에서 (public 메서드 수) ≠ (라우트 데코레이터 수)이면 위반 |
| 125 | ast+ | 후보: 컨트롤러 메서드 중 ①유스케이스 호출 0 또는 2회↑ ②`try/except` 뺀 제어흐름 ③`_command`/`schema_out` 생성이 아닌 호출 / 물음: 「이 문장이 «변환»인가 «판정»인가」 |
| 132 | ast | 모든 라우트 메서드에 ①라우트 데코레이터 ②인증 인자 ③상태 코드가 «그 파일 안에» 있어야 한다 |
| 140 | ast+ | 후보: `schema_in` 필드를 `if` 로 검사 후 `raise` 하는 자리 + 제약 선언(`Field(...)`·`@field_validator`)이 0인 스키마 / 물음: **Q2** |
| 151 | ast+ | 확정: 창구 폴더 이름 토큰에 기술 이름·다른 BC 이름 / 후보: 이름이 `domain_layer/<aggregate>/` 와 «같은» 것 / 물음: **Q1** |
| 153 | ast+ | 확정: `except <도메인 예외> as e:` 안에서 `e.<attr>` 접근이 있으면 위반 / 후보: 공개 함수 중 유스케이스 호출 0/2회↑ 또는 `except` 밖 제어흐름 / 물음: 「이 문장이 «계약↔응용 DTO 변환»인가」 |
| 156 | ast | `contract/request/*.py` 클래스 중 `<service>_service.py` 공개 함수 «파라미터» 애너테이션에 0회면 위반, 반환에만 나오면 자리 오배치 |
| 159 | ast | 거울 — `contract/response/*.py` 클래스가 «반환» 애너테이션에 0회면 위반 |
| 171 | ast+ | 후보: `contract/exception/` 클래스 중 ①기저를 뺀 이름이 접미사뿐 ②이름 토큰 ∩ #628 = ∅ / 물음: 「부르는 쪽이 이름만 보고 분기할 수 있나」 |
| 178 | ast | **독립 위반 주체 0** — #179 ∧ #509 ∧ #490 의 합. 검사기를 새로 만들지 않는다(D30) |
| 179 | ast | task 함수 본문 = `build_<use_case>()` 1회 + 유스케이스 1회 호출 + (선택)command 생성. 그 밖 문장이 있으면 위반. 파일당 task 하나 |
| 181 | ast+ | 확정: `cron_job/**` 에 「이미 했나」 판정(조회 후 조기 반환·`get_or_create`·중복 키·락) / 후보: **바깥이 부르는 입구 전부**(`cron_job/`·`webhook/**/*_controller.py`·`event_subscription/`) → 도달 유스케이스 중 리포지토리 읽기 0 + `save()` 만 있는 것 / 물음: 「두 번 와도 결과가 같나」 ← **멱등 물음의 소유자**(08-11 · C8 에 #513 에서 이관) |
| 191 | ast+ | 자동 통과: 첫 토큰이 애그리거트 루트 공개 메서드 이름과 같은 것 / 후보: 이름 전체가 애그리거트 이름이거나 `_list`·`_info`·`_detail`·`_status` 로 끝나는 것 / 물음: **Q1** |
| 194 | ast+ | 후보: `<use_case>_use_case.py` 의 `If`/`Match`/`Assert` 중 피연산자가 도메인 타입 속성 접근·값 객체 비교인 것 (제외: `Is None` 존재 확인 · 포트 실패 필드 확인) / 물음: **Q2** |
| 195 | ast | `repository.save/remove` 인자가 «같은 함수 안에서 루트 메서드 호출을 받은» 객체가 아니면 위반. `unit_of_work` 를 받았는데 루트 메서드 호출 0이어도 위반. 면제 셋(조회 전용·순수 위임·외부 조회)이 전부 기계로 보인다 |
| 196 | ast | `application_layer/**` 에 ①`port/` 밖 `ABC`/`Protocol` 상속 ②이름 `*Presenter`·`*InputBoundary`·`*OutputBoundary` ③진입 함수 반환이 `None` 인데 결과를 다른 객체에 넘김 |
| 197 | ast | 파라미터 애너테이션에 `*UnitOfWork` 가 있는데 본문에 `with <uow>:`·`save`·`remove`·`after_commit` 이 0이면 위반 |
| 207 | ast | `<use_case>_command.py` 필드 타입이 ①애그리거트 루트 ②`entity/` 클래스 ③ORM 모델이면 위반. 값 객체는 통과 |
| 210 | ast | `schema_out` 생성 인자가 참조하는 이름이 그 메서드의 `<use_case>_result`·요청 스키마 밖에서 오면 위반 |
| 213 | path | `*_query.py`(클래스 접미사 `…DomainBypassQuery`)가 `port/domain_bypass_query/<capability>/` 밖에 있으면 위반 |
| 227 | ast+ | 확정: 필드 타입이 `domain_layer/**` 면 위반(#228) / 후보: 필드가 하나뿐이거나 전부 표준 타입인 `<data>_*` 클래스 / 물음: 「이 자료를 원시값 인자로 «펴서» 넘길 수 있나」 |
| 228 | ast | ①import 에 `domain_layer` ②필드 애너테이션이 가리키는 심볼의 «정의 파일»이 `domain_layer/**` ③`<use_case>_{command,query,result}` 참조 — 하나라도 있으면 위반. **★ 토큰 검사를 쓰지 않는다**(`child_id` 오탐) |
| 231 | ast | `<A>_repository.py` 메서드 중 파라미터·반환에 그 애그리거트가 0회이고 반환형이 `bool`/`int` 도 아니면 위반 |
| 233 | ast+ | 확정: 폴더 이름 토큰 ∩ ({기술 이름}∪{BC 이름}∪{모델 표 이름}) ≠ ∅ / 후보: 이름이 명사 하나뿐 / 물음: **Q1** |
| 241 | ast | `<capability>_port.py` 클래스가 `__enter__`/`__exit__`/`commit`/`rollback`/`after_commit` 을 가지면 위반. 거꾸로 `*_unit_of_work.py` 가 셋(#245) 밖 메서드를 가지면 위반 |
| 254 | **human** | **Q4** — 기계는 «너무 갈린 쪽»(#546)만 보고 «너무 묶인 쪽»에 신호가 0이다 |
| 257 | ast+ | 확정: 응용·입구에서 리포지토리 객체에 «속성 접근 후 메서드 호출»(`order.line.change(...)`) / 후보: 루트 공개 메서드 중 자기 속성에 대입하면서 마지막 문장이 검증 호출/`raise` 조건이 아닌 것 / 물음: **Q4** |
| 259 | ast+ | 확정: `entity/` 클래스에 식별자 필드 0(#260) / 후보: ①`value_object/` 인데 `id`·`*_id` 를 가진 것 ②`entity/` 인데 `__eq__` 를 «전 필드»로 정의 / 물음: **Q4** |
| 268 | ast+ | 후보: 값 객체 클래스 중 `__post_init__`/`__init__` 에 `raise` 가 0인 것 / 물음: **Q2**(이 타입 조합만으로 잘못된 값이 «불가능»한가) |
| 269 | ast | `domain_layer/<A>/event/<E>.py` 클래스가 같은 BC 안에서 한 번도 참조되지 않으면 위반 |
| 271 | ast+ | 확정: 클래스 이름 첫 토큰이 애그리거트 루트 공개 메서드 이름과 같은 것(`ReduceInventory`↔`Inventory.reduce()`) / 후보: 마지막 토큰이 `-ed`/`-en` 도 아니고 불규칙 과거분사 목록에도 없는 것 / 물음: **Q1** |
| 280 | ast | 핸들러의 이벤트 파라미터가 `Call.args` 에 «통째»(`Name`)로 들어가면 위반. `Attribute(Name(e),'sku')` 처럼 필드만 넘기면 통과. `apply`/`handle`/`on_*` 이름의 애그리거트 메서드 호출도 위반 |
| 285 | ast+ | 후보: `<capability>_query.py` 메서드 중 반환이 `bool`/`int` 이고 그 구현이 애그리거트 리포지토리와 «같은 ORM 모델»을 질의 / 물음: 「이 수가 «애그리거트 컬렉션»을 세거나 합친 것인가」 |
| 292 | ast | `application/<bc>/**` 에서 `Exception` 하위 `ClassDef` 의 파일 경로가 셋(+`domain_bypass_query/**/exception.py`) 밖이면 위반 |
| 294 | ast | `adapter/persistence/**` 와 `port/unit_of_work/**` 에 `Exception` 상속 `ClassDef` 가 있으면 위반(넷째 자리) |
| 127 137 145 248 | human | **면제라 대상 밖** |

---

# 묶음 3 — `#299` ~ `#494`

| # | 바꿈 | 술어 |
|---|---|---|
| 299 | path | `domain_layer/*/` 이름이 {shared_value_object, domain_service} 밖이면 `<X>.py`(#256)와 `<X>_repository.py`(#282)가 있어야 한다 |
| 301 | ast+ | 후보: `domain_service/**` 공개 함수 중 «애그리거트 루트 타입 인자가 정확히 하나»인 것 / 물음: 「이 규칙이 «없을 때»를 판정하나」 (①루트 인자 0, ③루트 인자 ≥2 는 시그니처로 «센다») |
| 304 | ast | `domain_service/**` 에 `*Repository`·`*Port` 가 import·인자 애너테이션·호출로 나오면 위반 |
| 307 | ast | `domain_service/**` 공개 함수의 모든 인자 애너테이션이 (제네릭을 벗긴 뒤) `domain_layer/**` 정의 타입으로 해소돼야 한다 — **양성 허용목록**이라 닫힌 목록 문제가 없다 |
| 311 | ast+ | 후보: `domain_service/*.py` 중 파일명 토큰 ∩ 애그리거트 폴더 이름 = 0 (+`_service`·`_domain_service` 접미사) / 물음: 「겹쳐서 «행위»로 지은 것인가」 |
| 316 | **human** | **Q2** — 전건(「재료를 한 번에 못 모으는 경우」)이 코드에 흔적을 안 남긴다 |
| 319 | ast | 4갈래를 import 로 계산해 폴더와 대조 — `ORM`(#462) → persistence · `CONTRACT` → acl · `SOCKET`(#367) → external_system · 나머지 → capability |
| 343 | ast+ | 후보: `panel.py` 의 django 훅 본문에 `.objects`·`transaction`·루프·모델 필드 조건 / 물음: 「이 문장이 운영 «기능»인가 장고 «배선»인가」 |
| 347 | ast+ | 후보: `admin/<entity>/feature/*.py` 중 애그리거트를 import 하고 리포지토리 쓰기를 부르는 것 / 물음: 「이 조작을 사용자 API 도 하나」 |
| 355 | ast+ | 확정: `<A>_repository.py` 반환이 {A, Sequence[A], 값객체, bool·int·None} 밖 / 후보: bool·int 로 남은 것 / 물음: 「주어가 애그리거트인가 화면인가」 |
| 365 | path | `anticorruption_layer/*/` 이름이 `application/*/` BC 폴더 이름 집합의 원소가 아니면 위반 |
| 366 | ast | **#367 의 술어 그대로** — 「이 라이브러리가 소켓을 여나」 |
| 368 | ast+ | 후보: `external_system/**` 의 `time.sleep`·재시도 루프·`tenacity`·`backoff`·`*Breaker`·`*Limiter` 정의 / 물음: 「이게 «기계»인가 «값»인가」 |
| 372 | ast | 두 방향 — framework: `framework/*/*_port.py` 토큰 ∩ **전 BC 합집합** ≠ ∅ 이면 위반 / BC: `port/*/*_port.py` 토큰 ∩ **자기 BC 집합** = ∅ 이면 위반(framework 로 올라가야) |
| 389 | ast | `test/integration/**` 이 django_db 마커/`db`/`TestCase` 중 하나 + 리포지토리 구현 또는 HTTP 클라이언트 사용. 아니면 위반 (**#387 의 뒤집힌 술어**) |
| 390 | ast | 확정: `test/e2e/**` 중 입구(TestClient·API·`<job>_cron_job`)를 안 거치는 것 ※ 「수가 적어야」는 임계값이 없어 ㉰ 가 문면에서 걷었다 |
| 392 | ast | `test/factories/**` 의 모든 최상위 정의가 `factory.Factory`/`DjangoModelFactory` 상속 클래스여야 한다 |
| 393 | path | `framework/` 가 저장소 루트의 자식이고 `application/<bc>/**` 아래에 `framework/` 가 없다 ※ 「BC 가 하나도 없어도 존재하나」는 C2 가 #448 로 옮긴 옛 축 — ㉰ 가 걷었다 |
| 415 | ast | 모듈이 `<technology>` 라이브러리를 import 하고 공개 정의마다 그 라이브러리 이름을 하나 이상 참조 (**#396③ 과 같은 술어**) |
| 416 | ast | `framework/**`→`application/**` import 0(#46) + BC 폴더 이름 문자열 0 + #628 합집합 교집합 0 |
| 425 | ast+ | 후보: `framework/test/**` 에 합집합 토큰·BC 이름이 나오는 것 / 물음: 「이 재료의 뜻을 밖(HTTP·pytest·시간)이 정하나」 |
| 432 | ast | `<project>/**` 에서 BC 이름이 나오는 자리는 `urls.py` 의 `register_<bc>_api` 호출과 INSTALLED_APPS 등록 문자열뿐 |
| 433 | ast | `<project>/**` 에 도메인 예외를 원소로 갖는 컬렉션 리터럴 · BC 경로 리터럴(등록 문자열 제외)이 있으면 위반 |
| 448 | ast+ | 후보: `framework/**` 중 합집합 토큰이 이름·시그니처에 나오는 파일 / 물음: 「이 낱말의 뜻을 저장소 밖이 정하나」 |
| 449 | **human** | **Q0** — 주어가 «판정 절차»다. 코드 쪽 귀결은 #372·#448 이 이미 진다 |
| 451 | ast+ | 후보: `contract/exception/` 중 #454 술어를 통과 못 하는 클래스 / 물음: 「이 창구가 «혼자서» 답을 만들 수 있나」 |
| 452 | **human** | **Q0** — 판정 «축»만 규정한 행. 실물 위반은 #451 이 진다 |
| 453 | ast | `contract/exception/` 클래스의 `raise` 가 (a)`if` 분기 (b)`domain_layer/**/exception/` 타입을 잡은 `except` 에서 나오면 위반 |
| 454 | ast | 긍정형 — 공개 예외의 `raise` 는 `port/<capability>/exception.py` 나 인프라 예외를 잡은 `except` 안에서만 |
| 456 | ast | #454 술어 + `contract/exception/` 에 요청 필드 검증에서 나온 예외 0 |
| 463 | ast | 3단이 전부 기계 — ①남의 BC contract import·#367 소켓 ②서드파티 import(#396③) ③#628 합집합 교집합 |
| 470 | ast | `framework/`(미이관 `common/` 포함) 공개 함수·메서드 시그니처에 매개변수 이름 `kind`·`mode`·`bc`·`bounded_context`·`is_*` 가 있으면 위반 — D38 축자 「절차가 아니라 «판정이 틀렸다»는 사후 신호」. 참고 #606⑵(인자 수 증가·기본값 인자 등장은 리뷰 축) |
| 471 | ast | 모듈이 `*Port` ABC(#551·#403) 상속 클래스를 정의하면 `<capability>/`, 아니면 `<technology>/`. 어긋나면 위반 |
| 475 | ast+ | 후보: 유스케이스 안에서 `*DomainBypassQuery` 결과에 바인딩된 이름이 비교·불리언 피연산자로 흐르는 자리(지역 taint) / 물음: **Q2** |
| 480 | ast | 그 칸의 파일·클래스 이름에 `dto`·`Dto`·`DTO` 가 있거나 `_command`·`_result` 로 끝나면 위반 |
| 484 | ast | `contract/request/` 는 `Request`, `contract/response/` 는 `Response` 로 끝나고 `Result` 면 위반 |
| 485 | ast+ | 확정: 이름이 `notify`·`handle`·`execute`·`process`·`run`·`do` 이거나 `_command`·`_query` 접미사를 단 포트 메서드 / 후보: deny-list 밖인데 첫 `_`-토큰이 동사가 아니고 묻는 꼴(`has_`·`is_`·`can_`·`current_`)도 아닌 메서드 / 물음: 「이 이름이 무엇을 시키는지 말하나」 |
| 492 | ast+ | 후보: 정본 트리 칸 설명에 조건 표현(있을 수도·필요하면·커지면·권장·해도 된다)이 든 행 / 물음: 「«있어야 하나»인가 «어떻게 쓰나»인가」 (주어가 코드가 아니라 정본 문서 — #491 이 같은 주어로 이미 `path`) |
| 494 | **human** | **Q0** — 주어가 «규칙을 쓰는 사람». 코드 쪽 강제는 #493·#495·#496 |
| 346 | human | **면제라 대상 밖** |

---

# 묶음 4 — `#511` ~ `#636`

| # | 바꿈 | 술어 |
|---|---|---|
| 511 | ast+ | 후보 ㉠서명검증 데코레이터(#517)가 붙은 라우트 ㉡`<area>` 토큰이 벤더 사전에 있는 것 ㉢`webhook/<provider>/` 인데 provider 가 #628 업무 어휘 / 물음: 「이 스키마를 우리가 고칠 수 있나」 |
| 512 | ast+ | 후보: `<provider>` 토큰이 벤더 사전에 **없고** #628 어휘나 역할 접미(`_gateway|_provider|_client|_service|_api|_system`)와 겹치는 것 / 물음: 「보내는 쪽이 자기를 이렇게 부르나」 |
| 512 | ast+ | 확정: `webhook/<provider>/` 이름이 능력·역할 낱말 deny-list{gateway,provider,payment,billing,notification,auth,external}에 들면 위반 / 후보: #511 ㉡ 의 벤더 사전에 없는 이름 / 물음: 「보내는 쪽 문서가 자기를 이 이름으로 부르나」 |
| 516 | ast | `webhook/**` 공개 함수에 HTTP 라우트 데코레이터가 없거나 비-HTTP 소켓 라이브러리(`pika`·`kombu`·`confluent_kafka`·`grpcio`)를 import 하면 위반 |
| 520 | ast+ | 후보: 발행 호출이 ㉠`try:` 안 ㉡반환값을 바인딩·분기 ㉢발행 뒤 같은 함수에서 ACL·OHS 호출 / 물음: 「이 사실이 안 나가면 내가 할 일이 있나」 |
| 526 | **human** | **Q3** |
| 529 | ast+ | 후보: `external_broker_port.py` 를 쓰는 발행 자리 × 그 사실의 `<event>_subscription.py` 가 이 저장소 안에 있는 짝 / 물음: 「듣는 쪽이 따로 배포되나」 |
| 530 | **human** | **Q3** — 기계 몫은 #529 가 갖는다 |
| 532 | ast+ | 후보: external 구독 경로 유스케이스 + #533 봉투 인자 유무 / 물음: #181 과 같은 물음. **「도달 보장」은 술어가 안 선다** — 미들웨어 «설정»에 있어 저장소 밖이다(#603⑷ 가 선언 유무만 잰다) |
| 547 | ast+ | 후보 ⑴#546 의 잔여(대상은 **애그리거트 리포지토리** 타입 · 쓰기 메서드는 #597 이 `save`/`remove` 로 고정) ⑵`<A>_repository.py` 를 쓰는 `<use_case>/` 들의 부모 `<area>/` 집합 크기 ≥2 ⑶루트의 무제한 컬렉션 필드·`entity/` 수 / 물음: 「이 둘이 «동시에» 일어나면 업무가 정말 막아야 하나」 |
| 549 | ast | `adapter/persistence/repository/**` 에서 캐시 API 사용 0 · `select_for_update()` 결과에 캐시 0 · UoW 블록 안 캐시 읽기 0 |
| 553 | ast+ | 후보 ㉠#628 어휘가 조건식에 ㉡반환형 `bool` ㉢도메인 필드에 걸린 비교·산술 ㉣도메인 인스턴스 «메서드» 호출(재구성 제외) / 물음: **Q2** ← **Q2 의 소유자** |
| 556 | ast | ㉠도메인·응용에 재시도 기계(`tenacity`·`backoff`·`retrying`·`sleep` 루프) 0 ㉡벤더 오류 코드 비교가 `adapter/**` 밖 0(=#557) ㉢유스케이스 재호출은 `driving_layer/**` 에서만 |
| 558 | ast | #614 의 링 라벨로 파일마다 링을 정하고 그 링 규칙(#4·#5·#560·#615)을 건다 · 검사기 경로 필터에 `framework/` 통째 면제가 있으면 위반 |
| 559 | ast | **새 술어 0** — #560 ∧ #561 ∧ #562 가 곧 「이 파일이 순수한가」 |
| 563 | **human** | **Q3** |
| 564 | ast+ | 후보 ㉠트리 밖 `saga/`·`process_manager/`(#490) ㉡값 토큰이 `<use_case>/` 폴더 이름과 겹치는 Enum 필드를 가진 ORM 모델 / 물음: 「업무가 이 단계 이름을 입으로 부르나」 |
| 565 | ast+ | 후보: `domain_layer/**` 의 Enum 중 값 토큰이 `<use_case>/`·`<service>/` 이름과 겹치는 것 / 물음: **Q1** ← **단계 이름 물음의 소유자** |
| 567 | ast | 저장소 어디에도 `dto` 토큰이 폴더·파일·클래스·별칭 이름에 없다 |
| 580 | ast | **#579 와 같은 술어** — `test/`·`framework/test/` 밖에서 `fake/` import 하면 위반 + `dependency_wiring.py` 가 설정·플래그 분기로 페이크를 꽂으면 위반 |
| 584 594 595 512 | ast+ | **공통 사전 술어** — 폴더 이름 토큰 T ∩ (의존성 배포 이름 ∪ `framework/<technology>/`·`external_system/<system>/` 이름 ∪ 계기 낱말{nightly,daily,hourly,weekly,realtime,on_*} ∪ 전달 수단 접미{_client,_sdk,_api,_driver,_gateway,_queue}) ≠ ∅ → 후보 / 물음: 「그것이 바뀌어도 이 이름이 그대로인가」 ← **#595 가 소유자** |
| 584 | ast+ | 확정·후보: #595 의 술어를 `framework/<capability>/` 에 적용 / 물음: =#595 |
| 589 | ast+ | 장고 템플릿 파서로 `{% if %}`/`{% elif %}` 조건 노드를 뽑아 ㉠비교·산술 연산자 ㉡조건 토큰 ∩ #628 ≠ ∅ 를 후보 / 물음: **Q2** |
| 590 | ast+ | ㉠`presenter` 이름의 칸·파일 0 ㉡`<data>_out.py` 의 str 필드 중 문구계 이름(`message`·`body`·`subject`·`title`·`text`)을 후보 / 물음: 「이 값이 사람이 읽을 문구인가」 ← **소유자** |
| 591 | ast | **주어가 «검사기»다** — 검사기 소스에 ㉠`.git` 유무 가드(#613) ㉡변경 파일 필터 ㉢`legacy|brownfield|preserve|existing` 조기 반환 ㉣baseline·allowlist 파일이 있으면 위반 |
| 592 | **human** | **Q0** — 주어가 «대화 행위»(AskUserQuestion)라 검사할 대상이 없다 |
| 593 | ast | 허용: `ImportFrom(django.db → migrations, models)` · `ClassDef Migration` 하나 · 대입은 initial·dependencies·operations·replaces 넷뿐 · operations 원소는 전부 `migrations.*` 호출 / 위반: 그 밖의 `FunctionDef`·`RunPython`·`RunSQL`·`if`/`for`·도메인 import·데코레이터·최상단 상수. 보조: `makemigrations --check --dry-run` |
| 594 | ast+ | 확정·후보: #595 의 술어를 `port/<capability>/` 에 적용 / 물음: =#595 |
| 595 | ast+ | 확정: 이름의 `_`-토큰이 기술 이름 집합(#19)에 정확 일치(`smtp`·`redis`·`celery`) / 후보: 수단·계기 낱말 집합{client,cache,sync,cron,queue,http,rest}에 드는 토큰이 있는 이름 / 물음: 「그것(공급자·계기·수단)이 바뀌어도 이 이름이 그대로인가」 ← 물음의 소유자(#584·#594 가 참조) |
| 601 | ast | `E = {(subscription, use_case)}`(#509 로 간선 결정적) · `publishes(u) ⟺ uow.after_commit(...) 인자에 브로커 publish`(#539③) · `∃(s,u)∈E. publishes(u)` 면 위반(두 겹) |
| 603 | ast | 일곱 중 여섯이 «있나» 검사 — ⑴outbox 모델 + 같은 트랜잭션 쓰기 ⑶#533 ⑷데드레터 선언 ⑸순서 보장 선언 ⑹직렬화기 ⑺버전 필드 / 사람은 ⑵ 소비자 멱등(=#181) 하나 |
| 607 | ast+ | 후보 ㉠반환형 `bool`(#606⑴ 을 framework 전 파일로 확대) ㉡조건식에 «정책 리터럴»(숫자 임계값·상태 문자열) ㉢갈래마다 서로 다른 반환 리터럴 / 물음: **Q2**(#553 과 술어 공유) |
| 617 | ast | `framework/<capability>/<data>_out.py` 의 {식별자 ∪ 문자열 리터럴 키} 토큰 ∩ #628 합집합 ≠ ∅ 이면 위반 ※ **#628 이 재료 소비자로 이미 지명했고 형제 #518·#562·#587 이 전부 `ast` 였다** |
| 618 | ast+ | ㉠`_()`·`gettext`·`format_lazy`·`babel` 호출 0(=#588) ㉡필드 이름 ∩ 채널 설정 낱말(`host`·`port`·`url`·`endpoint`·`api_key`·`token`·`timeout`·`region`·`bucket`·`template_id`) ≠ ∅ → 위반 / 남는 후보는 #590 의 물음 |
| 619 | ast+ | 후보: 자료 클래스 중 필드가 «하나»이거나 모든 필드가 표준 타입이고 계약 시그니처에서 한 번만 쓰이는 것 / 물음: 「이것이 원시값 하나로 되나」 (뒷문장 「#228 자동 성립」은 `framework/`→`domain_layer/` import 0 으로 이미 기계 확정) |
| 629 | ast+ | 확정: 없음 / **후보: 집합 차** — `webhook/**`·`event_subscription/**` 이 부르는 유스케이스가 «쓰는» 애그리거트 집합 **A**, `cron_job/**` 이 부르는 유스케이스가 «쓰는» 집합 **B** → **A − B ≠ ∅ 이면 후보** (그 애그리거트는 바깥이 안 부르면 영영 안 채워진다) / 물음: 「이 입구가 «안 와도» 업무가 돌아가나」 |
| 644 | ast+ | 후보 ⑴행위 칸 실현(파일 또는 승격 본체·부품 — `__init__.py` 제외)의 물리 행수(빈 줄 제외) >200 — `check-layer-skeleton` ⓓ 채널이 행수·top-level 요약 페이로드로 방출(무조건 방출·exit 불산입 — diff 한정은 감사자 몫) ⑵확정 위반은 형태 규칙 #638~#643 소유 / 물음: 「역할 밖 응집 단위가 있는가 — ①이동/②동명 폴더 승격/③유지(houserules §1 캐스케이드)」 |
| 626 | **human** | **Q3** — 다만 **처방 이행**(받는 쪽에 `cron_job/` + `anticorruption_layer/<owner>/` 경로가 있나)은 `path` 로 «잰다» |
| 627 | ast | 구독 경로 유스케이스 안에서 사실 payload 의 «식별자 아닌»(`*_id` 아닌) 필드가 애그리거트 생성·변경 인자 → `save()` 로 흐르면 위반. `+=`·`Sum`·`count` 로 자기 저장 필드를 집계해도 위반 |
| 630 | ast | `models/**` 의 `Model` 하위 ClassDef 중 `Meta` 에 `abstract`/`proxy`/`managed=False` 가 없는 «신규»(diff 기준 추가) 클래스에 ⑴`db_table` 대입이 없거나 ⑵값 ≠ `<app_label>_` + snake(클래스명 − `Model`) 이면 위반. 기존 클래스는 테이블명 보존이라 면제 |
| 631 | ast | `models/**` 의 관계 필드(`ForeignKey`·`OneToOneField`·`ManyToManyField`) 첫 인자가 가리키는 모델이 «다른 BC 의» `models/**` 에 살면 위반 — 문자열 `"app.Model"` 은 app_label 로, 클래스 참조는 import 경로로 푼다(장고 contrib 등 BC 밖 모델은 대상 아님) |
| 632 | ast | `models/**` 의 `django.db.models.Model` 하위(가접 포함) ClassDef 이름이 `Model` 로 끝나지 않으면 위반 |
| 633 | ast | `<service>_service.py` 공개 함수의 파라미터가 2개 이상이면 위반 · 1개면 애너테이션 타입이 같은 서비스 `contract/request/**` 의 클래스가 아니면 위반 · 0개는 함수명이 `_query` 로 끝날 때만 |
| 634 | ast | `<service>_service.py` 모듈 수준 ClassDef 중 이름이 `_` 로 시작하지 않는 것이 있으면 위반 |
| 635 | ast | `<use_case>_use_case.py` 의 공개 ClassDef ≠ 1 이거나 `execute` 메서드가 없거나, `execute` 의 (self 외) 파라미터 ≠ 1 이거나 그 애너테이션이 같은 폴더 `_command`/`_query` 클래스가 아니거나, 반환 애너테이션이 같은 폴더 `_result` 클래스(또는 `Iterator[…]` 감쌈)가 아니면 위반 |
| 636 | ast | `bc_error_schema.py` 의 `<Bc>ErrorCode` ClassDef 기반 목록에 `StrEnum` 이 없으면 위반 |
| 522 625 | human | **면제라 대상 밖** |

---

## 실측으로 이미 깨져 있는 것 (8번 이관 때 볼 자리)

```
dddjango/scripts/check-layer-skeleton.py:80
LAYER_DIRS = ("domain_layer", "application_layer", "infra_layer", "presentation_layer")
                                                    ↑ 옛 이름       ↑ 옛 이름
_is_adopted = any((bc_dir/layer).is_dir() for layer in LAYER_DIRS)   ← 채택 신호가 «하나»
```

- **`#78` 위반** — 채택 신호 소스가 1개(둘 이상이어야 한다)
- **`#73`·`#76` 의 대상이 실재** — 옛 층 이름이 상수에 남아 있다
- **`#74` 위반** — `#74` 를 구현한 검사기가 0개(명세 `#612` 가 이미 적었다)

## 남은 정리 (다음 회차)

- **Q0 다섯(`#72`·`#449`·`#452`·`#494`·`#592`)의 «어겼을 때»를 `blocker` → `검사기` 로** — 위반할 파일을 지목할 수 없다
- **`#34` 의 예시 `dto_*`** 는 죽은 문면(D40·D55 가 `<use_case>_command.py` 로 바꿨다)
