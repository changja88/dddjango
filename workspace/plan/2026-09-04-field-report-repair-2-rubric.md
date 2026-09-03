# 현장 보고 수리 2 — 제보 수정 단계(D·E·F 문면·G·H) 절차·적대 리뷰 루브릭 (2026-09-04 사용자 «착수»)

- 대상: `2026-09-03-field-report-spring-dream-typecheck.md` 처분 상태 블록의 미결 5건 — D(항상 raise 도우미 `-> NoReturn` 문면 · R-18) · E(`Any` 정책 — 하우스룰 §4 절 + 검사기 #493 확장 · R-19) · F-1/F-2(composition root 주입 callable ≡ Protocol · 실배선 테스트 규율 — 문면 2줄 · F 본체는 발주측 36258bb 자체 수리) · G(발견 ⑪ boundary-imports 블록에 예외 소비 import 기재 조항) · H(발견 ⑫ pre-content 골격 상충 — Coordinator 골격 규범 ⓐ vs 검사기 면제 ⓑ 택일). A·A3·4·B·C 는 파트 1 종결(main 88a65a0).
- 성격: 그래프 정본 문면 리비전(D·F·G·H 후보) + 검사기 확장(E 후보 — byte 미러·픽스처 동반). 실행기(`design_pregate.py`) 무접촉 예정. 판형 = 파트 1 루브릭(`2026-09-03-field-report-repair-rubric.md`) · 승격 루브릭(`2026-09-03-pregate-promotion-rubric.md`) 동일: ⓪ 증거 → ① 문제 리뷰 ×3 → ② 계획 → ③ 계획 리뷰 ×3 → ④ 구현 → ⑤ 구현 리뷰 ×3 → ⑥ 독립 감사·재검. 매회 독립 서브에이전트 3기(A 기술·B 규범·C 증거/표본 외) · 3축(코퍼스 정합·일반화·무손실) · 심각도(BLOCKER/MAJOR/MINOR/검증됨).
- 결정 게이트 2(사용자 09-04 확정): ① 뒤 «범위 확정»(E 범위 — 시그니처 `Any` 0 무조건 · 변수 주석의 프레임워크 미러 자리 조건부 허용 여부 / H 택일 ⓐ·ⓑ / 나머지 유지·축소) → ⑥ 뒤 «머지 진행». 릴리즈·push 없음(사용자 요청 시 `make release`).
- 브랜치: `fix/field-report-2`(main c7573b6 기점). 산출: `workspace/eval/field-report-2/`(⓪ `evidence/` · rv1 · rv3 · rv5 · rv6).

## ⓪ 조사자(코디) 검증 결과 (2026-09-04 — 리뷰어는 이 전제를 공격한다)

(조사자 4기 실측 결과 병합 예정 — 아래 «코퍼스 좌표»는 코디 직접 확인분)

### 코퍼스 좌표 (코디 직접 확인 · 2026-09-04)

- **D**: 코퍼스 전체에 `NoReturn` 언급 0건(skills refs·SKILL.md·agents·command 전수 grep). `implementation-python/references/final.md` §1 «타입 힌트와 타입 시스템»(1.1~1.14 · 대부분 graph-owned) · §4.4 «None 반환 대신 예외 발생»(graph-owned · ttl `implementation-python-final.ttl` ≈806) · §15 «예외 처리»(15.1 산문 · 15.2/15.3 graph-owned) · §23 «mypy/pyright 최신 기능»(graph-owned). `sys.exit` 는 L442 match 예제 1곳뿐. → 착지 후보 = §4.4 블록 추기(예외 우선 문단과 같은 주제) 또는 §1.2 Optional 블록.
- **E**: 하우스룰 `discipline-houserules/SKILL.md` §4(graph-owned · 섹션 `s007-4` · b1 = R-3148/R-3149/R-3150 «모든 이름 첫 대입에 타입 — 예외 0» · «문법이 없는 자리» 목록 · 프레임워크 선언 예외 · «표준 문서군의 코드 예시는 개념 전달용 발췌라 적용 대상이 아니다») · §4.1 «왜 전부인가». 코퍼스 `Any` 언급 4건 전부 `architecture-ddd/references/final.md`(L485 R-3443 문장 «`object`/`Any`/JSON 입력의 타입 좁히기는 경계가 담당» · L1585~1619 Knowledge Level 예제 `values: dict[str, Any]`·`value: Any`). `Mapping[str, object]` 관용구 언급 0건. 검사기 #493 = `check-public-surface-annotation.py`(`_annotation_names` L341 · 함수 시그니처 L357~ · AnnAssign L379~ 순회).
- **F·G·H**: 조사자 실측에 코퍼스 좌표 포함(F = implementation-django-ninja composition_root 절·implementation-test/discipline-test · G = architect boundary-imports 형식 규범·design_pregate 스텁 방출 · H = Coordinator 골격 문면·#219/#635/#218/#193/#576 조건).

## ① 공격 질문 (항목마다 필답 · 판정 병기)

- D-1 «항상 raise 도우미 `-> None`» 이 플러그인이 만든 모양인가(코퍼스에 `-> None` raise 도우미 예제가 있는가) 아니면 코더 선택인가. 같은 저장소 다른 레인이 `NoReturn` 을 썼다면 «지식 부재» 가 아니라 «일관성» 문제 — 문면 1줄이 효과가 있는가(문면은 확률적 · B 기각으로 mypy 결정 실행은 없음). 표본 외(kkebi) 발생 유무.
- D-2 착지 자리(§4.4 vs §1.2 vs §15)와 문장이 기존 «예외 우선» 문단·OHS «부재·거절은 답» 경계 단서와 모순 없는가. `sys.exit` 까지 포함하는 문면이 dddjango 산출물(웹 서비스 · CLI 없음)에 과잉인가.
- E-1 «시그니처 `Any` 0 무조건» 이 실코드에서 지킬 수 있는가 — spring application `Any` 0 이 «레인이 이미 안 쓴다» 인지 «쓸 자리가 없었다» 인지. Django/ninja 프레임워크 미러(`clean() -> dict[str, Any]` · `request.user` · `**kwargs: Any` 오버라이드 · `Callable[..., Any]` 데코레이터)에서 `Any` 없이 mypy strict 를 통과하는 대체 형이 항상 존재하는가(`object` 로 바꾸면 상위 시그니처 호환 오류 나는 자리 열거).
- E-2 검사기 확장의 무손실: «명시 `Any`» 규칙이 현재 두 저장소 application 코드에서 몇 건 발화하는가(0 이 아니면 과거 산출물이 red 가 되는 소급 비용) · 제네릭 인자 안 `Any`(`dict[str, Any]`)를 위반으로 볼지 · 조건부 허용(프레임워크 미러)을 검사기가 결정적으로 구분할 수 있는가(못 하면 문면만 조건부·검사기는 시그니처만).
- E-3 규범 정합: §4 «예외 0» 취지 · R-3443 «`object`/`Any` 입력은 경계가 좁힘» · implementation-python 1.12 TypeIs · 12 pydantic strict · 23.1 mypy strict 설정 블록(`disallow_any_*` 언급?)과 새 절이 모순되는가. 아키텍처 예제(Knowledge Level `dict[str, Any]`)는 «예시 면제» 조항으로 커버되는가, 아니면 R-20(생성 모양은 strict 준수) 때문에 교체해야 하는가.
- F-1 «주입 callable ≡ Protocol 시그니처» 가 이미 #85·composition_root 절 문면에 함의돼 있는가(있다면 문면 추가는 중복 · 없다면 결손). 정적 대조로 검출 가능한 형상인가(검사기 후보로 승격할 근거) — 1레인 특이인지(표본 외 kkebi·spring 타 BC 불일치 0 이면 «문면 1줄» 이 적정).
- F-2 «BC 마다 실배선 테스트 1개» 가 implementation-test «매요청 호출 … 테스트 오버라이드 회피» 문면·#389(integration 은 실DB 자리)·#13/#385(타 BC OHS 계약 import 금지)와 정합한가. «1개» 강제가 기존 레인 산출물을 소급 red 로 만드는가(검사기 없음 → 감수자 판단 · 과적합 경계).
- G-1 «채널 전사 결손» 판정이 맞는가 — 블록에 적혔다면 pre-gate 가 #93 을 예보했을 것(실행기 스텁 방출 실측)인가, 아니면 애초 architect 가 «예외 소비 import» 를 블록 대상으로 인식할 문면이 없었는가(규범 문면 해석). 7건 명세 중 블록 밖 예외 소비 import 가 있는 명세 수(≥2 면 일반화).
- G-2 조항 추가의 무손실: 기존 명세 7건이 형식 red 가 되는가(소급 비용) · 예외 «소비」 import 를 블록에 넣으면 pre-gate 가 #93 을 **예보**하는 것이지 **막는** 것이 아니므로 설계 진화(use case 번역)가 그 시점에 일어나는 효과 = Phase 2 왕복 1회 절감 — 과대 추정 여부.
- H-1 캐스케이드 3종(#218/#193/#576)이 «빈 파일 삭제» 에서 결정적으로 발화하는가 — 아니면 카탈로그 레인의 특정 상태(다른 파일이 그 모듈을 import) 때문인가. ⓐ Coordinator 골격 규범이 «첫 슬라이스가 채운다» 로 바뀌면 슬라이스 0 골격 자체(디렉터리·`__init__.py`)와 pre-gate 스텁 실체화가 충돌하는가.
- H-2 ⓑ 검사기 면제는 «빈 모듈 영구 잔존» 을 허용하는가(0바이트 `.py` 실태) · 면제가 다른 규칙(#219 «하나»)의 취지를 약화하는가. ⓐ/ⓑ 외 제3안(빈 파일 대신 `raise NotImplementedError` 골격 / 골격 단계 검사기 스코프 제외)이 무손실인가.
- ⓒ 효과 전체: 5건을 고치면 무엇이 줄어드는가(레인당 왕복·분) — 각 항목의 관측 n(spring 런 · kkebi 런)과 «플러그인이 만든 모양 / 검사가 잡는 누락 / 반복 문면 후보» 분류(현장 보고 «판단 기준 4») 재확인.

## 3·5단계 3축 · 심각도

파트 1 루브릭 준용. 코퍼스 정합 = 건드리는 IRI·검사기·문법 성문 전수 열거(하우스룰 §4 절 신설 시 R-3148~3150 과 관계 명시 · 검사기 확장 시 docstring·registry·rulepack 5표면). 일반화 = Claude/Codex 동일·프로젝트 플래그 비의존·kkebi 대조. 무손실 = 검사기 검출 집합 변화는 «추가만»(E) · 게이트 강도 불변(G 는 예보 확대 · H 는 면제 추가 시 별도 증명).
