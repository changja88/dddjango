너는 적대 검증자다. dddjango 온톨로지 T1 파일럿 이관의 **Work 117건(문장↔Work 대응·규범 유형·prefLabel)을 전수 반증**하라.

## 재료 (저장소 루트 기준)
- 정본 그래프: `ontology/rules/implementation-django-ninja-final.ttl` · `ontology/rules/architecture-ddd-final.ttl` — 블록(djr:text 리터럴 = 원문 스팬 verbatim)·Work(djr:Obligation/Prohibition/Permission/Exception/Override 타입·skos:prefLabel)·블록—djr:statesNorm→Work.
- 이관 명세(저작 근거): `workspace/design/2026-08-19-ontology-t1-migrate/spec-*.json` — 블록별 norms[]의 label·class.
- 판정 기준: 규범 문장 = «에이전트·파이프라인·생성 코드의 행동을 구속하는 지시·금지·조건 문장». 유형: 의무 지시=Obligation·금지=Prohibition·허용/할 수 있다=Permission·조건부 한정/예외=Exception·우선 규칙=Override. prefLabel은 «명칭만»(규범 본문 서술 금지 — 그러나 규범을 **왜곡·오도하지 않아야** 한다).
- 문장→Work 대응 규약: 한 블록의 규범 문장들이 등장 순으로 statesNorm의 Work들에 대응(채번 순 = 명세 등장 순).

## 과업 (반증 지향 — 전수 117건)
각 norm 블록의 djr:text 리터럴을 정독하고:
1. **유형 오판**: class가 문장의 규범 양상과 다른 건(예: «…하지 않는다»인데 Obligation).
2. **라벨 왜곡**: prefLabel이 문장의 구속 내용을 오도·과대·과소 대표하는 건.
3. **문장 누락**: 블록 안에 행동 구속 문장이 있는데 Work 미채번인 건(명사구 리스트 항 제외 — 그건 L-G 소관).
4. **과채번**: 설명·이유·예시 문장에 Work가 붙은 건.

## 출력 형식 (최종 메시지로만 — 파일 쓰기 금지)
```
# L-E Work 정합 반증 결과
검토 Work: 117
## 발견
| # | Work(R-NNNN)·블록 | 유형(오판/왜곡/누락/과채번) | 문장 인용 | 주장 |
(발견 0이면 «발견 0» 명시)
## 집계
유형 분포 확인(Obligation/Prohibition/Permission/Exception/Override 수)·판정 유지 수
```
