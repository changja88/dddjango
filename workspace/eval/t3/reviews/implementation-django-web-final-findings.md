# T3 적대 리뷰 — implementation-django-web-final (spec + worksheet)

- 리뷰 일자: 2026-08-22 · 리뷰어: 적대 검증 서브에이전트
- 대상: `workspace/eval/t3/specs/implementation-django-web-final.spec.json` · `workspace/eval/t3/worksheets/implementation-django-web-final.md`
- 대조 재료: T3-authoring-brief · orders/implementation-django-web-final.md · E09 센서스(classify/recon) · 원문 final.md(현재 424행 — 드리프트 0 재확인) · check-*.py 27종 docstring 전수 + 2종 구현부(`check-transient-overmapping._is_target_handler`·`check-domain-model._check_application_side`) 실독
- 도구 재검증: `ontology_migrate.py`(--write 없이) **exit 0 재현** — 블록 114 · Work 128 · 절별 계수 worksheet 표와 전량 일치

## 판정 요약

**high 0 · medium 0 · low 4 — pass.** 전 12절 전수 검사에서 반박이 성립하는 지적은 low 4건뿐이다. 아래 «검증 통과 확인» 절에 반박을 시도했으나 실물 대조로 기각된 항목을 남긴다(재리뷰 중복 방지).

## 발견 (심각도·절·주장·수정안)

### F1 — low · 재진술 · s009-8(연관: s008-7·s011-10)

- **주장**: 문서 내 잠재 재진술 후보 3쌍이 spec `restates`에도 worksheet 관찰에도 없다.
  ⑴ 249행(s009-8/b8 N2 «QuerySet/Manager는 implementation-django, DB 성능 설계는 architecture-db로 넘긴다») ↔ §1 위임표 30·31행(s002-1/b6·b7) — 같은 이관 지식.
  ⑵ 216행(s008-7/b6) ↔ §1 위임표 28·29행(s002-1/b4·b5) — 같은 목적지, 트리거만 다름.
  ⑶ 276행(s011-10/b10 security 행) ↔ 248행(s009-8/b7) — «check --deploy 실행·미실행 사유» 의무가 사실상 동일.
- **반론 여지(그래서 low)**: E09 센서스 restate 열도 세 쌍을 안 잡았고, 각 문장이 맥락 고유 규범력(raw SQL 격상 조건·HTMX 트리거·증거/gap 기준)을 실으므로 별도 Work 판정은 §15 «축자 쌍» 기준에서 방어 가능하다. worksheet 메모 ⑺의 논리(행렬 행의 규범력 = 증거 기준)와도 정합.
- **수정안**: spec 수정 불요. worksheet «재진술 유예» 또는 «경계 판단 메모»에 세 쌍을 «비재진술 판정 후보 관찰»로 남겨 소급 패스가 같은 물음을 다시 열지 않게 한다.

### F2 — low · 규범식별 · s004-3

- **주장**: b5 N2(«승인 표시 계약·독자 failure 의 add/update 한정 …·구조 규칙만의 테스트 생성 금지») class=Exception 은 이견 여지가 있다. 문면은 조건부 의무+금지 복합문이고, 이 문장이 «어느 규범의 예외»인지의 모(母) 규범이 같은 문서 안에 명시돼 있지 않다(입장 심사 기본 규율은 discipline-tdd 소유). Obligation(조건부) 또는 Prohibition 판정도 성립한다.
- **수정안**: spec 유지 가능. worksheet 경계 메모에 class 판정 근거(무엇의 예외인가) 한 줄 보강 권고.

### F3 — low · 규범식별 · s011-10

- **주장**: b1 N3(«test-shaped 증거의 비자동의무·candidate 취급») class=Obligation 은 문면이 의무의 *부정*(«자동 의무가 아니라 …다»)이라 Permission(비의무 허용) 해석 여지가 있다. N4의 Exception 도 F2 와 같은 복합문 계열.
- **수정안**: spec 유지 가능(취급-의무 독해도 성립). 재분류한다면 N3 → Permission. worksheet 근거 한 줄 보강으로 충분.

### F4 — low · 배선 · s011-10

- **주장**: §10 검증 행렬 행 간 위임 방법이 비대칭이다. b8(HTMX 행, #99)은 gap 열의 문서 지목을 근거로 `agent-design-review-api` 병기, b9(service 예외 행, #100)는 같은 구조(§11 지목)인데 «행렬 행은 증거·gap 기준» 논리로 리뷰어 단독. #100의 논리를 b8에 적용하면 병기 불요이고, b8의 논리를 #100에 적용하면 §11 검사기 축 병기가 필요해진다 — 어느 쪽이든 한 방법으로 통일되지 않았다.
- **반론 여지(그래서 low)**: b8 병기는 문면 근거(«gap 열이 architecture-api handoff 지목»)가 있어 §16 기본값 이탈 요건 자체는 충족 — 오배선은 아니다.
- **수정안**: spec 수정 불요. worksheet 배선 집계에 비대칭 사유(agent 병기는 문서 지목 문면이 있을 때만·checker 병기는 정본 규범에만) 한 줄 명문화.

### F5 — low · 배선 · s002-1

- **주장**: architecture-db/api 축 위임(s002-1/b7·s009-8/b8 N2 등)에서 §16 표의 근거 «동상»(= ddd 행의 설계/구현 시점 분리 준용 가능 독해)에 대한 시점 판정이 생략됐다. ddd 축 2건은 «화면 전에»·«먼저 결정» 시점 문면을 명시 논증했으나 db/api 축은 문서 지목만으로 design-review 로 보냈다.
- **반론 여지(그래서 low)**: §16 표의 db/api 행 기본 delegatedTo 칸 문면 자체는 `agent-design-review-db`/`-api` 단일 기재라, 칸 문면 그대로 따른 것으로 방어 가능하다.
- **수정안**: spec 수정 불요. worksheet 기본값 이탈 근거 절에 «db/api 축은 §16 칸 문면 단일 기재를 따랐고 시점 분리는 ddd 행에만 명문» 한 줄 추가 권고.

## 검증 통과 확인 (반박 시도 → 기각 근거)

- **① 경계·kind**: 전 114블록 경계선(빈 줄·펜스·표 행·`---`·단독 `>`)을 원문 행 실물로 대조 — 오지정 0. 코드 펜스 후행 빈 줄 포함(메모 ⑴)은 §13 «구분자는 선행 블록 후행 귀속»이 명령하는 형태라 «펜스 전체» 문면과의 긴장은 해소된 것으로 판정(반박 기각). 머리행+구분행 병합 블록은 §13 «표 행 묶음 — 행 범위» 자연 단위 허용에 부합(반박 기각). s007-6/b3(169행) 불릿의 kind=prose 는 규범 0 사실 진술이라 정당.
- **② 규범 식별**: 절별 발주서 계수(2·12·11·10·15·10·7·6·12·6·14·24=129) ↔ spec(128) 대사 — 유일 차이 s005-4 15→14는 §15 «정본 1곳 승격+사본 restates» 규율의 정당한 강등이고 worksheet §1이 판정 포함 사유를 기록. 비계수 처분 전건(4행 정의문·169행 사실·209행 정의문·288행 사실 2문장) 발주서 비고와 일치. class 5종 전수 점검 — F2·F3 외 이견 없음.
- **③ 배선**: 27종 docstring 전수 실독으로 basis 전건 실물 대조. enforcedBy 2건 모두 정확 — `check-transient-overmapping.py`의 부분 커버 서술은 구현(`_is_target_handler`: 데코/어노테이션 신호뿐 · 스캔은 경로 무관 프로덕션 `*.py`)과 축자 일치, `check-synthetic-infra-exc.py`의 ⑴ ACL-EX2·driven_layer 한정도 일치. 기본값 도피 검사: 잔여 25종 중 이 문서 규범을 담당하는 검사기 0 — 특히 check-domain-model #257 확정 신호의 application_layer 한정(구현 645행 실측)·check-ninja-boundary-middleware 의 순서 축 부재·check-test-config ⑵⑶ 축이 basis 서술과 일치. delegatedTo 8건 이탈 전건에 문면 근거 존재. agent doc_key 전건 registry 8종(`ontology_migrate.py` AGENTS) 안.
- **④ 재진술**: same-doc 쌍 1건(s005-4/b1→s002-1/b10)만 spec `restates` — 방향(사본→정본)·블록 서수 정확. 교차 문서 유예 20건 전건을 SKILL.md 실물 행과 대조 — 좌표·문면 일치, §5·§9 사본 구멍 관찰 정확, 발주서 재진술 열 전 절 커버. 유예 대상의 spec 혼입 0(`restates` 키 1개 실측).

Serena: skipped — 문서·spec 대조 리뷰라 기본 도구로 충분.
