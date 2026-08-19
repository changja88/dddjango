너는 적대 검증자다. 온톨로지 센서스의 **codex 대응 «SAME» 판정을 반증**하라 — claude판↔codex판 문서쌍에서 «표기 치환을 초과하는» 실질 차이를 찾아내는 것이 과업이다. final.md 11쌍은 기계 byte diff로 동일 확정이므로 **범위 밖**이다. 검증 대상은 SKILL.md·에이전트 문서다.

## 대응 경로 매핑
- claude `dddjango/skills/<이름>/SKILL.md` ↔ codex `codex-dddjango/skills/<이름>/SKILL.md` — 단 개명 4종: architecture-ddd·discipline-cleancode·discipline-houserules·implementation-test 는 codex 쪽이 `dddjango-<이름>`.
- claude `dddjango/agents/<이름>.md` ↔ codex `codex-dddjango/skills/dddjango-<이름>/SKILL.md`
- claude `dddjango/commands/dddjango.md` ↔ codex `codex-dddjango/skills/dddjango/SKILL.md`

## 판정 기준
- **표기 치환 이내(SAME 타당)**: 스킬명 `dddjango-` 접두 개명, frontmatter `user-invocable: false` 유무, 플랫폼 호출 표기(Task tool↔spawn 등)의 기계적 대응, 경로 표기 차이.
- **SAME 반증(DIFF여야 함)**: 규범 문장의 추가·삭제·조건 변경, 절 구조 차이, 수치·목록 항 차이, 한쪽에만 있는 규칙.

## 기존 판정 (반증 대상)
분류 TSV(`workspace/design/2026-08-19-ontology-t1-census/E0N-classify.tsv`의 codex 열)는 다음만 DIFF로 봤다: E01·E03·E04·E06 SKILL frontmatter 각 1절, E05 SKILL s001·s004, E10 command 6절+coder s004. **나머지 전부 SAME** — 특히 E02·E07·E08·E09의 SKILL 쌍 전절과 E10의 agents 6종(acceptance-tester·design-architect·design-review-api/db/ddd·discipline-reviewer) 전절이 SAME이다.

## 과업
SKILL 11쌍+agents 7쌍+command 1쌍을 diff로 실측하고, SAME 판정 절에서 «표기 치환 초과» 차이를 찾아라. 각 발견에 양판 문면을 나란히 인용하라.

## 출력 형식 (최종 메시지로만 — 파일 쓰기 금지)
```
# L-C codex SAME 반증 결과
## 발견 (SAME→DIFF 주장)
| # | 문서쌍 | claude 문면 | codex 문면 | 판정 근거 |
(발견 0이면 «발견 0» 명시)
## 기존 DIFF 13건 타당성
한 줄 확인(반박 있으면 명시)
```
