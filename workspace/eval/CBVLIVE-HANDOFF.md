# CBV 2차 라이브 검증 핸드오프 (DR-48 ninja 클래스 컨트롤러)

> compact 후 이 문서로 라이브를 실행한다. 정본 맥락 = DEVLOG DR-48 · `[[dddjango-ninja-cbv]]` · spec/plan `workspace/specs/2026-06-08-ninja-class-based-views-{design,plan}.md`.

## 상태 (2026-06-08)
- 표준·에이전트·평가지·백스톱이 모두 클래스 컨트롤러 전제로 정합(11커밋·**미푸시**·브랜치 `eval/codex-determinism-n2`).
- **캐시 1.9.0 신선화 완료**(diff -rq 전수 일치 양 런타임·`__pycache__` 노이즈만). 라이브 준비됨.
- **fixture 2개 = 직전 라이브 baseline 동일 재구성 완료**(아래 ## fixture). 새 세션 dual `/dddjango`만 남음.

## 캐시 경로 (편집 시 반드시 재신선화 — DR-19)
- Claude: `~/.claude/plugins/cache/changja88/dddjango/1.0.0/` ← `rsync -a dddjango/ <캐시>`
- Codex: `~/.codex/plugins/cache/dddjango-local/dddjango/1.0.0/` ← `rsync -a codex-dddjango/ <캐시>`
- 편집 후: rsync + `md5 -q` 일치 검증 + **새 세션**(`/reload-plugins`는 캐시 재복사 안 함).

## fixture (✅ baseline 동일 재구성 2026-06-08)
- 경로: `~/Desktop/dddjango-cbvlive-claude` · `~/Desktop/dddjango-cbvlive-codex`.
- **직전 라이브(aclex2live·maj1live)의 공통 baseline `17d25a3`("config + catalog.Product + 고정 프롬프트/시드/셋업 = 스모크 마스터")을 그대로 복제 + ninja-extra만 추가**(= 단일 변수). aclex2live-codex 레포에서 `git archive 17d25a3`로 추출.
- 스택: `.venv`(py3.9.6) + **Django 4.2.30 · django-ninja 1.6.2**(직전과 동일) **+ django-ninja-extra 0.31.4**(CBV 단일 변수). requirements 3줄.
- 구성(에이전트가 보는 것): `config`(catalog 등록·plain) + **평면 `catalog/`(Product: name/price/stock)** + **Widget(10)·Gadget(3) 시드 db** + `manage.py` + `requirements.txt` + `.gitignore`. `git init` 순수-프로젝트 커밋(라이브 후 코드 `git diff`로 산출물 캡처·`.dddjango/`는 gitignore라 직접 read).
- 🔴 **반칙 차단(사용자 적출)**: 평가 메타 `PROMPT.md`(고정 게이트 답·스코프 노출)·`README.md`("이건 평가 fixture·PROMPT에 답 있다" 안내)·`setup.sh`(셋업 도구)를 **fixture에서 전부 제거**. setup.sh는 venv·시드 1회 셋업에만 쓰고 삭제 → 에이전트가 게이트 정답을 컨닝 못 함. (Codex가 직전 런에서 "PROMPT.md 고정 게이트 답은 ①" 그대로 읽은 게 증거.)
- 검증: venv·설치·migrate·시드·check 0 issues · ninja-extra import OK · `Product 시드=[(Widget,10),(Gadget,3)]` 양쪽 · 메타 3파일 부재 확인.
- ⚠️ catalog는 **평면 Product 모델 선재**(빈 startapp 아님) — "재고는 기존 catalog 소유" 성립 조건. (이전 빈-catalog·PROMPT 포함 fixture는 폐기·교체됨.)

## 라이브 절차 (정식 통제 입력 — 직전 라이브와 토씨/게이트 동일)
> 🔴 아래 프롬프트·게이트 답은 **사람이 직접 입력**한다 — fixture엔 PROMPT.md가 없다(컨닝 차단). 이 핸드오프가 유일한 사람용 입력처. 게이트는 에이전트가 **자율 제안**하게 두고, 사람이 아래 통제값으로 **승인/정정**한다.

**프롬프트(토씨 그대로 양 런타임에 붙여넣기)**:
> 재고가 부족하면 409로 거절하고, 충분하면 재고를 차감하며 주문을 생성하는 API.

**고정 게이트(직전 aclex2live 통제 — API 스택만 CBV 위해 Ninja 유지가 핵심)**:
| 게이트 | 답 |
|---|---|
| G0 배치(BC) | **① 새 독립 orders BC** (직전 aclex2live 산출물 `new independent order area` 동일·DR-14 결정성. 에이전트가 ①을 자율 제안하면 승인·다른 제안이면 ①로 정정) |
| G0 렌즈 | ddd + db + api |
| **API 스택** | **표준기본(Ninja)** — CBV 검증 대상. 직전 ninja 라이브도 Ninja로 켰음(과거 plain Django는 스택변수 제거용 옛 스모크 답이라 무관) |
| 테스트 러너 | 표준기본 |
| G1 멱등성 | 미도입 · transient=503 |
| G1·G2 승인 | 명백 결함만 반송 |
| thinking | OFF |

- 외부 공개 여부 물으면 **"내부전용"**(415 C정책 비적용 관측).
- **실행**: 각 fixture cwd에서 — Claude=새 Claude Code 세션→`/dddjango`에 §1, Codex=`codex` 세션→§1 프롬프트.
- 🔴 **이 플러그인-개발 세션에서 직접 돌리지 말 것**(cwd 오염 + 1.9.0 신선화 이전 시작이라 구버전 로드 위험·DR-19).
- 끝나면 `git -C <fixture> status/diff`로 산출물 캡처 + 채점(RUBRIC). ★ reviewer "무조건 클래스"는 자연 준수면 미발화 정상 → 함수형 주입 프록시로 별도.

## 검증 대상 (2차 라이브 핵심)
1. **클래스 컨트롤러 생성**: touched presentation → `@api_controller` + `<aggregate>_controller.py` + `register_controllers` + `NinjaExtraAPI`. 함수형 `@router.post` operation 잔존 **0**(외부공개 415 격리 예외 제외).
2. **reviewer "무조건 클래스" 실발화**(★핵심): 함수형 operation을 주입했을 때 discipline-reviewer가 **important**로 지적하는가(DR-21식 권고 강등 안 하는지). 별도 top-level 불릿로 가시화돼 있음.
3. **415 C정책**: 내부전용 기본 비적용이 정상으로 통과(reviewer 415 부재 비지적)·외부공개 *명시* 시 함수형 Router 격리.
4. **등록 단일 인스턴스 BC로컬**: `config`가 단일 `NinjaExtraAPI` 소유·`<app>_api_router.py`가 import해 등록(BC별 인스턴스 분열 0·catch-all 보존).
5. **기존 백스톱 16종 회귀 매트릭스**(DR-29식): 클래스 컨트롤러 픽스처에서 각 게이트 정상(known-bad exit2·known-good exit0). 특히 `check-{response-schema-bypass,openapi-error-declaration,error-centralization}`이 `from ninja_extra` 파일을 *스캔*하는지(0차 봉합 라이브 확인).
6. **NJ-1 PASS**: `NinjaExtraAPI`+`@api_controller` 스택을 채택으로 인식(JsonResponse/DRF 아님).

## 기대 · 주의
- 양 런타임 클래스 컨트롤러 생성 + reviewer important 발화 + 백스톱 정상이면 **효과 입증**.
- 🔴 **N=1·생성물 비결정·우열 금지**. 라이브 발화는 함수형 주입 프록시일 수 있음(자연 발화 아님).
- **3차 백스톱**("무조건 클래스" 부재신호)은 라이브 N≥2 후 신설.

## 백로그 (라이브와 별개)
- 정본↔skill 드리프트(전 11스킬·옵션A 보존) · `houserules §6.2` 섹션 본체 · reviewer `§6.1/§6.2` test-stack · test §20 · **푸시**(미요청).
