# aclex — DR-44(ACL 예외 전수성·1.5.0) 라이브 핸드오프 (2026-06-06)

> 너가 `/dddjango`를 직접 돌리고(드라이브), 끝나면 내가 산출물을 읽어 채점한다.
> 정직 경계: **N=1 sanity** — "DR-44 처방이 라이브에서 *실현/발화*하나"까지. **우열·결정성 결론 아님**(P4③ run-variance — 치명 레인이 런마다 갈림).

## 0. 준비 상태 (내가 완료)
- ✅ **플러그인 1.5.0 신선화**: Claude 캐시(`~/.claude/plugins/cache/changja88/dddjango/1.0.0/`)·Codex 캐시(`~/.codex/plugins/cache/dddjango-local/dddjango/1.0.0/`) 둘 다 레포 HEAD로 `diff -rq` **IDENTICAL**. 버전 1.4.0→**1.5.0**·백스톱 13종·**DR-44(ACL 전수성·포트앵커·reviewer C1/C2·api/architect 실패모드 열거)** 안착 확인.
- ✅ **커밋 `b7cf255`**(`feat(standard): … DR-44·1.5.0`, 14파일·푸시 안 함).
- ✅ **fixture 2개**(Django 4.2.30·**ninja·pytest 미설치 greenfield**·flat `config.settings`·catalog Product 시드 Widget10/Gadget3·깨끗 baseline·check 통과·application/ 없음):
  - `~/Desktop/dddjango-aclex-claude` — Claude (baseline `6e48b68`)
  - `~/Desktop/dddjango-aclex-codex` — Codex (baseline `32d1cf5`)
- ⚠️ **반드시 새 세션에서 시작** — 캐시를 방금 갱신해서 열려 있는 세션은 메모리에 구 1.4.0 에이전트 텍스트를 들고 있다. (기존 세션 쓰려면 `/reload-plugins` 후.)

## 1. 태스크 (양 런 공통 — rcqlive와 **동일 입력**, 변수 통제)
```
주문 생성 API. 별도 주문(order) 개념으로, 요청 상품·수량의 주문을 만든다. 재고는 기존 catalog가 소유하며, 주문 생성 시 catalog의 재고를 차감한다(재고 부족 시 409).
```
> ⚠️ 동시성·오버셀·CAS·재시도·pytest·venv·프레임워크를 **프롬프트에 명시하지 않는다** — 표준이 스스로 하는지가 관찰면. 이 태스크가 새 `orders` BC↔`catalog` BC를 **ACL로 통합**시키고 낙관적 CAS 동시성을 끌어내, DR-44가 노리는 *ACL 예외 전수 번역 + 경계 실패모드 매핑* 시나리오를 자연 발생시킨다(rcqlive에서 흠이 났던 바로 그 시나리오).

## 2. 고정 게이트 답 (변수 제거 — 양 런 공통)
| 게이트 | 답 | 이유 |
|---|---|---|
| G0 BC 배치 | **미강제** — "표준 판정-소유 원칙대로 결정해줘" | 강제하면 ACL 통합 축 죽음 |
| G0 렌즈 | **ddd + db + api** | HTTP 계약(409)·동시성 있음 |
| G0 스코프 | **제안대로** | 확장 금지 |
| API 스택/프레임워크 | **"표준 기본대로"** — ⚠️ plain 강제 **금지** | 표준이 스스로 Ninja로 수렴하는지 |
| 테스트 러너 | **"표준 기본대로"** | 표준이 스스로 pytest 부트스트랩하는지 |
| G1 멱등성 | **미도입** | 변수 제거(rcqlive와 동일) |
| G1 409 본문 | **available/requested 노출(기본)** | 변수 제거 |
| G1 API 버전 | **미도입**(`/api/orders`) | 변수 제거 |
| G1 설계 / G2 구현 | **명백한 결함 없으면 무수정 승인** | ⭐ **CAS 소진 status·ACL 번역 완전성은 *관찰 대상*이지 내가 끼어들 게 아니다** — 표준이 스스로 하는지 본다. 명백한 결함만 반송 |
| thinking | **OFF** (coder) | 비용 레버, 품질 무손실(DR-08) |

## 3. 실행
**Claude**:
```
cd ~/Desktop/dddjango-aclex-claude
claude                       # 새 세션
# 세션 안에서:  /dddjango  → §1 프롬프트 → §2 게이트 답
```
**Codex**:
```
cd ~/Desktop/dddjango-aclex-codex
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
내가 fixture의 `application/`·테스트·`.dddjango/`(설계명세)·`requirements.txt`·`pyproject.toml`을 직접 읽어 채점한다(붙여넣을 필요 없음). **특히 G1에서 코디네이터가 띄우는 설계명세(또는 `.dddjango/.../design-spec.md`)를 내가 읽어 D2(소진 status 열거)를 본다.**

## 5. 내가 채점할 핵심 — DR-44 관측 신호 (rcqlive 흠의 재발 여부)
> rcqlive Claude 흠: catalog `StockConflictError`(CAS 소진)가 order ACL 미번역→presentation 미매핑→**HTTP 500**. 1.5.0이 이걸 막나?

| DR-44 레버 | 관측 위치 | PASS(처방 실현) | FAIL/MISS(재발) |
|---|---|---|---|
| **D2** architect 실패모드 열거 | `.dddjango/.../design-spec.md` status·에러 표 | CAS 소진/경합 미해소 outcome이 **status 표에 열거**·retryable(503\|409) 배정 | 소진 outcome이 status 표에서 **누락**(rcqlive 갭 재발) |
| **A/E** ACL 전수 번역+포트앵커 | `application/<order>/infra_layer/acl/*.py` + 포트 ABC | ACL이 catalog 업스트림 예외(부족·미존재·**경합 소진**)를 **전수** 포트-선언 예외로 번역; 포트가 예외 집합 선언 | 경합/소진 예외가 ACL **미번역 raw 통과** |
| **(결과)** 경계 매핑 완전성 | `presentation/.../api*.py` 핸들러 + 실제 응답 | 소진→**의도된 retryable status**(미매핑 500 없음) | 소진 경로 **미매핑→500** |
| **C1/C2** reviewer 발화(누수 시) | 코디네이터 discipline-reviewer 노트 | 만약 ACL/핸들러 누락이 생기면 **C2 blocker / C1 important 발화**(라이브 차단) | 실위반인데 reviewer 미발화(DR-22 프로즈 실패 — P1a 전례) |
| 척추(상시) | SD-1~7·SH-1~10·NJ-1~6·FC-1~3·Q-1~7 | 빈혈 아님·계층 순수·Ninja 얇은 operation·BC FK 0·R/C/Q 명명 | 치명 레인 ❌ 1개 = 픽스처 FAIL |

> **유기적 한계(정직)**: DR-44는 주로 **생산자(예방) 측**이다 — A/E/D2가 architect·coder로 하여금 CAS 소진을 *전수 처리*하게 만드는지가 1차 관찰. **준수 런이면 C1/C2는 미발화(=정상)**. C1/C2 *발화*(차단 측)는 누수가 슬쩍 생겨야 보이는데, 사전 시뮬은 통과했으나 **라이브 발화는 미검증**(DR-22 위험: 프로즈 reviewer가 라이브서 미발화한 P1a 전례). 누수가 안 생기면 "예방 작동", 누수가 생겼는데 reviewer가 잡으면 "차단 작동", 누수가 생겼는데 미발화면 **DR-44 프로즈 갭**(→ 보류했던 B/백스톱 재개 트리거, REMAINING-ISSUES `ACL-EX`).

## 6. 한계 (정직)
**N=1.** 양 런타임 1회씩 = 우열 비교 아님. P4③ run-variance로 치명 FAIL 레인이 런마다 갈린다. 이 런은 **1.5.0(DR-44)이 rcqlive 흠을 라이브서 막나/잡나**의 방향타다. 드리프트/재발/미발화 발견 시 N≥2 후속(그때 B·백스톱 재검토). 정본=`workspace/design/2026-06-06-acl-exception-exhaustiveness.md`(v2)·DEVLOG DR-44·REMAINING-ISSUES `ACL-EX`.
