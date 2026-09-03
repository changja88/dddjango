# dddjango 플러그인 개선 로드맵 · 진행 대장 (2026-09-03 신설)

- 지위: 08-25 이후 플러그인 개선 효과(개정 배치·속도 리비전·수리 배치)의 **완료/진행/잔여를 한 장에 추적하는 관리 정본**. 각 배치의 설계·계획·리뷰 상세는 배치별 파일이 정본이고, 이 문서는 항목·의존·순서·결정 게이트만 관리한다.
- 갱신 규칙: 배치 착수·머지·릴리즈·설치 도달·결정 게이트 판정마다 해당 행을 갱신하고 §8 이력에 1행 append. 항목 번호(R-n)는 재사용하지 않는다.
- 관련 대장: pre-gate 관찰 실측 = `workspace/eval/pregate-observe/ledger.md` · 소요 조사 = `workspace/eval/2026-09-03-lane-duration-investigation.md` · 08-15 레인별 실행시간 보드 = `optimization-board.md`(08-15 이후 미갱신).

## 1. 완료

| # | 배치 | 릴리즈 | 날짜 | 핵심 내용 | 정본 |
|---|---|---|---|---|---|
| 1 | 플러그인 개정 배치(판정 12건) | v2.17.6 | 08-25 | 검사기 7건(#247·#245·#256/#351·#157/#484·#456·#197)·㉮ 철회 | `2026-08-25-plugin-revision-batch-plan.md` |
| 2 | #195 factory-born AnnAssign | v2.17.7 | 08-25 | kkebi 요청서 수리 | 커밋 51a0a53 |
| 3 | tarot 잔존 10건 → 판정 6건 | v2.17.8 | 08-25 | #440·#63 concrete 개정·#415+#107 보강·#389 삭제+#637 신설·#482 | 커밋 d69c842 |
| 4 | 리비전 7호 Result-match | v2.17.9 | 08-26 | 검사기 #15 match/elif 확장·#571 None path 정리 | 커밋 8fe7e5c·2f428ba |
| 5 | #101 자기-BC 한정 | v2.17.10 | 08-31 | ACL→OHS 규칙 충돌 봉합 | 커밋 b727c03 |
| 6 | 리비전 8호 신규 표면 스택 STOP | v2.17.11 | 09-01 | R-1645/R-0180 재정의·R-3403~3405 | `2026-09-01-new-surface-stack-stop-plan.md` |
| 7 | 리비전 9호 동명 폴더 승격 | v2.17.12 | 09-01 | R-3406~3422·규칙 #638~644·하위 검사기 10종 | `2026-09-01-slot-promotion-plan.md` |
| 8 | 리비전 10호 검사기·규범 정합 | v2.17.13 | 09-01 | #396 pydantic·베이스 3이름·#328↔#462 R-3423·#63 게이트·R-3417 rev2 | `2026-09-01-revision10-plan.md` |
| 9 | 속도 리비전 ⓪~⑦ pre-gate 관찰 모드 | v2.17.14 | 09-01 | 베이스라인·설계 v3·백테스트·R-3424~3438·`design_pregate.py` | `2026-09-01-pregate-ontology-plan.md`·design/2026-09-01-pregate-*.md |
| 10 | 수리 배치 1(라벨 닫힌 정의·스텁 충실도 5변경) | v2.17.15 | 09-02 | R-3433/R-3426 rev2·notification 소급 19→1 | `2026-09-02-pregate-repair-plan.md` |
| 11 | 소요 조사(fortune-reading 49h 해부) | 문서 | 09-03 | 22항목 분류·후보 8건 → 적대 리뷰로 3건 기각 | eval/2026-09-03-lane-duration-investigation.md |
| 12 | 수리 배치 2(3부) | v2.17.16 | 09-03 | Part 1 파서·마이그레이션·버전 스탬프·툴체인 digest·`--base` 재발화 / Part 2 registry provenance·R-3439~3441 / Part 3 계약 실존 3단·exit 5 | `2026-09-03-repair-batch-2-{rubric,plan}.md` |
| 13 | 관찰 실측 레인 3건(media-library·notification·email-template) | ledger | 09-02 | 오탐 0·미탐 0·③형 STOP 0 전 레인, 형식 반송 2·0·1 | pregate-observe/ledger.md |
| 14 | v2.17.16 양 런타임 설치·봉인 재발행 | 커밋 | 09-03 | cache_parity ok·조감도 추기 | 45d6b7c·7e93b08 |

## 2. 진행 중

| 항목 | 상태 | 완료 신호 |
|---|---|---|
| 수리 배치 3(R-5·R-6·R-7) — 루브릭 `2026-09-03-repair-batch-3-rubric.md` | 09-03 ⓪·① 완료 → **사용자 결정 ⓐ 보류·관찰 지속**(R-5d 처방 검증 상태로 대기·N-1 기각→R-1 이월) | 재개 트리거 = R-5 계열 ≥2 레인 발화 |
| spring_dream_server fortune-catalog 레인 관전 = pre-gate 승격 재실측(§8 전 기준) + 배치 2 효과 실측 | 09-03 12:22 런 폴더 `20260903-1214-fortune-catalog` · G0 통과(e1294f5·신규 BC·lens=ddd 단독·빚 0) · **G1 승인 13:43(9ee721e)** — pre-gate 4회(v2.17.16 스탬프) 형식 red 0·corrected 2(#392·#576 진탐·다음 실행 소멸)·filtered/ignored 0·실존 결손 0·처분 라벨 기재 적법 | `REPORT-fortune-catalog*.md` 발행 → ledger 레인 4 행 |

## 3. 잔여 항목 (의존·성격)

| R | 항목 | 성격 | 카탈로그 완주 의존 | 트리거·조건 | 출처 |
|---|---|---|---|---|---|
| R-1 | pre-gate 차단 승격 — `design_pregate.py` MODE 상수·R-3433/R-3436 개정(권고→반송 의무·skip 폐지)·manifest pipeline 그룹 등재 · **이월 2건(09-03 ①): R-3433 개정에 «구조 규칙(경로·폴더 존재 판정)은 filtered 대상 아님» 필수 조항 · 카탈로그 #392 처분 실측 병기** | 결정 게이트 | **예** | 레인 4 오탐 0·미탐 0·형식 ≤1 충족 → 10줄 브리프 → 승인 시 승격 배치 | 설계 v4 §8·ledger·배치 3 루브릭 ① |
| R-2 | 계약 실존 채널(exit 5) 차단 승격 | 결정 게이트 | **예(+1 레인)** | v2.17.16 레인 ≥2·도구 오류 0·진탐 ≥1 | 배치 2 Part 3 §10 |
| R-3 | 앵커 비조상 exit 승격 | 결정 게이트 | 아니오(증거 축적 유리) | 별도 결정 | 배치 2 Part 2 §8 |
| R-4 | Phase 2 main 머지 승인 시 `approved-merges.txt` 기록 | 운영(발주자) | 레인 중 | 미기록 시 provenance 채널 미발화 | 배치 2 Part 2 |
| R-5 | 스텁 문법 확장 잔여: #392 factory_boy·#160/#484 aux·abc.ABC/다중 base·**update 대상 symbols 병합(R-5d — P1 dedupe 검증됨·조건 5·관측 1레인 보류)**·자기 add ⑶ 이름 판정·동적 import/`import *`/네임스페이스 | 수리 이월 | 아니오 | 발화 ≥2레인 시(배치 3 ① 결과 09-03: 전건 필터 미달) | 배치 2 Part 1 §8·Part 3 §10·ledger 개선 후보 ① |
| R-6 | `--print-toolchain`·캐시 skip 행 «실존 결손 M건» 병기·소급 명세 픽스처 편입 | 수리 이월 | 아니오 | 수리 배치 3 후보 | 배치 2 Part 1 §8·Part 3 §10 |
| R-7 | 발화 매트릭스 EXPECTED 확대·rulepack 체인 문면 정렬 | 감사 이월(⑥) | 아니오 | 관찰 모드 기간 후속 | pregate ⑥ 감사 |
| R-8 | 리비전 10호 후속: naming ⓓ#36 환경 의존·CURATED_TECH↔tech_names 드리프트·A2 구조 마감(RHS 꼴 면제)·검사기 실행 인터프리터 계약 | 후보(미발주) | 아니오 | 실전 발화 시 | `2026-09-01-revision10-plan.md` |
| R-9 | 리비전 8호 잔여: 함수형 controller 형태 감지 결정적 백스톱 검사기 | 후보(미발주) | 아니오 | 실전 발화 시 | `2026-09-01-new-surface-stack-stop-plan.md` |
| R-10 | #571 nested variant/outcome 필드(검사기 밖·리뷰어 의존)·#16 registrar provenance 재확인·(선택) #189/#205 | 잔존 | 아니오 | 상세 접수 시 | 08-25 배치·리비전 7호 |
| R-11 | reading 레인 구판(v2.17.14) pre-gate 44회분 관찰 분석·소요 조사 최종 수치(≈60h) 갱신 | 분석 | 아니오 | 지시 시 병행 | speed-revision 메모리 |
| R-12 | **dddjango 발주 가이드**(배포본 `dddjango/README.md` + 템플릿) — 3부: G0 계약 최소본(목표·범위/비범위·허용 경로·상류 의존 실물·결정 전제·제약·수용 기준·결정 위임 범위·lens/런타임·머지 정책) · 운영 체크리스트(갱신 후 새 세션·상류 머지 후 개시·approved-merges.txt·exact 경로 pin 금지·exit 5 비차단·STOP 규약) · 템플릿. 산문 정본이되 내용은 렌더된 Coordinator Phase 0 문면에서만. 프로젝트 고유 관행(master.html·herdr·D-번호) 배제·kkebi 발주 문서로 일반성 대조 | 문서(신규) | 아니오 | 승격 배치 뒤 착수(사용자 09-03 «별개로») — 근거: STOP 25% 발주 모순·툴체인 pin STOP 2·approved-merges 미기재 위험·배포본 README 부재 | 09-03 대화 |
| R-13 | **dddjango-web 발주 가이드**(`dddjango-web/` 안 별도) — 같은 3부 판형·공통 운영 규칙 문장 공유 · G0 입력은 화면 요구·동결 시안·실물 API 계약 스냅숏·design_system 토큰 · 상류 의존 절에 «대상 API 계약이 dddjango 레인으로 완주·머지된 뒤» 교차 참조 · 정합 대상 = web 커맨드 md(산문 정본) | 문서(신규) | 아니오 | R-12와 같은 시점 | 09-03 대화 |
| R-14 | **현장 보고(typecheck) 수리 — 브랜치 `fix/field-typecheck` ④⑤ 완료·⑥ 감사 진입** — A: 값 객체 예제 교체 + R-3442(Obligation)·R-3443(Prohibition) 신설(`architecture-ddd` s016-3.1 · wiring discipline-reviewer 위임) · C′: 검사기 #493 import 별칭 해소(모듈 바인딩·그림자 pop·base+데코레이터) — C 문면(«하우스룰 §2 Enum 예외 누락»)은 ①에서 **불성립**(R-3154 기성문·조사자 검색 누락), 실물 뿌리 = 검사기 alias 오탐 · B 기각(발주측). 증거 `workspace/eval/field-report-typecheck/`(rv1·rv3·rv5·evidence-alias-strenum orig 6→0) · 양 저장소 차분 0 · verify 6/6 | 규범 리비전 + 검사기 수리 | 아니오 | ⑥ 감사·재검 → 릴리즈 게이트(즉시 v2.17.17 / 승격 배치 동승) · **미결 2(⑤ C MAJOR-1·3)**: R-3442 판별 기준(bool⊂int vs int→float — 하위 타입/수치 탑 승격으로 1문장 닫기)·적용 단위(값 객체 단위 vs 손대는 줄 단위 — houserules 줄 단위 전파 금지와 정렬) → rev2 clarification 사용자 결정 | 현장 보고 |
| R-15 | **base 이름 문자열 비교 family** — (a) 다른 검사기 5종의 별칭 미해소(`check-context-isolation.py:615`·`check-db-table.py:180`·`check-domain-model.py:846`·`check-port-adapter-pairing.py:137`·`check-usecase-dto-placement.py:171`) (b) #493 검사기의 **로컬 중간 base 전이 면제**(spring 27·kkebi 99 클래스 — 전 BC `bc_error_schema.py` · 08-31 promotion `TranslatableModelForm` 주석 우회 현존 · 현재 발화 0) | 검사기 후보 | 아니오 | 발화 관측 시 — R-14 Part 2와 같은 helper 판형(모듈 import 바인딩 해소) · 전이 면제는 면제 «추가»라 무손실 증명 별도 | 현장 보고 ③ 리뷰 C |
| R-16 | #493 검사기의 **파싱 실패 파일 조용한 green**(`check-public-surface-annotation.py` main — SyntaxError/OSError continue 후 «clean — 파일 N개»에 계수) — fail-closed 위반 후보 · 다른 검사기 동형 조사 필요 | 검사기 후보 | 아니오 | 다음 검사기 정합 배치 | 현장 보고 ③ 리뷰 A |
| R-14b | R-3442/3443의 **예방 경로 보강** — coder·discipline-reviewer는 `architecture-ddd`를 로드하지 않아(frontmatter) 관용구를 만드는 코더가 문면을 읽지 못함(⑤ C MAJOR-2). implementation-python 또는 coder md에 교차 참조 1줄 후보 · 문면의 «예방» 기대는 architect 명세 경유로 낮춤 | 규범 후보 | 아니오 | 다음 규범 정합 배치 | ⑤ 리뷰 C |
| R-17 | `architecture-ddd/references/final.md` 다른 예제 2곳(628·777행) `__post_init__(self)` 무주석 잔존 — 하우스룰 §4 자기 위반(범위 밖) | 문면 후보 | 아니오 | 다음 규범 정합 배치 | ⑤ 리뷰 B |

## 4. 권장 진행 순서 · 릴리즈 규칙

1. **R-11 분석** — reading 44회분에서 R-5 스텁 계열 발화 빈도를 뽑아 R-5 우선순위 근거로 삼는다.
2. **R-5·R-6·R-7 수리 배치 3** — 관례(원인→계획→적대 리뷰→적용→감사) · 브랜치 작업 · 릴리즈 보류.
3. **카탈로그 완주** → ledger 레인 4 행 → R-1 승격 브리프 → 승인 시 승격 배치 + 수리 배치 3을 함께 릴리즈.
- 릴리즈 규칙: 재실측 레인이 도는 동안은 릴리즈하지 않는다(재실측 데이터를 단일 버전으로 유지). Claude 캐시는 전 버전 보존이라 기술적 위험은 낮으나, Codex 레인이 병행 중이면 캐시 삭제로 STOP 위험(reading 선례 — pin은 배치 2에서 해소, 삭제 자체는 잔존).
- 레인 착수 규칙(발주측): 갱신 후 새 세션 · 상류 레인 머지 후 개시 · `approved-merges.txt` 기록 · exact 캐시 경로 pin 불요 · exit 5 비차단 래퍼 예외.

## 5. 결정 게이트 목록 (사용자 판정 필요)

| 게이트 | 입력 | 형식 |
|---|---|---|
| G-A pre-gate 차단 승격(R-1) | ledger 레인 4 §8 표 | 10줄 브리프·수치 기반 |
| G-B 계약 실존 채널 승격(R-2) | v2.17.16 레인 ≥2 결과 | 10줄 브리프 |
| G-C 앵커 비조상 exit 승격(R-3) | Part 2 스모크·레인 증거 | 10줄 브리프 |
| G-D 수리 배치 3 범위 확정 | R-11 분석 결과 | 항목 표 — **09-03 판정: ⓐ 보류(후보 전건 필터 미달)** |

## 6. 기각·비범위 (재제안 금지 포함)

G0 상류 하드 검사(R-3434 rev2로 봉인) · pytest 마커 정합 검사기 · symbols 대입식 관용(전제 오류) · 레인 경로 필터 · 도구 벤더링 · 자동 재앵커(epoch) · 라인 단위 provenance · #474(`__context__` 등가) · Result 노선 반전(D55) · #16 성문 없는 함수형 표면 승인.

## 7. 발주측 소관 (플러그인 밖)

character_catalog Ninja 전환 · turn_controller 실분해 · #396 빚 1줄 제거 · #63 헤더 계약 재추가 · 계정 BC 빚 11건 해소 확인 · 소비 명세 §6.3 래퍼 pin 정리. · **현장 보고 B(mypy·ruff format 결정적 G2 게이트) — 기각·발주측 소관**(프로젝트 툴체인 선택·pre-push 훅과 발주서 체크리스트가 소유 · R-12 가이드에 «툴체인 게이트는 훅·발주서 소유» 1줄만 반영 · reading REPORT의 mypy 무언급은 «미실행 사유 명시» 문면 미준수).

## 8. 이력

- 2026-09-03 신설 — 완료 14·진행 1·잔여 11 항목 기입. 카탈로그 레인 G0 통과 시점.
- 2026-09-03 수리 배치 3 착수(사용자 «진행해줘») — 절차 = 배치 2 판형 + ⓪ 증거 수집·⑥ 재검 보강. R-11 분석은 ⓪에 흡수.
- 2026-09-03 수리 배치 3 ⓪·① 완료 — 후보 전건 필터 미달/기각(R-5d 보류·N-1 기각→R-1 이월 2건). 증거 `workspace/eval/pregate-observe/reading-v21714/`(+rv1). 결정 게이트 G-D 상신.
- 2026-09-03 G-D 판정: 사용자 «권고안» = ⓐ 배치 3 보류·관찰 지속. 다음 = 카탈로그 완주 → ledger 레인 4 → G-A(R-1) 브리프(이월 2건 포함).
- 2026-09-03 사용자 «관전까지 다 하고 완벽하게 진행» — 카탈로그 완주 전 승격 배치 사전 준비 없음. 완주 후 ledger 레인 4 → G-A 브리프 → 승인 시 관례 전 단계로 승격 배치.
- 2026-09-03 R-12·R-13 등재 — 발주 가이드(dddjango/web 별개·판형 공유). 착수는 승격 배치 뒤.
- 2026-09-03 현장 보고(typecheck) 검증 — A·C 성립(R-14 등재) · B 기각(발주측 소관·사용자 확정).
- 2026-09-03 R-14 착수(사용자 확정 — 적대 리뷰 ①③⑤+감사 판형). B 기각 확정.
- 2026-09-03 R-14 ②③ 완료(계획 v2·문면 확정) → ④ 구현(브랜치 fix/field-typecheck: 검사기 alias 해소·픽스처·EXPECTED 3종·그래프 리비전 R-3442/R-3443·렌더·rulepack·LEDGER·미러) · R-15·R-16 등재.
- 2026-09-03 R-14 ④ 착지(b2e1f42·33b0bd7·27342a3) → ⑤ 적대 리뷰 3기 통과(BLOCKER 0·MAJOR 4는 문면 결정성 2 + 예방 경로 1 + 문서 stale 1) → MINOR 반영 · R-14b·R-17 등재.
