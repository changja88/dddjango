# E09 센서스 — implementation-django-web + discipline-houserules

P0 온톨로지(규칙 레지스트리) 도입을 위한 규범 문장 전수 인벤토리. 담당 4파일.

집계 기준:
- 규범 문장 = 행동을 구속하는 지시·금지·조건 문장. 마침표 단위로 셈하되, **표의 행은 행당 1규범**으로 셈(위임표·검증 행렬·선택표). 설명 산문·이유 서술·예제 코드는 제외. 애매한 문장은 보수적으로 포함하고 비고에 표시.
- ④쌍둥이는 파일 단위 판정으로 절에 상속.

## 파일별 요약

| 파일 | 행수 | 절수 | 규범 문장수 | ④쌍둥이(codex판) |
|---|---|---|---|---|
| implementation-django-web/SKILL.md | 50 | 3 | 18 | 존재 — `codex-dddjango/skills/implementation-django-web/SKILL.md` |
| implementation-django-web/references/final.md | 424 | 12 | 129 | 존재 — `codex-dddjango/skills/implementation-django-web/references/final.md` |
| discipline-houserules/SKILL.md | 83 | 10 | 71 | 존재 — `codex-dddjango/skills/dddjango-discipline-houserules/SKILL.md` (**dddjango- 접두 개명**) |
| discipline-houserules/references/final.md | 242 | 15 | 58 | 존재 — `codex-dddjango/skills/dddjango-discipline-houserules/references/final.md` |
| **합계** | 799 | **40** | **276** | 4/4 존재 |

## 1. implementation-django-web/SKILL.md (3절 · 18규범)

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---|---|---|---|---|
| 언제 쓰나 | 7 | 없음 | 명시 | 불명 | 로드 조건 1 + 경계 위임 6(화살표 목록 — 동사 없는 위임 매핑을 보수적으로 규범 포함). 위임 대상 스킬명이 관할 주체 역할 |
| 핵심 운영 원칙 | 9 | 없음 | 없음 | 불명 | final.md §1~§11의 요약 사본 9줄 — 각 줄이 (§N) 참조를 달고 있으나 **§5(static)·§9(auth)는 요약에서 누락**. houserules가 금지하는 «값 복제» 형태(사본 낡음 위험) |
| 상세 레퍼런스 | 2 | 없음 | 명시 | 불명 | «final.md 해당 절을 따른다» + «필요한 항목만 읽는다». 주제↔§N 매핑표 11행은 목차라 규범으로 안 셈. 값 소유는 final.md로 명시 |

## 2. implementation-django-web/references/final.md (12절 · 129규범)

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---|---|---|---|---|
| 머리말(출처 약어 블록) | 2 | 없음 | 명시 | 불명 | 소유 위임 2문장(implementation-django 소유·api/ninja 기준을 따른다). 출처 약어 [DDoc]/[TSD] 등은 근거 표기 체계이지 규칙 ID 아님 |
| §1 책임 범위와 handoff | 12 | 있음 | 명시 | 불명 | 위임표 6행 포함. «담당한다/포함 범위» 스코프 선언 2건 보수 포함. SKILL.md «언제 쓰나»와 동일 내용 중복(6건 위임이 양쪽에 존재) |
| §2 TemplateView/CBV/FBV 선택 | 11 | 있음 | 없음 | 불명 | 선택표 5행 포함(행마다 권장+주의 지시). «적합하다» 권고 1건 보수 포함 |
| §3 Context 준비와 표시 값 | 10 | 있음 | 명시 | 불명 | «중앙 영구 테스트 입장 심사»가 판정 주체로 명시(테스트 admission). placeholder·N+1·표시값 규칙 |
| §4 Templates·base·includes | 15 | 있음 | 없음 | 불명 | 기준 3묶음(base 4·includes 4·style 5). 템플릿 책임 규칙이 §1과 중복 서술 |
| §5 Static files·CSS·JS | 10 | 있음 | 없음 | 불명 | collectstatic «실행 또는 미실행 사유 보고» — 보고 의무이지 검사기 지목 아님 |
| §6 Web forms·POST flow | 7 | 있음 | 없음 | 불명 | validation order 서술은 사실 진술로 제외. PRG·fields 명시 나열 등 |
| §7 HTMX fragment·AJAX | 6 | 있음 | 없음 | 불명 | «HTMX view는 web adapter다» 정의문 제외. ninja/api 위임 1건 |
| §8 CSRF·XSS·security setting | 12 | 있음 | 없음 | 커버 | `manage.py check --deploy` 지목 — Django 내장 결정적 검사(플러그인 check-*.py 아님). 위임 2건(implementation-django·architecture-db) |
| §9 View auth·permission | 6 | 있음 | 없음 | 불명 | permission policy 결합 시 architecture-ddd 선결정 — 부분 위임이나 절 규칙의 판정 주체는 없음 |
| §10 Render acceptance checks | 14 | 있음 | 명시 | 불명 | 검증 행렬 8행 포함. «중앙 입장 심사» 판정 주체 명시. 절 자체 규칙(정직 보고)은 기계 검사 불가 성격 |
| §11 서버렌더 에러 처리 | 24 | 있음 | 명시 | 커버 | **최대 규범 밀도 절**. 문면 스크립트 지목은 없으나 `check-transient-overmapping.py`·`check-synthetic-infra-exc.py`·`check-error-centralization.py`(scripts/ 실존)와 명백 대응. «이 절이 소유»·«view-local 몫»·«private predicate에 둔다» 소유 배분 다수. **`discipline-houserules` §2 참조가 표류 의심**(아래 특이 발견 3) |

## 3. discipline-houserules/SKILL.md (10절 · 71규범)

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---|---|---|---|---|
| 무엇이고 왜 | 7 | 없음 | 명시 | 불명 | 값/절차 소유 분리 3문장 + 경계 위임 4(화살표 목록 보수 포함). «#N 본문 정본은 저장소 정본 명세·배포본 비동봉» — 참조 해소 불가 지점 명문화(2026-08-15) |
| §1 파일트리 결정 순서 | 28 | 있음 | 명시 | 커버 | 문서 전체에서 최대 밀도 절과 동급. `check-layer-skeleton`·`scripts/registry_gate.py` 문면 지목. 판정 물음·권한 경로(G0 사용자 ⓐ 결정→슬라이스 0)·귀속 차분 게이트·관찰 축 닫힌 목록(6축). 사고 날짜 각주(2026-08-12/08-13) 3건 — 규칙에 사건 이력 내장 |
| §2 충돌 중재 | 3 | 있음 | 명시 | 불명 | final.md 단일 출처 재선언 + implementation-test §4.2 단독 소유 |
| §3 구조 결정이 빠졌다는 신호 | 7 | 있음 | 명시 | 커버 | «판정은 final.md와 검사기가 한다» 명시. 신호 6개를 규범으로 셈(진단 조건문). `check-layer-skeleton` exit 2 해석 규칙 포함 |
| §4 타입 어노테이션 | 9 | 있음 | 없음 | 불명 | «모든 이름 첫 대입, 예외 0». 문법 부재 자리 3묶음을 규범으로 셈. 문면 스크립트 지목 없음 — `check-public-surface-annotation.py` 실존하나 이름상 공개 표면 한정으로 보여 전량 규칙과 부분 대응(확인 필요) |
| §4.1 왜 전부인가 | 2 | 있음 | 명시 | 불명 | 대부분 이유 서술(제외). «백스톱과 감수자가 집행한다» 집행 주체 명시 + «다른 선택임을 숨기지 않는다» 보수 포함. mypy strict = 시그니처만 부분 커버 명문 |
| §5 코드 주석·docstring 언어 | 4 | 있음 | 없음 | 불명 | 관례 우선→없으면 한국어→혼용 금지. 관찰이 입력인 닫힌 목록의 축 ③ |
| §6 패키지·의존성 | 0 | 있음 | 없음 | 불명 | 헤더만 — 내용은 §6.1·§6.2 |
| §6.1 부트스트랩·표준 도구셋 | 1 | 있음 | 명시 | 불명 | 한 문장에 지시 3개 압축(직접 다룬다·감지 존중·ninja §2.1 규율로 셋업, 임의 글로벌 설치 금지). 관할 문서(ninja §2.1) 지정 |
| §6.2 새 런타임 의존성 버전 선택 | 10 | 있음 | 명시 | 불명 | 핀 표기·매니페스트 위치는 ninja §2.1·implementation-django 소유로 명시(값 규칙만 여기). resolve-후-핀·안정 릴리스·막힌 환경 보고 |

## 4. discipline-houserules/references/final.md (15절 · 58규범)

§2·§4는 직속 본문 없이 하위 헤딩만 있어 하위 헤딩을 절로 셈.

| 절 | 규범 문장 수 | ①앵커 | ②소유자 | ③백스톱 | 비고 |
|---|---|---|---|---|---|
| 머리말(정본 선언 블록) | 3 | 없음 | 명시 | 커버 | 정본·복제 금지·`tree_mirror_check` 동기 계약·편입 상태(2026-08-11). «#N = 트리 개정 명세 538규칙 번호» — **ID 체계 정의문**(규범으로는 안 셈) |
| 무엇이고 왜 | 1 | 있음(#492) | 명시 | 불명 | #492(트리=무엇/스킬=어떻게 채널 분리). §0에 같은 #492 재등장 — 문서 내 중복 |
| §0 제1원칙 | 12 | 있음 | 명시 | 커버 | #486~#492 + 실현 주체 coder + «위반은 `check-layer-skeleton`이 잡는다». 검사 순서 규칙(#487) 포함 |
| §1 표준 트리 — 140행 | 3 | 있음 | 명시 | 커버 | **트리 140행 자체가 규범 «값»이나 문장으로 안 셈**(행 번호가 참조 좌표계). TREE:BEGIN/END 주석 내 «손으로 고치지 않는다» 포함. `scripts/standard_tree.py` = 검사기들이 import하는 유일 데이터 |
| §2 골격 — BC 직계 일곱뿐 | 7 | 있음(#81·#82·#10·#628) | 없음 | 불명 | #81은 §0 경유로 check-layer-skeleton 대응이 명백하나 이 절 문면엔 지목 없음. #628 업무 어휘(불용어 목록 = 저장소 데이터) — `check-business-vocabulary.py` 실존(문면 비지목) |
| §2 골격 — 입구 driving_layer | 8 | 있음(#88~#92·#178) | 명시 | 불명 | «늘리는 주체는 정본 트리» 명시. #92 의존 방향 예외 4종 — import 방향 검사기 문면 비지목 |
| §2 골격 — 만들지 않는 칸 | 5 | 있음(#20·#21·#58·#187·#314) | 없음 | 불명 | 금지 칸 열거. 폐쇄 검사와 명백 대응 추정 가능하나 문면 비지목 |
| §2 골격 — migrations 생성물만 | 3 | 있음(#336~#338·#593) | 명시 | 불명 | 허용 목록(#593)은 «도구 산출물의 모양이 정한다». elidable 언급은 «덤»이라 규범 제외 |
| §2 골격 — `<project>/` | 5 | 있음(#429·#430·#432·#436) | 명시 | 불명 | celery.py는 명문 조건부 항목(«#491 조건부 없음»과의 관계를 문면이 직접 방어 — 관할 분리 선언). #436 면제 목록 |
| §3 명명 | 3 | 있음 | 명시 | **비커버** | «권장 — 기계 검사기 없음·reviewer 점검» **명시적 비커버 선언은 4파일 중 유일**. 단 `check-naming.py`가 scripts/에 실존 — 문면과의 대응 확인 필요(표류 의심). 명명 전수는 매핑표 순서 편입 예정(자리표시 상태) |
| §4 이관 — 종료 기록 | 2 | 있음(#81·#490·#324 참조) | 명시 | 커버 | «검사기는 옛 이름을 더 알아보지 않는다» — 검사기 행동 계약. 옛 이름 재등장 = 트리 밖 칸 위반으로 흡수 |
| §4 이관 — brownfield 빚 | 3 | 있음(§4 경유) | 명시 | 커버 | «백스톱이 내는 위반이 곧 리팩터링 대상»(총칭 지목). 미루기는 사용자 승인 + `.dddjango/` 기록 |
| §4 이관 — 검사기 가드 계약 | 1 | 있음(#74) | 명시 | 커버 | 채택 신호 2+원 있는데 대상 0건이면 exit 2 — 조용 무동작 방지 가드 |
| §4 이관 — 규칙 개정 이행 순서 | 1 | 있음(#72) | 없음 | 불명 | 플러그인 셋(검사 스크립트·리뷰어 지침·표준 문서) 한 커밋 선행 → 코드 후행 |
| 배경 | 1 | 없음 | 없음 | 불명 | 파생 출처 서술(제외) + «이 문서는 값만 싣는다» 문서 범위 규정 1건 보수 포함. 결정 카드 57장은 저장소 정본 소재 |

## 4축 집계 (절 40 기준)

| 축 | 집계 |
|---|---|
| ①앵커 | 있음 33 / 없음 7 |
| ②소유자 | 명시 25 / 없음 15 |
| ③백스톱 | 커버 10 / 비커버 1 / 불명 29 |
| ④쌍둥이 | 존재 40 / 없음 0 |

## 특이 발견

1. **이중 ID 체계가 이미 존재하나 한쪽 문서군에만 있다.** houserules final.md는 무접두 `#N`(538규칙 설계 명세 번호) + «트리 N행» 행 좌표계라는 두 층의 안정 앵커를 이미 운용 중 — 온톨로지 레지스트리가 그대로 승계 가능한 기존 자산. 반면 web final.md는 §N 절 번호뿐이고 규칙 단위 ID가 없어(출처 약어 [DDoc] 등은 근거 표기이지 ID 아님) 두 문서군의 앵커 해상도가 비대칭이다.
2. **#N 규칙 «본문» 정본은 플러그인 배포본에 동봉되지 않는다**(houserules SKILL.md 무엇이고 왜, 2026-08-15 명문) — 배포본만 가진 소비자는 #N 참조를 해소할 수 없다. 레지스트리 도입 시 참조 해소 경로 설계가 필요한 지점.
3. **깨진(표류 의심) 상호 참조**: web final.md §11 «계산된 transient는 도메인 마커 타입으로 … (`discipline-houserules` §2)» — houserules SKILL.md §2는 «충돌 중재»(트리 택일 금지), references/final.md §2는 «골격 규칙»으로, 어느 쪽도 transient 마커·협력 포트 선언과 무관하다. 참조 대상이 개정 전 판을 가리키는 표류로 보인다.
4. **금지된 «값 복제»를 web SKILL.md가 하고 있다**: houserules는 «값을 SKILL.md에 복제하지 않는다»를 강제하지만, web SKILL.md «핵심 운영 원칙»은 final.md 규칙의 요약 사본 9줄이고 그마저 §5·§9를 누락했다(요약 커버리지 구멍 + 사본 낡음 위험의 실례). #492(채널 분리)도 hr final.md 안에서 두 번 등장(무엇이고 왜 + §0).
5. **문면-검사기 연결이 전반적으로 끊겨 있다**: 백스톱 불명이 29/40절. 실제 `dddjango/scripts/`에는 check-*.py 30여 개와 `checker_registry.py`(레지스트리 인프라)가 실존하며, 이름상 §11(check-transient-overmapping·check-synthetic-infra-exc), §4 타입(check-public-surface-annotation), #628(check-business-vocabulary), §3 명명(check-naming)과 대응돼 보이나 문서 문면이 지목하는 것은 `check-layer-skeleton`·`registry_gate.py`·`tree_mirror_check` 정도뿐이다. 특히 §3 명명은 «기계 검사기 없음»이라 쓰는데 check-naming.py가 존재한다 — 규칙↔검사기 매핑이 온톨로지의 1차 채움 대상.
6. **codex 쌍둥이의 비대칭 개명**: codex판은 `dddjango-discipline-houserules`로 접두 개명됐으나 `implementation-django-web`은 원명 유지 — 쌍둥이 대응표를 이름 규칙만으로 유도할 수 없다.
7. **hr final.md는 «편입 중» 문서다**(2026-08-11 첫 배포판): 층·칸별 상세 규칙·명명 전수가 매핑표(rule-owner-map) 순서로 편입 예정이라 §3 명명 등이 자리표시 상태 — 센서스 수치가 곧 늘어날 절이 예고돼 있다. 또 §1의 규칙 문면에 사고 이력(2026-08-12 라운드 1·08-13 라운드 2)이 각주로 내장된 독특한 서술 형식.
