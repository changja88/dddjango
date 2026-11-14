# 리팩토링 판 B — 여러 BC 운영 화면의 자리 · 단순한 admin · 시험 재료 자리(설계 v1)

상태: v2 — 독립 검토 둘(검사기 · 도구 / 글 · 그래프 · 트리 · 문서) 반영(v1 · 2026-11-14 `date` 19:38) · 좁은 재확인 둘 반영(v2 · `date` 20:03 — 처분 §15 끝 «v2 처분») · 사용자 결정 «빚 범위 = 다른 빚과 같이(가)» 반영(v3 · `date` 20:10) · 셋째 좁은 확인 둘 반영(v3) · 코드 변경 0. 판 A(같은 폴더 `design.md` v3.1)와 한 판 **2.38.0** 으로 묶는다(사용자 결정). 처분 목록은 §15.

- 출발: 사용자 결정 셋(2026-11-14 · 판 A 설계 §7 · §8 끝 결정 줄).
  - F4-159 «좋아 그럼 cross_context로 하자.» — 최상위 `cross_context/backoffice/` · web 길 없음.
  - F4-158 «규칙으로하자.» — admin 은 자기 BC 도메인 · 응용을 import 하지 않는다(검사기) · 규칙 걸린 쓰기는 자기 창구.
  - F4-175 «그렇게 하자.» — `fake/<선언>_<변형>.py` + `factories/` 만드는 함수 · 새 서랍 없음.
- 후보 셋(F4-178 · F4-177 · F4-174)은 재현한 뒤 넣을지 정했다(§4 ~ §6).
- 재현 판: 배포판 2.37.0(설치본 사본) · 작업 트리(판 A 반영 · 미커밋) · 리허설 클론 `workspace/scratch/refactor-rehearsal-1114/api`(읽기만 · 판 A 와 같은 클론).
  - 모든 검사기 실행은 `DJR_VIOLATIONS_DIR=<scratch 폴더>` 를 붙인다 — 클론에 설치 표식 `.dddjango/` 가 있어 붙이지 않으면 클론 `.dddjango/violations/` 에 기록이 생긴다(검토 m8 · v0 실행이 남긴 48 개는 §14).
- 작업 자리: `workspace/scratch/pan-b-cross-context/`(git 무시) — 손볼 자리 지도 `touchpoints.md` · `f159/` · `f158/` · `f175/` · `f177/` · `f178/` · 검토 `review-checkers/` · `review-text/`.
- 공개 기록 표기: 현장 BC 는 공용 이름표(scratch `bc-label-map.md` · 판 A 기록과 같은 표)로 적고, 현장 파일 · 심볼 · 줄은 일반 말로 적는다. 플러그인 경로 · 줄 · 규칙 번호 · 이 저장소 SHA 는 그대로다.
- 장부: 읽은 때 마지막 번호 F4-178 · 마지막 덧붙임 = F4-178 «처분 갱신(발주자)». 계획 확정 때 다시 읽는다(DEVELOPMENT §7.3 의 8).

## 0. 요약

### 사용자에게 바뀌는 것

- 여러 BC 값을 한 화면에 보이는 Django admin 화면은 저장소 루트 `cross_context/backoffice/` 에 산다.
  - 각 BC 창구(`driving_layer/open_host_service/`)만 부르고 식별자로 맞춘다. BC 는 이 칸을 모른다.
  - 그래서 이런 화면이 BC 순환을 만들지 않는다 — 클론 모의에서 순환 둘(계정 BC ↔ 이용 정책 BC · 캐릭터 BC ↔ 판촉 BC)이 0 이 된다(§1 «클론 재측정»).
  - 이 칸은 모델 · 날 SQL 을 두지 않고, 화면 주소는 모두 admin 로그인 뒤에 선다.
- BC admin 은 ORM · 폼 · 화면만 갖는다(F4-158).
  - 자기 BC 의 도메인 · 응용 · 합성 루트 · 저장 어댑터 · ACL 을 import 하면(자기 모델 모듈을 거쳐 다시 가져와도) 검사기가 막는다.
  - DB 로 걸 수 없는 규칙이 걸린 쓰기는 그 BC 창구를 부른다.
  - 옛 admin 의 빚은 다른 빚과 같다 — 기능 · 수정 실행 G0 에서 미룰 수 있고, 리팩토링은 늘 고친다(사용자 결정 · §2 «빚 범위»).
- #188 이 이름 다른 창구 · 사건 구독 · cron · webhook 이 부르는 영역을 입구로 센다(손님 API 있는 BC 범위 그대로 — 넓힘은 다음 판 후보).
- 시험 재료 — `fake/<선언>_<변형>.py`(선언 상속 · 기본 가짜와 나란히)와 `factories/` 의 `make_` 로 시작하는 만드는 함수를 받는다.
- 경로 앞 응답 정본이 흔한 ruff 기본(C901 10 · `ruff format` 줄 88)을 지난다. 옛 판 정본을 이미 옮긴 저장소도 그대로 통과한다. 문서는 «코드는 그대로 · 서식 · 주석 · import 차례는 프로젝트 도구 몫» 으로 검사기와 맞춘다(F4-178).
- #195 가 같은 BC 도메인 서비스에 한 번 넘겨 그 안에서 루트 메서드를 부른 애그리거트를 막지 않는다. 지금 잡던 «조회 정책을 부른 뒤 유스케이스가 필드를 직접 바꿈» 은 그대로 잡는다(F4-177).
- F4-174 는 2.34.0 에서 이미 고쳐졌다 — 수리 없음.

### 비용(어림 · §11)

| 갈래 | 크기 | 무엇 |
|---|---|---|
| 트리 172 ~ 182행(생성기 · 정본 · 미러 · 명세) | M | `mkrev2.py` 11행 · `file_tree.html` · `tree_mirror_check` 상수 · `spec_lint` 상수 · 명세 · 소유 지도 |
| 그래프 · 투영 · 미러 글 | L | 새 규범 7(R-3753 ~ R-3759) · 새 Expression 26 + 판 A Expression 고침 1(R-3625) · 문서 11 재투영 · 새 절 하나(§6 · `s019-6`) · LEDGER · 계수표 · rulepack · Codex 같은 뜻(§8 표) |
| 검사기(cross_context) | M | layer-skeleton · app-container · context-isolation · public-surface 넷 |
| 검사기(F4-158 · #188) | M | context-isolation 새 함수(다섯 자리 + 다시 내보내기 한 겹 · 파일당 한 줄) · usecase-dto-placement(범위 그대로 · 짝 넓힘) · composition-root #101 부칙 · 픽스처 9 레인 문구만 |
| 검사기(F4-175 · F4-177) | M | port-adapter-pairing · test-config · transaction-boundary(한 홉) |
| 정본 · 검사기(F4-178) | M | 새 정본 · 옛 판 자산 · 검사기 두 줄 · 고정 자리 열 안팎 · 그래프 리비전 셋 |
| refactor_audit | S | `_dddjango_run` 보류 · 경로 필터 줄(판 A 파일 · §1) · RD 사례 넷 |
| 시험 · 픽스처 · 변이 · 골든 | M | 픽스처 폴더 7 안팎 · 변이 40 안팎 · 함께 고치는 시험 파일 셋은 운영자가 모아 넣음 |
| 문서 | S | README · `docs/master/` · DEVELOPMENT · 요청 가이드 바뀔 것 없음 |
| 합 | L 판 하나 | v0 보다 줄었다(#188 넓힘 걷음 · F4-177 한 홉 · #668 파일당 한 줄) · 그래프 몫은 늘었다(리비전을 블록마다 셈) |
| (플러그인 밖) 대상 코드 이관 | L | 정지 · 판촉 화면 이전(기능 · 수정 실행 둘) · #668 빚 61 파일 — §9 |

### 사용자 질문

- **하나(답함 · 20:10)** — #668 의 옛 빚을 어디서 셀까(§2 «빚 범위»). 사용자 «우선은 다른 것들처럼 미룰수 있게 해야 할거 같아. 그런데 리팩토링때는 수리를 해야 하니깐 리팩토링 기능에도 들어가야해» = 다른 빚과 같이(운영자가 물은 «가») — 기능 · 수정 실행 G0 에서 미룰 수 있고, 리팩토링은 늘 고친다. (물음 차례: v1 의 «나» 는 «고치는 파일도 막는다» 였고 상시 미룸 결정(F4-84)과 부딪쳐 v2 에서 빚 질문으로 고쳐 다시 물었다.)
- 그 밖은 0 — touchpoints §8 물음 17 은 모두 «설계 처리» 다(§1). 후보 셋의 갈래와 검토 지적 처분도 규칙 목적 · 이미 있는 장치 · 사용자 결정에서 나온다(§15).
- 계획 승인 때 알릴 것(묻지 않음 · 이의 시 뒤집음)은 §12.

### 항목 표

| # | 항목 | 2.37.0 재현 | 처리 | 판 |
|---|---|---|---|---|
| 1 | F4-159 여러 BC admin 화면 | #450 2줄 · deps 순환 둘(«지원 안 함») · 빈 칸에 두면 app-container 붉음 | 트리 172 ~ 182행 · #664 ~ #667 · 검사기 넷 · refactor_audit 두 줄 | B |
| 2 | F4-158 admin 단순 · #188 | #188 8줄 · admin 자기 BC import 검사 없음 · #101 이 admin → 자기 창구를 막음 | #668 · #101 부칙 · #188 짝 넓힘 — 클론 #188 8 → 6 · #668 61 파일(61줄) · 빚 = 다른 빚과 같이(사용자 결정) | B |
| 3 | F4-175 시험 재료 | 변형 이름 #576 · 만드는 함수 #392 · 클론 #576 1줄 | #576 가장 긴 앞머리 변형 · #577 변형 상속 대조 · #392 정의마다 | B |
| 4 | F4-174 BC `test/conftest.py` | 재현 안 됨 — 2.33.0 에서만 · 2.34.0 에서 고쳐짐 | 수리 없음 · 글 세 곳에 부칙 한 구절(덤) | 장부만 |
| 5 | F4-178 경로 앞 응답 정본 ruff | C901 `_project_rows` 12 > 10 · format 두 곳(줄 130) · 줄 88 은 수십 곳 | 새 정본(최대 복잡도 6 · format 0) · 옛 판 자산도 받음 · 문서 «코드 그대로 · 서식 · 주석은 프로젝트 몫» | B |
| 6 | F4-177 #195 도메인 서비스 넘김 | 장난감 31 사례 모두 위반 · 현장 꼴 a | 같은 BC 도메인 서비스 한 홉을 따라가 «받음» · 지역 필드 대입이 있으면 셈하지 않음 | B |

## 1. F4-159 — 여러 BC 값을 보이는 Django admin 화면 → `cross_context/backoffice/`

### 결정(사용자 · 고정)

- 최상위 `cross_context/backoffice/` — 장고 앱 하나(`cross_context.backoffice`) · 모델 없음.
- 파일: `apps.py` · `urls.py` · `<screen>/panel.py` · `<screen>/form/<form>_form.py` · `<screen>/feature/<feature>.py` · `templates/admin/backoffice/<page>.html` · `test/integration/`.
- 나가는 import 는 각 BC 의 `driving_layer/open_host_service/` 뿐 · `application/` 에서 들어오는 import 0 · 업무 판정 0.
- BC 사이 업무 판정(예: 로그인 정지 확인)은 지금처럼 ACL → OHS.
- web 길은 사용자가 뺐다. 이름 `cross_context` 는 판정 물음(«이 코드는 BC 둘 이상의 값을 함께 쓰나?»)을 이름에 담으려고 골랐다.

### 재현(2.37.0 · 클론 · 장난감)

- 클론 #450 2줄 — 계정 BC · 이용 정책 BC «서로의 `anticorruption_layer/` 에 들어 있다».
- 클론 deps(판 A v1.3 기록) — «순환 성분(운영): 계정 BC · 이용 정책 BC — 지원 안 함(순환 묶음 · 묶음 계획을 먼저)».
- 클론 deps 그래프(작업 트리 `DepsScan` · `f159/deps_edges.py`) — 크기 2 이상 성분 둘. 간선은 방향마다 파일 하나다.

  | 방향 | 파일(하나) | 갈래 |
  |---|---|---|
  | 계정 BC → 이용 정책 BC | 계정 BC 의 로그인 정지 ACL 어댑터 | `ohs_acl` — 로그인 정지 판정(남김) |
  | 이용 정책 BC → 계정 BC | 이용 정책 BC 의 손님 찾기 ACL 어댑터 | `ohs_acl` — 정지 화면의 닉네임 찾기 · 읽기 |
  | 캐릭터 BC → 판촉 BC | 캐릭터 BC 의 할인 ACL 어댑터 | `ohs_acl` — 할인 판정(남김) |
  | 판촉 BC → 캐릭터 BC | 판촉 BC 의 admin 변경 폼 템플릿 | HTTP(브라우저가 상대 운영자 API 를 부름) |

  - 둘째 순환은 #450 에 안 보인다(ACL 쌍이 아님). 같은 템플릿은 두 BC(BC-다 · BC-나)의 API 도 부른다(순환은 아님 · `f159/admin_cross.out`).
- 빈 칸 장난감(`f159/toy-cc/good` — 표준 BC 하나 + 결정대로 지은 `cross_context/backoffice/`):
  - 2.37.0 check-app-container exit 2 — «Django 앱이 `application/` 밖 평면에 있다».
  - 2.37.0 check-layer-skeleton · check-context-isolation exit 0 — `cross_context/` 를 아예 안 본다(나쁜 장난감도 0).
- 간접 사례(F4-158 과 겹침 · `f159/admin_acl_builders.out`): BC admin 파일 15 · BC 6 이 자기 유스케이스를 거쳐 다른 BC ACL 을 쓴다. 순환은 위 둘뿐이다.

### 원인

- 트리에 «BC 둘 이상의 값을 한 화면에 모으는» 자리가 없다. core 의 BC 사이 통로는 ACL(창구 부르기)과 `published_event` 둘뿐이고, admin 은 «자기 앱의 모델을 안다»(houserules §5) 하나다.
- 그래서 Django admin 이전이 운영 화면을 BC 안으로 옮길 때마다 반대 방향 ACL(또는 브라우저 HTTP)이 생긴다.
- 조사 보고(`workspace/scratch/admin-cycle-research-1114/reports/`)의 결론과 같다 — 문헌은 «여러 BC 값 합성은 BC 위의 조립자» 로 한결같다. 조회 의존을 순환 셈에서 빼 주는 원전은 없다.
- 2.37.0 검사기에서 이 칸을 두면:
  - `check-app-container.py:244` 의 후보 루프가 `cross_context/backoffice`(`__init__.py` + `apps.py`)를 «`application/` 밖 장고 앱» 으로 잡는다(`:91-112` 후보 · `:150-184` 새 앱 = 이번 작업 · `:206-221` 이주 짝 없음).
  - `check-layer-skeleton.py:907-956` 은 BC · `framework/` · `<project>/` 셋만 본다 — 칸 폐쇄 · 고정 칸이 서지 않는다.
  - `check-context-isolation.py` `main` 은 `application/` 만 훑는다 — `cross_context/` 의 import 도, BC → `cross_context` import 도 안 본다.

### 자매 플러그인과 대조(CLAUDE.md «상대 플러그인의 같은 자리를 먼저»)

| | dddjango-web(`undecidable.md` §3 · tie-break 2) | dddjango(이 판) |
|---|---|---|
| 여러 BC 를 그리는 화면 | 그 화면 이름의 «일반 BC» — 도메인이 비어도 표준 골격 그대로 | BC 가 아닌 루트 칸 `cross_context/backoffice/` |
| BC 의 뜻 | 화면 · 기능 단위(표현계층) | 업무 경계의 이름(#82) |
| 칸 하나의 값 | web 골격 | BC 골격(직계 일곱 · 고정 칸 수십) + 상대 BC 마다 ACL(어댑터 다섯 역할 폴더) |
| 다른 BC 를 부르는 길 | in-process api_client(HTTP 계약) | 각 BC 창구 import(같은 프로세스 함수) |
| 도메인 | 가져도 된다(허용) | 업무 판정 0(금지 · #667) |

- 옮기지 않는 까닭(기록):
  - **사용자가 골랐다** — 운영자가 «후보 1 최상위 칸 · 후보 2 `application/` 아래 운영 콘솔 BC(web 꼴)» 를 함께 보였고 사용자가 루트 쪽을 골랐다(«좋아 그럼 cross_context로 하자.»).
  - core BC 는 업무 경계다(#82). 운영 화면 묶음은 업무 경계가 아니라 행위자 묶음이다.
  - 화면마다 BC 를 세우면 골격 + 상대 BC 마다 ACL 이 든다. 정지 화면 하나에 ACL 둘이다. 모델 없는 BC 에 changelist 를 붙이려면 프록시 모델이 든다.
- 기준 수준: #667(업무 판정 0)은 web 일반 BC(도메인 허용)보다 **엄격하다** — 이 몫은 사용자 결정(«업무 판정 0»)에서 온다. 그 밖(«다른 BC 내부를 모른다» · 파일 수)은 web 과 같은 수준이거나 가볍다(골격 없음).

### 고칠 설계

#### 트리 172 ~ 182행(끝에 붙임 — 기존 1 ~ 171행 번호 무변)

| 행 | 깊이 | 이름 | 칸 | 한 줄 |
|---|---|---|---|---|
| 172 | 0 | `cross_context/` | 고정 | BC 둘 이상의 값을 함께 쓰는 합성 칸들의 뿌리 · BC 밖 · BC 위 |
| 173 | 1 | `backoffice/` | 고정 | 운영자 화면(Django admin) 합성 · 장고 앱 `cross_context.backoffice` |
| 174 | 2 | `apps.py` | 고정 | 앱 등록 · label `backoffice` · 모델 없음 |
| 175 | 2 | `urls.py` | 고정 | 화면 주소 묶음 · 화면마다 `admin.site.admin_view` 로 감싼다 |
| 176 | 2 | `<screen>/` | 자리표시자 | 운영자 화면 하나(예: `suspension/`) |
| 177 | 3 | `panel.py` | 고정 | 화면 입구 — 주소 · 권한 · 기능으로 넘기기만 |
| 178 | 3 | `form/<form>_form.py` | 자리표시자 | 입력 폼 — 값의 모양만 |
| 179 | 3 | `feature/<feature>.py` | 자리표시자 | 한 기능 — 각 BC 창구를 따로 부르고 식별자로 맞춤 · 창구 예외를 화면 알림으로 |
| 180 | 2 | `templates/admin/backoffice/<page>.html` | 자리표시자 | admin 화면 템플릿(평평하게 — 화면별 하위 폴더 없음) |
| 181 | 2 | `test/` | 고정 | 이 칸의 시험 |
| 182 | 3 | `integration/` | 고정 | 화면 시험 — Django client 로 admin 주소를 열고 각 BC 는 진짜 |

- 행 설명 · 이름 · 파트 글(goal · inn · out · why)은 미리보기 `workspace/scratch/backoffice-tree-preview/patch.py` 의 글에서 옮긴다. 옮길 때:
  - «제안» 표지(칩 `prop` · 글 머리 `PROP`)는 걷고 칩은 `framework/` 행처럼 «신설» · `fix` 로 둔다. `file_tree.html` `<style>` 손편집(`.chg.prop` · 172 ~ 182행 색)은 하지 않는다. 파트 `sub` 의 «· 제안» 과 `why` 끝 dim 줄(«판 B 제안 …»)도 걷는다.
  - 공개 문서이므로 현장 BC 이름 · 현장 순환 예시를 빼고 일반 예(«정지 화면 — 손님 닉네임은 계정 쪽 BC, 정지는 정책 쪽 BC» 같은 뜻 낱말)로 쓴다.
  - 미리보기의 «세부는 설계 때 정한다» 두 곳(`urls.py` 메뉴 · 시험 재료)은 아래 물음 4 · 13 의 답으로 바꾼다.
- 칸 유형은 `tree_mirror_check` 가 낸다 — 장난감 파이프라인에서 손으로 적은 행과 같다(`f159/pipeline/` · `--write` 뒤 `--check` 0).
- 승격(data-sw) · 묶음(data-grp) 표기 없음 · 결정 카드 신설 없음(물음 15).

#### 규칙 글(새 규범 — 명세 #664 ~ #667 · 그래프 houserules 새 절 «§6 `cross_context/` — BC 밖 합성 칸»)

- **#664** — `cross_context/**` 가 `application/` 에서 import 하는 것은 각 BC 의 `driving_layer/open_host_service/` 아래(창구 서비스 함수 · 계약 · 창구 예외)뿐이다. BC 의 모델 · 유스케이스 · 도메인 · `composition_root/` · `test/` 를 import 하면 위반이다(`from application import <bc>` 꼴도). `get_model()` 로 모델을 꺼내도, 시험 밖에서 `get_user_model()` 을 불러도 위반이다. 이 칸은 모델 클래스(`models.Model` 을 잇는 클래스 — `managed = False` 도 · 별칭이나 프로젝트 추상 기저를 거쳐도 · 안 `Meta` 에 `db_table` · `managed` · `proxy` 가 있는 클래스도)를 정의하지 않고 날 SQL 길(`django.db` 의 `connection` · `connections` · `RawSQL` · DB 드라이버 모듈의 import · `.raw(` · `.extra(`)을 쓰지 않는다 — 값은 그 BC 창구로만 읽는다. 상대 import 가 `cross_context/` 밖에 닿아도 위반이다.
  - 자리 `트리 172~182행` · `ast` · principle · blocker · 집행 check-context-isolation.
- **#665** — `application/**` · `framework/**` · `<project>/**` 는 `cross_context` 를 import 하지 않는다 — BC 와 framework 는 이 칸을 모르고, `<project>/urls.py` 는 `include("cross_context.backoffice.urls")` 문자열로만 넣는다(`INSTALLED_APPS` 문자열도 import 가 아니다). `<project>/` 파일의 문자열 상수 가운데 `cross_context.` 로 시작하는 것은 `include(…)` 안의 `"cross_context.backoffice.urls"` 와 `INSTALLED_APPS` 의 앱 문자열(`cross_context.backoffice` · 그 `apps` 모듈의 설정 클래스)만 받는다 — 다른 문자열(`include("cross_context.….feature.…")` · ninja `add_router(…, "cross_context.….router")`)은 위반이다(재확인 N4). 그래서 이 칸은 BC 순환 셈(#450 · 리팩토링 deps)에 들지 않고, 화면이 `admin_view` 를 비켜 프로젝트 주소에 바로 붙지 않는다.
  - 자리 `트리 172행` · `ast` · principle · blocker · 집행 check-context-isolation.
- **#666** — `cross_context/backoffice/urls.py` 의 모든 `path(…)` · `re_path(…)` 호출(`urlpatterns` 대입 · `+` · `+=` · `.append` · `.extend` · 따로 둔 목록 어디서든)은 둘째 인자가 `admin.site.admin_view(…)` 호출이다 — admin 로그인 · 권한을 그대로 쓴다. 아니면 위반이다(`include(…)` 도 — 화면은 이 파일에 바로 적는다). `cross_context/**` 에서 이 파일 밖의 `path(…)` · `re_path(…)` · ninja `Router(…)` 호출도 위반이다 — 주소는 이 파일 하나에만 적는다(재확인 N4).
  - 자리 `트리 175행` · `ast` · principle · blocker · 집행 check-context-isolation.
  - 까닭: 감싸지 않으면 다른 BC 값(닉네임 등)을 보이는 화면이 로그인 없이 열린다. 결정의 «Django admin 화면» 에서 나온다(질문 생략 · 설계 처리).
- **#667** — `cross_context/` 는 업무 판정을 하지 않는다 — 각 BC 창구를 따로 부르고 식별자로 맞춰 보이기만 한다. 판정(예: 정지를 걸어도 되나 · 무엇이 지금 정지인가)은 그 BC 창구가 하고, 창구가 던지는 `<service>_published_error` 는 `feature/` 가 화면 알림으로 옮긴다. 한 BC 값만 보이는 화면은 그 BC 의 `driven_layer/django_<bounded_context>/admin/` 에 둔다. BC 사이 업무 판정은 지금처럼 ACL → OHS 다.
  - 자리 `트리 172·176~179행` · `human` · principle · blocker(명세 #657 과 같은 꼴) · 감수 discipline-reviewer(설계 쪽은 design-review-ddd).
- 명세 «자리» 열은 `트리 172~182행` 처럼 **띄우지 않고** 쓴다 — `spec_lint._expand_row_refs` 는 «172 ~ 182» 를 끝 두 행으로만 읽어 ③ 커버리지가 붉다(검토 실측).

#### 규칙 글(고침 — 리비전)

| 자리 | 지금 | 바꿈 | 정본(블록 · Norm) |
|---|---|---|---|
| houserules §0 #490 | «`framework/`·`<project>/` 는 이 원칙의 주어가 아니다» | 뒤에 «`cross_context/**` 는 주어다(트리 172~182행) — `<screen>/` 안은 `panel.py` · `form/` · `feature/` 뿐이고, 템플릿은 `templates/admin/backoffice/` 바로 아래 평평하게, `test/integration/` 안은 pytest 가 이름을 소유한다» | s003-0/b5 · R-3185 리비전 · 명세 #490 행 |
| houserules §1 제목 | «§1 표준 트리 — 171행» | «182행» | s004-1 `headingSnapshot`(Expression 없음 · 선례 4cd1999f) |
| houserules §1 TREE 블록 | 171행 | 182행(`tree_mirror_check --write` 가 쓴 글 그대로) | s004-1/b3 글(kind-code · Norm 없음) |
| houserules §1 «읽는 법» 최상위 | «최상위는 셋이다 — …» | «최상위는 넷이다 — … · `cross_context/`(BC 둘 이상의 값을 함께 쓰는 합성 — 그런 화면이 생길 때 만든다. `framework/` 처럼 있을 때 그 아래 칸을 본다)» | s004-1/b5 · R-3191 리비전(prefLabel «최상위는 넷뿐») |
| houserules §1 «읽는 법» 시험 재료 | (없음) | F4-175 두 줄(§3) | s004-1/b7 · 새 R-3758 · R-3759(R-3740 옆) |
| houserules §2 #658 | «시험은 주인의 표준 시험 자리(BC `test/` · 전역 규칙은 `framework/test/unit/`)» | «… · 여러 BC 화면은 `cross_context/backoffice/test/integration/`)» | s008/b5 · R-3716 리비전 |
| houserules §5 admin 줄 | «`django_<bounded_context>/admin/` — admin 은 자기 앱의 모델을 안다» | 뒤에 #668 문장(§2) · «여러 BC 값을 보이는 화면은 `cross_context/backoffice/`(§6)» | s018-5/b1 · 새 R-3757(R-3423 무변) |
| houserules 새 §6 | — | #664 ~ #667 | 새 절 `s019-6` · 새 R-3753 ~ R-3756 |
| houserules SKILL «§1 트리 171행» | 171 | 182 | s004-1/b2 · R-3112 리비전 |
| houserules SKILL 시험 자리 | «BC test/ 자식 · 전역 규칙은 framework/test/unit/» | «… · 여러 BC 화면은 `cross_context/backoffice/test/integration/`» | s004-1/b3 · R-3125 리비전 |
| architecture-ddd §3.2 항-(2) | «루트 평면 `<app>/` 은 #486·#490 위반» | 뒤에 «예외는 하나 — 모델 없는 운영자 화면 합성 앱 `cross_context/backoffice`(`discipline-houserules` `references/final.md` §1 트리 172~182행 · §6)» — SKILL.md 에 이미 `## §6 패키지·의존성` 이 있어 맨 «houserules §6» 으로 적지 않는다(글 재확인 N4) | s017-3.2/b9 · R-0122 리비전 |
| architecture-ddd §3.2 항-(3) | «컨텍스트 간 접근은 ACL·OHS 로만» | 뒤에 «BC 밖 합성 칸 `cross_context/` 는 BC 가 아니라 ACL 을 두지 않고 각 BC 의 OHS 만 부른다(#664)» | s017-3.2/b9 · R-0124 리비전(clarification) |
| implementation-django §18 머리 | admin 자리 하나 | 자리 둘(BC admin · `cross_context/backoffice/`) + 표기는 같다 · 새 자리는 «`discipline-houserules` `references/final.md` §6» 으로 가리키고, 이름표의 «houserules §4·§6.1»(SKILL 쪽)은 그대로 둔다(N4) | s094-18/b1 · R-3460 리비전 |
| implementation-test pytest 예시 | `testpaths = ["application"]` | `testpaths = ["application", "cross_context"]` 와 주석 «`cross_context/` 를 두는 저장소» | s021-4.1/b2 코드 글(Norm 없음) |

#### 검사기

- **check-layer-skeleton**(#488 · #490 — 판 A 밖 파일)
  - 새 함수 `_check_cross_context(cc_dir, out, cand)` — `cross_context/__init__.py` 부재는 #488, 그 아래는 기존 `_check_level(cc_dir, 172행, {}, out, cand)` 를 그대로 건다.
  - `main` 은 `target/"cross_context"` 가 있을 때만 부른다(`framework/` 와 같은 판 · `:948`). 채택 신호(#74 가드)에는 넣지 않는다.
  - `backoffice/` 아래 `static/` · `templatetags/` · `management/` 같은 폴더는 `<screen>/` 으로 읽혀 «`panel.py` 부재(177행)» 로 난다 — 막는 것은 맞으니 #490 글에 «`backoffice/` 의 폴더는 화면뿐» 한 마디를 붙인다(검토 덧붙임).
  - docstring «171행» → «182행» · #490 항에 `cross_context/` 한 마디.
- **check-app-container**(R-0122 — 판 A 밖 파일)
  - `:244` 후보 루프 첫 줄 — 후보가 저장소 상대 `cross_context/backoffice` 이고 `models.py` · `models/` · `migrations/` 가 모두 없으면 건너뛴다.
  - 모델 표지가 하나라도 있으면 «`cross_context/backoffice` 는 모델 없는 앱이다 — 모델 · 마이그레이션은 그 BC 의 `django_<bc>/` 에 둔다» 한 줄(blocker · 건드림 여부 무관).
  - `cross_context/` 아래 다른 앱(예: `cross_context/reporting/apps.py`)은 지금처럼 붉고, layer-skeleton #490 도 함께 잡는다. 파일 없이 클래스로 둔 모델은 #664 가 잡는다.
- **check-context-isolation**(#664 · #665 · #666 — 판 A 파일 · 판 A 가 고친 `_WindowTry` · `_check_acl` 묶음과 안 겹침)
  - 새 함수 `_check_cross_context(target, out)` 하나를 `main` 의 `_check_project_registration(target, findings)` 바로 뒤에서 부른다. `_scan_imports` 는 손대지 않는다(admin · 합성 루트를 `:333` 에서 건너뛰므로 #665 는 따로 훑는다).
  - #665 — `application/**` · `framework/**` · `<project>/`(기존 `_find_project_pkg`)의 모든 `.py`(admin · 합성 루트 포함 · 함수 안 import 포함)에서 첫 마디가 `cross_context` 인 절대 import · `<project>/` 의 `cross_context.` 로 시작하는 문자열 상수 가운데 받는 꼴 밖의 것(재확인 N4) — 받는 꼴은 `include(…)` 첫 인자(문자열이거나 튜플의 첫 칸)의 `"cross_context.backoffice.urls"` 와, 설정 모듈(`settings.py` · `settings/**`) 어디에 있든 값이 앱 문자열 둘(`cross_context.backoffice` · 그 `apps` 모듈의 설정 클래스 경로)과 같은 문자열이다 — 자리로 가리지 않는다(`LOCAL_APPS` 로 나눈 목록 · 다른 설정 파일의 `+=` · `LOGGING` 의 로거 이름을 받음 · 셋째 확인).
  - #664 — `cross_context/**` 의 `.py` 에서 첫 마디가 `application` 인 import 는 `application.<bc>.driving_layer.open_host_service…` 꼴만 받는다 · `get_model()` 호출 · 시험 밖 `get_user_model()` 호출 · 모델 클래스 정의(밑 클래스의 import 출처를 풀어 `django.db.models.Model` 에 닿거나 · 프로젝트 안 기저 클래스를 한 번 따라가 거기 닿거나 · 안 `Meta` 에 `db_table` · `managed` · `proxy` 대입이 있음 — 재확인 N5) · 날 SQL 길(`django.db` 에서 `connection` · `connections` 를, `django.db.models.expressions` · `django.db.models` 에서 `RawSQL` 을 가져오는 import · DB 드라이버 모듈(`sqlite3` · `psycopg` · `psycopg2` · `MySQLdb` · `pymysql` · `cx_Oracle` · `oracledb`) import · `.raw(` · `.extra(` 호출 — 이름 `cursor()` 대조는 걷는다 · 재확인 N6 · N7) · `cross_context/` 밖으로 나가는 상대 import.
  - #666 — `cross_context/backoffice/urls.py` 의 AST 전체에서 `path(…)` · `re_path(…)` 호출마다 둘째 인자(또는 `view=`)가 `….admin_view(…)` 호출인지 · 그 밖 `cross_context/**` 의 `path(…)` · `re_path(…)` · `Router(…)` 호출은 바로 위반(재확인 N4).
  - docstring «타 BC» 절에 세 줄.
- **check-public-surface-annotation**(#646 · #647 · #650 — 판 A 밖 파일)
  - `:175` `RULE_ROOTS = {"application", "framework", "cross_context"}`. BC admin 과 같은 타입 규율이 이 칸에 선다(시험 본문 갈래 `:1703` 도 같은 집합을 쓴다 · 검토가 제품 · 시험 파일 모두 #647 이 새로 섬을 확인).
- 걸지 않는 것(설계 처리 · 한계로 적음):
  - check-naming admin 가족(#340 ~ #348) — 판 A 가 고친 `_admin_dirs` 를 다시 건드리지 않는다. 이름 · 자리는 폐쇄(#490)와 트리 행이 이미 고정한다. 남는 #345(기능 하나 = 파일 하나)는 감수 물음으로 둔다.
  - check-test-config(#383 ~ #392) — `cross_context/backoffice/test/` 의 자식은 폐쇄가 `integration/` 하나로 닫는다. #389(integration 은 진짜 DB)는 안 건다 — 시험 재료 import 는 #664 가 막는다(물음 13).
  - check-business-vocabulary #46 — framework → `cross_context` 는 #665 가 잡으므로 #46 문면은 그대로.
- 검사기 수는 27 그대로다(물음 5).

#### refactor_audit · folder_group

- deps 그래프 — 고칠 것 없음.
  - `DepsScan._owner` 는 `application/` 밖 파일을 `@<첫 마디>` 주인으로 짓고, `emit` 은 그 참조를 `surface_in` 으로 싣는다. `adjacency` 는 BC ↔ BC 간선만 세고 HTTP 도 주인이 BC 일 때만 센다.
  - 그래서 `cross_context` 파일은 BC 마디가 아니고 순환에 들지 않는다(모의 · 검토 재측정으로 확인).
  - 레인 경로에는 이미 든다 — 제품 파일은 «공유 표면», 시험은 «받는 쪽 시험»(창구 모듈 import), 템플릿이 BC API 를 부르면 «HTTP 소비자»(`_lane_paths_of`).
- 명세의 «다른 BC 편집» 줄 — `_other_edits` 는 경로 꼴을 가리지 않는다. `cross_context/…` 줄은 갈래 «공유 표면» 으로 적으면 deps 와 맞는다(설계자 글 한 줄 · §8).
- **바꿀 것 하나 — `_dddjango_run` 의 보류 · 경로 필터 줄(판 A 파일)**
  - 지금: 실행의 BC 를 실행 줄 · «대상 BC 경로 필터» 줄 · 명세 file-plan 의 `application/<bc>/` 로만 모은다. `cross_context/` 만 쓰는 기능 실행은 BC 가 비어 «대상 BC 를 모른다» 보류가 된다 — 그 실행이 도는 동안 다른 모든 레인의 deps 가 보류로 멈춘다(`cmd_deps` 의 `maybe` 가 BC 없으면 참).
  - 바꿈: 경로 필터 줄의 `cross_context/…` 조각과 file-plan 의 `cross_context/` 경로를 `run.paths` 에 넣고, BC 가 비어도 `run.paths` 에 `cross_context/` 가 있으면 보류를 걸지 않는다. 겹침은 경로 교집합(`_path_hit` — 접두 포함)이 가른다.
  - 판 A 는 이 함수에서 두 자리(`_line_marked` · `run.line_g0`)를 고쳤다. 판 B 는 보류 줄과 경로 필터 줄만 고치고, 판 A 커밋 뒤 함수 이름으로 자리를 찾아 건다(줄 번호는 밀렸다).
  - 시험(RD 사례 넷): `cross_context/` 만 쓰는 실행(겹침 없음 → 보류 없음 · exit 0) · 같은 화면 파일을 함께 쓰는 리팩토링 레인(겹침 → exit 2) · 명세 `boundary-imports` 에 소비할 BC 창구를 적은 `cross_context/` 실행(그 BC 레인에서 «계획된 소비» 겹침) · G1 전(명세 없음) `cross_context/` 실행(보류 없음 · 겹침 못 봄 — 한계로 고정). 변이: 보류 예외 지움(첫 사례가 보류로 돌아감).
  - 한계: G1 전 `cross_context/` 실행은 명세가 없어 소비할 창구를 모른다 — 그 동안은 경로 겹침만 보인다. 실행이 창구를 쓰기 시작하면 명세 · 경로로 드러난다.
- folder_group — 고칠 것 없음. 새 트리 낱말 `backoffice` 가 묶음 금지어에 들어간다. 클론 25 BC `draft --summary` 출력이 트리 행 추가 앞뒤로 byte 같다(`f159/fg-wt.out` · `fg-tree.out`).

### touchpoints §8 물음 17 답

| # | 물음 | 답 | 처리 |
|---|---|---|---|
| 1 | `cross_context/` 는 고정 칸인가 · 모든 저장소에 있어야 하나 | 고정 이름 칸(172행)이지만 «있을 때 본다». 최상위 칸의 존재는 #488 의 주어가 아니다 — `framework/` 와 같은 판(`check-layer-skeleton.py:948`). 있으면 그 아래 고정 칸(173 · 174 · 175 · 181 · 182행)은 #488 로 반드시 있다 | 설계 처리 — 결정 «여러 BC 값 화면은 여기» 와 framework 선례 |
| 2 | 아래는 #490 폐쇄의 주어인가 · `<screen>/` 안 재량 | 주어다. `<screen>/` 안은 `panel.py` · `form/` · `feature/` 뿐(BC admin `<entity>/` 와 같음) · 템플릿은 평평하게 · `test/integration/` 안은 pytest 소유. 재량이 없어야 이 칸이 «두 BC 를 쓰는 아무 코드» 서랍이 되지 않는다 | 설계 처리 — 이름을 판정 물음으로 고른 결정의 뜻 |
| 3 | app-container 예외의 술어 | 둘 다 — 저장소 상대 `cross_context/backoffice` ∧ `models.py` · `models/` · `migrations/` 없음. 파일 없는 모델 클래스 · 날 SQL 은 #664 | 설계 처리 — 결정 «모델 없음» |
| 4 | 모델 없이 주소 · 메뉴 · #431 | `urls.py` 에 `app_name = "backoffice"` 와 화면마다 `path("<screen>/", admin.site.admin_view(<Screen>Panel.as_view()), name="<screen>")`. `<project>/urls.py` 가 `path("admin/backoffice/", include("cross_context.backoffice.urls"))` 를 `admin/` 줄 앞에 한 번 둔다. 문자열 등록이라 #430 · #431(import 부작용 등록 금지) · #433(`application.` 문자열만 봄) 어느 것에도 안 걸린다(`_check_project_rule_lists` · `_check_project_registration` 읽음 · 검토 장난감 27종 출력 무변). `<project>/` 가 화면 클래스를 import 해 바로 붙이면 #665. admin 첫 화면 목록에는 안 뜬다 — Django admin 목록은 등록 모델만 그린다. 화면은 `reverse("backoffice:<screen>")` 링크로 연다(클론은 운영자 메뉴가 이미 admin 밖 뿌리 처리기에서 admin 주소로 보낸다). 목록 덮어쓰기 템플릿(`admin/app_list.html`)은 사용자가 정한 파일 목록 밖이라 두지 않는다 | 설계 처리 · 이의 시 뒤집음 — 알릴 것 ① |
| 5 | 새 검사기냐 기존 검사기냐 | 기존 넷(layer-skeleton · app-container · context-isolation · public-surface). 27종 글이 조정자 · 스킬 · README · 그래프 여러 곳에 있어 28종은 글 비용이 크다 | 설계 처리 |
| 6 | BC admin 규칙 · 타입 · 시험 규칙을 걸까 | 타입(#646 · #647 · #650)은 건다(`RULE_ROOTS`). 이름(#340 ~ #348)은 폐쇄 · 트리 행이 대신하고 #345 는 감수(판 A 파일 재편집 피함). 시험(#383 ~ #392)은 폐쇄 · #664 가 대신한다 | 설계 처리 — 한계 기록 |
| 7 | 창구 예외 처리 의무(#473 같은) | 규칙 글 #667 에 둔다(`feature/` 가 창구 예외를 화면 알림으로) · 기계 검사 없음 · 감수. 놓치면 500 화면이라 해는 화면에 머문다 | 설계 처리 |
| 8 | «업무 판정 0» 기계 신호 | 간접 — #664 가 도메인 · 유스케이스 import · 모델 · 날 SQL 을 막아 판정 코드와 남의 표에 닿을 길이 없다. 남는 몫(파이썬으로 판정을 다시 짜기)은 #667 감수 물음 | 설계 처리 |
| 9 | `framework/` → `cross_context` 를 막나 | 막는다(#665) — framework 는 업무를 모른다(#46 와 같은 뜻) | 설계 처리 |
| 10 | deps 에서 «공유 표면» 그대로인가 | 그대로(도구 변경 0). 모의에서 정지 화면 기능 파일은 계정 BC · 이용 정책 BC 레인 경로의 «공유 표면» 으로 든다. 설계자 글에 «`cross_context/` 파일은 `공유 표면`(시험은 `받는 쪽 시험`)» 한 줄 | 설계 처리 |
| 11 | `cross_context/` 만 쓰는 실행의 G0 스캔 범위 · 다른 레인 보류 | 스캔 범위 = 손대는 BC + 그 실행이 파일을 쓰면 `cross_context/`. 빚 목록 경로 필터에 `cross_context/` 를 더한다(조정자 Phase 0 3번 · R-0194). 보류는 refactor_audit 두 줄로 없앤다(위) | 설계 처리 |
| 12 | 리팩토링 모드 대상이 되나 | 아니다(이 판) — `<영역>` 은 `application/` 아래 그대로. `cross_context/` 의 빚은 그 칸을 쓰는 기능 · 수정 실행이 갚는다. BC 리팩토링 레인은 «공유 표면» 으로 그 파일을 함께 고친다 | 설계 처리 |
| 13 | 시험 재료 자리 · `testpaths` | #385(BC 시험은 그 BC 것만 — 다른 BC 내부를 import 하지 않음)의 뜻을 따른다: 다른 BC 데이터는 그 BC 의 제품 입구(HTTP · admin 화면)나 창구(OHS) · 플랫폼 API(`get_user_model()` — 시험 안만)로 만든다. BC `test/` · 모델 import 는 #664 가 막는다. 재료는 시험 파일 안(F4-175 결정) · 공용 고정물은 `test/integration/conftest.py`(pytest 소유 자리). 프로젝트 `testpaths` 에 `cross_context` 를 더한다(옮긴 시험이 수집 밖이면 behavior_guard 가 이미 붉힌다 — `behavior_guard.py:1234`) | 설계 처리 — 플러그인 규정(#385)에서 · 현장 시험도 다른 BC 준비를 그 BC 제품 입구로 하는 관례가 있다(발주자 쪽 · 규정 아님) |
| 14 | 앱 label · 템플릿 셋째 마디 | label `backoffice` — 템플릿 `templates/admin/backoffice/` 와 맞는다(#348 의 뜻). BC 이름이 `backoffice` 면 Django 가 시작 때 label 겹침으로 멈춘다(소리 나는 실패 · 검사 없음) | 설계 처리 |
| 15 | 승격 · 묶음 표기 · 결정 카드 D61 | 표기 없음(BC admin 85 ~ 87행에도 없음 · `GROUPABLE_ROWS` 는 고정 리터럴). D61 없음 — `mkrev2.py` 가 다시 쓰는 결정 기록 파일은 CLAUDE.md 가 되돌리라고 정했다. 근거는 파트 «why» 글과 이 설계 · 판 기록에 둔다. `spec_lint` `LIVE_CARDS` · «58장» 무변 | 설계 처리 |
| 16 | 그래프 TREE 블록과 `tree_mirror_check --write` 순서 | `--write` 먼저 → 그 블록 글을 그래프 b3 에 옮김 → 게이트 → 렌더 → final.md 가 `--write` 결과와 byte 같은지 대조(§7) | 설계 처리 |
| 17 | 자매 플러그인 대조 | 위 «자매 플러그인과 대조» — 첫 까닭은 사용자 선택 · #667 은 web 보다 엄격(사용자 결정) | 설계 처리 — 기록 |

### 시험(DEVELOPMENT §3 체크리스트 8)

- 픽스처(장난감 `f159/toy-cc/` · 검토 장난감 `review-checkers/toys/cc-*` 를 줄여 옮김):
  - `skeleton/good_cross`(결정대로 지은 칸 · 0) · `skeleton/bad_cross`(#488 `apps.py` · `__init__.py` 없음 · #490 `utils.py` · `<screen>/helpers.py` · `models.py` · `cross_context/reporting/` · `backoffice/static/`).
  - `app_container/` — 통과 사례 `cross_context/backoffice`(모델 0) · 붉음 사례 둘(같은 자리에 `models.py` · 위장 이름 `cross_context/back_office/apps.py`).
  - `context_isolation/cross_good` · `cross_bad`:
    - #664 — 응용 · driven · 합성 루트 · `from application import <bc>` · `get_model` · 시험 밖 `get_user_model` · 시험의 BC 시험 재료 import · 밖으로 나가는 상대 import · `managed = False` 모델 클래스 · `connection.cursor()` · 프로젝트 추상 기저를 잇는 `Meta.db_table` 클래스 · `Model as M` · `connection.chunked_cursor()` · `RawSQL as R` · 드라이버 import(재확인 N5 · N6).
    - #665 — BC 도메인 · admin · 합성 루트 · framework · `<project>/urls.py` 의 화면 클래스 import · `<project>/` 의 `include("cross_context.….feature.…")` · `add_router(…, "cross_context.….router")` 문자열(N4).
    - #666 — 맨 뷰 · `include` · `+` · `+=` · `.append` · `.extend` · 따로 둔 목록 · `backoffice/urls.py` 밖의 `path` · ninja `Router`(N4).
    - 통과 — 창구 서비스 · 계약 · 예외 import · 시험 안 `get_user_model` · `<project>/urls.py` 의 `include("cross_context.backoffice.urls")` 문자열 · `INSTALLED_APPS` 문자열 · 창구가 준 페이지 값의 `page.cursor()`(N7 오탐 없음).
  - public-surface — `cross_context/` 제품 · 시험 파일에 #647 차단 한 줄씩(뿌리 넣기 확인).
- 변이(모두 붉어야 함): layer-skeleton `cross_context` 부르기 지움(bad_cross 가 0) · app-container 모델 표지 대조 지움 · app-container 자리 대조를 이름 끝으로 넓힘(위장 이름이 통과) · #664 창구 꼴 대조를 `driving_layer` 까지로 넓힘 · #664 `get_model` 지움 · #664 모델 클래스 지움 · #664 날 SQL 지움 · #665 framework 훑기 지움 · #665 `<project>` 훑기 지움 · #665 함수 안 import 를 안 봄 · #666 `urlpatterns` 대입만 봄(`+=` 사례가 통과) · #666 감쌈 대조 지움 · `RULE_ROOTS` 에서 뺌 · #664 모델 판정을 밑 이름 `Model` 하나로 좁힘(추상 기저 사례 통과) · #664 드라이버 · `connection` import 대조 지움 · #665 문자열 상수 훑기 지움 · #666 을 `urls.py` 한 파일만 봄(밖 `path` 통과).
- 골든 · EXPECTED: 새 픽스처는 하위 폴더 · 기존 `bad_rules`/`good` 무변이면 `findings_count_matrix` · `checker_baseline_matrix` 는 다시 낼 것이 없다(구현 때 `--scripts-dir` 대조로 확인). `checker_cross_matrix --emit-expected` · `construct_drift_report --emit-expected` · `gen_pregate_symbol_kinds` 는 검사기 파일 지문이 바뀌므로 다시 낸다.
- Codex byte 미러 넷(layer-skeleton · app-container · context-isolation · public-surface).

### 시제품 · 장난감(`f159/scripts-cc1/` = 작업 트리 사본 + 트리 172 ~ 182행 + `f159/patch_cc.py` + v1 고침)

| 장난감 | 판 | app-container | layer-skeleton | context-isolation |
|---|---|---|---|---|
| good(결정대로 지은 칸) | 2.37.0 | **2** «`application/` 밖 평면» | 0 | 0 |
| good | 시제품 | 0 | 0 | 0 |
| bad(아래 꼴 모음) | 2.37.0 | 2(모델 있는 앱) | 2(BC · framework 몫만) | **0** |
| bad | 시제품 | 2 «모델 없는 앱이다» | 2 · cross_context 몫 #488 1 · #490 4 | 2 · #664 5 · #665 2 |
| bad666(good + 맨 뷰 · `include`) | 시제품 | 0 | 0 | 2 · #666 2 |
| 검토 cc-imp(`+` · `+=` · `.append` · `.extend` · 따로 둔 목록 · `<project>` 직접 연결 · 시험의 BC 재료 · `get_model`) | v0 시제품 → v1 | — | — | #666 0 → **4** · #665 1 → **2** · #664 2 → 2 |
| 검토 cc-model(`managed = False` 모델 · `connection.cursor()`) | v0 → v1 | — | — | #664 0 → **2** |
| 검토 cc-proj(`INSTALLED_APPS` · `include` 문자열) | v1 | — | — | 0 |

- bad 의 꼴: `backoffice/utils.py` · `backoffice/models.py` · `<screen>/helpers.py`(#490) · `cross_context/reporting/`(#490 «트리에 없는 칸») · `apps.py` 없음(#488) · 기능 파일이 응용 · driven · 합성 루트 · `from application import orders` 를 import(#664 넷) · `apps.get_model()`(#664) · 도메인 파일 · framework 파일의 `cross_context` import(#665 둘).
- v0 시제품 검사기 27종을 good 장난감에 모두 돌렸다 — `cross_context` 를 짚는 줄 0(창구 import 가 #13 · #652 등 다른 규칙에 걸리지 않음).

### 클론 재측정(읽기만)

- 트리 행만 더한 판(`scripts-tree` — `standard_tree.py` 에 172 ~ 182행)으로 검사기 27종을 클론 루트에서 돌렸다 — exit 와 출력이 작업 트리 사본과 **27종 모두 byte 같다**(`f159/tree-effect/` · 검토가 81 실행으로 다시 확인). `cross_context/` 가 없는 저장소에는 새 행의 효과가 0 이다.
- 시제품 v1(`scripts-cc1`)도 클론에서 context-isolation 출력이 작업 트리 사본과 같다(새 줄 0 · #665 0).
- 순환 모의(`f159/deps_sim.py` — `DepsScan` 결과를 메모리에서만 바꿈):
  - 정지 화면 이동 — 이용 정책 BC 의 계정 BC ACL 폴더 참조 7 을 지운다(화면이 계정 BC 창구를 직접 부름).
  - 판촉 화면 이동 — 템플릿 HTTP 소비 3 의 주인을 `cross_context/…` 로 바꾼다.
  - 새 화면 파일의 창구 참조 넷을 `surface_in` 으로 더한다.
  - 결과: 크기 2 이상 성분 **2 → 0**. 남는 BC 간선(로그인 정지 · 할인 판정 ACL)은 한 방향이다(검토가 지금 작업 트리 `refactor_audit` 로 다시 확인).
  - 레인 경로: 계정 BC · 이용 정책 BC · 판촉 BC 레인에 새 기능 파일이 «공유 표면» 으로, 캐릭터 BC 레인에 «공유 표면» + 템플릿 «HTTP 소비자» 로 든다.

### 남는 한계

- 템플릿이 BC API 를 브라우저로 부르는 것은 import 가 아니라 #664 가 못 본다. deps 는 «HTTP 소비자» 로 세지만 순환은 만들지 않는다. 규칙 글은 «값은 창구로» 라 감수가 본다.
- #664 는 동적 길(`importlib.import_module("application.…")` · `apps.get_app_config(…).get_models()` · `ContentType…model_class()`)을 못 본다 — 일부러 비켜 가는 꼴이라 감수 몫이다(검토 덧붙임).
- 업무 판정 0 · 창구 예외 처리 · 기능 하나 = 파일 하나는 감수 물음이다(#667).
- admin 첫 화면 목록에 이 칸의 화면이 안 뜬다 — 링크로 연다(물음 4).
- `cross_context/` 의 빚은 리팩토링 모드로 갚지 못한다(물음 12).

### 버린 갈래

- dddjango-web 처럼 화면마다 일반 BC — 사용자가 루트 안을 골랐다(위 대조표).
- 운영자 읽기 간선을 순환 셈에서 빼기 · 사건 사본 · 의존 역전 — 조사 보고가 근거 없음 또는 비용 큼으로 접었다(판 A §8 추천 «나» 철회).
- 새 검사기 `check-cross-context.py` — 27종 글 비용.
- `cross_context/` 를 BC 처럼 deps 마디로 세기 — 마디가 되면 «받는 쪽» 으로 순서를 잡아야 하고 이 칸의 «BC 가 모름» 이 흐려진다. 레인 경로 셈만으로 충분하다(모의).

## 2. F4-158 — admin 은 ORM · 폼 · 화면만 · #188 짝 넓힘

### 결정(사용자 · 고정)

- admin(`driven_layer/django_<bc>/admin/`)은 자기 BC 의 `domain_layer` · `application_layer` 를 import 하지 않는다 — 검사기로.
- 일반 데이터(읽기 · 모델 필드나 DB 제약이 규칙을 지는 값)는 ORM 으로 바로.
- DB 제약으로 못 거는 업무 규칙이 걸린 쓰기는 그 BC 의 `open_host_service` 로 — 규칙은 창구 뒤 한 곳에 남고, cross_context 와 같은 부름 꼴이다.
- #188 은 그 영역을 import 하는 event_subscription · cron_job · webhook · 창구(이름 무관)를 입구 짝으로 받는다. admin 만 부르는 영역은 «admin ORM 또는 그 BC 창구» 를 가리키는 문구로 알린다.
- 사용자 목표 «admin은 단순해야 좋을거 같아».
- (출처 바로잡음) v0 가 이 목록에 둔 «손님 API 있는 BC 에서만 도는 것도 고친다» 는 사용자 결정이 아니다 — 결정 기억에 없고, 명세 #188 의 «REST 표면이 없는 BC 는 검사하지 않는다» 는 F4-86 때 검사기 동작을 적은 글이다. v1 은 이 판에서 넓히지 않는다(아래 «#188» · 운영자 판단).

### 재현(2.37.0 · 클론 · `f158/`)

- #188 — 클론 exit 2 · 188줄(G0 기록과 byte 같음) · #188 8줄(영역 8). 작업 트리 판도 같다(판 A 밖 파일).
- 원인 — `check-usecase-dto-placement.py`:
  - `:316` `if api is not None and _has_concrete_api_surface(...)` — API 표면이 없는 BC 는 #188 을 아예 안 본다.
  - `:318-326` 짝은 같은 이름 폴더 둘(`api/<area>` · `open_host_service/<area>`)뿐 · 반대 방향 `:327-328`.
- 표준 트리의 입구 칸(`standard_tree.py:51-81`): r9 `api/` · r12 `api/<area>/` · r17 `api/webhook/` · r18 `<provider>/`(webhook 은 driving 직계가 아니라 `api/` 아래) · r23 `open_host_service/` · r24 `<service>/` · r34 `cron_job/` · r36 `event_subscription/`.
- #188 문면은 산문이다 — 명세 `tree-revision-spec.md:517`(등급 `path`) · 트리 글 `mkrev2.py:1043`(WHAT 40) · `:1681` · `:1651`(NAMES). 그래프에는 조정자 예시 한 곳(s006/b9 → `commands/dddjango.md:147` «path 등급이라 filtered 불가» 목록의 «#188 area 1:1»)뿐이다.
- admin 의 자기 BC import — 지금 검사가 없다. `check-context-isolation.py:173-174` 가 admin 칸을 `django` 로 가르고 `_scan_imports` `:333-334` 가 바로 돌아온다. db-table 도 admin 을 뺀다(`check-db-table.py:276` · #327).
  - 같은 까닭으로 admin → **다른 BC** import 도 검사가 없다(클론 0 파일). 트리 글 `mkrev2.py:374` 는 «타 BC 금지는 그대로 걸린다» 라 적지만 기계가 안 지킨다 — 결함(시제품 픽스처로 재현).
- admin → 자기 창구를 **막는** 규칙이 있다 — #101 `check-composition-root.py:2682-2710` `_check_inner_driving_imports`(`_INNER_SEGMENTS` `:1852` 에 `driven_layer`). 시제품 픽스처에서 #101 이 났다(검토 재현). 결정을 따르려면 이 규칙에 부칙이 든다(판 A 밖 파일).

### 영역 8(클론 · 누가 부르나 · admin 이 하는 일)

| 영역 | 부르는 곳 | admin 일 | DB 가 규칙을 지나 | 갈래 |
|---|---|---|---|---|
| BC-차 대화 요약 설정 | admin 1 | 읽기 · 쓰기 | 시작 값 ≥ 1 은 CHECK · 지시 글 본문은 BC-바 값 | cross_context 화면(두 BC) |
| BC-라 설문 목록 | admin 1 | 쓰기 · 목록 · 폼에 BC-카 카드 폼 이름 | 아니오 — 설문의 카드 폼 맞춤(다른 BC 스키마 적합) · 고칠 때 보기 코드를 못 지움(앞 상태 비교) | 창구로 + cross_context 화면(카드 이름) |
| 판촉 BC 일반 판촉 | admin 2 | 쓰기 | 아니오 — 여러 줄 겹침 판정 | 창구로 + cross_context(결정) |
| 판촉 BC 가입 보너스 | admin + 사건 구독 | 읽기 · 쓰기 · 미리보기 | 예(CHECK) · 미리보기는 도메인 판정 | 이미 다른 입구 · 쓰기 ORM · 미리보기 창구 읽기 |
| BC-아 공지 작성 | admin 2 | 쓰기 · 지우기 | 거의 · «빈칸만» 금지는 regex CHECK 로 걸 수 있음 | ORM 으로(CHECK 하나 보강) |
| 이용 정책 BC 정지 | admin(빌더 7) + 이름 다른 창구 둘 | 읽기 · 쓰기 · 손님 닉네임은 계정 BC | 아니오 — 잠금 · 기간 · 같은 종류 정지 끝내기 | 이미 다른 입구 + cross_context 화면 |
| 이용 정책 BC 이용 한도 | admin 1 | 읽기 · 쓰기 | **예** — 하루 횟수 ≥ 1 CHECK | ORM 으로 |
| BC-사 추천 질문 작성 | admin 3 | 읽기 · 쓰기 · 미리보기 | 일부 — «목록 차례 = 시작 날짜 정렬»(여러 줄 규칙) · 미리보기는 도메인 판정 | 창구로 |

- 입구가 영역에 닿는 길은 모두 «직접 import + 빌더» 였다(창구 47 · 구독 6 · webhook 4 · 빌더만 0 · `f158/entrance_reach.txt`).
- 사용자가 꼽은 둘(일반 판촉 · 정지) 말고 대화 요약 설정 · 설문도 두 BC 값을 보인다 — 이관 때 cross_context 후보(§9).

### 고칠 설계

- **#668(새 · 명세 · 그래프 houserules §5 · R-3757)** — `driven_layer/django_<bounded_context>/admin/**`(옛 자리 `django_*/admin/**` 포함)는 자기 BC 의 `domain_layer/` · `application_layer/` · `composition_root/` · `driven_layer/adapter/persistence/` · `driven_layer/adapter/anticorruption_layer/` 를 import 하지 않는다(함수 안 · 상대 import · 그 BC 꾸러미에서 층 이름을 가져오는 꼴 포함). 자기 `driven_layer/django_<bounded_context>/` 모듈이 그 다섯 자리에서 묶은 이름을 그 모듈을 거쳐 가져와도 같다(한 겹). 단순 자료는 ORM 값으로 읽고 쓰고, DB 제약으로 걸 수 없는 업무 규칙(값 객체 규칙 포함)이 있는 쓰기는 그 BC 의 `driving_layer/open_host_service/` 를 부른다. 다른 BC 는 import 하지 않는다 — 두 BC 이상의 값을 보이는 화면은 `cross_context/backoffice/` 다.
  - 자리 `트리 83~87행` · `ast` · principle · blocker · 집행 check-context-isolation.
  - 줄은 **파일당 하나**(검토 m9) — 같은 판정 · 같은 고침 단위(파일)라 빚 질문을 줄인다. 걸린 import 는 줄 글 끝에 **정렬한 문자열 목록 칸**(`['a', 'b']`)으로 적는다(재확인 N9 · 글 N2). 줄 꼴 조건 둘(셋째 확인): 줄 글에 줄 번호를 넣지 않는다(파일 단위 줄 — `registry_gate.py` `_list_shrunk` 의 `file_level` 꼴) · 목록 칸의 값은 원문 글이 아니라 푼 절대 모듈 경로다(상대 · 절대 꼴을 바꿔도 새 줄이 되지 않음). registry_gate 는 목록 칸만 줄어든 줄을 그 파일이 앵커와 byte 같을 때만 잔존으로 본다(`registry_gate.py:1533` «F4-99 — 고치지 않은 파일»). 그래서 실행이 고친 admin 파일에서 걸린 import 를 **일부만** 걷거나 하나를 더하면 새 줄로 귀속돼 G2 가 막는다 — 고친 파일은 그대로 두거나(빚 ⓑ) 모두 걷는다(빚 ⓐ). 설계자 글(R-1683 한 줄)에 적는다.
  - `composition_root` · `persistence` · `anticorruption_layer` 를 넣은 까닭: admin 이 `build_` 로 유스케이스를 받거나, 리포지토리 어댑터로 도메인 애그리거트를 받거나, 자기 ACL 어댑터로 다른 BC 값을 받으면 같은 일을 이름만 바꿔 한다. 클론에서 합성 루트 · 저장 어댑터를 쓰는 admin 파일은 모두 도메인 · 응용도 쓰는 파일이라 붉은 파일 수는 늘지 않는다(질문 생략 · 결정 뜻에서 나옴 · 알릴 것 ②).
  - 다시 내보내기 한 겹(검토 I2): 모델 모듈이 도메인 값 객체를 choices 로 import 하는 것은 그대로 받는다(트리 · #326 몫). admin 이 그 이름을 모델 모듈에서 다시 가져오는 길만 막는다 — 막지 않으면 값 객체 줄(클론 66)이 가장 먼저 이 길로 빠진다.
    - 꼴(재확인 N8): 모델 모듈 쪽이 다섯 자리에서 묶은 이름 = `from … import X` · `from … import X as Y` · `import … as m`(모듈째) · 상대 import · 모듈 수준 이름 대입 별칭(`Kind = OrderKind` — 오른쪽이 묶은 이름 · 그 속성일 때). admin 쪽 = 그 이름을 모델 모듈에서 가져옴 · `from <모델 모듈> import *`(그 모듈이 묶은 이름이 하나라도 있으면 · 셋째 확인) · 자기 `django_<bc>/` 모듈을 모듈째 가져와(`from …models import order_model` · `import …order_model as m`) 그 별칭의 속성으로 묶은 이름을 씀(`m.OrderKind`).
  - 고칠 길(규칙 글 · 위반 글): 비교 · 필터 · 라벨은 ORM 값(모델 필드 값 · 모델이 가진 속성 · 메서드)으로 한다. 값 객체 규칙이 걸린 쓰기는 «규칙이 있는 쓰기» 라 그 BC 창구로 간다. v0 의 «모델 필드 `choices` 를 쓴다» 는 비교에 쓸 기호를 주지 않아 걷는다.
- **#101 부칙**(명세 `:435` · `check-composition-root.py` `_check_inner_driving_imports` 다섯 줄): 표준 자리 admin 파일이 자기 BC `open_host_service/` 를 import 하는 것은 #668 의 창구 부름이라 대상 밖이다 — 다른 BC driving 은 앞에서 #13 · #102 로 넘기고, api · cron · 구독은 그대로 #101(검토 범위 확인).
- **#188(고침 · 등급 path → ast)**: «REST 표면이 있는 BC 의 `application_layer/<area>/` 는 입구와 짝이다 — 같은 이름의 `driving_layer/api/<area>/` · `open_host_service/<area>/` 가 있거나, 같은 BC 의 `open_host_service/` · `event_subscription/` · `cron_job/` · `api/webhook/` 아래 파일이 그 영역을 import 하면(직접 · 그 영역을 짓는 `composition_root` 빌더) 짝이다. 부르는 것이 admin 뿐이면 «admin 은 ORM 으로 읽고 쓰거나, DB 로 걸 수 없는 규칙이 있는 쓰기는 그 BC 창구(open_host_service)를 부른다» 로 알린다. 반대 방향(REST BC 의 `api/<area>` → 응용)은 그대로. REST 표면이 없는 BC 는 지금처럼 보지 않는다.»
  - 시험 파일 · `composition_root/event_wiring.py` 는 입구로 세지 않는다(#89 — 입구는 driving 뿐).
  - **넓히지 않는 까닭(검토 I5 · 운영자 판단 · 질문 없음)**: 손님 API 없는 BC 까지 넓히면 클론에 기동 배선만 부르는 영역(BC-자 기동 영역 — Django 시스템 검사 등록 · 워커 기동 캐시 데우기) 한 줄이 새로 뜨는데, 표준 트리 driving 칸에 «기동 작업» 입구가 없어 고칠 자리가 없다. 리팩토링 G0 는 빚을 «항상 정리» 하므로 그 BC 레인이 멈춘다 — 이 판의 목적(리팩토링 길 막힘 풀기)과 어긋난다. 다음 판 후보: «기동 전용 영역의 자리를 먼저 정해야» 넓힐 수 있다.
- **#339**(`:652`) «화살표 · 앎의 범위는 규정하지 않는다» → «앎의 범위는 #668 하나만 건다(#9 · #326 은 #327 대로 안 건다)».
- **#327**(`:641`) «admin/** 는 … 잎 import 검사의 대상에서 뺀다» 끝에 «(#668 은 따로 건다)».
- **#347**(`:660` · 후보) → «업무 규칙이 있는 운영 쓰기는 그 BC 창구로 부르고 `feature/` 에는 화면만» — 이 후보는 #668 이 덮는다. 술어 표 `workspace/design/2026-08-11-predicates.md:169` 의 #347 줄도 함께 고친다(그 import 자체가 이제 blocker).
- 트리 글: `mkrev2.py:374`(admin/ — «타 BC 금지» 를 #668 로 · «여러 BC 값 화면은 `cross_context/backoffice/`») · `:378`(feature/) · `:1043` · `:1681`(#188) — §7 생성과 한 번에.
- 그래프: houserules §5 블록에 #668 한 문장(R-3757) — 설계자 · coder 가 G1 · 구현에서 알게 한다. 조정자 s006/b9 의 «#188 area 1:1» 예시는 뺀다(R-3433 — 이제 import 를 읽어 S3 인용 filtered 가 선다). discipline-reviewer #347 물음 글(s007/b43 · R-1092)도 맞춘다.
- 검사기:
  - `check-usecase-dto-placement.py`(판 A 밖) — `ENTRANCE_DIRS` · `_absolute_imports` · `_named_areas` · `_builder_areas` · `_area_callers` · `_check_structure` · `:316` 문은 남긴다(`f158/patch-usecase-dto.diff` 에서 문을 되살린 꼴 · `f159/scripts-188g/`).
  - `check-context-isolation.py`(판 A 파일) — `_admin_area` · `_scan_admin_imports`(다섯 자리 · 꾸러미 꼴 · 자기 `django_<bc>/` 모듈의 다시 내보내기 한 겹 · 다른 BC 는 기존 `_apply_other_bc` — 다른 BC 창구는 #13) · `_scan_imports` 첫 줄에서 admin 갈래로. 판 A 의 `_WindowTry` · `_check_acl` 묶음과 안 겹친다.
  - `check-composition-root.py`(판 A 밖) — #101 부칙(+5).

### 빚 범위 — **사용자 결정: 다른 빚과 같이(가)** (2026-11-14 · `date` 20:10)

- 사용자 원문: «우선은 다른 것들처럼 미룰수 있게 해야 할거 같아. 그런데 리팩토링때는 수리를 해야 하니깐 리팩토링 기능에도 들어가야해» — 운영자가 물은 가 · 나 가운데 «다른 빚과 같이» 는 «가» 다(«나» 는 기능 · 수정 실행에서 #668 만 따로 좁히는 특례였다). 이의 시 뒤집음.
- 사실: #668 은 admin 211 파일 가운데 61 파일(16 BC)에 걸린다(대상 저장소 사본 · BC 별 수는 §2 «클론 재측정»).
- 실현 — #668 은 특례 없이 다른 규칙의 빚과 같은 장치를 탄다:
  - 기능 · 수정 실행: 조정자 Phase 0 3번의 빚 목록(위반 경로가 `application/<대상 bc>/` 안인 진단)에 그 BC 의 #668 줄이 모두 든다 → G0 빚 질문 ⓐ 지금 정리 / ⓑ 미룸 · 상시 미룸 · 출처 있는 ⓑ · 재개 G0 · 스캔 단위 재승인 모두 지금 규칙 그대로. 조정자 글에 #668 몫 문장을 더하지 않는다(R-0194 리비전은 `cross_context/` 경로 필터 몫만).
  - 리팩토링 실행: BC 리팩토링 G0 빚 스캔에 그 BC 의 #668 줄이 든다 — 리팩토링 모드는 미룸이 없어(B1 «항상 정리» · 상시 미룸도 리팩토링 모드에는 서지 않는다 · `commands/dddjango.md:117`) 그 실행이 고친다. 고칠 길은 #668 규칙 글(ORM 값 · 규칙 있는 쓰기는 그 BC 창구) 그대로이고, 그 BC 에 맞는 창구 함수가 없으면 창구를 더하는 것까지 리팩토링(동작 불변) 몫이다.
  - 설계자(design-architect s005/b21 · R-1683 리비전) — «file-plan 이 admin 파일을 만들면 #668 에 맞게(ORM · 창구) 쓰고, 고치는 옛 admin 파일은 빚 결정대로 그 파일의 #668 import 를 모두 걷거나(ⓐ) 그대로 둔다(ⓑ) — 일부만 걷지 않는다»(줄 꼴에서 나옴).
  - discipline-reviewer(s007/b51 · R-1117 리비전 · §8) — 고친 admin 파일의 #668 이 빚 결정대로(ⓐ 면 0 · ⓑ 면 그대로)인지 묻는 줄.
  - G2: 만든 파일의 #668 은 새 줄이라 registry_gate 귀속으로 막힌다. ⓐ 를 고른 줄은 «G0 ⓐ 잔존 M»(`:229`)이 기계로 막고, ⓑ 면 줄 글이 그대로여야 하며 일부만 걷으면 귀속 red 다(위 줄 꼴).
- 비용(배포 보고 · 요청 가이드 확인 줄에 적음): 16 BC 를 건드리는 기능 · 수정 실행의 G0 빚 질문에 그 BC 의 admin 빚이 함께 뜬다(예: 이용 정책 BC 6 파일 · 판촉 BC 8 파일 · 계정 BC 1 파일). 상시 미룸을 세운 프로젝트는 묻지 않고 미뤄진다.
- v2 의 «나» 실현(첫 G0 에서 빼고 G1/G1′ 직전 재승인 · R-3474 리비전)은 걷었다 — 셋째 확인(글)이 짚은 «재개 G0 에서 #668 이 새 빚으로 다시 뜸» 구멍도 함께 없어진다. 새 Expression 은 26 이다.

### 시험

- 새 픽스처: `usecase_dto/entrance_pairs`(이름 다른 창구 · 빌더만 · cron · webhook · 구독 상대 import · admin 만 · 아무도 안 부름 — 모두 REST 표면 있는 BC) · `context_isolation/admin_imports`(도메인 · 상대 · 함수 안 · 합성 루트 · 저장 어댑터 · 자기 ACL · 꾸러미 꼴 · 모델 모듈 다시 내보내기(이름 · 모듈째 가져와 속성 · `import … as` · 대입 별칭 · 모델 모듈 상대 import — 재확인 N8) · 옛 자리 → 파일당 #668 한 줄(정렬한 목록 칸 — N9) · 자기 창구 통과 · 다른 BC 창구 #13 · 다른 BC 모델 #12) · `composition_root/admin_window`(#101 부칙).
- 기존 픽스처(문을 남긴 판 · `f159/sweep188g.txt` — 117 레인): usecase-dto **9 레인이 문구만** 바뀐다(+n −n · exit 무변). context_isolation/bad_rules 에 #668 +1. v0 의 «26 레인 #188 +1 · exit 0 → 2 넷» 은 문을 걷었을 때 몫이라 없어진다.
- `fixture_matrix` — GROUP_CASES 셋 · MUTATIONS 12(이름 다른 입구 무시 · 빌더 길 무시 · admin 문구 합침 · `_admin_area` 끔 · 상대 import 건너뜀 · 합성 루트 허용 · persistence · ACL 허용 · 다시 내보내기 한 겹 끔 · 다시 내보내기 속성 길 끔(N8) · 목록 칸 정렬 걷음(N9 — 차례 다른 사례로 죽음) · 옛 자리 끔 · #101 부칙을 driving 전체로 넓힘).
- 구현 차례(재확인 N10): C2 일꾼이 #668 검사기 시제품을 먼저 내 클론 61줄 · 셈 스크립트 `f159/adm668v1.py` 의 파일 집합과 맞추고, 검토 장난감(`review-checkers/toys/adm` · `adm2`)을 모두 잡은 뒤 픽스처를 굳힌다.
- 골든: `field_report_checker_smoke.py` `UsecaseAreaPairingRegression`(`:848-930` — `:878-879` 문구 · REST 건너뜀 사례는 그대로) · `findings_count_matrix.py:117` · `:136` · `checker_baseline_matrix.py:247` · `checker_cross_matrix --emit-expected` · `gen_pregate_symbol_kinds`(JSON 둘).
- Codex byte 미러 셋.

### 클론 재측정(작업 트리 사본 → 시제품 · `DJR_VIOLATIONS_DIR` 붙임)

- #188 **8 → 6**(`f159/u-188g.out`):
  - 가입 보너스 · 정지 — 사라짐(구독 · 이름 다른 창구가 짝).
  - 6(대화 요약 설정 · 설문 목록 · 일반 판촉 · 공지 작성 · 이용 한도 · 추천 질문 작성) — admin 문구로 남음.
  - 새 줄 0 · 나머지 줄 byte 같음.
- #668 새 빚 — **61 파일(파일당 한 줄 = 61줄) · 16 BC**(admin 파일 211 가운데 · 옛 자리 0 · 함수 안 import 0 · `f159/adm668v1.out` · 검토 셈과 같음):
  - 걸린 import(참고 · import 당이면 271): 응용 99(포트 7 포함) · 합성 루트 38 · 도메인 132(예외 61 · 값 객체 66 · 그 밖 5) · 저장 어댑터 2. 다시 내보내기 한 겹 · 꾸러미 꼴은 지금 0(막아 두는 몫). 값 객체만 쓰는 파일 8.
  - BC 별 파일: BC-거 11 · 판촉 BC 8 · 이용 정책 BC 6 · BC-라 6 · BC-카 5 · BC-사 4 · BC-하 4 · BC-아 4 · BC-바 3 · BC-타 3 · BC-파 2 · 계정 BC 1 · BC-차 1 · BC-마 1 · 캐릭터 BC 1 · BC-다 1.
- composition-root: 작업 트리 = 시제품 = G0 기록.

### 남는 한계

- «DB 로 걸 수 없는 규칙» 인지는 기계가 못 가린다 — admin 의 ORM 쓰기가 도메인에만 있는 규칙을 건너뛰는지(예: 공지 «빈칸만»)는 감수가 본다.
- #188 은 import 만 본다 — 실제로 부르는지는 안 본다. 동적 import 는 못 본다(클론 0). REST 표면 없는 BC 의 영역 짝은 보지 않는다(다음 판 — 기동 영역 자리 먼저).
- 다시 내보내기는 한 겹만 본다 — 두 겹(모델 모듈 → 다른 모듈 → admin)과 `getattr(m, "OrderKind")` 같은 동적 길은 못 본다.
- admin 의 벤더 SDK 금지는 여전히 검사가 없다.

### 버린 갈래

- 28번째 검사기 · check-naming(판 A 가 고친 `_admin_dirs` · 이름 검사 축 아님) · db-table #326 에 두기.
- 시험 파일 · `event_wiring` 을 입구로 세기.
- 빌더를 빼고 직접 import 만 세기 — 클론 결과는 같지만 #92 가 연 두 길과 어긋난다.
- import 당 한 줄(271) — 같은 고침 단위인데 질문만 네 배.
- 이 판에서 #188 을 손님 API 없는 BC 로 넓히기 — 위 «넓히지 않는 까닭».

## 3. F4-175 — 한 BC 안 공유 시험 재료

### 결정(사용자 · 고정)

- `fake/<declaration>_<variant>.py` 를 받는다 — 선언을 상속하고 페이크 규칙을 모두 지며 기본 페이크 옆에 둔다(결정의 예를 일반 이름으로: `order_lookup_port_recorder.py`).
- `factories/` 는 factory_boy 말고 보통 «만드는» 함수도 받는다. 새 서랍 폴더 없음. 그 밖은 시험 파일 안.

### 재현(2.37.0 · 장난감 `f175/toy` · 클론)

- #576(`check-port-adapter-pairing.py:1091` · 작업 트리 `:1093`)은 `py.stem not in decl_stems` — 변형 이름은 모두 막힌다.
- #392(`check-test-config.py:453-459`)는 `import factory` 나 `…Factory` 밑 클래스가 없으면 막는다 — 만드는 함수가 막힌다. 반대로 `import factory` 한 줄만 있으면 그 파일에 무엇이 있어도 통과한다.
- 덤: #577(`:1103`)은 밑 클래스의 접미사만 본다 — 다른 선언을 상속해도 통과한다.
- 클론: 계정 BC `test/fake/` 의 둘째 대역(기록하는 대역) 한 파일이 #576(판 A 설계 §7).

### 고칠 설계

- **#576** — 파일 이름이 선언과 같으면 기본 페이크. 아니면 `<선언>_` 로 시작하는 선언 가운데 **가장 긴 것**의 변형(`_fake_declaration` 신설).
  - 맞는 선언이 없으면 #576(현장 꼴 — 선언 이름 없이 지은 변형 — 은 이름 안내 문구로 남음).
  - 변형인데 `fake/<선언>.py` 가 옆에 없으면 #576(결정 «기본 페이크 옆»).
  - 가장 긴 앞머리를 택한 까닭: `stock_query` ⊂ `stock_query_port` 같은 겹침에서 «맞는 아무 선언» 이면 짝이 둘이 되고 짧은 쪽 상속이 통과한다. 선언 이름은 늘 `_port` · `_query` · `_unit_of_work` · `_repository` 로 끝나 겹침에서도 한 뜻으로 정해진다(검토 확인).
- **#577** — 변형 파일은 그 선언 파일의 맨 위 클래스 가운데 하나를 상속해야 한다(클래스 이름으로 대조 — `*_query` 는 `…DomainBypassQuery` 라 이름 변환으로는 못 맞춘다). 접미사 #577 이 이미 나온 파일에는 겹쳐 내지 않는다. 기본 페이크의 #577 은 그대로(접미사 — 둘의 엄격함이 다른 것은 기록만).
  - 변형이 기본 페이크를 상속하면(`class Spy(FakeOrderLookupPort)`) #577 이다 — 결정 글 «선언을 상속» 대로. 흔히 쓰는 꼴이라 규칙 글에 «선언을 바로 상속한다(기본 페이크 상속 아님)» 한 마디(검토 덧붙임).
- **#392** — 파일 단위가 아니라 맨 위 정의마다 본다(`_factories_misfits` 신설 · 한 파일 한 줄).
  - 받음: `…Factory` 밑 클래스(제네릭 꼴 `DjangoModelFactory[M]` 포함 — `_base_name` 이 `ast.Subscript` 면 `.value` 로 내려간다 · 검토 m2) · `make_` 로 시작하는 함수 · `_` 비공개 함수 · import · 상수.
  - 막음: 선언을 상속한 클래스(→ `fake/`) · pytest 고정물(→ `conftest.py`) · `test_*` 함수 · `Test*` 클래스 · 그 밖의 공개 클래스 · 함수 · 재료가 하나도 없는 모듈.
  - 공개 함수 위반 글은 «만드는 함수면 `make_` 로 이름을 바꾸거나, 그 시험 파일 안으로» 를 앞에 둔다(검토 m3 · 알릴 것 ⑥).
- **#388 그대로** — `unit/` 은 `factories/` 를 import 하지 않는다. 결정이 `unit/` 을 열지 않았고, 열면 ORM 행을 만드는 `make_` 함수가 unit 에 샌다(#387 은 시험 파일 안 `.objects` 만 본다). 질문 생략 · 설계 처리 · 알릴 것 ⑤.
- 트리 행 이름은 그대로 둔다 — `fake/<declaration>.py`(142행)는 자리표시자 «파일» 칸이라 #490 에서 이름이 자유다(`check-layer-skeleton.py:672` · `:796`). 설명 글만 고친다(`mkrev2.py:432` factories · `:433` fake · `:434` `<declaration>.py`) — §7 의 생성과 한 번에.

### 규칙 글(옛 → 새)

- houserules §1 «읽는 법»(graph · s004-1/b7 · R-3740 옆에 새 Norm 둘):
  - R-3758 «BC `test/fake/` 에는 기본 페이크 `<declaration>.py` 옆에 같은 선언의 둘째 대역 `<declaration>_<variant>.py` 를 둘 수 있다(예: `order_lookup_port_recorder.py` · 클래스 `OrderLookupRecorder(OrderLookupPort)`). 변형도 그 선언 클래스를 바로 상속하고 페이크 규칙(#575 · #577 ~ #581)을 그대로 진다. 기본 페이크가 없는 변형과 앞머리가 선언 이름이 아닌 파일은 위반이다(#576).» — 담당 check-port-adapter-pairing.
  - R-3759 «BC `test/factories/` 에는 factory_boy 팩토리와 `make_` 로 시작하는 만드는 함수가 온다(#392). 그 밖의 공용 시험 재료는 새 폴더를 만들지 않고 쓰는 시험 파일 안에 둔다. `unit/` 은 여전히 `factories/` 를 import 하지 않는다(#388).» — 담당 check-test-config.
- implementation-test §9.1(graph · s049-9.1/b3 · R-1816 리비전):
  - 옛 «팩토리는 **`…/test/factories/`**(패키지)에 둔다 — 이 폴더는 테스트 트리 단일 출처(`discipline-houserules` §2)에 …»
  - 새 «… 둔다 — factory_boy 를 쓰지 않는 공용 도메인 객체 생성은 같은 폴더의 `make_<x>()` 함수로 둔다(#392). 자리 규칙은 `discipline-houserules` §1 이 단일 출처라 …»(옛 «§2» 는 낡은 가리킴이라 함께 고침).
- 명세(산문 · spec_lint 대상):
  - #392(`:709`) «`factories/` 에는 `factory_boy` 픽스처만 온다.» → «… `factory_boy` 팩토리와 `make_` 로 시작하는 만드는 함수만 온다 — 맨 위 정의마다 본다(비공개 `_` 도우미 · import · 상수는 곁에). 가짜 구현은 `fake/`, pytest 고정물은 `conftest.py`, 시험은 `unit/` · `integration/` · `e2e/`, 그 밖은 쓰는 시험 파일 안.»
  - #576(`:898`) 덧붙임 «2026-11-14 · F4-175 — 부칙: 같은 선언의 둘째 대역은 `<declaration>_<variant>.py` 로 기본 페이크 옆에 둔다. 짝 선언은 앞머리가 `<선언>_` 로 맞는 가장 긴 선언이다. 기본 페이크가 없거나 맞는 선언이 없으면 위반.»
  - #577(`:899`) «선언당 하나» → «선언당 기본 하나(+ 변형)» · «변형은 그 선언 파일의 클래스를 바로 상속한다».

### 시험(장난감 26 경우 · 시제품 `f175/scripts-fix/` = 작업 트리 사본 + `f175/patch_fix.py`)

| 경우 | 기대 | 2.37.0 | 시제품 |
|---|---|---|---|
| 기본 페이크 | 통과 | 통과 | 통과 |
| `<선언>_recorder.py`(상속 · 기본 옆) | 통과 | #576 | 통과 |
| 변형 · 상속 없음 | #577 | #576 · #577 | #577 |
| 변형 · 다른 선언 상속 | #577 | #576 | #577(변형 줄) |
| 변형 · 기본 페이크 없음 | #576 | #576 | #576 |
| 앞머리가 선언 아님 | #576 | #576 | #576 |
| 현장 꼴(선언 이름 없는 변형) | #576 | #576 | #576(이름 안내) |
| 겹침 — `…_port_recorder` 가 긴 쪽 상속 · `…_port_spy` 가 짧은 쪽 상속 · `stock_query_audit` | 통과 · #577 · 통과 | #576 셋 | 통과 · #577 · 통과 |
| 변형이 `requests` 를 씀 | #578 | #576 · #578 | #578 |
| factory_boy · 제네릭 `DjangoModelFactory[M]` | 통과 · 통과 | 통과 · 통과 | 통과 · **#392(오탐 · v1 에서 고침)** |
| `make_account` + `_도우미` + 상수 · ORM 행을 만드는 `make_` | 통과 | #392 | 통과 |
| 가짜 포트 · 고정물 · `test_*` · 빌더 클래스 · `random_name()` · 상수뿐 · `make_` + 고정물 · `create_account()` | #392 | #392 | #392(까닭이 줄에 · `create_` 는 «`make_` 로» 안내) |
| factory_boy 파일 안 공개 도우미 `random_bio()` | #392(엄격) | 통과 | **#392 — 새로 붉어짐**(클론 · 픽스처 0) |
| BC `test/conftest.py`(autouse 아님 · autouse) | 0 · #383 | 0 · #383 | 0 · #383 |

- 변이 10(시제품 9 모두 죽음 · `f175/out/mutations.txt` + 제네릭 기저 풀기 지움) — `field_report_checker_smoke.py` 에 장난감 클래스 둘 · `_MUTATIONS` 10.
- 기존 픽스처: 판정 바뀜 0 · 문구만 5줄 → `findings_count_matrix --emit-expected` 두 키(`:129` · `:133`).
- `gen_pregate_symbol_kinds` 다시 냄(source_sha · `endswith("Factory")` 앵커는 남음).
- Codex byte 미러 두 파일. 시제품의 줄 이음이 사라진 조건 한 줄(`…and not unbased … and not any(`)은 구현 때 바로잡는다(검토 덧붙임).

### 클론 재측정(`f175/out`)

- #576 1 → 1 — 같은 파일 · 문구만(«`<선언>_<변형>` 이름으로»). 대상 쪽에서 `<선언>_<변형>` 이름으로 바꾸면 0(`f175/clone-sim` 으로 확인).
- #577 0 → 0 · #392 0 → 0. 판정이 바뀐 파일 — `fake/` 132 중 0 · `factories/` 35 중 0.

### 남는 한계

- `make_` 가 무엇을 돌려주는지는 보지 않는다.
- framework `test/fake/`(#621 ~ #623)는 변형을 받지 않는다(결정 = BC 안).
- 변형 클래스 이름 가운데에 `Port` 가 오면 #43(`check-naming.py:401`)에 걸린다 — 예시는 `OrderLookupRecorder` 꼴.

### 버린 갈래

- 트리 행 이름 바꾸기(검사기 효과 0) · «맞는 아무 앞머리» · #392 파일 단위 느슨한 판정 · 새 서랍 폴더(결정이 막음).

## 4. F4-174 — BC `test/conftest.py`(후보 → 넣지 않음 · 이미 고쳐짐)

- 재현(장난감 `f175/toy` · `check-layer-skeleton.py` · `check-test-config.py`):
  - 2.33.0 — BC `test/conftest.py` 에 `[#490]` · check-test-config 는 받음 — 보고 그대로.
  - 2.37.0 · 작업 트리 — #490 0줄 · autouse 면 #383 만 · 직계 `helpers.py` 는 #490 과 #384 가 함께 막음. 두 검사기 판정이 같다.
- 원인: 2.33.0 에 면제가 없었다. 2.34.0(4d785333 · F4-62 · F4-138)부터 `check-layer-skeleton.py:798-799`(`row.r == _BC_TEST_ROW` · conftest)가 면제한다 · 픽스처 `skeleton/bc_test_conftest`.
- 레인이 실제로 쓴 판은 확인하지 못했다(레인 폴더는 읽지 않음). 2.33.0 이하였다면 보고와 맞는다.
- 처분: 수리로 넣지 않는다. 장부 «2.34.0 에서 고침 · 2.37.0 재현 안 됨».
- 덤(글 셋 · §7 생성과 같이): 부칙이 빠진 글 — 명세 #490 행(`tree-revision-spec.md:816`) · 검사기 머리글(`check-layer-skeleton.py:13-14`) · 트리 136행 설명(`mkrev2.py:428`)에 «BC `test/` 직계 `conftest.py` 부칙» 한 구절.

## 5. F4-178 — 경로 앞 응답 정본이 흔한 ruff 를 못 지남(후보 · 높음 → 넣음)

### 재현(배포본 2.37.0 · ruff 0.17.3 `--isolated --target-version py312` · `f178/`)

- final.md «pre-route-canonical» 블록 = 자산 `scripts/pre_route_responses_canonical.py`(byte 같음). 작업 트리 자산 · final.md · 검사기도 배포본과 byte 같다 — 판 A 밖.

| 명령 | 옛 정본 |
|---|---|
| `check --select C90 --config 'lint.mccabe.max-complexity = 10'` | C901 `_project_rows` 12 > 10 |
| `format --check`(줄 88 기본) | 긴 줄 수십 곳을 다시 씀 |
| `format --check --line-length 130` | 현장과 같은 두 곳 — docstring 뒤 빈 줄 · `_add` f-string 따옴표 |
| `format` 줄 100 · 120 · 140 | 모두 다시 씀(깨끗한 줄 길이 없음) |
| `check`(0.17 기본 규칙) | I001(import 줄 94자) |
| `--select E,F,W,I,UP,B,C90,SIM` 줄 88 / 130 | E501 44 · I001 · C901 / C901 하나 |
| 플러그인 권장 설정(implementation-python §22.1 · 줄 88) | I001 |

- 함수별 복잡도 — `add_pre_route_responses` 10(경계) · `_add` 9 · `_applies` 7 · 나머지 6 이하.

### 원인

- 문서는 «글자 그대로» — implementation-django-ninja `final.md:904-906` · `:994` · `:912-913`(api.py «서명 · 몸통 글자 그대로») · coder `:53` · discipline-reviewer `:100`.
- 검사기는 구문 나무로 맞춘다 — `check-openapi-error-declaration.py:4220-4243` `_canonical_form`:
  - import 는 집합(차례 · 묶음 · 줄 나눔 · `__future__` 안 봄) · 그 밖 문장은 차례대로 `ast.dump(include_attributes=False)`(함수 몸통 · 데코레이터 · `type` 문 · 모듈 상수 · 함수 · 클래스 안 docstring 은 듦).
  - 맨 위 모듈 docstring · 주석(`# noqa` · `# type: ignore`) · 빈 줄 · 괄호 · 끝 쉼표 · 따옴표 꼴은 대조 밖.
  - 문서보다 검사기가 너그럽다. 그리고 옛 정본 코드 자체가 줄 88 에서 ruff format 을 못 지난다.
- 정본은 그래프다 — `implementation-django-ninja-final.ttl` s023-6.2 b37(R-3749 · 904 글) · b42(산문 · 994 글) · b43(코드 · 정본 전문) · `agent-coder.ttl` s004/b16 R-2548 · `agent-discipline-reviewer.ttl` s007/b19 R-1011. 셋 다 판 A 가 안 고쳤다.
- 정본을 고정한 자리: `pre_route_canonical_check.py:29-40`(자산 = Codex 미러 = 픽스처 셋 = 참조 글 블록 byte 대조) · `pre_route_behavior_smoke.py:37` · `api_error_backstop_matrix.py:5349` · `:6794-6798` · `:7077-7081` · `pregate_fixture_run.py:2011` · `:2078` · `anchor_diff_smoke.py:111` · `design_pregate.py:1245` · `:4645-4654` · `manifest_seal.py:66` · `reverse_coverage.py:181` · Makefile `:181` · `:252-253` · 픽스처 byte 사본 셋(`openapi_decl_missing/{good,bad_rules}` · `openapi_error_declaration/good`).

### 고칠 설계

- **새 정본**(`f178/new_canonical.py` · 302 → 451줄) — 동작이 같은 범위에서만 나눈다:
  - `_project_rows` 12 → 4(`_check_row` 6 · `_check_operations` 4) · `add_pre_route_responses` 10 → 6(`_check_targets` 5) · `_add` 9 → 5(`_merge_content` 5 · `_schema_options` 1) · `_applies` 7 → 5(`_when_holds` 1 · `_exempted` 3) · 작은 도우미 `_checks_csrf` · `_significant` · `_plain_option`. 가장 큰 복잡도 6.
  - 단락 평가를 지킨다(permissions 의 `a or b or ()` · `csrf_exempt` · "input" 의 게으른 `any` · exempt 보는 차례).
  - 모든 줄 88칸 안 · 여러 줄 나눔은 끝 쉼표로 고정.
  - ruff: C90(10) · 0.17 기본 · 넓은 묶음(88 · 130) · 플러그인 권장 설정 모두 0 · `format --check` 줄 88 · 100 · 120 · 130 · 140 모두 «already formatted»(검토 재확인). `--select ALL` 에만 TRY003 · EM102 · D1xx · PLR · SLF001 · CPY001 이 남는다(`# noqa` 로 받는 몫 — 아래 문서).
- **옛 사본 처리 — 옛 판 자산도 받음**: 검사기 `:3719` `PRE_ROUTE_CANONICAL_ASSETS = ("pre_route_responses_canonical.py", "pre_route_responses_canonical_2_37_0.py")` · 자산 `…_2_37_0.py`(= 2.37.0 정본) 새로 둠.
  - 까닭: 동작이 같음을 보였다(아래) · 검사기에 이미 이 장치가 있다(`:3716-3718` 주석 «옛 판도 받을 때는 그 판 자산을 더하고 이름을 잇는다») · 이미 착륙한 현장 둘을 다시 옮기게 하지 않는다(질문 생략 · 설계 처리).
  - 표 칸 이름 같은 판정 기준은 첫 자산에서만 읽는다(`:4289-4297`) — TypedDict 가 바뀌는 판에는 옛 자산을 뺀다. 지금은 둘이 그 몫에서 같다(검토 확인).
- **위반 글**(`:4357-4358`) «정본의 코드가 플러그인 정본과 다르다 …» 에 «서식 · 주석은 대조 밖 · 린트는 `# noqa`» 를 붙이고, «N번째 정의부터 다름» 은 **앞머리가 가장 길게 같은 자산**과 견준 번호를 그 자산 이름과 함께 낸다(검토 m4 — 지금은 늘 첫 자산과만 견줘 옛 판 사본 주인을 헛갈리게 한다).
- **문서 문구(검사기가 안 보는 것과 똑같이)** — final.md `:904-906`(b37):
  > `framework/ninja/pre_route_responses.py` — 플러그인 정본. 아래 정본 코드 블록을 옮기고 **코드는 고치지 않는다** — 검사기가 코드(구문 나무)를 정본과 맞춘다. 코드가 아닌 것은 프로젝트 포매터 · 린터에 맞춰도 되고 검사기도 보지 않는다: 서식(줄 나눔 · 괄호 · 끝 쉼표 · 빈 줄 · 따옴표 꼴), import 의 차례 · 묶음 · 줄 나눔, `from __future__ import annotations`, 주석(`# noqa: …` · `# type: ignore[…]`), 맨 위 모듈 docstring. 정의 · 문장 · 값 · 이름 · 차례와 함수 · 클래스 안 docstring 은 코드다. 린트가 정본 코드를 짚으면 코드를 고치지 않고 그 줄 `# noqa: <규칙>` 이나 파일 단위 무시로 둔다(코드를 바꾸는 자동 고침은 검사기가 막는다). 옛 판(2.37.0) 정본도 받는다 — 동작이 같아 바꾸지 않아도 된다. …(이하 그대로)
  - `:912-913` «`get_openapi_schema` 의 서명 · 몸통은 코드 그대로다(서식 · 주석은 위 정본과 같이 프로젝트 도구 몫)» — 이 클래스 블록도 줄 88 ruff format 이 다시 쓰는 같은 꼴의 잠복 결함이다.
  - `:993-994`(b42) «… 에 옮긴다(코드는 그대로 · 서식 · 주석은 위 «경로 앞 응답» 첫 항목대로)».
  - R-3749 이름표 «글자 그대로» → «코드 그대로(서식 · 주석 · import 차례 · 모듈 docstring 은 프로젝트 도구 몫)» · coder `:53`(R-2548) «… 이름 · 문장 · 차례를 바꾸지 않는다 · 포매터 · 린터가 바꾸는 서식 · 주석은 받는다» · discipline-reviewer `:100`(R-1011) «정본과 코드가 같고(서식 · 주석은 대조 밖)».
- 검사기 판정 논리는 무변 — 바꿀 것은 `:3719` 튜플과 위반 글 둘.

### 같은 동작 증거

- 저장소 동작 스모크 `pre_route_behavior_smoke.py --canonical` — 옛 · 새 모두 PASS(문서 operation 47 · 실제 요청 64 · 틀린 표 8 · mypy strict 4파일).
- 문서 대조(`f178/equality_harness.py` · `.venv-probe` Django 6.1 · Ninja 1.6.3 · ninja_extra 0.31.7) — 루트 API 넷의 마운트 문서 · JSON 400 표 · 틀린 표 8 꼴의 ValueError 글까지 10 꼴 같음(ninja_extra operationId 끝 8자는 실행마다 달라 가림 — 옛 정본끼리도 다름). 대조용 변이(exempt 메서드 조건 뒤집기)는 둘 다 붉다 — 도구가 차이를 본다(검토).
- 함수 퍼즈(씨앗 178) — `_plain` · `_can_fail` · `_applies` · `_add` · `_content` 각 3000회 · 표 검증 3000회 · 장난감 API 넷 × 무작위 표 1200회 · 어긋남 0.
- `from __future__` 꼴 · 줄 130 홑따옴표로 다시 짠 꼴 · 현장 꼴도 어긋남 0.

### 옛 사본 판정표(`f178/verdicts_table.md` · `_canonical_findings` 를 그대로 부름)

| 사본 | 2.37.0 검사기 | 새 정본만 | 새 + 옛 판 자산(채택) |
|---|---|---|---|
| a 옛 정본 그대로 | 통과 | 위반 | 통과 |
| b 옛 정본 + noqa + 서식 고침(현장 꼴) | 통과 | 위반 | 통과 |
| c 새 정본 | 위반 | 통과 | 통과 |
| d · e 옛 정본 ruff format(88 · 홑따옴표) | 통과 | 위반 | 통과 |
| f · g · g2 새 정본 + future · 다시 짬 · isort 한 줄씩 | 위반 | 통과 | 통과 |
| h 함수 안 docstring · i 한 글자 · j C901 손 나눔 · k `TYPE_CHECKING` 옮김 | 위반 | 위반 | 위반 |

### 시험

- `api_error_backstop_matrix.py` 사례(`:7077` 근처): 옛 정본 그대로 0 · 현장 꼴 0 · 옛 정본 + 한 글자 2(위반 글이 옛 판 자산 이름을 댐) · 새 정본 다시 짬 0 · `# noqa: PLR0913` 0 · 함수 docstring 2 · `TYPE_CHECKING` 옮김 2.
- 지금 사례의 기준 글 둘(future 사례 `'"""\nimport copy'` · docstring 사례 «정본(고치지 않는다)»)은 새 정본에서 안 찾아진다 — 그대로 두면 바꿈 없는 헛 초록이다. 고친 글이 원본과 다른지 확인하는 장치를 더하고 `:7077` 위반 글 조각도 바꾼다.
- 되돌아옴 막기: 동작 스모크에 단 하나를 더한다 — probe 요구 목록(`workspace/tools/probe-fixture-requirements.txt` · Makefile `:336`)에 `ruff==0.17.3` 고정 · C90(10) · 기본 규칙 · `format --check` 줄 88 · 130. 요구 목록을 고친 뒤 원본에서 `make probe-env` 를 다시 돌린다(배포 클론은 `.venv-probe` 를 원본에 링크한다 · §11).
- 선택: 옛 자산으로도 스모크 한 번(약 12초).
- 바뀌는 고정 자리: 자산 둘 + Codex byte 미러 둘 · 픽스처 byte 사본 셋 · `manifest_seal.py:66`(옛 자산 더함 · 봉인 대상) · `reverse_coverage.py:181` · `pre_route_canonical_check.py` ①(두 자산 미러) · 그래프 b37 · b42 · b43 · R-3749 · R-2548 · R-1011(새 Expression 셋) → 렌더 · LEDGER · 계수표 · q4 · rulepack · 소스 미러 `workspace/reference/implementation-django-ninja/reference/final.md` · Codex `dddjango-coder/SKILL.md:45` · `dddjango-discipline-reviewer/SKILL.md` 같은 뜻.

### 남는 한계

- 서식이 안 바뀌는 것은 ruff 0.17.3 · 겹따옴표 · 끝 쉼표 고정 · 줄 88 ~ 140 에서만 실측했다(black · pyright 는 못 돌림). 서식만 바뀌면 검사기는 통과한다(g 꼴).
- `ALL` 류 엄격 규칙(TRY · EM · D · PLR)은 여전히 `# noqa` 가 든다 — 문서가 그 길을 밝힌다.
- 퍼즈는 표본이다. 파일이 150줄 늘었다.

### 버린 갈래

- 문서만 고치기 — 흔한 기본(C901 10 · 줄 88)에서 여전히 붉다.
- byte 비교로 조이기 — 모든 포매터가 막힌다.
- 프로젝트 ruff 설정 바꾸기 — 현장 설정은 고치지 않는다.
- 모든 docstring 무시 · TypeAdapter 를 모듈 상수로(검증이 import 때로 옮겨 감) · 오류 글 줄이기(행 시험이 글을 고정).
- 새 정본만 받기 — 동작 이득 없이 이미 착륙한 현장만 다시 옮기게 한다.

## 6. F4-177 — #195 가 도메인 서비스에 넘긴 애그리거트를 «루트 호출 없음» 으로 봄(후보 · 중간 → 넣음)

### 재현

- 장난감 `f177/toy` 31 사례 · `python3 -B <2.37.0>/scripts/check-transaction-boundary.py .` → exit 2 · 31 사례 모두 `[#195]`(39줄).
- 현장 꼴(사례 a) — 유스케이스가 잠근 애그리거트를 같은 BC 도메인 서비스(초대 정책)의 수락 메서드에 넘기고, 그 안에서 애그리거트의 루트 메서드가 상태를 바꾸고, 유스케이스는 저장만 한다 → «save/remove 인자 — 같은 함수 안에서 루트 메서드 호출을 받은 적이 없다».
- 작업 트리 사본 = 2.37.0 = Codex 사본(byte 같음). 판 A 는 이 파일을 안 건드린다.
- 클론: 2.37.0 #195 0줄(ⓓ#355 11줄 · exit 0) — 클론은 이 꼴을 갖지 않는다(고친 길을 클론으로 시험하지 못함 · 회귀 확인만).

### 원인

- `check-transaction-boundary.py:1002-1009` `method_called` 는 같은 함수 안 `Name.m(…)` 의 받는 이름만 모은다. `C.accept(x=…)` 에서는 `C` 만 든다.
- `:1171-1180` save 인자가 `method_called` · `factory_born` 에 없으면 #195.
- `:1181-1183` `self._policy.m(x)` 꼴이면 «UoW 로 쓰기를 하는데 루트 메서드 호출이 0» 줄이 하나 더 선다.
- 단순화는 docstring `:52-55` «지역 흐름만 본다».
- 규칙 #195 는 산문이다 — 명세 `tree-revision-spec.md:524` «상태를 바꾸는 유스케이스는 애그리거트를 건너뛰지 않는다 — 건너뛸 수 있는 것은 조회 전용·순수 위임·외부 조회뿐이다» · 소유 지도 `:175`. 그래프 · alias · rulepack 에 없다.
- 목적 근거(인용만): architecture-ddd §3.2(`final.md:644`) «판정은 애그리거트가, 한 애그리거트에 안 담기면 도메인 서비스가» · `:930` · `:933`.

### 고칠 설계(v1 — 같은 BC 도메인 서비스 **한 홉** · 지역 필드 대입이 있으면 셈하지 않음)

- 판정 문면(docstring #195 항 끝 · 단순화 절에 «도메인 서비스 넘김» 단락):
  > 같은 BC 도메인 서비스(트리 74 ~ 75행 `domain_layer/domain_service/**`)에 넘긴 save 인자는, 넘겨받은 파라미터가 그 몸 안에서 `p.m(…)` 루트 메서드 호출을 받고, 그 몸 어디서도(중첩 범위 포함) 파라미터 너머 바꿈(속성 · 첨자 사슬의 대입 · 덧셈 대입 · 주석 대입 · 지움 · `setattr`/`delattr`/`vars` · `__dict__` · 속성 너머 그릇 바꿈 메서드 `p.<속성>.append(…)` 류)을 받지 않고, 다시 묶이지도 않고, 다른 호출의 인자로 다시 넘겨지지도 않으면(읽기 전용 내장 `isinstance` · `type` · `id` · `repr` · `str` · `len` · `bool` · `hash` 는 넘김으로 치지 않는다) «받은» 것으로 본다. 유스케이스 안에서 그 인자가 같은 꼴의 바꿈을 받았으면 서비스 쪽 루트 호출로 가리지 않는다. 서비스 안에서 다시 넘긴 것은 따라가지 않고 «받지 않음» 으로 본다.
- 따라가는 꼴(한 홉 · 검토 m10): `f(…)`(최상위 동기 def) · `C.m(…)`(staticmethod · classmethod) · `self.<속성>.m(…)`(`__init__` 이 `C` 로 주석한 파라미터나 `C()` 로 한 번만 물린 속성). import 는 최상위 절대 import 만.
- 따라가지 않는 꼴(지금처럼 위반): 두 홉(서비스 안 `cls.m` · `self.m` · 형제 서비스 · 모듈 도우미) · `C().m(…)`(현장 근거 없음) · 다른 데코레이터 · 클래스 데코레이터 · metaclass · 상속 메서드 · 별표 풀기 · `**` · 가변 인자 자리 · 다시 묶인 이름 · 다른 BC · 응용 층 도우미.
- **검토 B1 반영** — v0 시제품은 서비스 안 «root»(조회 메서드 포함)를 `method_called` 에 더해, 지역 필드 대입(`attr_assigned`)을 가렸다. 그래서 «조회 정책을 부른 뒤 유스케이스가 필드를 직접 바꿈» 을 2.37.0 은 잡고 v0 는 놓쳤다.
- **재확인 N1 반영(v2)** — v1 의 한 줄 고침(`and n not in attr_assigned`)은 `x.f = v` 한 꼴만 막았다. `+=` · `x.f: T = v` · `x.a.b = v` · `x.t[k] = v` · `del x.f` · `setattr(x, …)` · `x.items.append(v)` 는 여전히 서비스 조회로 가려졌다(운영자 재현 — 2.37.0 7 사례 각 1줄 · v1c 0 · `op-repro`). v2 는 지역 «가리지 않음» 집합을 **서비스 쪽 우회 판정과 같은 술어**로 만든다: 과녁이 Store/Del 인 Attribute · Subscript 사슬의 뿌리(AugAssign · AnnAssign 포함) · `setattr`/`delattr`/`vars` 의 첫 인자 · `x.<속성>.m(…)` 의 뿌리 가운데 `m` 이 그릇 바꿈 메서드 이름(`append` · `extend` · `insert` · `remove` · `pop` · `popitem` · `clear` · `update` · `add` · `discard` · `setdefault` · `sort` · `reverse` · `__setitem__` · `__delitem__`)인 것 — 이 이름은 서비스 «root» 로 가리지 않는다(검토 `review-checkers/scripts-v1g`). 아무 `x.<속성>.m(…)` 이나 세면 값 객체 읽기(`p.period.contains(now)` · `p.profile.is_public()`)까지 «바꿈» 이 되어 F4-177 의 뜻한 통과가 다시 붉어진다(셋째 확인 A · 운영자 재현 — v1d 는 `q_local_vo_read` · `q_isinstance_service` 를 붉힘 · v1g 는 통과).
- **재확인 N2 반영(v2)** — v1 의 한 홉은 서비스가 파라미터를 다른 호출의 인자로 다시 넘기면 따라가지도 막지도 않고, 그 몸에 `p.m()` 이 하나 있으면 «root» 로 봤다. 그래서 «조회 뒤 도우미 · 형제 서비스에 넘겨 필드를 바꿈» 을 2.37.0 · v0 는 잡고 v1 은 놓쳤다. v2 는 한 홉에서 파라미터를 다른 호출의 인자로 넘기면 그 서비스 결과를 «none»(fail-closed — 지금처럼 위반)으로 본다(`scripts-v1d`). 읽기 전용 내장(`isinstance` · `type` · `id` · `repr` · `str` · `len` · `bool` · `hash`)에 넘긴 것은 넘김이 아니다(셋째 확인 B · `scripts-v1g`). 현장 꼴 a 는 다른 파라미터만 넘겨 영향이 없다.
- **재확인 N3(선택 → 받음)** — 서비스 쪽 우회 판정에도 같은 그릇 바꿈 메서드 술어(`p.<속성>.append(…)` 류)를 넣는다 — 2.37.0 이 잡던 꼴이고 «멈추는 쪽이 기본» 이다. 장난감 31 사례 출력은 그대로다(셋째 확인 · `scripts-v1g` · 운영자 확인).
- v0 의 «순수한 넓힘 — 새 위반 0» 은 **틀렸다**(위 손실). v2 는 2.37.0 이 잡던 꼴을 모두 잡는다 — 장난감 31 + 검토 사례(`f177/` 의 13 사례)에서 2.37.0 위반 줄 집합 ⊇ v2 위반 줄 집합이고, 빠지는 줄은 «서비스 한 홉 안 루트 호출 · 넘김 없음 · 지역 변경 없음» 꼴(a · a2 · b2 · g3 · f1 · f2 · f4 ~ f6 · 검토 `query_method_service`)뿐이다. 운영자 확인: `scripts-v1d` · `scripts-v1g` 의 장난감 31 출력이 v1c 와 byte 같고(29줄 · exit 2) · 클론 출력도 v1c 와 byte 같다(11줄 · exit 0). 검토 장난감 18 사례에서 v1g 는 바꿈 꼴 12 를 모두 붉히고 뜻한 통과 다섯(`query_method_service` · `q_plain_root` · `q_vo_read_service` · `q_local_vo_read` · `q_isinstance_service`)을 통과시킨다.
- 새 이유 문면 둘(기존 문면 무변):
  - «save/remove 인자 — 넘긴 도메인 서비스 `X.m` 안에서 루트 메서드를 건너뛰고 필드를 직접 바꾼다 — 상태 변경은 애그리거트를 건너뛰지 않는다»
  - «… — 넘긴 도메인 서비스 `X.m` 안에서도 루트 메서드 호출을 받지 않았다 …»
- 후보 채널은 쓰지 않는다.
- 규칙 글: 명세 #195 행에 «같은 BC 도메인 서비스에 한 번 넘겨 그 안에서 루트 메서드를 부른 것도 «받음»(유스케이스가 그 인자의 필드를 직접 바꾸지 않을 때)» 한 마디(산문 · 그래프 무변).

### 시험

| 사례 | 꼴 | 기대 | 2.37.0 | v0 시제품 | v1(한 홉 + B1) |
|---|---|---|---|---|---|
| a · a2 | 현장 꼴(키워드 · 위치) | 통과 | 위반 | 통과 | 통과 |
| b | 서비스가 읽기만 | 위반 | 위반 | 위반 | 위반 |
| b2 · g3 | 조회 메서드(`is_active()`)만 | 통과(한계) | 위반 | 통과 | 통과 |
| c · c2 · c3 | 필드 직접 대입(c2 = 루트 호출도 · c3 = 둘째 홉) | 위반 | 위반 | 위반 | 위반 |
| d1 · d2 · d3 | 다른 BC 서비스 · 같은 파일 함수 · `self._` 도우미 | 위반 | 위반 | 위반 | 위반 |
| e1 ~ e4 | 두 홉(형제 서비스 · 모듈 도우미 · `cls._` · `self._`) | 위반(한계 · 현장 근거 없음) | 위반 | 통과 | **위반** |
| e5 | 순환 A → B → A · 루트 호출 0 | 위반 | 위반 | 위반 | 위반 |
| f1 · f2 | 주입 속성 · `C()` 로 한 번 물린 속성 | 통과 | 위반 | 통과 | 통과 |
| f3 | `C().m` | 위반(한계 · 현장 근거 없음) | 위반 | 통과 | **위반** |
| f4 ~ f6 | classmethod · 모듈 함수 · 파라미터 이름 다름 | 통과 | 위반 | 통과 | 통과 |
| f7 | 서비스 안 별칭 `t = p; t.m()` | 위반(fail-closed) | 위반 | 위반 | 위반 |
| f8 · f9 | 별표 풀기 | 위반 | 위반 | 위반 | 위반 |
| g · g2 | 루트 호출이 다른 파라미터에만 · 키워드 뒤바꿈 | 위반 | 위반 | 위반 | 위반 |
| i · j · k · h | 다시 묶음 · 속성 두 번 대입 · 다른 데코레이터 · 함수 안 가림 | 위반 | 위반 | 위반 | 위반 |
| 검토 `local_assign_after_query` | 조회 정책을 부른 뒤 유스케이스가 필드 직접 대입 | 위반 | 위반 | **통과(B1)** | 위반 |
| 검토 `local_assign_only` | 서비스 없이 필드 대입 | 위반 | 위반 | 위반 | 위반 |
| 재확인 `r_aug` · `r_annassign` · `r_nested` · `r_subscript` · `r_del` · `r_setattr` · `r_append` | 조회 정책 뒤 유스케이스의 다른 변경 꼴(N1) | 위반 | 위반 | 통과 | 위반(v1 통과 → v2 위반) |
| 재확인 `p_hidden_module` · `p_hidden_sibling` | 서비스가 조회 뒤 도우미 · 형제 서비스에 넘겨 필드 대입(N2) | 위반 | 위반 | 위반 | 위반(v1 통과 → v2 위반) |
| 재확인 `p_field_method` | 서비스가 조회 뒤 `p.items.append(…)`(N3) | 위반 | 위반 | — | 위반(v1 · v1d 통과 → v3 위반) |
| 셋째 확인 `q_vo_read_service` · `q_local_vo_read` · `q_isinstance_service` · `q_plain_root` | 값 객체 읽기 `p.period.contains(…)` · `isinstance(p, …)` 뒤 루트 호출 | 통과 | 위반 | — | 통과(v1d 는 둘을 붉힘 → v3 통과) |

- 합: 장난감 31 사례 위반 줄 2.37.0 39 · v0 19 · v1 27(`f159/tb-f177-scripts-v1c.out` · 한 홉 시제품 `f159/scripts-v1c/`) · 검토 장난감 v1 3(B1 사례 포함).
- 픽스처 `workspace/eval/fixtures/transaction_boundary/service_reach/`(장난감 축약 + B1 사례 + 재확인 N1 의 `+=` · 첨자 · `setattr` · N2 의 두 사례 · N3 사례 · 셋째 확인의 값 객체 읽기 · `isinstance` 통과 사례) · `fixture_matrix.py` 에 literal_loop 선례대로 POSITIVE_LANES 1행 · GROUP_CASES 1행(`^\[(ⓓ)?#195\]` 로 위반 사례 줄 고정 · b2 · g3 · f7 · e1 ~ e4 · f3 은 «받아들인 한계» 로 고정) · MUTATIONS 11행.
- 변이 13: 넘김 인정 걷음 · 필드 대입 막음 걷음 · 파라미터 대응 걷음 · 같은 BC 한정 걷음 · 다시 묶임 걷음 · 함수 안 가림 걷음 · 속성 한 번 대입 걷음 · 데코레이터 한정 걷음 · 별표 풀기 걷음 · 키워드 대응 걷음 · **지역 변경 가림 걷음(B1 사례 통과)** · **지역 가림을 `x.f = v` 대입으로 좁힘(N1 — `+=` 사례 통과)** · **넘김 fail-closed 걷음(N2 — 도우미 사례 통과)** · **그릇 바꿈 메서드 이름 목록을 아무 메서드로 넓힘(셋째 확인 A — `q_local_vo_read` 가 붉어짐)**. 한 홉 한정은 «두 홉 사례가 통과로 샘» 을 GROUP_CASES 고정이 잡는다.
- 골든: `findings_count_matrix` · `checker_baseline_matrix` 를 작업 트리 사본 대 시제품 사본으로 돌려 byte 같다(새 픽스처는 하위 폴더). `gen_pregate_symbol_kinds` 무영향(`.bases` 안 씀). 픽스처 86 폴더 2.37.0 = 시제품.
- Codex byte 미러 `codex-dddjango/skills/dddjango/scripts/check-transaction-boundary.py`.
- 시제품: `f177/scripts-fix-v1/` + `f159/scripts-v1c` 한 홉 스위치 + 검토 `review-checkers/scripts-v1g`(N1 · N2 · N3 · 셋째 확인 A · B) — 구현은 두 홉 코드를 걷어 v0 패치(+303)보다 작게 쓴다.

### 클론 재측정

- 2.37.0 · v1 출력 byte 같음(11줄 · #195 0 · exit 0 · `f159/tb-clone-v1c.out`). 클론의 같은 BC 도메인 서비스 넘김 171쌍은 출력 효과 0 이다(검토 m10).

### 남는 한계

- 조회 메서드도 «루트 호출» 로 센다(b2 · g3) — 지역 판정과 같은 너그러움. 단 유스케이스가 그 인자를 어떤 꼴로든 직접 바꾸거나(B1 · N1) 서비스가 그 인자를 다시 넘기면(N2) 셈하지 않는다.
- 두 홉 · `C().m` 은 따라가지 않는다(현장 근거가 생기면 넓힌다).
- 응용 층 도우미 · 다른 애그리거트의 static 메서드 · `domain_service/` 밖 정책은 따라가지 않는다.
- 「이 도메인 서비스가 정당한가」 는 의미 위반이라 감수 · check-domain-model #301 후보의 몫이다.

### 버린 갈래

- 넘기기만 하면 후보로 — 필드 대입 · 다른 BC · 다른 파라미터를 모두 후보로 내려 막을 것을 놓친다(30/31 후보).
- 못 풀면 후보 — d 를 약하게 만들고, 뒷받침할 현장 사례가 없다. CLAUDE.md «멈추는 쪽이 기본» 과도 어긋난다.
- 두 홉까지(v0) — 현장 수혜는 꼴 a 하나이고 클론 효과 0 이라 범위 · 변이만 키운다(검토 m10).
- 불린 메서드가 정말 상태를 바꾸는지 애그리거트 클래스까지 보기 — 지역 판정보다 엄격해져 기준이 갈린다.

## 7. 트리 파이프라인 계획

차례(한 사람이 한 번에 · 병렬 금지 — 생성물이 서로 물린다):

1. `docs/master/mkrev2.py` — 미리보기 `patch.py` 의 바뀜을 정본에 옮긴다(§1 «트리 172 ~ 182행» 의 옮길 때 규칙대로).
   - `GROUPS`(`:471`)와 순서 assert(`:483`)에 `cross_context/`.
   - `ROWS` 끝에 11행 · `PARTS`(`:492`)에 파트 `cross` · `_PROWS`(`:833`)에 `"cross"`.
   - `WHAT` 172 ~ 182 · `assert len(WHAT) == 182`(`:1634`) · `NAMES` 172 ~ 179 · `_NMR`(`:1881`) 확인.
   - 안내 글 «현행 표준: 2026-10-04 결선 재료 칸 반영. 171행의 경로…»(`:6657`) — 숫자와 날짜 · 이름을 새 판으로. 카드 60 머리 글(`:6278`)은 그 결정 때의 내력이라 **고치지 않는다**.
   - D8 툴팁 리프 수(`:6506` 한 자리) — «무접미 30 → 32 · 자리 33 → 34 · 고정 이름 22 → 25»(`:7070-7071` assert 가 대조 · 검토 확인).
   - F4-158 · F4-175 · F4-174 의 행 설명(`:374` · `:378` · `:428` · `:432` · `:433` · `:434` · `:1043` · `:1681`) — 같은 생성에서.
   - `SWAPPABLE_ROWS` · `GROUPABLE_ROWS` 무변.
2. `python3 -B docs/master/mkrev2.py` → `docs/master/file_tree.html` 다시 생성. 함께 바뀌는 `workspace/design/2026-08-07-decision-record.md` 는 **되돌린다**(CLAUDE.md — 고치지 않은 생성기도 결정 기록을 다르게 쓰므로 «차이 0» 을 조건으로 걸지 않는다).
3. `workspace/tools/tree_mirror_check.py` — `TREE_ROW_COUNT = 182`(`:40`) · docstring · 템플릿 글 «트리 171행»(`:145`) · «최상위 셋(BC·framework·<project>)»(`:191` → «넷») · `:269` 확인. `--write` → `dddjango/scripts/standard_tree.py` · houserules final.md TREE 블록. `--check` 0.
   - 장난감 파이프라인(`f159/pipeline/`)에서 상수 하나만 바꿔 `--write` → `--check` 0 · 낸 행이 손으로 적은 행과 같음을 봤다.
4. Codex byte 미러 `codex-dddjango/skills/dddjango/scripts/standard_tree.py`.
5. `workspace/tools/spec_lint.py` — `TREE_ROW_MAX = 182`(`:53`) · docstring ③(`:13`). `ROW_TO_CHECKER` 는 건드리지 않는다(소유 지도 골격 생성에만 쓰이고 지금도 143 ~ 171행이 없다 · 넣으면 #664 ~ #668 이 layer-skeleton 으로 감 · 검토 M13). `LIVE_CARDS` 무변.
6. 명세 `workspace/design/2026-08-08-tree-revision-spec.md`:
   - 새 행 #664 ~ #668(자리는 `트리 172~182행` · `트리 172·176~179행` 처럼 띄우지 않고 · ③ 커버리지).
   - #490 · #658 · #188 · #101 · #327 · #339 · #347 · #576 · #577 · #392 · #195 행 문면 · 집계표(판정 × 어겼을 때 · 규칙 수 — #188 path −1 · ast +1 · 새 ast 4 · human 1) 재실측.
   - 소유 지도 `workspace/plan/2026-08-11-rule-owner-map.md` — 새 행 664 ~ 668 · **#188 행(`:168`) 등급 path → ast**(⑧ 등급 불일치 방지).
   - 술어 표 `workspace/design/2026-08-11-predicates.md:169`(#347) 고침.
7. 그래프(DEVELOPMENT §3 · 체크리스트 1 ~ 6):
   1. 왕복 확인 — 현행 ttl 을 `canon_turtle` 로 다시 써 byte 같은지.
   2. `ontology/rules/discipline-houserules-final.ttl`:
      - s004-1 `headingSnapshot` «182행» · b3 글 = 3 의 final.md TREE 블록 글(손으로 옮기지 않고 스크립트로 읽어 넣음) · b5 글 + R-3191 리비전 · b7 글 + R-3758 · R-3759.
      - s003-0/b5 + R-3185 리비전 · s008/b5 + R-3716 리비전 · s018-5/b1 글 + R-3757 — 그 글 끝에 빈 줄 하나를 더한다(새 §6 헤딩 앞 구분자 · 블록 구분자는 앞 블록 끝에 붙는다 · 글 재확인 N3).
      - **새 절은 문서 끝(§5 뒤)에 번호 단 헤딩 `## §6 \`cross_context/\` — BC 밖 합성 칸` 으로 붙인다**(키 `s019-6` · 기존 절 키 밀림 0 · 선례 9ef6c4f6 §5 신설 · 가운데 삽입은 원장 부식이라 기각). 차례: houserules final.md 끝에 헤딩 씨앗을 먼저 심음 → 그래프 Section(`sectionNumber "6"` · `sectionOwner owner-graph`) · 블록(R-3753 ~ R-3756) → 아래 6 의 `--apply`.
   3. 나머지 ttl — `discipline-houserules-skill`(R-3112 · R-3125) · `architecture-ddd-final`(R-0122 · R-0124) · `implementation-django-final`(R-3460) · `implementation-test-final`(s021-4.1/b2 코드 글 · R-1816) · `implementation-django-ninja-final`(R-3749 · b42 글 · b43 코드) · `command-dddjango`(R-0194 · R-0338 · R-0340 · R-0341 · R-3520 · R-3433 · **R-3625 는 판 A 의 `@2026-11-14` Expression 글을 그 자리에서 고침** — Norm · Expression 두 노드의 `skos:prefLabel` 을 같이 고치고 `djr:revision` · `djr:revisionKind` 는 판 A 값 그대로 · 글 재확인 N7) · `agent-design-architect`(R-1683 · R-3424 · R-1725 · R-3573) · `agent-design-review-ddd`(R-3394) · `agent-discipline-reviewer`(R-1052 · R-1092 · R-1117 · R-1011) · `agent-coder`(R-2548). 블록 · Norm 은 §8 표.
   4. `ontology/ISSUED` 에 R-3753 ~ R-3759(7 · 판 A 는 ISSUED 를 안 바꿈 — `git status` 확인) · wiring: #664 · #665 · #666 · #668(R-3753 · R-3754 · R-3755 · R-3757) → `enforcedBy` check-context-isolation · #667(R-3756) → `delegatedTo` discipline-reviewer · **R-3758 → check-port-adapter-pairing(#576 · #577) · R-3759 → check-test-config(#392)** · `ontology/wiring/aliases.ttl` rule#664 ~ #668(소유 지도 행이 먼저 있어야 한다 — 6 이 앞선 까닭).
   5. `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_gate.py` green.
   6. 경로 글롭(5 뒤 — `derive_path_globs.section_iri` 가 그래프 질의로 절을 찾기 때문): `workspace/tools/section-path-map.tsv` 에 `discipline-houserules-final	6	172	cross_context/**` 한 행(`tree_row` 는 정수 하나) → 쓰기 실행(플래그 없음)으로 `ontology/wiring/paths.ttl` → `derive_path_globs.py --check`(Makefile `:191`).
   7. `ontology_render.py --apply` — 바뀐 문서 **11** 마다(houserules-final · houserules-skill · architecture-ddd-final · implementation-django-final · implementation-test-final · implementation-django-ninja-final · command-dddjango · agent-design-architect · agent-design-review-ddd · agent-discipline-reviewer · agent-coder).
   8. houserules final.md 가 3 의 `--write` 결과와 TREE 블록 byte 같은지 → `tree_mirror_check --check` 0.
   9. LEDGER — 재투영된 graph 절마다 `sha256(strip_marker(span))` 재기준선 행(사유 `rebaseline:<날짜> 판 B …` · migrated 칸 잇기) + **새 절 `s019-6` baseline 1행**. 판 A 가 이미 덧붙인 행(s005 · s006 · s007 · s011 · s012) 뒤에 잇는다.
   10. 계수표 `workspace/eval/fixtures/ontology_gate/target-counts.json` — NormShape/WorkShape = ISSUED 수(+7) · ExpressionShape += 7 + 26(R-3625 는 그 자리 고침이라 +0) · `AliasEntryShape` +5(rule#664 ~ #668) · `BlockShape` += 새 블록 수(§6 블록 · s018-5 · s004-1/b7 에 블록을 더하면 그만큼) · `SectionShape` +1 · q4 골든 `query_golden_check.py --emit`.
   11. `make rulepack`(소성물 둘 함께).
   12. 소스 미러 `workspace/reference/<skill>/reference/final.md` — 고친 graph 절은 옛 절을 새 절로 손으로 바꾸고, houserules 새 §6 은 소스 미러 **끝에 같은 절을 붙인다**(`corpus_mirror_sync._excise_graph_sections` 는 그래프 절마다 기준선 해시가 맞는 스팬 1건을 요구) → `corpus_mirror_sync.py --write` → `--check`(판 A 교훈: 그래프 절 재기준선 때 소스 미러 절도 손으로).
   13. `make verify-ontology`.
8. «171» 글 자리(대부분 graph-owned → 7 에서 함께):
   - 바꿈(트리 행 수를 뜻함): 조정자 registry #4(`commands/dddjango.md:190` · R-0338) · discipline-reviewer `:109`(R-1052) · design-architect `:72`(R-1683) · **design-architect `:92`(R-3424) · Codex `dddjango-design-architect/SKILL.md:86`** · houserules SKILL `:29`(R-3112) · Codex 짝 · `README.md:145`(«표준 트리 골격(171행)») · `docs/DEVELOPMENT.md:72` · `check-layer-skeleton.py:4` · `workspace/tools/reverse_coverage.py:11` · `:112` · `design_pregate._repo_root_packages` docstring «→ {application, framework}»(`:4923` → 셋).
   - **바꾸지 않음**(«BC 골격 171행» — BC 골격의 뜻이라 182 로 바꾸면 BC 밖 행까지 BC 가 가진다는 글이 된다 · 운영자 처분): houserules SKILL 머리 description · `README.md:226` · `docs/master/master.html:126`.
   - houserules SKILL `:30`(R-3125)의 Codex 짝 `dddjango-discipline-houserules/SKILL.md:26` 도 같은 뜻으로.
   - rulepack 라벨은 `make rulepack` 이 낸다.
9. 확인만: `design_pregate._repo_root_packages()`(`:4922-4930`) 가 `cross_context` 를 저장소 최상위로 세게 된다(자동 · 바랐던 것). check-naming `_TREE_DIR_NAMES`(`:101-113`)에 `backoffice` · `cross_context` 가 들어간다 — 면제 쪽이라 새 줄 없음(클론 27종 byte 같음으로 확인).

## 8. 조정자 · 에이전트 · 스킬 글(모두 graph-owned · Codex 같은 뜻)

### 블록 · Norm 표(검토 I6 — 고칠 블록마다)

| 문서 | 블록 | 고칠 Norm | 바꿈 | Codex 짝 |
|---|---|---|---|---|
| command-dddjango | s005/b8(Phase 0 3번) | R-0194 리비전 | 스캔 범위 · 빚 경로 필터 = 손대는 BC + 실행이 쓰면 `cross_context/`(#668 특례 없음 — §2) | `codex-dddjango/skills/dddjango/SKILL.md` |
| command-dddjango | s012/b4(R1 «대상 BC 경로 필터») | R-3520 리비전 | `cross_context/` 를 쓰는 실행은 그 경로도 적는다 | 같음 |
| command-dddjango | s007/b21 · b23 · b24(registry #4 · #6 · #7) | R-0338 · R-0340 · R-0341 리비전 | 182행 · «BC 밖 합성 칸 import 방향 · 모델 · 날 SQL · admin_view(#664 ~ #666) · admin import(#668)» · «container 위치 — `cross_context/backoffice` 하나 예외(모델 0)» | 같음(`:209` · `:211` · `:212`) |
| command-dddjango | s012/b1(deps 문단) | **R-3625 — 판 A 의 `@2026-11-14` 글을 그 자리에서 고침**(Expression 수 무변 · 체크리스트 1) | «`cross_context/` 파일은 BC 마디가 아니다 — 레인 경로의 공유 표면 · 받는 쪽 시험 · HTTP 소비자로 든다» 한 줄 | 같음 |
| command-dddjango | s006/b9(pre-gate filtered 목록) | R-3433 리비전 | «#188 area 1:1» 예시 뺌 | 같음 |
| agent-design-architect | s005/b21(패키지 구조) | R-1683 리비전 | 182행 · «BC 둘 이상의 값을 한 운영 화면에 보이면 `cross_context/backoffice/<screen>/` — 채널이 아니다» · admin 파일을 만들면 #668 대로 · 고치면 빚 결정대로 모두 걷거나 그대로 | `dddjango-design-architect/SKILL.md:68` |
| agent-design-architect | s005/b24(채널 물음 넷) | R-1725 리비전 | 끝에 «화면에 보이기만 하는 다른 BC 값은 채널을 만들지 않고 `cross_context/` 로 올린다 · 판정에 드는 값만 채널(ACL)» | 같은 절 |
| agent-design-architect | s005/b33(기계가독 채널 · «표준 171행 템플릿») | R-3424 리비전 | 182행 | `:86` |
| agent-design-architect | s008/b4(다른 BC 몫 판정 범주) | R-3573 리비전 | «`cross_context/…` 줄의 갈래는 `공유 표면`(시험은 `받는 쪽 시험`)» | 같은 절 |
| agent-design-review-ddd | s004/b6 | R-3394 리비전 | «… ACL/OHS 로만 명세됐는가 · 여러 BC 값 화면이 `cross_context/` 에서 창구만 부르는가(#664 · #667)» | `dddjango-design-review-ddd/SKILL.md` |
| agent-discipline-reviewer | s007/b28(트리 값) | R-1052 리비전 | 182행 · 소유 절 목록 «§0 ~ §4» 에 «§5 · §6(BC 밖 합성 칸)» 을 더함(#667 이 이 감수자 몫 · 글 재확인 N5) | `dddjango-discipline-reviewer/SKILL.md:102` |
| agent-discipline-reviewer | s007/b43(ⓓ 물음) | R-1092 리비전 | #347 물음 → «업무 규칙 있는 운영 쓰기가 창구로 가나(#668)» | `:119` 근처 |
| agent-discipline-reviewer | s007/b51(admin · 표현) | R-1117 리비전 | «#667 이 화면이 업무 판정을 하나 · 창구 예외를 화면 알림으로 옮기나 · 기능 하나 = 파일 하나(#345 뜻)» · «admin 이 ORM · 폼 · 화면만인가 · 고친 admin 파일의 #668 이 빚 결정대로인가(나)» | 같은 절 |
| agent-discipline-reviewer | s007/b19(정본 대조) | R-1011 리비전 | F4-178 «정본과 코드가 같고(서식 · 주석은 대조 밖)» | 같은 절 |
| agent-coder | s004/b16 | R-2548 리비전 | F4-178 «포매터 · 린터가 바꾸는 서식 · 주석은 받는다» | `dddjango-coder/SKILL.md:45` |
| houserules SKILL | s004-1/b2 · b3 | R-3112 · R-3125 리비전 | 182행 · 시험 자리에 `cross_context/backoffice/test/integration/` | `dddjango-discipline-houserules/SKILL.md:25` · `:26` |
| houserules final · architecture-ddd · implementation-django · implementation-test · ninja | §1 «규칙 글» 표 · §3 · §5 | — | — | `corpus_mirror_sync --write` |

- coder `:47`(BC 밖 슬라이스는 이미 예외 ⑴)는 확인만.
- 산문(NAR) 절은 이 판의 고칠 자리에 없다(검토가 `parse_sections` 로 확인). 만나면 LEDGER 재기준선 행.
- 커맨드 · 에이전트 본문은 런타임 프롬프트다 — 설계 근거 · 판 번호 같은 메타 글을 넣지 않는다.

### 번호 · 채번(구현 때 대장에 커밋 차례로 확정)

| 갈래 | 명세 #N | 그래프 |
|---|---|---|
| cross_context 나가는 import · 모델 · 날 SQL | #664 새 | R-3753 새(houserules 새 §6) |
| BC · framework · `<project>` → cross_context | #665 새 | R-3754 새 |
| `urls.py` 의 `admin_view` | #666 새 | R-3755 새 |
| 업무 판정 0 · 창구 예외 · 한 BC 화면은 BC admin | #667 새(human) | R-3756 새 · `delegatedTo` discipline-reviewer |
| admin import(F4-158) | #668 새 | R-3757 새(houserules §5) |
| fake 변형 · factories 만드는 함수(F4-175) | #576 · #577 · #392 고침 | R-3758 · R-3759 새(§1 «읽는 법» · R-3740 옆) |
| 트리 폐쇄 주어 · 최상위 넷 · #658 | #490 · #658 고침 | R-3185 · R-3191 · R-3716 리비전 |
| #188 · #101 · #327 · #339 · #347 · #195 | 고침(산문 · 명세) | 조정자 예시(R-3433) · 감수 물음(R-1092)만 |
| 그 밖 | — | §8 블록 표의 리비전 |

- 새 Expression 26 = houserules-final 3(R-3185 · R-3191 · R-3716) + houserules-skill 2(R-3112 · R-3125) + architecture-ddd 2(R-0122 · R-0124) + implementation-django 1(R-3460) + implementation-test 1(R-1816) + ninja 1(R-3749) + 조정자 6(R-0194 · R-0338 · R-0340 · R-0341 · R-3520 · R-3433) + design-architect 4(R-1683 · R-1725 · R-3424 · R-3573) + design-review-ddd 1(R-3394) + discipline-reviewer 4(R-1052 · R-1092 · R-1117 · R-1011) + coder 1(R-2548). 판 A Expression 고침 1(R-3625).
- 일꾼 시제품 둘이 같은 번호를 썼다(F4-158 = #664 · F4-175 = R-3753~). 위 표가 정한다.
- 다음 R 은 R-3753 이다(ISSUED 끝 R-3752 · 판 A 무변).

## 9. 대상 코드 이관 · 빚 셈

- 새 규칙이 기존 코드를 빚으로 만드는 곳(클론 기준):
  - #664 · #665 · #666 · #667 — 0(클론에 `cross_context/` 없음 · BC → `cross_context` import 0).
  - #668 admin import — **61 파일(61줄) · 16 BC**(§2). 가장 큰 새 빚이다 — 다른 빚과 같이 센다(사용자 결정 · §2 «빚 범위»).
  - #188 — 8 → 6(2 사라짐 · 6 문구 바뀜 · 새 줄 0).
  - #576 1 → 1(문구만) · #392 0 · #195 0(클론에 그 꼴 없음) · #63 0(옛 판 정본을 받음 — 현장 꼴 b 도 통과).
- G0 에서 보이는 방식(사용자 결정 — 다른 빚과 같이):
  - BC 리팩토링 G0 빚 스캔은 `application/<대상 bc>/` 경로 진단을 센다 — #668 줄도 그 BC 빚으로 뜬다(B1 «항상 정리»).
  - 기능 · 수정 실행 G0 에도 그 BC 의 #668 줄이 모두 뜬다(16 BC · 61 파일 가운데 그 BC 몫) — ⓐ 지금 정리 / ⓑ 미룸 · 상시 미룸이면 미뤄짐. 새로 만드는 admin 파일은 새 줄이라 G2 가 막는다.
  - `cross_context/` 진단은 그 칸을 쓰는 기능 · 수정 실행의 빚이다(§1 물음 11).
- 이관 차례(대상 저장소 · 플러그인 일 아님 · 배포 보고 · 작업 리스트에 적음):
  1. **정지 · 판촉 화면을 `cross_context/backoffice/` 로 — 기능 · 수정 실행으로.** 까닭은 하나 — 리팩토링 deps 가 순환에 든 BC 를 «지원 안 함» 으로 받지 않아 순환을 푸는 일 자체는 리팩토링으로 못 한다.
     - 정지: 이용 정책 BC 의 계정 BC ACL(손님 찾기)과 그 포트 · 닉네임을 쓰는 유스케이스 셋의 그 몫을 걷고, 화면이 계정 BC 닉네임 찾기 창구와 이용 정책 BC 정지 창구를 부른다. 운영자 메뉴의 이동 목적지 한 줄이 바뀐다.
     - 판촉: 변경 폼이 브라우저로 부르던 세 BC API 를 각 BC 창구로 바꾸고, 판촉 쓰기는 판촉 BC 창구로.
     - 이 기능 실행도 손대는 BC 의 #668 몫을 G0 빚 질문으로 받는다 — 그 BC 전체(이용 정책 BC 6 파일 · 판촉 BC 8 파일 · 계정 BC 1 파일 · 정지 · 판촉 admin 이 옮겨 가면 그 파일 줄은 함께 없어짐).
  2. 그 뒤 계정 BC · 이용 정책 BC · 캐릭터 BC · 판촉 BC 리팩토링이 deps 를 지난다(판 A 착륙 판정과 함께).
  3. 나머지 BC admin 은 그 BC 리팩토링이 #668 빚으로 갚는다 — 다른 BC 값을 보이기만 하는 화면(예: 신고 화면의 닉네임 · 대화 요약 설정의 지시 글 · 설문의 카드 폼 이름)은 `cross_context/`, BC 사이 업무 행위(예: 신고 글쓴이 정지)는 자기 창구 → 자기 유스케이스 → ACL, 규칙이 DB 에 다 걸리는 쓰기(예: 이용 한도)는 ORM.
     - 화면 이전이 밖 동작(주소 · 메뉴)을 바꾸면 리팩토링 정의대로 운영 전이면 G1 V 표 승인으로 받고, 운영 뒤면 기능 · 수정 실행으로 한다.
     - 간접으로 다른 BC 값을 쓰는 admin 파일은 클론에 15(6 BC · `f159/admin_acl_builders.out`) — 모두 #668 빚 61 파일 안에 든다.
- 배포 보고에 적을 것: 리팩토링 G0 에 #668 빚이 새로 뜨는 BC 와 파일 수 · (가면) 기능 · 수정 실행에도.

## 10. 문서 · 요청 가이드

- 사용자에게 보이는 동작이 바뀐다 — 배포 전에 고친다(DEVELOPMENT §6 «문서 현행화»).
  - `README.md` — `:145` 182행 · 핵심 규약 줄에 «여러 BC 운영 화면은 `cross_context/backoffice/`» · «admin 은 ORM · 폼 · 화면만». `:226` «같은 171행 트리» 는 BC 골격 뜻이라 그대로(§7 8). 판 A 가 이미 `README.md` 를 고쳤다(작업 트리) — 그 위에 덧쓴다.
  - `docs/master/file_tree.html` — §7 생성물(공개 문서 — 현장 이름 없음).
  - `docs/master/master.html` — 아래쪽 «기준 판» 줄(판 A 와 같이 2.38.0). `:126` «BC 골격 171행» 은 그대로.
  - `docs/master/work_flow.html` · `work_flow.spec.json` — 스캔 범위 · 트리 행 수 글이 없어 바꿀 것 없음(검토 확인).
  - `docs/DEVELOPMENT.md:72` 182행.
  - `docs/master/work_list.html` — 배포 뒤 F4-159 · 158 · 175 · 177 · 178 · 174 지움 · 이관 차례(§9) 한 줄 · 다음 판 후보 «#188 을 손님 API 없는 BC 로 — 기동 전용 영역 자리 먼저».
- 요청 가이드(`dddjango/REQUEST_GUIDE.md`) — **바뀔 것 없음**(판 B 몫). 요청은 «필요한 동작» 만 적고 자리는 플러그인이 정한다. 예시는 한 BC admin 읽기뿐이라 자리 지시가 없다. `<영역>` 은 `application/` 아래 그대로다(물음 12). 판 A 의 착륙 한 줄은 판 A 몫이다.

## 11. 크기 · 차례 · 병렬 단위 · 검사

### 단위(맡은 파일이 겹치지 않게)

| 단위 | 맡은 파일 | 크기 | 먼저 |
|---|---|---|---|
| T 트리 | `docs/master/mkrev2.py`(172 ~ 182행 · admin · feature · factories · fake · test 설명 · #188 글) · `file_tree.html` · `tree_mirror_check.py` · `standard_tree.py`(+Codex) · `spec_lint.py` · 명세 · 소유 지도 · 술어 표 | M | 판 A 커밋 뒤 |
| G 그래프 | `ontology/**` · 투영 md 11 · 소스 미러 · Codex 같은 뜻 · `section-path-map.tsv` · 계수표 · q4 · rulepack(§8 표 전부 · F4-178 · F4-175 몫 포함) | L | T 뒤(TREE 글이 T 생성물) |
| C1 cross_context 검사기 | layer-skeleton · app-container · public-surface(+Codex) · 픽스처 `skeleton/*_cross` · `app_container/` 사례 | M | T 의 `standard_tree.py` 뒤 |
| C2 context-isolation | `_check_cross_context` · F4-158 `_scan_admin_imports`(+Codex) · 픽스처 `context_isolation/cross_*` · `admin_imports` | M | 판 A 커밋 뒤 · C1 과 병렬 |
| C3 #188 | `check-usecase-dto-placement.py`(+Codex) · 픽스처 `usecase_dto/entrance_pairs` | S ~ M | 병렬 |
| C4 시험 재료 | `check-port-adapter-pairing.py`(판 A 파일 · #576 자리만) · `check-test-config.py`(+Codex) | S ~ M | 판 A 커밋 뒤 · 병렬 |
| C5 #195 | `check-transaction-boundary.py`(+Codex) · 픽스처 `transaction_boundary/service_reach/` | S ~ M | 병렬(판 A 와 무관) |
| C6 F4-178 | 자산 둘(+Codex) · `check-openapi-error-declaration.py` `:3719` · `:4357`(+Codex) · 픽스처 byte 사본 셋 · `manifest_seal.py` · `reverse_coverage.py` · `pre_route_canonical_check.py` · `api_error_backstop_matrix.py` 사례 · 스모크 ruff 단 · `probe-fixture-requirements.txt` | M | 병렬(그래프 몫은 G 에 넘김) |
| C7 #101 부칙 | `check-composition-root.py`(+Codex) · 픽스처 `composition_root/admin_window` | S | C2 와 함께 |
| R refactor_audit | `_dddjango_run` 두 자리(+Codex) | S | 판 A 커밋 뒤 |
| X 함께 고치는 시험 파일(운영자가 모아 넣음) | `workspace/tools/fixture_matrix.py`(C1 · C2 · C3 · C5 · C7 의 GROUP_CASES · MUTATIONS) · `field_report_checker_smoke.py`(C3 골든 · C4 변이 · 판 A 미커밋 위) · `refactor_audit_fixture_run.py`(R 의 RD 사례 넷 · 판 A 미커밋 위) | S | 일꾼은 행 · 사례 글을 자기 폴더에 내고 운영자가 한 번에 넣는다 |
| D 문서 | README · `docs/master/` · DEVELOPMENT · 판 기록 | S | 마지막 |

- 병렬로 돌릴 수 있는 것: C1 ~ C7 · R(서로 파일 안 겹침 · 공유 시험 파일 셋은 X 로 모음).
- C · R 일꾼은 맡은 픽스처 러너 · 스모크만 돈다. `make verify` 는 G · 골든 · 봉인 뒤 한 번만 — G 가 도는 동안 그래프 · 투영 · rulepack 이 어긋나 단마다 붉고, 일꾼 둘이 함께 돌면 임시 파일 경합이 난다(DEVELOPMENT §5).
- 모든 일꾼 · 운영자 실행은 클론 · 장난감에서 `DJR_VIOLATIONS_DIR=<자기 scratch 폴더>` 를 붙인다.
- 차례: 판 A 커밋(LEDGER · rulepack · 계수표 · smoke · `refactor_audit_fixture_run.py` · `pregate_symbol_kinds` 를 판 A 가 미커밋으로 들고 있다) → T → (C1 ~ C7 · R 병렬 · G 는 T 뒤 혼자) → X 모아 넣기 → 골든 · EXPECTED 갱신(체크리스트 8 — `findings_count_matrix` · `checker_baseline_matrix` · `checker_cross_matrix --emit-expected` · `construct_drift_report --emit-expected` · `gen_pregate_symbol_kinds`) → 요구 목록을 고쳤으면 원본에서 `make probe-env` 다시 → 봉인 ① → 커밋 → 검사 → D.

### 검사 고르기(DEVELOPMENT §5)

- 바뀐 경로에 `dddjango/` · `codex-dddjango/` · `ontology/` · `workspace/tools/` · `workspace/eval/` 가 들어 있다 → **`make verify` 전체**, rulepack · selector 가 바뀌므로 **`make verify-mutation`** 도. 커밋 뒤 push 전에 한 번.
- `docs/master/file_tree.html` · `mkrev2.py` → `tree_mirror_check.py` · `spec_lint.py`(verify 안에서 돈다 · 생성 직후 따로 한 번).
- `README.md` · 요청 가이드 → 요청 가이드 대상 명령(cmp · `request_guide_contract.py` · `reverse_coverage.py`).
- dddjango-web 은 안 바뀐다 → `make verify-web` 없음.
- 봉인: 봉인 대상(측정 도구 · byte 골든 · 매트릭스 · 새 자산)을 바꾸므로 커밋 직전 ① · 배포 커밋 뒤 chore ②(DEVELOPMENT §4).
- `claude plugin validate dddjango --strict` — 매니페스트 · 구조는 안 바뀌지만 새 최상위 칸을 문서가 가리키므로 배포 전 한 번.

## 12. 계획 승인 때 알릴 것(묻지 않음 · 이의 시 뒤집음)

- ① 여러 BC 운영 화면은 Django admin 첫 화면 목록에 안 뜬다 — 링크(`reverse("backoffice:<screen>")`)로 연다. 대상 저장소는 운영자 메뉴가 이미 admin 밖에서 admin 주소로 보낸다. 목록에 띄우려면 `admin/app_list.html` 덮어쓰기 한 행이 더 든다(정한 파일 목록 밖).
- ② F4-158 의 금지에 `composition_root` · 저장 어댑터(`persistence/`) · 자기 ACL(`anticorruption_layer/`)을 넣었다 — 결정 글은 도메인 · 응용 둘을 적었지만, admin 이 그 셋으로 유스케이스 · 도메인 객체 · 다른 BC 값을 받으면 같은 일을 이름만 바꿔 한다. 클론 붉은 파일 수는 61 그대로다.
- ③ `cross_context/` 화면의 시험은 다른 BC 데이터를 그 BC 의 화면 · API · 창구 · 플랫폼 API 로만 만든다(#385 의 뜻을 따른 설계 처리).
- ④ 순환을 푸는 정지 · 판촉 화면 이전은 리팩토링이 아니라 기능 · 수정 실행이다 — deps 가 순환 BC 를 받지 않는다(§9).
- ⑤ `unit/` 은 지금처럼 `factories/` 를 못 쓴다 — 만드는 함수는 integration · e2e 가 쓴다(§3 · #388 그대로).
- ⑥ `factories/` 의 만드는 함수는 이름이 `make_` 로 시작해야 한다(그 밖의 공개 함수 — 예: `build_account()` · `create_account()` — 는 #392 · 클론 영향 0). 변형 페이크는 기본 페이크가 옆에 있어야 하고 선언을 바로 상속한다.
- ⑦ factory_boy 파일 안의 공개 도우미 함수(예: `random_bio()`)가 새로 #392 에 걸린다 — 클론 · 픽스처에는 0 이다.
- ⑧ #188 은 이 판에서 손님 API 있는 BC 범위 그대로다 — 손님 API 없는 BC 로 넓히면 기동 배선만 부르는 영역이 고칠 자리 없이 붉어져, «기동 전용 영역의 자리» 를 정하는 다음 판으로 미룬다.
- ⑨ admin 이 자기 창구를 부르려면 #101(driving 을 안쪽에서 import 금지)에 부칙 한 줄이 든다 — 결정을 따르는 데 꼭 필요하다.
- ⑩ F4-178 — 경로 앞 응답 정본 파일이 302 → 451줄로 늘고, 옛 판(2.37.0) 정본도 계속 받는다. 이미 옮긴 저장소는 아무것도 안 해도 된다.
- ⑪ F4-174 는 2.34.0 에서 이미 고쳐졌다 — 장부에 그렇게 적는다.
- ⑫ (사용자 결정의 따름) 옛 admin 파일의 #668 을 미루면 그 파일의 걸린 import 는 그대로 두고, 정리하면 그 파일 몫을 모두 걷는다 — 고친 파일에서 일부만 걷으면 G2 가 막는다(줄이 파일당 하나라서).
- ⑬ `cross_context/` 의 주소는 `backoffice/urls.py` 한 파일에만 적고, `<project>/` 는 그 파일 하나만 문자열로 넣는다 — 다른 `cross_context.` 문자열 연결은 막힌다(#665 · #666).
- (v0 의 ⑩ «#668 이 G0 빚을 늘린다» 는 알림에서 빼고 사용자 질문으로 옮겼다 — §2 «빚 범위».)

## 13. 판 A 와 겹치는 파일

| 파일 | 판 A 가 고친 자리 | 판 B 가 고칠 자리 | 겹침 |
|---|---|---|---|
| `check-context-isolation.py` | docstring · `_WindowTry` · `_check_acl` 묶음 | 새 함수 둘(`_check_cross_context` · `_scan_admin_imports`) · `main` · `_scan_imports` 첫 줄 · docstring 다른 줄 | 함수 겹침 없음 · 같은 파일이라 판 A 커밋 뒤 |
| `check-port-adapter-pairing.py` | 머리글 · `_check_fake` 뒤 블록 · `_check_use_side`(#134 · F4-170) | 머리글 fake 줄 · `_check_fake` · 새 `_fake_declaration` | 같은 줄 없음 · 머리글이 붙어 있어 판 A 위에서 고친다 |
| `refactor_audit.py` | `_dddjango_run` 두 자리(`_line_marked` · `run.line_g0`) · `_Landing` · `_active_runs` · `_supplier_state` · `run-state` | `_dddjango_run` 보류 줄 · 경로 필터 줄 | 같은 함수 · 다른 줄 — 판 A 커밋 뒤 함수 이름으로 건다 |
| `check-naming.py` · `folder_group.py` · `check-api-error-controller-contract.py` | 판 A | 없음 | — |
| `check-usecase-dto-placement.py` · `check-composition-root.py` · `check-openapi-error-declaration.py` · `check-transaction-boundary.py` · `check-layer-skeleton.py` · `check-app-container.py` · `check-public-surface-annotation.py` · `check-test-config.py` | 없음 | 판 B | — |
| `commands/dddjango.md` · `command-dddjango.ttl` · Codex `SKILL.md` | deps 문단(R-3625 등 Norm 11 · `@2026-11-14`) · 폴더 선택 · 묶음 빚 | Phase 0 3번(R-0194) · R1 경로 필터(R-3520) · registry #4 · #6 · #7 · s006/b9(R-3433) · deps 문단 한 줄(R-3625 그 자리 고침) | R-3625 만 겹침 — 판 A Expression 글을 고친다 |
| `ontology/LEDGER.tsv` · `rulepack.json`(둘) · `target-counts.json` · `pregate_symbol_kinds.json`(둘) | 판 A 가 미커밋으로 들고 있음 | 판 B 도 바꿈 | 판 A 커밋 뒤에 한 번에 다시 낸다 |
| `workspace/tools/field_report_checker_smoke.py` · `refactor_audit_fixture_run.py` | 판 A 미커밋(크게 늘어남) | 사례 · 변이 덧붙임 | X 단위 — 판 A 커밋 뒤 운영자가 모아 넣음 |
| `workspace/tools/fixture_matrix.py` | 없음 | C1 · C2 · C3 · C5 · C7 행 | X 단위 |
| `README.md` · `docs/master/master.html` · `work_flow.*` | 판 A | 숫자 · 한 마디 | 판 A 글 위에 덧쓴다 |

## 14. 남는 걱정 · 장부 · 정리

- 그래프 개정 몫이 크다(새 Norm 7 · 새 Expression 26 · 판 A Expression 고침 1 · 문서 11 재투영 · 새 절 하나). 판 A 의 command-dddjango 리비전과 같은 판 안이라 R-3625 는 새 Expression 을 겹쳐 만들지 않는다.
- 클론에는 `cross_context/` 가 없어 새 검사기 길은 장난감으로만 시험했다. 첫 이관 실행이 실례다.
- #668 빚 범위는 사용자 결정(다른 빚과 같이)으로 확정했다 — 기능 · 수정 실행의 G0 빚 질문이 커지는 비용은 배포 보고 · 요청 가이드 확인 줄에 적는다.
- F4-178 옛 판 자산은 2.37.0 정본을 계속 짊어진다 — 정본 TypedDict 가 바뀌는 판에서 뺀다.
- 장부 처분(배포 뒤 · 사용자 로컬): F4-159 · F4-158 · F4-175 · F4-177 · F4-178 수리됨 2.38.0 · F4-174 «2.34.0 에서 고침 · 2.37.0 재현 안 됨» · 이관 차례는 «대상 코드 몫» 으로 · #188 넓힘은 다음 판 후보로.
- 클론 `.dddjango/violations/` 에 v0 조사 실행(11-14 18:32 ~ 18:49 · `DJR_VIOLATIONS_DIR` 없이 돈 검사기)이 남긴 기록 48 개가 있다(그 앞 01시대 286 개는 판 A 리허설 몫). 클론은 이 일의 scratch 밖이라 이 설계 일에서는 지우지 않았다 — 정리 때 운영자가 지운다(시각으로 가름).
- 이 일의 임시물(`workspace/scratch/pan-b-cross-context/` · `backoffice-tree-preview/` · `admin-cycle-research-1114/`)은 배포 뒤 정리한다 — 뒤 둘은 이 일이 만든 것인지 확인하고 지운다. `bc-label-map.md` 는 판 A · B 기록을 커밋하기 전까지 둔다.

## 15. v1 처분(검토 둘 · 2026-11-14)

검사기 · 도구 검토(`workspace/scratch/pan-b-cross-context/review-checkers/review.md` · 차단 1 · 중요 5 · 사소 10 · 덧붙임 5):

| # | 지적 | 처분 | 반영 자리 |
|---|---|---|---|
| B1 | F4-177 v0 가 «조회 정책 뒤 지역 필드 대입» 을 놓침 · «순수한 넓힘» 거짓 | 받음 — `and n not in attr_assigned` 한 줄 · 픽스처 사례 · 변이 · 주장 고침(운영자도 재현) | §6 |
| I1 | #668 이 `persistence` · ACL 길을 열어 둠 | 받음 — 금지 자리 다섯 · 클론 271 import · 61 파일 그대로 · 알릴 것 ② | §2 · §12 |
| I2 | 모델 모듈 다시 내보내기로 #668 을 비켜 감 · 값 객체 admin 의 길 없음 | 받음 — 한 겹 따라감 · «choices» 처방 걷음 · ORM 값 · 값 객체 규칙 쓰기는 창구 | §2 |
| I3 | #666 이 `+` · `+=` · `.append` · `.extend` · `<project>` 직접 연결을 놓침 | 받음 — #666 은 `urls.py` 의 모든 `path`/`re_path` · #665 에 `<project>/` | §1(시제품 v1 장난감 4줄 · 2줄 실측) |
| I4 | `cross_context/` 의 모델 클래스(`managed=False`) · 날 SQL | 받음 — #664 에 접음(새 번호 없음) · 장난감 실측 2줄 | §1 |
| I5 | #188 넓힘이 고칠 자리 없는 붉음(기동 영역)을 만듦 | 받음 — 운영자 판단 · 이 판은 넓히지 않음 · 다음 판 후보 · 클론 8 → 6 · 픽스처 9 레인 문구만 | §2 · §10 · §12 ⑧ |
| m1 | `from application.<bc> import domain_layer` 꾸러미 꼴 | 받음 — #668 문면 · 픽스처 | §2 |
| m2 | #392 가 제네릭 기저 `DjangoModelFactory[M]` 를 오탐 | 받음 — `ast.Subscript` 풀기 · 장난감 · 변이 | §3 |
| m3 | `create_account()` 안내 · `make_` 약속 | 받음 — 위반 글 «`make_` 로» · 알릴 것 ⑥ | §3 · §12 |
| m4 | F4-178 «N번째» 가 늘 첫 자산과 견줌 | 받음 — 가장 가까운 자산과 견주고 그 이름을 댐 | §5 |
| m5 | G1 전 `cross_context/` 실행의 소비 창구를 deps 가 모름 | 받음 — RD 사례 둘 더 · 한계 기록 | §1 refactor_audit |
| m6 | 함께 고치는 시험 파일이 표보다 넓음 | 받음 — X 단위 · §13 | §11 · §13 |
| m7 | 판 A 가 `_dddjango_run` 두 자리를 고침 · 줄 밀림 | 받음 — 함수 이름으로 · 글 맞춤 | §1 · §13 |
| m8 | 클론 `.dddjango/violations/` 에 기록이 생김 | 받음 — 모든 실행 `DJR_VIOLATIONS_DIR` · 남은 48 개는 정리 몫 | 머리 · §11 · §14 |
| m9 | #668 import 당 한 줄(269) — 질문 네 배 | 받음 — 파일당 한 줄(61) | §2 |
| m10 | F4-177 두 홉 · `cls.`/`self.` 안 홉 · `C().m` 은 근거 없음 | 받음 — 한 홉만(시제품 `scripts-v1c` · 장난감 27줄) | §6 |
| 덧붙임 1 | #664 동적 길 | 한계로 기록 | §1 |
| 덧붙임 2 | `backoffice/static/` 등이 «`panel.py` 부재» 로 남 · 템플릿 하위 폴더 | 받음 — #490 글 한 마디 · 트리 글 «평평하게» | §1 |
| 덧붙임 3 | 변형이 기본 페이크를 상속하면 #577 | 받음 — 규칙 글 «선언을 바로 상속» | §3 |
| 덧붙임 4 | 변형 · 기본 #577 엄격함 차이 | 기록만(이 판 밖) | §3 |
| 덧붙임 5 | 시제품 pairing 의 줄 이음 흔적 | 구현 때 바로잡음 | §3 |

글 · 그래프 · 트리 · 문서 검토(`workspace/scratch/pan-b-cross-context/review-text/review.md` · 차단 1 · 중요 7 · 사소 13):

| # | 지적 | 처분 | 반영 자리 |
|---|---|---|---|
| B1 | ⑩(#668 빚)은 알림이 아니라 사용자 질문 | 받음 — 운영자가 사용자에게 물음(가 · 나 · 추천 나) · 이 설계는 «나» 로 적고 «가» 몫을 둠 · ⑩ 알림 뺌 | §0 · §2 · §9 · §12 |
| I1 | houserules 새 절의 자리 · 헤딩 씨앗 · 원장 · 소스 미러 | 받음 — 문서 끝 `## §6` · 키 `s019-6` · 씨앗 → `--apply` · LEDGER baseline · 소스 미러 붙임 | §7 7.2 · 7.9 · 7.12 |
| I2 | 경로 글롭 단계가 그래프 앞 · `tree_row` 정수 | 받음 — 게이트(7.5) 뒤로 · `172` 하나 | §7 7.6 |
| I3 | «172 ~ 182» 띄운 표기는 끝 두 행만 읽힘 | 받음 — `172~182` 붙여 씀 | §1 · §7 6 |
| I4 | #188 등급 바꿈이 소유 지도에 안 닿음 | 받음 — 소유 지도 `:168` path → ast · 집계표 | §7 6 |
| I5 | R-3758 · R-3759 담당 · 계수표 두 칸 | 받음 — 배선 둘 · `AliasEntryShape` +5 · `BlockShape` · `SectionShape` +1 | §7 7.4 · 7.10 |
| I6 | 블록마다 Norm 미지정 · R-3625 겹침 · 문서 11 | 받음 — §8 블록 표 · R-3625 그 자리 고침 · 새 Expression 26 · 문서 11 | §7 · §8 |
| I7 | 공개 위생(현장 BC · 파일 · 줄) | 받음 — 공용 이름표(`bc-label-map.md`)대로 · 현장 파일 · 심볼 · 줄은 일반 말 · 트리 글 예시도 일반 이름 | 문서 전체 · §1 트리 |
| M1 | 결정 기록 «차이 0» 조건은 늘 멈춤 | 받음 — «되돌린다» 만 | §7 2 |
| M2 | 카드 60 머리 글은 내력 | 받음 — 고치지 않음 · `:6657` 은 날짜 · 이름도 | §7 1 |
| M3 | «171» 쓸기에서 빠진 자리 | 받음 — design-architect `:92`(+Codex `:86`) · SKILL `:30` Codex `:26` · `design_pregate` docstring | §7 8 · §8 |
| M4 | «BC 골격 182행» 은 틀린 글 | 받음 — «BC 골격 171행» 글은 바꾸지 않음(운영자 처분) | §7 8 · §10 |
| M5 | 미리보기 표지 · CSS | 받음 — 칩 «신설» · CSS 손편집 없음 · sub · dim 줄 걷음 | §1 트리 |
| M6 | 자매 대조 까닭 두 줄이 틀림 · 더 센 까닭 빠짐 | 받음 — 첫 까닭 = 사용자 선택 · #667 은 web 보다 엄격(사용자 결정) · #90 논거 뺌 | §1 |
| M7 | 출처 표기 둘 | 받음 — «손님 API» 줄은 결정 아님(출처 바로잡음 · 이 판은 안 넓힘) · 물음 13 · ③ 은 #385 뜻의 설계 처리로 | §1 · §2 · §12 |
| M8 | §12 에 `make_` 알림 | 받음 — ⑥ | §12 |
| M9 | 겹침표 · `make probe-env` | 받음 — `refactor_audit_fixture_run.py` · 요구 목록 뒤 `make probe-env` 다시 | §5 · §11 · §13 |
| M10 | §9 앞뒤 어긋남 · 이관 실행의 빚 질문 | 받음 — 까닭 하나(deps) · 운영 전 G1 V 표 · 이관 실행의 #668 몫 | §9 |
| M11 | 병렬 일꾼 동안 `make verify` 금지 | 받음 | §11 |
| M12 | 술어 표 #347 · 명세 #327 | 받음 | §2 · §7 6 |
| M13 | `ROW_TO_CHECKER` | 받음 — 건드리지 않음 | §7 5 |

- 받지 않은 지적: 없다. 사용자에게 새로 올릴 것은 «빚 범위» 하나뿐이다(운영자가 이미 물음).

## 15-2. v2 처분(좁은 재확인 둘 · 2026-11-14 · `date` 20:03)

- 재확인 글: 검사기 · 도구 `workspace/scratch/pan-b-cross-context/review-checkers/recheck.md` · 글 · 그래프 `…/review-text/recheck.md`.
- 운영자 재현(`workspace/scratch/pan-b-cross-context/op-repro/` · `DJR_VIOLATIONS_DIR` 붙임): N1 · N2 — 2.37.0 · v1c · v1d 를 장난감 `review-checkers/toys/tb` 에 돌려 사례마다 셈(2.37.0 13 사례 · v1c 2 사례 · v1d 9 사례 위반 — 빠진 둘은 `query_method_service`(뜻한 너그러움 b2) · `p_field_method`(N3)) · `f177/toy` 31 사례 v1c = v1d byte 같음 · 클론 v1c = v1d byte 같음. N4 · N5 · N6 · N7 — `scripts-cc1` 을 `toys/cc-route` · `toys/cc-v1` 에 돌려 #664 ~ #666 0줄(경로 · 기저 · 별칭) · `page.cursor()` 오탐 1줄. N8 — `f159/adm668v1.py` 를 `toys/adm2` 에 돌려 여섯 꼴 중 1. 글 N1 — `commands/dddjango.md:114` · `:117`(R-3474 목록) · `:229` 를 읽어 확인.

### 검사기 · 도구 재확인

| # | 등급 | 지적 | 처분 | 반영 자리 |
|---|---|---|---|---|
| N1 | 차단 | B1 고침이 `x.f = v` 한 꼴만 막음 | 받음 — 지역 가림 집합을 서비스 쪽 우회 판정과 같은 술어로(`scripts-v1d`) · 사례 일곱 · 변이 하나 | §6 |
| N2 | 중요 | 한 홉이 서비스 안 넘김을 «없는 일» 로 봄 | 받음 — 한 홉에서 다시 넘기면 «none»(fail-closed) · 사례 둘 · 변이 하나 | §6 |
| N3 | 사소 | 서비스가 필드 메서드로 바꿈 | 받음(선택 → 받음 · 멈추는 쪽) — 서비스 쪽 우회 판정에 `p.<속성>.m(…)` | §6 |
| N4 | 중요 | 문자열 연결로 `admin_view` 없는 주소 | 받음 — #665 `<project>/` 의 `cross_context.` 문자열은 두 꼴만 · #666 `urls.py` 밖 `path` · `re_path` · `Router` 위반 · 사례 · 변이 둘 | §1 규칙 글 · 검사기 · 시험 · §12 ⑬ |
| N5 | 중요 | #664 모델 판정이 이름 하나 | 받음 — import 출처 · 프로젝트 기저 한 번 · 안 `Meta` 의 `db_table` · `managed` · `proxy` · 사례 둘 · 변이 하나 | §1 |
| N6 · N7 | 사소 | 날 SQL 길 빠짐 · `page.cursor()` 오탐 | 받음 — import 출처(`connection` · `connections` · `RawSQL` · 드라이버)로 · 이름 `cursor()` 대조 걷음 · 사례 · 변이 하나 | §1 |
| N8 | 중요 | #668 다시 내보내기가 이름 꼴만 | 받음 — 모듈째 · `import … as` · 대입 별칭 · 상대 import · 속성 쓰기 · 사례 · 변이 하나 | §2 |
| N9 | 사소 | #668 줄 꼴이 G2 차분을 정함 | 받음 — 정렬한 문자열 목록 칸 · 고친 파일은 «모두 걷거나 그대로»(`registry_gate.py:1533` 의 앵커 같음 조건) · 변이 하나 | §2 |
| N10 | 사소 | #668 검사기 시제품 없음 | 받음 — C2 일꾼이 시제품부터(클론 61 · 셈 스크립트 · 검토 장난감 맞춤) | §2 시험 |
| 덧붙임 | — | `import_string("cross_context….")` 동적 길 | 한계로 — #664 동적 길과 같은 몫(감수) | §1 한계 |

### 글 · 그래프 재확인

| # | 등급 | 지적 | 처분 | 반영 자리 |
|---|---|---|---|---|
| N1 | 중요 | «나» 를 G1 배너 빚으로 적어 상시 미룸 · G2 «ⓐ 잔존» 대조 밖 · G1′ 빠짐 | 받음 — G1/G1′ 배너 직전 G0 재승인 빚 질문(`:114` 선례) · R-3474 목록에 한 마디(새 Expression 27) · «기계로 못 막음» 한계 걷음 · 사용자 질문의 «나» 문구를 고쳐 다시 묻는다 | §0 · §2 · §8 · §9 · §12 ⑫ |
| N2 | 사소 | 파일당 한 줄 × 귀속 N ∖ L — 일부만 걷으면 새 줄 | 받음 — 검사기 N9 와 한 처분 | §2 |
| N3 | 사소 | `s018-5/b1` 끝 빈 줄 | 받음 — R-3757 편집에서 빈 줄 하나 | §7 7.2 |
| N4 | 사소 | «houserules §6» 둘 | 받음 — 다른 문서는 «`references/final.md` §6» · R-3460 이름표 그대로 | §1 문서 표 |
| N5 | 사소 | 감수자 소유 절 목록에 새 §6 없음 | 받음 — R-1052 에 «§5 · §6» · s009/b3(R-3564)은 BC 파일만 보는 R2 라 넣지 않음 | §8 |
| N6 | 사소 | SKILL 안 «171» · «182» 나란히 | 받지 않음(선택) — M4 처분대로 description «BC 골격 171행» 은 그대로(뜻이 다름 · 읽는 쪽 혼동은 본문 «§1 트리 182행» 이 풀어 줌) | — |
| N7 | 사소 | R-3625 그 자리 고침의 손 갈 곳 둘 | 받음 — Norm · Expression prefLabel 같이 · revision · revisionKind 판 A 값 | §7 7.3 |

- 다음: 셋째 좁은 확인(검사기 · 도구 쪽 N1 · N2 · N4 · N5 · N8 처분 · 글 쪽 N1 처분만). 셋째에도 차단이 남으면 멈추고 사용자에게 묻는다.

## 15-3. v3 — 사용자 결정 · 셋째 좁은 확인 둘(2026-11-14 · `date` 20:10 ~)

- 사용자 결정(20:10): #668 빚 = 다른 빚과 같이(«가») — §0 · §2 «빚 범위» · §8 · §9 · §12 ⑫ 를 고침 · v2 의 «나» 실현과 R-3474 리비전을 걷음 · 새 Expression 26. 글 · 그래프 셋째 확인의 중요 하나(«재개 G0 에서 #668 이 새 빚으로 다시 뜸» — R-3484 의 새 빚 정의 · `commands/dddjango.md:121` 로 운영자 확인)는 «나» 특례에서만 생기는 구멍이라 이 결정으로 함께 없어진다.
- 셋째 좁은 확인(검사기 · 도구 · `review-checkers/recheck2.md`): 차단 0 · 중요 1 · 사소 여럿.
  - A(중요) — v2 의 `x.<속성>.m(…)` 을 모두 «바꿈» 으로 세면 값 객체 읽기가 붉어져 F4-177 의 뜻한 통과가 되돌아감 → 받음: 그릇 바꿈 메서드 이름 목록으로만(`scripts-v1g` · 운영자 재현 — v1d 붉음 · v1g 통과 · 장난감 31 · 클론 byte 같음) · 변이 하나 · §6.
  - B(사소) — `isinstance(p, …)` 가 넘김으로 셈 → 받음: 읽기 전용 내장 여덟은 넘김이 아님 · §6.
  - §6 판정 문면이 v1 글 → 받음: 바꿈 꼴 · 넘김 fail-closed · 그릇 바꿈 메서드로 다시 씀.
  - #665 설정 모듈 앱 문자열을 자리로 가리면 나눈 목록 · `+=` · 로거 이름이 오탐 → 받음: 설정 모듈 어디서든 값으로 · `include` 튜플 꼴 · §1.
  - #668 `from <모델 모듈> import *` 빠짐 → 받음 · 줄 꼴 조건 둘(줄 번호 없음 · 푼 절대 모듈 경로) → 받음 · §2.
  - N4 ~ N7 은 글로 닫힘 — `scripts-cc1` 은 아직 v1 이라 실행 확인은 구현 몫(C 일꾼이 시제품을 v3 글로 고쳐 검토 장난감 `cc-route` · `cc-v1` 을 모두 맞춘 뒤 픽스처를 굳힌다). 클론 `<project>/` 의 `cross_context.` 문자열 0/1684 — 지금 오탐 0.
- 글 · 그래프 셋째 확인(`review-text/recheck2.md`): 차단 0 · 중요 1(위 사용자 결정으로 없어짐) · N3 · N4 · N5 · N7 닫힘 · N6 이의 없음 · ⑫ ⑬ 숨은 결정 바뀜 없음 · 꼬리 «"나" 면 R-3474» 두 번은 결정으로 걷힘.
- 셋째 확인 뒤 차단 0 — 계획 승인 차례로 간다(남은 중요 둘은 운영자가 재현하고 고쳤고, 글 쪽은 사용자 결정으로 없어짐).
