# catalog 컨테이너 §0-1 회귀 — 진단 + 강한 수정 스펙 (적대 리뷰 대상)

> 목적: "기존 Django 앱(catalog)이 `application/<app>/` 밖 루트에 방치되는" 결함이 **다시는 회귀 안 하도록** 강한 지침/집행을 설계한다. 이 문서는 **적대 리뷰 대상 초안** — 리뷰어는 "이래도 또 샌다"를 찾는다.
> 작성 2026-06-02. 정본 일지=`workspace/DEVLOG.md`, 인벤토리=`workspace/eval/results/REMAINING-ISSUES.md`.

---

## §1. 진단 (실증)

### 1.1 회귀 타임라인 (전부 2026-06-02, 같은 태스크군 = "주문 생성+catalog 재고 차감")
| 시각 | 런 | catalog 위치 | 판정 |
|---|---|---|---|
| 02:05 | smoke4-codex | 루트 + 판정적재 | ❌ FAIL(SH-1/4 + SD-3) |
| 02:05 | smoke4-claude | 루트(판정누출X) | 🟡 contested(§632-2 오독→PASS 후 정정) |
| **05:06** | **poc-codex** | **`application/catalog/` 이주 이행**(4계층, `SeparateDatabaseAndState`로 db_table 보존) | **✅ SH-1/4 PASS**(루트 orphan만 SH-9 비치명) |
| later | smoke6-claude | 루트 회귀 | ❌ FAIL(SH-1/4) |
| 15:54 | smoke6-codex | 루트 + 판정적재 회귀 | ❌ FAIL(SH-1/4 가중) |

**FAIL → PASS → FAIL이 같은 날 펄럭임 = 비결정 확정.** poc-codex가 같은 태스크군·같은 표준·같은 런타임(Codex)으로 정확히 이주했으므로 **현 코퍼스로 정답이 가능**한데도 architect가 코인플립한다.

### 1.2 3중 집행 레그가 전부 뚫림 (왜 반드시 회귀하나)
- **Leg-1 (결정적 백스톱) = 구조상 부재.** `dddjango/scripts/check-layer-skeleton.py`의 `_find_bc_dirs`(69행)가 **`application/`의 자식만** BC로 열거 → 루트 `catalog/`는 **열거조차 안 됨**. 백스톱 6종 어디도 "앱이 application/ 아래인가"를 보지 않음(조사 A: 0/6).
- **Leg-2 (생산자/표준) = 오도.** `architecture-ddd/final.md:632`-(2) "단순 데이터소스면 …평면을 유지해도 된다"가 **위치를 침묵** → architect/coder가 "루트에 둬도 됨"으로 합리화. houserules §1.1 "기존 규약 존중"이 추가 탈출구.
- **Leg-3 (평가/감사) = 면제.** 평가자(조정자)가 §632-(2)를 *위치 면제*로 오독해 smoke4-claude·smoke6-claude에 PASS를 줬고, DR-24가 "underdetermined"로 분류 → 캐치넷마저 통과시킴.

### 1.3 표준 원문 빈칸 (조사 B·C 확정)
- §632-(2): "이주는 불필요하고 ACL/포트로 통합해 **평면을 유지해도 된다**" — *위치*(application/ 아래 vs 루트) **명시 0**. "평면"=4계층 미전개인지, 루트 허용인지 텍스트만으론 불명.
- houserules §0-1: "앱은 루트 평면이 아니라 `application/<app>/` 아래에 둔다" — **데이터소스 면제 조항 0**. SH-1/SH-4·마스크 C도 *4계층 전개*만 제어, *위치* 면제 없음.
- ∴ 올바른 판정은 "데이터소스여도 `application/<app>/`(flat: `infra_layer/django_<app>/`) 안 — 루트 금지". §632-(2)는 **4계층 면제일 뿐 위치 면제 아님**.

---

## §2. 수정 스펙 (3-leg — P1a/P2/P3 하드닝과 동형)

### Leg-1 (결정적·핵심) — 새 백스톱 `check-app-container.py` (§0-1 위치 전용)
`check-layer-skeleton.py`의 AND-합성·거짓양성0 철학을 그대로 재사용한다. **루트(=application/ 밖) Django 앱을 능동 적출**한다.

```
트리거 (AND — 전부 참일 때만 blocker):
  G1) 레포에 application/ 컨테이너 존재 = 표준 채택.  없으면 exit 0 (§1.1 기존규약 존중 — 전체평면 프로젝트 면제).
  열거) application/ 밖 "Django 앱 후보" D = 디렉터리이고 앱 마커 보유:
          D/models.py  OR  D/apps.py  OR  D/migrations/  (하나라도)
        제외: SKIP_DIRS(.venv 등) · application/ 자체와 그 하위 · 프로젝트 설정 패키지
              (settings.py 보유 & 앱마커 없음) · 앱마커 없는 잡동사니 패키지.
  각 D에 대해:
    G2) D가 이번 변경에서 touched (git status --porcelain 신규/수정/미추적).
        git 아니면 보수적 True(나머지 AND가 좁힘).
    G3) application/<D.name>/ 가 부재.
        존재하면 = 이미 이주됨, 루트 D는 orphan-중복(비치명 SH-9) → blocker 아님(cleanup/reviewer 영역).
  G1 ∧ (∃ D: 앱마커 ∧ G2 ∧ G3) → blocker (exit 2).

출력(blocker): "touched Django 앱 <D>가 application/ 밖 루트에 있음 — houserules §0-1 위반.
  application/<D>/ 로 이주하라(데이터소스면 flat: infra_layer/django_<D>/{models,migrations}/,
  4계층 전개는 §632-(2)로 면제 가능하나 *위치*는 면제 안 됨). 정당한 brownfield 보존 사유가
  있으면 코드에서 방치하지 말고 설계(G1)로 반송하라."
종료코드: 0=clean/미적용, 2=blocker, 1=usage.
```

**왜 이 가드 조합이 정밀한가 (회귀 사례 대조):**
- **smoke6 catalog** = 루트 + 새 `0002_add_stock_check` 마이그레이션(touched) + `application/catalog/` 부재 → G1∧G2∧G3 = **차단**. ✅ (회귀 봉쇄)
- **poc orphan** = 루트 catalog 미변경(untouched, baseline 0001 byte 보존) + `application/catalog/` 존재 → G2 거짓 ∧ G3 거짓 = **스킵**. ✅ (거짓양성 0)
- **전체평면 프로젝트**(application/ 자체가 없음) = G1 거짓 → exit 0. ✅ (§1.1 존중)
- **미관여 레거시**(billing 등 안 건드린 앱) = G2 거짓 → 스킵. ✅ (과잉이주 방지)

**와이어링**: G2(생산자 예방 게이트)에 다른 5종과 함께 등록 + `plugin.json` 버전 범프(캐시 갱신). Codex 미러(`codex-dddjango/`)·`workspace/reference` 3미러 동기.

### Leg-2 (생산자 예방) — 표준 텍스트 명문화
- **§632-(2) 보강**: "평면을 유지해도 된다"를 "**4계층 전개는 면제(애그리거트 불요)하되, 위치는 `application/<app>/` 아래 유지 — 루트 평면 금지. 데이터소스 앱은 `application/<app>/infra_layer/django_<app>/`에 둔다**"로 명시. "평면"=*깊이* 면제이지 *위치* 면제 아님을 못박는다.
- **houserules §0-1·§1.1 경계**: §1.1 "기존 규약 존중"은 *프로젝트 전체 레이아웃 철학*에 적용 — *이번 작업이 건드린(touched) 데이터소스 앱*을 루트에 방치하는 근거가 아님("무관한 기존 코드" ≠ "관여한 데이터소스"). touched 기존 앱은 §0-1 컨테이너로 들어온다.
- **design-architect 게이트 지시**: 스코프가 기존 앱을 건드리면 architect는 그 앱의 **컨테이너 배치를 명시 결정**하고 기본값은 `application/<app>/` 이주(데이터소스면 flat). 큰 blast-radius 우려가 있으면 G1 트레이드오프 옵션으로 표면화(미결정 방치 금지).

### Leg-3 (감사/평가)
- **rubric SH-1/SH-4·마스크 C**: "데이터소스도 위치 면제 없음 — §632-(2)는 4계층 면제일 뿐"을 명문(이번 채점 정정의 코드화). 마스크 C는 *4계층 전개 의무*만 제어하고 *위치*는 항상 §0-1.
- **discipline-reviewer**: "application/ 사용 중인데 루트(=밖)에 touched Django 앱이 있으면 blocker" 의미 체크 추가(leg-1의 의미 레인 짝).

---

## §3. "다시는 회귀 안 함"의 논리 (3-leg AND가 왜 필요한가)
단일 레그론 부족하다 — DR-24가 *결정적 백스톱도 좁은 텍스트 계약을 의미적으로 우회*당함을 보였다(P1a 변종). 그래서:
- leg-1(결정적)이 **구조적 루트-앱**을 모델 무관하게 차단 → 코인플립을 게이트로 전환.
- leg-2(생산자)가 **모호성 제거**로 애초에 루트에 안 두게 → 백스톱 반송 빈도↓.
- leg-3(감사)이 **백스톱이 못 보는 의미 변종**(이름 바꿔 이주, 비-루트 위치 등)을 사람/리뷰어 레인으로 포착.
세 레그가 서로의 사각을 덮어야 "never again"에 근접.

## §4. 적대 리뷰가 답해야 할 것 (이래도 또 새는 경로)
1. **백스톱 회피/누락**: leg-1 정의(루트 ∧ touched ∧ application/<name> 부재)를 만족시키며 *실질적으로 catalog를 비-DDD로 남기는* 경로? (예: 앱을 `src/`·`apps/` 등 *비-루트·비-application* 위치에 둠 / `application/<다른이름>/`로 일부만 옮김 / 판정만 비-앱 모듈에 둠 / models를 루트 비-앱 패키지에 숨김 / migrations 없이 unmanaged 모델.)
2. **거짓양성(과잉차단)으로 인한 무력화**: leg-1이 정당한 케이스를 잘못 막아 팀이 백스톱을 끄거나 우회 → 회귀 재유입? (정당한 §1.1 기존규약 프로젝트 / 모노레포 다중 application/ / Django 설정 패키지 / namespace package / 비-git 체크아웃 / 이름 다른 이주 catalog→inventory.)
3. **진단·충분성**: 근본원인이 정말 3-leg 부재인가, 아니면 *더 깊은 원인*(architect 비결정 자체 / §1.1 탈출구가 텍스트로 안 막힘 / 게이트 스티어링)인가? leg-2 표준 명문화가 코인플립을 실제로 제거하나, 아니면 §1.1을 모델이 계속 들먹이나? leg-1의 텍스트 계약은 DR-24 P1a처럼 좁아서 의미 변종에 뚫리나? "강력한 지침"이 되려면 추가로 필요한 것은?

---

## §5. 적대 리뷰 반영 — **개정 계획**(이게 정본, §2는 초안)
3개 렌즈(회피·거짓양성·진단) 적대 리뷰가 원안을 근본 개정시켰다. 핵심 3발견:

**발견 A (진단 절반 오류 — 1차 동인은 architect 코인플립)**: 회귀는 `design-architect.md`의 "데이터소스면 …**평면 유지로 결정한다**" 분기(설계 단계)에서 발생한다. 관측된 회귀 전부에서 루트 catalog는 *명세와 일치*(coder 일탈 아님) → leg-1(coder 산출물 백스톱)은 **이미 잘못 만든 뒤** 잡는 사후 청소다. DR-24도 "C2·C3는 design-spec(architect) 유입"이라 했다. **∴ 1차 무게는 leg-2(architect 예방), leg-1은 2차 안전망.** 원안의 "leg-1=핵심" 명명은 인과를 뒤집었다.

**발견 B (진짜 축은 위치가 아니라 *판정-소유 형태*)**: poc는 판정을 `application/catalog/domain_layer/.../decrease_stock`(**리치 도메인 메서드**)에 둬 §632-(1) 발동→이주. smoke6은 판정을 `published_service/stock_allocation.py`(**평면 함수**, domain_layer 부재)에 둬 architect가 §632-(2) 데이터소스→평면. **위치는 선행 "판정-소유 형태" 결정의 하류 그림자.** → 위치-전용 백스톱은 "**`application/catalog/`로 옮겼으나 판정은 평면 published_service 함수**" 변종을 통과시킨다(잔존경로 B-1).

**발견 C (§1.1이 닫히지 않은 상위-우선 탈출구)**: 원안은 §632·architect에만 위치강제를 박지만, houserules `SKILL.md §1`은 **§1.1(기존 규약 존중)이 §632보다 상위 우선**이다. baseline catalog는 `Product`+`0001`+db_table 보유라 "startapp stub"보다 확립돼 §1.1 "답습 금지" 단서를 비껴간다 → 모델이 "§632 발동 전에 §1.1로 존중"으로 빠져나감. **§1.1 본문 자체 + §0-1 불변식에 carve-out을 박아야 닫힌다.**

또 leg-1 백스톱은 그대로면 **다수 회피**(빈껍데기 G3 토큰[치명]·src/중첩 위치·models/ 패키지·판정-only 모듈·git-untouched)와 **다수 거짓양성**(§1.1 brownfield 무관앱·설정패키지+커스텀User·vendored·비-git 전면차단·rename 이주)을 낸다. 거짓양성은 `dddjango.md:80` all-or-nothing 팬에서 **한 번이면 파이프라인 정지→백스톱 비활성화→회귀 재유입**.

### 개정 레그 (우선순위 재배치)
- **Leg-2-A (1차·예방) — design-architect 결정 강제**: `design-architect.md`의 "평면 유지로 결정한다" 탈출구를 *조건부 폐기*. "이번 작업이 touched한 기존 앱이 **판정·불변식을 새로 소유**하거나 **새 쓰기 경로**가 생기면, 위치는 무조건 `application/<app>/`(데이터소스면 `infra_layer/django_<app>/`). 루트 평면은 **G1 트레이드오프 옵션으로만** 표면화 — 명세에 직접 박기 금지." 코인플립을 설계 게이트로 전환(왕복 0).
- **Leg-2-B (1차·예방) — §1.1/§0-1 본문 carve-out**: houserules `SKILL.md §1.1` + `references/final.md §0-1` *양쪽에* "이번 작업이 touched한 데이터소스 앱의 루트 평면은 '확립된 규약'으로 보지 않는다; 데이터소스여도 **위치는 §0-1**, **4계층 전개만 §632-(2) 면제**"를 양성으로 추가. §632·architect만 고치면 상위-우선 §1.1과 충돌해 샌다.
- **Leg-1 (2차·백스톱) — 하드닝 후 유지**(명명: 핵심→백스톱):
  - G3 강화: `application/<name>/` *디렉터리 존재*가 아니라 *실질 이주 증거*(앱 산출물/4계층 보유 = `_is_bc_to_check` 참, 또는 동일 db_table/label 앱이 application/ 하위 존재)일 때만 면제 → 빈껍데기 토큰·rename 둘 다 해결.
  - 앱마커 확장: `models/`(디렉터리) 포함.
  - 열거: **`git-touched ∧ 앱마커`로 먼저 좁힌 뒤 위치 판정**(docs/vendor 자연 배제 + src/·중첩 포착). 컨테이너는 `rglob` 금지·**레포 루트 직속 `application/` 고정**(가짜 `vendor/application/`·테스트미러 차단).
  - 거짓양성 가드(거짓양성≈0 필수): **차단 후보 = 이번 변경이 *생성*했거나 *판정 적재*된 앱**으로 한정(무관 brownfield 레거시 제외) · 설정패키지(`settings.py`|`urls.py`+`wsgi/asgi`)는 앱마커 무관 제외 · vendored/baseline-untouched·판정無 제외 · **비-git이면 차단 아니라 스킵**(보수적 True→스킵으로 반전) · namespace(`__init__.py` 부재) 제외.
- **Leg-1.5 (2차·신규 P-C) — 판정-소유 결정적 신호**: 잔존경로 B-1(옮겼으나 평면함수 판정) 차단. "비-`domain_layer` 모듈(published_service 등)에 비즈 분기 + 도메인 애그리거트 메서드 미호출" 신호를 결정적으로(`check-error-centralization` 류) 잡음. 위치-전용 leg-1로는 원리상 불가.
- **Leg-3 (3차·보조) — reviewer**: *완전 의미적* 케이스(옮긴 척만)만 보조. **1차 책임 금지** — DR-21·22가 두 번 실패, Codex는 TOML 격리 부재로 구조적 약함(`shiny-petting-lovelace §3b`).

### 잔존 재발 경로(개정안 전부 적용 후에도)
1. **판정-소유 평면함수 변종**(B-1) — Leg-1.5가 없으면 위치 게이트 통과·빈혈 잔존. Leg-1.5가 주 방어, leg-3 보조.
2. **§1.1 우선순위 충돌**(Leg-2-B를 §1.1 본문에 안 박으면) — prose 충실도 낮은 런타임서 잔류.
3. **leg-1 열거 회피**(`managed=False`+migrations無+파일명 변경) — leg-1.5/leg-3 의미 그물에만 의존.

### 와이어링/배포 주의
- 새 스크립트(leg-1·leg-1.5)는 `dddjango/scripts/` + **Codex 미러 `codex-dddjango/skills/dddjango/scripts/`** + `workspace/reference` 3미러 동기. `plugin.json` 버전 범프(캐시 갱신 — 양 런타임 stale 함정).
- G2 all-or-nothing 팬(`dddjango.md:80`)에 합류 → **거짓양성0이 릴리스 선결조건**(리뷰어2 "릴리스 보류" 권고). 거짓양성 가드(위) 미구현 상태로 와이어링 금지.

---

## §6. 구현 완료 (2026-06-02)
- **Phase 1 (예방·1차)**: architect "평면 유지로 결정" 탈출구 폐기 ×2 · houserules §1.1 carve-out ×2 · §0-1 위치 명문 ×3 · §632-(2) "위치 비면제" ×3 = **3미러 정합 ✅**. 옛 탈출구 문구 잔존 0.
- **Phase 2 (백스톱·2차)**: `check-app-container.py`(leg-1) 작성 + codex 미러(byte-identical) + 게이트 **7종 배선**(①~⑦, Claude+Codex) + plugin.json **1.0.2→1.0.3**. **적대 검증 전부 PASS**: 실 4픽스처(smoke4/6 차단·poc 면제) + 합성 6종(빈껍데기·src중첩 차단 / 무관앱·설정패키지·비-git·rename 면제), 좋은 프로젝트·레포 자체 오발화 0 → **거짓양성≈0 확정**.
- **Phase 3 (감사·3차)**: RUBRIC 마스크 C **위치/깊이 분리**(smoke6 SH 오판 교정) + discipline-reviewer 레드플래그를 catalog-touched·빈껍데기·published_service-빈혈 변종으로 ×2미러.
- **미구현(정직)**: **leg-1.5(판정-소유 형태 결정적 신호)는 미작성** — 결정적 빈혈 탐지는 FP 위험이 커 "거짓양성0" 원칙과 충돌. 잔존경로 B-1(`application/catalog/`로 옮겼으나 판정은 평면 `published_service` 함수=빈혈)은 현재 discipline-reviewer(leg-3)만 덮는다 → **reviewer 3 경고대로 런타임 의존 잔존 리스크**(Codex 격리 약함). 별도 신중 설계 과제로 보류; B-1이 실제 재발하면 그때 P-C형 결정적 신호 착수.
