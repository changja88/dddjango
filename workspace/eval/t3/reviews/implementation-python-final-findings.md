# T3 적대 리뷰 — implementation-python-final (2026-08-22)

- 대상: `workspace/eval/t3/specs/implementation-python-final.spec.json` + `workspace/eval/t3/worksheets/implementation-python-final.md`
- 대조: 발주서 · T3-authoring-brief · 원문 `dddjango/skills/implementation-python/references/final.md`(2675행 실측 일치) · `dddjango/scripts/check-*.py` 27종 로스터(실측 27) docstring 실독 · `ontology-authoring.md` §13~§16 · `ontology_migrate.py` 선두 docstring · 파일럿 spec 2건 + T3 동료 spec 전 파일 판형 대조 · `dddjango/skills/implementation-python/SKILL.md` · `dddjango/skills/discipline-houserules/SKILL.md`
- 기계 대조: 절 42·블록 114·Work 80(O65·Pr6·E6·P3·Override 0)·무소유 0·basis 공란 0 재계수 일치, `ontology_migrate.py` 검증 전용 exit 0 재현(센서스 좌표·절 해시·연속/비중첩/전량 커버 단언 통과).
- 배선 실물 대조 결과(반박 불성립 — 기록): ①`check-context-isolation.py` docstring «#453/#454 "없다"는 답» 실재 — s032-4.4 배선 정당. ②`check-choices-literal-consumption.py` 표제 «cleancode §2.14 소비 규율»·«보지 않는 것: 닫힌 집합의 미승격·비교식» 축자 실재 — s061-10.1 의 배선 1건/비배선 3건 분리 정당. ③`check-domain-model.py` #8 «밖으로 나가는 import 0 — …서드파티» 실재 — W44(pydantic 고정 금지) 정당. ④`check-public-surface-annotation.py` #493 문장 축자 실재 — W80 배선 정당. ⑤비배선 근거 4건(check-naming 무 PEP8 대소문자 축 · check-business-vocabulary #585 framework 한정 · check-context-isolation #166~#168 OHS 한정 · check-test-config 무 mypy/ruff 관할) 전부 docstring 실독으로 지지됨. ⑥kind=code 에 norms 부착·enforcedBy+delegatedTo 병기·표 단위 병합은 T3 동료 spec 다수 판형과 일치(병기 417건·code+norms 20건+ 실측). ⑦재진술 유예 14+1건의 SKILL.md 좌표·인용 문면 전건 실물 일치. ⑧worksheet §1 census 대사 42절 전건을 발주서와 재대조 — 일치(s112 차 1 사유 포함 타당).

## 발견 (심각도순)

### F1 — medium · 재진술 · s129-26.1 (2490행, b6 — W80)

**주장**: W80 «타입 어노테이션 상시 유지»의 원문 괄호 절은 `houserules «모든 이름 첫 대입에 타입»`을 **직접 인용**한 교차 문서 사본이고, 상대 정본 문면이 `dddjango/skills/discipline-houserules/SKILL.md` 51행(«**모든 이름은 "첫 대입"에 타입을 적는다 — 예외 0.**» — doc_key `discipline-houserules-skill`, 센서스 등재 확인)에 실재하는데, worksheet «재진술 유예» 절(15건)에 미등재다. spec 자신의 basis ①이 «문면이 houserules …을 직접 인용»이라 자인하므로 사본 관계는 저작자 스스로 증언한 상태다. 발주서 재진술 열이 N 이지만, 같은 «소유 지정+요지 재진술» 구조인 s061-10.1↔cleancode §2.14 는 발주서가 Y 로 걸어 유예 #5 에 올라갔다 — 센서스 열의 비대칭(발주서 s129 비고도 «houserules 소유 지목»이라고 관계를 인지)이며, 브리프 worksheet 양식 3의 census 열은 «참고»지 한정 열거가 아니다. 이대로면 T3 소급 패스가 이 쌍을 놓친다.

**수정안**: worksheet §3 에 16번째 유예 행 추가 — «s129-26.1/b6 W80 → discipline-houserules-skill/(타입 어노테이션 절, SKILL.md 51행) — 축자 인용(«모든 이름 첫 대입에 타입»); 발주서 열 N 은 census 과소 후보로 병기». spec 은 무변(교차 문서라 restates 미기재가 옳다).

### F2 — low · 경계kind · s111-19.6 (2142–2152 b1 · 2155–2162 b3)

**주장**: 두 표를 각각 머리행·구분행·데이터 행 전부 + 앞뒤 빈 줄까지 묶은 **표 전체 1 table-row 블록**(스팬 11·8행)으로 병합했다. 브리프 kind 정의는 «table-row(머리행·구분행 포함 **행 단위**)»이고 §13 도 «표 머리행·구분행**도** kind=table-row»(행 단위 블록을 전제한 문면)이며, 파일럿 판형(ddd s051-8, api s013-3.1 등)은 행마다 1블록(머리행 norms 0)이다. worksheet §4-④가 «표 단위 1 규범(P0 방침)»을 근거로 들지만 그것은 **계수 축**의 방침이지 블록 분해 축의 방침이 아니다 — 행 단위로 쪼개도 규범은 1건만 채번해 대표 행에 부착하면 계수는 불변이다. 다만 표 단위 병합이 T3 동료 spec 3건(implementation-django s067-14.1·implementation-test s004-1.1/s008-2/s034-7.1)에도 있어 관례가 갈라져 있고, norm 부착 자리의 자연성(표 한 벌=한 규범)이라는 옹호도 성립해 low.

**수정안**: 행 단위 블록으로 재분해(norm 은 첫 데이터 행 부착) 또는 — 병합 유지 시 — 소급 정합을 위해 «표 단위 table-row 병합» 관례를 브리프/§13 쪽에 명문화하는 결정을 T3 총괄에 회부(spec 4파일 공통 쟁점).

### F3 — low · 규범식별 · s092-16.1 (1798행, b3)

**주장**: 1798행 불릿 후단 «Free-threaded 빌드(3.13+)에서는 스레드도 가능»은 조건부 허용 서술인데 b3 의 Work 는 «CPU 병렬화의 multiprocessing·C 확장 기본» 1건(Obligation)뿐이라 Permission 1건 미채번 후보다. 발주서 계수 2 와는 일치하므로 spec 의 승계는 규율대로이나, 렌즈 ②의 «문면이 허용을 서술하는데 norms 에 없음»에 형식상 걸린다. 반론: 이 절은 s094-16.3 의사결정 #2(Free-threading 반영)가 같은 축을 별도 소유하고, 해당 구는 그 요지의 절내 압축이라 사실 서술로 볼 여지도 있어 low.

**수정안**: 소급 개정 시 b3 에 Permission Work(«Free-threaded 빌드의 스레드 CPU 병렬화 허용») 추가를 census 과소 후보로 회부하거나, worksheet §4-⑥ 제외 목록에 이 구를 명시해 판정을 기록으로 남긴다.

### F4 — low · 재진술 · s118-22.1 ↔ SKILL s004 30행 전단

**주장**: worksheet 유예 #12·#13 이 SKILL 30행 후단(«mypy/pyright strict …»)을 s121·s122 의 상대로 올리면서, **같은 불릿의 전단** «Ruff로 린트·포맷 통합 (§22–§23)»이 s118-22.1(ruff pyproject 설정 규범)의 요약 상대라는 사실은 미등재다. 발주서 s118 재진술 열이 N 이라 열 대조 기준으로는 위반이 아니나, s072-12.0(요약 1:N — 유예 #6)과 같은 구조이고 저작자가 그 불릿을 두 번 직접 인용하고도 전단을 흘렸다.

**수정안**: worksheet §3 에 유예 후보 행 추가(«s118-22.1/b1 → implementation-python-skill/s004 30행 전단 — 요약 1:N · 발주서 열 N 은 census 과소 후보») — F1 과 같은 소급 패스 재료.

### F5 — low · 배선 · s072-12.0 (1436행, b2 — W45)

**주장**: W45 «durable domain invariant 의 규칙 소유 경계 배치»의 basis 가 check-domain-model.py 를 «배치 축 결정적 백스톱»이라 하나 과대다. 그 docstring(#8·#249~#315)은 domain_layer **안**의 자리·격리·불변식 형태(#264·#268)를 물 뿐, 이 규범의 대표 실패 양태 — durable invariant 가 pydantic validator·adapter 등 **domain 밖 자리**에 눌러앉는 것 — 를 잡는 진단이 없고, 문면이 나열한 «application service» 자리는 관할 밖이다. 결정적으로 커버되는 것은 domain 쪽 절반뿐. 병기 reviewer 가 있고 basis 말미가 판정 한계를 자인하므로 low.

**수정안**: basis 를 «domain_layer 안의 자리·격리 축 한정 결정 백스톱(#8·#249~#315) — invariant 의 domain 밖 안착(validator 대행 등)은 검사 공백 · reviewer 몫»으로 정정(배선 자체는 유지 가능).

### F6 — low · 배선 · s004-1.2 (54행, b4 — W4)

**주장**: W4 basis 의 «check-test-config 는 pytest↔settings 바인딩 **한정**»은 부정확 — 실물 docstring 관할은 3슬라이스(⑴pytest↔settings 바인딩 ⑵`test/` 구조 #383~#392 ⑶`<project>/settings/` 환경축 #445~#447)다. 결론(mypy·ruff·pyright 설정 파일을 무는 검사기 부재 → 기본값 위임)은 유효하므로 배선 판단 무변. worksheet 2-2-4 도 동일 문구를 반복한다.

**수정안**: basis·worksheet 문구를 «check-test-config 관할은 pytest 바인딩·test/ 구조·settings 환경축 — `[tool.mypy]`·`[tool.ruff]`·pyrightconfig.json 비관할»로 정정.

### F7 — low · 재진술 · s111-19.6 (2159행, b3) ↔ s049-8.5 (971행, b2)

**주장**: 밑줄 관례 표의 `__var` 행(«네임 맹글링. 하위 클래스 충돌 방지 전용»)은 같은 문서 s049-8.5/b2 Work(«__var 는 하위 클래스 필드명 충돌 방지 한정», Exception)와 같은 규범의 문서 내 중복인데 spec `restates` 미연결·worksheet 미기록이다. 반론: b3 블록은 표 한 벌 준수라는 자체 Work 를 지고 해당 행은 그 부분집합이라 §15 «사본 블록»(정본 1곳 Work + 사본 restates) 꼴이 아니며, 발주서 열도 N — 확신 낮아 low.

**수정안**: worksheet §4-⑤에 기각 판정으로라도 기록(s040-6.2 기각례와 동형의 근거 남김) 또는 b3 에 restates 병기 여부를 소급 패스 쟁점으로 회부.

## 종합

- high 0 · medium 1 · low 6. 경계·kind(전량 원문 대조)·규범 계수(발주서 42절 전건 대사)·배선 실물(27종 docstring 실독 재검증)은 큰 틀에서 견고하다 — 성립한 반박의 중심은 재진술 소급 재료의 누락(F1·F4)과 basis 문구 정밀도(F5·F6)다.
- spec·worksheet 는 수정하지 않았다(리뷰 계약).

## 처분 (수리자 · 2026-08-22)

수리 범위는 자기 spec + worksheet 2파일뿐(브리프 «금지» 준수). 원문 md·`ontology/`·동료 spec 은 손대지 않았다. 재검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/implementation-python-final.spec.json` → **exit 0**(`--write` 미사용 · 42절·블록 114·Work 80 재계수 무변).

**반영 5 · 기각 2.**

| # | 처분 | 근거 한 줄 | 변경 파일 |
|---|---|---|---|
| F1 | **fixed** | 원문 2490행 괄호가 houserules SKILL.md 51행 «모든 이름은 «첫 대입»에 타입을 적는다 — 예외 0.»을 축자 인용함을 실물 대조로 확인(houserules `references/final.md` 에는 이 문장 없음 — 정본이 SKILL 쪽임도 확인) → worksheet §3 에 16번 유예 행 추가(`discipline-houserules-skill`/s007-4 · 발주서 열 `N` 은 census 과소 후보 병기). spec 은 지적대로 무변 — 교차 문서라 `restates` 미기재가 옳다. | worksheet |
| F2 | **rejected** | «행 단위 1블록이 의무»의 전제가 성립하지 않는다 — `ontology-authoring.md` 131행이 블록 경계의 자연 단위로 «문단·불릿·펜스·**표 행 묶음**»을 명문 열거한다. §13 128행의 «머리행·구분행도 kind=table-row»는 **kind 귀속** 규정이지 1행=1블록 명령이 아니다. 표 분해 축은 무변으로 두고, 관례 갈림(파일럿 행 단위 ↔ T3 동료 3건 표 단위)의 명문화만 §4-④에 T3 총괄 회부로 적시했다. | worksheet(기각 근거 추기) |
| F3 | **fixed**(기록 한정 — Work 미추가) | 1798행 후단 «Free-threaded 빌드(3.13+)에서는 스레드도 가능»은 주어가 «빌드의 능력»인 가능성 진술이라 1797행의 용처 지정(Permission 채번)과 층이 다르고, 채택 축은 `s094-16.3` 의사결정 #2 가 소유한다 → 발주서 계수 2 승계 유지, 대신 worksheet §4-⑥에 **제외 판정 4근거 + census 과소 후보 병기**를 명시해 소급 판단 재료로 남겼다. | worksheet |
| F4 | **fixed** | SKILL s004 30행 전단 «Ruff로 린트·포맷 통합 (§22–§23)» 실재 확인 — 후단을 유예 #12·#13 으로 올린 것과 대칭이 맞도록 worksheet §3 에 s118-22.1 행 추가(요약 1:N · census 과소 후보 병기). 절 순 유지를 위해 구 #12·#13·#14 → 신 #13·#14·#15 재번호. | worksheet |
| F5 | **fixed** | `check-domain-model.py` docstring 실독 결과 관할 50규칙은 전부 domain_layer **안**의 자리·격리·형태(#8·#249~#315)이고, invariant 가 pydantic validator·adapter·application service 에 안착하는 양태를 잡는 진단이 없음을 확인 → basis 를 «domain_layer 안의 자리·격리 축 한정 결정 백스톱 — domain 밖 안착은 검사 공백·reviewer 몫»으로 정정(배선 무변). | spec + worksheet |
| F6 | **fixed** | `check-test-config.py` docstring 이 관할을 «세 슬라이스»로 자기 선언(⑴pytest↔settings 바인딩 ⑵`test/` 구조 #383~#392 ⑶`<project>/settings/` 환경축 #445~#447) — «pytest 바인딩 한정»은 과소 기술이 맞다 → spec basis·worksheet 표 4행·§2-2-4 문구를 3슬라이스 열거로 정정. 비배선 결론(`[tool.mypy]`·`[tool.ruff]`·`pyrightconfig.json` 비관할)은 무변. | spec + worksheet |
| F7 | **rejected**(기각 판정은 기록) | 2159행 ↔ 971행이 같은 규범임은 확인했으나 `restates` 를 걸지 않는다 — `ontology_migrate.py` 의 `restates` 는 대상 IRI 가 `…/b<order>` 인 **블록 대 블록** 술어인데 b3 은 5행 관례 한 벌을 지는 블록이고 중복은 한 행뿐이라, 블록 전체를 사본으로 선언하면 나머지 4행까지 사본이라 주장하는 과대 진술이 된다(§15 사본 장치는 통째 사본용). 지적의 대안대로 **§4-⑤에 기각 판정과 근거를 기록**하고, 행 단위 재진술 표현력은 소급 패스 쟁점으로 회부했다. | worksheet(기각 근거 추기) |

---

# T3 적대 리뷰 — 라운드 2 (수리 반영본 재검 · 2026-08-22)

- 대상: F1~F7 처분 반영 후의 spec + worksheet(유예 17건 판·§2-2 3슬라이스 정정판).
- 재검 방식: 4렌즈 **전수 절** 재검사(표본 아님) — 42절 헤딩·스팬 좌표 전건 원문 실측(다음 헤딩-1 일치 42/42) · 블록 경계·kind 전건 원문 대조(빈 줄 귀속 §13 방향 일관 확인) · 발주서 42절 규범 수 ↔ spec Work 재대사(81↔80, 차 1 = s112 재진술 — 무변 타당) · `ontology_migrate.py` 검증 전용 재실행 **exit 0**(절 42·블록 114·Work 80 재계수 일치) · 배선 basis 인용 전건을 4검사기 docstring에서 축자 재대조(«#453/#454 "없다"는 답»·«보지 않는 것: 미승격·비교식»·«#8 …서드파티»·«#493 첫 대입» 전부 실재) · 도피 의심 후보로 27종 로스터 docstring 전수 재실독(usecase-dto-placement·response-schema-bypass·error-centralization·ninja-boundary-middleware·synthetic-infra-exc·naming·test-config·business-vocabulary 정독 포함) · `implementation-python/SKILL.md`·`discipline-houserules/SKILL.md` 좌표 실측.
- 라운드 1 처분의 실물 검증: F1(유예 #16 — houserules SKILL 51행 축자 실재·references/final.md grep 0 재현) ✓ · F3(§4-⑥ 제외 판정 4근거 수록) ✓ · F4(유예 #12 추가·재번호) ✓ · F5(basis «domain_layer 안 한정» 강등 문구 반영) ✓ · F6(3슬라이스 열거 정정 — docstring 문면과 일치) ✓ · F2/F7 기각 근거의 §4-④/⑤ 기록 ✓. `agent-design-review-ddd` 위임은 migrate 도구 AGENTS 8종 로스터에 실재 — 유효.

## 라운드 2 발견 (심각도순)

### R2-1 — medium · 재진술 · s032-4.4 ↔ SKILL s004 27행 후단 (유예 누락)

**주장**: worksheet 유예 #8 이 SKILL 27행 «예외는 도메인 최상위 클래스 정의 후 계층화; **None 반환 대신 예외 발생** (§15)»을 통째로 인용하면서 상대를 `s089-15.2` 하나에만 걸었다. 후단 «None 반환 대신 예외 발생»은 §15 어디에도 없는 문구이고(원문 grep — 유일 등장 = 622행 §4.4 헤딩) s032-4.4 헤딩의 **축자 사본**이다. 세미콜론으로 갈린 같은 불릿의 앞/뒤 절반을 각각 올리는 것이 이 worksheet 자신의 확립 관행(#13·#14 — 30행 전·후단, #3·#4 — 24행 앞·뒤)이며, «금지가 헤딩에 사는 절»도 유예 대상으로 올린 선례(#7 — s081-13.5)가 있다. §3 서두가 자기 선언한 기준(«열이 N 이어도 실물 대조로 사본 관계가 성립하면 유예로 올린다»)에 정면으로 걸리는 누락 — 이대로면 소급 패스가 이 쌍을 놓친다. SKILL 쪽 앵커 «(§15)»가 §4.4 를 빠뜨린 오앵커라는 사실도 소급 시 함께 볼 재료다.

**수정안**: worksheet §3 에 유예 행 추가 — «`s032-4.4`(헤딩+코드 운반) → `implementation-python-skill`/s004 27행 **후단** — 헤딩 축자 사본 · #8 과 같은 불릿의 반분 · SKILL 앵커 (§15)는 오앵커(§4.4 누락) 병기». spec 은 무변(교차 문서·§15 유예 계약).

### R2-2 — medium · 재진술 · s005-1.3 ↔ SKILL s004 21행 (유예 누락)

**주장**: SKILL 21행 «Union/Literal/NewType으로 상태 공간을 좁혀 잘못된 상태를 타입 레벨에서 차단 **(§1.3–§1.4)**»은 s005-1.3 의 유일 Work(W5 «합 타입으로 비정상 상태 배제» — 58행 «합 타입(Sum Type)을 사용해 비정상 상태를 배제하라»)의 요약 재진술이고 앵커가 §1.3 을 명시 지목하는데, 유예 표 16행 어디에도 21행이 없다. 요약 수준 쌍(#6 — s072↔29행, #9 — s092↔28행)을 올린 자기 기준과 비대칭이다. §3 서두의 «핵심 운영 원칙 18–31행 요약 11불릿»을 확인했다는 진술과 달리 21행 불릿만 무배정으로 남았다(§1.4 몫은 REF 범위 밖이라 s005 절반만 올리면 된다).

**수정안**: worksheet §3 에 유예 행 추가 — «`s005-1.3`/b1 → `implementation-python-skill`/s004 21행 — 요약 재진술(합 타입=Union) · 발주서 열 N 은 census 과소 후보 병기».

### R2-3 — low · 재진술 · s063-10.3 ↔ SKILL s004 23행 전단 (유예 후보 미기록)

**주장**: SKILL 23행 «dataclass(**slots**, frozen, kw_only)로 불변 값 객체를 표현 … (§10)»의 slots 언급은 s063-10.3 의사결정 #7(slots=True 권장)과 겹친다. 다만 불릿이 §10.4·10.5·10.8(REF 범위 밖)까지 묶는 총론이고 «권장» 규범의 재진술이라기보다 기능 열거에 가까워 사본 관계 확신이 낮다 — low. 소급 패스가 판단할 수 있게 후보로라도 기록해 두는 편이 §3 서두 기준과 정합한다.

**수정안**: §3 에 후보 행(또는 §4 메모) 추가 — 채택/기각 판정 포함.

### R2-4 — low · 재진술 · s116-21 W2 ↔ SKILL s003 14행 (유예 후보 미기록)

**주장**: 유예 #11 이 s116-21 W1(architecture-ddd 소유)↔s003 15행만 올리고, 같은 문단의 W2(«Django ORM 환경 적용의 implementation-django(§16) 담당»)와 s003 14행(«Django 모델·ORM·서비스·트랜잭션·설정 구현 → `implementation-django`»)의 대응은 미기록이다. 두 문면의 위임 대상은 같으나 서술 축이 달라(구조 패턴의 Django 적용 vs Django 구현 전반) 사본 판정 확신이 낮다 — low.

**수정안**: §3 후보 행 또는 §4-⑤ 기각 기록(어느 쪽이든 판정을 남긴다).

### R2-5 — low · 재진술 · s061-10.1 b8 (1213행) 절내 재참조 판정 미기록

**주장**: 1213행 선두 «위의 "지역적 분기 표현이면 `Literal` 가능"은 **유지하되**»는 같은 절 b5(1210행) Permission 의 절내 재확인 구다. F7 과 동형인 «블록 부분집합 중복»이라 `restates` 미연결 자체는 옳으나(블록 대 블록 술어 — 과대 진술 회피), F7·s040-6.2 는 §4-⑤에 채택/기각 판정을 기록한 반면 이 쌍은 기록이 없다. 소급 패스의 행 단위 표현력 쟁점 목록에 빠진다 — low.

**수정안**: §4-⑤에 기각 판정 1행 추가(F7 동형 근거 원용).

### R2-6 — low · 배선 · s072-12.0 W46·W48 — check-usecase-dto-placement 인접 축 비배선 근거 미기록

**주장**: §2-2 «배선하지 않은 근거» 4건에 s072 군이 없다. `check-usecase-dto-placement.py` docstring 은 #139(제약 선언은 schema_in — 컨트롤러 Field·validator 위반)·#142(요청 스키마는 도메인 객체를 만들지 않는다)·#202/#207(DTO 에 애그리거트·엔티티·ORM 행 금지)로 W46(validator 의 도메인 규칙 소유 금지)·W48(중복 domain model 금지)의 **인접 축**을 진다 — 27종 중 가장 «닮은 검사기»인데 비배선 판단 기록이 없다. 비배선 결론 자체는 타당하다(술어 불일치: #142 는 «스키마 안 도메인 객체 생성»을, W46 은 «validator 의 규칙 대행»을 문다 — 금액 계산을 원시 연산으로 대행하는 validator 는 #142 비발화). W44/W45 를 부분 커버 공개로 배선한 것과의 비대칭을 소급 검토가 물을 수 있으므로 근거를 남겨야 한다 — low.

**수정안**: §2-2 에 5번째 항 추가 — «s072-12.0 W46·W48 → check-usecase-dto-placement 비배선: #139/#142/#202·#207 은 스키마·DTO 자리의 술어이고 validator 의 규칙 대행·모델 중복 자체를 무는 진단이 없다».

### R2-7 — low · 규범식별 · s004-1.2 53행 후단 «X | None 을 사용할 수 있다» 판정 미기록

**주장**: 53행을 «사실 서술(P0 계수 비산입)»로 제외했는데, 후단 «Python 3.10+에서는 `X | None`을 사용할 수 있다»는 F3(1798행 «스레드도 가능»)과 같은 «가능» 꼴이라 조건부 Permission 독해 여지가 있다. F3 는 §4-⑥에 제외 판정 4근거+census 과소 후보 병기로 남겼으나 이 구는 전단(동등성 사실)만 언급되고 후단 판정이 없다. SKILL 20행이 «Optional→X | None»을 **지시**하는 강도 불일치(P0 특이3·유예 #2)와 얽힌 자리라 소급 개정 판단 재료가 된다 — 발주서 계수 2 와 일치하므로 low.

**수정안**: §4-⑥ 제외 목록의 s004-1.2 53행 항에 «후단 "사용할 수 있다"는 문법 가용성 진술로 판정(P0 특이3 개정 후보와 연동)» 명시.

## 라운드 2 종합

- high 0 · **medium 2** · low 5. 전부 worksheet(유예·판정 기록) 층의 지적 — spec 의 절 좌표·블록 경계·kind·계수·class·배선은 라운드 2 전수 재검에서 반박 불성립(기계 검증 exit 0 재현 포함). medium 2건은 라운드 1 이 세운 «열 N 이어도 실물 성립 시 유예 등재» 기준을 worksheet 자신이 두 자리에서 어긴 것이다.
- spec·worksheet 는 수정하지 않았다(리뷰 계약).

## 처분 — 라운드 2 (수리자 · 2026-08-22)

수리 범위는 자기 worksheet 1파일(브리프 «금지» 준수 — 원문 md·`ontology/`·동료 spec 미접촉). **spec 은 이번 라운드에서 무변** — 7건 전부 worksheet 층 지적이고, spec 변경을 요구한 지적이 없다. 재검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/implementation-python-final.spec.json` → **exit 0**(`--write` 미사용 · 42절·블록 114·Work 80 재계수 무변).

**반영 7 · 기각 0** — 단, R2-3 은 «판정을 기록하라»는 지적을 이행하되 **판정 내용은 사본 관계 기각**이다(지적이 요구한 산출물은 판정 기록이므로 처분은 fixed, 쌍 자체는 유예 미등재).

| # | 처분 | 근거 한 줄 | 변경 파일 |
|---|---|---|---|
| R2-1 | **fixed** | 원문 grep 결과 «None 반환 대신 예외 발생»의 유일 등장이 622행 §4.4 헤딩이고 §15(1716–1791행)에는 이 문구가 없음을 실측 확인 — SKILL 27행 후단은 §4.4 헤딩의 축자 사본이고 앵커 «(§15)»는 §4.4 를 빠뜨린 오앵커다 → worksheet §3 에 유예 행 추가(신 #4), 기존 s089 행(신 #10)은 «전단» 한정으로 정정하고 상호 참조를 걸었다. | worksheet |
| R2-2 | **fixed** | SKILL 21행 «Union/Literal/NewType으로 상태 공간을 좁혀 잘못된 상태를 타입 레벨에서 차단 (§1.3–§1.4)» ↔ 원문 58행 «합 타입(Sum Type)을 사용해 비정상 상태를 배제하라» 실물 대조 — 앵커가 §1.3 을 명시 지목하는 요약 재진술이고, s003 위임 4불릿·s004 요약 11불릿 중 21행만 무배정이던 비대칭이 사실로 확인됨 → 유예 행 추가(신 #3 · census 과소 후보 병기). §1.4(NewType) 몫은 REF 범위 밖이라 s005 절반만 대응한다고 명기. | worksheet |
| R2-3 | **fixed**(지적 이행 — 판정은 **사본 기각**) | SKILL 23행 주술이 «dataclass(…)로 **불변 값 객체를 표현**»이라 정본은 frozen 축(§10.4·REF 밖)이고 `slots` 는 괄호 안 옵션 열거인 반면, s063-10.3 규범은 «메모리 최적화 목적의 `slots=True` 권장»이라 **술어가 다르다**. 앵커 «(§10)»도 장 지목이라 상대 절이 특정되지 않는다 → 유예에 올리지 않고 **§3-1 «후보 판정 기록» 절을 신설해 기각 근거 3항 + 재검 조건**을 남겼다(지적의 «채택/기각 판정 기록» 요구 충족). | worksheet |
| R2-4 | **fixed**(판정은 **채택**) | 원문 §21 한 문장이 두 위임을 지는데(architecture-ddd §5·§6 / implementation-django **§16 서비스 레이어**) SKILL s003 14행이 «Django 모델·ORM·**서비스**·트랜잭션·설정 구현 → implementation-django» — 지목 대상·서비스 축이 겹치고, s003 위임 4불릿(13·14·15·16행) 중 14행만 무배정이던 자리다 → 유예 행 추가(신 #14). 다만 SKILL 은 Django 구현 전반이고 W2 는 구조 패턴의 Django 적용이라 **상대 쪽이 넓은 1:N 요약**임을 비고에 병기해 소급 패스가 축 차이를 보게 했다. | worksheet |
| R2-5 | **fixed**(기각 판정을 기록) | 1213행 선두가 b5(1210행) Permission 의 절내 재확인임은 확인했으나 `restates` 는 걸지 않는다 — b8 은 자기 Work 3건을 지는 블록이고 재확인은 선두 종속절 하나뿐이라 블록 대 블록 술어로 걸면 나머지 3 Work 까지 사본이라 주장하는 과대 진술이 되며(F7 동형), 이 구는 인용이 아니라 «유지하되 … 로 가른다»는 **유효 범위 조정**이라 §15 사본 꼴이 아니다 → §4-⑤에 기각 판정 1행 추가하고 F7 과 함께 행 단위 표현력 쟁점으로 회부. | worksheet |
| R2-6 | **fixed** | `check-usecase-dto-placement.py` docstring 실독 — #139 는 제약 선언의 **자리**, #142 는 스키마의 **도메인 객체 생성**, #202/#207 은 DTO 의 도메인 타입 **운반**을 물고, 세 규칙 모두 `application_layer/`·`driving_layer/api/**/schema/` **경로 한정**이다. W46(validator 의 규칙 대행)·W48(pydantic 으로 도메인 모델 재건)과 술어·방향·적용 자리가 모두 어긋남을 확인 → §2-2 에 5번째 항 추가(4건→5건), W44·W45 부분 커버 배선과의 비대칭 사유(그쪽은 «domain_layer 안 pydantic 고정»이 #8 서드파티 import 0 과 정확히 포개짐)도 함께 기록. 비배선 결론 무변. | worksheet |
| R2-7 | **fixed**(기록 한정 — Work 미추가) | 53행 후단 «Python 3.10+에서는 `X \| None`을 사용할 수 있다»는 주어가 **문법 가용성**이라 F3(1798행 «빌드의 능력»)과 같은 층이고, 1797행식 용처 지정이 없으며 이 절의 채번 2건은 지시 동사 문장(b1·b4)이다 → 발주서 계수 2 승계 유지, §4-⑥ 제외 목록의 s004-1.2 항을 전단/후단으로 갈라 **후단 제외 판정 3근거 + P0 특이3(SKILL 20행 «Optional→X \| None» 지시) 개정 후보 연동**을 명시했다. | worksheet |

**라운드 2 반영 후 상태**: 유예 **20건**(문서 상대 19 + 비문서 1 · 절 순 전건 재번호) · §3-1 후보 판정 1건(기각) · §2-2 비배선 근거 5건 · §4-⑤ 재진술 판정 4건(채택 1·기각 3) · §4-⑥ 제외 판정에 명시 항 2건.
