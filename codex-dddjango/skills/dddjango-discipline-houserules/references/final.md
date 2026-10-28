# dddjango 표준 파일트리
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

> **단일 출처.** 이 문서가 dddjango 플러그인이 만드는 코드의 파일트리 «값»의 정본이다 — SKILL.md·에이전트 문서는 여기를 가리키기만 하고 값을 복제하지 않는다. 트리 블록(§1)과 기계 사본(`scripts/standard_tree.py`)의 동기는 메인테이너 도구 `tree_mirror_check` 가 지킨다. 규칙 문면 끝의 `#N` 은 설계 명세(트리 개정 명세 538규칙)의 규칙 번호다.
>
> **편입 상태(2026-08-11).** 이 판은 새 표준 트리(140행)의 첫 배포판이다 — §0 제1원칙 · §1 트리 · §2 골격 규칙 · §4 이관이 정본이고, 층·칸별 상세 규칙과 명명 전수는 매핑표(`rule-owner-map`) 순서로 이 문서에 편입된다. 옛 판(4계층 `infra_layer`/`presentation_layer` 세대)의 상세 절은 이 판에서 걷혔다 — 옛 이름은 §4 이관 절이 다룬다.

## 무엇이고 왜
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

dddjango 는 **DDD · 클린 아키텍처 · 헥사고날** 셋을 조합해 Django 프로젝트를 조직한다. 그 조합의 물리적 표현이 이 표준 파일트리다 — 바운디드 컨텍스트(BC)마다 같은 골격, 입구(driving)와 출구(driven)의 물리 분리, 계약(`port`)과 구현(`adapter`)의 분리, 프레임워크 소유물(`framework/`)의 격리.

트리는 「무엇이 **있어야** 하나」를 정하고, 스킬은 「그것을 **어떻게 쓰나**」를 정한다 — 트리에 조건을 적어 두 채널로 만들지 않는다(#492).

## §0 제1원칙 — 골격은 내용과 무관하다
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

**모든 검사보다 먼저 서는 원칙이다**(#487 — 골격이 어긋나면 나머지 검사를 돌릴 이유가 없다).

- **#486** — 어느 BC 를 열어도 이 트리의 골격이 «그대로» 있다 — 내용이 있든 없든 상관없다. 파일트리를 지키지 않는 구현·설계는 «반환»이다.
- **#488** — 고정 이름의 칸은 «부모가 있으면» 반드시 있다 — 폴더는 비어도 `__init__.py` 로, 파일도 비면 «빈 파일»로 만든다. 칸의 승격 실현(#490 교체형)이 이미 있으면 그 실현이 이 충족이다 — 동명 빈 파일을 병설하지 않는다. 승격 허용 파일 칸의 빈 실현은 «빈 파일»이다 — 승격형은 내용이 생긴 뒤의 대체 실현이며, 예비 폴더형을 미리 파지 않는다. 빈 파일로 실현된 칸의 **내용 규칙**(진입점·포트 «하나» 등)은 내용이 생긴 뒤부터 선다 — Coordinator 가 빈 모듈을 error inventory 에서 제외하는 것(R-0319)과 같은 시점이며, 검사기는 내용 없는 골격 파일(0바이트·docstring/주석뿐)을 내용 규칙에서 건너뛴다. 빈 파일을 지워 red 를 푸는 것은 #488 위반이다.
- **#489** — `<…>` 가 붙은 자리표시자 칸만 그 개념이 실제로 생길 때 생긴다 — 그 외에 「이 BC 엔 없으니 뺀다」는 축소가 아니라 위반이다.
- **#490** — `application/<bounded_context>/**` 안에 트리에 없는 경로가 하나라도 있으면 위반이다(`utils/`·`common/`·`helpers/`). 폐쇄는 **칸**(폴더 + 트리가 이름을 준 파일)에만 걸리고, 트리가 리프로 닫은 폴더 «안»의 추가 모듈은 작성자 재량이다(#15). `framework/`·`<project>/` 는 이 원칙의 주어가 아니다. 단, §1 트리의 **승격 허용 표기**가 붙은 파일 칸은 두 실현을 갖는다 — `<이름>.py`(기본) ⇄ 동명 폴더 `<이름>/`(**동명 폴더 승격**). 유효한 승격 폴더는 트리에 있는 실현이지 «트리에 없는 경로»가 아니다(형태 요건은 아래). §1 트리의 **묶음 허용 표기**가 붙은 파일 칸(트리 64·66·68·71·73·75행)의 인스턴스 파일은 부모 바로 아래 **묶음** 한 계층으로 나눠 둘 수 있고, 유효한 묶음은 «트리에 없는 경로»가 아니다(요건은 아래 «의미 묶음» — #654~#656).
- **#491** — 칸의 유형은 셋뿐이고 «조건부»는 없다 — ① 고정 이름 ② `<>` 첫 등장 ③ `<>` 재등장(조상이 이미 연 낱말이라 값이 이미 채워져 있어 ①과 같다). «조건부 없음»의 주어는 칸의 **존재**(생성 조건)다 — 승격 허용 표기는 존재가 아니라 실현 형태(#490)의 값이다. 묶음 허용 표기도 칸의 존재가 아니라 실현 형태의 값이다.
- **#492** — 「그 파일이 있어야 하나」는 트리가 정하고 「그것을 어떻게 쓰나」는 스킬이 정한다. 묶음의 개수 조건(셋 · 둘)은 노드 조건이 아니다 — 의미 묶음(#654~#656 · D60)이 묶음 허용 여섯 칸에 한해 명시적으로 개정한 값이다.

골격의 실현 주체는 **coder** 다 — 승인 스코프의 BC 를 새로 만들거나 touched 하면(touched = G0 스코프의 그 BC — §4 와 같은 자 · 명세가 골격 실현을 지시한 데이터소스 BC 포함) 고정·재등장 칸을 빈 채로라도 실현한다. 위반은 `check-layer-skeleton` 이 잡는다. 칸의 승격 실현이 이미 있으면 그 실현이 곧 골격 실현이다 — 동명 빈 파일을 병설하지 않는다(#488).

동명 폴더 승격의 형태: 승격 폴더는 안에 **본체 `<이름>.py`** 와 **재수출 전용 `__init__.py`** 를 반드시 가진다 — 본체 없는 폴더는 위장이고, 형제 `<이름>.py` 와 `<이름>/` 의 공존도 위반이다(파일시스템은 공존을 허용하고 import 는 패키지가 이겨 조용한 위장 중복이 된다). 내부는 **1단 평평**이다 — 하위 폴더는 위반이며, 부품 군집이 폴더를 요구하면 그것은 트리 개정 신호이지 중첩 근거가 아니다. `__init__.py` 재수출은 `from .<모듈> import <이름> as <이름>`(redundant alias) 또는 `__all__` 선언으로 한다(mypy strict `--no-implicit-reexport` 가 인정하는 두 형태) — 본체 코드를 `__init__.py` 에 두지 않고, 폴더 내부 상호 참조는 `__init__` 경유 없이 모듈 직접 상대 import 로 한다. 바깥 import 표면(`...<칸>` 모듈 경로로 공개되는 이름 집합)은 승격·환원 어느 방향이든 불변이어야 한다 — 앞 `_` 이름은 표면 밖이다. `_` 정의를 다른 파일로 옮기면, 그 이름을 옛 모듈 경로로 가져오는 시험을 찾아 같은 창(단계)에서 정의를 가진 파일의 경로로 고친다 — 옛 모듈이 그 이름을 다시 import 해서 시험이 우연히 통과해도 같다. 승격은 `git mv` 로 이력을 보존한다.
승격 폴더는 «트리가 리프로 닫은 폴더»가 아니다 — 내부 재량은 **배열·명명 재량**이지 **파일 신설 재량이 아니다**. 부품 파일의 신설 근거는 감사 판정(동명 폴더 승격 발견)의 클러스터 열거 또는 후속 감사 신호뿐이고, #192(사설 조각은 쓰는 곳이 하나면 그 파일 안 `_` 함수 — ②′ 에서 두 부품 이상이 쓰는 정의는 종류대로 단계 · 틀 부품 · 잎이다)·#189(유스케이스 간 돌려쓰기 금지)가 부품 파일 각각에 그대로 적용되며, 정크드로어 이름(`utils.py`·`helpers.py` 류)은 위반이다. ②′ 승격의 부품 파일 이름은 업무 낱말이다 — 이름을 `_` 로 가른 낱말에 금지 낱말(`common` · `shared` · `base` · `core` · `util` · `utils` · `helper` · `helpers` · `misc` · `manager` · `handler` · `handlers` · `mixin` · `part` · `parts` · `branch` · `branches` · `step` · `steps` · `tools` · `frame`)이 하나라도 있으면 위반이다(`<업무>_utils.py` 같은 겹낱말 포함 · 틀 부품의 고정 이름 `<유스케이스 이름>_frame.py` 만 예외). 부품 클래스 이름은 `UseCase` 로 끝나지 않는다. 부품이 0개(본체+`__init__.py` 뿐)가 된 승격 폴더는 위반이다 — 틀 부품 · 잎만 남은 ②′ 폴더(갈래 · 단계 부품 0)도 같다(환원 신호 — 이번 작업 산출이면 발견 반영으로, 기존이면 G0 빚 경로로 환원한다). 저장(save)류 쓰기 호출은 본체에만 둔다 — 유스케이스 칸(트리 42행) 승격 폴더(② · ②′ 모두)에서는 틀 부품도 본체와 같은 자리여서, 저장 호출 · 이 BC 의 쓰기 경계 자원(저장소 `…Repository` · UoW `…UnitOfWork` 와 그것을 내는 팩토리) · 사실(도메인 이벤트) 발행 · 커밋 뒤 등록은 본체와 틀 부품(틀이 없는 ② 폴더는 본체)에만 둔다. 그 밖의 부품(갈래 · 단계 부품 · 잎 · ② 폴더의 형제 부품)은 그 자원을 매개변수 · 속성으로 받지도, 다른 객체의 속성 너머로 닿지도 않고(읽기 포함), 틀 부품의 이름 있는 메서드를 불러서만 읽고 쓴다(틀이 없는 ② 폴더면 본체가 읽고 쓰고 형제 부품에는 값만 넘긴다) — 한 실행 안의 여러 번 저장(스트림 도중 저장 포함)도 이 길이다. 다른 BC · 바깥 시스템 port 호출과 스트림 방출은 이 규범의 쓰기가 아니다. 틀 부품은 갈래를 모른다 — 콜백 · 컨텍스트를 받아 작업 단위 안에서 무엇이든 돌리게 하는 범용 틀 메서드는 위반이고, 틀 메서드가 작업 단위 안에서 `yield` 하는 생성기(읽기 생성기 포함)도 같은 위반이다(부르는 쪽이 작업 단위 안에서 무엇이든 돌리게 된다). 틀이 다시 읽은 애그리거트 하나에 루트 메서드를 적용하는 변경 함수(애그리거트만 받고, CAS 미스 때 다시 적용된다)는 그것이 아니다. 쓰기 경계가 갈래 흐름을 감싸면 둘 가운데 하나로 쓴다 — (i) 트랜잭션 구간을 본체에 두고 본체가 갈래 부품의 앞 · 뒤 조각을 부른다, (ii) 갈래를 모르는 틀 쓰기 도구(예: 애그리거트 여럿을 한 작업 단위에서 CAS 저장)를 쓰고 읽기 · 판정을 작업 단위 밖으로 옮긴다 — (ii) 는 그렇게 옮겨도 동작이 같을 때(시험이 확인)만이다. 틀 부품의 쓰기에도 유스케이스 쓰기 규범(#195 · #197)이 본체와 같이 걸린다.
**②′ 승격의 부품** — 부품은 유스케이스가 아니다: `execute` · `…UseCase` 이름 · 합성 루트 등록이 없고, 승격 폴더 밖의 제품 코드(컨트롤러 · 다른 유스케이스 · 합성 루트)는 부품 모듈을 import 하지 않는다(`__init__.py` 재수출은 본체의 공개 이름뿐이다). 부품은 네 종류다 — **갈래 부품**(본체 `match` 의 `case` 한 곳이 부르는 흐름) · **단계 부품**(본체와 부품 가운데 두 곳 이상이 부르는 흐름) · **틀 부품**(갈래 · 단계 부품이 함께 쓰는 실행 도구 — 쓰기 경계 자원 · 사실 발행 · 스트림 · 실패 접기 같은 것 — 폴더에 많아야 하나 · 이름은 `<유스케이스 이름>_frame.py`) · **잎**(두 곳 이상이 쓰는 무상태 정의 — 실행 기억 · 결과 타입 · 순수 함수 · 상수 — 흐름도 실행 도구도 아닌 것). 한 곳만 쓰는 흐름 · 정의는 부품이 아니라 그 곳 안 `_` 사설 정의다(#192). 업무 판정은 잎이 아니라 도메인이다(① · #194). 틀 부품과 잎은 갈래 · 단계 부품이 있을 때만 선다. 부품은 본체가 만든다 — 본체 `__init__` 이 생성자로 받은 의존으로 틀 → 단계 → 갈래 차례로 부품 클래스를 만들어 `self` 속성에 대입하고 필요한 것만 넘긴다(본체 생성자 시그니처와 합성 루트는 그대로다). 본체 `__init__` 이 형제 모듈 클래스를 만들어 `self` 속성에 두는 승격 폴더는 ②′ 폴더다(틀 파일 `<유스케이스 이름>_frame.py` 이 있는 폴더도 ②′ 다) — ② 로 두는 폴더의 형제는 `execute` 안에서 만들거나 함수로 부른다. 실행마다 바뀌는 상태는 잎이 정의한 실행 기억 객체 하나로 인자로 넘기고, 부품은 실행 사이 상태를 두지 않는다. **부품 클래스**(본체 `__init__` 이 만들어 `self` 속성에 대입하는 형제 모듈 클래스) · **틀 계약**(부품이나 본체가 부르는 틀 클래스 메서드) · **본체가 부르는 부품 메서드**는 공개 이름(앞 `_` 없음)이다 — 잎이 정의한 타입 · 상수 · 함수는 형제가 import 해도 `_` 이름이어도 된다. 폴더 밖에 대한 비공개는 재수출하지 않음과 바깥 import 금지가 지킨다. 각 부품에는 캐스케이드가 다시 걸린다 — 부품 안 ②′ 의 실현도 하위 폴더가 아니라 형제 부품 분할이다. 의존은 한 방향이다 — 본체 → 갈래 부품 → 단계 부품 → 틀 부품 → 잎. 본체는 모두를, 갈래 부품은 단계 · 틀 부품과 잎을, 단계 부품은 다른 단계 부품 · 틀 부품 · 잎을, 틀 부품과 잎은 잎만 import 한다(② 로 선 형제 부품도 방향에서는 잎이다). 유스케이스 칸 승격 폴더(② 포함) 전부에서 다음은 위반이다 — 부품 → 본체 import(`TYPE_CHECKING` 아래 · 함수 안 포함), 본체 객체를 부품에 넘기는 것(`self` 를 위치 · 키워드 인자로 — 부품이 Protocol 로 받아도 같다), 부품 함수 · 메서드(생성자 포함)의 인자 주석을 본체 클래스로 다는 것, 본체 메서드를 부품에 넘기는 것(`self.<메서드>` · `self` 를 잡는 `lambda` · 안쪽 함수 · `functools.partial`), 부품끼리의 순환 — 여기서 부품은 형제 모듈의 클래스와 함수를 모두 뜻한다. ②′ 폴더에서만 더 위반이다 — 갈래 → 갈래, 틀 · 잎 → 잎 아닌 형제.
칸을 «파일»로 명명하는 규범·검사기 문면(#256·#123·#193 …)은 그 칸의 실현 — 파일 또는 승격 본체 — 을 가리킨다. 승격 허용 표기의 값은 §1 트리가 소유한다(정본 `docs/file_tree.html` 의 data-sw · `standard_tree.Row.swappable` — 허용 칸: 트리 13·15·16·19·21·22·25·42·62·75·93·95·97행). 묶음 허용 표기의 값도 §1 트리가 소유한다(정본 `docs/file_tree.html` 의 data-grp · `standard_tree.Row.groupable` — 허용 칸: 트리 64·66·68·71·73·75행). 배제는 사유로만 선다 — ⓐ 범위 밖 서브트리(`framework/**`·`<project>/**`)·비-py(templates) ⓑ 도구 생성물(migrations) ⓒ 형태 명문 고정(composition_root #497 · api_router #107 · cron_job #174/#178 · event_subscription #509 · event_router #508 · apps #535/#538 · bc_error_schema #114/#572 · admin panel #342/#343) ⓓ 개념 원자 — 성장 출구가 새 인스턴스 파일(entity·값 객체·event·exception·계약·port 선언·domain repository 선언·`<entity>_model` #335 …). 배제 칸의 비대는 그 칸의 기존 규범이 관할한다 — 승격은 출구가 아니다. 배제·허용 표기를 바꾸는 주어는 정본 트리(트리 개정)다 — 프로젝트 관찰·판정 반복은 개정 제안 신호이지 현장 변경 근거가 아니다.

**의미 묶음** — §1 트리의 **묶음 허용 표기**(`data-grp`)가 붙은 파일 칸(트리 64·66·68·71·73·75행 — 엔티티 · 값 객체 · 이벤트 · 예외 · 공유 값 객체 · 도메인 서비스)의 인스턴스 파일은 그 부모 폴더(**묶음 부모**) 바로 아래 **묶음** 폴더 한 계층으로 나눠 둔다. 묶음은 승격이 아니다 — 서비스 칸 하위 폴더 `D` 는 `D/D.py` 가 있으면 승격(#638~#643), 없으면 묶음이다. 묶음 안 승격도 같은 형태 요건을 진다.

- **#654** — 묶음 안에는 폴더를 두지 않는다 — 묶음은 묶음 부모 바로 아래 한 계층뿐이다. 서비스 칸 묶음 안의 동명 폴더 승격은 파일 하나가 자란 것이라 계층으로 세지 않는다(그 안은 1단 평평 · #641). 묶음 허용 칸이 아닌 폴더 아래 폴더는 #490 이다.
- **#655** — 묶음 폴더는 내용 없는 `__init__.py`(0바이트 · docstring · 주석뿐 — #488 과 같은 자)를 갖는다 — 재수출 · `__all__` · 코드를 두지 않는다. 묶음 안 모듈은 모듈 경로로 직접 import 한다.
- **#656** — 묶음 허용 칸의 파일과 묶음 폴더는 `folder_group.place` 가 낸 자리에 둔다. 자리는 BC 하나씩, 파일 이름 · AST(반환 주석 · import · 클래스 기반) · 묶음 폴더 목록과 플러그인 낱말 목록만으로 정한다 — 프로젝트 설정은 없다. 그 함수의 설명이 곧 이 규칙의 문장이다.
  - **낱말** — 파일 이름(stem)을 `_` 로 자른다. 같은 묶음 부모 아래(묶음 안 포함) 단수 꼴이 낱말로 있는 복수 낱말은 단수로 접는다. 종류 낱말(앞 `invalid` · `unknown` · `nonexistent` · `unsupported` · 뒤 `mismatch`)은 떼고 읽는다. 서비스 칸은 첫 낱말이 동사면 떼고, 역할 낱말(`service` · `policy` · `resolver` · `renderer` · `reader` · `composer` · `filler` · `estimator`)은 어디서든 뗀다.
  - **업무 낱말** — 플러그인 낱말 목록(일반어 · 꾸밈말 · 동사 · 기술어 · 종류 낱말 · 트리 폴더 이름과 금지 이름)에 없고 영역 낱말도 아닌 낱말이다. 영역 낱말은 BC 이름의 낱말과, 애그리거트 폴더 안이면 그 애그리거트 이름의 낱말이다. 애매한 20 낱말(`part` · `reading` · `line` · `text` · `entry` · `share` · `slot` · `edition` · `reference` · `snapshot` · `check` · `code` · `setting` · `title` · `body` · `message` · `draft` · `summary` · `order` · `plan`)은 언제나 업무 낱말이다.
  - **단위** — 묶음 이름이 될 수 있는 것은 셋이다: 그 묶음 부모의 파일 이름 셋 이상에 맨 자리(바로 앞 낱말이 꾸밈말이 아닌 자리)로 나오는 업무 낱말 하나 · 이름 셋 이상에 나오는 이웃한 2~3 낱말 조합 구(앞 낱말은 꾸밈말 · 영역 낱말, 머리는 업무 낱말 · 일반어 · 영역 낱말 — 앞이 모두 영역 낱말이고 머리가 업무 낱말이면 그 업무 낱말 하나로 읽는다) · 이름 셋 이상에 나오는 같은 BC 의 여러 낱말 애그리거트 이름. 영역 낱말만으로 된 것 · 꾸밈말만으로 된 것 · 트리 폴더 이름이나 금지 이름이 하나라도 든 것은 단위가 아니다.
  - **자리** — 파일 이름을 왼쪽부터 읽어, 그 자리에서 시작하는 살아 있는 단위 가운데 가장 긴 것을 처음 잡은 묶음이 주인이다. 잡힌 것이 없으면 업무 낱말이나 다른 뜻 있는 낱말(영역 낱말 · 트리 폴더 이름과 금지 이름 · 동사 · 기술어)이 든 파일은 부모에 남는다. 빈 낱말(일반어 · 꾸밈말 · 종류 낱말)뿐인 값 객체 칸 파일은 그 파일을 import 하는 같은 BC 묶음 허용 칸 파일(쓰는 곳)이 모두 같은 묶음이고 그 부모에 그 묶음이 살아 있으면 그 묶음, 아니면 부모다. 서비스는 결정 함수(파일 이름과 같은 공개 함수 · 하나뿐인 공개 정의 · 그 클래스의 `__call__`)가 돌려주는 값 객체(예외 아님)가 정확히 한 묶음 이름에 있으면 그 이름의 묶음, 부모에 있거나 여러 묶음에 걸치면 부모다 — 돌려주는 값 객체가 없을 때만 그 서비스 칸과 같은 BC `shared_value_object/` 의 단위로 이름을 맞춘다.
  - **서고 죽음** — 새 묶음은 그 단위로 배정되고 단위가 맨 자리(구는 아무 자리)인 파일이 셋 이상이어야 선다(서비스 칸은 반환 · 이름으로 배정된 서비스 셋). 있는 묶음은 배정된 파일이 둘 이상이고 이름(서비스는 반환 포함)으로 배정된 파일이 하나라도 있으면 남고, 아니면 푼다. 부모의 살아 있는 묶음이 하나뿐이고 부모에 남는 파일이 없으면 그 묶음은 서지 않는다(통째 묶음 없음). 서비스 칸에 묶음 이름 `g` 와 같은 이름의 서비스(`g.py` · `g/g.py`)가 있으면 `g/` 는 서지 않는다. 죽을 묶음이 여럿이면 서비스 칸이 아닌 칸의 묶음을 먼저 보고(서비스 칸의 이름 맞추기는 그쪽의 살아 있는 단위를 쓴다), 그 안에서 (배정 수 · 부모 경로 · 이름)이 가장 작은 하나만 빼고 다시 계산한다.
  - 철자가 다른 단위는 합치지 않는다 — 묶음 이름은 단위 그대로다.
- **#657** — 여러 애그리거트가 함께 쓰는 개념(공유 값 객체 · 도메인 서비스가 던지는 것)의 업무 규칙 예외는 `shared_value_object/` 에 둔다 — 그 안에서는 다른 파일처럼 이름으로 묶는다(#656). 기계 술어가 없어 감수가 본다.

**어댑터 고정 골격** — `driven_layer/adapter/` 아래 ACL의 `anticorruption_layer/<other_bounded_context>/<capability>_adapter/`, 외부 시스템의 `external_system/<system>/<capability>_adapter/`, 그 밖 능력의 `<capability>/<technology>_adapter/` 는 처음부터 패키지다. 바깥 패키지와 `adapter/`·`command/`·`constant/`·`contract/`·`schema/` 다섯 역할 폴더에 `__init__.py` 를 반드시 둔다(#488). 역할 폴더는 내용이 없어도 생략하지 않는다. 초기화 파일은 재수출 전용이다(#640). 바깥에 구현 본체를 두거나 단일 `.py` 파일로 대체하지 않으며, 역할 폴더 안에 추가 폴더를 만들지 않는다(#490). 실제 내용 파일은 필요할 때만 만들며 200행 승격 신호의 대상이 아니다.

**#651 클래스별 파일** — `adapter/`·`command/`·`contract/`·`schema/` 의 내용 파일은 비공개 클래스를 포함해 클래스 하나당 파일 하나다. 같은 역할의 클래스가 여러 개면 각각 파일을 만든다. `constant/` 는 클래스 없이 관련 상수끼리 한 파일에 묶는다. 내용 없는 골격 파일과 재수출 초기화 파일은 클래스 수 검사의 대상이 아니다.

**역할 배치** — `adapter/` 는 포트를 구현하는 클래스를 소유한다. 외부 응답을 포트 반환값으로 바꾸는 reader 는 그 구현의 private 메서드 또는 본문에 둔다. `command/` 는 주입되는 호출 계약(Protocol 등)을 클래스별로 둔다. `contract/` 는 내부 계약 클래스를 소유하며 그 계약을 반환하는 builder 도 같은 파일에 둔다. `schema/` 는 외부 입출력 검증 클래스를 소유하며 관련 타입 별칭은 해당 스키마 파일에 둔다. `constant/` 는 프롬프트 등 관련 값을 `prompt.py` 같은 응집된 묶음으로 둔다. 반환 클래스가 포트 소유라는 이유로 외부 스키마를 아는 변환 함수를 포트 파일로 옮기지 않는다. 내부 참조는 모듈 직접 상대 import 로 연결한다. 기존 상속·명명·예외 번역 검사는 구현 역할 파일에, 의존 방향과 격리는 전체 역할 파일에 적용한다.
## §1 표준 트리 — 171행
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

행 번호는 정본의 행 번호이고, 규칙·검사기·명세가 「트리 N행」으로 이 번호를 가리킨다. `<…>` 는 자리표시자(§0 유형 ②③)다.

<!-- TREE:BEGIN — tree_mirror_check 가 쓴다 · 손으로 고치지 않는다 -->
```text
  1 application/<bounded_context>/
  2   composition_root/
  3     dependency_wiring.py
  4     event_wiring.py
  5     wiring_material.py
  6   published_event/
  7     <event>.py
  8   driving_layer/
  9     api/
 10       api_router.py
 11       bc_error_schema.py
 12       <area>/
 13         <area>_controller.py
 14         schema/
 15           schema_in.py
 16           schema_out.py
 17       webhook/
 18         <provider>/
 19           <provider>_controller.py
 20           schema/
 21             schema_in.py
 22             schema_out.py
 23     open_host_service/
 24       <service>/
 25         <service>_service.py
 26         contract/
 27           request/
 28             <request>_request.py
 29           response/
 30             <response>_response.py
 31           exception/
 32             <service>_published_error.py
 33             <exception>_exception.py
 34     cron_job/
 35       <job>_cron_job.py
 36     event_subscription/
 37       event_router.py
 38       <event>_subscription.py
 39   application_layer/
 40     <area>/
 41       <use_case>/
 42         <use_case>_use_case.py
 43         <use_case>_command.py
 44         <use_case>_query.py
 45         <use_case>_result.py
 46     port/
 47       <capability>/
 48         <capability>_port.py
 49         exception.py
 50         <data>_out.py
 51         <data>_in.py
 52       domain_bypass_query/
 53         <capability>/
 54           <capability>_query.py
 55           <data>_out.py
 56           <data>_in.py
 57           exception.py
 58       unit_of_work/
 59         <boundary>_unit_of_work.py
 60   domain_layer/
 61     <aggregate>/
 62       <aggregate>.py
 63       entity/
 64         <entity>.py
 65       value_object/
 66         <value_object>.py
 67       event/
 68         <event>.py
 69       <aggregate>_repository.py
 70       exception/
 71         <exception>.py
 72     shared_value_object/
 73       <value_object>.py
 74     domain_service/
 75       <domain_service>.py
 76   driven_layer/
 77     django_<bounded_context>/
 78       apps.py
 79       models/
 80         <entity>_model.py
 81       migrations/
 82         <migration>.py
 83       admin/
 84         <entity>/
 85           panel.py
 86           form/<form>_form.py
 87           feature/<feature>.py
 88       templates/admin/<bounded_context>/<page>.html
 89       templates/<bounded_context>/<capability>/<template>.html
 90     adapter/
 91       persistence/
 92         repository/
 93           <aggregate>_repository.py
 94         domain_bypass_query/
 95           <capability>_query.py
 96         unit_of_work/
 97           <boundary>_unit_of_work.py
 98       anticorruption_layer/
 99         <other_bounded_context>/
100           <capability>_adapter/
101             adapter/
102               <implementation>_adapter.py
103             command/
104               <command>.py
105             constant/
106               <constant>.py
107             contract/
108               <contract>.py
109             schema/
110               <schema>.py
111       external_system/
112         <system>/
113           <capability>_adapter/
114             adapter/
115               <implementation>_adapter.py
116             command/
117               <command>.py
118             constant/
119               <constant>.py
120             contract/
121               <contract>.py
122             schema/
123               <schema>.py
124       <capability>/
125         <technology>_adapter/
126           adapter/
127             <implementation>_adapter.py
128           command/
129             <command>.py
130           constant/
131             <constant>.py
132           contract/
133             <contract>.py
134           schema/
135             <schema>.py
136   test/
137     unit/
138     integration/
139     e2e/
140     factories/
141     fake/
142       <declaration>.py
143 framework/
144   broker/
145     internal/
146       internal_broker_port.py
147       internal_broker.py
148     external/
149       external_broker_port.py
150       external_broker.py
151   <capability>/
152     <capability>_port.py
153     exception.py
154     <data>_out.py
155     <data>_in.py
156     <technology>_adapter.py
157   <technology>/
158     <module>.py
159   pure/
160     <module>.py
161   test/
162     <module>.py
163     fake/
164       <declaration>.py
165     unit/
166 <project>/
167   api.py
168   urls.py
169   celery.py
170   settings/
171     <environment>.py
```
<!-- TREE:END -->

읽는 법:

- 최상위는 셋이다 — `application/<bounded_context>/`(BC 마다 하나) · `framework/`(저장소에 하나) · `<project>/`(Django 프로젝트 패키지).
- 폴더 이름이 끝에 `/` 를 달고, `admin/`·`templates/` 아래처럼 한 행이 하위 경로를 품기도 한다.
- 기계 사본은 `scripts/standard_tree.py` — 검사기들이 import 하는 유일한 트리 데이터다.

## §2 골격 규칙

### BC 직계 — 일곱뿐
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

- **#81** — `application/<bounded_context>/` 바로 아래에는 일곱 가지만 온다 — 층 폴더 넷(`driving_layer/` · `application_layer/` · `domain_layer/` · `driven_layer/`) · `test/` · `composition_root/` · `published_event/`. 여덟째는 없다.
- **#82** — BC 폴더 이름은 장고 앱 이름이 아니라 업무 경계의 이름이다(accounts · billing · ai_chat).
- **#10** — 네 칸을 모두 아는 것은 `composition_root` 하나뿐이다.
- **#628** — 이 BC 의 «업무 어휘»는 `domain_layer/**` 아래 공개 심볼(모듈·클래스·함수·Enum 값) 이름의 토큰 집합이다 — 폴더 이름만이 아니다. 별도의 «용어집 파일»은 두지 않는다. 불용어 목록(`Id`·`Status`·`Name`·`Item`·`Type`·`Value` …)도 저장소가 유지하는 데이터다.

### 입구 — `driving_layer/`
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

- **#88** — BC 의 입구 계층 폴더 이름은 `driving_layer/` 다 — `presentation_layer/` 를 쓰지 않는다.
- **#89** — 바깥 행위자가 BC 를 부르는 통로는 `driving_layer/` 뿐이다 — 다른 층에 입구를 두지 않는다.
- **#90** — `driving_layer/` 의 자식은 `api/` · `open_host_service/` · `cron_job/` · `event_subscription/` 넷뿐이고 «어떤 전송으로 오나»로만 갈린다 — HTTP · 같은 프로세스 함수 호출 · celery · 브로커. 「누가 부르나」(행위자)로 가르지 않는다. 같은 프로세스 함수 호출의 부르는 쪽에는 framework 의 요청 틀(Ninja 인증 · Django 미들웨어)도 들고, 틀이 `<project>/settings` 의 문자열로 등록해 부르는 BC 해석 함수도 `open_host_service/` 창구에 둔다 — 틀은 BC 를 import 하지 않고(#46 · #430) 창구는 요청 계약 하나를 받아 표준 라이브러리 자료만 돌려주며(#633 · #472) 계약 필드 이름은 틀이 정한 중립 낱말이다(#52).
- **#91** — 새 **전송**이 실제로 생기기 전에는 `driving_layer/` 의 자식을 늘리지 않는다 — 「새 행위자」로는 늘리지 않는다(웹훅이 그 반례다: 결제사라는 새 행위자가 왔지만 전송이 HTTP 라 2차 축 `webhook/<provider>/` 로 들어갔다). **늘리는 주체는 «정본 트리»다** — 개정되면 #486 에 따라 그 전송을 안 쓰는 BC 도 그 칸을 «빈 채로» 갖는다.
- **#92** — `driving_layer/` 의 잎은 `application_layer/<area>/` 아래만 의존한다 — 예외는 넷: 도메인 exception·값 객체(#95) · `composition_root` 의 `build_`(#97) · 남의 `published_event/`(#507) · `framework/<technology>/`·`framework/<capability>/` 의 계약·스키마(브로커 포트는 여기 없다 — `application_layer` 쪽만 #7 이 연다: `framework/broker/{internal,external}/*_broker_port.py` import 허용).
- **#178** — 소비 task 가 껍데기를 넘어 조율을 시작하면 새 칸을 여는 것이 아니라 입구 로직 금지 위반을 고친다.

### 만들지 않는 칸
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

- **#20** — 값이 하나뿐인 축으로는 폴더를 만들지 않는다. **#21** — 어떤 종류가 하나뿐이면 폴더가 아니라 파일로 둔다. (트리의 파일 칸들이 이 원리의 산물이다 — 예: `<aggregate>_repository.py`.) #21 의 주어는 트리 설계의 축·종류 결정이다 — 파일 칸의 동명 폴더 승격(#490 교체형 실현)은 종류 축 폴더가 아니라 #21 의 주어가 아니다. §1이 정한 세 어댑터의 역할 폴더는 현재 내용 파일 수와 관계없이 모두 실현한다(#488).
- **#58** — `application/**/management/commands/` 를 만들지 않는다.
- **#187** — 포트 선언에 BC 최상위 칸을 만들지 않는다 — 애그리거트에 안 붙는 포트는 `application_layer/port/` 에만 산다.
- **#314** — `domain_layer/` 에 `specification/` 폴더를 두지 않는다.
- **#658** — 저장소 루트의 `tests/` · `test/` 아래에는 `.py` 를 두지 않는다 — 이름과 무관하다(helpers · factories · fakes · conftest 포함 · 내용 없는 `__init__.py`(0바이트 · docstring · 주석뿐 — #655 와 같은 자)만 뺀다). BC `test/` · `framework/test/` 의 파일은 최상위 `tests` · `test` 패키지를 import 하지 않는다. 시험은 주인의 표준 시험 자리(BC `test/` · 전역 규칙은 `framework/test/unit/`)에 둔다. 레포 루트 `conftest.py`(공유 fixture 자리)와 루트 `tests/web/` · `test/web/`(web 시험)은 이 규칙 밖이다.

### `migrations/` — 생성물만
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

- **#336~#338·#593** — `driven_layer/django_<bounded_context>/migrations/` 에는 `makemigrations` 가 «생성한 것»만 둔다 — 사람이 손으로 데이터를 채우는 파일(`RunPython`·`RunSQL`)을 넣지 않는다. 마이그레이션은 「돌았다 / 안 돌았다」 두 상태뿐이라 배치 크기·부분 재실행·진행률이 구조적으로 안 된다. 대량 채우기는 파일이 아니라 **배포 절차의 한 «단계»** 다(Expand → Backfill → Contract — 그 코드는 트리 밖 `scripts/`, 규정하지 않는다). 허용 목록(#593)은 도구 산출물의 모양이 정한다 — 그 밖의 함수·분기·도메인 import·데코레이터는 위반이다. 덤 — `elidable` 을 안 달면 그 자리에서 squash 최적화가 끊긴다.

### `<project>/`
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

- **#429** — `<project>/` 에는 프레임워크가 «전역에 딱 하나»를 요구하는 것만 온다 — `api.py` · `urls.py` · `celery.py` · `settings/`. `celery.py` 항목의 «celery 채택» 전제는 **정본 트리(표준) 수준**의 채택이다 — 개별 프로젝트의 채택 여부가 아니다. celery 를 안 쓰는 프로젝트도 이 칸을 «빈 파일»로 갖는다(#488 — 빈 `celery.py` 가 규범 준수의 정상 상태이고, 뒤에 celery 가 필요해지면 그 빈 파일이 착지 자리다). 표준이 celery 를 버리는 개정에서만 이 목록이 다시 선다(#491 «조건부 없음»의 자리는 트리 1행 `application/**` 이라 여기 걸리지 않는다 — `<project>/` 파트는 이 목록이 관할한다).
- **#430** — `<project>/` 는 `application/` 을 «등록»만 하고 «타입»으로 알지 않는다 — 문자열 경로는 등록이고 import 는 앎이다.
- **#432** — `<project>/` 는 BC 가 늘어도 커지지 않는다 — 판정 물음은 「BC 하나를 통째로 지웠을 때 이 파일이 바뀌나」다.
- **#436** — `<project>/` 의 `health.py`·`home.py`·`asgi.py`·`wsgi.py` 는 표준 트리의 관할 밖이라 칸을 만들지 않는다(면제).

## §3 명명
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

- BC 이름은 업무 경계의 이름(#82 — §2). 파일·클래스 명명 규약 전수(창구 `_command`/`_query` · 계약 `…Request`/`…Response` · 어댑터 고정 패키지·구현 파일 · ORM `<entity>_model.py` 등)는 정본의 각 칸 «이름» 줄이 소유하며, 매핑표 순서로 이 절에 편입된다.
- **BC(앱)명↔애그리거트명 유사 변형 금지(권장 — 기계 검사기 없음·reviewer 점검)**: `ordering` vs `order` 같은 한 글자·복수형 차이로 헷갈리게 두지 않는다 — 같게 하거나 명확히 다른 컨텍스트명으로 한다(#82 물음에 딸린 점검 · 08-12 삭제분 감사에서 복원).
- **포트 자료의 방향**(2026-09-27): 방향의 기준점은 우리 안쪽이다 — 들어오면 `<data>_in`, 나가면 `<data>_out`. 포트·조회 계약(`port/<capability>/` · `port/domain_bypass_query/<capability>/` · `framework/<capability>/`) 메서드의 **인자**(우리가 내보내는 자료)를 `<data>_in` 으로 두지 않는다 — `_in` 은 어댑터만 만든다(#574). 같은 BC(framework 포트는 framework)의 다른 계약이 돌려준 `_in`(그 필드 포함)을 그대로 넘기는 것은 만드는 것이 아니다. 기계 판정은 G1 pre-gate 예보(선언 확정 #574)와 G2 #574(유스케이스의 생성 호출)다. 메서드가 이름 붙인 자료를 **돌려주면**(바깥의 답이 들어온다) 그 자료는 `<data>_in` 이다(원시 값·`None` 은 이 규칙 밖) — 기계 검사기가 없어 discipline-reviewer 가 설계 경량 점검과 구현 감사에서 본다. 이 규칙 이전의 `_out` 반환 자료와 실물 메서드에 이미 있는 `_in` 인자는 의미 빚이다 — 새로 만드는 자료는 이 규칙을 따르고, 기존 `_out` 자료를 새 메서드가 그대로 돌려주는 것은 허용한다(중복 `_in` 을 만들지 않는다 — 개명은 의미 빚 정리에서 한다). 파일 접미와 클래스 접미의 교차(`_out.py` 안의 `…In` 등)는 #573(`port/<capability>/` 만)이다.

## §4 이관 — 종료 기록과 빚

### 이관 종료 (2026-08-12)
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

옛 이름(`presentation_layer/`→`driving_layer/` · `infra_layer/`→`driven_layer/` · `published_service/`→`open_host_service/` · `acl/`→`anticorruption_layer/` · 루트 `common/`→`framework/`)의 이중 수용은 **2026-08-12 에 끝났다** — 검사기는 옛 이름을 더 알아보지 않는다. 옛 이름 재등장은 이제 별도 진단이 아니라 트리 밖 칸 위반(#81·#490 — 층 이름 위장은 #324)이다.

### brownfield 는 «면제»가 아니라 «아직 안 갚은 빚»이다
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

brownfield 는 코드의 속성이 아니라 규칙 변경의 그림자다 — 코드는 안 바뀌었는데 규칙이 바뀌어 위반이 됐다. 기능 요청의 「리팩터링 대상」은 따로 정의하지 않는다 — **백스톱이 내는 위반이 곧 그것이다**(리팩토링 모드는 BC 의미 점검 항목도 대상이다 · 2026-09-27). BC 를 작업하면(작업하는 BC = G0 스코프의 그 BC — 파일을 건드렸다는 사실이 그 BC 를 '작업 대상'으로 만들지 않는다) 그 BC 의 백스톱 위반을 «먼저» 정리하고 시작하며, 「가만 있어도 해로운」 위반은 그것을 기다리지 않는다. 미루기는 사용자에게 물어서만 가능하고 `.dddjango/` 에 기록된다.

### 검사기의 가드 계약
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

저장소가 표준을 채택한 신호(둘 이상의 신호원)가 있는데 검사 대상이 0건이면 검사기는 통과가 아니라 `exit 2` 로 막는다(#74) — 개명·경로 변화로 검사가 «조용히 무동작»이 되는 것을 막는 가드다.

### 규칙 개정의 이행 순서
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

- **#72** — 규칙을 바꾸는 개정은 플러그인 셋 — 검사 스크립트·리뷰어 지침·표준 문서 — 을 **한 커밋에서 먼저** 고치고, 코드(대상 저장소)는 그 «다음»에 옮긴다. 순서가 뒤집히면 코드가 아직 없는 규칙에 맞아 거짓 위반이 나거나, 규칙이 아직 없는 코드가 거짓 통과한다.

## 배경 (이 표준이 파생된 곳)
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

Evans(바운디드 컨텍스트·애그리거트·유비쿼터스 언어) · Vernon(애그리거트=트랜잭션 경계) · Martin(의존 규칙·Humble Object) · Cockburn(포트와 어댑터 — «who triggers or is in charge of the conversation»). 각 칸의 결정 근거·기각 대안은 저장소 정본의 결정 카드 58장에 있다 — 이 문서는 «값»만 싣는다.
## §5 driven 출구 면제 — 성문
<!-- graph-owned: 이 절의 정본은 ontology 그래프다 — 수정은 rules 정본에서, 이 본문 직접 수정 금지 -->

`django_<bounded_context>/` 와 ORM 모델을 import 할 수 있는 곳(driven 출구 허용면)은 셋뿐이다.

- `adapter/persistence/` 아래 셋 — `repository/`·`domain_bypass_query/`·`unit_of_work/`.
- `django_<bounded_context>/admin/` — admin 은 자기 앱의 모델을 안다.
- `adapter/<capability>/django_adapter/adapter/<implementation>_adapter.py` — **비애그리거트 ORM 쓰기 능력**의 django 기술 구현. persistence 셋에는 이 능력의 칸이 없어(리포지토리=애그리거트 전용 · bypass=조회 전용) 그 능력 포트 구현이 여기 온다. 이 면제는 구현 역할 파일에만 적용되며, `anticorruption_layer/`·`external_system/` 은 제외다(2호 실증·사용자 A안 — 리비전 10호 채번 · 집행 #328 `check-context-isolation`·#462 `check-port-adapter-pairing` 공동).
