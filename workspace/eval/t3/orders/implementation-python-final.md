# T3 발주 — implementation-python-final

- 원문: `dddjango/skills/implementation-python/references/final.md` (현재 2675행 — 센서스와 일치)
- 스코프: REF 42절 · 규범 81문장 (파일럿 기이관 절 제외됨)
- 산출: `workspace/eval/t3/specs/implementation-python-final.spec.json` + `workspace/eval/t3/worksheets/implementation-python-final.md`

| section_key | 헤딩 | 센서스 행 | 규범 수 | 운반체 | 재진술 | 비고 |
|---|---|---|---|---|---|---|
| s001 | Python 언어 특화 가이드 | 1–9 | 2 | none | Y:implementation-python-skill/s003 | 서문 정책 2(cleancode 위임+3.10+ 적극 채택) |
| s004-1.2 | 1.2 Optional과 None 처리 [단단한 파이썬] | 32–55 | 2 | code | Y:implementation-python-skill/s004 | Optional 명시+--strict-optional 강제; SKILL «X\|None»과 강도 불일치(P0 특이3); 펜스 주석 «반드시 None 체크»(P0 +1) T1 제외 |
| s005-1.3 | 1.3 Union과 합 타입으로 상태 공간 제어 [단단한 파이썬] | 56–82 | 1 | code | N | 합 타입으로 비정상 상태 배제하라 |
| s007-1.5 | 1.5 TypedDict: 이종 딕셔너리 타입 지정 [단단한 파이썬] | 103–121 | 1 | code | N | TypedDict 사용하라 |
| s013-1.11 | 1.11 Concatenate: 매개변수 추가/제거 [PEP 612] | 277–305 | 1 | code | N | Concatenate 용처 지정 서술 — 애매→포함(P0 승계) |
| s014-1.12 | 1.12 TypeIs vs TypeGuard: 타입 좁히기 [PEP 742, PEP 647] | 306–331 | 2 | code | N | TypeIs 사용하라+TypeGuard는 특수 경우만 |
| s025-3.3 | 3.3 __missing__으로 키별 디폴트 값 생성 [파이썬코딩의기술] | 515–529 | 1 | code | N | dict 상속+__missing__ 구현하라 |
| s032-4.4 | 4.4 None 반환 대신 예외 발생 [파이썬코딩의기술] | 622–642 | 1 | code | Y:전역규칙#453·#454 | dddjango 경계 단서 blockquote — OHS·승인된 failed-Result 경로는 raise 아닌 결과 분기 |
| s035-5.1 | 5.1 functools.wraps 필수 사용 [파이썬코딩의기술] [슬기로운 파이썬 트릭] | 666–688 | 1 | code | N | @wraps로 보존하라(헤딩에 «필수») |
| s037-5.3 | 5.3 클래스 데코레이터: 메타클래스 대안 [파이썬코딩의기술] | 726–744 | 1 | code | N | 메타클래스보다 클래스 데코레이터 사용하라 |
| s039-6.1 | 6.1 디스크립터 프로토콜 [파이썬코딩의기술] [파이썬 클린코드 2nd] | 747–750 | 1 | none | Y:implementation-python-skill/s004 | 재사용 애트리뷰트 로직 용처 지정 — 애매→포함(P0 승계) |
| s040-6.2 | 6.2 디스크립터 검증 프레임워크: ABC 기반 패턴 [Python 공식 Descriptor HowTo Gu | 751–825 | 2 | code | N | 의사결정 #5(External 채택)+레거시 참고 권장문(절 내 재진술) |
| s042-7.1 | 7.1 세터/게터 대신 평범한 애트리뷰트 [파이썬코딩의기술] | 828–857 | 1 | code | Y:implementation-python-skill/s004 | 평범한 애트리뷰트로 시작→필요 시 @property 전환하라 |
| s045-8.1 | 8.1 __call__로 호출 가능한 객체 [파이썬코딩의기술] | 882–898 | 1 | code | N | 상태 유지 훅은 클로저 대신 __call__ 클래스 |
| s046-8.2 | 8.2 @classmethod를 팩토리 메서드로 활용 [파이썬코딩의기술] [슬기로운 파이썬 트릭] | 899–918 | 1 | code | N | 대체 생성자는 @classmethod |
| s048-8.4 | 8.4 __repr__과 __str__ [슬기로운 파이썬 트릭] [파이썬코딩의기술] | 935–956 | 1 | code | N | 모든 클래스에 최소 __repr__ 구현하라 |
| s049-8.5 | 8.5 비공개(__) 대신 보호(_) 애트리뷰트 [파이썬코딩의기술] | 957–974 | 1 | code | N | __는 하위 클래스 충돌 방지에만 |
| s050-8.6 | 8.6 __init_subclass__로 하위 클래스 검증 (3.6+) [파이썬코딩의기술] | 975–994 | 1 | code | N | 메타클래스 대신 __init_subclass__ |
| s053-8.9 | 8.9 collections.abc로 커스텀 컨테이너 [파이썬코딩의기술] [단단한 파이썬] | 1047–1065 | 1 | code | N | collections.abc 상속 조건 서술 애매→포함(P0 승계); 펜스 주석 «dict 대신 UserDict»(P0 +1) T1 제외 |
| s061-10.1 | 10.1 Enum/StrEnum: 상수 그룹화 [단단한 파이썬] [Python 공식 문서] | 1182–1214 | 14 | code | Y:discipline-cleancode/§2.14 | P0 항 단위 계수 14 승계(다항 문장 분할); cleancode §2.14 요지 재진술+소유 지정; 고유 규범 밀집(P0 특이5) |
| s063-10.3 | 10.3 dataclass(slots=True): 메모리 최적화 (3.10+) [Python dataclas | 1231–1253 | 1 | code | N | 의사결정 #7 slots=True 권장; 주의문은 설명 |
| s070-11.1 | 11.1 연산자 오버로딩 규칙 [Fluent Python 2nd] | 1357–1425 | 3 | code | N | 핵심 규칙 bullet 3(NotImplemented 반환·__hash__ 동반 정의·@는 __matmul__) |
| s071-12 | 12. pydantic v2 -- 런타임 검증의 새 표준 | 1426–1431 | 1 | none | N | h2 헤더 blockquote 의사결정 #1(pydantic v2 API 사용) |
| s072-12.0 | 12.0 pydantic v2 boundary 결정 | 1432–1443 | 11 | none | Y:implementation-python-skill/s004 | dddjango 고유 boundary 결정 밀집 절(P0 특이5) — 경계 전용·도메인 진리값 금지 등 11 |
| s081-13.5 | 13.5 send, throw 사용 금지 [파이썬코딩의기술] | 1611–1614 | 1 | none | Y:implementation-python-skill/s004 | 금지는 헤딩·본문은 대안 지시 1(이터레이터 입력 또는 상태 클래스) |
| s089-15.2 | 15.2 최상위 예외 클래스 정의 [파이썬코딩의기술] | 1731–1749 | 1 | code | Y:implementation-python-skill/s004 | API 모듈 최상위 Exception 정의하라 |
| s090-15.3 | 15.3 @deprecated로 지원 중단 표시 (3.13+) [PEP 702] | 1750–1791 | 2 | code | N | 의사결정 #4(@deprecated)+레거시 조건 지시(3.13 미만 warnings.warn) |
| s092-16.1 | 16.1 GIL과 스레드 선택 기준 [파이썬코딩의기술] | 1794–1816 | 2 | code | Y:implementation-python-skill/s004 | 스레드=블로킹 I/O·CPU=multiprocessing; 펜스 주석 «Lock 필수»(P0 +1) T1 제외 |
| s093-16.2 | 16.2 asyncio.TaskGroup: 구조적 동시성 (3.11+) [PEP 654] | 1817–1858 | 1 | code | Y:implementation-python-skill/s004 | 의사결정 #3(TaskGroup 기본); 레거시 참고는 설명 |
| s094-16.3 | 16.3 Free-Threaded Python (3.13+) [PEP 703] | 1859–1892 | 1 | code | N | 의사결정 #2(Free-threading 반영); 현재 상태 목록은 설명 |
| s098-17 | 17. 성능 프로파일링과 최적화 | 1931–1936 | 1 | none | N | h2 헤더 blockquote 의사결정 #6(3단계 프로파일링 체계) |
| s109-19.4 | 19.4 bytes와 str 분리 (유니코드 샌드위치) [파이썬코딩의기술] | 2126–2136 | 1 | code | N | 인코딩/디코딩은 가장 먼 경계에서 수행하라 |
| s110-19.5 | 19.5 for/while 뒤 else 금지 [파이썬코딩의기술] | 2137–2140 | 1 | none | N | 루프 뒤 else 사용하지 마라 |
| s111-19.6 | 19.6 명명 규칙 [PEP 8] [슬기로운 파이썬 트릭] | 2141–2164 | 2 | table | N | 명명 표 2개=표 단위 각 1 규범(P0 방침 승계 — 행 단위 아님) |
| s112-20 | 20. 디자인 패턴 (Python 고유 구현) | 2165–2168 | 1 | none | Y:implementation-python-final/s001 | cleancode 위임 재진술(서문·SKILL과 3중) |
| s116-21 | 21. Repository / Unit of Work | 2232–2237 | 3 | none | Y:implementation-python-skill/s003 | 위임 스텁 — architecture-ddd(§5·§6)·implementation-django(§16) 소유 지정+본 문서 범위; SKILL 표 미등재(P0 특이4·6) |
| s118-22.1 | 22.1 권장 pyproject.toml 설정 | 2244–2282 | 1 | code | N | 권장 pyproject.toml 설정 블록=규범 1단위(P0 방침 승계 — 예제 아닌 구속 설정) |
| s121-23.1 | 23.1 mypy strict 모드 설정 | 2330–2354 | 1 | code | Y:implementation-python-skill/s004 | mypy strict 설정 블록=규범 1단위(P0 승계) |
| s122-23.2 | 23.2 pyright strict 모드 | 2355–2367 | 1 | code | Y:implementation-python-skill/s004 | pyright strict 설정 블록=규범 1단위(P0 승계) |
| s124-24 | 24. 테스트 | 2420–2425 | 1 | none | Y:implementation-python-skill/s003 | 위임 스텁(implementation-test 참조) — §25 존재와 긴장(P0 특이6); SKILL 표 미등재 |
| s126-25.1 | 25.1 repr 문자열 활용 | 2428–2441 | 1 | code | N | print 디버깅 시 repr 호출해야 한다 |
| s129-26.1 | 26.1 독스트링 규칙 [파이썬코딩의기술] | 2469–2493 | 6 | code | N | 대상별 독스트링 형식 4+중복 타입 서술 삭제+어노테이션 항상 유지(houserules 소유 지목) |
