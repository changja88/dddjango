너는 적대 검증자다. T1 파일럿 이관의 **wiring 배선 117건을 전수 반증**하라 — 잘못된 검사기 귀속과 «기본값 위임으로 도피한» 배선을 찾아내는 것이 과업이다.

## 재료 (저장소 루트 기준)
- 배선 정본: `ontology/wiring/implementation-django-ninja-final.ttl` · `ontology/wiring/architecture-ddd-final.ttl`(Work—djr:enforcedBy→검사기 `djr#c/<파일명>` / Work—djr:delegatedTo→에이전트 `djr#a/<doc_key>`) · `ontology/wiring/registry.ttl`(개체 대장).
- 저작 근거(basis 필드): `workspace/design/2026-08-19-ontology-t1-migrate/spec-*.json`.
- 규범 문장 실물: `ontology/rules/*.ttl`의 djr:text 리터럴(블록—statesNorm→Work).
- 4원 판단 기준(authoring §16): ① 규범 문면의 역할명 ② 검사기 docstring의 § 인용 ③ P0 «커버» 판정 ④ registry #N 대응. 위임 기본값 표: architecture-ddd→design-review-ddd(설계)/discipline-reviewer(구현)·architecture-db/api→해당 review 에이전트·implementation-*→discipline-reviewer·절차 층→command-dddjango. **기본값 이탈은 문면 근거 필요·역도 성립: 문면 근거가 있으면 기본값 도피는 오배선이다.**
- 검사기 실물: `dddjango/scripts/check-*.py`의 docstring(선두 20행이면 충분 — 특히 check-error-centralization·check-api-error-controller-contract·check-openapi-error-declaration·check-ninja-boundary-middleware·check-composition-root·check-domain-model·check-layer-skeleton·check-context-isolation).
- 참조: `workspace/plan/2026-08-11-rule-owner-map.md`(ⓒ/ⓓ 관례).

## 과업 (반증 지향 — 전수)
1. **enforcedBy 오귀속**: 그 검사기 docstring·검증 범위가 그 규범 문장을 실제로 집행하지 않는 건.
2. **enforcedBy 누락**: delegatedTo 기본값으로 처리됐지만 문면·docstring상 명백한 담당 검사기가 있는 건.
3. **위임 대상 오선정**: 문면이 다른 판정 주체(G1/Coordinator·특정 리뷰어)를 지목하는데 기본값으로 간 건(또는 그 역).
4. **basis 기재와 실배선 불일치**(spec의 basis 문구 vs ttl 트리플).

## 출력 형식 (최종 메시지로만 — 파일 쓰기 금지)
```
# L-F wiring 반증 결과
검토 배선: 117 Work
## 발견
| # | Work·문장 요지 | 현 배선 | 주장 배선 | 근거(docstring/문면 인용) |
(발견 0이면 «발견 0» 명시)
## 집계
검사기별·에이전트별 배선 수 확인 + 판정 유지 수
```
