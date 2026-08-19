너는 적대 코드 리뷰어다. T1에서 신설·개작된 온톨로지 도구의 **정확성 결함(correctness bug)**을 찾아라. 스타일·취향 지적은 범위 밖이다 — 정본(ontology/·코퍼스 md·원장)을 오염시키거나 오판(false green/red)을 낳는 결함만.

## 대상 (저장소 루트 기준 — 전부 신설/개작)
- `workspace/tools/ontology_migrate.py` — 이관 조립(스팬 산술 offs/span·무손실 검증·ISSUED 재사용 큐 reuse_queue·마커 제거 복원 원문·LEDGER append 중복 방지)
- `workspace/tools/ontology_render.py` — 렌더 투영(graph_sections의 절 키 복원 unquote·apply_to_corpus의 count==1 치환)
- `workspace/tools/ontology_render_sync.py` — 동기 검증(strip_marker·SyncDebt 강등·--smoke의 백업/복원)
- `workspace/tools/ontology_ledger_check.py` — 원장 부식(유효 행=마지막 행·현재 분할 대조)
- `workspace/tools/ontology_issued_check.py` — 대장 정합(WORK_RE 정규식 — canon 축약형 djr:R-NNNN과 전체 IRI 두 표기)
- `workspace/tools/ontology_structural_check.py` — SPARQL 5종·kind↔datatype
- `workspace/tools/ontology_census.py` — 절 분할(fence-aware·frontmatter·바이트 스팬)
- `workspace/tools/corpus_mirror_sync.py`의 개작부(_graph_owned_rows·_excise_graph_sections·write_skill의 스팬 보존 병합)
- `workspace/tools/ontology_gate.py`의 개작부(check_djr_fragments·rules 병합)

## 집중 질문 (반증 지향)
1. 경계 산술: 파일 끝 비개행·빈 파일·마지막 절·마커가 파일 마지막 절에 있을 때 — span/offs·strip_marker(`b"\n".join`)가 바이트를 잃거나 더하는 경로가 있나?
2. reuse 큐: 명세 순서 변경·부분 재실행 시 잘못된 rid 재사용으로 ISSUED↔rules 정합이 «조용히» 어긋나는 경로(검사기가 못 잡는)?
3. count==1 치환(render apply·mirror 병합): 스팬이 파일에 2회 등장하거나 0회일 때 fail-closed가 실제로 작동하나? replace 대상이 부분 문자열로 다른 절과 겹치는 경우?
4. 정규식: WORK_RE의 lookahead가 놓치는 표기(행 끝·`;`·`,` 뒤)? FRAGMENT_BAD가 과탐/미탐하는 문자?
5. ledger 유효 행 규약(마지막 행 유효)이 도구 간(ledger_check·mirror _graph_owned_rows·migrate existing_graph)에 일관 구현됐나?
6. census parse_sections: setext 헤딩·펜스 미폐쇄·frontmatter 미폐쇄 문서에서 절 경계가 틀어지며 무손실 단언을 «통과»하는(오판정인데 green) 경로?

## 출력 형식 (최종 메시지로만 — 파일 쓰기 금지)
```
# L-H 도구 코드 리뷰 결과
## 발견 (correctness만, 심각도: blocker=정본 오염·오판 / major=조건부 오판 / minor=한정 상황)
| # | 파일:행 | 심각도 | 결함 | 재현 시나리오 |
(발견 0이면 «발견 0» 명시)
```
