# T3 이관 spec 저작 계약 (전 저작·수리 에이전트 공통 필독)

> 역할: 배정 문서 1건의 REF 절 전량을 **migrate-spec/1 JSON**으로 저작한다. TTL·ISSUED·LEDGER·원문은 절대 직접 쓰지 않는다 — 조립은 `ontology_migrate.py`가 병합 단계에서 직렬 수행한다. 네 산출물은 **판단**이고, byte 등가는 도구가 기계 보장한다.

## 필독 (작업 전 실독 순서)

1. 자기 발주서 `workspace/eval/t3/orders/<doc_key>.md` — 스코프·드리프트 경고·재진술 좌표
2. `workspace/tools/ontology-authoring.md` **§13(블록 경계·공백 소유)·§14(IRI)·§15(공정)·§16(wiring 4원 종합)**
3. `workspace/tools/ontology_migrate.py` 선두 docstring — spec 스키마 정본
4. 파일럿 판형 2건: `workspace/design/2026-08-19-ontology-t1-migrate/spec-*.json`
5. **검사기 로스터 전수 실독**: `dddjango/scripts/check-*.py` 27종의 docstring 선두(§16 L-F 교훈 — 8종만 보고 9종 오배선한 실증이 있다. 27종 전수가 의무)

## spec 작성 규칙

- 대상 = 발주서의 REF 절 **전량**(NAR 절 제외·파일럿 기이관 절은 발주서에서 이미 제외됨).
- 행 번호는 **현재 파일 기준 1-indexed**. 발주서에 드리프트 경고가 있으면 센서스 행 번호를 믿지 말고 현재 파일에서 헤딩을 찾아 재확정한다.
- 절당 blocks: 첫 블록 시작 = `line_start+1`(헤딩 다음 행), 연속·비중첩·절 끝까지 전체 커버 — 도구가 단언하므로 누락 시 verify가 잡는다.
- kind 5종: `norm`(규범 문장 포함 문단/불릿) · `prose` · `code`(펜스 전체) · `table-row`(머리행·구분행 포함 행 단위) · `checklist-item`(`- [ ]` 한정).
- norm 블록의 `norms` 배열: 문장 등장 순 = 채번 순. class ∈ {Obligation, Prohibition, Permission, Exception, Override}. `label`은 짧은 한국어 명사구.
- **wiring**: 각 norm에 `enforcedBy`(검사기 파일명 배열) 또는 `delegatedTo`(에이전트 doc_key 배열) — 무소유 금지. `basis`에 4원 근거(①문면 역할명 ②docstring § 인용 ③P0 커버 ④registry #N) 중 실제 성립한 것을 한 줄로. 검사기 비커버 규범은 §16 위임 기본값 표를 따르고, 기본값 이탈·기본값 도피 양쪽 다 문면 근거 필요.
- **재진술**: 같은 문서 안 쌍만 spec `restates`에 넣는다. **다른 문서 상대는 spec에 넣지 말고** worksheet «재진술 유예» 절에 기록한다(전 웨이브 완료 후 소급 패스가 일괄 연결).

## 자기 검증 (제출 조건)

```
PYTHONPATH=workspace/tools .venv/bin/python workspace/tools/ontology_migrate.py workspace/eval/t3/specs/<doc_key>.spec.json
```
`--write` 없이(검증 전용) **exit 0**이 될 때까지 수리 후 제출. `--write`는 절대 금지.

## worksheet 양식 (`workspace/eval/t3/worksheets/<doc_key>.md`)

1. **census 대사**: 절별 (발주서 규범 수 ↔ 내 spec 규범 수) — 불일치 절은 사유 한 줄(과소/과대 산정 어느 쪽이 옳은지 판정 포함)
2. **배선 근거 표**: Work label · enforcedBy/delegatedTo · 4원 근거 — 전 규범
3. **재진술 유예**: 사본 블록 좌표 → 상대 문서/절 (census restate 열 참고·직접 확인 후)
4. **경계 판단 메모**: 애매했던 블록 경계·kind 판정과 근거

## 금지

- 원문 md·`ontology/` 전체·다른 에이전트의 spec/worksheet 수정 금지. 쓰는 파일은 자기 spec + worksheet 2개뿐.
- TTL 직접 저작 금지(`#` 주석·직렬화 규칙 등은 도구 소관 — 네가 신경 쓸 일이 없게 설계돼 있다).
