# 로드맵 5 — 렌즈별 점검 절 목록 (BC_AUDIT · 2026-09-27)

- 정본: `dddjango/scripts/refactor_audit.py` 상수 `LENS_SECTIONS`·`SECURITY_SECTIONS`(아래와 같다 · `--self-test` 가 절 실재를 대조한다).
- 토큰 형식: `<문서 키> §<절>` — 문서 키 = 규칙 팩 `document` 에서 `dddjango/` 를 뗀 경로(두 런타임 공통 표기 · Codex 는 도구가 사상표로 푼다) · 절 = 번호 있는 제목이면 번호(`§3` = 하위 절 3.1~3.8 포함), 없으면 제목 원문.
- 리뷰어 인용 좌표도 같은 형식이다: `<문서 키> §<절> «원문 인용»`. 인용 절은 하위 절 번호(`§3.2`)로 좁혀도 된다 — 도구는 인용이 그 절 본문(하위 절 포함)에 있는지만 본다. 점검 절 목록 밖 문서를 인용해도 `check` 는 막지 않는다(목록은 읽을 범위다).
- 뽑은 방법(진단 5B §1-4 재현): 규범이 있는 절을 문서별 최상위 절로 모으고, ① 파이프라인 절차 절(입력·산출·경계·실행 모드·입장 심사)과 ② 테스트 충분성 절(설계 원칙 «리팩토링은 기존 테스트 충분 가정» — 테스트 품질·검증 방식)과 ③ 규범 0 인 절(참고 문헌·목차)을 뺐다. 서버렌더 web(implementation-django-web)은 dddjango-web 몫이라 뺐다(결정 12).

## ddd

- agents/design-review-ddd.md §점검 항목 (도메인 lens만)
- skills/architecture-ddd/references/final.md §1 · §2 · §3 · §4 · §5 · §6 · §7 · §8 · §9

## api (HTTP 어댑터가 있을 때)

- agents/design-review-api.md §점검 항목 (계약 lens만)
- skills/architecture-api/references/final.md §3 · §4 · §5 · §6 · §7 · §8 · §9 · §10 · §11 · §12 · §13 · §14
- skills/implementation-django-ninja/references/final.md §1 · §2 · §3 · §4 · §5 · §6 · §7 · §8 · §10 · §11
  - 뺌: §9 Mounted Django client와 검증(테스트 검증 방식) · §12 참고 문헌
- skills/implementation-django/references/final.md §8 (REST API 경계와 기존 DRF 유지보수)

## db (Django 모델이 있을 때)

- agents/design-review-db.md §점검 항목 (데이터 lens만)
- skills/architecture-db/references/final.md §1 · §2 · §4 · §5 · §7 · §8 · §9 · §10 · §11 · §12 · §13
  - 뺌: §3·§6(규범 0) · §14 참고 문헌
- skills/implementation-django/references/final.md §1 · §2 · §3 · §4 · §5 · §9 · §10 · §11 · §12 · §15 · §16 · §17 · §18
  - 뺌: §6 뷰 패턴·§7 폼(서버렌더 표현계층 — web 몫) · §8(api 렌즈) · §13(보안 — 아래) · §14 테스트 패턴(테스트 충분성)

## 보안 절 (db 렌즈가 켜지면 db · 아니면 api · 둘 다 꺼지면 discipline)

- skills/implementation-django/references/final.md §13

## discipline (항상)

- agents/discipline-reviewer.md §Phase 2 점검 항목 (클린코드·TDD 규율만)
  - 테스트 항목은 배치·파일·디렉터리 이름만(케이스 이름 제외 — 0T 장치가 케이스 이름 변화를 red 로 본다) · 테스트 충분성(단언 강도·보호 범위·커버리지)은 항목이 아니다.
- skills/discipline-cleancode/references/final.md §1 · §2 · §3 · §4 · §5 · §6 · §8 · §9 · §10 · §11 · §12 · §13 · §14 · §16 · §17 · §18 · §핵심 요약 체크리스트
  - 뺌: §7·§15(규범 0)
- skills/discipline-houserules/SKILL.md §1 · §2 · §3 · §4 · §5
  - 뺌: §6 패키지·의존성(프로젝트 단위 도구 선택 — BC 코드 대상 아님)
- skills/discipline-houserules/references/final.md §0 · §1 · §2 · §3 · §4 · §5
- skills/implementation-python/references/final.md §1 · §3 · §4 · §5 · §6 · §7 · §8 · §10 · §11 · §12 · §13 · §15 · §16 · §17 · §19 · §21 · §22 · §23 · §25 · §26
  - 뺌: §24 테스트(테스트 충분성) · 규범 0 인 절(§2·§9·§14·§18·§20·§27·§28·부록·출처)

## 빼기로 한 문서 (전체)

- discipline-tdd · implementation-test — 테스트 설계·품질 규범(원칙 «리팩토링은 기존 테스트 충분 가정»). 테스트 파일 배치는 houserules §1(§1.2)이 discipline 에 이미 든다.
- implementation-django-web — dddjango-web 몫(결정 12).
- 각 스킬 `SKILL.md`(houserules 제외) — references/final.md 의 요약이다.
- Coordinator·coder·architect·acceptance-tester — 파이프라인 절차 문서다.
