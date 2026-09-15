# 적대 검토 처분 — 부모가 직접 재확인한 것 (2026-09-15)

rv-B·rv-C·rv-D 의 BLOCKER 를 액면으로 받지 않고 직접 실행해 확인한 결과다.
«확인» = 내가 명령을 돌려 같은 사실을 봤다. «미확인» = 아직 안 돌려봤다.

## 확인 — 설계 v1 을 무효화하는 것

### V1. 수리 3 은 이 결함을 못 잡는다 (rv-B B1 = rv-C C1) — **확인**
A8 `render-audit-impl.json` · `render-audit.json` 을 직접 열었다.

| | url | texts | 다이얼로그 텍스트 |
|---|---|---|---|
| 구현 실측 | `http://127.0.0.1:8891/related-persons/` | 13 | **0건** |
| 시안 실측 | `…/관계인.dc.html` | 15 | **0건** |

둘 다 **목록 페이지뿐**이다(«관계인 등록하기»는 목록의 버튼이지 다이얼로그가 아니다).
결함 컨테이너 `.rpe-scroll` 은 HTMX swap 으로만 들어오므로 `querySelectorAll` 은 0건 →
`clip.findings = []` → exit 0 green. **설계 v1 §6 브리프의 «수리 3 단독: 이번 결함 잡는다»는 거짓이었다.**
설계 §3.1 이 시안측에 대해 쓴 바로 그 이유(«다이얼로그 안이라 초기 렌더에 없다»)가
구현측에도 그대로 성립하는데 §2 가 그 대칭을 못 봤다.

### V2. §1 의 «결정적 반증»이 틀렸다 (rv-C C3) — **확인**
- A8 `design-spec.md:468` 기각(15) 목록에 **`--space-1` 이 있고 사유가 «미사용 space 단계»**다.
- 그런데 동결 `관계인.dc.html` 의 인라인 선언에 **2px 가 4건** 쓰인다:
  `padding: 2px 4px 0` · `gap: 2px` · **`padding: 2px 2px 4px`**(문제의 그것) · `padding: 0 2px`.
- 즉 기각 사유가 **사실과 다르다**. 토큰 축이 고갈된 게 아니라 **위반됐다**.
- 그리고 **토큰 처분을 검사하는 기계가 저장소에 0개**다
  (`grep -rln design-tokens dddjango-web/scripts/` → extract/refreeze 뿐 · 검사기 없음).

→ 내 §1 의 «토큰 축을 넓혀도 못 잡는다»는 철회한다. 정반대다: **기각 정당성 검사 하나면 G1 에서 잡힌다.**

### V3. audit_version 3 상향의 파급 (rv-D B1) — **확인**
`compare_render_audit.py` 의 `CURRENT_VERSION` 술어는 `:81`·`:100`·`:259` 3곳 + `:194` 리터럴 `2`.
v1→v2 선례(커밋 `72854ce3`)는 `fixtures_audit.sh` 에 **+67줄**의 새 버전 표본을 함께 넣었다.
→ 버전 올림을 포기할 이유는 아니지만(그것이 구버전 스니펫 차단의 유일한 수단),
   설계가 **작업 항목을 통째로 빠뜨렸다**.

### V4. `.mjs` 는 픽스처 글롭 밖 (rv-D B2) — **확인**
`run_fixtures.sh:10` 은 `fixtures_*.sh` 만 수집한다. `.mjs` 는 `fixtures_interactions.sh:10-11`
처럼 쉘 안에서 **명시 호출**해야 돈다.

### V5. `Makefile` 은 봉인 대상 (rv-D B3) — **확인**
`manifest_seal.py:143` 의 protocol 그룹에 `Makefile` 이 있고 `Makefile:187` 이
`manifest_seal.py --check --draft` 를 verify-base-core 에서 돌린다.
→ 변경 커밋 뒤 **별도 chore 봉인 커밋** 필요(`docs/DEVELOPMENT.md` §6).

### V6. 재동결 폐기 집합에 새 산출물이 없다 (rv-D B4 · rv-B 부수) — **확인**
`refreeze.py:32-37 FIXED_DISCARD_FILES` 에 없다. `design-ref` 는 폐기 트리이므로
거기서 파생된 표는 함께 폐기돼야 한다. 그리고 `web_refreeze_contract.py::check_d1` 이
폐기 이름을 `<산출물 폴더>` 로 쓰면 RED 로 잡는다 — 4곳 동시 결정이다.
(지난 사이클에 만든 기계 불변식이 의도대로 작동한다.)

## 확인 — 더 싼 길이 있다

### V7. 구현측에도 다이얼로그 상태 캡처가 존재한다 — **확인**(rv-B/C 가 못 본 사실)
`captures/related-390x844-06-registerform-step1-impl.png` 등 **구현측 폼 상태 캡처가 12장** 있다.
즉 G2 는 구현 다이얼로그를 실제로 연다. 브라우저 검사의 부착점이 «없다»가 아니라
**«초기 실측 1장이 아니라 case 순회에 붙여야 한다»**가 맞다.
다만 그 순회는 Coordinator 가 case 마다 수행하는 경로라 rv-B 의 집행 취약점이 그대로 붙는다.

### V8. 정적 CSS 만으로 잡을 수 있다 (rv-C C2) — **미확인**(수치는 rv-C 가 직접 셈)
rv-C 주장: A8 `web/**/*.css` 전수에서 `overflow: auto|scroll` 규칙 11건 · 가로 패딩 없음 5건 ·
`related_persons.css` 만 보면 2행. 링 확장은 `tokens.css:193` 에서 정적 파싱 가능.
→ 계획 단계에서 내가 직접 재현한다.

## 미결 — rv-A(판정 규칙) 회신 대기

기하 판정 규칙 자체의 결함은 rv-A 소관이다. 정적 검사로 방향이 바뀌어도
«링 바깥 확장 파싱»은 공유되므로 rv-A 의 발견은 여전히 유효하다.
