# DR-49 데이터소스 골격 개정 — 라이브 검증 핸드오프

> ✅ **완료(DR-50·2026-06-08)** — dual 라이브·채점 완료(Codex 정적FAIL 발견1·FC-2 / 데이터소스 골격 ①②③④ 입증 / Claude 정적준수·상). 결과지 `results/20260608-2143-dslive-codex.md`·`results/20260608-2156-dslive-claude.md`·DEVLOG DR-50. 아래는 실행 기록(참고).
>
> compact 후 이 문서로 라이브를 실행한다. 정본 = DEVLOG DR-49 · 메모리 `[[dddjango-datasource-skeleton-mandate]]` · 커밋 `d2a5536`. 방법론(캐시 신선화·fixture·프롬프트·게이트)은 `CBVLIVE-HANDOFF.md`와 동일 — 이 문서는 **DR-49 검증 포인트**를 더한다. DR-48(클래스 컨트롤러)도 같은 fixture라 **동시 관측**된다.

## 상태 (2026-06-08)
- DR-49 개정 커밋 `d2a5536`(eval/codex-determinism-n2·🔴미푸시): §632-(2) 데이터소스 면제 폐지 · application 이하 모든 BC 골격 무조건 · SH-3 치명 격상 · 발견1(catalog 두 군데) SH-1 복원. 표준·에이전트·평가지·백스톱 양 미러 byte-id. 적대검증 SHIP.
- 🔴 **캐시 재신선화 필요** — `CBVLIVE-HANDOFF.md`의 "1.9.0 신선화 완료"는 DR-49 *이전*. `d2a5536`(특히 houserules/ddd final.md·design-architect·discipline-reviewer·design-review-ddd·coordinator·check-layer-skeleton.py) 미반영. **라이브 전 필수**.
- 🔴 **fixture 재구성 필요** — 기존 `~/Desktop/dddjango-cbvlive-*`는 이전 산출물 오염. 깨끗한 baseline 재구성.

## 캐시 재신선화 (DR-19·라이브 전 필수)
```
rsync -a dddjango/      ~/.claude/plugins/cache/changja88/dddjango/1.0.0/
rsync -a codex-dddjango/ ~/.codex/plugins/cache/dddjango-local/dddjango/1.0.0/
```
- 후: `md5 -q` 일치 검증(변경 파일 집중) + **새 세션**(`/reload-plugins`는 캐시 재복사 안 함).
- (선택) plugin.json 버전 범프 1.9.0→1.10.0 — 캐시 무효화 확실히.

## fixture (CBVLIVE-HANDOFF와 동일 재구성·깨끗한 새 경로)
- baseline `17d25a3`(aclex2live-codex 레포 `git archive`) + Django 4.2.30·django-ninja 1.6.2·django-ninja-extra 0.31.4 + 평면 `catalog.Product`(name/price/stock·Widget10·Gadget3 시드 db) + `manage.py`·`requirements.txt`·`.gitignore` + `git init` 순수-프로젝트 커밋.
- 🔴 **eval-meta 제거**(컨닝 차단): `PROMPT.md`·`README.md`·`setup.sh` 전부 삭제(setup.sh는 venv·시드 1회 셋업에만 쓰고 삭제).
- **catalog = 평면 Product 선재**(빈 startapp 아님) = touched 데이터소스 → **골격 의무 트리거**(DR-49 핵심 조건). 새 경로 예: `~/Desktop/dddjango-dslive-{claude,codex}`.

## 프롬프트·게이트 (사람 직접 입력 — fixture에 PROMPT.md 없음)
**프롬프트(토씨 그대로)**:
> 재고가 부족하면 409로 거절하고, 충분하면 재고를 차감하며 주문을 생성하는 API.

**고정 게이트**: G0 BC=**① 새 독립 orders BC**(자율 제안 ①이면 승인·아니면 정정) · 렌즈 ddd+db+api · **API 스택=Ninja** · 테스트 러너 표준기본 · 멱등성 미도입·transient=503 · G1/G2 명백 결함만 반송 · thinking OFF · 외부공개 물으면 "내부전용".
- **실행**: 각 fixture cwd에서 Claude=새 세션→`/dddjango`+프롬프트, Codex=`codex` 세션→프롬프트. 🔴 이 플러그인-개발 세션에서 직접 돌리지 말 것(cwd 오염·구버전 로드).

## 검증 대상 (DR-49 핵심)
1. **데이터소스 catalog 골격 생성**(★핵심): touched catalog가 `application/catalog/`로 이주하며 **빈 골격 무조건** — `domain_layer/<aggregate>/{entity,value_object,repository,port,...}`(**애그리거트명=ORM 모델명 도출** `ProductModel`→`product`)·`presentation_layer/{api,schema}`·`infra_layer/acl`를 빈 패키지(`__init__.py`)로. 유스케이스 없으면 `application_layer`만 빈 계층. (architect 명세·coder 산출 관측.)
2. **check-layer-skeleton 라이브**: 골격 완비 시 exit0·**거짓양성 0**(정상 ordering BC 무발화). 데이터소스 골격 미비 시 exit2(생산 게이트 차단). ← *post-revision 첫 라이브 거짓양성 검증*.
3. **design-review-ddd 감수**: "평면 OK" 아닌 "데이터소스도 골격 무조건"으로 감수(평면 루트 데이터소스 반송).
4. **SH-3 치명 채점**: 종류 폴더·골격 준수(SH-3 PASS·미비 시 치명 FAIL).
5. **발견1(루트 잔재)**: 모델 이주 시 루트 `catalog/` 잔재 0(완전 이주)인가. 🔴 생산시점 백스톱 사각(`check-app-container` G3 면제) — reviewer가 루트 잔재를 잡는지 관측(잡으면 #1 후속 백스톱 불요 신호).
6. **DR-48 동시 관측**: ninja-extra 클래스 컨트롤러 생성·NJ-1 PASS·백스톱 16종 정상.

## 채점
- 개정 평가지로 dual 채점(RUBRIC SH-3 **치명**·마스크 C §1.1.M "위치·골격 ⊥ 판정 실내용"·EVAL 치명 정본 **SH-1·2·3·4·7**·§2.3③ 데이터소스 빈 골격 정당).
- 결과지: `results/<YYYYMMDD-HHMM>-dslive-{claude,codex}.md`.

## 기대·주의
- 양 런타임 데이터소스 catalog 골격 생성 + check-layer-skeleton exit0 + SH-3 준수면 **개정 효과 입증**.
- 🔴 **N=1·생성물 비결정·우열 금지·post-revision 첫 라이브**.
- **후속 신호**: 라이브서 reviewer가 루트 잔재를 important로 잡으면 발견1 생산시점 백스톱(check-app-container 강화)은 불요·prose 레인으로 충분. 못 잡으면 백스톱 보강 우선순위↑.
