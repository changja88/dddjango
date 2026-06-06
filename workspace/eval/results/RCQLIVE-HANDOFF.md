# rcqlive — 1.4.0 누적 미검증분 라이브 핸드오프 (2026-06-05)

> 너가 `/dddjango`를 직접 돌리고(드라이브), 끝나면 내가 산출물을 읽어 채점한다.
> 정직 경계: **N=1 sanity** — "DR-37/40/41/43이 라이브 런에서 작동/실현되나"까지. **우열·결정성 결론 아님**(런마다 치명 레인이 갈리는 P4③ run-variance 관측됨).

## 0. 준비 상태 (내가 완료)
- ✅ **플러그인 1.4.0 최신화**: Claude 캐시(`~/.claude/plugins/cache/changja88/dddjango/1.0.0/`)·Codex 캐시(`~/.codex/plugins/cache/dddjango-local/dddjango/1.0.0/`) 둘 다 레포 HEAD로 `diff -rq` **IDENTICAL**. 버전 1.3.0→1.4.0·백스톱 13종·DR-43 R/C/Q 안착 확인.
- ✅ **Codex config 복구**: `~/.codex/config.toml` superpowers `enabled=false→true`(spxoff 실험 종결·정상 상태). dddjango `=true` 유지.
- ✅ **fixture 2개**(Django 4.2.30·Python 3.9.6·**pytest·ninja 미설치 greenfield**·flat `config.settings`·catalog Product 시드 Widget10/Gadget3·깨끗한 baseline 커밋·check 통과):
  - `~/Desktop/dddjango-rcqlive-claude` — Claude
  - `~/Desktop/dddjango-rcqlive-codex` — Codex
- ⚠️ **반드시 새 세션에서 시작** — 캐시를 방금 갱신해서, 열려 있는 세션은 메모리에 구 1.3.0 에이전트 텍스트를 들고 있다. (기존 세션 쓰려면 `/reload-plugins` 후.)

## 1. 태스크 (양 런 공통 — 이전 nj2/c4/fk/pytest live와 **동일 입력**, 변수 통제)
```
주문 생성 API. 별도 주문(order) 개념으로, 요청 상품·수량의 주문을 만든다. 재고는 기존 catalog가 소유하며, 주문 생성 시 catalog의 재고를 차감한다(재고 부족 시 409).
```
> ⚠️ 동시성·오버셀·pytest·venv·프레임워크를 **프롬프트에 명시하지 않는다** — 표준이 스스로 하는지가 관찰면(이전 런과 동일). 이 태스크 하나가 새 `orders` BC를 끌어내 R/C/Q 응용 명명·BC FK 경계·네이밍·Ninja·동시성을 다 건드린다.

## 2. 고정 게이트 답 (변수 제거 — 양 런 공통)
| 게이트 | 답 | 이유 |
|---|---|---|
| G0 BC 배치 | **미강제** — "표준 판정-소유 원칙대로 결정해줘" | 강제하면 축 죽음 |
| G0 렌즈 | **ddd + db + api** | HTTP 계약(409)·동시성 있음 |
| G0 스코프 | **제안대로** | 확장 금지 |
| API 스택/프레임워크 | **"표준 기본대로"** — ⚠️ plain 강제 **금지** | 표준이 스스로 Ninja로 수렴하는지 |
| 테스트 러너 | **"표준 기본대로"** | 표준이 스스로 pytest 부트스트랩하는지 |
| G1 설계 / G2 구현 | **명백한 결함 없으면 무수정 승인** | 게이트·백스톱 발화 자체가 관찰 대상 |
| thinking | **OFF** (coder) | 비용 레버, 품질 무손실(DR-08) |

## 3. 실행
**Claude**:
```
cd ~/Desktop/dddjango-rcqlive-claude
claude                       # 새 세션
# 세션 안에서:  /dddjango  → §1 프롬프트 → §2 게이트 답
```
**Codex**:
```
cd ~/Desktop/dddjango-rcqlive-codex
codex                        # 새 세션 — dddjango 코디네이터 트리거
# §1 프롬프트 → §2 게이트 답
```
**끝나면 (양 런 공통) 채점 전 스모크:**
```
.venv/bin/python manage.py check
.venv/bin/python manage.py makemigrations && .venv/bin/python manage.py migrate
.venv/bin/pytest
```

## 4. 끝나면 나에게 "claude 끝났어" / "codex 끝났어"
내가 fixture의 `application/`·테스트·`requirements.txt`·`pyproject.toml`·`.dddjango/`를 직접 읽어 채점한다(붙여넣을 필요 없음).

## 5. 내가 채점할 핵심 — 이 런의 미검증 타깃 (관측 신호)
| DR | 관측(RUBRIC) | PASS 신호 | FAIL/MISS 신호 |
|---|---|---|---|
| **DR-43 R/C/Q 응용 명명** (헤드라인·SH-3) | 새 `orders` 응용 유스케이스 = **인터랙터 연산 객체** | 쓰기 `…Command`·읽기 `…Query`·입력 `@dataclass …Request`, 모두 `execute(request)`·repository/port 의존; 조회는 **Query 클래스**(selector 함수 아님) | `command/`에 `…Service`/자유함수·`query/` selector 함수·`dto/` 비-`@dataclass`·`execute` 부재 |
| **DR-41 네이밍** (SH-6) | 포트/구현 헥사고날 | 추상=개념+역할접미사(`…Port`/`Repository`/`Gateway`); 구현=확립 패턴명+기술접두; 일반 포트 `…Port`↔`…Adapter`; ORM `<Name>Model`·도메인 bare; `_app` 0 | `Interface`/`Impl`·파일명 약어·`_app` 잔존 |
| **DR-40 산출 폴더** | 플러그인 산출물 위치 | `.dddjango/<생성일>-<slug>/`에 설계·계획 산출 | 루트 흩뿌림·폴더 규약 위반 |
| **DR-37 BC FK 금지** (SD-7·SD-4) | cross-BC 참조 방식 | orders→catalog는 **ID 참조 + `published_service`/ACL 포트**, **ORM FK 0**·직접 import 0 | orders 모델이 catalog `Product`를 `ForeignKey`로 참조·catalog 도메인 직접 import |
| 척추(상시) | SD-1~7·SH-1~10·NJ-1~6·FC-1~3·Q-1~7 | 빈혈 아님·계층 순수·Ninja 얇은 operation·골든 행위표·구조/명명/동작 회귀 0 | 치명 레인 ❌ 1개 = 픽스처 FAIL |

> **유기적 한계(정직)**: 백스톱·reviewer는 위반이 없으면 발화 안 한다. 준수 런이면 "미발화 = 정상". 이 런은 **생산자(준수) 측면** — 표준이 스스로 R/C/Q 명명·FK 회피·네이밍을 하는지 확인이다. 백스톱 *차단* 측면(DR-43은 백스톱 N=0 보류)은 별도. **DR-43 시점 규칙**상 이 1.4.0 산출분은 R/C/Q 명명이 정식 채점 대상(SH-3 확장, 커밋 b2c3a25).

## 6. 한계 (정직)
**N=1.** 양 런타임 1회씩 = 우열 비교 아님. P4③ run-variance로 치명 FAIL 레인이 런마다 갈린다(Claude·Codex 둘 다 비결정 관측). 이 런은 1.4.0 변경분이 라이브에서 *실현되나*의 방향타다. 드리프트/회귀 발견 시 N≥2 후속.
