# T3 이관 검수표 — discipline-cleancode-skill

- 원문: `dddjango/skills/discipline-cleancode/SKILL.md` (56행 · 센서스 일치 · 드리프트 경고 없음 · `graph-owned` 마커 0건 — 좌표 환산 불요)
- spec: `workspace/eval/t3/specs/discipline-cleancode-skill.spec.json`
- 규모: REF 4절 · 블록 39 · Work 20(발주서 규범 20 — **전건 일치**)
- 자기 검증: `PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/discipline-cleancode-skill.spec.json` → **exit 0**(검증 전용 · `--write` 미사용)

## 1. census 대사 (발주서 규범 수 ↔ spec Work 수)

| section_key | 헤딩 | 발주서 | spec | 대사 |
|---|---|---|---|---|
| `s001` | (전문) — frontmatter | 2 | 2 | 일치 |
| `s003` | 언제 쓰나 | 5 | 5 | 일치 |
| `s004` | 핵심 운영 원칙 | 11 | 11 | 일치 |
| `s005` | 상세 레퍼런스 | 2 | 2 | 일치 |
| **합계** | — | **20** | **20** | **차 0** |

불일치 절 없음. 다툴 만한 계수의 승계 근거:

- `s001` **2** — frontmatter 를 code 가 아니라 **행 단위 prose/norm** 으로 분해한 웨이브 2 판례(`agent-coder`/s001 — 2행 `name:` prose · 3행 `description:` norm ×2)를 그대로 적용했다. `name:`·`user-invocable:`·`---` 는 플랫폼 표기라 prose, 규범은 `description` 한 줄 안의 마침표 2단위(«…필요하면 로드한다» / «…로 위임»)뿐이다. 센서스 note 의 «codex 는 name 접두 개명·user-invocable 필드 제거 — 플랫폼 표기 이내» 판정과 정합한다.
- `s004` **11** — 불릿 11 = 규범 11. 각 불릿이 «(§N)» 앵커로 final 한 절(또는 절 묶음)을 압축한 한 지시라 마침표 다단위여도 한 축이다(예: 불릿 2 는 §2.14 의 ~6지시 압축이지만 «판정 원리로 승격하라» 한 축 — 센서스 note «bullet2는 §2.14 ~6지시 압축»과 같은 계수).
- `s005` **2** — 표(17행)는 **비규범 좌표계**다. 규범은 표를 여는 지시(34행 «해당 절을 따른다»)와 닫는 지시(56행 «필요한 항목만 읽는다») 2건. 머리행·구분행은 한 블록, 데이터 17행은 행당 한 블록으로 나눠 §13 «표 머리행·구분행도 table-row(계수 2축에서는 데이터 행만 산입)» 를 지켰다(파일럿 `architecture-ddd-final`/s051-8 판형과 동형).

## 2. 배선 근거 표 (전 20 규범)

| 절 | 블록 | Work label | class | enforcedBy / delegatedTo | 4원 근거 |
|---|---|---|---|---|---|
| `s001` | b2 | 클린코드 원칙 필요 시 스킬 로드 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거1 |
| `s001` | b2 | Python 관용구·Django 특화 패턴의 타 스킬 위임 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거1 |
| `s003` | b1 | 언어 비종속 클린코드 원칙 필요 시 로드 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거1 |
| `s003` | b2 | Python 관용구·PEP8·타입 힌트·docstring 기계 규칙의 implementation-python 위임 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거2 |
| `s003` | b3 | Django 모델·ORM·서비스 레이어 특화 패턴의 implementation-django 위임 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거2 |
| `s003` | b4 | 도메인 전략·애그리거트·바운디드 컨텍스트의 architecture-ddd 위임 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거2 |
| `s003` | b5 | 테스트 코드 작성법의 implementation-test 위임 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거2 |
| `s004` | b1 | 이름은 의도를 드러낸다 — 한 개념 한 단어·품사·범위 비례 길이 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004` | b2 | 매직 값·상수 승격의 판정 원리 적용(닫힌 집합 승격·심볼 소비·허용 목록·birth-enum·wire Literal 재예외) | Obligation | enforcedBy `check-choices-literal-consumption.py` + delegatedTo `agent-discipline-reviewer` | 근거4 |
| `s004` | b3 | 함수는 작게 한 가지만 — 추상화 수준 통일·인수 최소·플래그 금지·명령조회 분리·부수효과 금지 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004` | b4 | 인터페이스 주석 필수·구현 주석 최소화 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004` | b5 | 모듈은 깊게 — 단순 인터페이스 뒤 강력 기능·얕은 모듈과 레드 플래그 경계 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004` | b6 | 행동이 상태를 결정한다 — 묻지 말고 시켜라·조건문의 다형성 대체·로직과 데이터 동거 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004` | b7 | SOLID 5원칙 적용 — 같은 이유는 모으고 다른 이유는 분리 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004` | b8 | DRY 는 지식의 중복을 금지한다 — 코드 유사성이 아닌 비즈니스 지식 단위 판단 | Prohibition | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004` | b9 | 오류는 설계로 먼저 제거하고 불가하면 예외 — 보호절·DbC·방어적 프로그래밍 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004` | b10 | 코드 스멜 감지·리팩토링 제거 — 기능 보존 검증하며 작은 단계 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s004` | b11 | 레거시는 Seam 보호 후 개선 — 임시 특성화 probe 의 영구 계약 고정 금지 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s005` | b1 | 주제별 상세는 references/final.md 의 해당 절을 따른다 | Obligation | delegatedTo `agent-discipline-reviewer` | 근거3 |
| `s005` | b20 | final.md 는 필요한 항목만 읽는다(전체 로드 불필요) | Permission | delegatedTo `agent-discipline-reviewer` | 근거3 |

**4원 근거 본문**(같은 근거를 쓰는 규범이 많아 코드로 참조 — 각 코드는 §16 4원 ①문면 역할명 ②docstring § 인용 ③P0 커버 ④registry/#N 대응 중 실제 성립한 것만 적었다):

- **근거1** — ①문면 — frontmatter description 은 스킬 라우터의 로드 트리거 문면 · ②check-*.py 27종 전수 실독 결과 스킬 로드·위임 판정 술어 0(에이전트 호출·스킬 선택은 검사기 관할 밖) · §16 표 discipline-cleancode → agent-discipline-reviewer
- **근거2** — ①문면 역할명 «→ <스킬명>»(경계 위임 선언) · ②27종 전수 실독 결과 스킬 경계 판정 술어 0 · §16 표 discipline-cleancode → agent-discipline-reviewer
- **근거3** — registry Agent 등재 · §16 위임 기본값 표(discipline-cleancode 문서군 → agent-discipline-reviewer · rule-owner-map ⓓ 유일 관례); check-*.py 27종 docstring 선두 전수 실독 결과 이 규범을 지목하는 ①역할명·②§ 인용·③P0 커버 근거 0
- **근거4** — ②check-choices-literal-consumption.py docstring 선두 «cleancode §2.14 소비 규율» 직접 § 인용(«선언된 심볼은 심볼로만 소비» 항의 결정적 부분집합 집행) + registry Checker 등재 + ③P0 «백스톱 부분 커버»; 같은 docstring 의 «보지 않는 것(의미 레인 = discipline-reviewer 몫)» 선언 때문에 위임 병기 — discipline-cleancode-final s026-2.14 배선과 동형

## 3. 재진술 유예 (다른 문서 상대 — spec 미기재 · T3 소급 패스 대상)

**문서 내 쌍은 spec 처리 완료** — `s001`/b2(frontmatter description) → `s003`/b1·b2·b3 에 `djr:restates` 를 걸었다. 방향 판단: 발주서 재진술 열은 s001↔s003 을 **상호** 표기하나(양쪽 Y), 정본은 **본문 절 `s003`** 으로 잡았다(위임 4건 전량 보유 = 더 완전 · description 은 python/django 2건만 압축). Work 는 양쪽 다 유지했다 — 근거는 §4 «재진술과 Work 승격» 메모.

아래는 **상대가 다른 문서**라 브리프 §21·공정 §15 에 따라 spec 에서 뺀 쌍이다. 상대 문서는 전부 직접 열어 대조했고, 이미 이관된 문서(마커 삽입본)의 좌표는 **마커 제거본(센서스) 기준으로 환산**해 적었다.

| # | 사본 블록(이 문서) | 상대 문서/절 | 확인한 상대 문면(센서스 좌표) | 비고 |
|---|---|---|---|---|
| 1 | `s004`/b1 W «이름은 의도를 드러낸다» | `discipline-cleancode-final`/s013-2.1·s017-2.5·s018-2.6·s016-2.4 | 109–121·167–186·187–198·149–166행 — «2.1 의도를 분명히 밝혀라»·«2.5 한 개념에 한 단어»·«2.6 클래스 이름은 명사, 메서드 이름은 동사»·«2.4 …변수 이름 길이» | 1불릿 ↔ 4절(요약 대 상세 1:N) |
| 2 | `s004`/b2 W «매직 값·상수 승격 판정 원리» | `discipline-cleancode-final`/s026-2.14 | 304–328행 «2.14 매직 값과 상수 승격 판정» — 306행 «오타의 실패 모드와 철자의 계약성으로 판정한다», 310–312행 승격 3원리 | **3중 사본 층(a)** — 센서스 note 의 «동기화 누락 1순위(P0 발견 5)». 소급 시 spec `restates` 가 아니라 **개정 동기화 대상**으로 올려야 한다(SKILL 불릿에 birth-enum·wire Literal 재예외까지 실려 있어 final §2.14 개정이 이 줄을 반드시 동반해야 함) |
| 3 | `s004`/b3 W «함수는 작게 한 가지만» | `discipline-cleancode-final`/s028-3.1·s029-3.2·s030-3.3·s031-3.4·s032-3.5·s033-3.6·s034-3.7 | 331–386·387–392·393–410·411–422·423–435·436–456·457–483행 | 1불릿 ↔ §3 전체(7절) |
| 4 | `s004`/b4 W «인터페이스 주석 필수·구현 주석 최소화» | `discipline-cleancode-final`/s041-4.2·s040-4.1·s056-6.4·s057-6.5 | 566–581행 «인터페이스 주석과 멤버 변수 주석은 짧게라도 반드시 작성해야 하며» · 549–565·698–703·704–737행 | SKILL 앵커 «(§4, §6.4–§6.5)» 가 상대 절을 직접 지목 |
| 5 | `s004`/b5 W «모듈은 깊게» | `discipline-cleancode-final`/s059-7.1·s060-7.2 | 740–755·756–818행 «7.1 깊은 모듈 vs 얕은 모듈»·«7.2 전략적 프로그래밍» | |
| 6 | `s004`/b6 W «행동이 상태를 결정한다» | `discipline-cleancode-final`/s063-8.1·s064-8.2·s065-8.3·s067-8.5 | 834–855·856–869·870–898·916–936행 | |
| 7 | `s004`/b7 W «SOLID 5원칙» | `discipline-cleancode-final`/s070-9.1·s072-9.2·s073-9.3·s074-9.4·s075-9.5 | 963–981·996–1028·1029–1048·1049–1066·1067–1090행 | |
| 8 | `s004`/b8 W «DRY 는 지식의 중복» | `discipline-cleancode-final`/s101-13.1 | 1718–1758행 «13.1 DRY는 지식의 중복을 금지하는 것이다» | 축자 수준 요약 |
| 9 | `s004`/b9 W «오류는 설계로 먼저 제거» | `discipline-cleancode-final`/s091-12.1·s092-12.2·s095-12.5·s096-12.6·s097-12.7 | 1541–1561·1562–1582·1618–1643·1644–1659·1660–1663행 | |
| 10 | `s004`/b10 W «코드 스멜·리팩토링» | `discipline-cleancode-final`/s112-15.1·s118-15.2 | 1926–1929·2106–2107행 | |
| 11 | `s004`/b11 W «레거시는 Seam 보호 후 개선» | `discipline-cleancode-final`/s126-16.2·s127-16.3·s128-16.4·s129-16.5 | 2279–2329·2330–2363·2364–2388·2389–2404행 — «임시 특성화 probe» 는 §16.5 특성화 테스트의 dddjango 고유 한정 | |
| 12 | `s003`/b1 W «클린코드 원칙 필요 시 로드» | `agent-discipline-reviewer`/s007 | 센서스 **124행** «로드한 discipline-cleancode·discipline-tdd·implementation-test·discipline-houserules 스킬의 절을 근거로 인용한다»(현재 파일 131행 — 마커 8건 제거 환산) | 로드 «조건»↔로드 «후 인용 의무» — 같은 축의 반쪽. 소급 시 restates 가 아니라 **인접 규범**으로 남길 후보 |
| 13 | `s004`/b2 W «매직 값·상수 승격» | `agent-discipline-reviewer`/s007 | 센서스 **77행** «상수 승격·심볼 소비 규율(백스톱 사각 전담) … 1곳째부터 승격 — `discipline-cleancode` §2.14»(현재 84행 환산) | 리뷰어 문면이 이 불릿과 final §2.14 를 **명시 인용** — 3중 사본 층(b). 2번과 같은 동기화 다발 |
| 14 | `s005`/b1·b20 W(단일 출처 지정 2건) | `discipline-cleancode-final` 문서 전체 | 1–21행 서문(«이 문서는 … 핵심 원칙을 언어 비종속적으로 종합한 것이다») | **재진술 아님으로 판정** — 포인터 규범(«어디를 읽어라»)이지 상대 규범의 재진술이 아니다. §3-1 기각 기록 |

### 3-1. 유예 기각 판정(대조했으나 재진술로 보지 않은 것)

- `s005` 의 §1–§17 매핑표 17행 — final 절 제목의 **인용 목록**이라 규범이 아니고(센서스 «매핑표 자체는 비규범»), 목차 사본은 `discipline-cleancode-final`/s002(목차, 22–44행)가 이미 같은 역할을 한다. 두 목록 간 결번·불일치는 재진술 문제가 아니라 **표 동기화** 문제라 소급 패스가 아니라 개정 채널로 넘긴다.
- `s003`/b2~b5(위임 4건) ↔ 상대 스킬들의 역방향 경계 선언 — `implementation-python-final` 검수표 §3 이 이미 «SKILL s003 13행 → discipline-cleancode» 를 유예 등재했다. **같은 쌍을 양쪽에서 두 번 올리지 않기 위해** 여기서는 등재하지 않고 상대 검수표의 등재를 지시한다(중복 유예 방지).

## 4. 경계 판단 메모

- **frontmatter 의 kind** — `---`(1·5행)은 절 헤딩(1행)과 prose(5행)로 갈렸다. 1행은 절 스팬의 헤딩 라인이라 `djr:headingSnapshot` 이 가져가고(도구가 자동), 블록은 2행부터 시작한다(§13 «첫 블록 시작 = line_start+1»). 5행 `---` 는 닫는 구분자라 6행(빈 줄)과 함께 prose `[5,6]` 으로 묶고, 4행 `user-invocable:` 은 별도 prose `[4,4]` 로 두었다 — **웨이브 행 단위 판례 동조(W3 적대 리뷰 F5 반영)**. 초판은 `[4,6]` 한 블록으로 병합했으나, 저작 시 인용한 `agent-coder`/s001 을 포함해 기이관 skill 12종 전건이 `[4,4]`+`[5,6]` 이라 블록 IRI 입도가 코퍼스 동형 구조와 어긋났다(byte 등가·Work 계수에는 영향 없음 — 재검증 exit 0·Work 20 불변). kind 는 그대로 prose 다: code 로 잡으면 datatype 이 `xsd:string` 이 되어 §16 셰이프 규약(norm/prose=@ko)과 어긋나고, YAML 을 «펜스»로 읽는 것도 §13 «code 리터럴 = 여는 펜스~닫는 펜스» 정의에 안 맞는다.
- **`description` 한 줄에 Work 2개** — §13 «해상도의 실현 층»(한 블록의 여러 규범 문장은 `statesNorm` 다중 연결 · 행 중간 분할 불요)을 그대로 썼다. 문장 등장 순 = 채번 순.
- **표 블록 분할** — 머리행+구분행을 한 블록으로, 데이터 행을 행당 한 블록으로 나눈 것은 파일럿(`spec-architecture-ddd-final.json` s051-8: `[2059,2060]` 머리+구분 → `[2061,2061]` 이후 행별)과 같은 판형이다. 이 절의 데이터 행은 규범을 지지 않지만, 소급 패스가 §N 행별로 final 절과 조인할 때 블록 IRI 가 필요해 행별 분할을 유지했다.
- **재진술과 Work 승격** — §15 는 «정본 1곳만 Work 승격 + 사본 블록에 `djr:restates`» 인데, 그 요건의 실물 선례는 파일럿의 **축자 쌍**(ninja §6.2↔§2.2)이다. `s001`/b2 는 축자 사본이 아니라 **라우터용 압축 재구성**(위임 4건 중 2건만·문면 상이)이라 Work 를 유지하고 블록 관계만 `restates` 로 남겼다. Work 를 접었다면 발주서 20 ↔ spec 18 의 과소가 생기고, «라우터가 읽는 트리거 규범»이라는 별개 집행 지점이 그래프에서 사라진다. 이 판정 규칙(축자·완전 등가일 때만 Work 0)은 이 묶음 3문서에 일관 적용했다.
- **`s004`/b2 의 배선** — 유일한 `enforcedBy` 다. `check-choices-literal-consumption.py` docstring 선두가 «cleancode §2.14 소비 규율» 을 **직접 § 인용**하므로 §16 «역도 성립: 담당 검사기의 문면·docstring 근거가 있는데 기본값으로 도피하면 오배선» 에 걸린다. 다만 같은 docstring 이 «보지 않는 것(의미 레인 = discipline-reviewer 몫)» 을 명시하므로 위임을 병기했다 — `discipline-cleancode-final`/s026-2.14 의 «선언된 집합 타입 값의 심볼 소비» 배선과 동형이다.
- **`④` 라벨을 `registry.ttl` 개체 등재에 쓰지 않는다(W3 적대 리뷰 F7 반영)** — §16·발주 계약의 4원 ④ 는 «registry **#N** 대응» 이다. 위임 기본값 basis(근거3)의 «registry Agent 등재» 는 개체 존재 사실이라 ④ 자리가 아니다 — 사실 기재는 남기고 «④» 접두만 뗐다(근거4 의 «registry Checker 등재» 도 같은 성질이라 함께). 위임 기본값 규범의 §16 요건은 «기본값 표 + 27종 전수 0» 경로만으로 충족된다.
- **`check-naming.py` 를 `s004`/b1 에 걸지 않은 판정** — 27종 전수 실독 결과 그 docstring 의 담당은 `#28`(원전 패턴 약어)·`#30`·`#33`·`#34`·`#36`·`#41`·`#43`·`#44` 등 **dddjango 트리 명명 규약**이고, «한 개념에 한 단어»·«클래스는 명사» 같은 보편 명명 원칙 술어는 0이다. 웨이브 1 의 `discipline-cleancode-final` §2 배선(전건 위임)과도 일치한다.
