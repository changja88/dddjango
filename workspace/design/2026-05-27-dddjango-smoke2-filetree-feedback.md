# dddjango 스모크 #2 피드백 로그 — 표준 파일트리 검증 런

작성일: 2026-05-27
대상: 재설치된 플러그인 `dddjango@dddjango-local` (commit `5925ce1` 반영본, user scope)
toy 프로젝트: `~/Desktop/dddjango-smoke/` — **그린필드 리셋**(config + `catalog.Product` 시드만, 확립된 비즈니스 레이아웃 없음). 백업: `~/Desktop/dddjango-smoke-backup-20260527-091808.tgz`
실행 기능: `/dddjango 재고가 부족하면 409로 거절하고, 충분하면 재고를 차감하며 주문을 생성하는 API`
G0 결정: 단일 상품 단건 · 동시 초과판매 방지(보장) · 인증·멱등성 제외 — **스모크 #1과 동일 조건**(파일트리 동작만 깨끗이 비교하려는 의도).

**이 스모크의 목적**: `5925ce1`에서 houserules를 단일 출처로 도입한 **표준 파일트리가 architect→coder→discipline-reviewer로 실제 작동하는지** 동적 검증. 그린필드는 houserules §1의 "확립된 규약 없음 → 표준 적용" 경로를 발동시키려는 셋업.

이 로그는 스모크 진행 중 누적한다. 전체 스모크가 끝나면 입력으로 개선 계획을 세운다. (현재 진행: G1 승인 완료, Phase 2 구현 진입 직전 — coder/discipline-reviewer 관찰은 미완.)

## 1. 통과 확인 (G0~G1)

- ✅ **그린필드 표준 발동**: 명세 §4가 "확립된 규약 없으므로 dddjango 표준 파일트리(`references/final.md`) 적용"을 명시. 그린필드 판정 정확.
- ✅ **#2 공백 닫힘**: 명세 §4 "패키지·테스트 구조 결정 (lens 무관, 항상 결정)"이 1급 섹션으로 존재. 스모크 #1의 최대 공백(구조 무결정, 사용자가 직접 발견)이 닫힘.
- ✅ **4계층 + Data Mapper + 의미군 테스트**: `domain_layer/application_layer/infra_layer/presentation_layer`, 도메인↔ORM 분리, 테스트 `catalog/test/{unit,integration}/`(평면 `tests.py` 탈피).
- ✅ **db lens가 SQLite no-op blocker 재발견**: G0의 `select_for_update`가 SQLite에서 무효임을 독립 발견 → 조건부 원자 UPDATE로 중재. 스모크 #1과 동일 추론 재현(파이프라인 일관성).
- ✅ **G0 요구 사수 중재 + 트레이드오프 G1 격상**: 동시 초과판매 방지 요구를 (a)원자 차감으로 지킴 + race 직접검증은 SQLite 한계로 인수기준 제외(PG 이연). ORM 위치 미해결 옵션을 명세에 남겨 G1에서 객관식 제시 → 표준 Data Mapper 분리(1번) 선택. 설계대로.

## 2. 개선 항목 (스모크 후 계획 대상)

### #A 표준 파일트리의 골격(`application/` 컨테이너 + 4계층)을 YAGNI 면제 구조 불변식으로 격상

- **현상**: architect가 표준 트리를 적용하면서 `application/<app>/{..._layer}` → `catalog/{..._layer}`로 **`application/` 컨테이너 레벨을 생략**(명세 §4.2). 근거로 YAGNI(전역지침 05·03, §6.8): "단일 기능에 새 앱/컨테이너 신설은 과한 구조화".
- **왜 문제 (래칫/락인 실패 모드)**: `application/` 컨테이너는 *기능당 비용*이 아니라 *프로젝트 1회성 기반 골격*이다. YAGNI는 "나중에 필요하면 싸게 추가" 전제인데 여기선 그 전제가 깨진다 —
  1. **retrofit 비대칭**: 지금=빈 디렉터리 하나. 나중=전 앱 이동 + INSTALLED_APPS·app_label·import·migrations 전면 수정(비싸고 위험).
  2. **"기존 규약 존중" 래칫**: feature #1에서 컨테이너를 빼면, feature #2에서 dddjango가 "컨테이너 없는 4계층"을 확립된 규약으로 인식해 현상 유지 → 컨테이너 도입 시점이 구조적으로 영영 도래하지 않음.
  - ∴ YAGNI로 미루면 = 사실상 영구 배제. architect의 범주 오인 = "프로젝트 1회 기반"을 "기능당 비용"으로 취급.
- **정밀 구분 (architect 판단의 절반은 옳음)**:
  - **① 골격**: `application/<app>/` 컨테이너 + 4개 `_layer/` → **의무(YAGNI 면제·구조 불변식)**.
  - **② 계층 내부 2차 분할**: 애그리거트/종류 하위폴더 → **YAGNI 유지(점진적 분할)**. architect의 "각 계층 내부는 평면"은 ②에 대해선 옳다(§2·§6.8).
- **완결 조건 (architect가 주저한 실질 이유까지 풀어야)**: `application/catalog/`는 INSTALLED_APPS `application.catalog`·app_label·모델 발견·migrations 경로 마찰을 부른다(§4.4 ORM 분리 마찰의 확장판). 컨테이너 의무화는 표준이 그 **Django 통합 집행 방안(중첩 패키지 앱 라벨 규약 등)을 §4.4처럼 함께 규정**해야 완결. 이번 스모크의 구현 단계가 그 마찰의 구체 사례를 제공할 것 → 거기서 집행 레시피 추출.
- **단, 적용 경계**: dddjango-관리(그린필드/미조직) 프로젝트에 표준을 *적용할 때*만 의무. 외부의 기존 비-dddjango 레이아웃을 가진 프로젝트는 §1대로 존중(침습 금지). 핵심은 **표준을 처음 까는 그 순간 컨테이너를 박아** 래칫을 원천 차단하는 것.
- **반영 위치(잠정)**: `discipline-houserules` `references/final.md`(① 골격을 YAGNI 면제 불변식으로 명시 + Django 통합 집행 방안) · houserules SKILL.md §1 결정 로직 · `agents/design-architect.md`(컨테이너 생략 금지) · 소스 코퍼스 `workspace/reference/discipline-houserules/reference/final.md` 동기화.
- **의의**: 스모크 #1의 #2(구조 무결정)는 닫혔는데, 닫고 보니 "표준을 적용은 하되 골격을 YAGNI로 침식"하는 한 단계 깊은 결함이 드러남. 이번 스모크 최대 수확.

### #B 명세 내부 일관성 자기리뷰 부재 (G1 전 점검 공백)

- **현상**: G2 규율 감사가 blocker **B1**(도메인 `Product.deduct_stock` 죽은 코드 / 차감 판정이 인프라로 샘)을 잡음. 뿌리는 **명세 §3.4의 내부 모순** — ddd 관점 "도메인이 차감 소유"라 적으면서 같은 절에서 db 중재로 "원자적 인프라 집행"을 채택. 둘의 긴장이 G1에서 화해되지 않은 채 구현으로 넘어갔다.
- **왜 문제**: 모순이 G1을 통과해 coder가 양쪽을 다 구현(도메인 메서드 + 인프라 원자 차감) → 죽은 코드 + 명세-코드 불일치 → G2에서야 발견(늦은 발견 = 재작업). architect의 lens 리뷰는 *정합성*을 보지만, "명세 절 간 명명/소유권/시그니처가 서로 모순 없나"라는 **기계적 자기리뷰**는 공백.
- **해결 (B1 자체)**: (b) 인프라 원자 집행으로 확정 + 죽은 도메인 메서드 제거 + §3.4 정정. DIP는 도메인 소유 포트(`ProductRepository.deduct_stock`)로 유지. 재감사 blocker 0. → 원자적 차감에선 "충분한가" 판정이 원자 쓰기 안에 있을 수밖에 없어 엔티티 메서드로는 안전 소유 불가라는 게 정직한 결론.
- **개선안 (파이프라인)**: design-architect가 lens 리뷰 반영/ G1 전에 **명세 자기리뷰**를 1회 — ① 커버리지(요구·구조결정 추적) ② 플레이스홀더 스캔 ③ **절 간 소유권·명명·시그니처 일관성**(예: "도메인이 X 소유" ↔ "인프라가 X 집행" 모순 탐지). superpowers `writing-plans`(type/naming consistency)·`brainstorming`(internal-consistency) 차용 후보의 강한 실증.
- **반영 위치(잠정)**: `agents/design-architect.md`(명세 자기리뷰 게이트) 또는 `discipline-houserules`에 "명세 자기리뷰" 절. #A와 함께 스모크 후 설계.

## 3. 스모크 종료 채점 (2026-05-27)

- **파일트리 검증 성공 (이번 런 목적)**: 표준 트리가 architect(명세 §4 결정)→coder(`catalog/{..._layer}/` 구축 + §4.4 마찰 집행)→discipline-reviewer(재감사 "4계층 트리 §4.3 일치")→검증보고 전 구간 통과. 지난 #2(구조 무결정) 공백 닫힘 확인.
- **파이프라인 동작**: G0→G1(lens 3종 리뷰·db blocker 중재·트레이드오프 G1 격상)→G2(이중루프 TDD·규율 감사·B1 수렴 재감사)→Phase3(정직 검증보고). blocker 0으로 종료. 12/12 테스트 OK·check 0·drift 없음·CHECK 실효 확인. 미실행 3건(mypy/ruff 미설치, race 직접검증) 사유 명시.
- **#A 증거 확보**: 산출물이 `catalog/{..._layer}/`(컨테이너 없음)로 나와 #A 전제를 구현물로 확증. 단일 앱 마찰 집행 레시피(re-import·단일 `catalog/migrations/`·`app_label`) 확보 → #A의 "Django 통합 집행 방안" 설계 입력.
- **남은 일 (스모크 후)**: #A(컨테이너 골격 YAGNI 면제 불변식화) + #B(명세 일관성 자기리뷰)를 묶어 houserules `final.md`(소스+배포본)·SKILL.md §1·design-architect 반영 설계. 비강제 nit 3건(타입 정밀도·created_at·loc 주석)은 정책상 nit 유지(houserules §4 — 시그니처 강제/정밀도 권장)로 옳게 등급됨.

## 4. 확정 진단 + 반영 (2026-05-27, plan 승인 후)

독립 에이전트 3개 삼각 검증으로 원인을 **3축**으로 재확정(초기 "architect가 YAGNI 과확장" 가설을 교정):
- **축1 — 표준 텍스트가 접기를 *허락***: architect는 `final.md`를 실제로 읽었고(명세가 §2 "단일·소규모 평면 허용"을 인용) 합법적으로 접을 수 있었다 — 판단 실수가 아니라 텍스트 결함(의무성 다이어그램 암시·YAGNI/`[선택]` 산재·불변식 경계 미명시).
- **축2 — 전달/와이어링 결함**: design-architect·discipline-reviewer가 `final.md`를 강제 로드 안 함, SKILL.md가 트리를 본문에 안 담고 선언만, SKILL §3(평면 금지)↔final §2(평면 허용) 자기모순, reviewer가 표준 아닌 명세와 대조.
- **축3 — 명세 자기모순 + 공백**: "표준 적용" 직후 "단, 평면/컨테이너 생략"(design-spec:273·279); ORM 명명·Django 앱 통합(HOW) 미명시.
- coder·테스트 무죄 확정.

**반영(이 커밋):**
- **`final.md`(소스+배포본 동일)**: §0 불변식 절 신설(긍정 명령문 6항) · YAGNI/`[선택]` 정정(종류 2차 폴더 항상 생성, `[선택]`=비어 있을 수 있음) · ORM 명명 규약(도메인 bare `Order` / ORM `<Name>Model`) · Django 앱 통합(`infra_layer/django_<app>/` startapp, `AppConfig.name`=점경로·`label='<app>'`, 루트 `models.py` 금지) · "단순 지원 앱 domain_layer 생략"을 명시 승인으로 제한.
- **SKILL.md(전달 교정)**: §1.2에 "final.md 반드시 읽기" + 불변식 6항 체크리스트 본문 호이스팅(in-context) · §3 레드플래그에 컨테이너 누락·종류폴더 평면화·앱 위치·ORM명 추가(SKILL↔final 모순 해소).
- **design-architect**: 불변식 생략·축소 금지 + final.md 필독 + ORM명·앱위치 명세화.
- **discipline-reviewer**: 구조 감사를 *표준 §0 불변식과 직접 대조*(명세 부합만으론 통과 안 함; 명세가 접었으면 설계 반송) + 레드플래그.
- **coder**: 명세-표준 괴리 시 멈춤 보고(방어 심층화).

**결정**: 종류 2차 폴더 = 항상 전체 골격(`[선택]` 포함, 비어도 생성) — 사용자 선택. 최대 입장이라 빈 폴더 노이즈가 거슬리면 가역 조정.

**남은 일**: 재설치 → 그린필드 toy 재리셋 → `/dddjango` 재현 동적검증(산출물이 §0 불변식 충족하는지). 커밋(이번 변경 + 미커밋 마켓플레이스 일원화 + 스모크 로그).
