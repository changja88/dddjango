# T3 발주 — implementation-django-final

- 원문: `dddjango/skills/implementation-django/references/final.md` (현재 1789행 — 센서스와 일치)
- 스코프: REF 63절 · 규범 223문장 (파일럿 기이관 절 제외됨)
- 산출: `workspace/eval/t3/specs/implementation-django-final.spec.json` + `workspace/eval/t3/worksheets/implementation-django-final.md`

| section_key | 헤딩 | 센서스 행 | 규범 수 | 운반체 | 재진술 | 비고 |
|---|---|---|---|---|---|---|
| s003-1 | 1. Django 설계 철학 | 25–28 | 1 | none | N | «모든 Django 코드 작성의 기반이다» — 프레이밍이나 보수적 포함(P0 애매—포함) |
| s004-1.1 | 1.1 전체 철학 (Overall) | 29–39 | 4 | table | N | 표 6행 중 의무 표지 4행만 규범(Less Code·DRY·Explicit·Consistency) |
| s005-1.2 | 1.2 모델 철학 (Models) [DDP] | 40–45 | 3 | none | N | - |
| s006-1.3 | 1.3 데이터베이스 API 철학 (Database API) [DDP] | 46–53 | 2 | table | N | «save() 명시적 호출 필요» 애매—포함(P0) |
| s007-1.4 | 1.4 URL 설계 철학 (URL Design) [DDP] | 54–60 | 3 | none | N | - |
| s008-1.5 | 1.5 템플릿 시스템 철학 (Template System) [DDP] | 61–67 | 2 | none | N | - |
| s009-1.6 | 1.6 뷰 철학 (Views) [DDP] | 68–75 | 3 | none | N | - |
| s011-2.1 | 2.1 포매팅 기본 규칙 [DCS] | 80–85 | 3 | none | N | black·88/79자·들여쓰기 — 결정적 도구 언급 있으나 백스톱 미지목 |
| s012-2.2 | 2.2 임포트 순서 [DCS] | 86–122 | 4 | code | N | 그룹 순서 규칙은 코드 펜스가 예시 운반 |
| s013-2.3 | 2.3 문자열 포매팅 [DCS] | 123–143 | 3 | code | N | 규범 3개 전부 코드 주석에 실림(P0) |
| s014-2.4 | 2.4 모델 코딩 스타일 [DCS] | 144–178 | 1 | code | N | 모델 내부 정의 순서 1~7 — 규칙 전체가 코드 주석 형태 |
| s015-2.5 | 2.5 선택지(Choices) 정의 [DCS] | 179–223 | 12 | code | N | Choices 계층 소유 단일 출처 절(원본). 사본 6곳+(P0 발견 6) — 사본 측에 Y 표기 |
| s016-2.6 | 2.6 템플릿 코딩 스타일 [DCS] | 224–227 | 1 | none | N | 전문 위임(implementation-django-web §4) |
| s017-2.7 | 2.7 뷰 코딩 스타일 [DCS] | 228–241 | 1 | code | N | «첫 매개변수 반드시 request» — 코드 주석 형태 |
| s019-3.1 | 3.1 프로젝트 레이아웃 [TSD] | 244–290 | 4 | code | N | 트리는 코드 펜스. blockquote 2개에 소유 위임 규범(implementation-test §4.2·discipline-houserules) |
| s020-3.2 | 3.2 앱 분리 기준 [TSD] | 291–307 | 3 | code | N | - |
| s021-3.3 | 3.3 설정(Settings) 분리 [TSD] [DfP] | 308–341 | 2 | code | N | - |
| s022-3.4 | 3.4 settings 접근 시 주의사항 [DCS] | 342–362 | 1 | code | N | 규칙은 좋은/나쁜 예 코드로 표현 |
| s024-4.1 | 4.1 Fat Model, Thin View 원칙 [TSD] | 365–407 | 4 | code | N | blockquote가 절 전체를 평면 Django 한정으로 조건화+blocker 선언(architecture-ddd §3.2 소유) |
| s026 | Abstract Base Class (추상 베이스 클래스) -- 권장 | 412–431 | 1 | code | N | Abstract Base Class 권장(P0 §4.2 분배 1) |
| s027 | Multi-table Inheritance -- 주의해서 사용 | 432–446 | 2 | code | N | MTI 주의+Abstract+FK 우선(P0 §4.2 분배 2) |
| s029-4.3 | 4.3 필드 선택 가이드 [DDoc] | 469–500 | 4 | code | Y:implementation-django-final/s015-2.5 | 도메인 판정 시 §2.5 계층 소유로 전환 — P0가 재진술로 명기(발견 6) |
| s030-4.4 | 4.4 모델 유효성 검증 [DDoc] | 501–529 | 3 | code | N | - |
| s032-5.1 | 5.1 Custom Manager와 QuerySet [DDoc] [TSD] | 532–575 | 2 | code | Y:implementation-django-final/s015-2.5 | 소비 규율 재진술이 코드 주석에(P0 발견 6) |
| s033-5.2 | 5.2 QuerySet 최적화 필수 패턴 [DDoc] | 576–612 | 3 | code,table | N | 관계 유형→메서드 선택 표 3행이 규범 |
| s034-5.3 | 5.3 only(), defer(), values() [DDoc] | 613–632 | 1 | code | N | - |
| s035-5.4 | 5.4 annotate()와 aggregate() [DDoc] | 633–659 | 1 | code | N | P0는 alias() 1건만 계수(annotate/filter 순서 문장은 설명 판정) |
| s036-5.5 | 5.5 bulk 연산 [DDoc] | 660–686 | 1 | code | N | 규범이 좋은/나쁜 예로만 표현 |
| s037-6 | 6. 뷰 패턴: CBV vs FBV | 687–692 | 3 | none | N | 본문 전체가 위임 문단(web §2·ninja·architecture-api) |
| s038-7 | 7. 폼과 유효성 검증 | 693–698 | 3 | none | N | 위임+durable invariant 경계 보장 |
| s039-8 | 8. REST API 경계와 기존 DRF 유지보수 | 699–704 | 5 | none | N | greenfield 기본 경로=Ninja·DRF 유지보수 한정 — 장 도입인데 규범 밀도 높음 |
| s040-8.1 | 8.1 기존 DRF Serializer 설계 [DRF] | 705–742 | 3 | code | N | - |
| s041-8.2 | 8.2 기존 DRF ViewSet과 Router [DRF] | 743–782 | 2 | code | N | - |
| s042-8.3 | 8.3 Permission 패턴 [DRF] | 783–799 | 3 | code | N | - |
| s043-8.4 | 8.4 Pagination 설정 [DRF] | 800–818 | 1 | code | N | - |
| s044-8.5 | 8.5 기존 DRF API 버전 관리 [DRF] | 819–853 | 2 | code | N | AcceptHeader 관행 애매—포함(P0) |
| s045-9 | 9. 시그널 사용 가이드라인 | 854–857 | 1 | none | N | «올바른 사용 시나리오를 명확히 알아야 한다»(P0 §9 도입) |
| s046-9.1 | 9.1 시그널을 사용해야 하는 경우 [DDoc] | 858–882 | 5 | code | N | blockquote 인용구: BC 경계 간은 published_event/·event_subscription/ 소유(#89·#90) |
| s047-9.2 | 9.2 시그널을 피해야 하는 경우 (안티패턴) [HS] | 883–915 | 4 | code | N | 코드 주석에 §16.4 전제 규범 1 포함 |
| s049-10.1 | 10.1 기본 원칙 [DDoc] [TSD] | 918–928 | 4 | code | N | 4규칙 전부 코드 블록 주석 형태 |
| s050-10.2 | 10.2 데이터 마이그레이션 — 금지 [DDoc] | 929–947 | 6 | code | N | §11.1·§11.2 인용이 문서 한정자 없이 architecture-db 절 번호를 지시(표류 — P0 발견 1) |
| s051-10.3 | 10.3 무중단(Zero-Downtime) 마이그레이션 [DfP] | 948–972 | 3 | code | N | - |
| s052-10.4 | 10.4 이미 이주가 결정된 뒤의 마이그레이션 이력 보존 [TSD] [DfP] | 973–1048 | 14 | code | N | 유일 백스톱 지목 절(check-db-table.py — 부분 커버). historical value 동결은 §2.5 .value 평탄화와 연동(동형 원리·재진술 아님 판정) |
| s054-11.1 | 11.1 N+1 문제 탐지와 해결 [DDoc] | 1051–1074 | 2 | code | N | query-count 테스트 입장 심사 조건(원본 — 사본은 s069-14.3) |
| s055-11.2 | 11.2 데이터베이스 인덱스 전략 [DDoc] | 1075–1108 | 3 | code | Y:implementation-django-final/s015-2.5 | 코드 주석의 소비 규율 재진술(P0 발견 6). §10.2 번호 충돌의 피해자 절 |
| s056-11.3 | 11.3 save(update_fields=...) [DDoc] | 1109–1123 | 1 | code | N | 좋은/나쁜 예 형태 |
| s057-11.4 | 11.4 exists()와 count() [DDoc] | 1124–1143 | 2 | code | N | 좋은/나쁜 예 형태 |
| s060-12.2 | 12.2 캐시 무효화 패턴 [DDoc] | 1183–1204 | 2 | code | N | - |
| s062-13.1 | 13.1 Django 내장 보안 기능 [DDoc] [OWASP] | 1207–1217 | 4 | table | N | 표 «주의사항» 열이 규범 4 운반(P0 발견 5) |
| s063-13.2 | 13.2 보안 설정 체크리스트 [DDoc] [OWASP] | 1218–1246 | 3 | code | N | production 설정 묶음 집계 1+check --deploy(백스톱 미지목)+CSRF_COOKIE_HTTPONLY 주의(코드 주석) |
| s064-13.3 | 13.3 Raw SQL 안전하게 사용 [DDoc] | 1247–1262 | 2 | code | N | 좋은/나쁜 예 형태 |
| s066-14 | 14. 테스트 패턴 | 1284–1287 | 3 | none | N | discipline-tdd 입장 심사 소유 명시(P0 §14 도입) |
| s067-14.1 | 14.1 TestCase 선택 기준 [DDoc] | 1288–1311 | 3 | table,code | N | 선택 표 집계 1+blockquote «신규 add는 무조건 pytest 관용구» |
| s069-14.3 | 14.3 pytest-django 활용 [TDD] | 1358–1394 | 2 | code | Y:implementation-django-final/s054-11.1 | assertNumQueries 입장 조건 재진술(P0 명기) |
| s070-14.4 | 14.4 테스트에서의 Django 공식 규칙 [DCS] | 1395–1414 | 3 | code | N | 규칙이 코드 주석 형태 |
| s072-15.1 | 15.1 미들웨어 실행 순서 [DDoc] | 1417–1428 | 1 | code | N | 실행 순서 다이어그램은 코드 펜스 |
| s073-15.2 | 15.2 커스텀 미들웨어 작성 [DDoc] | 1429–1472 | 2 | code | N | - |
| s075-16.1 | 16.1 서비스 레이어가 필요한 시점 [TSD] [HS] [CP] | 1475–1486 | 8 | none | N | 도입 기준 bullet 5+판단 기준·억지 분리 금지 — 판단형 규칙 |
| s076-16.2 | 16.2 HackSoft 서비스/셀렉터 패턴 [HS] | 1487–1525 | 5 | code | Y:implementation-django-final/s015-2.5 | 심볼 소비 재진술+평면/4계층 이중 문맥(P0 발견 6) |
| s077-16.3 | 16.3 DDD와 Django의 트레이드오프 [CP] | 1526–1557 | 2 | code | N | - |
| s078-16.4 | 16.4 트랜잭션과 일관성 경계 [DDoc] [CP] | 1558–1601 | 28 | code,table | N | 문서 최대 밀도 절(P0 발견 4). risky write 표 6행+«출처-불문 금지»+코드 주석 규범 1(#200) |
| s079-16.5 | 16.5 트랜잭셔널 Outbox 구현 [DDoc] | 1602–1667 | 11 | code | Y:implementation-django-final/s015-2.5 | 규범 상당수가 코드 주석·인용구(#58·birth-enum). 소비 규율 재진술 주석 포함(P0 발견 6) |
| s087 | Composite Primary Key -- 복합 기본키 | 1732–1747 | 2 | code | N | ⚠ bullet: BC 경계 ORM FK 금지 — 값 참조로(architecture-ddd §3.3 규칙3). 기능 절에 경계 규범 끼임(P0 §17.3 분배 2) |
