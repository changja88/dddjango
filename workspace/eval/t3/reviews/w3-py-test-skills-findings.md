# T3 적대 리뷰 — 묶음 «py-test-skills» (spec + worksheet)

- 대상: `implementation-python-skill` · `implementation-test-skill` · `discipline-tdd-skill` 의 spec 3건 + worksheet 3건
- 리뷰 방법: 4렌즈 전수 — 3문서 12절 전 블록(52·52·37)을 원문 SKILL.md 3건(68·68·53행 — 발주서 행수와 일치, 마커 0)과 기계+육안 대조. migrate 도구 dry-run 재현 3건 모두 exit 0 · Work 계수 20/46/26 = 발주서 스코프와 일치. kind↔내용 기계 대조(표 행 혼입·빈 norm·norm/prose 내 표 행) 0건. 검사기 27종 docstring 선두 전수 재실독 + 배선·비커버 근거에 인용된 7종(check-public-surface-annotation·check-domain-model·check-test-config·check-synthetic-infra-exc·check-idempotency-scope-creep·check-api-error-controller-contract·check-openapi-error-declaration)은 docstring 본문까지 재확인. 선례로 인용된 final spec 좌표(implementation-python-final 18절·implementation-test-final 29절·discipline-tdd-final 20절) 실물 대조 — 인용 절 키 전부 실재, 인용 배선(s129-26.1 b6→public-surface-annotation · s072-12.0 b2→domain-model · s021-4.1 b1→test-config · s049-9.1 b3 위치 Work→test-config · s025-5.5 b17 pending→command-dddjango) 전부 성립.
- 기계 확인 결과(참고): 무소유 norm 0 · basis 공란 0 · restates 대상 블록 실재 100% · 절 선두/후행 공백 귀속 §13 정합 · frontmatter 행 단위 분해(웨이브 2 판례) 정합. norms+restates 병존은 final spec 전반(39블록)에도 있는 수용 관례로 확인 — 지적하지 않음.

## 발견 (심각도순)

### F1 · medium · 재진술 · implementation-test-skill / s004
- **주장**: s004/b1(20행 — «먼저 `discipline-tdd` §5.5의 decision row를 확인한다 … 피라미드…add의 근거가 아니다»)과 s003/b1(11행 — «이 skill은 `discipline-tdd` §5.5가 … mechanics만 제공한다 …»)은 **같은 문서 안 재진술 쌍**인데 spec `restates` 미연결이다. worksheet §3 스스로 «축자 3중 사본 — final 머리말·본 스킬 s003·본 스킬 s004 b1 이 같은 §5.5 입장 게이트 문면»이라고 판정해 놓고, 두 블록의 교차 문서 관계(→ implementation-test-final s001 b1)만 유예 기록하고 문서 내 2본 사이는 잇지 않았다. 브리프 «같은 문서 안 쌍만 spec restates에 넣는다» 위반이고, 같은 spec이 s001/b2↔s003(문서 내 압축 사본)은 restates 로 처리한 자기 기준과도 비일관하다.
- **수정안**: s004/b1 에 `restates: ["implementation-test-skill/s003/b1"]` 추가(완전 진술·선행인 s003/b1 을 문서 내 정본으로) — 4번째 문장(피라미드 근거 부정)은 s003 에 없는 부분 중첩임을 worksheet §3 에 병기. 잇지 않는 선택을 유지하려면 «문서 내 2본 모두 외부 정본(final s001)의 사본이라 상호 연결을 소급 패스로 미룬다»는 근거를 worksheet 에 명시할 것.

### F2 · medium · 재진술 · discipline-tdd-skill / s003
- **주장**: worksheet §3 유예 표의 s003/b3·b4 상대 좌표가 실물과 다르다. ① b3(14행 «테스트 코드 품질 … → discipline-cleancode»)의 상대로 적은 `s061-14`는 final «14. Property-Based Testing → **implementation-test** 참조» 스텁이다(위임 상대도 주제도 불일치). ② b4(15행 «Django TestClient·API 테스트 메커니즘 → implementation-django»)의 상대로 적은 `s060-13`은 «13. 레거시 코드 다루기 → **discipline-cleancode**» 스텁이다. discipline-tdd-final 전문을 검색해도 implementation-django 를 지목하는 위임 스텁은 0건(§13~§15·§18 스텁의 위임 상대는 cleancode 1·implementation-test 3)이라 b4 는 상대 자체가 없다. 이대로면 소급 연결 패스가 허위 쌍 2건을 잇는다. 발주서 비고(«위임 4건이 final 위임 스텁(§8·§13~§15·§18)과 중복»)의 과대 서술을 «직접 확인 후» 의무 없이 승계한 형태다.
- **수정안**: b3 행은 «상대 없음(주제 일치 스텁 부재 — s060-13 은 레거시 주제로 cleancode 위임 대상만 동일)»로, b4 행은 «상대 없음(final 에 implementation-django 위임 스텁 부재)»로 정정. 발주서 비고와의 차이를 사유 한 줄로 남길 것.

### F3 · medium · 규범식별 · implementation-python-skill / s004
- **주장**: 혼합 deontic class 한 문장의 분할 기준이 묶음 안에서 비일관하고, 그 결과 class 정보가 유실된다. 같은 저작자가 implementation-test-skill 에서는 «한 문장 안 다른 deontic class 는 분할»(25·32·34행 → +3, 센서스 34 정합)을 기준으로 세웠는데, 본 문서 s004 b6(25행 «제너레이터로 지연 평가, send/throw **금지**» → Obligation 1)·b10(29행 «pydantic v2는 경계 전용, 도메인 진리값 사용 **금지**» → Prohibition 1)은 동형(의무절+금지절 병렬)임에도 1 Work 로 뒀다(센서스 11 승계). worksheet 의 구분 논거(«같은 한 축의 앞·뒷면»)는 test-skill 25행(mocker 사용/raw mock 금지 — 역시 한 축의 앞·뒷면)을 분할한 것과 상충한다. 특히 b10 은 정본(implementation-python-final s072-12.0)이 같은 내용을 b1 Obligation(경계 사용)+b2 Prohibition(고정 금지) **2 Work** 로 채번한 실물이 있어, 스킬 사본의 2→1 압축이 class 압축 표류인데 worksheet §3 해당 행은 «요약 사본»으로만 적고 표류 기록이 없다(tdd-skill worksheet 가 b37 강도 상향을 표류로 명기한 자기 관례와도 비일관).
- **수정안**: 택일 — ⑴ b6·b10 을 class 별 2 Work 로 분할(11→13)하고 census 대사에 «센서스 과소 — class 단일값 규약» 사유 행 추가, ⑵ 1 Work 유지 시 worksheet §1 에 test-skill 분할 기준과의 차이 논거를 정면으로 적고 §3 b10 행에 «final 2 Work→1 Work class 압축» 표류를 명기. 어느 쪽이든 두 worksheet 의 기준 문장을 일치시킬 것.

### F4 · low · 경계kind · implementation-python-skill / s005
- **주장**: worksheet §4 «표 블록 분해: 머리행+구분행을 한 블록으로 묶고 … 파일럿 `spec-architecture-ddd-final.json` s051-8 판형을 **그대로 따랐다**»는 허위 근거다. 파일럿 실물은 [2059,2060]=절 선두 빈 줄+머리행, **[2061,2061]=구분행 단독 블록**으로, 머리행·구분행을 병합하지 않았다. 병합 자체는 §13 «표 행 묶음» 자연 단위 안이라 위반이 아니고 3문서 공통 판형(36–37·44–45·37–38행)이라 일관적이지만, 기록된 근거가 사실과 다르다(브리프의 «table-row … 행 단위» 문면과의 긴장도 이 허위 인용 때문에 심사 불능이 된다).
- **수정안**: worksheet 문구를 «파일럿과 달리 머리행+구분행을 병합(§13 표 행 묶음 근거) — 파일럿은 구분행 단독 블록»으로 정정. 판형 통일이 목표면 구분행 분리로 재분해(블록 서수 +1 전파 확인).

### F5 · low · 재진술 · implementation-test-skill / s004
- **주장**: s004/b18(37행 «migration 전용 … 식별·수명 주기는 기존 규칙을 그대로 따른다 (§1.4, discipline-tdd §5.5)»)은 같은 절 b3(22행 둘째 문장 «이 절은 기술적으로 식별만 하고 수명 주기는 discipline-tdd에 넘긴다»)의 문서 내 재서술 성격인데 worksheet 는 교차 문서 상대(final s007-1.4·tdd-final s025-5.5 b46·b47)만 기록하고 b3↔b18 관계를 심사하지 않았다. 준거 지시문이라 별개 규범으로 볼 여지도 있어 low.
- **수정안**: worksheet §3 에 b3↔b18 심사 결과 한 줄 추가(재진술 아니면 그 근거, 맞으면 restates 연결 여부 판정).

### F6 · low · 배선 · implementation-python-skill / s004
- **주장**: b4(«dataclass(slots·frozen·kw_only) 불변 값 객체 표현») 의 비커버 근거(«dataclass 옵션 선택 술어 0»)가 인접 실물인 `check-domain-model.py` **#264 «값 객체 불변 — __init__/__post_init__ 밖 self 대입 금지»** 를 다루지 않는다. 규범의 축(표현 수단 선택)과 #264 의 축(불변성 행위 집행)이 달라 위임 결론 자체는 final s063-10.3 b1 선례와 정합하게 유지 가능하나, «불변 값 객체» 문면의 절반이 결정 검사기로 부분 커버되는 사실을 basis·worksheet 가 기록해야 §16 «기본값 도피» 역심사가 완결된다.
- **수정안**: basis 또는 worksheet §2 해당 행에 «check-domain-model #264 는 VO 불변 행위 축(인접) — 본 Work 의 표현 선택 축은 비커버» 한 줄 추가.

## 판정

**반송(pass=false)** — spec 수정을 요하는 medium 1건(F1)과 소급 패스를 오염시키는 worksheet 좌표 오류(F2), class 정보 유실 계열(F3)이 남아 있다. 배선 실물 대조·계수 대사·경계 규약은 그 외 전건 성립: F1~F3 수리(또는 근거 명문화) 후 재제출이면 충분하고 재저작 사유는 없다.

## 처분 (수리자 · 2026-08-22)

각 지적을 **원문·정본·파일럿 실물 대조**로 하나씩 판정했다. 쓴 파일은 대상 spec 3건 + worksheet 3건뿐이고
원문 SKILL.md·`ontology/`·타 에이전트 산출물은 손대지 않았다(`--write` 미사용).

| # | 처분 | 근거 한 줄 |
|---|---|---|
| F1 | **fixed** | 원문 11행(s003/b1 4문장)과 20행(s004/b1 4문장) 대조 결과 1~3문장이 문서 내 재진술 쌍임을 확인 — `implementation-test-skill.spec.json` s004/b1 에 `restates: ["implementation-test-skill/s003/b1"]` 추가, 부분 중첩(4문장 «피라미드…add 근거 아님»은 s003 에 없음)과 «외부 정본 사본이어도 문서 내 쌍은 수록» 판단을 worksheet §3 ① 에 병기. |
| F2 | **fixed** | `discipline-tdd/references/final.md` 실물 확인 — 1037–1040행 §14 = «Property-Based Testing → `implementation-test`», 1030–1033행 §13 = «레거시 코드 다루기 → `discipline-cleancode`», 전문에 `implementation-django` 0건. worksheet §3 ② 의 s003/b3·b4 행을 **«상대 없음» + 오기 정정 사유**로 교체하고, 발주서 비고(«위임 4건이 스텁과 중복») 승계를 파기한 사유를 절 말미에 명문화. |
| F3 | **fixed (택일 ⑴ — class 별 분할)** | 동형 판정 성립 확인(test-skill 25행은 분할, python-skill 25·29행은 미분할). 정본 `implementation-python-final` s072-12.0 이 b1 Obligation «경계 사용» + b2 **첫 Work** Prohibition «pydantic 고정 금지»로 2 Work 이고, 같은 spec 이 한 블록 안에서도 class가 다르면 Work를 나눈다(b5 Obl+Pro · b6 Obl+Exc). ⇒ b6·b10 을 각각 2 Work 로 분할(s004 11→13 · 문서 계 20→22), census 대사에 «센서스 과소 — class 단일값 규약» 사유행 추가, 두 worksheet §1 기준 문장 일치. *지적 문면 중 «b2 Prohibition»은 엄밀히는 «b2 의 첫 Work 가 Prohibition»(b2 는 3 Work 블록) — 결론에는 영향 없어 그대로 반영.* |
| F4 | **fixed (문구 정정)** | 파일럿 `spec-architecture-ddd-final.json` s051-8 실물 = b1 [2059,2060](절 선두 빈 줄+머리행) · **b2 [2061,2061] 구분행 단독** — 병합하지 않았음을 확인(현재 파일 2094–2098행 = 마커 삽입 전 2058–2061). worksheet §4 를 «파일럿과 다른 판형 — 병합 근거는 §13 표 행 묶음, 묶음 3문서 공통 적용»으로 정정. 재분해는 하지 않았다(병합 자체가 §13 안이고 3문서 판형 일관성을 깨뜨릴 뿐이므로 — 허위 근거만 교정). |
| F5 | **fixed (심사 결과 = 재진술 · 연결)** | b18(37행)은 b3(22행)의 대상 2종·준거 §1.4 를 그대로 쓰고 «기존 규칙을 그대로 따른다»로 압축 재지시할 뿐 새 규범 내용이 없으며, 인용된 §1.4 는 이 스킬 안에서 곧 b3 다 ⇒ 재진술로 판정해 s004/b18 에 `restates: ["implementation-test-skill/s004/b3"]` 추가하고 심사 근거를 worksheet §3 ① 에 기록(Work class·채번은 원문대로 유지). |
| F6 | **fixed** | `check-domain-model.py` docstring #264 «값 객체 불변 — `__init__`/`__post_init__` 밖 self 대입 금지» 실재 확인(파일 22행·집행부 386–396행). s004/b4 의 `basis` 와 worksheet §2 11행에 «#264 는 VO 불변 *행위* 집행 축(인접) — 본 Work 의 *표현 수단 선택* 축은 비커버» 한 줄 추가. 위임 결론은 final s063-10.3 b1 선례대로 유지. |

**계**: fixed 6 · rejected 0(전건 원문 대조로 성립 — 반영하지 않을 허위 지적 없음).

**제출 검증**(검증 전용 · `--write` 미사용):

```
PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/implementation-python-skill.spec.json  → exit 0 (블록 52 · Work 22)
PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/implementation-test-skill.spec.json    → exit 0 (블록 52 · Work 46)
PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/discipline-tdd-skill.spec.json         → exit 0 (블록 37 · Work 26)
```

Work 계수 변경은 implementation-python-skill 20→22 뿐이다(F3). ISSUED 에 3문서 경로의 기존 채번이 0건이라
재사용 정합 위반 없이 재채번되며, 도구는 센서스의 `line_start`/`line_end`/`sha256` 만 단언하므로 규범 수 변경은 검증에 영향이 없다.
