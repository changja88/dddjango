# T3 저작 검수표 — implementation-python-skill

- 원문: `dddjango/skills/implementation-python/SKILL.md (68행)` · spec: `workspace/eval/t3/specs/implementation-python-skill.spec.json`
- 자기 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/implementation-python-skill.spec.json` → **exit 0** (블록 4·5·11·32 = 52 · Work 22 · exit 0 · `--write` 미사용)
- 필독 이행: 발주서 · authoring.md §13~§16 · `ontology_migrate.py` 선두 docstring · 파일럿 spec 2건 · `dddjango/scripts/check-*.py` **27종 docstring 선두 전수 실독**(묶음 «py-test-skills» 3문서 공통 1회)

## 1. census 대사

| 절 | 헤딩 | 발주서(센서스) 규범 수 | spec 규범 수 | 블록 수 | 판정 |
|---|---|---|---|---|---|
| s001 | (전문) — frontmatter | 2 | 2 | 4 | 일치 |
| s003 | 언제 쓰나 | 5 | 5 | 5 | 일치 |
| s004 | 핵심 운영 원칙 | 11 | **13** | 11 | **불일치 — 센서스 과소** |
| s005 | 상세 레퍼런스 | 2 | 2 | 32 | 일치 |
| **계** | — | **20** | **22** | **52** | **불일치 절 1(s004)** |

계수 규약(묶음 «py-test-skills» 3문서 공통 · implementation-test-skill 검수표 §1 과 **같은 기준 문장**):
기본은 **문장 해상도**(§13 «Work 채번 단위가 문장»)이고, 여기에 **한 문장이 서로 다른 deontic class 의 절을
병렬로 질 때만 분할**한다 — djr 의 Work class 가 단일값이라 한 Work 로는 두 힘을 담을 수 없기 때문이다.
같은 문장 안이라도 **같은 class 의 병렬 절**은 나누지 않는다.
- **s004 불일치 사유(센서스 과소 — class 단일값 규약)**: 11불릿 중 2건이 의무절+금지절 병렬이라 분할했다.
  25행(Obligation «제너레이터로 지연 평가» + Prohibition «send/throw 금지») ·
  29행(Obligation «pydantic v2는 경계(입력 검증) 전용» + Prohibition «도메인 진리값으로 사용 금지»).
  11 + 2 = 13 → **내 산정 13 이 옳고 센서스 11 이 과소**다. 근거 3중:
  ⑴ 묶음 자매 문서 implementation-test-skill 이 동형 문장(25행 «도구는 mocker 픽스처; raw unittest.mock 폴백 금지» ·
  32행 · 34행)을 같은 기준으로 분할해 31 + 3 = 34 를 냈다 — «같은 한 축의 앞·뒷면»이라는 이전 판(1 Work)의 논거는
  test-skill 25행(mock 도구 선택의 앞·뒷면)에도 그대로 성립하므로 두 문서를 가르는 기준이 될 수 없다.
  ⑵ 정본 implementation-python-final 이 같은 내용을 2 Work 로 채번한 실물이 있다 —
  s072-12.0 b1 Obligation «pydantic v2 의 외부 입력·런타임 검증 경계 사용» + b2 첫 Work Prohibition
  «도메인 모델 기본 표현의 pydantic 고정 금지». 1 Work 압축은 정본 대비 class 압축 표류였다(→ §3 b10 행).
  ⑶ 같은 정본 spec 이 한 블록 안에서도 class 가 다르면 Work 를 나눈다(s072-12.0 b5 Obligation+Prohibition ·
  b6 Obligation+Exception) — 분할 기준이 코퍼스 관례임을 확인.
- 나머지 9불릿은 «1불릿 = 1문장 = 1규범»이라 분할이 발생하지 않았다(같은 class 의 병렬 절: 20·23·24·27·28·30행).
- s005 의 표 29행(머리행·구분행 포함 31행)은 주제→§ 라우팅이라 규범 0(센서스 «비규범» 판정 채택).

## 2. 배선 근거 표 (전 규범)

| # | 절·블록 | class | Work label | enforcedBy | delegatedTo | 4원 근거(① 문면 역할명 ② docstring § 인용 ③ P0 커버 ④ registry·기본값) |
|---|---|---|---|---|---|---|
| 1 | s001/b2 | Obligation | Python 관용구·타입·Protocol/ABC·경계 도구 코드 작업 시 우선 로드 | — | agent-discipline-reviewer | ①문면 — 프론트매터 description 은 스킬 라우터 트리거(«…먼저 로드한다») · ②check-*.py 27종 docstring 선두 전수 실독 — 스킬 로드 라우팅을 집행하는 검사기 0 · ④§16 위임 기본값 표(implementation-* → agent-discipline-reviewer) |
| 2 | s001/b2 | Obligation | 경계 밖 주제의 discipline-cleancode·implementation-django·architecture-ddd·implementation-test 위임 | — | agent-discipline-reviewer · agent-design-review-ddd | ①문면이 위임 상대 4종을 직접 지정 · ④§16 기본값(discipline-*·implementation-* → discipline-reviewer) + architecture-ddd 행은 명시 문면 우선(파일럿 L-F 중재 판례 · implementation-python-final s116-21 b1 «구조 패턴 선택 기준의 architecture-ddd 소유»→design-review-ddd 동일 배선) |
| 3 | s003/b1 | Obligation | Python 특화 구현 결정이 주 작업일 때 로드 | — | agent-discipline-reviewer | ①문면 «…주 작업일 때 로드한다» · ②check-*.py 27종 docstring 선두 전수 실독 — 스킬 로드 조건 판정 술어 0 · ④§16 기본값(implementation-*) |
| 4 | s003/b2 | Obligation | 기술무관 클린코드 원칙의 discipline-cleancode 위임 | — | agent-discipline-reviewer | ①문면 위임 화살표 «→ discipline-cleancode» · ④§16 기본값 표 — discipline-cleancode 문서군의 기본 Agent 도 discipline-reviewer(rule-owner-map ⓓ) |
| 5 | s003/b3 | Obligation | Django 모델·ORM·서비스·트랜잭션·설정 구현의 implementation-django 위임 | — | agent-discipline-reviewer | ①문면 «→ implementation-django» · ②check-*.py 27종 docstring 선두 전수 실독 — 스킬 간 관할 이관을 집행하는 검사기 0 · ④§16 기본값(implementation-*) |
| 6 | s003/b4 | Obligation | repository/UoW/핵사고날/CQRS/outbox 구조 패턴 선택의 architecture-ddd 위임 | — | agent-design-review-ddd | ①문면이 architecture-ddd 를 직접 지정 — 명시 문면이 기본값에 우선(파일럿 L-F 중재) · ④§16 기본값 표 architecture-ddd 설계 시점 행 → agent-design-review-ddd · implementation-python-final s116-21 b1 동일 배선 선례 |
| 7 | s003/b5 | Obligation | 테스트 코드 작성의 implementation-test 위임 | — | agent-discipline-reviewer | ①문면 «→ implementation-test» · ④§16 기본값(implementation-*) · implementation-python-final s124-24 b1 «테스트·디버깅의 implementation-test 위임» 동일 배선 |
| 8 | s004/b1 | Obligation | 타입 어노테이션의 전 코드베이스 일관 적용(Optional→X \| None·PEP 695 우선) | check-public-surface-annotation.py | agent-discipline-reviewer | ②check-public-surface-annotation.py docstring 선두 «타입 전면 검사기 — «첫 대입에 타입» 규율의 결정적 백스톱»·#493 — «전 코드베이스 일관 적용» 축을 결정적으로 집행 · ③Optional→X \| None·PEP 695 표기 축은 비커버(의미 레인) · ④§16 기본값 병기 · implementation-python-final s129-26.1 b6 동일 배선 선례 |
| 9 | s004/b2 | Obligation | Union/Literal/NewType 으로 상태 공간 축소(잘못된 상태의 타입 레벨 차단) | — | agent-discipline-reviewer | ②check-*.py 27종 docstring 선두 전수 실독 — 타입 표현 선택 술어 0 · ④§16 기본값 · implementation-python-final s005-1.3 b1 «합 타입으로 비정상 상태 배제» 동축 |
| 10 | s004/b3 | Obligation | Protocol 구조적 서브타이핑 기본·ABC 는 런타임 등록 한정 | — | agent-discipline-reviewer | ②check-*.py 27종 docstring 선두 전수 실독 — Protocol/ABC 선택 술어 0 · ④§16 기본값 · ③센서스 P0 특이2 역전 — final §9 본문에 대응 규범 없음(스킬 고유 규범) |
| 11 | s004/b4 | Obligation | dataclass(slots·frozen·kw_only) 의 불변 값 객체 표현·NamedTuple 의 불변 레코드 표현 | — | agent-discipline-reviewer | ②check-*.py 27종 docstring 선두 전수 실독 — dataclass 옵션 선택 술어 0 · ④§16 기본값 · implementation-python-final s063-10.3 b1 «dataclass(slots=True) 권장» 동축 · ③check-domain-model.py **#264 «값 객체 불변 — \_\_init\_\_/\_\_post\_init\_\_ 밖 self 대입 금지»는 VO 불변 «행위» 집행 축(인접)**이라 본 Work 의 «표현 수단 선택»(dataclass 옵션·NamedTuple) 축은 비커버 — §16 «기본값 도피» 역심사 기록 |
| 12 | s004/b5 | Obligation | 디스크립터·@property 의 검증·지연 계산 한정 사용(단순 필드는 평범한 애트리뷰트) | — | agent-discipline-reviewer | ②check-*.py 27종 docstring 선두 전수 실독 — 애트리뷰트 접근 형태 술어 0 · ④§16 기본값 · implementation-python-final s042-7.1 b1 «평범한 공개 애트리뷰트 시작·필요 시 @property 전환» 동축 |
| 13 | s004/b6 | Obligation | 제너레이터를 통한 지연 평가 사용 | — | agent-discipline-reviewer | ①문면 «제너레이터로 지연 평가» · ②check-*.py 27종 docstring 선두 전수 실독 — 제너레이터 프로토콜 술어 0 · ③센서스 P0 특이2 역전 — §13.2(지연 평가) 축은 final 본문 무규범(스킬 고유 규범) · ④§16 기본값(implementation-*) |
| 14 | s004/b6 | Prohibition | 제너레이터 send·throw 사용 금지 | — | agent-discipline-reviewer | ①문면 «send/throw 금지» — 앞 절과 deontic class 가 달라 별도 Work(묶음 공통 분할 기준) · ②check-*.py 27종 docstring 선두 전수 실독 — 제너레이터 프로토콜 술어 0 · ③implementation-python-final s081-13.5 b1 «send·throw 대신 이터레이터 입력 또는 상태 클래스 사용»(Obligation) 의 금지면 동축 · ④§16 기본값(implementation-*) |
| 15 | s004/b7 | Obligation | 커스텀 컨텍스트 매니저로 리소스 해제를 with 문에 명시 | — | agent-discipline-reviewer | ②check-*.py 27종 docstring 선두 전수 실독 — 컨텍스트 매니저 술어 0 · ④§16 기본값 · ③센서스 P0 특이2 역전 — final §14 본문에 대응 규범 없음(스킬 고유 규범) |
| 16 | s004/b8 | Obligation | 도메인 최상위 예외 클래스 정의 후 계층화와 None 반환 대신 예외 발생 | — | agent-discipline-reviewer | ②check-*.py 27종 docstring 선두 전수 실독 — 예외 계층 설계 술어 0(check-synthetic-infra-exc 는 driven 층 인프라 예외 합성 축) · ④§16 기본값 · implementation-python-final s089-15.2 b1 동축 |
| 17 | s004/b9 | Obligation | I/O 병목의 asyncio.TaskGroup(3.11+)·CPU 병목의 멀티프로세싱 선택 | — | agent-discipline-reviewer | ②check-*.py 27종 docstring 선두 전수 실독 — 동시성 수단 선택 술어 0 · ④§16 기본값 · implementation-python-final s092-16.1 b3·s093-16.2 b1 동축 |
| 18 | s004/b10 | Obligation | pydantic v2 의 경계(입력 검증) 전용 사용 | — | agent-discipline-reviewer | ①문면 «pydantic v2는 경계(입력 검증) 전용» · ②check-*.py 27종 docstring 선두 전수 실독 — «경계 전용» 사용 범위 판정 술어 0(check-domain-model 은 도메인 층 import 경계 축) · ③implementation-python-final s072-12.0 b1 «pydantic v2 의 외부 입력·런타임 검증 경계 사용»(Obligation) 동일 — 정본 2 Work 구성 복원 · ④§16 기본값(implementation-*) |
| 19 | s004/b10 | Prohibition | pydantic v2 의 도메인 진리값 사용 금지 | check-domain-model.py | agent-discipline-reviewer | ①문면 «도메인 진리값으로 사용 금지» — 앞 절과 deontic class 가 달라 별도 Work(묶음 공통 분할 기준) · ②check-domain-model.py docstring «#8 [ast] domain_layer 의 밖으로 나가는 import 0 — django·다른 층·다른 BC·서드파티» — 도메인 층의 pydantic(서드파티) 반입을 결정적으로 차단 · ③implementation-python-final s072-12.0 b2 «도메인 모델 기본 표현의 pydantic 고정 금지»(Prohibition)가 같은 규범을 check-domain-model.py 로 배선한 선례 · ④§16 기본값 병기 |
| 20 | s004/b11 | Obligation | Ruff 린트·포맷 통합과 mypy/pyright strict 모드 적용 | — | agent-discipline-reviewer | ②check-*.py 27종 docstring 선두 전수 실독 — ruff·mypy 설정을 집행하는 검사기 0(check-test-config 는 pytest↔Django settings 바인딩 축) · ④§16 기본값 · implementation-python-final s118-22.1·s121-23.1·s122-23.2 동축 |
| 21 | s005/b1 | Obligation | 주제별 references/final.md 해당 절 준수 | — | agent-discipline-reviewer | ①문면 «…해당 절을 따른다» — 상세 규범의 정본 위치 지정 · ②check-*.py 27종 docstring 선두 전수 실독 — 문서 라우팅 술어 0 · ④§16 기본값(implementation-*) |
| 22 | s005/b32 | Obligation | 필요한 항목만 부분 로드(전체 로드 불필요) | — | agent-discipline-reviewer | ①문면 «필요한 항목만 읽는다(전체 로드 불필요)» · ②check-*.py 27종 docstring 선두 전수 실독 — 로드 범위 술어 0 · ④§16 기본값(implementation-*) |

## 3. 재진술 유예

센서스 restate 열 기준. **문서 내 쌍은 spec `restates` 에 실렸고**(아래 ①), 교차 문서 쌍만 여기 유예한다.
좌표는 전부 **마커 제거본(센서스) 기준** — 상대 문서 `implementation-python-final` 은 웨이브 2 기이관이라 현재 파일에
`<!-- graph-owned … -->` 마커가 삽입돼 있으나, 아래 좌표는 마커 없는 센서스 좌표계의 절 키·블록 서수다.

① 문서 내(= spec 수록, 유예 아님)
| 사본 블록 | 정본 블록 | 근거 |
|---|---|---|
| s001/b2 (frontmatter description) | s003/b1 · s003/b2 · s003/b3 · s003/b4 · s003/b5 | description 은 «언제 쓰나»의 로드 조건 1 + 경계 위임 4 를 한 줄로 압축한 라우터 사본. 정본 = 완전 진술인 s003 |

② 교차 문서(유예 — 전 웨이브 완료 후 소급 패스가 연결)
| 사본 블록 | 상대 문서/절(센서스 좌표) | 대조 결과 |
|---|---|---|
| s004/b1 (§1) | implementation-python-final / s129-26.1 b6 «타입 어노테이션 상시 유지» · s004-1.2 b1 | 요약 사본 — 배선도 동일(check-public-surface-annotation.py) |
| s004/b2 (§1.3–§1.4) | implementation-python-final / s005-1.3 b1 «합 타입으로 비정상 상태 배제» | 요약 사본 |
| s004/b3 (§9) | — (상대 없음) | final §9 Protocol 절에 규범 0 — 센서스 «P0 특이2 역전» 실측 확인. 스킬 고유 규범이라 유예 불요 |
| s004/b4 (§10) | implementation-python-final / s061-10.1 b2~b8 · s063-10.3 b1 | 요약 사본(dataclass slots·Enum 승격) |
| s004/b5 (§6–§7) | implementation-python-final / s039-6.1 b1 · s040-6.2 b1 · s042-7.1 b1 | 요약 사본 |
| s004/b6 (§13.2, §13.5) | implementation-python-final / s081-13.5 b1 «send·throw 대신 …» | §13.5 만 상대 있음. §13.2(지연 평가)는 final 무규범 — 부분 사본. 본 spec 은 이 블록을 Obligation(지연 평가)+Prohibition(send·throw 금지) **2 Work** 로 채번했고, 상대는 뒤 Work 에만 대응 |
| s004/b7 (§14) | — (상대 없음) | final §14 with문 절에 규범 0(센서스 P0 특이2 역전) — 스킬 고유 규범 |
| s004/b8 (§15) | implementation-python-final / s089-15.2 b1 | 요약 사본 |
| s004/b9 (§16) | implementation-python-final / s092-16.1 b3 · s093-16.2 b1 | 요약 사본 |
| s004/b10 (§12.0) | implementation-python-final / s072-12.0 b1(Obligation «경계 사용») · b2 첫 Work(Prohibition «pydantic 고정 금지») | 요약 사본 — 배선도 동일(check-domain-model.py). **class 압축 표류 교정 기록**: 초판은 정본 2 Work 를 스킬 1 Work(Prohibition)로 압축해 Obligation 면을 잃었다. 본 판에서 class 별 2 Work 로 분할해 정본 구성을 복원했으므로 **잔여 표류 없음**(대조 결과는 «요약 사본») |
| s004/b11 (§22–§23) | implementation-python-final / s118-22.1 b1 · s121-23.1 b1 · s122-23.2 b1 | 요약 사본 |

s005 는 센서스 restate=N — 표는 라우팅 정보라 사본 관계 없음. 확인 결과 유예 대상 0.

## 4. 경계 판단 메모

- **frontmatter 의 kind**: 웨이브 2 판례대로 `code` 가 아니라 **행 단위 prose/norm**. 절 스팬 소유 분해(§13)에서
  s001 의 헤딩 라인은 여는 `---`(1행)이 되고, 블록은 2행부터 시작한다(도구 규약 `line_start+1`). 따라서
  b1=`name:`(prose) · b2=`description:`(norm 2) · b3=`user-invocable: false`(prose) · b4=닫는 `---`+빈 줄(prose).
- **`user-invocable: false` 는 규범인가**: 아니다 — 플랫폼 노출 설정 선언이고, 센서스 비고도 이를 «codex 판 부재»라는
  플랫폼 표기 차이로만 다룬다(규범 수 2 = description 2문장). prose 로 판정.
- **닫는 `---` 와 빈 줄**: 블록 간 구분자는 선행 블록 후행 귀속(§13)이라 6행(빈 줄)은 b4 에 붙였다.
- **절 선두 빈 줄**: s003/s004/s005 의 첫 블록은 각각 10·19·33 행에서 시작해 헤딩 직후 빈 줄을 첫 블록 선두에 귀속(§13 유일 예외).
- **표 블록 분해**: 머리행+구분행을 한 블록(b2 = 36–37행)으로 묶고 데이터 행은 1행 1블록.
  **파일럿과 다른 판형이다** — 파일럿 `spec-architecture-ddd-final.json` s051-8 실물은 [2059,2060]=절 선두 빈 줄+머리행,
  **[2061,2061]=구분행 단독 블록**으로 병합하지 않았다(초판의 «파일럿 판형을 그대로 따랐다» 기술은 오기 — 실물 대조로 정정).
  병합 근거는 §13 «표 행 묶음»의 자연 단위이고, 묶음 «py-test-skills» 3문서(36–37 · 44–45 · 37–38행)에 동일 적용해
  판형 내부 일관성을 유지했다. 마지막 데이터 행(66행)이 후행 빈 줄 67행을 흡수한다.
- **마지막 문장 블록**: 68행 «각 절은 … 필요한 항목만 읽는다»는 표와 분리된 별도 norm 블록.
