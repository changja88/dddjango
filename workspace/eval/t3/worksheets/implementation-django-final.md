# T3 저작 워크시트 — implementation-django-final

- 원문: `dddjango/skills/implementation-django/references/final.md` (1789행 · 센서스 좌표와 일치 — 드리프트 0, 절 스팬 해시 63/63 통과)
- spec: `workspace/eval/t3/specs/implementation-django-final.spec.json`
- 자기 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py …` → **exit 0** (1회 통과 · `--write` 미사용)
- 규모: REF 63절 · 블록 246 · Work 220 · restates 블록 6 (발주서 규범 223 — 차 3은 §3 재진술 «유예»가 아니라 문서 내 재진술 3건이 정본으로 흡수된 것)
- 필독 이행: 발주서 · authoring.md §13~§16 · migrate docstring · 파일럿 spec 2건 · `dddjango/scripts/check-*.py` **27종 전수 docstring 선두 실독**(로스터 실측 27 = `ls check-*.py | wc -l`)

---

## 1. census 대사 (발주서 규범 수 ↔ spec Work 수)

일치 60절 · 불일치 3절. 불일치는 전부 **같은 문서 내 재진술**로, 사본 블록을 `restates`로 연결하고 Work를 미승격한 결과다(§15 «정본 1곳만 Work 승격»). P0 계수는 문장 단위라 사본도 셌으므로 **P0가 과대 산정, 내 계수가 옳다**는 판정이다(과소 아님 — 규범 자체는 정본에 살아 있다).

| 절 | 발주서 | spec | 판정 |
|---|---|---|---|
| s003-1 | 1 | 1 | 일치 |
| s004-1.1 | 4 | 4 | 일치 (표 6행 중 의무 표지 4행만 — Loose Coupling·Quick Development는 프레임워크 성질 설명) |
| s005-1.2 | 3 | 3 | 일치 |
| s006-1.3 | 2 | 2 | 일치 (Terse Syntax 행은 성질 설명) |
| s007-1.4 | 3 | 3 | 일치 (bullet 4 중 «무한한 유연성»은 프레임워크 성질) |
| s008-1.5 | 2 | 2 | 일치 (HTML 비종속·보안 기본 2행은 성질 설명) |
| s009-1.6 | 3 | 3 | 일치 |
| s011-2.1 | 3 | 3 | 일치 |
| s012-2.2 | 4 | 4 | 일치 (그룹 순서 규범은 88행 산문, 펜스는 예시 운반) |
| s013-2.3 | 3 | 3 | 일치 (전부 코드 주석 운반) |
| s014-2.4 | 1 | 1 | 일치 |
| s015-2.5 | 12 | 12 | 일치 — 분해: b2 계층 소유 6 + b4 `.value` 3 + b5 소비 규율 3 |
| s016-2.6 | 1 | 1 | 일치 |
| s017-2.7 | 1 | 1 | 일치 |
| s019-3.1 | 4 | 4 | 일치 — 분해: b3 인용구 2(조직 소유·평면 나열 금지) + b4 인용구 2(houserules 소유·§3.1 배경 강등) |
| s020-3.2 | 3 | 3 | 일치 |
| s021-3.3 | 2 | 2 | 일치 |
| s022-3.4 | 1 | 1 | 일치 (359행은 사유 설명 — 규범은 코드 예에 있음) |
| s024-4.1 | 4 | 4 | 일치 — 인용구 2 + 본문 1 + 2000줄 1 |
| s026 | 1 | 1 | 일치 (P0 §4.2 분배 1) |
| s027 | 2 | 2 | 일치 — 코드 주석 «주의» 1 + Abstract+FK 우선 1 |
| **s029-4.3** | **4** | **3** | **불일치** — 496행 «§2.5 계층 소유대로 domain Enum 파생»은 P0가 재진술로 명기(발견 6). 사본 블록 b3 → `s015-2.5/b2` restates·Work 미승격. 나머지 3 = JSONField 한정·Decimal 사용·Float 회피 |
| s030-4.4 | 3 | 3 | 일치 |
| s032-5.1 | 2 | 2 | 일치 — 재진술(542행 코드 주석)은 P0도 비계수(비고로만 표기)라 b1 restates만 걸고 Work 증감 없음 |
| s033-5.2 | 3 | 3 | 일치 (선택 기준 표 3데이터행) |
| s034-5.3 | 1 | 1 | 일치 |
| s035-5.4 | 1 | 1 | 일치 (annotate/filter 순서는 P0 설명 판정 계승) |
| s036-5.5 | 1 | 1 | 일치 |
| s037-6 | 3 | 3 | 일치 |
| s038-7 | 3 | 3 | 일치 |
| s039-8 | 5 | 5 | 일치 — 701행 3 + 703행 2 |
| s040-8.1 | 3 | 3 | 일치 (740행 `source`는 가능성 설명) |
| s041-8.2 | 2 | 2 | 일치 |
| s042-8.3 | 3 | 3 | 일치 |
| s043-8.4 | 1 | 1 | 일치 |
| s044-8.5 | 2 | 2 | 일치 |
| s045-9 | 1 | 1 | 일치 |
| s046-9.1 | 5 | 5 | 일치 — 인용구 2 + 허용 조건 3 |
| s047-9.2 | 4 | 4 | 일치 — 코드 주석 1 + 회피 조건 3 |
| s049-10.1 | 4 | 4 | 일치 (전부 코드 주석) |
| s050-10.2 | 6 | 6 | 일치 — 931행 2 + 933행 3 + squash 정정 1 |
| s051-10.3 | 3 | 3 | 일치 — 코드 3단계 1 + bullet 2 |
| s052-10.4 | 14 | 14 | 일치 — 도입 1 + 코드 5 + fake-initial 2 + 검증 2 + 옛 루트 2 + db_table 우선 1 + historical 동결 1 |
| s054-11.1 | 2 | 2 | 일치 |
| s055-11.2 | 3 | 3 | 일치 — 재진술(1078행 코드 주석)은 P0 비계수라 b1 restates만, Work 증감 없음 |
| s056-11.3 | 1 | 1 | 일치 |
| s057-11.4 | 2 | 2 | 일치 |
| s060-12.2 | 2 | 2 | 일치 |
| s062-13.1 | 4 | 4 | 일치 (표 «주의사항» 열 4행) |
| s063-13.2 | 3 | 3 | 일치 |
| s064-13.3 | 2 | 2 | 일치 |
| s066-14 | 3 | 3 | 일치 |
| s067-14.1 | 3 | 3 | 일치 — 표 집계 1 + 인용구 2 |
| **s069-14.3** | **2** | **1** | **불일치** — 1393행 assertNumQueries 입장 조건은 P0가 §11.1 재진술로 명기. 사본 b4 → `s054-11.1/b1` restates·Work 미승격. 잔여 1 = `django_db` 명시 |
| s070-14.4 | 3 | 3 | 일치 |
| s072-15.1 | 1 | 1 | 일치 (1426행 흐름 방향은 동작 설명) |
| s073-15.2 | 2 | 2 | 일치 |
| s075-16.1 | 8 | 8 | 일치 — 1477행 2 + 도입 기준 5 + 억지 분리 금지 1 |
| **s076-16.2** | **5** | **4** | **불일치** — 1519행 셋째 문장 «어느 경우든 상태 값은 심볼로만 소비»가 §2.5 소비 규율 사본. 블록 단위라 b2에 restates를 걸되 같은 블록의 앞 두 문장(평면 한정·4계층 도메인 소유)은 고유 규범으로 승격 — 혼합 블록 처리 |
| s077-16.3 | 2 | 2 | 일치 |
| s078-16.4 | 28 | 28 | 일치 — 도입 2 + 코드 주석 1 + bullet 15(1581:1·1582:2·1583:2·1584:6·1585:2·1586:1·1587:1) + 표 도입 1 + 표 6행 + 말미 3 (2+1+15+1+6+3=28) |
| s079-16.5 | 11 | 11 | 일치 — 도입 4 + birth-enum 1 + 1637행 3 + 인용구 1 + 말미 2 (재진술 주석은 Work 미승격·대신 1637행을 3문장으로 분해) |
| s087 | 2 | 2 | 일치 |

**합계: 발주서 223 ↔ spec 220 (차 3 = 문서 내 재진술 사본 3건).**

---

## 2. 배선 근거 표 (전 규범 220)

근거 코드 (4원 = ①문면 역할명 ②docstring § 인용 ③P0 커버 ④registry #N):

- **D0** — 4원 지목 없음 → §16 위임 기본값 표(`implementation-*` → `agent-discipline-reviewer`)
- **D1** — ①문면 표지만 성립(검사기 담당 규칙 부재) → 기본값
- **D2** — 후보 검사기 docstring을 실독해 **스코프 밖**임을 확인하고 기본값(기본값 «도피» 아님을 근거로 명시)
- **E** — enforcedBy 성립(②docstring 직접 인용). 전 E 행은 의미 잔여분을 reviewer와 병행 배선

전 220행에서 `delegatedTo = agent-discipline-reviewer`가 성립한다(문서군 기본값 — 이 문서는 `implementation-*`). 아래 표의 «검사기» 열이 빈 행은 delegatedTo 단독이다.

| 절 | Work label | 검사기(enforcedBy) | 근거 |
|---|---|---|---|
| s003-1 | Django 설계 철학의 코드 작성 기반 준거 | — | D1 ①«모든 Django 코드 작성의 기반이다»(P0 보수적 포함) |
| s004-1.1 | Less Code — 최소 코드·보일러플레이트 배제 | — | D1 ①«작성되어야 하며» |
| s004-1.1 | DRY — 고유 개념·데이터의 단일 장소 | — | D1 ①«존재해야 한다» |
| s004-1.1 | 명시가 암시보다 낫다 — 마법의 조건부 사용 | — | D1 ①«~할 때만 사용한다» |
| s004-1.1 | 저수준~고수준 일관성 유지 | — | D1 ①«유지한다» |
| s005-1.2 | 모델의 객체 전 측면 캡슐화 | — | D2 check-domain-model 은 표준 트리 `domain_layer` 대상(#8·#256) — 평면 Django 모델 비커버 |
| s005-1.2 | 데이터·메타정보의 모델 클래스 정의 | — | D1 ①«정의한다» |
| s005-1.2 | 모델 자기완결성 | — | D1 ①«있어야 한다» |
| s006-1.3 | save() 명시적 호출 요구 | — | D1 ①«명시적 호출 필요»(P0 애매—포함) |
| s006-1.3 | 커스텀 SQL 작성 용이성 보존 | — | D1 ①«쉽게 작성할 수 있어야 한다» |
| s007-1.4 | URL의 Python 함수명 결합 금지 | — | D2 로스터 27종에 URLconf 축 검사기 없음 |
| s007-1.4 | 예쁜 URL 우선 | — | D1 ①«쉽거나 같아야 한다» |
| s007-1.4 | URL의 파일 확장자 포함 금지 | — | D1 ①«포함시키지 않는다» |
| s008-1.5 | 템플릿의 로직·표현 분리 | — | D2 check-naming #588·#589 는 사람 문구·템플릿 업무 판정 축 |
| s008-1.5 | 템플릿 기능의 표현 필수 범위 한정 | — | D1 ①«프로그래밍 언어를 발명하지 않는다» |
| s009-1.6 | 함수로 충분하면 클래스 미인스턴스화 | — | D1 |
| s009-1.6 | 요청 객체의 직접 전달 | — | D1 |
| s009-1.6 | GET·POST 명확 구분 | — | D1 |
| s011-2.1 | black 포매터 사용 | — | D2 ③P0 «백스톱 미지목»(발견 2)·로스터에 포매터 검사기 없음 |
| s011-2.1 | 코드 88자·문서 79자 줄 길이 | — | D2 동상 |
| s011-2.1 | Python 4칸·템플릿 2칸 들여쓰기 | — | D2 동상 |
| s012-2.2 | 임포트 그룹 순서·그룹 내 알파벳 정렬 | — | D2 context-isolation 의 import 규칙은 층·BC 방향 축(#2·#9·#93~#95) |
| s012-2.2 | isort 자동 정렬 사용 | — | D2 ③P0 «검사기로 지목되진 않음» |
| s012-2.2 | 편의 임포트 사용 | — | D1 |
| s012-2.2 | 다중 점 상대 임포트 회피·절대 임포트 | — | D1 |
| s013-2.3 | f-string 내 함수 호출 금지 | — | D1 ①코드 주석(P0 발견 5) |
| s013-2.3 | f-string 내 연산 금지 | — | D1 ①코드 주석 |
| s013-2.3 | 번역 대상 문자열의 f-string 금지 | — | D2 check-naming #588 은 렌더 «위치» 축 |
| s014-2.4 | 모델 내부 정의 순서 7단 | — | D1 ①코드 주석 1~7 |
| s015-2.5 | 값 집합 단일 출처는 domain_layer StrEnum | — | D2 choices-literal-consumption 은 «선언된 심볼의 존재»에 앵커된 소비 축 — 선언 계층 판정은 의미 레인 명시 |
| s015-2.5 | TextChoices 자체 선언의 순수 인프라 필드 한정 | — | D1 ①«한정한다» |
| s015-2.5 | 도메인 상태의 TextChoices 선언 금지 | — | D2 형태로 안 갈림(도메인 판정 유무는 의미) |
| s015-2.5 | 도메인 상태 필드의 domain Enum 파생 | — | D2 checker 는 리터럴 소비만 봄 |
| s015-2.5 | 도메인 판정 최초 발생 슬라이스의 파생형 전환 | — | D1 전환 «시점» 판정 |
| s015-2.5 | 기존 TextChoices 배치의 규약 부정(빚 선언) | — | D1 ①«규약이 아니라 아직 안 갚은 빚» |
| s015-2.5 | 직렬화 자리의 StrEnum 멤버 직접 배치 금지 | — | D2 checker 5)가 비-Constant 를 «정상»으로 통과시킴 |
| s015-2.5 | domain Enum 파생의 `.value` 평탄화 | — | D2 docstring 5)는 집행 규칙이 아니라 거짓양성 회피(면제) 조항이고 구현부(167~174행)는 `default=<문자열 Constant>`만 적출 — 위반형 `default=OrderStatus.PENDING`(멤버 직접)을 정상 통과시켜 커버 0(133행 쌍둥이·메모 5 원칙과 동일) |
| s015-2.5 | CheckConstraint·부분 인덱스 조건 값의 동일 파생 | — | D2 checker (b)는 filter/exclude 한정 — Meta 조건식 비커버 |
| s015-2.5 | choices·Enum 필드 값의 심볼 참조 의무 | `check-choices-literal-consumption.py` | **E** ②docstring 표제 + (a) default 리터럴 · (b) filter/exclude 리터럴 |
| s015-2.5 | 값 비교는 ==(is 금지) | — | D2 ②docstring «보지 않는 것»에 비교식 명시 제외 |
| s015-2.5 | 복합 상태 판정의 1차 시정은 애그리거트 술어·enum 프로퍼티 | — | D2 ②check-app-container «판정-소유 형태(빈혈) 같은 의미 변종은 범위 밖(discipline-reviewer 몫)» |
| s016-2.6 | 템플릿 코딩 스타일의 web §4 소유 위임 | — | D1 소유 포인터 |
| s017-2.7 | 뷰 첫 매개변수는 반드시 request | — | D1 ①코드 주석 |
| s019-3.1 | 테스트 디렉터리 조직의 implementation-test §4.2 소유 | — | D1 소유 포인터 |
| s019-3.1 | 테스트 파일 평면 나열 금지 | `check-test-config.py` | **E**(부분 — **표준 트리 한정 커버**) ②docstring ⑵ #383/#384 «test/ 직계 자식은 다섯뿐 — unit·integration·e2e·factories·fake» + #596 «직계 파일은 conftest·__init__ 만». 금지문 자체는 배치 불문 일반형이라 부착이 성립하나 결정적 커버는 표준 트리 `test/` 부분집합뿐이고, 운반체 문맥인 앱별 `tests/` 변종의 평면 나열은 검사기 밖(reviewer) — 메모 7과의 정합은 «일반형 금지문의 부분집합 커버»로 정리 |
| s019-3.1 | 생성 코드 표준 파일트리의 discipline-houserules 소유 | `check-layer-skeleton.py` | **E** ①문면 «배치 권위는 그 문서» + ②«표준 파일트리 골격 검사기 — 제1원칙(#486~#491)» |
| s019-3.1 | §3.1의 배경 강등(배치 권위 아님) | — | D1 ①«여기 §3.1은 그 표준의 배경이다» |
| s020-3.2 | 앱 이름은 간결한 복수형 단어 | — | D2 check-naming 담당 32규칙에 복수형 규칙 부재 |
| s020-3.2 | 한 문장 목적 서술 불가 시 앱 분리 | — | D1 |
| s020-3.2 | 앱 간 순환 의존 시 설계 재검토 | — | D2 context-isolation·event-publish #600 은 표준 트리 BC 축 — 평면 앱 순환 비커버 |
| s021-3.3 | 비밀 정보 하드코딩 절대 금지 | — | D2 check-test-config ⑶ 는 settings 환경축 분할(#445~#447)만 |
| s021-3.3 | .env 파일의 gitignore 등재 | — | D2 로스터에 `.gitignore` 판독 검사기 없음 |
| s022-3.4 | 모듈 최상위 settings 접근 회피 | — | D1 ①좋은/나쁜 예 운반 |
| s024-4.1 | 절 전체의 평면 Django 맥락 한정 | — | D1 ①인용구 한정 조항 |
| s024-4.1 | 표준 4계층의 평면 ORM 판정 메서드 blocker | — | D2 ②check-app-container «판정-소유 형태(빈혈) … discipline-reviewer 몫» |
| s024-4.1 | 비즈니스 로직의 모델·서비스 배치 | — | D2 평면 Django 축 |
| s024-4.1 | 모델 2000줄 초과 시 서비스 레이어 분리 검토 | — | D1 판단형 |
| s026 | 공통 필드 재사용 시 추상 베이스 클래스 권장 | — | D1 ①«가장 적합하다»(P0 §4.2 분배 1) |
| s027 | 다중 테이블 상속의 주의 사용 | — | D1 ①코드 주석 «주의:» |
| s027 | 추상 베이스 클래스+명시적 FK 우선 | — | D1 ①«더 낫다» 우선 규칙 |
| s029-4.3 | JSONField는 스키마 없는 데이터 한정 | — | D1 |
| s029-4.3 | 금액 필드의 DecimalField 사용 | — | D1 |
| s029-4.3 | 금액 필드의 FloatField 회피 | — | D1 |
| s030-4.4 | clean()의 Python 레벨 검증 수행 | — | D2 usecase-dto-placement #139 는 표준 트리 `schema_in` 축 |
| s030-4.4 | CheckConstraint 이중 방어 | — | D1 |
| s030-4.4 | full_clean() 호출 경로 확보 | — | D1 |
| s032-5.1 | QuerySet 메서드 체이닝 보장 | — | D2 transaction-boundary #282~#287 은 표준 트리 리포지토리 축 |
| s032-5.1 | get_queryset() 오버라이드 기본 필터 주의 | — | D1 판단형 |
| s033-5.2 | FK·O2O에는 select_related() | — | D1 표 행 운반 |
| s033-5.2 | M2M·역참조에는 prefetch_related() | — | D1 표 행 운반 |
| s033-5.2 | 조건부 프리페치에는 Prefetch() 객체 | — | D1 표 행 운반 |
| s034-5.3 | 프로파일링 없는 only()·defer() 공격적 사용 금지 | — | D1 |
| s035-5.4 | 불필요 계산 필드의 alias() 사용 | — | D1 |
| s036-5.5 | 루프 개별 save 대신 bulk 연산 | — | D2 transaction-boundary #599 는 리포지토리 `save_all` 축 |
| s037-6 | 서버렌더 뷰의 implementation-django-web §2 소유 | — | D1 소유 포인터 |
| s037-6 | JSON API 라우팅·스키마와 REST 계약의 소유 분리 | — | D1 소유 포인터(계약 «설계» 판정은 design-review-api 이나 이 문서 규범의 준수 판정은 기본값 유지) |
| s037-6 | 코어 문서의 service·selector 경계 한정 | — | D1 범위 한정 |
| s038-7 | 웹 폼의 implementation-django-web §6 소유 | — | D1 소유 포인터 |
| s038-7 | durable invariant의 model·DB 경계 보장 | — | D2 제약 «설계» 판정 검사기 부재 |
| s038-7 | 도메인 규칙의 architecture-ddd 소유 | — | D1 소유 포인터 |
| s039-8 | 신규 REST 계약은 API 계약 문제로 선행 처리 | — | D1 (③P0: 소유 문서 문면 미지정) |
| s039-8 | greenfield 기본 경로는 Django Ninja Router·Schema | — | D2 ninja-boundary-middleware 는 §6 미들웨어 자가등록 축 |
| s039-8 | DRF 내용의 유지보수·기채택 프로젝트 한정 | — | D1 범위 한정 |
| s039-8 | 신규 코드의 DRF 기본 권장 금지 | — | D1 |
| s039-8 | 도메인 규칙의 Django-side boundary 배치 | — | D2 ②check-app-container «판정-소유 형태는 discipline-reviewer 몫» |
| s040-8.1 | 시나리오별 Serializer 분리 | — | D2 로스터의 스키마 검사기는 ninja 표면(response-schema-bypass·openapi-error-declaration) |
| s040-8.1 | fields = `__all__` 회피 | — | D2 동상 |
| s040-8.1 | 공유 규칙의 모델·service·DB constraint 상향 | — | D2 usecase-dto-placement #139 는 표준 트리 축 |
| s041-8.2 | 액션별 Serializer 분리 | — | D2 DRF 표면 |
| s041-8.2 | 트랜잭션·부수효과·상태 전이의 model·service 경계 분리 | — | D2 transaction-boundary 는 표준 트리 유스케이스·리포지토리 축 |
| s042-8.3 | 전역 기본 permission의 settings 설정 | — | D2 DRF 표면 |
| s042-8.3 | ViewSet 레벨 permission 오버라이드 | — | D1 허용형 |
| s042-8.3 | 객체 레벨 권한은 has_object_permission() | — | D1 |
| s043-8.4 | APIView 직접 사용 시 수동 페이지네이션 호출 | — | D1 |
| s044-8.5 | AcceptHeaderVersioning 관행 채택 | — | D1 ①(P0 애매—포함) |
| s044-8.5 | 필드 삭제·변경은 새 버전에서만 | — | D2 business-vocabulary #604 «계약은 가산만»은 framework capability 계약 축 |
| s045-9 | 시그널 사용 시나리오의 명확한 인지 | — | D1 |
| s046-9.1 | BC 경계 간 트리거의 signal 금지(published_event 소유) | `check-event-publish.py` | **E** ①인용구 «#89·#90» + ②docstring #502·#507·#508 |
| s046-9.1 | signal 예시의 같은 BC 내부·서드파티 수신 한정 | — | D1 범위 한정 |
| s046-9.1 | 제어 불가 서드파티 모델 반응 시 signal 허용 | — | D1 허용 조건 |
| s046-9.1 | 순환 의존 회피형 앱 간 통신 시 signal 허용 | — | D1 허용 조건 |
| s046-9.1 | 다수 모델 일괄 핸들러 적용 시 signal 허용 | — | D1 허용 조건 |
| s047-9.2 | 외부 부수효과의 커밋 전 실행 금지(§16.4 전제) | `check-transaction-boundary.py` · `check-usecase-dto-placement.py` | **E** ①코드 주석 + ②#200 + #541 «커밋 전 발행 금지 — `.publish(` 직접 호출은 `uow.after_commit` 밖» — 금지문이 부수효과 종류를 한정하지 않아 발행형도 위반형이므로 s078-16.4/1585 쌍둥이 판과 배선 일치(양쪽 다 `.publish(` 한정 부분 커버·email 등은 reviewer) |
| s047-9.2 | 이미 결합된 컴포넌트 간 signal 회피 | — | D1 회피 조건 |
| s047-9.2 | save()·delete() 오버라이드로 충분할 때 signal 회피 | — | D1 회피 조건 |
| s047-9.2 | request_started·request_finished의 미들웨어 대체 | — | D2 ninja-boundary-middleware 의 유일 판정은 «BC driving 자가정의 미들웨어의 자가등록 적출» — 시그널을 계속 써도 발화하지 않아 커버 0(s072-15.1 순서 규범과 동형) |
| s049-10.1 | 마이그레이션을 작게 유지 | — | D1 ①코드 주석 |
| s049-10.1 | sqlmigrate로 실제 SQL 확인 | — | D2 결정적 절차이나 로스터에 실행 검사기 없음 |
| s049-10.1 | 마이그레이션 파일의 버전 관리 포함 | — | D2 #336(자리)·#337(파일명 꼴)은 VCS 포함과 무관 — gitignore 된 마이그레이션도 자리·이름이 맞으면 통과해 커버 0. 아래 gitignore 쌍둥이 규범과 동일 근거 |
| s049-10.1 | migrations/의 gitignore 등재 금지 | — | D2 `.gitignore` 판독 검사기 없음 |
| s050-10.2 | migrations/에는 makemigrations 산출물만 | `check-mechanism-ownership.py` | **E** ②#593 «허용 목록 밖은 전부 위반» |
| s050-10.2 | 손 편집 RunPython·RunSQL 데이터 마이그레이션 금지 | `check-mechanism-ownership.py` | **E** ②#593 «RunPython/RunSQL 제외» — 문면 정확 일치 |
| s050-10.2 | 대량 채우기는 Expand→Backfill→Contract 배포 단계 | — | D1 (인용 §11.1 은 architecture-db 절 — P0 발견 1 표류) |
| s050-10.2 | backfill 코드의 저장소 루트 scripts/ 배치 | — | D2 layer-skeleton 은 BC 내부 폐쇄만 — 트리 밖 자리 비커버 |
| s050-10.2 | 순서 결합 소량 정리의 단일 마이그레이션 접기 금지 | — | D2 #593 은 손편집 «형태» 축 |
| s050-10.2 | squash 시 데이터 마이그레이션 보존 정정 | — | D1 사실 정정형 |
| s051-10.3 | NOT NULL 컬럼 추가의 3단계 배포 | — | D1 ①코드 주석 «좋은 예: 3단계 배포» |
| s051-10.3 | 대형 테이블 마이그레이션의 작은 단위 분할 | — | D1 |
| s051-10.3 | PostgreSQL 무중단 도구 고려 | — | D1 판단형 |
| s052-10.4 | 이주 시점(WHEN)의 architecture-ddd §3.2 소유 분리 | — | D2 ②check-app-container 가 같은 §3.2 항-(2)를 «위치» 축으로만 집행한다고 명시 |
| s052-10.4 | AppConfig label의 기존 값 유지 | `check-db-table.py` | **E**(부분) ②apps #329 «label 명시» 존재 축 — 값 보존은 reviewer(#330 값 규약과 문면 충돌 지점) |
| s052-10.4 | 기존 테이블명의 db_table 명시 보존 | `check-db-table.py` | **E**(부분·**충돌**) ②docstring 실문면 «#630 신규 모델 `Meta.db_table` 존재 **+ 값** `<app_label>_<entity_snake>`»(구현부 417~420행 — 미명시·값 불일치 둘 다 blocker) · 대상은 신규 파일 한정(추적 모델 미검사). 이주는 신규 파일로 떨어지므로 «미명시» 위반형은 결정적 커버, 그러나 보존명이 규약과 다르면(`tbl_product`) #630 값 검사가 이 규범과 **반대로** 발화한다. 원문 §10.4(1037~1039행)의 «존재만 보고 값 형태는 보지 않는다»는 검사기 실물과 어긋난 서술 — **원문↔검사기 표류로 소급 패스 상신**(원문 수정은 이 공정 밖) |
| s052-10.4 | 기존 0001_initial 불변(재작성·삭제 금지) | `check-mechanism-ownership.py` | **E**(부분) ②#593 «사람이 직접 손대지 않는다 — 도구 산출물 모양 허용 목록 밖은 전부 위반»으로 허용 목록을 깨는 **손 편집** 재작성만 결정적. 원문이 명명한 대표 함정인 `makemigrations` 재생성(fresh initial)은 docstring이 «도구가 만들고 지우는 변경은 손편집이 아니다»라 주어(사람) 밖이고 삭제도 검사기 시야 밖 — 이력 정합(0002 연쇄·적용 기록) 판정 전체가 reviewer |
| s052-10.4 | 클래스 rename의 state-only 0002 반영 | — | D2 #593 허용 목록이 `SeparateDatabaseAndState` 를 통과시킴 |
| s052-10.4 | AlterModelTable 동반으로 state·실 db_table 정합 | — | D2 드리프트 확인은 `makemigrations --check` 절차(검사기 아님) |
| s052-10.4 | --fake-initial의 기본 도구 채택 금지 | — | D1 |
| s052-10.4 | 이력 전무 legacy 앱 편입 시 조건부 사용 | — | D1 조건 한정 |
| s052-10.4 | makemigrations --check 드리프트 0 확인 | — | D2 ③문면이 결정적 절차를 명시하나 로스터 비커버 |
| s052-10.4 | sqlmigrate로 0002의 DDL 미발행 확인 | — | D2 동상 |
| s052-10.4 | 이주 완료 시 옛 루트 앱 통째 삭제 | — | D2 ①«houserules §0 배타성» 문면은 있으나 ②check-app-container 는 문면이 명명한 실패 모드(move 를 copy 로 — 새 트리 완성 + 옛 루트 방치)에 구조적으로 발화하지 않는다: 옛 루트는 추적된 기존 디렉터리에 새 마이그레이션도 없어 G2 불성립, 성립해도 실질 이주 대응 앱이 이미 있어 G3 면제. 검사기가 커버하는 «미이주 방치»는 이 규범의 위반형이 아님 — 커버 0 |
| s052-10.4 | MIGRATION_MODULES 잔존 핀 금지 | — | D2 settings MIGRATION_MODULES 판독 검사기 없음 |
| s052-10.4 | 신규 db_table 규약 대비 이력 보존 우선 | — | D2 ①문면의 백스톱 지목은 이 Override 가 아니라 상대편 규범(신규 모델 db_table 규약 — `discipline-houserules` §4 소유)을 향한다 · ②docstring «기존 테이블명 보존(개명 강제 아님)»은 추적 모델 **미검사**를 밝히는 면제(부작위) 조항이라 이 Override 의 위반형(보존명을 규약으로 개명해 이력을 끊기)을 못 잡아 커버 0. 오히려 신규 파일 이주에서는 #630 값 검사가 보존명을 blocker 로 내 규범과 대적한다(위 «db_table 명시 보존» 행과 같은 표류) — 면제 인용을 배선 근거로 쓰지 않는다(메모 5 원칙) |
| s052-10.4 | 마이그레이션 historical value 리터럴 동결 | — | D2 ②choices-literal-consumption 3)은 migrations/ 를 **면제**하며 §10.4 를 면제 근거로 인용 — 집행 아님 |
| s054-11.1 | query-count 테스트는 중앙 입장 심사 이후에만 작성 | — | D2 입장 심사 검사기 부재(discipline-tdd 문서군 기본값도 discipline-reviewer) |
| s054-11.1 | 미입장 상태의 exact query-count 테스트 금지 | — | D2 test-config 는 바인딩·구조 축 |
| s055-11.2 | 인덱스 대상은 filter·exclude·order_by 빈출 필드 | — | D1 |
| s055-11.2 | 프로파일링 후 인덱스 추가 | — | D1 |
| s055-11.2 | 느린 쿼리의 EXPLAIN ANALYZE 확인 | — | D1 |
| s056-11.3 | 변경 필드 한정 save(update_fields=...) | — | D1 좋은/나쁜 예 운반 |
| s057-11.4 | 존재 확인은 exists() | — | D2 transaction-boundary #285 는 리포지토리 요약값 축 |
| s057-11.4 | 개수 확인은 count() | — | D2 동상 |
| s060-12.2 | 캐시 적합성 선판단 | — | D1 |
| s060-12.2 | 운영 캐시는 Redis·Memcached | — | D2 기술 선택 축 검사기 담당 규칙 부재 |
| s062-13.1 | csrf_exempt의 극히 제한적 사용 | — | D1 표 «주의사항» 열 운반(P0 발견 5) |
| s062-13.1 | safe·mark_safe 사용 주의 | — | D1 동상 |
| s062-13.1 | raw()·extra()의 직접 문자열 보간 금지 | — | D2 로스터에 raw SQL 보간 검사기 없음 |
| s062-13.1 | X_FRAME_OPTIONS DENY 설정 | — | D2 settings 값 검사기 없음 |
| s063-13.2 | production 보안 설정 묶음 적용 | — | D2 test-config ⑶ 은 환경축 «분할»만 |
| s063-13.2 | manage.py check --deploy 실행 | — | D2 ③P0 «파이프라인 백스톱으로 지목된 건 아님»(발견 2) |
| s063-13.2 | CSRF_COOKIE_HTTPONLY의 조건부 사용 | — | D1 조건 한정 |
| s064-13.3 | raw()의 파라미터화 쿼리 사용 | — | D1 좋은/나쁜 예 운반 |
| s064-13.3 | extra()의 params 파라미터 사용 | — | D1 동상 |
| s066-14 | 테스트 입장 심사의 discipline-tdd 소유 | — | D1 소유 명시 |
| s066-14 | framework 자체 시험 테스트 금지 | — | D2 test-config 는 테스트 «대상» 판정 비커버 |
| s066-14 | 승인된 테스트가 있을 때만 class·layout 선택 | — | D1 조건 한정 |
| s067-14.1 | 시나리오별 TestCase 선택 기준 | — | D1 표 집계 1(P0) |
| s067-14.1 | 신규 add 테스트의 pytest 관용구 의무 | `check-test-config.py` | **E**(부분) ②⑴ pytest↔Django settings 바인딩 |
| s067-14.1 | TestCase↔pytest 등가 매핑의 implementation-test §16 출처 | — | D1 출처 포인터 |
| s069-14.3 | @pytest.mark.django_db로 DB 접근 명시 | `check-test-config.py` | **E** ②#387 «unit 은 DB 를 켜지 않는다(django_db …)» · #389 |
| s070-14.4 | assertIs(x, True)로 타입까지 검증 | — | D1 코드 주석 운반 |
| s070-14.4 | assertRaisesMessage로 메시지까지 검증 | — | D1 동상 |
| s070-14.4 | 테스트 독스트링의 기대 동작 직서술 | — | D1 동상 |
| s072-15.1 | SecurityMiddleware 최선두·Session은 Authentication 앞 | — | D2 «MIDDLEWARE 를 AST 로 읽는 유일 검사기»는 데이터 소스 공유일 뿐 담당 규칙 근거가 아니다 — ninja-boundary-middleware 의 유일 판정은 «BC driving 자가정의 미들웨어의 자가등록 적출»이라 순서가 틀려도 exit 0(커버 0 · §16 역방향 문면) |
| s073-15.2 | 미들웨어의 경량 유지 | — | D1 |
| s073-15.2 | 미들웨어 하나 = 관심사 하나 | — | D1 |
| s075-16.1 | 비대 판단은 변경 이유·orchestration 복잡도로 | — | D1 판단형 |
| s075-16.1 | 서비스 레이어 도입은 기준 하나 이상 성립 시 | — | D1 조건 |
| s075-16.1 | 도입 기준 — 복수 모델·애그리거트·어댑터 조율 | — | D1 허용 조건 |
| s075-16.1 | 도입 기준 — 복수 entry point 흐름 중복 | — | D1 허용 조건 |
| s075-16.1 | 도입 기준 — use case의 명시적 트랜잭션 경계 소유 | — | D2 transaction-boundary 는 표준 트리 축 — 도입 «판단» 비커버 |
| s075-16.1 | 도입 기준 — 외부 side effect와 DB write 정렬 | — | D1 허용 조건 |
| s075-16.1 | 도입 기준 — persistence·orchestration 세부로 모델 난독화 | — | D1 허용 조건 |
| s075-16.1 | 짧은 절차의 억지 서비스 분리 금지 | — | D1 |
| s076-16.2 | 예시의 평면 Django 관례 한정 | — | D1 이중 문맥 한정 |
| s076-16.2 | 표준 4계층의 상태 판정·전이 도메인 소유 | — | D2 ②check-app-container «판정-소유 형태 … discipline-reviewer 몫» |
| s076-16.2 | 서비스 네이밍 `<entity>_<action>` | — | D2 check-naming #28 은 «service(단독 토큰)» 약어 금지 축 |
| s076-16.2 | 접두사 네임스페이싱 | — | D2 check-naming 32규칙에 접두 네임스페이싱 부재 |
| s077-16.3 | 대부분 프로젝트는 모델 메서드+서비스 함수로 충분 | — | D1 허용형 |
| s077-16.3 | Repository 패턴의 점진 도입 한정 | — | D1 조건 한정 |
| s078-16.4 | commit·rollback 경계는 use case 단위 | — | D2 transaction-boundary #195·#197·#200 은 유스케이스 «쓰기» 축 |
| s078-16.4 | atomic()은 최소 블록에 한정 | — | D1 |
| s078-16.4 | 표준 트리 응용 계층의 커밋 후 부작용은 uow.after_commit | `check-transaction-boundary.py` | **E** ①코드 주석 «#200» + ②#200 + ④#200 정확 일치 |
| s078-16.4 | atomic() owner는 application service | — | D1 경향형(보수적 포함) |
| s078-16.4 | select_for_update()는 pessimistic lock 필요 시에만 | — | D2 domain-model #549 는 «수정 조회는 캐시 우회» 축 |
| s078-16.4 | 잠금 범위·backend 지원·lock 검증 가능성 확인 | — | D1 |
| s078-16.4 | application-level check 단독 신뢰 금지 | — | D1 |
| s078-16.4 | 필수 불변식의 DB boundary 동반 설계 | — | D2 idempotency-scope-creep 은 «미요청 도입 차단» 축 |
| s078-16.4 | 커스텀 DB 백엔드 우회 금지(sqlite no-op 한계) | `check-mechanism-ownership.py` | **E** ②⑴ «DatabaseWrapper 서브클래스 + 트랜잭션/락 의미 변경 마커» AND 게이트 |
| s078-16.4 | 운영 정합용 잠금 코드 존치와 CheckConstraint 최종 방어선 | — | D1 제약 설계 판정 |
| s078-16.4 | race 패자 IntegrityError의 표현 계층 상태 코드 변환 | — | D2 transient-overmapping 은 Operational/DatabaseError 축이고 IntegrityError 는 **명시 제외** |
| s078-16.4 | 잠금 부족 시 백엔드 자작 대신 DB 아키텍처 검토 회귀 | `check-mechanism-ownership.py` | **E**(부분) ②⑴ «명세 승인 없이 커스텀 백엔드 교체» — 회귀 «절차»는 reviewer |
| s078-16.4 | 엔진·연결 의미 변경의 출처-불문 금지 | `check-mechanism-ownership.py` | **E**(부분) ①«출처-불문» 열거(몽키패치·connection_created·OPTIONS·isolation_level·conftest) vs ②검사기는 ENGINE 점경로 축만 |
| s078-16.4 | 연결 튜닝은 stock OPTIONS 허용 목록 한정 | — | D2 검사기 ⑴ 은 OPTIONS 키 목록을 보지 않음 |
| s078-16.4 | 외부 side effect의 커밋 전 실행 금지 | `check-transaction-boundary.py` · `check-usecase-dto-placement.py` | **E** ②#200 + #541 «커밋 전 발행 금지 — .publish( 직접 호출은 uow.after_commit 밖» |
| s078-16.4 | on_commit()으로 부수효과 시점 정렬 | `check-transaction-boundary.py` | **E** ②#200(정렬 창구 고정) |
| s078-16.4 | 결정 불명확 시 DB 아키텍처 검토 선행 | — | D1 절차 판정 |
| s078-16.4 | Idempotency-Key 계약과 DB idempotency storage 정합 | — | D2 §9.6 표제 공유일 뿐 판정 축은 G0 «미요청 멱등성 도입 차단»(scope 미요청 단정 ∧ G1 승인 부재)이라, 정당 채택된 멱등성의 계약↔storage **불일치**는 어떤 형태로도 안 잡힌다 — 커버 0. 같은 절 «필수 불변식의 DB boundary 동반 설계» 행과 동일 논거로 통일 |
| s078-16.4 | risky write 구현·리뷰 시 체크리스트 명시 | — | D1 리뷰 절차 의무 |
| s078-16.4 | 체크리스트 — transaction owner 명시 | — | D1 표 행 운반 |
| s078-16.4 | 체크리스트 — lock·idempotency 수단 명시 | — | D2 idempotency-scope-creep 은 미요청 도입 축 |
| s078-16.4 | 체크리스트 — DB constraint 명시 | — | D1 표 행 운반 |
| s078-16.4 | 체크리스트 — side effect timing 명시 | — | D1 표 행 운반(집행 축은 #200 이 별도 규범에서 짐) |
| s078-16.4 | 체크리스트 — isolation·retry 결정 명시 | — | D1 표 행 운반 |
| s078-16.4 | 체크리스트 — verification candidates와 근거 명시 | — | D1 표 행 운반(입장 결정 소유 = discipline-tdd) |
| s078-16.4 | verification candidates 행의 비의무성·discipline-tdd 소유 | — | D1 면제 조항 |
| s078-16.4 | 독자 production failure일 때만 add·아니면 reuse | — | D2 입장 심사 검사기 부재 |
| s078-16.4 | add 테스트의 django_db 마커 선택 기준 | `check-test-config.py` | **E**(부분) ②#387·#389 DB 신호 축 |
| s079-16.5 | 유실 불허 외부 발행의 Outbox 구현 | `check-broker-contract.py` | **E**(부분) ②#603 «⑴outbox … 선언 유무만 잰다» |
| s079-16.5 | 채택 기준·전달 보장의 타 문서 소유 | — | D1 소유 포인터 |
| s079-16.5 | outbox 행과 비즈니스 write의 동일 atomic 블록 저장 | — | D2 transaction-boundary 담당 규칙 11종(#4·#195·#197·#200·#282·#283·#285·#287·#355·#597·#599)은 애그리거트 리포지토리·유스케이스 쓰기 축 — **#546 은 이 검사기 담당이 아니다**(진단 메시지 내 원리 인용일 뿐 · 진단 소유는 check-domain-model 응용 축이고 그 역시 «한 트랜잭션 = 애그리거트 하나» 판정이라 outbox 행 동반 저장은 비커버) |
| s079-16.5 | 발행은 별도 디스패처가 수행 | — | D2 event-publish 는 published_event 표면 축 |
| s079-16.5 | 발행 이벤트 종류의 birth-enum 단일 출처 | — | D2 event-publish #504 는 «사실 하나=파일 하나» 축 |
| s079-16.5 | 디스패처 자리는 driving_layer/cron_job/(management/commands 금지) | `check-layer-skeleton.py` · `check-missable-entrance.py` | **E** ①«#58» + ②layer-skeleton «#58 … 금지 경로(management/commands)» + missable-entrance #172·#174 |
| s079-16.5 | 미발행 행의 select_for_update(skip_locked=True) 잠금 | — | D2 #599 는 `save_all` 경합 가드 축 |
| s079-16.5 | 발행 성공 시 published_at 기록 | — | D1 |
| s079-16.5 | management command 예시의 배경 한정 | — | D1 범위 한정 |
| s079-16.5 | at-least-once 전제의 소비자 멱등 | `check-broker-contract.py` · `check-missable-entrance.py` | **E** ②#532 «at-least-once 를 요구로 적는다» + #181 «멱등성은 유스케이스가 갖는다» |
| s079-16.5 | 유실 허용 in-process 후속은 on_commit()으로 충분 | — | D2 표준 트리는 #200 이 uow.after_commit 요구 — 평면 맥락 한정 |
| s087 | 복합 PK 예시의 같은 BC 내 가정 한정 | — | D1 조건 한정 |
| s087 | BC 경계 ORM FK 금지 — 값 참조 | `check-db-table.py` | **E** ①«architecture-ddd §3.3 규칙3» + ②모델 #631 «타 BC 모델을 FK·O2O·M2M 참조 금지(문자열 참조 포함)» — 정확 일치 |

**배선 집계**(적대 리뷰 수리 반영 — 2026-08-22): enforcedBy 부착 Work **23건** · enforcedBy 링크 **27건**(한 Work에 검사기 2종 부착이 **4건** — s047-9.2 커밋 전 부수효과 · s078/1585 외부 side effect · s079 디스패처 자리 · s079 at-least-once) · delegatedTo 단독 **197건** · delegatedTo 는 220/220. 무소유 0(도구가 단언 · 기계 계수 재확인). 등장 검사기 **10종**: mechanism-ownership 6 · test-config 4 · transaction-boundary 4 · db-table 3 · layer-skeleton 2 · usecase-dto-placement 2 · broker-contract 2 · missable-entrance 2 · choices-literal-consumption 1 · event-publish 1. 나머지 **17종**(api-error-controller-contract · app-container · business-vocabulary · common-container · composition-root · context-isolation · domain-model · error-centralization · idempotency-scope-creep · naming · ninja-boundary-middleware · openapi-error-declaration · port-adapter-pairing · public-surface-annotation · response-schema-bypass · synthetic-infra-exc · transient-overmapping)은 전수 실독 결과 이 문서 규범과 담당 규칙이 겹치지 않아 **의도적 미부착**이며, 그 판정 근거는 위 표의 D2 행과 §4 메모 7·10에 남겼다.

> 수리 이력: 초판 집계 문장은 «25 Work · 30 링크 · 2종 5건»이었으나 초판 spec 실측조차 30/33/3이었다(같은 단락 검사기별 계수 33만 실측과 일치 — 자기모순). 위 수치는 수리 후 spec을 기계 계수한 값이다.

---

## 3. 재진술 유예 (교차 문서 — spec 미기입·소급 패스 대상)

문서 내 쌍 3건은 spec `restates`로 이미 연결했다(§1 불일치 3절 + s032·s055·s079의 코드 주석 사본 — 총 6블록이 `s015-2.5/b2`·`s015-2.5/b5`·`s054-11.1/b1`을 가리킨다). 아래는 **다른 문서 상대**라 spec에 넣지 않고 유예한 사본이다(발주서 restate 열은 전 절 N이지만, 원문 직접 확인으로 사본 성격을 판정했다 — 단순 «소유 포인터»는 제외하고 규범 내용이 실제로 재진술된 것만 올린다).

| # | 사본 블록 좌표 | 상대 문서/절(추정) | 사본 내용 |
|---|---|---|---|
| 1 | `s024-4.1/b1` (367행 인용구) | architecture-ddd-final §3.2 | 판정·불변식의 `domain_layer` 애그리거트 소유 + 평면 ORM 판정 메서드 blocker |
| 2 | `s076-16.2/b2` (1519행) | architecture-ddd-final §3.2 | 표준 4계층의 상태 판정·전이 도메인 소유·값 집합 domain Enum 파생 |
| 3 | `s087/b3` (1745행) | architecture-ddd-final §3.3 규칙3 | BC 경계 ORM FK 금지 — 값 참조 |
| 4 | `s079-16.5/b1` (1604행) | architecture-ddd-final §3.7 · architecture-db-final §9.7 | Outbox 채택 기준 · 전달 보장·dead-letter 정책 |
| 5 | `s079-16.5/b2` (1607~1608행 주석) | architecture-ddd-final §3.7 | birth-enum(1종째부터 enum·append-only) |
| 6 | `s079-16.5/b3` (1637행) | discipline-houserules(표준 트리 #58) | `application/**/management/commands/` 금지 · 디스패처 자리 `driving_layer/cron_job/` |
| 7 | `s046-9.1/b1` (860행 인용구) | discipline-houserules / architecture-ddd (#89·#90) | BC 경계 간 트리거는 `published_event/`·`event_subscription/` 소유 |
| 8 | `s050-10.2/b1` (931행) | architecture-db-final §11.2 | 대형 backfill 이 요구하는 넷(배치·재실행·모니터링·부분 완료 결정) — **문서 한정자 없는 § 인용(P0 발견 1 표류)** |
| 9 | `s050-10.2/b2` (933행) | architecture-db-final §11.1 | Expand → Backfill → Contract 3단계 |
| 10 | `s078-16.4/b6` (1584행) | architecture-db-final §9.5 | 락·동시성 제어 회귀 경로 + stock OPTIONS 허용 범위 |
| 11 | `s078-16.4/b18` (1600행) | discipline-tdd-final | 입장 심사 add/reuse 판정 규칙 |
| 12 | `s054-11.1/b1` (1053~1055행) | discipline-tdd-final | 중앙 입장 심사 통과 뒤에만 query-count 테스트 |
| 13 | `s066-14/b1` (1286행) | discipline-tdd-final | 입장 심사 소유 + framework 자체 시험 테스트 금지 |
| 14 | `s067-14.1/b2` (1297행 인용구) | implementation-test-final §16 | `TestCase`→`django_db` · `TransactionTestCase`→`django_db(transaction=True)` 등가 매핑 |
| 15 | `s019-3.1/b3` (287행 인용구) | implementation-test-final §4.2 | 테스트 디렉터리 의미군 분리·평면 나열 금지 |
| 16 | `s015-2.5/b2` (203행) | architecture-ddd-final §3.2 (635행 «상태·종류 값 집합의 표기와 계층 소유») | 단일 출처는 domain enum · `models.TextChoices` 자체 선언은 순수 인프라 필드 한정 · 도메인 상태 필드의 domain Enum 파생 — 상대 문면이 이 절을 «`implementation-django` §2.5»로 명시 지시 |
| 17 | `s015-2.5/b4` (220행) | architecture-ddd-final §3.2 (635행) | ORM `default=` 등 직렬화 경계의 `.value` 평탄화 — 상대 문면이 §2.5를 명시 지시(정본 방향 후보: 여기가 메커니즘 정본) |
| 18 | `s015-2.5/b5` (222행) | architecture-ddd-final §3.2 (635행) | 소비는 심볼로만·비교는 `==` · 복합 상태 판정의 1차 시정은 애그리거트 술어·enum 프로퍼티 · 승격 판정·허용 목록은 `discipline-cleancode` §2.14 — **이 문서군 최대 재진술 군집** |
| 19 | `s015-2.5/b2` (203행 말미 «빚 선언») | architecture-ddd-final §3.2 (637행 말미) · discipline-houserules §4(brownfield) | «기존 배치가 일관돼 보여도 확립된 규약이 아니라 아직 안 갚은 빚 — 트리 결정의 입력이 아니다(2026-08-12)» — 세 문서 동일 선언 |

**유예 건수: 19.** (16~19는 2026-08-22 적대 리뷰 수리로 추가 — 초판은 같은 §3.2 상대의 더 약한 쌍 1·2만 올리고 최대 군집인 s015-2.5를 빠뜨렸다. 정본 방향 판정은 소급 패스 몫이므로 좌표만 기록한다.) (별도로 SKILL.md «핵심 운영 원칙»이 이 문서 §2.5·§4.1·§16.1~.5 등의 압축 사본이라는 P0 발견 7이 있으나, 사본 측 블록이 `implementation-django-skill` 문서 소관이라 여기서 좌표를 못 잡는다 — 소급 패스의 SKILL 담당분에서 잡아야 한다.)

---

## 4. 경계 판단 메모

1. **표 절의 블록 입도 2종.** 행마다 규범이 서는 표(§1.1·§1.3·§5.2 선택 기준·§13.1 주의사항·§16.4 risky write)는 §13대로 «행 단위» 블록으로 쪼갰다. 반면 §14.1 TestCase 선택 표는 P0가 표 **전체를 집계 1**로 셌고 개별 행이 독립 규범이 아니라, 머리행+구분행+데이터 4행을 **한 table-row 블록**으로 두고 Work 1개를 매달았다(행 분할 시 Work를 어느 행에 매달지 임의가 된다).
2. **혼합 블록의 restates.** §16.2 1519행은 한 문단 안에 «평면 예시 한정»·«4계층 도메인 소유»(고유 규범)와 «상태 값은 심볼로만 소비»(§2.5 사본)가 섞여 있다. 블록은 행 범위라 쪼갤 수 없으므로 블록에 `restates`를 걸고 **동시에** 고유 규범 2개를 Work로 승격했다. 파일럿(ddd s017-3.2/b1)은 사본만 있는 순수 케이스였다 — 혼합 케이스의 첫 판례다.
3. **코드 블록이 재진술 운반체인 경우.** §5.1(542행)·§11.2(1078행)·§16.5(1615행)는 사본이 코드 «주석»이다. 리터럴은 펜스 전체 verbatim이므로 블록 단위 `restates`를 코드 블록에 걸었다. §16.5 b2는 같은 블록의 다른 주석(birth-enum)이 고유 규범이라 §16.2와 같은 혼합 처리를 했다.
4. **§9.2 코드 주석의 «커밋 전 부수효과 금지»는 재진술로 보지 않았다.** §16.4 1585행과 내용이 겹치지만 문면이 «§16.4 on_commit 정렬이 **전제**다»라고 의존을 선언할 뿐 규범을 옮겨 적지 않았고, 센서스 restate 열도 N이며 P0가 이를 §9.2의 4번째 규범으로 독립 계수했다. 축자 사본이 아니므로 각자 Work.
5. **§10.4 historical value 동결 ↔ §2.5 `.value` 평탄화도 재진술 아님.** 발주서 비고의 «동형 원리» 판정을 계승했다 — §2.5는 «직렬화 자리에서 평탄화하라», §10.4는 «마이그레이션 파일의 값은 산 Enum을 참조하지 말라»로 대상과 금지 형태가 다르다. 다만 검사기 배선에서는 둘의 관계가 결정적이다: `check-choices-literal-consumption`이 `migrations/`를 **면제**하는 근거로 바로 이 §10.4를 인용하므로, §10.4 동결은 그 검사기의 집행 대상이 **아니다**(enforcedBy 미부착 — 인용이 있다고 배선하면 오배선이다).
6. **`---` 수평선과 후행 빈 줄의 귀속.** 절 말미의 `---`는 다음 절의 시작이 아니라 현재 절 스팬 안이므로 마지막 prose 블록으로 흡수했다(도구의 byte 등가 단언으로 확인). 헤딩 직후 빈 줄은 §13대로 첫 블록 선두에 귀속, 그 밖의 빈 줄은 선행 블록 후행에 귀속했다.
7. **평면 Django vs 표준 트리의 스코프 갈림이 배선의 주 위험이었다.** 이 문서의 다수 절(§4.1·§8.x·§11.x·§16.1~.3)은 «평면 Django» 맥락이고, 로스터 27종은 거의 전부 `application/<bc>/` 표준 트리 채택을 전제로 exit 0(«표준 미채택»)한다. 그래서 이름이 비슷하다는 이유로 배선하면(예: §5.5 bulk → `check-transaction-boundary #599`, §11.4 exists → `#285`) 대상 밖 오배선이 된다. D2 근거 행은 전부 이 확인을 거친 것이고, 반대로 표준 트리를 명시 지시하는 문장(§16.4 #200·§16.5 #58·§17.3 #631·§9.1 #89·#90)에서는 **기본값으로 도피하지 않고** 검사기를 붙였다.
8. **`agent-acceptance-tester`를 쓰지 않은 이유.** 테스트 «입장 심사» 규범(§11.1·§14 도입·§14.1·§16.4 말미)은 문면이 소유자를 `discipline-tdd`로 지목한다. §16 위임 기본값 표에서 `discipline-tdd` 문서군의 기본 Agent도 `agent-discipline-reviewer`이므로(rule-owner-map ⓓ 유일 관례) 기본값을 유지했다. registry의 `agent-acceptance-tester`는 기본값 표에 등장하지 않아 이탈 근거가 없다.
9. **§3.2 «앱 간 순환 의존» 판정.** `check-context-isolation`(BC 경계·층 방향)과 `check-event-publish #600`(공표 사실 BC 간 순환)이 «순환»을 다루지만 둘 다 표준 트리 BC 그래프가 대상이고, 이 절은 평면 Django 앱이다 — 기본값 도피가 아니라 스코프 밖 판정이다.
10. **§15.1 미들웨어 순서 — 초판 오배선을 D2로 정정(2026-08-22 적대 리뷰 수리).** 초판은 settings의 `MIDDLEWARE`를 AST로 읽는 검사기가 `check-ninja-boundary-middleware` 하나뿐이라는 이유로 부착하고 «부분 커버»라 적었다. 그러나 **데이터 소스 공유는 4원 근거가 아니다** — 그 검사기의 유일한 판정은 «BC driving 층 자가정의 미들웨어의 전역 MIDDLEWARE 자가등록 적출»이라, 순서가 틀려도·시그널을 계속 써도 자가등록이 아니면 exit 0이다. 커버 0을 «부분»이라 부른 것이므로 §15.1 순서 규범과 §9.2 «request_started/finished 미들웨어 대체» **둘 다 D2로 내렸다**. 이후 규칙: 담당 규칙(판정 축)이 위반형을 하나라도 잡지 못하면 «유일한 데이터 소스»여도 부착하지 않는다(§16 역방향 문면의 대칭).
