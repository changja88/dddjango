# T3 적대 리뷰 라운드 2 — discipline-tdd-final (spec + worksheet)

- 대상: `workspace/eval/t3/specs/discipline-tdd-final.spec.json`(2026-08-22 15:36판) · `workspace/eval/t3/worksheets/discipline-tdd-final.md`(15:39판)
- 대조: 발주서 `workspace/eval/t3/orders/discipline-tdd-final.md` · 계약 `workspace/eval/t3/T3-authoring-brief.md` · 원문 `dddjango/skills/discipline-tdd/references/final.md`(1122행 실측 일치·드리프트 0) · `dddjango/scripts/check-*.py` 27종 docstring 선두 전수 실독 · `workspace/tools/ontology-authoring.md` §13~§16 · 파일럿 spec 2건 실물
- 검사 방식: 44절 전수 — 180블록 행 범위·kind를 원문 행과 전건 대조(스크립트로 연속·비중첩·절 스팬 커버 기계 재검), 발주서 규범 수 44행 전건 대사, basis를 검사기 docstring 실물로 대조, restates 9건·유예 13건 좌표 실독. `ontology_migrate.py` 검증 전용 재실행 **exit 0** 재현(절 44 · 블록 180 · Work 150 신규).
- **라운드 1(F1~F4, 15:31판) 처리 확인**: F1(s015-4.2 뒷절 승격→4=4)·F2(s058-12.1 전량 강등→0) **반영 확인**(class 분포 O96→97·P30→29 정합). F3 미반영 판정(형제 Prohibition 관례 ⑴~⑷)과 F4 기준 명문화(워크시트 §4)는 **논거 성립으로 수용** — 재반박하지 않는다.

## 발견 (심각도 순)

### N1 — medium · 재진술 · s015-4.2

**주장**: s015-4.2/b2(244행)의 `restates`가 `s025-5.5/b12`만 지목하는데, 같은 블록의 **첫 문장** «시스템 장애가 보고되면 먼저 §5.5의 candidate로 두고 **승인 계약·독자 production failure·기존 권위 coverage를 확인한다**»는 s025-5.5/b2(398행 심사 행 확정 의무 — 심사표의 protected contract·unique failure·existing coverage 3열)의 **압축 재서술**이다. 이는 워크시트 §4가 F4 대응으로 명문화한 restates 기재 기준 ⑵ «정본 규범의 내용을 조건절·압축 행으로 재서술한 경우»에 정확히 해당하며, 같은 기준으로 처리된 s069-17.4/b1의 Admission 행(«계약·독자 failure·기존 coverage로 decision 확정» → Work 유지 + restates→b2)과 문면이 사실상 동일한 압축인데도 이 블록만 b2 연결이 없다 — 자기 기준의 비대칭 적용. Work #16 유지(트리거+절차 배치가 §5.5에 없음)는 옳고, 문제는 restates 배열의 대상 블록 누락뿐이다.

**수정안**: s015-4.2/b2의 `restates`를 `["discipline-tdd-final/s025-5.5/b12", "discipline-tdd-final/s025-5.5/b2"]`로 병기하고 note에 «첫 문장 = b2 심사 3열의 압축 재서술(s069 Admission 행과 동형), 둘째 문장 앞절 = b12 사본»으로 사유를 분리 기재. Work·계수는 불변(4=4 유지).

### N2 — low · 재진술 · s001

**주장**: s001/b1에서 강등된 문장(4~5행)의 **전반절** «요구·버그·피라미드·예제는 먼저 candidate일 뿐이며»는 s025-5.5/b2 둘째 규범(#37 «후보 목록·피라미드·coverage·과거 버그·상위 실패는 심사 우회 근거 아님»)과도 겹치는데 restates는 b17(후반절 «reuse·reject write 0»의 정본)만 지목한다. 센서스 비고가 «reuse·reject→write 0 규칙 3중 사본»으로 후반절만 짚었으므로 b17 단독도 방어 가능하나, 블록 단위 restates의 대상 배열에 b2를 병기하면 소급·소비층의 해상도가 나아진다. 축자 아닌 취지 겹침이라 확신 낮음.

**수정안**: s001/b1 restates에 `discipline-tdd-final/s025-5.5/b2` 병기 검토(미병기 시 워크시트 §3.1 #1 근거란에 «전반절은 b2 취지 겹침이나 축자 아님 — 미기재» 한 줄 명시로 갈음 가능).

### N3 — low · 규범식별 · s025-5.5

**주장**: b34(440행) 셋째 Work #60 «두 근거가 충돌하거나 어느 쪽도 명확하지 않을 **때만** `pending`이다»의 class Obligation은 문형과 어긋날 수 있다. 이 문서의 Exception 4건(#58 «형식만을 이유로 일괄 금지 배제»·#65 «…독립일 때만 각각 add»·#75 «…관련 테스트만 조정»·#116 «…있을 때만 후보») 전건이 같은 «…때만» 한정 문형인데 #60만 Obligation이다. 직전 Permission(#59 택일 입장)의 적용 범위를 좁히는 한정이라 Exception 독법이 형제들과 더 정합적. 다만 «그 경우에는 pending해야 한다»는 의무 독법도 성립해 low.

**수정안**: #60 class를 Exception으로 재검토하거나, 워크시트 §4 class 판정 메모에 «…때만+의무 결과» 문형의 Obligation/Exception 판정 기준 한 줄 추가.

### N4 — low · 규범식별 · s006-2.1

**주장**: b4(40행) Work #8 «명백한 깔끔한 해법의 즉시 입력»의 class Permission은 원문 명령형 «깔끔한 해법이 명백히 보인다면 **그것을 입력하라**»와 긴장이 있다. 같은 행의 형제 분기 #9(«몇 분 걸릴 것 같으면 적어 두고 복귀» = Obligation)와 조건-분기 구조가 대칭인데 class가 갈린다. 초록 막대 전략(§6 Fake It/명백한 구현)의 선택지 맥락으로 읽으면 Permission도 방어 가능해 low.

**수정안**: #8을 Obligation(조건부 의무)으로 통일하거나, 워크시트 §4 class 메모의 Permission 용례 목록에 40행 분기를 명시해 판정을 고정.

### N5 — low · 재진술 · 유예 목록(워크시트 §3.2)

**주장**: 유예 13건이 전부 `discipline-tdd-skill` 상대다. 이 문서가 **정본**인 교차 사본 가운데 **이미 저작된** 문서의 것 — 예: `agent-discipline-reviewer` s005/b6(L54 «첫-Green 비계 즉시 제거·기존 비계 임의 삭제 금지» ≈ 444행 s025-5.5/b36) · s007/b4(L68 «신규·확장 migration 전용 테스트 금지» ≈ 459행 b46, basis가 «discipline-tdd §5.5 인용» 명기) · `dddjango/agents/design-architect.md` 83행(«pending은 … G1 … reuse·reject는 test artifact write가 0» ≈ 418행 b17) — 이 미등재다. 규약상 restates·유예의 1차 책임은 사본 측 문서라 이 워크시트의 의무는 아니나, 실측한 사본 측 워크시트(`agent-discipline-reviewer` §3 R4)가 상대를 `agent-coder`·`command-dddjango`로만 지목하고 discipline-tdd-final 쪽 다리를 잡지 않아 **양쪽 모두에서 빠진 쌍**이 확인된다 — 소급 패스 누락 위험. 책임 소재가 갈려 확신 낮음 → low.

**수정안**: 워크시트 §3.2에 «정본-측 참고» 소절로 위 3좌표(+ command-dddjango s007의 §5.5 dispatch 사본군)를 추가 기재해 소급 패스 안전망을 이중화. spec은 무변(같은 문서 쌍 아님).

## 전수 검사에서 반박 불성립(클린) 확인 사항

- **경계·kind**: 44절·180블록 행 범위를 스크립트로 기계 재검(연속·비중첩·절 스팬 정확 커버) + 원문 실독 대조 — 코드 펜스 26건 전건 «여는 펜스~닫는 펜스+후행 구분자» 정합, 표 머리행·구분행 행 단위 table-row 28건 정합, `---` 별도 prose 14건·공백 소유(선행 후행 귀속·절 선두 예외 44/44) 일관. 명사구 불릿 14건 kind=norm·norms 0은 파일럿 ninja s022-6.1 b2~b14 실물과 동형임을 확인. code 운반체 규범 3건(s006-2.1·s035-7.5·s069-17.4)은 규범이 펜스에만 존재함을 원문으로 확인. 과대 병합·prose 뭉갬 0건.
- **규범 식별(계수)**: 발주서 44행 전건 대사 — 일치 39절 재검 통과, 불일치 5절(s001·s018-4.5·s021-5.1·s040-9.1·s058-12.1)의 강등은 정본 문면 대조로 전건 정당(축자/준축자 사본 확인, 라운드 1 F1·F2 반영 후 상태). s025-5.5의 57 재구성 경로(418행 5문·442행 5문·459행 4문 등)와 s006-2.1의 11 경로를 문장 단위로 재현 — 일치. s015-4.2 뒷절 승격의 유일성 근거(«장애로 실패»·«수정됐다» 전문 1회 출현)를 grep으로 재확인. 합계 156→150(−6) 재현.
- **배선**: 27종 docstring 선두 전수 실독 — discipline-tdd·§5.5·입장 심사를 담당으로 지목한 검사기 0(«TDD» 출현은 check-composition-root.py의 왜-서술 1건뿐 — 집행 아님). 근접 3종의 담당(check-test-config: pytest 바인딩·`test/` 트리·settings 환경축 / check-mechanism-ownership: migration «파일» 배치 4규칙 / check-composition-root: DI 배선 위치)을 실물로 확인 — 오배선 회피 판정 타당, enforcedBy 0은 도피가 아니라 실독 판정. delegatedTo 150 전건(기본값 148 + T4 1 + T5 병기 1) 기계 집계 일치, T4·T5 기본값 이탈의 문면 근거(418행 «Coordinator 게이트 명칭»·448행 설계 반송) 원문 실물 성립. basis 허위·공란 0.
- **재진술**: spec restates 9건 전건 same-doc·대상 블록 좌표 실물 정확(b2·b12·b17·b35·s036-7.6/b1), 정본 측(s036-7.6) 미기재로 §15 준수, 유예 대상의 spec 혼입 0. 발주서 재진술 열 Y 전건 처리(같은 문서 8 + 열 N인 s012-3.4 직접 확인 추가 + 교차 s025-5.5↔skill/s004 유예 #1). kind·class·블록 수 분포(norm 103·table-row 28·code 26·prose 23 / O97·P29·Perm14·Ov6·Ex4) 워크시트 주장과 기계 집계 일치.
- **도구 검증**: `ontology_migrate.py` 검증 전용 exit 0 재현(--write 미사용) — Work 신규 150·재사용 0.

## 종합

라운드 1의 medium 2건이 정확히 반영됐고 저작 품질은 전반적으로 높다. 잔여 지적은 medium 1(N1 — 자기 명문화 기준의 비대칭 적용으로 생긴 same-doc restates 대상 누락)과 low 4다. N1 반영 시 Work·계수·byte 등가는 모두 불변이며 restates 배열 1곳만 갈린다.

## 처분 (수리자 기록 · 2026-08-22)

원문 `dddjango/skills/discipline-tdd/references/final.md` 해당 행 대조 + 상대 문서 실물 확인으로 5건을 개별 판정했다. **fixed 4 · rejected 1**. 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/discipline-tdd-final.spec.json` → **exit 0**(`--write` 미사용 · 절 44 · 블록 180 · Work 신규 150 · 재사용 0 — 라운드 2 재현값과 동일).

| # | 처분 | 근거 (한 줄) |
|---|---|---|
| N1 | **fixed** | 244행 첫 문장이 398행 심사 행의 3열(protected contract/evidence·unique production failure·existing authoritative coverage)을 이름 그대로 압축한 재서술임을 원문 대조로 확인 — s069-17.4/b1 Admission 행과 동형이라 §4 기준 ⑵의 비대칭 적용이 맞다. `s015-4.2/b2` restates에 `s025-5.5/b2` 병기 + note를 문장별 사유로 분리. Work 4=4·계수·byte 등가 불변 |
| N2 | **rejected** | 4행 전반절 «요구·버그·피라미드·예제는 먼저 candidate일 뿐»과 #37 «…는 **이 행을 건너뛸 독립 근거가 아니다**»는 낱말 집합만 겹치고 실행위가 다르다 — 전반절에는 «심사 행»·«우회» 어휘도, 금지 실행위도 없다. 지위 선언은 같은 블록에 Work로 남은 전역 Override가 이미 지고 있어 b2 병기는 §4 기준 «문장 단위 되풀이»를 취지 겹침으로 헐겁게 만든다. 지적이 제시한 갈음안대로 워크시트 §3.1 #1 근거란에 기각 사유를 명문화 |
| N3 | **fixed** | 이 문서의 «…때만/…만 + 결과» 한정 문형이 결과절이 의무형이어도 Exception이라는 형제 관례가 성립(#75 «관련 테스트**만** 다음처럼 조정한다» — 결과 의무형인데 Exception · #65 · #116). 문형이 다른 «…**만으로** …하지 않는다»는 Prohibition(#62·#81·#83)으로 이미 갈려 있어 형태 기준이 선명하다. #60 → Exception. 부수 이득: Obligation 독법이면 #60이 b16 #50의 특례 반복이 되어 same-doc restates 후보가 되는데, 한정 독법은 #59 범위 한정이라 고유 실행위가 선다. 판정 기준은 워크시트 §4에 명문화 |
| N4 | **fixed** | 40행 두 분기의 문면이 «그것을 **입력하라**»(명령형) ↔ «…**돌아오자**»(청유형)로 대칭인데 초판이 #8만 Permission으로 갈랐다. 이 문서 Permission 용례는 전건 권고·허용 문형(§6.2 504행 «사용하면 좋다»·§6.3 508행 «그렇게 하는 것이 좋다»·decision 자격 허용)이라 명령형은 비원소다. #8 → Obligation(조건부 의무). §6 초록 막대 전략 맥락은 §6 문면이지 §2.1 40행의 문면이 아니라 반영 |
| N5 | **fixed** | 좌표 3건을 실물 대조로 전건 확인 — `agent-discipline-reviewer` s005/b6(spec L54–55 = 현재 파일 L58–59 첫-Green 비계 ≈ 444행)·s007/b4(spec L68 = 현재 파일 L75, 문면이 «근거 `discipline-tdd` §5.5»를 명시 인용 ≈ 459행)·`design-architect.md` 83행(«`pending`은 리뷰 뒤 0개여야 G1 … `reuse`·`reject`는 write 0» ≈ 418행 b17). 상대 워크시트 §3 R4가 상대를 `agent-coder`·`command-dddjango`로만 지목해 다리가 양쪽 모두에서 빠진 것도 실측 확인. 1차 책임이 사본 측이라는 지적의 유보도 옳으므로 **spec 무변**, 워크시트 §3.2에 «3.2.1 정본-측 참고» 소절(C1~C4)로 좌표만 기재해 소급 패스 안전망 이중화 |

**부수 변경**: N3·N4로 class 분포가 O97·P29·Perm14·Ov6·Ex4 → **O97·P29·Perm13·Ov6·Ex5**(합계 150 불변, Obligation은 −1+1 상쇄)로 갈렸다 — 라운드 2 «클린» 절의 분포 대사값은 이 판부터 후자를 기준으로 읽어야 한다. 그 밖의 검사 결과(경계·kind·계수·배선·byte 등가)는 5건 처분 어느 것도 건드리지 않는다.
