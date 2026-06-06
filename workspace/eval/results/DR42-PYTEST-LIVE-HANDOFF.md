# DR-42 pytest 테스트 표준 — 라이브 검증 핸드오프 (2026-06-04)

> 너가 `/dddjango`를 직접 돌리고, 끝나면 내가 산출물을 읽어 채점한다.
> 정직 경계: **N=1 sanity** — "DR-42(pytest 표준·§6.1 부트스트랩 해지·백스톱 ⑬)가 라이브 런에서 작동하나"까지. 우열·결정성 결론 아님.

## 0. 준비 상태 (내가 완료)
- ✅ **커밋**: `eval/codex-determinism-n2` — `d21730a`(plugin 표준)·`7c09b70`(eval/기록). push 안 함.
- ✅ **플러그인 최신화 1.3.0**: Claude 캐시(`~/.claude/plugins/cache/changja88/dddjango/1.0.0`)·Codex 캐시(`~/.codex/plugins/cache/dddjango-local/dddjango/1.0.0`) 둘 다 레포 HEAD로 정확 미러(stale 1.0.8→1.3.0). 백스톱 ⑬·러너준비 단계·§7 mocker·13종 반영 확인.
- ✅ **fixture 2개**(Django 4.2.30·Python 3.9.6·**pytest·ninja 미설치**·flat `config.settings`·catalog Product 시드 Widget10/Gadget3·baseline 커밋·check 통과):
  - `~/Desktop/dddjango-pytestlive-claude` — Claude
  - `~/Desktop/dddjango-pytestlive-codex` — Codex(인터랙티브)
- ⚠️ **반드시 새 세션에서 시작** — 캐시를 방금 갱신해서, 지금 열려 있는 세션은 메모리에 구 에이전트 텍스트(1.0.8)를 들고 있다. (기존 세션을 쓰려면 `/reload-plugins` 후.)

## 1. 태스크 (양 런 공통 — 이전 라이브 nj2live·c4live·fklive와 **동일 입력**, 변수 통제)
```
주문 생성 API. 별도 주문(order) 개념으로, 요청 상품·수량의 주문을 만든다. 재고는 기존 catalog가 소유하며, 주문 생성 시 catalog의 재고를 차감한다(재고 부족 시 409).
```
> ⚠️ 동시성·오버셀을 **프롬프트에 명시하지 않는다** — 표준 §9.6(Risky Write)이 알아서 동시성 테스트를 만든다(이전 런과 동일). 이 태스크가 도메인 판정·영속·동시성·HTTP를 다 끌어내 pytest 관용구·`mocker`·factory·`@pytest.mark.django_db` 관찰면이 넓다.

## 2. 고정 게이트 답 (변수 제거 — 양 런 공통)
| 게이트 | 답 | 이유 |
|---|---|---|
| G0 BC 배치 | **미강제** — "표준 판정-소유 원칙대로 결정" | 강제하면 축 죽음 |
| G0 렌즈 | **ddd + db + api** | HTTP 계약(409)·동시성 있음 |
| G0 스코프 | **제안대로** | 확장 금지 |
| API 스택/프레임워크 | **"표준 기본대로"** — ⚠️ plain 강제 **금지** | 표준이 스스로 Ninja로 수렴하는지 |
| **테스트 러너** | **"표준 기본대로"**(물으면) | ⭐ DR-42 본질 = 표준이 스스로 **pytest 부트스트랩**으로 가는지 |
| G1 설계 / G2 구현 | **명백한 결함 없으면 무수정 승인** | 게이트·백스톱 발화 자체가 관찰 대상 |
| thinking | **OFF** (coder) | 비용 레버, 품질 무손실(DR-08) |

> ⚠️ 인터랙티브(Codex)에서 "pytest 깔아라 / venv 확인하라" 같은 힌트 **주지 말 것** — 표준이 스스로 부트스트랩하는지가 진짜 테스트.

## 3. 실행
**Claude** (fixture `dddjango-pytestlive-claude`):
```bash
cd ~/Desktop/dddjango-pytestlive-claude
claude                       # 새 세션
# 세션 안에서:  /dddjango  → §1 프롬프트 → §2 게이트 답
```
**Codex** (fixture `dddjango-pytestlive-codex`):
```bash
cd ~/Desktop/dddjango-pytestlive-codex
codex                        # 새 세션 — dddjango 코디네이터 트리거
# §1 프롬프트 → §2 게이트 답
```
**끝나면 (양 런 공통) 채점 전 스모크:**
```bash
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations && .venv/bin/python manage.py migrate
.venv/bin/pytest             # 러너=pytest(pytest-django) — 부트스트랩이 깔았어야 함
# 만약 pytest 미설치로 실패하면 그 자체가 ⓑ 관찰 데이터(부트스트랩 실패) — 알려줘
```

## 4. 끝나면 나에게
- **"claude 끝났어" / "codex 끝났어"**만 알려주면, 내가 fixture의 `application/`·테스트·`requirements.txt`·`pyproject.toml`/`pytest.ini`·`.dddjango/`를 직접 읽어 채점한다(파일은 내가 읽으니 붙여넣을 필요 없음).
- 런 중 막히거나 게이트가 헷갈리면 그대로 물어봐.

## 5. 내가 채점할 DR-42 핵심 (관측 신호)
| # | 관측 | PASS 신호 | FAIL/MISS 신호 |
|---|---|---|---|
| **ⓐ** pytest 관용구 (RUBRIC Q-6) | 생성 테스트 = **함수형 `def test_*()` + plain `assert` + `@pytest.mark.django_db`**; mock은 `mocker` 픽스처; ORM 영속 픽스처는 **factory_boy** | `class X(TestCase)` + `self.assertEqual` + `from unittest import mock`(raw 패치) 폴백 |
| **ⓑ** greenfield 부트스트랩 (§6.1 해지) | `requirements.txt`/매니페스트에 **pytest·pytest-django 핀**(§6.2)·루트 **pytest 설정**(`[tool.pytest.ini_options]`/`pytest.ini`)에 `DJANGO_SETTINGS_MODULE = config.settings`(*감지*, 하드코딩 `settings.test` 아님)·acceptance Red가 import-death 없이 동작 | pytest 미설치·`manage.py test`로 fallback·설정에 `settings.test` 하드코딩(존재 안 함) |
| **ⓒ** 백스톱 ⑬ (`check-test-config`) | 준수 런이면 **미발화(exit0)** = 정상(설정에 DSM 있음). G2 배너에 13종 실행 흔적 | (설정 누락 시 발화·반송 — 준수 런에선 안 봐도 정상) |
| **ⓓ** 하니스 pytest 채점 (FC-2 falsifiable) | `.venv/bin/pytest`로 **그린바**; 핵심 판정 메서드에 mutation 주입 → **pytest 런 red** | pytest가 0개 수집(함수형 미수집)·mutation에도 green |
| 그 외 | Q-1·2·3·5·구조(SH)·동시성(Q-3 §20.5) | 구조·명명·동작 회귀 없음 | — |

> **유기적 한계(정직)**: 백스톱 ⑬·reviewer는 위반이 없으면 발화 안 한다. 준수 런이면 "미발화 = 정상"이고, 이 런은 **준수(생산자) 측면**(표준이 스스로 pytest를 쓰는지) 확인이다. 백스톱 *차단* 측면은 이미 self-test 16/16 + 적대 AST=SHIP로 확인됨(라이브 발화는 별도 N≥2 후속).
