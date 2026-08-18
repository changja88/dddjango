# E05 — implementation-django 규범 센서스 (P0)

담당: 문서 담당자 E05 · 판정일 2026-08-18

## 파일별 요약

| 파일 | 행수 | 절수 | 규범 문장수 |
|---|---|---|---|
| `dddjango/skills/implementation-django/SKILL.md` | 53 | 4 | 23 |
| `dddjango/skills/implementation-django/references/final.md` | 1789 | 70 | 223 |
| **합계** | 1842 | **74** | **246** |

- ④쌍둥이(파일 단위): 두 파일 모두 codex판 존재 — `codex-dddjango/skills/implementation-django/SKILL.md`, `codex-dddjango/skills/implementation-django/references/final.md` (find로 확인). 전 74절에 «있음» 상속.
- 축 판정 기준 메모:
  - ①앵커 «있음» = §N/§N.M 번호 절. SKILL.md의 번호 없는 관례 헤딩(«언제 쓰나» 등)과 final.md의 목차·참고 자료는 «없음»으로 판정(파일명 없이 코퍼스 내 유일성 없음).
  - ③백스톱: 스크립트명 지목은 §10.4의 `check-db-table.py`가 유일(+ 같은 절의 `makemigrations --check`·`sqlmigrate` 결정적 검증 절차) → 그 절만 «커버». 규범 문장 0인 절은 «비커버(규범 없음)», 나머지는 «불명».
  - 규범 문장 수는 산문 + 규칙을 실어 나르는 코드 주석·표 행을 포함(아래 비고에 표기). 애매 문장은 보수적으로 포함하고 비고에 남김.

## SKILL.md (4절)

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---|---|---|---|---|
| frontmatter(name·description·user-invocable) | 2 | 없음 | 명시 | 불명 | «먼저 로드한다» + 3방향 위임(web·ninja·architecture-api) |
| «언제 쓰나» | 7 | 없음 | 명시 | 불명 | 로드 조건 1 + 경계 위임 bullet 6 (web·ninja·api·ddd·db·python/cleancode) |
| «핵심 운영 원칙» | 12 | 없음 | 명시 | 불명 | final.md §들의 압축 재진술(§4.1·§16.1–.5·§2.5·§5·§10·§3.3–.4). Choices bullet 하나에 지시 4개 압축. 소유 포인터: architecture-ddd §3.2·§3.7, architecture-db §9.7 |
| «상세 레퍼런스» | 2 | 없음 | 없음 | 불명 | «해당 절을 따른다»·«필요한 항목만 읽는다». 주제→§ 매핑 표 15행(라우팅 테이블, 문장으로 안 셈) |

SKILL.md 소계: 규범 23 · 앵커 있음 0/4 · 소유자 명시 3/4 · 백스톱 커버 0/4.

## references/final.md (70절)

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---|---|---|---|---|
| 목차 | 0 | 없음 | 없음 | 비커버 | 규범 없음 |
| §1 도입 | 1 | 있음 | 없음 | 불명 | «모든 Django 코드 작성의 기반이다» — 프레이밍이나 보수적 포함 |
| §1.1 전체 철학 | 4 | 있음 | 없음 | 불명 | 표 6행 중 의무 표지 있는 4행(Less Code·DRY·Explicit·Consistency)만 셈. Loose Coupling·Quick Development는 설명으로 제외 |
| §1.2 모델 철학 | 3 | 있음 | 없음 | 불명 | 캡슐화·메타정보 배치·자기완결 |
| §1.3 DB API 철학 | 2 | 있음 | 없음 | 불명 | «save() 명시적 호출 필요»(애매—포함)·Raw SQL 용이성 |
| §1.4 URL 설계 철학 | 3 | 있음 | 없음 | 불명 | 함수명 결합 금지·확장자 금지 등 |
| §1.5 템플릿 철학 | 2 | 있음 | 없음 | 불명 | 로직/표현 분리·기능 최소 제공 |
| §1.6 뷰 철학 | 3 | 있음 | 없음 | 불명 | 함수 우선·request 직접 전달·GET/POST 구분 |
| §2 도입 | 0 | 있음 | 없음 | 비커버 | 프레이밍 1문장뿐 |
| §2.1 포매팅 기본 규칙 | 3 | 있음 | 없음 | 불명 | black·88/79자·들여쓰기 — 전형적 린터 커버 후보이나 스크립트 지목 없음 |
| §2.2 임포트 순서 | 4 | 있음 | 없음 | 불명 | 그룹 순서·isort·편의 임포트·절대 임포트 — isort 언급은 있으나 검사기로 지목되진 않음 |
| §2.3 문자열 포매팅 | 3 | 있음 | 없음 | 불명 | 규칙이 코드 주석(«함수 호출 금지»·«연산 금지»·번역 f-string 금지)에 실림 |
| §2.4 모델 코딩 스타일 | 1 | 있음 | 없음 | 불명 | 모델 내부 정의 순서(1~7) — 규칙 전체가 코드 주석 형태 |
| §2.5 선택지(Choices) 정의 | 12 | 있음 | 명시 | 불명 | **문서 내 핵심 규칙 절**: 계층 소유(단일 출처 domain StrEnum)·TextChoices 인프라 한정·파생 전환 시점·`.value` 평탄화·소비 규율(심볼만·`==`·`is` 금지). 소유 포인터: architecture-ddd §3.2·discipline-houserules §1.1·§4·discipline-cleancode §2.14. 날짜 낙인 «2026-08-12» 인용 |
| §2.6 템플릿 코딩 스타일 | 1 | 있음 | 명시 | 불명 | 전문 위임: implementation-django-web §4 소유 |
| §2.7 뷰 코딩 스타일 | 1 | 있음 | 없음 | 불명 | «첫 매개변수 반드시 request» — 코드 주석 형태 |
| §3.1 프로젝트 레이아웃 | 4 | 있음 | 명시 | 불명 | 테스트 평면 나열 금지·조직 규칙 implementation-test §4.2 소유·표준 파일트리는 discipline-houserules 소유(배치 권위 명시). 이 절 자신은 «배경»으로 강등돼 있음 |
| §3.2 앱 분리 기준 | 3 | 있음 | 없음 | 불명 | 복수형 명명·한 문장 목적·순환 의존 재검토 |
| §3.3 설정 분리 | 2 | 있음 | 없음 | 불명 | 비밀 하드코딩 절대 금지·.env gitignore |
| §3.4 settings 접근 주의 | 1 | 있음 | 없음 | 불명 | 모듈 최상위 접근 회피 — 규칙은 좋은/나쁜 예 코드로 표현 |
| §4.1 Fat Model | 4 | 있음 | 명시 | 불명 | 인용구가 절 전체를 «평면 Django 한정»으로 조건화 + 표준 4계층에서 평면 ORM 판정 메서드 = **blocker** 선언(architecture-ddd §3.2 소유). 2000줄 기준 |
| §4.2 모델 상속 패턴 | 3 | 있음 | 없음 | 불명 | Abstract 권장·MTI 주의·Abstract+FK 우선 |
| §4.3 필드 선택 가이드 | 4 | 있음 | 명시 | 불명 | 도메인 판정 발생 시 §2.5 계층 소유로 전환(재진술)·JSONField 한정·Decimal/Float |
| §4.4 모델 유효성 검증 | 3 | 있음 | 없음 | 불명 | clean()+CheckConstraint 이중 방어·full_clean() 호출 경로 |
| §5.1 Custom Manager/QuerySet | 2 | 있음 | 없음 | 불명 | 체이닝·get_queryset 오버라이드 주의. §2.5 소비 규율 재진술이 코드 주석에 |
| §5.2 QuerySet 최적화 | 3 | 있음 | 없음 | 불명 | 관계 유형→메서드 선택 표 3행 |
| §5.3 only/defer/values | 1 | 있음 | 없음 | 불명 | 프로파일링 없이 공격적 사용 금지 |
| §5.4 annotate/aggregate | 1 | 있음 | 없음 | 불명 | 불필요 계산 필드는 alias() |
| §5.5 bulk 연산 | 1 | 있음 | 없음 | 불명 | 루프 개별 save 대신 bulk — 좋은/나쁜 예로만 표현 |
| §6 뷰 패턴 (위임) | 3 | 있음 | 명시 | 불명 | 본문 전체가 위임 문단: web §2·ninja·architecture-api 소유, 코어는 §16 경계만 |
| §7 폼과 유효성 검증 (위임) | 3 | 있음 | 명시 | 불명 | web §6 소유 + durable invariant는 model/DB 경계에서도 보장 + 도메인 규칙은 architecture-ddd |
| §8 도입 | 5 | 있음 | 없음 | 불명 | greenfield 기본 경로 = Ninja·DRF 내용은 유지보수 한정·신규 코드에 DRF 기본 권장 금지·도메인 규칙은 Django-side boundary. «API 계약 문제»의 소유 문서(architecture-api)는 문면 미지정 |
| §8.1 기존 DRF Serializer | 3 | 있음 | 없음 | 불명 | 시나리오별 분리·`__all__` 회피·공유 규칙 상향 |
| §8.2 기존 DRF ViewSet | 2 | 있음 | 없음 | 불명 | 액션별 serializer·경계 로직 model/service로 |
| §8.3 Permission 패턴 | 3 | 있음 | 없음 | 불명 | 전역 기본·레벨 오버라이드·객체 권한 위치 |
| §8.4 Pagination | 1 | 있음 | 없음 | 불명 | APIView 수동 호출 필요 |
| §8.5 기존 DRF 버전 관리 | 2 | 있음 | 없음 | 불명 | AcceptHeader 관행(애매—포함)·필드 삭제/변경은 새 버전에서만 |
| §9 도입 | 1 | 있음 | 없음 | 불명 | «올바른 사용 시나리오를 명확히 알아야 한다» |
| §9.1 시그널 사용 경우 | 5 | 있음 | 명시 | 불명 | 인용구: BC 경계 간 트리거는 signal 아닌 published_event/·event_subscription/ 소유(#89·#90) — 이슈 번호가 앵커 역할. 허용 조건 3 |
| §9.2 시그널 회피 경우 | 4 | 있음 | 없음 | 불명 | 회피 조건 3 + 코드 주석의 «커밋 전 외부 부수효과 실행 금지(§16.4 전제)» |
| §10.1 마이그레이션 기본 원칙 | 4 | 있음 | 없음 | 불명 | 4규칙 전부 코드 블록 주석 형태(작게 유지·sqlmigrate 확인·버전 관리 포함·gitignore 금지) |
| §10.2 데이터 마이그레이션 — 금지 | 6 | 있음 | 없음 | 불명 | makemigrations 산출물만·RunPython/RunSQL 손 마이그레이션 금지·backfill은 scripts/·3단계 절차. **«§11.2»·«§11.1» 인용이 문서 한정자 없이 architecture-db의 절 번호를 가리킴(자기 문서 §11과 충돌) — 표류** |
| §10.3 무중단 마이그레이션 | 3 | 있음 | 없음 | 불명 | NOT NULL 3단계·대형 테이블 분할·pg 도구 고려 |
| §10.4 이력 보존 (이주 후) | 14 | 있음 | 명시 | 커버 | **유일한 백스톱 지목 절**: `check-db-table.py`(소유는 discipline-houserules §4·db_table 존재만 검사 = 부분 커버) + `makemigrations --check`·`sqlmigrate` 결정적 검증 절차 자체 명시. label 유지·0001 불변·state-only 0002·옛 루트 삭제·historical value 리터럴 동결. WHEN은 architecture-ddd §3.2 소유로 명시 분리 |
| §11.1 N+1 탐지 | 2 | 있음 | 명시 | 불명 | query-count 테스트는 «중앙 입장 심사» add/update 뒤에만(판정 주체 명명, 문서명은 §14·§16.4에서 discipline-tdd로 특정) |
| §11.2 인덱스 전략 | 3 | 있음 | 없음 | 불명 | 프로파일링 후 추가·EXPLAIN ANALYZE. §10.2가 가리키는 «§11.2 backfill 넷»과 무관(번호 충돌의 피해자 절) |
| §11.3 update_fields | 1 | 있음 | 없음 | 불명 | 변경 필드만 — 좋은/나쁜 예 형태 |
| §11.4 exists/count | 2 | 있음 | 없음 | 불명 | exists()·count() 사용 — 좋은/나쁜 예 형태 |
| §12.1 캐싱 수준 | 0 | 있음 | 없음 | 비커버 | 3수준 설명·예시만 |
| §12.2 캐시 무효화 | 2 | 있음 | 없음 | 불명 | 캐시 적합성 선판단·운영은 Redis/Memcached |
| §13.1 내장 보안 기능 | 4 | 있음 | 없음 | 불명 | 표 «주의사항» 열에 규범 4(csrf_exempt 제한·safe 주의·보간 금지·DENY) |
| §13.2 보안 설정 체크리스트 | 3 | 있음 | 없음 | 불명 | production 설정 묶음(집계 1)+`check --deploy` 실행+CSRF_COOKIE_HTTPONLY 주의 — `manage.py check --deploy`는 결정적 검사이나 파이프라인 백스톱으로 지목된 건 아님 |
| §13.3 Raw SQL | 2 | 있음 | 없음 | 불명 | raw()·extra() 파라미터화 — 좋은/나쁜 예 형태 |
| §13.4 인증과 인가 | 0 | 있음 | 없음 | 비커버 | 예시 코드만 |
| §14 도입 | 3 | 있음 | 명시 | 불명 | discipline-tdd 입장 심사 소유 명시·framework 자체 시험 금지·승인 테스트 있을 때만 선택 |
| §14.1 TestCase 선택 기준 | 3 | 있음 | 명시 | 불명 | 선택 표(집계 1) + 인용구 «신규 add는 무조건 pytest 관용구» + 등가 매핑 출처 implementation-test §16 |
| §14.2 Factory Boy | 0 | 있음 | 없음 | 비커버 | 사용법 설명으로 판정(«~한다» 3건은 예제 해설이라 제외 — 애매) |
| §14.3 pytest-django | 2 | 있음 | 없음 | 불명 | django_db 명시·assertNumQueries는 입장된 테스트에서만(§11.1 재진술, 판정 주체 암시만) |
| §14.4 Django 공식 테스트 규칙 | 3 | 있음 | 없음 | 불명 | assertIs(x, True)·assertRaisesMessage·독스트링 서술 형식 |
| §15.1 미들웨어 실행 순서 | 1 | 있음 | 없음 | 불명 | Security 첫 번째·Session은 Auth 앞 |
| §15.2 커스텀 미들웨어 | 2 | 있음 | 없음 | 불명 | 가볍게·단일 관심사 |
| §16.1 서비스 레이어 시점 | 8 | 있음 | 없음 | 불명 | 도입 기준 bullet 5 + 판단 기준·억지 분리 금지 — 전형적 비결정(판단형) 규칙 |
| §16.2 HackSoft 패턴 | 5 | 있음 | 명시 | 불명 | `<entity>_<action>` 네이밍·심볼 소비 재진술·평면/4계층 이중 문맥 주석(architecture-ddd §3.2) |
| §16.3 DDD 트레이드오프 | 2 | 있음 | 없음 | 불명 | 모델 메서드+서비스 함수 충분·Repository는 점진 도입 |
| §16.4 트랜잭션·일관성 경계 | 28 | 있음 | 명시 | 불명 | **문서 최대 밀도 절**. atomic 경계·on_commit 정렬·sqlite select_for_update no-op·«커스텀 DB 백엔드 우회 금지(출처-불문)»·stock OPTIONS 허용 목록·risky write 체크리스트 표 6행·verification candidates의 add/reuse 판정은 discipline-tdd 소유 명시. #200(uow.after_commit)·architecture-db §9.5 인용. 코드 주석에도 규범 1 |
| §16.5 Outbox 구현 | 11 | 있음 | 명시 | 불명 | 채택 기준 architecture-ddd §3.7·전달 보장 architecture-db §9.7 라우팅·birth-enum·디스패처 자리 driving_layer/cron_job/(#58 — management/commands 금지)·at-least-once 멱등. 규범 상당수가 코드 주석·인용구에 |
| §17.1 Django 5.0 | 0 | 있음 | 없음 | 비커버 | 기능 소개만 |
| §17.2 Django 5.1 | 0 | 있음 | 없음 | 비커버 | 기능 소개만 |
| §17.3 Django 5.2 | 2 | 있음 | 명시 | 불명 | ⚠ bullet: BC 경계 ORM FK 금지 — 값 참조로(architecture-ddd §3.3 규칙3). 기능 절에 경계 규칙이 끼워져 있음 |
| 참고 자료 | 0 | 없음 | 없음 | 비커버 | 출처 목록 |

final.md 소계: 규범 223 · 앵커 있음 68/70 · 소유자 명시 16/70 · 백스톱 커버 1/70(부분).

## 4축 집계 (74절 기준)

| 축 | 집계 |
|---|---|
| ①앵커 | 있음 68 / 없음 6 (SKILL.md 4절 + 목차·참고 자료) |
| ②소유자 | 명시 19 / 없음 55 |
| ③백스톱 | 커버 1 / 비커버 8(규범 0 절) / 불명 65 |
| ④쌍둥이 | 존재 74 / 부재 0 |

## 특이 발견

1. **문서 간 § 참조 충돌(표류 확정)**: §10.2가 «Expand → Backfill → Contract(§11.1)»·«§11.2가 대형 backfill에 요구하는 넷»으로 인용하는 §11.1·§11.2는 이 문서의 §11(N+1·인덱스)이 아니라 architecture-db의 §11.1(Expand/Backfill/Contract)·§11.2(Backfill 위험)다 — grep으로 확인. 문서 한정자 없는 크로스-도큐먼트 § 인용이라 자기 문서 번호와 충돌하며, 온톨로지 도입 시 «전역 유일 규칙 ID» 필요성의 직접 증거.
2. **백스톱 거의 전무**: 246개 규범 문장 중 결정적 검사기 지목은 §10.4의 `check-db-table.py` 단 1곳이고, 그 스크립트조차 소유가 discipline-houserules §4이며 db_table «존재»만 검사(값 형태 비검사 — 부분 커버임을 문면이 스스로 명시). black·isort·`check --deploy` 같은 결정적 도구가 언급되는 절(§2.1·§2.2·§13.2)도 파이프라인 백스톱으로 연결돼 있진 않음.
3. **이중 ID 체계 혼재**: § 번호 외에 이슈/결정 번호(«#58»·«#89·#90»·«#200»)와 날짜 낙인(«2026-08-12»)이 규칙 앵커로 병용됨 — 레지스트리 등록 시 ID 정규화 대상.
4. **규범 밀도 극단 편중**: §16.4(28)·§10.4(14)·§2.5(12) 상위 3절이 전체 246문장의 약 22%. dddjango 고유 결정(빚 선언·blocker·출처-불문 금지)이 이 3절에 집중돼 있고, 나머지 다수 절은 Django 일반 지식 1~4문장.
5. **코드 주석·표 행이 규범의 1차 운반체인 절 다수**: §2.3·§2.4·§2.7·§3.4·§10.1·§13.1(표 열)·§16.4·§16.5 — 산문 문장만 추출하는 방식의 레지스트리는 이 규칙들을 통째로 놓친다.
6. **동일 규칙 다중 재진술**: Choices 심볼 소비 규율(원본 §2.5)이 §4.3·§5.1 주석·§11.2 주석·§16.2·§16.5 주석 + SKILL.md 핵심 원칙까지 6곳 이상에서 재진술됨. 단일 출처 선언은 있으나 재진술 동기화가 수동.
7. **SKILL.md에 번호 앵커 없음**: 외부 참조는 전부 final.md §N으로 가고 SKILL.md는 관례 헤딩뿐 — SKILL.md의 «핵심 운영 원칙» 12문장은 final.md 규칙의 압축 사본이라 표류 위험 지점(현재는 §2.5 등과 일치 확인).
8. **번호 안정성을 위한 위임-잔존 절**: §6·§7은 본문이 위임 1문단뿐인데 챕터 번호를 유지 — § 번호가 이미 사실상의 안정 ID로 취급되고 있다는 흔적(온톨로지 앵커 설계에 유리한 관행).
