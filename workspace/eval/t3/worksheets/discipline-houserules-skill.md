# T3 이관 검수표 — discipline-houserules-skill

- 원문: `dddjango/skills/discipline-houserules/SKILL.md` (83행 · 센서스 일치 · 드리프트 경고 없음 · `graph-owned` 마커 0건 — 좌표 환산 불요)
- spec: `workspace/eval/t3/specs/discipline-houserules-skill.spec.json`
- 규모: REF 10절 · 블록 39 · Work 75(발주서 규범 75 — **전건 일치**)
- 자기 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/discipline-houserules-skill.spec.json` → **exit 0**(검증 전용 · `--write` 미사용)

## 1. census 대사 (발주서 규범 수 ↔ spec Work 수)

| section_key | 헤딩 | 발주서 | spec | 대사 |
|---|---|---|---|---|
| `s001` | (전문) — frontmatter | 4 | 4 | 일치 |
| `s003` | 무엇이고 왜 | 7 | 7 | 일치 |
| `s004-1` | §1 파일트리 결정 순서 | 28 | 28 | 일치 |
| `s005-2` | §2 충돌 중재 | 3 | 3 | 일치 |
| `s006-3` | §3 구조 결정이 빠졌다는 신호 | 7 | 7 | 일치 |
| `s007-4` | §4 타입 어노테이션 | 9 | 9 | 일치 |
| `s008-4.1` | §4.1 왜 전부인가 | 2 | 2 | 일치 |
| `s009-5` | §5 코드 주석·docstring 언어 | 4 | 4 | 일치 |
| `s011-6.1` | §6.1 부트스트랩·표준 도구셋 | 1 | 1 | 일치 |
| `s012-6.2` | §6.2 새 런타임 의존성의 버전 선택 | 10 | 10 | 일치 |
| **합계** | — | **75** | **75** | **차 0** |

불일치 절 없음. 계수가 갈릴 수 있는 절의 **문장 단위 분해 실물**(마침표 단위 · P0 승계):

- `s001` **4** — 발주서 note 의 «[adv 중재 정정 2026-08-19] norm 6→4 — 동상(로드 1+반드시 사용 1+단일 출처 1+위임 1)» 을 그대로 승계했다. `description` 한 줄 안 4문장이고, `name:`·`user-invocable:`·`---` 는 플랫폼 표기라 prose 다(웨이브 2 `agent-coder`/s001 판례).
- `s003` **7** = 13행 **3**(① 값=final.md·절차=SKILL.md 소유 분리 ② 값 복제 금지 ③ 무접두 `#N` 본문 정본=저장소 정본 명세·배포본에는 발췌만) + 17~20행 경계 불릿 **4**. 11행(«집안 규칙이다» 서술)은 prose 로 뺐다.
- `s004-1` **28** = 24행 **1**(«아래를 따른다») + 26행 **13** + 27행 **3** + 28행 **2** + 30행 **5** + 32행 **4**. 26행 13문장 실물: ① 소스 트리는 언제나 표준·기존 레이아웃 비입력 ② final.md §0·§1 을 읽고 그대로 실현 ③ 요약 대신 문서 ④ dddart 등으로 오인 금지 ⑤ 기존 배치는 «확립 규약» 아님(=안 갚은 빚) ⑥ 「일관 사용」 관찰은 반례 아님 ⑦ 집행 스코프 판정 물음 ⑧ 스코프 안→형태는 표준 ⑨ 스코프 밖→불이동·불수정 ⑩ 이동 권한은 G0 ⓐ→슬라이스 0 한 경로 ⑪ 기존 줄 전파·답습 금지 ⑫ 존치 legacy=동결된 빚 ⑬ 백스톱 `check-layer-skeleton`·#487 선행. 30행 5문장: TARGET=저장소 루트 / BC 폴더 TARGET 은 exit 1 / 게이트 증거=판정 차분 / 좁힌 selector green 은 증거 아님 / 스코프 밖 귀속의 1차 처방=철회. 32행 4문장: 닫힌 목록 6축 / 목록 밖은 비입력 / 배선 값 조건부지만 원칙은 무조건 / 신규 산출물 형태 문장(이동 권한 아님).
- `s006-3` **7** = 40행 lead-in **1**(«판정은 final.md 와 검사기가 한다») + 42~47행 신호 **6**. 센서스 note «신호 6개=진단 조건문으로 계수» 와 정합.
- `s007-4` **9** = 51행 **3** + 53행 **1**(«문법이 없는 자리뿐») + 55~57행 **3**(문법 부재 자리 3묶음 — P0 승계) + 59행 **2**.
- `s008-4.1` **2** — 63행 5문장 중 앞 3문장(노동·선택·결정성)은 **이유 서술**이라 제외하고, «주류와 다른 선택임을 숨기지 않는다»·«mypy strict 밖은 백스톱과 감수자가 집행» 2건만 보수 포함(센서스 note 와 동일 판정).
- `s011-6.1` **1** — 73행은 지시 3개(직접 다룸 / 기존 도구 감지·존중 / 부재 시 §2.1 규율 셋업·글로벌 설치 금지)를 한 마침표에 압축했다. **마침표 단위 1** 로 계수한 P0 판정을 승계했다 — 지시 단위로 쪼개면 3이 되지만 그러면 s004-1 의 다지시 문장(예 30행 T3)도 같이 쪼개져야 해 문서 내 계수 축이 어긋난다.
- `s012-6.2` **10** = 77행 **1** + 79행 **3** + 81행 **2** + 82행 **3** + 83행 **1**. 80행(«**왜**: 기억 기반 버전은 …»)은 **이유 서술 전용 불릿**이라 규범 0 → `prose` 블록이다. 이 절에서 유일하게 kind 가 norm 이 아닌 본문 불릿이다.

## 2. 배선 근거 표 (전 75 규범)

| 절 | 블록 | Work label | class | enforcedBy / delegatedTo | 4원 근거 |
|---|---|---|---|---|---|
| `s001` | b2 | 배치·타입 부착·주석 언어를 정하거나 검수할 때 로드 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거1 |
| `s001` | b2 | 신규 모듈·BC·테스트·프로젝트 레이아웃·코드 규약 결정 시 필수 사용 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거1 |
| `s001` | b2 | 트리와 규칙 «값»의 단일 출처는 references/final.md | Obligation | delegatedTo `agent-discipline-reviewer` | 근거1 |
| `s001` | b2 | 보편 클린코드·Python 타입 지식·테스트 타입 조직의 타 스킬 위임 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거2 |
| `s003` | b2 | 트리·칸·규칙 «값»은 final.md 단일 출처 소유 · SKILL.md 는 «언제 어떻게 읽나»만 소유 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s003` | b2 | 값을 SKILL.md 에 복제하지 않는다 | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s003` | b2 | 무접두 #N 규칙 «본문» 정본은 저장소 정본 명세 — 플러그인 문서에는 집행 발췌만 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s003` | b4 | 코드 내부 구조(네이밍·함수 크기·SOLID)의 discipline-cleancode 위임 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거2 |
| `s003` | b5 | DDD 계층·바운디드 컨텍스트 이론의 architecture-ddd 위임 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거2 |
| `s003` | b6 | Django 프로젝트 레이아웃 관용의 implementation-django 위임 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거2 |
| `s003` | b7 | 테스트 타입 조직·conftest 메커니즘의 implementation-test §4.2 위임 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거2 |
| `s004-1` | b1 | 새 코드·테스트 배치는 아래 결정 순서를 따른다 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004-1` | b2 | 소스 파일트리는 언제나 dddjango 표준 — 기존 레이아웃은 트리 결정의 입력이 아니다 | Obligation | enforcedBy `check-layer-skeleton.py` + delegatedTo `agent-discipline-reviewer` | 근거4 |
| `s004-1` | b2 | final.md §0 제1원칙과 §1 트리 140행을 읽고 그대로 실현 | Obligation | enforcedBy `check-layer-skeleton.py` + delegatedTo `agent-discipline-reviewer` | 근거4 |
| `s004-1` | b2 | 요약을 믿지 말고 문서를 읽는다 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004-1` | b2 | 이 트리는 dddjango 자신의 표준 — 타 플러그인 것으로 오인해 치우기 금지 | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004-1` | b2 | 기존 소스 배치를 «확립된 규약»으로 읽지 않는다 — 옛 층 이름·옛 위치는 아직 안 갚은 빚 | Prohibition | enforcedBy `check-layer-skeleton.py` + delegatedTo `agent-discipline-reviewer` | 근거4 |
| `s004-1` | b2 | 「모든 BC 가 일관 사용」류 관찰은 반례가 아니라 이 규칙이 태어난 사고 | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004-1` | b2 | 집행 스코프 판정 물음은 «승인 스코프에 근거가 있는가» — «내가 만들거나 수정하는가»가 아니다 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004-1` | b2 | 스코프 안 → 형태는 언제나 표준이고 기존 실물은 형태 결정의 입력이 아니다 | Obligation | enforcedBy `check-layer-skeleton.py` + delegatedTo `agent-discipline-reviewer` | 근거4 |
| `s004-1` | b2 | 스코프 밖 → 옮기지도 고치지도 않는다(정리·일관성·트리 밖 칸 위반·백스톱 red 어느 것도 이동 근거 아님) | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004-1` | b2 | 위반 판정은 빚 기록 권한 · 이동 권한은 G0 사용자 ⓐ 결정→슬라이스 0 한 경로에서만 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004-1` | b2 | 기존 파일 수정 시 표준은 추가·변경 줄의 형태만 — 기존 줄 전파·답습 금지 | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004-1` | b2 | 존치된 legacy 는 동결된 빚 — 신규 산출물의 형태 근거로 되읽기 금지 | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004-1` | b2 | 결정적 백스톱은 check-layer-skeleton 이고 다른 모든 검사보다 먼저 돈다(#487) | Obligation | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s004-1` | b3 | 승인된 test artifact 가 실제 있을 때만 의미군으로 조직 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004-1` | b3 | 승인 artifact 는 기존 프로젝트 테스트 위치나 표준 위치(트리 105~111행)에 둔다 | Obligation | enforcedBy `check-test-config.py` + delegatedTo `agent-discipline-reviewer` | 근거6 |
| `s004-1` | b3 | 구조 규칙 자체는 테스트를 만들거나 기존 테스트를 자동 이동하지 않는다 | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004-1` | b4 | 한 프로젝트 안에서 레이아웃 혼용 금지 | Prohibition | enforcedBy `check-layer-skeleton.py` + delegatedTo `agent-discipline-reviewer` | 근거4 |
| `s004-1` | b4 | 혼용 금지 규칙만으로 기존 테스트 이동 권한이 생기지 않는다 | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004-1` | b5 | 검사기의 TARGET 은 저장소 루트(application/ 의 부모) | Obligation | enforcedBy `check-layer-skeleton.py` + delegatedTo `agent-discipline-reviewer` | 근거4 |
| `s004-1` | b5 | BC 폴더·application/ 컨테이너 TARGET 은 사용 오류 exit 1 로 거절된다 | Obligation | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s004-1` | b5 | 게이트 증거는 판정 차분 — 앵커 대비 귀속 0 + legacy 잔존 별도 보고 · 귀속 red 의 «확립 규약» 수용 금지 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거7 |
| `s004-1` | b5 | 좁힌 TARGET·selector 로 얻은 green 은 게이트 증거가 아니다 | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거7 |
| `s004-1` | b5 | 승인 스코프 밖 파일의 귀속은 1차 처방이 그 변경의 철회 — 수리·재설계 금지 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004-1` | b6 | 관찰이 결정 입력인 축은 닫힌 목록 여섯 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004-1` | b6 | 목록 밖 축에서 기존 실물의 관찰은 결정의 입력이 아니다 | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004-1` | b6 | 배선 «값»은 Ninja 스택 조건부지만 ‹관찰 비입력› 원칙 자체는 무조건 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004-1` | b6 | ‹관찰 비입력›은 신규 산출물의 형태 문장 — 스코프 밖 실물의 이동·수정 권한을 만들지 않는다 | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s005-2` | b1 | 코퍼스가 서로 다른 트리를 제시해도 런타임에 택일하지 않는다 | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s005-2` | b1 | final.md 가 단일 출처이고 코퍼스는 파생 배경 — 남는 변수 없음 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s005-2` | b1 | 테스트 타입 조직은 implementation-test §4.2 가 단독 소유 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거2 |
| `s006-3` | b1 | 배치 결정 누락·빚 답습 신호의 판정은 final.md 와 검사기가 한다 | Obligation | enforcedBy `check-layer-skeleton.py` + delegatedTo `agent-discipline-reviewer` | 근거4 |
| `s006-3` | b2 | 신호 — 새 모듈이 층 구분 없이 한 디렉터리에 모임(평면 답습) | Prohibition | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s006-3` | b3 | 신호 — BC 직계에 트리 밖 여덟째 칸(#81) | Prohibition | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s006-3` | b4 | 신호 — 골격 칸이 비었다고 생략(#488) | Prohibition | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s006-3` | b5 | 신호 — 옛 이름이 새 코드에 재등장(이관 종료 후 트리 밖 칸 위반 #81·#490) | Prohibition | enforcedBy `check-layer-skeleton.py` | 근거5 |
| `s006-3` | b6 | 신호 — check-layer-skeleton exit 2 를 «기존 코드라 면제»로 읽음 | Prohibition | enforcedBy `check-layer-skeleton.py` + delegatedTo `agent-discipline-reviewer` | 근거4 |
| `s006-3` | b7 | 신호 — 좁힌 TARGET·즉석 selector 로 얻은 green(게이트 증거는 저장소 루트 레지스트리 전체 1회뿐) | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거7 |
| `s007-4` | b1 | 모든 이름은 «첫 대입»에 타입을 적는다 — 예외 0 | Obligation | enforcedBy `check-public-surface-annotation.py` | 근거8 |
| `s007-4` | b1 | 타입 부착 범위는 시그니처·모듈/클래스 변수·함수 지역 변수·테스트와 테스트 재료 전부 | Obligation | enforcedBy `check-public-surface-annotation.py` | 근거8 |
| `s007-4` | b1 | 「자명하니까 면제」를 두지 않는다 — 조건부 면제 금지 | Prohibition | enforcedBy `check-public-surface-annotation.py` + delegatedTo `agent-discipline-reviewer` | 근거9 |
| `s007-4` | b2 | 빠지는 곳은 «문법이 없는 자리»뿐(면제가 아니라 불가능) | Exception | enforcedBy `check-public-surface-annotation.py` | 근거8 |
| `s007-4` | b3 | 문법 부재 자리 ① for·with·except·언패킹·다중 대입·증강 대입 | Exception | enforcedBy `check-public-surface-annotation.py` | 근거8 |
| `s007-4` | b4 | 문법 부재 자리 ② 재대입·인스턴스 속성(타입은 클래스 본문에) | Exception | enforcedBy `check-public-surface-annotation.py` | 근거8 |
| `s007-4` | b5 | 문법 부재 자리 ③ 프레임워크 선언(모델 필드·class Meta·enum 멤버) | Exception | enforcedBy `check-public-surface-annotation.py` | 근거8 |
| `s007-4` | b6 | pydantic·ninja Schema·dataclass 필드는 `x: T` 필수 — bare 대입은 규칙 위반 이전에 버그 | Obligation | enforcedBy `check-public-surface-annotation.py` | 근거8 |
| `s007-4` | b6 | 표준 문서군의 코드 예시는 적용 대상 밖 — 규칙은 생성하는 프로덕션·테스트 코드에 건다 | Exception | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s008-4.1` | b1 | 주류(PEP 8·mypy 기본 관례)와 다른 선택임을 숨기지 않는다 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s008-4.1` | b1 | mypy strict 는 시그니처만 강제 — 나머지는 백스톱과 감수자가 집행 | Obligation | enforcedBy `check-public-surface-annotation.py` + delegatedTo `agent-discipline-reviewer` | 근거10 |
| `s009-5` | b1 | 기존 코드베이스의 주석 언어 관례를 우선한다 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s009-5` | b1 | 영어 주석이 지배적이면 영어로 맞춘다(일관성 최우선) | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s009-5` | b1 | 확립된 관례가 없으면 한국어로 쓴다 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s009-5` | b1 | 한 코드베이스 안에서 주석 언어를 섞지 않는다 | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s011-6.1` | b1 | 표준 도구셋은 기능 추가 흐름이 직접 다룬다 — 기존 도구 감지·존중, 부재 시 §2.1 버전-핀 규율 셋업(임의 글로벌 설치 금지) | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s012-6.2` | b1 | 새 런타임 의존성의 버전 «값» 규칙 적용 조건 — 핀 표기·매니페스트 위치는 타 스킬 소유 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s012-6.2` | b2 | 훈련 기억의 버전 번호를 적지 않는다 | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s012-6.2` | b2 | 무핀 설치로 받은 실제 설치 버전을 매니페스트에 핀한다 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s012-6.2` | b2 | 무핀 설치는 resolve 수단일 뿐 최종 상태는 핀 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s012-6.2` | b4 | '최신'은 기존 핀과 호환되는 최신이다 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s012-6.2` | b4 | 기존 프레임워크·핵심 의존성 핀 상향 금지 — 불가하면 보고(설계 반송) | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s012-6.2` | b5 | 안정 릴리스만 택한다 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s012-6.2` | b5 | resolve 결과가 pre/rc/dev 면 핀하지 말고 보고 | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s012-6.2` | b5 | 직접 의존성만 매니페스트에 핀하고 전이 의존성은 락파일에 맡긴다 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s012-6.2` | b6 | 막힌 환경 — 사설·제한 인덱스는 그 인덱스의 최신을 핀하고 resolve 불가면 기억값 금지·보고 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |

**4원 근거 본문**(공유 근거는 코드로 참조 — 각 코드는 §16 4원 ①문면 역할명 ②docstring § 인용 ③P0 커버 ④registry/#N 대응 중 **실제 성립한 것만** 적었다):

- **근거1** — ①문면 — frontmatter description 은 스킬 라우터의 로드 트리거 문면 · ②27종 전수 실독 결과 스킬 로드·선택 판정 술어 0 · §16 표 discipline-houserules → agent-discipline-reviewer
- **근거2** — ①문면 역할명 «→ <스킬명>»(경계 위임 선언) · ②27종 전수 실독 결과 스킬 경계 판정 술어 0 · §16 표 discipline-houserules → agent-discipline-reviewer
- **근거3** — registry Agent 등재 · §16 위임 기본값 표(discipline-houserules 문서군 → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례); check-*.py 27종 docstring 선두 전수 실독 결과 이 규범을 지목하는 ①역할명·②§ 인용·③P0 커버 근거 0
- **근거4** — ①문면 직접 지목 «결정적 백스톱은 `check-layer-skeleton` 이고 다른 모든 검사보다 먼저 돈다(#487)»(같은 절 말미) · ②check-layer-skeleton.py docstring «표준 파일트리 골격 검사기 — 제1원칙(#486~#491)의 결정적 백스톱»·«트리 데이터는 standard_tree.py(정본 140행의 기계 사본) 하나에서 온다» · ④rule-owner-map #486~#491·#81·#490 → scripts/check-layer-skeleton.py; 스코프·권한 판정은 기계 밖이라 위임 병기
- **근거5** — ①문면 직접 지목 «결정적 백스톱은 `check-layer-skeleton` 이고 다른 모든 검사보다 먼저 돈다(#487)»(같은 절 말미) · ②check-layer-skeleton.py docstring «표준 파일트리 골격 검사기 — 제1원칙(#486~#491)의 결정적 백스톱»·«트리 데이터는 standard_tree.py(정본 140행의 기계 사본) 하나에서 온다» · ④rule-owner-map #486~#491·#81·#490 → scripts/check-layer-skeleton.py
- **근거6** — ②check-test-config.py docstring ⑵ «트리 개정 명세 몫 — `test/` 구조 (트리 105~111행 · D56) #383/#384 `test/` 의 직계 자식은 다섯뿐» — 문면이 인용한 «final.md §1 트리 105~111행»과 행 범위 축자 일치 · registry Checker 등재; 승인 여부 판정은 기계 밖이라 위임 병기
- **근거7** — ①문면이 집행 도구로 `scripts/registry_gate.py` 를 명시 — check-*.py 27종 로스터 밖이라 enforcedBy 대상이 아니다(registry.ttl Checker 개체 = scripts/check-*.py glob) · ②27종 전수 실독 결과 게이트 증거·차분 판정 술어 0 · §16 표 discipline-houserules → agent-discipline-reviewer
- **근거8** — ②check-public-surface-annotation.py docstring «dddjango 타입 전면 검사기 — «첫 대입에 타입» 규율의 결정적 백스톱»·«#493 모든 이름은 «첫 대입»에 타입을 적는다 … 빠지는 것은 문법이 없는 여덟 자리뿐 … 재대입과 선언적 클래스 본문(ORM 모델 필드·ninja Schema 필드·enum 멤버)은 면제» 축자 일치 · ④rule-owner-map #493 → scripts/check-public-surface-annotation.py
- **근거9** — ②check-public-surface-annotation.py docstring «dddjango 타입 전면 검사기 — «첫 대입에 타입» 규율의 결정적 백스톱»·«#493 모든 이름은 «첫 대입»에 타입을 적는다 … 빠지는 것은 문법이 없는 여덟 자리뿐 … 재대입과 선언적 클래스 본문(ORM 모델 필드·ninja Schema 필드·enum 멤버)은 면제» 축자 일치 · ④rule-owner-map #493 → scripts/check-public-surface-annotation.py; 「자명한가」 판단은 기계 밖이라 위임 병기
- **근거10** — ②check-public-surface-annotation.py docstring «dddjango 타입 전면 검사기 — «첫 대입에 타입» 규율의 결정적 백스톱»·«#493 모든 이름은 «첫 대입»에 타입을 적는다 … 빠지는 것은 문법이 없는 여덟 자리뿐 … 재대입과 선언적 클래스 본문(ORM 모델 필드·ninja Schema 필드·enum 멤버)은 면제» 축자 일치 · ④rule-owner-map #493 → scripts/check-public-surface-annotation.py; ①문면이 «백스톱과 감수자»를 이원 지목해 검사기+에이전트 병기

## 3. 재진술 유예 (다른 문서 상대 — spec 미기재 · T3 소급 패스 대상)

**문서 내 쌍은 spec 처리 완료** — ① `s001`/b2 → `s003`/b2·b4·b7 ② `s005-2`/b1 → `s003`/b2·b7 ③ `s006-3`/b7(신호 6) → `s004-1`/b5(백스톱 실행 계약). ①②③ 모두 사본 쪽 Work 를 유지하고 블록 관계만 걸었다(사유 §4).

아래는 상대가 **다른 문서**라 spec 에서 뺀 쌍이다. 상대 문서는 전부 직접 열어 대조했고, **이미 이관된 문서의 좌표는 마커 제거본(센서스) 기준으로 환산**했다(`agent-*` 3종은 마커 6~8건 삽입 상태).

| # | 사본 블록(이 문서) | 상대 문서/절 | 확인한 상대 문면(센서스 좌표) | 비고 |
|---|---|---|---|---|
| 1 | `s001`/b2 W3 · `s003`/b2 W1·W2 | `discipline-houserules-final`/s001 | 3행 «이 문서가 dddjango 플러그인이 만드는 코드의 파일트리 «값»의 정본이다 — SKILL.md·에이전트 문서는 여기를 가리키기만 하고 값을 복제하지 않는다» | **상호 재진술**(발주서 양쪽 Y). 정본은 final s001, 사본이 skill 쪽. 소급 시 skill→final 방향으로 걸어야 한다 |
| 2 | `s004-1`/b2 W1·W2 | `discipline-houserules-final`/s003-0 · s004-1 | 13–25행 §0 제1원칙(#486~#492) · 26–180행 §1 표준 트리 140행 | 발주서 재진술 열이 지목한 주 쌍. skill 은 «§0(골격은 내용과 무관 · 고정 칸은 빈 채로도 · 트리 밖 칸은 반환)» 로 **3구 요약** — 요약 대 상세(1:N) |
| 3 | `s004-1`/b2 W5·W12 | `discipline-houserules-final`/s014 | 228–231행 «brownfield 는 «면제»가 아니라 «아직 안 갚은 빚»이다» · 230행 «백스톱이 내는 위반이 곧 그것이다» | 발주서 final s014 재진술 열이 이 절을 역지목(Y:discipline-houserules-skill/s004-1) — 쌍 확정 |
| 4 | `s004-1`/b2 W13 | `discipline-houserules-final`/s003-0 | 15행 «**모든 검사보다 먼저 서는 원칙이다**(#487 — 골격이 어긋나면 나머지 검사를 돌릴 이유가 없다)» | skill 은 여기에 **검사기 이름(`check-layer-skeleton`)까지** 실어 더 구체적이다 — 배선의 ①근거가 skill 쪽에만 있는 비대칭 |
| 5 | `s004-1`/b3 W2 | `discipline-houserules-final`/s004-1 (트리 블록) | 문면이 인용한 «`final.md` §1 트리 105~111행» = 현재 파일 **136~142행**(트리 1행 = 파일 32행 오프셋 +31) — `test/` 아래 `unit/`·`integration/`·`e2e/`·`factories/`·`fake/` | 좌표계가 **트리 내부 행 번호**라 파일 행과 다르다. 소급 시 블록 IRI 는 final s004-1/b3(code 펜스 31–172행) 하나뿐이라 트리 행 지목은 alias 나 별도 좌표 체계가 필요 — **T3 게이트 조항(무접두 #N 재검토)와 같은 자리** |
| 6 | `s004-1`/b2 W7·W8·W9·W10 (집행 스코프·이동 권한) | `agent-coder`/s004 · `agent-design-architect`/s005 | coder 센서스 **53행** «승인 스코프 밖 기존 배선·배치는 어떤 위반 판정을 근거로도 이 작업에서 옮기지 않는다(… `discipline-houserules` SKILL §1.1 판정 물음 · 2026-08-13)»(현재 57행) · architect 센서스 **62행** «`discipline-houserules` SKILL §1 을 따른다 — 소스 파일트리는 언제나 dddjango 표준 파일트리다»(현재 67행) | 두 에이전트 문서가 이 절을 **명시 인용**. 3중 사본 층 — 소급 시 이 절이 정본, 에이전트 쪽이 사본 |
| 7 | `s004-1`/b3 W1·W2·W3 (test artifact) | `agent-coder`/s004 · `agent-design-architect`/s005 | coder 센서스 **33행** «입장 표가 승인한 test artifact가 있을 때만 그 artifact를 의미군에 둔다. 구조 규칙만으로 test file·case·assertion·helper·move/split이나 빈 test package를 만들지 않는다»(현재 37행) · architect 센서스 62행 후단 동문 | 축자에 가까운 사본 — 소급 1순위 |
| 8 | `s004-1`/b5 W3·W4 (게이트 증거) | `agent-discipline-reviewer`/s007 | 센서스 **92행** «백스톱 exit 0 을 «의미 준수»의 증거로 읽지 않는다» · «범위 밖 legacy 잔존은 발견이 아니라 빚 보고 채널이고 거기서 수리·이동 지시를 만들지 않으며»(현재 99행) | 같은 규범의 리뷰어 시점 서술 |
| 9 | `s006-3`/b5 (신호 4 — 옛 이름 재등장) | `discipline-houserules-final`/s013 | 224–227행 «옛 이름 … 이중 수용은 2026-08-12 에 끝났다 … 이제 별도 진단이 아니라 트리 밖 칸 위반(#81·#490 — 층 이름 위장은 #324)» | 발주서 final s013 note «skill s006-3 신호 4가 이 절의 사본(원출처는 여기)» — **방향 확정**(정본=final s013) |
| 10 | `s006-3`/b3 (신호 2 — #81) | `discipline-houserules-final`/s006 | 185행 «**#81** — `application/<bounded_context>/` 바로 아래에는 일곱 가지만 온다 … 여덟째는 없다» | 신호형 재프레이밍 |
| 11 | `s006-3`/b4 (신호 3 — #488) | `discipline-houserules-final`/s003-0 | 18행 «**#488** — 고정 이름의 칸은 «부모가 있으면» 반드시 있다 — 폴더는 비어도 `__init__.py` 로, 파일도 비면 «빈 파일»로 만든다» | 동상 |
| 12 | `s006-3`/b6 (신호 5 — exit 2 를 면제로 읽기) | `discipline-houserules-final`/s014 | 230행 «brownfield 는 … 규칙이 바뀌어 위반이 됐다 … 「가만 있어도 해로운」 위반은 그것을 기다리지 않는다» | «빚은 면제가 아니다» 의 근거 절 |
| 13 | `s007-4` 전체(9 Work) | `agent-discipline-reviewer`/s007 | 센서스 **92행** ⑤ «타입 규율은 `check-public-surface-annotation` 이 전면(시그니처·지역·속성·모듈/클래스) 기계 소유다 — 네 몫은 ⓓ#69 후보의 물음과, 면제 자리에 억지로 어노테이트해 ORM/enum 을 깨뜨리는 역방향 오류뿐이다»(현재 99행) | **소유 분할 선언의 재진술** — 이 절의 «문법 부재 자리»(면제)와 리뷰어의 «역방향 오류» 가 같은 경계의 앞뒤. 배선(enforcedBy `check-public-surface-annotation.py`)의 ③근거이기도 하다 |
| 14 | `s009-5` 전체(4 Work) | `agent-discipline-reviewer`/s007 | 센서스 **92행** ④ «주석·docstring 언어가 프로젝트 관례(없으면 한국어)와 일치하는지도 여기서 본다(기계 밖)»(현재 99행) | 이 절의 위임 배선(«기계 밖» = 27종 미커버)의 ①근거를 겸한다 |
| 15 | `s011-6.1` · `s012-6.2` | `agent-discipline-reviewer`/s007 | 센서스 **71행** «근거 `implementation-test §7`·houserules §6.1/§6.2»(현재 78행) | 리뷰어가 이 두 절을 판정 근거로 **명시 인용** — 재진술이라기보다 소유 조인이라 소급 시 `restates` 대신 조인 표기 후보 |

### 3-1. 유예 기각 판정(대조했으나 재진술로 보지 않은 것)

- `s003`/b4~b7·`s001`/b2 W4 의 **경계 위임 4~3건** ↔ 상대 스킬 문서 — 위임은 «어디로 넘긴다» 포인터이고 상대 문서의 규범을 다시 말하지 않는다. `implementation-python-final` 검수표 §3-1 이 같은 부류를 이미 등재해 **중복 유예를 피한다**.
- `s012-6.2`/b1 W1 의 «핀 표기·매니페스트 위치는 `implementation-django-ninja` §2.1·`implementation-django` 소유» ↔ 상대 §2.1 — 이것도 소유 지정(위임)이지 재진술이 아니다. 다만 §2.1 개정 시 이 문장의 앵커가 깨질 수 있어 **앵커 무결성 점검 대상**으로만 남긴다.
- `s005-2`(§2 충돌 중재) ↔ `agent-design-architect`/s006(리뷰 반영·충돌 중재, 82–91행) — 이름이 겹치지만 architect 쪽은 **G1 리뷰 피드백 반영 절차**라 트리 코퍼스 충돌과 다른 사안이다. 기각.

## 4. 경계 판단 메모

- **frontmatter 의 블록 분해** — `[2,2]` prose(`name:`) → `[3,3]` norm(`description:` — Work 다중 연결) → `[4,4]` prose(`user-invocable:`) → `[5,6]` prose(닫는 `---` + 빈 줄). 1행 여는 `---` 는 절 헤딩 라인이라 `djr:headingSnapshot` 이 가져간다(§13 «첫 블록 시작 = line_start+1»). **초판의 `[4,6]` 병합을 행 단위로 갈랐다(W3 적대 리뷰 F6 반영)** — 기이관 skill 12종 전건이 `[4,4]`+`[5,6]` 이고 `agent-coder`/s001 도 같다. byte 등가·Work 계수 무영향(재검증 exit 0 · Work 75 불변).
- **`④` 라벨을 `registry.ttl` 개체 등재에 쓰지 않는다(W3 적대 리뷰 F7 반영)** — §16·발주 계약의 4원 ④ 는 «registry **#N** 대응» 이다. 위임 기본값 basis(근거3)의 «registry Agent 등재» 는 개체 존재 사실이라 ④ 자리가 아니다 — 사실 기재는 남기고 «④» 접두만 뗐다(근거6 의 «registry Checker 등재» 도 같은 성질이라 함께). 위임 기본값 규범의 §16 요건은 «기본값 표 + 27종 전수 0» 경로만으로 충족된다.

- **`s004-1` 이 이 묶음 최대 밀도 절** — 12행에 Work 28. 블록은 §13 자연 단위(리드인 문단 1 · 번호 항 3 · 굵은 문단 2 = 6블록)로만 갈랐고, 한 항 안 13문장은 `djr:statesNorm` **다중 연결**로 처리했다(§13 «해상도의 실현 층» — 행 중간 분할 금지). 항 하나를 문장별로 쪼개면 byte 등가는 유지되지만 마크다운 리스트 항의 자연 경계가 깨진다.
- **26행의 등장 순 = 채번 순** — 13 Work 의 순서는 위 §1 의 ①~⑬ 그대로다. 소급·검수 시 이 순서가 좌표다.
- **`s012-6.2`/b3(80행)만 prose** — «**왜**:» 로 시작하는 이유 전용 불릿이다. 규범 0 이라 norm 으로 올리면 발주서 10 을 11 로 과대 산정하게 된다. 반대로 79·81·82·83행은 굵은 지시로 열려 전부 norm 이다.
- **`s007-4` 의 `Exception` class 사용** — «빠지는 곳은 문법이 없는 자리뿐(면제가 아니라 불가능)» 과 그 3묶음, 그리고 «표준 문서군 코드 예시는 적용 대상 밖» 을 `Exception` 으로 잡았다. 문면이 스스로 «면제가 아니라 불가능» 이라 말하지만, 규범 유형 어휘에서 이 자리는 **본칙의 적용 제외**라 `Exception` 이 맞다 — `Permission` 으로 잡으면 «타입을 안 달 자유» 로 읽혀 본칙(예외 0)을 약화시킨다.
- **`check-layer-skeleton.py` 를 §1·§3 에 광범위 배선한 근거** — ①문면이 §1 말미에서 이 검사기를 **직접 지목**하고(«결정적 백스톱은 `check-layer-skeleton` 이고 다른 모든 검사보다 먼저 돈다(#487)»), ②docstring 25행이 같은 실행 순서를(«이 검사는 다른 모든 검사보다 «먼저» 돌고 … (#487)») 자기 선언하며, ④rule-owner-map 이 #486~#491·#81·#490·#488 을 이 검사기에 건다. §16 «역도 성립» 조항 때문에 이 근거들을 두고 위임 기본값으로 도피할 수 없다.
- **`scripts/registry_gate.py` 는 enforcedBy 대상이 아니다** — 게이트 증거·판정 차분(30행 T3~T5, 신호 6)의 집행 도구를 문면이 명시하지만, `registry.ttl` 의 Checker 개체는 `dddjango/scripts/check-*.py` glob 27종으로 닫혀 있다(`ontology_migrate.py --emit-registry`). 로스터 밖 도구를 `djr:enforcedBy` 로 걸면 게이트 ④(rules 전량 + wiring + vocab) 에서 미선언 개체 참조가 된다. 그래서 **문면 근거를 basis 에 명시한 위임**으로 처리했다 — 기본값 도피가 아니라 «로스터 밖» 사유의 이탈 기록이다. 같은 처리를 `tree_mirror_check`·`checker_lint.py`·`spec_lint.py` 에도 적용했다(→ `discipline-houserules-final` 검수표).
- **`check-test-config.py` 배선(§1.2)** — 27종 전수 실독이 없었으면 놓쳤을 배선이다. 문면이 인용한 «`final.md` §1 트리 105~111행» 과 그 docstring ⑵ 의 «`test/` 구조 (트리 105~111행 · D56)» 가 **행 범위까지 축자 일치**한다(§16 L-F 교훈의 실물 재현).
- **`agent-coder` 를 이 문서에서 쓰지 않은 이유** — «실현 주체는 coder» 문면은 `discipline-houserules-final`/s003-0 24행에만 있고 SKILL 쪽에는 없다. 문면 근거 없는 이탈 금지라 이 문서의 위임은 전건 `agent-discipline-reviewer` 다.
