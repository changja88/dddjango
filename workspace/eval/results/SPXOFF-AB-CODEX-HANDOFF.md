# SPXOFF A/B — superpowers 인과 분리 라이브 (Codex only) · 2026-06-05

> 목적: "superpowers 간섭이 Codex의 dddjango 오작동(특히 DR-42 pytest 미채택)의 *원인*인가"를 **통제된 A/B**로 검정. 변수 **1개**(superpowers on/off)만 바꾸고 나머지 전부 고정.

## 0. 사전등록 (pre-registration — 결과 본 뒤 합리화 금지)

**조작 변수**: superpowers 플러그인.
- **ON-arm** = 기존 `dddjango-pytestlive-codex` 런 (이미 채점 = `results/20260604-2311-pytestlive-codex.md`, **DR-42 FAIL** = pytest 미채택·구 catalog/ 잔존·timezone·presentation 과다).
- **OFF-arm** = 이번 런 (superpowers `enabled=false`).

**통제(전부 고정 — ON-arm과 동일):**
- 태스크 = §1 (ON-arm이 쓴 것과 verbatim 동일)
- 게이트 답 = §2 (동일)
- fixture baseline = `e47ca79` (동일 소스 clone, byte-identical 추적코드)
- 플러그인 = dddjango 1.3.0 (캐시=레포 HEAD, `diff -rq` IDENTICAL 검증함)
- 런타임 = Codex gpt-5.5 high (동일)
- thinking = OFF (coder)
- python = fresh `.venv` Django-only (ninja·pytest 미설치 = 진짜 greenfield)

**내 예측 (falsifiable):** superpowers OFF는 pytest 미스를 **고치지 못한다** — 원인은 C1(superpowers)이 아니라 **C3**(3줄 startapp stub `catalog/tests.py`를 '기존 manage.py test 관례'로 오판) **+ C4**(gpt-5.5 Django 기본=TestCase prior)이기 때문. 따라서 OFF-arm도 manage.py test로 가고 **DR-42 ⓐⓑ FAIL** 예측. 유일하게 확실한 변화 = 트랜스크립트에서 superpowers 스킬 read **0회**(조작 점검).

**판정 규칙:**
- OFF-arm이 **pytest 채택 + 전반 개선** → superpowers가 인과적으로 유의 (**내 분석 틀림·사용자 가설 맞음**). → 메커니즘 후속조사.
- OFF-arm이 **여전히 pytest 미스**(내 예측대로) → superpowers는 원인 아님으로 격리. 근본 = C3+C4. → 처방은 **L2(stub carve-out)**, superpowers 제거 아님. L1(우선순위 척추)는 churn·비용 이유로 별도 정당.
- 단일 축만 흔들리거나 모호 → N=1 변동 의심 → OFF 2회차(+필요시 fresh ON) 추가.

**조작 점검(manipulation check):** OFF-arm 트랜스크립트에 `Read SKILL.md (superpowers:...)` 가 **0**이어야 조작 성공. 1회라도 있으면 비활성 실패 → 보고.

## 1. 태스크 (붙여넣기 — ON-arm과 동일)
```
주문 생성 API. 별도 주문(order) 개념으로, 요청 상품·수량의 주문을 만든다. 재고는 기존 catalog가 소유하며, 주문 생성 시 catalog의 재고를 차감한다(재고 부족 시 409).
```
⚠️ 동시성·pytest·venv 힌트 **주지 말 것**(표준이 스스로 하는지가 관찰면).

## 2. 고정 게이트 답 (ON-arm과 동일)
| 게이트 | 답 | 이유 |
|---|---|---|
| G0 BC 배치 | **③ "표준 판정-소유 원칙대로 결정"** | 강제하면 축 죽음 |
| G0 렌즈 | **ddd + db + api** | 409·동시성 |
| G0 스코프 | **제안대로** | 확장 금지 |
| API 스택 | **"표준 기본대로"** — ⚠️ plain 강제 금지 | 표준이 Ninja로 수렴하나 |
| 테스트 러너 | (물으면) **"표준 기본대로"** | ⭐ DR-42 본질 |
| G1 / G2 | **명백한 결함 없으면 승인** | 게이트·백스톱 발화가 관찰대상 |
| thinking | **OFF** (coder) | 비용 레버 |

## 3. 실행

**superpowers OFF 이미 적용됨** — `~/.codex/config.toml` superpowers `enabled = false`, dddjango `= true` 유지. 백업 = `~/.codex/config.toml.bak-spxoff-20260605`.

```bash
cd ~/Desktop/dddjango-spxoff-codex
codex                 # ★ 반드시 새 세션 (config는 startup에 읽힘 — 기존 세션엔 OFF 미반영)
# 세션 안에서:  $dddjango  → §1 프롬프트 → §2 게이트 답
```

⚠️ fixture에 stale `.RUN-CRIB.md`(다른 "재고 예약" 태스크)·`README.md`(sample 템플릿)가 있다 — **ON-arm과 동일하게 그대로 두되(통제 변수), 무시하고 §1 태스크로** 시작.

**끝나면 채점 전 스모크:**
```bash
cd ~/Desktop/dddjango-spxoff-codex
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations && .venv/bin/python manage.py migrate
.venv/bin/pytest      # 부트스트랩됐으면 그린; pytest 미설치로 실패하면 그 자체가 ⓑ 데이터
```

## 4. 끝나면 나에게 "코덱스 끝났어"
내가 fixture를 직접 읽어 채점한다(붙여넣을 필요 없음):
- **1차 신호**: pytest 채택했나(requirements 핀·`pyproject` DSM·함수형+`assert`+`@django_db`+`mocker`+factory) vs `manage.py test`/TestCase 폴백.
- **C3**: 코디네이터 러너준비가 3줄 stub을 **greenfield→pytest**로 봤나 **manage.py test 관례**로 봤나(러너 결정 흔적).
- **조작 점검**: superpowers read 0회.
- **2차**: SH-1(구 `catalog/` 잔존?)·SD-6(`django.utils.timezone`)·presentation 파일 과다 — ON-arm 대비.
- 결과지 = `results/YYYYMMDD-HHmm-spxoff-codex.md` + ON-arm 대조표.

## 5. 복구 (런·채점 끝나면 필수)
```bash
cp ~/.codex/config.toml.bak-spxoff-20260605 ~/.codex/config.toml   # superpowers 다시 ON
```

## 6. 한계 (정직)
**N=1.** OFF-arm 1회 vs ON-arm 1회는 superpowers 효과와 런-변동이 교락. 결정적 분리엔 arm당 ≥2회 필요. 이번은 1차 방향타다. C3·C4는 N=1로 분리 불가(둘 다 기여 가능).
