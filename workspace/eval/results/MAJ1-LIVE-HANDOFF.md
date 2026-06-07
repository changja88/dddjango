# maj1 처방 라이브 dual 재검증 핸드오프 (2026-06-07)

> 너가 `/dddjango`를 직접 돌리고(드라이브), 끝나면 내가 산출물을 읽어 채점한다.
> **목표**: maj1 3층 처방(커밋 `57e6141`·plugin 1.6.0)이 라이브서 *실현(salience 효과)/발화(⑭ 차단)*하나.
> **정직 경계**: **N=1·P4③** — maj1은 런마다 갈리는 비결정(직전 Codex 준수/Claude 미준수)이라 1회로 *증명*이 아니라 *비결정 폭 축소* 관찰. 우열 결론 아님.

## 0. 준비 상태 (내가 완료)
- ✅ **캐시 신선화 1.6.0**: Claude(`~/.claude/plugins/cache/changja88/dddjango/1.0.0`)·Codex(`~/.codex/plugins/cache/dddjango-local/dddjango/1.0.0`) 둘 다 편집 10파일 `diff` IDENTICAL·버전 1.6.0·게이트 **14종**·⑭ `check-transient-overmapping.py` 안착.
- ✅ **커밋 `57e6141`**(maj1 3층 처방·18파일·미푸시·브랜치 `eval/codex-determinism-n2`).
- ✅ **fixture greenfield**: `~/Desktop/dddjango-maj1live-{claude,codex}` — baseline clone(claude `6e48b68`/codex `32d1cf5`)·`.venv` **Django 4.2.30만**(ninja/pytest 미설치)·catalog.Product·**Widget(10)·Gadget(3)** 시드·`order` 없음·`manage.py check` 0 issues.
- ⚠️ **반드시 새 세션** — 캐시를 방금 갱신했다(기존 세션은 구 에이전트 텍스트 메모리 보유; 쓰려면 `/reload-plugins` 후).

## 1. 태스크 (직전 라이브와 **동일 입력**·변수 통제)
```
주문 생성 API. 별도 주문(order) 개념으로, 요청 상품·수량의 주문을 만든다. 재고는 기존 catalog가 소유하며, 주문 생성 시 catalog의 재고를 차감한다(재고 부족 시 409).
```
> ⚠️ 동시성·CAS·예외 형식·입력 상한을 **프롬프트에 명시하지 않는다** — 표준이 스스로 하는지가 관찰면. 이 태스크가 낙관적 CAS 동시성을 끌어내 `OperationalError` 핸들러(maj1 관찰점)를 자연 발생시킨다.

## 2. 고정 게이트 답 (직전과 동일)
| 게이트 | 답 |
|---|---|
| G0 BC 배치 | **미강제** — "표준 판정-소유 원칙대로 결정해줘" |
| G0 렌즈 | **ddd + db + api** |
| G0 스코프 | **제안대로** |
| API 스택 | **"표준 기본대로"** — ⚠️ plain 강제 **금지** |
| 테스트 러너 | **"표준 기본대로"** |
| G1 멱등성/버전 | **미도입**(`/api/orders`) |
| G1 409 본문 | available/requested 노출(기본) |
| G1 설계 / G2 구현 | **명백한 결함만 반송**(경계 예외 매핑 완전성은 *관찰 대상*) |
| thinking | **OFF** (coder) |

## 3. 실행
**Claude**: `cd ~/Desktop/dddjango-maj1live-claude` → `claude`(새 세션) → `/dddjango` → §1 → §2
**Codex**: `cd ~/Desktop/dddjango-maj1live-codex` → `codex`(새 세션) → §1 → §2
**끝나면 스모크**: `.venv/bin/python manage.py check && .venv/bin/python manage.py migrate && .venv/bin/pytest`
**끝나면 나에게 "claude 끝났어" / "codex 끝났어"** — 내가 fixture에서 직접 읽어 채점.

## 4. maj1 확인 포인트 (이 라운드 초점)
### ⓐ 자연 관측 — 사용자 런 결과로 내가 채점
- coder가 `OperationalError`/`DatabaseError` 핸들러를 만드나(CAS·동시성에서 자연 등장).
- 만들면 **영구장애 구별 분기**가 있나? — **salience 효과**: `if not _is_retryable_db_error(exc): return _server_error(...)` 또는 sqlstate 분기로 영구장애 500·transient 503/409. (직전 Claude 흠 = 분기 0개·무조건 503.)
- **⑭ G2 게이트 배선**: coordinator가 G2 직전 **14종** 백스톱 실행 → clean 준수면 ⑭ exit0.
- reviewer 'transient 과잉매핑' — 준수 런이면 미발화(정상).
### ⓑ ⑭ 라이브 배선 검증 — 내가 채점 때 (DR-30식 위반 주입)
- clean 런 후, OperationalError 핸들러를 *무판정 통째 503*으로 개악 주입 → ⑭ 직접 실행 **exit2 차단** 확인(정밀도 시제품은 통과, 라이브 배선은 주입 프록시로).

## 5. 채점 신호
- **maj1 PASS**(실현): OperationalError/DatabaseError 핸들러가 분기로 영구장애(500)·transient(503/409) 구별. probe: `OperationalError("disk I/O error")` → 503 아님(500). **FAIL**(재발): 분기 0개·무조건 503 → ⑭이 잡아야(잡으면 게이트 반송=처방 작동).
- **척추(치명 레인)**: SD-1~7·SH-1·2·4·7·NJ-1·2·FC-1~3·Q-4 — 빈혈 아님·계층 순수·Ninja 얇은 operation·BC FK 0·테스트 진정성. **치명 ❌ 1개 = 픽스처 FAIL.**

## 6. 한계 (정직)
**N=1·P4③**. salience 효과는 1회로 *증명* 아님(비결정 폭 축소가 목표). ⑭ 차단력은 위반 주입으로 결정적 확인. 정본 `ACLEX-R2-ENFORCEMENT-PLAN.md §8`·메모리 `dddjango-aclex-r2`.
